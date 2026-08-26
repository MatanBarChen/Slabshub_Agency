"""Renders the shipping-rates widget in the SlabsHub brand design line."""
import sys, pathlib, html
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from widget import render, masthead

L = lambda s: f'<span class="ltr">{s}</span>'

ZONES = [
    ("ישראל", "IL", "$10", L("₪30"), f'{L("₪15–30")} · דואר רשום עד 500 גרם', "warn", f'רווח {L("₪0–15")}'),
    ("צפון אמריקה", "US · CA · MX", "$23", L("₪69"), f'{L("₪49")} · Eco Post לארה״ב', "good", f'רווח {L("₪20")}'),
    ("אירופה", "19 מדינות", "$19", L("₪57"), f'{L("₪45–49")} · משוער', "warn", f'רווח {L("₪8–12")}'),
    ("אסיה-פסיפיק ומזה״ת", "JP·AU·NZ·SG·HK·KR·TW·AE", "$29", L("₪87"), f'{L("₪60–70")} · משוער', "good", f'רווח {L("₪17–27")}'),
]
rows = "".join(
    f'<tr><td class="strong">{html.escape(n)}<span class="sub">{html.escape(c)}</span></td>'
    f'<td class="num">{p}<span class="sub">{ils}</span></td><td>{cost}</td>'
    f'<td style="text-align:left"><span class="pill {t}">{m}</span></td></tr>'
    for n, c, p, ils, cost, t, m in ZONES
)

OPEN = [
    ("שכבת אקספרס (EMS)",
     f'היום שירות אחד בלבד לכל יעד. EMS אמיתי: {L("₪118")} לארה״ב, {L("₪163–208")} ליעדים רחוקים. '
     'הצעה: <b>אירופה $45 · צפון אמריקה $49 · אסיה-פסיפיק $59</b>.'),
    ("משלוח חינם בינלאומי מעל סף",
     'על סלאב ב-$300 המשלוח הוא רעש. הצעה: <b>חינם מעל $250</b> — מנוף המרה שגם דוחף העלאת סל.'),
    ("ביטוח לפריטים יקרים",
     'פיקאצ׳ו ב-$999 ב-Eco Post רגיל הוא סיכון לא מכוסה. הצעה: <b>מעל $250 — EMS מבוטח בלבד</b>.'),
]
opens = "".join(
    f'<tr><td class="rank" style="width:34px">{i}</td>'
    f'<td class="strong" style="width:215px">{html.escape(t)}</td>'
    f'<td style="line-height:1.7">{d}</td></tr>'
    for i, (t, d) in enumerate(OPEN, 1)
)

BODY = (
    masthead("מהדורת סוכנות · יום ד׳ 26 באוגוסט 2026 · תעריפי משלוח")
    + '<div class="head"><h1>התעריפים אושרו, עוגלו, ונכנסו לתוקף</h1>'
      '<div class="deck">ארבעת האזורים מתומחרים עכשיו בדולרים עגולים. '
      'ישראל עברה ממשלוח חינם לתעריף — התעריף הראשון בהיסטוריה של החנות שגובה על משלוח מקומי.</div>'
      '<div class="byline">4 אזורים · 31 מדינות · כל תעריף אומת בקריאה חיה לקופה</div></div>'
    + '<div class="notice"><div class="notice-kicker">הערת מטבע — שווה לדעת</div>'
      '<div class="notice-body">ביקשת <b>₪29</b> לישראל, והגדרתי <b>$10</b>. הסיבה: החנות תומכת '
      'ב-USD בלבד, ואין ILS כמטבע מקומי לשוק ישראל — זה דורש Shopify Payments, ואתה סולק דרך '
      'iCount ו-PayPal. לכן לקוח ישראלי מחויב בדולרים בכל מקרה. '
      f'{L("$10")} הם {L("≈₪30")} — הפרש של שקל אחד, אבל מספר עגול בקופה. '
      f'אם אתה מעדיף בדיוק ₪29, אגדיר {L("₪29")} והלקוח יראה {L("$9.67")}. תגיד ואחליף.</div></div>'
    + '<h2>מה פעיל עכשיו — מחיר מול עלות אמיתית</h2>'
      '<table><tr><th>אזור</th><th class="num">מחיר ללקוח</th><th>עלות משוערת אליך</th>'
      '<th style="text-align:left">מרווח</th></tr>' + rows + '</table>'
    + '<h2>שלוש הצעות שנשארו פתוחות</h2><table>' + opens + '</table>'
    + '<div class="colophon">עלויות — דואר רשום מקומי עד 500 גרם ₪15–30 (topdelivery.co.il) · '
      'Eco Post לארה״ב 500–750 גרם ₪49.20 · EMS לארה״ב ₪118, יעדים רחוקים ₪163–208 (israelpost.co.il). '
      'המרה לפי ₪3 לדולר. עלויות אירופה ואסיה מסומנות כמשוערות — לא נמצא מחירון רשמי לפי יעד.</div>'
)

if __name__ == "__main__":
    out = pathlib.Path(__file__).resolve().parent.parent / "docs" / "shipping-rates-2026-08-26.png"
    render(BODY, out, width=1020, height=1055)
    print(out)
