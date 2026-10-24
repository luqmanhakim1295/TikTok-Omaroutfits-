"""Send a finished video to the owner's TikTok drafts (Creator Inbox) via Zernio.

usage: python3 tools/zernio_draft.py <public-video-url> "<caption>" [--dry-run]

The Zernio API key is injected by the environment's network secret for
zernio.com (Authorization: Bearer ...), so it never appears here. TikTok
ignores the caption and settings on inbox drafts; the owner pastes the
caption and picks the sound in the app. Prints the Zernio post id and its
final status.
"""
import json, subprocess, sys, time

API = "https://zernio.com/api/v1"
ACCOUNT = "6adb115f0bd5cc901dada9b0"   # TikTok @omaroutfits


def call(method, path, body=None):
    cmd = ["curl", "-sS", "-m", "120", "-X", method, f"{API}{path}",
           "-H", "Content-Type: application/json"]
    if body is not None:
        cmd += ["--data", json.dumps(body)]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True, check=True).stdout)


url, caption = sys.argv[1], sys.argv[2]
body = {
    "content": caption,
    "mediaItems": [{"type": "video", "url": url}],
    "platforms": [{"platform": "tiktok", "accountId": ACCOUNT}],
    "publishNow": True,
    "tiktokSettings": {"draft": True, "privacyLevel": "PUBLIC_TO_EVERYONE",
                       "allowComment": True, "allowDuet": False, "allowStitch": False,
                       "contentPreviewConfirmed": True, "expressConsentGiven": True},
}
if "--dry-run" in sys.argv:
    body["dryRun"] = True
    print(json.dumps(call("POST", "/posts", body)))
    sys.exit()
post = call("POST", "/posts", body)["post"]
pid = post["_id"]
for _ in range(30):
    p = call("GET", f"/posts/{pid}").get("post", {})
    plats = [(x.get("status"), x.get("errorMessage") or x.get("error")) for x in p.get("platforms", [])]
    if p.get("status") not in ("publishing", "uploading", "scheduled", "pending"):
        break
    time.sleep(10)
print(pid, p.get("status"), plats)
