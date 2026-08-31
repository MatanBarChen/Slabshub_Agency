---
description: הפעלת סוכן chat-agent (Chat_Agent) — דוח ביקושים מהצ'אט באתר ותחזוקת מוח הצ'אט
argument-hint: <ריק = דוח ביקושים של היום | "שבוע" | "רענן קטלוג" | הנחיה לשינוי התנהגות הצ'אט>
---

Launch ONLY the `chat-agent` agent for: $ARGUMENTS

Rules for this run:
- No arguments → today's demand report: which cards customers asked for in the on-site chat that we don't stock, which leads are waiting for follow-up, and anything critical from the handoffs.
- "שבוע" / a date range → same report over that window instead of today.
- "רענן קטלוג" → pull products via Shopify MCP and rebuild `prototype/sales-agent/catalog.json`, then report how many products / how many in stock.
- Any other instruction → a change to the live chat's behaviour: edit `prototype/sales-agent/system-prompt.md` (never the truth rules), and report the diff in one line.
- Output: `reports/demand/demand-log.md` (append, never overwrite), then report back to Matan in Hebrew.
- Customer contact details never leave `prototype/sales-agent/conversations/` — not into the report, not into a commit, not into chat.
- The agent never contacts a customer and never writes to the live theme.
- Do NOT chain into other agents — individual run. If demand justifies sourcing, say so and let Matan decide whether to run `/looking`.
