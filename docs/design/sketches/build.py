import pathlib, re, sys
repo = pathlib.Path(__file__).resolve().parents[3]
here = pathlib.Path(__file__).parent
def themed(svg):
    svg = re.sub(r'<\?xml[^>]*>', '', svg)
    svg = svg.replace('fill="#12181C"', 'fill="currentColor"').replace('stroke="#12181C"', 'stroke="currentColor"')
    return svg.replace('fill="#0F6B6B"', 'style="fill:var(--color-accent)"')
t = (here / "home.template.html").read_text()
t = t.replace("{{TOKENS}}", (repo / "brand/tokens/tokens.css").read_text())
t = t.replace("{{WORDMARK}}", themed((repo / "brand/logo/wordmark-small-light.svg").read_text()))
t = t.replace("{{LENS}}", themed((repo / "brand/logo/lens-light.svg").read_text()))
t = t.replace("{{OTTIE}}", (repo / "brand/logo/avatar.svg").read_text().replace('<rect width="1254" height="1254" fill="#F4F1EA"/>', ""))
(here / "home-sketch.html").write_text(t)
print("ok", len(t))
