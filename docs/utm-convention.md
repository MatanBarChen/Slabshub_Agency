# UTM Convention — SlabsHub

Every product link published on social media must carry UTM parameters so Analytics can attribute Shopify sessions and orders back to the exact post.

## Format

```
https://slabshub.com/products/<handle>?utm_source=<source>&utm_medium=<medium>&utm_campaign=<campaign>
```

| Parameter | Allowed values |
|---|---|
| `utm_source` | `facebook`, `instagram` |
| `utm_medium` | `paid` (ads), `organic` (feed posts), `story` |
| `utm_campaign` | `YYYY-MM-DD-<product-handle>` — the date the campaign/draft was created + the Shopify product handle. Weekly campaigns use `YYYY-MM-DD-weekly` |

## Example

```
https://slabshub.com/products/raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151?utm_source=instagram&utm_medium=organic&utm_campaign=2026-08-02-raw-card-mewtwo-183-pokemon-japanese-scarlet-violet-151
```

## Rules

- Lowercase everything. No spaces (handles are already kebab-case).
- The campaign name in the draft filename, the copy file, and the UTM must match exactly — this is the join key Analytics uses.
- Never strip UTMs to "clean up" a link; the short look is what link-in-bio tools are for.
