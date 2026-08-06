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
| `sections/comics-404.liquid` + `templates/404.json` | 404 page (catch mini-game) |
| `sections/comics-product.liquid` + `templates/product.json` | DYNAMIC product page: {{ product }} data, real Add-to-Cart form, front/back gallery, related row |
| `sections/comics-collection.liquid` + `templates/collection.json` | DYNAMIC collection: full catalog loop (paginate 48), client-side price filters + sort, in-grid advert |
| `sections/comics-index.liquid` + `templates/index.json` | DYNAMIC front page: hero carousel auto-picks 5 priciest available cards, fresh-pulls grid, Classifieds under $15, newsletter = real {% form 'customer' %}, nav from main-menu linklist |
| `sections/comics-cart.liquid` + `templates/cart.json` | DYNAMIC cart ("Your Pull List"): real {{ cart.items }}, single-copy badges (inventory==1) vs qty steppers (AJAX /cart/change.js), real checkout button, empty state |
| `snippets/comics-spec-parser.liquid` | Description → spec-sheet renderer: converts "Key: Value" lines (incl. <br data-*> breaks) into RTL/LTR dot-leader rows; falls back to raw HTML for bullet-style descriptions |
| `snippets/comics-embed-test.liquid` | Write-access test — safe to delete |

Verified rendered: `https://slabshub.com/pages/anything-missing?preview_theme_id=184094687343` shows the Comics 404 (screenshot: `../preview-shopify-404.png`).

## Still to deploy

- about (`templates/page.comics-about.json` → section; Matan assigns template to a Page in admin)
- search page, policy pages (optional polish)
- QA sweep on preview, then Matan publishes the theme from admin (Online Store → Themes → "Updated copy of Black & White" → Publish).

## Local files here

- `templates-404.liquid` — original standalone-template approach (superseded by the section approach, kept for reference)
- `snippets-comics-balls.liquid` — source of the deployed snippet
