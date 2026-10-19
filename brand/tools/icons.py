"""Export the raster icon set and web manifest into brand/logo/icons/.

Usage:
    DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run --no-project \
        --with fonttools --with uharfbuzz --with cairosvg --with pillow python brand/tools/icons.py

Raster icons use a solid tile (paper lens on ink) so they read on light and dark browser
tabs alike, and favicon.svg is the same tile.
Store icons (Apple touch, App Store, maskable) are full-bleed squares: the platform rounds them.
"""

import io
import json
import sys
from pathlib import Path

import cairosvg
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wordmark as wm  # noqa: E402

BRAND = Path(__file__).resolve().parent.parent
OUT = BRAND / "logo" / "icons"


def tile(rounded: bool, lens_width: float, stroke_ratio: float, glint: str = wm.TEAL_DARK) -> str:
    """1024 canvas: ink background, paper lens centered at lens_width of the canvas."""
    xh = wm.x_height(wm.DISPLAY)
    lens, (x0, y0, x1, y1) = wm.lens_shapes(xh, wm.PAPER_LIGHT, glint, stroke_ratio=stroke_ratio)
    w = x1 - x0
    scale = 1024 * lens_width / w
    tx = 512 - (x0 + w / 2) * scale
    ty = 512 - ((y0 + y1) / 2) * scale
    rx = ' rx="228"' if rounded else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">'
            f'<rect width="1024" height="1024"{rx} fill="{wm.INK_LIGHT}"/>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({scale:.4f})">{lens}</g></svg>')


def png(svg: str, size: int) -> Image.Image:
    data = cairosvg.svg2png(bytestring=svg.encode(), output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Tiny sizes: bigger lens and heavier rims so the two rings survive 16 px.
    small = tile(rounded=True, lens_width=0.86, stroke_ratio=0.22)
    regular = tile(rounded=True, lens_width=0.72, stroke_ratio=0.16)
    bleed = tile(rounded=False, lens_width=0.70, stroke_ratio=0.16)
    maskable = tile(rounded=False, lens_width=0.56, stroke_ratio=0.16)  # inside the 80% safe zone

    files = {}
    for s in (16, 32, 48):
        files[f"favicon-{s}.png"] = png(small, s)
    files["apple-touch-icon.png"] = png(bleed, 180).convert("RGB")
    files["icon-192.png"] = png(regular, 192)
    files["icon-512.png"] = png(regular, 512)
    files["icon-maskable-512.png"] = png(maskable, 512).convert("RGB")
    files["app-icon-1024.png"] = png(bleed, 1024).convert("RGB")  # App Store: square, no alpha
    avatar_svg = (BRAND / "logo" / "avatar.svg").read_text()
    files["avatar-800.png"] = Image.open(io.BytesIO(cairosvg.svg2png(
        bytestring=avatar_svg.encode(), output_width=800, output_height=800))).convert("RGB")
    seal_svg = (BRAND / "logo" / "seal-light.svg").read_text()
    files["seal-800.png"] = Image.open(io.BytesIO(cairosvg.svg2png(
        bytestring=seal_svg.encode(), output_width=800, output_height=800)))

    for name, im in files.items():
        im.save(OUT / name, optimize=True)
    files["favicon-48.png"].save(OUT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)],
                                 append_images=[files["favicon-16.png"], files["favicon-32.png"]])
    # The SVG favicon is the same solid tile: the transparent, theme-following lens was only
    # about 4 px tall at 16 px and faded out on both tab colors.
    (BRAND / "logo" / "favicon.svg").write_text(small + "\n")

    manifest = {
        "name": "dins",
        "short_name": "dins",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "theme_color": wm.PAPER_LIGHT,
        "background_color": wm.PAPER_LIGHT,
        "display": "browser",
    }
    (OUT / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")
    for p in sorted(OUT.iterdir()):
        print(p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
