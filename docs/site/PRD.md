# dins.dev site: Requirements

Status: Draft for Din's review (2026-10-21). Sections 1 to 8 were agreed one by one in the brainstorm on 2026-10-19 and 2026-10-21; the decisions and their reasons are in `docs/WORK_LEDGER.md`.
Owner: Din
Related: `docs/BRAND.md` (locked brand), `docs/design/sketches/home-sketch.html` (home page skeleton), `brand/ottie/README.md` (Ottie sheets and manifest), `docs/site/PLAN.md` (how it gets built).

## 1. Purpose and audience

dins.dev is Din's portfolio. Its first job is to support applications to US master's programs in data science or ML and data engineering, which open in mid-January 2027. Its second is to show recruiters for data engineering, then AI and LLM engineering roles, what Din builds. The ML and AI skill should show through the work itself, above all through Ask Ottie, a small, well-evaluated RAG system that visitors can use.

| Audience | What they need | In about |
|---|---|---|
| Admissions committees (primary) | Who Din is, what Din has built and how Din works, with evidence | 2 to 5 minutes, often careful reading |
| Recruiters and hiring managers | Role fit, real projects, contact | 30 seconds |
| Curious visitors | Something memorable and well made | One scroll |

Success: the site is live by **December 12, 2026**; it reads as one brand; Ask Ottie answers grounded questions about Din correctly and declines what it should; and nothing on it looks unfinished or mechanical.

## 2. Pages and content

### Routes

- `/`: the home page (section 2.2).
- `/work`: every published project as a grid of windows, filterable by ML, data engineering, data science and research.
- `/work/<project>`: the case study. It opens with the project's window and live demo, then a summary block (problem, Din's role, stack, results with real numbers), then the story. At the bottom, an "Ask Ottie about this project" bar that only searches that project's sources (retrieval filtered by metadata).
- `/writing` and `/writing/<post>`: case studies, devlogs and notes, with an RSS feed.
- `/about`: opens on the studio's zoomed-in screen, then bio, an education and experience timeline (the thesis appears here and as a research project), skills, English and French, and a resume download.
- `/contact`: the letter (section 2.2), also reachable as its own page.
- `/privacy` (short and plain), a 404 page where Ottie shrugs.
- SEO files: `sitemap.xml`, `robots.txt`, `llms.txt`, `/.well-known/security.txt`, RSS.

Not in v1: a French translation of the site, comments, a newsletter, a `/uses` page.

### Home page (skeleton accepted by Din, 2026-10-19)

One visual family, top to bottom. The sketch is a reference for layout and motion, not final design or copy.

1. **Lens (hero):** the intro pulls the page into focus through Ottie's right lens. Ask Ottie is the hero: Din's name, a role line, suggested questions written for recruiters and admissions, and Resume, Email, GitHub and LinkedIn visible on first paint. A faint mono letter field resolves into real library words near the cursor and sweeps while Ottie retrieves.
2. **Windows (work):** a scroll-pinned center stage with 3 or 4 featured projects. Each tilts in as a floating window, lands in focus with its demo running inside, then tilts away for the next; title, one-liner, tags and "View project" fade in step, with a progress rail. Phones: no pinning, windows stacked flat.
3. **Paper (writing):** the latest 3 posts as cards that drift up at different speeds with a small tilt that settles; hover lifts one card and softens the others. Phones: stacked flat.
4. **Studio (about):** a dark studio where a laptop unfolds, a terminal types `whoami` and `cat about.txt` in step with the scroll, and the camera dollies into the screen; then "Read the full story". CSS 3D first; a Blender-rendered frame sequence is an optional upgrade after launch.
5. **Letter (contact):** a sheet rising out of an envelope is the form ("Dear Din,", message on ruled lines, reason chips: a role, admissions, just saying hi; "From" with name and email). "Seal and send" folds the sheet, the envelope closes, an Ottie wax seal stamps on, and Ottie carries it off. Then "Sent. Thank you." with "Write another".
6. Footer.

### Content model

Typed Astro content collections in the repo, no CMS. A missing or wrong field fails the build.

| Collection | Format | Fields (main) |
|---|---|---|
| `projects` | MDX | title, kind (ML, data engineering, data science, research), summary, role, stack, results, featured order, demo (live, chart or video), stage capture (16:10), repo link, `status: draft / published` |
| `writing` | MDX | title, kind (case study, devlog, note), date, summary, motif, optional linked project, `devlog` (uses social card C), `status` |
| `library` | Markdown, one topic per file | topic or question, approved text, audience tags, sources, language, `approved_on` (set by Din only). Never rendered as a page. |
| `suggested` | YAML | suggested questions and their reviewed static answers with sources |

- Drafts never render in production, so placeholder projects (`passfx`, `claude-runner`, `claudehome`) cannot ship.
- Every project needs a stage capture: a demo or video that works in a 16:10 window.
- Ottie's corpus is the library plus the published project and writing pages, so the site and Ottie speak from the same approved source.
- The library is public in this repo (Din, 2026-10-21).

### How content reaches the library

1. Raw sources (GitHub READMEs, resume, LinkedIn data export, undergrad thesis) and the interview transcript stay in the private `handbook` repo.
2. The interview: Claude runs the question bank with Din in a Claude Code session.
3. Claude drafts short library entries, each citing where its facts came from.
4. Entries reach this repo only through a PR Din reviews. Only Din sets `approved_on`.
5. CI fails if an entry has no approval date, or if any entry or page mentions a deny-list topic (visa status, finances, personal life).

The interview questions with Din's approved answers become the golden eval set; deny-list, off-topic and injection questions form the adversarial set. Content freeze: **December 1, 2026**.

## 3. Ask Ottie

### What Ottie answers

- **In scope:** Din's work, projects, skills, education and thesis, what Din is looking for, how to get in touch, and the site itself.
- **Off-topic** (general coding help, other people, opinions): a friendly redirect back to Din.
- **Deny-list** (visa status, finances, personal life): a polite decline plus Din's email.
- **Not in the library:** "I don't know that one. Din would, here's how to ask." Ottie never guesses.
- **Voice:** Ottie talks about Din, never as Din, keeps answers short and cites its sources. English, and French when asked in French.

### How it works

1. **Build time (Python, `rag/`):** library entries and published pages are chunked by heading with metadata (source, URL, kind, project, language), embedded with bge-m3 (open weights), and written with a keyword index to one versioned **binary** index file served as a static asset.
2. **Per question:** browser to the Worker's `/api/ask`: Turnstile, a per-visitor rate limit and the daily budget; the question is embedded with bge-m3 on Workers AI; hybrid search returns the top 6 chunks (filtered to one project on project pages). If nothing scores high enough, Ottie takes the "don't know" path **without calling the model**. Otherwise Claude Haiku answers, streamed, followed by source chips and "how this answer was made" (chunks, scores, model, timing).
3. **Suggested questions** are answered by a script using the real pipeline, reviewed by Din in a PR and served as static text. Site builds never call the model.
4. **Answer backends** behind one interface: a fake (tests, local work, preview deploys) and the Anthropic API (live checks, production). The earlier "Claude Code on Din's membership" backend is dropped.

### Cost and safety

- A $100 hard limit on the Anthropic console, a daily budget of about $1 in the Worker (roughly 2,500 answers), answers capped at about 350 tokens, questions at 300 characters, the last 3 turns kept, the system prompt cached. Expected cost is about $0.0004 per answer.
- No tools and no side effects; the corpus is public, so a prompt injection has nothing secret to reach.
- Answers render as plain text with simple formatting, never raw HTML.
- When the API is down or the budget is spent, Ottie is "resting" and shows the best-matching pages as links plus Din's contact links. When Workers AI is down, search falls back to keywords only.
- An anonymous question log (question, sources used, scores, thumbs up or down; no IP address, no cookies) is kept for 30 days and disclosed on `/privacy`. It is how the eval set grows from real questions.

### Evals

- **Golden set:** interview questions (English and some French) with Din's approved answers and the sources each should cite. **Adversarial set:** deny-list, off-topic, injection and unknown questions.
- **Metrics and starting bars** (revisit after the first baseline): retrieval recall@6 at least 0.9, answer faithfulness at least 0.95 (a judge checks every claim against the retrieved chunks), 100 percent correct refusals on the deny-list, answering in the question's language, latency.
- **When:** retrieval evals on every PR (no model cost). Answer evals on demand and before each release, in GitHub Actions on manual trigger, with a separate eval key (spend cap about $5) stored as a GitHub secret. Haiku judges routine runs; Sonnet judges release runs.

## 4. Ottie on the site

Ottie is the 3D character in `brand/ottie/dist/` (twelve states, accepted by Din on 2026-10-20 and 2026-10-21). Ottie is about 25 to 30 percent of the hero's height and never the headline.

| State | When |
|---|---|
| run-in, then wave | First visit: "Hi, I'm Ottie." Returning visitors get just the wave. |
| idle | Default: breathing, blinks, small weight shifts |
| think | While Ottie retrieves |
| nod, then point | When an answer lands; points toward the sources |
| talk | While a speech bubble shows |
| shrug | "Don't know" answers and the 404 page |
| nap, then wake | A minute with nothing happening, or lots of background clicking; wakes on the next real interaction |
| point, then jump | Contact: points at the letter; jumps when it is sent |
| poke | Clicking Ottie: a small hop and a random line |
| tip (idle plus a bubble) | About 20 seconds without interaction: one helpful line, at most 3 per visit |

Rules:
- Never in the way: Ottie never covers the input or the answer and stays silent while someone types or an answer streams.
- Speaks sparingly: bubbles of at most 90 characters, at most one every 20 seconds, from a reviewed script file in the repo, never generated live.
- "Quiet Ottie" toggle (remembered in the visitor's browser): on screen but silent and still.
- Reduced motion: a still pose that changes with gentle crossfades.
- Decorative to screen readers; anything useful Ottie says also exists in the real UI.
- Phones: smaller, below the questions, no tips or naps.
- Eyes do not follow the cursor (they are rendered into the frames).
- Appears on: home (hero corner), project pages (beside the project Ask bar), contact, 404, devlog posts. Not on the About studio, the writing list or formal pages.

Loading (Din: "make sure Ottie loads good and the website is smooth"):
- The neutral still (`brand/reference/ottie-3d-neutral.webp`, sized in advance) is in the HTML, so nothing shifts.
- The idle sheet loads once the page is idle; wave is preloaded right after.
- Other states are fetched just before they are needed: think on focusing the question box, nod and shrug while an answer streams, nap after the idle timer, jump when the letter form is filled in.
- Sheets decode off the main thread; playback pauses when Ottie is off screen or the tab is hidden. Sheet files are cached long term.
- A typical visit loads about 0.6 to 0.9 MB of Ottie, not the full 2.4 MB.

## 5. Stack

Versions checked on npm and nodejs.org on 2026-10-21; pinned to minor versions, patches through Renovate.

| Layer | Choice |
|---|---|
| Site | Astro 7.4: static pages, interactive islands only where needed (Din, 2026-10-21) |
| Islands | Svelte 5 (Din, 2026-10-21) |
| Styling | Plain CSS on `brand/tokens/tokens.css`, scoped per component |
| Motion | GSAP 3.15 with ScrollTrigger for the set pieces; CSS for small touches; no smooth-scroll library |
| Ottie player | In-house TypeScript canvas module built on the approved preview's logic |
| Hosting | Cloudflare Workers with static assets, deployed by Workers Builds (Astro's adapter no longer supports Pages) |
| Ask Ottie runtime | Astro API route on the Worker; Turnstile; Workers rate limiting binding; Workers AI (bge-m3); `@anthropic-ai/sdk` with Claude Haiku |
| Data | D1 for the daily budget counter and the question log, with a nightly cron deleting entries older than 30 days |
| Contact | Email Routing's `send_email` binding to `din@dins.dev`, behind Turnstile |
| RAG build and evals | Python with uv in `rag/`: chunking, bge-m3, keyword index, pytest |
| Tooling | Node 24 LTS, pnpm, TypeScript 6.0 (`@astrojs/check` does not support 7 yet), Vitest 4.1 (Cloudflare's Workers pool does not support 5 yet), Playwright 1.64 with axe, Prettier, ESLint, Ruff |

Free-plan constraints shape two choices: the search index is binary (no JSON parsing inside the 10 ms CPU limit), and a test checks that build-time and Workers AI bge-m3 embeddings agree.

## 6. Quality bar

- **Accessibility:** WCAG 2.2 AA. Every set piece has a calm version under reduced motion (no lens intro, the stage as a plain list, About opening on the screen, the letter as a plain form). Full keyboard access, a visible teal focus ring, a skip link, no focus traps in pinned sections. Ask Ottie answers are announced once complete. axe at zero violations, plus one manual VoiceOver pass before launch.
- **Smoothness:** no layout shift (reserved boxes, metric-matched font fallbacks, two preloaded self-hosted WOFF2 fonts subset to Latin and French); animate only transform, opacity and canvas; 60 fps and no main-thread task over 50 ms through the set pieces on a 2020 laptop and a mid-range phone; at most 100 KB gzipped of first-party JavaScript on the home page before interaction; Save-Data or low-memory devices get the still Ottie and no lens intro. Lighthouse performance is reported but not a gate until the post-launch optimization pass (Din, 2026-10-21).
- **SEO:** unique titles and descriptions, canonicals, sitemap, social cards generated at build time (card A by default, C for devlogs), Person structured data with `sameAs`, `llms.txt`; all content in real HTML. Lighthouse SEO 100.
- **Privacy:** no cookies and no consent banner; the only outside scripts are Turnstile and Cloudflare Web Analytics; the question log as in section 3; contact messages are emailed, not stored; `/privacy` lists all of it in plain words.
- **Security:** the Anthropic key as a Worker secret per environment, a strict content security policy, HSTS, `security.txt`, input limits, rate limit, Turnstile and budget on every API route.
- **Failure modes:** readable with JavaScript off (suggested answers are static, the contact form still submits); Ottie resting when the API or budget is out; keyword-only search when Workers AI is down; the still Ottie when a sheet fails; the 404 with Ottie.

## 7. Acceptance criteria

Din accepts the site when, on the production URL:

1. Every route in section 2 exists, passes `check.sh` and CI, and has no placeholder content.
2. The home page set pieces (lens, windows, paper, studio, letter) are each approved by Din in a preview, or ship as their calm version.
3. Ask Ottie meets the eval bars in section 3 on a Sonnet-judged release run, declines every deny-list question, and goes to "resting" correctly when the budget is spent.
4. Ottie plays the states in section 4 on their triggers, loads as described, and never covers the input or answer.
5. axe reports zero violations, Lighthouse accessibility and SEO are 100, and the VoiceOver pass and a real phone check are done.
6. The smoothness budget holds: the home page JavaScript budget passes in CI, and performance traces show 60 fps through the set pieces.
7. The contact form delivers to `din@dins.dev`, and the site is verified in Search Console and Bing with a sitemap submitted.
8. Spend limits are set: $100 on the production key, about $5 on the eval key, the daily budget active.

## 8. Risks

1. **Content, not code.** Real projects are not built yet. If they slip, the stage launches with what is ready and the rest stay drafts; placeholders never ship.
2. **Set pieces take longer than planned.** Any set piece not approved by December 1 launches as its calm version.
3. **The domain.** `dins.dev` is not bought yet (task 0.6). Production, the contact form and Email Routing need it; it must be done by about November 12.

## 9. Open questions

- The exact role line and suggested questions (written with Din during M1).
- Whether Ottie's French lines ship in v1 (the answers follow the question's language either way).
- The Blender studio upgrade and Ottie's celebrate state, after launch.
