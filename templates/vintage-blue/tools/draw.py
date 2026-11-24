"""Draw the Vintage Blue illustration layers as SVG.

Run:  python3 templates/vintage-blue/tools/draw.py <out-dir>
Then: node templates/vintage-blue/tools/render.mjs <out-dir>

Every layer is drawn procedurally, so the template ships no third-party artwork.
Replace any rendered .webp in ../assets with a painted version of the same size
and transparency to upgrade the look without touching the code.
"""
import math
import random
import sys
from pathlib import Path

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'svg')
OUT.mkdir(parents=True, exist_ok=True)

BLUE = ['#eef3f8', '#d5e0ec', '#bccbde', '#a3b8d2', '#8aa3c3', '#6f8bb0', '#57739a', '#425d82']
GOLD = {'light': '#ecd398', 'mid': '#cfa957', 'deep': '#9f7b33', 'ink': '#7a5a22'}
CREAM = {'light': '#fffaf0', 'mid': '#f4e6c4', 'deep': '#dcc28a', 'ink': '#b39457'}


def f(n):
    return f'{n:.1f}'.rstrip('0').rstrip('.')


def path(points, close=True):
    d = 'M' + ' L'.join(f'{f(x)},{f(y)}' for x, y in points)
    return d + (' Z' if close else '')


def smooth(points, close=False):
    """Catmull-Rom spline through points as cubic Beziers."""
    if len(points) < 3:
        return path(points, close)
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
        f'<defs>{defs}</defs>{body}</svg>'
    )


def ridge(rng, w, base, amp, peaks, step=4):
    """A mountain ridge: a few given peaks blended with fractal roughness."""
    ys = []
    for i in range(0, w + step, step):
        y = base
        for px, ph, pw in peaks:
            y -= ph * math.exp(-((i - px) / pw) ** 2)
        ys.append([i, y])
    for octave, scale in ((24, 1), (9, .45), (4, .22)):
        phase = rng.random() * 100
        for p in ys:
            p[1] += amp * scale * (math.sin(p[0] / octave + phase) + .6 * math.sin(p[0] / (octave * .53) + phase * 1.7))
    return ys


def engraving(rng, line, depth, color, density=2.4, opacity=.55, width=.55):
    """Short hatch strokes hanging from a ridge line, like a copper-plate print."""
    out = []
    for i in range(1, len(line) - 1):
        x, y = line[i]
        slope = (line[i + 1][1] - line[i - 1][1]) / (line[i + 1][0] - line[i - 1][0])
        for _ in range(int(density)):
            xx = x + rng.uniform(-2, 2)
            start = y + rng.uniform(1, 6)
            length = rng.uniform(depth * .25, depth)
            lean = slope * length * .8
            out.append(f'M{f(xx)},{f(start)} q{f(lean * .3)},{f(length * .5)} {f(lean)},{f(length)}')
    return f'<path d="{" ".join(out)}" stroke="{color}" stroke-width="{width}" fill="none" opacity="{opacity}" stroke-linecap="round"/>'


TEXTURE = (
    '<filter id="paper" x="-5%" y="-5%" width="110%" height="110%">'
    '<feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="n"/>'
    '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -.9 .62" result="grain"/>'
    '<feComposite in="SourceGraphic" in2="grain" operator="in" result="g"/>'
    '<feBlend in="SourceGraphic" in2="g" mode="multiply"/>'
    '</filter>'
)

# ---------------------------------------------------------------- sky
def draw_sky():
    w, h = 480, 900
    defs = (
        '<linearGradient id="s" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#f4f6f9"/><stop offset=".55" stop-color="#e8edf3"/><stop offset="1" stop-color="#dbe4ee"/></linearGradient>'
        '<filter id="cloud" x="-30%" y="-30%" width="160%" height="160%">'
        '<feTurbulence type="fractalNoise" baseFrequency=".012 .03" numOctaves="4" seed="7"/>'
        '<feColorMatrix type="matrix" values="0 0 0 0 .72  0 0 0 0 .77  0 0 0 0 .84  0 0 0 1.6 -.72"/>'
        '<feGaussianBlur stdDeviation="2"/></filter>'
        '<filter id="streak"><feTurbulence type="fractalNoise" baseFrequency=".004 .08" numOctaves="2" seed="11"/>'
        '<feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 2 -1"/></filter>'
        + TEXTURE
    )
    body = (
        f'<rect width="{w}" height="{h}" fill="url(#s)"/>'
        f'<rect width="{w}" height="{h * .7}" filter="url(#cloud)" opacity=".75"/>'
        f'<rect width="{w}" height="{h * .7}" filter="url(#streak)" opacity=".5"/>'
        f'<rect width="{w}" height="{h}" fill="#fff" opacity=".001" filter="url(#paper)"/>'
    )
    svg('sky', w, h, body, defs)


# ---------------------------------------------------------------- mountains
def mountain_layer(name, seed, base, amp, peaks, fill_top, fill_bottom, ink, castle=False, ridges=3):
    rng = random.Random(seed)
    w, h = 480, 460
    line = ridge(rng, w, base, amp, peaks)
    shape = path(line + [[w, h], [0, h]])
    defs = (
        f'<linearGradient id="g{name}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{fill_top}"/><stop offset=".7" stop-color="{fill_bottom}"/>'
        f'<stop offset="1" stop-color="{fill_bottom}" stop-opacity=".0"/></linearGradient>'
        f'<linearGradient id="m{name}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset=".45" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#eef3f8" stop-opacity=".95"/></linearGradient>'
        f'<clipPath id="c{name}"><path d="{shape}"/></clipPath>' + TEXTURE
    )
    parts = [f'<path d="{shape}" fill="url(#g{name})"/>']
    hatch = [engraving(rng, line, 34, ink, 3.4, .6)]
    # Secondary ridges inside the mass give the folded-valley look.
    for k in range(ridges):
        sub_base = base + 40 + k * 46
        sub = ridge(rng, w, sub_base, amp * .7, [(rng.uniform(40, 440), rng.uniform(30, 80), rng.uniform(40, 90)) for _ in range(3)])
        hatch.append(f'<path d="{path(sub + [[w, h], [0, h]])}" fill="{fill_top}" opacity=".35"/>')
        hatch.append(f'<path d="{path(sub, False)}" stroke="{ink}" stroke-width=".7" fill="none" opacity=".45"/>')
        hatch.append(engraving(rng, sub, 18, ink, 1.6, .38, .5))
    parts.append(f'<g clip-path="url(#c{name})">{"".join(hatch)}</g>')
    parts.append(f'<path d="{path(line, False)}" stroke="{ink}" stroke-width=".9" fill="none" opacity=".7"/>')
    if castle:
        parts.append(hill_fort(rng, 360, ridge_y(line, 360) + 6, ink, fill_top))
    parts.append(f'<rect width="{w}" height="{h}" fill="url(#m{name})"/>')
    svg(name, w, h, f'<g filter="url(#paper)">{"".join(parts)}</g>', defs)


def ridge_y(line, x):
    return min(line, key=lambda p: abs(p[0] - x))[1]


def hill_fort(rng, x, y, ink, fill):
    """A small walled palace sitting on the ridge, drawn in line work."""
    g = [f'<g transform="translate({x},{y})" stroke="{ink}" stroke-width=".6" fill="#e9eef5">']
    g.append('<path d="M-38,0 L-38,-18 L-20,-18 L-20,-26 L4,-26 L4,-18 L34,-18 L34,0 Z"/>')
    for wx in range(-34, 32, 6):
        g.append(f'<rect x="{wx}" y="-14" width="2.4" height="5" fill="{ink}" opacity=".6"/>')
    for wx in range(-16, 2, 5):
        g.append(f'<rect x="{wx}" y="-23" width="2" height="4" fill="{ink}" opacity=".6"/>')
    g.append('<path d="M-38,-18 l0,-3 l3,0 l0,2 l3,0 l0,-2 l3,0 l0,2 l3,0 l0,-2 l3,0 l0,3" fill="none"/>')
    g.append('</g>')
    return ''.join(g)


def draw_mountains():
    mountain_layer('mountains-far', 3, 190, 4, [(150, 120, 70), (250, 70, 60), (60, 60, 60), (400, 50, 90)],
                   '#dbe4ef', '#c9d6e6', BLUE[5], ridges=2)
    mountain_layer('mountains-near', 8, 250, 5, [(340, 110, 60), (430, 80, 50), (90, 50, 80), (200, 30, 60)],
                   '#c6d4e5', '#aebfd6', BLUE[6], castle=True, ridges=3)


# ---------------------------------------------------------------- forest
def canopy(rng, cx, cy, r, fill, ink, light):
    blobs = []
    for _ in range(rng.randint(6, 10)):
        a = rng.uniform(0, math.tau)
        d = rng.uniform(0, r * .55)
        blobs.append((cx + math.cos(a) * d, cy + math.sin(a) * d * .8 - r * .1, r * rng.uniform(.38, .6)))
    out = [f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(rr)}" fill="{fill}" stroke="{ink}" stroke-width=".45" stroke-opacity=".55"/>' for x, y, rr in blobs]
    marks, shade = [], []
    for x, y, rr in blobs:
        for _ in range(int(rr * 1.2)):
            a = rng.uniform(math.pi * 1.05, math.pi * 1.95)
            px, py = x + math.cos(a) * rr * rng.uniform(.3, .9), y + math.sin(a) * rr * rng.uniform(.3, .9)
            marks.append(f'M{f(px)},{f(py)} q1.2,-1.4 2.4,0')
        for _ in range(int(rr * .8)):
            a = rng.uniform(0, math.pi)
            px, py = x + math.cos(a) * rr * rng.uniform(.2, .95), y + math.sin(a) * rr * rng.uniform(.2, .95)
            shade.append(f'M{f(px)},{f(py)} l1.6,1.6')
    out.append(f'<path d="{" ".join(marks)}" stroke="{light}" stroke-width=".7" fill="none" opacity=".85"/>')
    out.append(f'<path d="{" ".join(shade)}" stroke="{ink}" stroke-width=".5" fill="none" opacity=".45"/>')
    return ''.join(out)


def cypress(rng, x, base, hgt, fill, ink, light):
    w = hgt * .16
    d = f'M{f(x)},{f(base - hgt)} C{f(x + w)},{f(base - hgt * .7)} {f(x + w * 1.1)},{f(base - hgt * .2)} {f(x + w * .4)},{f(base)} L{f(x - w * .4)},{f(base)} C{f(x - w * 1.1)},{f(base - hgt * .2)} {f(x - w)},{f(base - hgt * .7)} {f(x)},{f(base - hgt)} Z'
    marks = ' '.join(f'M{f(x - w * .5 + rng.uniform(0, w))},{f(base - hgt * t)} l2,-2' for t in [rng.uniform(.1, .9) for _ in range(int(hgt / 4))])
    return f'<path d="{d}" fill="{fill}" stroke="{ink}" stroke-width=".5"/><path d="{marks}" stroke="{light}" stroke-width=".7"/>'


def tall_tree(rng, x, base, hgt, fill, ink, light):
    trunk = f'<path d="M{f(x - 2)},{f(base)} C{f(x - 1)},{f(base - hgt * .5)} {f(x + 2)},{f(base - hgt * .7)} {f(x)},{f(base - hgt * .85)} L{f(x + 1.5)},{f(base - hgt * .85)} C{f(x + 3)},{f(base - hgt * .6)} {f(x + 2)},{f(base - hgt * .4)} {f(x + 3)},{f(base)} Z" fill="{ink}" opacity=".7"/>'
    crowns = ''.join(canopy(rng, x + rng.uniform(-14, 14), base - hgt * t, hgt * .13, fill, ink, light) for t in (.62, .78, .92))
    return trunk + crowns


def draw_forest():
    rng = random.Random(21)
    w, h = 480, 500
    rows = [
        (170, BLUE[2], BLUE[5], BLUE[0], 16, 26),
        (230, BLUE[3], BLUE[6], BLUE[1], 20, 32),
        (300, BLUE[3], BLUE[6], BLUE[1], 24, 38),
        (370, BLUE[4], BLUE[7], BLUE[2], 28, 44),
        (440, BLUE[4], BLUE[7], BLUE[2], 32, 50),
    ]
    parts = []
    for y0, fill, ink, light, rmin, rmax in rows:
        parts.append(f'<rect x="0" y="{y0}" width="{w}" height="{h - y0}" fill="{fill}"/>')
        x = -20
        while x < w + 20:
            r = rng.uniform(rmin, rmax)
            kind = rng.random()
            if kind < .14:
                parts.append(cypress(rng, x, y0 + r * .4, r * 3.4, fill, ink, light))
            elif kind < .22:
                parts.append(tall_tree(rng, x, y0 + r * .3, r * 5.5, fill, ink, light))
            else:
                parts.append(canopy(rng, x, y0 - r * .25 + rng.uniform(-8, 8), r, fill, ink, light))
            x += r * rng.uniform(.9, 1.4)
    # A couple of white cottages tucked into the trees, as in toile prints.
    for cx, cy in ((70, 360), (210, 290)):
        parts.append(f'<g transform="translate({cx},{cy})" stroke="{BLUE[6]}" stroke-width=".6"><path d="M-14,0 L-14,-12 L0,-22 L14,-12 L14,0 Z" fill="#f4f7fa"/><path d="M-17,-11 L0,-24 L17,-11" fill="none"/><rect x="-4" y="-8" width="4" height="8" fill="{BLUE[4]}"/><rect x="6" y="-9" width="4" height="4" fill="{BLUE[4]}"/></g>')
    defs = ('<linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".25" stop-color="#fff" stop-opacity="1"/></linearGradient>'
            '<mask id="top"><rect width="480" height="500" fill="url(#fade)"/></mask>' + TEXTURE)
    svg('forest', w, h, f'<g mask="url(#top)" filter="url(#paper)">{"".join(parts)}</g>', defs)


# ---------------------------------------------------------------- flowers
def petal_path(h, w, scallop=0):
    s = scallop
    return (f'M{f(-w * .35)},0 C{f(-w * 1.15)},{f(-h * .45)} {f(-w * .95)},{f(-h * 1.02)} {f(-w * .35)},{f(-h * .98 + s)} '
            f'Q0,{f(-h * 1.08)} {f(w * .35)},{f(-h * .98 + s)} C{f(w * .95)},{f(-h * 1.02)} {f(w * 1.15)},{f(-h * .45)} {f(w * .35)},0 Z')


def peony(rng, cx, cy, r, tone, uid, tilt=0):
    """Cream or blue cupped flower built from rings of scalloped petals."""
    pal = {'cream': (CREAM['light'], CREAM['mid'], CREAM['deep'], CREAM['ink']),
           'gold': ('#fbefcf', '#efd593', '#cfa957', '#9f7b33'),
           'blue': ('#e6eef8', '#9fb6d6', '#5f7fae', '#3d5b88')}[tone]
    defs = (f'<radialGradient id="p{uid}" cx=".5" cy="1" r="1.1"><stop offset="0" stop-color="{pal[2]}"/>'
            f'<stop offset=".55" stop-color="{pal[1]}"/><stop offset="1" stop-color="{pal[0]}"/></radialGradient>')
    out = [f'<g transform="translate({f(cx)},{f(cy)}) rotate({f(tilt)}) scale(1,.86)">']
    rings = [(10, 1.0), (9, .82), (8, .64), (7, .46), (6, .3)]
    for k, (n, scale) in enumerate(rings):
        off = rng.uniform(0, 360)
        for i in range(n):
            a = off + i * 360 / n + rng.uniform(-8, 8)
            h = r * scale * rng.uniform(.92, 1.06)
            out.append(f'<path transform="rotate({f(a)})" d="{petal_path(h, h * .62, rng.uniform(-2, 3))}" fill="url(#p{uid})" stroke="{pal[3]}" stroke-width=".6" stroke-opacity=".7"/>')
            out.append(f'<path transform="rotate({f(a)})" d="M0,{f(-h * .2)} Q{f(h * .06)},{f(-h * .6)} 0,{f(-h * .9)}" stroke="{pal[3]}" stroke-width=".4" opacity=".35" fill="none"/>')
    out.append(f'<circle r="{f(r * .12)}" fill="{pal[2]}"/>')
    for i in range(14):
        a = i * math.tau / 14
        out.append(f'<circle cx="{f(math.cos(a) * r * .12)}" cy="{f(math.sin(a) * r * .12)}" r="{f(r * .03)}" fill="{GOLD["deep"]}"/>')
    out.append('</g>')
    return defs, ''.join(out)


def rose(rng, cx, cy, r, uid):
    """Blue cabbage rose: spiralling petals with a tight centre."""
    defs = (f'<radialGradient id="r{uid}" cx=".5" cy=".9" r="1"><stop offset="0" stop-color="#3d5b88"/>'
            f'<stop offset=".6" stop-color="#6f8fbf"/><stop offset="1" stop-color="#c9d8ee"/></radialGradient>')
    out = [f'<g transform="translate({f(cx)},{f(cy)}) scale(1,.9)">']
    for k in range(7):
        n = 7 - k // 2
        scale = 1 - k * .13
        off = rng.uniform(0, 360)
        for i in range(n):
            a = off + i * 360 / n
            h = r * scale
            out.append(f'<path transform="rotate({f(a)})" d="{petal_path(h, h * .85, 4)}" fill="url(#r{uid})" stroke="#2f4a73" stroke-width=".6" stroke-opacity=".6"/>')
    spiral = ' '.join(f'{f(math.cos(t) * r * .04 * t)},{f(math.sin(t) * r * .04 * t)}' for t in [i * .35 for i in range(1, 22)])
    out.append(f'<polyline points="{spiral}" fill="none" stroke="#2f4a73" stroke-width="1" opacity=".7"/>')
    out.append('</g>')
    return defs, ''.join(out)


def leaf(rng, x, y, length, angle, uid, tone='gold', width=.2):
    """Serrated acanthus-like leaf, base at (x, y), pointing along angle."""
    pal = {'gold': (GOLD['light'], GOLD['mid'], GOLD['deep'], GOLD['ink']),
           'blue': ('#c9d8ee', '#8aa6cf', '#5675a6', '#36527d')}[tone]
    w = length * width
    left, right = [], []
    teeth = 7
    for i in range(teeth * 2 + 1):
        t = i / (teeth * 2)
        bulge = math.sin(math.pi * t ** .7) * w * (1 - t * .35)
        tooth = (1.0 if i % 2 else .62)
        left.append((-bulge * tooth, -length * t))
        right.append((bulge * tooth, -length * t))
    outline = smooth(left + right[::-1][1:], True)
    veins = ' '.join(f'M0,{f(-length * t)} L{f(s * math.sin(math.pi * t ** .8) * w * .8)},{f(-length * (t + .08))}'
                     for t in [i / 8 for i in range(1, 8)] for s in (-1, 1))
    defs = (f'<linearGradient id="l{uid}" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{pal[2]}"/>'
            f'<stop offset=".5" stop-color="{pal[1]}"/><stop offset="1" stop-color="{pal[0]}"/></linearGradient>')
    body = (f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)})">'
            f'<path d="{outline}" fill="url(#l{uid})" stroke="{pal[3]}" stroke-width=".6"/>'
            f'<path d="M0,0 Q{f(w * .1)},{f(-length * .5)} 0,{f(-length * .96)}" stroke="{pal[3]}" stroke-width=".9" fill="none"/>'
            f'<path d="{veins}" stroke="{pal[3]}" stroke-width=".45" fill="none" opacity=".7"/></g>')
    return defs, body


def sprig(rng, x, y, length, angle, color='#5f7fae'):
    """Small delphinium-like stem of five-petal florets."""
    out = [f'<g transform="translate({f(x)},{f(y)}) rotate({f(angle)})">',
           f'<path d="M0,0 Q4,{f(-length * .5)} 0,{f(-length)}" stroke="#4d6a96" stroke-width="1.1" fill="none"/>']
    for i in range(7):
        t = .3 + i * .1
        fx, fy = (rng.uniform(-6, 6), -length * t)
        rr = 4.5 - i * .4
        for k in range(5):
            a = k * math.tau / 5
            out.append(f'<circle cx="{f(fx + math.cos(a) * rr * .7)}" cy="{f(fy + math.sin(a) * rr * .7)}" r="{f(rr * .55)}" fill="{color}" stroke="#2f4a73" stroke-width=".3"/>')
        out.append(f'<circle cx="{f(fx)}" cy="{f(fy)}" r="1" fill="#f4e6c4"/>')
    out.append('</g>')
    return ''.join(out)


def bush(rng, x, y, r, fill='#9fb4d2', ink='#56739c'):
    return canopy(rng, x, y, r, fill, ink, '#dfe8f3')


class Bouquet:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.defs, self.body, self.n = [], [], 0

    def add(self, drawn):
        d, b = drawn
        self.defs.append(d)
        self.body.append(b)

    def uid(self):
        self.n += 1
        return self.n

    def peony(self, *a, **k):
        self.add(peony(self.rng, *a, uid=self.uid(), **k))

    def rose(self, *a):
        self.add(rose(self.rng, *a, uid=self.uid()))

    def leaf(self, *a, **k):
        self.add(leaf(self.rng, *a, uid=self.uid(), **k))

    def raw(self, s):
        self.body.append(s)


def draw_flower_border():
    """Bottom border used on the cover, hero, cards and closing."""
    b = Bouquet(31)
    rng = b.rng
    w, h = 480, 340
    for x in range(-20, 520, 34):
        b.raw(bush(rng, x, 250 + rng.uniform(-30, 10), rng.uniform(26, 38)))
    for x, y, a in ((30, 210, -30), (90, 190, -10), (150, 230, 20), (330, 230, -20), (390, 190, 10), (450, 210, 30), (240, 240, 0), (200, 250, -40), (280, 250, 40)):
        b.raw(sprig(rng, x, 330, 150 + rng.uniform(0, 50), a * 1.2))
    for x, y, ln, a in ((10, 280, 110, -55), (60, 260, 120, -25), (120, 290, 100, 15), (170, 300, 120, -10), (230, 290, 110, 20),
                        (300, 300, 120, 10), (360, 290, 100, -15), (420, 260, 120, 25), (470, 280, 110, 55), (250, 320, 130, -5),
                        (80, 300, 130, -40), (400, 300, 130, 40), (200, 320, 120, -30), (280, 320, 120, 30), (0, 250, 120, -70), (480, 250, 120, 70)):
        b.leaf(x, y + 30, ln * 1.6, a * 1.15)
    b.peony(36, 228, 70, 'cream', tilt=-8)
    b.peony(444, 228, 70, 'cream', tilt=8)
    b.peony(240, 262, 58, 'cream')
    b.peony(120, 200, 38, 'gold', tilt=-14)
    b.peony(360, 200, 38, 'gold', tilt=14)
    b.rose(130, 300, 46)
    b.rose(350, 300, 46)
    b.rose(18, 330, 40)
    b.rose(462, 330, 40)
    b.rose(240, 340, 36)
    b.peony(190, 316, 30, 'cream')
    b.peony(290, 316, 30, 'cream')
    svg('flowers', w, h, ''.join(b.body), ''.join(b.defs))


def draw_corner_bouquet():
    """Cluster hugging the oval portrait frame's lower edge."""
    b = Bouquet(41)
    rng = b.rng
    for x, y, ln, a in ((40, 170, 90, -70), (60, 170, 80, -30), (110, 175, 80, 40), (140, 170, 70, 80), (90, 180, 70, 5)):
        b.leaf(x, y, ln, a)
    b.raw(sprig(rng, 30, 175, 70, -45))
    b.raw(sprig(rng, 150, 175, 60, 50))
    b.peony(60, 120, 42, 'cream', tilt=-10)
    b.rose(112, 140, 34)
    b.peony(124, 96, 22, 'gold')
    svg('bouquet', 180, 190, ''.join(b.body), ''.join(b.defs))


def draw_leaf_spray():
    """Faded gold foliage used at the edges of story and gift cards."""
    b = Bouquet(51)
    rng = b.rng
    for i in range(11):
        b.leaf(40 + rng.uniform(-10, 10), 330, 140 + rng.uniform(-40, 40), -60 + i * 11 + rng.uniform(-4, 4),
               tone='gold' if i % 3 else 'blue', width=.3)
    svg('leaves', 220, 340, ''.join(b.body), ''.join(b.defs))


# ---------------------------------------------------------------- palm
def palm(rng, x, base, hgt, lean):
    top = (x + lean, base - hgt)
    trunk_pts = [(x + lean * t ** 1.6, base - hgt * t) for t in [i / 12 for i in range(13)]]
    left = [(px - 7 * (1 - i / 14) - 2, py) for i, (px, py) in enumerate(trunk_pts)]
    right = [(px + 7 * (1 - i / 14) + 2, py) for i, (px, py) in enumerate(trunk_pts)]
    out = [f'<path d="{smooth(left + right[::-1], True)}" fill="url(#trunk)" stroke="{GOLD["ink"]}" stroke-width=".7"/>']
    rings = []
    for i in range(1, 40):
        t = i / 40
        px, py = x + lean * t ** 1.6, base - hgt * t
        hw = 7 * (1 - t * .85) + 2
        rings.append(f'M{f(px - hw)},{f(py)} q{f(hw)},{f(3)} {f(hw * 2)},0')
    out.append(f'<path d="{" ".join(rings)}" stroke="{GOLD["ink"]}" stroke-width=".6" fill="none" opacity=".75"/>')
    fronds = []
    for k in range(11):
        ang = -170 + k * 17 + rng.uniform(-6, 6)
        a = math.radians(ang)
        ln = rng.uniform(80, 120) * (hgt / 330)
        droop = ln * (.55 if abs(ang + 90) > 40 else .2)
        end = (top[0] + math.cos(a) * ln, top[1] + math.sin(a) * ln * .7 + droop)
        ctrl = (top[0] + math.cos(a) * ln * .55, top[1] + math.sin(a) * ln * .75 - ln * .12)
        fronds.append(f'<path d="M{f(top[0])},{f(top[1])} Q{f(ctrl[0])},{f(ctrl[1])} {f(end[0])},{f(end[1])}" stroke="{GOLD["deep"]}" stroke-width="1.4" fill="none"/>')
        leaflets = []
        for j in range(1, 22):
            t = j / 22
            px = (1 - t) ** 2 * top[0] + 2 * (1 - t) * t * ctrl[0] + t * t * end[0]
            py = (1 - t) ** 2 * top[1] + 2 * (1 - t) * t * ctrl[1] + t * t * end[1]
            dx = 2 * (1 - t) * (ctrl[0] - top[0]) + 2 * t * (end[0] - ctrl[0])
            dy = 2 * (1 - t) * (ctrl[1] - top[1]) + 2 * t * (end[1] - ctrl[1])
            norm = math.hypot(dx, dy) or 1
            nx, ny = -dy / norm, dx / norm
            size = (1 - t * .7) * ln * .32
            for s in (-1, 1):
                ex = px + nx * size * s + dx / norm * size * .5
                ey = py + ny * size * s + dy / norm * size * .5 + size * .45
                leaflets.append(f'M{f(px)},{f(py)} Q{f((px + ex) / 2 + nx * 2 * s)},{f((py + ey) / 2)} {f(ex)},{f(ey)}')
        fronds.append(f'<path d="{" ".join(leaflets)}" stroke="url(#frond)" stroke-width="2" fill="none" stroke-linecap="round"/>')
        fronds.append(f'<path d="{" ".join(leaflets)}" stroke="{GOLD["ink"]}" stroke-width=".35" fill="none" opacity=".6"/>')
    out.extend(fronds)
    return ''.join(out)


def draw_palm():
    rng = random.Random(61)
    w, h = 260, 560
    defs = (f'<linearGradient id="trunk" x1="0" x2="1"><stop offset="0" stop-color="{GOLD["deep"]}"/><stop offset=".5" stop-color="{GOLD["light"]}"/><stop offset="1" stop-color="{GOLD["mid"]}"/></linearGradient>'
            f'<linearGradient id="frond" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD["light"]}"/><stop offset="1" stop-color="{GOLD["mid"]}"/></linearGradient>')
    body = palm(rng, 150, 560, 300, -30) + palm(rng, 70, 560, 420, 40)
    svg('palm', w, h, body, defs)


# ---------------------------------------------------------------- castle
def draw_castle():
    rng = random.Random(71)
    w, h = 320, 240
    ink = '#4b6690'
    defs = (
        '<linearGradient id="wall" x1="0" x2="1"><stop offset="0" stop-color="#a9bcd8"/><stop offset=".5" stop-color="#e3eaf4"/><stop offset="1" stop-color="#8ea6c8"/></linearGradient>'
        '<linearGradient id="roof" x1="0" x2="1"><stop offset="0" stop-color="#5a78a6"/><stop offset=".45" stop-color="#9db3d6"/><stop offset="1" stop-color="#46638f"/></linearGradient>'
        '<filter id="wash" x="-10%" y="-10%" width="120%" height="120%"><feTurbulence type="fractalNoise" baseFrequency=".04" numOctaves="3" seed="3"/>'
        '<feDisplacementMap in="SourceGraphic" scale="3"/></filter>'
        '<filter id="mist" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="7"/></filter>'
    )
    parts = []

    def tower(cx, base, tw, th, roof_h):
        top = base - th
        parts.append(f'<rect x="{f(cx - tw / 2)}" y="{f(top)}" width="{f(tw)}" height="{f(th)}" fill="url(#wall)" stroke="{ink}" stroke-width=".6"/>')
        parts.append(f'<path d="M{f(cx - tw / 2 - 3)},{f(top)} Q{f(cx - tw * .2)},{f(top - roof_h * .4)} {f(cx)},{f(top - roof_h)} Q{f(cx + tw * .2)},{f(top - roof_h * .4)} {f(cx + tw / 2 + 3)},{f(top)} Z" fill="url(#roof)" stroke="{ink}" stroke-width=".6"/>')
        parts.append(f'<line x1="{f(cx)}" y1="{f(top - roof_h)}" x2="{f(cx)}" y2="{f(top - roof_h - 8)}" stroke="{ink}" stroke-width=".8"/>')
        for wy in range(int(top + 8), int(base - 6), 14):
            parts.append(f'<path d="M{f(cx - 1.6)},{wy + 5} v-3 a1.6,1.6 0 0 1 3.2,0 v3 Z" fill="{ink}" opacity=".75"/>')

    parts.append(f'<path d="M30,200 Q160,150 290,200 L290,240 L30,240 Z" fill="#b8c9e0" filter="url(#wash)"/>')
    parts.append(f'<rect x="96" y="128" width="128" height="72" fill="url(#wall)" stroke="{ink}" stroke-width=".6"/>')
    for x in range(96, 224, 8):
        parts.append(f'<rect x="{x}" y="123" width="5" height="6" fill="url(#wall)" stroke="{ink}" stroke-width=".4"/>')
    parts.append(f'<path d="M150,200 v-22 a10,10 0 0 1 20,0 v22 Z" fill="{ink}" opacity=".8"/>')
    for x, base, tw, th, rh in ((82, 205, 20, 92, 40), (238, 205, 20, 92, 40), (120, 160, 18, 70, 36), (200, 160, 18, 70, 36),
                                (160, 140, 28, 70, 62), (60, 210, 14, 54, 26), (260, 210, 14, 54, 26), (140, 130, 12, 40, 24), (180, 130, 12, 40, 24)):
        tower(x, base, tw, th, rh)
    clouds = ''.join(f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(rx * .45)}" fill="#fff"/>'
                     for cx, cy, rx in [(rng.uniform(10, 310), rng.uniform(195, 235), rng.uniform(30, 60)) for _ in range(12)])
    body = (f'<g filter="url(#wash)">{"".join(parts)}</g><g filter="url(#mist)" opacity=".95">{clouds}</g>'
            f'<g filter="url(#mist)" opacity=".7"><ellipse cx="40" cy="150" rx="40" ry="14" fill="#fff"/><ellipse cx="290" cy="120" rx="36" ry="12" fill="#fff"/></g>')
    svg('castle', w, h, body, defs)


# ---------------------------------------------------------------- oval frame
def draw_frame():
    """Ornate gold oval; the portrait sits in the transparent window."""
    w, h = 300, 400
    cx, cy, rx, ry = 150, 200, 118, 168
    defs = (f'<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{GOLD["light"]}"/>'
            f'<stop offset=".35" stop-color="{GOLD["deep"]}"/><stop offset=".55" stop-color="#f6e3a8"/>'
            f'<stop offset=".8" stop-color="{GOLD["mid"]}"/><stop offset="1" stop-color="{GOLD["deep"]}"/></linearGradient>'
            '<filter id="bevel"><feGaussianBlur in="SourceAlpha" stdDeviation="1.5" result="b"/>'
            '<feSpecularLighting in="b" surfaceScale="3" specularConstant=".9" specularExponent="18" lighting-color="#fff8e0" result="s">'
            '<feDistantLight azimuth="235" elevation="45"/></feSpecularLighting>'
            '<feComposite in="s" in2="SourceAlpha" operator="in" result="s2"/>'
            '<feComposite in="SourceGraphic" in2="s2" operator="arithmetic" k2="1" k3=".8"/>'
            '<feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#6b5320" flood-opacity=".35"/></filter>')
    beads = ''.join(f'<circle cx="{f(cx + math.cos(t) * (rx + 13))}" cy="{f(cy + math.sin(t) * (ry + 13))}" r="2.6" fill="url(#gold)"/>'
                    for t in [i * math.tau / 64 for i in range(64)])
    scroll = lambda x, y, s, r: (f'<g transform="translate({x},{y}) rotate({r}) scale({s})"><path d="M0,0 C-10,-14 -30,-10 -28,6 C-26,18 -10,16 -12,6 C-13,0 -20,0 -20,5" '
                                 f'fill="none" stroke="url(#gold)" stroke-width="5" stroke-linecap="round"/>'
                                 f'<path d="M0,0 C10,-14 30,-10 28,6 C26,18 10,16 12,6 C13,0 20,0 20,5" fill="none" stroke="url(#gold)" stroke-width="5" stroke-linecap="round"/></g>')
    shell = (f'<path d="M{cx - 22},{cy - ry - 8} Q{cx},{cy - ry - 52} {cx + 22},{cy - ry - 8} Q{cx},{cy - ry - 22} {cx - 22},{cy - ry - 8} Z" fill="url(#gold)"/>'
             + ''.join(f'<path d="M{cx},{cy - ry - 12} L{f(cx + math.cos(a) * 26)},{f(cy - ry - 12 + math.sin(a) * 30)}" stroke="{GOLD["ink"]}" stroke-width=".8"/>'
                       for a in [math.radians(-160 + i * 20) for i in range(8)]))
    body = (f'<g filter="url(#bevel)">'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx + 6}" ry="{ry + 6}" fill="none" stroke="url(#gold)" stroke-width="13"/>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx - 2}" ry="{ry - 2}" fill="none" stroke="{GOLD["deep"]}" stroke-width="2"/>'
            f'{beads}{shell}{scroll(cx, cy + ry + 14, 1, 0)}{scroll(cx - rx - 12, cy, .8, -90)}{scroll(cx + rx + 12, cy, .8, 90)}'
            f'{scroll(cx, cy - ry - 4, .7, 180)}</g>')
    svg('frame', w, h, body, defs)


draw_sky()
draw_mountains()
draw_forest()
draw_flower_border()
draw_corner_bouquet()
draw_leaf_spray()
draw_palm()
draw_castle()
draw_frame()
print('svg ->', OUT)
