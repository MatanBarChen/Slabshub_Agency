# APPROVED — ready to publish manually
- Platform: instagram-story
- Proposed publish time: יום חמישי 2026-08-20, 21:00 IDT — slot: il-thu-eve (docs/schedule-slots.md § Israel-local slots), 24.5h after the IG feed hero
- Rescheduled 2026-08-16: original 06/08 slot lapsed unpublished (see drafts/state.json _sync_note)
- Status: APPROVED (by Matan in chat, 2026-08-04)

## Final copy

**פריים 1 (הוק):**
"הסלאב שרד את הדירוג. עכשיו תגנו עליו 🛡️"

**פריים 2 (פרטים):**
"מתאים ל-PSA | ₪19-22 | 3+ = 15% הנחה אוטומטית"

**פריים 3 (CTA):**
"לינק בסטורי → Slab Guard, 25 יחידות בלבד"

## Asset
`assets/2026-08-04-slab-guard-launch/export/reel-handfan-story-1080x1920.mp4` — 8s, 1080x1920, audio kept.
The three frame texts above are burned in (RTL, Heebo, 0.35s cross-fades at 0.0–2.7 / 2.7–5.4 / 5.4–8.0s).

Reframing applied: the delivered clip was 720x1280 but the actual footage occupied only 720x960 — it shipped
with baked-in letterbox bars (cropdetect: `crop=720:960:0:160`). Those were cropped off, the footage scaled to
960x1280 and padded onto a #0B0B0D canvas at y=330. That yields a clean dark band up top for the text and
leaves the bottom 310px clear for IG's native link sticker. Regenerate with
`python3 scripts/bake_slabguard_assets.py`.

## Link
https://slabshub.com/products/slab-guard-silicone-bumper-for-psa-graded-slabs?utm_source=instagram&utm_medium=story&utm_campaign=2026-08-04-slab-guard-launch

## Checklist
- [x] Copy matches platform limits — each of the 3 frame lines under 12 words, well within story-overlay readability norms.
- [x] UTM parameters present and correct — utm_source=instagram, utm_medium=story, utm_campaign=2026-08-04-slab-guard-launch (exact match).
- [x] No unverified price/scarcity claims — ₪19-22 range and "3+ = 15% הנחה" match brief UPDATE 2; "25 יחידות בלבד" matches confirmed total inventory (15 solid + 10 glitter); PSA-only, no CGC/BGS claim.
- [x] Asset format matches placement dimensions — 9:16 vertical footage, native fit for IG story canvas (1080x1920), per orchestrator-supplied spec (8s, ready, no reprocessing needed).

## Verification notes
- RESOLVED 2026-08-16: the 3 frame lines are burned in, RTL-shaped and timed; source letterbox bars removed and clip re-mastered to native 1080x1920.
- Frame 2 wording: "3+ = 15% הנחה אוטומטית" is rendered on screen as "15% הנחה מ-3 יחידות" for RTL legibility — same claim, and the caption text above is unchanged.
- Storyboard file (video-storyboard.md) predates this footage and was written for a different planned shot — treat reel-handfan.mp4 as the actual asset, ignore the storyboard's superseded shot list.
- Promo claim verified against Shopify 2026-08-16: automatic discount "Slab Guard — 3+ units 15% off" is ACTIVE (min qty 3, both variants).

