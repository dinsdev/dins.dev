<p>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="brand/logo/lockup-dark.svg">
    <img src="brand/logo/lockup-light.svg" alt="dins" height="64">
  </picture>
</p>

Look closer.

This repo is home to dins, my studio for data and AI work, client websites and small iOS games. Right now it holds the brand system and the setup plan. The dins.dev website will be built here next, followed by pages for each game.

## What's here

| Path | What it is |
|---|---|
| `brand/logo/` | Final logo files: wordmark, lens, lockup, app icon, favicon, Ottie seal (light, dark, mono) |
| `brand/tools/` | Scripts that generate those files from the Fraunces font and the traced Ottie art |
| `brand/fonts/` | Fraunces and Instrument Sans, vendored under the SIL Open Font License |
| `holding/` | The "under construction" page shown at dins.dev until the site launches |
| `brand/logo/icons/` | Favicons, app icons, avatar PNGs and the web manifest |
| `brand/tokens/` | Design tokens: `tokens.json` (source) and generated `tokens.css` |
| `brand/specimen/` | Type, scale and color specimens used to make brand decisions |
| `docs/BRAND.md` | The brand guide (rules) |
| `brand/brand-guide.html` | The visual brand guide, self-contained, built by `brand/tools/guide.py` |
| `docs/` | Requirements, plan, task list and a work ledger of decisions |

## Regenerating the logo files

Needs [uv](https://docs.astral.sh/uv/).

```bash
uv run --no-project --with fonttools --with uharfbuzz python brand/tools/wordmark.py final
uv run --no-project --python 3.12 --with pillow --with vtracer python brand/tools/seal.py
python3 brand/tools/tokens.py
DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib uv run --no-project --with fonttools --with uharfbuzz --with cairosvg --with pillow python brand/tools/icons.py
python3 brand/tools/sheet.py
```

The icons step needs Homebrew's `cairo`. The last command rebuilds `brand/logo/logo-sheet.html`, a self-contained overview of every mark.

## License

Fraunces and Instrument Sans are under the SIL Open Font License (`brand/fonts/OFL.txt`, `brand/fonts/OFL-InstrumentSans.txt`). The dins name, logos and the Ottie character are not licensed for reuse.
