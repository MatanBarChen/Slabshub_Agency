"""Gemini text-to-image helper for agency agents.

Reads GEMINI_API_KEY from .env internally and NEVER prints it.
Generates a background/scene image ONLY (no product card in the prompt) to avoid
AI text-corruption risk on card text — the real product photo is composited on
top separately with Pillow.

Usage:
  py scripts/gemini_image.py --prompt-file "path/to/prompt.txt" --out "path/to/bg.png" [--model gemini-3.1-flash-image] [--aspect 4:5]
"""
import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
API = "https://generativelanguage.googleapis.com/v1beta"


def _key() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY not found in .env")


def _curl(args, timeout=120):
    p = subprocess.run(["curl", "-s", *args], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.exit(f"curl failed (exit {p.returncode})")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="gemini-3.1-flash-image")
    ap.add_argument("--aspect", default="4:5")
    a = ap.parse_args()

    key = _key()
    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": a.aspect},
        },
    }
    tmp = Path(a.out).with_suffix(".req.json")
    tmp.write_text(json.dumps(body), encoding="utf-8")

    resp = _curl(["-X", "POST", f"{API}/models/{a.model}:generateContent",
                  "-H", f"x-goog-api-key: {key}", "-H", "Content-Type: application/json",
                  "-d", f"@{tmp}"])
    tmp.unlink(missing_ok=True)

    data = json.loads(resp)
    if "error" in data:
        sys.exit(f"API error: {json.dumps(data['error'])[:500]}")

    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError):
        sys.exit(f"unexpected response shape: {json.dumps(data)[:500]}")

    img_b64 = None
    for part in parts:
        if "inlineData" in part:
            img_b64 = part["inlineData"]["data"]
            break
    if not img_b64:
        sys.exit(f"no image in response: {json.dumps(data)[:500]}")

    Path(a.out).write_bytes(base64.b64decode(img_b64))
    size = Path(a.out).stat().st_size
    if size < 10_000:
        sys.exit(f"output too small ({size} bytes) — likely an error image")
    print(f"SAVED: {a.out} ({size} bytes)")


if __name__ == "__main__":
    main()
