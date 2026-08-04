---
description: הפעלת סוכן creative — ויז'ואלים/סטוריבורד/פרומפטים לוידאו מבריף קיים
argument-hint: <מוצר / נתיב בריף> [תוצר ספציפי: תמונה / סטוריבורד / פרומפטים]
---

Launch ONLY the `creative` agent for: $ARGUMENTS

Rules for this run:
- Locate the brief in `briefs/` (and the copy file in `copy/` if it exists, for matching overlays). If no brief exists, STOP and tell Matan to run `/brief` first.
- If Matan named a specific deliverable (image / storyboard / video prompts), produce only that.
- Respect skip rules: no promo.html when Gemini image generation works; no ad-format creative while paid is blocked. Veo video generation only for approved campaigns (pay-per-use) — storyboard + prompts are free, generation is not.
- Output: files in `assets/<campaign>/`, then report back in Hebrew with the visual concept. Do NOT chain into publisher — this is an individual run.
