"""Build brand/brand-guide.html, a self-contained brand guide page (also published as an Artifact).

Usage:  python3 brand/tools/guide.py
Inlines tokens.css and theme-following SVG marks, and embeds every image as a data URI.
"""

import base64
import re
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent
MIME = {"svg": "image/svg+xml", "png": "image/png", "webp": "image/webp", "jpg": "image/jpeg"}


def inline(name: str, cls: str) -> str:
    """A mono SVG that follows the text color, with its last shape (period or glint) in the accent."""
    s = (BRAND / "logo" / name).read_text().strip()
    s = re.sub(r' role="img" aria-label="[^"]*"', ' aria-hidden="true" focusable="false"', s)
    s = s.replace("<svg ", f'<svg class="{cls}" ', 1)
    last = list(re.finditer(r'fill="currentColor"', s))[-1]
    return s[: last.start()] + 'fill="var(--color-accent)"' + s[last.end():]


def embed(m: re.Match) -> str:
    name = m.group(1)
    path = BRAND / name if "/" in name else BRAND / "logo" / name
    return f'src="data:{MIME[name.rsplit(".", 1)[1]]};base64,{base64.b64encode(path.read_bytes()).decode()}"'


page = (BRAND / "tools" / "brand-guide.template.html").read_text()
page = page.replace("{{TOKENS_CSS}}", (BRAND / "tokens" / "tokens.css").read_text())
page = page.replace("{{LENS}}", inline("lens-mono.svg", "lens"))
page = page.replace("{{WORDMARK_SMALL}}", inline("wordmark-small-mono.svg", "wm"))
page = page.replace("{{WORDMARK}}", inline("wordmark-mono.svg", "wm"))
page = re.sub(r'src="([\w./-]+\.(?:svg|png|webp|jpg))"', embed, page)
assert "{{" not in page
out = BRAND / "brand-guide.html"
out.write_text(page)
print(out, f"{len(page) // 1024} KB")
