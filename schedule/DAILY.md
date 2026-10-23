# Daily production run (3 videos a day)

The owner's standing order: make TikTok videos from the raw-material library
one product at a time, alternating **Baju** and **Seluar**, each video from a
different product folder, **3 videos per day**, each scheduled to auto-post on
TikTok through Metricool. When a category runs out, start it again from its
first folder (next cycle) with different scenes. All rules in `CLAUDE.md`
apply to every video.

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
  path, scene windows used, Metricool uuid, publish time).

## Steps for each of the 3 videos

1. `type = next_type`, `folder = folders[type][pointer[type]]`.
2. Download the folder's files into a new, empty scratchpad directory:
   `gdown -q "https://drive.google.com/uc?id=<id>" -O <dir>/<name>` (retry up
   to 3 times; if Drive's quota blocks a file, carry on with the rest and say
   so in the report).
3. Edit following `CLAUDE.md` (workflow, non-negotiables, default recipe):
   - Contact sheets: `tools/sheet.sh`. Sharpness: `tools/sharpprof.py`,
     `tools/sharpwin.py`.
   - Measure centres before cropping: `tools/darkx.py` (dark garments vs.
     light background), `tools/colorx.py` (coloured prints), placket/collar
     strips every 0.25 s for shirts. Check every pick on a grid with a red
     centre line.
   - On cycle 2 and later, read this folder's earlier `history` entries and
     pick different windows and a different hook.
   - Render 1080x1920 **60 fps**, no text, no colour filter, no audio:
     `python3 tools/render_plan.py plan.json <rawdir> <out.mp4> --fps 60`.
   - Verify the render: check sheet with centre lines, top strip (no nose or
     eyes), Laplacian per cut, and no belly/boxer frames. Fix anything before
     going on.
4. Save as `output/daily/<type>_<folder-slug>_c<cycle>.mp4`, add a README
   line, commit, push. Delete the raw files to free disk.
5. Public URL (the repo is public):
   `https://raw.githubusercontent.com/luqmanhakim1295/TikTok-Omaroutfits-/<branch>/<path>`.
   Confirm it answers 200/206 before scheduling.
6. Schedule on Metricool (`createScheduledPost`): blogId `7603396`,
   timezone `Asia/Kuala_Lumpur`, provider `tiktok`.
   - Time: the same day, three slots at least 3 hours apart between 11:00 and
     23:00, taken from `getBestTimeToPostByNetwork` (tiktok, today). Fallback:
     12:30, 18:30, 21:30. Never a time in the past.
   - `info`: `autoPublish: true`, `draft: false`, `media: [<url>]`,
     `tiktokData: {title: <short product title>, privacyOption:
     "PUBLIC_TO_EVERYONE", commercialContentOwnBrand: true, autoAddMusic:
     false, isAigc: false}`, plus the other fields the tool requires.
   - Caption: under 5 words, casual Malay/English about the product (e.g.
     "Polo hijau, simple tapi kemas"), then 3 hashtags: #omaroutfits, one
     product tag, #ootdmalaysia. **No call to action** ("DM untuk order",
     "link in bio"...): sales go through the TikTok yellow basket. Never
     invent fabric, sizes or prices. Use the same short line as the
     TikTok `title`.
   - If Metricool returns an error, retry once with the fix it names; if it
     still fails, create it as a draft instead and report that.
7. Update `queue.json`: append to `history`; `pointer[type] += 1` (when it
   reaches the end: back to 0 and `cycle[type] += 1`); flip `next_type`.
   Commit and push.

If a folder's footage cannot make a clean video (all blurred, off-centre or
showing belly/boxer), skip it: note it in `history` with `skipped: <reason>`,
advance the pointer, and take the next folder of the same type.

## Report

After the three videos, send all three files to the owner (SendUserFile) and
reply in Malay with a short table: video, folder, length, scheduled time and
Metricool planner link. Mention anything skipped or left as a draft.
