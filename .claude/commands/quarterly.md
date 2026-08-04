---
description: דוח כספי רבעוני בסגנון חברה ציבורית — analytics במצב פיננסי
argument-hint: <רבעון אופציונלי (ברירת מחדל: הרבעון הנוכחי עד היום)>
---

Launch ONLY the `analytics` agent in FINANCIAL MODE for: $ARGUMENTS

Rules for this run:
- Default window: current quarter to date. Structure per CLAUDE.md "Corporate reporting" section.
- COGS from docs/cogs.md — every product sold without a cost line gets flagged (never silently estimated). Opex from docs/usage-limits.md consumption log.
- Output: reports/financials/YYYY-Qn.md, then report back to Matan in Hebrew. The orchestrator then renders the P&L + KPIs as a clean widget (visual-first rule) — investor-grade, professional.
- No chaining into other agents.
