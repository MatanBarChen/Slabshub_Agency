---
description: הפעלת סוכן copywriter — קופי לפלטפורמות מבריף קיים
argument-hint: <מוצר / נתיב בריף> [פלטפורמות ספציפיות, ברירת מחדל: הכול חוץ ממודעות חסומות]
---

Launch ONLY the `copywriter` agent for: $ARGUMENTS

Rules for this run:
- Locate the brief in `briefs/` (by product handle if a path wasn't given). If no brief exists, STOP and tell Matan to run `/brief` first — do not spawn product-intelligence yourself.
- Respect skip rules: no Facebook-ad copy while Meta paid is blocked, no Hebrew variant unless requested.
- If Matan named specific platforms in the arguments, write only those sections.
- Output: copy file in `copy/`, then report back in Hebrew with the strongest hook. Do NOT chain into creative/publisher — this is an individual run.
