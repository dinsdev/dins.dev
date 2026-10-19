# Work ledger

Decisions and why, work done, verification results, approvals, blockers, handoff status. Newest entries first.

## 2026-10-19

### Ottie puppet route (Din)

- **Locked:** Ottie is built in Blender: layered painted parts (complete underneath, so nothing reveals a seam), mesh deformation with an armature so the fur bends instead of hinging, animation authored as curves with anticipation, overlap, follow-through and secondary motion, rendered to WebP sprite sheets, with live pupils and glint drawn in the browser from a per-frame eye manifest. Spec: `docs/design/ottie/BRIEF.md`.
- **Why:** the earlier cut-out spike looked cheap (rigid pasted-on arms, a metronome wave). Din ruled out third parties (Rive animators) and AI video (not reliable enough on a live site). Blender keeps the painted canonical look, is free, and its sprite-sheet output plays the same in every browser. A redrawn vector rig was the lighter alternative, but its quality ceiling is lower and it drifts from the brand art.
- **Gate:** no Ottie state ships until Din approves it side by side in the preview page. Idle and wave come first. If Ottie is not approved by launch, the site uses a still Ottie.
- **Next:** a separate session builds it from a `/goal` prompt, on branch `feat/ottie-puppet` in its own worktree. This session continues the site PRD and plan.

### Site brainstorm: direction and home page skeleton (Din and Claude)

The site PRD and plan are still being written; these are the decisions locked so far.

- **Purpose:** a portfolio for a US master's in data science or ML/data engineering (primary) and data engineer, then AI/LLM engineer roles. The ML and AI skill shows through the work itself, not through claims.
- **Home page (approach A, chosen over a chat-only site and a classic portfolio with a widget):** Ask Ottie is the hero (name, role line, suggested questions written for recruiters and admissions, Resume/Email/GitHub/LinkedIn visible on first paint), with real crawlable pages underneath. A chat-only page would be invisible to search, to `llms.txt` and to screen readers, and would lose readers who don't type.
- **Ask Ottie:** a RAG pipeline over Din's approved library, answered by Claude Haiku. One answer-provider interface with three backends: a fake (tests and CI), Claude Code on Din's membership (local development, terms to be checked first), the Anthropic API (staging and production). Budget: a $100 spend cap, rate limits and Turnstile. Answers in English, and in French when asked in French; the site itself stays English for v1.
- **Library:** sources are GitHub repos, resume, LinkedIn, the undergrad thesis, and an in-depth interview by a Claude agent. Nothing reaches Ottie without Din's sign-off; raw transcripts stay in `handbook`; a deny-list (visa status, finances, personal life) gets a polite decline. The interview question bank plus Din's approved answers doubles as the eval set.
- **Pushbacks Din accepted:** a brand-native "Look closer" lens intro instead of the React Bits Hyperspeed effect (heavy WebGL, delays the first 30 seconds, and its neon glow breaks the calm brand); React Bits is inspiration only, we write our own versions; one quiet motion budget (letter field, small teal click sparks, scroll reveals, Ottie); Ottie is a 2D cut-out puppet in the canonical style, not pixel art, and stays quiet while someone types or reads; writing lives at `dins.dev/writing`, not a `blog.` subdomain, so everything ranks for Din's name on one domain.
- **Content timing:** real projects (ML, pipelines, data science, each with a visual demo) and the interview come later. `passfx`, `claude-runner` and `claudehome` are placeholders until then. A content freeze around December 1 is proposed.
- **Routes and content model (section 1, locked):** `/`, `/work`, `/work/<project>` (with an "Ask Ottie about this project" bar that only searches that project), `/writing` and posts with RSS, `/about`, `/contact`, `/privacy`, a 404 with Ottie, plus the agreed SEO files. Typed content collections for projects, writing and the Ottie-only library; Ottie's corpus is the library plus the pages. Not in v1: a French site, comments, a newsletter, `/uses`.
- **Home page skeleton (Accepted by Din):** one visual family. Lens: the intro pulls the page into focus through Ottie's right lens, and a faint mono letter field resolves into real library words near the cursor (and sweeps while Ottie retrieves). Windows: projects on a scroll-pinned center stage, each tilting in and landing in focus with its demo inside a browser window. Paper: writing as floating cards that drift in and settle. Studio: About as a dark studio where a laptop unfolds, a terminal types `whoami`, and the camera dollies into the screen (CSS 3D first; a Blender-rendered frame sequence is an optional upgrade). Letter: contact as a sheet of paper that folds into an envelope, gets an Ottie wax seal and is carried off by Ottie.
- **Sketch:** `docs/design/sketches/home-sketch.html` (built by `build.py` from `home.template.html`, the real tokens and logo). A rough reference for layout and motion, not final design or copy.
- **Verification:** rendered with headless Chrome in light and dark at 1440 px, including forced scroll states for the stage, studio and letter. Limits: headless Chrome will not go below about 500 px wide, so phone layouts are unchecked, and it stops its clock mid-animation, so the full letter fold was only checked by Din live.

### Going public (Din)

- **Decision:** `dins.dev` is public from today instead of at launch, so progress is visible as it happens.
- **Before the first push:** a scan found account-security details and personal plans in the docs. Din had them moved to a new private `handbook` repo, and the unpushed history was rewritten so they never appear here. The public repo starts from one initial commit; the earlier local history is archived privately.
- **Repo setup:** squash merge only, branches deleted after merge, secret scanning and push protection on, Dependabot alerts on, and a ruleset on `main` (pull request required, no force push or deletion, linear history).

### Brand guide page (Claude)

- Built `brand/brand-guide.html` from `brand/tools/brand-guide.template.html` with `brand/tools/guide.py` (inlines tokens.css and theme-following marks, embeds every image) and published it privately: https://claude.ai/artifact/R8qLpurwsRu6PHmZzeDy2t. Sections: logo (with clear space, minimum sizes and don'ts), icons, social cards, color (live contrast ratios, click to copy), typography (live fluid scale), Ottie, voice, space and motion, files. The page runs on the dins tokens themselves.
- New defaults introduced and recorded in BRAND.md: clear space and minimum sizes.
- Pose sheet embedded as a 1400 px WebP (`brand/concepts/ottie-poses-web.webp`, 110 KB) instead of the 1.8 MB PNG. `brand/tools/sheet.py` now embeds PNG and WebP too.
- Verification: script syntax check; one Quick Look render (dark theme) looked right. Quick Look does not run scripts, so the swatches and spacing scale were not seen rendered; check them on the live page.

### Checklist sync

- Read the live checklist first, kept every tick Din had made, marked the finished brand work done and republished. Fixed the self-save baking the "Saving..." status into the page.

### Ottie pose sheet

- Din approved one Codex image (reference: canonical Ottie). Result `brand/concepts/ottie-poses.png`: five poses on white, on model (same glasses, proportions and style), each separable for cutouts. First try, no second image used. Din approved it. With this, every brand item is locked: type guidelines and scale, color, logo, style rules, tokens, icons, social cards and Ottie's poses.

### Social cards (Din)

- **Locked:** A (Paper) is the default card for every page; C (Paper with Ottie) for devlogs and game posts. B (Charcoal) dropped for thumbnail legibility. Why: recruiters and admissions see these in LinkedIn and email, where a clean title wins; Ottie belongs on the playful content. `brand/tools/sheet.py` now embeds SVGs into any template, which the cards page uses.

### Type scale, tokens and icons

- **Type scale locked (Din):** ten steps from Display (48 to 76 px) to Data (12.5 to 13 px), fluid between 375 and 1280 px, headings at weight 500 below the 600 wordmark, H4 in the sans, body capped at 66 characters. Rules added: curly quotes in display text, tabular digits. Specimen rows are static HTML because Quick Look does not run scripts.
- **Tokens (Claude):** `brand/tokens/tokens.json` plus generated `tokens.css`. Spacing, radius, layout and motion values are Claude's defaults, recorded in BRAND.md.
- **Icons (Claude):** `brand/tools/icons.py` rasterizes with cairosvg (needs Homebrew cairo; run with `DYLD_FALLBACK_LIBRARY_PATH=/opt/homebrew/lib`). 16 px check, enlarged on light and dark tab colors: the solid tile reads as glasses; the earlier transparent, theme-following `favicon.svg` was about 4 px tall and faded on both, so `favicon.svg` is now the same solid tile. Din approved the solid-tile favicon.

### First commit (Din's go)

- First local commit of the fresh repo: brand files, tools and docs.

### Launch checklist (Claude)

- Published a private, self-saving checklist page of every task in order. It covers private tasks too, so its source and builder live in the private `handbook` repo.

### Apple and game conventions (Din)

- **Locked:** `dev.dins.<game>` bundle IDs, `support@dins.dev`, one game page template (landing, support, privacy, press kit), collect-nothing privacy by default, TestFlight-first release flow, and a first-paid-game checklist (Small Business Program, banking and tax forms, EU trader status, encryption flag). Monetization, age rating and countries are decided per game.

### SEO and analytics (Din)

- **Locked:** baseline built around ranking for Din's name (Person structured data with `sameAs` links), Search Console domain property plus Bing, branded social cards, `llms.txt`, Cloudflare Web Analytics instead of Google Analytics (no cookies, no banner), a free uptime monitor. No keyword strategy.

### Tracking and docs (Din)

- **Locked:** TASKS.md stays the single plan and board; GitHub Issues only for bugs, ideas and outside feedback; README in every repo; the ledger is the decision log; changelogs for games only; shared conventions live in `handbook`. Why: two to-do lists drift apart, and Din's global rules already make the docs the source of truth.
- **Added:** `README.md` with the lockup (light and dark via `<picture>`), contents, regeneration commands and license notes.

### Checks, CI and dependencies (Din)

- **Locked:** one `check.sh` shared by laptop and CI; pre-commit hooks with gitleaks (GitHub secret scanning does not cover private repos on the free plan); GitHub Actions; Cloudflare Git integration for previews (no Cloudflare token in GitHub); Renovate weekly; Unity tests local-only until a game nears release.

### Branching, PRs and commits (Din)

- **Locked:** trunk-based with short-lived branches, a PR for every change, squash merge, Conventional Commits, SemVer tags for games only. Why: PRs give checks, preview links and a written record that doubles as portfolio evidence. Branch protection comes from a GitHub ruleset now that the repo is public.

### Repo map (Din)

- **Locked:** `dins.dev` (made public right away on 2026-10-19, see below), `handbook` (private), `.github` (public), one private repo per new game, `template-site` and demos (public when ready). SuperOttie's code stays in Din's personal account, with a showcase page at `superottie.dins.dev` in this repo. Nothing is created on GitHub yet.

### Logo (Din and Claude)

- **Approved (Din):** wordmark, lens, lockup, app icon and favicon, then the Ottie seal. The brand files are complete.
- **Seal built:** Din approved one Codex image (`brand/concepts/ottie-seal-draft.png`, prompt beside it, references: canonical Ottie and the logo direction sheet). `brand/tools/seal.py` snaps it to five Ottie colors, keys out the background, traces it with vtracer, snaps the traced fills again and wraps the art in a ring drawn in code. Outputs: `seal-light.svg`, `seal-dark.svg`, `avatar.svg` (no ring, for platforms that crop to a circle). First fit clipped the ears and whiskers on the ring; the art is now scaled to 0.84 and dropped so the shoulders run off the bottom.
- **Tooling note:** vtracer segfaults on Python 3.14, so `seal.py` runs on Python 3.12 through uv.
- **Logo sheet:** `brand/tools/sheet.py` builds `brand/logo/logo-sheet.html` from `brand/tools/logo-sheet.template.html` with every SVG embedded, because the browser pane's local-file view cannot load linked images and the preview server list only reads the shared `~/Develop/.claude/launch.json` (outside this project, left untouched).
- **Verification:** seal and avatar rendered with Quick Look and checked by eye at 600, 300 and 48 px.

- **Wordmark spec (Din):** Fraunces weight 600, SOFT 50, picked from a 3 x 3 weight and softness sheet (`brand/logo/explorations/wordmark-variants.html`).
- **Built:** `brand/tools/wordmark.py final` shapes "dins." with HarfBuzz (kerning on) and writes true vector paths, so the SVGs need no font. Outputs in `brand/logo/`: wordmark (display and small masters), lens, lockup, each in light, dark and mono; app icon (paper lens on ink, 1024 canvas); favicon (follows the system theme). Fraunces is vendored in `brand/fonts/` with its OFL license.
- **Lens iteration:** a rim matching the Fraunces stem (0.24 of the lens diameter) read as two donuts and pushed the glint onto the rim. Final rim is 0.14 of the diameter (0.19 for the favicon so it survives 16 px), with the glint inside the right lens.
- **Verification:** rendered the logo sheet, app icon and favicon with Quick Look and checked them by eye. The favicon was only checked at 64 px so far; 16 px needs a check in a real browser tab.

### Typography (Din)

- **Fonts locked:** Fraunces (display), Instrument Sans (text and UI), JetBrains Mono (mono). Chosen from four systems compared side by side in light and dark (`brand/specimen/type-options.html`). Next: draw the wordmark from Fraunces outlines.

### Repo map and reopened items (Din)

- **SuperOttie stays personal** in Din's own GitHub account and is not part of dins. Every new game goes in the `dinsdev` org with a `dev.dins.<game>` bundle ID.
- **Repo map revised (still Proposed):** `dins.dev` private until launch, then public; demos public when ready.
- **Reopened:** Din considers the fonts, typography and the real logo not decided yet. The earlier type trio and the logo sheet are now candidates and direction, not final. Next: compare font options side by side, then draw the real logo in the chosen font.

### Fresh start

- **Din's call:** the earlier repo held website concepts that are not finalized, so it was renamed to `~/Develop/dins.dev-concepts` (kept intact, with its own git history) and this repo was started clean with only what was decided in the brainstorm. Carried over: the approved logo direction sheet and its prompt, the Ottie reference art, and the type specimen Din approved. Nothing was pushed anywhere.
- Note: the shared `~/Develop/.claude/launch.json` entry `dins-puppet-spike` still points at the old path and needs updating if that spike is ever previewed again.

### Brand and identity decisions (Din)

- **Brand:** "dins" for everything. dins.dev is the hub; games live on subdomains such as `superottie.dins.dev`.
- **Handles:** `dinsdev` on GitHub (organization), YouTube, TikTok and X. `dins` was taken on GitHub by an active personal account since 2011. `dinsdev` beat `dins-dev` because X and Instagram do not allow hyphens.
- **Platforms:** GitHub, YouTube, TikTok, X. LinkedIn stays personal.
- **Email addresses:** `din@`, `dinesh@` (alias), `hello@`, `support@`, catch-all, forwarded to Din's personal inbox. Sending through "Send mail as" on a free provider to start.
- **Domain:** buy `dins.dev` for 4 years on Cloudflare. Already have a Cloudflare account and an Apple Developer account.
- **Timeline:** applications open mid-January 2027, so the portfolio goes live by mid-December 2026.
- **Brand system:** logo system, palette, warm charcoal dark mode, type trio, Ottie rules and voice with tagline "Look closer." All locked; details in `docs/BRAND.md`.

### Why some brand calls went the way they did

- **Logo:** of four directions (`brand/concepts/logo-directions.png`), the wordmark matches the site's serif headline, the lens holds up at favicon size where the seal does not, and the seal keeps Ottie's charm for game and social use. The d-lens monogram read as a broken letter and was dropped.
- **Dark mode:** Din preferred a calm, Claude Code style dark over a glowing ink-teal look. The accent stays dins teal rather than Claude orange, so it borrows the feel without imitating Anthropic's brand.
- **Voice:** "I", never "we", because Din is one person and a fake "we" costs trust with admissions and clients.

### Verification

- Contrast ratios computed with the WCAG formula for every text color on its background (numbers in `docs/BRAND.md`). Amber fails as text on the light background (2.0:1), so it is decoration only there.
- `dins.dev` availability: the .dev registry RDAP returned 404 (not registered) on 2026-10-19.
