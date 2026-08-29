"""Builds catalog.json for the sales-agent prototype from Shopify product data.

Page 1 (50 products) comes from a saved Shopify Admin API result; page 2 (17
products) is kept alongside as page2.json. Rerun after any catalog change.
"""
import json, re, sys, html
from collections import Counter

SRC = sys.argv[1]
BASE = "prototype/sales-agent/"

def clean(t):
    if not t:
        return ""
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

def url_for(handle):
    return "https://slabshub.com/products/" + (handle or "")

items = []

with open(SRC, encoding="utf-8") as f:
    for e in json.load(f)["data"]["products"]["edges"]:
        n = e["node"]
        pr = n.get("priceRangeV2", {})
        items.append({
            "title": n.get("title"),
            "handle": n.get("handle"),
            "status": n.get("status"),
            "type": n.get("productType"),
            "vendor": n.get("vendor"),
            "inventory": n.get("totalInventory") or 0,
            "price": pr.get("minVariantPrice", {}).get("amount"),
            "price_max": pr.get("maxVariantPrice", {}).get("amount"),
            "url": n.get("onlineStoreUrl") or url_for(n.get("handle")),
            "image": (n.get("featuredImage") or {}).get("url"),
            "description": clean(n.get("description"))[:700],
        })

with open(BASE + "page2.json", encoding="utf-8") as f:
    for p in json.load(f):
        p.setdefault("price_max", p.get("price"))
        p.setdefault("image", None)
        p["url"] = url_for(p.get("handle"))
        p["description"] = clean(p.get("description"))[:700]
        items.append(p)

seen, merged = set(), []
for p in items:
    if p["handle"] in seen:
        continue
    seen.add(p["handle"])
    merged.append(p)

merged.sort(key=lambda p: (0 if p["inventory"] > 0 else 1, -float(p["price"] or 0)))

catalog = {
    "shop": "SlabsHub",
    "currency": "ILS",
    "ships_to": ["IL", "US", "GB", "DE", "FR", "CA", "AU", "JP", "and 24 more"],
    "contact_email": "Slabshub@gmail.com",
    "products": merged,
}

with open(BASE + "catalog.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=1)

in_stock = [p for p in merged if p["inventory"] > 0]
print("total products:", len(merged))
print("in stock:", len(in_stock))
print("status:", dict(Counter(p["status"] for p in merged)))
print("price range in stock:", min(float(p["price"]) for p in in_stock), "-", max(float(p["price"]) for p in in_stock), "ILS")
print("bytes:", len(json.dumps(catalog, ensure_ascii=False)))
