"""Meta Graph API connection check for the SlabsHub agency.

Reads META_PAGE_TOKEN / META_PAGE_ID / META_IG_USER_ID from .env internally and
NEVER prints the token — status only.

READ-ONLY. This script cannot publish anything: it only issues GET requests.

Usage:
  py scripts/meta_check.py
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
API = "https://graph.facebook.com/v21.0"

REQUIRED_SCOPES = [
    "pages_show_list",
    "pages_manage_posts",
    "pages_read_engagement",
    "instagram_basic",
    "instagram_content_publish",
    "read_insights",
]


def _env() -> dict:
    if not ENV_PATH.exists():
        sys.exit(f"No .env found at {ENV_PATH}")
    values = {}
    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        values[key.strip()] = val.strip()
    return values


def _get(path: str, token: str, params: str = "") -> dict:
    # curl instead of urllib: the local TLS-inspection proxy breaks Python's cert validation
    url = f"{API}/{path}?access_token={token}"
    if params:
        url += f"&{params}"
    proc = subprocess.run(
        ["curl", "-s", url], capture_output=True, text=True, timeout=60
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"error": {"message": f"Unreadable response: {proc.stdout[:200]}"}}


def _fail(msg: str, fix: str = "") -> None:
    print(f"  ❌ {msg}")
    if fix:
        print(f"     → {fix}")


def main() -> None:
    env = _env()
    token = env.get("META_PAGE_TOKEN", "")
    page_id = env.get("META_PAGE_ID", "")
    ig_id = env.get("META_IG_USER_ID", "")

    print("Meta Graph API — connection check (read-only)\n")

    # --- 1. keys present -----------------------------------------------
    print("1. Values in .env")
    missing = [
        name
        for name, val in (
            ("META_PAGE_TOKEN", token),
            ("META_PAGE_ID", page_id),
            ("META_IG_USER_ID", ig_id),
        )
        if not val
    ]
    if missing:
        for name in missing:
            _fail(f"{name} is empty or missing")
        print("\n     Check the format — no quotes, no spaces around '='.")
        sys.exit(1)
    print(f"  ✅ all three present (token: {len(token)} chars, not shown)\n")

    # --- 2. token identity + expiry ------------------------------------
    print("2. Token")
    debug = _get("debug_token", token, f"input_token={token}")
    if "error" in debug:
        _fail(
            debug["error"].get("message", "unknown error"),
            "Token is invalid or expired. Regenerate it in Graph API Explorer.",
        )
        sys.exit(1)

    data = debug.get("data", {})
    expires = data.get("expires_at", None)
    token_type = data.get("type", "?")
    scopes = data.get("scopes", [])

    print(f"  Type: {token_type}")
    if token_type != "PAGE":
        _fail(
            f"this is a {token_type} token, not a PAGE token",
            "Run me/accounts with a long-lived USER token and take the "
            "access_token from the response.",
        )

    if expires == 0:
        print("  ✅ Expires: never")
    else:
        _fail(
            f"token expires (expires_at={expires})",
            "Extend the USER token in the Access Token Debugger first, then "
            "re-run me/accounts. Otherwise publishing breaks in ~60 days.",
        )

    granted = set(scopes)
    absent = [s for s in REQUIRED_SCOPES if s not in granted]
    if absent:
        _fail(f"missing scopes: {', '.join(absent)}", "Add them and regenerate the token.")
    else:
        print("  ✅ all six required scopes granted")
    print()

    # --- 3. the page ----------------------------------------------------
    print("3. Facebook Page")
    page = _get(page_id, token, "fields=name,username,fan_count")
    if "error" in page:
        _fail(page["error"].get("message", "unknown error"), "Check META_PAGE_ID.")
    else:
        print(f"  ✅ {page.get('name', '?')} (id {page.get('id', '?')})")
        if page.get("fan_count") is not None:
            print(f"     followers: {page['fan_count']}")
    print()

    # --- 4. instagram ----------------------------------------------------
    print("4. Instagram")
    ig = _get(ig_id, token, "fields=username,followers_count,media_count")
    if "error" in ig:
        _fail(
            ig["error"].get("message", "unknown error"),
            "Check META_IG_USER_ID, and that the IG account is Professional "
            "and linked to the Page.",
        )
    else:
        print(f"  ✅ @{ig.get('username', '?')} (id {ig.get('id', '?')})")
        print(
            f"     followers: {ig.get('followers_count', '?')}, "
            f"posts: {ig.get('media_count', '?')}"
        )
    print()

    print("Done. Nothing was published — this check only reads.")


if __name__ == "__main__":
    main()
