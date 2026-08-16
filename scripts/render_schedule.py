#!/usr/bin/env python3
"""Render drafts/state.json as the SlabsHub schedule widget (PNG).

Usage: python3 scripts/render_schedule.py [out.png]
Colors: green=APPROVED/PUBLISHED, yellow=PENDING_APPROVAL, red=BLOCKED,
grey=SKIPPED/ON_HOLD. Slots whose publish_at has passed are marked overdue.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "drafts" / "state.json"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
IDT = timezone(timedelta(hours=3))

PLATFORM = {
    "instagram-feed": ("IG פיד", "#e1306c"),
    "instagram-story": ("IG סטורי", "#c13584"),
    "facebook-organic": ("FB אורגני", "#1877f2"),
    "facebook-ad": ("FB ממומן", "#5b6b8c"),
}

STATUS = {
    "PUBLISHED":        ("פורסם",   "#22c55e", "#0d2818"),
    "APPROVED":         ("מאושר",   "#4ade80", "#12301f"),
    "QUEUED":           ("בתור",    "#4ade80", "#12301f"),
    "PENDING_APPROVAL": ("ממתין לאישור", "#facc15", "#302708"),
    "ON_HOLD":          ("מוקפא",   "#94a3b8", "#1e242e"),
    "SKIPPED":          ("מדולג",   "#94a3b8", "#1e242e"),
    "BLOCKED":          ("חסום",    "#f87171", "#2e1414"),
}

ORDER = ["PENDING_APPROVAL", "BLOCKED", "APPROVED", "QUEUED", "PUBLISHED", "ON_HOLD", "SKIPPED"]


def fmt_date(iso):
    if not iso:
        return "—"
    dt = datetime.fromisoformat(iso).astimezone(IDT)
    days = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]
    return f"{days[dt.weekday()]} {dt.day:02d}/{dt.month:02d} · {dt:%H:%M}"


def build_html(state, now):
    counts = {}
    rows_html = []
    overdue_total = 0

    for camp in state["campaigns"]:
        posts = sorted(camp["posts"], key=lambda p: ORDER.index(p["status"]))
        post_rows = []
        for p in posts:
            st = p["status"]
            counts[st] = counts.get(st, 0) + 1
            label, color, bg = STATUS[st]
            plat_name, plat_color = PLATFORM.get(p["platform"], (p["platform"], "#64748b"))
            overdue = ""
            if p["publish_at"] and st in ("APPROVED", "QUEUED", "PENDING_APPROVAL"):
                if datetime.fromisoformat(p["publish_at"]) < now:
                    overdue = '<span class="overdue">חלף</span>'
                    overdue_total += 1
            blockers = ""
            if p.get("blockers"):
                blockers = '<span class="blockers">' + " · ".join(p["blockers"]) + "</span>"
            post_rows.append(f"""
            <div class="row" style="--accent:{color}">
              <div class="cell plat"><span class="pill" style="background:{plat_color}22;color:{plat_color};border-color:{plat_color}55">{plat_name}</span></div>
              <div class="cell label">{p['label']}{blockers}</div>
              <div class="cell when">{fmt_date(p['publish_at'])}{overdue}</div>
              <div class="cell status"><span class="badge" style="color:{color};background:{bg};border-color:{color}44">{label}</span></div>
            </div>""")

        rows_html.append(f"""
        <section class="camp">
          <header class="camp-head">
            <span class="emoji">{camp['emoji']}</span>
            <span class="ctitle">{camp['title']}</span>
            <span class="price">{camp['price']}</span>
            <span class="tag">{camp['tag']}</span>
          </header>
          {''.join(post_rows)}
        </section>""")

    def chip(st, cls):
        n = counts.get(st, 0)
        if not n:
            return ""
        return f'<span class="chip {cls}">{STATUS[st][0]} <b>{n}</b></span>'

    chips = (chip("PENDING_APPROVAL", "y") + chip("APPROVED", "g") + chip("PUBLISHED", "g")
             + chip("BLOCKED", "r") + chip("SKIPPED", "s") + chip("ON_HOLD", "s"))

    stale_days = (now.date() - datetime.fromisoformat(state["updated"]).date()).days
    banner = ""
    if stale_days > 2 or overdue_total:
        parts = []
        if stale_days > 2:
            parts.append(f"הקובץ עודכן לאחרונה ב־{datetime.fromisoformat(state['updated']):%d/%m} — {stale_days} ימים ללא עדכון")
        if overdue_total:
            parts.append(f"{overdue_total} סלוטים שזמנם חלף וסטטוסם לא עודכן")
        banner = f'<div class="banner">⚠️ {" · ".join(parts)}</div>'

    return f"""<meta charset="utf-8">
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#0b0d12; font-family:"DejaVu Sans",sans-serif; direction:rtl;
         color:#e6e9ef; padding:28px; width:1000px; }}
  .top {{ display:flex; align-items:baseline; gap:14px; margin-bottom:6px; }}
  h1 {{ font-size:26px; letter-spacing:-.4px; }}
  h1 span {{ color:#a78bfa; }}
  .date {{ color:#7c8598; font-size:14px; margin-right:auto; }}
  .chips {{ display:flex; gap:8px; margin:14px 0 6px; flex-wrap:wrap; }}
  .chip {{ font-size:13px; padding:5px 12px; border-radius:999px; border:1px solid; }}
  .chip b {{ font-size:14px; }}
  .chip.g {{ color:#4ade80; background:#12301f; border-color:#4ade8044; }}
  .chip.y {{ color:#facc15; background:#302708; border-color:#facc1544; }}
  .chip.r {{ color:#f87171; background:#2e1414; border-color:#f8717144; }}
  .chip.s {{ color:#94a3b8; background:#1e242e; border-color:#94a3b844; }}
  .banner {{ margin:14px 0 20px; padding:11px 16px; border-radius:10px; font-size:14px;
             background:#2e1f08; color:#fbbf24; border:1px solid #f59e0b44; }}
  .camp {{ background:#11141b; border:1px solid #1f2532; border-radius:14px;
           margin-bottom:14px; overflow:hidden; }}
  .camp-head {{ display:flex; align-items:center; gap:10px; padding:13px 18px;
                background:#151924; border-bottom:1px solid #1f2532; }}
  .emoji {{ font-size:19px; }}
  .ctitle {{ font-weight:bold; font-size:16px; white-space:nowrap; }}
  .price {{ font-size:14px; color:#a78bfa; background:#a78bfa18; padding:2px 10px;
            border-radius:6px; border:1px solid #a78bfa33; }}
  .tag {{ font-size:12.5px; color:#7c8598; margin-right:auto; white-space:nowrap;
          overflow:hidden; text-overflow:ellipsis; }}
  .row {{ display:grid; grid-template-columns:110px 1fr 210px 130px; align-items:center;
          gap:12px; padding:11px 18px; border-bottom:1px solid #171b24;
          border-right:3px solid var(--accent); }}
  .row:last-child {{ border-bottom:none; }}
  .pill {{ font-size:12px; padding:3px 10px; border-radius:6px; border:1px solid; display:inline-block; }}
  .label {{ font-size:14.5px; }}
  .blockers {{ display:block; font-size:12px; color:#7c8598; margin-top:3px; }}
  .when {{ font-size:13.5px; color:#9aa4b8; }}
  .overdue {{ font-size:11.5px; color:#fbbf24; background:#2e1f08; border:1px solid #f59e0b44;
              padding:1px 7px; border-radius:5px; margin-right:8px; }}
  .badge {{ font-size:13px; padding:4px 12px; border-radius:999px; border:1px solid;
            display:inline-block; font-weight:bold; }}
  .foot {{ color:#5c6479; font-size:12px; margin-top:14px; }}
</style>
<div class="top">
  <h1>SlabsHub · <span>לוח פרסום</span></h1>
  <div class="date">{now:%d/%m/%Y} · {now:%H:%M} IDT</div>
</div>
<div class="chips">{chips}</div>
{banner}
{''.join(rows_html)}
<div class="foot">מקור: drafts/state.json · עודכן {datetime.fromisoformat(state['updated']):%d/%m/%Y}</div>
<script>document.body.setAttribute("data-h", document.documentElement.scrollHeight);</script>
"""


def measure_height(html_path):
    dom = subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu",
        "--window-size=1000,800", "--virtual-time-budget=2000",
        "--dump-dom", str(html_path),
    ], capture_output=True, text=True).stdout
    m = re.search(r'data-h="(\d+)"', dom)
    return int(m.group(1)) + 28 if m else 1600


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reports" / "schedule.png"
    now = datetime.now(IDT)
    state = json.loads(STATE.read_text(encoding="utf-8"))
    html = build_html(state, now)
    tmp = Path("/tmp/claude-0/schedule.html")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(html, encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    # headless --screenshot captures the viewport only, so size the window to the
    # page: measure it once via --dump-dom on a probe that writes height into the DOM.
    height = measure_height(tmp)
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=2", f"--window-size=1000,{height}",
        f"--screenshot={out}", str(tmp),
    ], check=True, capture_output=True)
    print(out)


if __name__ == "__main__":
    main()
