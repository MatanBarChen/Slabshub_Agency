import sys, json, html, pathlib
sys.path.insert(0, "/home/user/Slabshub_Agency/scripts")
from widget import render, masthead

L = lambda s: f'<span class="ltr">{s}</span>'
rows = json.load(open("/home/user/Slabshub_Agency/docs/ils-reprice-plan.json", encoding="utf-8"))
d = {r["title"]: r for r in rows}
active = [r for r in rows if r["status"] == "ACTIVE"]

SHOW = [
 ("Slab Guard — צבע אחיד", "Slab Guard | Silicone Bumper — Solid Color"),
 ("Slab Guard — גליטר", "Slab Guard | Silicone Bumper — Glitter Gradient"),
 ("Eevee 1st Ed · CGC 7", "CGC 7 | Eevee [1st Edition] #51 Pokemon Jungle"),
 ("Mewtwo #183 · Japanese 151", "RAW CARD | Mewtwo #183 Japanese Scarlet & Violet 151"),
 ("Pikachu Van Gogh #085", "RAW CARD | Pikachu with Grey Felt Hat #85 Pokemon Promo"),
 ("Charizard CD Promo · PSA 9", "PSA 9 | Charizard [Holo] #6 Pokemon Japanese CD Promo"),
]
def row(n, k):
    r = d[k]
    tone = "good" if abs(r["drift"]) < 3 else "warn"
    return ('<tr><td class="strong">' + html.escape(n) + '</td>'
            '<td class="num">' + L("${:,.2f}".format(r["usd"])) + '</td>'
            '<td class="num strong">' + L("\u20aa{:,}".format(r["ils"])) + '</td>'
            '<td style="text-align:left"><span class="pill ' + tone + '">'
            + L("{:+.1f}%".format(r["drift"])) + '</span></td></tr>')

body = "".join(row(n, k) for n, k in SHOW)

STEPS = [
 ("אתה", "להפוך את מטבע החנות ל-ILS",
  "Shopify Admin → Settings → General → Store currency → Israeli Shekel. "
  "<b>רק אתה יכול לעשות את זה</b> — אין ל-API הרשאה לשנות מטבע חנות."),
 ("אני", "לתמחר מחדש 68 וריאנטים",
  f"התוכנית מוכנה ורצה בפקודה אחת. שווי הקטלוג הפעיל: {L('$7,959')} → {L('₪23,849')} — "
  f"סטייה נטו של {L('0.1%-')} מהמרה ישרה. הסטייה הגדולה ביותר בפריט בודד: {L('7.7%')}."),
 ("אני", "לתקן את תעריפי המשלוח",
  f"היום הם מוגדרים בדולרים ({L('$10 / $19 / $23 / $29')}) ויהפכו לשקלים באותם מספרים. "
  f"אחליף ל-{L('₪29 / ₪59 / ₪69 / ₪89')} — בדיוק ה-{L('₪29')} שביקשת לישראל."),
 ("אני", "לעדכן את הקופי בפרסום",
  "שש טיוטות גל 1 ומה שאחריהן. Eevee עובר מ-$24.99 ל-₪79, Slab Guard לשקלים."),
]
steps = "".join(
    f'<tr><td style="width:52px"><span class="pill {"warn" if w=="אתה" else "flat"}">{w}</span></td>'
    f'<td class="strong" style="width:210px">{html.escape(t)}</td>'
    f'<td style="line-height:1.7">{x}</td></tr>' for w, t, x in STEPS)

BODY = (
    masthead(f"מהדורת סוכנות · {L('26.08.2026')} · מעבר לשקלים")
    + '<div class="head"><h1>המעבר לשקלים — מוכן לרוץ, חוץ מהצעד שרק אתה יכול</h1>'
      '<div class="deck">שינוי מטבע החנות הוא פעולה בהגדרות בלבד — ל-API אין גישה אליה. '
      'התמחור מחדש של כל הקטלוג כבר מחושב ומחכה.</div>'
      f'<div class="byline">68 וריאנטים · שער {L("₪3.0")} לדולר · תוכנית מלאה ב-docs/ils-reprice-plan.json</div></div>'

    + '<div class="notice alarm"><div class="notice-kicker">הסכנה — Shopify לא ממיר מחירים</div>'
      '<div class="notice-body">כשמחליפים מטבע, <b>המספרים נשארים כמו שהם</b>. '
      f'הצ׳אריזרד ב-{L("$1,199")} הופך ל-{L("₪1,199")} — הנחה של 67% בטעות. הפיקאצ׳ו ב-{L("$999")} '
      f'הופך ל-{L("₪999")}. לכן סדר הפעולות קריטי: <b>נועלים את החנות בסיסמה, מחליפים מטבע, '
      'אני מריץ את התמחור, פותחים.</b> חלון החשיפה: דקות.</div></div>'

    + '<h2>מי עושה מה</h2><table>' + steps + '</table>'
    + '<h2>דוגמאות מהתוכנית — מוצרי הקמפיינים</h2>'
      '<table><tr><th>מוצר</th><th class="num">היום</th><th class="num">אחרי</th>'
      '<th style="text-align:left">מול המרה ישרה</th></tr>' + body + '</table>'

    + '<div class="notice"><div class="notice-kicker">שתי החלטות שנשארות לך</div>'
      f'<div class="notice-body"><b>1. השער.</b> חישבתי לפי {L("₪3.0")} לדולר. אם אתה רוצה כרית '
      f'לתנודות שער, {L("₪3.2")} או {L("₪3.3")} יעלו את כל הקטלוג ב-7–10%.<br>'
      f'<b>2. Slab Guard.</b> המרה נאמנה נותנת {L("₪15")} ו-{L("₪19")}. המחיר שרצית במקור היה '
      f'{L("₪19")} ו-{L("₪22")} — זו העלאת מחיר אמיתית, לא תוצר של ההמרה. תגיד מה עדיף.</div></div>'

    + '<div class="colophon">מטבע מקומי לשוק ישראל (להציג ₪ בלי לשנות את מטבע החנות) דורש '
      'Shopify Payments — החנות סולקת ב-iCount, אז זה לא זמין. שינוי מטבע החנות הוא הדרך היחידה. '
      'שים לב: אחרי המעבר גם קונה מארה״ב, בריטניה ויפן יראה שקלים.</div>')

render(BODY, "/home/user/Slabshub_Agency/docs/ils-switch-2026-08-26.png", width=1020, height=1265)
print("ok")
