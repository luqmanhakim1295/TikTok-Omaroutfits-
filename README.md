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

`output/omaroutfits_teal_knit_top.mp4`: teal textured knit split-neck top, no title or colour grade: 15s, 9 hard cuts, full-body shots 2s and details 1.5s (front, top-down POV texture, split neckline, back, hand on chest, back shoulder, angled medium shot, neckline side view, crossed arms; all whole-body cuts measured and cropped to centre), gentle zoom-out framed below the mouth. From IMG_0386/0388/0389/0391-2.

`output/omaroutfits_teal_knit_top_v2.mp4`: second cut of the teal knit top with all-new scenes: holding phone, hands and cuffs close-up, top-down hem and loafers, side view, hand at the collar, upper back close-up, hands in pockets close-up, sleeve texture, open-hands pose. Whole-body cuts framed mouth to knee and centred on the torso; close-ups cropped from the 4K tripod clips.

`output/omaroutfits_grey_cargo_pants.mp4`: grey cargo pants, no title or colour grade: 12s, 7 hard cuts, full waist-to-hem shots 2s and details 1.5s (front, front and cargo pocket, phone into the cargo pocket, side, closing the pocket flap, hand into the front pocket, back), whole-body cuts measured by garment colour and cropped to centre; zoomed tripod crops removed because they looked broken. From IMG_0368/0369/0370.

`output/omaroutfits_dark_grey_trackpants.mp4`: dark grey track pants with the "E" logo, no title or colour grade: 12.5s, 7 hard cuts (front with drawstring, logo close-up, side, phone into the side pocket, front with the tee, hand in pocket with logo, back). Full waist-to-hem cuts measured and centred; only native close-ups used for details (the IMG_0399 close-ups had camera blur and were left out). From IMG_0397/0398/0400.

`output/omaroutfits_petronas_f1_jersey.mp4`: white F1-style team jersey (Petronas/Porsche Motorsport print), no title or colour grade: 14s, 8 hard cuts alternating full shots (2s) and native close-ups (1.5s): front with hands in pockets, Petronas chest logos, side with hand in pocket, Rapyd sleeve, back (PETRONAS DARKTRACE), collar trim and AK logo, other side holding the phone (Audi Sport sleeve), red/black side panel. Whole-body cuts framed mouth to knee and cropped to centre by background difference; gentle zoom-out. From IMG_0339/0342/0346.

`output/omaroutfits_elgini_grey_pants.mp4`: Elgini grey wide-leg pants, no title or colour grade: 14s, 8 hard cuts alternating full waist-to-hem shots (2s) and native close-ups (1.5s): front with hands in pockets, tying the drawstring, side with hand in pocket, phone going into the pocket, back, embroidered logo by the pocket, leg lift showing the stretch, elastic waistband. Full cuts measured by background difference and cropped to centre the legs. From IMG_0347/0350/0351/0352.

`output/omaroutfits_black_oversized_tee.mp4`: plain black oversized tee, no title or colour grade: 14s, 8 hard cuts alternating mouth-to-knee full shots (2s) and native close-ups (1.5s): crossed arms (the crop pans gently to follow him so he stays centred), ribbed collar, back, drop-shoulder sleeve, side with hand in pocket, holding the phone, hand on hip, crossed arms from the side. Full cuts centred on the torso and checked with centre lines; top kept at mouth level. From IMG_0307/0308/0309.

`output/omaroutfits_brown_z_tee.mp4`: brown oversized tee with the "Z" patch, no title or colour grade: 14s, 8 hard cuts alternating mouth-to-knee full shots (2s) and native close-ups (1.5s): front with hands in pockets, Z patch close-up, side, ribbed collar, back, drop-shoulder seam, other side, holding the phone with the patch in view. Full cuts centred on the torso and checked with centre lines; top kept at mouth level (no nose). From IMG_0310/0315/0316.

`output/omaroutfits_blue_cord_shirt.mp4`: light blue corduroy long-sleeve shirt with chest pocket, no title or colour grade: 14s, 8 hard cuts alternating mouth-to-knee full shots (2s) and native close-ups (1.5s): crossed arms, chest pocket and rib texture, side with hand in pocket, rolled sleeve, back, curved hem and placket, hands in pockets, buttons and collar. Full cuts measured by garment colour, fine-tuned with centre lines; side cut cropped below the face so the nose never shows. From IMG_0301/0302/0303/0304/0306.

`output/omaroutfits_black_camp_shirt.mp4`: black camp-collar shirt, cut in the style of the owner's "Casual boleh, formal pun boleh" reference (without its text): 11.1s, 7 hard cuts timed like the reference (1.3/1.0/0.8/1.6/1.8/2.6/2.0s), static framing, one directional-blur whip between the last detail and the first full shot. Open collar hook, button placket, wider back-shoulder shot showing the yoke seam and sleeve (smooth fabric), then full shots (feet to mouth): turning, back, hands in pockets, smoothing the shirt front. Full shots centred and checked with centre lines; top at mouth level. From IMG_0271/0272/0300.

`output/omaroutfits_cream_pleated_pants.mp4`: cream wide-leg pleated trousers, usual recipe (no text, no grade, gentle zoom-out): 11s, 6 hard cuts: crossed legs standing, front pocket and pleat with hand into the pocket, sitting cross-legged, side seam and pocket, back, side step. Every close-up where the shirt was lifted (belly or boxer showing) or the camera was soft was removed; only sharp, clean close-ups kept. Full cuts measured and centred on the legs, checked with centre lines. From IMG_0262/0263/0264/0265.

`output/omaroutfits_green_polo.mp4`: dark green polo, usual recipe (no text, no grade, gentle zoom-out): 14s, 8 hard cuts alternating mouth-to-knee full shots (2s) and native close-ups (1.5s): front, hand on chest with buttons and fabric, crossed arms, shoulder and sleeve, back, polo on a hanger, side, collar and placket. Full cuts centred on the torso (placket on the centre line) and checked with centre lines; tripod stretches with the light stand in frame avoided. From IMG_0233/0235/0236.

`output/omaroutfits_black_track_pants.mp4`: black track pants, usual recipe (no text, no grade, gentle zoom-out): 14s, 8 hard cuts alternating full waist-to-hem shots (2s) and sharp close-ups (1.5s): front with hands in pockets, elastic waistband and drawstring, side, phone into the pocket, back, fabric drape, three-quarter stance, hand into the side pocket. Only clear windows used (the blurred kick was dropped); every close-up checked frame by frame so no belly or boxer shows. From IMG_0238/0239/0240/0246.

`output/omaroutfits_petronas_f1_jersey_race.mp4`: F1-vibe cut of the Petronas jersey (owner asked for "vibe F1"), no text, no grade: 13s, 11 fast hard cuts (1s close-ups, 1.5s full shots) with a 14% "snap" zoom-out at the start of each cut (`snap` motion) and a horizontal whip blur across every cut like a car passing (`tools_whip.py`). Petronas chest, front, Rapyd sleeve, side, Audi Sport sleeve, back, Machina Drive chest, collar and AK logo, back close-up, side stripe, side with phone. Full shots centred, top at mouth level. From IMG_0339/0342/0346.

`output/omaroutfits_twotone_windbreaker.mp4`: two-tone (black/olive) hooded windbreaker with motion effects matched to each shot, no text or grade: 11.5s, 6 cuts. Owner asked to show the face for this one, but only while looking down: full shots framed from the top of the head (zoom anchored to the top edge, `pull_top`) using windows where he looks down. Slow-motion (half speed, from the 60 fps footage) on the two action moments (pulling the hood up, putting the jacket on), gentle eased zoom-out on full shots, a fast "snap" zoom on the sleeve/side detail, and a horizontal whip blur on every cut. Front, back, side detail, putting on, hood up with hands in pockets. Soft handheld cuff close-ups (IMG_0182) left out; three Drive files (IMG_0180, IMG_0203-2, IMG_0205) could not be downloaded (Drive download quota). From IMG_0178-2/0179/0203.
