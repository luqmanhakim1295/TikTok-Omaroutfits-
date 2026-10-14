# TikTok-Omaroutfits-

Auto-edit outfit videos into one short TikTok (9:16, 1080x1920, max 15 seconds).

## What the script does

`edit_video.py`:
1. **Takes only the clear parts.** It scores every moment for sharpness and drops the blurry or shaky ones.
2. **Crops from the mouth down.** It finds the face and starts the frame at the mouth, so the face is hidden and the outfit is in focus.
3. **Keeps it to 15 seconds or less.** It picks the clearest cuts (about 2s on screen each, at most 2 from each video).
4. **Adds motion and transitions.** Each cut gets a slow camera move (zoom in, zoom out, pan) and cuts are joined with transitions (zoom, slide, blur, fade).

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
| `--segment` | 2.3 | Length of each cut in seconds, including the transition overlap (2.3 = ~2s on screen) |
| `--transition` | 0.3 | Transition length in seconds (0 = hard cuts) |
| `--no-motion` | off | Turn off the zoom/pan camera moves |
| `--per-video` | 2 | Maximum cuts taken from one video |
| `--min-quality` | 0.5 | How strict the blur filter is (raise it to drop more) |
| `--fallback-top` | 0 | When no face is detected: crop this fraction off the top (0 = full frame, suits close-ups) |
| `--crf` | 21 | Video quality (lower = sharper, bigger file) |
| `--cache` | – | JSON file to store the analysis, so a re-run is fast (4K analysis takes a while) |
| `--mouth-offset` | 0 | Moves the top of the crop: `0.03` = a bit lower, `-0.03` = a bit higher |
| `--music` | – | Audio file to play under the video |
| `--keep-audio` | off | Keep the original audio (only with `--transition 0`) |

If no face is detected (a close-up that is already below the chin), the full frame is used. For a mirror selfie where the phone covers the face, use `--fallback-top 0.22`.

## Result

`output/omaroutfits_open_neck.mp4`: 14.3s, 7 different scenes of ~2s each with motion and transitions (front full outfit, open-neck collar, waist/hem, side view, front buttons, shoulder and sleeve, hand on collar), from IMG_0266/0267/0269. Silent, so the trending sound can be added in the TikTok app.
