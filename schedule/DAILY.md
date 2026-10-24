# Daily production run (3 videos a day)

The owner's standing order: make TikTok videos from the raw-material library
one product at a time, alternating **Baju** and **Seluar**, each video from a
different product folder, **3 videos per day**. Each video goes to the
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
5. Send to TikTok drafts: confirm the raw GitHub URL
   (`https://raw.githubusercontent.com/luqmanhakim1295/TikTok-Omaroutfits-/<branch>/<path>`,
   the repo is public) answers 200/206, then
   `python3 tools/zernio_draft.py <url> "<caption>"` and check it ends
   `published` (= delivered to the inbox). The Zernio key comes from the
   environment's network secret for zernio.com. On an error, retry once; if
   it still fails, say so in the report and send the file in the chat only.
   Suggested caption for the owner to paste: under 5 words, casual
   Malay/English about the product (e.g. "Polo hijau, simple tapi kemas"),
   then 3 hashtags: #omaroutfits, one product tag, #ootdmalaysia. **No call
   to action** ("DM untuk order", "link in bio"...): sales go through the
   TikTok yellow basket. Never invent fabric, sizes or prices.
6. Update `queue.json`: append to `history`; `pointer[type] += 1` (when it
   reaches the end: back to 0 and `cycle[type] += 1`); flip `next_type`.
   Commit and push.

If a folder's footage cannot make a clean video (all blurred, off-centre or
showing belly/boxer), skip it: note it in `history` with `skipped: <reason>`,
advance the pointer, and take the next folder of the same type.

## Report

After the three videos, send all three files to the owner (SendUserFile) and
reply in Malay with a short table: video, folder, length, suggested caption
(in a code block, easy to copy) and whether the TikTok draft arrived. Remind him of his upload settings: High quality upload on, Allow
comment on, everything else (Duet, Stitch, branded/commercial content
label, AI label) off. Mention anything skipped.
