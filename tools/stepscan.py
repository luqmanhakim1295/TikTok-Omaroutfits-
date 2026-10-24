"""Find tripod windows with one movement and a steady, centrable body.

usage: python3 tools/stepscan.py clip t0 t1 [--rows 0.35 0.95] [--win 2.0] [--dump]

The person is found with MediaPipe's multiclass selfie segmenter (works where
background difference fails: auto exposure, shiny floor, beige trousers on a
beige floor). The model is downloaded to ~/.cache/omar on first use; mediapipe
needs libegl1 (apt-get install -y libegl1 libgles2).

Per frame (10 fps): body centre = (L5 + R95) / 2 of the mask inside the
`rows` band (default: legs), and motion = share of mask pixels that flipped
since the previous frame. A window is good when its motion has exactly one
burst (still -> one step or pose change -> still) and the body centre stays
put, so a fixed crop keeps it on the centre line for the whole cut. Prints
the best windows with the crop centre to use (source px) and the drift.
"""
import argparse, os, subprocess, sys, urllib.request
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import edit_video as e

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/image_segmenter/"
             "selfie_multiclass_256x256/float32/latest/selfie_multiclass_256x256.tflite")


def segmenter():
    import mediapipe as mp
    from mediapipe.tasks.python import vision, BaseOptions
    path = os.path.expanduser("~/.cache/omar/selfie_multiclass_256x256.tflite")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, path)
    return vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=BaseOptions(model_asset_path=path), output_category_mask=True))


def person_masks(clip, t0, t1, fps=10, w=270):
    W, H, _ = e.probe(clip)
    h = int(round(H * w / W / 2) * 2)
    out = subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-ss", f"{t0:.2f}", "-t", f"{t1 - t0:.2f}",
         "-i", clip, "-an", "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    n = len(out) // (w * h * 3)
    import mediapipe as mp
    F = np.frombuffer(out[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
    with segmenter() as seg:
        masks = [seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(f))
                             ).category_mask.numpy_view() > 0 for f in F]
    return masks, W / w


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("clip"); ap.add_argument("t0", type=float); ap.add_argument("t1", type=float)
    ap.add_argument("--rows", type=float, nargs=2, default=(0.35, 0.95))
    ap.add_argument("--win", type=float, default=2.0)
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--dump", action="store_true", help="print per-frame values")
    a = ap.parse_args()

    masks, k = person_masks(a.clip, a.t0, a.t1, a.fps)
    cx, mot, prev = [], [], None
    for m in masks:
        h = m.shape[0]
        band = m[int(a.rows[0] * h):int(a.rows[1] * h)]
        c = band.sum(0).astype(float)
        if c.sum() < 300:
            cx.append(np.nan); mot.append(np.nan); prev = None; continue
        cdf = np.cumsum(c) / c.sum()
        cx.append((np.searchsorted(cdf, .05) + np.searchsorted(cdf, .95)) / 2 * k)
        mot.append(0.0 if prev is None else float((band ^ prev).sum() / band.sum()))
        prev = band
    cx, mot = np.array(cx), np.array(mot)
    ts = a.t0 + np.arange(len(cx)) / a.fps
    if a.dump:
        for t, c, mo in zip(ts, cx, mot):
            print(f"{t:7.1f} {c:6.0f} {mo:.3f}")

    n, thr = int(a.win * a.fps), 0.04
    res = []
    for i in range(0, len(cx) - n, max(1, a.fps // 4)):
        c, mo = cx[i:i + n], mot[i:i + n]
        if np.isnan(c).any() or np.isnan(mo).any():
            continue
        sm = np.convolve(mo, np.ones(3) / 3, "same")
        act = sm > thr
        bursts = int(act[0]) + int(np.sum(act[1:] & ~act[:-1]))
        still_ends = sm[:3].mean() < thr and sm[-3:].mean() < thr
        res.append((bursts, (c.max() - c.min()) / 2, ts[i], (c.max() + c.min()) / 2,
                    still_ends, sm.max()))
    good = sorted((r for r in res if r[0] == 1), key=lambda r: (not r[4], r[1]))
    print("start  centre drift ends_still peak")
    picked = []
    for b, d, t, c, s, p in good:
        if any(abs(t - x) < a.win for x in picked):
            continue
        picked.append(t)
        print(f"{t:6.2f} {c:6.0f} {d:5.0f}  {s!s:5} {p:.2f}")
        if len(picked) >= 20:
            break
