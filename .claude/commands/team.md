---
description: לוח בקרה ויזואלי לסוכנים — מי רץ לאחרונה, מה הפיק, מה בתור
argument-hint: [ריק]
---

Render the agents control board in chat (orchestrator inline — NO agent spawns, this is a read-only status view):

1. Gather freshness data cheaply:
   - `for d in briefs copy assets drafts reports/looking design; do ls -t "$d" | head -2; done` (Bash) — newest deliverable per agent directory.
   - `drafts/state.json` — pending-approval counts and campaign pipelines.
2. Render ONE widget (visualization, RTL, per the visual-first rule): a card grid, one card per agent — product-intelligence, copywriter, creative, publisher, analytics, design-agent, scout, chat-agent. Each card: Tabler icon, agent name, one-line role, last run date + latest deliverable (campaign name), and a status dot: 🟢 fresh output ≤48h · ⚪ idle · 🟡 has work waiting on it (e.g., publisher with drafts pending Matan's approval, analytics when the weekly report is due).
3. Below the grid, one short prose line: what's waiting on whom (e.g., "3 טיוטות ממתינות לאישור מתן; דוח שבועי הבא ביום ראשון").

Keep it lean: two cheap reads, one widget, no file writes.
