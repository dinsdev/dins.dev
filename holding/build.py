"""Assemble the dins.dev holding page assets from the brand sources.

Usage:
    uv run --no-project --with fonttools --with brotli python holding/build.py

Copies the tokens, logos, icons and Ottie's idle sheet into holding/public/assets/
and writes small WOFF2 subsets of Fraunces and Instrument Sans (Latin, fixed axes
where the page only needs one value). Rerun it whenever a brand source changes;
never edit the files under assets/ by hand.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
OUT = ROOT / "holding" / "public" / "assets"

# Basic Latin, Latin-1 (accents, the copyright sign) and curly quotes.
UNICODES = [*range(0x20, 0x7F), *range(0xA0, 0x100), 0x2018, 0x2019, 0x201C, 0x201D, 0x2026]

FONTS = {
    # The page sets Fraunces at weight 500 with SOFT 50 and WONK 0 (BRAND.md rule 4);
    # optical size stays variable so the headline tracks its size.
    "fraunces.woff2": (BRAND / "fonts" / "Fraunces-VF.ttf", {"SOFT": 50, "WONK": 0, "wght": 500}),
    "instrument-sans.woff2": (BRAND / "fonts" / "InstrumentSans-VF.ttf", {"wdth": 100, "wght": (400, 600)}),
}

COPIES = {
    "tokens.css": BRAND / "tokens" / "tokens.css",
    "lockup-light.svg": BRAND / "logo" / "lockup-light.svg",
    "lockup-dark.svg": BRAND / "logo" / "lockup-dark.svg",
    "ottie-idle.webp": BRAND / "ottie" / "dist" / "idle.webp",
    "fonts/OFL-Fraunces.txt": BRAND / "fonts" / "OFL.txt",
    "fonts/OFL-InstrumentSans.txt": BRAND / "fonts" / "OFL-InstrumentSans.txt",
}

# Icons are served from the site root, where browsers and the manifest look for them.
ROOT_COPIES = {
    name: BRAND / "logo" / "icons" / name
    for name in ("favicon.ico", "apple-touch-icon.png", "icon-192.png", "icon-512.png", "icon-maskable-512.png", "site.webmanifest")
} | {"favicon.svg": BRAND / "logo" / "favicon.svg"}


def build_font(src: Path, axes: dict[str, float | tuple[float, float]], dst: Path) -> int:
    font = instancer.instantiateVariableFont(TTFont(src), axes)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga", "calt", "ccmp", "locl", "mark", "mkmk"]
    options.name_IDs = ["*"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=UNICODES)
    subsetter.subset(font)
    dst.parent.mkdir(parents=True, exist_ok=True)
    font.flavor = "woff2"
    font.save(dst)
    return dst.stat().st_size


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    for name, (src, axes) in FONTS.items():
        size = build_font(src, axes, OUT / "fonts" / name)
        print(f"fonts/{name}: {size:,} bytes")
    for name, src in COPIES.items():
        (OUT / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, OUT / name)
        print(f"{name}: copied")
    for name, src in ROOT_COPIES.items():
        shutil.copy2(src, OUT.parent / name)
        print(f"/{name}: copied")


if __name__ == "__main__":
    main()
