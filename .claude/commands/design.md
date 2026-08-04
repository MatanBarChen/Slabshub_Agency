---
description: הפעלת סוכן design-agent — ביקורת עיצוב והצעות שדרוג לחנות
argument-hint: <סקופ (למשל "עמוד הבית", "עמוד מוצר", "כל החנות") או בקשה חופשית>
---

Launch ONLY the `design-agent` agent for: $ARGUMENTS

Rules for this run:
- If no scope given, default scope: home page + one product page.
- First check `design/` — if an audit for this scope exists < 30 days old, extend it rather than re-audit (unless the user asked for a fresh one).
- Output: audit file in `design/`, then report back to Matan in Hebrew: top 3 recommendations with impact/effort, one line each. Do NOT build anything — building approved items goes through the Orchestrator with the `anthropic-skills:web` skill, as a separate step after Matan picks what he wants.
