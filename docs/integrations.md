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

**Audit 2026-08-17 (token verified live against Graph API):**
- `META_PAGE_TOKEN` is set and VALID — but it is a **user token** (identity: Matan Bar Chen, id 122374206914002189), not a Page token.
- Granted scopes: ads_management, ads_read, business_management, pages_show_list, pages_read_engagement, pages_manage_metadata, pages_manage_ads, pages_messaging, instagram_basic, publish_video, catalog_management, leads_retrieval, whatsapp_*.
- **Missing scopes for organic publishing:** `pages_manage_posts` (FB feed posts), `instagram_content_publish` (IG posts), `read_insights`.
- **Token sees NO pages:** `/me/accounts` is empty and Business "SlabsHub.com" (id 1384456153755717) has no owned/client pages. Either no FB Page is linked to the business, or the page wasn't selected during the OAuth grant.
- `META_PAGE_ID` in `.env` is WRONG — it holds Matan's user id, not a page id. `META_IG_USER_ID` is EMPTY.
- **Paid side is closer to ready:** ad account `act_631106849003586` is ACTIVE and ads_management is granted — but ad creation still needs a Page identity, so the page gap blocks paid too.

**Fix path (Matan, ~15 min):**
1. Verify the SlabsHub Facebook Page exists and is connected to Business Manager "SlabsHub.com"; link the IG professional account to that page.
2. Re-run the token grant (Graph API Explorer or Facebook Login for Business) adding `pages_manage_posts`, `instagram_content_publish`, `read_insights` — and select the SlabsHub page in the asset picker during the grant.
3. Then the orchestrator finishes the rest: pull the Page id + Page access token from `/me/accounts`, pull the IG user id from the page, and Matan pastes the corrected `META_PAGE_TOKEN` / `META_PAGE_ID` / `META_IG_USER_ID` into `.env`.

**App identifiers (confirmed 2026-09-04 from Meta's "Getting Started with Marketing API" email):**
- App: `slabshub.com` — App ID `1385848300175812`
- Business: `SlabsHub.com` — Business ID `1384456153755717`
The app itself exists and is live; the gap is purely the Page link + the missing publishing scopes on the token.

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
