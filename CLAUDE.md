# Omaroutfits TikTok editing rules

These are the owner's standing rules, collected from their feedback. They
apply to every edit unless the owner says otherwise for that video. "Macam
biasa" / "cam biasa" means: follow all of these.

## Non-negotiables

1. **Whole-body / full-trouser shots must be centred.** The body sits on
   the vertical centre line of the 9:16 frame for the whole cut. Never judge
   by eye: measure with `edit_video.subject_center()` (background-difference
   against an empty stretch at the start of the tripod clip) and crop with
   `edit_video.centered_box()`. If centring would need a crop so tight it
   cuts the shoulders, pick a different, better-centred window instead.
   Verify on the rendered output with a centre line drawn on frames.
2. **Frame up to the mouth: no higher, and no lower.** The top edge sits at
   mouth level: never show the nose or eyes, at any point of the cut
   (including the start of the zoom-out), but don't crop the top down to the
   neck or shoulders either. On whole-body shots this competes with rule 1:
   first look for a window where the body is already centred; if the
   footage has none (tripod set off-centre), crop only as much as needed so
   the top stays at mouth/neck level, allowing the body up to ~3 % off
   centre (~30 px of 1080). Never cut the collar/neckline or shoulders to
   get a perfect centre. Check the top strip of the rendered frames.
2a. **Shirt/top videos: no need to show the feet.** For a shirt video, the
   "whole-body" cuts frame from the mouth down to about the knees
   (e.g. a 1518x2700 crop from 4K), centred on the torso: measure with
   `subject_center(..., rows=(0, 0.55))` so crossed legs don't pull the
   centre. This keeps the top at mouth level and the shirt dead centre
   with no compromise. Trouser videos still show waist to hem in full;
   there the area above the belt can be cropped freely to centre the legs.
2b. **If background differencing is unreliable** (shiny floor reflections,
   camera or set moved, no empty stretch), measure with
   `edit_video.garment_center()` instead (colour mask for cool-toned
   garments). Always confirm with centre lines on the rendered output.
3. **Only clear footage.** No blur or shake (use the sharpness analysis,
   then look at the frames; motion blur from a hand moving is acceptable,
   camera blur is not).
4. **15 seconds or less**, 1080x1920.
5. **No repeated scenes.** Every cut is a different shot or angle; don't
   put two similar shots back to back.

## Default recipe

- About 9 scenes, hard cuts, total 15 s.
- Full-body or full trousers (waist to hem) shots: **2 s**. Detail shots:
  **1.5 s**.
- Alternate wide and detail shots.
- Gentle zoom-out on every cut: motion `pull_soft` (8 %, eased). Not fast.
- **No text and no colour filter** by default (the "Cinematic OOTD" title
  and grade were only for specific requests).
- **No audio**; the owner adds a trending sound in TikTok.
- Good scenes the owner likes: crossed arms (show the whole shirt), phone
  going into a pocket, hand in pocket, back view, fabric texture, logos /
  patches, wide-leg vs jogger via hem cord.

## Workflow

1. Download the Drive folder (`gdown`), check for files already on disk.
2. Keyframe contact sheets every 2 s to catalogue shots.
3. Sharpness/face analysis (`analyse()` via a background job).
4. Pick windows; for whole-body cuts measure the subject centre (rule 1).
5. Render a check sheet (start/middle/end of each cut) and inspect it.
6. Render, then inspect the output: centre lines on whole-body cuts and
   the top strip on face cuts. Only then send the video.
