"""Add the small "omaroutfits" watermark outside the garment (owner's order:
very small, 50 % opacity, only visible if you look for it).

usage: python3 tools/watermark.py in.mp4 out.mp4 [--text omaroutfits] [--size 26] [--opacity 0.5]
       [--spots '[["v",10,1000],null,["h",120,1000]]']

The person is found with the segmenter from stepscan.py on frames every
0.25 s. A few candidate spots on the background are scored by how often the
person (and so the garment) touches them, and the watermark goes in the
spot he never touches; spots under TikTok's own buttons and caption (right
edge, bottom) and its top bar are left out. Text colour follows the
background there: white on dark, black on light. Each
cut is placed on its own (close-ups leave no background in some spots), on
free background when there is any, else where the least garment shows.
Prints the spot per cut.

--spots: manual spot per cut (orientation "h"/"v", x, y in output px; null =
automatic). Use it when the segmenter misreads the garment: beige/neutral
trousers are often labelled skin, so the automatic spot lands on them. Check a
zoomed frame of every cut after.
"""
import argparse, json, os, subprocess, sys
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stepscan import segmenter
import mediapipe as mp

FONT = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--text", default="omaroutfits")
ap.add_argument("--size", type=int, default=24)
ap.add_argument("--opacity", type=float, default=0.5)
ap.add_argument("--spots", help="JSON list, one [o, x, y] or null per cut")
a = ap.parse_args()
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"

W, H = 1080, 1920
w, h = 270, 480
fps = 10
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.src, "-vf", f"fps={fps},scale={w}:{h}",
                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src],
                           capture_output=True, text=True).stdout)
# Brighten dark frames (graded / black garments) so the segmenter still
# finds the body: CLAHE on the lightness channel.
clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(4, 4))
def lift(f):
    lab = cv2.cvtColor(f, cv2.COLOR_RGB2LAB)
    lab[..., 0] = clahe.apply(lab[..., 0])
    return np.ascontiguousarray(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB))
with segmenter() as seg:
    cats = [seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=lift(f))
                        ).category_mask.numpy_view().reshape(h, w) for f in F]
def body(c):
    """His body only: the largest connected blob (racks of hanging clothes
    behind him are labelled clothes too, but they are separate blobs)."""
    m = (c > 0).astype(np.uint8)
    e = cv2.erode(m, np.ones((5, 5), np.uint8))   # break thin links to the racks
    n, lab, st, _ = cv2.connectedComponentsWithStats(e, 8)
    if n <= 1:
        return m
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return cv2.dilate((lab == i).astype(np.uint8), np.ones((5, 5), np.uint8)) & m
# Dark garments on dark racks can slip past the segmenter, so the pose
# skeleton (shoulders, elbows, wrists, hips, knees) adds the torso and limbs:
# their convex hull, widened, counts as garment too.
from mediapipe.tasks.python import vision, BaseOptions
pose_model = os.path.expanduser("~/.cache/omar/pose_landmarker_full.task")
hulls = []
if os.path.exists(pose_model):
    with vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=pose_model), num_poses=1)) as pl:
        for f in F:
            r = pl.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=lift(f)))
            m = np.zeros((h, w), np.uint8)
            if r.pose_landmarks:
                L = r.pose_landmarks[0]
                pts = np.array([[L[i].x * w, L[i].y * h] for i in (11, 12, 13, 14, 15, 16, 23, 24, 25, 26)
                                if L[i].visibility > 0.3], np.float32)
                hips = [L[i] for i in (23, 24) if L[i].visibility > 0.3]
                if hips:
                    pts = np.vstack([pts, [[hp.x * w, h - 1] for hp in hips]]) if len(pts) else pts
                if len(pts) >= 3:
                    cv2.fillConvexPoly(m, cv2.convexHull(pts.astype(np.float32)).astype(np.int32), 1)
                    m = cv2.dilate(m, np.ones((15, 15), np.uint8))
            hulls.append(m)
else:
    hulls = [np.zeros((h, w), np.uint8) for _ in F]
bodies = [body(c) | hm for c, hm in zip(cats, hulls)]
person = np.array([cv2.dilate(b, np.ones((5, 5), np.uint8)) for b in bodies])
clothes = np.array([cv2.dilate(((((c == 4) | (c == 5)) & (b > 0)) | (hm > 0)).astype(np.uint8),
                               np.ones((5, 5), np.uint8)) for c, b, hm in zip(cats, bodies, hulls)])

# Cuts: big jumps between consecutive frames.
g = F.astype(np.int16).mean(3)
diff = np.abs(np.diff(g, axis=0)).mean((1, 2))
thr = max(18.0, float(np.median(diff)) * 4)
bounds = [0] + [i + 1 for i, d in enumerate(diff) if d > thr] + [len(F)]
bounds = [b for i, b in enumerate(bounds) if i == 0 or b - bounds[i - 1] >= 3 or b == len(F)]

tw = int(a.size * 0.56 * len(a.text)) + 8   # rough text box in output px
th = int(a.size * 1.3)
xs = [18, 120, 300, 560, W - 18 - tw]
ys = list(range(170, 1700, 60))
# Leave out TikTok's own UI: buttons on the right below the middle, caption at the bottom.
spots = [("h", x, y, tw, th) for y in ys for x in xs if not (x > 700 and y > 800)]
# Vertical text along the left edge (and the right edge above the buttons):
# fits the thin strip of background beside the body in tight shots.
spots += [("v", 10, y, th, tw) for y in range(200, 1500, 60)]
spots += [("v", W - 10 - th, y, th, tw) for y in range(200, 700, 60)]

from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype(FONT, a.size)
tmp = os.path.join(os.path.dirname(os.path.abspath(a.dst)), ".wm_" + os.path.basename(a.dst))
os.makedirs(tmp, exist_ok=True)
pngs = {}
for col, rgb in (("white", (255, 255, 255)), ("black", (0, 0, 0))):
    bb = font.getbbox(a.text)
    img = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 6), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((2 - bb[0], 3 - bb[1]), a.text, font=font, fill=rgb + (int(255 * a.opacity),))
    for o, im in (("h", img), ("v", img.rotate(90, expand=True))):
        p = os.path.join(tmp, f"{o}_{col}.png"); im.save(p); pngs[(o, col)] = (p, im.size)

placed = []
for k in range(len(bounds) - 1):
    f0, f1 = bounds[k], bounds[k + 1]
    best = None
    for o, x, y, bw, bh in spots:
        x0, y0, x1, y1 = (int(v * w / W) for v in (x - 12, y - 12, x + bw + 12, y + bh + 12))
        x0, y0 = max(x0, 0), max(y0, 0)
        p = float(person[f0:f1, y0:y1, x0:x1].mean())
        c = float(clothes[f0:f1, y0:y1, x0:x1].mean())
        score = 3 * p + 8 * c + (0.01 if o == "v" else 0) + (0.02 if 300 <= x <= 600 else 0)   # any body part (the garment segment can miss a dark jacket) and the garment both count
        if best is None or score < best[0]:
            best = (score, o, x, y, p, c, float(F[f0:f1, y0:y1, x0:x1].mean()))
    _, o, x, y, p, c, lum = best
    manual = json.loads(a.spots) if a.spots else []
    if k < len(manual) and manual[k]:
        o, x, y = manual[k]
        bw, bh = (tw, th) if o == "h" else (th, tw)
        x0, y0, x1, y1 = (int(v * w / W) for v in (x, y, x + bw, y + bh))
        p = float(person[f0:f1, y0:y1, x0:x1].mean()); c = float(clothes[f0:f1, y0:y1, x0:x1].mean())
        lum = float(F[f0:f1, y0:y1, x0:x1].mean())
    colour = "black" if lum > 150 else "white"
    t0, t1 = f0 / fps, (f1 / fps if f1 < len(F) else dur + 1)
    placed.append({"t": [round(t0, 2), round(min(t1, dur), 2)], "o": o, "x": x, "y": y,
                   "person": round(p, 3), "garment": round(c, 3), "colour": colour})

inputs, chain, last = [], [], "0:v"
for n, pl in enumerate(placed):
    inputs += ["-i", pngs[(pl["o"], pl["colour"])][0]]
    out = f"v{n}"
    chain.append(f"[{last}][{n + 1}:v]overlay={pl['x']}:{pl['y']}:enable='between(t,{pl['t'][0]:.2f},"
                 f"{pl['t'][1] if pl['t'][1] < dur else dur + 1:.2f})'[{out}]")
    last = out
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.src, *inputs, "-filter_complex", ";".join(chain),
                "-map", f"[{last}]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", "-an", a.dst], check=True)
import shutil; shutil.rmtree(tmp, ignore_errors=True)
print(json.dumps(placed))
