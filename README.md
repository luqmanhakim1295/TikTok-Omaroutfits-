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

`output/daily/seluar_cargo-elgini_c1_v3.mp4`: same 7 cuts as v2 with the camera-tracking effect the owner asked for: every wide cut's crop follows his body (tracked, measured by segmentation) with an eased 8 % push-in anchored to the shoes, close-ups with a centred push-in. Wide cuts measure 544-553 px of 540.

`output/daily/baju_boru-moon_c1.mp4`: Boru "MOON" tee, the cut of `omaroutfits_moon_tee.mp4` (original colours) re-rendered at 60 fps. From IMG_0402/0403/0405/0408.

`output/daily/seluar_cargo-grey_c1.mp4`: grey cargo pants, 10.5s, 6 cuts at 60 fps: hands on hips with belt, cargo pocket close-up, back, opening the cargo flap, crossed legs, hand on the front pocket. New windows versus the earlier grey cargo video. From IMG_0368/0369/0370.

`output/daily/baju_f1-team_c1.mp4`: F1 team jersey, 11s, 6 cuts at 60 fps with the camera-tracking effect: front hands in pockets, Porsche/Machina Drive print close-up, side turn with hand into pocket, Petronas logo close-up, front pulling the hem, back (PETRONAS DARKTRACE). Close-ups chosen so no beard or face fills the frame. The tripod clip stops above the feet, so wide cuts run from the mouth to the bottom of the footage. From IMG_0339/0343.

`output/daily/seluar_elgini-grey_c1.mp4`: grey Elgini wide-leg pants, 10.5s, 6 cuts at 60 fps with the camera-tracking effect: front hand into pocket, drawstring close-up, side view, hand into pocket close-up, back, logo close-up. Barefoot stretches of the tripod clip left out; wide cuts waist to shoes, measured 535-553 px of 540. From IMG_0347/0350/0352.

`output/daily/baju_polyester-black_c1.mp4`: black polyester tee, 12.5s, 7 cuts at 60 fps with the camera-tracking effect: front hand on hip, phone close-up, front hem pull, neckline and fabric weave close-up, back, sleeve pinch close-up, front with phone. Top edge at mouth level. From IMG_0307/0308/0309.

`output/daily/seluar_elgini-relaxed-pants_c1.mp4`: dark grey Elgini relaxed pants, 11s, 6 cuts at 60 fps with the camera-tracking effect: front hands in pockets, hand into the pocket close-up, side view, logo close-up, back, crossed arms with the full trousers. One movement per cut; wide cuts measure 534-555 px of 540. Stretches where the shirt lifted (IMG_0398 ~0:09-0:14) left out. From IMG_0397/0398/0399/0400.

`output/daily/baju_sweat-shirt-v-neck-grey_c1.mp4`: textured v-neck sweatshirt (grey-green zigzag knit) with white trousers, 9s, 5 cuts at 60 fps with the camera-tracking effect: front, hand on the chest close-up, back, shoulder knit close-up, crossing the arms. Full shots from the chin to the shoes. Close-ups chosen without the face; a side view where the clip cuts off the feet was left out. From IMG_0386/0391/0391-2.

`output/daily/seluar_jogger-pants-black_c1.mp4`: black jogger pants, 11s, 6 cuts at 60 fps with the camera-tracking effect: front, phone into the pocket close-up, side step, hand into the pocket close-up, back, front hands in pockets. Waist to shoes on the wide cuts (534-550 px of 540). Two close-ups where lifting the shirt showed the boxer band (IMG_0239 ~0:47-0:49 and ~1:05) were left out. From IMG_0238/0239/0240.

`output/daily/baju_textured_c1.mp4`: olive seersucker ("textured") shirt, 10.5s, 6 cuts at 60 fps with the camera-tracking effect, new windows (IMG_0253 tripod, not used in the earlier olive videos): collar and seersucker texture close-up, front, shoulder texture close-up, side, back yoke close-up, back. The IMG_0253 tripod clip stops at the shin, so full shots run from the mouth to the bottom of the footage. Wide cuts measure 538-553 px of 540. From IMG_0253/0255/0256.

`output/daily/seluar_os-red-stripe_c1.mp4`: beige track pants with yellow and red side stripes (OS Red Stripe), 10.5s, 6 cuts at 60 fps with the camera-tracking effect: front, tying the hem cord close-up, side with the stripes, red stripe close-up, back, phone into the pocket close-up. Wide cuts measure 533-552 px of 540. Seated close-ups that show bare legs (IMG_0358 hem, IMG_0363) were left out. From IMG_0356/0357/0358/0359.

`output/daily/baju_vpg_c1.mp4`: black textured knit polo (VPG) with white trousers, 11s, 6 cuts at 60 fps with the camera-tracking effect: front hands in pockets, collar and herringbone knit close-up, side, back knit close-up, back, front. Full shots from the chin to the shoes. The back cut is tracked on the trousers because the dark clothes rack beside him pulled the segmentation off. From IMG_0383/0384/0392/0393.

`output/daily/seluar_yooka-black-slack_c1.mp4`: Yooka black slacks, 10.5s, 6 cuts at 60 fps with the camera-tracking effect, new windows (not the ones in the earlier black slacks video): front step, hand into the front pocket close-up, back, elastic back waist close-up, front hands in pockets, hand into the side pocket close-up. Waist to shoes on the wide cuts (519-538 px of 540); the barefoot part of IMG_0317 left out. From IMG_0317/0319.

`output/daily/baju_yooka-black-plain-long-sleeves_c1.mp4`: Yooka black plain long-sleeve shirt, 10.5s, 6 cuts at 60 fps with the camera-tracking effect, new windows (not those in the earlier black long-sleeve video): buttoning the cuff, placket and buttons close-up, back, shirt hem close-up, front hands in pockets, collar and shoulder close-up. Top at mouth level; the tripod clip stops at the shins, so full shots run to the bottom of the footage. Front cuts tracked on the trousers because the dark rack beside him pulled the segmentation off. From IMG_0266/0267/0269.

`output/daily/seluar_yooka-white-slack_c1.mp4`: Yooka white (cream) slacks, 9.5s, 5 cuts at 60 fps with the camera-tracking effect, new windows (not those in the earlier cream pleated video): front, phone into the pocket close-up, side with hand in pocket, back, seated. Waist to shoes on the standing cuts. Close-ups where a purple waistband showed under the lifted shirt (IMG_0263 ~0:44, ~0:57, ~1:14) and a soft side-seam close-up were left out. From IMG_0262/0263/0264/0265.

`output/daily/baju_yooka-corduroy-blue_c1.mp4`: Yooka light blue corduroy shirt, 9s, 5 cuts at 60 fps with the camera-tracking effect, new windows (not those in the earlier blue cord video): front with the phone, chest pocket and cord texture close-up, crossing the arms, curved hem close-up, hands on hips. Top at mouth level; the tripod clip stops at the thigh, so full shots run to the bottom of the footage. Three Drive files (IMG_0301, IMG_0302, IMG_0306) could not be downloaded (Drive quota), so the video uses IMG_0303/0304/0305 only.

`output/samples/baju_vpg_textstyle.mp4`: style test on the VPG video after the owner's reference (@newtstore.com): big mustard Inter Black text behind the person (MediaPipe segmentation) with a thin outline over the body so it stays readable, letters popping in ("KNIT POLO" on the front shot, "TEXTURED" on the side shot), torn-paper wipes into and out of the first close-up, and a glitch hit into the back view. No closing CTA (owner's choice). Made with `tools/fx_style.py` and `schedule/plans/baju_vpg_textstyle_fx.json`.

`output/daily/baju_yooka-corduroy-blue_c1_v2.mp4`: corduroy blue redone after the owner caught blurred cuts (the v1 wide cuts from IMG_0305 0:21 and 0:38 were out of focus, Laplacian ~10). 9s, 5 cuts, camera-tracking effect: crossing the arms, chest pocket close-up, hands in pockets, curved hem close-up, back. All wide cuts from the sharp IMG_0302 tripod clip (per-cut Laplacian 433-2087), top at mouth level.

`output/daily/seluar_os-red-stripe_c1_v2.mp4`: OS Red Stripe redone after the owner said v1 was too zoomed in. 9s, 5 cuts, camera-tracking effect: front, tying the hem cord close-up, side with the stripes, hand on the pocket close-up (waistband and yellow stripe in shot), back. Wide crops 3540 of 3840 px tall (v1: 3040), so the shirt hem, the whole waist and the shoes stay in frame through the push. A handheld front shot with a bare foot and a turning shot were left out.

`output/daily/seluar_baggy-corduroy-pants_c2.mp4`: baggy corduroy pants, cycle 2 (new windows), 8.5s, 5 cuts with the camera-tracking effect: front tying the drawstring, hand into the pocket by the DENIM patch, front hands in pockets, hand into the back pocket with the patch, hand in the side pocket. Wide crops 3600 of 3840. Left out: a blurred pocket close-up, a side view too far to the frame edge to centre, and a back view where the shirt lifted and showed skin. From IMG_0276/0279.

`output/daily/baju_yooka-open-collar-black_c1.mp4`: Yooka black open-collar (camp) shirt, 9s, 5 cuts with the camera-tracking effect, from the IMG_0274 tripod clip (not used in the earlier black camp shirt video): rolling the sleeve and crossing the arms, open collar and placket close-up, side with arms crossed, collar and shoulder close-up, back. Top at mouth level; the clip stops at the thigh, so full shots run to the bottom of the footage. From IMG_0271/0272/0274 (IMG_0300 not used: it contains a shirt-change stretch).

`output/daily/seluar_cargo-elgini_c2.mp4`: beige Elgini cargo pants, cycle 2 (new windows), 7.5s, 4 cuts with the camera-tracking effect: front with the MERDEKA tee, front and cargo pocket close-up, side with hand into the cargo pocket, front hands relaxed. Wide crops 1840 of 1920 tall, tracked on the legs. Short on purpose: the remaining sharp close-ups were either shirt-dominated or near repeats. From IMG_0557/0558/0559/0560.

`output/daily/baju_zeke-coffee_c1.mp4`: Zeke coffee-brown oversized tee, 7s, 4 cuts with the camera-tracking effect: front hands into pockets, Z patch and collar close-up, back, ribbed collar close-up. Short on purpose: most of this folder's handheld footage is soft or dark (Laplacian under 60), so only the sharp IMG_0315 close-ups and the IMG_0316 tripod clip were used.

`output/daily/seluar_cargo-grey_c2.mp4`: grey cargo pants, cycle 2 (new windows), 9s, 5 cuts with the camera-tracking effect: front hands in pockets, opening the cargo pocket flap close-up, back with hand into the back pocket, side pocket and cargo flap close-up, front hands on hips with the belt. Wide crops 3600 of 3840. From IMG_0368/0369/0370.

`output/daily/baju_zeke-windbreaker_c1.mp4`: Zeke two-tone windbreaker (black/olive), 7s, 4 cuts with the camera-tracking effect, new windows (not those in the earlier two-tone windbreaker video): front with hood up and hands in pockets, phone into the side pocket, back, side zip and cuff. Crops start below the mouth (he looks down under the hood). The sleeve close-ups in IMG_0182 were out of focus and left out. From IMG_0203-2/0205.

`output/daily/seluar_elgini-grey_c2.mp4`: grey Elgini wide-leg pants, cycle 2 (new windows), 8.5s, 5 cuts with the camera-tracking effect: back with hand to the back pocket, tying the drawstring close-up, front hands in pockets, phone into the side pocket close-up, hand in the pocket with the logo. Shod stretches of the tripod clip only (the rest is barefoot). From IMG_0347/0350/0351/0352.

`output/daily/baju_advo-polo-green_c2.mp4`: Advo green polo, cycle 2 (new windows), 7.5s, 4 cuts with the camera-tracking effect: crossed arms, collar and shoulder close-up, back turned to the side, hands into pockets. Top at mouth level; this tripod clip stops at the shin, so full shots run to the bottom of the footage. A side view too far right of centre was left out. From IMG_0233/0235.

`output/daily/seluar_elgini-relaxed-pants_c2.mp4`: Elgini relaxed pants, cycle 2 (new windows), 9s, 5 cuts with the camera-tracking effect: front with the drawstring, logo close-up, side step, pocket and logo close-up, front hands in pockets. Wide crops 3600 of 3840. From IMG_0397/0398/0400.

`output/daily/baju_boru-japan_c2.mp4`: Boru Mount Fuji long-sleeve tee, cycle 2 (new windows), 7s, 4 cuts with the camera-tracking effect: front pushing up the sleeves, chest logo close-up, back with the Mount Fuji print, back print close-up. Top at mouth level. From IMG_0275/0277/0278.

`output/daily/seluar_jogger-pants-black_c2.mp4`: Jogger pants black, cycle 2 (new windows), 7.3s, 4 cuts with the camera-tracking effect: front weight shift, phone going into the pocket (whole move, from the hand to fully inside), front with hands at the back, elastic waistband close-up. Wide crops 3600 of 3840. From IMG_0238/0239/0246.

`output/daily/baju_boru-moon_c2.mp4`: Boru "MOON" tee, cycle 2 (new windows), 6.75s, 4 cuts with the camera-tracking effect: back view with the MOON print (tracked), chest logo close-up, hands clasping behind the back, back print close-up. The front tripod footage is out of focus, so back views only. From IMG_0402/0403/0405/0408.

`output/daily/seluar_os-red-stripe_c2.mp4`: OS Red Stripe, cycle 2 (new windows), 11s, 6 cuts with the camera-tracking effect, all four angles (rule 2f): front turning to show the stripes (hems tied), embroidered logo close-up, right side, pocket lining close-up, left side, back (hems tied). Wide crops 3540 of 3840 (left side 3340 to keep him centred). From IMG_0356/0361/0365.

`output/daily/baju_f1-team_c2.mp4`: F1 team jersey, cycle 2 (new windows), 12.5s, 7 cuts with the camera-tracking effect, all four angles (rule 2f): front, Petronas/UEM print close-up, right side (Audi/Endless sleeve), Porsche/Machina Drive print close-up, left side (Rapyd sleeve), red side panel close-up, back (PETRONAS DARKTRACE). Top at mouth level or lower; the tripod clip stops above the feet. From IMG_0339/0342/0343/0346.

`output/daily/seluar_yooka-black-slack_c2.mp4`: Yooka black slacks, cycle 2 (new windows), 12.75s, 7 cuts with the camera-tracking effect, four angles (rule 2f): front with crossed arms, pleated front waist close-up, left side, back waist close-up, back, right side with hand into pocket, seated with legs crossed. The tripod clip has no right-side shot, so the right side is a handheld waist-to-shin shot. Wide crops 3540 of 3840 (seated 3340). From IMG_0317/0318/0319.

`output/daily/seluar_jogger-pants-black_c2_v2.mp4`: Jogger pants black c2 redone for rule 2f (front, left, right, back), 11.25s, 6 cuts with the camera-tracking effect: front weight shift, phone going into the pocket (whole move), left side, elastic waistband close-up, right side (crop 3300 tall to keep him centred, he stands left in that shot), back. From IMG_0238/0239/0246.

`output/daily/baju_boru-moon_c2_v2.mp4`: Boru "MOON" tee c2 redone for rule 2f (front, left, right, back), 12.75s, 7 cuts with the camera-tracking effect: front, chest logo close-up, left side, hands clasping behind the back, right side, back print close-up, back with the MOON print. The front and side shots read low on the Laplacian only because the plain black front has little texture (checked at full size: beard and logo are sharp). Top below the mouth on every cut. From IMG_0402/0403/0405/0408.

`output/daily/baju_polyester-black_c2.mp4`: black polyester tee, cycle 2 (new windows), 11s, 6 cuts with the camera-tracking effect, four angles (rule 2f): front, neckline stitching close-up, left side, crossed-arms sleeve close-up, right side, back. Top below the mouth. From IMG_0308/0309.

`output/daily/seluar_yooka-white-slack_c2.mp4`: Yooka white (cream) slacks, cycle 2 (new windows), 9.5s, 5 cuts with the camera-tracking effect, four angles (rule 2f): front crossing the legs, front pleat and pocket close-up, left side with hand in pocket, right side with phone, back. Wide crops 3540 of 3840. Waistband close-ups with the shirt lifted (purple band, IMG_0263 ~2:06-2:16) left out again. From IMG_0262/0263/0265.

`output/daily/baju_sweat-shirt-v-neck-grey_c2.mp4`: textured v-neck sweatshirt, cycle 2 (new windows), 9.5s, 5 cuts with the camera-tracking effect, four angles (rule 2f): front, v-neck knit close-up, right side with hand in pocket, left side, back. Top at chin level, no mouth. Close-ups that show the face (IMG_0386 ~0:16-0:36) left out. From IMG_0382/0386/0391-2.

`output/daily/seluar_baggy-corduroy-pants_c3.mp4`: baggy corduroy pants, cycle 3 (new windows), 9s, 5 cuts with the camera-tracking effect: front, leather patch close-up, left side profile, hand into the pocket close-up, back. The footage has no clear right-side shot (he only turns to his right once, in a blurred stretch), so rule 2f is short one angle here. Wide crops 3600 of 3840. From IMG_0276/0279.
