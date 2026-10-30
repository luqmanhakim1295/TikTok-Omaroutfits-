"""Dress the hard cuts of a finished video (focus-mode editing styles).

usage: python3 tools/style_fx.py in.mp4 out.mp4 --cuts 2.0 3.5 ... [--flash] [--punch]

--flash: a quick white flash peaking on each cut (0.15 s).
--punch: the first 0.25 s after each cut zooms from 112 % back to 100 %
         (eased), like a punch-in beat.
Frames are streamed, so long 1080x1920 videos don't need to fit in memory.
"""
import argparse, json, subprocess
import numpy as np, cv2

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--cuts", type=float, nargs="+", required=True)
ap.add_argument("--flash", action="store_true")
ap.add_argument("--punch", action="store_true")
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
    if a.flash:
        d = min((abs(t - c) for c in a.cuts), default=9)
        if d < 0.075:
            k = 0.7 * (1 - d / 0.075)
            f = cv2.addWeighted(f, 1 - k, np.full_like(f, 255), k, 0)
    enc.stdin.write(np.ascontiguousarray(f).tobytes())
    n += 1
enc.stdin.close(); enc.wait(); dec.wait()
print(n, "frames")
