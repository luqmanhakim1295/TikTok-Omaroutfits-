"""Quality checks for a rendered video (CLAUDE.md workflow step 6).

usage:
  python3 tools/qc.py sheet  video.mp4 out.png  c0 c1 ... cN   # start/middle/end of each cut, red centre line
  python3 tools/qc.py check  video.mp4 prefix   c0 c1 ... cN   # prints duration + median Laplacian per cut,
                                                               # writes prefix_tops.png (top strip of each cut)
  python3 tools/qc.py wmzoom workdir                           # 240x240 zooms of every watermark spot
                                                               # (reads workdir/wm.json and workdir/out.mp4,
                                                               # writes workdir/zoom.png)

c0..cN are the cut boundaries build_focus.py prints ("cuts [0.0, 2.0, ...]").
"""
import json, os, subprocess, sys, tempfile
import numpy as np, cv2


def frame(video, t, w=None):
    vf = ["-vf", f"scale={w}:-2"] if w else []
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{max(t, 0):.3f}", "-i", video, "-frames:v", "1",
                        *vf, "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return cv2.imdecode(np.frombuffer(r, np.uint8), cv2.IMREAD_COLOR)


def times(c0, c1):
    return [c0 + 0.05, (c0 + c1) / 2, c1 - 0.08]


def sheet(video, out, cuts):
    tiles = []
    for c0, c1 in zip(cuts, cuts[1:]):
        for t in times(c0, c1):
            f = frame(video, t, 150)
            cv2.line(f, (f.shape[1] // 2, 0), (f.shape[1] // 2, f.shape[0]), (0, 0, 255), 1)
            tiles.append(f)
    h, w = tiles[0].shape[:2]
    per = 9
    rows = []
    for i in range(0, len(tiles), per):
        row = tiles[i:i + per]
        row += [np.zeros((h, w, 3), np.uint8)] * (per - len(row))
        rows.append(np.hstack(row))
    cv2.imwrite(out, np.vstack(rows))


def check(video, prefix, cuts):
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                video], capture_output=True, text=True).stdout)
    laps, tops = [], []
    for c0, c1 in zip(cuts, cuts[1:]):
        vals = []
        for t in np.linspace(c0 + 0.1, c1 - 0.1, 5):
            g = cv2.cvtColor(frame(video, t), cv2.COLOR_BGR2GRAY)
            vals.append(cv2.Laplacian(g, cv2.CV_64F).var())
        laps.append(int(np.median(vals)))
        for t in (c0 + 0.05, c1 - 0.08):
            f = frame(video, t, 216)
            tops.append(f[: f.shape[0] // 8])
    row = [np.hstack(tops[i:i + 6]) for i in range(0, len(tops), 6)]
    wmax = max(r.shape[1] for r in row)
    row = [np.pad(r, ((0, 0), (0, wmax - r.shape[1]), (0, 0))) for r in row]
    cv2.imwrite(prefix + "_tops.png", np.vstack(row))
    print(round(dur, 2), laps)


def wmzoom(work):
    w = json.load(open(os.path.join(work, "wm.json")))
    video = os.path.join(work, "out.mp4")
    tiles = []
    for k, p in enumerate(w):
        bw, bh = (160, 34) if p["o"] == "h" else (34, 160)
        cx = max(0, min(1080 - 240, p["x"] + bw // 2 - 120))
        cy = max(0, min(1920 - 240, p["y"] + bh // 2 - 120))
        for t in times(*p["t"]):
            f = frame(video, t)[cy:cy + 240, cx:cx + 240].copy()
            cv2.putText(f, str(k), (4, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            tiles.append(f)
    per = 6
    rows = []
    for i in range(0, len(tiles), per):
        row = tiles[i:i + per]
        row += [np.zeros((240, 240, 3), np.uint8)] * (per - len(row))
        rows.append(np.hstack(row))
    cv2.imwrite(os.path.join(work, "zoom.png"), np.vstack(rows))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        sheet(sys.argv[2], sys.argv[3], [float(c) for c in sys.argv[4:]])
    elif cmd == "check":
        check(sys.argv[2], sys.argv[3], [float(c) for c in sys.argv[4:]])
    elif cmd == "wmzoom":
        wmzoom(sys.argv[2])
    else:
        sys.exit(__doc__)
