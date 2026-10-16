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

`output/omaroutfits_open_neck.mp4`: 15s, 9 different scenes alternating 2s and 1.5s, with motion and 0.25s transitions: crossed arms (full shirt), open-neck collar, hand on chest, back view, side collar, waist/hem, rolling sleeves, holding phone (medium), side view. From IMG_0266/0267/0269.

`output/omaroutfits_mount_fuji_cinematic.mp4`: "Cinematic OOTD" style (after a reference TikTok): 15s, 9 hard cuts of 2s/1.5s alternating wide and detail shots (front, chest logo, back, back-print close-up, rolling sleeves, hand on chest, side-back turn, chest logo from the side, hands on hips), muted film grade, "Cinematic OOTD" title, gentle 8% eased zoom-out whose widest frame stops at the mouth. From IMG_0275, IMG_0277 and IMG_0278.

`output/omaroutfits_olive_seersucker_cinematic.mp4`: same Cinematic OOTD recipe for the olive seersucker shirt: 15s, 9 hard cuts of 2s/1.5s (front, texture close-up, back, cuff button, rolling sleeves, front placket, crossed arms, hem and pocket, side-back turn), muted grade, title, gentle zoom-out framed to the mouth. From IMG_0253/0255/0256/0257/0259.

`output/omaroutfits_black_slacks.mp4`: same cut recipe for the black slacks but with no title and no colour grade: 15s, 9 hard cuts of 2s/1.5s (front, waist button, crossed legs and arms, front pleats, sitting cross-legged, side pocket, side view, elastic back waist, adjusting the waistband), gentle zoom-out. From IMG_0317/0318/0319.

`output/omaroutfits_beige_track_pants.mp4`: beige track pants, no title or colour grade: 15s, 9 hard cuts where full waist-to-hem shots get 2s and details 1.5s (front wide-leg, embroidered logo, side stripes close-up, side view, phone going into the side pocket, pulling the hem cord, gathered cuff, inner seam, front jogger fit), gentle zoom-out. From IMG_0356–0365.

`output/omaroutfits_khaki_ribbed_pants.mp4`: khaki ribbed wide pants, no title or colour grade: 15s, 9 hard cuts, full waist-to-hem shots 2s and details 1.5s (front centred, ribbed pocket texture, phone into pocket, back centred, back pocket with DENIM patch, hand in pocket, foot on stool, side waistband and cord, sitting cross-legged), gentle zoom-out. From IMG_0276 and IMG_0279.
