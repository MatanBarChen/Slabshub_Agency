"""Bakes the IG-feed overlay onto promo-main.png and exports at 1080x1350.

Follows assets/2026-08-04-slab-guard-launch/image-spec.md sec. "IG feed",
with the price badge set to the live store price (₪19, verified
2026-08-26). Renders through Chromium so the brand fonts are used directly.
"""
import base64, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAMP = ROOT / "assets" / "2026-08-04-slab-guard-launch"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
GOLD, INK = "#D9B36B", "#0B0B0D"

img = base64.b64encode((CAMP / "promo-main.png").read_bytes()).decode()
fonts = (ROOT / "docs" / "widget" / "fonts.css").read_text(encoding="utf-8")


def build(out, w, h, headline=None, price=None, show_promo=True):
    """headline=None renders the clean upscale with no overlay (FB organic uses this)."""
    HTML = f"""<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8"><style>
{fonts}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;background:{INK}}}
.canvas{{position:relative;width:{w}px;height:{h}px;background:{INK}}}
.base{{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;background:{INK}}}
/* keeps the headline legible over the upper third without dimming the product */
.veil{{position:absolute;left:0;right:0;top:0;height:38%;
 background:linear-gradient(180deg,rgba(11,11,13,.92) 0%,rgba(11,11,13,.55) 62%,rgba(11,11,13,0) 100%)}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:22%;
 background:linear-gradient(0deg,rgba(11,11,13,.90) 0%,rgba(11,11,13,.45) 55%,rgba(11,11,13,0) 100%)}}
.headline{{position:absolute;top:{int(h*0.062)}px;right:{int(w*0.068)}px;left:{int(w*0.068)}px;
 font-family:'Frank Ruhl Libre',serif;font-weight:700;color:#fff;text-align:right;
 font-size:{int(w*0.093)}px;line-height:1.16;letter-spacing:-.015em;
 text-shadow:0 2px 18px rgba(0,0,0,.6)}}
.badge{{position:absolute;bottom:{int(h*0.055)}px;right:{int(w*0.068)}px;text-align:right}}
.eyebrow{{font-family:'Heebo',sans-serif;font-weight:500;color:rgba(255,255,255,.72);
 font-size:{int(w*0.027)}px;letter-spacing:.14em;margin-bottom:{int(h*0.011)}px}}
.pill{{display:inline-block;background:{INK};border:{max(2,int(w*0.0028))}px solid {GOLD};
 border-radius:999px;padding:{int(h*0.013)}px {int(w*0.045)}px;color:#fff;
 font-family:'Heebo',sans-serif;font-weight:700;font-size:{int(w*0.062)}px;
 letter-spacing:.01em;direction:ltr;box-shadow:0 6px 26px rgba(0,0,0,.55)}}
.promo{{position:absolute;bottom:{int(h*0.062)}px;left:{int(w*0.068)}px;
 background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.34);
 border-radius:999px;padding:{int(h*0.009)}px {int(w*0.032)}px;color:#fff;
 font-family:'Heebo',sans-serif;font-weight:500;font-size:{int(w*0.028)}px;
 letter-spacing:.02em;backdrop-filter:blur(3px)}}
</style></head><body><div class="canvas">
<img class="base" src="data:image/png;base64,{img}">
{'<div class="veil"></div><div class="foot"></div>' if headline else ''}
{f'<div class="headline">{headline}</div>' if headline else ''}
{f'<div class="badge"><div class="eyebrow">סיליקון ל-PSA</div><span class="pill">{price}</span></div>' if price else ''}
{'<div class="promo">3 ומעלה — 15% הנחה</div>' if headline and show_promo else ''}
</div></body></html>"""
    tmp = CAMP / "_render.html"
    tmp.write_text(HTML, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={w},{h}",
                    f"--screenshot={out}", f"file://{tmp}"], check=True, capture_output=True)
    tmp.unlink()
    print(f"{out.name}  {w}x{h}")


if __name__ == "__main__":
    build(CAMP / "ig-feed-1080x1350.png", 1080, 1350, "הסלאב שלך.<br>הצבע שלך.", "₪19")
    # FB organic runs the same hero clean — image-spec.md defines no overlay for it
    build(CAMP / "fb-organic-1080x1350-clean.png", 1080, 1350)
