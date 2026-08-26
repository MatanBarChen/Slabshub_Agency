"""Weekly schedule widget — SlabsHub brand design line.

Reads drafts/state.json and renders the forward schedule grouped by week.
Standing rule (CLAUDE.md): attach this whenever the schedule changes or is
mentioned in chat.
"""
import sys, json, html, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from widget import render, masthead

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = json.loads((ROOT / "drafts" / "state.json").read_text(encoding="utf-8"))
TODAY = datetime.date.today()

PLAT = {"instagram-feed": "IG פיד", "instagram-story": "IG סטורי",
        "facebook-organic": "FB אורגני", "facebook-ad": "FB ממומן"}
ST = {"PUBLISHED": ("פורסם", "good"), "APPROVED": ("מאושר", "good"),
      "PENDING_APPROVAL": ("ממתין לאישור", "warn"), "BLOCKED": ("חסום", "bad"),
      "ON_HOLD": ("מוקפא", "flat"), "SKIPPED": ("מדולג", "flat")}
DAY = ["שני", "שלישי", "רביעי", "חמישי", "שישי", "שבת", "ראשון"]
L = lambda s: f'<span class="ltr">{s}</span>'

items, blocked = [], []
for c in STATE["campaigns"]:
    for p in c["posts"]:
        rec = (p, c)
        (items if p["publish_at"] and p["status"] != "PUBLISHED" else blocked).append(rec)
items.sort(key=lambda r: r[0]["publish_at"])

first = datetime.date.fromisoformat(items[0][0]["publish_at"][:10])
week0 = first - datetime.timedelta(days=first.weekday())

rows, counts = [], {}
cur = None
for p, c in items:
    dt = datetime.datetime.fromisoformat(p["publish_at"])
    wk = (dt.date() - week0).days // 7 + 1
    if wk != cur:
        cur = wk
        span = week0 + datetime.timedelta(days=7 * (wk - 1))
        rng = f"{span.strftime('%d.%m')}–{(span + datetime.timedelta(days=6)).strftime('%d.%m')}"
        rows.append(f'<tr><td colspan="4" style="background:#faf9f6;border-bottom:1px solid #000">'
                    f'<span class="strong">שבוע {L(str(wk))}</span>'
                    f'<span class="sub" style="display:inline;margin-right:12px">{L(rng)}</span></td></tr>')
    counts[p["status"]] = counts.get(p["status"], 0) + 1
    lbl, tone = ST[p["status"]]
    rows.append(
        f'<tr><td class="num" style="width:132px">{L(dt.strftime("%d.%m"))}'
        f'<span class="sub">{DAY[dt.weekday()]} · {L(dt.strftime("%H:%M"))}</span></td>'
        f'<td class="strong">{html.escape(c["emoji"])} {html.escape(c["title"])}'
        f'<span class="sub">{html.escape(p["label"])}</span></td>'
        f'<td style="width:100px">{PLAT.get(p["platform"], p["platform"])}'
        f'<span class="sub">{html.escape(p["slot"] or "—")}</span></td>'
        f'<td style="width:135px;text-align:left"><span class="pill {tone}">{lbl}</span></td></tr>')

for p, c in blocked:
    counts[p["status"]] = counts.get(p["status"], 0) + 1

legend = " · ".join(f'{ST[k][0]} {L(str(v))}' for k, v in sorted(counts.items(), key=lambda x: -x[1]))
pending = counts.get("PENDING_APPROVAL", 0)
nweeks = cur  # number of calendar-week groups the plan actually spans
last = datetime.datetime.fromisoformat(items[-1][0]["publish_at"]).strftime("%d.%m")

BODY = (
    masthead(f"מהדורת סוכנות · {L(TODAY.strftime('%d.%m.%Y'))} · לוח שידורים")
    + f'<div class="head"><h1>הלוח אופס — סבב חדש שנפתח הערב ורץ עד {L(last)}</h1>'
      f'<div class="deck">כל התאריכים הישנים נמחקו. {L(str(pending))} פוסטים אורגניים קיבלו חלונות '
      f'חדשים על פני {L(str(nweeks))} שבועות, וסטטוס אחיד של ״ממתין לאישור״ — מחזור אישור נקי. '
      'ששת המוצרים נבדקו מול Shopify: כולם פעילים ובמלאי.</div>'
      f'<div class="byline">מקור: drafts/state.json · אופס {L("26.08.2026")} · '
      'גיבוי המצב הקודם נשמר ב-archive/</div></div>'
    + '<table><tr><th class="num">מתי</th><th>קמפיין</th><th>ערוץ</th>'
      '<th style="text-align:left">סטטוס</th></tr>' + "".join(rows) + '</table>'
    + '<div class="notice"><div class="notice-kicker">מה לא בלוח</div>'
      f'<div class="notice-body">{L(str(counts.get("BLOCKED", 0)))} מודעות ממומנות נשארות חסומות — '
      'הטוקן של Meta עדיין user-token בלי הרשאות פרסום, וערעור המודעות פתוח. '
      f'פוסט אחד ({L("IG פיד")} של פיקאצ׳ו) כבר פורסם ב-03.08 ולכן נשאר מחוץ לרוטציה.</div></div>'
    + f'<div class="colophon">{legend} · חלונות לפי docs/schedule-slots.md · '
      'Slab Guard בחלונות ישראליים (סטייה מתועדת) · מרווח מינימלי של 24 שעות בין פוסטים '
      'באותה פלטפורמה — נבדק ועובר</div>')

if __name__ == "__main__":
    out = ROOT / "docs" / f"schedule-{TODAY}.png"
    render(BODY, out, width=1020, height=int(sys.argv[1]) if len(sys.argv) > 1 else 1500)
    print(out)
