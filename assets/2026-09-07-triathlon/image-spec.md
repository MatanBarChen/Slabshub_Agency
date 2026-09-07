# Image Spec — Triathlon Campaign (2026-09-07)

3 products × 3 days × 2 posts = 18 posts. Copy: `copy/2026-09-07-triathlon.md` (already written in
parallel — this mapping was checked against its "ויז'ואל:" lines per post and adjusted where a real
photo / IP-safety constraint required a different execution; deviations are called out inline).

Language on all visuals: **no baked-in text from the Gemini generation step** (Hebrew corrupts in
AI-generated images; per-brief rule, we never bake Hebrew into a model-generated image). Where a post
needed a number/price/data callout, it was added as a **programmatic Pillow text overlay** (digits,
`₪`/`$` symbols and English words only — no Hebrew glyphs, no shaping/bidi risk) directly onto the
finished composite, never through the Gemini prompt. All Hebrew copy stays in the caption, matching
established practice from the Eevee/Umbreon campaigns.

Every visual is built from a **real Shopify product photo** composited onto a Gemini-generated
*empty* background (no card/product ever in the generation prompt — zero risk of AI corrupting card
text, cert numbers, or grading labels). No Pokemon IP was added beyond what's already printed on the
real product photos.

## Method (same pipeline for all 3 products)

1. `scripts/gemini_image.py` — generated 8 empty premium-background plates (no product, no text), one
   per visual identity: Slab Guard ×2 (glitter-pink/mint, spectrum), Mewtwo ×2 (psychic ascension,
   balanced comparison), Jigglypuff ×4 (pastel-neon intro, museum spotlight, mysterious rarity,
   cinematic neon-crossbeam grail).
2. Downloaded/reused real product photos (Jigglypuff: 4 Shopify CDN images; Mewtwo: existing
   `product.png`/`promo-main.png` from the 2026-08-02 campaign; Slab Guard: existing photos from
   `assets/slab-guard/photos/` and the 2026-08-04 launch composite).
3. Composited the **unmodified** product photo onto each background locally (Python/Pillow):
   feathered rectangular edge blend, soft drop shadow, faint floor reflection, light vignette. No
   redraw, no upscale-hallucination — every card/slab pixel is byte-identical to the source photo.
4. Where copy called for a data/price callout, added it as a Pillow-drawn text bar (see above).
5. Fidelity check on every composite: grading label / cert / card text matches the source photo,
   nothing invented.

Cost: 8 Gemini image-generation calls (background-only, no card content) — logged in
`docs/usage-limits.md`. All compositing/text was done locally with Pillow — $0.

---

## Product 1 — Slab Guard (₪19 solid / ₪22 glitter)

Brief: `briefs/2026-08-04-slab-guard-market.md` · Existing reusable assets:
`assets/2026-08-04-slab-guard-launch/` (promo-main.png, reel-handfan.mp4),
`assets/slab-guard/photos/` (solid-colors.jpg, glitter-gradient.jpg, on-slab.png — real photo of the
glitter guard mounted on a graded slab).

| Post | Day/Time | Platform | Angle | File | Ratio | What's on screen |
|---|---|---|---|---|---|---|
| D1 | 12:30 | facebook-organic | קוד צבעים לאספנים | `slab-guard/d1-fb-colorcode.jpg` | 1:1 | Reused `promo-main.png` (6-color fan, dark studio bg), square crop |
| D1 | 20:30 | instagram-feed (flagship) | תוספת במחיר קפה | `slab-guard/d1-ig-protect-raw.jpg` | 4:5 | Real photo: glitter guard mounted **on an actual graded slab**, cert/label visible through the case; `₪19–₪22` text bar added |
| D2 | 12:30 | instagram-story (3 frames) | הנחה אוטומטית 3+ | `slab-guard/d2-story-f1/f2/f3.jpg` | 9:16 | 3 pan/zoom variants of the color fan, padded to story height, clean top/bottom text zones for the sticker + "15%" graphic Matan adds in the posting tool |
| D2 | 20:30 | facebook-organic | שדרוג נצנצים | `slab-guard/d2-fb-glitter.jpg` | 1:1 | **Adapted from copy's "on-slab" comparison** (we only have one real on-slab photo, used above) — direct side-by-side of the real solid-colors photo vs. real glitter-gradient photo, same premium bg, same treatment |
| D3 | 12:30 | instagram-feed (2nd angle) | מלאי מוגבל אמיתי | `slab-guard/d3-ig-stock.jpg` | 4:5 | Both lines stacked (solid fan + glitter fan) on the spectrum bg; `"25 UNITS. NO RESTOCK DATE."` / `"15 SOLID + 10 GLITTER"` text bar |
| D3 | 20:30 | instagram-story (3 frames) | סגירת מחיר ישירה | **reuse `assets/2026-08-04-slab-guard-launch/reel-handfan.mp4`** | 9:16 video | Existing 8s reel already shows all colors; explicitly pre-approved for reuse in this campaign's brief |

---

## Product 2 — PSA 10 Jigglypuff Japanese Old Maid (₪109)

Brief: `briefs/2026-09-07-psa-10-jigglypuff-japanese-old-maid.md` · New product, no prior assets.
Source photos downloaded to `jigglypuff/`: `front.png` (clean, Jigglypuff illustration side),
`back.png` (clean, Old Maid character-grid back), `img6919.jpg`/`img6921.jpg` (same shots with the
storefront's social-icon watermark strip — not used as composite sources).

| Post | Day/Time | Platform | Angle | File | Ratio | What's on screen |
|---|---|---|---|---|---|---|
| D4 | 12:30 | facebook-organic | מה זה בכלל | `jigglypuff/d1-fb-intro.jpg` | 1:1 | `front.png` on pastel pink/cyan neon bg, full slab legible incl. cert 83965614 |
| D4 | 20:30 | instagram-feed (flagship) | ציון מושלם | `jigglypuff/d1-ig-psa10.jpg` | 4:5 | `front.png` under a museum spotlight beam — "GEM MT 10" label reads clearly, hero shot |
| D5 | 12:30 | instagram-story (3 frames) | הוכחת שוק | `jigglypuff/d2-story-f1/f2/f3.jpg` | 9:16 | **F1:** Pillow data card `$30 · $35.36 · $37` "RECENT PSA 10 SALES (2026)" · **F2:** Pillow data card `₪109` "AT MARKET – NOT A DISCOUNT" · **F3:** real `front.png` product shot |
| D5 | 20:30 | facebook-organic | נדירות אמיתית | `jigglypuff/d2-fb-rarity.jpg` | 1:1 | **Adapted from copy's "next to other Pokemon cards"** — avoided per the no-added-IP rule (we won't fabricate/include other Pokemon cards); used the real `back.png` (unique Old Maid character-grid back) on a moody single-glow bg instead, framed as "this is what makes it different" |
| D6 | 12:30 | instagram-feed (2nd angle) | גראייל לאספנים | `jigglypuff/d3-ig-grail.jpg` | 4:5 | `front.png` on the most dramatic bg — crossing magenta/cyan light beams, cinematic vignette |
| D6 | 20:30 | instagram-story (3 frames) | סגירת מחיר | `jigglypuff/d3-story-f1/f2/f3.jpg` | 9:16 | **F1:** real `front.png` · **F2:** Pillow data card `₪109` "1 UNIT IN STOCK" · **F3:** real `front.png`, cinematic grail bg |

---

## Product 3 — RAW Mewtwo #183 Japanese 151 (₪59)

Brief: `briefs/2026-08-02-raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151.md` · Reused
existing assets from `assets/2026-08-02-raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151/`
(`promo-main.png` psychic hero, `product.png` clean source photo) — no need to redownload.

| Post | Day/Time | Platform | Angle | File | Ratio | What's on screen |
|---|---|---|---|---|---|---|
| D7 | 12:30 | facebook-organic | היכרות עם הקלף | `mewtwo/d1-fb-intro.jpg` | 1:1 | Reused `promo-main.png`, square crop |
| D7 | 20:30 | instagram-feed (flagship) | הפוקימון האייקוני | `mewtwo/d1-ig-iconic.jpg` | 4:5 | Reused `promo-main.png`, tighter zoom crop (different framing from the FB post) |
| D8 | 12:30 | instagram-story (3 frames) | מיקום מול השוק | `mewtwo/d2-story-f1/f2/f3.jpg` | 9:16 | **F1:** real `product.png` on balance bg · **F2:** Pillow VS card `₪59` "OUR PRICE" vs `$19.99–$24.59` "RECENT RAW SALES" · **F3:** real `product.png` |
| D8 | 20:30 | facebook-organic | פוטנציאל דירוג | `mewtwo/d2-fb-grading.jpg` | 1:1 | Real `product.png` on ascension-glow bg + Pillow text bar `"PSA 10 SELLS FOR $125"` / `"SOURCE: PRICECHARTING"` — matches the brief's explicit "no fake PSA slab, real number only" instruction |
| D9 | 12:30 | instagram-feed (2nd angle) | יחידה אחרונה | `mewtwo/d3-ig-waiting.jpg` | 4:5 | Reused `promo-main.png`, wider crop with more negative space ("waiting" framing) |
| D9 | 20:30 | instagram-story (3 frames) | סגירה במחיר | `mewtwo/d3-story-f1/f2/f3.jpg` | 9:16 | **F1:** real `product.png` on ascension bg · **F2:** Pillow data card `₪59` "1 UNIT IN STOCK" · **F3:** real `product.png` |

---

## Adaptations from the copy's suggested visuals (flagged for Matan/copywriter review)

1. **Slab Guard D2 20:30** — copy asked for "guard mounted on slab, solid vs. glitter, same angle." We
   only have one real "mounted on a slab" photo (glitter, used on D1 20:30). Substituted a direct
   product-only comparison (same background, same framing) — still delivers "compare the two lines."
2. **Jigglypuff D5 20:30** — copy asked for "the slab next to regular Pokemon cards" to show contrast.
   Skipped to avoid adding extra Pokemon card art beyond the actual product photo (house IP rule).
   Used the card's own unique back design instead — it is itself an unusual/rare element non-collectors
   won't recognize, which serves the same "this is different" goal without fabricating extra cards.
3. Several posts where copy asked for a numbers/price graphic (Jigglypuff D5/D6, Mewtwo D8/D9) got a
   **programmatic Pillow text card** rather than a product photo with baked text — same information,
   safer execution (no AI text-corruption risk, no Hebrew-in-AI-image risk).

## Usage log

Logged in `docs/usage-limits.md` under "יומן צריכה" — 8× `gemini-3.1-flash-image` background-only
calls for this campaign (2026-09-07), all compositing done locally with Pillow at $0.
