#!/usr/bin/env python3
"""Auto-edit raw outfit clips into a short TikTok video.

Rules:
  * only keep footage that is sharp (not blurry / no motion blur)
  * crop from mouth level downwards (face above the mouth is hidden)
  * final video is <= 15 seconds, 1080x1920 (9:16)

Usage:
  python3 auto_edit.py INPUT_DIR -o output.mp4 [--duration 14] [--music song.mp3]
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm", ".3gp")
OUT_W, OUT_H, OUT_FPS = 1080, 1920, 30
ANALYSIS_FPS = 10          # frames per second sampled for analysis
MIN_CLIP, MAX_CLIP = 1.5, 3.0  # seconds per cut
BLUR_REL = 0.65            # frame is blurry if sharpness < BLUR_REL * video median
MOUTH_RATIO = 0.78         # mouth sits ~78% down the detected face box

FACE_CASCADE = cv2.CascadeClassifier(
    os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml"))


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration",
         "-of", "json", path], capture_output=True, text=True, check=True)
    info = json.loads(out.stdout)
    return float(info["format"]["duration"])


def analyse(path):
    """Sample the video and return per-sample (time, sharpness, mouth_y, face_cx).

    Frames are read through OpenCV, which applies the rotation metadata so the
    coordinates match what ffmpeg will output after auto-rotation.
    """
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    step = max(1, round(fps / ANALYSIS_FPS))
    samples, idx = [], 0
    w = h = None
    while True:
        ok = cap.grab()
        if not ok:
            break
        if idx % step == 0:
            ok, frame = cap.retrieve()
            if not ok:
                break
            h, w = frame.shape[:2]
            scale = 540 / max(h, w)
            small = cv2.resize(frame, (int(w * scale), int(h * scale)))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
            sharp = cv2.Laplacian(gray, cv2.CV_64F).var()
            faces = FACE_CASCADE.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=6,
                minSize=(int(gray.shape[1] * 0.08),) * 2)
            mouth_y = face_cx = None
            if len(faces):
                fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
                mouth_y = (fy + fh * MOUTH_RATIO) / scale
                face_cx = (fx + fw / 2) / scale
            samples.append((idx / fps, sharp, mouth_y, face_cx))
        idx += 1
    cap.release()
    return samples, w, h


def find_segments(samples, duration):
    """Return candidate sharp segments: list of (start, end, score)."""
    if not samples:
        return []
    sharp = np.array([s[1] for s in samples])
    thresh = BLUR_REL * np.median(sharp)
    good = sharp >= thresh
    segs, start = [], None
    dt = 1.0 / ANALYSIS_FPS
    # skip the first/last 0.5s (usually hand reaching for the phone)
    for (t, _, _, _), g in zip(samples, good):
        ok = g and 0.5 <= t <= duration - 0.5
        if ok and start is None:
            start = t
        elif not ok and start is not None:
            segs.append((start, t))
            start = None
    if start is not None:
        segs.append((start, samples[-1][0] + dt))

    out = []
    for s, e in segs:
        # split long sharp runs into MAX_CLIP pieces
        t = s
        while e - t >= MIN_CLIP:
            ce = min(t + MAX_CLIP, e)
            sel = sharp[[(s0 >= t and s0 < ce) for s0, *_ in samples]]
            out.append((t, ce, float(sel.mean())))
            t = ce
    return out


def crop_box(samples, start, end, w, h):
    """Crop (x, y, cw, ch) from mouth level down with 9:16 aspect."""
    ys = [m for t, _, m, _ in samples if start <= t < end and m is not None]
    xs = [c for t, _, m, c in samples if start <= t < end and m is not None]
    top = int(np.median(ys)) if ys else 0
    cx = float(np.median(xs)) if xs else w / 2
    ch = h - top
    cw = int(round(ch * 9 / 16))
    if cw > w:  # too wide: keep full width, trim the bottom to keep 9:16
        cw = w
        ch = int(round(cw * 16 / 9))
    x = int(np.clip(cx - cw / 2, 0, w - cw))
    return x - x % 2, top - top % 2, cw - cw % 2, ch - ch % 2


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input_dir")
    ap.add_argument("-o", "--output", default="output.mp4")
    ap.add_argument("--duration", type=float, default=14.0,
                    help="target length in seconds (max 15)")
    ap.add_argument("--music", help="optional audio track to put under the video")
    ap.add_argument("--keep-audio", action="store_true",
                    help="keep original clip audio (ignored if --music is set)")
    args = ap.parse_args()
    target = min(args.duration, 15.0)

    files = sorted(os.path.join(args.input_dir, f) for f in os.listdir(args.input_dir)
                   if f.lower().endswith(VIDEO_EXTS))
    if not files:
        sys.exit(f"no videos found in {args.input_dir}")

    candidates = []  # (score, file, start, end, crop)
    for order, f in enumerate(files):
        dur = probe(f)
        samples, w, h = analyse(f)
        segs = find_segments(samples, dur)
        print(f"{os.path.basename(f)}: {dur:.1f}s, {len(segs)} sharp segment(s)")
        for s, e, score in segs:
            candidates.append((score, order, f, s, e, crop_box(samples, s, e, w, h)))

    if not candidates:
        sys.exit("no sharp footage found")

    # pick the sharpest segments, at most 2 per source video for variety,
    # until the target duration is filled
    candidates.sort(key=lambda c: -c[0])
    picked, total, per_file = [], 0.0, {}
    for c in candidates:
        if total >= target:
            break
        if per_file.get(c[2], 0) >= 2 and len(files) > 1:
            continue
        length = min(c[4] - c[3], target - total)
        if length < 1.0:
            continue
        picked.append((c[1], c[3], c[2], c[3] + length, c[5]))
        per_file[c[2]] = per_file.get(c[2], 0) + 1
        total += length
    picked.sort()  # keep original shooting order

    with tempfile.TemporaryDirectory() as tmp:
        parts = []
        for i, (_, s, f, e, (x, y, cw, ch)) in enumerate(picked):
            part = os.path.join(tmp, f"part{i:02d}.mp4")
            vf = (f"crop={cw}:{ch}:{x}:{y},scale={OUT_W}:{OUT_H}:flags=lanczos,"
                  f"setsar=1,fps={OUT_FPS},format=yuv420p")
            cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{s:.3f}", "-i", f,
                   "-t", f"{e - s:.3f}", "-vf", vf, "-c:v", "libx264", "-preset", "medium",
                   "-crf", "18"]
            if args.keep_audio and not args.music:
                cmd += ["-af", "aresample=44100", "-ac", "2", "-c:a", "aac", "-b:a", "192k"]
            else:
                cmd += ["-an"]
            subprocess.run(cmd + [part], check=True)
            parts.append(part)
            print(f"  cut {i + 1}: {os.path.basename(f)} {s:.1f}-{e:.1f}s "
                  f"crop {cw}x{ch}+{x}+{y}")

        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as fh:
            fh.writelines(f"file '{p}'\n" for p in parts)
        joined = os.path.join(tmp, "joined.mp4")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", lst, "-c", "copy", joined], check=True)

        if args.music:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-i", args.music,
                            "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                            args.output], check=True)
        else:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", joined, "-c", "copy",
                            "-movflags", "+faststart", args.output], check=True)

    print(f"done: {args.output} ({total:.1f}s, {len(picked)} cuts)")


if __name__ == "__main__":
    main()
