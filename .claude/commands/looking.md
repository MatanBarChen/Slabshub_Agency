---
description: הפעלת סוכן scout — סריקת שוק ומציאת קלפים שכדאי לקנות לחנות
argument-hint: <סקופ אופציונלי: תקציב / סט / פוקימון (למשל "עד $50", "vintage", "Prismatic")>
---

Launch ONLY the `scout` agent for: $ARGUMENTS

Rules for this run:
- If no scope given, default: general sweep, budget $15–$150 per card.
- The agent uses Tavily (scripts/tavily_search.py via Bash, or Tavily MCP tools if loaded) — max ~10 calls.
- Output: buy-list report at `reports/looking/looking.md` (always this name — previous run gets renamed to looking-<date>.md), then report back to Matan in Hebrew: top 2 picks, one line each. This is a recommendation only — nothing is purchased; Matan decides and buys manually.
- Do NOT chain into other agents — individual run.
