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
1a. **Centred also while moving.** With camera tracking or any moving
   crop, the subject stays on the centre line for the whole cut, not just
   at the start. For shirts, measure the placket (button line) x every
   0.25 s from chest crops with a grid, because background difference is
   pulled off by the arms. Then make the crop x follow it (piecewise-linear
   expression, see `tools_trackx.py`).
2a. **Full-body shots show the whole outfit.** For shirts and tops too, a
   full-body cut runs from the mouth down to the feet (shirt, trousers,
   shoes), centred on the torso/placket. If the footage itself stops above
   the feet, frame from the mouth to the bottom of the footage and tell the
   owner. Pick windows where the body is already centred, because the
   full-height crop leaves almost no room to shift sideways. Trouser
   videos still show waist to hem in full; there the area above the belt
   can be cropped freely to centre the legs. (This replaces the old "mouth
   to knee" framing for shirts.)
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
6. **Every cut must show the product clearly.** The garment fills most of
   the frame and it's obvious what the cut is showing. Never a cut where
   floor, wall or background dominates (e.g. a low crop that is mostly
   floor and shoes, or a top-down POV that is half floor). If a crop only
   shows an unreadable patch of fabric, drop it and pick another shot.
6a. **Never show belly, boxer/underwear waistband or bare skin.** Waist
   close-ups where the shirt is lifted (tucking, adjusting the waistband)
   often show the boxer band or belly: check every frame of every cut and
   drop those parts. Never use shirtless or changing footage.
7. **No zoomed-in crops that look broken ("pecah").** Never make a detail
   shot by cropping a small region (e.g. 1080x1920) out of a wide tripod
   shot: the result is soft and blocky. Detail shots must come from real
   close-up footage. Light crops of whole-body shots for centring are fine.
   Check: Laplacian variance of each rendered cut; a crop far below the
   native close-ups (e.g. ~15 vs 800+) is broken and must go. Fewer scenes
   (shorter video) is better than a broken one.

## Default recipe

- 1080x1920 at **60 fps** (owner's request; `tools/render_plan.py --fps 60`).
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
  patches, wide-leg vs jogger via hem cord, rolled-up sleeves.

## Workflow

1. Download the Drive folder (`gdown`), check for files already on disk.
2. Keyframe contact sheets every 2 s to catalogue shots.
3. Sharpness/face analysis (`analyse()` via a background job).
4. Pick windows; for whole-body cuts measure the subject centre (rule 1).
5. Render a check sheet (start/middle/end of each cut) and inspect it.
6. Render, then inspect the output: centre lines on whole-body cuts and
   the top strip on face cuts. Only then send the video.

## Daily production

The owner's standing order is 3 videos a day from the raw-material library,
alternating Baju and Seluar. Each video goes to the owner's TikTok drafts
through Zernio (`tools/zernio_draft.py`); he adds the sound and posts. See `schedule/DAILY.md` for the steps and `schedule/queue.json`
for the state.
Suggested captions: under 5 words plus 3 hashtags, no call to action ("DM untuk
order" etc.): sales go through the TikTok yellow basket.
