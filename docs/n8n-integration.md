# תכנון אינטגרציית n8n — SlabsHub Agency

> סטטוס: מתוכנן, ממתין לחיבור Meta API (הטוקן שמתן מפיק ישרת גם את n8n).
> עיקרון-על: n8n = צנרת (טריגרים, אישורים, פרסום). Claude Code = מוח (בריפים, קופי, קריאייטיב, אימות).
> כלל הברזל נשאר: שום פוסט לא מתפרסם בלי אישור מפורש של מתן — ב-n8n זה ממומש ככפתור אישור לפני כל פרסום.

---

## ארכיטקטורת החיבור בין המערכות

הבעיה: קבצי ה-drafts חיים על המחשב של מתן; n8n (ענן) לא קורא קבצים מקומיים.
הפתרון: **תור פרסום ב-Supabase** (ה-MCP כבר מחובר לסוכנות — אפס תשתית חדשה).

```
Claude Code                     Supabase                       n8n
───────────                     ────────                       ───
מתן מאשר טיוטה בצ'אט  ──▶  INSERT publish_queue  ◀──poll──  Workflow 1
                                                              │ כפתור אישור סופי (Telegram)
                                                              │ פרסום ל-FB/IG בסלוט
                            UPDATE status='published' ◀──────┘
(analytics קורא גם מכאן)
```

### טבלת `publish_queue` (Supabase)

| עמודה | סוג | הערות |
|---|---|---|
| id | uuid, pk | |
| campaign | text | `YYYY-MM-DD-<product-handle>` — תואם utm_campaign |
| platform | text | facebook-organic / instagram-feed / instagram-story / facebook-ad |
| caption | text | הקופי הסופי כולל האשטגים |
| image_url | text | **חייב URL ציבורי** — ראה "הערת נכסים" למטה |
| first_comment | text, nullable | ללינק-בתגובה-ראשונה (פוסטים של FB) |
| link | text | ה-URL עם UTM |
| publish_at | timestamptz | הסלוט מ-docs/schedule-slots.md |
| status | text | approved → published / failed / skipped |
| post_id | text, nullable | מזהה הפוסט שחזר מ-Meta |
| error | text, nullable | |
| created_at | timestamptz | |

**הערת נכסים:** ה-Instagram Graph API דורש שהתמונה/וידאו יהיו ב-URL ציבורי. לפני הכנסת שורה לתור, Claude מעלה את הנכס המקומי ל-CDN של Shopify (דרך ה-Shopify MCP, כלי העלאת תמונות) ושומר את ה-URL שחזר ב-`image_url`.

---

## Workflow 1 — "Publish with Approval" (הליבה)

מפרסם טיוטות מאושרות בסלוט שלהן, עם כפתור אישור סופי אצל מתן.

| # | Node | תפקיד |
|---|---|---|
| 1 | **Schedule Trigger** | כל 15 דקות |
| 2 | **Supabase (Postgres)** | `SELECT * FROM publish_queue WHERE status='approved' AND publish_at <= now() + interval '20 min'` |
| 3 | **IF** | אין שורות → סיום שקט |
| 4 | **Telegram — Send & Wait for Approval** | תצוגה מקדימה (תמונה + קפשן + פלטפורמה + שעה) עם כפתורים ✅ פרסם / ⏭️ דלג. timeout 6 שעות → skipped |
| 5 | **Switch (platform)** | פיצול לפי פלטפורמה |
| 5a | **HTTP Request — FB photo post** | `POST graph.facebook.com/v21.0/{PAGE_ID}/photos` עם `url`, `caption`, token |
| 5b | **HTTP Request — FB first comment** | `POST /{post-id}/comments` עם `message` = first_comment (אם קיים) |
| 5c | **HTTP Request — IG create container** | `POST /{IG_USER_ID}/media` עם `image_url`, `caption` |
| 5d | **HTTP Request — IG publish** | `POST /{IG_USER_ID}/media_publish` עם `creation_id` (לסטורי: להוסיף `media_type=STORIES` בשלב 5c) |
| 6 | **Supabase (Postgres)** | `UPDATE publish_queue SET status='published', post_id=... WHERE id=...` |
| 7 | **Telegram — Notify** | "פורסם ✓" + לינק לפוסט |
| E | **Error branch** | status='failed' + error, הודעת שגיאה למתן. בלי retry אוטומטי — פרסום כפול גרוע מפרסום שנכשל |

**בצד של Claude:** כשמתן מאשר טיוטה בצ'אט, ה-orchestrator (1) מעלה את הנכס ל-Shopify CDN, (2) מכניס שורה ל-publish_queue, (3) מעדכן את הטיוטה ואת `drafts/_index.md` לסטטוס `QUEUED`. אחרי שהפוסט עולה — analytics יכול לקרוא post_id מהטבלה בשביל insights.

---

## Workflow 2 — "New Product Alert" (טריגר אוטומטי)

מחליף את הצורך של מתן לכתוב "מוצר חדש עלה לחנות".

| # | Node | תפקיד |
|---|---|---|
| 1 | **Shopify Trigger** | webhook `products/create` (דורש credential של Shopify Admin ב-n8n) |
| 2 | **Filter** | רק `status=active` (לא טיוטות חנות) |
| 3 | **Telegram — Send Message** | "🆕 מוצר חדש: {title} ({price}). להכין קמפיין? פתח את הסוכנות והרץ `/brief {handle}`" |

שלב מתקדם (אופציונלי, בהמשך): במקום הודעה בלבד — קריאת HTTP ל-webhook מקומי שמריץ את Claude Code ב-headless (`claude -p "/brief <handle>"`), כך שהבריף כבר מחכה כשמתן נכנס. דורש חשיפת endpoint מהמחשב (למשל cloudflared tunnel) — לא לגרסה הראשונה.

הרחבה קלה באותה תבנית: webhook על `inventory_levels/update` או cron שבועי ששואל את Shopify על מוצרים בני 14+ יום בלי מכירות → התראת "מלאי תקוע".

---

## Credentials שצריך להכין ב-n8n

| Credential | מקור | הערות |
|---|---|---|
| Meta Page Token | אותו `META_PAGE_TOKEN` מה-.env | + PAGE_ID + IG_USER_ID |
| Shopify Admin API | Shopify Admin → Apps → Develop apps → token ל-n8n | ל-Shopify Trigger |
| Supabase | Project Settings → Database connection string | ל-nodes של Postgres |
| Telegram Bot | @BotFather → בוט חדש → token; מתן שולח לו /start | ערוץ האישורים |

מתן מזין את כולם ישירות ב-n8n Credentials — לא דרך הצ'אט, לא בקבצים בסביבת העבודה (מדיניות הסודות הרגילה).

## סדר הקמה

1. ✅ (בתהליך) מתן משלים את חיבור Meta — טוקן + הרשאות.
2. יצירת טבלת `publish_queue` ב-Supabase (Claude יריץ את ה-migration דרך ה-MCP כשנתחיל).
3. הקמת בוט Telegram (5 דקות מול BotFather).
4. בניית Workflow 1 ובדיקה על פוסט אחד אמיתי מאושר.
5. בניית Workflow 2.
6. עדכון `docs/integrations.md` + הגדרות ה-publisher בהתאם (סטטוס QUEUED חדש).
