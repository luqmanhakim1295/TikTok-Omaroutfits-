# TikTok-Omaroutfits-

Auto-edit outfit videos into one short TikTok (9:16, 1080x1920, max 15 seconds).

## What the script does

`edit_video.py`:
1. **Takes only the clear parts.** It scores every moment for sharpness and drops the blurry or shaky ones.
2. **Crops from the mouth down.** It finds the face and starts the frame at the mouth, so the face is hidden and the outfit is in focus.
3. **Keeps it to 15 seconds or less.** It picks the clearest cuts (2.5s each by default, at most 2 from each video).

## How to use it

Requirements: Python 3, `ffmpeg`.

```bash
pip install -r requirements.txt

# put all the videos in one folder, e.g. raw/
python3 edit_video.py raw/ -o omar_outfit.mp4

# with music
python3 edit_video.py raw/ -o omar_outfit.mp4 --music lagu.mp3

# keep the original audio
python3 edit_video.py raw/ -o omar_outfit.mp4 --keep-audio
```

### Options

| Option | Default | What it does |
|---|---|---|
| `--max-seconds` | 15 | Maximum length of the final video |
| `--segment` | 2.5 | Length of each cut (seconds) |
| `--per-video` | 2 | Maximum cuts taken from one video |
| `--min-quality` | 0.5 | How strict the blur filter is (raise it to drop more) |
| `--mouth-offset` | 0 | Moves the top of the crop: `0.03` = a bit lower, `-0.03` = a bit higher |
| `--music` | – | Audio file to play under the video |
| `--keep-audio` | off | Keep the original audio |

If no face is detected (for example when a phone covers the face in a mirror selfie), the crop starts at 22% from the top. Adjust it with `--mouth-offset`.
