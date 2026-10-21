# dins.dev site: Build plan

Status: Draft for Din's review (2026-10-21). Requirements: `docs/site/PRD.md`. Task status lives in `docs/TASKS.md` (Phase 2); decisions and verification results go in `docs/WORK_LEDGER.md`.
Deadline: live by **December 12, 2026**, with a few days of buffer before mid-December. Content freeze **December 1**.

## Approach

Build the plain, accessible site first and layer motion on top, so that at every point there is something shippable. Each milestone ends with a preview link Din can check and green checks in CI. Milestones overlap on purpose: Ottie, Ask Ottie and the set pieces are independent once the pages exist. Logic (player, search, budget, API) is built test first; visual set pieces are judged by Din in the preview.

## Repo layout

```
dins.dev/
  site/            Astro 7 app (pages, Svelte islands, Ottie player, Worker API routes)
    src/content/   projects, writing, library, suggested
    src/ottie/     canvas player, loader, triggers, lines file
    src/api/       ask, contact (Astro endpoints on the Worker)
    migrations/    D1 schema
  rag/             Python (uv): chunking, bge-m3 embedding, binary index, evals
    evals/         golden.yaml, adversarial.yaml
  brand/           unchanged; site imports tokens, fonts and Ottie sheets from here
  docs/
  check.sh         every local check; CI runs the same script
```

A pnpm workspace with `site/` as its first package, so game pages can join later as their own packages.

## Environments

| Environment | Where | Answer backend | Data |
|---|---|---|---|
| Local | `wrangler dev` through Astro | Fake by default, real API with a dev key when asked | Local D1 |
| Preview | Workers Builds, one link per branch | Fake | Preview D1 |
| Production | Workers Builds from `main` on `dins.dev` | Anthropic API, $100 limit | Production D1 |

Secrets: the Anthropic key as a Worker secret per environment; the eval key as a GitHub Actions secret. No Cloudflare token in GitHub.

## Milestones

### M0. Foundation (October 22 to 26)

- Set up `site/` (Astro 7.4, Svelte 5, the Cloudflare adapter, TypeScript 6) and `rag/` (uv, Python 3.12 or later).
- Wire in `brand/tokens/tokens.css` and the self-hosted fonts (WOFF2, subset to Latin and French).
- `check.sh`, pre-commit (formatting, lint, gitleaks), GitHub Actions on every PR, Renovate weekly.
- Workers Builds connected to the repo (Din authorizes it once in the Cloudflare dashboard).
- **Verify:** a starter page deploys to a preview link; `check.sh` and CI are green; gitleaks blocks a planted test secret.

### M1. Pages and content (October 27 to November 6)

- Content collections with schemas; sample projects and posts marked draft.
- Every route in PRD section 2 as static pages: `/work`, case studies with the summary block, `/writing` with RSS, `/about` with the timeline, `/contact` as a plain form, `/privacy`, the 404.
- SEO: titles, canonicals, sitemap, `robots.txt`, `llms.txt`, `security.txt`, Person structured data, social cards generated at build time from the approved templates.
- The no-JavaScript and reduced-motion baselines.
- With Din: the role line and the suggested questions.
- **Verify:** Playwright visits every route in light and dark; axe zero violations; Lighthouse accessibility and SEO 100; drafts absent from a production build; the site reads with JavaScript off.

### M2. Ottie on the site (November 2 to 12)

- The canvas player ported from the approved preview: ticks, exits, crossfades, `shift`, `loop_start`, `exit_via`, `enter_from`; off-thread decoding; pause off screen and in hidden tabs.
- The loader: inline still, idle when the page is idle, wave preloaded, other states fetched ahead of their triggers.
- Triggers for run-in and wave, idle, poke, tips, nap and wake; the reviewed lines file; Quiet Ottie; reduced motion; phone layout.
- **Verify:** unit tests for the player's state logic; a performance trace with Ottie playing shows no long tasks and no layout shift; network log shows the loading order; Din approves Ottie's behaviour in the preview.

### M3. Ask Ottie (November 6 to 22)

- `rag/`: chunking, bge-m3 embedding, the keyword index and the binary index format with a round-trip test; the deny-list scan and the approval check; the embedding agreement test against Workers AI.
- The Worker: `/api/ask` with Turnstile, rate limiting, the D1 budget counter, hybrid search, the "don't know" path, streaming from the answer backend, the resting mode; the question log with the 30-day cron.
- The Svelte Ask Ottie island: suggested questions (static answers), streaming answers, source chips, "how this answer was made", thumbs up or down, the project-filtered bar on case studies.
- Ottie's think, nod, point, talk and shrug wired to the answer flow.
- The eval harness: retrieval evals on every PR, answer evals on manual trigger.
- **Verify:** Worker tests for every path in PRD section 3 on the fake backend; retrieval recall@6 at least 0.9 on the sample library; one answer eval run on the real API with Haiku as judge; spending stops at the daily budget in a test.

### M4. Set pieces (November 13 to 29)

In this order, each approved by Din in the preview before the next starts, each with its calm version:

1. Lens intro and the letter field (canvas).
2. Windows: the scroll-pinned project stage (GSAP ScrollTrigger); flat stack on phones.
3. Paper: the floating writing cards.
4. Studio: the laptop, terminal and dolly in CSS 3D.
5. Letter: the folding contact form with the `send_email` binding and Turnstile; Ottie points, then jumps.

- **Verify:** screenshots at key scroll positions attached to each PR; performance traces at 60 fps with no task over 50 ms on a 2020 laptop and a mid-range phone; the home page JavaScript budget (100 KB gzipped) passes in CI; Din's approval recorded in the ledger.

### Content track (Din, November 1 to December 1)

- The interview in early November; library entries arrive through PRs Din approves.
- Real projects as they are ready, each with a stage capture; the resume PDF.
- **Content freeze December 1.**

### M5. Hardening and launch (December 1 to 12)

- Answer evals with Sonnet as judge on the final library; fix what fails.
- VoiceOver pass, a real phone check, final performance traces.
- Production keys and spend caps; security headers checked; Search Console and Bing verified with the sitemap (task 1.13); Cloudflare Web Analytics and the uptime monitor on.
- **Verify:** every acceptance criterion in PRD section 7, with results in the ledger. Live by December 12.

### After launch

- The performance optimization pass (Lighthouse performance as a gate again).
- Optional: the Blender studio upgrade and Ottie's celebrate state.

## Dependencies on Din

| What | Needed by |
|---|---|
| Authorize Workers Builds in the Cloudflare dashboard | M0 |
| Role line and suggested questions | M1 |
| Buy `dins.dev` (task 0.6) and set up Email Routing (task 0.8) | About November 12 |
| Anthropic production key ($100 limit) and eval key (about $5) | M3 |
| The interview and library reviews | November |
| Approval of each set piece in the preview | M4 |

## Fallbacks

- A set piece not approved by December 1 ships as its calm version.
- Projects not ready by the freeze stay drafts; the stage shows what is real.
- If the Anthropic API or budget is unavailable at launch, Ask Ottie runs in resting mode with suggested answers still working.
