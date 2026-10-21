# Ottie

Ottie, the animated mascot of dins.dev, as packed sprite sheets the site
plays. Ottie is a 3D character built and animated in Blender (decisions in
`docs/WORK_LEDGER.md`). The model, the Blender files, the build tools and the
rendered frames are private and live in a separate local repo,
`~/Develop/dins-ottie`; this folder holds only what the website needs.

## What is here

- `dist/`: one WebP sprite sheet per state, plus `manifest.json` (and
  `manifest.js`, the same data as a script, so the preview opens without a
  server). States: idle, wave, run-in, think, nod, point, shrug, poke, jump,
  nap, wake and talk. 2,404 KB together.
- `preview/index.html`: a standalone player used for approval: every state on
  a button, paper and charcoal side by side, real size and 2x, clean exits
  with a crossfade fallback, a chaining demo and a reduced-motion still.
- `../reference/ottie-3d-neutral.webp`: the neutral pose at full render size,
  the reference for the final look.

Preview: `python3 -m http.server 8765 --directory brand/ottie`, then open
http://127.0.0.1:8765/preview/index.html.

## Manifest

Top level: `version`, `display_scale` (frames are drawn at 2x the display
size), `total_bytes` and `states`. Each state has:

- `file`, `frame` (width and height in pixels), `cols` (drawings per sheet
  row), `count` (drawings).
- `loop` (true for idle, think, talk and nap), `tickrate` (ticks per second,
  24) and `drawings_per_second` (for information).
- `frames[i].d`: how many ticks drawing `i` is held.
- `frames[i].ground`: the point between the feet, in frame pixels. The
  player aligns it across states so Ottie never jumps when a state changes.
- `frames[i].shift` (run-in, poke, jump, wake): a whole-body offset in frame
  pixels for travel and hops. The drawings are rendered in place to keep the
  sheets small, and the player adds the shift.
- `exits`: drawings that match the neutral pose, where the player can leave
  without a pop (otherwise it crossfades over 3 ticks).
- `loop_start`: the drawings before it play once (nap dozing off), then the
  rest loops.
- `exit_via`: the state to play on the way out (nap leaves through wake).
- `enter_from`: the state whose loop pose this one starts on (wake from nap).

Every state starts and ends on the neutral pose, except that nap loops on a
sleeping pose and leaves through wake.

## Rebuilding

The sheets are rebuilt in the private repo (`brand/ottie/README.md` there has
the commands) and copied into `dist/` here.
