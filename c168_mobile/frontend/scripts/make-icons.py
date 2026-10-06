"""Regenerate the phone-version icons.

Two pieces, deliberately different:
  * tab favicon (favicon.ico, icons/mark-192.png) = the desktop graphic: blue mark on a
    TRANSPARENT background, so the browser's tab strip shows through (this is what the
    desktop site uses at /favicon.ico).
  * app icons (icon-192/512, apple-touch-icon, icon-maskable-512) = the same mark in
    white on the brand-blue gradient the logo itself uses — a full-bleed tile, which is
    what iOS/Android home screens expect (the old white-background version read as a
    dirty white chip).

Source art: images/count_logo.png (blue mark, transparent) and images/count_whitelogo.png
(white mark, transparent cut-outs).
Run from anywhere:  python c168_mobile/frontend/scripts/make-icons.py
Writes c168_mobile/frontend/public/{favicon.ico,icons/*.png}.
The built site serves c168_mobile/frontend/dist/, so copy the files there too (or run
`npm run build`, which copies public/ verbatim).
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
PUBLIC = ROOT / "c168_mobile" / "frontend" / "public"
ICONS = PUBLIC / "icons"

# 135° ramp sampled off the mark in images/count_logo.png (top-left → bottom-right).
GRAD_FROM, GRAD_TO = (83, 200, 242), (3, 83, 249)
MARK_CROP = (14, 42, 108, 138)  # mark inside count_whitelogo.png; wordmark starts at x=131

# Mark size as a fraction of the canvas. The maskable entry stays inside the web-app
# manifest's safe circle (a square of side s fits when s/√2 ≤ 0.4·N → s ≤ 0.566·N).
SIZES = [
    ("icon-192.png", 192, 0.62),
    ("icon-512.png", 512, 0.62),
    ("apple-touch-icon.png", 180, 0.62),
    ("icon-maskable-512.png", 512, 0.52),
]


def white_mark() -> Image.Image:
    logo = Image.open(ROOT / "images" / "count_whitelogo.png").convert("RGBA")
    return logo.crop(MARK_CROP)


def blue_mark() -> Image.Image:
    """The desktop favicon graphic: blue mark, transparent background."""
    logo = Image.open(ROOT / "images" / "count_logo.png").convert("RGBA")
    return logo.crop(logo.split()[3].getbbox())


def gradient(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)
    for i in range(2 * size):
        t = i / (2 * size - 1)
        rgb = tuple(round(a + (b - a) * t) for a, b in zip(GRAD_FROM, GRAD_TO))
        draw.line([(i, 0), (0, i)], fill=rgb + (255,))
    return img


def center(canvas: Image.Image, mark: Image.Image, ratio: float) -> Image.Image:
    width = round(canvas.width * ratio)
    mark = mark.resize((width, round(width * mark.height / mark.width)), Image.LANCZOS)
    canvas.alpha_composite(mark, ((canvas.width - mark.width) // 2, (canvas.height - mark.height) // 2))
    return canvas


def tile(size: int, ratio: float) -> Image.Image:
    return center(gradient(size), white_mark(), ratio)


def mark_on_transparent(size: int, ratio: float = 0.92) -> Image.Image:
    return center(Image.new("RGBA", (size, size), (0, 0, 0, 0)), blue_mark(), ratio)


def main() -> None:
    for name, size, ratio in SIZES:
        path = ICONS / name
        tile(size, ratio).save(path)
        print(f"wrote {path.relative_to(ROOT)}")

    # Tab favicon = the desktop graphic (transparent). Rendered from a 512 canvas so the
    # 16px entry is not a downscale of an already-small image.
    favicon = PUBLIC / "favicon.ico"
    mark_on_transparent(512).save(favicon, sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"wrote {favicon.relative_to(ROOT)}")

    png = ICONS / "mark-192.png"
    mark_on_transparent(192).save(png)
    print(f"wrote {png.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
