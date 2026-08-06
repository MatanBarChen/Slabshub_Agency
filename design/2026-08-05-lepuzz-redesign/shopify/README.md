# Comics → Shopify embedding

Target theme (sandbox, UNPUBLISHED): **"Updated copy of Black & White"** — `gid://shopify/OnlineStoreTheme/184094687343`.
The live theme ("Black & White", MAIN) is never written to via API; publishing is manual by Matan from the admin.

Preview any page on the sandbox by appending `?preview_theme_id=184094687343` to a store URL.

## Deployment approach

- Standalone Comics pages are deployed as **sections** with a JSON template using `"layout": false` (no old-theme header/footer). Reason: `templates/*.json` can't be deleted via API (delete is permission-blocked), and a same-name `.liquid` template can't coexist — so we overwrite the JSON template to point at our section instead.
- Shared pokeball SVG symbols live once in `snippets/comics-balls.liquid`; every page calls `{% render 'comics-balls' %}`.

## Deployed so far (2026-08-06)

| Theme file | Purpose |
|---|---|
| `snippets/comics-balls.liquid` | 6 pixel pokeball SVG symbols (shared) |
| `sections/comics-404.liquid` | Full Comics 404 page (catch mini-game) |
| `templates/404.json` | `layout: false` → `comics-404` section |
| `snippets/comics-embed-test.liquid` | Write-access test — safe to delete |

Verified rendered: `https://slabshub.com/pages/anything-missing?preview_theme_id=184094687343` shows the Comics 404 (screenshot: `../preview-shopify-404.png`).

## Still to deploy

home (index), collection, product, about (page template), cart — same section+JSON-template pattern; product/collection/cart should swap hardcoded product arrays for Liquid objects (`collection.products`, `product`, `cart`).

## Local files here

- `templates-404.liquid` — original standalone-template approach (superseded by the section approach, kept for reference)
- `snippets-comics-balls.liquid` — source of the deployed snippet
