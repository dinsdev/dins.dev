# dins: Tasks

Status vocabulary: Proposed, Planned, In progress, Implemented, Verified, Accepted (Din only), Done (Din) for setup Din does by hand.

## Phase 0: Foundation

| ID | Task | Status |
|---|---|---|
| 0.1 | Account security baseline (details in the private handbook) | Done (Din, 2026-10-19) |
| 0.5 | Cloudflare account | Done (Din) |
| 0.6 | Buy `dins.dev` on Cloudflare: 4 years, auto-renew on | Done (Din, 2026-10-21), bought for 1 year by mistake (expires 2027-10-21) |
| 0.6a | **To do (Din):** extend `dins.dev` to 4 years and confirm auto-renew is on | Planned (Din) |
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
| 1.12 | Create repos on GitHub, protect `main`, first push | Implemented (Din's go): `dinsdev/dins.dev` with a ruleset on `main` (no deletion, no force push, linear history, PRs); PRs 1 to 3 merged |
| 1.13 | Search Console, Bing Webmaster Tools, Cloudflare Web Analytics, uptime monitor | Planned (baseline accepted by Din, 2026-10-19) |
| 1.13a | Site template: titles, canonicals, sitemap, social cards, structured data, `llms.txt` | Planned (with the site) |
| 1.14 | Ottie pose sheet (`brand/concepts/ottie-poses.png`) | Accepted (Din, 2026-10-19); cutouts at site build |
| 1.15 | HTML checklist of everything to do, made at the end of the brainstorm | Implemented (private page; source in `handbook`) |

## Phase 2: Portfolio site

| ID | Task | Status |
|---|---|---|
| 2.1 | Write the site PRD and build plan (earlier concepts in `~/Develop/dins.dev-concepts` are reference only) | Implemented (2026-10-21): `docs/site/PRD.md`, `docs/site/PLAN.md`; Din started the build on them ("Now let's start on the plans") |
| 2.1a | Lock routes, content model and the home page skeleton (sketch in `docs/design/sketches/`) | Accepted (Din, 2026-10-19) |
| 2.2 | Lock the Ottie puppet route (Blender, mesh deformation, sprite sheets, live eyes; `docs/design/ottie/BRIEF.md`) | Accepted (Din, 2026-10-19) |
| 2.3 | Build Ottie milestone 1: idle and wave, approved by Din in the preview page | Superseded: the 2D idle and wave were Accepted (Din, 2026-10-19), then Din moved Ottie to a 3D look; the 2D work is in the private `dins-ottie` repo |
| 2.3a | 3D Ottie model from Tripo (Smart Mesh P2.0, multi-view), then cleanup, eyes, glasses, fur and rig in Blender | Accepted (Din, 2026-10-20: base, look and rig) |
| 2.3b | 3D idle and wave, rendered, packed and approved in the preview | Accepted (Din, 2026-10-20: "idle approved, wave approved"; idle 243 KB, wave 367 KB) |
| 2.4 | Build Ottie milestone 2: the remaining states (run-in, think, nod, point, shrug, poke, jump, nap, wake, talk; celebrate not built) | Accepted (Din, 2026-10-21: "All approved"; total 2,404 KB at q45) |
| 2.4a | Talk mouth: shape keys on the Tripo mouth cavity (Din chose option A) | Accepted (Din, 2026-10-21) |
| 2.4b | Lock the 3D look in `docs/BRAND.md`; keep only the sheets, manifest and preview in this repo and move the 3D source to the private `~/Develop/dins-ottie` | Implemented (2026-10-21) |
| 2.4c | A private GitHub remote for `dins-ottie` (Git LFS for the model, `.blend` files and textures) | Implemented (Din's go, 2026-10-21): `dinsdev/dins-ottie` |
| 2.10 | M0 Foundation: `site/` and `rag/` set up, checks, CI, Renovate, Workers Builds previews. Plan: `docs/site/plans/M0-foundation.md` | Planned (Oct 22 to 26); plan written, Din's answers to its 7 questions recorded |
| 2.10a | Connect Workers Builds to the repo in the Cloudflare dashboard | Planned (Din, M0) |
| 2.10b | Install the Renovate app on `dinsdev/dins.dev` | Planned (Din, M0) |
| 2.11 | M1 Pages and content: every route, content collections, SEO files, no-JS and reduced-motion baselines. Plan: `docs/site/plans/M1-pages.md` | Planned (Oct 27 to Nov 6); plan written |
| 2.11a | Copy and facts only Din can give: role line, suggested questions, bio, timeline, links, resume (D1 to D9 in the M1 plan) | Planned (Din; role line and questions by the M1 review, the rest by Dec 1) |
| 2.12 | M2 Ottie on the site: canvas player, loader, triggers, lines, Quiet Ottie. Plan: `docs/site/plans/M2-ottie.md` | Planned (Nov 2 to 12); plan written |
| 2.12a | Review Ottie's lines | Planned (Din, M2) |
| 2.12b | Approve Ottie in the preview | Planned (Din, M2) |
| 2.13 | M3 Ask Ottie: RAG build, Worker API, D1, budget, streaming UI, evals. Plan: `docs/site/plans/M3-ask-ottie.md` | Planned (Nov 6 to 22); plan written |
| 2.13a | Approve the bge-m3 model download (about 2.3 GB) | Done (Din approved, 2026-10-21) |
| 2.13b | Anthropic eval workspace ($5 a month, $10 in December) and the GitHub secret `ANTHROPIC_EVAL_API_KEY` | Planned (Din, M3; name and limits approved 2026-10-21) |
| 2.13c | A read-only Workers AI token in Din's shell for one agreement test | Approved (Din, 2026-10-21); Din creates it at M3 Task 14 |
| 2.13d | Review the sample library entries and Ottie's French fixed lines | Planned (Din, M3) |
| 2.14 | M4 Set pieces, each approved by Din. Plan: `docs/site/plans/M4-set-pieces.md` | Planned (Nov 13 to 29); plan written, Din's answers to its 10 questions recorded |
| 2.14a | Shared foundation and contact delivery (`/api/contact`, the plain letter) | Planned |
| 2.14b | Gate 1: lens intro and letter field | Planned |
| 2.14c | Gate 2: windows (the project stage) | Planned |
| 2.14d | Gate 3: paper (writing cards) | Planned |
| 2.14e | Gate 4: the studio (about) | Planned |
| 2.14f | Gate 5: the letter (folding contact form) | Planned |
| 2.14g | Set the `CONTACT_TO` secret in preview and production; confirm one real letter arrives | Planned (Din, with 2.14a) |
| 2.15 | Content track (Din): interview, library PRs, real projects, resume; freeze Dec 1 | Planned (Nov 1 to Dec 1) |
| 2.16 | M5 Hardening and launch: release evals, VoiceOver, phone check, keys, Search Console; live by Dec 12. Plan: `docs/site/plans/M5-launch.md` | Planned (Dec 1 to 12); plan written |
| 2.17 | After launch: performance optimization pass (Lighthouse performance as a gate again) | Planned (after launch) |

## Phase 3: Games pipeline

| ID | Task | Status |
|---|---|---|
| 3.1 | Use `dev.dins.<game>` bundle IDs for every new game | Planned |
| 3.2 | Game subdomain template: landing, `/support`, `/privacy`, press kit | Planned |
| 3.3 | Game conventions (identity, privacy, release flow, first paid game checklist) | Accepted (Din, 2026-10-19) |
| 3.4 | SuperOttie showcase page at `superottie.dins.dev` | Planned |

## Phase 4: Business

Tracked in the private `handbook` repo.
