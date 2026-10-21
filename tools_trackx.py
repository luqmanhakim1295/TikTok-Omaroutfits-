"""Camera-tracking crop: print an ffmpeg crop-x expression (t = seconds into the cut)
that follows the subject. usage: trackx.py clip start length bg_time cw [r0 r1] [W]"""
import sys, subprocess, numpy as np, cv2
p, st, L, bg_t, cw = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
r0, r1 = (float(sys.argv[6]), float(sys.argv[7])) if len(sys.argv) > 7 else (0.3, 0.97)
W = int(sys.argv[8]) if len(sys.argv) > 8 else 2160
w, h, fps = 270, 480, 10
def frames(a, d, f):
    o = subprocess.run(["ffmpeg","-loglevel","error","-ss",f"{a}","-t",f"{d}","-i",p,"-an","-vf",f"fps={f},scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True,check=True).stdout
    n = len(o)//(w*h); return np.frombuffer(o[:n*w*h],np.uint8).reshape(n,h,w).astype(np.int16)
bg = np.median(frames(bg_t, 2, 5), axis=0)
cs = []
for f in frames(st, L, fps):
    m = np.abs(f-bg) > 28; m[:int(r0*h)] = 0; m[int(r1*h):] = 0
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((5,5),np.uint8))
    c = m.sum(0).astype(float)
    cdf = np.cumsum(c)/max(c.sum(),1)
    cs.append((np.searchsorted(cdf,.05)+np.searchsorted(cdf,.95))/2*W/w if c.sum() > 50 else np.nan)
cs = np.array(cs); idx = np.arange(len(cs)); ok = ~np.isnan(cs)
cs = np.interp(idx, idx[ok], cs[ok])
k = 7; pad = np.pad(cs, k//2, mode="edge"); sm = np.convolve(pad, np.ones(k)/k, mode="valid")  # smooth like a camera operator
xs = np.clip(sm - cw/2, 0, W - cw)
pts = [(i/fps, xs[i]) for i in range(0, len(xs), 3)] + [(L, xs[-1])]
expr = f"{pts[-1][1]:.0f}"
for (a, xa), (b, xb) in reversed(list(zip(pts, pts[1:]))):
    expr = f"if(lt(t,{b:.2f}),{xa:.0f}+({xb-xa:.0f})*(t-{a:.2f})/{b-a:.2f},{expr})"
print(expr)
print("centres", [int(x) for x in sm[::3]], file=sys.stderr)
