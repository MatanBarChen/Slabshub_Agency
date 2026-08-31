"""Render slabshub-chat.liquid as a standalone page, in the homepage's design system.

The tokens and page chrome below are copied from sections/comics-index.liquid so the
preview shows the component exactly as it will look in place. Run, then open
preview.html (or serve it) to check the design before touching the live theme.
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "https://uvlkacfnbnsqpizktcfi.supabase.co/functions/v1/chat"

src = io.open(os.path.join(HERE, "slabshub-chat.liquid"), encoding="utf-8").read()
src = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", src, flags=re.S)
src = re.sub(r"\{%-?\s*assign.*?-?%\}", "", src)
src = src.replace("{{ SHC_ENDPOINT }}", ENDPOINT).strip()

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SlabsHub — The Enquiry Desk (preview)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Lora:ital,wght@0,400;0,600;1,400;1,600&display=swap" rel="stylesheet">
<style>
  :root {
    --color-honeycomb-yellow: #ffd931;
    --color-carbon-black: #000000;
    --color-ink-black: #231f20;
    --color-fog-gray: #a6a8aa;
    --color-smoke-line: #d6d6d6;
    --font-display: 'Times Now', 'Playfair Display', 'Times New Roman', serif;
    --font-body: 'Times New Roman', Times, serif;
    --font-ui: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    --font-product: 'Lora', 'Times New Roman', serif;
    --text-caption: 11px; --text-body: 16px; --text-subheading: 23px;
    --text-heading-sm: 27px; --text-heading: 40px; --text-display: 47px;
    --tracking-ui: 0.073em; --tracking-nav: 0.063em; --tracking-wide: 0.091em;
    --page-max-width: 1200px; --gap: 15px;
    --radius-card: 12px; --radius-pill: 25px; --radius-hero: 45px;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background-color: #dce8f2;
    background-image:
      linear-gradient(rgba(46, 111, 183, 0.10) 1px, transparent 1px),
      linear-gradient(90deg, rgba(46, 111, 183, 0.10) 1px, transparent 1px);
    background-size: 22px 22px;
    color: var(--color-carbon-black);
    font-family: var(--font-body); font-size: var(--text-body); line-height: 1.15;
  }
  a { color: inherit; text-decoration: none; }
  .wrap { max-width: var(--page-max-width); margin: 0 auto; padding: 0 20px; }
  section { padding: 42px 0; }
  .badge { display: inline-block; background: var(--color-fog-gray); border-radius: var(--radius-card); padding: 3px 9px; font-family: var(--font-ui); font-size: var(--text-caption); letter-spacing: var(--tracking-ui); text-transform: uppercase; }
  .badge.stock { background: transparent; border: 1px solid var(--color-carbon-black); }
  .masthead { background: var(--color-honeycomb-yellow); border-bottom: 2px solid var(--color-carbon-black); }
  .logo-row { text-align: center; padding: 26px 20px 16px; }
  .logo { font-family: var(--font-display); font-weight: 500; font-size: 64px; line-height: 0.87; }
  .logo em { font-style: italic; font-weight: 400; }
  .logo-tag { display: block; margin-top: 10px; font-family: var(--font-ui); font-size: var(--text-caption); letter-spacing: 0.24em; text-transform: uppercase; }
  .hero { padding: 55px 0 40px; text-align: center; }
  .hero .kicker-row { display: flex; justify-content: center; margin-bottom: 18px; }
  .hero h1 { font-family: var(--font-display); font-weight: 400; font-size: var(--text-display); line-height: 0.9; max-width: 760px; margin: 0 auto 16px; }
  .hero h1 em { font-style: italic; }
  .hero p { line-height: 1.3; color: var(--color-ink-black); max-width: 520px; margin: 0 auto; }
  .section-head { display: flex; align-items: baseline; justify-content: space-between; gap: 15px; margin-bottom: 25px; border-top: 3px solid var(--color-carbon-black); padding-top: 5px; position: relative; }
  .section-head::before { content: ""; position: absolute; top: 5px; left: 0; right: 0; border-top: 1px solid var(--color-carbon-black); }
  .section-head h2 { font-family: var(--font-display); font-weight: 500; font-size: var(--text-heading-sm); line-height: 0.9; padding-top: 12px; }
  .section-head h2 .no { font-family: var(--font-ui); font-weight: 100; font-size: 14px; letter-spacing: var(--tracking-ui); vertical-align: super; margin-right: 6px; }
  .card { background: #fff; border: 1px solid var(--color-carbon-black); border-radius: var(--radius-card); padding: var(--gap); }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap); }
  .stub { height: 210px; display: flex; align-items: center; justify-content: center; font-family: var(--font-ui); font-size: var(--text-caption); letter-spacing: var(--tracking-ui); text-transform: uppercase; color: var(--color-fog-gray); }
</style>
</head>
<body>

<header class="masthead">
  <div class="logo-row">
    <span class="logo">Slabs<em>Hub</em></span>
    <span class="logo-tag">The Graded Card Circular</span>
  </div>
</header>

<section class="hero">
  <div class="wrap">
    <div class="kicker-row"><span class="badge stock">Collector-run &middot; Israel &rarr; worldwide</span></div>
    <h1>Every card tells a story.<br><em>Ours come with a grade.</em></h1>
    <p>Graded Pok&eacute;mon slabs and hand-picked raw cards &mdash; photographed in-hand, priced against real sold listings, shipped protected.</p>
  </div>
</section>

__COMPONENT__

<section>
  <div class="wrap">
    <div class="section-head"><h2><span class="no">&#8470; 1</span>Fresh pulls, ready to ship</h2></div>
    <div class="grid-3">
      <div class="card stub">card</div><div class="card stub">card</div><div class="card stub">card</div>
    </div>
  </div>
</section>

</body>
</html>
"""

out = PAGE.replace("__COMPONENT__", src)
path = os.path.join(HERE, "preview.html")
io.open(path, "w", encoding="utf-8").write(out)
print("wrote " + path)
