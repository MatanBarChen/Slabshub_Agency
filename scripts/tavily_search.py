"""Tavily helper for agency agents.

Reads TAVILY_API_KEY from .env internally and NEVER prints it — results only.
Usage:
  py scripts/tavily_search.py search "query" [--max 5] [--days N] [--topic news|general] [--answer]
  py scripts/tavily_search.py extract "https://url1" ["https://url2" ...]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def _key() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("TAVILY_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("TAVILY_API_KEY not found in .env")


def _post(endpoint: str, payload: dict) -> dict:
    # curl instead of urllib: the local TLS-inspection proxy breaks Python's cert validation
    proc = subprocess.run(
        [
            "curl", "-s", "-X", "POST", f"https://api.tavily.com/{endpoint}",
            "-H", f"Authorization: Bearer {_key()}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload),
        ],
        capture_output=True, text=True, timeout=90,
        encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        sys.exit(f"curl failed (exit {proc.returncode})")
    d = json.loads(proc.stdout)
    if isinstance(d, dict) and d.get("detail"):
        sys.exit(f"API ERROR: {d['detail']}")
    return d


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--max", type=int, default=5)
    s.add_argument("--days", type=int, default=None)
    s.add_argument("--topic", default="general")
    s.add_argument("--answer", action="store_true")

    e = sub.add_parser("extract")
    e.add_argument("urls", nargs="+")

    args = ap.parse_args()

    if args.cmd == "search":
        payload = {
            "query": args.query,
            "max_results": args.max,
            "topic": args.topic,
            "include_answer": args.answer,
        }
        if args.days:
            payload["days"] = args.days
        d = _post("search", payload)
        if d.get("answer"):
            print("ANSWER:", d["answer"])
        for r in d.get("results", []):
            print(f"- {r.get('title', '')[:100]}\n  {r.get('url')}\n  {r.get('content', '')[:200]}")
    else:
        d = _post("extract", {"urls": args.urls})
        for r in d.get("results", []):
            print(f"=== {r.get('url')} ===")
            print(r.get("raw_content", "")[:4000])
        for f in d.get("failed_results", []):
            print(f"FAILED: {f.get('url')}")


if __name__ == "__main__":
    main()
