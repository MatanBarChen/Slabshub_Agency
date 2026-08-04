---
description: בדיקת לימיטים ועלויות — צריכת Claude, קרדיטים, מנויים ומדד תמורה
argument-hint: [ריק]
---

Run the on-demand usage/limits check (same as the trigger words "בדיקת לימיטים" / "בדיקת טוקנים"). No agent spawns — the orchestrator does this inline:

1. Refresh the automatically-checkable data:
   - Claude Code: via Bash — `npx --yes ccusage@latest daily --json | tail -c 3000`, `npx --yes ccusage@latest monthly --json | tail -c 1200`, `npx --yes ccusage@latest blocks --active --json | tail -c 900`.
   - Runway: curl `https://api.dev.runwayml.com/v1/organization` (note: api.dev host) with headers `Authorization: Bearer $RUNWAY_API_SECRET` (from `.env`, never print the key) and `X-Runway-Version: 2024-11-06` → `creditBalance`.
2. Update `docs/usage-limits.md`: the table rows checked, the "מדד תמורה (Claude ROI)" line, and the "עדכון אחרון" header line.
3. Present to Matan in chat (Hebrew, visual-first — two widgets):
   - **Widget 1 — subscriptions & services table**: summary cards on top (total fixed monthly cost — currently ₪195 + Claude Max — and this month's variable spend from the consumption log), then a row per service with plan (paid/free), limit, usage, green/yellow/red status dot (Runway highlighted red while at 0 credits).
   - **Widget 2 — Claude Max, two metrics**: (a) quota — current 5h window burn + reset time + today's total; (b) value/ROI — month-to-date API-equivalent, daily pace, projected month vs Max subscription price. API-equivalent values measure consumption, not billing — Matan pays flat Max.
4. Close with one short prose line: anything 🟡/🔴, and the real out-of-pocket variable spend this month (from the consumption log — יומן צריכה).

Notes: Gemini/Tavily usage is not queryable — report from the consumption log only. Official Max quota % lives only in `/usage` in the app.
