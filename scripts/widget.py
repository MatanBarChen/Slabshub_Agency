"""SlabsHub in-chat widget renderer — brand style from the live site.

Builds an HTML sheet using docs/widget/style.css + docs/widget/fonts.css and
screenshots it with headless Chromium.

Usage (from another script):
    from widget import render
    render(body_html, out_png, width=1020, height=900)
"""
import pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "docs" / "widget" / "style.css"
FONTS = ROOT / "docs" / "widget" / "fonts.css"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def sheet(body_html: str, width: int = 1020) -> str:
    return (
        '<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8"><style>'
        + FONTS.read_text(encoding="utf-8")
        + CSS.read_text(encoding="utf-8")
        + f"body{{width:{width}px}}"
        + '</style></head><body><div class="sheet">'
        + body_html
        + "</div></body></html>"
    )


def masthead(edition: str) -> str:
    return (
        '<div class="masthead"><div class="wordmark">SLABSHUB</div>'
        f'<div class="edition">{edition}</div></div>'
    )


def render(body_html: str, out_png, width: int = 1020, height: int = 900, scale: int = 2) -> pathlib.Path:
    out_png = pathlib.Path(out_png)
    with tempfile.TemporaryDirectory() as td:
        html = pathlib.Path(td) / "w.html"
        html.write_text(sheet(body_html, width), encoding="utf-8")
        subprocess.run(
            [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={scale}", f"--window-size={width + 50},{height}",
             f"--screenshot={out_png}", f"file://{html}"],
            check=True, capture_output=True,
        )
    return out_png
