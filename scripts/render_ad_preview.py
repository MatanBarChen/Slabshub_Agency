#!/usr/bin/env python3
"""Compose an Instagram-style preview of a finished feed post (visual + caption).

Usage: python3 scripts/render_ad_preview.py <image> <caption.txt> <out.png> [handle]

Renders the picked visual and its final caption together as a platform-style
mockup, so the post can be judged the way a follower will actually see it.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
WIDTH = 720


def build(img: Path, caption: str, handle: str) -> str:
    body = html.escape(caption).strip()
    # hashtags and the "link in bio" line read as links on IG
    out_lines = []
    for line in body.split("\n"):
        words = [
            f'<span class="tag">{w}</span>' if w.startswith("#") else w
            for w in line.split(" ")
        ]
        out_lines.append(" ".join(words))
    body = "<br>".join(out_lines)

    return f"""<meta charset="utf-8"><style>
  * {{ margin:0; padding:0; box-sizing:border-box }}
  body {{ width:{WIDTH}px; background:#0a0a0a; font-family:"Heebo","DejaVu Sans",sans-serif;
          color:#f5f5f5; padding:22px; }}
  .card {{ background:#000; border:1px solid #262626; border-radius:14px; overflow:hidden; }}
  .head {{ display:flex; align-items:center; gap:11px; padding:12px 14px; }}
  .av {{ width:36px; height:36px; border-radius:50%; flex:0 0 36px;
         background:conic-gradient(from 200deg,#f9ce34,#ee2a7b,#6228d7,#f9ce34); padding:2px; }}
  .av i {{ display:block; width:100%; height:100%; border-radius:50%; background:#111;
           background-image:linear-gradient(135deg,#2a1f3d,#0e0e12);
           font-style:normal; color:#c9a227; font-size:13px; font-weight:900;
           display:flex; align-items:center; justify-content:center; }}
  .who {{ font-size:14px; font-weight:700; line-height:1.25 }}
  .who small {{ display:block; font-weight:400; font-size:11.5px; color:#a8a8a8 }}
  .dots {{ margin-left:auto; color:#c7c7c7; font-size:19px; letter-spacing:1px }}
  .shot {{ display:block; width:100%; }}
  .acts {{ display:flex; align-items:center; gap:15px; padding:11px 14px 6px;
           font-size:21px; color:#fafafa }}
  .acts .save {{ margin-left:auto }}
  .likes {{ padding:2px 14px 7px; font-size:13.5px; font-weight:700 }}
  .cap {{ padding:0 14px 12px; font-size:13.5px; line-height:1.62; direction:rtl; text-align:right }}
  .cap b {{ font-weight:700 }}
  .tag {{ color:#5b9bd5 }}
  .when {{ padding:0 14px 14px; font-size:11px; color:#8e8e8e; text-transform:uppercase;
           letter-spacing:.4px }}
</style>
<div class="card">
  <div class="head">
    <div class="av"><i>SH</i></div>
    <div class="who">{handle}<small>פוסט אורגני · Instagram Feed</small></div>
    <div class="dots">•••</div>
  </div>
  <img class="shot" src="{img.as_uri()}">
  <div class="acts"><span>♥</span><span>💬</span><span>➤</span><span class="save">🔖</span></div>
  <div class="likes">תצוגה מקדימה — טרם פורסם</div>
  <div class="cap"><b>{handle}</b> {body}</div>
  <div class="when">מתוזמן · רביעי 19/08 20:30 IDT</div>
</div>
<script>addEventListener("load",()=>document.body.setAttribute("data-h",
  document.documentElement.scrollHeight));</script>
"""


def main():
    img = Path(sys.argv[1]).resolve()
    cap_file, out = Path(sys.argv[2]), Path(sys.argv[3])
    handle = sys.argv[4] if len(sys.argv) > 4 else "slabshub"
    page = build(img, cap_file.read_text(encoding="utf-8"), handle)

    tmp = Path("/tmp/claude-0/ad-preview.html")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(page, encoding="utf-8")

    probe = subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", f"--window-size={WIDTH},900",
        "--virtual-time-budget=4000", "--dump-dom", str(tmp),
    ], capture_output=True, text=True).stdout
    m = re.search(r'data-h="(\d+)"', probe)
    height = int(m.group(1)) + 22 if m else 2400
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={WIDTH},{height}", "--force-device-scale-factor=2",
        "--virtual-time-budget=3000", f"--screenshot={out}", str(tmp),
    ], check=True, capture_output=True)
    print(out)


if __name__ == "__main__":
    main()
