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
    words = ["retail media rails.", "AdTech.", "mobile apps.", "fintech flows."]
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
    g.append(f'<text x="{cx}" y="{cy+58}" text-anchor="middle" class="mono" font-size="10" letter-spacing="1.5" fill="{t["muted"]}">ADTECH</text>')
    # live bid ticker under the exchange
    bids = ["bid 2.41 EUR", "bid 3.08 EUR", "bid 1.97 EUR", "bid 2.76 EUR"]
    tick = []
    for i, b in enumerate(bids):
        tick.append(f'<text class="mono w{i}" style="transform-box:fill-box" x="{cx}" y="{cy+80}" text-anchor="middle" '
                    f'font-size="11" fill="{t["link"]}">{b}</text>')
    g += tick

    # left text block
    x0 = 64
    g.append(f'<text class="mono in d1" x="{x0}" y="118" font-size="13" letter-spacing="2.2" fill="{t["link"]}">'
             f'FOUNDER &amp; MD · ONE TECH GROUP</text>')
    g.append(f'<text class="sans in d2" x="{x0-3}" y="186" font-size="66" font-weight="640" letter-spacing="-2.2" '
             f'fill="{t["text"]}">Lucas Lingens</text>')
    g.append(f'<g class="in d3"><text class="sans" x="{x0}" y="238" font-size="26" fill="{t["secondary"]}">I build</text>')
    for i, w in enumerate(words):
        g.append(f'<text class="mono w{i}" style="transform-box:fill-box" x="{x0+98}" y="238" font-size="25" '
                 f'font-weight="700" fill="{t["link"]}">{w}</text>')
    g.append('</g>')
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


# ---------------------------------------------------------------- open source
OSS = [
    dict(repo="onetechgroupll/eigen-beam", name="eigen.beam", license="MIT",
         l1="Mobile live-sync presentations: the presenter steers,",
         l2="the audience follows on their own phones, in lockstep.",
         tags=["SVELTEKIT", "SSE", "MCP", "BUN", "RAILWAY"]),
]


def oss_card(t, p):
    W, H = 1200, 196
    sw = 282 - 44  # same stage width as the focus cards
    style = font_css() + BASE_CSS + """
@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:.25}}
.live{animation:blink 1.6s steps(1) infinite}
"""
    g = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>',
         f'<rect x="22" y="38" width="{sw}" height="120" rx="8" fill="{t["section"]}"/>',
         f'<g transform="translate(22,38)">{stage_sync(t, sw)}</g>']
    x = 22 + sw + 36
    g.append(f'<text class="mono" x="{x}" y="50" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">OPEN SOURCE · {p["license"]}</text>')
    g.append(f'<circle class="live" cx="{W-30}" cy="32" r="2.5" fill="{t["success"]}"/>')
    g.append(f'<text class="sans" x="{x}" y="88" font-size="26" font-weight="620" letter-spacing="-.5" fill="{t["text"]}">{p["name"]}</text>')
    g.append(f'<text class="sans" x="{x}" y="116" font-size="14" fill="{t["secondary"]}">{p["l1"]}</text>')
    g.append(f'<text class="sans" x="{x}" y="136" font-size="14" fill="{t["secondary"]}">{p["l2"]}</text>')
    tx = x
    for tag in p["tags"]:
        w = len(tag) * 10 * MONO_ADV + 16
        g.append(f'<rect x="{tx:.0f}" y="152" width="{w:.0f}" height="20" rx="4" fill="{t["primary_light"]}"/>')
        g.append(f'<text class="mono" x="{tx+8:.0f}" y="166" font-size="10" fill="{t["link"]}">{tag}</text>')
        tx += w + 6
    g.append(f'<text class="mono" x="{W-28}" y="166" text-anchor="end" font-size="12" fill="{t["link"]}">github.com/{p["repo"]} →</text>')
    alt = f'Open source ({p["license"]}): {p["name"]}. {p["l1"]} {p["l2"]}'
    return svg(W, H, alt, style, "".join(g))


# ---------------------------------------------------------------- terminal
BOLD = ' font-weight="700"'


def terminal(t):
    """Typed terminal session: whoami, lucas --help, top (live bars), principles."""
    W = 1200
    fs = 15
    adv = fs * MONO_ADV
    lh = 24
    X = 32
    TX = X + 2 * adv
    txt, sec, mut, link, ok = t["text"], t["secondary"], t["muted"], t["link"], t["success"]
    # rows: (kind, segments | text, extra)  kind: cmd | out | gap | top
    flags = [("--business", "finance, controlling, planning"),
             ("--product ", "from problem to shipped product"),
             ("--build   ", "writes and ships own software"),
             ("--lead    ", "leads teams and developers"),
             ("--deals   ", "investments, holdings, M&A")]
    procs = [("101", "deals.invest", [.62, .78, .55, .7, .62]),
             ("102", "product.ship", [.84, .66, .9, .74, .84]),
             ("103", "team.lead", [.58, .72, .64, .8, .58]),
             ("104", "cashflow.plan", [.46, .6, .52, .44, .46]),
             ("105", "code.review", [.7, .52, .76, .6, .7])]
    rows = [("cmd", "whoami"),
            ("out", [("mainly founder & md @ one tech group", sec), (" · building companies since 2008", mut)]),
            ("gap",),
            ("cmd", "lucas --help"),
            ("out", [("usage: lucas ", sec), ("[--business] [--product] [--build] [--lead] [--deals]", mut)])]
    rows += [("out", [("  " + f, link, True), ("  " + d, sec)]) for f, d in flags]
    rows += [("gap",), ("cmd", "top -o impact"),
             ("out", [("  PID  PROCESS          STATE   LOAD", mut)])]
    rows += [("top", p) for p in procs]
    rows += [("gap",), ("cmd", "cat ./principles"),
             ("out", [("01  ", mut), ("probe reality before you trust your model", link, True)]),
             ("out", [("02  ", mut), ("read the source of truth, don't reconstruct", sec)]),
             ("out", [("03  ", mut), ("root cause over shortcut", sec)]),
             ("out", [("04  ", mut), ("done = works in production", sec)]),
             ("gap",)]
    y = 76
    layout = []
    for r in rows:
        if r[0] == "gap":
            y += 10
            continue
        layout.append((r, y))
        y += lh
    H = y + lh + 18
    css = [font_css(geist=False, mono_bold=True), BASE_CSS,
           "@keyframes ping{0%,100%{opacity:1}50%{opacity:.3}}.run{animation:ping 1.4s ease-in-out infinite}"]
    g = [f'<clipPath id="win"><rect x="0" y="0" width="{W}" height="{H}" rx="12"/></clipPath>',
         f'<g clip-path="url(#win)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>'
         f'<rect width="{W}" height="40" fill="{t["section"]}"/></g>',
         f'<path d="M0,40.5 H{W}" stroke="{t["border"]}"/>',
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>']
    for k in range(3):
        g.append(f'<circle cx="{24+k*18}" cy="20.5" r="5.5" fill="{t["idle"]}"/>')
    g.append(f'<text class="mono" x="{W/2}" y="25" text-anchor="middle" font-size="12" fill="{mut}">lucas@otg — ~/ — zsh</text>')
    defs, body = ['<defs>'], []
    t0 = 0.4
    for i, (r, y) in enumerate(layout):
        kind = r[0]
        if kind == "cmd":
            text = r[1]
            width = len(text) * adv + 16
            dur = 0.05 * len(text)
            vals = ";".join(f"{min(k * adv, width):.1f}" for k in range(len(text) + 1)) + f";{width:.1f}"
            anim = (f'<animate attributeName="width" values="{vals}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="discrete" fill="freeze"/>')
            css.append(f"@keyframes p{i}{{to{{opacity:1}}}}.p{i}{{opacity:0;animation:p{i} .01s {t0:.2f}s forwards}}")
            body.append(f'<text class="mono pfx p{i}" x="{X}" y="{y}" font-size="{fs}" fill="{ok}">$</text>')
            body.append(f'<text class="mono" clip-path="url(#cl{i})" x="{TX}" y="{y}" font-size="{fs}" font-weight="700" '
                        f'fill="{txt}" xml:space="preserve">{esc(text)}</text>')
            t0 += dur + 0.3
        else:
            width = W - TX - 24
            dur = 0.22
            anim = (f'<animate attributeName="width" values="0;{width:.1f}" begin="{t0:.2f}s" dur="{dur:.2f}s" '
                    f'calcMode="spline" keySplines=".2 .7 .3 1" keyTimes="0;1" fill="freeze"/>')
            if kind == "out":
                spans = "".join(f'<tspan fill="{c[1]}"{BOLD if len(c) > 2 else ""}>{esc(c[0])}</tspan>'
                                for c in r[1])
                body.append(f'<text class="mono" clip-path="url(#cl{i})" x="{TX}" y="{y}" font-size="{fs}" '
                            f'xml:space="preserve">{spans}</text>')
            else:  # top row with a live load bar
                pid, name, loads = r[1]
                bx, bw = TX + 32 * adv, 260  # LOAD column = char 32 of the header
                vals = ";".join(f"{v * bw:.1f}" for v in loads)
                dur_bar = 4 + int(pid) % 3
                body.append(f'<g clip-path="url(#cl{i})">'
                            f'<text class="mono" x="{TX}" y="{y}" font-size="{fs}" xml:space="preserve">'
                            f'<tspan fill="{mut}">  {pid}  </tspan><tspan fill="{txt}">{name:<17}</tspan></text>'
                            f'<circle class="run" style="animation-delay:{int(pid) % 5 * .2:.1f}s" cx="{TX + 24.5 * adv:.1f}" cy="{y-5}" r="3.2" fill="{ok}"/>'
                            f'<text class="mono" x="{TX + 25.6 * adv:.1f}" y="{y}" font-size="{fs}" fill="{sec}">R</text>'
                            f'<rect x="{bx:.1f}" y="{y-11}" width="{bw}" height="10" rx="3" fill="{t["section"]}"/>'
                            f'<rect x="{bx:.1f}" y="{y-11}" width="{loads[0]*bw:.1f}" height="10" rx="3" fill="{t["primary"]}">'
                            f'<animate attributeName="width" values="{vals}" dur="{dur_bar}s" repeatCount="indefinite" '
                            f'calcMode="spline" keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1;.4 0 .2 1"/></rect></g>')
            t0 += dur + 0.06
        defs.append(f'<clipPath id="cl{i}"><rect x="{TX - 2 if kind == "cmd" else TX - 4}" y="{y-fs-2}" width="0" height="{lh}">{anim}</rect></clipPath>')
    defs.append('</defs>')
    y = layout[-1][1] + lh + 10
    css.append(f"@keyframes bl{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}"
               f"@keyframes on{{to{{visibility:visible}}}}"
               f".cur{{visibility:hidden;animation:on .01s {t0:.2f}s forwards, bl 1s steps(1) {t0:.2f}s infinite}}")
    body.append(f'<text class="mono" x="{X}" y="{y}" font-size="{fs}" fill="{ok}">$</text>')
    body.append(f'<rect class="cur" x="{TX}" y="{y-fs+2}" width="{adv:.1f}" height="{fs+2}" fill="{link}"/>')
    title = ("Terminal. whoami: mainly founder and MD at One Tech Group, building companies since 2008. "
             "Roles: business (finance, controlling, planning), product, build (writes and ships own software), "
             "lead (teams and developers), deals (investments, holdings, M&amp;A). "
             "Principles: probe reality before you trust your model; read the source of truth; "
             "root cause over shortcut; done means works in production.")
    return svg(W, H, title, "".join(css), "".join(g + defs + body))


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------- skyline
LIGHT_ON = {"light": "#e0a106", "dark": "#fbbf24"}   # warm window / clock light
CLOCK_SEP = {"light": "#dc2626", "dark": "#f87171"}  # Lichtzeitpegel separators
LINE = {"light": "#bdb6ab", "dark": "#55514c"}


def skyline(t, mode, crop=None, label=True, phase="day", weather="clear", temp=None, season=None,
            pod=None, lit_by=None):
    """Duesseldorf skyline as flat line illustration.

    crop=(x, y, w, h) renders a viewBox crop (used for the square avatar).
    phase: day | dusk | night   weather: clear | partly | cloudy | fog | rain | snow | storm
    Everything that emits light goes into L and is drawn above the night overlay.
    """
    W, H = 1200, 400
    G = 300  # promenade / waterline
    on = LIGHT_ON[mode]
    st = LINE[mode]  # line-art stroke: stronger than --ds-border, still warm-neutral
    css = font_css(geist=False, mono_bold=True) + BASE_CSS + f"""
@keyframes waves{{from{{transform:translateX(0)}}to{{transform:translateX(-48px)}}}}
.wave{{animation:waves 4s linear infinite}}.wave2{{animation-duration:6s}}
@keyframes glow{{0%,100%{{opacity:.35}}50%{{opacity:.8}}}}
.glow{{animation:glow 3s ease-in-out infinite}}
@keyframes flick{{0%,92%,100%{{opacity:1}}94%{{opacity:.35}}96%{{opacity:1}}97%{{opacity:.5}}}}
.sign{{animation:flick 7s steps(1) infinite}}
@keyframes win{{0%,100%{{opacity:0}}40%,70%{{opacity:1}}}}
.win{{opacity:0;animation:win 9s ease-in-out infinite}}
@keyframes beacon{{0%,60%,100%{{opacity:.15}}70%,85%{{opacity:1}}}}
.beacon{{animation:beacon 2s steps(1) infinite}}
"""
    night, dusk = phase == "night", phase == "dusk"
    css += SKY_CSS
    g, L = [], []
    vb = crop or (0, 0, W, H)
    g.append(f'<defs><clipPath id="frame"><rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" rx="{0 if crop else 12}"/></clipPath></defs>')
    g.append('<g clip-path="url(#frame)">')
    g.append(f'<rect width="{W}" height="{H}" fill="{t["page"]}"/>')
    g += sky_layers(t, mode, phase, weather, G)

    def bldg(pts, fill=None, stroke=st, extra=""):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts) + " Z"
        return f'<path d="{d}" fill="{fill or t["card"]}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round"{extra}/>'

    def windows(x0, y0, cols, rows, dx, dy, w=4, h=3, seed=0):
        out = []
        for r in range(rows):
            for c in range(cols):
                x, y = x0 + c * dx, y0 + r * dy
                out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{t["border"]}"/>')
                k = (r * 7 + c * 13 + seed) % 23
                if k in ((0, 5, 9, 14, 18) if night else (0, 9, 14) if dusk else (0, 5)):
                    cls = "" if night and k in (9, 14) else "win"
                    L.append(f'<rect class="{cls}" style="animation-delay:{(k + r + c) % 9}s" x="{x}" y="{y}" '
                             f'width="{w}" height="{h}" fill="{on}"/>')
        return "".join(out)

    # birds (back)
    for i, (y, dur, beg) in enumerate([(70, 38, 0), (95, 46, 12), (58, 52, 25)]):
        g.append(f'<path d="M-6,-3 Q-3,-6 0,0 Q3,-6 6,-3" fill="none" stroke="{t["muted"]}" stroke-width="1.4" '
                 f'stroke-linecap="round"><animateMotion dur="{dur}s" begin="{-beg}s" repeatCount="indefinite" '
                 f'path="M-20,{y} C300,{y-20} 800,{y+20} 1220,{y-10}"/></path>')

    # haze skyline (back layer)
    haze = [(0, 240), (40, 225), (95, 250), (330, 230), (380, 245), (600, 236), (660, 250),
            (720, 228), (780, 244), (990, 232), (1040, 248), (1100, 226), (1150, 242)]
    for i, (x, y) in enumerate(haze):
        g.append(f'<rect x="{x}" y="{y}" width="{48 + (i % 3) * 10}" height="{G - y}" fill="{t["border_light"]}"/>')

    # 1. office tower with chimneys (left)
    g.append(f'<rect x="62" y="70" width="7" height="60" fill="{t["card"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(f'<rect x="80" y="70" width="7" height="60" fill="{t["card"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(bldg([(48, G), (48, 128), (130, 128), (130, G)]))
    g.append(windows(56, 138, 9, 16, 8, 9.5, seed=1))
    # 2. domed block
    g.append(f'<path d="M140,{G} V188 A28,28 0 0 1 196,188 V{G} Z" fill="{t["section"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(windows(148, 196, 5, 10, 9, 9.5, seed=4))

    # 3. Gehry buildings, Neuer Zollhof (wavy)
    gehry = [(210, 262, 175, t["card"]), (266, 312, 150, t["primary_subtle"]), (316, 352, 190, t["section"])]
    for x0, x1, top, fill in gehry:
        mid = (x0 + x1) / 2
        d = (f"M{x0},{G} C{x0-6},{top+60} {x0+8},{top+20} {x0+4},{top} "
             f"Q{mid},{top-10} {x1-2},{top+4} C{x1+6},{top+40} {x1-8},{top+90} {x1},{G} Z")
        g.append(f'<path d="{d}" fill="{fill}" stroke="{st}" stroke-width="1.5"/>')
        g.append(windows(int(x0 + 10), top + 16, int((x1 - x0 - 16) / 9), int((G - top - 24) / 12), 9, 12, w=3, h=5, seed=x0))

    # 4. Stadttor (rhomboid glass tower) with LL rooftop sign
    sx0, sx1, sxt0, sxt1, stop = 372, 420, 392, 440, 150
    g.append(bldg([(sx0, G), (sx1, G), (sxt1, stop), (sxt0, stop)], fill=t["primary_light"], stroke=t["primary"]))
    for k in range(1, 8):
        y = stop + k * (G - stop) / 8
        f = (y - stop) / (G - stop)
        xa, xb = sxt0 + (sx0 - sxt0) * f, sxt1 + (sx1 - sxt1) * f
        g.append(f'<line x1="{xa:.1f}" y1="{y:.1f}" x2="{xb:.1f}" y2="{y:.1f}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>')
    g.append(f'<line x1="{sxt0}" y1="{stop}" x2="{sx1}" y2="{G}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>')
    g.append(f'<line x1="{sxt1}" y1="{stop}" x2="{sx0}" y2="{G}" stroke="{t["primary"]}" stroke-width=".8" opacity=".45"/>')
    # sign: frame on two legs, glowing LL
    bx, by = sxt0 + 4, stop - 30
    g.append(f'<line x1="{bx+8}" y1="{stop}" x2="{bx+8}" y2="{by+22}" stroke="{st}" stroke-width="1.5"/>')
    g.append(f'<line x1="{bx+32}" y1="{stop}" x2="{bx+32}" y2="{by+22}" stroke="{st}" stroke-width="1.5"/>')
    L.append(f'<rect class="glow" x="{bx-4}" y="{by-4}" width="48" height="30" rx="6" fill="{t["primary"]}" opacity=".35"/>')
    L.append(f'<rect x="{bx}" y="{by}" width="40" height="22" rx="4" fill="{t["primary"]}"/>')
    L.append(f'<text class="mono sign" x="{bx+20}" y="{by+16.5}" text-anchor="middle" font-size="16" '
             f'font-weight="700" letter-spacing="1" fill="#ffffff">LL</text>')

    # 5. Rheinturm with Lichtzeitpegel
    rx = 490
    g.append(bldg([(rx - 13, G), (rx + 13, G), (rx + 6, 92), (rx - 6, 92)]))
    pod_fill = pod or t["primary"]
    if night or dusk:
        L.append(f'<rect class="glow" x="{rx-30}" y="73" width="60" height="24" rx="10" fill="{pod_fill}" opacity=".35"/>')
    g.append(f'<rect x="{rx-24}" y="78" width="48" height="14" rx="6" fill="{pod_fill}"/>')
    if lit_by and label:
        g.append(f'<path d="M{rx+26},85 H{rx+40}" stroke="{t["muted"]}" stroke-width=".8"/>'
                 f'<text class="mono" x="{rx+44}" y="88.5" font-size="9.5" fill="{t["muted"]}">lit by @{esc(lit_by)}</text>')
    g.append(f'<rect x="{rx-20}" y="81.5" width="40" height="4" rx="2" fill="{t["primary_light"]}" opacity=".9"/>')
    g.append(f'<rect x="{rx-18}" y="68" width="36" height="10" rx="4" fill="{t["card"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(f'<rect x="{rx-11}" y="61" width="22" height="7" rx="3" fill="{t["card"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(f'<line x1="{rx}" y1="61" x2="{rx}" y2="18" stroke="{st}" stroke-width="2"/>')
    g.append(f'<line x1="{rx}" y1="38" x2="{rx}" y2="18" stroke="{t["muted"]}" stroke-width="1"/>')
    L.append(f'<circle class="beacon" cx="{rx}" cy="16" r="2.6" fill="{CLOCK_SEP[mode]}"/>')
    # clock: hours tens(2) hours(9) | min tens(5) min(9) | sec tens(5) sec(9); seconds at the bottom
    groups = [("h10", 2, None), ("h1", 9, None), ("m10", 5, 3600), ("m1", 9, 600), ("s10", 5, 60), ("s1", 9, 10)]
    y = 104
    step = 4.1
    for gi, (_, n, period) in enumerate(groups):
        if gi:
            L.append(f'<rect x="{rx-1.6}" y="{y-1}" width="3.2" height="2" fill="{CLOCK_SEP[mode]}"/>')
            y += step
        # lamp k (1-based from the bottom of the group) is lit once the digit >= k
        for k in range(n, 0, -1):
            g.append(f'<circle cx="{rx}" cy="{y:.1f}" r="1.25" fill="{t["idle"]}"/>')
            if period:
                frac = k / (n + 1)
                L.append(f'<circle cx="{rx}" cy="{y:.1f}" r="1.25" fill="{on}" opacity="0">'
                         f'<animate attributeName="opacity" values="0;1" keyTimes="0;{frac:.4f}" dur="{period}s" '
                         f'calcMode="discrete" repeatCount="indefinite"/></circle>')
            y += step
    if label:
        g.append(f'<path d="M{rx+8},180 H{rx+26}" stroke="{t["muted"]}" stroke-width=".8"/>')
        g.append(f'<text class="mono" x="{rx+30}" y="183.5" font-size="9.5" fill="{t["muted"]}">lichtzeitpegel</text>')

    # 6. Altstadt: Schlossturm, St. Lambertus, gabled houses
    houses = [(530, 248), (556, 240), (622, 252), (648, 238), (676, 246), (704, 242), (732, 252)]
    for i, (x, top) in enumerate(houses):
        w = 26
        g.append(bldg([(x, G), (x, top + 12), (x + w / 2, top), (x + w, top + 12), (x + w, G)],
                      fill=t["card"] if i % 2 else t["section"]))
        g.append(windows(x + 5, top + 18, 2, max(1, (G - top - 24) // 11), 11, 11, w=5, h=5, seed=i * 3))
    # Schlossturm
    g.append(bldg([(584, G), (584, 214), (606, 214), (606, G)], fill=t["section"]))
    g.append(f'<path d="M581,216 Q595,192 609,216 Z" fill="{t["primary_subtle"]}" stroke="{st}" stroke-width="1.5"/>')
    g.append(f'<line x1="595" y1="200" x2="595" y2="186" stroke="{st}" stroke-width="1.5"/>')
    # St. Lambertus (twisted, slightly leaning spire)
    lx = 770
    g.append(bldg([(lx - 18, G), (lx - 18, 246), (lx + 30, 246), (lx + 30, G)], fill=t["section"]))
    g.append(bldg([(lx - 9, G), (lx - 9, 192), (lx + 9, 192), (lx + 9, G)]))
    g.append(bldg([(lx - 11, 192), (lx + 3, 126), (lx + 11, 192)], fill=t["primary_subtle"]))
    g.append(f'<path d="M{lx-7},180 L{lx+4},150 M{lx-3},188 L{lx+7},162" stroke="{st}" stroke-width=".9"/>')
    g.append(f'<circle cx="{lx}" cy="206" r="4" fill="none" stroke="{st}" stroke-width="1.2"/>')

    # 7. Rheinkniebruecke (cable-stayed, single pylon)
    px, deck = 960, 262
    g.append(f'<rect x="806" y="{deck}" width="394" height="5" fill="{t["section"]}" stroke="{st}" stroke-width="1.2"/>')
    for k in range(8):
        y0 = 92 + k * 12
        for side in (-1, 1):
            g.append(f'<line x1="{px}" y1="{y0}" x2="{px + side * (34 + k * 22)}" y2="{deck}" stroke="{st}" stroke-width="1"/>')
    g.append(bldg([(px - 5, G), (px + 5, G), (px + 3, 70), (px - 3, 70)]))
    for pier in (850, 1070, 1160):
        g.append(f'<rect x="{pier-3}" y="{deck+5}" width="6" height="{G-deck-5}" fill="{t["section"]}" stroke="{st}" stroke-width="1.2"/>')
    for i, (beg, rev) in enumerate([(0, False), (-3.5, True), (-7, False)]):
        path = f"M810,{deck-2} H1200" if not rev else f"M1200,{deck-2} H810"
        col = on if i != 1 else CLOCK_SEP[mode]
        L.append(f'<rect x="-4" y="-2" width="8" height="3.4" rx="1.5" fill="{col}"><animateMotion dur="9s" begin="{beg}s" '
                 f'repeatCount="indefinite" path="{path}"/></rect>')

    # promenade + trees
    g.append(f'<rect x="0" y="{G-3}" width="{W}" height="5" fill="{t["border"]}"/>')
    for i, x in enumerate(range(14, W, 23)):
        if 800 < x < 1200 and i % 2:
            continue
        r = 5 + (i % 3)
        g.append(f'<circle cx="{x}" cy="{G-3-r}" r="{r}" fill="{t["success"]}" opacity=".45"/>')

    # river
    g.append(f'<rect x="0" y="{G+2}" width="{W}" height="{H-G}" fill="{t["primary_light"]}"/>')
    g.append(f'<line x1="{rx}" y1="{G+8}" x2="{rx}" y2="{G+70}" stroke="{t["primary"]}" stroke-width="3" '
             f'stroke-dasharray="6 6" opacity=".18"/>')
    g.append(f'<line x1="{px}" y1="{G+8}" x2="{px}" y2="{G+60}" stroke="{t["primary"]}" stroke-width="2" '
             f'stroke-dasharray="5 7" opacity=".14"/>')
    for i, y in enumerate([G + 18, G + 38, G + 62, G + 84]):
        cls = "wave" if i % 2 == 0 else "wave wave2"
        g.append(f'<path class="{cls}" d="M0,{y} H{W+48}" stroke="{t["primary"]}" stroke-width="1.2" '
                 f'stroke-dasharray="{10+i*4} {26+i*6}" stroke-dashoffset="{i*13}" opacity=".28"/>')

    # boats
    def sailboat(c):
        return (f'<path d="M-14,0 H14 L9,7 H-9 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1.2"/>'
                f'<line x1="0" y1="0" x2="0" y2="-28" stroke="{st}" stroke-width="1.2"/>'
                f'<path d="M1.5,-27 L16,-3 H1.5 Z" fill="{c}"/><path d="M-1.5,-22 L-11,-3 H-1.5 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1"/>')
    g.append(f'<g>{sailboat(t["primary"])}<animateMotion dur="70s" begin="-20s" repeatCount="indefinite" '
             f'path="M-40,{G+30} H1240"/></g>')
    g.append(f'<g>{sailboat(t["accent"])}<animateMotion dur="95s" begin="-70s" repeatCount="indefinite" '
             f'path="M-40,{G+56} H1240"/></g>')
    ship = (f'<path d="M-46,0 H50 L42,10 H-40 Z" fill="{t["card"]}" stroke="{st}" stroke-width="1.3"/>'
            f'<rect x="-34" y="-9" width="62" height="9" rx="2" fill="{t["card"]}" stroke="{st}" stroke-width="1.2"/>'
            f'<rect x="-22" y="-16" width="30" height="7" rx="2" fill="{t["section"]}" stroke="{st}" stroke-width="1.2"/>'
            + "".join(f'<rect x="{-30 + k * 9}" y="-6" width="5" height="3" fill="{t["primary"]}" opacity=".7"/>' for k in range(7))
            + f'<text class="mono" x="-38" y="7.5" font-size="6.5" font-weight="700" fill="{t["link"]}">LL</text>')
    g.append(f'<g>{ship}<animateMotion dur="120s" begin="-35s" repeatCount="indefinite" path="M1260,{G+80} H-60"/></g>')

    # a small green crocodile, mostly submerged, swimming downstream (head to the right)
    cg, cd = t["success"], ("#15803d" if mode == "light" else "#166534")
    croc = (
        f'<path d="M-30,1 Q-40,-1 -50,2" stroke="{cg}" stroke-width="3" fill="none" stroke-linecap="round">'
        f'<animate attributeName="d" dur="1.6s" repeatCount="indefinite" '
        f'values="M-30,1 Q-40,-1 -50,2;M-30,1 Q-40,3 -50,0;M-30,1 Q-40,-1 -50,2"/></path>'
        f'<path d="M-32,1 Q-24,-6 -6,-6 Q6,-6 12,-3 L28,-3 Q32,-2.5 32,0.5 L32,1 Z" fill="{cg}" stroke="{cd}" stroke-width="1"/>'
        + "".join(f'<path d="M{x},-5.6 l2,-2.6 l2,2.6 Z" fill="{cd}"/>' for x in (-22, -16, -10, -4, 2))
        + f'<circle cx="15" cy="-5.5" r="3.2" fill="{cg}" stroke="{cd}" stroke-width="1"/>'
        f'<circle cx="15.4" cy="-6" r="1.8" fill="{t["card"]}"/><circle cx="16" cy="-6" r=".9" fill="#1f2937"/>'
        f'<circle cx="29" cy="-3.2" r="1" fill="{cd}"/>'
        f'<path d="M-36,4 H36" stroke="{t["primary"]}" stroke-width="1.2" stroke-dasharray="6 5" opacity=".45"/>'
        f'<path d="M34,2 l6,-2 M34,3 l6,2" stroke="{t["primary"]}" stroke-width="1" opacity=".45"/>'
    )
    g.append(f'<g><g><g transform="scale(1.7)">{croc}</g><animateTransform attributeName="transform" type="translate" dur="2.2s" '
             f'repeatCount="indefinite" values="0,0;0,1.5;0,0"/></g>'
             f'<animateMotion dur="85s" begin="-50s" repeatCount="indefinite" path="M-60,{G+44} H1260"/></g>')

    if night or dusk:
        g.append(f'<rect width="{W}" height="{H}" fill="{NIGHT[mode]}" opacity="{(0.5 if mode == "light" else 0.38) if night else 0.12}"/>')
    g += L
    g += season_fx(t, mode, season, G, W)
    g += weather_fx(t, mode, weather, G, W, H)

    if label:
        g.append(f'<text class="mono" x="32" y="44" font-size="13" font-weight="700" letter-spacing="2.4" fill="{"#a9bcf0" if night and mode == "light" else t["link"]}">DÜSSELDORF</text>')
        sub = "51.23° N · 6.77° E"
        if temp is not None:
            sub += f" · {temp:.0f} °C · {WEATHER_LABEL[weather]}"
        lab = t["muted"] if not night else ("#c9cfe0" if mode == "light" else t["muted"])
        g.append(f'<text class="mono" x="32" y="62" font-size="10.5" letter-spacing="1" fill="{lab}">{sub}</text>')
        if season:
            g.append(f'<text class="mono" x="32" y="80" font-size="10.5" font-weight="700" letter-spacing="1" '
                     f'fill="{"#f87171" if season in ("hoppeditz", "karneval") and (night or mode == "dark") else "#dc2626" if season in ("hoppeditz", "karneval") else lab}">{SEASON_LABEL[season]}</text>')

    g.append('</g>')
    if crop is None:
        g.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>')
    title = "Duesseldorf skyline: Rheinturm with Lichtzeitpegel clock, Stadttor with LL sign, Neuer Zollhof, Altstadt, Rheinkniebruecke, Rhine"
    out = svg(W, H, title, css, "".join(g))
    if crop:
        out = out.replace(f'width="{W}" height="{H}" viewBox="0 0 {W} {H}"',
                          f'width="{crop[2]}" height="{crop[3]}" viewBox="{crop[0]} {crop[1]} {crop[2]} {crop[3]}"', 1)
    return out


NIGHT = {"light": "#16203a", "dark": "#05070d"}
WEATHER_LABEL = {"clear": "clear", "partly": "partly cloudy", "cloudy": "cloudy", "fog": "fog",
                 "rain": "rain", "snow": "snow", "storm": "thunderstorm"}
SKY_CSS = """
@keyframes drift{from{transform:translateX(-260px)}to{transform:translateX(1460px)}}
.cloud{animation:drift linear infinite}
@keyframes twinkle{0%,100%{opacity:.25}50%{opacity:1}}
.star{animation:twinkle 3s ease-in-out infinite}
@keyframes fogmove{0%,100%{transform:translateX(-40px)}50%{transform:translateX(40px)}}
.fog{animation:fogmove 18s ease-in-out infinite}
@keyframes flash{0%,88%,92%,96%,100%{opacity:0}89%,94%{opacity:.55}}
.flash{opacity:0;animation:flash 9s steps(1) infinite}
"""


def sky_layers(t, mode, phase, weather, G):
    """Background: night/dusk sky, sun or moon, stars, clouds (all behind the buildings)."""
    W = 1200
    out = []
    night, dusk = phase == "night", phase == "dusk"
    if night:
        out.append(f'<rect width="{W}" height="{G}" fill="{NIGHT[mode]}" opacity="{0.92 if mode == "light" else 0.75}"/>')
    if dusk:
        out.append('<defs><linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#f97316" stop-opacity="0"/>'
                   f'<stop offset="1" stop-color="#f97316" stop-opacity="{0.3 if mode == "light" else 0.22}"/></linearGradient></defs>')
        out.append(f'<rect width="{W}" height="{G}" fill="url(#dusk)"/>')
    if weather in ("cloudy", "rain", "snow", "storm", "fog") and not night:
        out.append(f'<rect width="{W}" height="{G}" fill="{t["section"]}" opacity=".7"/>')
    open_sky = weather in ("clear", "partly")
    if night and open_sky:
        for i in range(42):
            x, y = (i * 263) % 1180 + 10, (i * 97) % 190 + 12
            out.append(f'<circle class="star" style="animation-delay:{i % 7 * .45:.2f}s" cx="{x}" cy="{y}" '
                       f'r="{1.1 if i % 3 else 1.6}" fill="#f4f1ea"/>')
        out.append('<circle cx="1090" cy="64" r="20" fill="#f4f1ea"/>'
                   f'<circle cx="1101" cy="57" r="18" fill="{NIGHT[mode]}"/>')
    elif open_sky and not night:
        sx, sy, r = (1080, 236, 34) if dusk else (1070, 74, 24)
        col = "#f97316" if dusk else ("#f5b301" if mode == "light" else "#fbbf24")
        out.append(f'<circle cx="{sx}" cy="{sy}" r="{r + 14}" fill="{col}" opacity=".18"/>'
                   f'<circle cx="{sx}" cy="{sy}" r="{r}" fill="{col}"/>')
    n = {"clear": 0, "partly": 3, "cloudy": 6, "fog": 3, "rain": 6, "snow": 6, "storm": 7}[weather]
    cfill = ("#3a4258" if mode == "light" else "#2a2a2e") if night else ("#ffffff" if mode == "light" else "#2c2b28")
    if weather in ("rain", "storm"):
        cfill = ("#d9d6d0" if mode == "light" else "#3a3835") if not night else cfill
    for i in range(n):
        y = 36 + (i * 41) % 130
        s = 0.8 + (i % 3) * 0.25
        dur = 140 + (i * 37) % 90
        out.append(f'<g class="cloud" style="animation-duration:{dur}s;animation-delay:-{(i * 53) % dur}s">'
                   f'<g transform="translate(0,{y}) scale({s})">'
                   f'<path d="M0,30 a18,18 0 0 1 16,-22 a26,26 0 0 1 46,-4 a20,20 0 0 1 34,12 a14,14 0 0 1 4,14 Z" '
                   f'fill="{cfill}" stroke="{LINE[mode]}" stroke-width="1.2" opacity=".95"/></g></g>')
    return out


def weather_fx(t, mode, weather, G, W, H):
    """Foreground precipitation, fog and lightning."""
    out = []
    if weather in ("rain", "storm"):
        out.append('<defs><pattern id="rain" width="34" height="46" patternUnits="userSpaceOnUse">'
                   f'<line x1="6" y1="0" x2="2" y2="12" stroke="{t["primary"]}" stroke-width="1.2" opacity=".45"/>'
                   f'<line x1="24" y1="22" x2="20" y2="34" stroke="{t["primary"]}" stroke-width="1.2" opacity=".35"/>'
                   '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="-12 46" '
                   'dur=".55s" repeatCount="indefinite"/></pattern></defs>')
        out.append(f'<rect width="{W}" height="{H}" fill="url(#rain)"/>')
    if weather == "snow":
        out.append('<defs><pattern id="snow" width="40" height="60" patternUnits="userSpaceOnUse">'
                   '<circle cx="8" cy="10" r="1.8" fill="#ffffff"/><circle cx="28" cy="38" r="1.4" fill="#ffffff"/>'
                   '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="10 60" '
                   'dur="5s" repeatCount="indefinite"/></pattern></defs>')
        out.append(f'<rect width="{W}" height="{H}" fill="url(#snow)" stroke="none"/>')
        out.append(f'<rect width="{W}" height="{H}" fill="url(#snow)" opacity=".6" transform="translate(17,23)"/>')
    if weather == "fog":
        for i, (y, h, o) in enumerate([(170, 60, .55), (225, 50, .65), (275, 40, .7)]):
            out.append(f'<rect class="fog" style="animation-delay:-{i * 5}s" x="-60" y="{y}" width="{W + 120}" '
                       f'height="{h}" rx="{h / 2}" fill="{t["page"]}" opacity="{o}"/>')
    if weather == "storm":
        out.append(f'<rect class="flash" width="{W}" height="{H}" fill="#ffffff"/>')
        out.append('<path class="flash" d="M820,40 L796,112 L816,112 L792,190 L846,96 L824,96 L846,40 Z" fill="#fde68a"/>')
    return out


# ---------------------------------------------------------------- seasons (Duesseldorf calendar)
SEASON_LABEL = {"hoppeditz": "11.11. Hoppeditz erwacht · Helau!", "karneval": "Helau!",
                "advent": "Advent", "christmas": "Frohe Weihnachten", "newyear": "Frohes neues Jahr!"}
CONFETTI = ["#dc2626", "#1d48c0", "#e0a106", "#16a34a", "#b6358f", "#529abd"]


def easter(y):
    """Anonymous Gregorian algorithm."""
    import datetime as dt
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g_ = (b - f + 1) // 3
    h = (19 * a + b - d - g_ + 15) % 30
    i, k = c // 4, c % 4
    l_ = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l_) // 451
    month = (h + l_ - 7 * m + 114) // 31
    day = (h + l_ - 7 * m + 114) % 31 + 1
    return dt.date(y, month, day)


def season_for(now):
    """now: datetime in Europe/Berlin -> season key or None."""
    import datetime as dt
    d = now.date()
    if (d.month == 12 and d.day == 31 and now.hour >= 18) or (d.month == 1 and d.day == 1 and now.hour < 2):
        return "newyear"
    if d.month == 11 and d.day == 11:
        return "hoppeditz"
    e = easter(d.year)
    if e - dt.timedelta(days=52) <= d <= e - dt.timedelta(days=47):  # Weiberfastnacht .. Veilchendienstag
        return "karneval"
    if d.month == 12 and 24 <= d.day <= 26:
        return "christmas"
    nov27 = dt.date(d.year, 11, 27)
    first_advent = nov27 + dt.timedelta(days=(6 - nov27.weekday()) % 7)
    if first_advent <= d <= dt.date(d.year, 12, 23):
        return "advent"
    return None


def _rope(W, y0=262, sag=10, span=150):
    pts = []
    for x0 in range(0, W, span):
        pts.append(f"M{x0},{y0} Q{x0 + span / 2},{y0 + 2 * sag} {x0 + span},{y0}")
    return " ".join(pts)


def _on_rope(x, y0=262, sag=10, span=150):
    u = (x % span) / span
    return y0 + 2 * sag * 2 * u * (1 - u)  # quadratic bezier with control at 2*sag -> peak sag


def season_fx(t, mode, season, G, W):
    if not season:
        return []
    line = LINE[mode]
    out = [f'<style>@keyframes bulb{{0%,100%{{opacity:.25}}50%{{opacity:1}}}}.bulb{{animation:bulb 1.6s ease-in-out infinite}}'
           '@keyframes burst{0%{transform:scale(.15);opacity:0}10%{opacity:1}70%{opacity:.9}100%{transform:scale(1);opacity:0}}'
           '.burst{transform-box:fill-box;transform-origin:center;animation:burst 2.6s ease-out infinite}</style>']
    if season in ("hoppeditz", "karneval"):
        out.append(f'<path d="{_rope(W)}" fill="none" stroke="{line}" stroke-width="1.2"/>')
        for k, x in enumerate(range(8, W, 22)):
            y = _on_rope(x)
            col = "#dc2626" if k % 2 == 0 else "#ffffff"
            out.append(f'<path d="M{x-6},{y:.1f} L{x+6},{y:.1f} L{x},{y+11:.1f} Z" fill="{col}" stroke="{line}" stroke-width=".6"/>')
        tiles = []
        for k in range(8):
            x, y = (k * 23) % 70 + 4, (k * 37) % 90 + 3
            tiles.append(f'<rect x="{x}" y="{y}" width="4" height="7" rx="1" fill="{CONFETTI[k % 6]}" '
                         f'transform="rotate({(k * 47) % 180} {x + 2} {y + 3})"/>')
        out.append('<defs><pattern id="confetti" width="80" height="100" patternUnits="userSpaceOnUse">' + "".join(tiles)
                   + '<animateTransform attributeName="patternTransform" type="translate" from="0 0" to="16 100" '
                     'dur="6s" repeatCount="indefinite"/></pattern></defs>')
        out.append(f'<rect width="{W}" height="{G}" fill="url(#confetti)" opacity=".7"/>')
        # "Helau!" bubble left of the LL sign, tail pointing at it
        bx, by, bw, bh = 318, 92, 66, 24
        out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="6" fill="{t["card"]}" stroke="#dc2626" stroke-width="1.5"/>'
                   f'<path d="M{bx+bw-14},{by+bh-.5} L{bx+bw+10},{by+bh+12} L{bx+bw-4},{by+bh-.5} Z" fill="{t["card"]}" stroke="#dc2626" stroke-width="1.5" stroke-linejoin="round"/>'
                   f'<rect x="{bx+bw-14.5}" y="{by+bh-3}" width="11" height="2.4" fill="{t["card"]}"/>')
        out.append(f'<text class="mono" x="{bx+bw/2}" y="{by+16.5}" text-anchor="middle" font-size="12" font-weight="700" fill="#dc2626">Helau!</text>')
    if season in ("advent", "christmas"):
        out.append(f'<path d="{_rope(W)}" fill="none" stroke="{line}" stroke-width="1"/>')
        warm = LIGHT_ON[mode]
        for k, x in enumerate(range(10, W, 18)):
            y = _on_rope(x) + 3
            col = warm if k % 3 else "#dc2626"
            out.append(f'<circle class="bulb" style="animation-delay:{(k % 5) * .32:.2f}s" cx="{x}" cy="{y:.1f}" r="2.6" fill="{col}"/>')
        # tree in front of the Altstadt
        tx, base = 700, G - 3
        for k, (w, h) in enumerate([(46, 26), (36, 24), (24, 22)]):
            y = base - 18 - k * 18
            out.append(f'<path d="M{tx - w / 2},{y} L{tx},{y - h} L{tx + w / 2},{y} Z" fill="#1f7a3e" stroke="{line}" stroke-width=".8"/>')
        out.append(f'<rect x="{tx-3}" y="{base-18}" width="6" height="18" fill="#7b400e"/>')
        for k, (dx, dy) in enumerate([(-12, -24), (8, -30), (-4, -44), (6, -58), (-8, -62), (2, -74)]):
            out.append(f'<circle class="bulb" style="animation-delay:{k * .27:.2f}s" cx="{tx + dx}" cy="{base + dy}" r="2" fill="{warm}"/>')
        out.append(f'<path d="M{tx},{base-90} l2.4,5 5.4,.6 -4,3.6 1.2,5.3 -5,-2.8 -5,2.8 1.2,-5.3 -4,-3.6 5.4,-.6 z" fill="{warm}"/>')
    if season == "newyear":
        for k, (cx, cy, r) in enumerate([(230, 92, 42), (640, 70, 52), (820, 118, 38), (1010, 64, 48), (300, 112, 30), (1120, 150, 30)]):
            col = CONFETTI[k % 6] if mode == "light" else ["#f87171", "#7e97e3", "#fbbf24", "#4ade80", "#d56db6", "#a4c9dc"][k % 6]
            rays = "".join(f'<line x1="{cx}" y1="{cy}" x2="{cx + r * __import__("math").cos(a / 14 * 6.2832):.1f}" '
                           f'y2="{cy + r * __import__("math").sin(a / 14 * 6.2832):.1f}" stroke="{col}" stroke-width="2" '
                           f'stroke-linecap="round" stroke-dasharray="3 5"/>' for a in range(14))
            out.append(f'<g class="burst" style="animation-delay:{k * .55:.2f}s">{rays}</g>')
    return out


AVATAR_CROP = (262, 14, 380, 380)  # centred on LL sign + Rheinturm for the circular avatar mask


# ---------------------------------------------------------------- stats
SERIES_1 = {"light": "#223e89", "dark": "#3f65cf"}  # --ds-chart-series-1


def calendar_stats(days):
    """days: [(iso_date, count)] sorted ascending -> dict of derived numbers."""
    import datetime as dt
    total = sum(c for _, c in days)
    longest = cur = 0
    for _, c in days:
        cur = cur + 1 if c > 0 else 0
        longest = max(longest, cur)
    i = len(days) - 1
    if days and days[-1][1] == 0:  # today not started yet
        i -= 1
    current = 0
    while i >= 0 and days[i][1] > 0:
        current += 1
        i -= 1
    wd = [0] * 7
    for d, c in days:
        wd[dt.date.fromisoformat(d).weekday()] += c
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months = {}
    for d, c in days:
        months[d[:7]] = months.get(d[:7], 0) + c
    keys = sorted(months)[-12:]
    return dict(total=total, longest=longest, current=current, weekday=names[wd.index(max(wd))],
                months=[(k, months[k]) for k in keys])


def stats(t, mode, st):
    W, H = 1200, 300
    css = font_css(mono_bold=False) + BASE_CSS + """
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@media (prefers-reduced-motion: no-preference){.bar{transform-box:fill-box;transform-origin:50% 100%;
animation:grow .9s cubic-bezier(.2,.7,.3,1) both}}
"""
    g = []
    tiles = [(f"{st['total']:,}", "contributions", "last 12 months"),
             (f"{st['longest']}", "days", "longest streak"),
             (f"{st['current']}", "days", "current streak"),
             (st["weekday"], "", "busiest weekday")]
    tw, th, gap = 280, 136, 20
    for i, (num, unit, lab) in enumerate(tiles):
        x, y = (i % 2) * (tw + gap) + .5, (i // 2) * (th + 26) + .5  # 2*136+26 = 298 < H
        g.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>')
        g.append(f'<text class="mono" x="{x+22}" y="{y+34}" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">{lab.upper()}</text>')
        fs = 42 if len(num) < 8 else 34
        g.append(f'<text class="sans" x="{x+20}" y="{y+96}" font-size="{fs}" font-weight="640" letter-spacing="-1.2" '
                 f'fill="{t["text"]}">{num}<tspan class="mono" dx="8" font-size="13" font-weight="400" letter-spacing="0" '
                 f'fill="{t["secondary"]}">{unit}</tspan></text>')
    # monthly bars (single series: no legend, title names it)
    cx, cw = 600.5, 599
    g.append(f'<rect x="{cx}" y=".5" width="{cw-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>')
    g.append(f'<text class="sans" x="{cx+24}" y="38" font-size="16" font-weight="600" fill="{t["text"]}">Contributions per month</text>')
    g.append(f'<text class="mono" x="{cx+24}" y="58" font-size="10.5" fill="{t["muted"]}">last 12 months · includes private repos</text>')
    months = st["months"]
    base, top = 250, 96
    mx = max(c for _, c in months) or 1
    n = len(months)
    slot = (cw - 48) / n
    bw = slot - 14
    for gi in range(3):
        y = base - (base - top) * gi / 2
        g.append(f'<line x1="{cx+24}" x2="{cx+cw-24}" y1="{y:.1f}" y2="{y:.1f}" stroke="{t["border_light"]}"/>')
    imax = max(range(n), key=lambda i: months[i][1])
    mn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for i, (k, c) in enumerate(months):
        h = max(2, (base - top) * c / mx)
        x = cx + 24 + i * slot + 7
        r = min(4, bw / 2, h / 2)
        d = (f"M{x:.1f},{base} V{base-h+r:.1f} Q{x:.1f},{base-h:.1f} {x+r:.1f},{base-h:.1f} "
             f"H{x+bw-r:.1f} Q{x+bw:.1f},{base-h:.1f} {x+bw:.1f},{base-h+r:.1f} V{base} Z")
        g.append(f'<path class="bar" style="animation-delay:{i*0.05:.2f}s" d="{d}" fill="{SERIES_1[mode]}"/>')
        g.append(f'<text class="mono" x="{x+bw/2:.1f}" y="{base+20}" text-anchor="middle" font-size="10" '
                 f'fill="{t["muted"]}">{mn[int(k[5:7])-1]}</text>')
        if i in (imax, n - 1):
            g.append(f'<text class="mono" x="{x+bw/2:.1f}" y="{base-h-8:.1f}" text-anchor="middle" font-size="10.5" '
                     f'fill="{t["secondary"]}">{c:,}</text>')
    g.append(f'<line x1="{cx+24}" x2="{cx+cw-24}" y1="{base+.5}" y2="{base+.5}" stroke="{t["border"]}"/>')
    alt = (f"{st['total']:,} contributions in the last 12 months; longest streak {st['longest']} days; current streak "
           f"{st['current']} days; busiest weekday {st['weekday']}. Per month: "
           + ", ".join(f"{mn[int(k[5:7])-1]} {c}" for k, c in months))
    return svg(W, H, alt, css, "".join(g))


# ---------------------------------------------------------------- contact row
def button(t, label, icon):
    fs = 14
    w = int(52 + len(label) * fs * 0.56)
    H = 40
    css = font_css(mono=False) + BASE_CSS
    ic = {
        "linkedin": (f'<rect x="14" y="11" width="18" height="18" rx="4" fill="{t["primary"]}"/>'
                     '<text x="23" y="25" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" '
                     'font-size="12" font-weight="700" fill="#ffffff">in</text>'),
        "web": (f'<circle cx="23" cy="20" r="8.5" fill="none" stroke="{t["link"]}" stroke-width="1.5"/>'
                f'<ellipse cx="23" cy="20" rx="3.6" ry="8.5" fill="none" stroke="{t["link"]}" stroke-width="1.2"/>'
                f'<line x1="14.5" y1="20" x2="31.5" y2="20" stroke="{t["link"]}" stroke-width="1.2"/>'),
    }[icon]
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="{H-1}" rx="8" fill="{t["card"]}" stroke="{t["border"]}"/>'
            + ic + f'<text class="sans" x="42" y="25" font-size="{fs}" font-weight="560" fill="{t["text"]}">{label}</text>')
    return svg(w, H, label, css, body)


def open_to(t):
    parts = [("BASED IN", "Düsseldorf"), ("OPEN TO", "tech partnerships · talent")]
    fs = 12
    adv = fs * MONO_ADV
    x = 0
    body = []
    for k, (lab, val) in enumerate(parts):
        w = int(28 + (len(lab) + len(val) + 2) * adv)
        body.append(f'<rect x="{x+.5}" y=".5" width="{w-1}" height="31" rx="16" fill="{t["card"]}" stroke="{t["border"]}"/>')
        body.append(f'<circle cx="{x+15}" cy="16" r="2.5" fill="{t["success"] if k else t["link"]}"/>')
        body.append(f'<text class="mono" x="{x+25}" y="20" font-size="{fs}" fill="{t["muted"]}">{lab}'
                    f'<tspan dx="{adv:.1f}" fill="{t["text"]}">{val}</tspan></text>')
        x += w + 8
    css = font_css(geist=False) + BASE_CSS
    return svg(int(x - 8), 32, "Based in Düsseldorf. Open to tech partnerships and talent.", css, "".join(body))


# ---------------------------------------------------------------- org card (links to the OTG org)
def org_card(t):
    W, H = 1200, 132
    css = font_css(mono_bold=True) + BASE_CSS + """
@keyframes fan0{0%,15%{transform:rotate(0)}40%,80%{transform:rotate(-16deg)}100%{transform:rotate(0)}}
@keyframes fan2{0%,15%{transform:rotate(0)}40%,80%{transform:rotate(16deg)}100%{transform:rotate(0)}}
.k0{transform-box:view-box;transform-origin:96px 150px;animation:fan0 7s cubic-bezier(.3,.7,.2,1) infinite}
.k2{transform-box:view-box;transform-origin:96px 150px;animation:fan2 7s cubic-bezier(.3,.7,.2,1) infinite}
@media (prefers-reduced-motion: reduce){.k0{transform:rotate(-16deg)}.k2{transform:rotate(16deg)}}
@keyframes nudge{0%,100%{transform:translateX(0)}50%{transform:translateX(5px)}}
.arrow{animation:nudge 1.8s ease-in-out infinite}
"""
    g = [f'<clipPath id="oc"><rect width="{W}" height="{H}" rx="12"/></clipPath>',
         f'<g clip-path="url(#oc)"><rect width="{W}" height="{H}" fill="{t["card"]}"/>']
    for k in (0, 2, 1):  # front card last so it sits on top
        front = k == 1
        g.append(f'<g class="k{k}"><rect x="72" y="26" width="48" height="66" rx="6" fill="{t["primary"] if front else t["section"]}" '
                 f'stroke="{t["primary"] if front else t["border"]}"/>'
                 + ("".join(f'<rect x="{80 + c * 11}" y="{36 + r * 9}" width="8" height="6" rx="1" fill="#ffffff" opacity=".9"/>'
                            for r in range(3) for c in range(3)) if front else "") + '</g>')
    g.append('</g>')
    g.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{t["border"]}"/>')
    g.append(f'<text class="mono" x="168" y="46" font-size="11" letter-spacing="1.8" fill="{t["muted"]}">BUILDING</text>')
    g.append(f'<text class="sans" x="166" y="82" font-size="30" font-weight="640" letter-spacing="-.8" fill="{t["text"]}">One Tech Group</text>')
    g.append(f'<text class="sans" x="168" y="108" font-size="15" fill="{t["secondary"]}">The ad infrastructure for publishers.</text>')
    g.append(f'<text class="mono" x="{W-80}" y="72" text-anchor="end" font-size="13" fill="{t["link"]}">github.com/One-Tech-Group-GmbH</text>')
    g.append(f'<g class="arrow"><path d="M{W-62},66 h22 m-8,-8 l8,8 l-8,8" fill="none" stroke="{t["link"]}" stroke-width="2" '
             f'stroke-linecap="round" stroke-linejoin="round"/></g>')
    return svg(W, H, "Building One Tech Group: the ad infrastructure for publishers. Opens the organization on GitHub.", css, "".join(g))


# ---------------------------------------------------------------- Rheinturm color chips (no embedded fonts: tiny files)
def rt_chip(t, name, fill):
    w = int(28 + len(name) * 7.6 + 14)  # ~7.6px per char of system mono at 12.5px; 14px right padding
    body = (f'<rect x=".5" y=".5" width="{w-1}" height="29" rx="15" fill="{t["card"]}" stroke="{t["border"]}"/>'
            f'<circle cx="16" cy="15" r="6" fill="{fill}"/>'
            f'<text x="28" y="19.5" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12.5" '
            f'fill="{t["secondary"]}">{name}</text>')
    return svg(w, 30, f"Light up the Rheinturm in {name}", "", body)


# ---------------------------------------------------------------- gravity contribution graph
LEVELS = {"light": ["#f0eeea", "#c9d4f2", "#93a8e6", "#4d6fd0", "#1d48c0"],
          "dark": ["#252422", "#1e2a44", "#243056", "#3a57b8", "#7e97e3"]}


def gravity(t, mode, days):
    """"Settle": the contribution calendar collapses into weekly bars (active days per week) and rebuilds."""
    import datetime as dt
    weeks = [days[i:i + 7] for i in range(0, len(days), 7)]
    first = next((i for i, w in enumerate(weeks) if any(c for _, c in w)), 0)
    weeks = weeks[first:]
    n = len(weeks)
    W = 1200
    step = min(26.0, (W - 96) / max(n, 1))
    cs = step - 4
    x0 = (W - n * step + 4) / 2
    y0 = 74
    base = y0 + 7 * step  # floor under row 6
    H = int(base + 46)
    nz = sorted(c for _, c in days if c > 0)
    q = [nz[int(len(nz) * f)] if nz else 1 for f in (.25, .5, .75)]

    def level(c):
        return 0 if c == 0 else 1 + sum(c > v for v in q)

    T, t_set, d_set, t_back = 12.0, 3.0, 0.9, 9.0
    css = font_css(mono_bold=True) + BASE_CSS
    g = [f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["card"]}" stroke="{t["border"]}"/>',
         f'<text class="mono" x="24" y="34" font-size="11" letter-spacing="1.6" fill="{t["muted"]}">CONTRIBUTIONS · LAST 12 MONTHS</text>']
    # phase caption cross-fade (top right)
    for k, (lab, show) in enumerate([("calendar", "1;1;0;0;1;1"), ("active days per week", "0;0;1;1;0;0")]):
        g.append(f'<text class="mono" x="{W-24}" y="34" text-anchor="end" font-size="11" letter-spacing="1" fill="{t["link"]}" opacity="{show[0]}">'
                 f'{lab}<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="{show}" '
                 f'keyTimes="0;{t_set/T:.4f};{(t_set+.5)/T:.4f};{t_back/T:.4f};{(t_back+.5)/T:.4f};1"/></text>')
    g.append(f'<line x1="{x0-6:.1f}" x2="{x0 + n*step + 2:.1f}" y1="{base + 2.5:.1f}" y2="{base + 2.5:.1f}" stroke="{t["border"]}"/>')
    last_month = None
    for c, wk in enumerate(weeks):
        x = x0 + c * step
        m = dt.date.fromisoformat(wk[0][0]).month
        if m != last_month:
            g.append(f'<text class="mono" x="{x:.1f}" y="{base + 22:.1f}" font-size="10" fill="{t["muted"]}">'
                     f'{["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][m-1]}</text>')
            last_month = m
        active = [r for r, (_, cnt) in enumerate(wk) if cnt > 0]
        lag = c * 0.025
        ts, te, tb, tbe = t_set + lag, t_set + lag + d_set, t_back + lag, t_back + lag + d_set
        kt = f"0;{ts/T:.4f};{te/T:.4f};{tb/T:.4f};{tbe/T:.4f};1"
        for r, (_, cnt) in enumerate(wk):
            y = y0 + r * step
            lv = level(cnt)
            if lv == 0:
                g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" rx="3" fill="{LEVELS[mode][0]}">'
                         f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" values="1;1;0;0;1;1" keyTimes="{kt}"/></rect>')
                continue
            target = 7 - len(active) + active.index(r)
            dy = (target - r) * step
            g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" rx="3" fill="{LEVELS[mode][lv]}">'
                     f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" '
                     f'values="0 0;0 0;0 {dy:.1f};0 {dy:.1f};0 0;0 0" keyTimes="{kt}" calcMode="spline" '
                     f'keySplines="0 0 1 1;.5 0 .2 1;0 0 1 1;.5 0 .2 1;0 0 1 1"/></rect>')
    return svg(W, H, "Contribution calendar of the last 12 months; it settles into weekly bars of active days and rebuilds.",
               css, "".join(g))


# ---------------------------------------------------------------- live data
LAT, LON = 51.2277, 6.7735


def http_json(url, data=None, headers=None):
    import json
    import urllib.request
    req = urllib.request.Request(url, data=data, headers=headers or {"User-Agent": "profile-svg-builder"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())


def fetch_calendar(user, token):
    import json
    q = ('query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{'
         'weeks{contributionDays{date contributionCount}}}}}}')
    res = http_json("https://api.github.com/graphql",
                    data=json.dumps({"query": q, "variables": {"u": user}}).encode(),
                    headers={"Authorization": f"bearer {token}", "User-Agent": "profile-svg-builder",
                             "Content-Type": "application/json"})
    weeks = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"]]


def wmo_to_weather(code):
    if code in (0, 1):
        return "clear"
    if code == 2:
        return "partly"
    if code == 3:
        return "cloudy"
    if code in (45, 48):
        return "fog"
    if code in (71, 73, 75, 77, 85, 86):
        return "snow"
    if code in (95, 96, 99):
        return "storm"
    return "rain"  # drizzle, rain, showers, freezing rain


def fetch_weather():
    import datetime as dt
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
         "&current=weather_code,temperature_2m&daily=sunrise,sunset&timezone=Europe%2FBerlin&forecast_days=1")
    w = http_json(u)
    from zoneinfo import ZoneInfo
    now = dt.datetime.now(ZoneInfo("Europe/Berlin")).replace(tzinfo=None)  # real time, not the API's 15-min slot
    rise = dt.datetime.fromisoformat(w["daily"]["sunrise"][0])
    sset = dt.datetime.fromisoformat(w["daily"]["sunset"][0])
    m = dt.timedelta(minutes=1)
    # dusk ~ civil twilight: it is dark ~30 min after sunset (and light ~30 min before sunrise)
    if rise - 30 * m <= now <= rise + 30 * m or sset - 30 * m <= now <= sset + 30 * m:
        phase = "dusk"
    elif rise < now < sset:
        phase = "day"
    else:
        phase = "night"
    return dict(phase=phase, weather=wmo_to_weather(w["current"]["weather_code"]),
                temp=w["current"]["temperature_2m"])


def main():
    import argparse
    import os
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="fetch calendar + weather, write live SVGs")
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--phase")
    ap.add_argument("--weather")
    ap.add_argument("--season", choices=sorted(SEASON_LABEL))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def write(name, content):
        p = out / name
        p.write_text(content, encoding="utf-8")
        print(f"{p}  {p.stat().st_size/1024:.0f} KB")

    if args.live:
        user = os.environ.get("GH_USER", "onetechgroupll")
        days = fetch_calendar(user, os.environ["GITHUB_TOKEN"])
        st = calendar_stats(days)
        try:
            wx = fetch_weather()
        except Exception as e:  # weather is decoration: fall back, never fail the build
            print("weather unavailable:", e)
            wx = dict(phase="day", weather="clear", temp=None)
        if args.phase:
            wx["phase"] = args.phase
        if args.weather:
            wx["weather"] = args.weather
        import datetime as dt
        from zoneinfo import ZoneInfo
        wx["season"] = args.season or season_for(dt.datetime.now(ZoneInfo("Europe/Berlin")))
        from rheinturm import COLORS, load_state
        rt = load_state()
        print("weather:", wx)
        for mode, t in THEMES.items():
            write(f"stats-{mode}.svg", stats(t, mode, st))
            write(f"gravity-{mode}.svg", gravity(t, mode, days))
            write(f"skyline-{mode}.svg", skyline(t, mode, **wx, pod=COLORS[rt["color"]][0 if mode == "light" else 1],
                                                 lit_by=rt.get("user")))
        return

    for name, fn in [("header", header), ("focus", focus), ("terminal", terminal)]:
        for mode, t in THEMES.items():
            write(f"{name}-{mode}.svg", fn(t))
    for mode, t in THEMES.items():
        write(f"skyline-{mode}.svg", skyline(t, mode))
        write(f"avatar-{mode}.svg", skyline(t, mode, crop=AVATAR_CROP, label=False))
        write(f"btn-linkedin-{mode}.svg", button(t, "LinkedIn", "linkedin"))
        write(f"btn-web-{mode}.svg", button(t, "onetech.group", "web"))
        write(f"open-to-{mode}.svg", open_to(t))
        write(f"org-card-{mode}.svg", org_card(t))
        from rheinturm import COLORS
        for name, (lf, df) in COLORS.items():
            write(f"rt-{name}-{mode}.svg", rt_chip(t, name, lf if mode == "light" else df))
        for p in OSS:
            write(f"oss-{p['repo'].split('/')[1]}-{mode}.svg", oss_card(t, p))


if __name__ == "__main__":
    main()
