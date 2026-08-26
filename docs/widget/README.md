# ווידג'טים בצ'אט — שפת העיצוב של SlabsHub

עודכן: 2026-08-26.

## מאיפה הטוקנים

**לא מהגדרות התמה.** התמה הפעילה (`Updated copy of Black & White`) מגדירה DM Sans + Archivo Narrow
וסכמות צבע בז'/אפור — אבל הדפים החיים דורסים אותה עם מערכת עיצוב משלהם. הטוקנים כאן נקראו
מה-CSS custom properties של **הדף החי** (`curl https://slabshub.com/`, 26.08.2026):

| טוקן | ערך | שימוש |
|---|---|---|
| `--color-honeycomb-yellow` | `#ffd931` | רקע ה-masthead |
| `--color-carbon-black` | `#000000` | קווי הפרדה 2px, כותרות |
| `--color-ink-black` | `#231f20` | טקסט גוף |
| `--color-fog-gray` | `#a6a8aa` | טקסט משני, כותרות עמודה |
| `--color-smoke-line` | `#d6d6d6` | קו הפרדה בין שורות |
| `--font-display` | `'Times Now','Playfair Display',serif` | כותרות |
| `--font-body` | `'Times New Roman',serif` | גוף |
| `--font-product` | `'Lora',serif` | מספרים ומחירים |
| `--font-ui` | `'Helvetica Neue',sans` | תוויות, caption |
| `--radius-card` / `--radius-pill` / `--radius-hero` | `12px` / `25px` / `45px` | פינות |
| `--tracking-nav/ui/wide` | `.063em` / `.073em` / `.091em` | ריווח אותיות |

הכלל: אם האתר משתנה — לקרוא מחדש ולעדכן כאן. לא להמציא ערכים.

## עברית

`Times Now`, `Playfair Display` ו-`Lora` הן בלי גליפים עבריים. הבחירה:

- **Frank Ruhl Libre** — המקבילה העברית ל-display/body. פונט עיתונות עברי קלאסי, מתאים בדיוק
  לאסתטיקה העיתונאית של האתר.
- **Heebo** — המקבילה ל-`--font-ui` (Helvetica Neue).

שניהם מוטמעים כ-base64 ב-`fonts.css` יחד עם Playfair Display ו-Lora ללטינית, כדי שהרינדור
יעבוד זהה בשתי המכונות בלי גישה לרשת.

## שימוש

```python
import sys; sys.path.insert(0, "scripts")
from widget import render, masthead

body = masthead("מהדורת סוכנות · יום ד׳ 26 באוגוסט 2026 · דוח תפעול") + """
  <div class="head"><h1>כותרת</h1>
    <div class="deck">תת-כותרת</div>
    <div class="byline">שורת קרדיט</div></div>
  <h2>כותרת סעיף</h2>
  <table>...</table>
  <div class="colophon">מקורות</div>"""

render(body, "out.png", width=1020, height=1200)
```

מחלקות זמינות: `.sheet .masthead .wordmark .edition .head h1 .deck .byline h2
.notice[.alarm] .notice-kicker .notice-body .strong .sub .num .ltr .pill[.good/.warn/.bad/.flat]
.rank .colophon`

## שני כללים שנלמדו בדרך

1. **מטבע ומספרים חייבים `<span class="ltr">`.** בהקשר RTL המחרוזת `₪15–30` מתהפכת ל-`15₪–30`.
   המחלקה `.ltr` (`direction:ltr; unicode-bidi:isolate`) פותרת. תאי `td.num` כבר מטופלים.
2. **גובה החלון נקבע ידנית.** אין auto-fit בצילום — לרנדר, להסתכל, ולכוונן את `height`
   עד שאין חיתוך ואין רווח לבן מיותר בתחתית.
