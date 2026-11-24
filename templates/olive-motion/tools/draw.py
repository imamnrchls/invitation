"""Make independent motion layers from Olive Garden artwork. Requires Pillow."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

theme = Path(__file__).resolve().parents[1]
garden = theme.parent / "olive-garden" / "assets"
assets = theme / "assets"
assets.mkdir(exist_ok=True)
landscape = Image.open(garden / "garden-landscape.webp").convert("RGB")
botanical = Image.open(garden / "botanical.webp").convert("RGBA")


def save(image, name):
    image.save(assets / f"{name}.webp", quality=87, method=6)


def fade_crop(box, size, fade, strength=1):
    image = landscape.crop(box).resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    width, height = size
    alpha = Image.new("L", size)
    draw = ImageDraw.Draw(alpha)
    for y in range(height):
        opacity = min(y / fade, 1) * strength
        draw.line((0, y, width, y), fill=round(255 * opacity))
    image.putalpha(alpha)
    return image


sky = ImageOps.fit(landscape.crop((365, 58, 925, 230)), (480, 900))
save(Image.blend(sky, Image.new("RGB", sky.size, "#f8f5eb"), .78), "sky")
save(fade_crop((230, 220, 990, 455), (960, 360), 165, .68), "mountains-far")
save(fade_crop((120, 298, 1110, 578), (960, 385), 150, .83), "mountains-near")
save(fade_crop((65, 355, 1105, 800), (960, 680), 280), "forest")

stem = botanical.crop((0, 0, 238, 480))
save(stem, "palm")
save(stem.rotate(-28, expand=True, resample=Image.Resampling.BICUBIC), "leaves")
save(botanical.crop((0, 135, 430, 500)), "bouquet")

flowers = Image.new("RGBA", (960, 680))
corner = ImageOps.contain(botanical, (710, 495), Image.Resampling.LANCZOS)
accent = ImageOps.mirror(ImageOps.contain(botanical, (465, 310), Image.Resampling.LANCZOS))
flowers.alpha_composite(accent, (500, 680 - accent.height))
flowers.alpha_composite(corner, (0, 680 - corner.height))
save(flowers, "flowers")

pavilion = landscape.crop((292, 434, 757, 722)).resize((640, 400), Image.Resampling.LANCZOS).convert("RGBA")
mask = Image.new("L", pavilion.size)
draw = ImageDraw.Draw(mask)
for step in range(100):
    inset = step * .9
    draw.ellipse((inset, inset * .7, 639 - inset, 399 - inset * .7), fill=round(step * 255 / 99))
pavilion.putalpha(mask)
save(pavilion, "pavilion")

frame = Image.new("RGBA", (600, 800))
draw = ImageDraw.Draw(frame)
draw.ellipse((65, 66, 535, 734), outline="#f8f5eb", width=15)
draw.ellipse((63, 64, 537, 736), outline="#b09a68", width=3)
draw.ellipse((77, 78, 523, 722), outline="#d9c591", width=3)
save(frame, "frame")
