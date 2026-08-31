"""Local prototype of the SlabsHub AI sales agent.

Run:  py prototype/sales-agent/server.py
Then open http://localhost:8787

Nothing here touches the live store. The catalog is a snapshot in catalog.json;
rebuild it with build_catalog.py after inventory changes.
"""
import json, os, re, urllib.request, urllib.error, datetime, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
MODEL = os.environ.get("AGENT_MODEL", "claude-sonnet-5")
PORT = int(os.environ.get("AGENT_PORT", "8787"))
MAX_TOOL_ROUNDS = 6


def _env_value(name):
    val = os.environ.get(name)
    if val:
        return val.strip()
    envfile = os.path.join(ROOT, ".env")
    if os.path.exists(envfile):
        with open(envfile, encoding="utf-8-sig", errors="replace") as f:
            for line in f:
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == name:
                    return v.strip().strip("'\"")
    return None


def load_key():
    return _env_value("ANTHROPIC_API_KEY")


def load_workspace_id():
    return _env_value("ANTHROPIC_WORKSPACE_ID")


with open(os.path.join(HERE, "catalog.json"), encoding="utf-8") as f:
    CATALOG = json.load(f)
with open(os.path.join(HERE, "system-prompt.md"), encoding="utf-8") as f:
    SYSTEM = f.read()

PRODUCTS = CATALOG["products"]
LOGDIR = os.path.join(HERE, "conversations")
os.makedirs(LOGDIR, exist_ok=True)

GRADE_RE = re.compile(r"^(PSA|CGC|BGS)\s*(\d+)", re.I)
WORD_RE = re.compile(r"[^0-9a-zA-Z֐-׿]+")


def _log_jsonl(filename, entry):
    entry = {"at": datetime.datetime.now().isoformat(timespec="seconds"), **entry}
    with open(os.path.join(LOGDIR, filename), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def grade_of(p):
    m = GRADE_RE.match(p["title"])
    if m:
        return m.group(1).upper() + " " + m.group(2)
    return "RAW" if p["title"].startswith("RAW") else None


def search_catalog(query=None, min_price=None, max_price=None, grade=None,
                   product_type=None, in_stock_only=True, limit=6):
    results = []
    text_matches = 0
    out_of_stock_hits = 0
    terms = [t for t in WORD_RE.split((query or "").lower()) if len(t) > 1]
    for p in PRODUCTS:
        title = p["title"].lower()
        hay = title + " " + (p.get("description") or "").lower() + " " + (p.get("vendor") or "").lower()
        score = 0
        for t in terms:
            if t in title:
                score += 3
            elif t in hay:
                score += 1
        if terms and score == 0:
            continue
        text_matches += 1
        price = float(p["price"] or 0)
        if min_price is not None and price < float(min_price):
            continue
        if max_price is not None and price > float(max_price):
            continue
        g = grade_of(p) or ""
        if grade and grade.upper().replace(" ", "") not in g.replace(" ", ""):
            continue
        if product_type and product_type.lower() not in (p.get("type") or "").lower():
            continue
        if in_stock_only and p["inventory"] <= 0:
            out_of_stock_hits += 1
            continue
        results.append((score, price, p))
    results.sort(key=lambda r: (-r[0], -r[1]))
    if terms and not results:
        _log_jsonl("demand.jsonl", {
            "event": "out_of_stock" if out_of_stock_hits else ("filtered_out" if text_matches else "no_match"),
            "query": query, "grade": grade, "min_price": min_price, "max_price": max_price,
        })
    out = []
    for _, _, p in results[:int(limit)]:
        out.append({
            "title": p["title"],
            "grade": grade_of(p),
            "price_ils": p["price"],
            "price_max_ils": p["price_max"] if p["price_max"] != p["price"] else None,
            "in_stock": p["inventory"],
            "url": p["url"],
            "type": p.get("type"),
            "description": (p.get("description") or "")[:400] or None,
        })
    resp = {"matches": len(results), "showing": len(out), "products": out}
    if terms:
        resp["reminder"] = ("If the exact card the customer asked about is NOT in 'products', "
                            "call record_wishlist for it now, before replying.")
    return resp


def record_wishlist(card, contact=None, notes=None):
    _log_jsonl("wishlist.jsonl", {"card": card, "contact": contact, "notes": notes})
    return {"status": "saved",
            "note": "Recorded for Matan's daily sourcing review. Do not promise the card will be found, a timeframe, or a price."}


def _recent_handoffs(minutes=15):
    path = os.path.join(LOGDIR, "handoffs.jsonl")
    if not os.path.exists(path):
        return []
    cutoff = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f.readlines()[-20:]:
            try:
                e = json.loads(line)
                if datetime.datetime.fromisoformat(e["at"]) >= cutoff:
                    out.append(e)
            except (ValueError, KeyError):
                continue
    return out


def _same_request(a, b):
    """Word overlap, so a reworded repeat of the same ask still counts as one."""
    wa = set(re.findall(r"[\w']+", (a or "").lower()))
    wb = set(re.findall(r"[\w']+", (b or "").lower()))
    if not wa or not wb:
        return False
    return len(wa & wb) / len(wa | wb) >= 0.45


def request_human(reason, summary, contact=None):
    # Backstop for the prompt rule: one handoff per conversation. The model has
    # escalated the same request several times in a row before, which reaches
    # Matan as several separate interruptions about one customer.
    for prev in _recent_handoffs():
        if _same_request(prev.get("summary"), summary) or (
                contact and prev.get("contact") == contact):
            return {"status": "already_open",
                    "note": ("This request is already with Matan - not logged again. "
                             "Tell the customer it is already passed on, and carry on "
                             "helping them. If the card is one we do not stock, the right "
                             "tool is record_wishlist, not request_human.")}
    entry = {
        "at": datetime.datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "summary": summary,
        "contact": contact,
    }
    with open(os.path.join(LOGDIR, "handoffs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"status": "logged", "note": "Matan has been notified. Do not promise a response time."}


TOOLS = [
    {
        "name": "search_catalog",
        "description": ("Search live SlabsHub inventory. English keywords only. Returns only real "
                        "products. Call this before naming any product, price or stock level."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "English keywords: pokemon name, set, card number"},
                "min_price": {"type": "number", "description": "Minimum price in ILS"},
                "max_price": {"type": "number", "description": "Maximum price in ILS"},
                "grade": {"type": "string", "description": "e.g. 'PSA 9', 'PSA 10', 'CGC 9', 'RAW'"},
                "product_type": {"type": "string", "description": "'Pokemon TCG' or 'Accessories'"},
                "in_stock_only": {"type": "boolean", "default": True},
                "limit": {"type": "integer", "default": 6},
            },
        },
    },
    {
        "name": "record_wishlist",
        "description": ("Record a card the customer wants but the shop does not have right now, so Matan "
                        "can try to source it. Call after search_catalog came up empty for a specific card "
                        "and the customer confirmed interest. Include contact details only if the customer "
                        "gave them for this purpose."),
        "input_schema": {
            "type": "object",
            "properties": {
                "card": {"type": "string", "description": "English card description: name, set, number, grade if given. e.g. 'Charizard Base Set PSA 8'"},
                "contact": {"type": "string", "description": "Email or WhatsApp the customer left for a restock heads-up, if any"},
                "notes": {"type": "string", "description": "Budget, condition preference, or other context, in English"},
            },
            "required": ["card"],
        },
    },
    {
        "name": "request_human",
        "description": "Last resort. Hand the conversation to Matan for a discount request, an existing order, extra photos, an unhappy customer, or a purchase over 1,000 ILS of an item we stock. Ask for the customer's contact details first. NEVER use this for a card we do not stock or a restock heads-up - that is record_wishlist. Never call it twice in one conversation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "discount | photos | order | high_value | unknown | unhappy"},
                "summary": {"type": "string", "description": "What the customer wants, in one or two sentences"},
                "contact": {"type": "string", "description": "Email or phone the customer gave, if any"},
            },
            "required": ["reason", "summary"],
        },
    },
]

DISPATCH = {"search_catalog": search_catalog, "record_wishlist": record_wishlist, "request_human": request_human}


def call_anthropic(key, messages):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 1200,
        "system": SYSTEM,
        "tools": TOOLS,
        "messages": messages,
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read())


def run_turn(key, messages):
    """Runs the agent loop until it produces a final text reply."""
    trace = []
    for _ in range(MAX_TOOL_ROUNDS):
        resp = call_anthropic(key, messages)
        blocks = resp.get("content", [])
        messages.append({"role": "assistant", "content": blocks})
        tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
        if not tool_uses:
            text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
            return text.strip(), messages, trace
        results = []
        for tu in tool_uses:
            fn = DISPATCH.get(tu["name"])
            try:
                out = fn(**tu.get("input", {})) if fn else {"error": "unknown tool"}
            except Exception as e:
                out = {"error": str(e)}
            trace.append({"tool": tu["name"], "input": tu.get("input", {}), "output": out})
            results.append({
                "type": "tool_result",
                "tool_use_id": tu["id"],
                "content": json.dumps(out, ensure_ascii=False),
            })
        messages.append({"role": "user", "content": results})
    return "Sorry, I got stuck there. Can you rephrase?", messages, trace


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, payload, ctype="application/json"):
        if isinstance(payload, bytes):
            data = payload
        else:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            with open(os.path.join(HERE, "index.html"), "rb") as f:
                return self._send(200, f.read(), "text/html")
        if path == "/api/health":
            return self._send(200, {
                "key": bool(load_key()),
                "workspace": bool(load_workspace_id()),
                "model": MODEL,
                "products": len(PRODUCTS),
                "in_stock": sum(1 for p in PRODUCTS if p["inventory"] > 0),
            })
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, {"error": "not found"})
        key = load_key()
        if not key:
            return self._send(200, {"reply": "ANTHROPIC_API_KEY is missing from .env - add it and reload.", "trace": []})
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            messages = payload.get("messages") or []
            reply, messages, trace = run_turn(key, messages)
            stamp = datetime.datetime.now().strftime("%Y-%m-%d")
            with open(os.path.join(LOGDIR, stamp + ".jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps({"reply": reply, "trace": trace}, ensure_ascii=False) + "\n")
            return self._send(200, {"reply": reply, "messages": messages, "trace": trace})
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            return self._send(200, {"reply": "API error (" + str(e.code) + "): " + detail, "trace": []})
        except Exception:
            traceback.print_exc()
            return self._send(200, {"reply": "Server error - check the terminal.", "trace": []})


if __name__ == "__main__":
    in_stock = sum(1 for p in PRODUCTS if p["inventory"] > 0)
    print("SlabsHub sales agent prototype")
    print("  model    : " + MODEL)
    print("  catalog  : " + str(len(PRODUCTS)) + " products, " + str(in_stock) + " in stock")
    print("  api key  : " + ("found" if load_key() else "MISSING - add ANTHROPIC_API_KEY to .env"))
    print("  open     : http://localhost:" + str(PORT))
    Handler.timeout = 30
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    srv.daemon_threads = True
    srv.serve_forever()
