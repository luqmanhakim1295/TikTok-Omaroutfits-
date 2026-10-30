"""Dress the hard cuts of a finished video (focus-mode editing styles).

usage: python3 tools/style_fx.py in.mp4 out.mp4 --cuts 2.0 3.5 ... [--flash] [--punch]
       [--tears 2.0 ...] [--glitches 5.5 ...]

--flash: a quick white flash peaking on each cut (0.15 s).
--punch: the first 0.25 s after each cut zooms from 112 % back to 100 %
         (eased), like a punch-in beat.
--tears: torn-paper wipe across these cuts (0.24 s, white ragged edge).
--glitches: RGB split, sliced rows and a white hit on these cuts (0.22 s).
Frames are streamed, so long 1080x1920 videos don't need to fit in memory.
"""
import argparse, json, subprocess
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--cuts", type=float, nargs="+", required=True)
ap.add_argument("--flash", action="store_true")
ap.add_argument("--punch", action="store_true")
ap.add_argument("--tears", type=float, nargs="*", default=[])
ap.add_argument("--glitches", type=float, nargs="*", default=[])
a = ap.parse_args()

p = json.loads(subprocess.run(
    ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
     "stream=width,height,r_frame_rate", "-of", "json", a.src],
    capture_output=True, text=True).stdout)["streams"][0]
W, H = p["width"], p["height"]
num, den = map(int, p["r_frame_rate"].split("/")); fps = num / den

dec = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-i", a.src, "-f", "rawvideo",
                        "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
                        "-s", f"{W}x{H}", "-r", f"{num}/{den}", "-i", "-", "-c:v", "libx264",
                        "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", a.dst], stdin=subprocess.PIPE)


def frame_at(i):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", a.src, "-vf", f"select=eq(n\\,{i})",
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "bgr24", "-"],
                       capture_output=True).stdout
    return np.frombuffer(r, np.uint8).reshape(H, W, 3)


rng = np.random.default_rng(7)
half = int(0.12 * fps)
tears = {}
for tc in a.tears:
    c = int(round(tc * fps))
    edge = np.cumsum(rng.normal(0, 9, H)); edge -= edge.mean()
    tears[c] = (frame_at(c - 1), frame_at(c), edge)
gl = [int(round(t * fps)) for t in a.glitches]
xx = np.arange(W)[None, :]
n = 0
while True:
    buf = dec.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    t = n / fps
    if a.punch:
        since = [t - c for c in a.cuts if 0 <= t - c < 0.25]
        if since:
            u = since[0] / 0.25
            s = 1 + 0.12 * (1 - u) ** 2
            M = cv2.getRotationMatrix2D((W / 2, H / 2), 0, s)
            f = cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    for c, (old, new, edge) in tears.items():
        if c - half <= n < c + half:
            p_ = (n - (c - half)) / (2 * half); p_ = p_ * p_ * (3 - 2 * p_)
            bx = ((-0.15 + 1.3 * p_) * W + edge)[:, None]
            reveal = xx < bx
            band = (xx >= bx) & (xx < bx + 26 + 10 * np.abs(np.sin(np.arange(H) / 7))[:, None])
            f = np.where(reveal[..., None], new if n < c else f, old if n >= c else f)
            f = f.copy(); f[band] = (238, 240, 242)
    for c in gl:
        if c - int(0.1 * fps) <= n < c + int(0.12 * fps):
            g = f.copy(); b, gg, r = cv2.split(g); sh = int(rng.integers(12, 30))
            g = cv2.merge([np.roll(b, -sh, 1), gg, np.roll(r, sh, 1)])
            for _ in range(6):
                y = int(rng.integers(0, H - 80)); h = int(rng.integers(20, 90))
                g[y:y + h] = np.roll(g[y:y + h], int(rng.integers(-80, 80)), 1)
            g = cv2.addWeighted(g, 0.75, np.roll(f, int(rng.integers(60, 140)), 1), 0.25, 0)
            if abs(n - c) <= 1:
                g = cv2.addWeighted(g, 0.4, np.full_like(g, 255), 0.6, 0)
            f = g
    if a.flash:
        d = min((abs(t - c) for c in a.cuts), default=9)
        if d < 0.075:
            k = 0.7 * (1 - d / 0.075)
            f = cv2.addWeighted(f, 1 - k, np.full_like(f, 255), k, 0)
    enc.stdin.write(np.ascontiguousarray(f).tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(n, "frames")
