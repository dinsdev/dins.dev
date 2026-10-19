"""Trace the flat Ottie draft into the dins seal SVGs.

Usage:
    uv run --no-project --python 3.12 --with pillow --with vtracer python brand/tools/seal.py
    (vtracer segfaults on Python 3.14 as of 2026-10-19, so this pins 3.12)

Steps: snap every pixel of brand/concepts/ottie-seal-draft.png to the five Ottie colors,
key out the white background, trace with vtracer, snap the traced fills to the palette
again, then wrap the art in a ring drawn in code so the circle is exact.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import vtracer
from PIL import Image, ImageDraw, ImageFilter

BRAND = Path(__file__).resolve().parent.parent
DRAFT = BRAND / "concepts" / "ottie-seal-draft.png"
OUT = BRAND / "logo"

# Ottie's own colors (brand rule 3: they stay in the mascot) plus brand ink and white.
OTTIE = {
    "brown": "#8A5A3B",
    "dark": "#5E3B25",
    "cream": "#F1DCC0",
    "ink": "#12181C",
    "white": "#FFFFFF",
}
PAPER_LIGHT, INK_LIGHT = "#F4F1EA", "#12181C"
PAPER_DARK, INK_DARK = "#1F1E1C", "#ECE9E2"


def rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


PALETTE = {name: rgb(h) for name, h in OTTIE.items()}


def nearest(c: tuple[int, int, int]) -> str:
    return min(PALETTE, key=lambda n: sum((a - b) ** 2 for a, b in zip(c, PALETTE[n])))


def quantize(img: Image.Image) -> Image.Image:
    """Snap to the palette, clean anti-alias specks, key out the outer white."""
    img = img.convert("RGB")
    pal_img = Image.new("P", (1, 1))
    flat = []
    for name in OTTIE:
        flat += list(PALETTE[name])
    pal_img.putpalette(flat + [0, 0, 0] * (256 - len(OTTIE)))
    q = img.quantize(palette=pal_img, dither=Image.Dither.NONE)
    q = q.filter(ImageFilter.ModeFilter(5)).convert("RGB")
    # Background: flood fill the white that touches the corners with magenta, then make it clear.
    key = (255, 0, 255)
    w, h = q.size
    for corner in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        if q.getpixel(corner) == PALETTE["white"]:
            ImageDraw.floodfill(q, corner, key, thresh=0)
    rgba = q.convert("RGBA")
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            if px[x, y][:3] == key:
                px[x, y] = (0, 0, 0, 0)
    return rgba


def trace(rgba: Image.Image) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        src, dst = Path(tmp) / "in.png", Path(tmp) / "out.svg"
        rgba.save(src)
        vtracer.convert_image_to_svg_py(
            str(src), str(dst), colormode="color", hierarchical="stacked", mode="spline",
            filter_speckle=10, color_precision=8, layer_difference=24, corner_threshold=60,
            length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=2,
        )
        return dst.read_text()


def art_paths(svg: str) -> str:
    """Keep the traced paths, snapping each fill to the palette."""
    out = []
    for m in re.finditer(r"<path[^>]*/>", svg):
        tag = m.group(0)
        fill = re.search(r'fill="(#[0-9A-Fa-f]{6})"', tag)
        if not fill:
            continue
        snapped = OTTIE[nearest(rgb(fill.group(1)))]
        out.append(tag.replace(fill.group(0), f'fill="{snapped}"'))
    return "".join(out)


def seal_svg(art: str, size: int, paper: str, ring: str, with_ring: bool = True) -> str:
    c = size / 2
    stroke = size * 0.032
    r = size * 0.47
    clip_r = r - stroke / 2 if with_ring else size / 2
    # Shrink the head so ears and whiskers clear the ring, and drop it so the shoulders
    # run off the bottom and the ring itself draws the lower edge.
    scale, drop = (0.84, 0.08 * size) if with_ring else (0.9, 0.06 * size)
    fit = f"translate({c:.1f} {c + drop:.1f}) scale({scale}) translate({-c:.1f} {-c:.1f})"
    ring_el = (f'<circle cx="{c}" cy="{c}" r="{r:.1f}" fill="none" stroke="{ring}" stroke-width="{stroke:.1f}"/>'
               if with_ring else "")
    bg = (f'<circle cx="{c}" cy="{c}" r="{clip_r:.1f}" fill="{paper}"/>' if with_ring
          else f'<rect width="{size}" height="{size}" fill="{paper}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" role="img" aria-label="Ottie">'
            f'<defs><clipPath id="seal"><circle cx="{c}" cy="{c}" r="{clip_r:.1f}"/></clipPath></defs>'
            f'{bg}<g clip-path="url(#seal)"><g transform="{fit}">{art}</g></g>{ring_el}</svg>\n')


def main() -> None:
    img = Image.open(DRAFT)
    size = img.size[0]
    rgba = quantize(img)
    art = art_paths(trace(rgba))
    OUT.mkdir(exist_ok=True)
    files = {
        "seal-light.svg": seal_svg(art, size, PAPER_LIGHT, INK_LIGHT),
        "seal-dark.svg": seal_svg(art, size, PAPER_DARK, INK_DARK),
        "avatar.svg": seal_svg(art, size, PAPER_LIGHT, INK_LIGHT, with_ring=False),
    }
    for name, body in files.items():
        (OUT / name).write_text(body)
        print(OUT / name, f"{len(body) // 1024} KB")


if __name__ == "__main__":
    main()
