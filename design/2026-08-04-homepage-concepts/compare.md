# Homepage Concepts — Compare (2026-08-04)

Source audit: `current-home.png`. Current-state weaknesses (evidence-based):
1. Hero uses a bright pink/blue Wordle-tile gradient — reads as generic Shopify template, clashes with "premium dark collector" brand.
2. Product cards sit on hot-pink tiles with blue neon-glow borders — toy-store visual language undermines trust on $1,199 items.
3. No trust signal (cert lookup, grading explainer) visible above the fold anywhere on the page.
4. Flat grid gives the $1,199 Charizard CD Promo the same visual weight as a $5 raw card — no hero product.
5. Default Shopify nav ("Welcome to our store" bar, tiny logo) — no brand presence, thin wayfinding.

Screenshots: `current-home.png`, `concept-1.png`, `concept-2.png`, `concept-3.png`. Source: `concept-1.html`, `concept-2.html`, `concept-3.html`.

---

## Concept 1 — The Vault
**Thesis:** Store as a high-security vault of grails — Linear-style discipline, near-black canvas, hairline grid, mono cert numbers, one ember CTA color.
**Best at:** Trust and speed-to-scan — cert numbers and "verify" links are baked into every card and the hero stat row (1,200+ authenticated / 100% cert-verifiable) does more trust work per pixel than anything on the live site.
**Risk:** Least emotionally distinctive of the three — restrained enough that it could read as "generic dark SaaS" if the ember accent and mono details get diluted during build.

## Concept 2 — The Gallery
**Thesis:** Museum/editorial — warm-lit frames, serif display type, curator-note copy tone, cards presented as displayed masterpieces.
**Best at:** Perceived value — the framed-card treatment and placard copy make the $19.99 Mewtwo and the $1,199 Charizard both feel curated, not discounted. Strongest differentiation from every competitor's dark-grid template.
**Risk:** Serif + slow pacing reads slower/heavier than a collector expects when scanning for price and grade fast; needs a tighter "scan mode" (larger price, grade badge) if conversion speed is the priority over browsing delight.

## Concept 3 — The Arena
**Thesis:** Drop-culture energy — condensed type, live price ticker, "recent sales" feed, purple-to-ember gradient used with discipline on CTAs and badges only.
**Best at:** Urgency and repeat-visit hooks — the ticker and live-feed strip give collectors a reason to check back, which the current static grid has zero of.
**Risk:** Highest execution risk — gradients/motion/ticker can tip into "crypto-drop-site" territory and undercut trust if not kept disciplined; live-feed content needs real data or it reads as fake social proof.

---

## Concept 4 — The Gallery After Dark (hybrid: Gallery layout × Arena palette)
**Thesis:** Museum pacing/typography (Fraunces serif, curator notes, whitespace) owns structure; Arena's exact token set (`--purple:#8b5cf6`, `--ember:#ff4d2e`, `--ember2:#ff8a3d`, `--bg:#0a0a0d`) owns all color. The "Featured Acquisitions" grid was rebuilt (2026-08-04, Matan-requested revision) directly off the live store's own product-card anatomy — audited via headless screenshots of slabshub.com + /collections/all, saved as `store-cards.png` / `store-cards-home.png` — reusing its exact title pattern (`GRADE | Name #num Set`, e.g. "PSA 9 | Charizard [Holo] #6 Pokemon Japanese CD Promo") as a grade-pill + serif-name split, and its "$X USD" price convention, elevated with grade-colored glow borders (PSA=ember, CGC=purple) instead of the store's flat pink/blue tiles. Arena's ticker still becomes the "Recent Results" auction strip (kept as-is per direction).
**Best at:** Solves Concept 2's "too slow to scan" risk (mono cert/price data adds scan speed) without losing its premium differentiation, and solves Concept 3's "crypto-drop-site" risk (same energetic palette, but disciplined by Gallery's whitespace and serif restraint). Now also the most evidence-honest concept — every claim in the featured grid traces to a real product title/price, and the only cert number shown (Charizard CD Promo, #10017252) is real and links to `psacard.com/cert/10017252`; no fabricated cert numbers, "sold to"/"watched by" social-proof, or unverified condition claims (grep-verified clean).
**Risk:** Requires disciplined build — if a developer reintroduces filled gradient buttons from Arena's literal markup instead of the restrained outline/pill treatment used here, it collapses back into Concept 3. The "Recent Results" strip (kept unchanged per direction) still contains illustrative status tags (SOLD / 2 REMAINING) that need real sales data before ship — same risk flagged on Concept 3, not yet resolved. Real cert numbers for the CGC 10 Charizard VSTAR and condition detail for the two raw cards should be pulled from the live product pages before build so the "View piece" placeholders become real numbers.

## Recommendation
**The Vault** is the safest ship — it fixes all 5 current-state trust/hierarchy problems fastest and lowest-risk. **The Gallery** is the strongest brand differentiator if Matan wants the store to feel unmistakably premium vs. every other card shop. Arena is the highest-upside/highest-risk pick — best if the goal is repeat engagement over trust-building, but needs real (not simulated) sales data to earn the live-feed claims.
