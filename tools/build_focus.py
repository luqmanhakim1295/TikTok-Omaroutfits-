"""Build a focus-mode shirt video from a cut list, framing every wide cut
from the mouth down and on the body's centre line (tools/shirtframe.py).

usage: python3 tools/build_focus.py spec.json rawdir out.mp4 workdir

spec.json:
{"style": "classic" | "flash_punch" | "torn_glitch" | "cinematic" | "fast_beat" | "text_behind" | "split_screen" | "detail_first",
 "tops": {"IMG_0275.MOV": 150},          # mouth-line row for back/side views per clip
 "ch": {"IMG_0275.MOV": 3400},           # crop height per clip (room to centre)
 "cuts": [["IMG_0275.MOV", 131.6, 2.0, "back"],   # optional 5th item: crop height for this cut, 6th: {"top": row, "cx": centre} overrides
          ["IMG_0278.MOV", 82.2, 1.5, "detail"], ...],
 "text": {...fx_style spec...},           # text_behind only
 "tilt": 640}                             # cinematic: tilt-up travel of the first cut (px)
views: front (mouth line from the pose fit), back / side (row from "tops",
torso-mask centre), detail (full frame). Writes the plan and x-expressions to
workdir, renders, then applies the style's post effect.
"""
import json, os, subprocess, sys

spec_path, raw, out, work = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__))
spec = json.load(open(spec_path))
style = spec["style"]
os.makedirs(work, exist_ok=True)
motion_wide = {"cinematic": "drift", "fast_beat": "snap"}.get(style, "push_top")
motion_det = {"cinematic": "drift"}.get(style, "push_soft")
plan, cuts_t, t = [], [], 0.0
for k, (clip, start, length, view, *over) in enumerate(spec["cuts"]):
    if view == "detail":
        # optional overrides: [.., "detail", ch, {"top": row}] to keep a face out
        o = dict(over[1]) if len(over) > 1 else {}
        plan.append([clip, start, length, o.get("top", 0), 1080, over[0] if over else 3840, motion_det])
    else:
        xe = os.path.join(work, f"x{k}.txt")
        cmd = [sys.executable, os.path.join(here, "shirtframe.py"), os.path.join(raw, clip),
               str(start), str(length), xe, "--ch", str(over[0] if over else spec["ch"][clip])]
        o = dict(over[1]) if len(over) > 1 else {}
        top_row = o.get("top", spec["tops"][clip])
        cmd += (["--noface"] if view != "front" else []) + ["--top", str(top_row)]
        if "cx" in o:
            cmd += ["--cx", str(o["cx"])]
        r = json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip().splitlines()[-1])
        print(k, clip, start, view, r)
        top = r["top"]
        if style == "cinematic" and k == 0:
            travel = spec.get("tilt", 600)
            top = f"'{top + travel}-{travel}*pow(min(t/{length},1),2)*(3-2*min(t/{length},1))'"
        plan.append([clip, start, length, top, 1080, r["ch"], motion_wide, os.path.basename(xe)])
    t += length
    cuts_t.append(round(t, 3))
cuts_t = cuts_t[:-1]
pj = os.path.join(work, "plan.json")
json.dump(plan, open(pj, "w"), indent=1)
base = os.path.join(work, "base.mp4")
cmd = [sys.executable, os.path.join(here, "render_plan.py"), pj, raw, base, "--fps", "60"]
if style == "cinematic":
    cmd += ["--grade", spec.get("grade", "schedule/grades/moody_street_dark.txt")]
subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
fx = [sys.executable, os.path.join(here, "style_fx.py"), base, out, "--cuts", *map(str, cuts_t)]
if style == "flash_punch":
    subprocess.run(fx + ["--flash", "--punch"], check=True, stdout=subprocess.DEVNULL)
elif style == "torn_glitch":
    tears = [str(c) for i, c in enumerate(cuts_t) if i % 2 == 0]
    gl = [str(c) for i, c in enumerate(cuts_t) if i % 2 == 1]
    subprocess.run(fx + ["--tears", *tears, "--glitches", *gl], check=True, stdout=subprocess.DEVNULL)
elif style == "text_behind":
    sp = os.path.join(work, "text.json"); json.dump(spec["text"], open(sp, "w"))
    subprocess.run([sys.executable, os.path.join(here, "fx_style.py"), base, out, sp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
elif style == "split_screen":
    # Opener: the first two wide cuts (front, back) side by side for the
    # length of the first cut, then the rest of the cuts full screen.
    a, b = spec["cuts"][0][2], spec["cuts"][1][2]
    L = min(a, b)
    fc = (f"[0:v]trim=0:{L},setpts=PTS-STARTPTS,split=2[f1][f2];"
          f"[0:v]trim={a}:{a + L},setpts=PTS-STARTPTS,scale=520:924[bk];"
          f"[f1]scale=1080:1920,boxblur=30:3,eq=brightness=-0.12[bg];[f2]scale=520:924[fr];"
          f"[bg][fr]overlay=13:498[t1];[t1][bk]overlay=547:498,setsar=1[op];"
          f"[0:v]trim={a + b},setpts=PTS-STARTPTS[rest];[op][rest]concat=n=2:v=1[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", base, "-filter_complex", fc, "-map", "[v]",
                    "-r", "60", "-c:v", "libx264", "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", out], check=True)
    t = t - a - b + L
    cuts_t = [round(c - a - b + L, 3) for c in cuts_t[1:]]
else:
    os.replace(base, out)
print("cuts", [0.0] + cuts_t + [round(t, 3)])
