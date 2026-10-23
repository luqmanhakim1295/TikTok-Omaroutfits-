import sys, subprocess, numpy as np, cv2
# usage: colorx.py clip t0 t1 fps hue_lo hue_hi -> x centre (source px) of a saturated print colour (OpenCV hue 0-179)
path=sys.argv[1]; t0,t1=float(sys.argv[2]),float(sys.argv[3]); fps=float(sys.argv[4])
W,H=540,960; k=2160/W
out=subprocess.run(["ffmpeg","-loglevel","error","-ss",str(t0),"-t",str(t1-t0),"-i",path,"-an","-vf",f"fps={fps},scale={W}:{H}","-f","rawvideo","-pix_fmt","bgr24","-"],capture_output=True,check=True).stdout
n=len(out)//(W*H*3); F=np.frombuffer(out[:n*W*H*3],np.uint8).reshape(n,H,W,3)
for i,f in enumerate(F):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV); h,s,v=hsv[...,0],hsv[...,1],hsv[...,2]
    m=(h>=int(sys.argv[5]))&(h<=int(sys.argv[6]))&(s>70)&(v>70)
    ys,xs=np.nonzero(m)
    if len(xs)<150: print(f"{t0+i/fps:.2f} -"); continue
    print(f"{t0+i/fps:.2f} {np.median(xs)*k:.0f} {(np.percentile(xs,5)+np.percentile(xs,95))/2*k:.0f} {len(xs)} {np.median(ys)*k:.0f}")
