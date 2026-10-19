# dins: Setup Plan

Status: Draft from the 2026-10-19 brainstorm
Deadline that drives everything: portfolio live by mid-December 2026 (applications open mid-January 2027).

## Approach

Set up the skeleton properly and grow the rest when it is needed. Each phase ends with something Din can check. The order puts what admissions will see (the portfolio) ahead of things that only matter later (games, business paperwork).

## Phases

| Phase                            | Outcome                                                               | Depends on                       |
| -------------------------------- | --------------------------------------------------------------------- | -------------------------------- |
| 0. Foundation                    | Accounts secured, domain, DNS hygiene, email, handles, GitHub org     | none                             |
| 1. Brand production and workflow | SVG logos, design tokens, repos on GitHub, checks and preview deploys | 0                                |
| 2. Portfolio site                | dins.dev live (planned in its own PRD)                                | 1                                |
| 3. Games pipeline                | Per-game subdomain template, release flow                             | 1                                |
| 4. Business                      | Business name, bank account, bookkeeping, templates                   | first client or revenue in sight |

## Phase 0: Foundation

### Accounts and security

- Account security (password manager, passkeys, recovery setup) and the accounts inventory are kept in the private `handbook` repo, never here.
- `@dins.dev` addresses are for public contact. Logins and recovery use a separate personal address, so a domain problem can never lock Din out.

### Domain and DNS

- Register `dins.dev` on Cloudflare Registrar for 4 years with auto-renew on. As of 2026-10-19 the .dev registry's RDAP lookup returned "not found", so it appears available.
- Notes: .dev is HTTPS-only (browsers enforce it). Cloudflare Registrar requires Cloudflare DNS.
- Turn on DNSSEC. Add CAA records (which certificate authorities may issue for the domain). Publish `/.well-known/security.txt` once the site exists.

### Email

Receiving through Cloudflare Email Routing (free), forwarding to Din's personal inbox:

| Address            | Purpose                                |
| ------------------ | -------------------------------------- |
| `din@dins.dev`     | Din: applications, recruiters, clients |
| `dinesh@dins.dev`  | Alias of `din@` for formal contexts    |
| `hello@dins.dev`   | Public contact on the site             |
| `support@dins.dev` | App Store support for every game       |
| catch-all          | Everything else                        |

Sending: the personal inbox's "Send mail as" through a free outgoing mail (SMTP) provider, authenticated for dins.dev. SPF, DKIM and DMARC records set and checked. Upgrade to a paid mailbox (Fastmail, Google Workspace) only if volume grows.

Verification: send from `din@dins.dev` to an outside address and confirm SPF, DKIM and DMARC all pass in the message headers.

### Handles

- `dinsdev` everywhere: GitHub (organization), YouTube (Brand Account channel), TikTok (personal/creator account), X. Display name "dins". Bios, avatars and posts stay empty until the brand assets exist, then all profiles get filled at once.
- Optional: `@dins.dev` on Bluesky, verified through DNS.

## Phase 1: Brand production and workflow

### Brand production

- Decide the fonts, then draw the real logo as clean SVG: the wordmark "dins." (from the chosen display font, tuned spacing, teal period), the lens (two circles and a bridge, teal glint) and the Ottie seal. Use the palette tokens in `docs/BRAND.md`.
- Export a favicon set, app-icon sizes and social preview templates.
- Design tokens as a file the site imports (colors, fonts, light and dark).
- Ottie pose sheet (wave, thinking, celebrating, shrug, sleeping), one Codex image, generated when the site build needs it.
- Fill all social profiles at once with avatar (the seal), name and bio.

### Repo map (locked by Din, 2026-10-19)

| Repo in `dinsdev`          | Visibility | Holds                                                                                  |
| -------------------------- | ---------- | -------------------------------------------------------------------------------------- |
| `dins.dev` (this repo)     | Public (since 2026-10-19) | Brand assets and docs now; the portfolio site and later the game subdomain pages |
| `handbook`                 | Private    | Account security, business and personal notes, the private checklist, templates |
| `.github`                  | Public     | Org profile README and default files (SECURITY.md, issue templates)                    |
| one repo per new game      | Private    | The Unity project for each new dins game                                               |
| `template-site` and demos  | Public when ready | One repo per client demo, generated from a template repo                               |

SuperOttie's code stays a personal project in Din's own GitHub account. It still gets a showcase page at `superottie.dins.dev`, which lives in this repo with the other game pages. Every new game goes in the `dinsdev` org.

Reasoning: Din chose to make `dins.dev` public from the start (2026-10-19) so progress is visible as it happens; a history with docs, tests and a decision ledger is a hiring signal. Being public also makes GitHub secret scanning, push protection and branch rulesets free. Private details live in `handbook`. Games are commercial, so private. Game web pages share the brand and Cloudflare setup, so they join this repo as a new workspace when the first one is due (no restructuring before then). Demos stay separate so each can be handed to or forked for a client.

### Workflow conventions (to be decided next, one at a time)

- **Branching, PRs and commits (locked by Din, 2026-10-19):**
  - Trunk-based: `main` always deployable; short-lived branches named `type/short-description` (`feat/hero`, `fix/favicon-16px`). Checkpoint commits on branches are fine.
  - A PR for every change, even solo: checks run, Cloudflare posts a preview link, and the PR records why. PR template: what changed, why, how it was tested, screenshots for visual changes. Review: Din plus Claude's `/code-review` for anything non-trivial.
  - Squash merge only, delete the branch after. The PR title becomes the commit on `main`.
  - Conventional Commits: `type(scope): what changed`, types `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`.
  - Protecting `main`: a GitHub ruleset requires a pull request, blocks force pushes and deletion, and keeps history linear. Required status checks are added once CI exists.
  - Versions: the site deploys continuously from `main`; games use SemVer tags and a changelog.
- **Checks, CI and dependency updates (locked by Din, 2026-10-19):**
  - One `check.sh` runs every check; CI runs the same script. Heavier checks (Playwright, Lighthouse) may run in CI only so the local loop stays under about 2 minutes.
  - pre-commit hooks (the Python `pre-commit` framework): format and lint changed files, gitleaks secret scan (GitHub's own secret scanning and push protection are on too).
  - Checks: Prettier and ESLint (web), Ruff (Python), `astro check` and TypeScript, Vitest and pytest, Playwright smoke tests with axe (zero violations), Lighthouse CI (performance at least 90, accessibility 100, SEO 100), lychee link check.
  - CI: GitHub Actions on every PR (2,000 free minutes a month on private repos). Previews: Cloudflare's Git integration builds every branch and comments the preview link, so no Cloudflare token lives in GitHub.
  - Dependencies: Renovate opens one grouped PR a week; Dependabot security alerts stay on.
  - Games: Unity tests run locally before merge until a game nears release; GameCI is added when it pays off.
- **Tracking and docs (locked by Din, 2026-10-19):**
  - `docs/TASKS.md` is the plan and the board. PRs reference task IDs. No GitHub Projects board until collaborators or clients need one.
  - GitHub Issues only for work outside the plan: bugs, ideas, and outside feedback once repos are public. Templates: bug, idea. Labels: `bug`, `idea`, and one area label (`brand`, `site`, `games`, `infra`).
  - Every repo: `README.md` for humans, `AGENTS.md` and `CLAUDE.md` for agents, the four project docs. The work ledger is the decision log (no separate ADR files). `CHANGELOG.md` for games only, generated from Conventional Commits.
  - Shared conventions are written once in `handbook`; each repo's AGENTS.md links to them.
- Environments: local, per-PR preview, production. Secrets only in Cloudflare and GitHub secret stores.

### SEO and analytics baseline (locked by Din, 2026-10-19)

The search that matters most is Din's own name: dins.dev, Din's GitHub and Din's LinkedIn should rank first and read as one person.

- Google Search Console domain property (one DNS record covers every subdomain) and Bing Webmaster Tools (imported from Search Console; it also feeds DuckDuckGo and several AI assistants).
- Every page: unique title and description, canonical URL, sitemap, `robots.txt`, a branded social preview card template (paper, wordmark, page title).
- Structured data: Person for Din with `sameAs` links to GitHub, LinkedIn, YouTube, X and TikTok; Organization for dins with the logo; VideoGame on each game page with its App Store link.
- `llms.txt`: a plain summary of Din and the work for AI assistants.
- Cloudflare Web Analytics (free, no cookies, no banner). No Google Analytics.
- A free uptime monitor that emails Din if dins.dev goes down.
- Not doing: keyword strategy or SEO blogging.

## Phase 3: Games pipeline (conventions locked by Din, 2026-10-19)

- **Identity:** the Apple Developer account is most likely individual, so the App Store seller name is Din's legal name until there is a corporation. The brand appears through the marketing and support URLs, a "by dins" card on the splash or credits screen, and the trailer end card ("Look closer." plus the seal).
- **Bundle IDs:** `dev.dins.<game>` for every new game (permanent once shipped). SuperOttie is personal and keeps its own.
- **Support email:** `support@dins.dev` for every game.
- **Game page template:** `<game>.dins.dev` with a landing page (trailer, screenshots, App Store badge), `/support` (FAQ, support email), `/privacy` (required by App Store Connect) and a press kit (icon, screenshots, short description).
- **Privacy:** collect nothing by default. No third-party analytics or ad SDKs, so the App Store label is "Data Not Collected", there is no tracking prompt, and the privacy policy is one paragraph. Ads would be a deliberate per-game decision.
- **Release flow:** TestFlight internal, then TestFlight with a few friends, then App Review. SemVer tags, build number = commit count, a changelog.
- **First paid game:** apply to Apple's Small Business Program (15 percent commission instead of 30) before the first sale; banking and tax forms in App Store Connect need the Phase 4 bank account; EU trader status means a public contact address in the EU, so use a business mailing address or leave the EU out at first (per game); set the "no non-exempt encryption" flag once if the game only uses standard HTTPS.
- **Per game, decided later:** paid up front or free with in-app purchases, age rating, countries.
- Later: Universal Links served from the game's subdomain.

## Phase 4: Business (later)

Business, tax and timing notes are kept in the private `handbook` repo. In short: register the business name only when real paid work appears, keep a separate account and simple bookkeeping, have contract and invoice templates ready, and book one accountant session before the first paid client.

## Verification approach

Each phase's checks are listed in its section and in `docs/PRD.md` section 5. Results go in `docs/WORK_LEDGER.md`.
