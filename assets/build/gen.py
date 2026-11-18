#!/usr/bin/env python3
"""Generate the six README SVGs (hero / pace / terminal x dark / light).

One layout function per image, fed a theme dict, so the dark and light
variants share geometry exactly and differ only in colour.
Output: the parent directory of this script (assets/).
Run: python3 assets/build/gen.py
"""
import math
import os
import sys

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SANS = '-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif'
MONO = 'ui-monospace, SFMono-Regular, Menlo, Consolas, monospace'

THEMES = {
    "dark": dict(
        bg="#181818", panel="#212121", hair="#2f2f2f",
        text="#ecece8", muted="#9b9a94",
        clay="#d97757", sage="#9bb07c",
        grid="#2a2a2a", axis="#4b4a46", conn="#5a5955", dots="#3b3b39", node="#333332",
        band="#ecece8", band_op="0.055", band_label="#9b9a94",
    ),
    "light": dict(
        bg="#faf9f5", panel="#ffffff", hair="#e6e3d9",
        text="#1f1e1c", muted="#6f6d66",
        # #c96442 is 3.70:1 on #faf9f5; #b3532f keeps the hue and reaches 4.75:1.
        clay="#b3532f", sage="#5f7347",
        grid="#ebe8df", axis="#c4c0b4", conn="#c4bfb2", dots="#dcd8cd", node="#dedacf",
        band="#1f1e1c", band_op="0.045",
        # muted text sitting on the band: #6f6d66 would be 4.50:1 there
        band_label="#67655e",
    ),
}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_open(w, h, title, desc=None):
    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-labelledby="t">',
        f'<title id="t">{esc(title)}</title>',
    ]
    if desc:
        out.append(f"<desc>{esc(desc)}</desc>")
    return out


def base_style(t, extra=""):
    return f"""<style>
.sans {{ font-family: {SANS}; }}
.mono {{ font-family: {MONO}; }}
.tx {{ fill: {t['text']}; }}
.mu {{ fill: {t['muted']}; }}
.clay {{ fill: {t['clay']}; }}
.sage {{ fill: {t['sage']}; }}
{extra}</style>"""


def card(w, h, t):
    # 1px hairline border drawn on the half-pixel so it stays crisp.
    return (f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="20" '
            f'fill="{t["bg"]}" stroke="{t["hair"]}" stroke-width="1"/>')


# --------------------------------------------------------------------------
# 1. Hero
# --------------------------------------------------------------------------
def hero(t):
    W, H = 1280, 420
    s = svg_open(
        W, H,
        "model-routing: the top-tier main session (Mythos, Fable) decides and "
        "accepts; four Opus subagents read, code, debug and review.",
    )
    s.append(base_style(t, """
.eyebrow { font-size: 22px; letter-spacing: 4px; }
.title { font-size: 76px; font-weight: 700; letter-spacing: -1.5px; }
.tag { font-size: 28px; }
.node { font-size: 24px; font-weight: 600; }
.sub { font-size: 22px; }
.cap { font-size: 22px; }
"""))
    s.append(card(W, H, t))

    # Left: wordmark
    s.append('<text class="mono eyebrow mu" x="72" y="104">CLAUDE CODE SKILL</text>')
    s.append('<text class="sans title tx" x="68" y="190">model-routing</text>')
    for i, line in enumerate([
        "The top-tier model decides.",
        "Opus does the work.",
        "The week stays on pace.",
    ]):
        s.append(f'<text class="sans tag mu" x="72" y="{250 + 40 * i}">{line}</text>')

    # Right: routing diagram
    cy = 210
    main_x, main_w, main_h = 668, 212, 100
    main_r = main_x + main_w
    opus_x, opus_w, opus_h = 990, 120, 48
    opus_ys = [cy - 117, cy - 39, cy + 39, cy + 117]
    caps = ["read", "code", "debug", "review"]
    stem_end = main_r + 22
    ctrl = (stem_end + opus_x) / 2

    s.append(f'<g fill="none" stroke="{t["conn"]}" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round">')
    for yc in opus_ys:
        s.append(f'<path d="M{main_r} {cy} H{stem_end} C{ctrl} {cy} {ctrl} {yc} {opus_x} {yc}"/>')
    s.append("</g>")

    # Main node
    s.append(f'<rect x="{main_x}" y="{cy - main_h / 2}" width="{main_w}" height="{main_h}" rx="14" '
             f'fill="{t["panel"]}" stroke="{t["node"]}" stroke-width="1.5"/>')
    s.append(f'<circle cx="{main_x + 22}" cy="{cy - 18}" r="5" fill="{t["clay"]}"/>')
    s.append(f'<text class="sans node tx" x="{main_x + 36}" y="{cy - 10}">Main session</text>')
    s.append(f'<text class="sans sub mu" x="{main_x + 36}" y="{cy + 22}">Mythos · Fable</text>')
    s.append(f'<text class="mono cap clay" x="{main_x + 2}" y="{cy + main_h / 2 + 38}">decide · accept</text>')

    # Opus nodes
    for yc, cap in zip(opus_ys, caps):
        s.append(f'<rect x="{opus_x}" y="{yc - opus_h / 2}" width="{opus_w}" height="{opus_h}" rx="12" '
                 f'fill="{t["panel"]}" stroke="{t["node"]}" stroke-width="1.5"/>')
        s.append(f'<circle cx="{opus_x + 22}" cy="{yc}" r="5" fill="{t["sage"]}"/>')
        s.append(f'<text class="sans node tx" x="{opus_x + 36}" y="{yc + 8}">Opus</text>')
        s.append(f'<text class="mono cap sage" x="{opus_x + opus_w + 22}" y="{yc + 7}">{cap}</text>')

    s.append("</svg>")
    return "\n".join(s) + "\n"


# --------------------------------------------------------------------------
# 2. Pace chart
# --------------------------------------------------------------------------
X0, X1 = 120, 1196          # x = 0% .. 100%
YB, YT = 452, 88            # y = 0% .. 100%


def px(x):
    return X0 + (X1 - X0) * x / 100.0


def py(y):
    return YB - (YB - YT) * y / 100.0


# Knots for two plausible cumulative-usage curves (x = % of week, y = % used).
# Soft plateaus around x ~ 14-17, 27-31, 41-45 are nights; slopes vary by day.
KX = [0, 2, 4, 6, 8.5, 11, 13.5, 15, 17, 19.5, 22, 24.5, 27, 29, 31, 33.5, 36,
      38.5, 41, 43, 45, 47, 48.5, 50]
TOP_Y = [0, 3.4, 6.0, 8.6, 11.8, 15.4, 19.6, 20.8, 21.4, 24.6, 29, 33.2, 38, 39.4,
         40, 43.6, 49, 54.6, 60, 62.2, 63, 64.6, 67, 70]
WK_Y = [0, 0.8, 2.0, 4.0, 6.6, 9.2, 12, 12.8, 13.2, 15.2, 18, 21, 24.4, 25.4, 26,
        28, 31.4, 35, 38.8, 40.4, 41, 42, 44, 46]


def monotone(xs, ys, step=0.25):
    """Fritsch-Carlson monotone cubic interpolation, sampled every `step`."""
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [0.0] * (n - 2) + [d[-1]]
    for i in range(1, n - 1):
        m[i] = 0.0 if d[i - 1] * d[i] <= 0 else (d[i - 1] + d[i]) / 2
    for i in range(n - 1):
        if d[i] == 0:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        h = a * a + b * b
        if h > 9:
            tau = 3 / math.sqrt(h)
            m[i], m[i + 1] = tau * a * d[i], tau * b * d[i]
    out = []
    for i in range(n - 1):
        x0, x1, y0, y1 = xs[i], xs[i + 1], ys[i], ys[i + 1]
        hh = x1 - x0
        k = max(1, int(round(hh / step)))
        for j in range(k):
            tt = j / k
            h00 = 2 * tt**3 - 3 * tt**2 + 1
            h10 = tt**3 - 2 * tt**2 + tt
            h01 = -2 * tt**3 + 3 * tt**2
            h11 = tt**3 - tt**2
            out.append((x0 + tt * hh, h00 * y0 + h10 * hh * m[i] + h01 * y1 + h11 * hh * m[i + 1]))
    out.append((xs[-1], ys[-1]))
    return out


def pace(t):
    W, H = 1280, 560
    s = svg_open(
        W, H,
        "Pace check: quota used against week elapsed. A dashed even-burn line "
        "runs from 0,0 to 100,100 with a plus/minus 10 point band. At 50% of the "
        "week the top-tier bar is at 70% (20 points ahead: back off) and the weekly "
        "bar is at 46% (on pace). 90% used is a hard stop.",
    )
    s.append(base_style(t, """
.tick { font-size: 22px; font-variant-numeric: tabular-nums; }
.axt { font-size: 22px; }
.ann { font-size: 24px; }
.lab { font-size: 24px; }
.labb { font-weight: 600; }
"""))
    s.append(card(W, H, t))

    # Gridlines (solid, recessive) at 0/25/50/75/100
    s.append(f'<g stroke="{t["grid"]}" stroke-width="1.5" fill="none">')
    for v in (25, 50, 75):
        s.append(f'<line x1="{X0}" y1="{py(v):.1f}" x2="{X1}" y2="{py(v):.1f}"/>')
    # vertical gridlines stop at the 90% rule; the strip above it stays clear for its label
    for v in (25, 50, 75, 100):
        s.append(f'<line x1="{px(v):.1f}" y1="{py(90):.1f}" x2="{px(v):.1f}" y2="{YB}"/>')
    s.append("</g>")
    # Axes (baseline + y axis), one step stronger
    s.append(f'<path d="M{X0} {YT} V{YB} H{X1}" fill="none" stroke="{t["axis"]}" stroke-width="1.5"/>')

    # +/-10 pt band around the even-burn line
    band = [(0, 0), (0, 10), (90, 100), (100, 100), (100, 90), (10, 0)]
    d = "M" + " L".join(f"{px(x):.1f} {py(y):.1f}" for x, y in band) + " Z"
    s.append(f'<path class="avoid-soft" d="{d}" fill="{t["band"]}" fill-opacity="{t["band_op"]}"/>')

    # Band edges as invisible geometry for the collision check only
    s.append(f'<g class="avoid" fill="none" stroke="none">'
             f'<line x1="{px(0):.1f}" y1="{py(10):.1f}" x2="{px(90):.1f}" y2="{py(100):.1f}"/>'
             f'<line x1="{px(10):.1f}" y1="{py(0):.1f}" x2="{px(100):.1f}" y2="{py(90):.1f}"/></g>')

    # 90% threshold: solid, neutral
    s.append(f'<line class="avoid" x1="{X0}" y1="{py(90):.1f}" x2="{X1}" y2="{py(90):.1f}" '
             f'stroke="{t["muted"]}" stroke-width="2"/>')

    # Even-burn diagonal: dashed reference
    s.append(f'<line class="avoid" x1="{px(0)}" y1="{py(0)}" x2="{px(100)}" y2="{py(100)}" '
             f'stroke="{t["muted"]}" stroke-width="2" stroke-dasharray="10 8"/>')

    # Trajectories
    top = monotone(KX, TOP_Y)      # ends at 70
    wk = monotone(KX, WK_Y)        # ends at 46
    assert abs(top[-1][1] - 70) < 1e-6 and abs(wk[-1][1] - 46) < 1e-6
    for pts in (top, wk):
        assert all(b[0] >= a[0] and b[1] >= a[1] - 1e-9 for a, b in zip(pts, pts[1:])), "non-monotonic"
    for pts, col in ((wk, t["sage"]), (top, t["clay"])):
        d = "M" + " L".join(f"{px(x):.1f} {py(y):.1f}" for x, y in pts)
        s.append(f'<path class="avoid" d="{d}" fill="none" stroke="{col}" stroke-width="3" '
                 'stroke-linejoin="round" stroke-linecap="round"/>')
    for pts, col in ((wk, t["sage"]), (top, t["clay"])):
        x, y = pts[-1]
        s.append(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="7" fill="{col}" '
                 f'stroke="{t["bg"]}" stroke-width="3"/>')

    # Axis ticks
    for v in (0, 25, 50, 75, 100):
        s.append(f'<text class="sans tick mu" x="{X0 - 16}" y="{py(v) + 8:.1f}" text-anchor="end">{v}%</text>')
        s.append(f'<text class="sans tick mu" x="{px(v):.1f}" y="{YB + 38}" text-anchor="middle">{v}%</text>')
    s.append(f'<text class="sans axt mu" x="40" y="54">quota used</text>')
    s.append(f'<text class="sans axt mu" x="{X1}" y="528" text-anchor="end">week elapsed</text>')

    # Direct labels
    # threshold label: above the line, right-aligned short of the band
    s.append(f'<text class="sans ann tx" x="{px(76):.1f}" y="{py(90) - 14:.1f}" text-anchor="end">90% → stop spending this bar</text>')
    # region labels
    s.append(f'<text class="sans ann mu" x="{X0 + 18}" y="{py(57):.1f}">ahead of the line → back off</text>')
    s.append(f'<text class="sans ann mu" x="{X1 - 18}" y="{py(12):.1f}" text-anchor="end">behind the line → room to escalate</text>')

    # even-burn label, rotated along the diagonal, above it
    ang = math.degrees(math.atan2(py(0) - py(100), px(100) - px(0)))
    ex, ey = px(68), py(68)
    nx, ny = -math.sin(math.radians(ang)), -math.cos(math.radians(ang))
    lx, ly = ex + nx * 10, ey + ny * 10
    s.append(f'<text class="sans axt" fill="{t["band_label"]}" x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
             f'transform="rotate({-ang:.2f} {lx:.1f} {ly:.1f})">even-burn line</text>')

    # end labels (text tokens; the coloured dot beside each carries identity)
    tx_, ty_ = px(50), py(70)
    s.append(f'<text class="sans lab tx" x="{tx_ - 18:.1f}" y="{ty_ - 22:.1f}" text-anchor="end">'
             f'<tspan class="labb">top-tier 70%</tspan><tspan class="mu"> · </tspan>'
             f'<tspan class="mono mu">BACK_OFF_TOP</tspan></text>')
    wx_, wy_ = px(50), py(46)
    s.append(f'<text class="sans lab tx" x="{wx_ + 18:.1f}" y="{wy_ + 46:.1f}">'
             f'<tspan class="labb">weekly 46%</tspan><tspan class="mu"> · on pace</tspan></text>')

    s.append("</svg>")
    return "\n".join(s) + "\n"


# --------------------------------------------------------------------------
# 3. Terminal
# --------------------------------------------------------------------------
TERM_LINES = [
    "$ python3 scripts/pace.py --weekly 46 --top 70 --resets-at 2026-11-25T05:00:00Z",
    "window: 50.0% elapsed, resets in 3d 12h",
    "bar        used  line  delta  projected",
    "weekly      46%   50%     -4        92%",
    "top-tier    70%   50%    +20       140%",
    "verdict: BACK_OFF_TOP",
    "action:  Top-tier is burning ahead of the line. Main session delegates more",
    "         to Opus and keeps its context small. No top-tier subagents.",
]


def term_line_markup(i, line):
    """Return inner markup for one line. No whitespace outside the text itself."""
    if i == 0:
        assert line.startswith("$ ")
        return f'<tspan class="mu">$</tspan>{esc(line[1:])}'
    if i == 2:
        return f'<tspan class="mu">{esc(line)}</tspan>'
    if i == 4:
        k = line.index("+20")
        return f'{esc(line[:k])}<tspan class="clay">+20</tspan>{esc(line[k + 3:])}'
    if i == 5:
        k = line.index("BACK_OFF_TOP")
        return f'{esc(line[:k])}<tspan class="clay">BACK_OFF_TOP</tspan>{esc(line[k + 12:])}'
    return esc(line)


def terminal(t):
    W = 1280
    bar_h = 60
    first = bar_h + 56
    lh = 35
    H = first + lh * (len(TERM_LINES) - 1) + 46
    s = svg_open(
        W, H,
        "Terminal output of pace.py: weekly bar 46% used against a 50% line (on "
        "pace); top-tier bar 70% used, 20 points ahead, projected 140%. "
        "Verdict: BACK_OFF_TOP.",
    )
    s.append(base_style(t, f"""
.term {{ font-size: 23px; white-space: pre; }}
.wtitle {{ font-size: 22px; font-weight: 500; }}
"""))
    s.append('<defs><clipPath id="win"><rect x="0.5" y="0.5" width="1279" '
             f'height="{H - 1}" rx="20"/></clipPath></defs>')
    s.append(card(W, H, t))
    # title bar (raised), clipped to the window's rounded corners
    s.append(f'<rect x="0" y="0" width="{W}" height="{bar_h}" fill="{t["panel"]}" clip-path="url(#win)"/>')
    s.append(f'<line x1="0" y1="{bar_h - 0.5}" x2="{W}" y2="{bar_h - 0.5}" stroke="{t["hair"]}" stroke-width="1"/>')
    # redraw the outer border on top so the bar does not cover it
    s.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="20" fill="none" '
             f'stroke="{t["hair"]}" stroke-width="1"/>')
    for k in range(3):
        s.append(f'<circle cx="{38 + 26 * k}" cy="{bar_h / 2}" r="7" fill="{t["dots"]}"/>')
    s.append(f'<text class="sans wtitle mu" x="{W / 2}" y="{bar_h / 2 + 8}" text-anchor="middle">pace.py</text>')

    for i, line in enumerate(TERM_LINES):
        y = first + lh * i
        s.append(f'<text class="mono term tx" xml:space="preserve" x="48" y="{y}" '
                 f'data-line="{i}">{term_line_markup(i, line)}</text>')
    s.append("</svg>")
    return "\n".join(s) + "\n"


def main():
    builders = {"hero": hero, "pace": pace, "terminal": terminal}
    for name, fn in builders.items():
        for mode, t in THEMES.items():
            path = os.path.join(OUT, f"{name}-{mode}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(fn(t))
            print("wrote", path)


if __name__ == "__main__":
    sys.exit(main())
