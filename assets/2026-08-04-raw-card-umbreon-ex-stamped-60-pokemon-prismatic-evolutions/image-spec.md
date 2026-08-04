# Image Spec — RAW Umbreon ex [Stamped] #60/131 (Prismatic Evolutions)

**Campaign date:** 2026-08-04
**Base product image (Shopify):** https://cdn.shopify.com/s/files/1/0622/2069/7711/files/Umbreonex_Stamped_60PokemonPrismaticEvolutions.png?v=1747635903
**Generated hero image:** `promo-main.png` (in this directory) — see "Generated asset" below.

## Visual concept

Umbreon owns **dark/moonlight**, not psychic-purple (that's Mewtwo's lane — keep this one distinct).
Near-black canvas, a deep midnight-blue radial glow behind the card, thin **golden ring light-trails**
echoing Umbreon's signature yellow rings drifting through the lower third, a soft crescent-moon-colored
silver glow entering from the upper-left, and a faint glossy-floor reflection below the card. The card
stays sealed in its protective sleeve exactly as photographed — that sleeve is part of the "stamped
promo, never opened for grading" story, not something to strip away.

## Placements

### IG feed — 1080x1350 (4:5) — primary
- Card+sleeve centered, ~66% of frame height, sharp, pixel-exact to the source photo.
- Background: #08090d base, midnight-blue radial glow center-low, golden ring trails left/right,
  crescent-moon silver glow top-left, glossy floor reflection bottom.
- Text overlay (top safe zone, above card): hook, max 6 words —
  **"Surprise Box exclusive. Stamped. $24.99."** (trim to fit; primary short version: **"The stamped Umbreon. Priced below market."**)
- Price badge: bottom-right, pill, gold-edged dark fill: **$24.99** with micro-label
  "market ~$30" beneath (small, honest; full comp detail + date stays in the caption, not on-image).
- Small tag bottom-left, uppercase, letterspaced, 60% white: **"RAW · STAMPED · 1 LEFT"**.

### IG story — 1080x1920 (9:16)
- Same background system, extend canvas vertically (add more near-black + faint gold trail at
  top and bottom); card at ~55% height, centered slightly above middle.
- Top text: **"The accessible Umbreon."** Bottom third: **"$24.99 — pack-exclusive stamp."** +
  link sticker zone left clear (bottom 250px).

### FB ad / square — 1080x1080 (1:1)
- Card shifted left-of-center at ~68% height; right column stacks: hook line, price badge,
  "Shop now" ghost button. Same dark moonlit background, crop the golden trails to fit square.

## Rules applied
- Max 6 words per text overlay.
- No Pokemon logos or extra IP added — only the product photo itself (set logo/stamp visible on
  the card are part of the original photo, not added).
- RAW card, no grade claims. Do not conflate with the #161 SIR "Moonbreon" chase card in copy or
  on-image text — this is the stamped promo variant, explicitly "the accessible Umbreon."
- Comp range is wide ($22–$197, market down 61% since release per brief) — keep on-image price
  comparison to a soft "below market" claim, not a specific dollar-gap number.

## Generated asset — promo-main.png

- **Method:** two-stage generation, not a single AI edit of the card. A first attempt asking
  Gemini (`gemini-3.1-flash-image`) to composite+relight the card directly produced text corruption
  (misspelled "Evolves from Eevee" → "Fevee", wrong card number 060/151 vs the real 060/131, garbled
  set-logo text, wrong copyright year) — unacceptable for a product image where the card number and
  identity must be accurate. Rejected.
- **Fix:** generated the moonlit background *only* via Gemini text-to-image (no card in the prompt,
  so zero text-corruption risk), then composited the **actual, unmodified Shopify product photo**
  onto it programmatically (Python/Pillow — feathered edge mask + vignette blend + soft floor
  reflection). This guarantees the card pixels are byte-for-byte the real photo: 100% pixel-faithful,
  card number 060/131 and all text exactly as printed.
- Fidelity check: card number, "Evolves from Eevee," attack text, set stamp, illustrator credit,
  and copyright line all confirmed identical to the source photo.
- `product.png` in this folder is the untouched downloaded source photo used for the composite.
- **No text baked in** on promo-main.png — overlay the hook/price in the posting tool so copy stays
  editable per placement.
