#!/usr/bin/env python3
"""Bake final publish-ready Slab Guard assets from the campaign spec.

Reads:  assets/2026-08-04-slab-guard-launch/{promo-main.png, reel-handfan.mp4}
Writes: assets/2026-08-04-slab-guard-launch/export/
          promo-ig-feed-1080x1350.png   IG feed hero, overlays baked in
          promo-fb-organic-1080x1350.png FB organic, clean (no overlay per draft)
          reel-handfan-story-1080x1920.mp4  IG story, 3 RTL frame texts burned in

Overlay copy/placement follows image-spec.md; the story frame texts follow the
approved draft (which supersedes video-storyboard.md). Text is rendered through
Chromium so Hebrew RTL shaping is correct, then composited with ffmpeg.
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parent.parent
CAMP = ROOT / "assets" / "2026-08-04-slab-guard-launch"
OUT = CAMP / "export"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

INK = "#0B0B0D"
GOLD = "#D9B36B"

FONT = '"Heebo","DejaVu Sans",sans-serif'

# Story frame texts, from the approved draft. (start, end) in seconds of the 8s clip.
STORY_FRAMES = [
    (0.0, 2.7, "הסלאב שרד את הדירוג.<br>עכשיו תגנו עליו 🛡️", None),
    (2.7, 5.4, "מתאים ל-PSA", "₪19–22 · 15% הנחה מ-3 יחידות"),
    (5.4, 8.0, "לינק בסטורי → Slab Guard", "25 יחידות בלבד"),
]


def shoot(html, out, w, h, transparent=False):
    """Render an HTML string to a PNG at exactly w x h."""
    tmp = Path("/tmp/claude-0") / f"bake-{out.stem}.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(html, encoding="utf-8")
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={w},{h}", "--force-device-scale-factor=1",
        "--virtual-time-budget=3000", f"--screenshot={out}", str(tmp),
    ]
    if transparent:
        cmd.insert(2, "--default-background-color=00000000")
    subprocess.run(cmd, check=True, capture_output=True)
    return out


def base_css(w, h):
    return f"""
  @page {{ margin:0 }}
  * {{ margin:0; padding:0; box-sizing:border-box }}
  html,body {{ width:{w}px; height:{h}px; overflow:hidden }}
  body {{ font-family:{FONT}; direction:rtl; }}
"""


def ig_feed():
    """IG feed hero — 1080x1350, headline + price pill + promo micro-badge."""
    bg = (CAMP / "promo-main.png").as_uri()
    html = f"""<meta charset="utf-8"><style>{base_css(1080, 1350)}
  body {{ background:{INK} url("{bg}") center/cover no-repeat; position:relative; }}
  /* keep the top zone readable without hiding the product */
  .scrim-top {{ position:absolute; inset:0 0 auto 0; height:44%;
                background:linear-gradient(180deg,rgba(11,11,13,.92) 0%,rgba(11,11,13,.55) 55%,rgba(11,11,13,0) 100%); }}
  .scrim-bot {{ position:absolute; inset:auto 0 0 0; height:26%;
                background:linear-gradient(0deg,rgba(11,11,13,.9) 0%,rgba(11,11,13,.35) 60%,rgba(11,11,13,0) 100%); }}
  h1 {{ position:absolute; top:84px; right:72px; left:72px; text-align:right;
        color:#fff; font-weight:900; font-size:96px; line-height:1.04;
        letter-spacing:-2.5px; text-shadow:0 4px 40px rgba(0,0,0,.6); }}
  h1 em {{ font-style:normal; color:{GOLD}; }}
  .kicker {{ position:absolute; top:36px; right:74px; color:{GOLD}; font-weight:700;
             font-size:26px; letter-spacing:5px; opacity:.9; }}
  .price {{ position:absolute; bottom:76px; right:72px; text-align:center; }}
  .price .cap {{ color:rgba(255,255,255,.72); font-size:25px; font-weight:400;
                 letter-spacing:2.5px; margin-bottom:14px; }}
  .price .pill {{ display:inline-block; background:rgba(11,11,13,.82); border:2.5px solid {GOLD};
                  color:#fff; font-weight:900; font-size:62px; padding:12px 42px;
                  border-radius:999px; letter-spacing:-1px;
                  box-shadow:0 10px 44px rgba(0,0,0,.55); }}
  .promo {{ position:absolute; bottom:96px; left:72px; display:inline-block;
            background:rgba(255,255,255,.1); border:1.5px solid rgba(255,255,255,.32);
            color:#fff; font-weight:700; font-size:28px; padding:13px 26px;
            border-radius:999px; backdrop-filter:blur(6px); }}
</style>
<div class="scrim-top"></div><div class="scrim-bot"></div>
<div class="kicker">SLAB GUARD</div>
<h1>הסלאב שלך.<br><em>הצבע שלך.</em></h1>
<div class="promo">15% הנחה מ-3 יחידות</div>
<div class="price"><div class="cap">סיליקון ל-PSA</div><div class="pill">₪19</div></div>
"""
    return shoot(html, OUT / "promo-ig-feed-1080x1350.png", 1080, 1350)


def fb_organic():
    """FB organic — same hero, clean upscale, no ad-style overlay (per draft)."""
    out = OUT / "promo-fb-organic-1080x1350.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error", "-i", str(CAMP / "promo-main.png"),
        "-vf", "scale=1080:1350:flags=lanczos", str(out),
    ], check=True)
    return out


def ig_feed_proof():
    """Alternative IG feed hero built from the real in-use footage.

    image-spec.md flags "guard actually mounted on a graded slab" as the single
    strongest missing asset for this launch — but reel-handfan.mp4 already
    contains exactly that shot. This pulls a still from it (t=6.8s, fan fully
    spread, hand in frame) and dresses it with the same overlay system.
    """
    still = Path("/tmp/claude-0/proof-still.png")
    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error", "-ss", "6.8", "-i", str(CAMP / "reel-handfan.mp4"),
        "-frames:v", "1",
        # drop the baked-in letterbox, then crop 4:3 -> 4:5 and scale to feed size
        "-vf", "crop=720:960:0:160,crop=720:900:0:60,scale=1080:1350:flags=lanczos",
        str(still),
    ], check=True)

    bg = still.as_uri()
    html = f"""<meta charset="utf-8"><style>{base_css(1080, 1350)}
  body {{ background:{INK} url("{bg}") center/cover no-repeat; position:relative; }}
  .scrim-top {{ position:absolute; inset:0 0 auto 0; height:42%;
                background:linear-gradient(180deg,rgba(11,11,13,.93) 0%,rgba(11,11,13,.6) 52%,rgba(11,11,13,0) 100%); }}
  .scrim-bot {{ position:absolute; inset:auto 0 0 0; height:30%;
                background:linear-gradient(0deg,rgba(11,11,13,.93) 0%,rgba(11,11,13,.4) 60%,rgba(11,11,13,0) 100%); }}
  .kicker {{ position:absolute; top:40px; right:74px; color:{GOLD}; font-weight:700;
             font-size:26px; letter-spacing:5px; opacity:.92; }}
  h1 {{ position:absolute; top:92px; right:72px; left:72px; text-align:right;
        color:#fff; font-weight:900; font-size:88px; line-height:1.06;
        letter-spacing:-2.4px; text-shadow:0 4px 40px rgba(0,0,0,.7); }}
  h1 em {{ font-style:normal; color:{GOLD}; }}
  .price {{ position:absolute; bottom:76px; right:72px; text-align:center; }}
  .price .cap {{ color:rgba(255,255,255,.75); font-size:25px; font-weight:400;
                 letter-spacing:2.5px; margin-bottom:14px; }}
  .price .pill {{ display:inline-block; background:rgba(11,11,13,.85); border:2.5px solid {GOLD};
                  color:#fff; font-weight:900; font-size:62px; padding:12px 42px;
                  border-radius:999px; letter-spacing:-1px;
                  box-shadow:0 10px 44px rgba(0,0,0,.6); }}
  .promo {{ position:absolute; bottom:96px; left:72px; display:inline-block;
            background:rgba(255,255,255,.12); border:1.5px solid rgba(255,255,255,.34);
            color:#fff; font-weight:700; font-size:28px; padding:13px 26px;
            border-radius:999px; }}
</style>
<div class="scrim-top"></div><div class="scrim-bot"></div>
<div class="kicker">SLAB GUARD</div>
<h1>הסלאב שרד<br>את הדירוג.<br><em>עכשיו תשמור עליו.</em></h1>
<div class="promo">15% הנחה מ-3 יחידות</div>
<div class="price"><div class="cap">סיליקון ל-PSA</div><div class="pill">₪19</div></div>
"""
    return shoot(html, OUT / "promo-ig-feed-proof-1080x1350.png", 1080, 1350)


def story_overlay(idx, headline, sub):
    """One transparent 1080x1920 text plate.

    Layout matches the reframed video: the clip sits at y=330..1610, so the top
    330px is a clean dark band for the headline and the bottom 310px stays clear
    for IG's native link sticker.
    """
    sub_html = f'<div class="sub">{sub}</div>' if sub else ""
    html = f"""<meta charset="utf-8"><style>{base_css(1080, 1920)}
  body {{ background:transparent; position:relative; }}
  .scrim {{ position:absolute; inset:0 0 auto 0; height:660px;
            background:linear-gradient(180deg,rgba(11,11,13,.95) 0%,rgba(11,11,13,.9) 46%,rgba(11,11,13,0) 100%); }}
  .box {{ position:absolute; top:104px; right:70px; left:70px; text-align:right; }}
  .kicker {{ color:{GOLD}; font-weight:700; font-size:27px; letter-spacing:6px;
             margin-bottom:22px; }}
  h2 {{ color:#fff; font-weight:900; font-size:64px; line-height:1.14;
        letter-spacing:-1.8px; text-shadow:0 4px 34px rgba(0,0,0,.75); }}
  .sub {{ margin-top:26px; display:inline-block; background:rgba(11,11,13,.8);
          border:1.5px solid {GOLD}; border-radius:999px; color:#fff;
          font-weight:700; font-size:33px; padding:14px 30px; }}
</style>
<div class="scrim"></div>
<div class="box"><div class="kicker">SLAB GUARD</div><h2>{headline}</h2>{sub_html}</div>
"""
    return shoot(html, Path(f"/tmp/claude-0/story-f{idx}.png"), 1080, 1920, transparent=True)


def story_video():
    """Reframe the clip to a real 1080x1920 story and burn in the three frame texts.

    The source is 720x1280 but the actual footage is only 720x960 — it ships with
    baked-in letterbox bars (cropdetect: crop=720:960:0:160). Those are cropped
    off, the footage is scaled to 960x1280 and padded onto a #0B0B0D 1080x1920
    canvas, which also creates the clean text band at the top.
    """
    src = CAMP / "reel-handfan.mp4"
    out = OUT / "reel-handfan-story-1080x1920.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    plates = [story_overlay(i, h, s) for i, (_, _, h, s) in enumerate(STORY_FRAMES)]

    inputs = ["-i", str(src)]
    for p in plates:
        # -loop/-t give each still a real 8s timeline; without it the fade filter
        # freezes every plate at its t=0 alpha (i.e. fully transparent).
        inputs += ["-loop", "1", "-t", "8", "-i", str(p)]

    steps = [
        f"[0:v]crop=720:960:0:160,scale=960:1280:flags=lanczos,"
        f"pad=1080:1920:60:330:color={INK},setsar=1[base]"
    ]
    prev = "base"
    for i, (start, end, _, _) in enumerate(STORY_FRAMES):
        # cross-fade each plate in/out so text does not pop
        steps.append(
            f"[{i+1}:v]format=rgba,fade=t=in:st={start:.2f}:d=0.35:alpha=1,"
            f"fade=t=out:st={end - 0.35:.2f}:d=0.35:alpha=1[p{i}]"
        )
        steps.append(f"[{prev}][p{i}]overlay=0:0:enable='between(t,{start:.2f},{end:.2f})'[v{i}]")
        prev = f"v{i}"

    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error", *inputs,
        "-filter_complex", ";".join(steps),
        "-map", f"[{prev}]", "-map", "0:a?", "-t", "8",
        "-c:v", "libx264", "-profile:v", "high", "-crf", "18", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-r", "24", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "160k", str(out),
    ], check=True)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in (ig_feed, ig_feed_proof, fb_organic, story_video):
        path = fn()
        print(f"{path.relative_to(ROOT)}  ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.exit(main())
