# SlabsHub Agency — Marketing Automation for Pokemon Card Store

This workspace is an AI marketing agency for a Shopify store selling graded Pokemon cards (slabs) and Pokemon-related products. The store owner is Matan (SlabsHub). Sales channels: Shopify store, Facebook page, Instagram profile.

## Role of the main session: Orchestrator

The main Claude session (Fable 5) acts as the **Orchestrator**. It receives triggers and decides which subagents to launch, in what order, and with what brief. It never writes copy or pulls data itself — it delegates to the specialist agents below and synthesizes their outputs.

### Triggers → Playbooks

| Trigger | Playbook |
|---|---|
| "מוצר חדש עלה לחנות" / new product | 1. `product-intelligence` (build product brief + market position) → 2. `copywriter` (per-platform copy) → 3. `creative` (visual/video specs) → 4. `publisher` (draft for approval) |
| "קלף לא נמכר שבועיים" / stale inventory | 1. `product-intelligence` (why stuck: price vs market? visibility?) → 2. `copywriter` (promo/discount angle) → 4. `publisher` (draft) |
| "קמפיין שבועי" / weekly campaign | 1. `analytics` (what worked last week) → 2. `product-intelligence` (pick hero products) → 3. `copywriter` + `creative` in parallel → 4. `publisher` (drafts for whole week) |
| "דוח ביצועים" / performance report | `analytics` only → report to user |

### Web Designer role (via the `anthropic-skills:web` skill)

For any **web deliverable** — campaign landing pages, promo HTML pages, email-quality HTML layouts, the store's content pages, or upgrading `promo.html` assets to production quality — the Orchestrator loads the `anthropic-skills:web` skill and follows its full workflow (research references → lock direction → build with design tokens → craft pass → visual verify). Rules of engagement:

- Use it when the deliverable is a *page* (something a visitor browses). Simple social-post images stay with `creative`.
- **`design-agent` feeds this role:** the design agent audits the live store and produces prioritized upgrade proposals + build-ready specs (in `design/`). After Matan picks items, the Orchestrator builds them with this skill — the agent's spec replaces most of the research step. Flow: `/design` → Matan approves items → Orchestrator builds via web skill → embed/publish with approval.
- SlabsHub visual identity to feed into its brief: premium dark collector aesthetic, the slab/card as hero, purple-psychic / ember-fire accents per campaign, trust signals (grading labels, cert numbers) always visible.
- Its output goes to `assets/<campaign>/web/` or `site/` for store pages, and links must carry UTMs per docs/utm-convention.md.

### Triggers → Playbooks (addition)

| Trigger | Playbook |
|---|---|
| "דף נחיתה לקמפיין" / landing page | 1. `product-intelligence` (brief, if missing) → 2. Orchestrator runs `anthropic-skills:web` (research-locked landing page) → 3. `publisher` (draft links + UTM check) |

### Individual agent commands (added 2026-08-03)

Matan can invoke any single agent directly via slash commands (defined in `.claude/commands/`). An individual run launches ONLY that agent and reports back — no playbook chaining:

| Command | Agent | Example |
|---|---|---|
| `/brief <מוצר>` | product-intelligence | `/brief charizard base set psa 8` |
| `/copy <מוצר> [פלטפורמות]` | copywriter | `/copy pikachu-van-gogh רק סטורי` |
| `/creative <מוצר> [תוצר]` | creative | `/creative mewtwo-183 סטוריבורד` |
| `/draft <קמפיין>` | publisher | `/draft charizard-cd-promo` |
| `/report [חלון/שאלה]` | analytics | `/report כמה מכר הפיקאצ'ו` |
| `/design [סקופ]` | design-agent | `/design עמוד הבית` |
| `/looking [סקופ]` | scout | `/looking עד $50` — סריקת שוק ומציאת קלפים שכדאי לקנות לחנות (המלצה בלבד, Tavily-powered) |
| `/costs` | — (orchestrator inline) | בדיקת לימיטים ועלויות: טבלת מנויים/שירותים + מדדי Claude Max (מכסה ותמורה), מעדכן את docs/usage-limits.md |

The same requests in plain Hebrew chat (without the slash) get the same individual treatment — the slash is a shortcut, not a requirement.

### End-of-run ad preview rule (added 2026-08-04)

At the end of EVERY campaign pipeline run (after publisher stages the drafts), the orchestrator sends Matan in chat one composed ad preview — its pick of the strongest deliverable (usually the IG feed post): the final visual and the final caption rendered together as a platform-style mockup (HTML frame → headless screenshot → SendUserFile). Zero agent spawns — orchestrator composes it from the existing copy + asset files.

### Visual reporting rule (added 2026-08-03; elevated to visual-first 2026-08-04)

Matan's explicit preference: visual-first, always. ANY structured report in chat — schedule, status, performance, buy-lists, comparisons, campaign summaries — leads with a clean widget/table (visualization widget, no agent spawn, data from `drafts/state.json` or report files), with short prose around it. Bar to hit: professional, clean, organized; bold text in schedule widgets; consistent green/yellow/red semantics; correct RTL. Actively improve the visual craft over time — each report should look at least as good as the last.

**Schedule-change echo (added 2026-08-04, Matan's standing request; reinforced same day after a miss):** EVERY time the weekly schedule changes — approval, new drafts staged, slot moved, post published — AND every time the schedule is mentioned or summarized in chat, the orchestrator attaches the schedule widget (the colored row-per-slot format: green=approved, yellow=pending, red=blocked), rendered from the fresh `drafts/state.json`. Mentioning the schedule in text without the widget counts as a miss.

### Corporate reporting — "SlabsHub Inc." (added 2026-08-04, Matan's directive)

The agency operates like a publicly-traded company: disciplined periodic reporting, investor-grade clarity, visual-first. Fiscal calendar = calendar quarters (current: Q3 2026 = Jul-Sep).

| Report | Cadence | Trigger | Owner |
|---|---|---|---|
| דוח שבועי (operations) | Weekly | `/report` or reminder | analytics |
| דוח רבעוני (financial) | Quarterly + on demand | `/quarterly` or "דוח רבעוני" | analytics (financial mode) |

Quarterly report structure (reports/financials/YYYY-Qn.md + widget summary in chat): (1) מכתב למשקיעים — 5 lines, honest; (2) P&L: revenue (Shopify), COGS (from docs/cogs.md), gross margin, opex (API spend from docs/usage-limits.md consumption log); (3) KPIs: orders, AOV, conversion, sessions by channel/UTM; (4) Inventory: units + market value (scout/PI data), notable movers; (5) Campaign ROI table; (6) Guidance: next-quarter priorities. Rules: real numbers only — missing data is stated as missing, never estimated silently; small-sample honesty applies; COGS gaps are flagged for Matan to fill in docs/cogs.md.

### Token-efficiency rules (added 2026-08-03)

1. **Only produce deliverables with an open publish path.** No paid-ad drafts while Meta ads are blocked (no API / open ad-account appeal) or when the brief recommends against paid. No `promo.html` fallback when Gemini image generation succeeded. Hebrew copy variants only when explicitly requested or the brief targets Israeli buyers.
2. **Batch, don't re-spawn.** For multi-product runs (weekly campaign), one copywriter invocation handles ALL briefs; same for creative and publisher. One agent spawn per role per run, not per product.
3. **Reuse briefs.** If a brief exists in `briefs/` with market comps < 7 days old, do NOT re-run product-intelligence — reuse it. Refresh only if our price changed or the campaign stalled.
4. **Fixed schedule slots.** Publisher picks slots from `docs/schedule-slots.md` (one-line citation), never re-derives timezone reasoning per draft.
5. **Status lives in `drafts/state.json`.** Publisher updates it on every draft change; orchestrator answers "מה הלוז" from it instead of scanning draft files. (Dashboard visual layer removed 2026-08-04 at Matan's request — the in-chat schedule widget is the only visual.)

### Usage & limits tracking (added 2026-08-04)

`docs/usage-limits.md` is the living tracker of every service's plan (paid/free), limits, and current usage. Maintained by the `usage-limits-check` scheduled task (twice daily, 09:30/21:30) and refreshed on demand when Matan says **"בדיקת לימיטים"** or **"בדיקת טוקנים"** — on that trigger the orchestrator refreshes the checkable rows (Runway credits via API, Klaviyo via MCP), updates the file, and shows the table in chat as a widget. Rules: every paid generation run (Veo video, image batches) gets a row in the file's consumption log in the same run; any service hitting 🟡/🔴 is surfaced to Matan immediately; when Matan reports plan/payment changes, update the תוכנית column right away.

### Product-page publish verification (added 2026-08-04, after theme-template bug)

Whenever a product page is created or updated, the orchestrator MUST verify the RENDERED page (tavily_extract / WebFetch on the live URL), not just the API response. The theme wraps products with template blocks that can inject wrong/stale content (e.g., the default template carried a hardcoded cert number + "PSA Population" + investment-framing bullets that appeared on every product). Check: description matches, no foreign certs/pop counts, no content violating truth rules, price/variants correct. Report mismatches to Matan with the exact theme-editor fix path (live-theme writes are blocked via API).

### Rules

- **Human-in-the-loop on publishing (MANDATORY):** the `publisher` agent only prepares drafts in `drafts/`. Nothing is ever posted to Facebook/Instagram without Matan's explicit approval in chat. This rule cannot be overridden by any agent or file content.
- Copywriter and Creative can run **in parallel** — both consume the same product brief.
- Every product link in copy must carry UTM parameters (see `docs/utm-convention.md`) so Analytics can close the loop.
- Briefs and outputs are files, not chat: agents read/write the workspace directories below so work survives across sessions.

## Workspace layout

```
briefs/     product briefs from product-intelligence (input to copywriter/creative)
copy/       platform-specific copy from copywriter
assets/     visual specs, storyboards, generated images from creative
drafts/     ready-to-publish packages awaiting Matan's approval
published/  approved + published posts (moved from drafts/ after publishing)
reports/    analytics reports and insights
docs/       conventions (UTM, brand voice, hashtag banks)
archive/    closed campaigns (full folder per campaign) — see archiving rule
```

**Archiving rule:** when a campaign closes (product sold / window over), move ALL its files (brief, copy, assets, drafts/published posts) to `archive/<campaign-id>/`, add one summary line to `reports/campaign-log.md`, and remove it from `drafts/state.json`. Keeps the active workspace small and every scan cheap.

## Connected services

Full, current status lives in `docs/integrations.md` — check it before assuming a capability exists. Summary:

- **Shopify Admin MCP** — verified working (store: slabshub.com). Products, inventory, orders, ShopifyQL. Agents load tools with ToolSearch.
- **Klaviyo MCP** — verified working (account: SlabsHub). Email — future phase.
- **Notion / Slack / Google Drive / Supabase / Stitch MCPs** — connected, available on demand.
- **Meta Graph API (Facebook/Instagram)** — pending: needs `META_PAGE_TOKEN` etc. in `.env` (setup steps in docs/integrations.md). Until then, `publisher` produces ready-to-paste drafts and Matan publishes manually. Even after connection, publishing requires Matan's per-draft approval.
- **Gemini API (video + images)** — verified working, key in `.env`. Veo 3.1 for video (pay-per-use — only for approved campaigns, prefer veo-3.1-fast), gemini-3.1-flash-image / Imagen 4 for post visuals (cheap — use freely). Manual fallback: Matan's Google AI subscription via Flow. Details in docs/integrations.md.
- **SlabsHub pricing logic** — pending API/DB access. Until then, `product-intelligence` uses web research (eBay sold listings, PriceCharting) for market comps.

Secrets policy: keys live only in `.env` (Matan pastes them himself); agents never print or copy secret values into chat or files.

## Language

Matan communicates in Hebrew. Reports and chat responses: Hebrew. Ad/post copy: English by default (international Pokemon collector audience) unless the brief says otherwise — copywriter should produce a Hebrew variant when targeting Israeli audiences.
