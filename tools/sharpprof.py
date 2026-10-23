import sys, subprocess, numpy as np, cv2
# usage: sharpprof.py clip t0 t1 -> per-second min/mean Laplacian (540x960, 6 fps)
path=sys.argv[1]; t0,t1=float(sys.argv[2]),float(sys.argv[3]); w,h,fps=540,960,6
a=t0; line=[]
while a<t1:
    d=min(20,t1-a)
    out=subprocess.run(["ffmpeg","-loglevel","error","-ss",str(a),"-t",str(d),"-i",path,"-an","-vf",f"fps={fps},scale={w}:{h}","-f","rawvideo","-pix_fmt","gray","-"],capture_output=True,check=True).stdout
    n=len(out)//(w*h); F=np.frombuffer(out[:n*w*h],np.uint8).reshape(n,h,w)
    s=[cv2.Laplacian(f,cv2.CV_64F).var() for f in F]
    for j in range(0,n,fps):
        seg=s[j:j+fps]; line.append(f"{a+j/fps:.0f}:{min(seg):.0f}")
    a+=d
for i in range(0,len(line),10): print(" ".join(line[i:i+10]))
