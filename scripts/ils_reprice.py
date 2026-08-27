"""USD -> ILS repricing plan for the store-currency switch.

Converts every variant at RATE, then snaps to a clean Israeli retail price point.
Run with --apply to write the new prices to Shopify (requires the store currency
to already be ILS — otherwise you would be setting shekel numerals as dollars).
"""
import json, pathlib, sys

RATE = 3.0  # ILS per USD — set by Matan; restate it in every output
LADDER = [15, 19, 22, 25, 29, 35, 39, 45, 49, 55, 59, 69, 79, 89, 99, 109, 119,
          139, 159, 179, 199, 229, 249, 279, 299, 349, 399, 449, 499, 549, 599,
          699, 799, 899, 990, 1190, 1390, 1590, 1790, 1990, 2290, 2490, 2990,
          3590, 3990, 4290, 4990]


def snap(usd: float) -> int:
    """Convert then land on the nearest clean price point (relative distance)."""
    target = usd * RATE
    return min(LADDER, key=lambda p: abs(p - target) / target)


def plan(variants):
    out = []
    for v in variants:
        usd = float(v["price"])
        ils = snap(usd)
        out.append({"id": v["id"], "title": v["product"]["title"],
                    "status": v["product"]["status"], "usd": usd, "ils": ils,
                    "raw": round(usd * RATE, 2),
                    "drift": round((ils - usd * RATE) / (usd * RATE) * 100, 1)})
    return out


if __name__ == "__main__":
    src = pathlib.Path(sys.argv[1])
    rows = plan(json.loads(src.read_text(encoding="utf-8")))
    pathlib.Path("docs/ils-reprice-plan.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    live = [r for r in rows if r["status"] == "ACTIVE"]
    print(f"{len(rows)} variants ({len(live)} active) · rate {RATE} ILS/USD")
    print(f"max drift from straight conversion: {max(abs(r['drift']) for r in rows)}%")
    for r in sorted(live, key=lambda r: -r["usd"])[:8]:
        print(f"  ${r['usd']:>8,.2f} -> ₪{r['ils']:>6,}  ({r['drift']:+.1f}%)  {r['title'][:52]}")
