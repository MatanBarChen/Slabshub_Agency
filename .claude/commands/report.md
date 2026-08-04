---
description: הפעלת סוכן analytics — דוח ביצועים
argument-hint: [חלון זמן, ברירת מחדל: 7 ימים אחרונים מול 7 שלפניהם] [שאלה ספציפית]
---

Launch ONLY the `analytics` agent for: $ARGUMENTS

Rules for this run:
- Default window: last 7 days vs the 7 before; override if Matan specified one.
- If Matan asked a specific question (e.g. "כמה מכר הפיקאצ'ו"), answer just that — a focused pull, not the full weekly report format.
- Cross-reference `published/` and `drafts/state.json` for what was live.
- Output: report in `reports/` (full report only; skip the file for quick focused questions), then the answer/top recommendations in Hebrew.
