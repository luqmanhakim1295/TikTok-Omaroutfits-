"""Add the "text behind subject" look to a finished video (owner's reference
from @newtstore.com): big mustard letters pop in behind the person, a torn
paper wipe and a glitch hit at chosen cuts.

usage: python3 tools/fx_style.py in.mp4 out.mp4 spec.json

spec.json:
{"texts": [{"start": 0.0, "end": 2.0, "lines": ["KNIT", "POLO"], "y": 0.30}],
 "tears": [2.0], "glitches": [7.0]}

texts: lines drawn behind the person (MediaPipe segmentation, see
stepscan.py), letters popping in one by one over the first 0.5 s; y is the
top of the text block as a fraction of the height. tears / glitches: times of
hard cuts in the input to dress with a torn-paper wipe / a glitch hit.
"""
import json, subprocess, sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stepscan import segmenter
import mediapipe as mp

FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
MUSTARD = (11, 138, 201)          # BGR of #C98A0B
SHADOW = (20, 40, 60)

src, dst, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
probe = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "stream=width,height,r_frame_rate", "-of", "json", src],
    capture_output=True, text=True).stdout)["streams"][0]
W, H = probe["width"], probe["height"]
num, den = map(int, probe["r_frame_rate"].split("/")); FPS = num / den

raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", src, "-f", "rawvideo",
                      "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
N = len(frames)


def text_layers(lines, y0):
    """One RGBA layer per letter, all the same size as the frame."""
    size = 400
    font = ImageFont.truetype(FONT, size)
    widest = max(font.getbbox(l)[2] - font.getbbox(l)[0] for l in lines)
    size = int(size * (W * 0.94) / widest)
    font = ImageFont.truetype(FONT, size)
    layers, y = [], int(y0 * H)
    for line in lines:
        bb = font.getbbox(line)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        for i, ch in enumerate(line):
            if ch == " ":
                continue
            img = Image.new("L", (W, H), 0)
            d = ImageDraw.Draw(img)
            cx = x + font.getlength(line[:i])
            d.text((cx, y - bb[1]), ch, font=font, fill=255)
            layers.append(np.array(img))
        y += int((bb[3] - bb[1]) * 1.08)
    return layers


def person_mask(seg, f):
    small = cv2.resize(f, (360, 640))
    m = seg.segment(mp.Image(image_format=mp.ImageFormat.SRGB,
                             data=np.ascontiguousarray(small[..., ::-1]))
                    ).category_mask.numpy_view() > 0
    m = cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)
    return cv2.GaussianBlur(m, (0, 0), 3)[..., None]


def pop(age, k):
    """Scale-in for letter k, age seconds into the text."""
    t = (age - k * 0.06) / 0.18
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    return 1 + 0.25 * np.sin(np.pi * t) * (1 - t)  # small overshoot


out = []
texts = [(s, text_layers(s["lines"], s.get("y", 0.3))) for s in spec.get("texts", [])]
with segmenter() as seg:
    for n in range(N):
        t = n / FPS
        f = frames[n].astype(np.float32)
        active = [(s, L) for s, L in texts if s["start"] <= t < s["end"]]
        if active:
            m = person_mask(seg, frames[n])
            bg = f.copy()
            for s, L in active:
                age = t - s["start"]
                for k, layer in enumerate(L):
                    sc = pop(age, k)
                    if sc == 0:
                        continue
                    a = layer.astype(np.float32) / 255
                    if abs(sc - 1) > 1e-3:
                        ys, xs = np.nonzero(layer)
                        c = (float(xs.mean()), float(ys.mean()))
                        M = cv2.getRotationMatrix2D(c, 0, sc)
                        a = cv2.warpAffine(a, M, (W, H))
                    sh = np.roll(a, (10, 8), (0, 1))[..., None]
                    bg = bg * (1 - 0.45 * sh) + np.array(SHADOW) * 0.45 * sh
                    a = a[..., None]
                    bg = bg * (1 - a) + np.array(MUSTARD) * a
            f = bg * (1 - m) + f * m
            if spec.get("outline", True):
                # Thin outline of the letters drawn over the person, so the
                # word still reads where the body hides the fill.
                for s, L in active:
                    age = t - s["start"]
                    for k, layer in enumerate(L):
                        if pop(age, k) < 1:
                            continue
                        e = cv2.morphologyEx(layer, cv2.MORPH_GRADIENT, np.ones((7, 7), np.uint8))
                        a = (e.astype(np.float32) / 255 * 0.9)[..., None] * m
                        f = f * (1 - a) + np.array(MUSTARD) * a
        out.append(np.clip(f, 0, 255).astype(np.uint8))

rng = np.random.default_rng(7)
for tc in spec.get("tears", []):
    c = int(round(tc * FPS)); half = int(0.12 * FPS)
    a_img, b_img = frames[c - 1], frames[c]
    edge = np.cumsum(rng.normal(0, 9, H)); edge -= edge.mean()
    for n in range(c - half, c + half):
        p = (n - (c - half)) / (2 * half)
        p = p * p * (3 - 2 * p)
        bx = (-0.15 + 1.3 * p) * W + edge
        xx = np.arange(W)[None, :]
        reveal = xx < bx[:, None]
        band = (xx >= bx[:, None]) & (xx < bx[:, None] + 26 + 10 * np.abs(np.sin(np.arange(H) / 7))[:, None])
        base = (out[n] if n < c else a_img).copy() if n < c else a_img.copy()
        nxt = out[n] if n >= c else b_img
        img = np.where(reveal[..., None], nxt, base)
        img[band] = (238, 240, 242)
        out[n] = img

for tc in spec.get("glitches", []):
    c = int(round(tc * FPS))
    for n in range(c - int(0.1 * FPS), c + int(0.12 * FPS)):
        if not 0 <= n < N:
            continue
        f = out[n].copy()
        b, g, r = cv2.split(f)
        sh = int(rng.integers(12, 30))
        f = cv2.merge([np.roll(b, -sh, 1), g, np.roll(r, sh, 1)])
        for _ in range(6):
            y = int(rng.integers(0, H - 80)); h = int(rng.integers(20, 90))
            f[y:y + h] = np.roll(f[y:y + h], int(rng.integers(-80, 80)), 1)
        ghost = np.roll(out[n], int(rng.integers(60, 140)), 1)
        f = cv2.addWeighted(f, 0.75, ghost, 0.25, 0)
        if abs(n - c) <= 1:
            f = cv2.addWeighted(f, 0.4, np.full_like(f, 255), 0.6, 0)
        if n >= c:
            gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            f = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        out[n] = f

enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                        "-s", f"{W}x{H}", "-r", f"{num}/{den}", "-i", "-", "-c:v", "libx264",
                        "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
for f in out:
    enc.stdin.write(f.tobytes())
enc.stdin.close(); enc.wait()
