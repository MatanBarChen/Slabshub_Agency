# DRAFT — awaiting approval
- Platform: instagram-story
- Proposed publish time: Tuesday 2026-08-04, 04:00 IDT (= Monday 2026-08-03, 21:00 ET / 18:00 PT) — US weekday-evening collector peak (19:00–22:00 local ET), and >24h after the IG feed post to respect per-platform spacing. Story lives 24h, covering the full US Monday evening + Tuesday daytime.
- Status: APPROVED (by Matan in chat, 2026-08-02) — **content rewritten 2026-09-07 for HE/ILS repricing; re-approval recommended before publishing.**

## Final copy

Story text overlays (video already carries on-screen text per storyboard; use these only if posting as image frames or adding sticker text):

- Frame 1 — Hook: "Mewtwo AR מהיפני 151 — ₪59 בלבד 🔥"
- Frame 2 — Detail: "כמעט זהה למחיר השוק הנוכחי (Sports Card Investor, ספט 2026)."
- Frame 3 — CTA: "עותק גולמי אחד. לחצו על הקישור ⬆️"

Primary treatment: post reel-shot3.mp4 as a single story segment with the link sticker in the bottom-third clear zone. **The clip's own baked-in on-screen text still reads a USD figure ("$19.99 — under market price") that is under review — do not rely on it being correct or current; the overlay frames above and the link sticker are the source of truth, not the clip's burned-in text.** Add the link sticker labeled "לחנות" pointing to the UTM link below.

## Asset

`C:\Users\matan\Desktop\Slabshub Agency\assets\2026-08-02-raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151\reel-shot3.mp4`
— Veo vertical video, measured 720x1280 (exact 9:16), 8 seconds. Corresponds to storyboard shot 3 (card tilt + burned-in "$19.99 — under market price" glow pulse — **USD text baked into the clip, flagged in state.json for visual review, not fixed by copywriter**). 720x1280 meets IG story minimum; 1080x1920 is the recommended res (non-blocking). Bottom 250px left clear per image-spec for the link sticker.

## Link

https://slabshub.com/products/raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151?utm_source=instagram&utm_medium=story&utm_campaign=2026-08-02-raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151
(attach via link sticker)

## Checklist
- [x] Copy is Hebrew, RTL-natural; card/set names kept in English inline (Mewtwo, Art Rare, 151) per CLAUDE.md rule
- [x] Price updated to ₪59 in overlay text; no dependency on the clip's burned-in USD price being correct — flagged explicitly in Final copy and Asset sections
- [x] No grade/NM claims in overlay text (per storyboard honesty guardrails); Frame 2 cites only the re-verified 2026-09-07 SCI comp, framed as "same market range," not "under market" (the $24.59/$125 figures from Aug-2 are dropped, unverified this run)
- [x] "עותק גולמי אחד" = literal inventory
- [x] UTM parameters unchanged and correct — utm_campaign matches campaign name exactly; utm_medium=story; URL parses
- [x] Asset format matches placement dimensions — 720x1280 = exact 9:16 vertical (minor: below recommended 1080x1920, non-blocking)

### Verification notes
- Rewritten 2026-09-07. This is one of the two clips (with Umbreon's reel-moonlight.mp4) that burns a USD price into the frame — per the orchestrator's brief, that is a visual-team fix, not mine, so the overlay copy here is written to not depend on the clip's on-screen number being accurate.
- If Matan prefers the 3-frame image version instead of the video, the frames need to be produced from promo-main.png at 1080x1920 — not staged here; the video treatment is the ready asset.
