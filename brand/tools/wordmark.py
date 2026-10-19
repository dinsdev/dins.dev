"""Draw the dins wordmark from Fraunces outlines as SVG paths.

Usage:
    uv run --no-project --with fonttools --with uharfbuzz python brand/tools/wordmark.py final
    (or "variants" for the weight and softness exploration sheet)

Shapes the text with HarfBuzz (so kerning applies), draws each glyph at the chosen
variable-font axes, and writes SVG with real paths (no font needed to display it).
The final period is filled with the brand accent; everything else uses currentColor.
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

BRAND = Path(__file__).resolve().parent.parent
FONT = BRAND / "fonts" / "Fraunces-VF.ttf"

INK_LIGHT, PAPER_LIGHT, TEAL_LIGHT = "#12181C", "#F4F1EA", "#0F6B6B"
INK_DARK, PAPER_DARK, TEAL_DARK = "#ECE9E2", "#1F1E1C", "#5CBFB8"


def shape(text: str, axes: dict[str, float], tracking: float):
    """Return (glyph paths, bounds). tracking is extra advance in em/1000."""
    face = hb.Face(hb.Blob.from_file_path(str(FONT)))
    font = hb.Font(face)
    font.set_variations(axes)
    upem = face.upem
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True})

    glyphs, x = [], 0.0
    xmin = ymin = float("inf")
    xmax = ymax = float("-inf")
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        ox, oy = x + pos.x_offset, pos.y_offset
        svg_pen = SVGPathPen(None)
        font.draw_glyph_with_pen(info.codepoint, TransformPen(svg_pen, (1, 0, 0, -1, ox, -oy)))
        bounds_pen = BoundsPen(None)
        font.draw_glyph_with_pen(info.codepoint, TransformPen(bounds_pen, (1, 0, 0, -1, ox, -oy)))
        if bounds_pen.bounds:
            a, b, c, d = bounds_pen.bounds
            xmin, ymin, xmax, ymax = min(xmin, a), min(ymin, b), max(xmax, c), max(ymax, d)
        glyphs.append((text[info.cluster], svg_pen.getCommands()))
        x += pos.x_advance + (tracking / 1000 * upem if i < len(text) - 1 else 0)
    return glyphs, (xmin, ymin, xmax, ymax), upem


def wordmark_svg(axes: dict[str, float], tracking: float = -20, accent: str = TEAL_LIGHT,
                 height: float | None = None, text: str = "dins.") -> str:
    glyphs, (x0, y0, x1, y1), upem = shape(text, axes, tracking)
    pad = upem * 0.02
    vb = (x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    paths = []
    for ch, d in glyphs:
        fill = accent if ch == "." else "currentColor"
        paths.append(f'<path fill="{fill}" d="{d}"/>')
    size = f' height="{height}"' if height else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb[0]:.1f} {vb[1]:.1f} {vb[2]:.1f} {vb[3]:.1f}"'
            f'{size} role="img" aria-label="dins">' + "".join(paths) + "</svg>")


def variants() -> Path:
    weights = [500, 600, 700]
    softs = [0, 50, 100]
    cells = []
    for w in weights:
        for s in softs:
            axes = {"wght": w, "opsz": 144, "SOFT": s, "WONK": 0}
            light = wordmark_svg(axes, accent=TEAL_LIGHT, height=96)
            dark = wordmark_svg(axes, accent=TEAL_DARK, height=40)
            small = wordmark_svg(axes, accent=TEAL_LIGHT, height=22)
            label = f"weight {w} · soft {s}"
            cells.append(f"""
      <figure>
        <figcaption>{escape(label)}</figcaption>
        <div class="big">{light}</div>
        <div class="row"><div class="dark">{dark}</div><div class="tiny">{small}</div></div>
      </figure>""")
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>dins wordmark variants</title>
<style>
  * {{ box-sizing: border-box; margin: 0; }}
  body {{ background: #1b1d1f; padding: 16px; font: 13px/1.4 ui-monospace, monospace; color: #ece9e2; }}
  h1 {{ font-size: 14px; font-weight: 500; padding: 4px 4px 14px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: 14px; }}
  figure {{ background: {PAPER_LIGHT}; color: {INK_LIGHT}; border-radius: 12px; padding: 18px 22px 20px; display: flex; flex-direction: column; gap: 16px; }}
  figcaption {{ color: #4A555C; letter-spacing: .06em; text-transform: uppercase; font-size: 11.5px; }}
  .big {{ display: flex; justify-content: center; padding: 10px 0 4px; }}
  .row {{ display: flex; gap: 12px; align-items: stretch; }}
  .dark {{ background: {PAPER_DARK}; color: {INK_DARK}; border-radius: 8px; padding: 12px 16px; flex: 1; display: flex; justify-content: center; }}
  .tiny {{ border: 1px solid #ddd8cc; border-radius: 8px; padding: 12px 14px; display: flex; align-items: center; }}
</style></head><body>
<h1>dins wordmark: Fraunces at display size (opsz 144), real outlines. Each card: big on paper, small on charcoal, tiny for nav size.</h1>
<main class="grid">{''.join(cells)}
</main></body></html>
"""
    out = BRAND / "logo" / "explorations" / "wordmark-variants.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


# Final logo spec (Din, 2026-10-19): Fraunces weight 600, SOFT 50, WONK 0.
DISPLAY = {"wght": 600, "opsz": 144, "SOFT": 50, "WONK": 0}
SMALL = {"wght": 600, "opsz": 36, "SOFT": 50, "WONK": 0}  # thicker hairlines for nav sizes
DISPLAY_TRACKING = -15
SMALL_TRACKING = 5


def x_height(axes: dict[str, float]) -> float:
    font = hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT))))
    font.set_variations(axes)
    return font.get_glyph_extents(font.get_nominal_glyph(ord("x"))).y_bearing


def lens_shapes(xh: float, ink: str, accent: str, stroke_ratio: float = 0.14) -> tuple[str, tuple]:
    """Ottie's glasses in font units, centered on the x-height middle (y up is negative).

    Outer lens diameter is 1.12 x the x-height. The rim sits between the Fraunces hairline and
    stem weight: a full-stem rim read as two donuts with no room for the glint.
    Returns (svg elements, bounds).
    """
    d_outer = 1.12 * xh
    s = stroke_ratio * d_outer
    r = (d_outer - s) / 2
    temple = 0.50 * r
    gap = 0.62 * r  # between the outer edges of the two rims
    cy = -xh / 2
    cx1 = temple + s / 2 + r
    cx2 = cx1 + 2 * r + s + gap
    bx1, bx2 = cx1 + r, cx2 - r
    lift = 0.24 * r
    t_y = cy - 0.42 * r
    # temple stubs leave the rims at the upper outer edge and run outward, slightly up
    lx = cx1 - r * 0.91
    rx = cx2 + r * 0.91
    els = (f'<g fill="none" stroke="{ink}" stroke-width="{s:.1f}" stroke-linecap="round">'
           f'<circle cx="{cx1:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>'
           f'<circle cx="{cx2:.1f}" cy="{cy:.1f}" r="{r:.1f}"/>'
           f'<path d="M{bx1:.1f} {cy - 0.12 * r:.1f} Q{(bx1 + bx2) / 2:.1f} {cy - 0.12 * r - lift:.1f} {bx2:.1f} {cy - 0.12 * r:.1f}"/>'
           f'<path d="M{lx:.1f} {t_y:.1f} L{lx - temple:.1f} {t_y - 0.18 * temple:.1f}"/>'
           f'<path d="M{rx:.1f} {t_y:.1f} L{rx + temple:.1f} {t_y - 0.18 * temple:.1f}"/>'
           '</g>'
           f'<circle cx="{cx2 + 0.33 * r:.1f}" cy="{cy - 0.33 * r:.1f}" r="{0.17 * r:.1f}" fill="{accent}"/>')
    x0 = lx - temple - s / 2
    x1 = rx + temple + s / 2
    y0 = cy - r - s / 2
    y1 = cy + r + s / 2
    return els, (x0, y0, x1, y1)


def _svg(vb, body, label="dins", extra=""):
    x, y, w, h = vb
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x:.1f} {y:.1f} {w:.1f} {h:.1f}" '
            f'role="img" aria-label="{label}"{extra}>{body}</svg>\n')


def wordmark_body(axes, tracking, ink, accent, dx=0.0):
    glyphs, bounds, upem = shape("dins.", axes, tracking)
    paths = "".join(f'<path fill="{accent if ch == "." else ink}" d="{d}"/>' for ch, d in glyphs)
    g = f'<g transform="translate({dx:.1f} 0)">{paths}</g>' if dx else paths
    x0, y0, x1, y1 = bounds
    return g, (x0 + dx, y0, x1 + dx, y1), upem


def pad(b, p):
    x0, y0, x1, y1 = b
    return (x0 - p, y0 - p, x1 - x0 + 2 * p, y1 - y0 + 2 * p)


def final() -> list[Path]:
    out = BRAND / "logo"
    out.mkdir(exist_ok=True)
    written = []
    themes = {"light": (INK_LIGHT, TEAL_LIGHT), "dark": (INK_DARK, TEAL_DARK), "mono": ("currentColor", "currentColor")}
    xh = x_height(DISPLAY)
    for name, (ink, acc) in themes.items():
        body, b, upem = wordmark_body(DISPLAY, DISPLAY_TRACKING, ink, acc)
        (out / f"wordmark-{name}.svg").write_text(_svg(pad(b, upem * 0.02), body))
        body, b, upem = wordmark_body(SMALL, SMALL_TRACKING, ink, acc)
        (out / f"wordmark-small-{name}.svg").write_text(_svg(pad(b, upem * 0.02), body))
        lens, lb = lens_shapes(xh, ink, acc)
        (out / f"lens-{name}.svg").write_text(_svg(pad(lb, 20), lens, "dins lens"))
        gap = 0.38 * xh
        dx = lb[2] + gap
        body, wb, upem = wordmark_body(DISPLAY, DISPLAY_TRACKING, ink, acc, dx=dx)
        bb = (min(lb[0], wb[0]), min(lb[1], wb[1]), max(lb[2], wb[2]), max(lb[3], wb[3]))
        (out / f"lockup-{name}.svg").write_text(_svg(pad(bb, upem * 0.02), lens + body))
        written += [out / f"{k}-{name}.svg" for k in ("wordmark", "wordmark-small", "lens", "lockup")]

    # App icon: paper lens on ink, calm teal glint, 1024 canvas
    lens, (x0, y0, x1, y1) = lens_shapes(xh, PAPER_LIGHT, TEAL_DARK)
    w = x1 - x0
    scale = 1024 * 0.70 / w
    tx = 512 - (x0 + w / 2) * scale
    ty = 512 - ((y0 + y1) / 2) * scale
    icon = (f'<rect width="1024" height="1024" rx="228" fill="{INK_LIGHT}"/>'
            f'<g transform="translate({tx:.1f} {ty:.1f}) scale({scale:.4f})">{lens}</g>')
    (out / "app-icon.svg").write_text(_svg((0, 0, 1024, 1024), icon, "dins"))
    written.append(out / "app-icon.svg")

    # favicon.svg is written by brand/tools/icons.py (a solid tile reads better at 16 px).
    return written


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "variants"
    if cmd == "variants":
        print(variants())
    elif cmd == "final":
        for f in final():
            print(f)
    else:
        sys.exit(f"unknown command: {cmd}")
