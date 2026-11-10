"""Short product-feature labels on a finished video (owner, 2026-11-12, after
TikTok Shop's "non-interactive content" violation: the video has to say what
the product does). One label per chosen cut, e.g. "Elastic waist",
"Deep side pockets": white bold text on a soft dark pill, fading in and out,
centred horizontally.

usage: python3 tools/feature_text.py in.mp4 out.mp4 labels.json

labels.json: [{"start": 2.0, "end": 3.5, "text": "Elastic waist", "y": 0.12}, ...]
y (optional, default 0.12) is the top of the pill as a fraction of the
height. Keep labels off the product: for trousers use the shirt area at the
top (y about 0.10-0.14); for shirts use the trouser area (y about 0.68-0.72),
above TikTok's caption. Only state what the footage shows (never invent
fabric, sizes or prices). Run it before tools/watermark.py.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
if not os.path.exists(FONT):
    FONT = "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
SIZE, PADX, PADY, FADE = 52, 34, 18, 0.18

src, dst, spec = sys.argv[1], sys.argv[2], json.load(open(sys.argv[3]))
W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", src],
                               capture_output=True, text=True).stdout.strip().split(","))
font = ImageFont.truetype(FONT, SIZE)
tmp = tempfile.mkdtemp(prefix=".ft_", dir=os.path.dirname(os.path.abspath(dst)))
inputs, chain, last = [], [], "0:v"
for n, lab in enumerate(spec):
    bb = font.getbbox(lab["text"])
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    img = Image.new("RGBA", (tw + 2 * PADX, th + 2 * PADY), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], radius=img.height // 2, fill=(15, 15, 15, 150))
    d.text((PADX - bb[0], PADY - bb[1]), lab["text"], font=font, fill=(255, 255, 255, 255))
    p = os.path.join(tmp, f"l{n}.png"); img.save(p)
    s, e = float(lab["start"]), float(lab["end"]); dur = e - s
    inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", p]
    x = (W - img.width) // 2
    y = int(lab.get("y", 0.12) * H)
    chain.append(f"[{n + 1}:v]format=rgba,fade=in:st=0:d={FADE}:alpha=1,"
                 f"fade=out:st={max(dur - FADE, 0):.3f}:d={FADE}:alpha=1,setpts=PTS+{s:.3f}/TB[l{n}]")
    chain.append(f"[{last}][l{n}]overlay={x}:{y}:eof_action=pass[v{n}]")
    last = f"v{n}"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, *inputs, "-filter_complex", ";".join(chain),
                "-map", f"[{last}]", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", "-an", dst], check=True)
import shutil; shutil.rmtree(tmp, ignore_errors=True)
print(len(spec), "labels")
