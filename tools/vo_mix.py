"""Add a voice-over (and optional background music) to a finished video.

usage: python3 tools/vo_mix.py video.mp4 vo.mp3 out.mp4 plan.json [--music music.mp3]

plan.json:
{
  "segments": [[src_start, src_end, place_at, tempo], ...],  # VO phrases cut from vo.mp3
                                                            # (word times from Scribe) and
                                                            # placed on the cut they describe;
                                                            # tempo 1.0 = unchanged (keep <= 1.08)
  "music_start": 3.0,        # where in music.mp3 the bed starts
  "music_db": -10,           # music gain before ducking (bed ends ~10 dB under the VO)
  "fade_in": 0.3, "fade_out": 0.8,
  "lufs": -14
}

The video stream is copied untouched (1080x1920 60 fps stays as rendered) and
the output keeps the video's exact length. Audio: AAC 192 kbps 48 kHz stereo
(Zernio needs AAC >= 128 kbps). The music is ducked under the voice with a
sidechain compressor, then the whole mix is loudness-normalised.
"""
import json, subprocess, sys

args = sys.argv[1:]
music = None
if "--music" in args:
    i = args.index("--music"); music = args[i + 1]; del args[i:i + 2]
video, vo, out, plan = args
p = json.load(open(plan))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            video], capture_output=True, text=True, check=True).stdout)

inputs = ["-i", video, "-i", vo]
parts, labels = [], []
for k, (a, b, at, tempo) in enumerate(p["segments"]):
    f = (f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
         f"afade=t=in:d=0.02,afade=t=out:st={max(b - a - 0.04, 0):.3f}:d=0.04")
    if abs(tempo - 1) > 1e-3:
        f += f",atempo={tempo}"
    f += f",adelay={int(at * 1000)}|{int(at * 1000)}[s{k}]"
    parts.append(f); labels.append(f"[s{k}]")
parts.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,apad,atrim=0:{dur:.3f},"
             "loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,asplit=2[vo][key]")  # loudnorm outputs 192 kHz
if music:
    inputs += ["-i", music]
    ms = p.get("music_start", 0.0)
    fo = p.get("fade_out", 0.8)
    parts.append(f"[2:a]atrim={ms}:{ms + dur:.3f},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=stereo,"
                 f"volume={p.get('music_db', -10)}dB,afade=t=in:d={p.get('fade_in', 0.3)},"
                 f"afade=t=out:st={dur - fo:.3f}:d={fo}[bed]")
    parts.append("[bed][key]sidechaincompress=threshold=0.05:ratio=3:attack=20:release=350[duck]")
    parts.append("[vo][duck]amix=inputs=2:normalize=0[mix]")
    last = "mix"
else:
    parts.append("[key]anullsink"); last = "vo"
parts.append(f"[{last}]loudnorm=I={p.get('lufs', -14)}:TP=-1.5:LRA=9,aresample=48000,atrim=0:{dur:.3f}[a]")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts),
                "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-ac", "2", "-t", f"{dur:.3f}", "-movflags", "+faststart", out], check=True)
print("ok", out, round(dur, 2))
