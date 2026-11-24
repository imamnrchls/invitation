"""Convert rendered PNG layers to WebP assets and compose the page backdrop.

Usage: python3 pack.py <png-dir> [<gigi-balang.svg>]
"""
import shutil
import sys
from pathlib import Path

from PIL import Image

src = Path(sys.argv[1])
assets = Path(__file__).resolve().parents[1] / 'assets'
assets.mkdir(exist_ok=True)
opaque = {'sky'}

for png in sorted(src.glob('*.png')):
    image = Image.open(png)
    if png.stem in opaque:
        image = image.convert('RGB')
    image.save(assets / f'{png.stem}.webp', quality=78, method=6)
    print(png.stem, image.size)

# The page backdrop and the With Love / schedule vignette are composites.
layers = {name: Image.open(src / f'{name}.png').convert('RGBA') for name in ('sky', 'mountain', 'hills', 'house')}
scene = Image.new('RGBA', (960, 1400))
scene.alpha_composite(layers['sky'].resize((960, 1800)).crop((0, 0, 960, 1400)))
scene.alpha_composite(layers['mountain'], (0, 330))
scene.alpha_composite(layers['hills'], (0, 650))
scene.alpha_composite(layers['house'], (0, 720))
scene.convert('RGB').save(assets / 'backdrop.webp', quality=70, method=6)

vignette = Image.new('RGBA', (960, 760))
vignette.alpha_composite(layers['mountain'], (0, -120))
vignette.alpha_composite(layers['hills'], (0, 100))
vignette.alpha_composite(layers['house'], (0, 80))
mask = Image.radial_gradient('L').resize((960, 760)).point(lambda v: max(0, min(255, int((235 - v) * 2.2))))
vignette.putalpha(Image.composite(vignette.getchannel('A'), Image.new('L', vignette.size), mask))
vignette.save(assets / 'pavilion.webp', quality=80, method=6)

if len(sys.argv) > 2:
    shutil.copy(sys.argv[2], assets / 'gigi-balang.svg')
