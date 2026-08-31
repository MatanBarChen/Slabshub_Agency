# Floating chat widget — parked 2026-08-31

The original delivery of the sales agent: a launcher button pinned to the corner of
every storefront page, opening a floating chat panel. **Built, tested, never went
live.** Parked in favour of a chat section embedded directly in the homepage, so the
corner stays free for Shopify's own chat/email widget.

Nothing here is obsolete — the backend it talks to is the same one the inline version
uses. To bring it back, follow "Install" below. To run both at once, don't: two chat
entry points on one page confuse visitors and double the API spend.

## What it is

`slabshub-agent.liquid` — one self-contained Shopify snippet, ~12KB, no build step,
no dependencies. It carries its own CSS (all selectors namespaced `sh-`), its own
markup and its own JS.

- **Launcher**: a Pokedex-style device drawn in inline SVG — red shell, blue lens with
  a glow, two blinking LEDs. Swaps to a close icon when open.
- **Panel**: floating chat with a greeting, suggestion chips ("יש לך צ'ריזארד?",
  "משהו עד 100 שקל", "מה זה PSA 9?", "אפשר הנחה?"), a message list and an input.
- **RTL Hebrew** throughout, including `aria-label`s. Escape closes the panel.
- **No API key in the browser.** The page only ever talks to the endpoint below; the
  Anthropic key lives server-side as a Supabase secret.

## Backend (shared with the inline version)

| | |
|---|---|
| Endpoint | `https://uvlkacfnbnsqpizktcfi.supabase.co/functions/v1/chat` |
| Supabase project | `SlabsHub_Chat` — `uvlkacfnbnsqpizktcfi`, Frankfurt |
| Health check | `GET` the endpoint → model, product count, whether the key is set |
| Request | `POST {"message": "...", "conversation_id": "..."}` |
| Response | `{reply, conversation_id, trace}` — `trace` lists every tool call |

Conversation history lives server-side: the browser sends one message plus an id,
never a transcript, so a visitor cannot forge the agent's turns or inject
instructions into the history.

Allowed origins are enforced by the function: slabshub.com and subdomains,
myshopify.com, localhost. A new host must be added there or the fetch is rejected.

## Install

The snippet's own header carries these steps too. Order matters — step 3 without
steps 1-2 is exactly the silent failure described below.

1. Themes → the theme labelled **Live** → ⋯ → Edit code
2. Snippets → Add a new snippet → name it **`slabshub-agent`** (Shopify appends
   `.liquid`), paste the whole file, Save
3. Layout → `theme.liquid` → add `{% render 'slabshub-agent' %}` just before `</body>`

## Gotchas — all three cost us time on 2026-08-31

- **A missing snippet fails silently.** `{% render %}` pointing at a snippet that
  doesn't exist renders nothing and raises no storefront error. The page loads
  perfectly, just without the widget. First install had step 3 done and steps 1-2
  not, and there was no visible symptom to chase.
- **The name is exact and case-sensitive.** `Slabshub_agent` ≠ `slabshub-agent`.
  A capital letter or an underscore instead of the hyphen produces the same silent
  nothing. The Shopify code editor cannot rename a file — create a new one with the
  correct name and delete the old.
- **Only `layout/theme.liquid` carries the render tag.** The store also has
  `theme.pagefly.liquid` and `theme.shogun.landing.liquid`; pages built with PageFly
  or Shogun use those layouts and will NOT show the widget unless the tag is added
  to each of them.

## State of the live theme as of parking

Theme: `Updated copy of Black & White` (MAIN, id 184094687343).

- `layout/theme.liquid` **still contains `{% render 'slabshub-agent' %}`** before
  `</body>`. Harmless — it renders nothing while no matching snippet exists — but it
  is a live no-op. Remove it when convenient, or leave it as the hook for bringing
  this widget back.
- `snippets/Slabshub_agent.liquid` exists from the mistyped first attempt and is
  never rendered by anything. Safe to delete; it is dead weight in the theme.

## Why it was parked

Not a defect — the widget worked. A corner bubble reads as a support widget, and the
store wants that corner for Shopify's own chat/email. An inline section on the
homepage frames the agent as a way to shop rather than a way to complain, and it is
seen without a click.
