#!/usr/bin/env python3
"""Auto-edit raw outfit videos into one short TikTok clip (<=15s, 9:16).

What it does:
  1. Scans every video in the input folder and scores each moment for
     sharpness (Laplacian variance), so blurry / shaky parts are skipped.
  2. Detects the face and crops from the mouth down (face hidden, outfit shown).
  3. Picks the clearest segments across all videos, total <= --max-seconds.
  4. Joins them into one 1080x1920 MP4.

Usage:
  python3 edit_video.py INPUT_DIR -o output.mp4
  python3 edit_video.py INPUT_DIR -o output.mp4 --music song.mp3 --max-seconds 12
"""
import argparse
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")
OUT_W, OUT_H = 1080, 1920
SAMPLE_FPS = 5

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def find_videos(folder):
    return sorted(
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith(VIDEO_EXTS))


def analyse(path):
    """Sample the video and return per-sample (time, sharpness, mouth_y, face_cx)."""
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    step = max(1, round(fps / SAMPLE_FPS))
    samples = []
    for i in range(0, n, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if not ok:
            break
        # Phone videos may carry rotation metadata; OpenCV applies it, so use the
        # decoded frame size rather than the container's.
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        small = cv2.resize(gray, (w * 480 // max(w, h), h * 480 // max(w, h)))
        scale = w / small.shape[1]

        faces = face_cascade.detectMultiScale(small, 1.1, 5, minSize=(30, 30))
        mouth_y = face_cx = None
        if len(faces):
            fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
            mouth_y = (fy + 0.78 * fh) * scale  # mouth sits ~3/4 down the face box
            face_cx = (fx + fw / 2) * scale

        # Sharpness of the part we will actually keep (below the mouth).
        top = int(mouth_y / scale) if mouth_y else small.shape[0] // 4
        region = small[top:] if top < small.shape[0] - 20 else small
        sharp = cv2.Laplacian(region, cv2.CV_64F).var()
        samples.append((i / fps, sharp, mouth_y, face_cx))
    cap.release()
    return {"path": path, "w": w, "h": h, "duration": n / fps, "samples": samples}


def best_segments(info, seg_len):
    """Slide a window over the video; score = worst sharpness in the window
    (one blurry moment ruins a segment)."""
    s = info["samples"]
    win = max(1, int(seg_len * SAMPLE_FPS))
    out = []
    for a in range(0, max(1, len(s) - win + 1)):
        chunk = s[a:a + win]
        score = min(c[1] for c in chunk)
        out.append((score, chunk[0][0], chunk))
    return out


def crop_box(info, chunk, mouth_offset):
    """Fixed crop for a segment: top edge at the mouth, 9:16, centred on the body."""
    w, h = info["w"], info["h"]
    ys = [c[2] for c in chunk if c[2] is not None]
    xs = [c[3] for c in chunk if c[3] is not None]
    # No face found -> assume mouth around 22% from the top (typical mirror selfie).
    top = int(np.median(ys)) if ys else int(h * 0.22)
    top = max(0, min(top + int(mouth_offset * h), int(h * 0.6)))
    ch = h - top
    cw = min(w, int(ch * OUT_W / OUT_H))
    ch = int(cw * OUT_H / OUT_W)
    cx = int(np.median(xs)) if xs else w // 2
    x = max(0, min(cx - cw // 2, w - cw))
    return x, top, cw - cw % 2, ch - ch % 2


def render(segments, out_path, music, keep_audio):
    tmp = tempfile.mkdtemp()
    parts = []
    for k, (info, start, length, (x, y, cw, ch)) in enumerate(segments):
        part = os.path.join(tmp, f"part{k}.mp4")
        vf = (f"crop={cw}:{ch}:{x}:{y},scale={OUT_W}:{OUT_H}:flags=lanczos,"
              f"setsar=1,fps=30,unsharp=5:5:0.6")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}",
               "-t", f"{length:.3f}", "-i", info["path"], "-vf", vf,
               "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-pix_fmt", "yuv420p"]
        if keep_audio:
            cmd += ["-af", "aresample=44100", "-ac", "2", "-c:a", "aac"]
        else:
            cmd += ["-an"]
        subprocess.run(cmd + [part], check=True)
        parts.append(part)

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    joined = os.path.join(tmp, "joined.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                    "-safe", "0", "-i", lst, "-c", "copy", joined], check=True)

    if music:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                        "-i", music, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-shortest", "-movflags", "+faststart",
                        out_path], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined,
                        "-c", "copy", "-movflags", "+faststart", out_path],
                       check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input_dir")
    ap.add_argument("-o", "--output", default="output.mp4")
    ap.add_argument("--max-seconds", type=float, default=15.0)
    ap.add_argument("--segment", type=float, default=2.5,
                    help="length of each cut in seconds (default 2.5)")
    ap.add_argument("--per-video", type=int, default=2,
                    help="max cuts taken from one source video")
    ap.add_argument("--min-quality", type=float, default=0.5,
                    help="reject cuts sharper than less than this fraction of "
                         "the video's sharpest moment (0-1, default 0.5)")
    ap.add_argument("--mouth-offset", type=float, default=0.0,
                    help="shift crop top by this fraction of height (+ = lower)")
    ap.add_argument("--music", help="audio file to put under the video")
    ap.add_argument("--keep-audio", action="store_true",
                    help="keep the original audio (ignored if --music is set)")
    args = ap.parse_args()

    videos = find_videos(args.input_dir)
    if not videos:
        sys.exit(f"No videos found in {args.input_dir}")

    candidates = []
    for v in videos:
        info = analyse(v)
        print(f"analysed {os.path.basename(v)}: {info['duration']:.1f}s, "
              f"{info['w']}x{info['h']}, face found in "
              f"{sum(s[2] is not None for s in info['samples'])}/{len(info['samples'])} samples")
        seg = min(args.segment, info["duration"])
        for score, start, chunk in best_segments(info, seg):
            candidates.append((score, info, start, seg, chunk))

    # Sharpness scales differ per camera/video; normalise per video so one
    # very detailed video does not take every slot.
    by_video = {}
    for c in candidates:
        by_video.setdefault(c[1]["path"], []).append(c[0])
    norm = {p: max(v) or 1 for p, v in by_video.items()}
    # A video that is blurry throughout still has max 1.0 after normalising,
    # so also compare against the typical best across all videos.
    global_ref = float(np.median(list(norm.values())))
    candidates.sort(key=lambda c: c[0] / norm[c[1]["path"]], reverse=True)

    chosen, used, total = [], {}, 0.0
    for score, info, start, seg, chunk in candidates:
        if total + seg > args.max_seconds + 1e-6:
            continue
        if score < args.min_quality * norm[info["path"]] or \
                score < args.min_quality * 0.5 * global_ref:
            continue  # too blurry; a shorter video beats a blurry one
        p = info["path"]
        if used.get(p, 0) >= args.per_video:
            continue
        if any(c[0]["path"] == p and abs(c[1] - start) < seg for c in chosen):
            continue  # no overlapping cuts
        chosen.append((info, start, seg, crop_box(info, chunk, args.mouth_offset)))
        used[p] = used.get(p, 0) + 1
        total += seg

    # Keep the original filming order (by file, then by time).
    chosen.sort(key=lambda c: (videos.index(c[0]["path"]), c[1]))
    for info, start, seg, box in chosen:
        print(f"  cut {os.path.basename(info['path'])} @ {start:.1f}s for {seg:.1f}s crop={box}")
    render(chosen, args.output, args.music, args.keep_audio and not args.music)
    print(f"done -> {args.output} ({total:.1f}s)")


if __name__ == "__main__":
    main()
