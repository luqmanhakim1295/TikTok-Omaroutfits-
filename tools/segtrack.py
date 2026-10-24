"""Camera-tracking crop from person segmentation (see stepscan.py).

usage: python3 tools/segtrack.py clip start length cw [--rows 0.35 0.95] [--fixed]

Prints an ffmpeg crop-x expression (t = seconds into the cut) that keeps the
body centre ((L5 + R95) / 2 of the mask in the `rows` band) on the centre line
of a crop `cw` wide, smoothed like a camera operator. With --fixed, prints the
single x that best centres the whole cut instead. The per-0.3 s centres go to
stderr so the drift can be checked.
"""
import argparse, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stepscan import person_masks
import edit_video as e

ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("start", type=float); ap.add_argument("length", type=float)
ap.add_argument("cw", type=int)
ap.add_argument("--rows", type=float, nargs=2, default=(0.35, 0.95))
ap.add_argument("--fixed", action="store_true")
a = ap.parse_args()

fps = 10
W, _, _ = e.probe(a.clip)
masks, k = person_masks(a.clip, a.start, a.start + a.length + 0.1, fps)
cs = []
for m in masks:
    h = m.shape[0]
    c = m[int(a.rows[0] * h):int(a.rows[1] * h)].sum(0).astype(float)
    cdf = np.cumsum(c) / max(c.sum(), 1)
    cs.append((np.searchsorted(cdf, .05) + np.searchsorted(cdf, .95)) / 2 * k if c.sum() > 300 else np.nan)
cs = np.array(cs); idx = np.arange(len(cs)); ok = ~np.isnan(cs)
cs = np.interp(idx, idx[ok], cs[ok])
sm = np.convolve(np.pad(cs, 3, mode="edge"), np.ones(7) / 7, mode="valid")
print("centres", [int(x) for x in sm[::3]], file=sys.stderr)
if a.fixed:
    c = (sm.max() + sm.min()) / 2
    print(int(np.clip(c - a.cw / 2, 0, W - a.cw)), file=sys.stdout)
    print(f"centre {c:.0f}, drift +-{(sm.max() - sm.min()) / 2:.0f}", file=sys.stderr)
    sys.exit()
xs = np.clip(sm - a.cw / 2, 0, W - a.cw)
pts = [(i / fps, xs[i]) for i in range(0, len(xs), 3)]
if pts[-1][0] < a.length:
    pts.append((a.length, xs[-1]))
expr = f"{pts[-1][1]:.0f}"
for (t0, x0), (t1, x1) in reversed(list(zip(pts, pts[1:]))):
    expr = f"if(lt(t,{t1:.2f}),{x0:.0f}+({x1 - x0:.0f})*(t-{t0:.2f})/{t1 - t0:.2f},{expr})"
print(expr)
