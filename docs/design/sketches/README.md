# Site sketches

Rough, working references for layout and motion from the site brainstorm. Not final design, art or copy.

- `home-sketch.html`: the home page skeleton Din accepted on 2026-10-19 (lens intro, letter field, Ask Ottie hero, center stage, floating paper, studio, letter). Open it in a browser; everything is inlined.
- `home.template.html`: the source. `build.py` fills in the real tokens (`brand/tokens/tokens.css`), wordmark, lens and Ottie avatar, and writes `home-sketch.html`.

Rebuild after editing the template:

```bash
python3 docs/design/sketches/build.py
```

URL flags for screenshots (headless Chrome cannot scroll or wait for animations):

| Flag | Effect |
|---|---|
| `?shot` | Skip the intro; `?shot=answer` also asks a sample question |
| `&theme=light` or `dark` | Force a theme |
| `&at=0..1` | Show only the project stage at that scroll progress |
| `&only=writing` | Show only the writing section |
| `&only=about&ap=0..1` | Show only the studio at that scroll progress |
| `&only=contact&st=...` | Show only the letter, optionally in a state such as `folding tucked closed sealed` |
