# Image Spec — Slab Guard (Silicone Bumper for PSA Slabs)

Campaign: 2026-08-04-slab-guard-launch
Product: https://slabshub.com/products/slab-guard-silicone-bumper-for-psa-graded-slabs
Language: **Hebrew only** (primary), all overlays RTL-aligned. Niche English terms (PSA) kept as-is per how Israeli collectors actually write.
Prices in content: **₪19** solid / **₪22** glitter — the live store prices (Shopify variants SG-SOLID / SG-GLITTER, verified 2026-08-26). The store sells in USD only, so visuals and copy both quote USD.
> Corrected 2026-08-26. This spec previously said ₪19/₪22 and told visuals to hide the USD price; that no > longer matched the store and would have advertised a price the checkout does not charge.
Promo (automatic in cart): קונים 3 ומעלה — 15% הנחה אוטומטית בקופה. Use as a small secondary badge, not the headline (headline stays product/color-led).

## Base images (source photos)

- **Solid colors (6-frame fan)** — primary hero base:
  Local: `assets/slab-guard/photos/slab-guard-solid-colors.jpg`
  CDN: https://cdn.shopify.com/s/files/1/0622/2069/7711/files/slab-guard-solid-colors_9f4e39d2-6dea-45a5-9eaf-c2cb9ea945ac.jpg
- **Glitter/gradient (4-frame fan)** — premium-tier base:
  Local: `assets/slab-guard/photos/slab-guard-glitter-gradient.jpg`
  CDN: https://cdn.shopify.com/s/files/1/0622/2069/7711/files/slab-guard-glitter-gradient_6d8631f2-bca4-4737-b2cb-26c4c0f5c629.jpg

## Generated hero: `promo-main.png` (in this folder)

AI composite (Gemini 3.1 Flash Image, image-to-image): input was the real solid-colors fan photo; the model was
instructed to preserve the six frames exactly as photographed (same shapes/colors/count/arrangement, no redraw, no
added text or logos) and recompose them onto a near-black charcoal studio backdrop with soft upper-left key light,
a subtle warm gold rim light, and a dark glossy floor reflection. Top ~25% left dark/clean for a text headline;
bottom ~15% left clean for a price badge. 928x1152 (~4:5) — upscale to 1080x1350 on export.

**Verified:** all six frames present, colors accurate to source (pink, purple, blue, mint, yellow, red), fan
arrangement unchanged, no artifacts on the product itself, no added text/watermark/logo. This is a playful-premium
accessory shot, not a museum/grail treatment — colors are the hero, energy stays bright against the dark canvas.

## Placements

### 1. IG feed — 1080x1350 (4:5) — primary hero
> **Built:** `ig-feed-1080x1350.png` (26.08.2026), overlay burned in via `scripts/slab_guard_hero.py`.
> Clean no-overlay twin for FB organic: `fb-organic-1080x1350-clean.png`.
- Base: `promo-main.png`, upscaled to 1080x1350 (already 4:5, no cropping needed).
- Color fan centered, occupying the lower two-thirds; do not crop any frame at the left/right edges.
- Text overlay, top dark zone, right-aligned RTL, white, bold, tight tracking:
  **"הסלאב שלך. הצבע שלך."** (4 words)
- Price badge: bottom-right, pill, gold (#D9B36B) on near-black, white text **"₪19"**;
  small caps line above it in muted white: "סיליקון ל-PSA".
- Secondary micro-badge, bottom-left, small pill: **"3+ = 15% הנחה"**.

### 2. IG story — 1080x1920 (9:16)
- Extend `promo-main.png` top/bottom with solid near-black (#0B0B0D) to fill the taller canvas (pad, do not
  re-crop the fan — cropping risks cutting the leftmost/rightmost frames).
- **Frame 1:** overlay top-right RTL: **"שישה צבעים חדשים הגיעו"** (4 words). Bottom sticker zone (last 250px)
  kept clear for the native link sticker. CTA text above it: **"לינק בביו"**.
- **Frame 2** (optional second card): glitter/gradient CDN photo on the same dark treatment, overlay:
  **"קולקציית הגליטר הפרימיום"** (3 words), price badge **"₪22"**.

### 3. FB ad — 1080x1080 (1:1)
- Center-crop `promo-main.png` to square, biased toward the bottom (keep the fan + floor reflection in frame);
  full image width is already narrower than the fan spread so no color frame is cut at the left/right edges —
  verify at export regardless.
- Overlay top-right RTL: **"6 צבעים. סלאב אחד."** (4 words). Price pill bottom-right as in the feed version.
- Keep to the ~20% text-coverage discipline for ad delivery.

## Missing asset — flag for Matan

We do not yet have a photo of the guard actually mounted **on** a graded slab — this would be the single
strongest asset for this launch (proof of fit + the actual use case, not just the accessory in isolation).
Recommended shot list for Matan to capture:
1. **Guard on slab, straight-on front shot** — PSA label fully legible through/around the guard, even studio
   lighting, dark backdrop to match this campaign's palette.
2. **Corner close-up macro** — one corner of the slab with the guard snugly wrapped around the edge, shows the
   fit quality (this is the category's #1 complaint area — a good macro shot pre-empts "does it actually fit"
   objections).
3. **Hand mid-snap onto the slab** — the guard being pressed/snapped into place, ideally mid-motion, catches
   the satisfying "click" moment. This shot alone would upgrade the video hook (see storyboard shot 1) from a
   static zoom to a real product-in-use hook.

Once any of these exist, re-run creative to regenerate `promo-main.png` and the video hook around the real
in-use shot — it will outperform the isolated color-fan hero for conversion-driving placements (FB ad, story
frame 1).

## Style rules applied
- Palette: near-black (#0B0B0D) background, product colors as the only accent (no imposed color scheme), gold
  (#D9B36B) for price badges to match SlabsHub's existing trust-signal convention.
- Playful-premium energy — bright, high-contrast, not somber. This is an accessory launch, not a grail card.
- No Pokémon IP beyond the product photo itself.
- Max 6 words per text overlay; all overlays right-aligned RTL.
