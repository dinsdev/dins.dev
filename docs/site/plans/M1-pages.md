# M1 Pages and content: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Status: Proposed (plan only, written 2026-10-21 by the M1 plan session; nothing here is built). Task 2.11 in `docs/TASKS.md`. Build branch: `feat/m1-pages`, cut from `main` after M0 is merged.

**Goal:** Every route in PRD section 2 as static, accessible, crawlable Astro pages on typed content collections, with the SEO files, build-time social cards, the no-JavaScript and reduced-motion baselines and a drafts guard, so M2, M3 and M4 can enhance a finished, calm site.

**Architecture:** Astro 7.4 prerenders every page (no `prerender = false` anywhere in M1). Content lives in four collections defined in `site/src/content.config.ts` with schemas in `site/src/lib/schemas.ts`. One pair of build flags, resolved in Node from M0's shared deploy (`site/src/lib/deploy.ts`) plus `DINS_SHOW_DRAFTS` and injected with Vite `define`, decides whether drafts render (dev, previews and the local e2e build) and whether pages carry `noindex` (preview deploys only). Pure logic (schemas, sorting, SEO strings, contact parsing, card layout) lives in `site/src/lib/` and `site/src/og/` and is unit tested with Vitest; pages are tested with Playwright and axe against the built site. Social cards are rendered to PNG after the build by a small Astro integration (Node, satori and resvg) that reads a card spec each page writes into its own head.

**Tech Stack:** Astro 7.4, @astrojs/cloudflare 14.4, @astrojs/mdx 8.1, @astrojs/rss 4.0, satori 0.63, @resvg/resvg-js 2.6, TypeScript 6.0, Vitest 4.1, Playwright 1.64 with @axe-core/playwright 4.14, @lhci/cli 0.15, pnpm, Node 24. Plain CSS on `brand/tokens/tokens.css`. No Svelte islands in M1.

**Spec:** `docs/site/PRD.md` (sections 2, 4 "appears on", 6 and 7), `docs/site/PLAN.md` (M1), `docs/BRAND.md`, layout reference `docs/design/sketches/home-sketch.html` (source `home.template.html`; not final design or copy).

## Global Constraints

- Versions pinned to minor: `@astrojs/mdx@~8.1.0`, `@astrojs/rss@~4.0.19`, `satori@~0.63.2`, `@resvg/resvg-js@~2.6.2`, `@axe-core/playwright@~4.14.0`, `@lhci/cli@~0.15.1`. Everything else comes from M0's pins (Astro 7.4, TypeScript 6.0, Vitest 4.1, Playwright 1.64).
- Zod comes from `astro/zod` (Zod 4). `defineCollection` and `reference` come from `astro:content`, loaders from `astro/loaders`.
- Astro 7 compiles with the Rust compiler: unclosed tags are errors and `<div>` inside `<p>` is not auto-corrected. `compressHTML` defaults to `'jsx'`, so whitespace between inline elements is dropped: write `{" "}` where a space matters.
- Prerendering runs in workerd by default (`prerenderEnvironment: 'workerd'`). Page and endpoint code must not use `node:fs`, `process.env` or native modules. Node-only work (env flags, social cards) happens in `astro.config.mjs` and integration hooks.
- Drafts never render in a production build (PRD 2). The deploy comes from M0's shared `deployFromEnv` (`local`, `preview`, `production`; production only from Workers Builds on `main`). Drafts show on `preview`, on `local` with `DINS_SHOW_DRAFTS=1`, and in `astro dev`. `DINS_SHOW_DRAFTS=1` on `production` fails the build.
- Never invent facts about Din. Every sample is `status: draft`, says it is a sample in its own text, and renders with a visible "Draft" badge carrying `data-draft`.
- Light and dark come only from `brand/tokens/tokens.css` (`prefers-color-scheme`, overridden by `html[data-theme]`). Teal is the only accent; amber never as text on paper.
- Type: Fraunces only down to H3, H4 and below in Instrument Sans, labels and data in JetBrains Mono, body at most 66 characters per line. Curly apostrophes in display text and headings (I’m).
- The wordmark is always the SVG from `brand/logo/`, never live text.
- WCAG 2.2 AA. axe at zero violations with its default rules, on every route, in light and dark. Visible teal focus ring, a skip link, one `h1` per page.
- Lighthouse accessibility 100 and SEO 100 are gates; performance is a warning only (Din, 2026-10-21).
- No `style="…"` attributes in server-rendered HTML (M5's CSP drops them): use classes or scoped `<style>` blocks.
- Ottie is decorative to screen readers (`aria-hidden="true"`, `alt=""`). Ottie appears on home, project pages, contact, 404 and devlog posts only.
- Privacy: no cookies. The theme choice is the only thing M1 stores, in `localStorage`, and `/privacy` says so.
- Writing style in UI strings, comments and commit messages: no em dashes, no en dashes as separators, no buzzwords; Conventional Commits; no `Co-Authored-By` or any attribution line.

## Review Focus

1. **Every collection empty in production.** All M1 content is draft, so a production build has no projects, posts or suggested answers. `/`, `/work/`, `/writing/`, RSS, sitemap and `llms.txt` must still build, return 200 and show a calm empty state, never a broken grid or an invalid feed. Pinned by the empty-array unit tests in Task 4 and the production-build checks in Task 18.
2. **Hostile or long titles.** A title with `</script>`, `&`, quotes, French accents or 120 characters must not break JSON-LD, RSS, `<title>` or the social card. Pinned by `jsonLdScript` tests (Task 6), card title sizing tests (Task 17) and the escaping test in Task 16.
3. **Trailing slashes and unknown paths.** `/work` and `/work/` reach the same page, canonicals are always the slashed absolute form, and `/work/nope/` returns status 404 with the Ottie 404 page. Pinned by `canonicalUrl` tests (Task 6) and the 404 status test (Task 15).
4. **A published post linking a draft project.** In production the post must render without a link to a page that does not exist. Pinned by the `linkedProject` test (Task 4).
5. **Blocked storage and the theme toggle.** With `localStorage` throwing (Safari private mode, strict settings) the page must still render, follow the system theme and let the toggle work for the current page. Pinned by the `saveTheme` unit test and the blocked-storage e2e test (Task 8).

---

## File structure

Created by M1 unless marked "modify". Paths are relative to the repo root.

```
site/
  astro.config.mjs                      modify: mdx, define flag, social cards integration
  playwright.config.ts                  modify: drafts on for M0's server; dark, no-js, reduced-motion, phone projects beside chromium
  lighthouserc.cjs                      Lighthouse CI config
  package.json                          modify: deps and scripts (check:drafts, lhci, launch:blockers)
  scripts/
    check-drafts.ts                     drafts guard over a production build
    launch-blockers.ts                  prints copy Din still owes (not part of check.sh)
  src/
    env.d.ts                            modify (M0's): declare __DINS_BUILD_FLAGS__
    content.config.ts                   the four collections
    content/
      projects/_README.md               how to add a project (ignored by the loader)
      projects/_captures/sample-window.svg
      projects/passfx.mdx               sample, draft
      projects/claude-runner.mdx        sample, draft
      projects/claudehome.mdx           sample, draft
      writing/_README.md
      writing/sample-case-study.mdx     sample, draft
      writing/sample-devlog.mdx         sample, draft
      writing/sample-note.mdx           sample, draft
      library/_README.md                M3 adds entries
      suggested/suggested.yaml          two sample entries, draft
    data/
      site.ts                           identity and links (Din fills the nulls)
      profile.ts                        role line, about teaser, bio, timeline, skills, languages
    lib/
      drafts.ts                         resolveBuildFlags(deploy, showDraftsEnv), isVisible (pure)
      build.ts                          BUILD_FLAGS, SHOW_DRAFTS (reads the define)
      schemas.ts                        zod schemas and enums for every collection and profile
      kinds.ts                          labels for project and writing kinds
      content.ts                        sorting, filtering, validation (pure)
      collections.ts                    getCollection wrappers (Astro only)
      seo.ts                            canonicalUrl, pageTitle, jsonLd helpers, card paths
      page.ts                           prop types for the layout (SeoProps, NavKey, CardSpecInput)
      sitemap.ts                        buildSitemap, INDEXABLE_STATIC_ROUTES
      textfiles.ts                      buildRobotsTxt, buildLlmsTxt, buildSecurityTxt
      contact.ts                        field names, limits, reasons, parseContact
      theme.ts                          theme toggle logic
      dates.ts                          formatDate, formatYearMonth
      launch.ts                         launchBlockers (pure)
    og/
      spec.ts                           CardSpec schema, extract and strip the card meta
      card.ts                           cardElement, titleSize, renderCard
      assets.ts                         loads fonts and SVGs from brand/
    integrations/
      social-cards.ts                   astro:build:done hook writing /og/*.png
    styles/
      site.css                          base layout, focus, skip link, reduced motion, prose, forms
    layouts/
      BaseLayout.astro                  modify (M0 creates it): SEO head, head slot, nav, footer, theme script
    components/
      Seo.astro  Nav.astro  Footer.astro  ThemeToggle.astro  Wordmark.astro
      Draft.astro  QuickLinks.astro  SuggestedAnswers.astro  AskSlot.astro  OttieSlot.astro
      ProjectWindow.astro  ProjectCard.astro  ProjectSummary.astro  WorkGrid.astro  WorkFilters.astro
      PostCard.astro  Motif.astro  Timeline.astro  ContactForm.astro  Prose.astro
    pages/
      index.astro
      work/index.astro  work/[id].astro  work/kind/[kind].astro
      writing/index.astro  writing/[id].astro
      about.astro
      contact/index.astro  contact/sent.astro  contact/not-sent.astro
      privacy.astro  404.astro
      rss.xml.ts  sitemap.xml.ts  robots.txt.ts  llms.txt.ts  .well-known/security.txt.ts
  tests/
    unit/  drafts schemas content profile seo sitemap textfiles contact theme dates launch og-spec og-card check-drafts (.test.ts)
    unit/fixtures/  html-with-card.html
    e2e/   routes.ts helpers.ts pages.spec.ts seo.spec.ts home.spec.ts work.spec.ts case-study.spec.ts
           writing.spec.ts about.spec.ts contact.spec.ts misc.spec.ts theme.spec.ts no-js.spec.ts
           reduced-motion.spec.ts layout.spec.ts
brand/
  tools/card_fonts.py                   writes static card fonts (satori renders variable fonts at their default)
  fonts/cards/*.ttf                     generated, committed
check.sh                                modify: production build, then check:drafts
.github/workflows/ci.yml                modify: Lighthouse step after e2e
```

Responsibilities are split so that pure logic never imports `astro:content`: `content.ts` takes plain arrays, `collections.ts` is the only file that calls `getCollection`. That keeps every rule unit testable in Node.

## Interfaces other milestones build on

These names are the contract. They are repeated in the shared notes folder for the M2, M3 and M4 plan sessions.

- **Build flags:** `import { BUILD_FLAGS, SHOW_DRAFTS } from "site/src/lib/build"`. `BUILD_FLAGS: { showDrafts: boolean; noindex: boolean }`, from `resolveBuildFlags(deploy, process.env.DINS_SHOW_DRAFTS)` where `deploy` is M0's `Deploy`. Other milestones read the deploy itself from M0's `site/src/lib/deploy-env.ts`, not from these flags. The RAG build (M3) must apply the same rule to the production index: only `status: published` entries, and never library entries with `sample: true`.
- **Visible content:** `getVisibleProjects()`, `getVisiblePosts()`, `getVisibleSuggested()` in `site/src/lib/collections.ts`, each already sorted. A project's slug is its file name (`entry.id`); its URL is `/work/<id>/`. A post's URL is `/writing/<id>/`.
- **Ask Ottie slots (M3):** `AskSlot.astro` with props `{ scope: "site" } | { scope: "project"; project: string }` renders `<div class="ask-slot" data-ask-scope data-ask-project>` around a `<slot />`. M3 mounts its island inside. Home suggested answers render as `<details data-suggested-id="<id>">` inside `<section id="suggested">`; M3's island may take them over.
- **Ottie slot (M2):** `OttieSlot.astro` with props `{ placement: "hero" | "project" | "contact" | "404" | "devlog"; state?: "idle" | "shrug" }` renders `<div class="ottie-slot" data-ottie-placement data-ottie-state aria-hidden="true">` holding the neutral still, sized 180 x 220 in a reserved box. It is a placeholder: M2's Task 16 replaces every `<OttieSlot placement=…>` with M2's `<Ottie context=…>` (`hero` becomes `home`) and deletes `OttieSlot.astro`.
- **Set pieces (M4):** home sections are `<header id="top" data-setpiece="lens">`, `<section id="work" data-setpiece="windows">`, `<section id="writing" data-setpiece="paper">`, `<section id="about" data-setpiece="studio">`, `<section id="contact" data-setpiece="letter">`. `/about` opens with `<div class="screen-panel" data-setpiece="studio-screen">`. `<html>` has class `no-js`, replaced by `js` by an inline script, so calm and enhanced CSS can branch. `BaseLayout.astro` has `<slot name="head" />` inside `<head>` for M4's `MotionHead.astro`.
- **Contact (M4 implements `/api/contact` and extends this module):** `site/src/lib/contact.ts` exports `CONTACT_FIELDS` (`message`, `reason`, `name`, `email`, honeypot `website`, Turnstile `cf-turnstile-response`), `CONTACT_LIMITS` (`name` 100, `email` 254, `message` 4000), `REASONS` (`role`, `admissions`, `hi`), `CONTACT_REDIRECTS` (`sent: "/contact/sent/"`, `notSent: "/contact/not-sent/"`) and `parseContact(form: FormData | URLSearchParams): ContactResult`, which also strips control characters other than newline and tab. A plain form post answers with a `303` to one of the two pages; a fetch with `Accept: application/json` gets JSON. A post without JavaScript has no Turnstile token and is never accepted (Din, 2026-10-21), so it lands on `/contact/not-sent/`, which carries a `mailto:din@dins.dev` link; the form carries a `<noscript>` note saying the same. The form holds an empty `<div data-turnstile-slot>` where M4 renders Turnstile.

## Assumes

From M0 (Foundation), merged before M1 starts:

- The shared contract in `docs/site/plans/README.md` (where it disagrees with this plan, it wins).
- `site/` builds with `pnpm --dir site build` and serves the built Worker with `pnpm --dir site serve` (wrangler dev on 127.0.0.1:8787, `GET /api/health`); `astro.config.mjs` sets `site: "https://dins.dev"`, the Cloudflare adapter with the custom entry `site/src/worker.ts`, `@astrojs/svelte` and `session: false`. Default `output` (static), `build.format: "directory"`, `trailingSlash: "ignore"`.
- M0's build-time deploy: `site/src/lib/deploy.ts` (`type Deploy = "local" | "preview" | "production"`, `deployFromEnv(ci, branch)`), the `__DINS_DEPLOY__` define, its declaration in `site/src/env.d.ts`, and `site/src/lib/deploy-env.ts` (`DEPLOY`). M1 adds `__DINS_BUILD_FLAGS__` next to it.
- `site/src/layouts/BaseLayout.astro` exists (props `{ title, description }`), imports `site/src/styles/global.css` (tokens and `fonts.css`), preloads the Fraunces and Instrument Sans WOFF2 files from `brand/fonts/web/`, links the favicon, writes `<meta name="dins-deploy" content={DEPLOY}>`, and has a skip link and `<main id="main">`. M1 rewrites it with the SEO head, nav and footer, keeping M0's imports, preloads and deploy meta.
- `/ottie/` serves `brand/ottie/dist/` (M0). M0 links only `favicon.svg`; M1 copies the full icon set (`brand/logo/icons/*` and `favicon.svg`) into `site/public/` in Task 8.
- Fonts: `brand/fonts/Fraunces-VF.ttf` (already there) and M0's web fonts in `brand/fonts/web/` (WOFF2, with their OFL licences). Task 17's `card_fonts.py` searches both and reads TTF or WOFF2.
- Vitest runs `site/tests/unit/**/*.test.ts` in Node (`pnpm --dir site test:unit`); Worker tests (`@cloudflare/vitest-plugin`) are a separate project M1 does not use.
- `site/playwright.config.ts` exists with baseURL `http://127.0.0.1:8787`, a `chromium` project, a `webServer` that runs `pnpm build && pnpm serve` and waits on `/api/health`, and honours `BASE_URL` (M5 runs it against https://dins.dev). M1 adds `DINS_SHOW_DRAFTS=1` to that server and its own projects beside `chromium` (Task 8).
- `./check.sh [--e2e]` runs format, lint, `pnpm --dir site check`, unit tests and a build; `.github/workflows/ci.yml` has the jobs `check` and `e2e`.

From M2, M3, M4 and M5:

- M2's Task 16 replaces `OttieSlot.astro` with `<Ottie context=…>` and deletes it; M3 mounts the Ask island inside `AskSlot.astro` and fills `suggested.yaml` with reviewed answers; M4 implements `/api/contact` on M1's `contact.ts`, Turnstile and the set pieces on the hooks above, and adjusts M1's contact landing pages; M5 owns the CSP and security headers, the release scan and the `security.txt` expiry test (M1 owns the file).
- M3 asked for these schema details (shared notes, 2026-10-21) and M1 adopts them: library `topic`, `audience`, `sources`, `language` (`en` or `fr`), `approved_on` (date or null) and `sample` (boolean); suggested `question`, `answer`, `sources`, `language`, `generated_on`. `status: published` is the only "reviewed by Din" flag for every collection (contract), so suggested entries have no `reviewed_by_din` field.

## Din tasks (copy and facts only Din can provide)

These are Din's to write or confirm. Claude can interview Din and draft from Din's answers, but nothing ships until Din approves it in a PR. Each one is a launch blocker that `pnpm --dir site launch:blockers` (Task 5) lists until done.

| # | What | Where it goes | Needed by |
|---|---|---|---|
| D1 | The role line under "Hi, I’m Din." (one line, about 60 to 90 characters; it also appears on the home social card) | `site/src/data/profile.ts` `roleLine` | M1 review in the preview (PLAN: "With Din: the role line and the suggested questions") |
| D2 | The suggested questions (about 4 or 5, written for recruiters and admissions; one may be French). Their answers come later from M3's script and Din's review | `site/src/content/suggested/suggested.yaml` | M1 review, answers in M3 |
| D3 | About text: the bio (2 to 4 short paragraphs), the education and experience timeline (with the thesis), skills grouped, and the language levels for English and French | `site/src/data/profile.ts` | Content freeze, December 1 |
| D4 | The home "About" teaser (one or two sentences above "Read the full story") | `profile.ts` `aboutTeaser` | Content freeze |
| D5 | Name for structured data and the page footer: "Din" only, or the full name as well | `site/src/data/site.ts` `legalName` | Before launch |
| D6 | Links: the LinkedIn URL, which GitHub profile to show (`github.com/dinsdev` or a personal one), and the full `sameAs` list (only profiles that exist) | `site.ts` | Before launch |
| D7 | The resume PDF | `site/public/resume.pdf`, then `site.ts` `links.resume = "/resume.pdf"` | Content freeze |
| D8 | Review the UI copy Claude drafts (section headings, empty states, 404 text, contact intro, privacy page) in the preview | the page files | M1 review |
| D9 | Real projects and posts (content track 2.15) | `site/src/content/projects/`, `writing/` | Content freeze |

---

## Task 1: Build flags and the drafts rule

**Files:**
- Create: `site/src/lib/drafts.ts`, `site/src/lib/build.ts`
- Modify: `site/astro.config.mjs`, `site/src/env.d.ts`
- Test: `site/tests/unit/drafts.test.ts`

**Interfaces:**
- Consumes: M0's `type Deploy` and `deployFromEnv(ci, branch)` from `site/src/lib/deploy.ts`.
- Produces: `type BuildFlags = { showDrafts: boolean; noindex: boolean }`, `resolveBuildFlags(deploy: Deploy, showDraftsEnv: string | undefined): BuildFlags`, `isVisible(status: Status, showDrafts: boolean): boolean`, `type Status = "draft" | "published"`; `BUILD_FLAGS` and `SHOW_DRAFTS` from `build.ts`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/drafts.test.ts
import { describe, expect, it } from "vitest";
import { isVisible, resolveBuildFlags } from "../../src/lib/drafts";

describe("resolveBuildFlags", () => {
  it("hides drafts and allows indexing in a plain local build (check.sh, CI)", () => {
    expect(resolveBuildFlags("local", undefined)).toEqual({ showDrafts: false, noindex: false });
  });
  it("shows drafts without noindex locally with DINS_SHOW_DRAFTS=1 (e2e and Lighthouse builds)", () => {
    expect(resolveBuildFlags("local", "1")).toEqual({ showDrafts: true, noindex: false });
  });
  it("treats any other DINS_SHOW_DRAFTS value as off", () => {
    expect(resolveBuildFlags("local", "true").showDrafts).toBe(false);
  });
  it("shows drafts and sets noindex on preview deploys", () => {
    expect(resolveBuildFlags("preview", undefined)).toEqual({ showDrafts: true, noindex: true });
  });
  it("hides drafts in production", () => {
    expect(resolveBuildFlags("production", undefined)).toEqual({ showDrafts: false, noindex: false });
  });
  it("refuses DINS_SHOW_DRAFTS=1 in production", () => {
    expect(() => resolveBuildFlags("production", "1")).toThrow(/production/);
  });
});

describe("isVisible", () => {
  it("always shows published entries", () => {
    expect(isVisible("published", false)).toBe(true);
  });
  it("shows drafts only when drafts are on", () => {
    expect(isVisible("draft", false)).toBe(false);
    expect(isVisible("draft", true)).toBe(true);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/drafts.test.ts`
Expected: FAIL, cannot resolve `../../src/lib/drafts`.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/drafts.ts
// Decides at build time whether drafts render and whether pages say noindex.
// Pure on purpose: astro.config.mjs (Node) calls it with M0's deploy and injects the result with Vite define.
import type { Deploy } from "./deploy";

export type Status = "draft" | "published";
export type BuildFlags = { showDrafts: boolean; noindex: boolean };

export function resolveBuildFlags(deploy: Deploy, showDraftsEnv: string | undefined): BuildFlags {
  const forced = showDraftsEnv === "1";
  if (deploy === "production") {
    if (forced) throw new Error("DINS_SHOW_DRAFTS=1 is not allowed in a production build");
    return { showDrafts: false, noindex: false };
  }
  // Preview deploys: drafts on so Din can review them, never indexed.
  if (deploy === "preview") return { showDrafts: true, noindex: true };
  // Local builds (laptop, GitHub Actions): drafts only when asked, never public, so no noindex.
  return { showDrafts: forced, noindex: false };
}

export function isVisible(status: Status, showDrafts: boolean): boolean {
  return status === "published" || showDrafts;
}
```

```ts
// site/src/lib/build.ts
// The build flags as seen by pages. In `astro dev` drafts always show.
import type { BuildFlags } from "./drafts";

export const BUILD_FLAGS: BuildFlags = __DINS_BUILD_FLAGS__;
export const SHOW_DRAFTS: boolean = import.meta.env.DEV || BUILD_FLAGS.showDrafts;
```

Add one line to M0's `site/src/env.d.ts`, next to its `__DINS_DEPLOY__` declaration:

```ts
declare const __DINS_BUILD_FLAGS__: import("./lib/drafts").BuildFlags;
```

In `site/astro.config.mjs`, reuse M0's deploy value and add the flags to M0's `vite.define` block:

```js
import { deployFromEnv } from "./src/lib/deploy.ts"; // M0
import { resolveBuildFlags } from "./src/lib/drafts.ts";

const deploy = deployFromEnv(process.env.WORKERS_CI, process.env.WORKERS_CI_BRANCH); // M0
const buildFlags = resolveBuildFlags(deploy, process.env.DINS_SHOW_DRAFTS);

export default defineConfig({
  // ...M0's existing settings...
  vite: {
    define: {
      __DINS_DEPLOY__: JSON.stringify(deploy), // M0
      __DINS_BUILD_FLAGS__: JSON.stringify(buildFlags),
    },
  },
});
```

- [ ] **Step 4: Run the tests and the build**

Run: `pnpm --dir site exec vitest run tests/unit/drafts.test.ts`
Expected: PASS, 8 tests.

Run: `WORKERS_CI=1 WORKERS_CI_BRANCH=main DINS_SHOW_DRAFTS=1 pnpm --dir site build`
Expected: FAIL with "DINS_SHOW_DRAFTS=1 is not allowed in a production build".

Run: `pnpm --dir site build && pnpm --dir site check`
Expected: both PASS.

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/drafts.ts site/src/lib/build.ts site/src/env.d.ts site/astro.config.mjs site/tests/unit/drafts.test.ts
git commit -m "feat(site): build flags that decide drafts and noindex"
```

## Task 2: Collection schemas and content config

**Files:**
- Create: `site/src/lib/schemas.ts`, `site/src/lib/kinds.ts`, `site/src/content.config.ts`, `site/src/content/{projects,writing,library}/_README.md`
- Modify: `site/package.json` (add `@astrojs/mdx`), `site/astro.config.mjs` (add `mdx()`)
- Test: `site/tests/unit/schemas.test.ts`

**Interfaces:**
- Consumes: `Status` from Task 1.
- Produces: `PROJECT_KINDS`, `WRITING_KINDS`, `MOTIFS`, `LANGUAGES`, `AUDIENCES`, types `ProjectKind`, `WritingKind`, `Motif`; schema factories `makeProjectSchema(image)`, `makeWritingSchema(projectRef)`; schemas `librarySchema`, `suggestedSchema`, `statusSchema`, `linkSchema`; `KIND_LABELS`, `WRITING_KIND_LABELS` from `kinds.ts`. Collection names `projects`, `writing`, `library`, `suggested`.

- [ ] **Step 1: Install MDX**

Run: `pnpm --dir site add @astrojs/mdx@~8.1.0`
Why: projects and writing are MDX (PRD 2). Add `mdx()` to `integrations` in `site/astro.config.mjs` (`import mdx from "@astrojs/mdx";`).

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/unit/schemas.test.ts
import { describe, expect, it } from "vitest";
import { z } from "astro/zod";
import {
  librarySchema,
  makeProjectSchema,
  makeWritingSchema,
  suggestedSchema,
} from "../../src/lib/schemas";

const fakeImage = () => z.object({ src: z.string(), width: z.number(), height: z.number() });
const projectSchema = makeProjectSchema(fakeImage);
const writingSchema = makeWritingSchema(z.string());

const project = {
  title: "Sample project",
  kind: "data-engineering",
  summary: "Sample summary.",
  role: "Sample role.",
  stack: ["python"],
  results: [{ value: "n/a", label: "Sample result" }],
  capture: { src: "/c.png", width: 1600, height: 1000 },
  captureAlt: "Sample capture",
  status: "draft",
};

describe("projects", () => {
  it("accepts a complete project", () => {
    expect(projectSchema.safeParse(project).success).toBe(true);
  });
  it.each(["title", "kind", "summary", "role", "stack", "results", "capture", "captureAlt", "status"])(
    "fails without %s",
    (field) => {
      const { [field]: _removed, ...rest } = project as Record<string, unknown>;
      expect(projectSchema.safeParse(rest).success).toBe(false);
    },
  );
  it("rejects an unknown kind", () => {
    expect(projectSchema.safeParse({ ...project, kind: "web" }).success).toBe(false);
  });
  it("rejects a status other than draft or published", () => {
    expect(projectSchema.safeParse({ ...project, status: "placeholder" }).success).toBe(false);
  });
  it("accepts a video demo with a site path and rejects an outside URL", () => {
    expect(projectSchema.safeParse({ ...project, demo: { type: "video", src: "/media/x.mp4" } }).success).toBe(true);
    expect(projectSchema.safeParse({ ...project, demo: { type: "video", src: "https://evil.test/x.mp4" } }).success).toBe(false);
  });
  it("limits featured order to 1 through 4", () => {
    expect(projectSchema.safeParse({ ...project, featured: 1 }).success).toBe(true);
    expect(projectSchema.safeParse({ ...project, featured: 5 }).success).toBe(false);
  });
  it("needs an https repo link when one is given", () => {
    expect(projectSchema.safeParse({ ...project, repo: "https://github.com/dinsdev/x" }).success).toBe(true);
    expect(projectSchema.safeParse({ ...project, repo: "not a url" }).success).toBe(false);
  });
});

describe("writing", () => {
  const post = {
    title: "Sample post",
    kind: "devlog",
    date: "2026-10-27",
    summary: "Sample summary.",
    motif: "lens",
    status: "draft",
  };
  it("accepts a post and coerces the date", () => {
    const r = writingSchema.safeParse(post);
    expect(r.success).toBe(true);
    expect(r.success && r.data.date instanceof Date).toBe(true);
  });
  it("rejects an unknown motif", () => {
    expect(writingSchema.safeParse({ ...post, motif: "sparkles" }).success).toBe(false);
  });
  it("accepts an optional linked project", () => {
    expect(writingSchema.safeParse({ ...post, project: "passfx" }).success).toBe(true);
  });
});

describe("library", () => {
  const entry = {
    topic: "Sample topic",
    audience: ["recruiters"],
    sources: [{ label: "Sample source" }],
    approved_on: "2026-11-03",
  };
  it("accepts an approved entry and defaults language to en", () => {
    const r = librarySchema.safeParse(entry);
    expect(r.success && r.data.language).toBe("en");
  });
  it("fails a non-sample entry without approved_on (only Din sets it)", () => {
    const r = librarySchema.safeParse({ ...entry, approved_on: null });
    expect(r.success).toBe(false);
    expect(!r.success && r.error.issues[0].path).toEqual(["approved_on"]);
  });
  it("lets a sample entry go without approval", () => {
    expect(librarySchema.safeParse({ ...entry, approved_on: null, sample: true }).success).toBe(true);
  });
  it("rejects a language other than en or fr", () => {
    expect(librarySchema.safeParse({ ...entry, language: "de" }).success).toBe(false);
  });
});

describe("suggested", () => {
  const item = {
    question: "Sample question?",
    answer: "Sample answer.",
    sources: [{ label: "About", href: "/about/" }],
    order: 1,
    status: "draft",
  };
  it("accepts a suggested answer", () => {
    expect(suggestedSchema.safeParse(item).success).toBe(true);
  });
  it("needs at least one source", () => {
    expect(suggestedSchema.safeParse({ ...item, sources: [] }).success).toBe(false);
  });
  it("only allows site paths or https links as sources", () => {
    expect(suggestedSchema.safeParse({ ...item, sources: [{ label: "x", href: "javascript:alert(1)" }] }).success).toBe(false);
  });
});
```

- [ ] **Step 3: Run the test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/schemas.test.ts`
Expected: FAIL, cannot resolve `../../src/lib/schemas`.

- [ ] **Step 4: Write the implementation**

```ts
// site/src/lib/schemas.ts
// Collection schemas (PRD section 2). Factories take Astro's image() and reference()
// so the same rules can be unit tested without astro:content.
import { z } from "astro/zod";

export const PROJECT_KINDS = ["ml", "data-engineering", "data-science", "research"] as const;
export const WRITING_KINDS = ["case-study", "devlog", "note"] as const;
export const MOTIFS = ["nodes", "bars", "lens"] as const;
export const LANGUAGES = ["en", "fr"] as const;
export const AUDIENCES = ["admissions", "recruiters", "visitors"] as const;

export type ProjectKind = (typeof PROJECT_KINDS)[number];
export type WritingKind = (typeof WRITING_KINDS)[number];
export type Motif = (typeof MOTIFS)[number];

export const statusSchema = z.enum(["draft", "published"]);
const sitePath = z.string().regex(/^\/(?!\/)/, "must be a site path starting with /");
const href = z.string().regex(/^(\/(?!\/)|https:\/\/)/, "must be a site path or an https link");
export const linkSchema = z.object({ label: z.string().min(1), href });
const sourceSchema = z.object({ label: z.string().min(1), url: z.url().optional() });

export function makeProjectSchema<I extends z.ZodType>(image: () => I) {
  return z.object({
    title: z.string().min(1).max(80),
    kind: z.enum(PROJECT_KINDS),
    summary: z.string().min(1).max(200),
    role: z.string().min(1).max(300),
    stack: z.array(z.string().min(1)).min(1),
    results: z.array(z.object({ value: z.string().min(1), label: z.string().min(1) })).min(1),
    featured: z.number().int().min(1).max(4).optional(),
    demo: z
      .object({ type: z.enum(["live", "chart", "video"]), src: sitePath })
      .optional(),
    capture: image(),
    captureAlt: z.string().min(1),
    repo: z.url({ protocol: /^https$/ }).optional(),
    status: statusSchema,
  });
}

export function makeWritingSchema<R extends z.ZodType>(projectRef: R) {
  return z.object({
    title: z.string().min(1).max(120),
    kind: z.enum(WRITING_KINDS),
    date: z.coerce.date(),
    summary: z.string().min(1).max(240),
    motif: z.enum(MOTIFS),
    project: projectRef.optional(),
    // PRD lists a devlog flag (social card C). Left out, it follows kind === "devlog".
    devlog: z.boolean().optional(),
    status: statusSchema,
  });
}

export const librarySchema = z
  .object({
    topic: z.string().min(1),
    audience: z.array(z.enum(AUDIENCES)).min(1),
    sources: z.array(sourceSchema).min(1),
    language: z.enum(LANGUAGES).default("en"),
    approved_on: z.coerce.date().nullable().default(null),
    sample: z.boolean().default(false),
  })
  .refine((d) => d.sample || d.approved_on !== null, {
    message: "approved_on is required; only Din sets it",
    path: ["approved_on"],
  });

export const suggestedSchema = z.object({
  question: z.string().min(1).max(120),
  answer: z.string().min(1).max(1500),
  sources: z.array(linkSchema).min(1),
  language: z.enum(LANGUAGES).default("en"),
  order: z.number().int().min(1),
  generated_on: z.coerce.date().nullable().default(null),
  status: statusSchema,
});
```

```ts
// site/src/lib/kinds.ts
import type { ProjectKind, WritingKind } from "./schemas";

export const KIND_LABELS: Record<ProjectKind, string> = {
  ml: "ML",
  "data-engineering": "Data engineering",
  "data-science": "Data science",
  research: "Research",
};

export const WRITING_KIND_LABELS: Record<WritingKind, string> = {
  "case-study": "Case study",
  devlog: "Devlog",
  note: "Note",
};
```

```ts
// site/src/content.config.ts
import { defineCollection, reference } from "astro:content";
import { file, glob } from "astro/loaders";
import { librarySchema, makeProjectSchema, makeWritingSchema, suggestedSchema } from "./lib/schemas";

// Files starting with _ (READMEs, capture folders) are not entries.
const projects = defineCollection({
  loader: glob({ pattern: "**/[^_]*.mdx", base: "./src/content/projects" }),
  schema: ({ image }) => makeProjectSchema(image),
});

const writing = defineCollection({
  loader: glob({ pattern: "**/[^_]*.mdx", base: "./src/content/writing" }),
  schema: makeWritingSchema(reference("projects")),
});

// Ottie's library: never rendered as a page (PRD 2).
const library = defineCollection({
  loader: glob({ pattern: "**/[^_]*.md", base: "./src/content/library" }),
  schema: librarySchema,
});

const suggested = defineCollection({
  loader: file("src/content/suggested/suggested.yaml"),
  schema: suggestedSchema,
});

export const collections = { projects, writing, library, suggested };
```

Create the three READMEs (the leading `_` keeps them out of the collections):

```md
<!-- site/src/content/projects/_README.md -->
# Projects

One MDX file per project; the file name is the URL (`passfx.mdx` is `/work/passfx/`). Frontmatter is checked by `src/lib/schemas.ts`, and a missing or wrong field fails the build. `status: draft` never renders in production. The stage capture must be 16:10 and lives in `_captures/`. The name `kind` is reserved (it is the filter route).
```

```md
<!-- site/src/content/writing/_README.md -->
# Writing

One MDX file per post; the file name is the URL. `kind` is `case-study`, `devlog` or `note`; devlogs get social card C and Ottie. `project` links a project by its file name. `status: draft` never renders in production.
```

```md
<!-- site/src/content/library/_README.md -->
# Library

Ottie's approved library (PRD section 2). Never rendered as a page. Entries reach this folder only through a PR Din reviews, and only Din sets `approved_on`. Sample entries for tests and evals carry `sample: true` and never reach the production index. M3 owns the entries.
```

- [ ] **Step 5: Run the tests**

Run: `pnpm --dir site exec vitest run tests/unit/schemas.test.ts`
Expected: PASS, all tests.

Run: `pnpm --dir site check`
Expected: PASS (empty collections only warn).

- [ ] **Step 6: Commit**

```bash
git add site/src/lib/schemas.ts site/src/lib/kinds.ts site/src/content.config.ts site/src/content site/tests/unit/schemas.test.ts site/package.json site/astro.config.mjs pnpm-lock.yaml
git commit -m "feat(site): typed content collections for projects, writing, library and suggested"
```

## Task 3: Sample content, clearly marked

**Files:**
- Create: `site/src/content/projects/_captures/sample-window.svg`, `site/src/content/projects/{passfx,claude-runner,claudehome}.mdx`, `site/src/content/writing/{sample-case-study,sample-devlog,sample-note}.mdx`, `site/src/content/suggested/suggested.yaml`

**Interfaces:**
- Consumes: the schemas from Task 2.
- Produces: draft entries the e2e tests in later tasks visit: projects `passfx` (featured 1, `data-engineering`), `claude-runner` (featured 2, `ml`), `claudehome` (featured 3, `research`); posts `sample-case-study` (linked to `passfx`), `sample-devlog`, `sample-note`; suggested `sample-what-does-din-do`, `sample-open-to-roles`.

The three project names are Din's placeholder repos (PRD 2). Their text says nothing about what they do, because that would be an invented fact.

- [ ] **Step 1: Create the capture (exactly 16:10)**

```svg
<!-- site/src/content/projects/_captures/sample-window.svg -->
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
  <rect width="1600" height="1000" fill="#F4F1EA"/>
  <rect x="80" y="80" width="1440" height="840" rx="20" fill="none" stroke="#2B3A44" stroke-opacity=".25" stroke-width="4" stroke-dasharray="18 14"/>
  <text x="800" y="520" text-anchor="middle" font-family="ui-monospace, Menlo, monospace" font-size="48" fill="#4A555C">Sample capture (16:10)</text>
</svg>
```

- [ ] **Step 2: Create the sample projects**

```mdx
---
# site/src/content/projects/passfx.mdx
title: passfx
kind: data-engineering
summary: Sample project. Din writes the real summary when this project is ready.
role: Sample role line. Din fills this in.
stack: [sample]
results:
  - value: "n/a"
    label: Sample result. Real numbers only, from Din.
featured: 1
capture: ./_captures/sample-window.svg
captureAlt: A sample capture placeholder in a 16:10 window
status: draft
---

This is a sample case study. It shows the layout only and says nothing about the real project.

## The problem

Sample section.

## What I built

Sample section.

## Results

Sample section.
```

```mdx
---
# site/src/content/projects/claude-runner.mdx
title: claude-runner
kind: ml
summary: Sample project. Din writes the real summary when this project is ready.
role: Sample role line. Din fills this in.
stack: [sample]
results:
  - value: "n/a"
    label: Sample result. Real numbers only, from Din.
featured: 2
capture: ./_captures/sample-window.svg
captureAlt: A sample capture placeholder in a 16:10 window
status: draft
---

This is a sample case study. It shows the layout only and says nothing about the real project.
```

```mdx
---
# site/src/content/projects/claudehome.mdx
title: claudehome
kind: research
summary: Sample project. Din writes the real summary when this project is ready.
role: Sample role line. Din fills this in.
stack: [sample]
results:
  - value: "n/a"
    label: Sample result. Real numbers only, from Din.
featured: 3
capture: ./_captures/sample-window.svg
captureAlt: A sample capture placeholder in a 16:10 window
status: draft
---

This is a sample case study. It shows the layout only and says nothing about the real project.
```

- [ ] **Step 3: Create the sample posts**

````mdx
---
# site/src/content/writing/sample-case-study.mdx
title: Sample case study post
kind: case-study
date: 2026-10-27
summary: A sample post that shows the layout of a case study. Not real content.
motif: nodes
project: passfx
status: draft
---

This is a sample post. It exists so the layout can be reviewed, and says nothing about Din's work.

## A heading

A paragraph of sample text long enough to show the reading measure, line height and the way links look, like [the work page](/work/).

- A list item
- Another list item

```python
print("sample code block")
```
````

```mdx
---
# site/src/content/writing/sample-devlog.mdx
title: Sample devlog post
kind: devlog
date: 2026-10-26
summary: A sample devlog that shows card C and Ottie's spot. Not real content.
motif: lens
status: draft
---

This is a sample devlog. It says nothing about Din's work.
```

```mdx
---
# site/src/content/writing/sample-note.mdx
title: Sample note
kind: note
date: 2026-10-25
summary: A sample note. Not real content.
motif: bars
status: draft
---

This is a sample note. It says nothing about Din's work.
```

- [ ] **Step 4: Create the sample suggested answers**

```yaml
# site/src/content/suggested/suggested.yaml
# Suggested questions for the home page (PRD 2 and 3). Din writes the questions;
# M3's script drafts the answers from the library; Din reviews them in a PR and sets
# status: published. Samples below say nothing about Din.
- id: sample-what-does-din-do
  question: Sample question about Din's work?
  answer: Sample answer. The real answer comes from Ottie's library after Din reviews it.
  sources:
    - label: About
      href: /about/
  order: 1
  status: draft
- id: sample-open-to-roles
  question: Sample question about roles?
  answer: Sample answer. The real answer comes from Ottie's library after Din reviews it.
  sources:
    - label: Contact
      href: /contact/
  order: 2
  status: draft
```

- [ ] **Step 5: Verify the content parses**

Run: `pnpm --dir site check && pnpm --dir site build`
Expected: PASS with no schema errors.

Then break one field on purpose to prove the build guards it: change `kind: ml` to `kind: web` in `claude-runner.mdx` and run `pnpm --dir site build`.
Expected: FAIL naming `claude-runner` and `kind`. Revert the change.

- [ ] **Step 6: Commit**

```bash
git add site/src/content
git commit -m "feat(site): sample projects, posts and suggested answers, all drafts"
```

## Task 4: Content helpers (sorting, filtering, validation)

**Files:**
- Create: `site/src/lib/content.ts`, `site/src/lib/collections.ts`
- Test: `site/tests/unit/content.test.ts`

**Interfaces:**
- Consumes: `isVisible`, `Status` (Task 1); `PROJECT_KINDS`, `ProjectKind` (Task 2).
- Produces (pure, `content.ts`): `visible<T>(entries, showDrafts)`, `sortProjects`, `featuredProjects(projects, max = 4)`, `kindsWithProjects(projects): ProjectKind[]`, `sortPosts`, `latestPosts(posts, n = 3)`, `linkedProject(post, projects)`, `postsForProject(posts, projectId)`, `readingMinutes(body: string): number`, `assertStageRatio(size, id)`, `validateProjects(projects)`, `RESERVED_PROJECT_IDS = ["kind"]`. (Astro, `collections.ts`): `getVisibleProjects()`, `getVisiblePosts()`, `getVisibleSuggested()`, each `Promise<CollectionEntry<...>[]>`, sorted.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/content.test.ts
import { describe, expect, it } from "vitest";
import {
  assertStageRatio,
  featuredProjects,
  kindsWithProjects,
  latestPosts,
  linkedProject,
  postsForProject,
  readingMinutes,
  sortPosts,
  sortProjects,
  validateProjects,
  visible,
} from "../../src/lib/content";

const proj = (id: string, data: Record<string, unknown> = {}) => ({
  id,
  data: { title: id, kind: "ml", status: "published", capture: { width: 1600, height: 1000 }, ...data },
});
const post = (id: string, date: string, data: Record<string, unknown> = {}) => ({
  id,
  data: { title: id, date: new Date(date), status: "published", ...data },
});

describe("visibility", () => {
  it("drops drafts unless drafts are on", () => {
    const all = [proj("a"), proj("b", { status: "draft" })];
    expect(visible(all, false).map((p) => p.id)).toEqual(["a"]);
    expect(visible(all, true).map((p) => p.id)).toEqual(["a", "b"]);
  });
  it("handles empty collections (production before launch)", () => {
    expect(visible([], false)).toEqual([]);
    expect(featuredProjects([])).toEqual([]);
    expect(kindsWithProjects([])).toEqual([]);
    expect(latestPosts([])).toEqual([]);
  });
});

describe("projects", () => {
  it("puts featured projects first in featured order, then the rest by title", () => {
    const sorted = sortProjects([proj("zeta"), proj("beta", { featured: 2 }), proj("alpha"), proj("gamma", { featured: 1 })]);
    expect(sorted.map((p) => p.id)).toEqual(["gamma", "beta", "alpha", "zeta"]);
  });
  it("returns at most four featured projects", () => {
    const many = [1, 2, 3, 4].map((n) => proj(`p${n}`, { featured: n })).concat(proj("p5"));
    expect(featuredProjects(many).map((p) => p.id)).toEqual(["p1", "p2", "p3", "p4"]);
  });
  it("lists only kinds that have projects, in the PRD order", () => {
    expect(kindsWithProjects([proj("a", { kind: "research" }), proj("b", { kind: "ml" })])).toEqual(["ml", "research"]);
  });
  it("accepts a 16:10 capture within 1 percent", () => {
    expect(() => assertStageRatio({ width: 1600, height: 1000 }, "a")).not.toThrow();
    expect(() => assertStageRatio({ width: 1601, height: 1000 }, "a")).not.toThrow();
  });
  it("rejects a capture that is not 16:10", () => {
    expect(() => assertStageRatio({ width: 1920, height: 1080 }, "a")).toThrow(/a: stage capture must be 16:10/);
  });
  it("rejects two projects with the same featured order", () => {
    expect(() => validateProjects([proj("a", { featured: 1 }), proj("b", { featured: 1 })])).toThrow(/featured 1/);
  });
  it("rejects the reserved id kind", () => {
    expect(() => validateProjects([proj("kind")])).toThrow(/reserved/);
  });
});

describe("posts", () => {
  it("sorts newest first, then by id", () => {
    const sorted = sortPosts([post("b", "2026-10-01"), post("a", "2026-10-01"), post("c", "2026-11-01")]);
    expect(sorted.map((p) => p.id)).toEqual(["c", "a", "b"]);
  });
  it("returns the latest three", () => {
    const four = ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"].map((d, i) => post(`p${i}`, d));
    expect(latestPosts(four).map((p) => p.id)).toEqual(["p3", "p2", "p1"]);
  });
  it("links a post to its project only when that project is visible", () => {
    const p = post("x", "2026-10-01", { project: { collection: "projects", id: "draft-one" } });
    expect(linkedProject(p, [proj("other")])).toBeNull();
    expect(linkedProject(p, [proj("draft-one")])?.id).toBe("draft-one");
  });
  it("finds posts for a project", () => {
    const posts = [post("x", "2026-10-01", { project: { collection: "projects", id: "a" } }), post("y", "2026-10-02")];
    expect(postsForProject(posts, "a").map((p) => p.id)).toEqual(["x"]);
  });
});

describe("readingMinutes", () => {
  it("is at least one minute", () => {
    expect(readingMinutes("")).toBe(1);
  });
  it("counts about 220 words a minute and ignores MDX import lines", () => {
    const body = "import X from './x.astro';\n" + Array.from({ length: 441 }, () => "word").join(" ");
    expect(readingMinutes(body)).toBe(3);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/content.test.ts`
Expected: FAIL, cannot resolve `../../src/lib/content`.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/content.ts
// Pure rules over collection entries. collections.ts feeds these from astro:content.
import { isVisible, type Status } from "./drafts";
import { PROJECT_KINDS, type ProjectKind } from "./schemas";

type Entry<D> = { id: string; data: D };
type Ref = { collection: string; id: string };

export const RESERVED_PROJECT_IDS = ["kind"];

export function visible<T extends Entry<{ status: Status }>>(entries: T[], showDrafts: boolean): T[] {
  return entries.filter((e) => isVisible(e.data.status, showDrafts));
}

export function sortProjects<T extends Entry<{ title: string; featured?: number }>>(projects: T[]): T[] {
  return [...projects].sort((a, b) => {
    const fa = a.data.featured ?? Number.POSITIVE_INFINITY;
    const fb = b.data.featured ?? Number.POSITIVE_INFINITY;
    return fa - fb || a.data.title.localeCompare(b.data.title, "en");
  });
}

export function featuredProjects<T extends Entry<{ title: string; featured?: number }>>(projects: T[], max = 4): T[] {
  return sortProjects(projects.filter((p) => p.data.featured !== undefined)).slice(0, max);
}

export function kindsWithProjects(projects: Entry<{ kind: ProjectKind }>[]): ProjectKind[] {
  return PROJECT_KINDS.filter((k) => projects.some((p) => p.data.kind === k));
}

export function sortPosts<T extends Entry<{ date: Date }>>(posts: T[]): T[] {
  return [...posts].sort((a, b) => b.data.date.getTime() - a.data.date.getTime() || a.id.localeCompare(b.id));
}

export function latestPosts<T extends Entry<{ date: Date }>>(posts: T[], n = 3): T[] {
  return sortPosts(posts).slice(0, n);
}

export function linkedProject<P extends Entry<unknown>>(post: Entry<{ project?: Ref }>, projects: P[]): P | null {
  const id = post.data.project?.id;
  return id ? (projects.find((p) => p.id === id) ?? null) : null;
}

export function postsForProject<T extends Entry<{ project?: Ref }>>(posts: T[], projectId: string): T[] {
  return posts.filter((p) => p.data.project?.id === projectId);
}

export function readingMinutes(body: string): number {
  const text = body.replace(/^(import|export)\s.*$/gm, "");
  const words = text.match(/\S+/g)?.length ?? 0;
  return Math.max(1, Math.ceil(words / 220));
}

export function assertStageRatio(size: { width: number; height: number }, id: string): void {
  const ratio = size.width / size.height;
  if (Math.abs(ratio - 1.6) / 1.6 > 0.01) {
    throw new Error(`${id}: stage capture must be 16:10, got ${size.width}x${size.height}`);
  }
}

export function validateProjects(
  projects: Entry<{ featured?: number; capture: { width: number; height: number } }>[],
): void {
  const seen = new Map<number, string>();
  for (const p of projects) {
    if (RESERVED_PROJECT_IDS.includes(p.id)) throw new Error(`${p.id}: this project id is reserved`);
    assertStageRatio(p.data.capture, p.id);
    const f = p.data.featured;
    if (f !== undefined) {
      if (seen.has(f)) throw new Error(`${p.id} and ${seen.get(f)} both use featured ${f}`);
      seen.set(f, p.id);
    }
  }
}
```

```ts
// site/src/lib/collections.ts
// The only module that calls getCollection. Everything it returns is visible and sorted.
import { getCollection } from "astro:content";
import { SHOW_DRAFTS } from "./build";
import { sortPosts, sortProjects, validateProjects, visible } from "./content";

export async function getVisibleProjects() {
  const all = await getCollection("projects");
  validateProjects(all); // drafts too, so a bad capture fails before it is published
  return sortProjects(visible(all, SHOW_DRAFTS));
}

export async function getVisiblePosts() {
  return sortPosts(visible(await getCollection("writing"), SHOW_DRAFTS));
}

export async function getVisibleSuggested() {
  const items = visible(await getCollection("suggested"), SHOW_DRAFTS);
  return items.sort((a, b) => a.data.order - b.data.order);
}
```

- [ ] **Step 4: Run the tests**

Run: `pnpm --dir site exec vitest run tests/unit/content.test.ts && pnpm --dir site check`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/content.ts site/src/lib/collections.ts site/tests/unit/content.test.ts
git commit -m "feat(site): content helpers for visibility, order and stage captures"
```

## Task 5: Site identity, profile copy and launch blockers

**Files:**
- Create: `site/src/data/site.ts`, `site/src/data/profile.ts`, `site/src/lib/launch.ts`, `site/scripts/launch-blockers.ts`
- Modify: `site/src/lib/schemas.ts` (add `profileSchema`, `siteSchema`), `site/package.json` (script `launch:blockers`)
- Test: `site/tests/unit/profile.test.ts`, `site/tests/unit/launch.test.ts`

**Interfaces:**
- Consumes: `statusSchema` (Task 2), `isVisible` (Task 1).
- Produces: `site: SiteConfig` with `name`, `legalName: string | null`, `url`, `email`, `links: { github: string | null; linkedin: string | null; resume: string | null }`, `sameAs: string[]`; `profile: Profile` with draftable fields `roleLine`, `aboutTeaser`, `bio`, `skills`, `languages` (each `{ status, value }`) and `timeline: TimelineEntry[]` (each with its own `status`); `visibleValue(d, showDrafts)`; `launchBlockers(site, profile, counts): string[]`.

- [ ] **Step 1: Write the failing tests**

```ts
// site/tests/unit/profile.test.ts
import { describe, expect, it } from "vitest";
import { profileSchema, siteSchema, visibleValue } from "../../src/lib/schemas";
import { profile } from "../../src/data/profile";
import { site } from "../../src/data/site";

describe("profile data", () => {
  it("parses", () => {
    expect(profileSchema.safeParse(profile).success).toBe(true);
  });
  it("keeps every sample as a draft", () => {
    const sampleText = JSON.stringify(profile).match(/Sample/g)?.length ?? 0;
    const draftSections = [profile.roleLine, profile.aboutTeaser, profile.bio, profile.skills, profile.languages]
      .filter((d) => d.status === "draft").length;
    expect(sampleText).toBeGreaterThan(0);
    expect(draftSections).toBe(5);
    expect(profile.timeline.every((t) => t.status === "draft")).toBe(true);
  });
  it("rejects a timeline date that is not YYYY or YYYY-MM", () => {
    const bad = { ...profile, timeline: [{ ...profile.timeline[0], start: "Sept 2024" }] };
    expect(profileSchema.safeParse(bad).success).toBe(false);
  });
});

describe("site data", () => {
  it("parses and uses https links only", () => {
    expect(siteSchema.safeParse(site).success).toBe(true);
    expect(siteSchema.safeParse({ ...site, sameAs: ["http://example.com"] }).success).toBe(false);
  });
});

describe("visibleValue", () => {
  it("hides a draft unless drafts are on", () => {
    expect(visibleValue({ status: "draft", value: "x" }, false)).toBeNull();
    expect(visibleValue({ status: "draft", value: "x" }, true)?.value).toBe("x");
    expect(visibleValue({ status: "published", value: "x" }, false)?.value).toBe("x");
  });
});
```

```ts
// site/tests/unit/launch.test.ts
import { describe, expect, it } from "vitest";
import { launchBlockers } from "../../src/lib/launch";
import { profile } from "../../src/data/profile";
import { site } from "../../src/data/site";

describe("launchBlockers", () => {
  it("lists every missing fact while the samples are in place", () => {
    const list = launchBlockers(site, profile, { projects: 0, posts: 0, suggested: 0 });
    expect(list).toEqual(
      expect.arrayContaining([
        expect.stringMatching(/role line/),
        expect.stringMatching(/bio/),
        expect.stringMatching(/timeline/),
        expect.stringMatching(/LinkedIn/),
        expect.stringMatching(/resume/),
        expect.stringMatching(/published project/),
        expect.stringMatching(/suggested/),
      ]),
    );
  });
  it("is empty when everything is published and filled in", () => {
    const pub = <T>(d: { value: T }) => ({ status: "published" as const, value: d.value });
    const done = {
      ...profile,
      roleLine: pub(profile.roleLine), aboutTeaser: pub(profile.aboutTeaser), bio: pub(profile.bio),
      skills: pub(profile.skills), languages: pub(profile.languages),
      timeline: profile.timeline.map((t) => ({ ...t, status: "published" as const })),
    };
    const filled = { ...site, legalName: "Name", links: { github: "https://github.com/x", linkedin: "https://www.linkedin.com/in/x", resume: "/resume.pdf" } };
    expect(launchBlockers(filled, done, { projects: 3, posts: 3, suggested: 4 })).toEqual([]);
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir site exec vitest run tests/unit/profile.test.ts tests/unit/launch.test.ts`
Expected: FAIL, missing exports and modules.

- [ ] **Step 3: Write the implementation**

Add `import { isVisible, type Status } from "./drafts";` to the imports at the top of `site/src/lib/schemas.ts`, then append:

```ts
const draftable = <T extends z.ZodType>(value: T) => z.object({ status: statusSchema, value });
const yearMonth = z.string().regex(/^\d{4}(-(0[1-9]|1[0-2]))?$/, "use YYYY or YYYY-MM");
const https = z.url({ protocol: /^https$/ });

export const timelineEntrySchema = z.object({
  status: statusSchema,
  kind: z.enum(["education", "experience"]),
  title: z.string().min(1),
  org: z.string().min(1),
  start: yearMonth,
  end: yearMonth.nullable(), // null means ongoing
  detail: z.string().optional(),
  project: z.string().optional(), // a project id, linked when that project is visible
});

export const profileSchema = z.object({
  roleLine: draftable(z.string().min(1).max(90)),
  aboutTeaser: draftable(z.string().min(1).max(240)),
  bio: draftable(z.array(z.string().min(1)).min(1)),
  timeline: z.array(timelineEntrySchema),
  skills: draftable(z.array(z.object({ group: z.string().min(1), items: z.array(z.string().min(1)).min(1) })).min(1)),
  languages: draftable(z.array(z.object({ name: z.string().min(1), level: z.string().min(1) })).min(1)),
});

export const siteSchema = z.object({
  name: z.string().min(1),
  legalName: z.string().min(1).nullable(),
  url: https,
  email: z.email(),
  links: z.object({
    github: https.nullable(),
    linkedin: https.nullable(),
    resume: z.string().regex(/^\/[\w./-]+\.pdf$/).nullable(),
  }),
  sameAs: z.array(https),
});

export type Profile = z.infer<typeof profileSchema>;
export type TimelineEntry = z.infer<typeof timelineEntrySchema>;
export type SiteConfig = z.infer<typeof siteSchema>;

export function visibleValue<T>(d: { status: Status; value: T }, showDrafts: boolean) {
  return isVisible(d.status, showDrafts) ? d : null;
}
```

```ts
// site/src/data/site.ts
// Facts and links about Din. A null is something only Din can fill in (see the M1 plan, Din tasks).
import { siteSchema, type SiteConfig } from "../lib/schemas";

export const site: SiteConfig = siteSchema.parse({
  name: "Din",
  legalName: null,
  url: "https://dins.dev",
  email: "din@dins.dev",
  links: {
    github: "https://github.com/dinsdev",
    linkedin: null,
    resume: null,
  },
  sameAs: ["https://github.com/dinsdev"],
});
```

```ts
// site/src/data/profile.ts
// Din's copy for the home hero and /about. Every value here is a sample until Din writes it.
import { profileSchema, type Profile } from "../lib/schemas";

export const profile: Profile = profileSchema.parse({
  roleLine: { status: "draft", value: "Sample role line. Din writes this." },
  aboutTeaser: { status: "draft", value: "Sample about teaser. Din writes one or two sentences here." },
  bio: {
    status: "draft",
    value: [
      "Sample bio paragraph. Din writes the real bio.",
      "A second sample paragraph, to show the spacing between paragraphs.",
    ],
  },
  timeline: [
    { status: "draft", kind: "experience", title: "Sample role", org: "Sample organization", start: "2025-01", end: null, detail: "Sample detail." },
    { status: "draft", kind: "education", title: "Sample degree", org: "Sample university", start: "2020", end: "2024", detail: "Sample thesis line." },
  ],
  skills: { status: "draft", value: [{ group: "Sample group", items: ["sample skill", "another sample skill"] }] },
  languages: {
    status: "draft",
    value: [
      { name: "English", level: "Sample level. Din fills this in." },
      { name: "French", level: "Sample level. Din fills this in." },
    ],
  },
});
```

```ts
// site/src/lib/launch.ts
// What Din still owes before launch. Printed by `pnpm --dir site launch:blockers`; M5 can gate on it.
import type { Profile, SiteConfig } from "./schemas";

export function launchBlockers(
  site: SiteConfig,
  profile: Profile,
  counts: { projects: number; posts: number; suggested: number },
): string[] {
  const out: string[] = [];
  const draft = (label: string, d: { status: string }) => d.status === "draft" && out.push(`${label} is still a sample (profile.ts)`);
  draft("The role line", profile.roleLine);
  draft("The about teaser", profile.aboutTeaser);
  draft("The bio", profile.bio);
  draft("Skills", profile.skills);
  draft("Language levels", profile.languages);
  if (profile.timeline.length === 0 || profile.timeline.some((t) => t.status === "draft")) out.push("The timeline has sample or missing entries (profile.ts)");
  if (!site.legalName) out.push("The name for structured data is not set (site.ts legalName)");
  if (!site.links.linkedin) out.push("The LinkedIn URL is not set (site.ts)");
  if (!site.links.resume) out.push("The resume PDF is not linked (site.ts links.resume)");
  if (counts.projects === 0) out.push("There is no published project");
  if (counts.posts === 0) out.push("There is no published post");
  if (counts.suggested === 0) out.push("There are no published suggested answers");
  return out;
}
```

```ts
// site/scripts/launch-blockers.ts
// Usage: pnpm --dir site launch:blockers  (exit 1 while anything is missing)
import { readdirSync, readFileSync } from "node:fs";
import { launchBlockers } from "../src/lib/launch.ts";
import { profile } from "../src/data/profile.ts";
import { site } from "../src/data/site.ts";

const published = (dir: string) =>
  readdirSync(new URL(`../src/content/${dir}/`, import.meta.url))
    .filter((f) => f.endsWith(".mdx") && !f.startsWith("_"))
    .filter((f) => /^status:\s*published\s*$/m.test(readFileSync(new URL(`../src/content/${dir}/${f}`, import.meta.url), "utf8"))).length;
const suggestedYaml = readFileSync(new URL("../src/content/suggested/suggested.yaml", import.meta.url), "utf8");

const list = launchBlockers(site, profile, {
  projects: published("projects"),
  posts: published("writing"),
  suggested: suggestedYaml.match(/^\s+status:\s*published\s*$/gm)?.length ?? 0,
});
for (const item of list) console.log(`- ${item}`);
console.log(list.length ? `${list.length} launch blockers` : "No launch blockers");
process.exit(list.length ? 1 : 0);
```

Add to `site/package.json` scripts: `"launch:blockers": "node scripts/launch-blockers.ts"` (Node 24 runs TypeScript with type stripping; the scripts use only erasable syntax and `.ts` import extensions).

- [ ] **Step 4: Run the tests and the script**

Run: `pnpm --dir site exec vitest run tests/unit/profile.test.ts tests/unit/launch.test.ts`
Expected: PASS.

Run: `pnpm --dir site launch:blockers`
Expected: exit 1, listing 12 blockers (five sample profile sections, the timeline, legalName, LinkedIn, resume, and no published project, post or suggested answer), ending "12 launch blockers".

- [ ] **Step 5: Commit**

```bash
git add site/src/data site/src/lib/schemas.ts site/src/lib/launch.ts site/scripts/launch-blockers.ts site/package.json site/tests/unit/profile.test.ts site/tests/unit/launch.test.ts
git commit -m "feat(site): site identity, sample profile copy and a launch blockers list"
```

## Task 6: SEO helpers

**Files:**
- Create: `site/src/lib/seo.ts`, `site/src/lib/dates.ts`
- Test: `site/tests/unit/seo.test.ts`, `site/tests/unit/dates.test.ts`

**Interfaces:**
- Consumes: `SiteConfig` (Task 5).
- Produces: `SITE_URL`, `canonicalUrl(pathname, site = SITE_URL): string`, `pageTitle(title?: string): string`, `jsonLdScript(data: unknown): string`, `personJsonLd(site, description: string | null)`, `websiteJsonLd(site)`, `profilePageJsonLd(site, description)`, `articleJsonLd(input)`, `cardPath(pathname): string`, `cardUrlText(pathname): string`; `formatDate(d: Date): string`, `isoDate(d: Date): string`, `formatYearMonth(s: string | null): string`.

- [ ] **Step 1: Write the failing tests**

```ts
// site/tests/unit/seo.test.ts
import { describe, expect, it } from "vitest";
import { canonicalUrl, cardPath, cardUrlText, jsonLdScript, pageTitle, personJsonLd } from "../../src/lib/seo";
import { site } from "../../src/data/site";

describe("canonicalUrl", () => {
  it.each([
    ["/", "https://dins.dev/"],
    ["/work", "https://dins.dev/work/"],
    ["/work/", "https://dins.dev/work/"],
    ["/work/passfx?x=1#top", "https://dins.dev/work/passfx/"],
    ["//work//passfx", "https://dins.dev/work/passfx/"],
    ["/rss.xml", "https://dins.dev/rss.xml"],
  ])("%s -> %s", (input, expected) => {
    expect(canonicalUrl(input)).toBe(expected);
  });
});

describe("pageTitle", () => {
  it("names the site on its own for the home page", () => {
    expect(pageTitle()).toBe("Din · dins.dev");
  });
  it("adds the site to other titles", () => {
    expect(pageTitle("Work")).toBe("Work · dins.dev");
  });
});

describe("jsonLdScript", () => {
  it("cannot close the script tag or open a comment", () => {
    const out = jsonLdScript({ headline: "</script><!-- &  " });
    expect(out).not.toMatch(/<|>|&/);
    expect(JSON.parse(out).headline).toBe("</script><!-- &  ");
  });
});

describe("personJsonLd", () => {
  it("describes Din with sameAs and leaves out what is unknown", () => {
    const p = personJsonLd(site, null);
    expect(p["@type"]).toBe("Person");
    expect(p["@id"]).toBe("https://dins.dev/#person");
    expect(p.name).toBe("Din");
    expect(p.sameAs).toEqual(site.sameAs);
    expect("description" in p).toBe(false);
    expect("alternateName" in p).toBe(false);
  });
  it("uses the full name with Din as alternateName once Din sets it", () => {
    const p = personJsonLd({ ...site, legalName: "Full Name" }, "Role line");
    expect(p.name).toBe("Full Name");
    expect(p.alternateName).toBe("Din");
    expect(p.description).toBe("Role line");
  });
});

describe("cards", () => {
  it.each([
    ["/", "/og/index.png", "dins.dev"],
    ["/work/", "/og/work.png", "dins.dev/work"],
    ["/work/passfx/", "/og/work/passfx.png", "dins.dev/work/passfx"],
    ["/work/passfx", "/og/work/passfx.png", "dins.dev/work/passfx"],
  ])("%s", (path, png, text) => {
    expect(cardPath(path)).toBe(png);
    expect(cardUrlText(path)).toBe(text);
  });
});
```

```ts
// site/tests/unit/dates.test.ts
import { describe, expect, it } from "vitest";
import { formatDate, formatYearMonth, isoDate } from "../../src/lib/dates";

describe("dates", () => {
  it("formats a post date in UTC so build time zones do not shift it", () => {
    expect(formatDate(new Date("2026-10-27T00:00:00Z"))).toBe("27 October 2026");
    expect(isoDate(new Date("2026-10-27T00:00:00Z"))).toBe("2026-10-27");
  });
  it("formats timeline months and open ranges", () => {
    expect(formatYearMonth("2024-09")).toBe("Sep 2024");
    expect(formatYearMonth("2020")).toBe("2020");
    expect(formatYearMonth(null)).toBe("now");
  });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `pnpm --dir site exec vitest run tests/unit/seo.test.ts tests/unit/dates.test.ts`
Expected: FAIL, modules missing.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/seo.ts
import type { SiteConfig } from "./schemas";

export const SITE_URL = "https://dins.dev";

/** Absolute canonical URL. Page routes always end in "/", files keep their extension. */
export function canonicalUrl(pathname: string, site = SITE_URL): string {
  let p = (pathname.split(/[?#]/)[0] || "/").replace(/\/{2,}/g, "/");
  if (!p.startsWith("/")) p = `/${p}`;
  const last = p.split("/").pop() ?? "";
  if (!p.endsWith("/") && !last.includes(".")) p += "/";
  return new URL(p, site).href;
}

export function pageTitle(title?: string): string {
  return title ? `${title} · dins.dev` : "Din · dins.dev";
}

/** JSON for a <script type="application/ld+json">, safe against </script> and comment tricks. */
export function jsonLdScript(data: unknown): string {
  return JSON.stringify(data)
    .replace(/</g, "\\u003c")
    .replace(/>/g, "\\u003e")
    .replace(/&/g, "\\u0026")
    .replace(/ /g, "\\u2028")
    .replace(/ /g, "\\u2029");
}

const personId = (site: SiteConfig) => `${site.url}/#person`;

export function personJsonLd(site: SiteConfig, description: string | null) {
  const name = site.legalName ?? site.name;
  return {
    "@context": "https://schema.org",
    "@type": "Person",
    "@id": personId(site),
    name,
    ...(name !== site.name ? { alternateName: site.name } : {}),
    url: `${site.url}/`,
    email: `mailto:${site.email}`,
    ...(description ? { description } : {}),
    sameAs: site.sameAs,
  };
}

export function websiteJsonLd(site: SiteConfig) {
  return {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "@id": `${site.url}/#website`,
    url: `${site.url}/`,
    name: "dins",
    inLanguage: "en",
    publisher: { "@id": personId(site) },
  };
}

export function profilePageJsonLd(site: SiteConfig, description: string | null) {
  return {
    "@context": "https://schema.org",
    "@type": "ProfilePage",
    url: `${site.url}/about/`,
    mainEntity: personJsonLd(site, description),
  };
}

export function articleJsonLd(input: { site: SiteConfig; title: string; summary: string; date: Date; path: string }) {
  return {
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    headline: input.title,
    description: input.summary,
    datePublished: input.date.toISOString().slice(0, 10),
    url: canonicalUrl(input.path),
    image: new URL(cardPath(input.path), SITE_URL).href,
    author: { "@id": personId(input.site) },
  };
}

function trimmed(pathname: string): string {
  return canonicalUrl(pathname).slice(SITE_URL.length).replace(/^\/|\/$/g, "");
}

export function cardPath(pathname: string): string {
  return `/og/${trimmed(pathname) || "index"}.png`;
}

export function cardUrlText(pathname: string): string {
  const t = trimmed(pathname);
  return t ? `dins.dev/${t}` : "dins.dev";
}
```

```ts
// site/src/lib/dates.ts
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function formatDate(d: Date): string {
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" }).format(d);
}

export function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function formatYearMonth(s: string | null): string {
  if (s === null) return "now";
  const [year, month] = s.split("-");
  return month ? `${MONTHS[Number(month) - 1]} ${year}` : year;
}
```

- [ ] **Step 4: Run the tests**

Run: `pnpm --dir site exec vitest run tests/unit/seo.test.ts tests/unit/dates.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/seo.ts site/src/lib/dates.ts site/tests/unit/seo.test.ts site/tests/unit/dates.test.ts
git commit -m "feat(site): canonical URLs, titles, structured data and card paths"
```

## Task 7: Contact form contract

**Files:**
- Create: `site/src/lib/contact.ts`
- Test: `site/tests/unit/contact.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `CONTACT_FIELDS`, `CONTACT_LIMITS` (`message` 4000), `REASONS`, `type Reason = "role" | "admissions" | "hi"`, `CONTACT_REDIRECTS = { sent: "/contact/sent/", notSent: "/contact/not-sent/" }`, `type ContactInput`, `type ContactResult = { ok: true; value: ContactInput } | { ok: false; spam: boolean; errors: Partial<Record<"message" | "name" | "email", string>> }`, `parseContact(form: FormData | URLSearchParams): ContactResult` (strips control characters other than newline and tab). M4's `/api/contact` imports this module and extends it rather than writing a second parser, so the form and the endpoint cannot drift.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/contact.test.ts
import { describe, expect, it } from "vitest";
import { CONTACT_LIMITS, parseContact } from "../../src/lib/contact";

const form = (fields: Record<string, string>) => new URLSearchParams(fields);
const good = { message: "  Hello Din  ", reason: "admissions", name: " Sam ", email: "sam@example.com", website: "" };

describe("parseContact", () => {
  it("accepts a good message and trims it", () => {
    expect(parseContact(form(good))).toEqual({
      ok: true,
      value: { message: "Hello Din", reason: "admissions", name: "Sam", email: "sam@example.com" },
    });
  });
  it("defaults an unknown or missing reason to hi", () => {
    const r = parseContact(form({ ...good, reason: "sales" }));
    expect(r.ok && r.value.reason).toBe("hi");
  });
  it.each(["message", "name", "email"])("requires %s", (field) => {
    const r = parseContact(form({ ...good, [field]: "   " }));
    expect(r.ok).toBe(false);
    expect(!r.ok && r.errors[field as "message"]).toBeTruthy();
  });
  it("rejects an email without a domain", () => {
    const r = parseContact(form({ ...good, email: "sam@" }));
    expect(!r.ok && r.errors.email).toMatch(/email/);
  });
  it("rejects text over the limits", () => {
    const r = parseContact(form({ ...good, message: "x".repeat(CONTACT_LIMITS.message + 1) }));
    expect(!r.ok && r.errors.message).toMatch(/4000/);
  });
  it("strips control characters but keeps newlines and tabs", () => {
    const r = parseContact(form({ ...good, message: "a\u0000b\r\nc\td\u001b\u007f", name: "Sam\u0007" }));
    expect(r.ok && r.value.message).toBe("ab\nc\td");
    expect(r.ok && r.value.name).toBe("Sam");
  });
  it("rejects a message that is only control characters", () => {
    const r = parseContact(form({ ...good, message: "\u0000\u0001" }));
    expect(!r.ok && r.errors.message).toBeTruthy();
  });
  it("flags a filled honeypot as spam without saying why", () => {
    expect(parseContact(form({ ...good, website: "http://spam.test" }))).toEqual({ ok: false, spam: true, errors: {} });
  });
  it("reads FormData too", () => {
    const fd = new FormData();
    for (const [k, v] of Object.entries(good)) fd.set(k, v);
    expect(parseContact(fd).ok).toBe(true);
  });
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/contact.test.ts`
Expected: FAIL, module missing.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/contact.ts
// The contact form's contract, shared by the page (M1) and /api/contact (M4).

export const CONTACT_FIELDS = {
  message: "message",
  reason: "reason",
  name: "name",
  email: "email",
  honeypot: "website",
  turnstile: "cf-turnstile-response",
} as const;

// Admissions letters run long; the PRD sets no limit (M4).
export const CONTACT_LIMITS = { name: 100, email: 254, message: 4000 } as const;

export const REASONS = [
  { value: "role", label: "A role" },
  { value: "admissions", label: "Admissions" },
  { value: "hi", label: "Just saying hi" },
] as const;
export type Reason = (typeof REASONS)[number]["value"];

/** Where a plain form post is sent back with a 303. A post without JavaScript has no Turnstile
 * token and is never accepted (Din, 2026-10-21), so it always lands on notSent. */
export const CONTACT_REDIRECTS = { sent: "/contact/sent/", notSent: "/contact/not-sent/" } as const;

export type ContactInput = { message: string; reason: Reason; name: string; email: string };
type Field = "message" | "name" | "email";
export type ContactResult =
  | { ok: true; value: ContactInput }
  | { ok: false; spam: boolean; errors: Partial<Record<Field, string>> };

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// C0 and C1 control characters except tab (09) and newline (0A). CR (0D) goes too, so CRLF becomes LF.
const CONTROL = /[\u0000-\u0008\u000B-\u001F\u007F-\u009F]/g;

export function parseContact(form: FormData | URLSearchParams): ContactResult {
  const get = (k: string) => String(form.get(k) ?? "").replace(CONTROL, "").trim();
  if (get(CONTACT_FIELDS.honeypot)) return { ok: false, spam: true, errors: {} };

  const value = {
    message: get(CONTACT_FIELDS.message),
    name: get(CONTACT_FIELDS.name),
    email: get(CONTACT_FIELDS.email),
  };
  const errors: Partial<Record<Field, string>> = {};
  if (!value.message) errors.message = "Please write a message.";
  else if (value.message.length > CONTACT_LIMITS.message) errors.message = `Please keep the message under ${CONTACT_LIMITS.message} characters.`;
  if (!value.name) errors.name = "Please add your name.";
  else if (value.name.length > CONTACT_LIMITS.name) errors.name = `Please keep your name under ${CONTACT_LIMITS.name} characters.`;
  if (!EMAIL.test(value.email) || value.email.length > CONTACT_LIMITS.email) errors.email = "Please check your email address.";
  if (Object.keys(errors).length) return { ok: false, spam: false, errors };

  const raw = get(CONTACT_FIELDS.reason);
  const reason = (REASONS.find((r) => r.value === raw)?.value ?? "hi") as Reason;
  return { ok: true, value: { ...value, reason } };
}
```

- [ ] **Step 4: Run the test**

Run: `pnpm --dir site exec vitest run tests/unit/contact.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/contact.ts site/tests/unit/contact.test.ts
git commit -m "feat(site): contact form contract shared with the future endpoint"
```

## Task 8: Layout shell, theme toggle and the e2e harness

**Files:**
- Create: `site/src/styles/site.css`, `site/src/lib/theme.ts`, `site/src/lib/page.ts`, `site/src/components/{Seo,Nav,Footer,ThemeToggle,Wordmark,Draft,Prose}.astro`, `site/tests/e2e/{routes.ts,helpers.ts,pages.spec.ts,theme.spec.ts,layout.spec.ts}`
- Modify: `site/src/layouts/BaseLayout.astro`, `site/playwright.config.ts`, `site/src/pages/index.astro` (temporary shell until Task 9)
- Test: `site/tests/unit/theme.test.ts` and the e2e specs above

**Interfaces:**
- Consumes: `BUILD_FLAGS` (Task 1), `canonicalUrl`, `pageTitle`, `jsonLdScript`, `cardPath`, `cardUrlText`, `SITE_URL` (Task 6), `site` (Task 5).
- Produces: `BaseLayout.astro` props `SeoProps & { current?: NavKey }` from `site/src/lib/page.ts`, i.e. `{ title?: string; description: string; card: CardSpecInput | null; type?: "website" | "article"; noindex?: boolean; jsonLd?: object[]; current?: NavKey }` where `type CardSpecInput = { variant: "A" | "C" | "home"; label: string; title: string; subtitle?: string }` and `type NavKey = "work" | "writing" | "about" | "contact"`; `Draft.astro` props `{ status: Status; as?: "div" | "span" | "li" | "article" }`; `Prose.astro` (a styled wrapper for MDX); e2e `ROUTES`, `NOT_FOUND_PATH`, `expectNoAxeViolations(page)`; `theme.ts` exports `THEME_KEY`, `nextTheme`, `currentTheme`, `saveTheme`, `initThemeToggle`.

- [ ] **Step 1: Install axe if M0 did not**

Run: `pnpm --dir site list @axe-core/playwright || pnpm --dir site add -D @axe-core/playwright@~4.14.0`
Why: axe runs inside the Playwright tests (zero violations is an M1 gate).

- [ ] **Step 2: Write the failing theme unit test**

```ts
// site/tests/unit/theme.test.ts
import { describe, expect, it } from "vitest";
import { currentTheme, nextTheme, saveTheme } from "../../src/lib/theme";

const doc = (theme?: string) => ({ documentElement: { dataset: theme ? { theme } : {} } }) as unknown as Document;

describe("theme", () => {
  it("flips light and dark", () => {
    expect(nextTheme("light")).toBe("dark");
    expect(nextTheme("dark")).toBe("light");
  });
  it("prefers an explicit choice, then the system", () => {
    expect(currentTheme(doc("dark"), false)).toBe("dark");
    expect(currentTheme(doc(), true)).toBe("dark");
    expect(currentTheme(doc("purple"), false)).toBe("light");
  });
  it("survives storage that throws (private browsing)", () => {
    const blocked = { setItem: () => { throw new Error("SecurityError"); } };
    expect(() => saveTheme("dark", blocked)).not.toThrow();
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/theme.test.ts`
Expected: FAIL, module missing.

- [ ] **Step 3: Write `theme.ts`**

```ts
// site/src/lib/theme.ts
// The only thing the site stores: the visitor's theme choice, in localStorage (listed on /privacy).
export type Theme = "light" | "dark";
export const THEME_KEY = "dins-theme";

export function nextTheme(t: Theme): Theme {
  return t === "dark" ? "light" : "dark";
}

export function currentTheme(doc: Document, prefersDark: boolean): Theme {
  const t = doc.documentElement.dataset.theme;
  if (t === "light" || t === "dark") return t;
  return prefersDark ? "dark" : "light";
}

export function saveTheme(t: Theme, storage: Pick<Storage, "setItem"> | null): void {
  try {
    storage?.setItem(THEME_KEY, t);
  } catch {
    // Storage is blocked: the choice lasts for this page only.
  }
}

export function initThemeToggle(button: HTMLButtonElement | null): void {
  if (!button) return;
  const media = window.matchMedia("(prefers-color-scheme: dark)");
  const label = () => {
    const next = nextTheme(currentTheme(document, media.matches));
    button.setAttribute("aria-label", `Switch to ${next} theme`);
  };
  button.hidden = false;
  label();
  button.addEventListener("click", () => {
    const next = nextTheme(currentTheme(document, media.matches));
    document.documentElement.dataset.theme = next;
    let storage: Storage | null = null;
    try { storage = window.localStorage; } catch { storage = null; }
    saveTheme(next, storage);
    label();
  });
  media.addEventListener("change", label);
}
```

Run: `pnpm --dir site exec vitest run tests/unit/theme.test.ts`
Expected: PASS.

- [ ] **Step 4: Replace the Playwright projects and server**

In `site/playwright.config.ts`, keep M0's base URL, reporter and web server, add `DINS_SHOW_DRAFTS=1` to the server, and add M1's projects beside M0's `chromium`. `chromium` (light) stays the default: it runs every spec no other project claims, so the M2 to M5 specs land there without touching this file.

```ts
import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BASE_URL ?? "http://127.0.0.1:8787";
const desktop = devices["Desktop Chrome"];
// Specs that belong to one of M1's special projects; chromium runs everything else.
const claimed = [/no-js\.spec\.ts/, /reduced-motion\.spec\.ts/, /layout\.spec\.ts/];

export default defineConfig({
  testDir: "tests/e2e",
  forbidOnly: !!process.env.CI,
  fullyParallel: true,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: { baseURL, trace: "retain-on-failure" },
  projects: [
    { name: "chromium", use: { ...desktop, colorScheme: "light" }, testIgnore: claimed },
    { name: "dark", use: { ...desktop, colorScheme: "dark" }, testMatch: /pages\.spec\.ts/ },
    { name: "no-js", use: { ...desktop, javaScriptEnabled: false }, testMatch: /no-js\.spec\.ts/ },
    { name: "reduced-motion", use: { ...desktop, reducedMotion: "reduce" }, testMatch: /reduced-motion\.spec\.ts/ },
    { name: "phone", use: { ...devices["iPhone 13"], defaultBrowserType: "chromium" }, testMatch: /layout\.spec\.ts/ },
  ],
  // M0's server (wrangler dev, so /api/* works). Local runs build with drafts on (indexable, never deployed)
  // so the sample pages exist. With BASE_URL set (a preview or production), test that site instead.
  webServer: process.env.BASE_URL
    ? undefined
    : {
        command: "pnpm build && pnpm serve",
        url: `${baseURL}/api/health`,
        env: { DINS_SHOW_DRAFTS: "1" },
        reuseExistingServer: !process.env.CI,
        timeout: 180_000,
      },
});
```

- [ ] **Step 5: Write the e2e helpers and route list**

```ts
// site/tests/e2e/routes.ts
// Every route the e2e suite visits. Content routes come from the content files, so a new
// project or post is covered without editing this file.
import { readdirSync, readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const CONTENT = fileURLToPath(new URL("../../src/content/", import.meta.url));
// Local runs build with DINS_SHOW_DRAFTS=1; a BASE_URL run (M5, production) only sees published content.
export const DRAFTS_SHOWN = !process.env.BASE_URL;

type Item = { id: string; kind: string };
function items(dir: string): Item[] {
  return readdirSync(CONTENT + dir)
    .filter((f) => f.endsWith(".mdx") && !f.startsWith("_"))
    .map((f) => ({ f, text: readFileSync(`${CONTENT}${dir}/${f}`, "utf8") }))
    .filter(({ text }) => DRAFTS_SHOWN || !/^status:\s*draft\s*$/m.test(text))
    .map(({ f, text }) => ({ id: f.slice(0, -4), kind: text.match(/^kind:\s*(\S+)/m)?.[1] ?? "" }));
}

export const PROJECTS = items("projects");
export const POSTS = items("writing");

// Grows as page tasks land (Tasks 9 to 15 each add their routes here).
export const STATIC_ROUTES: string[] = ["/"];
export const UTILITY_ROUTES: string[] = []; // noindex pages, not in the sitemap
export const CONTENT_ROUTES: string[] = [];
export const NOT_FOUND_PATH = "/this-page-does-not-exist/";

export const ROUTES = () => [...STATIC_ROUTES, ...CONTENT_ROUTES, ...UTILITY_ROUTES];
```

```ts
// site/tests/e2e/helpers.ts
import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

export async function expectNoAxeViolations(page: Page) {
  const { violations } = await new AxeBuilder({ page }).analyze();
  const summary = violations.map((v) => `${v.id}: ${v.nodes.map((n) => n.target.join(" ")).join(", ")}`).join("\n");
  expect(violations, summary).toEqual([]);
}
```

```ts
// site/tests/e2e/pages.spec.ts
// Runs in the chromium (light) and dark projects: every route renders and axe finds nothing.
import { expect, test } from "@playwright/test";
import { expectNoAxeViolations } from "./helpers";
import { NOT_FOUND_PATH, ROUTES } from "./routes";

for (const path of ROUTES()) {
  test(`${path} renders with one h1 and no axe violations`, async ({ page }) => {
    const res = await page.goto(path);
    expect(res?.status()).toBe(200);
    await expect(page.locator("h1")).toHaveCount(1);
    await expect(page.locator("main#main")).toBeVisible();
    await expectNoAxeViolations(page);
  });
}

test("the skip link is the first tab stop and moves focus to main", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const skip = page.getByRole("link", { name: "Skip to content" });
  await expect(skip).toBeFocused();
  await expect(skip).toBeVisible();
  await page.keyboard.press("Enter");
  await expect(page.locator("main#main")).toBeFocused();
});

test("focus shows a solid ring", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  const outline = await page.evaluate(() => getComputedStyle(document.activeElement as Element).outlineStyle);
  expect(outline).toBe("solid");
});

test.describe("not found", () => {
  test.skip(true, "enabled in Task 15 when the 404 page lands");
  test("unknown paths return 404", async ({ page }) => {
    const res = await page.goto(NOT_FOUND_PATH);
    expect(res?.status()).toBe(404);
  });
});
```

```ts
// site/tests/e2e/theme.spec.ts
import { expect, test } from "@playwright/test";

test("the toggle switches theme and remembers it", async ({ page }) => {
  await page.goto("/");
  const toggle = page.locator("[data-theme-toggle]");
  await expect(toggle).toBeVisible();
  await toggle.click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  expect(bg).toBe("rgb(31, 30, 28)"); // #1F1E1C warm charcoal
});

test("blocked storage does not break the page or the toggle", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(() => {
    Object.defineProperty(window, "localStorage", { get() { throw new Error("SecurityError"); } });
  });
  await page.goto("/");
  await page.locator("[data-theme-toggle]").click();
  await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");
  expect(errors).toEqual([]);
});
```

```ts
// site/tests/e2e/layout.spec.ts
// Phone width (390 px): nothing scrolls sideways on any route.
import { expect, test } from "@playwright/test";
import { ROUTES } from "./routes";

for (const path of ROUTES()) {
  test(`${path} has no horizontal scroll on a phone`, async ({ page }) => {
    await page.goto(path);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
  });
}
```

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark tests/e2e/pages.spec.ts tests/e2e/theme.spec.ts`
Expected: FAIL (no skip link, no toggle, M0's starter page).

- [ ] **Step 6: Write the styles**

```css
/* site/src/styles/site.css: site-wide layout on top of tokens.css (imported after global.css). */
*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0;
  background: var(--color-paper);
  color: var(--color-ink);
  font-family: var(--font-text);
  font-size: var(--text-body);
  line-height: var(--text-body-lh);
}
img, svg, video { max-width: 100%; height: auto; display: block; }
a { color: var(--color-accent); text-underline-offset: 0.2em; }
a:hover { text-decoration-thickness: 2px; }
:focus-visible { outline: 2px solid var(--color-accent); outline-offset: 3px; border-radius: 2px; }
main:focus { outline: none; }

.wrap { width: min(100% - 2 * var(--gutter), var(--page-max)); margin-inline: auto; }
.stack > * + * { margin-block-start: var(--space-5); }
.section { padding-block: var(--space-9); }
.eyebrow { color: var(--color-accent); display: block; margin-block-end: var(--space-3); }

.skip-link {
  position: absolute; left: var(--space-4); top: -100px; z-index: 100;
  background: var(--color-surface); color: var(--color-ink);
  padding: var(--space-3) var(--space-4); border-radius: var(--radius-sm);
}
.skip-link:focus { top: var(--space-4); }

.sr-only {
  position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px;
  overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0;
}

.btn {
  display: inline-flex; align-items: center; gap: var(--space-2);
  min-height: 44px; padding: 0 var(--space-4);
  border: 1px solid var(--color-hairline); border-radius: var(--radius-pill);
  background: var(--color-surface); color: var(--color-ink);
  font: inherit; font-weight: 500; text-decoration: none; cursor: pointer;
}
.btn-primary { background: var(--color-accent); border-color: var(--color-accent); color: var(--color-paper); }

.tag {
  font-family: var(--font-mono); font-size: var(--text-data);
  padding: 2px var(--space-2); border-radius: var(--radius-sm);
  background: var(--color-accent-soft); color: var(--color-ink);
}

.empty { color: var(--color-muted); max-width: var(--measure); }

/* Motion: small, token-timed, and only when the visitor has not asked for less. */
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
  a, .btn { transition: color var(--motion-fast) var(--motion-ease), background-color var(--motion-fast) var(--motion-ease); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important; animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important; scroll-behavior: auto !important;
  }
}
```

- [ ] **Step 7: Write the shell components**

```ts
// site/src/lib/page.ts: prop types shared by the layout and its components
export type NavKey = "work" | "writing" | "about" | "contact";
export type CardSpecInput = { variant: "A" | "C" | "home"; label: string; title: string; subtitle?: string };
export type SeoProps = {
  title?: string;
  description: string;
  card: CardSpecInput | null;
  type?: "website" | "article";
  noindex?: boolean;
  jsonLd?: object[];
};
```

```astro
---
// site/src/components/Wordmark.astro: the dins wordmark SVG, light or dark by theme. Never live text.
import Light from "../../../brand/logo/wordmark-small-light.svg";
import Dark from "../../../brand/logo/wordmark-small-dark.svg";
---
<span class="wordmark">
  <Light class="light" aria-hidden="true" height="28" width="80" />
  <Dark class="dark" aria-hidden="true" height="28" width="80" />
</span>
<style>
  .wordmark { display: inline-flex; }
  .wordmark :global(svg) { height: 28px; width: auto; }
  .dark { display: none; }
  @media (prefers-color-scheme: dark) {
    :global(:root:not([data-theme="light"])) .light { display: none; }
    :global(:root:not([data-theme="light"])) .dark { display: block; }
  }
  :global(:root[data-theme="dark"]) .light { display: none; }
  :global(:root[data-theme="dark"]) .dark { display: block; }
</style>
```

```astro
---
// site/src/components/ThemeToggle.astro: hidden until its script runs, so no dead button without JavaScript.
---
<button type="button" class="btn icon-btn" data-theme-toggle hidden aria-label="Switch theme">
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
    <circle cx="12" cy="12" r="4.5" />
    <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
  </svg>
</button>
<script>
  import { initThemeToggle } from "../lib/theme";
  initThemeToggle(document.querySelector<HTMLButtonElement>("[data-theme-toggle]"));
</script>
<style>
  .icon-btn { width: 44px; padding: 0; justify-content: center; }
  .icon-btn[hidden] { display: none; }
</style>
```

```astro
---
// site/src/components/Nav.astro
import Wordmark from "./Wordmark.astro";
import ThemeToggle from "./ThemeToggle.astro";
import { site } from "../data/site";
import type { NavKey } from "../lib/page";
interface Props { current?: NavKey }
const { current } = Astro.props;
const items: { key: NavKey; href: string; label: string }[] = [
  { key: "work", href: "/work/", label: "Work" },
  { key: "writing", href: "/writing/", label: "Writing" },
  { key: "about", href: "/about/", label: "About" },
  { key: "contact", href: "/contact/", label: "Contact" },
];
---
<header class="site-header">
  <div class="wrap bar">
    <a class="mark" href="/" aria-label="dins, home"><Wordmark /></a>
    <nav aria-label="Main">
      <ul>
        {items.map((i) => (
          <li><a href={i.href} aria-current={current === i.key ? "page" : undefined}>{i.label}</a></li>
        ))}
      </ul>
    </nav>
    <div class="right">
      {site.links.resume && <a class="btn" href={site.links.resume}>Resume</a>}
      <ThemeToggle />
    </div>
  </div>
</header>
<style>
  .site-header { border-block-end: 1px solid var(--color-hairline); }
  .bar { display: flex; align-items: center; gap: var(--space-5); min-height: 64px; flex-wrap: wrap; }
  .mark { display: inline-flex; }
  nav ul { display: flex; gap: var(--space-4); list-style: none; margin: 0; padding: 0; flex-wrap: wrap; }
  nav a { color: var(--color-ink); text-decoration: none; font-weight: 500; padding-block: var(--space-2); }
  nav a[aria-current="page"] { color: var(--color-accent); text-decoration: underline; }
  .right { margin-inline-start: auto; display: flex; gap: var(--space-2); }
</style>
```

```astro
---
// site/src/components/Footer.astro
import { site } from "../data/site";
const year = new Date().getUTCFullYear();
---
<footer class="site-footer">
  <div class="wrap row">
    <p class="tagline">Look closer<span aria-hidden="true">.</span></p>
    <ul class="links">
      <li><a href={`mailto:${site.email}`}>Email</a></li>
      {site.links.github && <li><a href={site.links.github}>GitHub</a></li>}
      {site.links.linkedin && <li><a href={site.links.linkedin}>LinkedIn</a></li>}
      <li><a href="/rss.xml">RSS</a></li>
      <li><a href="/privacy/">Privacy</a></li>
    </ul>
    <p class="t-small">© {year} dins. Made by Din, with Ottie.</p>
  </div>
</footer>
<style>
  .site-footer { border-block-start: 1px solid var(--color-hairline); padding-block: var(--space-7); margin-block-start: var(--space-9); }
  .row { display: flex; flex-wrap: wrap; gap: var(--space-4) var(--space-6); align-items: baseline; }
  .tagline { font-family: var(--font-display); font-size: var(--text-h4); margin: 0; }
  .tagline span { color: var(--color-accent); }
  .links { display: flex; gap: var(--space-4); list-style: none; padding: 0; margin: 0; flex-wrap: wrap; }
</style>
```

```astro
---
// site/src/components/Draft.astro: marks draft content so it is visible in review and
// detectable by the drafts guard (data-draft must never appear in a production build).
import type { Status } from "../lib/drafts";
interface Props { status: Status; as?: "div" | "span" | "li" | "article"; class?: string }
const { status, as: Tag = "div", class: className } = Astro.props;
const draft = status === "draft";
---
<Tag class:list={[className, { "is-draft": draft }]} data-draft={draft ? "" : undefined}>
  {draft && <span class="draft-badge t-label">Draft, hidden on dins.dev</span>}
  <slot />
</Tag>
<style>
  .is-draft { outline: 1px dashed var(--color-line); outline-offset: 4px; }
  .draft-badge { display: inline-block; color: var(--color-muted); margin-block-end: var(--space-2); }
</style>
```

```astro
---
// site/src/components/Prose.astro: reading styles for MDX bodies.
---
<div class="prose"><slot /></div>
<style>
  .prose { max-width: var(--measure); }
  .prose :global(h2) { font: var(--text-h2-weight) var(--text-h2) / var(--text-h2-lh) var(--font-display); letter-spacing: var(--text-h2-tracking); font-variation-settings: "SOFT" 50, "WONK" 0; margin-block: var(--space-7) var(--space-4); }
  .prose :global(h3) { font: var(--text-h3-weight) var(--text-h3) / var(--text-h3-lh) var(--font-display); font-variation-settings: "SOFT" 50, "WONK" 0; margin-block: var(--space-6) var(--space-3); }
  .prose :global(p), .prose :global(li) { font-size: var(--text-body); line-height: var(--text-body-lh); }
  .prose :global(code) { font-family: var(--font-mono); font-size: var(--text-data); }
  .prose :global(pre) { overflow-x: auto; padding: var(--space-4); border-radius: var(--radius-md); background: var(--color-surface); border: 1px solid var(--color-hairline); }
</style>
```

```astro
---
// site/src/components/Seo.astro
import { BUILD_FLAGS } from "../lib/build";
import { SITE_URL, canonicalUrl, cardPath, jsonLdScript, pageTitle } from "../lib/seo";
import type { SeoProps } from "../lib/page";
const { title, description, card, type = "website", noindex = false, jsonLd = [] } = Astro.props as SeoProps;
const path = Astro.url.pathname;
const canonical = canonicalUrl(path);
const image = new URL(card ? cardPath(path) : "/og/index.png", SITE_URL).href;
const fullTitle = pageTitle(title);
---
<title>{fullTitle}</title>
<meta name="description" content={description} />
<link rel="canonical" href={canonical} />
{(noindex || BUILD_FLAGS.noindex) && <meta name="robots" content="noindex" />}
<meta property="og:site_name" content="dins" />
<meta property="og:type" content={type} />
<meta property="og:title" content={title ?? "Hi, I’m Din."} />
<meta property="og:description" content={description} />
<meta property="og:url" content={canonical} />
<meta property="og:image" content={image} />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content={card ? card.title : "dins.dev"} />
<meta name="twitter:card" content="summary_large_image" />
{card && <meta name="dins:card" content={JSON.stringify({ ...card, path })} />}
{jsonLd.map((d) => <script type="application/ld+json" set:html={jsonLdScript(d)} />)}
```

Replace the body of `site/src/layouts/BaseLayout.astro`, keeping M0's token and font imports and preload links in the head:

```astro
---
// site/src/layouts/BaseLayout.astro (M0 creates it; M1 replaces it with this, keeping M0's imports and preloads)
import "../styles/global.css"; // M0: tokens and fonts
import "../styles/site.css";
import Seo from "../components/Seo.astro";
import Nav from "../components/Nav.astro";
import type { NavKey, SeoProps } from "../lib/page";
import Footer from "../components/Footer.astro";
import { DEPLOY } from "../lib/deploy-env"; // M0
type Props = SeoProps & { current?: NavKey };
const { current, ...seo } = Astro.props;
---
<!doctype html>
<html lang="en" class="no-js">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="color-scheme" content="light dark" />
    <meta name="dins-deploy" content={DEPLOY} /><!-- M0 -->
    <script is:inline>
      document.documentElement.classList.replace("no-js", "js");
      try {
        var t = localStorage.getItem("dins-theme");
        if (t === "light" || t === "dark") document.documentElement.dataset.theme = t;
      } catch (e) {}
    </script>
    <!-- M0's Fraunces and Instrument Sans preloads stay here -->
    <Seo {...seo} />
    <link rel="icon" href="/favicon.ico" sizes="48x48" />
    <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="alternate" type="application/rss+xml" title="dins.dev writing" href="/rss.xml" />
    <slot name="head" /><!-- M4's MotionHead.astro -->
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <Nav current={current} />
    <main id="main" tabindex="-1"><slot /></main>
    <Footer />
  </body>
</html>
```

Replace `site/src/pages/index.astro` with a temporary shell (Task 9 replaces it):

```astro
---
import BaseLayout from "../layouts/BaseLayout.astro";
---
<BaseLayout description="Din’s portfolio." card={null}>
  <div class="wrap section"><h1 class="t-display">Hi, I’m Din.</h1></div>
</BaseLayout>
```

- [ ] **Step 8: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/pages.spec.ts tests/e2e/theme.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS (the 404 test is skipped).

Copy the full icon set (M0 links only `favicon.svg`): `cp brand/logo/icons/* brand/logo/favicon.svg site/public/`.

Run: `pnpm --dir site check && pnpm --dir site build && (pnpm --dir site serve &) && sleep 5 && curl -sI http://127.0.0.1:8787/favicon.ico | head -1 && curl -sI http://127.0.0.1:8787/site.webmanifest | head -1`
Expected: `check` PASS; two `HTTP/1.1 200 OK` lines. Stop the server afterwards.

- [ ] **Step 9: Commit**

```bash
git add site/src/styles/site.css site/src/lib/theme.ts site/src/lib/page.ts site/src/components site/src/layouts/BaseLayout.astro site/src/pages/index.astro site/playwright.config.ts site/public site/tests site/package.json pnpm-lock.yaml
git commit -m "feat(site): page shell with skip link, nav, footer, theme toggle and e2e harness"
```

## Task 9: Home page in its plain form

**Files:**
- Create: `site/src/components/{QuickLinks,SuggestedAnswers,AskSlot,OttieSlot,ProjectWindow,ProjectCard,PostCard,Motif,ContactForm}.astro`, `site/tests/e2e/home.spec.ts`
- Modify: `site/src/pages/index.astro`, `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `getVisibleProjects`, `getVisiblePosts`, `getVisibleSuggested` (Task 4), `featuredProjects`, `latestPosts`, `readingMinutes` (Task 4), `profile`, `site`, `visibleValue` (Task 5), `personJsonLd`, `websiteJsonLd` (Task 6), `CONTACT_*`, `REASONS` (Task 7), `BaseLayout`, `Draft` (Task 8), `KIND_LABELS`, `WRITING_KIND_LABELS` (Task 2), `formatDate`, `isoDate` (Task 6).
- Produces: the components listed in "Interfaces other milestones build on"; `ProjectCard` props `{ project: CollectionEntry<"projects">; headingLevel?: 2 | 3 }`; `PostCard` props `{ post: CollectionEntry<"writing">; headingLevel?: 2 | 3 }`; `ProjectWindow` props `{ project: CollectionEntry<"projects">; eager?: boolean }`; `Motif` props `{ name: Motif }`; `ContactForm` props `{ headingId?: string }`.

The plain home page follows the sketch's order (lens hero, windows, paper, studio, letter, footer) as calm, static sections. M4 enhances each section in place.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/e2e/home.spec.ts
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN } from "./routes";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
});

test("the hero has Din's name and the quick links on first paint", async ({ page }) => {
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Hi, I’m Din.");
  const quick = page.getByRole("navigation", { name: "Quick links" });
  await expect(quick.getByRole("link", { name: "Email" })).toHaveAttribute("href", "mailto:din@dins.dev");
  await expect(quick.getByRole("link", { name: "GitHub" })).toBeVisible();
  const box = await quick.boundingBox();
  expect(box && box.y + box.height).toBeLessThan(page.viewportSize()!.height);
});

test("suggested questions open to their static answer and sources", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "no published suggested answers yet");
  const first = page.locator("#suggested details").first();
  await first.locator("summary").click();
  await expect(first.locator(".answer")).toBeVisible();
  await expect(first.getByRole("link").first()).toHaveAttribute("href", /^\//);
});

test("the sections M4 enhances are present in order", async ({ page }) => {
  const order = await page.locator("[data-setpiece]").evaluateAll((els) => els.map((e) => e.getAttribute("data-setpiece")));
  expect(order).toEqual(["lens", "windows", "paper", "studio", "letter"]);
});

test("featured work and latest writing link to their pages", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "no published content yet");
  await expect(page.locator("#work").getByRole("link", { name: /passfx/ })).toHaveAttribute("href", "/work/passfx/");
  await expect(page.locator("#writing article")).toHaveCount(3);
});

test("drafts show a visible badge", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "production has no drafts");
  await expect(page.locator("[data-draft]").first()).toBeVisible();
});

test("the Ask and Ottie slots are in place", async ({ page }) => {
  await expect(page.locator('.ask-slot[data-ask-scope="site"]')).toHaveCount(1);
  await expect(page.locator('.ottie-slot[data-ottie-placement="hero"]')).toHaveAttribute("aria-hidden", "true");
});

test("the home page carries Person and WebSite structured data", async ({ page }) => {
  const types = await page.locator('script[type="application/ld+json"]').evaluateAll((els) => els.map((e) => JSON.parse(e.textContent!)["@type"]));
  expect(types).toEqual(expect.arrayContaining(["Person", "WebSite"]));
});
```

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/home.spec.ts`
Expected: FAIL (the shell has none of this).

- [ ] **Step 2: Write the small components**

```astro
---
// site/src/components/QuickLinks.astro: Resume, Email, GitHub, LinkedIn (PRD 2: visible on first paint).
import { site } from "../data/site";
const links = [
  site.links.resume && { label: "Resume", href: site.links.resume },
  { label: "Email", href: `mailto:${site.email}` },
  site.links.github && { label: "GitHub", href: site.links.github },
  site.links.linkedin && { label: "LinkedIn", href: site.links.linkedin },
].filter(Boolean) as { label: string; href: string }[];
---
<nav class="quick" aria-label="Quick links">
  <ul>{links.map((l) => <li><a class="btn" href={l.href}>{l.label}</a></li>)}</ul>
</nav>
<style>
  .quick ul { display: flex; flex-wrap: wrap; gap: var(--space-2); list-style: none; padding: 0; margin: 0; }
</style>
```

```astro
---
// site/src/components/AskSlot.astro: where M3 mounts Ask Ottie. Without JavaScript only the slot content shows.
interface Props { scope: "site" | "project"; project?: string }
const { scope, project } = Astro.props;
---
<div class="ask-slot" id={scope === "site" ? "ask" : "ask-project"} data-ask-scope={scope} data-ask-project={project}>
  <slot />
</div>
<style>
  :global(.js) .ask-slot[data-ask-scope="site"] { min-height: 3.5rem; } /* reserved so M3's island does not shift the page */
</style>
```

```astro
---
// site/src/components/OttieSlot.astro: a placeholder, decorative spot for Ottie. M2's Task 16 replaces every use with
// <Ottie context=…> (hero becomes home) and deletes this file.
import { Image } from "astro:assets";
import still from "../../../brand/reference/ottie-3d-neutral.webp";
interface Props { placement: "hero" | "project" | "contact" | "404" | "devlog"; state?: "idle" | "shrug" }
const { placement, state = "idle" } = Astro.props;
---
<div class="ottie-slot" data-ottie-placement={placement} data-ottie-state={state} aria-hidden="true">
  <Image src={still} alt="" width={180} height={220} loading={placement === "hero" ? "eager" : "lazy"} />
</div>
<style>
  .ottie-slot { width: 180px; aspect-ratio: 180 / 220; flex: none; }
  .ottie-slot :global(img) { width: 100%; height: 100%; object-fit: contain; }
  @media (max-width: 640px) { .ottie-slot { width: 120px; } }
</style>
```

```astro
---
// site/src/components/SuggestedAnswers.astro: static, reviewed answers that work without JavaScript (PRD 3 and 6).
import type { CollectionEntry } from "astro:content";
import Draft from "./Draft.astro";
interface Props { items: CollectionEntry<"suggested">[] }
const { items } = Astro.props;
---
{items.length > 0 && (
  <section id="suggested" class="suggested" aria-labelledby="suggested-h">
    <h2 id="suggested-h" class="t-label eyebrow">Questions people ask</h2>
    <div class="list">
      {items.map((s) => (
        <Draft status={s.data.status}>
          <details data-suggested-id={s.id} lang={s.data.language}>
            <summary>{s.data.question}</summary>
            <div class="answer">
              <p>{s.data.answer}</p>
              <ul class="sources" aria-label="Sources">
                {s.data.sources.map((src) => <li><a href={src.href}>{src.label}</a></li>)}
              </ul>
            </div>
          </details>
        </Draft>
      ))}
    </div>
  </section>
)}
<style>
  .list { display: grid; gap: var(--space-2); }
  details { background: var(--color-surface); border: 1px solid var(--color-hairline); border-radius: var(--radius-md); }
  summary { cursor: pointer; padding: var(--space-3) var(--space-4); font-weight: 500; min-height: 44px; }
  .answer { padding: 0 var(--space-4) var(--space-4); }
  .answer p { margin-block: 0 var(--space-3); max-width: var(--measure); }
  .sources { display: flex; flex-wrap: wrap; gap: var(--space-2); list-style: none; padding: 0; margin: 0; font-size: var(--text-small); }
</style>
```

```astro
---
// site/src/components/ProjectWindow.astro: a 16:10 window holding the stage capture (and a video demo when there is one).
import type { CollectionEntry } from "astro:content";
import { Image } from "astro:assets";
interface Props { project: CollectionEntry<"projects">; eager?: boolean }
const { project, eager = false } = Astro.props;
const { capture, captureAlt, demo } = project.data;
const isSvg = capture.format === "svg";
---
<figure class="window" data-demo-type={demo?.type}>
  <div class="chrome" aria-hidden="true"><i></i><i></i><i></i><span class="addr t-data">dins.dev/work/{project.id}</span></div>
  <div class="screen">
    {demo?.type === "video" ? (
      <video src={demo.src} poster={capture.src} controls muted playsinline preload="none" aria-label={captureAlt}></video>
    ) : isSvg ? (
      <Image src={capture} alt={captureAlt} loading={eager ? "eager" : "lazy"} />
    ) : (
      <Image src={capture} alt={captureAlt} widths={[640, 960, 1280]} sizes="(min-width: 1000px) 720px, 100vw" loading={eager ? "eager" : "lazy"} />
    )}
  </div>
</figure>
<style>
  .window { margin: 0; border-radius: var(--radius-lg); overflow: hidden; background: var(--color-surface); border: 1px solid var(--color-hairline); }
  .chrome { display: flex; align-items: center; gap: 6px; padding: var(--space-2) var(--space-3); border-block-end: 1px solid var(--color-hairline); }
  .chrome i { width: 10px; height: 10px; border-radius: 50%; background: var(--color-hairline); }
  .addr { margin-inline-start: var(--space-3); color: var(--color-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .screen { aspect-ratio: 16 / 10; }
  .screen :global(img), .screen video { width: 100%; height: 100%; object-fit: cover; }
</style>
```

```astro
---
// site/src/components/ProjectCard.astro
import type { CollectionEntry } from "astro:content";
import Draft from "./Draft.astro";
import ProjectWindow from "./ProjectWindow.astro";
import { KIND_LABELS } from "../lib/kinds";
interface Props { project: CollectionEntry<"projects">; headingLevel?: 2 | 3 }
const { project, headingLevel = 3 } = Astro.props;
const H = `h${headingLevel}` as "h2" | "h3";
const href = `/work/${project.id}/`;
---
<Draft status={project.data.status} as="article" class="project-card">
  <ProjectWindow project={project} />
  <div class="text">
    <span class="t-label eyebrow">{KIND_LABELS[project.data.kind]}</span>
    <H class="t-h3"><a href={href}>{project.data.title}</a></H>
    <p class="t-body">{project.data.summary}</p>
    <ul class="tags" aria-label="Stack">{project.data.stack.map((s) => <li class="tag">{s}</li>)}</ul>
  </div>
</Draft>
<style>
  .text { padding-block-start: var(--space-4); }
  .text :global(h2), .text :global(h3) { margin: 0 0 var(--space-2); }
  .text :global(h2 a), .text :global(h3 a) { color: var(--color-ink); text-decoration: none; }
  .text :global(h2 a:hover), .text :global(h3 a:hover) { color: var(--color-accent); }
  .tags { display: flex; gap: var(--space-2); flex-wrap: wrap; list-style: none; padding: 0; margin: var(--space-3) 0 0; }
</style>
```

`Motif.astro` draws the three decorative motifs from the sketch (`docs/design/sketches/home.template.html`, the `.motif` SVGs), using the same paths:

```astro
---
// site/src/components/Motif.astro: decorative post motifs (from the home sketch). Hidden from screen readers.
import type { Motif } from "../lib/schemas";
interface Props { name: Motif }
const { name } = Astro.props;
const xs = [20, 40, 60, 80, 100, 120, 140, 160, 180];
---
<svg class="motif" viewBox="0 0 200 90" fill="none" aria-hidden="true" focusable="false">
  {name === "nodes" && (
    <Fragment>
      <g stroke="var(--color-line)" stroke-opacity=".35">
        {[18, 45, 72].map((y) => xs.map((x) => <circle cx={x} cy={y} r="3" />))}
      </g>
      <g stroke="var(--color-accent)" stroke-width="1.4"><path d="M100 45 L60 18 M100 45 L140 72 M100 45 L160 18" /></g>
      <g fill="var(--color-accent)"><circle cx="60" cy="18" r="4" /><circle cx="140" cy="72" r="4" /><circle cx="160" cy="18" r="4" /><circle cx="100" cy="45" r="6" /></g>
    </Fragment>
  )}
  {name === "bars" && (
    <Fragment>
      <g stroke="var(--color-line)" stroke-opacity=".3"><path d="M44 17h140M44 39h140M44 61h140M44 83h140" /></g>
      <g fill="var(--color-accent)"><rect x="44" y="12" width="128" height="9" rx="2" /><rect x="44" y="34" width="112" height="9" rx="2" /><rect x="44" y="78" width="136" height="9" rx="2" /></g>
      <rect x="44" y="56" width="70" height="9" rx="2" fill="var(--color-amber)" />
    </Fragment>
  )}
  {name === "lens" && (
    <Fragment>
      <g stroke="var(--color-ink)" stroke-width="5" stroke-linecap="round"><circle cx="78" cy="48" r="22" /><circle cx="130" cy="48" r="22" /><path d="M100 44q4-5 8 0M56 39l-12-3M152 39l12-3" /></g>
      <circle cx="138" cy="40" r="4" fill="var(--color-accent)" />
    </Fragment>
  )}
</svg>
<style>
  .motif { width: 100%; height: auto; max-height: 90px; }
</style>
```

```astro
---
// site/src/components/PostCard.astro
import type { CollectionEntry } from "astro:content";
import Draft from "./Draft.astro";
import Motif from "./Motif.astro";
import { WRITING_KIND_LABELS } from "../lib/kinds";
import { readingMinutes } from "../lib/content";
import { formatDate, isoDate } from "../lib/dates";
interface Props { post: CollectionEntry<"writing">; headingLevel?: 2 | 3 }
const { post, headingLevel = 3 } = Astro.props;
const H = `h${headingLevel}` as "h2" | "h3";
---
<Draft status={post.data.status} as="article" class="post-card">
  <Motif name={post.data.motif} />
  <p class="meta">
    <span class="t-label">{WRITING_KIND_LABELS[post.data.kind]}</span>
    <time class="t-data" datetime={isoDate(post.data.date)}>{formatDate(post.data.date)}</time>
    <span class="t-data">{readingMinutes(post.body ?? "")} min read</span>
  </p>
  <H class="t-h3"><a href={`/writing/${post.id}/`}>{post.data.title}</a></H>
  <p class="t-small">{post.data.summary}</p>
</Draft>
<style>
  :global(.post-card) { background: var(--color-surface); border: 1px solid var(--color-hairline); border-radius: var(--radius-md); padding: var(--space-5); }
  .meta { display: flex; gap: var(--space-3); flex-wrap: wrap; align-items: baseline; margin: var(--space-3) 0; color: var(--color-muted); }
  :global(.post-card) :global(h2), :global(.post-card) :global(h3) { margin: 0 0 var(--space-2); }
  :global(.post-card) :global(h2 a), :global(.post-card) :global(h3 a) { color: var(--color-ink); text-decoration: none; }
</style>
```

```astro
---
// site/src/components/ContactForm.astro: the letter as a plain form. M4 turns it into the folding letter and adds
// Turnstile in [data-turnstile-slot]. Without JavaScript there is no Turnstile token, so the <noscript> note points to email.
import { CONTACT_FIELDS as F, CONTACT_LIMITS as L, REASONS } from "../lib/contact";
import { site } from "../data/site";
---
<form class="letter-form" method="post" action="/api/contact" data-letter-form>
  <p class="salute" id="salute">Dear Din,</p>
  <div class="field">
    <label for="c-message">Message</label>
    <textarea id="c-message" name={F.message} rows="7" required maxlength={L.message} aria-describedby="salute"></textarea>
  </div>
  <fieldset class="field reasons">
    <legend>Why are you writing?</legend>
    {REASONS.map((r, i) => (
      <label class="chip"><input type="radio" name={F.reason} value={r.value} checked={i === 0} /> {r.label}</label>
    ))}
  </fieldset>
  <fieldset class="field from">
    <legend>From</legend>
    <label for="c-name">Your name</label>
    <input id="c-name" name={F.name} type="text" required maxlength={L.name} autocomplete="name" />
    <label for="c-email">Your email</label>
    <input id="c-email" name={F.email} type="email" required maxlength={L.email} autocomplete="email" />
  </fieldset>
  <!-- Honeypot: catches scripted posts that do run JavaScript. Posts without JavaScript are refused anyway (no Turnstile token). -->
  <div class="hp" aria-hidden="true">
    <label for="c-website">Leave this field empty</label>
    <input id="c-website" name={F.honeypot} type="text" tabindex="-1" autocomplete="off" />
  </div>
  <div data-turnstile-slot></div>
  <noscript>
    <p class="noscript t-small">This form needs JavaScript to check that a person is writing. Without it, please email <a href={`mailto:${site.email}`}>{site.email}</a>.</p>
  </noscript>
  <div class="foot">
    <button class="btn btn-primary" type="submit">Seal and send</button>
    <p class="t-small">Or email <a href={`mailto:${site.email}`}>{site.email}</a>.</p>
  </div>
</form>
<style>
  .letter-form { display: grid; gap: var(--space-5); max-width: 40rem; background: var(--color-surface); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); padding: var(--space-6); }
  .salute { font-family: var(--font-display); font-size: var(--text-h3); margin: 0; font-variation-settings: "SOFT" 50, "WONK" 0; }
  .field { display: grid; gap: var(--space-2); border: 0; padding: 0; margin: 0; }
  legend { font-weight: 600; margin-block-end: var(--space-2); padding: 0; }
  label { font-weight: 500; }
  textarea, input[type="text"], input[type="email"] {
    font: inherit; color: var(--color-ink); background: var(--color-paper);
    border: 1px solid var(--color-line); border-radius: var(--radius-sm); padding: var(--space-3); min-height: 44px; width: 100%;
  }
  .reasons { display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .reasons legend { width: 100%; }
  .chip { display: inline-flex; align-items: center; gap: var(--space-2); min-height: 44px; padding: 0 var(--space-3); border: 1px solid var(--color-hairline); border-radius: var(--radius-pill); }
  .hp { position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden; }
  .noscript { margin: 0; padding: var(--space-3) var(--space-4); border-radius: var(--radius-sm); background: var(--color-accent-soft); color: var(--color-ink); }
  .foot { display: flex; flex-wrap: wrap; gap: var(--space-4); align-items: center; }
  .foot p { margin: 0; }
</style>
```

- [ ] **Step 3: Write the home page**

```astro
---
// site/src/pages/index.astro: the calm home page. M4 layers the set pieces onto the data-setpiece sections.
import BaseLayout from "../layouts/BaseLayout.astro";
import AskSlot from "../components/AskSlot.astro";
import ContactForm from "../components/ContactForm.astro";
import Draft from "../components/Draft.astro";
import OttieSlot from "../components/OttieSlot.astro";
import PostCard from "../components/PostCard.astro";
import ProjectCard from "../components/ProjectCard.astro";
import QuickLinks from "../components/QuickLinks.astro";
import SuggestedAnswers from "../components/SuggestedAnswers.astro";
import { getVisiblePosts, getVisibleProjects, getVisibleSuggested } from "../lib/collections";
import { featuredProjects, latestPosts } from "../lib/content";
import { SHOW_DRAFTS } from "../lib/build";
import { visibleValue } from "../lib/schemas";
import { personJsonLd, websiteJsonLd } from "../lib/seo";
import { profile } from "../data/profile";
import { site } from "../data/site";

const role = visibleValue(profile.roleLine, SHOW_DRAFTS);
const teaser = visibleValue(profile.aboutTeaser, SHOW_DRAFTS);
const featured = featuredProjects(await getVisibleProjects());
const posts = latestPosts(await getVisiblePosts());
const suggested = await getVisibleSuggested();
const publishedRole = profile.roleLine.status === "published" ? profile.roleLine.value : null;
---
<BaseLayout
  description={publishedRole ?? "Din’s portfolio: projects, writing, and Ottie, who answers questions about Din’s work."}
  card={{ variant: "home", label: "Portfolio", title: "Hi, I’m Din.", subtitle: publishedRole ?? undefined }}
  jsonLd={[personJsonLd(site, publishedRole), websiteJsonLd(site)]}
>
  <header class="hero wrap" id="top" data-setpiece="lens">
    <div class="hero-text stack">
      <h1 class="t-display">Hi, I’m Din.</h1>
      {role && <Draft status={role.status} as="div"><p class="t-lead role">{role.value}</p></Draft>}
      <AskSlot scope="site" />
      <QuickLinks />
      <SuggestedAnswers items={suggested} />
    </div>
    <OttieSlot placement="hero" />
  </header>

  <section class="section wrap" id="work" data-setpiece="windows" aria-labelledby="work-h">
    <span class="t-label eyebrow">Work</span>
    <h2 id="work-h" class="t-h1">Selected work</h2>
    {featured.length ? (
      <ol class="grid">{featured.map((p) => <li><ProjectCard project={p} /></li>)}</ol>
    ) : (
      <p class="empty" data-empty>Projects are on their way.</p>
    )}
    <p><a href="/work/">All work</a></p>
  </section>

  <section class="section wrap" id="writing" data-setpiece="paper" aria-labelledby="writing-h">
    <span class="t-label eyebrow">Writing</span>
    <h2 id="writing-h" class="t-h1">Behind the work</h2>
    {posts.length ? (
      <div class="grid">{posts.map((p) => <PostCard post={p} />)}</div>
    ) : (
      <p class="empty" data-empty>The first posts are on their way.</p>
    )}
    <p><a href="/writing/">All writing</a></p>
  </section>

  <section class="section wrap" id="about" data-setpiece="studio" aria-labelledby="about-h">
    <span class="t-label eyebrow">About</span>
    <h2 id="about-h" class="t-h1">Look closer.</h2>
    {teaser && <Draft status={teaser.status}><p class="t-lead">{teaser.value}</p></Draft>}
    <p><a class="btn" href="/about/">Read the full story</a></p>
  </section>

  <section class="section wrap" id="contact" data-setpiece="letter" aria-labelledby="contact-h">
    <span class="t-label eyebrow">Contact</span>
    <h2 id="contact-h" class="t-h1">Write to me.</h2>
    <p class="t-lead">Roles, admissions questions, or just a hello. It lands in my inbox.</p>
    <ContactForm />
  </section>
</BaseLayout>
<style>
  .hero { display: flex; gap: var(--space-7); align-items: flex-end; padding-block: var(--space-8) var(--space-7); flex-wrap: wrap; }
  .hero-text { flex: 1 1 32rem; min-width: 0; }
  .role { margin: 0; }
  .grid { display: grid; gap: var(--space-6); grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); list-style: none; padding: 0; margin: var(--space-6) 0; }
</style>
```

The home route `/` is already in `STATIC_ROUTES`, so `routes.ts` does not change in this task. Quick links sit above the suggested answers so they stay on first paint however many questions Din adds.

- [ ] **Step 4: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/home.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS. The featured project links point to `/work/<id>/`, which 404 until Task 11; only the home route is visited here.

- [ ] **Step 5: Din checks the home page in the preview**

Run: `DINS_SHOW_DRAFTS=1 pnpm --dir site build && pnpm --dir site serve`, open http://127.0.0.1:8787/ in light and dark and at phone width. Din judges the calm layout against the sketch (not final design). Record Din's notes in the PR description.

- [ ] **Step 6: Commit**

```bash
git add site/src/components site/src/pages/index.astro site/tests/e2e/home.spec.ts
git commit -m "feat(site): calm home page with hero, suggested answers and section hooks"
```

## Task 10: /work with filters

**Files:**
- Create: `site/src/components/{WorkGrid,WorkFilters}.astro`, `site/src/pages/work/index.astro`, `site/src/pages/work/kind/[kind].astro`, `site/tests/e2e/work.spec.ts`
- Modify: `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `getVisibleProjects`, `kindsWithProjects` (Task 4), `KIND_LABELS` (Task 2), `ProjectCard` (Task 9), `BaseLayout` (Task 8).
- Produces: routes `/work/` and `/work/kind/<kind>/` (only kinds with at least one visible project); `WorkGrid` props `{ projects: CollectionEntry<"projects">[] }`; `WorkFilters` props `{ kinds: ProjectKind[]; current: ProjectKind | "all" }`.

Filters are links to static pages, so they work without JavaScript, are crawlable, and announce themselves with `aria-current`. This is a plan decision (see Open questions).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/e2e/work.spec.ts
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN, PROJECTS } from "./routes";

test("the work page lists every visible project", async ({ page }) => {
  await page.goto("/work/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Work");
  await expect(page.locator("article.project-card")).toHaveCount(PROJECTS.length);
});

test("filters are links with the current one marked", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs projects");
  await page.goto("/work/");
  const filters = page.getByRole("navigation", { name: "Filter projects" });
  await expect(filters.getByRole("link", { name: "All" })).toHaveAttribute("aria-current", "page");
  await filters.getByRole("link", { name: "ML" }).click();
  await expect(page).toHaveURL(/\/work\/kind\/ml\/$/);
  await expect(page.locator("article.project-card")).toHaveCount(PROJECTS.filter((p) => p.kind === "ml").length);
  await expect(page.getByRole("navigation", { name: "Filter projects" }).getByRole("link", { name: "ML" })).toHaveAttribute("aria-current", "page");
});

test("a kind without projects has no filter link and no page", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs projects");
  await page.goto("/work/");
  await expect(page.getByRole("link", { name: "Data science" })).toHaveCount(0);
  const res = await page.goto("/work/kind/data-science/");
  expect(res?.status()).toBe(404);
});
```

In `site/tests/e2e/routes.ts`, change `STATIC_ROUTES` to `["/", "/work/"]` and add the kind pages to `CONTENT_ROUTES`:

```ts
const KINDS = ["ml", "data-engineering", "data-science", "research"];
export const KIND_ROUTES = KINDS.filter((k) => PROJECTS.some((p) => p.kind === k)).map((k) => `/work/kind/${k}/`);
export const CONTENT_ROUTES: string[] = [...KIND_ROUTES];
```

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/work.spec.ts`
Expected: FAIL, `/work/` is 404.

- [ ] **Step 2: Write the components and pages**

```astro
---
// site/src/components/WorkFilters.astro
import type { ProjectKind } from "../lib/schemas";
import { KIND_LABELS } from "../lib/kinds";
interface Props { kinds: ProjectKind[]; current: ProjectKind | "all" }
const { kinds, current } = Astro.props;
---
{kinds.length > 1 && (
  <nav class="filters" aria-label="Filter projects">
    <ul>
      <li><a class="btn" href="/work/" aria-current={current === "all" ? "page" : undefined}>All</a></li>
      {kinds.map((k) => (
        <li><a class="btn" href={`/work/kind/${k}/`} aria-current={current === k ? "page" : undefined}>{KIND_LABELS[k]}</a></li>
      ))}
    </ul>
  </nav>
)}
<style>
  .filters ul { display: flex; flex-wrap: wrap; gap: var(--space-2); list-style: none; padding: 0; margin: var(--space-5) 0; }
  .filters a[aria-current="page"] { background: var(--color-accent); border-color: var(--color-accent); color: var(--color-paper); }
</style>
```

```astro
---
// site/src/components/WorkGrid.astro
import type { CollectionEntry } from "astro:content";
import ProjectCard from "./ProjectCard.astro";
interface Props { projects: CollectionEntry<"projects">[] }
const { projects } = Astro.props;
---
{projects.length ? (
  <ul class="grid">{projects.map((p) => <li><ProjectCard project={p} headingLevel={2} /></li>)}</ul>
) : (
  <p class="empty" data-empty>
    Projects are on their way. Meanwhile, <a href="/writing/">read the writing</a> or <a href="/contact/">write to Din</a>.
  </p>
)}
<style>
  .grid { display: grid; gap: var(--space-7) var(--space-6); grid-template-columns: repeat(auto-fit, minmax(min(100%, 22rem), 1fr)); list-style: none; padding: 0; margin: 0; }
</style>
```

```astro
---
// site/src/pages/work/index.astro
import BaseLayout from "../../layouts/BaseLayout.astro";
import WorkFilters from "../../components/WorkFilters.astro";
import WorkGrid from "../../components/WorkGrid.astro";
import { getVisibleProjects } from "../../lib/collections";
import { kindsWithProjects } from "../../lib/content";
const projects = await getVisibleProjects();
---
<BaseLayout title="Work" description="Every project Din has published: ML, data engineering, data science and research." card={{ variant: "A", label: "Work", title: "Work" }} current="work">
  <div class="wrap section">
    <h1 class="t-h1">Work</h1>
    <p class="t-lead">Projects in ML, data engineering, data science and research, each with what it does and how it went.</p>
    <WorkFilters kinds={kindsWithProjects(projects)} current="all" />
    <WorkGrid projects={projects} />
  </div>
</BaseLayout>
```

```astro
---
// site/src/pages/work/kind/[kind].astro
import BaseLayout from "../../../layouts/BaseLayout.astro";
import WorkFilters from "../../../components/WorkFilters.astro";
import WorkGrid from "../../../components/WorkGrid.astro";
import { getVisibleProjects } from "../../../lib/collections";
import { kindsWithProjects } from "../../../lib/content";
import { KIND_LABELS } from "../../../lib/kinds";
import type { ProjectKind } from "../../../lib/schemas";

export async function getStaticPaths() {
  const projects = await getVisibleProjects();
  return kindsWithProjects(projects).map((kind) => ({ params: { kind }, props: { projects } }));
}
const kind = Astro.params.kind as ProjectKind;
const { projects } = Astro.props;
const label = KIND_LABELS[kind];
---
<BaseLayout title={`${label} projects`} description={`Din’s ${label} projects, with what each one does and how it went.`} card={{ variant: "A", label: "Work", title: `${label} projects` }} current="work">
  <div class="wrap section">
    <h1 class="t-h1">{label} projects</h1>
    <WorkFilters kinds={kindsWithProjects(projects)} current={kind} />
    <WorkGrid projects={projects.filter((p) => p.data.kind === kind)} />
  </div>
</BaseLayout>
```

- [ ] **Step 3: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/work.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/WorkGrid.astro site/src/components/WorkFilters.astro site/src/pages/work site/tests/e2e
git commit -m "feat(site): work page with kind filters that work without JavaScript"
```

## Task 11: Case studies

**Files:**
- Create: `site/src/components/ProjectSummary.astro`, `site/src/pages/work/[id].astro`, `site/tests/e2e/case-study.spec.ts`
- Modify: `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `getVisibleProjects`, `getVisiblePosts`, `postsForProject` (Task 4), `ProjectWindow`, `AskSlot`, `OttieSlot`, `PostCard`, `Draft` (Tasks 8, 9), `Prose` (Task 8), `KIND_LABELS`.
- Produces: route `/work/<id>/`; `ProjectSummary` props `{ project: CollectionEntry<"projects"> }`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/e2e/case-study.spec.ts
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN } from "./routes";

test.skip(!DRAFTS_SHOWN, "needs a project");

test.beforeEach(async ({ page }) => {
  await page.goto("/work/passfx/");
});

test("opens with the window, then the summary block", async ({ page }) => {
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("passfx");
  const window = page.locator("figure.window");
  const summary = page.locator("dl.summary");
  await expect(window).toBeVisible();
  const [w, s] = [await window.boundingBox(), await summary.boundingBox()];
  expect(w!.y).toBeLessThan(s!.y);
  for (const term of ["Problem", "Role", "Stack", "Results"]) {
    await expect(summary.locator("dt", { hasText: term })).toHaveCount(1);
  }
});

test("the capture keeps a 16:10 screen", async ({ page }) => {
  const box = await page.locator("figure.window .screen").boundingBox();
  expect(Math.abs(box!.width / box!.height - 1.6)).toBeLessThan(0.02);
});

test("ends with the project Ask slot and Ottie", async ({ page }) => {
  await expect(page.locator('.ask-slot[data-ask-scope="project"][data-ask-project="passfx"]')).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "Ask Ottie about this project" })).toBeVisible();
  await expect(page.locator('.ottie-slot[data-ottie-placement="project"]')).toHaveCount(1);
});

test("lists writing linked to the project", async ({ page }) => {
  await expect(page.getByRole("link", { name: "Sample case study post" })).toHaveAttribute("href", "/writing/sample-case-study/");
});
```

In `routes.ts`, add `...PROJECTS.map((p) => `/work/${p.id}/`)` to `CONTENT_ROUTES`.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/case-study.spec.ts`
Expected: FAIL, 404.

- [ ] **Step 2: Write the summary block and the page**

```astro
---
// site/src/components/ProjectSummary.astro: problem, Din's role, stack, results with real numbers (PRD 2).
import type { CollectionEntry } from "astro:content";
interface Props { project: CollectionEntry<"projects"> }
const { summary, role, stack, results, repo } = Astro.props.project.data;
---
<dl class="summary">
  <div><dt class="t-label">Problem</dt><dd>{summary}</dd></div>
  <div><dt class="t-label">Role</dt><dd>{role}</dd></div>
  <div><dt class="t-label">Stack</dt><dd><ul class="inline">{stack.map((s) => <li class="tag">{s}</li>)}</ul></dd></div>
  <div class="results"><dt class="t-label">Results</dt><dd><ul>{results.map((r) => <li><span class="value t-data">{r.value}</span> {r.label}</li>)}</ul></dd></div>
  {repo && <div><dt class="t-label">Code</dt><dd><a href={repo}>Source on GitHub</a></dd></div>}
</dl>
<style>
  .summary { display: grid; gap: var(--space-5); grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr)); margin: var(--space-7) 0; padding: var(--space-6); background: var(--color-surface); border: 1px solid var(--color-hairline); border-radius: var(--radius-lg); }
  dt { color: var(--color-accent); margin-block-end: var(--space-2); }
  dd { margin: 0; }
  ul { list-style: none; padding: 0; margin: 0; }
  .inline { display: flex; flex-wrap: wrap; gap: var(--space-2); }
  .value { font-size: var(--text-h4); color: var(--color-ink); }
</style>
```

```astro
---
// site/src/pages/work/[id].astro: the case study.
import { render } from "astro:content";
import BaseLayout from "../../layouts/BaseLayout.astro";
import AskSlot from "../../components/AskSlot.astro";
import Draft from "../../components/Draft.astro";
import OttieSlot from "../../components/OttieSlot.astro";
import PostCard from "../../components/PostCard.astro";
import ProjectSummary from "../../components/ProjectSummary.astro";
import ProjectWindow from "../../components/ProjectWindow.astro";
import Prose from "../../components/Prose.astro";
import { getVisiblePosts, getVisibleProjects } from "../../lib/collections";
import { postsForProject } from "../../lib/content";
import { KIND_LABELS } from "../../lib/kinds";
import { site } from "../../data/site";

export async function getStaticPaths() {
  const projects = await getVisibleProjects();
  const posts = await getVisiblePosts();
  return projects.map((project) => ({ params: { id: project.id }, props: { project, related: postsForProject(posts, project.id) } }));
}
const { project, related } = Astro.props;
const { Content } = await render(project);
const { title, summary, kind, status } = project.data;
---
<BaseLayout title={title} description={summary} type="article" card={{ variant: "A", label: "Case study", title }} current="work">
  <Draft status={status} as="article" class="wrap section case">
    <header class="stack">
      <span class="t-label eyebrow">Case study · {KIND_LABELS[kind]}</span>
      <h1 class="t-h1">{title}</h1>
      <p class="t-lead">{summary}</p>
    </header>
    <ProjectWindow project={project} eager />
    <ProjectSummary project={project} />
    {project.data.demo && project.data.demo.type !== "video" && (
      <p><a class="btn" href={project.data.demo.src}>Open the {project.data.demo.type === "chart" ? "chart" : "live demo"}</a></p>
    )}
    <Prose><Content /></Prose>
    <section class="ask-project" aria-labelledby="ask-project-h">
      <div class="ask-text">
        <h2 id="ask-project-h" class="t-h3">Ask Ottie about this project</h2>
        <AskSlot scope="project" project={project.id}>
          <p class="t-small">Questions about {title}? <a href={`mailto:${site.email}?subject=${encodeURIComponent(title)}`}>Email Din</a>.</p>
        </AskSlot>
      </div>
      <OttieSlot placement="project" />
    </section>
    {related.length > 0 && (
      <section aria-labelledby="related-h">
        <h2 id="related-h" class="t-h3">Writing about this project</h2>
        <div class="related">{related.map((p) => <PostCard post={p} />)}</div>
      </section>
    )}
  </Draft>
</BaseLayout>
<style>
  .ask-project { display: flex; gap: var(--space-6); align-items: flex-end; flex-wrap: wrap; margin-block: var(--space-9) var(--space-7); padding-block-start: var(--space-6); border-block-start: 1px solid var(--color-hairline); }
  .ask-text { flex: 1 1 24rem; }
  .related { display: grid; gap: var(--space-5); grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr)); }
</style>
```

- [ ] **Step 3: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/case-study.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS for all three sample projects.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/ProjectSummary.astro site/src/pages/work/[id].astro site/tests/e2e
git commit -m "feat(site): case studies with the window, summary block and project Ask slot"
```

## Task 12: /writing, posts and RSS

**Files:**
- Create: `site/src/pages/writing/index.astro`, `site/src/pages/writing/[id].astro`, `site/src/pages/rss.xml.ts`, `site/tests/e2e/writing.spec.ts`
- Modify: `site/package.json` (add `@astrojs/rss`), `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `getVisiblePosts`, `getVisibleProjects`, `linkedProject`, `readingMinutes` (Task 4), `articleJsonLd` (Task 6), `PostCard`, `Motif`, `OttieSlot`, `Prose`, `Draft`.
- Produces: routes `/writing/`, `/writing/<id>/`, `/rss.xml`.

- [ ] **Step 1: Install RSS**

Run: `pnpm --dir site add @astrojs/rss@~4.0.19`
Why: the writing feed (PRD 2).

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/e2e/writing.spec.ts
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN, POSTS } from "./routes";

test("the writing page lists posts newest first", async ({ page }) => {
  await page.goto("/writing/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Writing");
  const dates = await page.locator("article.post-card time").evaluateAll((els) => els.map((e) => e.getAttribute("datetime")!));
  expect(dates).toEqual([...dates].sort().reverse());
  expect(dates).toHaveLength(POSTS.length);
});

test("a post shows its kind, date, reading time and linked project", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs a post");
  await page.goto("/writing/sample-case-study/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Sample case study post");
  await expect(page.locator("header time")).toHaveAttribute("datetime", "2026-10-27");
  await expect(page.getByText(/min read/)).toBeVisible();
  await expect(page.getByRole("link", { name: "passfx" })).toHaveAttribute("href", "/work/passfx/");
});

test("devlogs get Ottie, other posts do not", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs posts");
  await page.goto("/writing/sample-devlog/");
  await expect(page.locator('.ottie-slot[data-ottie-placement="devlog"]')).toHaveCount(1);
  await page.goto("/writing/sample-note/");
  await expect(page.locator(".ottie-slot")).toHaveCount(0);
});

test("the RSS feed is valid and lists the visible posts", async ({ request }) => {
  const res = await request.get("/rss.xml");
  expect(res.status()).toBe(200);
  const xml = await res.text();
  expect(xml).toMatch(/^<\?xml/);
  expect(xml).toContain("<rss");
  expect(xml.match(/<item>/g)?.length ?? 0).toBe(POSTS.length);
  for (const p of POSTS) expect(xml).toContain(`https://dins.dev/writing/${p.id}/`);
});
```

In `routes.ts`, change `STATIC_ROUTES` to `["/", "/work/", "/writing/"]` and add `...POSTS.map((p) => `/writing/${p.id}/`)` to `CONTENT_ROUTES`.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/writing.spec.ts`
Expected: FAIL, 404.

- [ ] **Step 3: Write the pages and the feed**

```astro
---
// site/src/pages/writing/index.astro
import BaseLayout from "../../layouts/BaseLayout.astro";
import PostCard from "../../components/PostCard.astro";
import { getVisiblePosts } from "../../lib/collections";
const posts = await getVisiblePosts();
---
<BaseLayout title="Writing" description="Case studies, devlogs and notes from Din." card={{ variant: "A", label: "Writing", title: "Writing" }} current="writing">
  <div class="wrap section">
    <h1 class="t-h1">Writing</h1>
    <p class="t-lead">Case studies, devlogs and notes. Also as an <a href="/rss.xml">RSS feed</a>.</p>
    {posts.length ? (
      <div class="list">{posts.map((p) => <PostCard post={p} headingLevel={2} />)}</div>
    ) : (
      <p class="empty" data-empty>The first posts are on their way.</p>
    )}
  </div>
</BaseLayout>
<style>
  .list { display: grid; gap: var(--space-5); grid-template-columns: repeat(auto-fit, minmax(min(100%, 20rem), 1fr)); margin-block-start: var(--space-6); }
</style>
```

```astro
---
// site/src/pages/writing/[id].astro
import { render } from "astro:content";
import BaseLayout from "../../layouts/BaseLayout.astro";
import Draft from "../../components/Draft.astro";
import Motif from "../../components/Motif.astro";
import OttieSlot from "../../components/OttieSlot.astro";
import Prose from "../../components/Prose.astro";
import { getVisiblePosts, getVisibleProjects } from "../../lib/collections";
import { linkedProject, readingMinutes } from "../../lib/content";
import { WRITING_KIND_LABELS } from "../../lib/kinds";
import { formatDate, isoDate } from "../../lib/dates";
import { articleJsonLd } from "../../lib/seo";
import { site } from "../../data/site";

export async function getStaticPaths() {
  const posts = await getVisiblePosts();
  const projects = await getVisibleProjects();
  return posts.map((post) => ({ params: { id: post.id }, props: { post, project: linkedProject(post, projects) } }));
}
const { post, project } = Astro.props;
const { Content } = await render(post);
const { title, summary, kind, date, motif, status } = post.data;
const isDevlog = post.data.devlog ?? kind === "devlog";
const label = WRITING_KIND_LABELS[kind];
---
<BaseLayout
  title={title}
  description={summary}
  type="article"
  card={{ variant: isDevlog ? "C" : "A", label, title }}
  jsonLd={[articleJsonLd({ site, title, summary, date, path: Astro.url.pathname })]}
  current="writing"
>
  <Draft status={status} as="article" class="wrap section post">
    <header class="stack">
      <Motif name={motif} />
      <p class="meta"><span class="t-label">{label}</span>{" "}<time class="t-data" datetime={isoDate(date)}>{formatDate(date)}</time>{" "}<span class="t-data">{readingMinutes(post.body ?? "")} min read</span></p>
      <h1 class="t-h1">{title}</h1>
      <p class="t-lead">{summary}</p>
      {project && <p class="t-small">From the project <a href={`/work/${project.id}/`}>{project.data.title}</a>.</p>}
    </header>
    <div class="body">
      <Prose><Content /></Prose>
      {isDevlog && <OttieSlot placement="devlog" />}
    </div>
  </Draft>
</BaseLayout>
<style>
  .post header { max-width: var(--measure); margin-block-end: var(--space-7); }
  .post :global(.motif) { max-width: 200px; }
  .meta { display: flex; gap: var(--space-3); flex-wrap: wrap; color: var(--color-muted); margin: 0; }
  .body { display: flex; gap: var(--space-7); align-items: flex-start; flex-wrap: wrap; }
  .body :global(.prose) { flex: 1 1 32rem; }
</style>
```

```ts
// site/src/pages/rss.xml.ts
import rss from "@astrojs/rss";
import type { APIContext } from "astro";
import { getVisiblePosts } from "../lib/collections";

export async function GET(context: APIContext) {
  const posts = await getVisiblePosts();
  return rss({
    title: "dins.dev writing",
    description: "Case studies, devlogs and notes from Din.",
    site: context.site!,
    items: posts.map((p) => ({
      title: p.data.title,
      pubDate: p.data.date,
      description: p.data.summary,
      link: `/writing/${p.id}/`,
    })),
    customData: "<language>en</language>",
  });
}
```

- [ ] **Step 4: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/writing.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add site/src/pages/writing site/src/pages/rss.xml.ts site/tests/e2e site/package.json pnpm-lock.yaml
git commit -m "feat(site): writing list, posts and the RSS feed"
```

## Task 13: /about with the timeline

**Files:**
- Create: `site/src/components/Timeline.astro`, `site/src/pages/about.astro`, `site/tests/e2e/about.spec.ts`
- Modify: `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `profile`, `site`, `visibleValue`, `TimelineEntry` (Task 5), `formatYearMonth` (Task 6), `profilePageJsonLd` (Task 6), `getVisibleProjects` (Task 4), `Draft`.
- Produces: route `/about/`; `Timeline` props `{ entries: TimelineEntry[]; projectIds: string[] }`; the `#resume` section anchor.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/e2e/about.spec.ts
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN } from "./routes";

test.beforeEach(async ({ page }) => {
  await page.goto("/about/");
});

test("opens on the screen, then bio, timeline, skills and languages", async ({ page }) => {
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("About");
  await expect(page.locator('[data-setpiece="studio-screen"]')).toBeVisible();
  if (DRAFTS_SHOWN) {
    for (const name of ["Education and experience", "Skills", "Languages"]) {
      await expect(page.getByRole("heading", { level: 2, name })).toBeVisible();
    }
    await expect(page.locator("ol.timeline > li")).toHaveCount(2);
    await expect(page.locator("ol.timeline time").first()).toHaveAttribute("datetime", /^\d{4}(-\d{2})?$/);
  }
});

test("carries ProfilePage structured data about Din", async ({ page }) => {
  const data = await page.locator('script[type="application/ld+json"]').evaluateAll((els) => els.map((e) => JSON.parse(e.textContent!)));
  expect(data.find((d) => d["@type"] === "ProfilePage")?.mainEntity["@type"]).toBe("Person");
});

test("offers the resume only when one is linked", async ({ page }) => {
  const link = page.getByRole("link", { name: /Download the resume/ });
  const count = await link.count();
  if (count) await expect(link).toHaveAttribute("href", /\.pdf$/);
  else await expect(page.locator("#resume")).toHaveCount(0);
});
```

In `routes.ts`, add `"/about/"` to `STATIC_ROUTES`.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/about.spec.ts`
Expected: FAIL, 404.

- [ ] **Step 2: Write the timeline and the page**

```astro
---
// site/src/components/Timeline.astro: education and experience, newest first.
import type { TimelineEntry } from "../lib/schemas";
import { formatYearMonth } from "../lib/dates";
import Draft from "./Draft.astro";
interface Props { entries: TimelineEntry[]; projectIds: string[] }
const { entries, projectIds } = Astro.props;
const sorted = [...entries].sort((a, b) => b.start.localeCompare(a.start));
---
<ol class="timeline">
  {sorted.map((e) => (
    <li>
      <Draft status={e.status}>
        <p class="when t-data">
          <time datetime={e.start}>{formatYearMonth(e.start)}</time> to{" "}
          {e.end ? <time datetime={e.end}>{formatYearMonth(e.end)}</time> : "now"}
        </p>
        <h3 class="t-h4">{e.title}, {e.org}</h3>
        <p class="t-small kind">{e.kind === "education" ? "Education" : "Experience"}</p>
        {e.detail && <p>{e.detail}</p>}
        {e.project && projectIds.includes(e.project) && <p><a href={`/work/${e.project}/`}>See the project</a></p>}
      </Draft>
    </li>
  ))}
</ol>
<style>
  .timeline { list-style: none; padding: 0; margin: 0; border-inline-start: 2px solid var(--color-hairline); }
  .timeline > li { padding: 0 0 var(--space-6) var(--space-5); position: relative; }
  .timeline > li::before { content: ""; position: absolute; left: -7px; top: 0.4em; width: 12px; height: 12px; border-radius: 50%; background: var(--color-accent); }
  .when { color: var(--color-muted); margin: 0; }
  h3 { margin: var(--space-1) 0; }
  .kind { margin: 0; }
</style>
```

```astro
---
// site/src/pages/about.astro: the calm About. M4 turns the screen panel into the studio's zoom.
import BaseLayout from "../layouts/BaseLayout.astro";
import Draft from "../components/Draft.astro";
import Timeline from "../components/Timeline.astro";
import { getVisibleProjects } from "../lib/collections";
import { SHOW_DRAFTS } from "../lib/build";
import { isVisible } from "../lib/drafts";
import { visibleValue } from "../lib/schemas";
import { profilePageJsonLd } from "../lib/seo";
import { profile } from "../data/profile";
import { site } from "../data/site";

const bio = visibleValue(profile.bio, SHOW_DRAFTS);
const skills = visibleValue(profile.skills, SHOW_DRAFTS);
const languages = visibleValue(profile.languages, SHOW_DRAFTS);
const timeline = profile.timeline.filter((t) => isVisible(t.status, SHOW_DRAFTS));
const projectIds = (await getVisibleProjects()).map((p) => p.id);
const publishedRole = profile.roleLine.status === "published" ? profile.roleLine.value : null;
---
<BaseLayout title="About" description="Who Din is: bio, education and experience, skills and languages." card={{ variant: "A", label: "About", title: "About Din" }} jsonLd={[profilePageJsonLd(site, publishedRole)]} current="about">
  <div class="wrap section stack">
    <div class="screen-panel" data-setpiece="studio-screen">
      <pre class="t-data"><span aria-hidden="true">$ </span>whoami{"\n"}din</pre>
    </div>
    <h1 class="t-h1">About</h1>
    {bio && <Draft status={bio.status} class="bio">{bio.value.map((p) => <p class="t-body">{p}</p>)}</Draft>}

    {timeline.length > 0 && (
      <section aria-labelledby="timeline-h">
        <h2 id="timeline-h" class="t-h2">Education and experience</h2>
        <Timeline entries={timeline} projectIds={projectIds} />
      </section>
    )}

    {skills && (
      <section aria-labelledby="skills-h">
        <h2 id="skills-h" class="t-h2">Skills</h2>
        <Draft status={skills.status}>
          <dl class="skills">
            {skills.value.map((g) => <div><dt class="t-label">{g.group}</dt><dd>{g.items.join(", ")}</dd></div>)}
          </dl>
        </Draft>
      </section>
    )}

    {languages && (
      <section aria-labelledby="languages-h">
        <h2 id="languages-h" class="t-h2">Languages</h2>
        <Draft status={languages.status}>
          <ul class="langs">{languages.value.map((l) => <li><strong>{l.name}</strong>: {l.level}</li>)}</ul>
        </Draft>
      </section>
    )}

    {site.links.resume && (
      <section id="resume" aria-labelledby="resume-h">
        <h2 id="resume-h" class="t-h2">Resume</h2>
        <p><a class="btn btn-primary" href={site.links.resume} download>Download the resume (PDF)</a></p>
      </section>
    )}
  </div>
</BaseLayout>
<style>
  .screen-panel { background: #1F1E1C; color: #ECE9E2; border-radius: var(--radius-lg); padding: var(--space-6); max-width: 40rem; }
  .screen-panel pre { margin: 0; font-size: var(--text-body); white-space: pre-wrap; }
  .skills { display: grid; gap: var(--space-4); grid-template-columns: repeat(auto-fit, minmax(min(100%, 16rem), 1fr)); }
  .skills dt { color: var(--color-accent); }
  .skills dd { margin: var(--space-1) 0 0; }
  .langs { padding-inline-start: var(--space-5); }
</style>
```

The screen panel uses the dark palette's fixed values on purpose (it is a screen in both themes); its text contrast is 13.7 (BRAND.md).

- [ ] **Step 3: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/about.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add site/src/components/Timeline.astro site/src/pages/about.astro site/tests/e2e
git commit -m "feat(site): about page with the timeline, skills and languages"
```

## Task 14: /contact as a plain form

**Files:**
- Create: `site/src/pages/contact/index.astro`, `site/src/pages/contact/sent.astro`, `site/src/pages/contact/not-sent.astro`, `site/tests/e2e/contact.spec.ts`
- Modify: `site/tests/e2e/routes.ts`

**Interfaces:**
- Consumes: `ContactForm`, `OttieSlot` (Task 9), `CONTACT_FIELDS`, `CONTACT_LIMITS`, `CONTACT_REDIRECTS` (Task 7).
- Produces: routes `/contact/`, `/contact/sent/`, `/contact/not-sent/` (the last two `noindex` and never in the sitemap). M4 adjusts these pages rather than creating its own.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/e2e/contact.spec.ts
import { expect, test } from "@playwright/test";

test("the contact page is a real form that posts to /api/contact", async ({ page }) => {
  await page.goto("/contact/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Write to me.");
  const form = page.locator("form[data-letter-form]");
  await expect(form).toHaveAttribute("method", "post");
  await expect(form).toHaveAttribute("action", "/api/contact");
  await expect(page.getByLabel("Message")).toHaveAttribute("maxlength", "4000");
  await expect(page.getByLabel("Your email")).toHaveAttribute("type", "email");
  await expect(page.getByRole("radio", { name: "A role" })).toBeChecked();
});

test("the honeypot is out of reach for keyboard and screen readers", async ({ page }) => {
  await page.goto("/contact/");
  const hp = page.locator('input[name="website"]');
  await expect(hp).toHaveAttribute("tabindex", "-1");
  await expect(page.locator(".hp")).toHaveAttribute("aria-hidden", "true");
});

test("the browser blocks an empty submit", async ({ page }) => {
  await page.goto("/contact/");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page).toHaveURL(/\/contact\/$/);
  expect(await page.getByLabel("Message").evaluate((el: HTMLTextAreaElement) => el.validity.valueMissing)).toBe(true);
});

test("the sent and not-sent pages exist and are not indexed", async ({ page }) => {
  for (const [path, heading] of [["/contact/sent/", "Sent. Thank you."], ["/contact/not-sent/", "Not sent."]]) {
    await page.goto(path);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText(heading);
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", "noindex");
  }
});

test("the not-sent page offers email instead", async ({ page }) => {
  await page.goto("/contact/not-sent/");
  await expect(page.getByRole("main").getByRole("link", { name: "din@dins.dev" })).toHaveAttribute("href", "mailto:din@dins.dev");
});
```

In `routes.ts`, add `"/contact/"` to `STATIC_ROUTES` and set `UTILITY_ROUTES` to `["/contact/sent/", "/contact/not-sent/"]`.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/contact.spec.ts`
Expected: FAIL, 404.

- [ ] **Step 2: Write the pages**

```astro
---
// site/src/pages/contact/index.astro
import BaseLayout from "../../layouts/BaseLayout.astro";
import ContactForm from "../../components/ContactForm.astro";
import OttieSlot from "../../components/OttieSlot.astro";
---
<BaseLayout title="Contact" description="Write to Din about a role, admissions, or just to say hello." card={{ variant: "A", label: "Contact", title: "Write to Din" }} current="contact">
  <div class="wrap section layout">
    <div class="stack">
      <h1 class="t-h1">Write to me.</h1>
      <p class="t-lead">Roles, admissions questions, or just a hello. It lands in my inbox.</p>
      <ContactForm />
    </div>
    <OttieSlot placement="contact" />
  </div>
</BaseLayout>
<style>
  .layout { display: flex; gap: var(--space-7); align-items: flex-end; flex-wrap: wrap; }
  .layout > .stack { flex: 1 1 32rem; }
</style>
```

```astro
---
// site/src/pages/contact/sent.astro: where a no-JavaScript submit lands after a 303 (CONTACT_REDIRECTS.sent).
import BaseLayout from "../../layouts/BaseLayout.astro";
---
<BaseLayout title="Message sent" description="Your message to Din was sent." card={null} noindex>
  <div class="wrap section stack">
    <h1 class="t-h1">Sent. Thank you.</h1>
    <p class="t-lead">I’ll reply to the email you gave.</p>
    <div class="actions"><a class="btn" href="/contact/">Write another</a><a class="btn" href="/">Back to the home page</a></div>
  </div>
</BaseLayout>
<style>
  .actions { display: flex; flex-wrap: wrap; gap: var(--space-2); }
</style>
```

```astro
---
// site/src/pages/contact/not-sent.astro: where a post that was not accepted lands (CONTACT_REDIRECTS.notSent).
// Every post without JavaScript lands here, because it carries no Turnstile token (Din, 2026-10-21).
import BaseLayout from "../../layouts/BaseLayout.astro";
import { site } from "../../data/site";
---
<BaseLayout title="Message not sent" description="Your message could not be sent from the form." card={null} noindex>
  <div class="wrap section stack">
    <h1 class="t-h1">Not sent.</h1>
    <p class="t-lead">The form could not send your message. It needs JavaScript to check that a person is writing, and something stopped that check.</p>
    <p>Your message is not lost if you still have it: email it to <a href={`mailto:${site.email}`}>{site.email}</a> and it reaches the same inbox.</p>
    <div class="actions"><a class="btn" href="/contact/">Back to the form</a></div>
  </div>
</BaseLayout>
<style>
  .actions { display: flex; flex-wrap: wrap; gap: var(--space-2); }
</style>
```

- [ ] **Step 3: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark --project=phone tests/e2e/contact.spec.ts tests/e2e/pages.spec.ts tests/e2e/layout.spec.ts`
Expected: PASS. A real submit returns 404 until M4 builds `/api/contact`; that is expected in M1. M4 answers no-JavaScript posts with a 303 to `/contact/not-sent/`.

- [ ] **Step 4: Commit**

```bash
git add site/src/pages/contact site/tests/e2e
git commit -m "feat(site): contact page as a plain form, with sent and error pages"
```

## Task 15: /privacy and the 404

**Files:**
- Create: `site/src/pages/privacy.astro`, `site/src/pages/404.astro`, `site/tests/e2e/misc.spec.ts`
- Modify: `site/tests/e2e/routes.ts`, `site/tests/e2e/pages.spec.ts` (enable the 404 test), possibly `site/wrangler.jsonc`

**Interfaces:**
- Consumes: `BaseLayout`, `OttieSlot`, `site`.
- Produces: routes `/privacy/` and the 404 page.

- [ ] **Step 1: Write the failing tests**

```ts
// site/tests/e2e/misc.spec.ts
import { expect, test } from "@playwright/test";

test("privacy lists what the site does and does not collect", async ({ page }) => {
  await page.goto("/privacy/");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Privacy");
  for (const text of ["No cookies", "Cloudflare Web Analytics", "Turnstile", "30 days", "not stored", "local storage"]) {
    await expect(page.getByText(text, { exact: false }).first()).toBeVisible();
  }
});

test("unknown paths get the 404 page with Ottie and a way home", async ({ page }) => {
  for (const path of ["/this-page-does-not-exist/", "/work/nope/", "/writing/nope"]) {
    const res = await page.goto(path);
    expect(res?.status(), path).toBe(404);
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("This page is not here.");
    await expect(page.locator('.ottie-slot[data-ottie-placement="404"]')).toHaveAttribute("data-ottie-state", "shrug");
    await expect(page.getByRole("main").getByRole("link", { name: "Home" })).toHaveAttribute("href", "/");
  }
});

test("slashless paths reach the same page", async ({ page }) => {
  const res = await page.goto("/work");
  expect(res?.status()).toBe(200);
  await expect(page).toHaveURL(/\/work\/$/);
});
```

In `pages.spec.ts`, delete the `test.skip(true, ...)` line in the "not found" block, and in `routes.ts` add `"/privacy/"` to `STATIC_ROUTES`.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/misc.spec.ts`
Expected: FAIL.

- [ ] **Step 2: Write the pages**

```astro
---
// site/src/pages/privacy.astro: plain words (PRD 2 and 6). Din reviews this text (Din task D8).
import BaseLayout from "../layouts/BaseLayout.astro";
import { site } from "../data/site";
const updated = "2026-10-27";
---
<BaseLayout title="Privacy" description="What dins.dev collects (very little) and why." card={{ variant: "A", label: "Privacy", title: "Privacy" }}>
  <div class="wrap section">
    <article class="prose-page stack">
      <h1 class="t-h1">Privacy</h1>
      <p class="t-lead">No cookies, no ads, no tracking across sites, and no consent banner, because there is nothing to consent to.</p>
      <h2 class="t-h3">What runs on this site</h2>
      <ul>
        <li><strong>Cloudflare Web Analytics</strong> counts page views without cookies and without identifying you.</li>
        <li><strong>Cloudflare Turnstile</strong> checks that the Ask Ottie box and the contact form are used by a person. It is Cloudflare’s privacy-friendly alternative to a CAPTCHA.</li>
      </ul>
      <h2 class="t-h3">Ask Ottie</h2>
      <p>When you ask Ottie a question, the site keeps an anonymous log: the question, which sources were used, their scores, and your thumbs up or down if you give one. No IP address and no cookies. Entries are deleted after 30 days. The log is how the answers get better.</p>
      <h2 class="t-h3">The contact form</h2>
      <p>Your message, name and email are emailed to Din and not stored on this site.</p>
      <h2 class="t-h3">In your browser</h2>
      <p>If you switch between light and dark, the choice is kept in your browser’s local storage so the next page matches. It never leaves your device.</p>
      <h2 class="t-h3">Questions</h2>
      <p>Email <a href={`mailto:${site.email}`}>{site.email}</a>.</p>
      <p class="t-small">Last updated <time datetime={updated}>27 October 2026</time>.</p>
    </article>
  </div>
</BaseLayout>
<style>
  .prose-page { max-width: var(--measure); }
</style>
```

```astro
---
// site/src/pages/404.astro: Ottie shrugs (PRD 2 and 4). M2 plays the shrug state on this slot.
import BaseLayout from "../layouts/BaseLayout.astro";
import OttieSlot from "../components/OttieSlot.astro";
---
<BaseLayout title="Page not found" description="This page is not on dins.dev." card={null} noindex>
  <div class="wrap section layout">
    <div class="stack">
      <h1 class="t-h1">This page is not here.</h1>
      <p class="t-lead">It may have moved, or it never existed. These are a good place to start:</p>
      <ul class="links">
        <li><a class="btn" href="/">Home</a></li>
        <li><a class="btn" href="/work/">Work</a></li>
        <li><a class="btn" href="/writing/">Writing</a></li>
        <li><a class="btn" href="/contact/">Contact</a></li>
      </ul>
    </div>
    <OttieSlot placement="404" state="shrug" />
  </div>
</BaseLayout>
<style>
  .layout { display: flex; gap: var(--space-7); align-items: flex-end; flex-wrap: wrap; }
  .layout > .stack { flex: 1 1 28rem; }
  .links { display: flex; flex-wrap: wrap; gap: var(--space-2); list-style: none; padding: 0; margin: 0; }
</style>
```

- [ ] **Step 3: Run the tests**

Run: `pnpm --dir site exec playwright test --project=chromium --project=dark tests/e2e/misc.spec.ts tests/e2e/pages.spec.ts`
Expected: PASS. If the unknown-path test gets status 200 or the plain Workers 404 instead of the page, add `"not_found_handling": "404-page"` to the `assets` block in `site/wrangler.jsonc`, rebuild and rerun; expected PASS. If `/work` does not redirect to `/work/`, check that `assets.html_handling` is the default `"auto-trailing-slash"`.

- [ ] **Step 4: Commit**

```bash
git add site/src/pages/privacy.astro site/src/pages/404.astro site/tests/e2e site/wrangler.jsonc
git commit -m "feat(site): privacy page and the 404 with Ottie"
```

## Task 16: SEO files (sitemap, robots, llms.txt, security.txt)

**Files:**
- Create: `site/src/lib/sitemap.ts`, `site/src/lib/textfiles.ts`, `site/src/pages/{sitemap.xml.ts,robots.txt.ts,llms.txt.ts}`, `site/src/pages/.well-known/security.txt.ts`, `site/tests/e2e/seo.spec.ts`
- Test: `site/tests/unit/sitemap.test.ts`, `site/tests/unit/textfiles.test.ts`

**Interfaces:**
- Consumes: `BUILD_FLAGS` (Task 1), `getVisibleProjects`, `getVisiblePosts`, `kindsWithProjects` (Task 4), `profile`, `site` (Task 5), `canonicalUrl` (Task 6).
- Produces: `INDEXABLE_STATIC_ROUTES`, `buildSitemap(urls: { path: string; lastmod?: Date }[]): string`, `buildRobotsTxt(noindex: boolean): string`, `buildLlmsTxt(input: LlmsInput): string`, `buildSecurityTxt(now: Date): string`; routes `/sitemap.xml`, `/robots.txt`, `/llms.txt`, `/.well-known/security.txt`.

The site writes its own `sitemap.xml` (PRD names that file) instead of using `@astrojs/sitemap`, which writes `sitemap-index.xml`; the route list is small and already known.

- [ ] **Step 1: Write the failing unit tests**

```ts
// site/tests/unit/sitemap.test.ts
import { describe, expect, it } from "vitest";
import { buildSitemap, INDEXABLE_STATIC_ROUTES } from "../../src/lib/sitemap";

describe("buildSitemap", () => {
  it("lists absolute, slashed URLs with an optional lastmod", () => {
    const xml = buildSitemap([{ path: "/" }, { path: "/writing/a", lastmod: new Date("2026-10-27T00:00:00Z") }]);
    expect(xml).toContain("<loc>https://dins.dev/</loc>");
    expect(xml).toContain("<loc>https://dins.dev/writing/a/</loc><lastmod>2026-10-27</lastmod>");
    expect(xml.startsWith('<?xml version="1.0" encoding="UTF-8"?>')).toBe(true);
  });
  it("escapes XML characters", () => {
    expect(buildSitemap([{ path: "/a&b/" }])).toContain("a&amp;b");
  });
  it("is valid with only the static pages (production before launch)", () => {
    const xml = buildSitemap(INDEXABLE_STATIC_ROUTES.map((path) => ({ path })));
    expect(xml.match(/<url>/g)).toHaveLength(6);
  });
});
```

```ts
// site/tests/unit/textfiles.test.ts
import { describe, expect, it } from "vitest";
import { buildLlmsTxt, buildRobotsTxt, buildSecurityTxt } from "../../src/lib/textfiles";

describe("robots.txt", () => {
  it("allows crawling and names the sitemap in production", () => {
    const txt = buildRobotsTxt(false);
    expect(txt).toContain("Allow: /");
    expect(txt).toContain("Disallow: /api/");
    expect(txt).toContain("Sitemap: https://dins.dev/sitemap.xml");
  });
  it("blocks everything on previews", () => {
    expect(buildRobotsTxt(true)).toBe("User-agent: *\nDisallow: /\n");
  });
});

describe("llms.txt", () => {
  it("follows the llms.txt shape and leaves out empty sections", () => {
    const txt = buildLlmsTxt({ roleLine: null, projects: [], posts: [] });
    expect(txt.startsWith("# dins.dev\n\n> ")).toBe(true);
    expect(txt).toContain("## Pages");
    expect(txt).toContain("- [Work](https://dins.dev/work/)");
    expect(txt).not.toContain("## Projects");
  });
  it("lists projects and posts with their summaries", () => {
    const txt = buildLlmsTxt({
      roleLine: "Role line",
      projects: [{ id: "a", title: "A [b]", summary: "S." }],
      posts: [{ id: "p", title: "P", summary: "T." }],
    });
    expect(txt).toContain("> Role line");
    expect(txt).toContain("- [A \\[b\\]](https://dins.dev/work/a/): S.");
    expect(txt).toContain("- [P](https://dins.dev/writing/p/): T.");
  });
});

describe("security.txt", () => {
  it("has the RFC 9116 fields with an expiry 180 days out", () => {
    const txt = buildSecurityTxt(new Date("2026-10-27T12:00:00Z"));
    expect(txt).toContain("Contact: mailto:din@dins.dev\n");
    expect(txt).toContain("Expires: 2027-04-25T00:00:00.000Z\n");
    expect(txt).toContain("Preferred-Languages: en, fr\n");
    expect(txt).toContain("Canonical: https://dins.dev/.well-known/security.txt\n");
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/sitemap.test.ts tests/unit/textfiles.test.ts`
Expected: FAIL, modules missing.

- [ ] **Step 2: Write the implementation**

```ts
// site/src/lib/sitemap.ts
import { canonicalUrl } from "./seo";

export const INDEXABLE_STATIC_ROUTES = ["/", "/work/", "/writing/", "/about/", "/contact/", "/privacy/"];

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

export function buildSitemap(urls: { path: string; lastmod?: Date }[]): string {
  const body = urls
    .map((u) => `<url><loc>${esc(canonicalUrl(u.path))}</loc>${u.lastmod ? `<lastmod>${u.lastmod.toISOString().slice(0, 10)}</lastmod>` : ""}</url>`)
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${body}\n</urlset>\n`;
}
```

```ts
// site/src/lib/textfiles.ts
import { SITE_URL } from "./seo";

export function buildRobotsTxt(noindex: boolean): string {
  if (noindex) return "User-agent: *\nDisallow: /\n";
  return `User-agent: *\nAllow: /\nDisallow: /api/\n\nSitemap: ${SITE_URL}/sitemap.xml\n`;
}

type Item = { id: string; title: string; summary: string };
export type LlmsInput = { roleLine: string | null; projects: Item[]; posts: Item[] };

const mdText = (s: string) => s.replace(/([[\]])/g, "\\$1");

export function buildLlmsTxt({ roleLine, projects, posts }: LlmsInput): string {
  const lines = [
    "# dins.dev",
    "",
    `> ${roleLine ?? "Din’s portfolio: projects, writing, and how to get in touch."}`,
    "",
    "Ottie, on the home page, answers questions about Din’s work from a library Din approved.",
    "",
    "## Pages",
    "",
    `- [Work](${SITE_URL}/work/): every published project`,
    `- [Writing](${SITE_URL}/writing/): case studies, devlogs and notes`,
    `- [About](${SITE_URL}/about/): bio, education, experience and skills`,
    `- [Contact](${SITE_URL}/contact/): how to reach Din`,
  ];
  const section = (title: string, base: string, items: Item[]) => {
    if (!items.length) return;
    lines.push("", `## ${title}`, "", ...items.map((i) => `- [${mdText(i.title)}](${SITE_URL}/${base}/${i.id}/): ${i.summary}`));
  };
  section("Projects", "work", projects);
  section("Writing", "writing", posts);
  return `${lines.join("\n")}\n`;
}

export function buildSecurityTxt(now: Date): string {
  const expires = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 180));
  return [
    "Contact: mailto:din@dins.dev",
    `Expires: ${expires.toISOString()}`,
    "Preferred-Languages: en, fr",
    `Canonical: ${SITE_URL}/.well-known/security.txt`,
    "",
  ].join("\n");
}
```

The expected date in the test is checked by hand: 2026-10-27 plus 180 days is 2027-04-25.

- [ ] **Step 3: Write the endpoints**

```ts
// site/src/pages/sitemap.xml.ts
import { getVisiblePosts, getVisibleProjects } from "../lib/collections";
import { kindsWithProjects } from "../lib/content";
import { buildSitemap, INDEXABLE_STATIC_ROUTES } from "../lib/sitemap";

export async function GET() {
  const projects = await getVisibleProjects();
  const posts = await getVisiblePosts();
  const urls = [
    ...INDEXABLE_STATIC_ROUTES.map((path) => ({ path })),
    ...kindsWithProjects(projects).map((k) => ({ path: `/work/kind/${k}/` })),
    ...projects.map((p) => ({ path: `/work/${p.id}/` })),
    ...posts.map((p) => ({ path: `/writing/${p.id}/`, lastmod: p.data.date })),
  ];
  return new Response(buildSitemap(urls), { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
```

```ts
// site/src/pages/robots.txt.ts
import { BUILD_FLAGS } from "../lib/build";
import { buildRobotsTxt } from "../lib/textfiles";

export function GET() {
  return new Response(buildRobotsTxt(BUILD_FLAGS.noindex), { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
```

```ts
// site/src/pages/llms.txt.ts
import { getVisiblePosts, getVisibleProjects } from "../lib/collections";
import { buildLlmsTxt } from "../lib/textfiles";
import { profile } from "../data/profile";

export async function GET() {
  const pick = (e: { id: string; data: { title: string; summary: string } }) => ({ id: e.id, title: e.data.title, summary: e.data.summary });
  const body = buildLlmsTxt({
    roleLine: profile.roleLine.status === "published" ? profile.roleLine.value : null,
    projects: (await getVisibleProjects()).map(pick),
    posts: (await getVisiblePosts()).map(pick),
  });
  return new Response(body, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
```

```ts
// site/src/pages/.well-known/security.txt.ts
import { buildSecurityTxt } from "../../lib/textfiles";

export function GET() {
  return new Response(buildSecurityTxt(new Date()), { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
```

- [ ] **Step 4: Write the SEO e2e spec**

```ts
// site/tests/e2e/seo.spec.ts (chromium project)
import { expect, test } from "@playwright/test";
import { CONTENT_ROUTES, ROUTES, STATIC_ROUTES, UTILITY_ROUTES } from "./routes";

test("every route has a unique title, a description and an absolute slashed canonical", async ({ page }) => {
  const titles = new Set<string>();
  for (const path of ROUTES()) {
    await page.goto(path);
    const title = await page.title();
    expect(titles.has(title), `duplicate title ${title}`).toBe(false);
    titles.add(title);
    await expect(page.locator('meta[name="description"]')).toHaveAttribute("content", /.{20,}/);
    await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", `https://dins.dev${path}`);
  }
});

test("every indexable route is in the sitemap and no utility route is", async ({ request }) => {
  const xml = await (await request.get("/sitemap.xml")).text();
  for (const path of [...STATIC_ROUTES, ...CONTENT_ROUTES]) expect(xml).toContain(`<loc>https://dins.dev${path}</loc>`);
  for (const path of UTILITY_ROUTES) expect(xml).not.toContain(path);
  expect(xml).not.toContain("404");
});

test("robots.txt, llms.txt and security.txt are served", async ({ request }) => {
  const robots = await request.get("/robots.txt");
  expect(robots.status()).toBe(200);
  expect(await robots.text()).toContain("Sitemap: https://dins.dev/sitemap.xml");
  const llms = await request.get("/llms.txt");
  expect(llms.status()).toBe(200);
  expect(await llms.text()).toMatch(/^# dins\.dev/);
  const sec = await request.get("/.well-known/security.txt");
  expect(sec.status()).toBe(200);
  expect(await sec.text()).toMatch(/^Contact: mailto:din@dins\.dev$/m);
});

test("JSON-LD on every route parses", async ({ page }) => {
  for (const path of ROUTES()) {
    await page.goto(path);
    const blocks = await page.locator('script[type="application/ld+json"]').allTextContents();
    for (const b of blocks) expect(() => JSON.parse(b)).not.toThrow();
  }
});
```

- [ ] **Step 5: Run the tests**

Run: `pnpm --dir site exec vitest run tests/unit/sitemap.test.ts tests/unit/textfiles.test.ts`
Expected: PASS.

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/seo.spec.ts`
Expected: PASS. If `/.well-known/security.txt` is 404 because the dot folder was skipped, move the endpoint to `site/src/pages/[wellKnown]/security.txt.ts`, add `export function getStaticPaths() { return [{ params: { wellKnown: ".well-known" } }]; }`, fix the import path to `../../lib/textfiles`, rebuild and rerun; expected PASS.

- [ ] **Step 6: Commit**

```bash
git add site/src/lib/sitemap.ts site/src/lib/textfiles.ts site/src/pages site/tests
git commit -m "feat(site): sitemap, robots.txt, llms.txt and security.txt"
```

## Task 17: Social cards at build time

**Files:**
- Create: `brand/tools/card_fonts.py`, `brand/fonts/cards/*.ttf` (generated), `site/src/og/{spec,card,assets}.ts`, `site/src/integrations/social-cards.ts`, `site/tests/unit/og-spec.test.ts`, `site/tests/unit/og-card.test.ts`, `site/tests/unit/fixtures/html-with-card.html`
- Modify: `site/astro.config.mjs`, `site/package.json`, `site/tests/e2e/seo.spec.ts`

**Interfaces:**
- Consumes: the `dins:card` meta from `Seo.astro` (Task 8), `cardPath`, `cardUrlText` (Task 6).
- Produces: `cardSpecSchema`, `type CardSpec = { variant: "A" | "C" | "home"; label: string; title: string; subtitle?: string; path: string }`, `extractCardSpec(html): CardSpec | null`, `stripCardMeta(html): string` (spec.ts); `titleSize(title, variant): number`, `cardElement(spec, assets)`, `renderCard(spec, assets): Promise<Buffer>`, `CARD_COLORS` (card.ts); `loadCardAssets(): Promise<CardAssets>` (assets.ts); the `socialCards()` integration writing `/og/<path>.png` for every page that has a card.

The cards follow `brand/tools/social-cards.template.html` (A for every page, C for devlogs, the home variant of A with the role line). Satori draws variable fonts at their default instance, so the brand fonts are instanced once into static TTFs.

- [ ] **Step 1: Generate the static card fonts**

```python
# brand/tools/card_fonts.py
"""Write static font instances for the build-time social cards (satori draws variable fonts at
their default instance, which is not the brand's Fraunces 500 SOFT 50).

Usage:  uv run --with "fonttools>=4.67,<5" --with "brotli>=1.2,<2" python brand/tools/card_fonts.py
Output: brand/fonts/cards/*.ttf (committed; used only at build time, never served).
"""

import shutil
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "brand" / "fonts" / "cards"
SEARCH = [ROOT / "brand" / "fonts", ROOT / "brand" / "fonts" / "web"]

JOBS = [
    ("[Ff]raunces*", "Fraunces-Card-500.ttf", {"wght": 500, "opsz": 96, "SOFT": 50, "WONK": 0}),
    ("[Ii]nstrument*", "InstrumentSans-Card-400.ttf", {"wght": 400, "wdth": 100}),
    ("[Jj]et[Bb]rains*", "JetBrainsMono-Card-400.ttf", {"wght": 400}),
    ("[Jj]et[Bb]rains*", "JetBrainsMono-Card-500.ttf", {"wght": 500}),
]


def find(pattern: str) -> Path:
    for folder in SEARCH:
        hits = sorted(p for p in folder.glob(pattern) if p.suffix in {".ttf", ".woff2"} and "Italic" not in p.name)
        if hits:
            return hits[0]
    sys.exit(f"No source font matching {pattern} in {', '.join(map(str, SEARCH))}")


OUT.mkdir(parents=True, exist_ok=True)
for pattern, name, axes in JOBS:
    src = find(pattern)
    font = TTFont(src)
    if "fvar" in font:
        present = {a.axisTag for a in font["fvar"].axes}
        font = instantiateVariableFont(font, {k: v for k, v in axes.items() if k in present})
    font.flavor = None
    font.save(OUT / name)
    print(f"{src.name} -> {name}")
shutil.copy(ROOT / "brand" / "fonts" / "OFL.txt", OUT / "OFL.txt")
```

Run: `uv run --with "fonttools>=4.67,<5" --with "brotli>=1.2,<2" python brand/tools/card_fonts.py`
Expected: four lines `... -> Fraunces-Card-500.ttf` and so on, and four TTFs in `brand/fonts/cards/`. Check that each source was a variable font or the right static weight (the script prints the source name); if M0's subset WOFF2 files are static instances at another weight, point `JOBS` at the matching file instead. Check that each TTF keeps its OFL licence text (copied as `OFL.txt`; if M0 vendored separate licences for Instrument Sans and JetBrains Mono, copy those too).

- [ ] **Step 2: Install the renderer**

Run: `pnpm --dir site add -D satori@~0.63.2 @resvg/resvg-js@~2.6.2`
Why: satori lays the card out from the template's rules, resvg turns its SVG into a PNG; both run only at build time in Node.

- [ ] **Step 3: Write the failing tests**

```html
<!-- site/tests/unit/fixtures/html-with-card.html: how Astro escapes the meta Seo.astro writes -->
<!doctype html><html><head><title>x</title><meta name="dins:card" content="{&quot;variant&quot;:&quot;A&quot;,&quot;label&quot;:&quot;Case study&quot;,&quot;title&quot;:&quot;Fish &amp; chips &lt;3 “quoted”&quot;,&quot;path&quot;:&quot;/work/passfx/&quot;}"><meta name="description" content="d"></head><body></body></html>
```

```ts
// site/tests/unit/og-spec.test.ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { extractCardSpec, stripCardMeta } from "../../src/og/spec";

const html = readFileSync(new URL("./fixtures/html-with-card.html", import.meta.url), "utf8");

describe("card meta", () => {
  it("reads the spec back with entities decoded", () => {
    expect(extractCardSpec(html)).toEqual({ variant: "A", label: "Case study", title: "Fish & chips <3 “quoted”", path: "/work/passfx/" });
  });
  it("returns null when a page has no card", () => {
    expect(extractCardSpec("<html><head></head></html>")).toBeNull();
  });
  it("rejects a malformed spec instead of drawing garbage", () => {
    expect(() => extractCardSpec('<meta name="dins:card" content="{&quot;variant&quot;:&quot;Z&quot;}">')).toThrow();
  });
  it("strips the meta from the shipped page and keeps the rest", () => {
    const out = stripCardMeta(html);
    expect(out).not.toContain("dins:card");
    expect(out).toContain('<meta name="description" content="d">');
  });
});
```

```ts
// site/tests/unit/og-card.test.ts
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { CARD_COLORS, renderCard, titleSize } from "../../src/og/card";
import { loadCardAssets } from "../../src/og/assets";

const pngSize = (b: Buffer) => ({ width: b.readUInt32BE(16), height: b.readUInt32BE(20) });

describe("titleSize", () => {
  it("uses the template sizes for normal titles", () => {
    expect(titleSize("A pipeline that tells you when it is wrong", "A")).toBe(78);
    expect(titleSize("Short", "C")).toBe(64);
    expect(titleSize("Hi, I’m Din.", "home")).toBe(104);
  });
  it("steps down for long titles so they fit in three lines", () => {
    expect(titleSize("x".repeat(70), "A")).toBe(64);
    expect(titleSize("x".repeat(110), "A")).toBe(52);
    expect(titleSize("x".repeat(110), "C")).toBe(44);
  });
});

describe("colors", () => {
  it("match the light tokens", () => {
    const css = readFileSync(new URL("../../../brand/tokens/tokens.css", import.meta.url), "utf8");
    const root = css.slice(0, css.indexOf("@media"));
    for (const [token, hex] of Object.entries(CARD_COLORS)) {
      expect(root).toContain(`--color-${token}: ${hex};`);
    }
  });
});

describe("renderCard", () => {
  it.each(["A", "C", "home"] as const)("draws a 1200 x 630 PNG for variant %s", async (variant) => {
    const assets = await loadCardAssets();
    const png = await renderCard({ variant, label: "Case study", title: "Fish & chips “quoted” é", subtitle: "Role line", path: "/work/passfx/" }, assets);
    expect(png.subarray(1, 4).toString()).toBe("PNG");
    expect(pngSize(png)).toEqual({ width: 1200, height: 630 });
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/og-spec.test.ts tests/unit/og-card.test.ts`
Expected: FAIL, modules missing.

- [ ] **Step 4: Write the card code**

```ts
// site/src/og/spec.ts: the card spec a page writes into its head and the build reads back.
import { z } from "astro/zod";

export const cardSpecSchema = z.object({
  variant: z.enum(["A", "C", "home"]),
  label: z.string().min(1),
  title: z.string().min(1),
  subtitle: z.string().optional(),
  path: z.string().startsWith("/"),
});
export type CardSpec = z.infer<typeof cardSpecSchema>;

const META = /<meta name="dins:card" content="([^"]*)"\s*\/?>/;

const decode = (s: string) =>
  s.replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");

export function extractCardSpec(html: string): CardSpec | null {
  const m = html.match(META);
  return m ? cardSpecSchema.parse(JSON.parse(decode(m[1]))) : null;
}

export function stripCardMeta(html: string): string {
  return html.replace(META, "");
}
```

```ts
// site/src/og/assets.ts: fonts and marks for the cards, read from brand/ at build time (Node only).
import { readFile } from "node:fs/promises";

const BRAND = new URL("../../../brand/", import.meta.url);
const read = (p: string) => readFile(new URL(p, BRAND));

export type CardFont = { name: string; data: Buffer; weight: 400 | 500; style: "normal" };
export type CardMark = { src: string; ratio: number };
export type CardAssets = { fonts: CardFont[]; lockup: CardMark; seal: CardMark };

async function mark(path: string): Promise<CardMark> {
  const svg = (await read(path)).toString("utf8");
  const [, , w, h] = (svg.match(/viewBox="([^"]+)"/)?.[1] ?? "0 0 1 1").split(/\s+/).map(Number);
  return { src: `data:image/svg+xml;base64,${Buffer.from(svg).toString("base64")}`, ratio: w / h };
}

export async function loadCardAssets(): Promise<CardAssets> {
  return {
    fonts: [
      { name: "Fraunces", data: await read("fonts/cards/Fraunces-Card-500.ttf"), weight: 500, style: "normal" },
      { name: "Instrument Sans", data: await read("fonts/cards/InstrumentSans-Card-400.ttf"), weight: 400, style: "normal" },
      { name: "JetBrains Mono", data: await read("fonts/cards/JetBrainsMono-Card-400.ttf"), weight: 400, style: "normal" },
      { name: "JetBrains Mono", data: await read("fonts/cards/JetBrainsMono-Card-500.ttf"), weight: 500, style: "normal" },
    ],
    lockup: await mark("logo/lockup-light.svg"),
    seal: await mark("logo/seal-dark.svg"),
  };
}
```

```ts
// site/src/og/card.ts: social cards A (Paper), C (Paper with Ottie) and the home card,
// laid out from brand/tools/social-cards.template.html (BRAND.md, locked 2026-10-19).
import satori from "satori";
import { Resvg } from "@resvg/resvg-js";
import { cardUrlText } from "../lib/seo";
import type { CardAssets } from "./assets";
import type { CardSpec } from "./spec";

// The light palette from brand/tokens/tokens.css (a unit test keeps these in sync).
export const CARD_COLORS = { paper: "#F4F1EA", ink: "#12181C", muted: "#4A555C", accent: "#0F6B6B" } as const;
const PANEL = CARD_COLORS.ink;

type Node = { type: string; props: Record<string, unknown> & { children?: Node | Node[] | string } };
const h = (type: string, style: Record<string, unknown>, ...children: (Node | string)[]): Node => ({
  type,
  props: { style, children: children.length === 1 ? children[0] : children },
});
const img = (src: string, width: number, height: number): Node => ({ type: "img", props: { src, width, height } });

export function titleSize(title: string, variant: CardSpec["variant"]): number {
  if (variant === "home") return 104;
  const [normal, mid, small] = variant === "C" ? [64, 54, 44] : [78, 64, 52];
  if (title.length <= 60) return normal;
  return title.length <= 90 ? mid : small;
}

const label = (text: string) =>
  h("div", { fontFamily: "JetBrains Mono", fontWeight: 500, fontSize: 22, letterSpacing: 1.76, textTransform: "uppercase", color: CARD_COLORS.accent }, text);
const url = (path: string) => h("div", { fontFamily: "JetBrains Mono", fontWeight: 400, fontSize: 24, color: CARD_COLORS.muted }, cardUrlText(path));
const title = (text: string, size: number, maxWidth: number) =>
  h("div", { display: "block", fontFamily: "Fraunces", fontWeight: 500, fontSize: size, letterSpacing: -0.02 * size, lineHeight: 1.04, maxWidth, lineClamp: 3 }, text);

export function cardElement(spec: CardSpec, assets: CardAssets): Node {
  const lockup = img(assets.lockup.src, Math.round(46 * assets.lockup.ratio), 46);
  if (spec.variant === "C") {
    return h("div", { display: "flex", width: 1200, height: 630, background: CARD_COLORS.paper, color: CARD_COLORS.ink },
      h("div", { display: "flex", flexDirection: "column", justifyContent: "space-between", flex: 1, padding: "72px 64px 72px 80px" },
        lockup,
        h("div", { display: "flex", flexDirection: "column", gap: 22 }, label(spec.label), title(spec.title, titleSize(spec.title, "C"), 640)),
        url(spec.path)),
      h("div", { display: "flex", width: 420, alignItems: "center", justifyContent: "center", background: PANEL },
        img(assets.seal.src, 300, Math.round(300 / assets.seal.ratio))));
  }
  const body = spec.variant === "home"
    ? h("div", { display: "flex", flexDirection: "column" },
        title(spec.title, 104, 1040),
        ...(spec.subtitle ? [h("div", { fontFamily: "Instrument Sans", fontSize: 34, lineHeight: 1.4, color: CARD_COLORS.muted, marginTop: 18 }, spec.subtitle)] : []))
    : title(spec.title, titleSize(spec.title, "A"), 980);
  return h("div", { display: "flex", flexDirection: "column", justifyContent: "space-between", width: 1200, height: 630, padding: "72px 80px", background: CARD_COLORS.paper, color: CARD_COLORS.ink },
    h("div", { display: "flex", justifyContent: "space-between", alignItems: "center" }, lockup, label(spec.label)),
    body,
    url(spec.path));
}

export async function renderCard(spec: CardSpec, assets: CardAssets): Promise<Buffer> {
  // satori's element type is React-like; our plain nodes match its runtime shape.
  const svg = await satori(cardElement(spec, assets) as unknown as Parameters<typeof satori>[0], { width: 1200, height: 630, fonts: assets.fonts });
  return new Resvg(svg, { fitTo: { mode: "width", value: 1200 } }).render().asPng();
}
```

```ts
// site/src/integrations/social-cards.ts: after the build, draw one card per page that asked for one.
import type { AstroIntegration } from "astro";
import { mkdir, readdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { cardPath } from "../lib/seo";
import { loadCardAssets } from "../og/assets";
import { renderCard } from "../og/card";
import { extractCardSpec, stripCardMeta } from "../og/spec";

export default function socialCards(): AstroIntegration {
  return {
    name: "dins-social-cards",
    hooks: {
      "astro:build:done": async ({ dir, logger }) => {
        const out = fileURLToPath(dir);
        const files = (await readdir(out, { recursive: true })).filter((f) => f.endsWith(".html"));
        // The served root is the folder of the shallowest index.html (dist/ or dist/client/).
        const rootIndex = files.filter((f) => path.basename(f) === "index.html").sort((a, b) => a.split(path.sep).length - b.split(path.sep).length)[0];
        const root = path.join(out, path.dirname(rootIndex ?? "index.html"));
        const assets = await loadCardAssets();
        let count = 0;
        for (const rel of files) {
          const file = path.join(out, rel);
          const html = await readFile(file, "utf8");
          const spec = extractCardSpec(html);
          if (!spec) continue;
          const png = path.join(root, cardPath(spec.path));
          await mkdir(path.dirname(png), { recursive: true });
          await writeFile(png, await renderCard(spec, assets));
          await writeFile(file, stripCardMeta(html));
          count++;
        }
        logger.info(`${count} social cards written`);
      },
    },
  };
}
```

In `site/astro.config.mjs`, add `import socialCards from "./src/integrations/social-cards.ts";` and append `socialCards()` to `integrations`.

- [ ] **Step 5: Run the unit tests**

Run: `pnpm --dir site exec vitest run tests/unit/og-spec.test.ts tests/unit/og-card.test.ts`
Expected: PASS.

- [ ] **Step 6: Add the e2e check and build**

Append to `site/tests/e2e/seo.spec.ts`:

```ts
test("every page's og:image is a real PNG and the card meta is gone", async ({ page, request }) => {
  for (const path of ROUTES()) {
    await page.goto(path);
    const image = await page.locator('meta[property="og:image"]').getAttribute("content");
    expect(image).toMatch(/^https:\/\/dins\.dev\/og\/.+\.png$/);
    const res = await request.get(new URL(image!).pathname);
    expect(res.status(), image!).toBe(200);
    expect(res.headers()["content-type"]).toContain("image/png");
    await expect(page.locator('meta[name="dins:card"]')).toHaveCount(0);
  }
});
```

Run: `DINS_SHOW_DRAFTS=1 pnpm --dir site build`
Expected: the log ends with "N social cards written" where N equals the number of routes with a card (every route except the 404, sent and error pages).

Run: `pnpm --dir site exec playwright test --project=chromium tests/e2e/seo.spec.ts`
Expected: PASS.

- [ ] **Step 7: Din checks the cards**

Open `site/dist/client/og/index.png` (or `site/dist/og/` if the build has no `client` folder), `og/work/passfx.png` and `og/writing/sample-devlog.png` side by side with `brand/social/social-cards.html`. Din confirms they match cards A, home and C. Record the result in the PR.

- [ ] **Step 8: Commit**

```bash
git add brand/tools/card_fonts.py brand/fonts/cards site/src/og site/src/integrations site/astro.config.mjs site/package.json pnpm-lock.yaml site/tests
git commit -m "feat(site): social cards A, C and home drawn at build time"
```

## Task 18: The drafts guard

**Files:**
- Create: `site/scripts/check-drafts.ts`
- Modify: `site/package.json` (script `check:drafts`), `check.sh`
- Test: `site/tests/unit/check-drafts.test.ts`

**Interfaces:**
- Consumes: the `data-draft` marker (Task 8), the content folders.
- Produces: `findDraftLeaks(input: { files: Map<string, string>; draftRoutes: string[] }): string[]` (exported from the script for the test), the `pnpm --dir site check:drafts` command, and its place in `check.sh`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/check-drafts.test.ts
import { describe, expect, it } from "vitest";
import { findDraftLeaks } from "../../scripts/check-drafts";

const files = (entries: Record<string, string>) => new Map(Object.entries(entries));

describe("findDraftLeaks", () => {
  it("passes a clean production build with empty states", () => {
    const leaks = findDraftLeaks({
      files: files({ "index.html": "<p data-empty>", "work/index.html": "<p data-empty>", "sitemap.xml": "<loc>https://dins.dev/</loc>" }),
      draftRoutes: ["/work/passfx/"],
    });
    expect(leaks).toEqual([]);
  });
  it("catches a data-draft marker", () => {
    expect(findDraftLeaks({ files: files({ "index.html": '<div data-draft="">' }), draftRoutes: [] })).toEqual(["index.html: contains data-draft"]);
  });
  it("catches a built draft page, its card and its mentions", () => {
    const leaks = findDraftLeaks({
      files: files({ "work/passfx/index.html": "x", "og/work/passfx.png": "x", "sitemap.xml": "https://dins.dev/work/passfx/", "llms.txt": "/work/passfx/" }),
      draftRoutes: ["/work/passfx/"],
    });
    expect(leaks).toEqual(expect.arrayContaining([
      "work/passfx/index.html: draft page was built",
      "og/work/passfx.png: draft card was built",
      "sitemap.xml: mentions /work/passfx/",
      "llms.txt: mentions /work/passfx/",
    ]));
  });
  it("catches any library page", () => {
    expect(findDraftLeaks({ files: files({ "library/x/index.html": "x" }), draftRoutes: [] })).toEqual(["library/x/index.html: library entries are never pages"]);
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/check-drafts.test.ts`
Expected: FAIL, module missing.

- [ ] **Step 2: Write the script**

```ts
// site/scripts/check-drafts.ts
// Drafts never render in production (PRD 2). Run after a production build:
//   env -u DINS_SHOW_DRAFTS pnpm --dir site build && pnpm --dir site check:drafts
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export function findDraftLeaks({ files, draftRoutes }: { files: Map<string, string>; draftRoutes: string[] }): string[] {
  const leaks: string[] = [];
  for (const [file, text] of files) {
    if (/^library\//.test(file)) leaks.push(`${file}: library entries are never pages`);
    if (/\.(html|xml|txt)$/.test(file) && text.includes("data-draft")) leaks.push(`${file}: contains data-draft`);
  }
  for (const route of draftRoutes) {
    const trimmed = route.replace(/^\/|\/$/g, "");
    if (files.has(`${trimmed}/index.html`)) leaks.push(`${trimmed}/index.html: draft page was built`);
    if (files.has(`og/${trimmed}.png`)) leaks.push(`og/${trimmed}.png: draft card was built`);
    for (const feed of ["sitemap.xml", "rss.xml", "llms.txt"]) {
      if (files.get(feed)?.includes(route)) leaks.push(`${feed}: mentions ${route}`);
    }
  }
  return leaks;
}

function draftRoutes(content: string): string[] {
  const out: string[] = [];
  for (const [dir, base] of [["projects", "work"], ["writing", "writing"]]) {
    for (const f of readdirSync(path.join(content, dir))) {
      if (!f.endsWith(".mdx") || f.startsWith("_")) continue;
      if (/^status:\s*draft\s*$/m.test(readFileSync(path.join(content, dir, f), "utf8"))) out.push(`/${base}/${f.slice(0, -4)}/`);
    }
  }
  return out;
}

function walk(root: string, rel = ""): [string, string][] {
  return readdirSync(path.join(root, rel)).flatMap((name) => {
    const r = rel ? `${rel}/${name}` : name;
    const full = path.join(root, r);
    if (statSync(full).isDirectory()) return walk(root, r);
    return [[r, /\.(html|xml|txt)$/.test(name) ? readFileSync(full, "utf8") : ""] as [string, string]];
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const site = fileURLToPath(new URL("..", import.meta.url));
  const dist = existsSync(path.join(site, "dist/client")) ? path.join(site, "dist/client") : path.join(site, "dist");
  const html = readFileSync(path.join(dist, "index.html"), "utf8");
  if (html.includes('name="dins-deploy" content="preview"')) {
    console.error("check:drafts needs a production build (DINS_SHOW_DRAFTS unset)");
    process.exit(2);
  }
  const files = new Map(walk(dist));
  const leaks = findDraftLeaks({ files, draftRoutes: draftRoutes(path.join(site, "src/content")) });
  // Before launch every collection is empty in production: the lists must show content or a calm empty state.
  for (const page of ["index.html", "work/index.html", "writing/index.html"]) {
    const text = files.get(page) ?? "";
    if (!text.includes("<article") && !text.includes("data-empty")) leaks.push(`${page}: neither content nor an empty state`);
  }
  for (const l of leaks) console.error(`draft leak: ${l}`);
  const required = ["index.html", "work/index.html", "writing/index.html", "about/index.html", "contact/index.html", "privacy/index.html", "404.html", "sitemap.xml", "rss.xml", "robots.txt", "llms.txt", ".well-known/security.txt"];
  const missing = required.filter((f) => !existsSync(path.join(dist, f)));
  for (const m of missing) console.error(`missing from the production build: ${m}`);
  console.log(leaks.length + missing.length ? "Drafts guard FAILED" : "Drafts guard passed: no drafts in the production build");
  process.exit(leaks.length + missing.length ? 1 : 0);
}
```

Note: the `dins-deploy` meta (M0) only says `preview` on preview deploys. A local `DINS_SHOW_DRAFTS=1` build reports `local` and is caught instead by the `data-draft` scan (every sample is a draft), which is the case `check.sh` must never miss.

Add to `site/package.json` scripts: `"check:drafts": "node scripts/check-drafts.ts"`.

In `check.sh`, after M0's build step (replace it if M0 builds without clearing the variable):

```bash
echo "== production build and drafts guard"
env -u DINS_SHOW_DRAFTS pnpm --dir site build
pnpm --dir site check:drafts
```

- [ ] **Step 3: Run the test and the guard**

Run: `pnpm --dir site exec vitest run tests/unit/check-drafts.test.ts`
Expected: PASS.

Run: `env -u DINS_SHOW_DRAFTS pnpm --dir site build && pnpm --dir site check:drafts`
Expected: "Drafts guard passed: no drafts in the production build". The production `/work/` shows "Projects are on their way."

Run: `DINS_SHOW_DRAFTS=1 pnpm --dir site build && pnpm --dir site check:drafts`
Expected: FAIL with `draft leak:` lines for the samples (proves the guard bites). Rebuild without the variable afterwards.

Run: `./check.sh`
Expected: PASS, under 2 minutes (note the time in the PR).

- [ ] **Step 4: Commit**

```bash
git add site/scripts/check-drafts.ts site/tests/unit/check-drafts.test.ts site/package.json check.sh
git commit -m "feat(site): drafts guard over the production build in check.sh"
```

## Task 19: No-JavaScript and reduced-motion baselines

**Files:**
- Create: `site/tests/e2e/no-js.spec.ts`, `site/tests/e2e/reduced-motion.spec.ts`

**Interfaces:**
- Consumes: `ROUTES` (Task 8), every page.
- Produces: the two baselines M4 must keep green while it adds motion.

- [ ] **Step 1: Write the specs**

```ts
// site/tests/e2e/no-js.spec.ts (project no-js: JavaScript disabled)
import { expect, test } from "@playwright/test";
import { DRAFTS_SHOWN, ROUTES } from "./routes";

for (const path of ROUTES()) {
  test(`${path} reads without JavaScript`, async ({ page }) => {
    await page.goto(path);
    await expect(page.locator("html")).toHaveClass(/no-js/);
    await expect(page.locator("h1")).toBeVisible();
    const text = await page.locator("main").innerText();
    expect(text.trim().length).toBeGreaterThan(40);
    await expect(page.getByRole("navigation", { name: "Main" }).getByRole("link")).toHaveCount(4);
    await expect(page.locator("[data-theme-toggle]")).toBeHidden();
  });
}

test("suggested answers open without JavaScript", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "no published suggested answers yet");
  await page.goto("/");
  const first = page.locator("#suggested details").first();
  await first.locator("summary").click();
  await expect(first.locator(".answer")).toBeVisible();
});

test("without JavaScript the contact form says to email instead", async ({ page }) => {
  await page.goto("/contact/");
  await expect(page.locator("form[data-letter-form]")).toHaveAttribute("action", "/api/contact");
  const note = page.locator("form[data-letter-form] .noscript");
  await expect(note).toBeVisible();
  await expect(note.getByRole("link", { name: "din@dins.dev" })).toHaveAttribute("href", "mailto:din@dins.dev");
});

test("work filters navigate without JavaScript", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs projects");
  await page.goto("/work/");
  await page.getByRole("navigation", { name: "Filter projects" }).getByRole("link", { name: "ML" }).click();
  await expect(page).toHaveURL(/\/work\/kind\/ml\/$/);
});
```

```ts
// site/tests/e2e/reduced-motion.spec.ts (project reduced-motion)
import { expect, test } from "@playwright/test";
import { ROUTES } from "./routes";

for (const path of ROUTES()) {
  test(`${path} has no motion when reduced motion is asked for`, async ({ page }) => {
    await page.goto(path);
    const moving = await page.evaluate(() =>
      [...document.querySelectorAll("*")].filter((el) => {
        const s = getComputedStyle(el);
        const ms = (v: string) => Math.max(...v.split(",").map((x) => parseFloat(x) * (x.trim().endsWith("ms") ? 1 : 1000)));
        return ms(s.transitionDuration) > 1 || (s.animationName !== "none" && ms(s.animationDuration) > 1);
      }).length,
    );
    expect(moving).toBe(0);
    expect(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior)).toBe("auto");
  });
}
```

- [ ] **Step 2: Run them**

Run: `pnpm --dir site exec playwright test --project=no-js --project=reduced-motion`
Expected: PASS on every route. If a route fails, fix the page (never the test): content hidden behind `.js`, a control that needs JavaScript without a fallback, or a transition outside the `no-preference` query.

- [ ] **Step 3: Commit**

```bash
git add site/tests/e2e/no-js.spec.ts site/tests/e2e/reduced-motion.spec.ts
git commit -m "test(site): no-JavaScript and reduced-motion baselines on every route"
```

## Task 20: Lighthouse accessibility and SEO gates

**Files:**
- Create: `site/lighthouserc.cjs`
- Modify: `site/package.json` (dev dep and `lhci` script), `.github/workflows/ci.yml`, `.gitignore` (`site/.lighthouseci/`)

**Interfaces:**
- Consumes: the built site with drafts shown (indexable), the route list.
- Produces: `pnpm --dir site lhci` and a CI step after e2e.

- [ ] **Step 1: Install and configure**

Run: `pnpm --dir site add -D @lhci/cli@~0.15.1`
Why: Lighthouse accessibility and SEO 100 are M1 gates.

```js
// site/lighthouserc.cjs
// Accessibility and SEO are gates at 100; performance is a warning until the post-launch pass (Din, 2026-10-21).
// Local and CI runs use the DINS_SHOW_DRAFTS=1 build (indexable, never deployed); M5 sets BASE_URL for production.
const base = process.env.BASE_URL ?? "http://127.0.0.1:8787";
const paths = ["/", "/work/", "/work/passfx/", "/writing/", "/writing/sample-case-study/", "/about/", "/contact/", "/privacy/"];

module.exports = {
  ci: {
    collect: {
      url: paths.map((p) => new URL(p, base).href),
      numberOfRuns: 1,
      ...(process.env.BASE_URL ? {} : { startServerCommand: "pnpm serve", startServerReadyPattern: "Ready on" }),
      settings: { preset: "desktop" },
    },
    assert: {
      assertions: {
        "categories:accessibility": ["error", { minScore: 1 }],
        "categories:seo": ["error", { minScore: 1 }],
        "categories:performance": ["warn", { minScore: 0.9 }],
      },
    },
    upload: { target: "filesystem", outputDir: ".lighthouseci" },
  },
};
```

When `BASE_URL` points at production, the sample paths do not exist; M5 replaces them with real ones (noted in Doc updates).

Add `"lhci": "lhci autorun --config=lighthouserc.cjs"` to `site/package.json` and `site/.lighthouseci/` to `.gitignore`.

- [ ] **Step 2: Run it**

Run: `DINS_SHOW_DRAFTS=1 pnpm --dir site build && pnpm --dir site lhci`
Expected: all assertions pass for accessibility and SEO on all eight URLs; performance may warn. If SEO fails on "Links do not have descriptive text" or accessibility on contrast, fix the page and rerun.

- [ ] **Step 3: Add the CI step**

In `.github/workflows/ci.yml`, in M0's e2e job after Playwright (which already built with `DINS_SHOW_DRAFTS=1`):

```yaml
      - name: Lighthouse (accessibility and SEO gates)
        run: pnpm --dir site lhci
        env:
          DINS_SHOW_DRAFTS: "1"
      - name: Lighthouse reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: lighthouse
          path: site/.lighthouseci
```

If M0 pinned actions to commit SHAs, pin `upload-artifact` the same way.

- [ ] **Step 4: Commit**

```bash
git add site/lighthouserc.cjs site/package.json pnpm-lock.yaml .github/workflows/ci.yml .gitignore
git commit -m "ci(site): Lighthouse accessibility and SEO gates at 100"
```

## Task 21: Full verification and the preview for Din

**Files:**
- Modify: none (fixes only if something fails, each in its own commit)

- [ ] **Step 1: Run everything locally**

Run: `./check.sh`
Expected: PASS (format, lint, `astro check`, unit tests, production build, drafts guard), under 2 minutes.

Run: `pnpm --dir site test:e2e`
Expected: PASS across the light, dark, no-js, reduced-motion and phone projects.

Run: `DINS_SHOW_DRAFTS=1 pnpm --dir site build && pnpm --dir site lhci`
Expected: accessibility 100 and SEO 100 on every URL.

Run: `pnpm --dir site launch:blockers`
Expected: exit 1 listing Din's open items (D1 to D7). This is expected in M1 and goes in the PR description.

- [ ] **Step 2: Check the M1 verification list from PLAN.md**

| PLAN.md M1 verify item | Evidence |
|---|---|
| Playwright visits every route in light and dark | `pages.spec.ts` in the light and dark projects |
| axe zero violations | `expectNoAxeViolations` on every route, both themes |
| Lighthouse accessibility and SEO 100 | `pnpm --dir site lhci` output and the CI artifact |
| Drafts absent from a production build | `check:drafts` in `check.sh` |
| Readable with JavaScript off | `no-js.spec.ts` |

- [ ] **Step 3: Hand the preview to Din**

Ask Din before pushing `feat/m1-pages` (pushing and PRs need Din's go). Once pushed, Workers Builds deploys a preview with drafts shown and `noindex`. Din checks, in light and dark and on a phone: the home page against the sketch, `/work/` and its filters, a case study, `/writing/` and a post, `/about/`, `/contact/`, `/privacy/`, the 404, and the three social cards. Din's verdict is recorded in the ledger; only Din sets Accepted.

---

## Open questions for Din

### Decided

- **Contact without JavaScript versus Turnstile.** Decided (Din, 2026-10-21, through M4's decision 1). The question: PRD 6 says the contact form still submits with JavaScript off, but Turnstile (PRD 5) needs JavaScript. The first version of this plan recommended accepting token-less posts behind the honeypot and a stricter rate limit. Din chose instead: without JavaScript there is no Turnstile token, so the post is never accepted. It lands on `/contact/not-sent/` with a `mailto:din@dins.dev` link, and the form shows a `<noscript>` note pointing to the same address. The honeypot stays as a cheap filter for scripted posts that do run JavaScript, and the "Or email din@dins.dev" line under the button stays for everyone. PRD 6's "the contact form still submits" needs the matching edit (see Doc updates).

### Open

1. **Previews show drafts.** The plan shows drafts (with a "Draft, hidden on dins.dev" badge) on Workers Builds preview deploys and marks those pages `noindex`, so Din can review sample and unpublished content before it ships. Production (`main`) never shows them, and a build that tries is refused. PRD 2 only says "never in production". Recommendation: keep previews showing drafts; the repo is public anyway, so a preview reveals nothing new.
2. **Work filters as static pages.** Filters are links to `/work/kind/<kind>/` pages (crawlable, no JavaScript, `aria-current`), shown only for kinds with projects. PRD 2 says "filterable" without saying how. This adds a route family to PRD 2. Alternative: one page with a small script. Recommendation: static pages.
3. **The `devlog` field.** PRD 2 lists both `kind: devlog` and a `devlog` flag (card C). The plan keeps the flag optional and defaults it to `kind === "devlog"`. Should the flag go, so there is one way to say it?
4. **Name in structured data.** "Din" or the full name (with "Din" as `alternateName`)? Ranking for Din's name depends on it (ledger, SEO and analytics). And should Person data carry a photo? The plan leaves out `image`, since the seal and avatar are Ottie, not Din.
5. **Theme toggle.** The sketch has one; the PRD does not mention it. The plan keeps a small one (system theme by default, choice saved in `localStorage` and listed on `/privacy`). Keep it for v1?
6. **Library samples.** M3 asked for `sample: true` entries without `approved_on`. The schema makes `approved_on` required for every non-sample entry, so the build fails on an unapproved entry (PRD 2's CI rule), and samples never reach the production index (M3). Is that the rule Din wants?

## Doc updates to apply on merge

- `docs/TASKS.md` row 2.11: status to Implemented when the build lands, Verified after the checks pass, with a link to this plan; add Din tasks D1 to D8 as rows (Done (Din) when each lands).
- `docs/site/PRD.md` section 2, routes: add `/work/kind/<kind>/` (if open question 2 is accepted), `/contact/sent/` and `/contact/not-sent/` (noindex, never in the sitemap; `/contact/not-sent/` carries a `mailto:din@dins.dev` link, because a post without JavaScript has no Turnstile token and is never accepted, Din 2026-10-21), and state that previews show drafts with `noindex` (if open question 1 is accepted). `sitemap.xml` is written by the site itself.
- `docs/site/PRD.md` section 6, failure modes: replace "the contact form still submits" with "without JavaScript the contact form points to email (a post has no Turnstile token and is not accepted)" (Din, 2026-10-21).
- `docs/site/PRD.md` section 2, content model: record the exact fields M1 added or pinned down: projects `capture` (16:10, checked at build), `captureAlt`, `demo` as `{ type, src }` with `src` a site path, `featured` 1 to 4 and unique, `repo` https only, and the reserved id `kind`; writing `motif` (`nodes`, `bars`, `lens`) and `devlog` defaulting from `kind`; library `audience` values (`admissions`, `recruiters`, `visitors`), `approved_on` nullable only with `sample: true`; suggested `order`, `generated_on`, `language`, `sources` as `{ label, href }`; contact message limit 4000 characters.
- `docs/site/PLAN.md` M1: note the drafts flags (M0's shared deploy plus `DINS_SHOW_DRAFTS`), the `check:drafts` step in `check.sh`, and `pnpm --dir site launch:blockers` (M5 can make it a launch gate).
- `docs/site/PLAN.md` M5: Lighthouse against production needs real case study and post paths in `site/lighthouserc.cjs` instead of the samples; M5's release scan can reuse `findDraftLeaks`.
- `docs/WORK_LEDGER.md`: an entry for the M1 decisions (previews show drafts, static filter pages, own sitemap instead of `@astrojs/sitemap`, social cards via satori with static font instances in `brand/fonts/cards/`, the contact contract with the sent and not-sent pages), with the verification results and Din's preview verdict.
- `brand/tools/` README or `docs/BRAND.md` "Social preview cards": mention `card_fonts.py` and that the site renders the cards with satori from the same rules as `social-cards.template.html`.
