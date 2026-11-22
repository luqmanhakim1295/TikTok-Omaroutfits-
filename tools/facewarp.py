"""Change the lower face a little so it looks different, without an AI look.

usage: python3 tools/facewarp.py in.mp4 out.mp4 --ranges 0 2.8 [t0 t1 ...] [--strength 1.0] [--check sheet.png]

Built for tripod footage where the head touches the top edge (only the nose,
mouth, beard and chin are in frame), so it tracks the face with the pose
model's nose and mouth corners (~/.cache/omar/pose_landmarker_full.task)
instead of a face mesh, which needs the eyes. Points are smoothed over time,
then a few spots are moved by a small fraction of the mouth width and the
image is bent around them with a smooth displacement field (cv2.remap):
  - nose wings a little wider, nose tip a little lower
  - lips a little fuller, mouth a touch wider
  - lower jaw a little wider, chin a little longer
Anchors around the face keep the shirt, hair and background still. Only the
given time ranges (front views) are changed: on back views the pose model
invents a face on the back of the head. The change fades in/out over 6 frames
at range edges. Real pixels only (no generated texture), so grain and light
stay those of the camera. Video re-encoded libx264 crf 17, same fps; no audio.
"""
import argparse, os, subprocess, sys
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("out")
ap.add_argument("--ranges", type=float, nargs="+", required=True)
ap.add_argument("--strength", type=float, default=1.0)
ap.add_argument("--check")
a = ap.parse_args()
rng = list(zip(a.ranges[::2], a.ranges[1::2]))

import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
pl = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=os.path.expanduser("~/.cache/omar/pose_landmarker_full.task")),
    running_mode=vision.RunningMode.VIDEO))

cap = cv2.VideoCapture(a.inp)
fps = cap.get(cv2.CAP_PROP_FPS) or 60
frames, pts = [], []
PAD = 300
k = 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    frames.append(f)
    t = k / fps
    p = None
    if any(t0 <= t < t1 for t0, t1 in rng):
        big = cv2.copyMakeBorder(f, PAD, 0, 0, 0, cv2.BORDER_REPLICATE)
        r = pl.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(big, cv2.COLOR_BGR2RGB)),
                                int(k * 1000 / fps))
        if r.pose_landmarks:
            L = r.pose_landmarks[0]
            p = np.array([[L[i].x * big.shape[1], L[i].y * big.shape[0] - PAD] for i in (0, 9, 10)], np.float32)
    pts.append(p)
    k += 1
H, W = frames[0].shape[:2]
n = len(frames)
found = np.array([p is not None for p in pts])
print("frames", n, "tracked", int(found.sum()), file=sys.stderr)

P = np.zeros((n, 3, 2), np.float32)
R = 4
for k in range(n):
    if found[k]:
        idx = [j for j in range(max(0, k - R), min(n, k + R + 1)) if found[j]]
        P[k] = np.mean([pts[j] for j in idx], axis=0)
wgt = np.zeros(n, np.float32)
F = 6
miss = np.where(~found)[0]
for k in np.where(found)[0]:
    d = np.min(np.abs(miss - k)) if len(miss) else F + 1
    wgt[k] = min(1.0, d / F)


def field(p, w):
    nose, mL, mR = p
    mc = (mL + mR) / 2
    mw = max(np.linalg.norm(mL - mR), 1.0)
    up = (nose - mc) / (np.linalg.norm(nose - mc) + 1e-6)
    side = np.array([-up[1], up[0]], np.float32)
    if np.dot(mL - mR, side) < 0:
        side = -side
    s = a.strength * w
    C, D = [], []
    def add(pt, v):
        C.append(pt); D.append(v * s)
    for sg in (-1, 1):
        add(nose + sg * side * 0.33 * mw - up * 0.08 * mw, sg * side * 0.07 * mw)   # nose wings
        add(mc + sg * side * 0.52 * mw, sg * side * 0.04 * mw)                      # mouth corners
        add(mc + sg * side * 0.95 * mw - up * 0.65 * mw, sg * side * 0.07 * mw)     # lower jaw
    add(nose - up * 0.02 * mw, -up * 0.04 * mw)                                    # nose tip
    add(mc + up * 0.16 * mw, up * 0.03 * mw)                                       # upper lip
    add(mc - up * 0.20 * mw, -up * 0.05 * mw)                                      # lower lip
    add(mc - up * 1.05 * mw, -up * 0.07 * mw)                                      # chin
    for sg in (-1, 0, 1):
        add(nose + up * 0.7 * mw + sg * side * 0.6 * mw, np.zeros(2))              # above the nose stays
    for ang in np.linspace(0, 2 * np.pi, 16, endpoint=False):
        add(mc + np.array([np.cos(ang), np.sin(ang)], np.float32) * 2.1 * mw, np.zeros(2))
    return np.array(C, np.float32), np.array(D, np.float32), mw


def warp(img, p, w):
    ctrl, disp, mw = field(p, w)
    x0, y0 = np.floor(ctrl.min(0)).astype(int); x1, y1 = np.ceil(ctrl.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    if x1 - x0 < 8 or y1 - y0 < 8:
        return img
    sig = 0.45 * mw
    kern = lambda A, B: np.exp(-((A[:, None] - B[None]) ** 2).sum(-1) / (2 * sig * sig))
    coef = np.linalg.solve(kern(ctrl, ctrl) + 1e-3 * np.eye(len(ctrl)), disp)
    step = 3
    gx, gy = np.meshgrid(np.arange(x0, x1, step, dtype=np.float32), np.arange(y0, y1, step, dtype=np.float32))
    Dv = kern(np.stack([gx.ravel(), gy.ravel()], 1), ctrl) @ coef
    dx = cv2.resize(Dv[:, 0].reshape(gx.shape), (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
    dy = cv2.resize(Dv[:, 1].reshape(gx.shape), (x1 - x0, y1 - y0), interpolation=cv2.INTER_CUBIC)
    mx, my = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
    o = img.copy()
    o[y0:y1, x0:x1] = cv2.remap(img, (mx - dx).astype(np.float32), (my - dy).astype(np.float32), cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return o


ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                       "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "slow",
                       "-pix_fmt", "yuv420p", "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
samples = []
for k in range(n):
    o = warp(frames[k], P[k], wgt[k]) if wgt[k] > 0 else frames[k]
    ff.stdin.write(o.tobytes())
    if a.check and wgt[k] == 1 and k % 40 == 0:
        samples.append((frames[k], o, P[k]))
ff.stdin.close(); ff.wait()
if a.check and samples:
    rows = []
    for f, o, p in samples[:4]:
        mc = (p[1] + p[2]) / 2; mw = np.linalg.norm(p[1] - p[2]); r = int(2.0 * mw)
        y0, y1 = int(max(0, mc[1] - r)), int(min(H, mc[1] + r)); x0, x1 = int(max(0, mc[0] - r)), int(min(W, mc[0] + r))
        A = cv2.resize(f[y0:y1, x0:x1], (360, 360)); B = cv2.resize(o[y0:y1, x0:x1], (360, 360))
        rows.append(np.hstack([A, B]))
    cv2.imwrite(a.check, np.vstack(rows))
print("ok", a.out, n)
