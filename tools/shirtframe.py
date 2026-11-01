"""Frame a shirt wide cut from the mouth down, centred on the shoulders.

usage: python3 tools/shirtframe.py clip start length xexpr_out [--lip 0.65]

Owner's rule for tops: the frame starts at the mouth (so the collar and both
shoulders show) and the body sits on the centre line. Segmentation of the
legs (segtrack.py) centres the trousers, not the shirt, and a fixed top row
drifts off the mouth when he moves, so this measures the body itself with
MediaPipe's pose landmarker (model cached in ~/.cache/omar, 10 fps):

- top: the lowest nose-to-mouth line over the whole cut (nose y + lip *
  (mouth y - nose y)), so the nose never shows and the mouth line is the top
  edge at the frame where the head is lowest. The crop runs from there to the
  bottom of the footage (feet when the clip has them).
- x: the shoulder midpoint, smoothed like segtrack.py, written to xexpr_out
  as a piecewise-linear ffmpeg expression for render_plan.py.

Prints one JSON line: top, ch, cw, the mouth y range (a wide range means the
head moves a lot, pick a steadier window) and the per-0.3 s shoulder centres.
Use it in a plan as [clip, start, length, top, cx, ch, "push_top", xexpr].
"""
import argparse, json, os, subprocess, sys, urllib.request
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import edit_video as e
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

URL = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
       "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("start", type=float); ap.add_argument("length", type=float)
ap.add_argument("out")
ap.add_argument("--lip", type=float, default=0.65)
ap.add_argument("--top", type=int, help="mouth-line row to use when the face isn't visible (back/side views): take it from a front cut of the same clip")
ap.add_argument("--noface", action="store_true", help="back/profile view: ignore the pose fit (it can invent a face on the back of the head); use --top and the torso mask")
ap.add_argument("--cx", type=int, help="fixed body centre (source px) when the mask is pulled off by a dark rack beside him; check it on a frame first")
ap.add_argument("--ch", type=int, help="crop height (default: from the top to the bottom of the footage); smaller leaves room to centre")
a = ap.parse_args()

import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
model = os.path.expanduser("~/.cache/omar/pose_landmarker_full.task")
if not os.path.exists(model):
    os.makedirs(os.path.dirname(model), exist_ok=True)
    urllib.request.urlretrieve(URL, model)

W, H, _ = e.probe(a.clip)
w = 540; h = int(round(H * w / W / 2) * 2); fps = 10
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{a.start:.2f}", "-t", f"{a.length + 0.1:.2f}",
                      "-i", a.clip, "-an", "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
                      "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
opts = vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=model),
                                    running_mode=vision.RunningMode.VIDEO)
nose, mouth, cx = [], [], []
with vision.PoseLandmarker.create_from_options(opts) as pl:
    for i, f in enumerate(F):
        r = pl.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f)),
                                int(i * 1000 / fps))
        if not r.pose_landmarks:
            nose.append(np.nan); mouth.append(np.nan); cx.append(np.nan); continue
        L = r.pose_landmarks[0]
        sh = (L[11].y + L[12].y) / 2 * H
        if L[0].visibility < 0.8 or (L[9].y + L[10].y) / 2 * H > sh - 80:
            # Face hidden (back or profile view) or a broken fit: no mouth
            # line from this frame, and the torso mask gives the centre.
            nose.append(np.nan); mouth.append(np.nan); cx.append(np.nan); continue
        nose.append(L[0].y * H)
        mouth.append((L[9].y + L[10].y) / 2 * H)
        cx.append((L[11].x + L[12].x) / 2 * W)
nose, mouth, cx = map(np.array, (nose, mouth, cx))
if a.noface:
    nose[:] = np.nan; mouth[:] = np.nan; cx[:] = np.nan
line = nose + a.lip * (mouth - nose)
face = int((~np.isnan(line)).sum())
if face >= 3:
    top = int(np.nanmax(line)) // 2 * 2
    if a.top is not None:
        top = max(top, a.top)
elif a.top is not None:
    top = a.top
else:
    sys.exit("face not visible: pass --top from a front cut of the same clip")
if face < 0.6 * len(cx):
    # Back/profile views: centre on the torso (rows from the top line to
    # 45 % of the height) from the person mask instead of the shoulders.
    from stepscan import person_masks
    masks, k = person_masks(a.clip, a.start, a.start + a.length + 0.1, fps)
    cx = []
    for m in masks:
        mh = m.shape[0]
        c = m[int(top / H * mh) + 2:int(0.45 * mh)].sum(0).astype(float)
        cdf = np.cumsum(c) / max(c.sum(), 1)
        cx.append((np.searchsorted(cdf, .05) + np.searchsorted(cdf, .95)) / 2 * k if c.sum() > 100 else np.nan)
    cx = np.array(cx)
if a.cx is not None:
    cx = np.full(len(nose), float(a.cx))
ch = (a.ch or H - top) // 2 * 2
cw = int(ch * 9 / 16) // 2 * 2
if cw > W:
    cw = W // 2 * 2; ch = int(cw * 16 / 9) // 2 * 2
idx = np.arange(len(cx)); ok = ~np.isnan(cx)
cx = np.interp(idx, idx[ok], cx[ok])
sm = np.convolve(np.pad(cx, 3, mode="edge"), np.ones(7) / 7, mode="valid")
xs = np.clip(sm - cw / 2, 0, W - cw)
pts = [(i / fps, xs[i]) for i in range(0, len(xs), 3)]
if pts[-1][0] < a.length:
    pts.append((a.length, xs[-1]))
expr = f"{pts[-1][1]:.0f}"
for (t0, x0), (t1, x1) in reversed(list(zip(pts, pts[1:]))):
    expr = f"if(lt(t,{t1:.2f}),{x0:.0f}+({x1 - x0:.0f})*(t-{t0:.2f})/{t1 - t0:.2f},{expr})"
open(a.out, "w").write(expr + "\n")
print(json.dumps({"top": top, "ch": ch, "cw": cw,
                  "mouth": [int(np.nanmin(mouth)), int(np.nanmax(mouth))] if face else None,
                  "face_frames": f"{face}/{len(nose)}",
                  "clamped": bool((sm - cw / 2 < 0).any() or (sm + cw / 2 > W).any()),
                  "centres": [int(c) for c in sm[::3]]}))
