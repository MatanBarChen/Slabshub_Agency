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

## The chat agent

The on-site chat links to products too, and those clicks need to be attributable
without stealing credit from the ad that paid for the visit.

| Case | What the link carries |
|---|---|
| Visitor arrived with UTMs (from an ad) | the inbound `utm_source`/`utm_medium`/`utm_campaign` are passed through **unchanged**, plus `utm_content=chat-agent` |
| Visitor arrived direct | `utm_source=chat-agent`, `utm_medium=onsite`, `utm_campaign=chat-landing-he` or `chat-landing-en`, plus `utm_content=chat-agent` |

The rule behind it: the campaign that bought the session keeps the session.
`utm_content` is what says the chat closed it, so Analytics can ask "how many of
this campaign's orders went through the agent?" without breaking the join key.

Adds two values to the tables above — `utm_source: chat-agent` and
`utm_medium: onsite`. Applied in the browser at render time, never written into
the catalog, so what the agent quotes stays exactly what it said.

## Rules

- Lowercase everything. No spaces (handles are already kebab-case).
- The campaign name in the draft filename, the copy file, and the UTM must match exactly — this is the join key Analytics uses.
- Never strip UTMs to "clean up" a link; the short look is what link-in-bio tools are for.
