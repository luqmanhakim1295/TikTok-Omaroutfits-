"""Add F1-style whip blur at each cut: python3 whip.py in.mp4 out.mp4 t1 t2 ..."""
import subprocess, sys
src, dst, cuts = sys.argv[1], sys.argv[2], [float(t) for t in sys.argv[3:]]
soft = "+".join(f"between(t,{t-0.14:.3f},{t-0.07:.3f})+between(t,{t+0.07:.3f},{t+0.14:.3f})" for t in cuts)
hard = "+".join(f"between(t,{t-0.07:.3f},{t+0.07:.3f})" for t in cuts)
vf = f"dblur=angle=0:radius=14:enable='{soft}',dblur=angle=0:radius=45:enable='{hard}'"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", vf, "-c:v", "libx264", "-crf", "18",
                "-preset", "medium", "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", dst], check=True)
