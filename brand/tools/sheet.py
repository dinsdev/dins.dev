"""Embed brand/logo SVGs into an HTML template so the page opens without a server.

Usage:  python3 brand/tools/sheet.py                       (logo sheet)
        python3 brand/tools/sheet.py <template> <output>   (any other page, paths from the repo root)
"""

import base64
import re
import sys
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent
ROOT = BRAND.parent
if len(sys.argv) == 3:
    template, out = (ROOT / sys.argv[1]).read_text(), ROOT / sys.argv[2]
else:
    template, out = (BRAND / "tools" / "logo-sheet.template.html").read_text(), BRAND / "logo" / "logo-sheet.html"


MIME = {"svg": "image/svg+xml", "png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}


def embed(m: re.Match) -> str:
    """A bare name is a file in brand/logo; a path with a slash is relative to brand/."""
    name = m.group(1)
    path = BRAND / name if "/" in name else BRAND / "logo" / name
    data = base64.b64encode(path.read_bytes()).decode()
    return f'src="data:{MIME[name.rsplit(".", 1)[1]]};base64,{data}"'


out.write_text(re.sub(r'src="([\w./-]+\.(?:svg|png|webp|jpg))"', embed, template))
print(out, f"{out.stat().st_size // 1024} KB")
