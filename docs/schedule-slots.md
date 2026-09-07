# Fixed publishing slots — SlabsHub

Times are IDT (Israel). **Two slots per day** (updated 2026-09-07 at Matan's request — was one slot/day).
Publisher: pick a slot, cite it as `slot: <name>` — do NOT re-derive timezone math per draft.

| Slot name | IDT | US ET | Audience | Best for |
|---|---|---|---|---|
| `us-eve-a` | 03:30 | 20:30 (prev day) | US collectors, evening peak | IG feed hero, FB organic openers, premium/English content |
| `il-eve-b` | 20:30 | 13:30 | Israeli collectors prime time + US lunch | IG stories, Hebrew content, accessories |
| `il-noon-a` | 12:30 | 05:30 | Israeli lunch break — Hebrew campaigns | Second daily slot for Hebrew/Israel-only campaigns running 2 posts/day |

The two slots are **17h apart** within a calendar day, which keeps every same-platform
pair ≥24h apart as long as a platform appears at most once per day (see below).

## Spacing rules
- **A platform appears at most once per calendar day.** With 3 surfaces
  (`instagram-feed`, `instagram-story`, `facebook-organic`) and 2 slots, this is always
  satisfiable — never put two IG-feed posts in the same day.
- **≥24h between posts on the same platform.** Same-slot-consecutive-days = exactly 24h ✓.
  Slot A day N → slot B day N = 17h ✗ for the *same* platform (fine for different ones).
  Slot B day N → slot A day N+1 = 7h ✗ — never schedule the same platform across that gap.
- Never same-minute FB + IG twins — the 17h A/B stagger handles this automatically.
- Paid ad flights start only AFTER the campaign's organic posts have landed (retarget warmed traffic).

## Legacy slot names
The old one-per-day grid (`us-mon-eve` … `us-sun-aft`, and the Israel-local
`il-wed-eve`/`il-thu-eve`/`il-sat-eve` deviation used by the Slab Guard launch) is retired.
Drafts still citing those names are rescheduled onto `us-eve-a` / `il-eve-b`.

## Standard campaign shape
FB organic (opener) → IG feed (hero) → IG story, one per day, alternating slots so no two
posts of the same platform land within 24h. At 2 posts/day two campaigns interleave —
one in slot A, one in slot B — rather than one campaign burning both slots.

## Deviation — Triathlon campaign (2026-09-07)
Matan's directive: one product occupies both daily slots (`il-noon-a` 12:30 + `il-eve-b` 20:30)
for 3 consecutive days, Hebrew/Israel-only campaign. The interleave rule above is suspended for
this campaign (and for future Hebrew-only campaigns run the same way) — a single product may burn
both daily slots as long as the ≥24h same-platform spacing rule still holds across the 3-day block
(it does: FB/IG-feed/IG-story each land exactly 32h or ~39.5h apart, never <24h).
