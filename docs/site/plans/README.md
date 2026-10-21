# Site plans: the shared contract

Six plans, one per milestone, written in parallel on 2026-10-21. This file is where they meet. **Where a plan disagrees with this file, this file wins**, and the plan is amended to match (the amendments are listed per plan below, with their status).

| Plan | Milestone | Dates |
|---|---|---|
| [M0-foundation.md](M0-foundation.md) | Foundation | October 22 to 26 |
| [M1-pages.md](M1-pages.md) | Pages and content | October 27 to November 6 |
| [M2-ottie.md](M2-ottie.md) | Ottie on the site | November 2 to 12 |
| [M3-ask-ottie.md](M3-ask-ottie.md) | Ask Ottie | November 6 to 22 |
| [M4-set-pieces.md](M4-set-pieces.md) | Set pieces | November 13 to 29 |
| [M5-launch.md](M5-launch.md) | Hardening and launch | December 1 to 12 |

Requirements stay in `docs/site/PRD.md`, milestones in `docs/site/PLAN.md`, status in `docs/TASKS.md`. An implementer reads this file, then the plan for their milestone.

## Rule for names

The milestone that lands first owns a name; later milestones import it. If a later milestone needs more, it extends the owner's file rather than writing a second one. A name not listed here is local to its plan.

## The seams

### Toolchain and config (owner M0)

| What | Name |
|---|---|
| Worker | `dins-site`, custom entry `site/src/worker.ts` exporting `{ fetch }` (M3 adds `scheduled`) |
| Bindings | `ASSETS`, D1 `DB` (databases `dins-site` and `dins-site-preview`) |
| Runtime env var | `SITE_ENV`: `production`, `preview`, `local` (`.dev.vars`), `test` (Worker tests) |
| Previews | the `previews` block in `site/wrangler.jsonc` (Din, 2026-10-21). Every binding and var is declared at the top level **and** again under `previews`. There is no `env.preview`. |
| Workers tests | `@cloudflare/vitest-plugin` 1.4 with Vitest 4.1 (Din, 2026-10-21) |
| Scripts | site `dev`, `build`, `serve` (wrangler dev on 127.0.0.1:8787), `check`, `test`, `test:unit`, `test:worker`, `test:e2e`; root `./check.sh [--e2e]`; CI jobs `check` and `e2e` |
| Base layout | `site/src/layouts/BaseLayout.astro` (M0 creates it, M1 fills it). Not `Base.astro`. |
| Global styles | `site/src/styles/global.css` (M0); M1 adds `site/src/styles/site.css` |
| Python | uv project `rag/`. M0's skeleton package `dins_rag` (`dins_rag.paths.SITE_ASK_DIR`) stays; M3 adds `ottie_rag` beside it, and M3's Task 9 test keeps the two paths equal. |
| Health | `GET /api/health` returns `{ ok, service: "dins-site", env: SITE_ENV }` |

### Build-time deploy (owner M0, new)

Four plans each invented their own way to tell a production build from a preview build (M1 `resolveBuildFlags`, M2 `labEnabled`, M4 `PUBLIC_DEPLOY_ENV`, M5 `PUBLIC_DEPLOY`). There is one:

```ts
// site/src/lib/deploy.ts (pure; astro.config.mjs and tests import it)
export type Deploy = "local" | "preview" | "production";

/** Only Workers Builds sets WORKERS_CI, so a production build can only come from there. */
export function deployFromEnv(ci: string | undefined, branch: string | undefined): Deploy {
  if (ci !== "1") return "local";
  return branch === "main" ? "production" : "preview";
}
```

- `astro.config.mjs` defines `__DINS_DEPLOY__` as `JSON.stringify(deployFromEnv(process.env.WORKERS_CI, process.env.WORKERS_CI_BRANCH))`; `site/src/env.d.ts` declares it; `site/src/lib/deploy-env.ts` exports `export const DEPLOY: Deploy = __DINS_DEPLOY__;` for site code.
- GitHub Actions and local builds are `local` (they never deploy).
- M0 checks on the first preview build that the page reports `preview` (BaseLayout writes `<meta name="dins-deploy" content={DEPLOY}>`).
- Consumers: M1's drafts flags (`showDrafts` is true on `preview`, or on `local` with `DINS_SHOW_DRAFTS=1`; `noindex` is true on `preview`; `DINS_SHOW_DRAFTS=1` on `production` throws), M2's lab pages (built unless `production`; `DINS_LABS` override kept), M4's release flags (`preview` releases are full on `local` and `preview`, calm on `production`), M5's headers, CSP and analytics beacon.
- This is build time only. Worker code reads `SITE_ENV` at runtime.

### Pages and markup (owner M1)

| What | Name |
|---|---|
| Layout props | `SeoProps & { current?: NavKey }` from `site/src/lib/page.ts` |
| Head slot | `BaseLayout.astro` has `<slot name="head" />` inside `<head>` (M4's `MotionHead.astro` uses it) |
| No-JS flag | `<html class="no-js">`, swapped to `js` by an inline script |
| Set-piece hooks | `data-setpiece="lens|windows|paper|studio|letter"` on `#top`, `#work`, `#writing`, `#about`, `#contact`; `data-setpiece="studio-screen"` on `/about`. Not `data-piece`. |
| Ask slot | `AskSlot.astro`, `{ scope: "site" } | { scope: "project"; project }`, renders `.ask-slot[data-ask-scope][data-ask-project]`; suggested answers as `#suggested details[data-suggested-id]` |
| Ottie slot | M1's `OttieSlot.astro` is a placeholder. M2's Task 15 replaces every `<OttieSlot placement=…>` with M2's `<Ottie context=…>` (`hero` becomes `home`) and deletes `OttieSlot.astro`. |
| Content | `getVisibleProjects()`, `getVisiblePosts()`, `getVisibleSuggested()` in `site/src/lib/collections.ts`; `status: published` is the only "reviewed by Din" flag, for every collection |
| SEO files | `/sitemap.xml` (the site writes it; there is no `@astrojs/sitemap` and no `sitemap-index.xml`), `/robots.txt`, `/llms.txt`, `/.well-known/security.txt`, all generated routes in `site/src/pages/`. The sitemap lists `INDEXABLE_STATIC_ROUTES` plus content, so `/contact/sent/` and `/contact/not-sent/` are never in it. |

### Contact (owner M1; M4 builds the endpoint)

One module, `site/src/lib/contact.ts` (M1, Task 7). M4 imports it; there is no `site/src/lib/contact/parse.ts`.

- `CONTACT_FIELDS`: `message`, `reason`, `name`, `email`, honeypot `website`, Turnstile `cf-turnstile-response`.
- `CONTACT_LIMITS = { name: 100, email: 254, message: 4000 }` (M4's message limit; the PRD sets none and admissions letters run long).
- `REASONS` with labels "A role", "Admissions", "Just saying hi".
- `CONTACT_REDIRECTS = { sent: "/contact/sent/", notSent: "/contact/not-sent/" }`. There is no `/contact/error/`.
- `parseContact(form: FormData | URLSearchParams): ContactResult`, which also strips control characters other than newline and tab (from M4's Task 5 tests).
- M1 creates both landing pages. `/contact/not-sent/` carries a `mailto:din@dins.dev` link, and the form carries a `<noscript>` note, because a post without JavaScript has no Turnstile token and is never accepted (Din, 2026-10-21, M4 decision 1).
- The recipient comes only from the `CONTACT_TO` Worker secret (Din, 2026-10-21, M4 decision 2).

### Ottie (owner M2)

`site/src/ottie/events.ts` exactly as M2's "The public interface": `cueOttie(type, extra?)` dispatches `ottie:cue` with `detail.type`; `onOttieCue`, `onOttieState` (`detail.state`); attributes `[data-ottie-avoid]` and `[data-ottie-host]`. There are no state-named cues (`"point"`, `"jump"`, `"think"`) and no `prefetchOttie`: callers say what happened, M2's director decides what Ottie does and what to fetch.

- **Ask (M3):** `ask:focus`, `ask:typing`, `ask:submit`, `ask:stream`, `ask:answer` (`{ sources }`), `ask:unknown`, `ask:resting`, `ask:error`, `ask:reset`. No talk while streaming.
- **Letter (M4):** `letter:open` (in view: point), `letter:ready` (form filled in: fetch jump), `letter:sent` (jump). The envelope flies off after `onOttieState` reports `idle` following `jump`.
- **A second Ottie by the letter is decided** (Din, 2026-10-21, M4 decision 4): home shows the hero Ottie and a second Ottie beside the letter in `#contact`; `/contact` shows only the letter Ottie. M2's existing `context="contact"` is the letter Ottie in both places (no new context, no `instance` prop):
  - `ask:*` cues go to `home` and `project` hosts; `letter:*` cues go to `contact` hosts.
  - The greeting (run-in, wave, first line) plays only in the page's first host; a `contact` host starts in idle.
  - All hosts on a page share one loader, so a sheet is fetched and decoded once.
  - At most one host animates at a time (the one most in view); any other shows its still.
- M2 computes its own mode (reduced motion, Save-Data, `deviceMemory <= 2`, the same thresholds as M4's `motion.ts`) and also treats `<html data-motion="calm">` (M4's `?calm` review switch) as reduced.
- Point faces screen right only until Din approves mirroring (M2 open question 3).

### Ask Ottie (owner M3)

| What | Name |
|---|---|
| State event for M4 | `ask:state` on `window`, `detail.phase` in `idle | retrieving | streaming | done | dont-know | resting | error` |
| Turnstile, server | `site/src/lib/turnstile.ts`: `verifyTurnstile({ token, secret, remoteip, action, hostnames, fetcher, timeoutMs }): Promise<{ ok: boolean; codes: string[] }>` |
| Turnstile, browser | `site/src/lib/turnstile-client.ts` (shared with the letter, so not under `lib/ask/`): `loadTurnstile(): Promise<TurnstileApi>`, `siteKey()`, `TURNSTILE_TEST_SITEKEY` |
| Turnstile names | secret `TURNSTILE_SECRET_KEY`, build variable `PUBLIC_TURNSTILE_SITE_KEY`, var `TURNSTILE_EXPECTED_HOSTNAMES` |
| Whichever of M3 or M4 reaches Turnstile first | creates both files with these signatures; the other imports them |
| Answer backend | real only when `ASK_BACKEND=anthropic` and `SITE_ENV` is `production` or `local`. There is no `ASK_LIVE_HOSTS`. |
| Budget | var `ASK_DAILY_BUDGET_USD` (default `"1"`); table `budget_daily(day TEXT PRIMARY KEY, spent_nano_usd INTEGER)`; question log `question_log` (migration `0001_ask.sql`) |
| Routes | `POST /api/ask`, `POST /api/ask-feedback` |
| Index | `site/public/ask/index-v1.bin`, committed; layout in `rag/INDEX_FORMAT.md` |
| CLI | `ottie-rag` (`check`, `check --release`, `eval-retrieval`, `fixtures`) |
| Answer evals | workflow `answer-evals`, `workflow_dispatch` input `judge` (`haiku` or `sonnet`), secret `ANTHROPIC_EVAL_API_KEY`, artifact `answer-eval-report` |

### Set pieces (owner M4)

| What | Name |
|---|---|
| Release flags | `site/src/lib/setpieces/flags.ts`: `RELEASES`, `pieceEnabled(piece)`, values `calm`, `preview`, `full` (not `site/src/config/set-pieces.ts`) |
| Motion | `site/src/lib/motion.ts` (`resolveMotion`, `currentMotion`, `onMotionChange`) and `<html data-motion="full|calm">` set before first paint by `MotionHead.astro` |
| JavaScript budget | `pnpm --dir site budget` (`site/scripts/budget.ts`), run by `check.sh` after the build: 100 KB gzipped for the initial module graph plus inline scripts, never GSAP |

### Tests (owner M0, extended by M1)

- The Playwright web server stays M0's: `pnpm build && pnpm serve` (wrangler dev, so `/api/*` works), waiting on `/api/health`, with `DINS_SHOW_DRAFTS=1` added by M1. Not `astro preview` on 4321.
- The `chromium` project stays and is the default: it runs every spec that no other project claims (the M2, M3, M4 and M5 specs land there). M1 adds `dark`, `no-js`, `reduced-motion` and `phone` for its own specs. M1's `light` project is `chromium`.
- Unit tests in `site/tests/unit/` (Node), Worker tests in `site/tests/worker/` (workerd), end to end in `site/tests/e2e/`.

### Security headers and CSP (owner M5)

- One module, `site/src/lib/security/headers.ts`, with `csp.ts`, the build-time integration that merges into `_headers`, and middleware for Worker responses. M2's `/ottie/*` caching rule in `site/public/_headers` is kept by the merge.
- Astro's `security.csp` hashes inline `<script>` and `<style>` elements, so the inline scripts in M1 (theme, `no-js`), M2 (pre-paint) and M4 (`MotionHead`, `LensIntro`) need no extra work.
- **No `style="…"` attributes in server-rendered HTML.** The CSP has no `unsafe-inline` or `unsafe-hashes` for styles, so the browser drops them. Use classes, an inline `<style>` element (hashed), or set properties from JavaScript (CSSOM writes are allowed). This affects M2's Ottie box and M4's stage (`--n`), paper cards (`--r`, `--dy`) and studio screen (`view-transition-name`).
- Outside hosts: `challenges.cloudflare.com` (Turnstile), `static.cloudflareinsights.com` and `cloudflareinsights.com` (Web Analytics, production only).

## Amendments by plan

Each plan session applies its own list to its own file. Status: **Pending** until the amended plan is merged here.

- **M0:** add `site/src/lib/deploy.ts`, `deploy-env.ts`, the `__DINS_DEPLOY__` define and the `dins-deploy` meta, with tests, and the preview check in Task 13. Pending.
- **M1:** `Base.astro` to `BaseLayout.astro` (M0 creates it; M1 modifies). `<slot name="head" />`. Drafts flags read the shared deploy. Contact: message limit 4000, control-character stripping, `notSent` and `/contact/not-sent/` (with the mailto link) in place of `/contact/error/`. Playwright: keep M0's server and the `chromium` project as above. Pending.
- **M2:** `Base.astro` to `BaseLayout.astro`. `context="contact"` also placed in the home `#contact` section, and the multi-host rules above. Task 15 swaps `OttieSlot`. Lab pages read the shared deploy. No `style` attribute on the Ottie box. Respect `data-motion="calm"`. Pending.
- **M3:** move the browser Turnstile loader to `site/src/lib/turnstile-client.ts`. Pending.
- **M4:**
  - Use M1's `contact.ts`: Task 5 becomes an extension, and `contact/parse.ts` goes away.
  - Task 7 adjusts M1's landing pages instead of creating them.
  - `deployEnv()` reads the shared deploy.
  - `env.preview` becomes the `previews` block.
  - `data-piece` becomes `data-setpiece`.
  - The Ottie bridge uses the `letter:*` cues and M2's `<Ottie context="contact">` (not `instance="letter"`), and its test reads `detail.type`.
  - No `style` attributes, in three places.
  - M2's Task 15 places the letter Ottie on home and `/contact`; M4 does not mount a second copy.

  Pending.
- **M5:**
  - `Base.astro` becomes `BaseLayout.astro`.
  - `PUBLIC_DEPLOY` becomes the shared deploy (`deployFromEnv` moves out of `headers.ts`).
  - The `previews` block replaces `env.preview`.
  - `/sitemap.xml` replaces `/sitemap-index.xml`.
  - `security.txt` is read from the build output (`dist/client/.well-known/security.txt`).
  - M3's real budget names, and no `ASK_LIVE_HOSTS`.
  - `site/src/lib/setpieces/flags.ts` for the set-piece switch.
  - Open questions 3 and 4 are already answered by Din through M4's decisions 1 and 2.

  Pending.
