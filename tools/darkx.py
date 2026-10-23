import sys, subprocess, numpy as np
# usage: darkx.py clip t0 t1 y0 y1 [fps] [bg_t]  -> centre of dark (trouser) pixels in band y0..y1 (source px)
path=sys.argv[1]; t0,t1=float(sys.argv[2]),float(sys.argv[3]); y0,y1=int(sys.argv[4]),int(sys.argv[5])
fps=float(sys.argv[6]) if len(sys.argv)>6 else 4; W,H=540,960; k=2160/W
def grab(a,d,f):
    out=subprocess.run(["ffmpeg","-loglevel","error","-ss",str(a),"-t",str(d),"-i",path,"-an","-vf",f"fps={f},scale={W}:{H}","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True,check=True).stdout
    n=len(out)//(W*H); return np.frombuffer(out[:n*W*H],np.uint8).reshape(n,H,W)
bgdark=None
if len(sys.argv)>7:
    bg=np.median(grab(float(sys.argv[7]),1.5,4),axis=0); bgdark=bg<70
a,b=int(y0/k),int(y1/k)
for i,f in enumerate(grab(t0,t1-t0,fps)):
    m=f<55
    if bgdark is not None: m&=~bgdark
    m=m[a:b]; c=m.sum(0).astype(float)
    if c.sum()<200: print(f"{t0+i/fps:.2f} -"); continue
    cdf=np.cumsum(c)/c.sum(); L=np.searchsorted(cdf,.03)*k; R=np.searchsorted(cdf,.97)*k
    print(f"{t0+i/fps:.2f} {(L+R)/2:.0f} {L:.0f} {R:.0f}")
