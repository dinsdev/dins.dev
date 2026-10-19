"""Generate brand/tokens/tokens.css from brand/tokens/tokens.json.

Usage:  python3 brand/tools/tokens.py

Output: CSS custom properties for color (light, dark by system setting, and an explicit
data-theme override in both directions), fonts, the fluid type scale, spacing, radius,
layout and motion, plus one class per type step (.t-display ... .t-data).
"""

import json
from pathlib import Path

BRAND = Path(__file__).resolve().parent.parent
T = json.loads((BRAND / "tokens" / "tokens.json").read_text())


def rem(px: float) -> str:
    return f"{px / 16:.4g}rem"


def fluid(lo: float, hi: float) -> str:
    vmin, vmax = T["viewport"]["min"], T["viewport"]["max"]
    if lo == hi:
        return rem(lo)
    slope = (hi - lo) / (vmax - vmin)
    base = lo - slope * vmin
    return f"clamp({rem(lo)}, {rem(base)} + {slope * 100:.4g}vw, {rem(hi)})"


def colors(theme: str, indent: str) -> str:
    return "\n".join(f"{indent}--color-{k}: {v};" for k, v in T["color"][theme].items())


lines = ["/* Generated from tokens.json by brand/tools/tokens.py. Do not edit by hand. */", "", ":root {"]
lines.append(colors("light", "  "))
for k, v in T["font"].items():
    lines.append(f"  --font-{k}: {v};")
for name, s in T["type"].items():
    lines.append(f"  --text-{name}: {fluid(s['min'], s['max'])};")
    lines.append(f"  --text-{name}-lh: {s['lineHeight']};")
    lines.append(f"  --text-{name}-weight: {s['weight']};")
    lines.append(f"  --text-{name}-tracking: {s['tracking']};")
for k, v in T["space"].items():
    lines.append(f"  --space-{k}: {rem(v)};")
for k, v in T["radius"].items():
    lines.append(f"  --radius-{k}: {v}px;")
lines.append(f"  --measure: {T['layout']['measure']};")
lines.append(f"  --page-max: {T['layout']['page']}px;")
lines.append(f"  --gutter: max({T['layout']['gutterMin']}px, env(safe-area-inset-left, 0px));")
for k, v in T["motion"].items():
    lines.append(f"  --motion-{k}: {v};")
lines.append("  color-scheme: light;")
lines.append("}")
lines.append("")
lines.append("@media (prefers-color-scheme: dark) {")
lines.append('  :root:not([data-theme="light"]) {')
lines.append(colors("dark", "    "))
lines.append("    color-scheme: dark;")
lines.append("  }")
lines.append("}")
lines.append("")
lines.append(':root[data-theme="dark"] {')
lines.append(colors("dark", "  "))
lines.append("  color-scheme: dark;")
lines.append("}")
lines.append("")
lines.append("/* Type steps. Fraunces always runs with SOFT and optical sizing on. */")
fr = T["fraunces"]
for name, s in T["type"].items():
    body = [
        f"font-family: var(--font-{s['family']});",
        f"font-size: var(--text-{name});",
        f"line-height: var(--text-{name}-lh);",
        f"font-weight: var(--text-{name}-weight);",
        f"letter-spacing: var(--text-{name}-tracking);",
    ]
    if s["family"] == "display":
        body += ["font-optical-sizing: auto;", f'font-variation-settings: "SOFT" {fr["soft"]}, "WONK" {fr["wonk"]};',
                 "text-wrap: balance;"]
    if "color" in s:
        body.append(f"color: var(--color-{s['color']});")
    if "transform" in s:
        body.append(f"text-transform: {s['transform']};")
    if "numeric" in s:
        body.append(f"font-variant-numeric: {s['numeric']};")
    if name == "body":
        body.append("max-width: var(--measure);")
    lines.append(f".t-{name} {{ " + " ".join(body) + " }")
lines.append("")

out = BRAND / "tokens" / "tokens.css"
out.write_text("\n".join(lines))
print(out)
