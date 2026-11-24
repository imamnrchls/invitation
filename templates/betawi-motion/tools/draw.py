"""Draw the Betawi Motion illustration layers as SVG.

Run:  python3 templates/betawi-motion/tools/draw.py <svg-dir>
Then: node templates/vintage-blue/tools/render.mjs <svg-dir> <png-dir>
      python3 templates/betawi-motion/tools/pack.py <png-dir>

Everything is drawn procedurally: a rumah kebaya, kembang kelapa, gigi balang
trim, pastel mountains and a lily meadow. Replace any .webp in ../assets with a
painted version of the same size and transparency to upgrade the look.
"""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'svg')
OUT.mkdir(parents=True, exist_ok=True)

PEACH = ['#fbeee4', '#f5d6c2', '#eab79b', '#d9977a', '#b9735a']
SAGE = ['#eef2e2', '#d3e0bf', '#b2c896', '#8fad72', '#6b8a52', '#4e6a3c']
LAKE = ['#e7eef2', '#c9d8e0', '#a9bfcc']
PINK = ['#fde7ee', '#f7bfd0', '#ee93ad', '#d9688b', '#b24a6c']
GOLD = ['#f3dfa4', '#d9b65f', '#a9852f']
RIBBON = ['#e2483d', '#f2b632', '#53a35a', '#3f7fc4', '#e76fa6', '#8c5bc0', '#f07c2c', '#2fb0a8']


def f(n):
    return f'{n:.1f}'.rstrip('0').rstrip('.')


def path(points, close=True):
    return 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in points) + (' Z' if close else '')


def smooth(points, close=False):
    pts = points + points[:2] if close else [points[0]] + points + [points[-1]]
    d = f'M{f(pts[1][0])},{f(pts[1][1])}'
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{f(c1[0])},{f(c1[1])} {f(c2[0])},{f(c2[1])} {f(p2[0])},{f(p2[1])}'
    return d + (' Z' if close else '')


def svg(name, w, h, body, defs=''):
    (OUT / f'{name}.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<defs>{defs}{PAPER}</defs>{body}</svg>')


PAPER = ('<filter id="paper" x="-5%" y="-5%" width="110%" height="110%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="5" result="n"/>'
         '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -.8 .6" result="g"/>'
         '<feComposite in="SourceGraphic" in2="g" operator="in" result="t"/>'
         '<feBlend in="SourceGraphic" in2="t" mode="multiply"/></filter>')


def hatch(rng, line, depth, color, density=3, opacity=.5, width=.55):
    out = []
    for i in range(1, len(line) - 1):
        x, y = line[i]
        slope = (line[i + 1][1] - line[i - 1][1]) / (line[i + 1][0] - line[i - 1][0])
        for _ in range(density):
            length = rng.uniform(depth * .25, depth)
            lean = slope * length * .8
            out.append(f'M{f(x + rng.uniform(-2, 2))},{f(y + rng.uniform(1, 5))} q{f(lean * .3)},{f(length * .5)} {f(lean)},{f(length)}')
    return f'<path d="{" ".join(out)}" stroke="{color}" stroke-width="{width}" fill="none" opacity="{opacity}" stroke-linecap="round"/>'


def ridge(rng, w, base, peaks, rough, step=3):
    pts = []
    for x in range(0, w + step, step):
        y = base
        for px, ph, pw in peaks:
            y -= ph * math.exp(-((x - px) / pw) ** 2)
        pts.append([x, y])
    for octave, scale in ((14, 1), (6, .5), (3, .3)):
        ph = rng.random() * 50
        for p in pts:
            p[1] += rough * scale * math.sin(p[0] / octave + ph) * math.cos(p[0] / (octave * 1.7) + ph)
    return pts


# ---------------------------------------------------------------- sky
def draw_sky():
    defs = ('<linearGradient id="s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#dfe7f1"/>'
            '<stop offset=".45" stop-color="#eef0f4"/><stop offset="1" stop-color="#f9f1ea"/></linearGradient>'
            '<filter id="cloud" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".008 .022" numOctaves="4" seed="9"/>'
            '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.9 -.85"/><feGaussianBlur stdDeviation="3"/></filter>'
            '<filter id="shade" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".01 .03" numOctaves="3" seed="21"/>'
            '<feColorMatrix type="matrix" values="0 0 0 0 .72  0 0 0 0 .76  0 0 0 0 .84  0 0 0 1.4 -.78"/><feGaussianBlur stdDeviation="4"/></filter>')
    body = ('<rect width="480" height="900" fill="url(#s)"/><rect width="480" height="620" filter="url(#shade)" opacity=".6"/>'
            '<rect width="480" height="620" filter="url(#cloud)"/><rect width="480" height="900" fill="#fff" opacity=".001" filter="url(#paper)"/>')
    svg('sky', 480, 900, body, defs)


# ---------------------------------------------------------------- mountain
def draw_mountain():
    rng = random.Random(4)
    w, h = 480, 420
    line = ridge(rng, w, 372, [(236, 236, 30), (282, 196, 26), (196, 168, 28), (322, 146, 34), (150, 112, 36), (372, 86, 44), (90, 60, 54), (420, 40, 50)], 9)
    shape = path(line + [[w, h], [0, h]])
    defs = (f'<linearGradient id="m" x1="0" y1="0" x2="0" y2="1"><stop offset=".1" stop-color="{PEACH[1]}"/>'
            f'<stop offset=".6" stop-color="{PEACH[2]}"/><stop offset="1" stop-color="{PEACH[3]}"/></linearGradient>'
            f'<clipPath id="c"><path d="{shape}"/></clipPath>'
            '<linearGradient id="mist" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#f6efe9" stop-opacity=".9"/></linearGradient>')
    parts = [f'<path d="{shape}" fill="url(#m)"/>', '<g clip-path="url(#c)">']
    parts.append(hatch(rng, line, 46, PEACH[4], 4, .55))
    for k in range(5):
        cx = rng.uniform(130, 350)
        sub = ridge(rng, w, 372 + k * 4, [(cx, rng.uniform(90, 200), rng.uniform(16, 28)), (cx + 40, rng.uniform(60, 120), 20)], 7)
        parts.append(f'<path d="{path(sub + [[w, h], [0, h]])}" fill="{PEACH[0]}" opacity=".28"/>')
        parts.append(hatch(rng, sub, 30, PEACH[4], 2, .4, .5))
    # snow-light streaks down the gullies
    for _ in range(40):
        x = rng.uniform(150, 340)
        y = rng.uniform(120, 300)
        parts.append(f'<path d="M{f(x)},{f(y)} q{f(rng.uniform(-6, 6))},12 {f(rng.uniform(-10, 10))},{f(rng.uniform(20, 40))}" stroke="#fff" stroke-width="1.2" opacity=".5" fill="none"/>')
    parts.append('</g>')
    parts.append(f'<path d="{path(line, False)}" stroke="{PEACH[4]}" stroke-width=".8" fill="none" opacity=".7"/>')
    parts.append(f'<rect width="{w}" height="{h}" fill="url(#mist)"/>')
    svg('mountain', w, h, f'<g filter="url(#paper)">{"".join(parts)}</g>', defs)


# ---------------------------------------------------------------- hills and lake
def draw_hills():
    rng = random.Random(8)
    w, h = 480, 300
    parts = []
    left = ridge(rng, w, 230, [(40, 120, 90), (150, 60, 60)], 3)
    right = ridge(rng, w, 230, [(440, 120, 90), (330, 70, 60)], 3)
    for line, tone in ((left, SAGE[2]), (right, SAGE[2])):
        shape = path(line + [[w, h], [0, h]])
        parts.append(f'<path d="{shape}" fill="{tone}"/>')
        parts.append(hatch(rng, line, 22, SAGE[5], 3, .45))
        parts.append(f'<path d="{path(line, False)}" stroke="{SAGE[5]}" stroke-width=".7" fill="none" opacity=".6"/>')
    lake_top = 214
    parts.append(f'<rect x="0" y="{lake_top}" width="{w}" height="{h - lake_top}" fill="url(#lake)"/>')
    shimmer = ' '.join(f'M{f(rng.uniform(0, w))},{f(rng.uniform(lake_top + 4, h - 4))} h{f(rng.uniform(8, 40))}' for _ in range(90))
    parts.append(f'<path class="shimmer" d="{shimmer}" stroke="#fff" stroke-width="1" opacity=".8"/>')
    parts.append(f'<path d="M0,{lake_top} H{w}" stroke="{SAGE[4]}" stroke-width=".8" opacity=".6"/>')
    # far shore trees
    for x in range(0, w, 7):
        if 120 < x < 360 and rng.random() < .7:
            continue
        hgt = rng.uniform(4, 12)
        parts.append(f'<ellipse cx="{x}" cy="{f(lake_top - hgt / 2)}" rx="{f(hgt * .6)}" ry="{f(hgt / 2)}" fill="{SAGE[3]}" opacity=".9"/>')
    defs = (f'<linearGradient id="lake" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{LAKE[1]}"/>'
            f'<stop offset="1" stop-color="{LAKE[0]}"/></linearGradient>')
    svg('hills', w, h, f'<g filter="url(#paper)">{"".join(parts)}</g>', defs)


# ---------------------------------------------------------------- rumah kebaya
def gigi_row(x0, x1, y, size, fill, stroke, step=None):
    """Gigi balang: a row of downward teeth with rounded tips."""
    step = step or size
    d = []
    x = x0
    while x < x1 - 1:
        d.append(f'M{f(x)},{f(y)} L{f(x + step)},{f(y)} L{f(x + step * .62)},{f(y + size * .7)} '
                 f'A{f(step * .14)},{f(step * .14)} 0 0 1 {f(x + step * .38)},{f(y + size * .7)} Z')
        x += step
    return f'<path d="{" ".join(d)}" fill="{fill}" stroke="{stroke}" stroke-width=".5"/>'


def draw_house():
    rng = random.Random(12)
    w, h = 480, 340
    ground = 272
    p = []
    # grass ground
    p.append(f'<path d="M0,{ground - 6} Q240,{ground - 16} 480,{ground - 6} L480,{h} L0,{h} Z" fill="url(#grass)"/>')
    # banana and shrubs behind the house
    for x, s in ((70, 1), (420, 1.1), (110, .8), (380, .8)):
        p.append(shrub(rng, x, ground - 40, 34 * s))
    # roof (limasan)
    ridge_y, eave_y = 104, 182
    p.append(f'<path d="M150,{ridge_y} L330,{ridge_y} L414,{eave_y} L66,{eave_y} Z" fill="url(#roof)" stroke="#6b4f36" stroke-width=".8"/>')
    tiles = []
    for y in range(ridge_y + 6, eave_y, 6):
        t = (y - ridge_y) / (eave_y - ridge_y)
        xl, xr = 150 - 84 * t, 330 + 84 * t
        tiles.append(f'M{f(xl)},{y} H{f(xr)}')
        off = 3 if (y // 6) % 2 else 0
        for x in range(int(xl) + off, int(xr), 7):
            tiles.append(f'M{x},{y} v-5')
    p.append(f'<path d="{" ".join(tiles)}" stroke="#7a5a3e" stroke-width=".45" opacity=".55"/>')
    p.append(f'<path d="M150,{ridge_y} L66,{eave_y} M330,{ridge_y} L414,{eave_y}" stroke="#5e432c" stroke-width="1.2"/>')
    p.append(f'<rect x="146" y="{ridge_y - 4}" width="188" height="5" rx="2" fill="#8a6748"/>')
    # front awning (topi / markis) with gigi balang trim
    aw_top, aw_bot = 186, 200
    p.append(f'<path d="M84,{aw_top} L396,{aw_top} L404,{aw_bot} L76,{aw_bot} Z" fill="#f3ecdc" stroke="#8b7a60" stroke-width=".6"/>')
    p.append(f'<path d="{" ".join(f"M{x},{aw_top} l-1,{aw_bot - aw_top}" for x in range(88, 396, 5))}" stroke="#c9b48f" stroke-width=".6"/>')
    p.append(gigi_row(76, 404, aw_bot, 8, '#fbf6ea', '#8b7a60', 8))
    p.append(f'<path d="M66,{eave_y} H414" stroke="#5e432c" stroke-width="1.6"/>')
    p.append(gigi_row(66, 414, eave_y + 1, 6, '#e9dcc0', '#7a5a3e', 6))
    # walls with krepyak (vertical lattice)
    wall_top, wall_bot = 208, ground - 4
    p.append(f'<rect x="96" y="{wall_top}" width="288" height="{wall_bot - wall_top}" fill="#efe5cf"/>')
    p.append(f'<path d="{" ".join(f"M{x},{wall_top} V{wall_bot}" for x in range(98, 384, 3))}" stroke="#b99f78" stroke-width=".6" opacity=".7"/>')
    for x in (126, 196, 266, 336):
        p.append(f'<rect x="{x}" y="{wall_top + 10}" width="22" height="30" fill="#5f8a5c" stroke="#3f5f3d" stroke-width=".7"/>')
        p.append(f'<path d="M{x + 11},{wall_top + 10} v30 M{x},{wall_top + 25} h22" stroke="#e9e1c8" stroke-width=".8"/>')
    p.append(f'<rect x="228" y="{wall_top + 4}" width="26" height="{wall_bot - wall_top - 4}" fill="#4e7a4d" stroke="#2f4f2f" stroke-width=".8"/>')
    p.append(f'<path d="M241,{wall_top + 4} V{wall_bot}" stroke="#d8cfaf" stroke-width=".8"/>')
    # porch floor, columns and langkan railing
    p.append(f'<rect x="80" y="{wall_bot}" width="320" height="8" fill="#d9cdb3" stroke="#8b7a60" stroke-width=".6"/>')
    for x in (88, 150, 214, 268, 330, 392):
        p.append(f'<rect x="{x - 3.5}" y="{aw_bot + 6}" width="7" height="{wall_bot - aw_bot - 6}" fill="#fbf8f0" stroke="#9c8c72" stroke-width=".6"/>')
    rail_top = wall_bot - 20
    p.append(f'<path d="M84,{rail_top} H208 M274,{rail_top} H396" stroke="#7e6a50" stroke-width="2"/>')
    bal = ' '.join(f'M{x},{rail_top} V{wall_bot}' for x in list(range(88, 208, 5)) + list(range(276, 396, 5)))
    p.append(f'<path d="{bal}" stroke="#a48d6c" stroke-width="1.2"/>')
    # steps
    for i in range(3):
        p.append(f'<rect x="{220 - i * 6}" y="{wall_bot + 8 + i * 4}" width="{42 + i * 12}" height="4" fill="#e6dcc6" stroke="#9c8c72" stroke-width=".5"/>')
    # potted plants on the porch
    for x in (118, 178, 302, 362):
        p.append(f'<path d="M{x - 6},{wall_bot} l2,-9 h8 l2,9 Z" fill="#c98b5a"/>')
        p.append(f'<circle cx="{x}" cy="{wall_bot - 13}" r="7" fill="{SAGE[3]}"/>')
    # grass blades
    blades = ' '.join(f'M{f(x)},{f(y)} q{f(rng.uniform(-3, 3))},-6 {f(rng.uniform(-4, 4))},-{f(rng.uniform(6, 14))}'
                      for x, y in [(rng.uniform(0, w), rng.uniform(ground, h)) for _ in range(600)])
    p.append(f'<path d="{blades}" stroke="{SAGE[4]}" stroke-width=".7" fill="none" opacity=".6"/>')
    defs = ('<linearGradient id="roof" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#a98a69"/><stop offset="1" stop-color="#c7aa86"/></linearGradient>'
            f'<linearGradient id="grass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SAGE[2]}"/><stop offset="1" stop-color="{SAGE[3]}"/></linearGradient>')
    svg('house', w, h, f'<g filter="url(#paper)">{"".join(p)}</g>', defs)


def shrub(rng, x, y, r):
    out = []
    for _ in range(7):
        a = rng.uniform(0, math.tau)
        out.append(f'<circle cx="{f(x + math.cos(a) * r * .5)}" cy="{f(y + math.sin(a) * r * .35)}" r="{f(r * rng.uniform(.4, .6))}" fill="{SAGE[3]}" stroke="{SAGE[5]}" stroke-width=".4" stroke-opacity=".5"/>')
    return ''.join(out)


# ---------------------------------------------------------------- meadow for the close-up start
def draw_meadow():
    rng = random.Random(15)
    w, h = 480, 260
    p = [f'<rect y="40" width="{w}" height="{h - 40}" fill="url(#g)"/>']
    for layer in range(4):
        blades = []
        for _ in range(500):
            x = rng.uniform(-10, w + 10)
            y = rng.uniform(40 + layer * 40, h)
            ln = rng.uniform(14, 40) * (1 + layer * .3)
            blades.append(f'M{f(x)},{f(y)} q{f(rng.uniform(-6, 6))},-{f(ln * .6)} {f(rng.uniform(-10, 10))},-{f(ln)}')
        p.append(f'<path d="{" ".join(blades)}" stroke="{SAGE[3 + layer % 3]}" stroke-width="{.7 + layer * .2}" fill="none" opacity=".75"/>')
    defs = (f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SAGE[2]}" stop-opacity="0"/>'
            f'<stop offset=".25" stop-color="{SAGE[2]}"/><stop offset="1" stop-color="{SAGE[3]}"/></linearGradient>')
    svg('meadow', w, h, ''.join(p), defs)


# ---------------------------------------------------------------- kembang kelapa
def draw_kembang():
    """Radial burst of ribbon strands; spun by CSS, mounted on a bamboo pole."""
    rng = random.Random(23)
    s, c = 240, 120
    p = []
    for ring, (count, r0, r1, width) in enumerate(((54, 16, 112, 2.6), (40, 12, 84, 3), (28, 8, 54, 3.4))):
        for i in range(count):
            a = i * math.tau / count + ring * .07
            color = RIBBON[(i + ring * 3) % len(RIBBON)]
            bend = rng.uniform(-.12, .12)
            x0, y0 = c + math.cos(a) * r0, c + math.sin(a) * r0
            x1, y1 = c + math.cos(a + bend) * r1, c + math.sin(a + bend) * r1
            mx, my = c + math.cos(a + bend * .4) * (r0 + r1) / 2, c + math.sin(a + bend * .4) * (r0 + r1) / 2
            p.append(f'<path d="M{f(x0)},{f(y0)} Q{f(mx)},{f(my)} {f(x1)},{f(y1)}" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>')
            # paper-cut notches along the strand
            for t in (.35, .55, .75):
                nx, ny = c + math.cos(a + bend * t) * (r0 + (r1 - r0) * t), c + math.sin(a + bend * t) * (r0 + (r1 - r0) * t)
                p.append(f'<circle cx="{f(nx)}" cy="{f(ny)}" r="{f(width * .45)}" fill="#fff" opacity=".7"/>')
            if ring == 0:
                p.append(f'<circle cx="{f(x1)}" cy="{f(y1)}" r="2.6" fill="{RIBBON[(i + 2) % len(RIBBON)]}" stroke="#fff" stroke-width=".6"/>')
    p.append(f'<circle cx="{c}" cy="{c}" r="10" fill="{GOLD[1]}" stroke="{GOLD[2]}"/><circle cx="{c}" cy="{c}" r="4" fill="#e2483d"/>')
    svg('kembang', s, s, ''.join(p))


# ---------------------------------------------------------------- banana tree
def banana_leaf(x, y, ln, ang, wd, color, ink):
    rad = math.radians(ang)
    ex, ey = x + math.cos(rad) * ln, y + math.sin(rad) * ln
    nx, ny = -math.sin(rad), math.cos(rad)
    mx, my = (x + ex) / 2, (y + ey) / 2 + ln * .12
    a = (mx + nx * wd, my + ny * wd)
    b = (mx - nx * wd, my - ny * wd)
    ribs = ' '.join(f'M{f(x + (ex - x) * t)},{f(y + (ey - y) * t + ln * .12 * math.sin(math.pi * t))} l{f(nx * wd * .9)},{f(ny * wd * .9 + 4)}'
                    f' M{f(x + (ex - x) * t)},{f(y + (ey - y) * t + ln * .12 * math.sin(math.pi * t))} l{f(-nx * wd * .9)},{f(-ny * wd * .9 + 4)}'
                    for t in [i / 12 for i in range(1, 12)])
    return (f'<path d="M{f(x)},{f(y)} Q{f(a[0])},{f(a[1])} {f(ex)},{f(ey)} Q{f(b[0])},{f(b[1])} {f(x)},{f(y)} Z" fill="{color}" stroke="{ink}" stroke-width=".6"/>'
            f'<path d="M{f(x)},{f(y)} Q{f(mx)},{f(my)} {f(ex)},{f(ey)}" stroke="{ink}" stroke-width=".9" fill="none"/>'
            f'<path d="{ribs}" stroke="{ink}" stroke-width=".35" opacity=".6"/>')


def draw_banana():
    w, h = 220, 400
    p = ['<path d="M104,400 C100,300 108,230 110,170 L122,170 C120,230 126,300 124,400 Z" fill="#a9b98a" stroke="#5f7448" stroke-width=".7"/>']
    p.append('<path d="M108,380 q6,-4 14,0 M108,330 q6,-4 14,0 M109,280 q6,-4 13,0 M110,230 q6,-4 12,0" stroke="#5f7448" stroke-width=".6" fill="none"/>')
    for ang, ln, wd, col in ((-160, 110, 24, '#b9cfae'), (-20, 110, 24, '#b9cfae'), (-130, 120, 26, '#a5c09c'), (-50, 120, 26, '#a5c09c'),
                             (-100, 120, 22, '#c3d6b8'), (-75, 125, 24, '#9fbb97'), (-175, 90, 20, '#aec6a4'), (-5, 90, 20, '#aec6a4')):
        p.append(banana_leaf(116, 172, ln, ang, wd, col, '#5c7a5a'))
    svg('banana', w, h, f'<g filter="url(#paper)">{"".join(p)}</g>')


# ---------------------------------------------------------------- flowers
def lily(cx, cy, r, rot, pal=PINK):
    out = [f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(rot)})">']
    for i in range(6):
        a = i * 60 + (15 if i % 2 else 0)
        out.append(f'<g transform="rotate({a})"><path d="M0,0 C{f(r * .35)},{f(-r * .3)} {f(r * .22)},{f(-r * .9)} 0,{f(-r)} C{f(-r * .22)},{f(-r * .9)} {f(-r * .35)},{f(-r * .3)} 0,0 Z" fill="url(#lily)" stroke="{pal[4]}" stroke-width=".5"/>'
                   f'<path d="M0,{f(-r * .1)} V{f(-r * .8)}" stroke="{pal[3]}" stroke-width="1.6" opacity=".7"/>'
                   + ''.join(f'<circle cx="{f(s * r * .08)}" cy="{f(-r * t)}" r=".9" fill="{pal[4]}"/>' for t, s in ((.3, 1), (.42, -1), (.5, 1), (.36, -1))) + '</g>')
    for i in range(6):
        a = math.radians(i * 60 + 20)
        out.append(f'<path d="M0,0 L{f(math.cos(a) * r * .5)},{f(math.sin(a) * r * .5)}" stroke="#8fae5c" stroke-width=".8"/>'
                   f'<ellipse cx="{f(math.cos(a) * r * .52)}" cy="{f(math.sin(a) * r * .52)}" rx="2.2" ry="1.2" fill="#a2552f"/>')
    out.append('</g>')
    return ''.join(out)


def calla(x, base, hgt, tilt):
    top = base - hgt
    return (f'<g transform="rotate({f(tilt)} {f(x)} {f(base)})">'
            f'<path d="M{f(x)},{f(base)} Q{f(x + 3)},{f(base - hgt * .5)} {f(x)},{f(top + 18)}" stroke="#6f9a4e" stroke-width="2.4" fill="none"/>'
            f'<path d="M{f(x)},{f(top + 22)} C{f(x - 16)},{f(top + 8)} {f(x - 14)},{f(top - 14)} {f(x + 2)},{f(top - 18)} C{f(x + 22)},{f(top - 16)} {f(x + 18)},{f(top + 4)} {f(x)},{f(top + 22)} Z" fill="url(#calla)" stroke="#a8b39a" stroke-width=".6"/>'
            f'<path d="M{f(x)},{f(top + 16)} q-2,-12 1,-24" stroke="#e9c34a" stroke-width="3" stroke-linecap="round"/></g>')


def hydrangea(rng, cx, cy, r):
    out = []
    for _ in range(int(r * 1.6)):
        a, d = rng.uniform(0, math.tau), r * math.sqrt(rng.random())
        x, y = cx + math.cos(a) * d, cy + math.sin(a) * d * .85
        col = rng.choice(['#9fb6e0', '#b5c4ea', '#8aa3d6', '#c7c3ec', '#a9bde6'])
        rr = rng.uniform(3.6, 5.2)
        out.append(f'<g transform="translate({f(x)},{f(y)}) rotate({f(rng.uniform(0, 90))})">'
                   + ''.join(f'<ellipse cx="0" cy="{f(-rr * .55)}" rx="{f(rr * .45)}" ry="{f(rr * .6)}" transform="rotate({k * 90})" fill="{col}" stroke="#6f86b8" stroke-width=".3"/>' for k in range(4))
                   + '<circle r=".9" fill="#f6efc8"/></g>')
    return ''.join(out)


def lupine(rng, x, base, hgt, col):
    out = [f'<path d="M{f(x)},{f(base)} V{f(base - hgt)}" stroke="#6f9a4e" stroke-width="1.4"/>']
    for i in range(int(hgt / 4)):
        t = i / (hgt / 4)
        y = base - hgt * .25 - (hgt * .75) * t
        rr = 3.4 * (1 - t * .7)
        for s in (-1, 1):
            out.append(f'<ellipse cx="{f(x + s * rr * .8)}" cy="{f(y)}" rx="{f(rr)}" ry="{f(rr * .7)}" fill="{col}" stroke="#5a4e9a" stroke-width=".3"/>')
    return ''.join(out)


def leafy(rng, x, base, hgt, ang, col='#8fb070'):
    rad = math.radians(ang)
    ex, ey = x + math.sin(rad) * hgt, base - math.cos(rad) * hgt
    nx, ny = math.cos(rad), math.sin(rad)
    w = hgt * .16
    return (f'<path d="M{f(x)},{f(base)} Q{f((x + ex) / 2 + nx * w)},{f((base + ey) / 2 + ny * w)} {f(ex)},{f(ey)} Q{f((x + ex) / 2 - nx * w)},{f((base + ey) / 2 - ny * w)} {f(x)},{f(base)} Z" fill="{col}" stroke="#5e7d47" stroke-width=".5"/>'
            f'<path d="M{f(x)},{f(base)} L{f(ex)},{f(ey)}" stroke="#5e7d47" stroke-width=".5"/>')


FLOWER_DEFS = (f'<radialGradient id="lily" cx=".5" cy="1" r="1"><stop offset="0" stop-color="{PINK[3]}"/><stop offset=".55" stop-color="{PINK[2]}"/><stop offset="1" stop-color="{PINK[0]}"/></radialGradient>'
               '<linearGradient id="calla" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#f3f1e4"/><stop offset="1" stop-color="#d8dcc4"/></linearGradient>')


def draw_flowers():
    rng = random.Random(33)
    w, h = 480, 340
    p = []
    for _ in range(70):
        p.append(leafy(rng, rng.uniform(0, w), h + 4, rng.uniform(50, 120), rng.uniform(-35, 35), rng.choice(['#9cbc7c', '#86a866', '#acc790'])))
    for x in (30, 120, 200, 280, 360, 450, 80, 400):
        p.append(lupine(rng, x + rng.uniform(-10, 10), h - 40, rng.uniform(90, 140), rng.choice(['#8f86d6', '#a49ae0', '#7d9be0'])))
    for x, hgt, tilt in ((60, 190, -10), (95, 160, 6), (385, 160, -6), (420, 190, 10), (230, 170, -4), (255, 150, 6)):
        p.append(calla(x, h, hgt, tilt))
    for cx, cy, r in ((150, 300, 34), (330, 300, 34), (10, 310, 36), (470, 310, 36), (240, 330, 30)):
        p.append(hydrangea(rng, cx, cy, r))
    for cx, cy, r, rot in ((40, 260, 34, 10), (440, 260, 34, -10), (180, 270, 30, 30), (300, 270, 30, -30), (110, 315, 32, 0), (370, 315, 32, 0), (240, 285, 28, 12)):
        p.append(lily(cx, cy, r, rot))
    for _ in range(40):
        x, y = rng.uniform(0, w), rng.uniform(280, h)
        p.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rng.uniform(2, 3.5))}" fill="{rng.choice(["#f2c94c", "#f6a96b", "#fff"])}" stroke="#c99a2e" stroke-width=".3"/>')
    svg('flowers', w, h, ''.join(p), FLOWER_DEFS)


def blossom(cx, cy, r, rot, col):
    out = [f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(rot)})">']
    for k in range(5):
        out.append(f'<path transform="rotate({k * 72})" d="M0,0 C{f(r * .5)},{f(-r * .2)} {f(r * .55)},{f(-r * .95)} 0,{f(-r)} C{f(-r * .55)},{f(-r * .95)} {f(-r * .5)},{f(-r * .2)} 0,0 Z" fill="{col}" stroke="{PINK[4]}" stroke-width=".4"/>')
    out.append(f'<circle r="{f(r * .22)}" fill="#f8e1a0"/><circle r="{f(r * .1)}" fill="{PINK[4]}"/></g>')
    return ''.join(out)


def draw_hanging():
    """Pink blossom branch tumbling down from the top-left corner."""
    rng = random.Random(41)
    w, h = 220, 380
    p = ['<path d="M-10,-10 C40,40 70,90 90,160 C105,215 100,270 120,330" stroke="#7a6248" stroke-width="3" fill="none"/>',
         '<path d="M60,70 C100,90 140,90 170,120 M90,170 C60,200 50,240 40,290" stroke="#7a6248" stroke-width="2" fill="none"/>']
    for _ in range(40):
        x, y = rng.uniform(10, 190), rng.uniform(10, 340)
        p.append(leafy(rng, x, y, rng.uniform(18, 30), rng.uniform(-160, 160), rng.choice(['#9cbc7c', '#86a866'])))
    for _ in range(26):
        x, y = rng.uniform(20, 190), rng.uniform(20, 340)
        p.append(blossom(x, y, rng.uniform(8, 13), rng.uniform(0, 72), rng.choice([PINK[1], PINK[2], '#f4a7c0'])))
    for _ in range(8):
        x, y = rng.uniform(30, 180), rng.uniform(60, 330)
        p.append(f'<path d="M{f(x)},{f(y)} c-4,8 -2,14 2,16 c4,-2 6,-8 2,-16 Z" fill="#8ea7de" stroke="#5f77b0" stroke-width=".4"/>')
    svg('hanging', w, h, ''.join(p))


def draw_pinktree():
    rng = random.Random(47)
    w, h = 240, 220
    p = ['<path d="M118,220 C116,180 112,150 120,120 M120,150 C100,130 90,110 80,100 M121,140 C140,120 150,110 162,96" stroke="#7a6248" stroke-width="4" fill="none"/>']
    for _ in range(90):
        a, d = rng.uniform(0, math.tau), rng.uniform(0, 1) ** .6
        x, y = 120 + math.cos(a) * d * 100, 100 + math.sin(a) * d * 62
        p.append(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rng.uniform(5, 11))}" fill="{rng.choice([PINK[1], PINK[2], "#f2a9bb", "#e9879f"])}" opacity=".85"/>')
    dots = ' '.join(f'M{f(120 + math.cos(a) * d * 96)},{f(100 + math.sin(a) * d * 60)} l1.5,1.5' for a, d in [(rng.uniform(0, math.tau), rng.random()) for _ in range(200)])
    p.append(f'<path d="{dots}" stroke="{PINK[4]}" stroke-width=".7" opacity=".5"/>')
    svg('pinktree', w, h, f'<g filter="url(#paper)">{"".join(p)}</g>')


def draw_bouquet():
    rng = random.Random(51)
    p = []
    for _ in range(14):
        p.append(leafy(rng, 90 + rng.uniform(-30, 30), 190, rng.uniform(50, 90), rng.uniform(-70, 70)))
    p.append(calla(60, 190, 130, -18) + calla(128, 190, 120, 16))
    p.append(hydrangea(rng, 120, 150, 26))
    p.append(lily(62, 140, 32, 12) + lily(100, 168, 24, -20))
    svg('bouquet', 180, 190, ''.join(p), FLOWER_DEFS)


def draw_leaves():
    rng = random.Random(57)
    p = []
    for ang in range(-60, 70, 14):
        p.append(banana_leaf(40, 330, rng.uniform(150, 220), ang - 90, 22, rng.choice(['#b9cfae', '#a5c09c', '#c3d6b8']), '#5c7a5a'))
    for _ in range(6):
        p.append(blossom(rng.uniform(40, 180), rng.uniform(80, 300), 10, rng.uniform(0, 72), PINK[2]))
    svg('leaves', 220, 340, ''.join(p))


def draw_frame():
    """Gold oval with a gigi balang crest and pink blossoms."""
    w, h = 300, 400
    cx, cy, rx, ry = 150, 200, 118, 168
    defs = (f'<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD[0]}"/><stop offset=".4" stop-color="{GOLD[2]}"/>'
            f'<stop offset=".6" stop-color="#f8e9bd"/><stop offset="1" stop-color="{GOLD[1]}"/></linearGradient>')
    p = [f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 6}" ry="{ry + 6}" fill="none" stroke="url(#gold)" stroke-width="11"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 15}" ry="{ry + 15}" fill="none" stroke="{SAGE[4]}" stroke-width="2.4" stroke-dasharray="1 6" stroke-linecap="round"/>',
         f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 1}" ry="{ry - 1}" fill="none" stroke="{GOLD[2]}" stroke-width="1.6"/>']
    # crest: a short gigi balang arc on top
    for i in range(-5, 6):
        a = math.radians(-90 + i * 7)
        x, y = cx + math.cos(a) * (rx + 18), cy + math.sin(a) * (ry + 18)
        p.append(f'<path transform="translate({f(x)},{f(y)}) rotate({f(math.degrees(a) + 90)})" d="M-6,0 L6,0 L0,-12 Z" fill="{SAGE[4]}" stroke="{GOLD[2]}" stroke-width=".6"/>'
                 f'<circle transform="translate({f(x)},{f(y)}) rotate({f(math.degrees(a) + 90)})" cy="-13" r="2" fill="{GOLD[1]}"/>')
    for x, y, r, col in ((40, 330, 14, PINK[2]), (62, 352, 11, PINK[1]), (258, 70, 12, PINK[2]), (240, 50, 9, PINK[1])):
        p.append(blossom(x, y, r, x, col))
    svg('frame', w, h, ''.join(p), defs)


def draw_gigi():
    """Repeating gigi balang tile for borders (rendered as SVG, not raster)."""
    tile = ('<svg xmlns="http://www.w3.org/2000/svg" width="36" height="34" viewBox="0 0 36 34">'
            f'<rect width="36" height="9" fill="{SAGE[4]}"/><rect y="9" width="36" height="2" fill="{GOLD[1]}"/>'
            f'<circle cx="9" cy="4.5" r="1.6" fill="{GOLD[0]}"/><circle cx="27" cy="4.5" r="1.6" fill="{GOLD[0]}"/>'
            f'<path d="M0,11 H36 L24,24 A6,6 0 0 1 12,24 Z" fill="{SAGE[4]}"/>'
            f'<path d="M18,14 l3,5 -3,5 -3,-5 Z" fill="{GOLD[0]}"/><circle cx="18" cy="28" r="2.4" fill="{GOLD[1]}"/></svg>')
    (OUT.parent / 'gigi-balang.svg').write_text(tile)


draw_sky()
draw_mountain()
draw_hills()
draw_house()
draw_meadow()
draw_kembang()
draw_banana()
draw_flowers()
draw_hanging()
draw_pinktree()
draw_bouquet()
draw_leaves()
draw_frame()
draw_gigi()
print('svg ->', OUT)
