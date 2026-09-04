# Integrations Status — SlabsHub Agency

Last verified: 2026-08-04

## ✅ Connected & verified (working now)

| Service | What it gives us | Used by |
|---|---|---|
| **Shopify Admin MCP** | Products, prices, inventory, orders, ShopifyQL analytics, collections, discounts, image upload | product-intelligence, analytics, publisher |
| **Klaviyo MCP** | Email campaigns, lists/segments, templates, flows, coupons (account: SlabsHub, ILS) | future email agent |
| **Notion MCP** | Docs/databases — can host campaign calendar & approval board | orchestrator |
| **Slack MCP** | Notifications/approvals channel if wanted | orchestrator |
| **Google Drive MCP** | Read shared assets (product photos, brand files) | creative |
| **Stitch MCP** | UI/screen design generation | creative (experimental) |
| **Tavily MCP** | Live web access: `tavily_search`, `tavily_extract`, `tavily_crawl`, `tavily_map`, `tavily_research` — market comps (eBay sold, PriceCharting), trend research (verified 2026-08-04) | product-intelligence, analytics, design-agent |
| **Scheduled tasks** | Cron triggers — weekly campaign, stale-inventory scan | orchestrator |

## 🔑 Connected but awaiting Matan's authorization (OAuth)

These appear in the workspace but need a one-time authorization in **claude.ai → Settings → Connectors** (or `/mcp` in an interactive `claude` terminal):

| Connector | Why we want it | Priority |
|---|---|---|
| **Canva** (plugin:marketing:canva) | Real branded post/story designs instead of HTML mockups | ✅ AUTHORIZED by Matan 2026-08-04 — tools load from the next session; verify with ToolSearch "canva" and move to the Connected table |
| **Ahrefs** (plugin:marketing:ahrefs) | SEO/keyword data for store pages | LOW (later phase) |
| **Supermetrics** (plugin:marketing:supermetrics) | Cross-channel ad metrics aggregation | LOW (needs paid account) |

Note: plugin:marketing:klaviyo is redundant — the direct Klaviyo MCP is already connected. Ignore it.

## ❌ Not available as MCP — connect via direct API (keys in `.env`)

### 1. Meta Graph API (Facebook + Instagram) — publishing & insights

**Status 2026-09-04 — ✅ CONNECTED. Verified end-to-end against the live Graph API.**

| Asset | Value | State |
|---|---|---|
| App | `Slabshub_Agency` — app id `1544161646661896` | the token was issued by this app, not by `slabshub.com` (`1385848300175812`); both exist under the business |
| Business | `SlabsHub.com` — `1384456153755717` | ✓ |
| Page | `Pokeslabshub` — `1361507090367793` | ✓ created 2026-09-04, business-owned, page token derived and reads fine |
| Instagram | `pokeslabshub` — `17841426420081172` | ✓ professional, linked to the page, 1,572 followers / 71 posts |
| Scopes | pages_show_list, pages_read_engagement, pages_manage_posts, instagram_basic, instagram_content_publish, read_insights | ✓ all six granted, none declined |
| Ad account | `1081186441399359` (Slabshub_Agency) | differs from `act_631106849003586` in the old audit — reconcile before the first paid run |

`META_PAGE_ID` and `META_IG_USER_ID` are now correct in `.env` (written by the orchestrator 2026-09-04).

**Token:** `META_PAGE_TOKEN` holds the LONG-lived user token, valid until **2026-11-03**. The page token derived from it (`GET /{page-id}?fields=access_token`) came back with `expires_at=0` — **it never expires** — and carries all six scopes plus public_profile. So the November date is not a cliff: derive the page token once and it keeps working. Re-do the extend flow only if the user token is ever revoked.

IG publishing quota checked live: `GET /{ig-user-id}/content_publishing_limit` → 0 of 25 posts used in the rolling 24h window.

Quirk worth remembering: `/me/accounts` returns an EMPTY list even though everything works — business-owned pages under the new Pages experience are not listed there for this app. Do NOT read that as "no page". Read the page node directly instead: `GET /1361507090367793?fields=access_token` returns the page token, and `?fields=instagram_business_account` returns the IG id.

Original setup steps (reference):
1. https://developers.facebook.com → Create App (type: Business).
2. Add products: **Facebook Login for Business** + permissions `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`, `read_insights`.
3. Link the app to the SlabsHub Facebook Page and the Instagram professional account.
4. Generate a **long-lived Page access token** (Graph API Explorer → extend token) and put it in `.env` as `META_PAGE_TOKEN`, plus `META_PAGE_ID` and `META_IG_USER_ID`.

Key endpoints the publisher will use (only after Matan approves each draft in chat):
- FB post: `POST https://graph.facebook.com/v21.0/{page-id}/feed` (`message`, `link`)
- FB photo post: `POST /{page-id}/photos` (`url`, `caption`)
- IG post (2 steps): `POST /{ig-user-id}/media` (`image_url`, `caption`) → `POST /{ig-user-id}/media_publish` (`creation_id`)
- IG Reel: `POST /{ig-user-id}/media` (`media_type=REELS`, `video_url`) → poll status → `media_publish`
- Insights: `GET /{ig-media-id}/insights?metric=reach,likes,shares,saved` / `GET /{page-post-id}/insights`

Human-in-the-loop stays mandatory even after this is wired: token in place ≠ auto-publish.

### 1b. n8n (planned) — triggers + approval-gated auto-publishing
Full plan in `docs/n8n-integration.md`. Blocked on the same Meta token as above; uses Supabase as the publish queue between Claude Code and n8n. Human approval (Telegram button) stays mandatory per post.
NOTE (2026-08-31): a SlabsHub Supabase project now exists — `SlabsHub_Chat` / `uvlkacfnbnsqpizktcfi`, free tier, created to host the storefront chat (section 1c). n8n can reuse it as the publish queue; no second project needed.

### 1c. Storefront chat — Supabase Edge Function ✅ LIVE (deployed 2026-08-31)
The on-site chat runs in the cloud 24/7, so it no longer depends on Matan's desktop being on.

- **Project:** `SlabsHub_Chat` / `uvlkacfnbnsqpizktcfi`, region Frankfurt (eu-central-1), **free tier — $0/month**.
- **Endpoint:** `https://uvlkacfnbnsqpizktcfi.supabase.co/functions/v1/chat` (function slug `chat`, `verify_jwt=false` — storefront visitors are anonymous).
- **Secret:** `ANTHROPIC_API_KEY` lives only in Supabase Edge Function secrets. Matan sets it himself; it is never in code, git or the browser. `GET` on the endpoint reports whether it is present.
- **Cost shape:** function invocations are free within 500K/month; the only spend is Anthropic tokens per conversation. Throttled at 40 messages/hour/IP so an open endpoint cannot run up the bill.
- **Data:** catalog, deployed system prompt, conversations, wishlist, demand and handoffs are all Postgres tables with RLS on and no policies — only the function's service role reads them. Customer contact details live in `wishlist` and stay there (CLAUDE.md rule unchanged).
- **Source of truth stays in git:** `prototype/sales-agent/system-prompt.md` and `catalog.json`; `prompt_to_sql.py` / `catalog_to_sql.py` push them to the cloud without a redeploy. Full runbook in `prototype/sales-agent/README.md`.

### 2. Video & image generation — Gemini API ✅ CONNECTED (verified 2026-08-02)
`GEMINI_API_KEY` is set in `.env` and verified. Available models confirmed on this key:
- **Video:** `veo-3.1-generate-preview` (top quality), `veo-3.1-fast-generate-preview` (cheaper/faster — default), `veo-3.1-lite-generate-preview`
- **Images:** `gemini-3.1-flash-image` (fast edits/compositing — default), `imagen-4.0-generate-001` (highest quality stills)
- Creative agent may call these via Bash (curl), reading the key from `.env` — never printing it.
- Cost note: Veo is pay-per-use (~$1.5–6 per 8s clip). Prefer `veo-3.1-fast` and generate only for approved campaigns, not exploratory drafts. Images cost cents — use freely.
- If a call returns quota/billing errors, billing may need enabling in Google AI Studio — fall back to the manual Flow workflow below.

#### Runway API — key verified 2026-08-04, ⚠ 0 credits
`RUNWAY_API_SECRET` in `.env`, validated against /v1/organization. Blocked on credit top-up (Matan's call). When funded, notable models for us beyond gen4_turbo video: `product_swap`, `product_ugc`, `product_campaign_image` (purpose-built product-marketing generators), `multi_shot_video`. Until then: Veo via Gemini API is the video engine.

#### ✅ PRIMARY video workflow — Flow via browser automation (verified 2026-08-05)
The orchestrator drives Flow (labs.google/flow) in Matan's real Chrome via the Claude-in-Chrome extension, using his Google AI Pro subscription (₪45/month) — zero cash per clip. Verified end-to-end on the Umbreon ring-light clip (15 credits). Flow model picker: Veo 3.1 Fast is our default; settings pinned to 9:16, x1 output, confirm-before-generating Always.
Steps: open Flow project → Matan clicks "Upload media" for the start frame (native file dialog — the ONE manual step; his click, not the extension's) → orchestrator pastes the prompt, sets model/aspect, sends, approves the credit confirmation, waits (~2-4 min), downloads → file moved into `assets/<campaign>/`.
Limits: needs Matan present with Chrome open (won't work from scheduled tasks); brittle to Flow UI changes; 2FA prompt on first login of a session. API Veo (pay-per-use) stays as the fallback for hands-off runs.

#### Manual fallback — Veo via Flow, fully by hand
The original hybrid pipeline (kept for when browser automation is unavailable):
1. `creative` writes ready-to-paste Veo prompts in `assets/<campaign>/video-prompts.md`, and names which Shopify product image to upload as the start frame.
2. Matan opens **Flow** (labs.google/flow — supports image-to-video), uploads the card image, pastes the prompt, generates (~30s per clip).
3. Matan saves the .mp4 into the campaign's `assets/` directory; `publisher` attaches it to the draft.

Full API automation (agent generates video itself) would require Gemini API with pay-per-use billing (`GEMINI_API_KEY` in `.env`, model `veo-3.1`, ~$1.5–6 per 8s clip) — deliberately deferred; the subscription flow is free and good enough.

### 3. SlabsHub pricing logic
When Matan provides the SlabsHub API/DB access (`SLABSHUB_API_URL` + key, or Supabase table), product-intelligence switches from web-comps to authoritative market values. The Supabase MCP is already connected — if SlabsHub data lives in Supabase, this is zero extra setup: just tell the orchestrator the project/table name.

## .env convention

Secrets live in `C:\Users\matan\Desktop\Slabshub Agency\.env` (never committed, never printed in chat/files). Matan pastes keys himself — agents only read variable names, and reference them as env vars in scripts.

```
META_PAGE_TOKEN=
META_PAGE_ID=
META_IG_USER_ID=
GEMINI_API_KEY=        # or RUNWAY_API_SECRET
SLABSHUB_API_URL=
SLABSHUB_API_KEY=
```
