#!/usr/bin/env python3
"""Generate the animated profile SVGs (light + dark) in OTG design language.

Run:  python3 tools/build_svgs.py   -> writes assets/*.svg
Fonts (Geist, Space Mono; SIL OFL) are subset-free woff2 embedded as data URIs,
because an SVG rendered via <img> cannot load external fonts.
"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "tools" / "fonts"
OUT = ROOT / "assets"

# OTG Design System tokens (docs/reference-tokens.md)
THEMES = {
    "light": dict(page="#f9f8f6", card="#ffffff", section="#f5f4f1", border="#e8e5e0",
                  border_light="#f0eeea", text="#1a1a1a", secondary="#5e5b56", muted="#6f6a64",
                  primary="#1d48c0", link="#1d48c0", primary_light="#f0f3fb", primary_subtle="#e4eafa",
                  success="#16a34a", accent="#4338ca", idle="#d9d6d0", grid_op="0.55"),
    "dark": dict(page="#161514", card="#1e1d1b", section="#252422", border="#333130",
                 border_light="#292826", text="#edebe8", secondary="#a8a49e", muted="#98938c",
                 primary="#4d6fd0", link="#7e97e3", primary_light="#1e2a44", primary_subtle="#243056",
                 success="#16a34a", accent="#818cf8", idle="#3d3a36", grid_op="0.7"),
}

MONO_ADV = 0.612  # Space Mono advance width / em (612/1000)


def b64(name):
    return base64.b64encode((FONTS / name).read_bytes()).decode()


def font_css(geist=True, mono=True, mono_bold=False):
    css = []
    if geist:
        css.append("@font-face{font-family:'Geist';font-weight:100 900;"
                   f"src:url(data:font/woff2;base64,{b64('geist-latin-variable.woff2')}) format('woff2');}}")
    if mono:
        css.append("@font-face{font-family:'Space Mono';font-weight:400;"
                   f"src:url(data:font/woff2;base64,{b64('space-mono-latin-400.woff2')}) format('woff2');}}")
    if mono_bold:
        css.append("@font-face{font-family:'Space Mono';font-weight:700;"
                   f"src:url(data:font/woff2;base64,{b64('space-mono-latin-700.woff2')}) format('woff2');}}")
    return "\n".join(css)


BASE_CSS = """
.sans{font-family:'Geist',-apple-system,'Segoe UI',Helvetica,Arial,sans-serif}
.mono{font-family:'Space Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
@media (prefers-reduced-motion: reduce){*{animation:none!important}
.in,.w0,.pfx{opacity:1!important;transform:none!important}.cur{visibility:visible!important}
.spark{stroke-dashoffset:0!important}}
"""


def svg(w, h, title, style, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{title}"><title>{title}</title>'
            f'<style>{style}</style>{body}</svg>\n')


# ---------------------------------------------------------------- header
def header(t):
    W, H = 1200, 340
    words = ["retail media rails.", "ad exchanges.", "mobile apps.", "fintech flows."]
    n = len(words)
    slot = 3.2
    cycle = slot * n
    word_css = []
    for i, _ in enumerate(words):
        a = i / n * 100
        b = (i + 1) / n * 100
        word_css.append(
            f"@keyframes w{i}{{0%,{max(a-0.01,0):.2f}%{{opacity:0;transform:translateY(10px)}}"
            f"{a+1.5:.2f}%,{b-2:.2f}%{{opacity:1;transform:translateY(0)}}"
            f"{b-0.5:.2f}%,100%{{opacity:0;transform:translateY(-10px)}}}}"
            f".w{i}{{opacity:0;animation:w{i} {cycle}s infinite}}")
    style = font_css(mono_bold=True) + BASE_CSS + "".join(word_css) + f"""
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.caret{{animation:blink 1s steps(1) infinite}}
@keyframes pulse{{0%{{r:5;opacity:.9}}100%{{r:16;opacity:0}}}}
.ping{{animation:pulse 1.8s ease-out infinite}}
@keyframes dash{{to{{stroke-dashoffset:-24}}}}
.flow{{stroke-dasharray:3 9;animation:dash 1.2s linear infinite}}
@keyframes ring{{0%{{r:34;opacity:.55}}100%{{r:70;opacity:0}}}}
.ring{{animation:ring 2.4s ease-out infinite}}
.ring2{{animation-delay:1.2s}}
@keyframes rise{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.in{{opacity:0;animation:rise .7s ease-out forwards}}
.d1{{animation-delay:.1s}}.d2{{animation-delay:.3s}}.d3{{animation-delay:.5s}}.d4{{animation-delay:.7s}}
"""
    # network geometry
    cx, cy = 905, 170
    srcs = [("POS", 735, 82), ("DOOH", 715, 140), ("APP", 715, 200), ("WEB", 735, 258)]
    dsts = [("BRAND·A", 1085, 105), ("BRAND·B", 1100, 170), ("BRAND·C", 1085, 235)]
    g = []
    g.append(f'<defs><pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
             f'<circle cx="2" cy="2" r="1.1" fill="{t["border"]}"/></pattern>'
             f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["page"]}" stop-opacity="1"/>'
             f'<stop offset=".55" stop-color="{t["page"]}" stop-opacity=".2"/>'
             f'<stop offset="1" stop-color="{t["page"]}" stop-opacity="0"/></linearGradient></defs>')
    g.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["page"]}" stroke="{t["border"]}"/>')
    g.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#dots)" opacity="{t["grid_op"]}"/>')
    g.append(f'<rect x="1" y="1" width="760" height="{H-2}" rx="12" fill="url(#fade)"/>')

    # edges + packets
    for i, (_, x, y) in enumerate(srcs):
        path = f"M{x+28},{y} C{x+90},{y} {cx-80},{cy} {cx-34},{cy}"
        g.append(f'<path d="{path}" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
        g.append(f'<path class="flow" d="{path}" fill="none" stroke="{t["primary"]}" stroke-width="1.5" opacity=".55"/>')
        g.append(f'<circle r="3.5" fill="{t["primary"]}"><animateMotion dur="2.4s" begin="{i*0.6}s" '
                 f'repeatCount="indefinite" path="{path}" keyPoints="0;1" keyTimes="0;1" calcMode="spline" '
                 f'keySplines=".5 0 .5 1"/></circle>')
    for i, (_, x, y) in enumerate(dsts):
        path = f"M{cx+34},{cy} C{cx+80},{cy} {x-90},{y} {x-40},{y}"
        g.append(f'<path d="{path}" fill="none" stroke="{t["border"]}" stroke-width="1.5"/>')
        g.append(f'<circle r="3.5" fill="{t["success"]}"><animateMotion dur="2.4s" begin="{1.2+i*0.8}s" '
                 f'repeatCount="indefinite" path="{path}" calcMode="spline" keyPoints="0;1" keyTimes="0;1" '
                 f'keySplines=".5 0 .5 1"/></circle>')
    # nodes
    for label, x, y in srcs:
        g.append(f'<rect x="{x-28}" y="{y-13}" width="56" height="26" rx="6" fill="{t["card"]}" stroke="{t["border"]}"/>')
        g.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" class="mono" font-size="10.5" fill="{t["secondary"]}">{label}</text>')
    for label, x, y in dsts:
        g.append(f'<rect x="{x-40}" y="{y-13}" width="80" height="26" rx="6" fill="{t["card"]}" stroke="{t["border"]}"/>')
        g.append(f'<circle cx="{x-27}" cy="{y}" r="2.5" fill="{t["success"]}"/>')
        g.append(f'<text x="{x+5}" y="{y+4}" text-anchor="middle" class="mono" font-size="10.5" fill="{t["secondary"]}">{label}</text>')
    g.append(f'<circle class="ring" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{t["primary"]}" stroke-width="1.5"/>')
    g.append(f'<circle class="ring ring2" cx="{cx}" cy="{cy}" r="34" fill="none" stroke="{t["primary"]}" stroke-width="1.5"/>')
    g.append(f'<circle cx="{cx}" cy="{cy}" r="34" fill="{t["primary"]}"/>')
    g.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" class="mono" font-weight="700" font-size="16" fill="#ffffff">OTG</text>')
    g.append(f'<text x="{cx}" y="{cy+58}" text-anchor="middle" class="mono" font-size="10" letter-spacing="1.5" fill="{t["muted"]}">EXCHANGE</text>')
    # live bid ticker under the exchange
    bids = ["bid 2.41 EUR", "bid 3.08 EUR", "bid 1.97 EUR", "bid 2.76 EUR"]
    tick = []
    for i, b in enumerate(bids):
        tick.append(f'<text class="mono w{i}" style="transform-box:fill-box" x="{cx}" y="{cy+80}" text-anchor="middle" '
                    f'font-size="11" fill="{t["link"]}">{b}</text>')
    g += tick

    # left text block
    x0 = 64
    g.append(f'<text class="mono in d1" x="{x0}" y="92" font-size="13" letter-spacing="2.2" fill="{t["link"]}">'
             f'FOUNDER &amp; MD · ONE TECH GROUP</text>')
    g.append(f'<text class="sans in d2" x="{x0-3}" y="160" font-size="66" font-weight="640" letter-spacing="-2.2" '
             f'fill="{t["text"]}">Lucas Lingens</text>')
    g.append(f'<g class="in d3"><text class="sans" x="{x0}" y="212" font-size="26" fill="{t["secondary"]}">I build</text>')
    for i, w in enumerate(words):
        g.append(f'<text class="mono w{i}" style="transform-box:fill-box" x="{x0+98}" y="212" font-size="25" '
                 f'font-weight="700" fill="{t["link"]}">{w}</text>')
    g.append('</g>')
    # status pill
    py = 262
    g.append(f'<g class="in d4"><rect x="{x0}" y="{py-17}" width="318" height="32" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>')
    g.append(f'<circle class="ping" cx="{x0+19}" cy="{py-1}" r="5" fill="{t["success"]}"/>')
    g.append(f'<circle cx="{x0+19}" cy="{py-1}" r="2.5" fill="{t["success"]}"/>')
    g.append(f'<text class="mono" x="{x0+34}" y="{py+3}" font-size="12" fill="{t["secondary"]}">shipping with Claude + Codex</text>')
    g.append(f'<rect class="caret" x="{x0+296}" y="{py-8}" width="7" height="14" fill="{t["link"]}"/></g>')
    return svg(W, H, "Lucas Lingens, Founder and MD of One Tech Group", style, "".join(g))


# ---------------------------------------------------------------- focus cards
def focus(t):
    W, H = 1200, 330
    cw, gap, x0, y0, ch = 282, 24, 0, 0, 328  # 4*282+3*24 = 1200
    style = font_css(mono_bold=False) + BASE_CSS + """
@keyframes dash{to{stroke-dashoffset:0}}
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.25}}
.live{animation:blink 1.6s steps(1) infinite}
@keyframes scroll{from{transform:translateY(0)}to{transform:translateY(-120px)}}
.ledger{animation:scroll 6s linear infinite}
@keyframes draw{0%{stroke-dashoffset:420}60%,100%{stroke-dashoffset:0}}
.spark{stroke-dasharray:420;animation:draw 5s ease-out infinite}
"""
    cards = [
        ("01", "AdTech", "Real-time auctions,", "decided in milliseconds."),
        ("02", "Retail Media", "From shelf to screen", "to measured sale."),
        ("03", "Mobile Applications", "Native apps, e.g. live-sync:", "every phone in lockstep."),
        ("04", "FinTech", "Money flows that", "reconcile themselves."),
    ]
    g = []
    g.append(f'<defs><clipPath id="led"><rect x="0" y="0" width="236" height="112"/></clipPath></defs>')
    for i, (num, title, l1, l2) in enumerate(cards):
        x = x0 + i * (cw + gap)
        y = y0 + 1
        g.append(f'<g transform="translate({x},{y})">')
        g.append(f'<rect x=".5" y=".5" width="{cw-1}" height="{ch-3}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>')
        g.append(f'<text class="mono" x="22" y="36" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">{num} /</text>')
        g.append(f'<circle class="live" cx="{cw-30}" cy="32" r="2.5" fill="{t["success"]}"/>')
        # animation stage
        g.append(f'<rect x="22" y="54" width="{cw-44}" height="120" rx="8" fill="{t["section"]}"/>')
        g.append(f'<g transform="translate(22,54)">{STAGES[i](t, cw-44)}</g>')
        g.append(f'<text class="sans" x="22" y="218" font-size="21" font-weight="620" letter-spacing="-.4" fill="{t["text"]}">{title}</text>')
        g.append(f'<text class="sans" x="22" y="250" font-size="14" fill="{t["secondary"]}">{l1}</text>')
        g.append(f'<text class="sans" x="22" y="270" font-size="14" fill="{t["secondary"]}">{l2}</text>')
        tags = TAGS[i]
        tx = 22
        for tag in tags:
            w = len(tag) * 10 * MONO_ADV + 16
            g.append(f'<rect x="{tx}" y="288" width="{w:.0f}" height="20" rx="4" fill="{t["primary_light"]}"/>')
            g.append(f'<text class="mono" x="{tx+8}" y="302" font-size="10" fill="{t["link"]}">{tag}</text>')
            tx += w + 6
        g.append('</g>')
    return svg(W, H, "Focus areas: AdTech, Retail Media, Mobile Applications, FinTech", style, "".join(g))


TAGS = [["RTB", "SSP", "DOOH"], ["CMaaS", "IN-STORE"], ["iOS", "SWIFT", "LIVE-SYNC"], ["BILLING", "LEDGER"]]


def stage_adtech(t, w):
    # 5 bidders, bars animate; winner flashes primary
    out = []
    bw, gap = 26, 14
    base = 100
    vals = [[40, 70, 55, 30, 40], [62, 35, 80, 58, 62], [30, 58, 42, 75, 30], [75, 50, 64, 46, 75], [50, 82, 38, 60, 50]]
    for k in range(5):
        x = 22 + k * (bw + gap)
        hs = vals[k]
        ys = ";".join(str(base - h) for h in hs)
        hh = ";".join(str(h) for h in hs)
        out.append(f'<rect x="{x}" y="{base-hs[0]}" width="{bw}" height="{hs[0]}" rx="3" fill="{t["idle"]}">'
                   f'<animate attributeName="height" values="{hh}" dur="6s" repeatCount="indefinite" calcMode="spline" '
                   f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/>'
                   f'<animate attributeName="y" values="{ys}" dur="6s" repeatCount="indefinite" calcMode="spline" '
                   f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/>'
                   f'<animate attributeName="fill" values="{fills(t, hs)}" keyTimes="0;.25;.5;.75;1" dur="6s" repeatCount="indefinite" calcMode="discrete"/>'
                   f'</rect>')
    out.append(f'<line x1="14" x2="{w-14}" y1="{base+.5}" y2="{base+.5}" stroke="{t["border"]}"/>')
    out.append(f'<text class="mono" x="14" y="18" font-size="10" fill="{t["muted"]}">bids/s 48k</text>')
    out.append(f'<text class="mono" x="{w-14}" y="18" text-anchor="end" font-size="10" fill="{t["link"]}">p95 9ms</text>')
    return "".join(out)


def fills(t, hs):
    # highlight if this bidder is the max at that keyframe (computed across all bidders at render time)
    return ";".join(t["primary"] if h >= 75 else t["idle"] for h in hs)


def stage_retail(t, w):
    out = []
    y = 62
    xs = [36, w / 2, w - 36]
    path = f"M{xs[0]},{y} L{xs[2]},{y}"
    out.append(f'<path d="{path}" stroke="{t["border"]}" stroke-width="2" stroke-dasharray="2 6"/>')
    # shelf icon
    sx = xs[0]
    out.append(f'<g><rect x="{sx-20}" y="{y-24}" width="40" height="48" rx="4" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<line x1="{sx-20}" x2="{sx+20}" y1="{y-4}" y2="{y-4}" stroke="{t["border"]}"/>'
               f'<rect x="{sx-14}" y="{y-18}" width="8" height="12" rx="1" fill="{t["accent"]}"/>'
               f'<rect x="{sx-3}" y="{y-16}" width="8" height="10" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx+8}" y="{y-20}" width="6" height="14" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx-14}" y="{y+2}" width="10" height="14" rx="1" fill="{t["idle"]}"/>'
               f'<rect x="{sx+1}" y="{y+4}" width="12" height="12" rx="1" fill="{t["accent"]}" opacity=".6"/></g>')
    # screen icon (flashes when packet arrives)
    mx = xs[1]
    out.append(f'<rect x="{mx-24}" y="{y-20}" width="48" height="32" rx="4" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<rect x="{mx-19}" y="{y-15}" width="38" height="22" rx="2" fill="{t["primary"]}" opacity=".15">'
               f'<animate attributeName="opacity" values=".15;.15;.9;.15;.15" keyTimes="0;.42;.5;.62;1" dur="3s" repeatCount="indefinite"/></rect>'
               f'<line x1="{mx}" x2="{mx}" y1="{y+12}" y2="{y+22}" stroke="{t["border"]}" stroke-width="2"/>'
               f'<line x1="{mx-10}" x2="{mx+10}" y1="{y+22}" y2="{y+22}" stroke="{t["border"]}" stroke-width="2"/>')
    # receipt icon
    rx = xs[2]
    out.append(f'<path d="M{rx-15},{y-24} h30 v46 l-5,-4 l-5,4 l-5,-4 l-5,4 l-5,-4 l-5,4 z" fill="{t["card"]}" stroke="{t["border"]}"/>'
               f'<line x1="{rx-9}" x2="{rx+9}" y1="{y-14}" y2="{y-14}" stroke="{t["idle"]}" stroke-width="2"/>'
               f'<line x1="{rx-9}" x2="{rx+5}" y1="{y-7}" y2="{y-7}" stroke="{t["idle"]}" stroke-width="2"/>'
               f'<line x1="{rx-9}" x2="{rx+9}" y1="{y+2}" y2="{y+2}" stroke="{t["success"]}" stroke-width="2.5">'
               f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;.82;.88;.97;1" dur="3s" repeatCount="indefinite"/></line>')
    out.append(f'<circle r="4" fill="{t["primary"]}"><animateMotion dur="3s" repeatCount="indefinite" path="{path}" '
               f'keyPoints="0;.5;.5;1;1" keyTimes="0;.42;.6;.85;1" calcMode="linear"/></circle>')
    out.append(f'<text class="mono" x="14" y="112" font-size="10" fill="{t["muted"]}">exposure</text>')
    out.append(f'<text class="mono" x="{w-14}" y="112" text-anchor="end" font-size="10" fill="{t["link"]}">+uplift</text>')
    return "".join(out)


def stage_sync(t, w):
    out = []
    # presenter phone
    px, py = 30, 14
    out.append(f'<rect x="{px}" y="{py}" width="50" height="92" rx="8" fill="{t["card"]}" stroke="{t["primary"]}" stroke-width="1.5"/>')
    slides = 4
    dur = 8
    # presenter slide counter
    for s in range(slides):
        a, b = s / slides, (s + 1) / slides
        out.append(f'<g opacity="0"><animate attributeName="opacity" values="{window(a, b)[0]}" keyTimes="{window(a, b)[1]}" '
                   f'dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/>'
                   f'<rect x="{px+7}" y="{py+12}" width="36" height="{14+s*8}" rx="2" fill="{t["primary"]}" opacity=".85"/>'
                   f'<text class="mono" x="{px+25}" y="{py+82}" text-anchor="middle" font-size="9" fill="{t["muted"]}">{s+1}/{slides}</text></g>')
    # waves
    for k in range(2):
        out.append(f'<circle cx="{px+50}" cy="{py+46}" r="6" fill="none" stroke="{t["primary"]}" stroke-width="1.2" opacity="0">'
                   f'<animate attributeName="r" values="6;48" dur="2s" begin="{k}s" repeatCount="indefinite"/>'
                   f'<animate attributeName="opacity" values=".6;0" dur="2s" begin="{k}s" repeatCount="indefinite"/></circle>')
    # audience phones
    for j in range(3):
        ax, ay = 118 + j * 34, 28 + (j % 2) * 10
        out.append(f'<rect x="{ax}" y="{ay}" width="26" height="48" rx="5" fill="{t["card"]}" stroke="{t["border"]}"/>')
        lag = 0.15 + j * 0.07
        for s in range(slides):
            a, b = s / slides, (s + 1) / slides
            out.append(f'<rect x="{ax+4}" y="{ay+6}" width="18" height="{7+s*4}" rx="1.5" fill="{t["primary"]}" opacity="0">'
                       f'<animate attributeName="opacity" values="{window(a, b)[0]}" keyTimes="{window(a, b)[1]}" begin="{lag:.2f}s" '
                       f'dur="{dur}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
        out.append(f'<circle cx="{ax+13}" cy="{ay+42}" r="2" fill="{t["success"]}"/>')
    out.append(f'<text class="mono" x="{w-14}" y="108" text-anchor="end" font-size="10" fill="{t["link"]}">&lt;80ms</text>')
    return "".join(out)


def stage_fintech(t, w):
    out = []
    rows = [("INV-2041", "+1,240.00"), ("PAYOUT", "-380.50"), ("INV-2042", "+2,915.00"), ("FEE", "-12.90"),
            ("INV-2043", "+760.00"), ("REFUND", "-95.00")]
    out.append('<g clip-path="url(#led)"><g class="ledger">')
    for rep in range(2):
        for k, (ref, amt) in enumerate(rows):
            yy = 22 + (rep * len(rows) + k) * 20
            col = t["success"] if amt.startswith("+") else t["secondary"]
            out.append(f'<circle cx="16" cy="{yy-4}" r="2.5" fill="{t["success"]}"/>'
                       f'<text class="mono" x="26" y="{yy}" font-size="10" fill="{t["muted"]}">{ref}</text>'
                       f'<text class="mono" x="{w/2+20}" y="{yy}" text-anchor="end" font-size="10" fill="{col}">{amt}</text>')
    out.append('</g></g>')
    # sparkline on the right
    sx = w / 2 + 34
    pts = [(0, 80), (14, 72), (28, 76), (42, 58), (56, 62), (70, 44), (84, 40)]
    d = "M" + " L".join(f"{sx+x},{y}" for x, y in pts)
    out.append(f'<line x1="{sx-6}" x2="{sx-6}" y1="10" y2="104" stroke="{t["border"]}"/>')
    out.append(f'<path class="spark" d="{d}" fill="none" stroke="{t["primary"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
    out.append(f'<text class="mono" x="{w-10}" y="104" text-anchor="end" font-size="10" fill="{t["link"]}">Δ 0.00</text>')
    return "".join(out)


def window(a, b):
    """values/keyTimes that show an element only during [a, b) of a discrete cycle."""
    if a <= 0:
        return "1;0", f"0;{b:.3f}"
    return "0;1;0", f"0;{a:.3f};{b:.3f}"


STAGES = [stage_adtech, stage_retail, stage_sync, stage_fintech]


# ---------------------------------------------------------------- terminal
def terminal(t):
    W = 1200
    fs = 15
    adv = fs * MONO_ADV
    lh = 26
    lines = [
        ("$", "whoami"),
        (">", "founder & md @ one tech group — retail media · adtech · mobile apps · fintech"),
        ("$", "cat ./workflow"),
        (">", "claude orchestrates · codex builds · humans decide · ship daily"),
        ("$", "ls ./building"),
        (">", "ad-exchange/   retail-media-os/   mobile-apps/   billing-rails/"),
        ("$", "echo $MOTTO"),
        (">", "probe reality before you trust your model."),
    ]
    H = 70 + lh * len(lines) + 36
    css = [font_css(geist=False, mono_bold=True), BASE_CSS]
    t0 = 0.4
    g = [f'<clipPath id="win"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>',
         f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>'
         f'<rect width="{W}" height="40" fill="{t["section"]}"/></g>',
         f'<path d="M0,40.5 H{W}" stroke="{t["border"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>']
    for k, c in enumerate([t["idle"], t["idle"], t["idle"]]):
        g.append(f'<circle cx="{24+k*18}" cy="20.5" r="5.5" fill="{c}"/>')
    g.append(f'<text class="mono" x="{W/2}" y="25" text-anchor="middle" font-size="12" fill="{t["muted"]}">lucas@otg — ~/</text>')
    g.append('<defs>')
    clips = []
    for i, (p, txt) in enumerate(lines):
        y = 76 + i * lh
        x = 32 + 2 * adv
        width = len(txt) * adv + 16
        steps = len(txt)
        dur = 0.045 * steps if p == "$" else 0.35
        timing = f"steps({steps},end)" if p == "$" else "ease-out"
        css.append(f"@keyframes p{i}{{to{{opacity:1}}}}.p{i}{{opacity:0;animation:p{i} .01s {t0:.2f}s forwards}}")
        if p == "$":
            vals = ";".join(f"{min(k * adv, width):.1f}" for k in range(steps + 1)) + f";{width:.1f}"
            anim = (f'<animate attributeName="width" values="{vals}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="discrete" fill="freeze"/>')
        else:
            anim = (f'<animate attributeName="width" values="0;{width:.1f}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1" fill="freeze"/>')
        clips.append(f'<clipPath id="cl{i}"><rect x="{x}" y="{y-fs-2}" width="0" height="{lh}">{anim}</rect></clipPath>')
        t0 += dur + (0.25 if p == "$" else 0.55)
    g += clips
    g.append('</defs>')
    for i, (p, txt) in enumerate(lines):
        y = 76 + i * lh
        pc = t["success"] if p == "$" else t["muted"]
        tc = t["text"] if p == "$" else (t["link"] if i == len(lines) - 1 else t["secondary"])
        fw = ' font-weight="700"' if p == "$" else ""
        g.append(f'<text class="mono pfx p{i}" x="32" y="{y}" font-size="{fs}" fill="{pc}">{p}</text>')
        g.append(f'<text class="mono" clip-path="url(#cl{i})" x="{32+2*adv}" y="{y}" font-size="{fs}"{fw} '
                 f'fill="{tc}" xml:space="preserve">{esc(txt)}</text>')
    y = 76 + len(lines) * lh
    css.append(f"@keyframes bl{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
               f"@keyframes on{{to{{visibility:visible}}}}"
               f".cur{{visibility:hidden;animation:on .01s {t0:.2f}s forwards, bl 1s steps(1) {t0:.2f}s infinite}}")
    g.append(f'<text class="mono" x="32" y="{y}" font-size="{fs}" fill="{t["success"]}">$</text>')
    g.append(f'<rect class="cur" x="{32+2*adv}" y="{y-fs+2}" width="{adv:.1f}" height="{fs+2}" fill="{t["link"]}"/>')
    return svg(W, H, "Terminal: whoami, workflow, what I am building, motto", "".join(css), "".join(g))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    OUT.mkdir(exist_ok=True)
    for name, fn in [("header", header), ("focus", focus), ("terminal", terminal)]:
        for mode, t in THEMES.items():
            p = OUT / f"{name}-{mode}.svg"
            p.write_text(fn(t), encoding="utf-8")
            print(f"{p.relative_to(ROOT)}  {p.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
