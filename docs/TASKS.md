# dins: Tasks

Status vocabulary: Proposed, Planned, In progress, Implemented, Verified, Accepted (Din only), Done (Din) for setup Din does by hand.

## Phase 0: Foundation

| ID | Task | Status |
|---|---|---|
| 0.1 | Account security baseline (details in the private handbook) | Done (Din, 2026-10-19) |
| 0.5 | Cloudflare account | Done (Din) |
| 0.6 | Buy `dins.dev` on Cloudflare: 4 years, auto-renew on | Planned (Din, 2026-10-20) |
| 0.7 | Turn on DNSSEC, add CAA records | Planned |
| 0.8 | Email Routing: `din@`, `dinesh@`, `hello@`, `support@`, catch-all to the personal inbox | Planned |
| 0.9 | "Send mail as" with an outgoing mail provider, SPF, DKIM, DMARC | Planned |
| 0.10 | Verify a sent message passes SPF, DKIM and DMARC | Planned |
| 0.11 | GitHub organization `dinsdev` | Done (Din) |
| 0.12 | Claim `dinsdev` on YouTube (Brand Account), TikTok, X | Done (Din) |
| 0.14 | Optional: `@dins.dev` handle on Bluesky | Proposed |
| 0.15 | Create the private `handbook` repo with the accounts inventory | Implemented (2026-10-19) |

## Phase 1: Brand production and workflow

| ID | Task | Status |
|---|---|---|
| 1.1 | Lock brand basics (personality, color, dark mode, Ottie, voice, names) | Accepted (Din, 2026-10-19) |
| 1.1a | Decide fonts and typography | Accepted (Din, 2026-10-19): Fraunces, Instrument Sans, JetBrains Mono |
| 1.1b | Decide the real logo (drawn in the chosen font) | Accepted (Din, 2026-10-19) |
| 1.2 | SVG wordmark "dins." (display and small masters, light, dark, mono) | Accepted (Din, 2026-10-19) |
| 1.3 | SVG lens mark, lockup, app icon, favicon | Accepted (Din, 2026-10-19); solid-tile favicon approved after the 16 px check |
| 1.4 | SVG Ottie seal (light, dark, avatar) | Accepted (Din, 2026-10-19) |
| 1.5 | Favicon set, app-icon sizes, avatar PNGs, web manifest | Implemented |
| 1.5a | Social preview card template | Accepted (Din, 2026-10-19): A default, C for devlogs and game posts |
| 1.5b | Type scale | Accepted (Din, 2026-10-19) |
| 1.6 | Design tokens file (light and dark) | Implemented: `brand/tokens/` |
| 1.7 | Fill social profiles (avatar, name, bio) | Planned |
| 1.8 | Decide repo map and visibility | Accepted (Din, 2026-10-19) |
| 1.9 | Decide branching, PR flow and commit conventions | Accepted (Din, 2026-10-19) |
| 1.10 | Decide checks, CI and dependency updates | Accepted (Din, 2026-10-19) |
| 1.11 | Decide issue tracking and docs conventions | Accepted (Din, 2026-10-19) |
| 1.11a | README for this repo | Implemented |
| 1.12 | Create repos on GitHub, protect `main`, first push | Planned (needs Din's go) |
| 1.13 | Search Console, Bing Webmaster Tools, Cloudflare Web Analytics, uptime monitor | Planned (baseline accepted by Din, 2026-10-19) |
| 1.13a | Site template: titles, canonicals, sitemap, social cards, structured data, `llms.txt` | Planned (with the site) |
| 1.14 | Ottie pose sheet (`brand/concepts/ottie-poses.png`) | Accepted (Din, 2026-10-19); cutouts at site build |
| 1.15 | HTML checklist of everything to do, made at the end of the brainstorm | Implemented (private page; source in `handbook`) |

## Phase 2: Portfolio site

| ID | Task | Status |
|---|---|---|
| 2.1 | Write the site PRD and build plan (earlier concepts in `~/Develop/dins.dev-concepts` are reference only) | In progress |
| 2.1a | Lock routes, content model and the home page skeleton (sketch in `docs/design/sketches/`) | Accepted (Din, 2026-10-19) |
| 2.2 | Lock the Ottie puppet route (Blender, mesh deformation, sprite sheets, live eyes; `docs/design/ottie/BRIEF.md`) | Accepted (Din, 2026-10-19) |
| 2.3 | Build Ottie milestone 1: idle and wave, approved by Din in the preview page | Planned (separate session, branch `feat/ottie-puppet`) |
| 2.4 | Build Ottie milestone 2: the remaining states | Planned |

## Phase 3: Games pipeline

| ID | Task | Status |
|---|---|---|
| 3.1 | Use `dev.dins.<game>` bundle IDs for every new game | Planned |
| 3.2 | Game subdomain template: landing, `/support`, `/privacy`, press kit | Planned |
| 3.3 | Game conventions (identity, privacy, release flow, first paid game checklist) | Accepted (Din, 2026-10-19) |
| 3.4 | SuperOttie showcase page at `superottie.dins.dev` | Planned |

## Phase 4: Business

Tracked in the private `handbook` repo.
