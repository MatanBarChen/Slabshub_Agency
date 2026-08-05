# Image Spec — CGC 7 Eevee [1st Edition] #51 Pokemon Jungle (stale-inventory push)

**Campaign date:** 2026-08-05
**Brief:** briefs/2026-08-03-eevee-1st-edition-51-pokemon-jungle-graded-7-cgc.md
**Copy:** copy/2026-08-05-eevee-jungle-cgc7.md
**Base product image (Shopify, front):** https://cdn.shopify.com/s/files/1/0622/2069/7711/files/CGC7Eevee_51PokemonJungle.jpg?v=1746460932
**Generated assets:** `promo-feed-1080x1350.png`, `promo-story-1080x1920.png` (in this directory)

Scope note: this is a $24.99 stale card (476 days listed, 0 sold trailing 365d). Lean deliverable —
one feed visual + one story variant, no video/Veo, no ad-format square (paid not approved), no
promo.html (Gemini generation succeeded).

## Visual concept

Warm 1999 WOTC Jungle-era nostalgia, distinct from the cooler psychic-purple / moonlit-dark
treatments used on other campaigns. Near-black espresso-brown canvas with a soft amber-gold
spotlight glow rising from behind the slab (like candlelight/firelight), fine film grain, gentle
vignette, faint glossy floor reflection below the case. Reads as "the original vintage Eevee, lit
like a museum piece" — matches the "OG Eevee before the Eeveelutions" hook in the copy.

## Placements

### Feed — `promo-feed-1080x1350.png` (4:5, IG feed / also works as FB feed post)
- CGC 7 slab centered, ~62% of frame height, pixel-exact to the source photo, full grading label
  visible (Near Mint 7, Centering/Surface/Corners/Edges subgrades, "Jungle - 1st Edition - 51/64").
- Background: near-black base, warm amber radial glow top-to-center, soft charcoal "platform" the
  slab rests on, faint floor reflection beneath.
- **Text overlay to add in posting tool (not baked in — keeps copy editable per the umbreon-campaign
  lesson: baking text via image-gen risks corrupting real card text elsewhere in the frame):**
  - Top safe zone: **"1999. 1st Edition. The OG Eevee."** (6 words, from copy Frame 1 hook)
  - Price badge, bottom-right, gold-edged dark pill: **$24.99**
  - Small tag bottom-left, uppercase/letterspaced: **"CGC 7 · 1 IN STOCK"**
- No market/discount comparison on-image — brief flags comps as unverified, so keep the on-image
  claim to price + scarcity only (matches copy's no-dollar-gap rule).

### Story — `promo-story-1080x1920.png` (9:16, IG/FB Story)
- Same amber-glow system extended vertically, slab centered at ~50% frame height with more
  headroom/footroom for the spotlight cone and reflection.
- Text overlay to add in posting tool, 3-frame script from copy:
  - Frame 1: **"1999. 1st Edition. The OG Eevee. 🧡"**
  - Frame 2: **"CGC 7, Near Mint. Jungle set. Only 1 in stock."**
  - Frame 3: **"$24.99 — swipe up to see the card →"**
- Keep bottom ~250px clear for the link-sticker zone.

## Rules applied
- Max 6 words per on-image text frame (overlay text listed above, to be added in the posting tool).
- No Pokemon logos/IP added beyond the actual product photo — set stamp, "1st Edition" mark, and
  copyright line visible on the card are original to the photo, not added.
- Grading label never cropped — full CGC label with subgrades stays in frame in both placements.
- No invented cert numbers or card details — CGC 7, Jungle, 1st Edition, 51/64 all read directly
  off the real product photo.
- No price/market dollar-gap claim on-image (comps unverified per brief warning) — price + scarcity
  only.

## Generated asset — method

- **Two-stage generation** (same approach validated on the 2026-08-04 Umbreon campaign, which
  found that asking Gemini to composite+relight the card directly corrupts small card text):
  1. Generated the amber/vintage background **only** via Gemini text-to-image
     (`gemini-3.1-flash-image`, prompt explicitly excludes any card/text/logo) — zero text-corruption
     risk since no card content is in the generation prompt.
  2. Downloaded the real Shopify product photo (front image), cropped only to remove the storefront's
     social-icon watermark strip below the case (case and full grading label untouched), then
     composited the **unmodified card crop** onto the generated background programmatically
     (Python/Pillow — feathered edge blend, soft drop shadow, faint floor reflection, light corner
     vignette).
  3. This guarantees the card pixels are the real photo: CGC 7, "Jungle - 1st Edition - 51/64",
     subgrades (9/7/7/7.5), Eevee card text/art all byte-identical to the source.
- Fidelity check: grade, set line, cert subgrades, card name/HP/attack text, edition mark, and
  copyright line all confirmed identical to the source photo in both output files.
- `product.jpg` in this folder is the untouched downloaded source photo (front) used for the composite.
- No text baked into either PNG — hook/price/tag overlays are added in the posting tool per
  placement, per the "keep copy editable, avoid AI-text-corruption" rule established on the Umbreon
  campaign.

## Cost estimate

- 2x Gemini image-generation calls (`gemini-3.1-flash-image`, background-only, no card content) —
  well under $0.01 total (image generation is "cents" per docs/integrations.md; no Veo/video used).
- Compositing done locally with Python/Pillow — $0.
- **Total run cost: negligible (well under $0.05).** Orchestrator: please log this run in
  `docs/usage-limits.md` consumption log (Gemini API, image gen, 2026-08-05, ~$0.01 est.).
