"""
shopify_staged_upload.py — step 2 of hosting campaign media on the Shopify CDN.

Step 1 (orchestrator, via the Shopify MCP): stagedUploadsCreate → save the targets as JSON:
  [{"file": "<local path>", "url": "...", "resourceUrl": "...", "p": {param: value, ...}}, ...]
Step 2 (this script): POST each file to its staged target.
Step 3 (orchestrator, via the Shopify MCP): fileCreate with each resourceUrl → public cdn.shopify.com URLs.

Usage: py scripts/shopify_staged_upload.py <targets.json>
"""
import json, sys
from pathlib import Path
import truststore  # Google storage endpoints fail certifi verification on this machine; use the Windows cert store
truststore.inject_into_ssl()
import requests

ROOT = Path(__file__).resolve().parent.parent
targets = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
ok = 0
for t in targets:
    path = ROOT / t["file"]
    with open(path, "rb") as fh:
        r = requests.post(t["url"], data=t["p"], files={"file": (path.name, fh)}, timeout=300)
    good = r.status_code < 300
    ok += good
    print(r.status_code, path.name, "ok" if good else r.text[:200].replace("\n", " "))
print(f"{ok}/{len(targets)} uploaded")
