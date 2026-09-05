"""Render comics-chat.liquid to standalone HTML, once per language.

The section is a full document already, so unlike the inline-section preview there
is no page chrome to fake — but it IS driven by Liquid conditionals, so this
resolves the subset of Liquid the file actually uses rather than stripping tags
blindly. If a construct is added to the section that isn't handled here, this
raises instead of silently rendering something that differs from the storefront.

Run: py build_preview.py   ->   preview-he.html, preview-en.html
Serve over localhost (not file://) — the edge function rejects a null origin.
"""
import datetime
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "comics-chat.liquid")

# Storefront globals the section touches. No favicon in preview, so the block
# guarded by `settings.favicon != blank` is dropped exactly as it would be.
CONDITIONS = {
    "settings.favicon != blank": False,
}


def resolve_ifs(text, lang):
    """Collapse {% if %}/{% else %}/{% endif %}, innermost first."""
    conds = dict(CONDITIONS)
    conds["lang == 'en'"] = (lang == "en")

    pattern = re.compile(
        r"\{%-?\s*if\s+(?P<cond>[^%]+?)\s*-?%\}"
        r"(?P<body>(?:(?!\{%-?\s*(?:if|endif)\b).)*?)"
        r"\{%-?\s*endif\s*-?%\}",
        re.S,
    )
    while True:
        m = pattern.search(text)
        if not m:
            break
        cond = m.group("cond").strip()
        if cond not in conds:
            raise ValueError("preview cannot evaluate condition: " + cond)
        body = m.group("body")
        parts = re.split(r"\{%-?\s*else\s*-?%\}", body)
        chosen = parts[0] if conds[cond] else (parts[1] if len(parts) > 1 else "")
        text = text[:m.start()] + chosen + text[m.end():]
    if re.search(r"\{%-?\s*(if|else|endif)\b", text):
        raise ValueError("unresolved if/else left in template")
    return text


def collect_assigns(text):
    """Pull {% assign %} values out in order, returning (vars, text-without-them)."""
    vars_ = {}
    out = []
    for line in text.split("\n"):
        m = re.match(r"\s*\{%-?\s*assign\s+(\w+)\s*=\s*(.+?)\s*-?%\}\s*$", line)
        if not m:
            out.append(line)
            continue
        name, expr = m.group(1), m.group(2)
        lit = re.match(r"^'(.*)'$", expr, re.S)
        if lit:
            vars_[name] = lit.group(1)
            continue
        split = re.match(r"^(\w+)\s*\|\s*split:\s*'(.*)'$", expr)
        if split:
            vars_[name] = vars_[split.group(1)].split(split.group(2))
            continue
        default = re.match(r"^section\.settings\.\w+\s*\|\s*default:\s*'(.*)'$", expr)
        if default:
            continue  # lang is supplied by resolve_ifs, not needed downstream
        raise ValueError("preview cannot evaluate assign: " + expr)
    return vars_, "\n".join(out)


def expand_fors(text, vars_):
    pattern = re.compile(
        r"\{%-?\s*for\s+(\w+)\s+in\s+(\w+)\s*-?%\}(.*?)\{%-?\s*endfor\s*-?%\}", re.S
    )

    def sub(m):
        item, coll, body = m.group(1), m.group(2), m.group(3)
        values = vars_.get(coll) or []
        return "".join(body.replace("{{ " + item + " }}", v) for v in values)

    text = pattern.sub(sub, text)
    if re.search(r"\{%-?\s*(for|endfor)\b", text):
        raise ValueError("unresolved for loop left in template")
    return text


def substitute(text, vars_, lang):
    year = str(datetime.date.today().year)
    text = text.replace("{{ 'now' | date: '%Y' }}", year)
    text = text.replace("{{ canonical_url }}", "https://slabshub.com/pages/preview")
    text = text.replace("{{ lang }}", lang)

    def one(m):
        name, filt = m.group(1), m.group(2)
        if name not in vars_:
            raise ValueError("preview has no value for {{ " + name + " }}")
        val = vars_[name]
        if filt == "escape":
            val = (val.replace("&", "&amp;").replace("<", "&lt;")
                      .replace(">", "&gt;").replace('"', "&quot;"))
        return val

    text = re.sub(r"\{\{\s*(\w+)(?:\s*\|\s*(\w+))?\s*\}\}", one, text)
    if "{{" in text or "{%" in text:
        leftover = re.findall(r"\{[{%][^}]*[}%]\}", text)[:3]
        raise ValueError("unrendered Liquid left: " + repr(leftover))
    return text


def build(lang):
    src = io.open(SRC, encoding="utf-8").read()
    src = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", src, flags=re.S)
    src = re.sub(r"\{%\s*schema\s*%\}.*?\{%\s*endschema\s*%\}", "", src, flags=re.S)
    src = resolve_ifs(src, lang)
    vars_, src = collect_assigns(src)
    src = expand_fors(src, vars_)
    src = substitute(src, vars_, lang).strip() + "\n"
    path = os.path.join(HERE, "preview-" + lang + ".html")
    io.open(path, "w", encoding="utf-8").write(src)
    return path, len(src)


for lang in ("he", "en"):
    path, size = build(lang)
    print("wrote " + os.path.basename(path) + "  (" + str(size) + " chars)")
