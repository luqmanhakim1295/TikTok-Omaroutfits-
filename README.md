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

`output/omaroutfits_twotone_windbreaker.mp4`: two-tone (black/olive) hooded windbreaker with motion effects matched to each shot, no text or grade: 11.5s, 6 cuts. Owner asked to show the face for this one, but only while looking down: full shots framed from the top of the head (zoom anchored to the top edge, `pull_top`) using windows where he looks down. Slow-motion (from the 60 fps footage) on the two action moments: the hook runs the full hood-up move until the head is covered (1.5x slow), and putting the jacket on (2x slow), gentle eased zoom-out on full shots, a fast "snap" zoom on the sleeve/side detail, and a horizontal whip blur on every cut. Order: hood-up hook, back view, side detail, front, putting on, hood up with hands in pockets; every full shot re-centred on the zip/spine and checked with centre lines. Soft handheld cuff close-ups (IMG_0182) left out; three Drive files (IMG_0180, IMG_0203-2, IMG_0205) could not be downloaded (Drive download quota). From IMG_0178-2/0179/0203.

`output/omaroutfits_beige_cargo_pants.mp4`: beige cargo pants, usual recipe (no text, no grade, gentle zoom-out): 12.5s, 7 hard cuts alternating full waist-to-hem shots (2s) and native close-ups (1.5s): front with hands in pockets, cargo pocket and zip, side, back pocket, three-quarter back, front pocket and pleat with cargo flap, front. This footage is 1080p (not 4K), so full shots use only light crops (no more than ~15% upscale) and windows where he is already near the centre; the straight back view was too far off-centre to crop without softening, so a three-quarter back shot and a back-pocket close-up are used instead. From IMG_0557/0558/0560.

`output/omaroutfits_khaki_ribbed_tracking.mp4`: khaki ribbed wide pants in a "camera tracking" style (owner's request), no text or grade: 10.5s, 6 cuts. On the tripod shots the crop pans to follow him like a camera operator (subject measured every 0.1 s by background difference, smoothed, turned into a moving crop with `tools_trackx.py`) with a slow push-in: walking into frame, uncrossing legs on the stool, turning from side to back. Native close-ups with their own handheld movement plus the same push: hand in the ribbed pocket, DENIM patch, back pocket. Every frame checked for belly or boxer (the stretches where the waistband showed were left out). From IMG_0276/0279.

`output/omaroutfits_olive_seersucker_tracking.mp4`: olive seersucker shirt in the camera-tracking style, weighted towards the rolled-up sleeves (owner's request), no text or grade. Redone after the owner's feedback (object not centred, full shots must show the whole outfit): 12s, 7 cuts. The three tripod shots (IMG_0261) are framed from the mouth to the bottom of the footage (the clip never shows the feet; it ends at the shin), so the whole shirt and trousers are in shot. The crop follows the shirt placket, measured by hand every 0.25 s, so it stays on the centre line while he moves (the camera-tracking pan), with a gentle zoom-out anchored to the top edge: rolling the sleeve up (hook), front with sleeves rolled, hands into pockets. Native close-ups between them: placket and collar, back yoke texture, medium front shot with rolled sleeves (IMG_0259), shoulder texture. A soft rolled-cuff close-up (Laplacian ~16) and a dark side shot were left out. From IMG_0256/0259/0261.

`output/omaroutfits_black_slacks_tracking.mp4`: black slacks redone in the same style as the olive seersucker tracking video (owner: "sama"), no text or grade: 12.5s, 7 hard cuts alternating full shots (2s) and details (1.5s). Full tripod shots (IMG_0317) run from the top of the footage (chest; the clip never shows the face) to the feet, centred on the legs: the leg silhouette is measured every 0.25 s (dark-trouser mask against the empty background) and the crop follows it (camera-tracking pan), with a gentle zoom-out anchored to the bottom edge (`pull_bottom`) so the shoes stay in shot. Order: front with hands in pockets, back elastic waist, side view, buttoning the waistband, back view, hand to the pocket, seated with crossed legs (IMG_0318, full width so the crossed knee is not cut; the clip ends at the ankle). Windows where the shirt lifted and showed the boxer band (IMG_0319 around 0:27) and the off-centre phone shot were left out. From IMG_0317/0318/0319.

`output/omaroutfits_black_longsleeve_shirt.mp4`: black long-sleeve shirt, re-edited from the open-neck footage (IMG_0266/0267/0269) with the current rules, no text or grade: 12.5s, 7 hard cuts alternating full shots (2s) and native close-ups (1.5s): crossed arms (hook), placket and buttons, back view, shoulder and sleeve, holding the phone, hand on the chest, rolling the sleeve. Full tripod shots are framed from the mouth (no nose or eyes) to the bottom of the footage (shins; the clip does not reach the feet). The crop follows the placket, measured every 0.25 s, so the shirt stays on the centre line, with a gentle zoom-out anchored to the top edge. A hand-in-pocket close-up was left out because the shirt sat at the edge of the frame. IMG_0268 was not used: its colour reads blue, not black.

`output/omaroutfits_moon_tee.mp4`: black tee with the "MOON" back print, usual recipe, no text, colour filter or audio (a moonlight grade was tried first, but the owner asked for the original colours): 12.5s, 7 hard cuts (print close-up hook, back view raising an arm, chest logo with hand, front holding the phone, back with hands clasped, front with hands in pockets, back view). Full tripod shots framed from the mouth (no nose) to the bottom of the footage, centred on the back print (purple colour mask) or the neckline, with the crop following the print on the arm-raise shot. From IMG_0402/0403/0405/0408.

`output/omaroutfits_mount_fuji_tee.mp4`: navy long-sleeve Mount Fuji tee, re-edited from the "Cinematic OOTD" footage with the usual recipe (no text, colour filter or audio): 12s, 7 hard cuts alternating native close-ups (1.5s) and full shots (2s): back-print close-up (hook), back view, chest logo, front holding the phone, back print medium shot, front with hands in pockets, hand on the chest logo. Full tripod shots run from the mouth/chin (no nose) to the bottom of the footage (shins), centred on the back print (teal colour mask) or the neckline. Out-of-focus stretches (IMG_0275 2:18-2:20) and soft close-ups were left out. From IMG_0275/0277/0278.

`output/omaroutfits_black_textured_polo.mp4`: black textured (herringbone-stripe) johnny-collar polo, usual recipe at 1080x1920 **60 fps** (owner's request; render with `edit_video.FPS = 60`), no text, colour filter or audio: 14s, 8 hard cuts alternating full shots (2s) and native close-ups (1.5s): front with hands in pockets (feet in shot), collar and placket, front holding the phone, top-down view of the whole shirt, back view, shoulder and sleeve texture, front adjusting the sleeve, upper back close-up. Full shots are centred on the collar point or the back collar (measured every 0.25-0.5 s) and framed from the mouth/chin with no nose; windows where he swayed off-centre were skipped. From IMG_0383/0384/0385/0392/0393.

`output/omaroutfits_dark_grey_trackpants_v2.mp4`: dark grey "E" track pants re-edited with the current rules at 1080x1920 60 fps, no text, colour filter or audio: 11s, 6 hard cuts: front with the drawstring (full waist to shoes), logo and side pocket, side view, hand in the pocket with logo, back view, front with the tee and crossed arms. Full shots are centred on the whole-trouser silhouette (dark mask from waist to hem, measured every 0.25 s) and keep the shoes in frame (crop taken from the empty floor below the feet). The IMG_0399 close-ups are blurred, and a logo close-up cut off at the frame edge was dropped. From IMG_0397/0398/0400.

## Daily production (output/daily/)

`output/daily/baju_advo-polo-green_c1.mp4`: Advo dark green polo, 12.5s, 7 cuts at 60 fps: front hands in pockets, shoulder close-up, crossed arms, hand on chest, back, polo on a hanger, holding the phone. Full shots framed from the mouth (no nose) to the bottom of the footage, centred on the placket/back. From IMG_0233/0235/0236.

`output/daily/seluar_baggy-corduroy-pants_c1.mp4`: khaki ribbed baggy corduroy pants, 14s, 8 cuts at 60 fps: front with drawstring, hand in the ribbed pocket, back, DENIM patch, front hands in pockets, phone into the pocket, seated cross-legged, hand in the back pocket. Full shots waist to shoes, centred by background difference. The stretch where the shirt was lifted at the waist (IMG_0279 0:38-0:48) was left out. From IMG_0276/0279.

`output/daily/baju_boru-japan_c1.mp4`: Boru Japan "Mount Fuji" long-sleeve tee, the same cut as `omaroutfits_mount_fuji_tee.mp4` re-rendered at 60 fps. From IMG_0275/0277/0278.

`output/daily/seluar_cargo-elgini_c1_v2.mp4`: beige Elgini cargo pants, 12.5s, 7 cuts at 60 fps, redone after owner feedback (v1 was off-centre and the people moved several times per cut). Every cut now has one movement only: front step with hands in pockets (tracked crop), phone into the front pocket, back view weight shift, hand into the side cargo pocket, side view hand into pocket, hand into the back pocket, front sway (IMG_0558). Body centre measured with person segmentation (`tools/stepscan.py`, `tools/segtrack.py`) and checked on the render: wide cuts average 541-551 px of 540. From IMG_0557/0558/0559/0560.

`output/daily/baju_boru-moon_c1.mp4`: Boru "MOON" tee, the cut of `omaroutfits_moon_tee.mp4` (original colours) re-rendered at 60 fps. From IMG_0402/0403/0405/0408.

`output/daily/seluar_cargo-grey_c1.mp4`: grey cargo pants, 10.5s, 6 cuts at 60 fps: hands on hips with belt, cargo pocket close-up, back, opening the cargo flap, crossed legs, hand on the front pocket. New windows versus the earlier grey cargo video. From IMG_0368/0369/0370.
