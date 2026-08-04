---
description: הפעלת סוכן publisher — אריזת קופי+קריאייטיב לטיוטות מוכנות לאישור
argument-hint: <מוצר / קמפיין> [פלטפורמות ספציפיות]
---

Launch ONLY the `publisher` agent for: $ARGUMENTS

Rules for this run:
- Inputs: the campaign's copy file from `copy/` and assets from `assets/`. If either is missing, STOP and tell Matan what to run first (`/copy` or `/creative`) — do not spawn those agents yourself.
- Slots from `docs/schedule-slots.md` (one-line citation). Update `drafts/_index.md`.
- Skip rules apply: no facebook-ad drafts while Meta paid is blocked.
- HARD RULE unchanged: drafts only, nothing is ever published without Matan's approval in chat.
- Report back in Hebrew: draft paths + proposed schedule table.
