# usage: sharpwin.py clip t0 t1 [L] -> best L-second windows by minimum Laplacian sharpness
import sys, subprocess, numpy as np, cv2
path, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]); L = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
w, h, fps = 540, 960, 10
out = subprocess.run(["ffmpeg","-loglevel","error","-ss",f"{t0}","-t",f"{t1-t0}","-i",path,"-an","-vf",f"fps={fps},scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True,check=True).stdout
n=len(out)//(w*h); F=np.frombuffer(out[:n*w*h],np.uint8).reshape(n,h,w)
sh=np.array([cv2.Laplacian(f,cv2.CV_64F).var() for f in F])
mv=np.array([0]+[np.abs(F[i].astype(np.int16)-F[i-1]).mean() for i in range(1,n)])
k=int(L*fps); res=[]
for i in range(0,n-k):
    res.append((sh[i:i+k].min(), t0+i/fps, sh[i:i+k].mean(), mv[i+1:i+k].mean()))
res.sort(reverse=True)
print(path.split('/')[-1], f"{t0}-{t1}", "median sharp", round(float(np.median(sh))))
for r in res[:200:25]: print(f"  start {r[1]:.1f} minsharp {r[0]:.0f} mean {r[2]:.0f} motion {r[3]:.1f}")
