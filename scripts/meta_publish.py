"""
meta_publish.py — publishes APPROVED posts from drafts/state.json to Facebook / Instagram
through the Meta Graph API, at their scheduled time.

Usage:
  py scripts/meta_publish.py --due            # publish everything APPROVED whose publish_at is due (run by the scheduler)
  py scripts/meta_publish.py --dry-run --due  # show what would be published, publish nothing
  py scripts/meta_publish.py --post <draft-file-path>   # publish one specific approved post now

Rules baked in (do not relax):
  * Only posts with status APPROVED are ever published. PENDING_APPROVAL is never touched.
  * A post is "due" when now is within [publish_at - 5 min, publish_at + 90 min]. Older approved posts are
    reported as MISSED and left alone — a human decides what to do with them.
  * Media must have a public URL in the post's "hosted" field (Shopify CDN). No hosted URL → BLOCKED, nothing sent.
  * Every publish is recorded: state.json → PUBLISHED + permalink, and a record in published/.
"""
import argparse, json, os, re, sys, time, subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import truststore  # use the Windows certificate store (certifi fails on some CDNs on this machine)
truststore.inject_into_ssl()
import requests
from dotenv import load_dotenv

for _s in (sys.stdout, sys.stderr):  # Windows console defaults to cp1252; captions are Hebrew
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:  # noqa
        pass
ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "drafts" / "state.json"
LOG = ROOT / "published" / "meta-publish.log"
load_dotenv(ROOT / ".env")

TOKEN = os.getenv("META_PAGE_TOKEN")
PAGE_ID = os.getenv("META_PAGE_ID")
IG_ID = os.getenv("META_IG_USER_ID")
G = "https://graph.facebook.com/v21.0"
IL = timezone(timedelta(hours=3))  # IDT; publish_at values in state.json carry their own offset anyway


def log(msg):
    line = f"{datetime.now(IL).isoformat(timespec='seconds')} {msg}"
    print(line)
    LOG.parent.mkdir(exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def page_token():
    r = requests.get(f"{G}/{PAGE_ID}", params={"fields": "access_token", "access_token": TOKEN}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


def read_draft(path):
    text = (ROOT / path).read_text(encoding="utf-8")
    m = re.search(r"## Final copy\s*\n(.*?)\n## ", text, re.S)
    body = (m.group(1) if m else "").strip()
    caption = re.sub(r"\*\*האשטאגים:\*\*\s*", "", body)
    caption = re.sub(r"\*\*CTA:\*\*\s*", "", caption)
    caption = caption.replace("**", "").strip()
    link = None
    lm = re.search(r"## Link\s*\n(\S+)", text)
    if lm:
        link = lm.group(1).strip()
    assets = []
    am = re.search(r"## Asset\s*\n([^\n]+)", text)
    if am:
        assets = [a.strip() for a in am.group(1).split(",") if a.strip().lower().endswith((".jpg", ".jpeg", ".png", ".mp4"))]
    return caption, link, assets


def host_on_facebook(tok, local_path):
    """Upload a local image to the page as an UNPUBLISHED photo and return its public CDN URL.
    Used so Instagram (which only accepts public URLs) can fetch media that lives on this machine."""
    with open(ROOT / local_path, "rb") as fh:
        r = requests.post(f"{G}/{PAGE_ID}/photos", data={"published": "false", "access_token": tok},
                          files={"source": (Path(local_path).name, fh)}, timeout=120)
    if r.status_code >= 400:
        raise RuntimeError(f"FB host upload failed: {r.text[:300]}")
    pid = r.json()["id"]
    j = requests.get(f"{G}/{pid}", params={"fields": "images", "access_token": tok}, timeout=30).json()
    imgs = sorted(j.get("images", []), key=lambda i: i.get("width", 0), reverse=True)
    if not imgs:
        raise RuntimeError(f"FB host: no images for photo {pid}")
    return imgs[0]["source"]


def resolve_media(tok, post, assets):
    """Public URLs for the post's media: state.json 'hosted' first, else FB-hosted copies of the local files."""
    hosted = list(post.get("hosted") or [])
    if hosted:
        return hosted
    out = []
    for a in assets:
        if a.lower().endswith(".mp4"):
            raise RuntimeError(f"video {a} needs a hosted URL (Shopify CDN) — add it to the post's 'hosted' field")
        out.append(host_on_facebook(tok, a))
    if out:
        post["hosted"] = out
    return out


def fb_publish(tok, post, caption, link, assets):
    link_in_comment = "בתגובה" in caption and link
    if assets and assets[0].lower().endswith((".jpg", ".jpeg", ".png")):
        with open(ROOT / assets[0], "rb") as fh:
            r = requests.post(f"{G}/{PAGE_ID}/photos", data={"caption": caption, "access_token": tok},
                              files={"source": (Path(assets[0]).name, fh)}, timeout=120)
        if r.status_code >= 400:
            raise RuntimeError(f"FB photo post failed: {r.text[:300]}")
        pid = r.json().get("post_id") or r.json().get("id")
    else:
        r = requests.post(f"{G}/{PAGE_ID}/feed", data={"message": caption, "link": link, "access_token": tok}, timeout=60)
        if r.status_code >= 400:
            raise RuntimeError(f"FB feed post failed: {r.text[:300]}")
        pid = r.json()["id"]
    if link_in_comment:
        requests.post(f"{G}/{pid}/comments", data={"message": link, "access_token": tok}, timeout=60)
    return pid, f"https://www.facebook.com/{pid}"


def ig_wait(tok, cid):
    for _ in range(40):
        r = requests.get(f"{G}/{cid}", params={"fields": "status_code,status", "access_token": tok}, timeout=30).json()
        if r.get("status_code") == "FINISHED":
            return
        if r.get("status_code") == "ERROR":
            raise RuntimeError(f"IG container error: {r}")
        time.sleep(5)
    raise RuntimeError("IG container never finished")


def ig_publish_one(tok, params):
    params["access_token"] = tok
    r = requests.post(f"{G}/{IG_ID}/media", data=params, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"IG media create failed: {r.text}")
    cid = r.json()["id"]
    ig_wait(tok, cid)
    r = requests.post(f"{G}/{IG_ID}/media_publish", data={"creation_id": cid, "access_token": tok}, timeout=60)
    if r.status_code >= 400:
        raise RuntimeError(f"IG publish failed: {r.text}")
    mid = r.json()["id"]
    pl = requests.get(f"{G}/{mid}", params={"fields": "permalink", "access_token": tok}, timeout=30).json().get("permalink")
    return mid, pl


def ig_feed(tok, caption, hosted):
    return ig_publish_one(tok, {"image_url": hosted[0], "caption": caption})


def ig_story(tok, hosted):
    ids, pl = [], None
    for url in hosted:
        p = {"media_type": "STORIES"}
        if url.lower().split("?")[0].endswith(".mp4"):
            p["video_url"] = url
        else:
            p["image_url"] = url
        mid, pl = ig_publish_one(tok, p)
        ids.append(mid)
        time.sleep(3)
    return ",".join(ids), pl or f"https://www.instagram.com/stories/pokeslabshub/"


def publish(post, campaign, dry):
    caption, link, assets = read_draft(post["file"])
    plat = post["platform"]
    missing = [a for a in assets if not (ROOT / a).exists()]
    if missing:
        return "BLOCKED", f"asset missing on disk: {missing}"
    if plat in ("instagram-feed", "instagram-story") and not assets and not post.get("hosted"):
        return "BLOCKED", "no media for Instagram"
    if dry:
        return "DRY", f"{plat} · {len(assets)} local / {len(post.get('hosted') or [])} hosted · {caption[:60]!r}"
    tok = page_token()
    if plat == "facebook-organic":
        mid, permalink = fb_publish(tok, post, caption, link, assets)
    elif plat == "instagram-feed":
        mid, permalink = ig_feed(tok, caption, resolve_media(tok, post, assets))
    elif plat == "instagram-story":
        mid, permalink = ig_story(tok, resolve_media(tok, post, assets))
    else:
        return "SKIPPED", f"platform {plat} is not published by this script"
    post["status"] = "PUBLISHED"
    post["published_at"] = datetime.now(IL).isoformat(timespec="seconds")
    post["media_id"] = mid
    post["permalink"] = permalink
    rec = ROOT / "published" / (Path(post["file"]).stem + ".md")
    rec.write_text(
        f"# Published — {campaign['title']} · {post.get('label','')}\n\n- Platform: {plat}\n- Published: {post['published_at']}\n"
        f"- Media id: {mid}\n- Permalink: {permalink}\n- Draft: {post['file']}\n- Published by: scripts/meta_publish.py (scheduled)\n",
        encoding="utf-8",
    )
    return "PUBLISHED", permalink


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--due", action="store_true")
    ap.add_argument("--post")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-git", action="store_true")
    a = ap.parse_args()
    if not (TOKEN and PAGE_ID and IG_ID):
        sys.exit("META_* keys missing in .env")
    state = json.loads(STATE.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    changed = False
    for c in state["campaigns"]:
        for p in c["posts"]:
            if p.get("status") != "APPROVED" or not p.get("publish_at"):
                continue
            if a.post and p.get("file") != a.post:
                continue
            at = datetime.fromisoformat(p["publish_at"])
            if a.due and not (at - timedelta(minutes=5) <= now <= at + timedelta(minutes=90)):
                if now > at + timedelta(minutes=90):
                    log(f"MISSED  {p['file']} (was due {p['publish_at']})")
                continue
            if not (a.due or a.post):
                continue
            try:
                st, info = publish(p, c, a.dry_run)
            except Exception as e:  # noqa
                st, info = "ERROR", str(e)[:400]
            log(f"{st:9} {p['file']} · {info}")
            if st == "PUBLISHED":
                changed = True
    if changed:
        state["updated"] = datetime.now(IL).date().isoformat()
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
        if not a.no_git:
            subprocess.run(["git", "add", "drafts/state.json", "published/"], cwd=ROOT)
            subprocess.run(["git", "commit", "-q", "-m", "Published: scheduled Meta posts", "-m", "Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"], cwd=ROOT)
            subprocess.run(["git", "push", "-q"], cwd=ROOT)


if __name__ == "__main__":
    main()
