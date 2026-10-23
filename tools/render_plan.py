"""Render a cut plan with edit_video.render.

usage: python3 tools/render_plan.py plan.json rawdir out.mp4 [--fps 60] [--grade FILE]

plan.json is a list of cuts:
  [clip, start, length, top, cx, ch, motion, optional x-expression file]
The crop is ch tall (9:16), centred on cx, starting at row `top`. When an
x-expression file is given (piecewise-linear ffmpeg expression in t), the
crop x follows it instead, for camera-tracking cuts.
"""
import argparse, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import edit_video as e

ap = argparse.ArgumentParser()
ap.add_argument("plan"); ap.add_argument("rawdir"); ap.add_argument("out")
ap.add_argument("--fps", type=int, default=60)
ap.add_argument("--grade", help="file holding an ffmpeg colour filter (default: none)")
a = ap.parse_args()
e.FPS = a.fps
base = os.path.dirname(os.path.abspath(a.plan))
segs, mots = [], []
for name, start, length, top, cx, ch, mot, *xe in json.load(open(a.plan)):
    path = os.path.join(a.rawdir, name); W, H, _ = e.probe(path)
    cw = int(ch * 9 / 16) // 2 * 2; ch = int(cw * 16 / 9) // 2 * 2
    x = max(0, min(cx - cw // 2, W - cw))
    if xe:
        x = "'" + open(os.path.join(base, xe[0])).read().strip() + "'"
    print(name, start, length, cw, ch, top, mot, "track" if xe else x)
    segs.append(({"path": path, "w": W, "h": H}, start, length, (x, top, cw, ch)))
    mots.append(mot)
grade = open(a.grade).read().strip() if a.grade else None
e.render(segs, a.out, None, False, transition=0, motions=mots, grade=grade)
