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
The single most important missing piece. Setup (Matan does once, ~30 min):
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
NOTE (2026-08-03): no SlabsHub Supabase project exists yet (the two projects on the account belong to other ventures, both inactive) — creating one is a cost decision for Matan, pending.

### 2. Video & image generation — Gemini API ✅ CONNECTED (verified 2026-08-02)
`GEMINI_API_KEY` is set in `.env` and verified. Available models confirmed on this key:
- **Video:** `veo-3.1-generate-preview` (top quality), `veo-3.1-fast-generate-preview` (cheaper/faster — default), `veo-3.1-lite-generate-preview`
- **Images:** `gemini-3.1-flash-image` (fast edits/compositing — default), `imagen-4.0-generate-001` (highest quality stills)
- Creative agent may call these via Bash (curl), reading the key from `.env` — never printing it.
- Cost note: Veo is pay-per-use (~$1.5–6 per 8s clip). Prefer `veo-3.1-fast` and generate only for approved campaigns, not exploratory drafts. Images cost cents — use freely.
- If a call returns quota/billing errors, billing may need enabling in Google AI Studio — fall back to the manual Flow workflow below.

#### Runway API — key verified 2026-08-04, ⚠ 0 credits
`RUNWAY_API_SECRET` in `.env`, validated against /v1/organization. Blocked on credit top-up (Matan's call). When funded, notable models for us beyond gen4_turbo video: `product_swap`, `product_ugc`, `product_campaign_image` (purpose-built product-marketing generators), `multi_shot_video`. Until then: Veo via Gemini API is the video engine.

#### Fallback / zero-cost workflow — Veo via Matan's Google AI subscription
Matan has a Google AI subscription that includes Veo. The working pipeline is hybrid:
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
