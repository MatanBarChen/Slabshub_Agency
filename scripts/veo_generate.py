"""Veo video generation helper for agency agents.

Reads GEMINI_API_KEY from .env internally and NEVER prints it.
Usage:
  py scripts/veo_generate.py --image "path/to/start-frame" --prompt-file "path/to/prompt.txt" --out "path/to/out.mp4" [--model veo-3.1-fast-generate-preview] [--aspect 9:16] [--seconds 8]
"""
import argparse
import base64
import json
import subprocess
import sys
import time
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
API = "https://generativelanguage.googleapis.com/v1beta"


def _key() -> str:
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("GEMINI_API_KEY="):
            return line.split("=", 1)[1].strip()
    sys.exit("GEMINI_API_KEY not found in .env")


def _curl(args, timeout=180):
    p = subprocess.run(["curl", "-s", *args], capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        sys.exit(f"curl failed (exit {p.returncode})")
    return p.stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="veo-3.1-fast-generate-preview")
    ap.add_argument("--aspect", default="9:16")
    ap.add_argument("--seconds", type=int, default=8)
    a = ap.parse_args()

    key = _key()
    img = Path(a.image).read_bytes()
    mime = "image/jpeg" if img[:2] == b"\xff\xd8" else "image/png"
    prompt = Path(a.prompt_file).read_text(encoding="utf-8").strip()

    body = {
        "instances": [{
            "prompt": prompt,
            "image": {"bytesBase64Encoded": base64.b64encode(img).decode(), "mimeType": mime},
        }],
        "parameters": {"aspectRatio": a.aspect, "durationSeconds": a.seconds},
    }
    tmp = Path(a.out).with_suffix(".req.json")
    tmp.write_text(json.dumps(body), encoding="utf-8")

    op = json.loads(_curl(["-X", "POST", f"{API}/models/{a.model}:predictLongRunning",
                           "-H", f"x-goog-api-key: {key}", "-H", "Content-Type: application/json",
                           "-d", f"@{tmp}"]))
    tmp.unlink(missing_ok=True)
    name = op.get("name")
    if not name:
        sys.exit(f"submit failed: {json.dumps(op)[:400]}")
    print(f"submitted: {name}")

    for i in range(60):
        time.sleep(10)
        st = json.loads(_curl(["-H", f"x-goog-api-key: {key}", f"{API}/{name}"]))
        if st.get("done"):
            if st.get("error"):
                sys.exit(f"operation error: {json.dumps(st['error'])[:400]}")
            samples = st.get("response", {}).get("generateVideoResponse", {}).get("generatedSamples", [])
            if not samples:
                sys.exit(f"no samples: {json.dumps(st.get('response', {}))[:400]}")
            uri = samples[0]["video"]["uri"]
            _curl(["-L", "-H", f"x-goog-api-key: {key}", "-o", a.out, uri], timeout=300)
            size = Path(a.out).stat().st_size
            if size < 100_000:
                sys.exit(f"download too small ({size} bytes) — check {a.out} for an error body")
            print(f"SAVED: {a.out} ({size} bytes)")
            return
    sys.exit("timeout waiting for operation")


if __name__ == "__main__":
    main()
