"""Weekly schedule widget — SlabsHub brand design line.

Reads drafts/state.json and renders the row-per-slot board.
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
L = lambda s: f'<span class="ltr">{s}</span>'


def when(p):
    if not p.get("publish_at"):
        return '<span class="sub" style="margin:0">—</span>'
    d = datetime.date.fromisoformat(p["publish_at"][:10])
    t = L(d.strftime("%d.%m"))
    if p["status"] in ("APPROVED", "PENDING_APPROVAL") and d < TODAY:
        return f'{t}<span class="sub" style="color:#b20a2c">עבר · {(TODAY - d).days} ימים</span>'
    return t


rows, counts, overdue = [], {}, 0
for c in STATE["campaigns"]:
    rows.append(
        f'<tr><td colspan="4" style="background:#faf9f6;border-bottom:1px solid #000">'
        f'<span class="strong">{html.escape(c["emoji"])} {html.escape(c["title"])}</span>'
        f'<span class="sub" style="display:inline;margin-right:12px">{html.escape(c["price"])} · '
        f'{html.escape(c["tag"])}</span></td></tr>')
    for p in c["posts"]:
        counts[p["status"]] = counts.get(p["status"], 0) + 1
        d = p.get("publish_at")
        if d and p["status"] in ("APPROVED", "PENDING_APPROVAL") \
           and datetime.date.fromisoformat(d[:10]) < TODAY:
            overdue += 1
        lbl, tone = ST[p["status"]]
        blockers = (f'<span class="sub" style="color:#b20a2c">'
                    f'{html.escape(" · ".join(p["blockers"]))}</span>') if p.get("blockers") else ""
        rows.append(
            f'<tr><td style="width:105px">{PLAT.get(p["platform"], p["platform"])}</td>'
            f'<td>{html.escape(p["label"])}{blockers}</td>'
            f'<td class="num" style="width:150px">{when(p)}</td>'
            f'<td style="width:135px;text-align:left"><span class="pill {tone}">{lbl}</span></td></tr>')

legend = " · ".join(f'{ST[k][0]} {L(str(v))}' for k, v in sorted(counts.items(), key=lambda x: -x[1]))

BODY = (
    masthead(f"מהדורת סוכנות · {L(TODAY.strftime('%d.%m.%Y'))} · לוח שידורים")
    + '<div class="head"><h1>הלוח עומד — כל חלון שאושר כבר עבר</h1>'
      f'<div class="deck">{L(str(overdue))} פוסטים מאושרים או ממתינים לאישור שתאריך הפרסום '
      'שלהם חלף, ורק אחד מסומן כפורסם. עכשיו כשהקופה עובדת, זה החסם היחיד שנשאר בין '
      'התוכן לבין מכירה.</div>'
      f'<div class="byline">מקור: drafts/state.json · עודכן {L(STATE["updated"])}</div></div>'
    + '<table><tr><th>פלטפורמה</th><th>תוכן</th><th class="num">חלון</th>'
      '<th style="text-align:left">סטטוס</th></tr>' + "".join(rows) + '</table>'
    + f'<div class="colophon">{legend}</div>')

if __name__ == "__main__":
    out = ROOT / "docs" / f"schedule-{TODAY}.png"
    render(BODY, out, width=1020, height=int(sys.argv[1]) if len(sys.argv) > 1 else 1500)
    print(out)
