"""Turn catalog.json into the SQL that refreshes the cloud catalog.

    py prototype/sales-agent/catalog_to_sql.py

Writes catalog.sql next to it. Chat_Agent then runs that file's contents through
the Supabase MCP `execute_sql` tool against project uvlkacfnbnsqpizktcfi.
The statement is a full replace: products missing from the snapshot are deleted,
so the chat can never recommend something that left the store.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "catalog.json"), encoding="utf-8") as f:
    products = json.load(f)["products"]

rows = []
for p in products:
    rows.append({
        "handle": p["handle"],
        "title": p["title"],
        "status": p.get("status"),
        "type": p.get("type"),
        "vendor": p.get("vendor"),
        "inventory": int(p.get("inventory") or 0),
        "price": float(p["price"]) if p.get("price") else None,
        "price_max": float(p["price_max"]) if p.get("price_max") else None,
        "url": p.get("url"),
        "image": p.get("image"),
        "description": p.get("description"),
    })

payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("'", "''")

sql = (
    "with snapshot as (select * from jsonb_to_recordset('" + payload + "'::jsonb) as x("
    "handle text, title text, status text, type text, vendor text, inventory integer, "
    "price numeric, price_max numeric, url text, image text, description text)), "
    "upserted as (insert into public.products "
    "(handle,title,status,type,vendor,inventory,price,price_max,url,image,description,synced_at) "
    "select handle,title,status,type,vendor,inventory,price,price_max,url,image,description,now() "
    "from snapshot on conflict (handle) do update set "
    "title=excluded.title, status=excluded.status, type=excluded.type, vendor=excluded.vendor, "
    "inventory=excluded.inventory, price=excluded.price, price_max=excluded.price_max, "
    "url=excluded.url, image=excluded.image, description=excluded.description, synced_at=now() "
    "returning handle), "
    "removed as (delete from public.products where handle not in (select handle from snapshot) returning 1) "
    "select (select count(*) from upserted) as synced, (select count(*) from removed) as removed;"
)

out = os.path.join(HERE, "catalog.sql")
with open(out, "w", encoding="utf-8") as f:
    f.write(sql)

in_stock = sum(1 for r in rows if r["inventory"] > 0)
print("wrote " + out)
print("  products : " + str(len(rows)) + " (" + str(in_stock) + " in stock)")
print("  sql size : " + str(round(len(sql) / 1024, 1)) + " KB")
