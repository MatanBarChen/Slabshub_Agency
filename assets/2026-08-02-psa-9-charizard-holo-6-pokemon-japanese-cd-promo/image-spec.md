# Image Spec — PSA 9 Charizard Holo #6, Japanese CD Promo

Campaign date: 2026-08-02
Product: https://slabshub.com/products/psa-9-charizard-holo-6-pokemon-japanese-cd-promo
Price: $1,199 (recent PSA 9 eBay sales: $1,250–$1,450 — copy-safe comp claim)

## Base images (Shopify CDN)

- **Front (primary base for all placements):**
  https://cdn.shopify.com/s/files/1/0622/2069/7711/files/Charizard_Holo_6PokemonJapaneseCDPromo.png?v=1746856362
- Back (carousel slide 2 / story frame 2 only — authenticity shot):
  https://cdn.shopify.com/s/files/1/0622/2069/7711/files/BACKCharizard_Holo_6PokemonJapaneseCDPromo.png?v=1746856362

## Generated hero: `promo-main.png` (in this folder)

AI-composited scene (Gemini 3.1 Flash Image): original slab photo placed on a near-black
charcoal studio set, ember-orange rim light from below/behind, rising embers and faint heat
shimmer around (never over) the slab, warm reflection on a dark glossy floor. Top ~20% left
dark and clean for text overlay. 4:5 (928x1152 — upscale to 1080x1350 on export).

**Verified:** PSA label is fully legible and correct ("1998 P.M. JAPANESE / CHARIZARD – HOLO /
CD PROMO / #6 / MINT 9 / 10017252"), card artwork and layout faithful at feed viewing size.
Known limitation: the card's tiny Japanese body text softens under extreme zoom (>2x) —
irrelevant at feed size, but do NOT use promo-main.png for close-up crops of the card text.
For close-ups, crop the original Shopify photo instead. `promo.html` is the no-AI fallback.

## Placements

### 1. IG feed — 1080x1350 (4:5)
- Base: `promo-main.png` (already 4:5).
- Slab occupies lower two-thirds, centered; do not crop any slab edge, label always fully visible.
- Text overlay, top dark zone, centered, white, bold, tight tracking:
  **"THE 1999 CD PROMO CHARIZARD"** (5 words, ~64px at 1080w)
- Price badge: bottom-right, pill, ember-orange (#FF7A1A) on near-black, white text **"$1,199"**;
  small caps line above it: "PSA 9 MINT" in muted gold (#D9B36B).

### 2. IG story — 1080x1920 (9:16)
- Extend promo-main.png top/bottom with solid near-black (#0B0908) + a few ember specks
  (or regenerate at 9:16 if needed). Slab centered vertically, ~55% of frame height.
- Frame 1 overlay (top): **"RECENT SALES: $1,250–$1,450"** (small, muted) above
  **"OURS: $1,199"** (large, ember-orange). Both ≤6 words.
- Bottom: link sticker zone kept clear (bottom 250px). CTA text: **"One copy. Tap to shop."**
- Optional frame 2: back-of-slab Shopify photo on the same black treatment, overlay
  **"Cert 10017252. Verify it."**

### 3. FB ad — 1080x1080 (1:1)
- Center-crop promo-main.png to square, biased downward so the full slab + reflection stay
  in frame and the label keeps ≥60px clearance from the top edge.
- Overlay top-left: **"PSA 9. UNDER RECENT SALES."** (4 words). Price pill bottom-right as feed.
- Keep 20% text-coverage discipline for ad delivery.

## Style rules applied
- Palette: near-black #0B0908 background, ember orange #FF7A1A accents, muted gold #D9B36B,
  white text. High contrast, premium collector look.
- The slab is the hero; the PSA label is the trust signal — never cropped, never covered.
- No extra Pokemon IP (no pokeballs, logos, character art) beyond the product photo itself.
- Max 6 words per text overlay.
