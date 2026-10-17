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
import json
import os
import subprocess
import sys
import tempfile

import cv2
import numpy as np

VIDEO_EXTS = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")
OUT_W, OUT_H = 1080, 1920
SAMPLE_FPS = 5
ANALYSE_W = 540

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
profile_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_profileface.xml")


def find_videos(folder):
    return sorted(
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.lower().endswith(VIDEO_EXTS))


def probe(path):
    """Display size (after phone rotation) and duration via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
         "stream=width,height:stream_side_data=rotation:format=duration",
         "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    st = d["streams"][0]
    w, h = st["width"], st["height"]
    rot = 0
    for sd in st.get("side_data_list", []):
        rot = int(sd.get("rotation", rot))
    if abs(rot) % 180 == 90:
        w, h = h, w
    return w, h, float(d["format"]["duration"])


def detect_mouth(gray):
    """Return (mouth_y, face_cx) in the given image's pixels, or (None, None)."""
    faces = list(face_cascade.detectMultiScale(gray, 1.1, 6, minSize=(40, 40)))
    if not faces:
        faces = list(profile_cascade.detectMultiScale(gray, 1.1, 6, minSize=(40, 40)))
    if not faces:
        flipped = cv2.flip(gray, 1)
        for fx, fy, fw, fh in profile_cascade.detectMultiScale(flipped, 1.1, 6, minSize=(40, 40)):
            faces.append((gray.shape[1] - fx - fw, fy, fw, fh))
    if not faces:
        return None, None
    # Faces in the lower half are false hits on fabric/hands in these videos.
    faces = [f for f in faces if f[1] + f[3] < gray.shape[0] * 0.5]
    if not faces:
        return None, None
    fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
    return fy + 0.78 * fh, fx + fw / 2  # mouth sits ~3/4 down the face box


def analyse(path):
    """Sample the video and return per-sample (time, sharpness, mouth_y, face_cx).

    Frames are decoded by ffmpeg (fast, handles HEVC and phone rotation) at
    SAMPLE_FPS and ANALYSE_W pixels wide."""
    w, h, duration = probe(path)
    aw = ANALYSE_W
    ah = int(round(h * aw / w / 2) * 2)
    scale = w / aw
    proc = subprocess.Popen(
        ["ffmpeg", "-loglevel", "error", "-threads", "0", "-i", path, "-an",
         "-vf", f"fps={SAMPLE_FPS},scale={aw}:{ah}", "-f", "rawvideo",
         "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    samples = []
    k = 0
    while True:
        buf = proc.stdout.read(aw * ah)
        if len(buf) < aw * ah:
            break
        gray = np.frombuffer(buf, np.uint8).reshape(ah, aw)
        mouth_y, face_cx = detect_mouth(gray)
        # Sharpness of the part we will actually keep (below the mouth).
        top = int(mouth_y) if mouth_y and mouth_y < ah - 40 else 0
        sharp = cv2.Laplacian(gray[top:], cv2.CV_64F).var()
        # Very dark frames (hand over lens) have no usable detail either.
        if gray.mean() < 25:
            sharp = 0.0
        samples.append((k / SAMPLE_FPS, sharp,
                        mouth_y * scale if mouth_y else None,
                        face_cx * scale if face_cx else None))
        k += 1
    proc.wait()
    return {"path": path, "w": w, "h": h, "duration": duration, "samples": samples}


def subject_center(path, start, length, bg_start, bg_len=2.0, w=270,
                   rows=(0.0, 1.0)):
    """Horizontal centre (in source pixels) of the person over a cut.

    Uses a static-camera trick: the median of frames from an empty stretch
    (bg_start..bg_start+bg_len, before the person walks in) is the background;
    pixels that differ from it are the person. Returns (cx, left, right) as
    the median over the cut, so whole-body shots can be cropped to centre.
    `rows` limits the measurement to a band of the frame (fractions of the
    height), e.g. (0, 0.55) to centre on the torso in a shirt video."""
    W, H, _ = probe(path)
    h = int(round(H * w / W / 2) * 2)

    def frames(t0, dur, fps):
        out = subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.2f}", "-t", f"{dur:.2f}",
             "-i", path, "-an", "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
             "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
        n = len(out) // (w * h)
        return np.frombuffer(out[:n * w * h], np.uint8).reshape(n, h, w).astype(np.int16)

    bg = np.median(frames(bg_start, bg_len, 5), axis=0)
    cs, ls, rs = [], [], []
    for f in frames(start, length, 5):
        mask = np.abs(f - bg) > 28
        mask[:int(rows[0] * h)] = False
        mask[int(rows[1] * h):] = False
        mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN,
                                np.ones((5, 5), np.uint8))
        cols = mask.sum(axis=0).astype(float)
        if cols.sum() < 50:
            continue
        cdf = np.cumsum(cols) / cols.sum()
        ls.append(np.searchsorted(cdf, 0.05))
        cs.append(np.searchsorted(cdf, 0.5))
        rs.append(np.searchsorted(cdf, 0.95))
    k = W / w
    if not cs:
        return W / 2, 0, W
    return float(np.median(cs)) * k, float(np.median(ls)) * k, float(np.median(rs)) * k


def garment_center(path, start, length, rows=(0.2, 0.95), w=270, min_blue=6,
                   v_range=(45, 215)):
    """Horizontal centre of a cool-toned garment (grey/blue/navy) over a cut.

    Works where background differencing doesn't (camera moved, shiny floor):
    keeps pixels whose blue channel beats red by `min_blue` and whose
    brightness is mid-range, which in these warm-lit rooms isolates the
    garment from the orange/beige walls, white shoes and black rack."""
    W, H, _ = probe(path)
    h = int(round(H * w / W / 2) * 2)
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}",
         "-i", path, "-an", "-vf", f"fps=5,scale={w}:{h}", "-f", "rawvideo",
         "-pix_fmt", "bgr24", "-"], capture_output=True, check=True).stdout
    n = len(out) // (w * h * 3)
    frames = np.frombuffer(out[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
    cs = []
    for f in frames:
        b, g, r = (f[..., i].astype(np.int16) for i in range(3))
        v = f.max(axis=2)
        mask = ((b - r) > min_blue) & (v > v_range[0]) & (v < v_range[1])
        mask[:int(rows[0] * h)] = False
        mask[int(rows[1] * h):] = False
        mask = cv2.morphologyEx(mask.astype(np.uint8), cv2.MORPH_OPEN,
                                np.ones((5, 5), np.uint8))
        cols = mask.sum(axis=0).astype(float)
        if cols.sum() < 200:
            continue
        cs.append(np.searchsorted(np.cumsum(cols) / cols.sum(), 0.5))
    return float(np.median(cs)) * W / w if cs else W / 2


def centered_box(W, H, cx, top=0, bottom=None, margin=0.0):
    """Largest 9:16 crop with its horizontal centre at cx, top edge >= top
    (mouth rule) and bottom edge at `bottom` (default: frame bottom, keeps feet)."""
    bottom = H if bottom is None else bottom
    half = min(cx, W - cx)
    cw = int(min(2 * half, (bottom - top) * 9 / 16) * (1 - margin)) // 2 * 2
    ch = int(cw * 16 / 9) // 2 * 2
    x = int(round(cx - cw / 2))
    y = bottom - ch
    return max(0, min(x, W - cw)), max(top, y), cw, ch


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


def crop_box(info, chunk, mouth_offset, fallback_top):
    """Fixed crop for a segment: top edge at the mouth, 9:16, centred on the body."""
    w, h = info["w"], info["h"]
    ys = [c[2] for c in chunk if c[2] is not None]
    xs = [c[3] for c in chunk if c[3] is not None]
    # No face found -> usually a close-up already below the chin; crop
    # fallback_top of the height off the top (0 = keep the full frame).
    top = int(np.median(ys)) if ys else int(h * fallback_top)
    top = max(0, min(top + int(mouth_offset * h), int(h * 0.6)))
    ch = h - top
    cw = min(w, int(ch * OUT_W / OUT_H))
    ch = int(cw * OUT_H / OUT_W)
    cx = int(np.median(xs)) if xs else w // 2
    x = max(0, min(cx - cw // 2, w - cw))
    return x, top, cw - cw % 2, ch - ch % 2


# Slow camera moves applied in turn to each cut (zoompan expressions; F is the
# cut's frame count, so each move runs over the whole cut).
MOTIONS = {
    "zoom_in": ("1+0.10*on/F", "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"),
    "zoom_out": ("1.10-0.10*on/F", "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"),
    "pan_up": ("1.10", "iw/2-iw/zoom/2", "(ih-ih/zoom)*(1-on/F)"),
    "pan_down": ("1.10", "iw/2-iw/zoom/2", "(ih-ih/zoom)*on/F"),
    "push": ("1+0.05*on/F", "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"),
    # Eased zoom out: starts 20% tighter, slows down as it reaches the full
    # frame, so the widest view is exactly the crop (e.g. top edge at mouth).
    "pull": ("1+0.20*pow(1-on/F,2)", "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"),
    # Gentle zoom out: only 8%, eased in and out (smoothstep) over the cut.
    "pull_soft": ("1+0.08*(1-(on/F)*(on/F)*(3-2*on/F))",
                  "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"),
}
MOTION_ORDER = ["zoom_in", "zoom_out", "pan_down", "zoom_in", "pan_up"]
# ffmpeg xfade transitions used in turn between cuts.
TRANSITIONS = ["zoomin", "smoothleft", "hblur", "smoothup", "smoothright", "fadeblack"]
FPS = 30
# Muted "cinematic" look: softer contrast, lifted blacks, cooler shadows,
# slightly less saturation, a light vignette and fine grain.
CINEMATIC_GRADE = (
    "eq=contrast=0.94:saturation=0.82:brightness=-0.01,"
    "curves=r='0/0.03 0.5/0.49 1/0.96':g='0/0.04 0.5/0.5 1/0.97':"
    "b='0/0.08 0.5/0.52 1/0.95',"
    "colorbalance=rs=-0.04:bs=0.05:rh=0.03:bh=-0.03,"
    "vignette=angle=PI/6,noise=alls=5:allf=t")
FONT_DIR = "/usr/share/fonts/truetype/freefont"


def title_filter(title, start=0.15, end=1.9):
    """Two-line title like "Cinematic / OOTD": first word in serif italic,
    the rest in small spaced capitals, fading in and out over the chest."""
    first, _, rest = title.partition(" ")
    fade = (f"if(lt(t,{start:.2f}),0,if(lt(t,{start + 0.3:.2f}),(t-{start:.2f})/0.3,"
            f"if(lt(t,{end - 0.3:.2f}),1,if(lt(t,{end:.2f}),({end:.2f}-t)/0.3,0))))")
    # drawtext can't escape a quote inside a quoted value, so drop quotes.
    esc = lambda t: t.replace("'", "").replace("\\", "").replace(":", "\\:")
    parts = [f"drawtext=fontfile={FONT_DIR}/FreeSerifItalic.ttf:text='{esc(first)}':"
             f"fontsize=130:fontcolor=white:alpha='{fade}':x=(w-tw)/2:y=h*0.40:"
             f"shadowcolor=black@0.35:shadowx=2:shadowy=2"]
    if rest:
        parts.append(f"drawtext=fontfile={FONT_DIR}/FreeSerif.ttf:text='{esc(rest.upper())}':"
                     f"fontsize=58:fontcolor=white:alpha='{fade}':x=(w-tw)/2:y=h*0.40+150:"
                     f"shadowcolor=black@0.35:shadowx=2:shadowy=2")
    return ",".join(parts)


def render(segments, out_path, music, keep_audio, crf=21, motion=True,
           transition=0.3, motions=None, grade=None, title=None):
    """Render each cut (crop + optional camera move), then join them, with
    xfade transitions of `transition` seconds when > 0. `motions` optionally
    names a MOTIONS key per cut (None entries fall back to MOTION_ORDER)."""
    tmp = tempfile.mkdtemp()
    parts = []
    use_audio = keep_audio and not transition
    for k, (info, start, length, (x, y, cw, ch)) in enumerate(segments):
        part = os.path.join(tmp, f"part{k}.mp4")
        vf = f"fps={FPS},crop={cw}:{ch}:{x}:{y},"
        if motion:
            name = (motions[k] if motions and k < len(motions) else None) \
                or MOTION_ORDER[k % len(MOTION_ORDER)]
            z, mx, my = MOTIONS[name]
            frames = max(1, round(length * FPS) - 1)
            z, mx, my = (e.replace("F", str(frames)) for e in (z, mx, my))
            # Upscale first so zoompan's whole-pixel steps don't make it judder.
            vf += (f"scale={OUT_W * 2}:{OUT_H * 2}:flags=lanczos,"
                   f"zoompan=z='{z}':x='{mx}':y='{my}':d=1:"
                   f"s={OUT_W}x{OUT_H}:fps={FPS},")
        else:
            vf += f"scale={OUT_W}:{OUT_H}:flags=lanczos,"
        vf += "setsar=1,unsharp=5:5:0.6,"
        if grade:
            vf += grade + ","
        vf += "format=yuv420p"
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}",
               "-t", f"{length:.3f}", "-i", info["path"], "-vf", vf,
               "-c:v", "libx264", "-preset", "medium", "-crf", "16"]
        if use_audio:
            cmd += ["-af", "aresample=44100", "-ac", "2", "-c:a", "aac"]
        else:
            cmd += ["-an"]
        subprocess.run(cmd + [part], check=True)
        parts.append(part)

    joined = os.path.join(tmp, "joined.mp4")
    if transition and len(parts) > 1:
        inputs, chain, offset, last = [], [], 0.0, "0:v"
        for p in parts:
            inputs += ["-i", p]
        for k in range(1, len(parts)):
            offset += segments[k - 1][2] - transition
            name = TRANSITIONS[(k - 1) % len(TRANSITIONS)]
            out = f"v{k}"
            chain.append(f"[{last}][{k}:v]xfade=transition={name}:"
                         f"duration={transition}:offset={offset:.3f}[{out}]")
            last = out
        if title:
            chain.append(f"[{last}]{title_filter(title)}[vt]")
            last = "vt"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
                        "-filter_complex", ";".join(chain), "-map", f"[{last}]",
                        "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
                        "-pix_fmt", "yuv420p", joined], check=True)
    else:
        lst = os.path.join(tmp, "list.txt")
        with open(lst, "w") as f:
            f.writelines(f"file '{p}'\n" for p in parts)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat",
                        "-safe", "0", "-i", lst,
                        *(["-vf", title_filter(title)] if title else []),
                        "-c:v", "libx264", "-preset",
                        "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
                        *(["-c:a", "aac"] if use_audio else []), joined],
                       check=True)

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
    ap.add_argument("--segment", type=float, default=2.3,
                    help="length of each cut in seconds, including the "
                         "transition overlap (default 2.3 = ~2s on screen)")
    ap.add_argument("--transition", type=float, default=0.3,
                    help="transition length in seconds (0 = hard cuts)")
    ap.add_argument("--no-motion", action="store_true",
                    help="no zoom/pan camera moves")
    ap.add_argument("--cinematic", action="store_true",
                    help="muted film-style colour grade")
    ap.add_argument("--title", help='opening title, e.g. "Cinematic OOTD"')
    ap.add_argument("--per-video", type=int, default=2,
                    help="max cuts taken from one source video")
    ap.add_argument("--min-quality", type=float, default=0.5,
                    help="reject cuts sharper than less than this fraction of "
                         "the video's sharpest moment (0-1, default 0.5)")
    ap.add_argument("--mouth-offset", type=float, default=0.0,
                    help="shift crop top by this fraction of height (+ = lower)")
    ap.add_argument("--fallback-top", type=float, default=0.0,
                    help="when no face is found, crop this fraction off the top "
                         "(0 = full frame, 0.22 = typical mirror selfie)")
    ap.add_argument("--crf", type=int, default=21,
                    help="x264 quality: lower = sharper and bigger file (default 21)")
    ap.add_argument("--cache", help="JSON file to store/reuse the slow analysis")
    ap.add_argument("--music", help="audio file to put under the video")
    ap.add_argument("--keep-audio", action="store_true",
                    help="keep the original audio (ignored if --music is set)")
    args = ap.parse_args()

    videos = find_videos(args.input_dir)
    if not videos:
        sys.exit(f"No videos found in {args.input_dir}")

    cache = {}
    if args.cache and os.path.exists(args.cache):
        with open(args.cache) as f:
            cache = json.load(f)
    candidates = []
    for v in videos:
        key = f"{os.path.abspath(v)}:{os.path.getsize(v)}"
        info = cache.get(key) or analyse(v)
        cache[key] = info
        if args.cache:
            with open(args.cache, "w") as f:
                json.dump(cache, f)
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
        overlap = args.transition if chosen else 0.0
        if total + seg - overlap > args.max_seconds + 1e-6:
            continue
        if score < args.min_quality * norm[info["path"]] or \
                score < args.min_quality * 0.5 * global_ref:
            continue  # too blurry; a shorter video beats a blurry one
        p = info["path"]
        if used.get(p, 0) >= args.per_video:
            continue
        if any(c[0]["path"] == p and abs(c[1] - start) < seg for c in chosen):
            continue  # no overlapping cuts
        chosen.append((info, start, seg, crop_box(info, chunk, args.mouth_offset,
                                                 args.fallback_top)))
        used[p] = used.get(p, 0) + 1
        total += seg - overlap

    # Keep the original filming order (by file, then by time).
    chosen.sort(key=lambda c: (videos.index(c[0]["path"]), c[1]))
    for info, start, seg, box in chosen:
        print(f"  cut {os.path.basename(info['path'])} @ {start:.1f}s for {seg:.1f}s crop={box}")
    render(chosen, args.output, args.music, args.keep_audio and not args.music,
           args.crf, not args.no_motion, args.transition,
           grade=CINEMATIC_GRADE if args.cinematic else None, title=args.title)
    print(f"done -> {args.output} ({total:.1f}s)")


if __name__ == "__main__":
    main()
