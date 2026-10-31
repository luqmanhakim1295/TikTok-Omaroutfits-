# Daily production run (5 videos a day)

The owner's standing order: make TikTok videos from the raw-material library
one product at a time, alternating **Baju** and **Seluar**, each video from a
different product folder, **5 videos per day**. Each video goes to the
owner's TikTok drafts (Creator Inbox) through Zernio; he opens the draft in
the TikTok app, adds the trending sound and caption, and posts. Videos are
also sent in the chat. No Metricool. When a
category runs out, start it again from its first folder (next cycle) with
different scenes. All rules in `CLAUDE.md` apply to every video.

Library: https://drive.google.com/drive/folders/1bj6BKxjf1ypsHf_-tn7F9VR-YIJ78VJm
(`claude.mp4` in the library root is not raw material; ignore it.)

## State

`schedule/queue.json`:
- `folders.Baju` / `folders.Seluar`: product folders in order, each with its
  Drive file names and ids.
- `next_type`: category of the next video ("Baju" or "Seluar").
- `pointer.<type>`: index of the next folder in that category.
- `cycle.<type>`: current pass through that category (1 = first pass).
- `history`: one entry per finished video (date, type, folder, cycle, output
  path, scene windows used, suggested caption, Zernio post id).

## Setup (fresh container)

`pip install -r requirements.txt gdown matplotlib` and
`apt-get install -y libegl1 libgles2` (mediapipe segmentation for
`tools/stepscan.py` / `tools/segtrack.py`; the model downloads itself).

## Before the new videos

TikTok accepts at most **5 API drafts per rolling 24 h** for this account
(confirmed 2026-10-26..28: the 6th always fails with
`Spam_risk_too_many_pending_share`), and after a failure Zernio blocks the
account for 10+ minutes. So send at most 5 drafts per run, oldest first:
resend any `history` entry whose `delivery` starts with `draft_failed`
(same URL and caption), then the new videos, and stop sending at the first
failure; mark the rest `draft_failed` for the next run. Still make the 5
new videos every run. TikTok refuses new inbox drafts with
`Spam_risk_too_many_pending_share` while too many drafts sit unposted in
the owner's inbox: then record `draft_failed`, carry on, and tell the owner
to post or delete the old drafts.

## Focus mode (owner, 2026-10-31)

"Lepas ni cuba buat video yooka open collar dgn boru japan sahaja, ulang2 je
tapi video lain editing style." While `queue.json` has a `focus` block, ignore
`next_type`/`pointer`: every video comes from `focus.folders`, alternating
(`focus.next`), still 5 a day. Each video uses the next editing style for
that product (`focus.next_style[folder]`, wrapping round `focus.styles`), so
no two videos of the same product share a style until the list is used up.
Footage repeats are fine; reuse windows but vary order, hook and style. All
CLAUDE.md non-negotiables still apply (sharp, centred, four angles, top at
mouth level or lower, no belly/boxer, 60 fps, 15 s or less, no audio).

Styles:
- `classic`: wide/detail alternation, tracked crop and push-in (default recipe).
- `text_behind`: big English word behind him (`tools/fx_style.py`, texts only),
  e.g. "OPEN COLLAR", "MOUNT FUJI". Owner asked for English text, no closing CTA.
- `cinematic`: owner's reference (slow rainy-street tilt): long calm cuts with
  the `drift` motion, an opening tilt-up (crop y expression in the plan, e.g.
  trousers up to the print) and the moody warm grade
  (`--grade schedule/grades/moody_street.txt`). The only style with a colour grade.
- `torn_glitch`: no text; hard cuts dressed with torn-paper wipes and glitch
  hits (`tools/fx_style.py` tears/glitches).
- `fast_beat`: 12-16 short cuts of 0.6-0.8 s, same four angles plus details.
- `flash_punch`: white flash and a quick zoom punch at each cut
  (`tools/style_fx.py`).
- `split_screen`: opens with front and back side by side (two 540-wide
  tracked panels), then normal cuts.
- `detail_first`: opens on three close-ups, then reveals the four angles.
Name outputs `output/daily/baju_<slug>_f<n>_<style>.mp4` (n = running number
per product in focus mode) and record `style` in the history entry.

## Steps for each of the 5 videos

1. `type = next_type`, `folder = folders[type][pointer[type]]`.
2. Download the folder's files into a new, empty scratchpad directory:
   `gdown -q "https://drive.google.com/uc?id=<id>" -O <dir>/<name>` (retry up
   to 3 times; if Drive's quota blocks a file, carry on with the rest and say
   so in the report).
3. Edit following `CLAUDE.md` (workflow, non-negotiables, default recipe):
   - Contact sheets: `tools/sheet.sh`. Sharpness: `tools/sharpprof.py`,
     `tools/sharpwin.py`.
   - Pick windows with one movement only (CLAUDE.md rule 2d):
     `tools/stepscan.py clip t0 t1` lists windows with a single step/pose
     change and the crop centre to use.
   - Measure centres before cropping: `tools/stepscan.py` /
     `tools/segtrack.py` (person segmentation; use for beige or neutral
     garments and whenever background difference is unreliable),
     `tools/darkx.py` (dark garments vs.
     light background), `tools/colorx.py` (coloured prints), placket/collar
     strips every 0.25 s for shirts. Check every pick on a grid with a red
     centre line.
   - Four angles in every video (CLAUDE.md rule 2f): one sharp wide cut each
     of front, left side, right side and back. Mark the angles on the tripod
     contact sheet first and build the plan around them; report any angle
     the footage doesn't have.
   - On cycle 2 and later, read this folder's earlier `history` entries and
     pick different windows and a different hook.
   - Camera-tracking effect (CLAUDE.md rule 1a): every wide cut gets a
     tracked crop (`tools/segtrack.py clip start len cw > xN.txt`, then
     `"xN.txt"` as the 8th field of its plan entry) with `push_bottom`
     (trousers) or `push_top` (shirts); close-ups full frame with `push_soft`.
   - Render 1080x1920 **60 fps**, no text, no colour filter, no audio:
     `python3 tools/render_plan.py plan.json <rawdir> <out.mp4> --fps 60`.
   - Verify the render: check sheet with centre lines, top strip (no nose or
     eyes), Laplacian per cut, and no belly/boxer frames. Fix anything before
     going on.
4. Save as `output/daily/<type>_<folder-slug>_c<cycle>.mp4`, add a README
   line, commit, push. Delete the raw files to free disk.
5. Send to TikTok drafts: confirm the raw GitHub URL
   (`https://raw.githubusercontent.com/luqmanhakim1295/TikTok-Omaroutfits-/<branch>/<path>`,
   the repo is public) answers 200/206, then
   `python3 tools/zernio_draft.py <url> "<caption>"` and check it ends
   `published` (= delivered to the inbox). The Zernio key comes from the
   environment's network secret for zernio.com. On an error, retry once; if
   it still fails, say so in the report and send the file in the chat only.
   Caption (passed to zernio_draft.py and given in the report): **under 10
   words, no hashtags at all**, casual Malay/English about the product (e.g.
   "Polo hijau ni simple tapi nampak kemas"). TikTok ignores captions on
   inbox drafts (API limit), so the owner pastes it from the report. **No call
   to action** ("DM untuk order", "link in bio"...): sales go through the
   TikTok yellow basket. Never invent fabric, sizes or prices.
6. Update `queue.json`: append to `history`; `pointer[type] += 1` (when it
   reaches the end: back to 0 and `cycle[type] += 1`); flip `next_type`.
   Commit and push.

If a folder's footage cannot make a clean video (all blurred, off-centre or
showing belly/boxer), skip it: note it in `history` with `skipped: <reason>`,
advance the pointer, and take the next folder of the same type.

## Report

After the five videos, send all five files to the owner (SendUserFile) and
reply in Malay with a short table: video, folder, length, suggested caption
(in a code block, easy to copy) and whether the TikTok draft arrived. Remind him of his upload settings: High quality upload on, Allow
comment on, everything else (Duet, Stitch, branded/commercial content
label, AI label) off. Mention anything skipped.
