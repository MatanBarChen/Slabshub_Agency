---
description: הפעלת סוכן product-intelligence — בריף מוצר בודד לפי דרישה
argument-hint: <שם מוצר / handle / קריטריון (למשל "לא נמכר שבועיים")>
---

Launch ONLY the `product-intelligence` agent for: $ARGUMENTS

Rules for this run:
- First check `briefs/` — if a brief for this product exists with comps < 7 days old, report it and STOP (don't re-research) unless the user asked for a refresh.
- Output: brief file in `briefs/`, then report back to Matan in Hebrew: the angle, price position, and any warning. Do NOT chain into copywriter/creative/publisher — this is an individual run.
