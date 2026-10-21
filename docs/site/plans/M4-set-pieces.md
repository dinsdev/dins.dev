# M4 Set pieces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the five home page set pieces (lens and letter field, windows, paper, studio, letter) on top of the plain M1 pages, each behind a release flag, each with a calm version, each approved by Din in a preview before the next one starts, plus the `/api/contact` endpoint the letter posts to.

**Architecture:** Every set piece is an Astro component whose server-rendered HTML is the calm version (real content, real links, a real form, readable without JavaScript). A tiny loader stub per piece checks the motion profile and the piece's release flag, waits until the section is about one viewport away, then dynamically imports a vanilla TypeScript enhancer that adds the motion with GSAP 3.15 and ScrollTrigger (or canvas for the letter field). The motion math lives in pure functions that are tested first; the enhancers only map that math onto `transform` and `opacity`. Pinning uses CSS `position: sticky` inside a tall section (ScrollTrigger only drives the timeline), so there is no pin spacer and no layout shift.

**Tech Stack:** Astro 7.4, @astrojs/cloudflare 14.4 (Workers with static assets), TypeScript 6.0, GSAP 3.15 with ScrollTrigger, Canvas 2D, Vitest 4.1 (unit and Workers projects set up by M0), Playwright 1.64 with @axe-core/playwright 4.14, Cloudflare Turnstile, the Email Service `send_email` binding, the Workers rate limiting binding.

**Spec:** `docs/site/PRD.md` (sections 2.2, 4, 6, 7, 8), `docs/site/PLAN.md` (M4 section, task 2.14 in `docs/TASKS.md`), the sketch `docs/design/sketches/home-sketch.html` (built from `home.template.html`, a reference for layout and motion, not final design), `docs/BRAND.md` (locked), the 2026-10-21 entries in `docs/WORK_LEDGER.md`.

## Global Constraints

- Animate only `transform`, `opacity` and canvas pixels. No animated `filter`, `width`, `height`, `top`, `left`, `margin`, `clip-path`, `box-shadow` or `grid-template-rows` (PRD section 6). The sketch's blur effects are replaced (see "Decisions" below).
- 60 fps and no main-thread task over 50 ms through every set piece on a 2020 laptop and a mid-range phone (PRD section 6).
- At most 100 KB gzipped of first-party JavaScript on the home page before interaction, a CI gate (PRD sections 6 and 7). GSAP never ships in the initial module graph.
- Each set piece's JavaScript loads only when the section nears the viewport (about one viewport ahead).
- Save-Data or low-memory devices (`navigator.deviceMemory <= 2`) get no lens intro and the calm version of every piece (PRD section 6).
- Reduced motion gets the calm version of every piece: no lens intro, the stage as a plain list, the studio already on the screen, the letter as a plain form (PRD section 6).
- No layout shift: the calm layout is what first paints; the full layout is switched on only while the section is still below the viewport.
- Full keyboard access, a visible teal focus ring, no focus traps in pinned sections, WCAG 2.2 AA, axe at zero violations (PRD section 6).
- Any looping motion that runs on its own longer than 5 seconds can be paused or stops by itself (WCAG 2.2.2).
- Readable and usable with JavaScript off: every piece is plain HTML, and the contact form still submits (PRD section 6).
- Placeholders never ship: a section with no published content is not rendered (PRD section 2, content model).
- Brand: tokens from `brand/tokens/tokens.css` only (no new colors), the lens and wordmark are never stretched, rotated, recolored or given effects, amber is never text on light, teal is the one accent, calm dark mode with no glow (`docs/BRAND.md`).
- Copy: no em dashes, no en dashes as separators, no buzzwords; Din's voice is "I"; Ottie talks about Din; refer to Din by name in docs and comments.
- Contact privacy: messages are emailed, never stored or logged (PRD section 6). Nothing personal (Din's inbox) in `wrangler.jsonc`; this repo is public.
- Versions: GSAP pinned `~3.15.0` (checked on npm 2026-10-21: 3.15.0, standard no-charge license). Everything else follows M0's pins.
- Set pieces not approved by December 1 ship as their calm version (PRD section 8). The release flags make this automatic.

## Review Focus

These inputs are implied by the spec but easy to miss; each has a test in the task named.

1. A keyboard user tabbing through the pinned stage reaches every project link and leaves the section normally, and the focused link is visible (Task 13, `setpieces-keyboard.spec.ts`).
2. A visitor who jumps past a set piece (nav link to `#contact`) before its JavaScript arrives sees no content jump; the piece stays calm for that page view (Task 3 `canEnhance`, Task 13 e2e "jumping past the stage").
3. The home page with 0 or 1 published projects or 0 to 2 published posts renders no empty stage or empty paper section and no placeholder (Tasks 13 and 15).
4. A contact submission with a filled honeypot, a missing Turnstile token (JavaScript off), a cross-origin `Origin`, a 20 KB body or a CR/LF in the name is handled without sending mail, and nothing the visitor typed ever reaches the logs (Task 6).
5. Turning on reduced motion while the page is open switches every running piece to calm without a reload and without leftover transforms (Task 1 `onMotionChange`, Task 13 e2e "turning on reduced motion live"; the studio and paper use the same `gsap.matchMedia` revert).

## Decisions taken in this plan (Din can veto in review)

- **Sticky instead of ScrollTrigger `pin`.** The sketch's CSS sticky pinning is kept; ScrollTrigger maps scroll to a timeline with `scrub`. A `pin` would insert a pin spacer when the JavaScript arrives, which is a layout shift, and reparents the section.
- **Blur replaced.** The sketch blurs the page during the intro, the windows out of focus, the captions and the unhovered paper cards. `filter: blur` is not on the PRD's allowed list and is expensive on phones. Depth is shown with opacity, scale and a darker hairline instead. Din judges the look in the preview.
- **Astro components plus vanilla TypeScript enhancers, no Svelte islands for the set pieces.** The content is static and already in the HTML; a Svelte island would ship the content twice (HTML plus serialized props) and add hydration work. The letter is a real `<form>` enhanced in place.
- **Release flags.** `site/src/lib/setpieces/flags.ts` holds one release value per piece: `calm` (calm everywhere), `preview` (full in local and preview builds, calm in production) or `full`. A piece moves to `preview` when its work starts and to `full` only when Din approves it (recorded in the ledger). An unknown deploy environment counts as production, so a misconfigured build never ships unapproved motion.
- **`/api/contact` and the plain letter form come first,** right after the shared foundation, because contact delivery is an acceptance criterion (PRD section 7, item 7) and does not need a visual gate. The folding animation stays the fifth gate.
- **Lens intro plays once per browser session** (`sessionStorage`, wrapped in try and catch), not on every load, and any key, wheel, touch or click ends it at once.
- **Studio terminal "typing" uses transform only:** the full text is in the DOM from the start (screen readers read all of it), and a cover strip per line slides right in `ch` steps to reveal the characters. The laptop is built at its final, zoomed-in size and scaled down at the start, so the text stays sharp when the camera arrives.
- **Stage snap is off.** Each project has a dwell zone in the timeline (it holds still for 12 percent of its segment) instead of scroll snapping, which tends to fight trackpads and keyboards. Din can ask for snap in the preview.

## Assumes

From M0 (Foundation):
- `site/` scaffold with `pnpm --dir site dev|build|test|test:e2e|check`, `./check.sh`, Vitest projects for `tests/unit` and `tests/worker` (whether through `@cloudflare/vitest-pool-workers` or the renamed `@cloudflare/vitest-plugin`; Task 6 tests the handler directly with a fake env, so it runs under either), and a Playwright config whose `webServer` serves the built site with Wrangler locally and honors `BASE_URL`.
- A build-time variable `PUBLIC_DEPLOY_ENV` with values `local`, `preview` or `production`. If M0 names it differently, only `deployEnv()` in Task 2 changes.
- `wrangler.jsonc` with a top-level production Worker and an `env.preview` block (as the M5 notes describe), `.dev.vars` gitignored.
- `overflow-x: clip` (not `hidden`) on `html` and `body` in the global styles, because `overflow: hidden` on an ancestor breaks `position: sticky`. Task 11 adds it if missing.
- If M0 or M5 already ships `pnpm --dir site budget`, Task 4 extends it rather than creating it.

From M1 (Pages and content):
- `site/src/pages/index.astro` composes the home page from section components in this order: hero, work, writing, about, contact, footer, inside a base layout `site/src/layouts/BaseLayout.astro` with a `<slot name="head" />` (or equivalent) for head content.
- Collection fields: `projects` with `title`, `summary`, `kind`, `stack` (string array), `featured` (number or absent), `status`, and a stage capture `stage: { kind: "video" | "image", src, poster, alt }` (16:10). `writing` with `title`, `kind`, `date`, `summary`, `motif`, `status`. `library` entries with `approved_on` and `sample`.
- `/about` and `/contact` exist as plain pages; `/contact` has a plain form or none. M4 replaces the form with the `Letter` component and adds a screen header to `/about`.
- The sitemap integration accepts a filter (M4 adds `/contact/sent/` and `/contact/not-sent/` to the excluded list).

From M2 (Ottie):
- `site/src/ottie/events.ts` exporting `cueOttie(cue, opts?)` (cues include `"point"` and `"jump"`, `opts.instance` picks a mounted Ottie) and `prefetchOttie(state)`. The `Ottie` component can be mounted a second time with `instance="letter"`. If the names differ, only `site/src/lib/setpieces/letter/ottie-bridge.ts` changes.
- Ottie reads `<html data-motion>` (set by Task 1) to choose the still pose on Save-Data and low-memory devices.

From M3 (Ask Ottie):
- The Ask island dispatches `window` event `ask:state` with `detail.phase` in `idle | retrieving | streaming | done | dont-know | resting | error`. If M3 uses other names, only `site/src/lib/setpieces/field/ask-bridge.ts` changes.
- `site/src/lib/turnstile.ts` exporting `verifyTurnstile({ token, secret, remoteip?, action?, fetcher? }): Promise<{ ok: boolean; codes: string[] }>` and a browser loader `loadTurnstile(): Promise<Turnstile>` in `site/src/lib/turnstile-client.ts`. Task 6 creates them if absent, with these exact signatures.
- Secret `TURNSTILE_SECRET_KEY`, public var `PUBLIC_TURNSTILE_SITE_KEY` (names shared with the M3 and M5 notes).

From Din:
- Email Routing for `dins.dev` set up (task 0.8, about November 12), the `CONTACT_TO` secret set in preview and production, and approval of each gate in the preview.

## Repo map

```
site/
  src/
    lib/
      motion.ts                         resolveMotion, readMotionInput, currentMotion, onMotionChange      (Task 1)
      setpieces/
        flags.ts                        RELEASES, pieceEnabled, deployEnv                                    (Task 2)
        lazy.ts                         canEnhance, whenNear, bootPiece                                       (Task 3)
        gsap.ts                         one place that imports and registers gsap + ScrollTrigger            (Task 3)
        field/words.ts                  extractFieldWords                                                     (Task 8)
        field/model.ts                  mulberry32, layoutRows, createField, stepField, charAt, advanceSweep (Task 9)
        field/renderer.ts               canvas atlas renderer (browser)                                      (Task 10)
        field/ask-bridge.ts             listens to ask:state                                                  (Task 10)
        stage/pose.ts                   windowPose, activeIndex, progressForIndex, poseToTransform           (Task 12)
        stage/stage-enhance.ts          GSAP enhancer for the windows                                        (Task 13)
        paper/paper-enhance.ts          GSAP enhancer for the paper                                          (Task 15)
        studio/frame.ts                 studioFrame, revealCounts                                            (Task 17)
        studio/studio-enhance.ts        GSAP enhancer for the studio                                         (Task 18)
        letter/machine.ts               letterReducer, phaseClasses                                          (Task 20)
        letter/letter-enhance.ts        form enhancer (fetch, fold, Turnstile, Ottie)                        (Task 7 plain, Task 21 motion)
        letter/ottie-bridge.ts          cueOttie / prefetchOttie adapter                                      (Task 21)
      contact/parse.ts                  parseContact, REASONS, LIMITS                                         (Task 5)
      contact/handler.ts                handleContact                                                         (Task 6)
    components/home/
      MotionHead.astro                  inline head script: data-motion and data-intro                       (Tasks 1, 11)
      LensIntro.astro, lens-intro.css                                                                         (Task 11)
      LetterField.astro, letter-field.css                                                                     (Task 10)
      WorkStage.astro, work-stage.css                                                                         (Tasks 12 to 13)
      PaperStack.astro, PaperCard.astro, paper.css                                                            (Task 15)
      studio/Studio.astro, studio/StudioScreen.astro, studio/studio.css, studio/terminal.ts                  (Tasks 17 to 18)
      letter/Letter.astro, letter/letter.css                                                                  (Tasks 7, 21)
    pages/api/contact.ts                                                                                       (Task 6)
    pages/contact/sent.astro, pages/contact/not-sent.astro                                                     (Task 7)
    styles/view-transitions.css                                                                                (Task 18)
  scripts/budget.ts                                                                                            (Task 4)
  tests/unit/  motion, flags, lazy, budget, fps, field-words, field-model, pose, studio-frame, studio-tokens,
               terminal-lines, contact-parse, letter-machine, motion-properties                                (per task)
  tests/worker/contact.test.ts                                                                                 (Task 6)
  tests/e2e/   setpieces-loading, setpieces-keyboard, setpieces-calm, letter, shots (tag @shots), perf (tag @perf)
```

## How a gate works (applies to the gate steps in Tasks 11, 14, 16, 19 and 22)

1. Set the piece's release to `"preview"` in `flags.ts` when its first task starts.
2. Finish the piece's tasks with `./check.sh` green.
3. Run `pnpm --dir site test:e2e --grep @shots` and `pnpm --dir site test:e2e --grep @perf` (Task 4) and keep the PNGs and the perf JSON.
4. Ask Din for the go to push and open the PR (AGENTS.md: pushing and PRs need Din's go). Attach the screenshots and the perf summary to the PR description.
5. Din reviews the Workers Builds preview link on a laptop and a phone, full and calm (`?calm`).
6. On Din's approval, set the release to `"full"`, add a ledger entry quoting Din, and mark the TASKS row Accepted only if Din says so.
7. The next piece starts after the merge. If Din has not approved a piece by December 1, its release stays `"preview"`, which already means calm in production.

Branching: each gate is one squash-merged PR from `feat/m4-set-pieces`, recreated from `main` after each merge. The foundation and the contact endpoint (Tasks 1 to 7) are the first PR.

---

## Part A. Shared foundation

### Task 1: Motion profile and the `data-motion` head script

**Files:**
- Create: `site/src/lib/motion.ts`
- Create: `site/src/components/home/MotionHead.astro`
- Modify: `site/src/layouts/BaseLayout.astro` (render `<MotionHead />` first in `<head>`)
- Test: `site/tests/unit/motion.test.ts`

**Interfaces:**
- Produces: `type MotionMode = "full" | "calm"`; `interface MotionInput { reducedMotion: boolean; saveData: boolean; deviceMemory: number | undefined; search: string }`; `resolveMotion(input: MotionInput): MotionMode` (self-contained, no imports or closures, so its source can be inlined); `readMotionInput(w?: Window): MotionInput`; `currentMotion(): MotionMode` (reads `<html data-motion>`, anything but `"full"` is calm); `onMotionChange(fn: (m: MotionMode) => void): () => void` (re-resolves on `prefers-reduced-motion` changes, updates `data-motion`, calls `fn`, returns an unsubscribe).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/motion.test.ts
import { describe, expect, it } from "vitest";
import { resolveMotion, type MotionInput } from "../../src/lib/motion";

const base: MotionInput = { reducedMotion: false, saveData: false, deviceMemory: 8, search: "" };

describe("resolveMotion", () => {
  it("is full by default", () => {
    expect(resolveMotion(base)).toBe("full");
  });
  it("is calm under reduced motion", () => {
    expect(resolveMotion({ ...base, reducedMotion: true })).toBe("calm");
  });
  it("is calm with Save-Data", () => {
    expect(resolveMotion({ ...base, saveData: true })).toBe("calm");
  });
  it("is calm on low-memory devices (2 GB or less)", () => {
    expect(resolveMotion({ ...base, deviceMemory: 2 })).toBe("calm");
    expect(resolveMotion({ ...base, deviceMemory: 0.5 })).toBe("calm");
    expect(resolveMotion({ ...base, deviceMemory: 4 })).toBe("full");
  });
  it("treats an unknown deviceMemory (Safari, Firefox) as enough", () => {
    expect(resolveMotion({ ...base, deviceMemory: undefined })).toBe("full");
  });
  it("is calm when the URL asks for ?calm, in any position", () => {
    expect(resolveMotion({ ...base, search: "?calm" })).toBe("calm");
    expect(resolveMotion({ ...base, search: "?a=1&calm=1" })).toBe("calm");
    expect(resolveMotion({ ...base, search: "?calmness=1" })).toBe("full");
  });
  it("survives toString, so the head script can inline it", () => {
    const rebuilt = new Function(`return (${resolveMotion.toString()})`)() as typeof resolveMotion;
    expect(rebuilt(base)).toBe("full");
    expect(rebuilt({ ...base, search: "?calm" })).toBe("calm");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/motion.test.ts`
Expected: FAIL, cannot resolve `../../src/lib/motion`.

- [ ] **Step 3: Write minimal implementation**

```ts
// site/src/lib/motion.ts
export type MotionMode = "full" | "calm";

export interface MotionInput {
  reducedMotion: boolean;
  saveData: boolean;
  deviceMemory: number | undefined;
  search: string;
}

// Self-contained on purpose: MotionHead.astro inlines this function's source.
export function resolveMotion(input: MotionInput): MotionMode {
  if (/(?:^|[?&])calm(?:=[^&]*)?(?:&|$)/.test(input.search)) return "calm";
  if (input.reducedMotion || input.saveData) return "calm";
  if (typeof input.deviceMemory === "number" && input.deviceMemory <= 2) return "calm";
  return "full";
}

interface NavigatorHints {
  connection?: { saveData?: boolean };
  deviceMemory?: number;
}

export function readMotionInput(w: Window = window): MotionInput {
  const nav = w.navigator as Navigator & NavigatorHints;
  return {
    reducedMotion: w.matchMedia("(prefers-reduced-motion: reduce)").matches,
    saveData: Boolean(nav.connection?.saveData),
    deviceMemory: nav.deviceMemory,
    search: w.location.search,
  };
}

export function currentMotion(): MotionMode {
  return document.documentElement.dataset.motion === "full" ? "full" : "calm";
}

export function onMotionChange(fn: (m: MotionMode) => void): () => void {
  const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
  const update = () => {
    const mode = resolveMotion(readMotionInput());
    document.documentElement.dataset.motion = mode;
    fn(mode);
  };
  mq.addEventListener("change", update);
  return () => mq.removeEventListener("change", update);
}
```

```astro
---
// site/src/components/home/MotionHead.astro
// Runs before first paint so CSS can pick the full or calm layout without a shift.
import { resolveMotion } from "../../lib/motion";
const src = `(function(){try{var r=${resolveMotion.toString()};var n=navigator,c=n.connection;` +
  `var mode=r({reducedMotion:matchMedia("(prefers-reduced-motion: reduce)").matches,` +
  `saveData:!!(c&&c.saveData),deviceMemory:n.deviceMemory,search:location.search});` +
  `document.documentElement.dataset.motion=mode;}catch(e){}})();`;
---
<script is:inline set:html={src} />
```

In `BaseLayout.astro`, render `<MotionHead />` as the first child of `<head>`. Default CSS everywhere is the calm layout; the full layout is only ever selected with `:root[data-motion="full"]`, so JavaScript off means calm.

- [ ] **Step 4: Run test to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/motion.test.ts`
Expected: PASS (7 tests).

- [ ] **Step 5: Check the head script renders and the page still builds**

Run: `pnpm --dir site build && grep -rl 'dataset.motion' site/dist --include=index.html | head -3`
Expected: the built home page path (for example `site/dist/client/index.html`; the adapter decides the folder).

Note for M5: the inline script must be covered by the CSP (`security.csp` hashes or an explicit hash). Listed under "Doc updates".

- [ ] **Step 6: Commit**

```bash
git add site/src/lib/motion.ts site/src/components/home/MotionHead.astro site/src/layouts/BaseLayout.astro site/tests/unit/motion.test.ts
git commit -m "feat(site): motion profile and data-motion head script"
```

### Task 2: Release flags per set piece

**Files:**
- Create: `site/src/lib/setpieces/flags.ts`
- Test: `site/tests/unit/flags.test.ts`

**Interfaces:**
- Produces: `type SetPiece = "lens" | "windows" | "paper" | "studio" | "letter"`; `type Release = "calm" | "preview" | "full"`; `type DeployEnv = "local" | "preview" | "production"`; `RELEASES: Readonly<Record<SetPiece, Release>>`; `deployEnv(raw?: string): DeployEnv`; `pieceEnabled(piece: SetPiece, env?: DeployEnv, releases?: Record<SetPiece, Release>): boolean` (build-time only; used in component frontmatter).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/flags.test.ts
import { describe, expect, it } from "vitest";
import { deployEnv, pieceEnabled, RELEASES, type Release, type SetPiece } from "../../src/lib/setpieces/flags";

const all = (r: Release): Record<SetPiece, Release> =>
  ({ lens: r, windows: r, paper: r, studio: r, letter: r });

describe("deployEnv", () => {
  it("maps known values", () => {
    expect(deployEnv("local")).toBe("local");
    expect(deployEnv("preview")).toBe("preview");
    expect(deployEnv("production")).toBe("production");
  });
  it("treats anything unknown or missing as production (fail calm)", () => {
    expect(deployEnv(undefined)).toBe("production");
    expect(deployEnv("")).toBe("production");
    expect(deployEnv("staging")).toBe("production");
  });
});

describe("pieceEnabled", () => {
  it("calm is off everywhere", () => {
    for (const env of ["local", "preview", "production"] as const)
      expect(pieceEnabled("windows", env, all("calm"))).toBe(false);
  });
  it("preview is on in local and preview, off in production", () => {
    expect(pieceEnabled("windows", "local", all("preview"))).toBe(true);
    expect(pieceEnabled("windows", "preview", all("preview"))).toBe(true);
    expect(pieceEnabled("windows", "production", all("preview"))).toBe(false);
  });
  it("full is on everywhere", () => {
    expect(pieceEnabled("windows", "production", all("full"))).toBe(true);
  });
  it("ships with nothing full until Din approves", () => {
    expect(Object.values(RELEASES)).not.toContain("full");
  });
});
```

The last test is deleted in the same commit that flips the first piece to `"full"` after Din's approval (Task 11 Step 8).

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/flags.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write minimal implementation**

```ts
// site/src/lib/setpieces/flags.ts
// One release value per set piece. "preview" shows the full version in local and
// preview builds and the calm version in production. Move a piece to "full" only
// after Din approves it in the preview, with a ledger entry.
export type SetPiece = "lens" | "windows" | "paper" | "studio" | "letter";
export type Release = "calm" | "preview" | "full";
export type DeployEnv = "local" | "preview" | "production";

export const RELEASES: Readonly<Record<SetPiece, Release>> = {
  lens: "calm",
  windows: "calm",
  paper: "calm",
  studio: "calm",
  letter: "calm",
};

export function deployEnv(raw: string | undefined = import.meta.env.PUBLIC_DEPLOY_ENV): DeployEnv {
  if (raw === "local" || raw === "preview") return raw;
  return "production";
}

export function pieceEnabled(
  piece: SetPiece,
  env: DeployEnv = deployEnv(),
  releases: Readonly<Record<SetPiece, Release>> = RELEASES,
): boolean {
  const r = releases[piece];
  return r === "full" || (r === "preview" && env !== "production");
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/flags.test.ts`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/flags.ts site/tests/unit/flags.test.ts
git commit -m "feat(site): release flags for the home set pieces"
```

### Task 3: Lazy loader, the enhance guard and the GSAP module

**Files:**
- Create: `site/src/lib/setpieces/lazy.ts`
- Create: `site/src/lib/setpieces/gsap.ts`
- Modify: `site/package.json` (add `gsap`)
- Test: `site/tests/unit/lazy.test.ts`

**Interfaces:**
- Consumes: `currentMotion()` from Task 1.
- Produces:
  - `canEnhance(top: number, viewportHeight: number): boolean`: true only when the section's top edge is at or below the bottom of the viewport, so switching to the tall full layout cannot move anything the visitor sees.
  - `whenNear(el: Element, load: () => Promise<unknown>, rootMargin?: string): () => void`: one-shot IntersectionObserver, default margin `"100% 0px 100% 0px"`; a failed import is swallowed (the piece stays calm).
  - `bootPiece(el: HTMLElement, load: () => Promise<{ enhance(el: HTMLElement): void }>, opts?: { needsFull?: boolean; guardLayout?: boolean }): void`: does nothing when `opts.needsFull !== false` and `currentMotion() === "calm"`; otherwise calls `whenNear`, and after import checks `canEnhance(el.getBoundingClientRect().top, innerHeight)` when `guardLayout` is true before calling `enhance`.
  - `site/src/lib/setpieces/gsap.ts` exports `{ gsap, ScrollTrigger }` with the plugin registered once.

- [ ] **Step 1: Install GSAP**

Run: `pnpm --dir site add gsap@~3.15.0`
Expected: `gsap 3.15.0` in `site/package.json` dependencies and the lockfile updated. (Why: the set pieces' scroll timelines, per the locked stack.)

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/unit/lazy.test.ts
import { describe, expect, it } from "vitest";
import { canEnhance } from "../../src/lib/setpieces/lazy";

describe("canEnhance", () => {
  it("allows enhancing while the section is still below the viewport", () => {
    expect(canEnhance(900, 900)).toBe(true);
    expect(canEnhance(1800, 900)).toBe(true);
  });
  it("refuses once any part of the section is on screen or above it", () => {
    expect(canEnhance(899, 900)).toBe(false);
    expect(canEnhance(0, 900)).toBe(false);
    expect(canEnhance(-4000, 900)).toBe(false);
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/lazy.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 4: Write the implementation**

```ts
// site/src/lib/setpieces/lazy.ts
import { currentMotion, onMotionChange } from "../motion";

export function canEnhance(top: number, viewportHeight: number): boolean {
  return top >= viewportHeight;
}

export function whenNear(
  el: Element,
  load: () => Promise<unknown>,
  rootMargin = "100% 0px 100% 0px",
): () => void {
  if (!("IntersectionObserver" in window)) return () => {};
  const io = new IntersectionObserver(
    (entries) => {
      if (!entries.some((e) => e.isIntersecting)) return;
      io.disconnect();
      load().catch(() => {
        // The calm markup is already on the page; nothing else to do.
      });
    },
    { rootMargin },
  );
  io.observe(el);
  return () => io.disconnect();
}

let watching = false;

export function bootPiece(
  el: HTMLElement,
  load: () => Promise<{ enhance(el: HTMLElement): void }>,
  opts: { needsFull?: boolean; guardLayout?: boolean } = {},
): void {
  if (!watching) {
    watching = true;
    onMotionChange(() => {}); // keeps <html data-motion> current for the CSS
  }
  if (opts.needsFull !== false && currentMotion() === "calm") return;
  whenNear(el, async () => {
    const mod = await load();
    if (opts.guardLayout && !canEnhance(el.getBoundingClientRect().top, window.innerHeight)) return;
    mod.enhance(el);
  });
}
```

```ts
// site/src/lib/setpieces/gsap.ts
// The only module that imports GSAP, so it lands in one lazy chunk shared by the enhancers.
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
export { gsap, ScrollTrigger };
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/lazy.test.ts`
Expected: PASS (2 tests). `whenNear` and `bootPiece` are covered end to end in Task 13 (`setpieces-loading.spec.ts`).

- [ ] **Step 6: Commit**

```bash
git add site/package.json pnpm-lock.yaml site/src/lib/setpieces/lazy.ts site/src/lib/setpieces/gsap.ts site/tests/unit/lazy.test.ts
git commit -m "feat(site): lazy set-piece loader and the shared GSAP module"
```

### Task 4: JavaScript budget gate, screenshot and perf harness

**Files:**
- Create (or extend if M0/M5 shipped it): `site/scripts/budget.ts`
- Modify: `site/package.json` (script `"budget": "node scripts/budget.ts"`), `check.sh` (run `pnpm --dir site budget` after the build), the CI workflow if `check.sh` is not what CI runs
- Create: `site/tests/e2e/helpers/scroll.ts`, `site/tests/e2e/helpers/fps.ts`
- Create: `site/tests/e2e/shots.spec.ts` (tag `@shots`), `site/tests/e2e/perf.spec.ts` (tag `@perf`)
- Modify: `site/playwright.config.ts` (exclude `@shots` and `@perf` from the default run with `grepInvert: /@shots|@perf/`)
- Test: `site/tests/unit/budget.test.ts`, `site/tests/unit/fps.test.ts`

**Interfaces:**
- Produces:
  - `staticImports(code: string): string[]` (top-level `import ... from "x"`, `import "x"`, `export ... from "x"`; never `import("x")`).
  - `htmlEntries(html: string): { srcs: string[]; inline: string[] }` (module scripts, modulepreload links, inline scripts; external `http(s)://` URLs dropped).
  - `initialGraph(entries: string[], read: (path: string) => string | undefined, resolve: (from: string, spec: string) => string): string[]`.
  - `gzipSize(text: string): number`.
  - `findGsap(chunks: { path: string; code: string }[]): string[]` (paths whose code contains `"ScrollTrigger"` or `"GreenSock"`).
  - `fpsStats(timestamps: number[]): { fps: number; p95GapMs: number; gapsOver25: number }`.
  - `scrollToProgress(page: Page, selector: string, p: number): Promise<void>` (scrolls so that the section's own scroll range is at fraction `p`, then waits two animation frames and 700 ms for the scrub to settle).

- [ ] **Step 1: Write the failing budget test**

```ts
// site/tests/unit/budget.test.ts
import { describe, expect, it } from "vitest";
import { findGsap, gzipSize, htmlEntries, initialGraph, staticImports } from "../../scripts/budget";

describe("staticImports", () => {
  it("finds minified static imports and re-exports", () => {
    const code = `import{a as b}from"./chunk-A.js";import"./side.js";export{c}from"./re.js";`;
    expect(staticImports(code)).toEqual(["./chunk-A.js", "./side.js", "./re.js"]);
  });
  it("ignores dynamic imports", () => {
    expect(staticImports(`const m=()=>import("./lazy.js");`)).toEqual([]);
  });
});

describe("htmlEntries", () => {
  it("collects module scripts, modulepreloads and inline scripts, not third parties", () => {
    const html = `<head><script>var a=1</script><link rel="modulepreload" href="/_astro/x.js">
      <script type="module" src="/_astro/page.js"></script>
      <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async></script></head>`;
    const e = htmlEntries(html);
    expect(e.srcs.sort()).toEqual(["/_astro/page.js", "/_astro/x.js"]);
    expect(e.inline).toEqual(["var a=1"]);
  });
});

describe("initialGraph", () => {
  it("follows static imports once each and skips dynamic ones", () => {
    const files: Record<string, string> = {
      "/_astro/page.js": `import"./a.js";const l=()=>import("./lazy.js");`,
      "/_astro/a.js": `import"./b.js";import"./page.js";`,
      "/_astro/b.js": `1`,
      "/_astro/lazy.js": `import"./gsap.js";`,
    };
    const resolve = (from: string, spec: string) => new URL(spec, `https://x${from}`).pathname;
    expect(initialGraph(["/_astro/page.js"], (p) => files[p], resolve).sort())
      .toEqual(["/_astro/a.js", "/_astro/b.js", "/_astro/page.js"]);
  });
});

describe("findGsap", () => {
  it("flags chunks that contain GSAP", () => {
    expect(findGsap([{ path: "a.js", code: `x.registerPlugin("ScrollTrigger")` }, { path: "b.js", code: "1" }]))
      .toEqual(["a.js"]);
  });
});

describe("gzipSize", () => {
  it("is smaller than the raw size for repetitive text", () => {
    expect(gzipSize("a".repeat(1000))).toBeLessThan(100);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/budget.test.ts`
Expected: FAIL, cannot find `../../scripts/budget`.

- [ ] **Step 3: Write the budget script**

```ts
// site/scripts/budget.ts
// Home page JavaScript budget: first-party JS loaded before any interaction, gzipped.
// Fails above 100 KB or when GSAP leaks into the initial module graph.
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, posix } from "node:path";
import { gzipSync } from "node:zlib";

export const LIMIT_BYTES = 100 * 1024;

export function staticImports(code: string): string[] {
  const out: string[] = [];
  const re = /(?:^|[;\s}])(?:import\s*(?:[\w$*{}\s,]+?\s*from\s*)?|export\s*(?:\*|\{[^}]*\})\s*from\s*)["']([^"']+)["']/g;
  for (const m of code.matchAll(re)) out.push(m[1]);
  return out;
}

export function htmlEntries(html: string): { srcs: string[]; inline: string[] } {
  const srcs = new Set<string>();
  const inline: string[] = [];
  for (const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)) {
    const src = /\bsrc=["']([^"']+)["']/.exec(m[1])?.[1];
    if (src) {
      if (!/^https?:\/\//.test(src)) srcs.add(src);
    } else if (!/type=["']application\/(ld\+)?json["']/.test(m[1]) && m[2].trim()) {
      inline.push(m[2].trim());
    }
  }
  for (const m of html.matchAll(/<link\b[^>]*rel=["']modulepreload["'][^>]*>/g)) {
    const href = /\bhref=["']([^"']+)["']/.exec(m[0])?.[1];
    if (href && !/^https?:\/\//.test(href)) srcs.add(href);
  }
  return { srcs: [...srcs], inline };
}

export function initialGraph(
  entries: string[],
  read: (path: string) => string | undefined,
  resolve: (from: string, spec: string) => string,
): string[] {
  const seen = new Set<string>();
  const stack = [...entries];
  while (stack.length) {
    const p = stack.pop()!;
    if (seen.has(p)) continue;
    const code = read(p);
    if (code === undefined) continue;
    seen.add(p);
    for (const spec of staticImports(code)) stack.push(resolve(p, spec));
  }
  return [...seen];
}

export function gzipSize(text: string): number {
  return gzipSync(text, { level: 9 }).length;
}

export function findGsap(chunks: { path: string; code: string }[]): string[] {
  return chunks.filter((c) => /["']ScrollTrigger["']|GreenSock/.test(c.code)).map((c) => c.path);
}

function findIndexHtml(dist: string): { html: string; root: string } {
  for (const sub of ["client", ""]) {
    const root = join(dist, sub);
    const file = join(root, "index.html");
    if (existsSync(file)) return { html: readFileSync(file, "utf8"), root };
  }
  throw new Error(`No index.html under ${dist}. Run pnpm --dir site build first.`);
}

function listJs(dir: string): string[] {
  return readdirSync(dir).flatMap((f) => {
    const p = join(dir, f);
    return statSync(p).isDirectory() ? listJs(p) : p.endsWith(".js") ? [p] : [];
  });
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const dist = join(process.cwd(), "dist");
  const { html, root } = findIndexHtml(dist);
  const { srcs, inline } = htmlEntries(html);
  const read = (p: string) => (existsSync(join(root, p)) ? readFileSync(join(root, p), "utf8") : undefined);
  const graph = initialGraph(srcs, read, (from, spec) => posix.normalize(posix.join(posix.dirname(from), spec)));
  const rows = graph.map((p) => ({ path: p, gz: gzipSize(read(p)!) }));
  const inlineGz = inline.reduce((n, s) => n + gzipSize(s), 0);
  const total = rows.reduce((n, r) => n + r.gz, 0) + inlineGz;
  const allJs = listJs(root).map((p) => ({ path: p.slice(root.length), code: readFileSync(p, "utf8") }));
  const lazyGz = allJs.filter((c) => !graph.includes(c.path)).reduce((n, c) => n + gzipSize(c.code), 0);
  for (const r of rows.sort((a, b) => b.gz - a.gz)) console.log(`${(r.gz / 1024).toFixed(1).padStart(7)} KB  ${r.path}`);
  console.log(`${(inlineGz / 1024).toFixed(1).padStart(7)} KB  inline scripts`);
  console.log(`initial: ${(total / 1024).toFixed(1)} KB gzipped (limit ${LIMIT_BYTES / 1024} KB)`);
  console.log(`lazy, all other chunks (report only): ${(lazyGz / 1024).toFixed(1)} KB gzipped`);
  const leaked = findGsap(allJs.filter((c) => graph.includes(c.path)));
  if (leaked.length) {
    console.error(`GSAP is in the initial graph: ${leaked.join(", ")}`);
    process.exit(1);
  }
  if (total > LIMIT_BYTES) process.exit(1);
}
```

If M0 or M5 already shipped a `budget` script, keep theirs and add only the `findGsap` check and the lazy report, with the same tests.

- [ ] **Step 4: Run the tests and the script**

Run: `pnpm --dir site exec vitest run tests/unit/budget.test.ts && pnpm --dir site build && pnpm --dir site budget`
Expected: tests PASS (6); the script prints the chunk table and `initial: N KB gzipped (limit 100 KB)` and exits 0.

- [ ] **Step 5: Write the failing fps test**

```ts
// site/tests/unit/fps.test.ts
import { describe, expect, it } from "vitest";
import { fpsStats } from "../e2e/helpers/fps";

describe("fpsStats", () => {
  it("reports 60 fps for steady 16.67 ms frames", () => {
    const t = Array.from({ length: 121 }, (_, i) => i * (1000 / 60));
    const s = fpsStats(t);
    expect(s.fps).toBeCloseTo(60, 0);
    expect(s.gapsOver25).toBe(0);
  });
  it("counts long gaps and the 95th percentile gap", () => {
    const t = [0, 16, 32, 48, 100, 116, 132];
    const s = fpsStats(t);
    expect(s.gapsOver25).toBe(1);
    expect(s.p95GapMs).toBe(52);
  });
  it("handles fewer than two samples", () => {
    expect(fpsStats([5])).toEqual({ fps: 0, p95GapMs: 0, gapsOver25: 0 });
  });
});
```

- [ ] **Step 6: Run it to verify it fails, then implement**

Run: `pnpm --dir site exec vitest run tests/unit/fps.test.ts` (expected FAIL), then:

```ts
// site/tests/e2e/helpers/fps.ts
export function fpsStats(ts: number[]): { fps: number; p95GapMs: number; gapsOver25: number } {
  if (ts.length < 2) return { fps: 0, p95GapMs: 0, gapsOver25: 0 };
  const gaps = ts.slice(1).map((t, i) => t - ts[i]);
  const sorted = [...gaps].sort((a, b) => a - b);
  const p95 = sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * 0.95) - 1)];
  return {
    fps: (gaps.length * 1000) / (ts[ts.length - 1] - ts[0]),
    p95GapMs: Math.round(p95),
    gapsOver25: gaps.filter((g) => g > 25).length,
  };
}
```

Run again. Expected: PASS (3 tests).

- [ ] **Step 7: Write the scroll helper, the shots spec and the perf spec**

```ts
// site/tests/e2e/helpers/scroll.ts
import type { Page } from "@playwright/test";

export async function scrollToProgress(page: Page, selector: string, p: number): Promise<void> {
  await page.evaluate(
    ({ selector, p }) => {
      const el = document.querySelector<HTMLElement>(selector);
      if (!el) throw new Error(`missing ${selector}`);
      const top = el.getBoundingClientRect().top + window.scrollY;
      const range = Math.max(0, el.offsetHeight - window.innerHeight);
      window.scrollTo({ top: top + range * p, behavior: "instant" });
    },
    { selector, p },
  );
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  await page.waitForTimeout(700);
}
```

```ts
// site/tests/e2e/shots.spec.ts
// Screenshots for the gate PRs. Run: pnpm --dir site test:e2e --grep @shots
import { test } from "@playwright/test";
import { scrollToProgress } from "./helpers/scroll";

const PIECES = [
  { name: "lens", selector: "#top", points: [0] },
  { name: "windows", selector: "#work", points: [0, 0.25, 0.5, 0.75, 1] },
  { name: "paper", selector: "#writing", points: [0, 0.5, 1] },
  { name: "studio", selector: "#about", points: [0, 0.2, 0.45, 0.7, 1] },
  { name: "letter", selector: "#contact", points: [0, 1] },
];
const VIEWPORTS = [{ name: "laptop", width: 1440, height: 900 }, { name: "phone", width: 390, height: 844 }];

for (const piece of PIECES)
  for (const vp of VIEWPORTS)
    for (const theme of ["light", "dark"] as const)
      for (const mode of ["full", "calm"] as const)
        test(`@shots ${piece.name} ${vp.name} ${theme} ${mode}`, async ({ page }) => {
          await page.setViewportSize({ width: vp.width, height: vp.height });
          await page.emulateMedia({ colorScheme: theme });
          await page.addInitScript(() => sessionStorage.setItem("dins:intro-seen", "1"));
          await page.goto(mode === "calm" ? "/?calm" : "/");
          // Let the lazy loader see each section on the way down.
          for (let y = 0; y < 30; y++) await page.mouse.wheel(0, 900);
          for (const p of piece.points) {
            await scrollToProgress(page, piece.selector, p);
            await page.screenshot({ path: `test-results/shots/${piece.name}/${vp.name}-${theme}-${mode}-${p}.png` });
          }
        });
```

```ts
// site/tests/e2e/perf.spec.ts
// Frame pacing and long tasks through the set pieces. Run: pnpm --dir site test:e2e --grep @perf
// CPU throttling is a proxy for a mid-range phone, not proof; Din checks real devices.
import { expect, test } from "@playwright/test";
import { writeFileSync, mkdirSync } from "node:fs";
import { fpsStats } from "./helpers/fps";

for (const profile of [{ name: "laptop", rate: 1, w: 1440, h: 900 }, { name: "phone-proxy", rate: 4, w: 412, h: 915 }])
  test(`@perf scroll the home page (${profile.name})`, async ({ page, browserName }) => {
    test.skip(browserName !== "chromium", "CDP throttling and longtask entries are Chromium only");
    await page.setViewportSize({ width: profile.w, height: profile.h });
    const cdp = await page.context().newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: profile.rate });
    await page.addInitScript(() => {
      (window as any).__long = [];
      new PerformanceObserver((l) => (window as any).__long.push(...l.getEntries().map((e) => e.duration)))
        .observe({ type: "longtask", buffered: true });
    });
    await page.goto("/");
    await page.waitForLoadState("networkidle");
    await page.evaluate(() => {
      (window as any).__frames = [];
      const tick = (t: number) => { (window as any).__frames.push(t); requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    });
    const height = await page.evaluate(() => document.documentElement.scrollHeight);
    for (let y = 0; y < height; y += 120) { await page.mouse.wheel(0, 120); await page.waitForTimeout(16); }
    const frames: number[] = await page.evaluate(() => (window as any).__frames);
    const longTasks: number[] = await page.evaluate(() => (window as any).__long);
    const stats = { profile: profile.name, ...fpsStats(frames), longTasks };
    mkdirSync("test-results/perf", { recursive: true });
    writeFileSync(`test-results/perf/${profile.name}.json`, JSON.stringify(stats, null, 2));
    expect(longTasks.filter((d) => d > 50)).toEqual([]);
    if (profile.rate === 1) expect(stats.p95GapMs).toBeLessThanOrEqual(20);
  });
```

Note: the long-task assertion holds under both profiles; the frame-gap assertion holds only unthrottled, because a 4x throttled headless run is noisier than a real phone. The JSON for both goes in each gate PR.

- [ ] **Step 8: Run the harness once on the current site**

Run: `pnpm --dir site test:e2e --grep @shots && pnpm --dir site test:e2e --grep @perf`
Expected: PNGs under `site/test-results/shots/`, JSON under `site/test-results/perf/`, both tests PASS on the M1 plain home page. `test-results/` must already be gitignored (M0); if not, add it.

- [ ] **Step 9: Commit**

```bash
git add site/scripts/budget.ts site/package.json check.sh site/playwright.config.ts site/tests/unit/budget.test.ts site/tests/unit/fps.test.ts site/tests/e2e/helpers site/tests/e2e/shots.spec.ts site/tests/e2e/perf.spec.ts
git commit -m "test(site): home JS budget gate, set-piece screenshots and perf harness"
```

### Task 4a: Motion property guard

**Files:**
- Create: `site/tests/unit/motion-properties.test.ts`

**Interfaces:**
- Consumes: every `*.css` file under `site/src/components/home/` and every `*.ts` file under `site/src/lib/setpieces/`.

- [ ] **Step 1: Write the test (it passes today because the folders are nearly empty; it guards every later task)**

```ts
// site/tests/unit/motion-properties.test.ts
// PRD section 6: only transform, opacity and canvas animate.
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const ROOT = new URL("../../src/", import.meta.url).pathname;
const ALLOWED = new Set(["transform", "opacity", "none", "visibility"]);

function files(dir: string, ext: string): string[] {
  try {
    return readdirSync(dir).flatMap((f) => {
      const p = join(dir, f);
      return statSync(p).isDirectory() ? files(p, ext) : p.endsWith(ext) ? [p] : [];
    });
  } catch {
    return [];
  }
}

function keyframeProps(css: string): string[] {
  const out: string[] = [];
  for (const m of css.matchAll(/@keyframes\s+[\w-]+\s*\{/g)) {
    let depth = 1, i = m.index! + m[0].length, body = "";
    while (depth && i < css.length) { const c = css[i++]; if (c === "{") depth++; if (c === "}") depth--; if (depth) body += c; }
    for (const p of body.matchAll(/([a-z-]+)\s*:/g)) out.push(p[1]);
  }
  return out;
}

function transitionProps(css: string): string[] {
  const out: string[] = [];
  for (const m of css.matchAll(/transition(?:-property)?\s*:\s*([^;}]+)/g))
    for (const part of m[1].replace(/\([^)]*\)/g, "").split(",")) out.push(part.trim().split(/\s+/)[0]);
  return out;
}

describe("set-piece motion uses only transform and opacity", () => {
  for (const f of files(join(ROOT, "components/home"), ".css")) {
    it(f.slice(ROOT.length), () => {
      const css = readFileSync(f, "utf8");
      const bad = [...keyframeProps(css), ...transitionProps(css)].filter((p) => !ALLOWED.has(p) && !p.startsWith("--"));
      expect(bad).toEqual([]);
    });
  }
  for (const f of files(join(ROOT, "lib/setpieces"), ".ts")) {
    it(f.slice(ROOT.length), () => {
      const ts = readFileSync(f, "utf8");
      expect(ts).not.toMatch(/\.style\.(filter|width|height|top|left|margin\w*|clipPath|boxShadow)\s*=/);
    });
  }
});
```

Note: `transition: all` is rejected by this test on purpose (the sketch's `.rz` chips used it).

- [ ] **Step 2: Run it**

Run: `pnpm --dir site exec vitest run tests/unit/motion-properties.test.ts`
Expected: PASS (or "no tests" if no files exist yet; it starts guarding as files land).

- [ ] **Step 3: Commit**

```bash
git add site/tests/unit/motion-properties.test.ts
git commit -m "test(site): guard set pieces to transform and opacity motion"
```

---

## Part B. Contact delivery (not a visual gate; ships with the foundation PR)

Precheck: if `site/src/pages/api/contact.ts` already exists from M1, read it, keep its behaviour, and turn Tasks 5 and 6 into adding the missing tests and cases listed here (honeypot, origin, size, logging) instead of rewriting.

### Task 5: Contact form parsing shared by browser and Worker

**Files:**
- Create: `site/src/lib/contact/parse.ts`
- Test: `site/tests/unit/contact-parse.test.ts`

**Interfaces:**
- Produces: `REASONS = ["role", "admissions", "hi"] as const`; `type Reason`; `REASON_LABELS: Record<Reason, string>` (`"A role"`, `"Admissions"`, `"Just saying hi"`); `LIMITS = { message: 4000, name: 100, email: 254 }`; `interface ContactInput { message: string; email: string; name: string; reason: Reason; token: string; honeypot: string }`; `type ContactField = "message" | "email" | "name" | "reason"`; `type ParseResult = { ok: true; value: ContactInput } | { ok: false; errors: Partial<Record<ContactField, string>> }`; `parseContact(form: FormData): ParseResult`. Field names in the form: `message`, `email`, `name`, `reason`, `cf-turnstile-response`, `website` (the honeypot).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/contact-parse.test.ts
import { describe, expect, it } from "vitest";
import { LIMITS, parseContact } from "../../src/lib/contact/parse";

function fd(fields: Record<string, string>): FormData {
  const f = new FormData();
  for (const [k, v] of Object.entries(fields)) f.set(k, v);
  return f;
}
const good = { message: "Hi Din, about a data role.", email: "a@b.co", name: "Ada", reason: "role", "cf-turnstile-response": "tok", website: "" };

describe("parseContact", () => {
  it("accepts a good letter and trims it", () => {
    const r = parseContact(fd({ ...good, message: "  hello  ", name: " Ada " }));
    expect(r).toEqual({ ok: true, value: { message: "hello", email: "a@b.co", name: "Ada", reason: "role", token: "tok", honeypot: "" } });
  });
  it("needs a message", () => {
    const r = parseContact(fd({ ...good, message: "   " }));
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors.message).toBe("Write a few words first.");
  });
  it("needs a plausible email", () => {
    for (const email of ["", "no-at", "a@b", "a b@c.co", "x".repeat(250) + "@b.co"]) {
      const r = parseContact(fd({ ...good, email }));
      expect(r.ok).toBe(false);
      if (!r.ok) expect(r.errors.email).toBe("Add an email so I can reply.");
    }
  });
  it("limits the message length", () => {
    const r = parseContact(fd({ ...good, message: "a".repeat(LIMITS.message + 1) }));
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.errors.message).toBe(`Keep it under ${LIMITS.message} characters.`);
  });
  it("strips line breaks and control characters from the name", () => {
    const r = parseContact(fd({ ...good, name: "Ada\r\nBcc: x@y.z\u0007" }));
    expect(r.ok && r.value.name).toBe("Ada Bcc: x@y.z");
  });
  it("keeps line breaks in the message but drops other control characters", () => {
    const r = parseContact(fd({ ...good, message: "line one\nline two\u0000" }));
    expect(r.ok && r.value.message).toBe("line one\nline two");
  });
  it("falls back to the first reason when the value is unknown", () => {
    const r = parseContact(fd({ ...good, reason: "<script>" }));
    expect(r.ok && r.value.reason).toBe("role");
  });
  it("name is optional", () => {
    const r = parseContact(fd({ ...good, name: "" }));
    expect(r.ok && r.value.name).toBe("");
  });
  it("passes the honeypot and token through for the handler to judge", () => {
    const r = parseContact(fd({ ...good, website: "http://spam", "cf-turnstile-response": "" }));
    expect(r.ok && r.value.honeypot).toBe("http://spam");
    expect(r.ok && r.value.token).toBe("");
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/contact-parse.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/contact/parse.ts
// Shared by the letter in the browser and /api/contact on the Worker.
export const REASONS = ["role", "admissions", "hi"] as const;
export type Reason = (typeof REASONS)[number];
export const REASON_LABELS: Record<Reason, string> = { role: "A role", admissions: "Admissions", hi: "Just saying hi" };
export const LIMITS = { message: 4000, name: 100, email: 254 } as const;

export interface ContactInput { message: string; email: string; name: string; reason: Reason; token: string; honeypot: string }
export type ContactField = "message" | "email" | "name" | "reason";
export type ParseResult = { ok: true; value: ContactInput } | { ok: false; errors: Partial<Record<ContactField, string>> };

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const str = (f: FormData, k: string) => { const v = f.get(k); return typeof v === "string" ? v : ""; };

export function parseContact(form: FormData): ParseResult {
  const message = str(form, "message").replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  const email = str(form, "email").trim();
  const name = str(form, "name").replace(/[\r\n]+/g, " ").replace(/[\u0000-\u001F\u007F]/g, "").trim();
  const rawReason = str(form, "reason");
  const reason = (REASONS as readonly string[]).includes(rawReason) ? (rawReason as Reason) : REASONS[0];
  const errors: Partial<Record<ContactField, string>> = {};
  if (!message) errors.message = "Write a few words first.";
  else if (message.length > LIMITS.message) errors.message = `Keep it under ${LIMITS.message} characters.`;
  if (!EMAIL.test(email) || email.length > LIMITS.email) errors.email = "Add an email so I can reply.";
  if (name.length > LIMITS.name) errors.name = `Keep your name under ${LIMITS.name} characters.`;
  if (Object.keys(errors).length) return { ok: false, errors };
  return { ok: true, value: { message, email, name, reason, token: str(form, "cf-turnstile-response"), honeypot: str(form, "website") } };
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/contact-parse.test.ts`
Expected: PASS (9 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/contact/parse.ts site/tests/unit/contact-parse.test.ts
git commit -m "feat(site): contact form parsing shared by the letter and the Worker"
```

### Task 6: `/api/contact` on the Worker with Turnstile, rate limit and `send_email`

**Files:**
- Create: `site/src/lib/contact/handler.ts`
- Create: `site/src/pages/api/contact.ts`
- Create only if M3 has not: `site/src/lib/turnstile.ts` (signature in "Assumes")
- Modify: `site/wrangler.jsonc` (bindings for production and `env.preview`), `site/.dev.vars.example`
- Test: `site/tests/worker/contact.test.ts`

**Interfaces:**
- Consumes: `parseContact`, `REASON_LABELS` (Task 5); `verifyTurnstile` (M3 or this task).
- Produces:
  - `interface ContactEnv { EMAIL: { send(m: OutgoingEmail): Promise<{ messageId: string }> }; CONTACT_LIMITER: { limit(o: { key: string }): Promise<{ success: boolean }> }; CONTACT_TO: string }`
  - `interface OutgoingEmail { to: string; from: { email: string; name: string }; replyTo: { email: string; name?: string }; subject: string; text: string }`
  - `interface ContactDeps { verify(token: string, ip: string | null): Promise<boolean>; log(event: string, data?: Record<string, string | number>): void }`
  - `handleContact(request: Request, env: ContactEnv, deps: ContactDeps): Promise<Response>`
  - Responses: JSON `{ ok: true }` (200) or `{ ok: false, code, errors? }` with `code` in `invalid | verify | rate | origin | too-large | send` (400, 403, 429, 403, 413, 502) when `Accept` includes `application/json`; otherwise `303` to `/contact/sent/` or `/contact/not-sent/`.

- [ ] **Step 1: Write the failing Worker test**

```ts
// site/tests/worker/contact.test.ts
import { beforeEach, describe, expect, it, vi } from "vitest";
import { handleContact, type ContactDeps, type ContactEnv, type OutgoingEmail } from "../../src/lib/contact/handler";

const ORIGIN = "https://dins.dev";
let sent: OutgoingEmail[];
let logs: string[];
let env: ContactEnv;
let deps: ContactDeps;
let allow: boolean;
let human: boolean;

beforeEach(() => {
  sent = []; logs = []; allow = true; human = true;
  env = {
    EMAIL: { send: async (m) => { sent.push(m); return { messageId: "m1" }; } },
    CONTACT_LIMITER: { limit: async () => ({ success: allow }) },
    CONTACT_TO: "din@dins.dev",
  };
  deps = {
    verify: vi.fn(async () => human),
    log: (event, data) => logs.push(JSON.stringify({ event, ...data })),
  };
});

function post(fields: Record<string, string>, opts: { json?: boolean; origin?: string; body?: BodyInit } = {}): Request {
  const body = opts.body ?? new URLSearchParams(fields);
  return new Request(`${ORIGIN}/api/contact`, {
    method: "POST",
    body,
    headers: {
      accept: opts.json === false ? "text/html" : "application/json",
      origin: opts.origin ?? ORIGIN,
      "cf-connecting-ip": "203.0.113.9",
    },
  });
}
const good = { message: "Hi Din, about a data role.", email: "ada@example.com", name: "Ada", reason: "admissions", "cf-turnstile-response": "tok", website: "" };

describe("POST /api/contact", () => {
  it("sends one plain-text email to CONTACT_TO with the visitor as reply-to", async () => {
    const res = await handleContact(post(good), env, deps);
    expect(res.status).toBe(200);
    expect(await res.json()).toEqual({ ok: true });
    expect(sent).toHaveLength(1);
    expect(sent[0].to).toBe("din@dins.dev");
    expect(sent[0].replyTo).toEqual({ email: "ada@example.com", name: "Ada" });
    expect(sent[0].from.email).toBe("letters@dins.dev");
    expect(sent[0].subject).toBe("Letter from dins.dev: Admissions");
    expect(sent[0].text).toContain("Hi Din, about a data role.");
  });
  it("redirects to /contact/sent/ for a no-JavaScript post", async () => {
    const res = await handleContact(post(good, { json: false }), env, deps);
    expect(res.status).toBe(303);
    expect(res.headers.get("location")).toBe("/contact/sent/");
  });
  it("returns field errors and sends nothing for an invalid letter", async () => {
    const res = await handleContact(post({ ...good, email: "nope" }), env, deps);
    expect(res.status).toBe(400);
    expect(await res.json()).toEqual({ ok: false, code: "invalid", errors: { email: "Add an email so I can reply." } });
    expect(sent).toHaveLength(0);
  });
  it("treats a missing Turnstile token (JavaScript off) as unverified and points to the fallback page", async () => {
    const res = await handleContact(post({ ...good, "cf-turnstile-response": "" }, { json: false }), env, deps);
    expect(res.status).toBe(303);
    expect(res.headers.get("location")).toBe("/contact/not-sent/");
    expect(deps.verify).not.toHaveBeenCalled();
    expect(sent).toHaveLength(0);
  });
  it("rejects a failed Turnstile check", async () => {
    human = false;
    const res = await handleContact(post(good), env, deps);
    expect(res.status).toBe(403);
    expect((await res.json()).code).toBe("verify");
    expect(sent).toHaveLength(0);
  });
  it("rate limits before calling Turnstile", async () => {
    allow = false;
    const res = await handleContact(post(good), env, deps);
    expect(res.status).toBe(429);
    expect(deps.verify).not.toHaveBeenCalled();
  });
  it("pretends success for a filled honeypot and sends nothing", async () => {
    const res = await handleContact(post({ ...good, website: "http://spam.example" }), env, deps);
    expect(res.status).toBe(200);
    expect(sent).toHaveLength(0);
  });
  it("rejects a cross-origin post", async () => {
    const res = await handleContact(post(good, { origin: "https://evil.example" }), env, deps);
    expect(res.status).toBe(403);
    expect((await res.json()).code).toBe("origin");
  });
  it("rejects a body over 16 KB", async () => {
    const res = await handleContact(post({}, { body: new URLSearchParams({ ...good, message: "a".repeat(17000) }) }), env, deps);
    expect(res.status).toBe(413);
    expect(sent).toHaveLength(0);
  });
  it("maps a send failure to 502 and logs only the error code", async () => {
    env.EMAIL.send = async () => { throw Object.assign(new Error("ada@example.com bounced"), { code: "E_DELIVERY_FAILED" }); };
    const res = await handleContact(post(good), env, deps);
    expect(res.status).toBe(502);
    expect(logs.join("\n")).toContain("E_DELIVERY_FAILED");
  });
  it("never logs what the visitor typed", async () => {
    await handleContact(post(good), env, deps);
    env.EMAIL.send = async () => { throw Object.assign(new Error("ada@example.com"), { code: "E_X" }); };
    await handleContact(post(good), env, deps);
    await handleContact(post({ ...good, email: "bad" }), env, deps);
    const all = logs.join("\n");
    for (const secret of ["ada@example.com", "Hi Din", "Ada", "203.0.113.9"]) expect(all).not.toContain(secret);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/worker/contact.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the handler**

```ts
// site/src/lib/contact/handler.ts
// The letter's endpoint. Messages are emailed and never stored or logged (PRD section 6).
import { parseContact, REASON_LABELS } from "./parse";

export interface OutgoingEmail {
  to: string;
  from: { email: string; name: string };
  replyTo: { email: string; name?: string };
  subject: string;
  text: string;
}
export interface ContactEnv {
  EMAIL: { send(m: OutgoingEmail): Promise<{ messageId: string }> };
  CONTACT_LIMITER: { limit(o: { key: string }): Promise<{ success: boolean }> };
  CONTACT_TO: string;
}
export interface ContactDeps {
  verify(token: string, ip: string | null): Promise<boolean>;
  log(event: string, data?: Record<string, string | number>): void;
}

const MAX_BYTES = 16 * 1024;
type Code = "invalid" | "verify" | "rate" | "origin" | "too-large" | "send";
const STATUS: Record<Code, number> = { invalid: 400, verify: 403, rate: 429, origin: 403, "too-large": 413, send: 502 };

export async function handleContact(request: Request, env: ContactEnv, deps: ContactDeps): Promise<Response> {
  const wantsJson = (request.headers.get("accept") ?? "").includes("application/json");
  const ok = () => (wantsJson ? Response.json({ ok: true }) : redirect("/contact/sent/"));
  const fail = (code: Code, errors?: Record<string, string>) => {
    deps.log("contact_rejected", { code });
    return wantsJson
      ? Response.json({ ok: false, code, ...(errors ? { errors } : {}) }, { status: STATUS[code] })
      : redirect("/contact/not-sent/");
  };

  const origin = request.headers.get("origin");
  if (origin && origin !== new URL(request.url).origin) return fail("origin");
  const raw = await request.arrayBuffer();
  if (raw.byteLength > MAX_BYTES) return fail("too-large");

  let form: FormData;
  try {
    form = await new Request(request.url, { method: "POST", body: raw, headers: request.headers }).formData();
  } catch {
    return fail("invalid");
  }
  const parsed = parseContact(form);
  if (!parsed.ok) return fail("invalid", parsed.errors);
  const letter = parsed.value;
  if (letter.honeypot) {
    deps.log("contact_honeypot");
    return ok();
  }

  const ip = request.headers.get("cf-connecting-ip");
  const { success } = await env.CONTACT_LIMITER.limit({ key: ip ?? "unknown" });
  if (!success) return fail("rate");
  if (!letter.token || !(await deps.verify(letter.token, ip))) return fail("verify");

  const reason = REASON_LABELS[letter.reason];
  const from = letter.name ? `${letter.name} <${letter.email}>` : letter.email;
  try {
    await env.EMAIL.send({
      to: env.CONTACT_TO,
      from: { email: "letters@dins.dev", name: "dins.dev letters" },
      replyTo: letter.name ? { email: letter.email, name: letter.name } : { email: letter.email },
      subject: `Letter from dins.dev: ${reason}`,
      text: `Reason: ${reason}\nFrom: ${from}\n\n${letter.message}\n`,
    });
  } catch (err) {
    deps.log("contact_send_failed", { code: String((err as { code?: string }).code ?? "unknown") });
    return fail("send");
  }
  deps.log("contact_sent");
  return ok();
}

function redirect(location: string): Response {
  return new Response(null, { status: 303, headers: { location } });
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/worker/contact.test.ts`
Expected: PASS (11 tests).

- [ ] **Step 5: Create `verifyTurnstile` only if M3 has not**

Run: `test -f site/src/lib/turnstile.ts && echo exists || echo create`
If `create`: write the module and its unit test with a fake `fetcher`.

```ts
// site/src/lib/turnstile.ts
export async function verifyTurnstile(o: {
  token: string; secret: string; remoteip?: string; action?: string; fetcher?: typeof fetch;
}): Promise<{ ok: boolean; codes: string[] }> {
  if (!o.token || o.token.length > 2048) return { ok: false, codes: ["missing-or-long-token"] };
  const body = new URLSearchParams({ secret: o.secret, response: o.token });
  if (o.remoteip) body.set("remoteip", o.remoteip);
  try {
    const res = await (o.fetcher ?? fetch)("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body });
    const data = (await res.json()) as { success?: boolean; action?: string; "error-codes"?: string[] };
    const actionOk = !o.action || data.action === o.action;
    return { ok: Boolean(data.success) && actionOk, codes: data["error-codes"] ?? (actionOk ? [] : ["action-mismatch"]) };
  } catch {
    return { ok: false, codes: ["siteverify-unreachable"] };
  }
}
```

```ts
// site/tests/unit/turnstile.test.ts
import { describe, expect, it } from "vitest";
import { verifyTurnstile } from "../../src/lib/turnstile";

const fake = (json: unknown) => (async () => new Response(JSON.stringify(json))) as unknown as typeof fetch;

describe("verifyTurnstile", () => {
  it("passes on success with the right action", async () => {
    expect((await verifyTurnstile({ token: "t", secret: "s", action: "contact", fetcher: fake({ success: true, action: "contact" }) })).ok).toBe(true);
  });
  it("fails on a different action", async () => {
    expect((await verifyTurnstile({ token: "t", secret: "s", action: "contact", fetcher: fake({ success: true, action: "ask" }) })).ok).toBe(false);
  });
  it("fails without calling out on an empty token", async () => {
    expect((await verifyTurnstile({ token: "", secret: "s", fetcher: fake({ success: true }) })).ok).toBe(false);
  });
  it("fails closed when siteverify is unreachable", async () => {
    const down = (async () => { throw new Error("down"); }) as unknown as typeof fetch;
    expect((await verifyTurnstile({ token: "t", secret: "s", fetcher: down })).ok).toBe(false);
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/turnstile.test.ts` (FAIL first if written test-first, then PASS, 4 tests).

- [ ] **Step 6: Wire the route and the bindings**

```ts
// site/src/pages/api/contact.ts
import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { handleContact, type ContactEnv } from "../../lib/contact/handler";
import { verifyTurnstile } from "../../lib/turnstile";

export const prerender = false;

export const POST: APIRoute = ({ request }) =>
  handleContact(request, env as unknown as ContactEnv, {
    verify: async (token, ip) =>
      (await verifyTurnstile({ token, secret: env.TURNSTILE_SECRET_KEY, remoteip: ip ?? undefined, action: "contact" })).ok,
    log: (event, data) => console.log(JSON.stringify({ event, ...data })),
  });
```

Add to `site/wrangler.jsonc`, at the top level and again inside `env.preview` (bindings are not inherited by environments):

```jsonc
"send_email": [{ "name": "EMAIL" }],
"ratelimits": [{ "name": "CONTACT_LIMITER", "namespace_id": "2001", "simple": { "limit": 3, "period": 60 } }]
```

No `destination_address` in the file: the recipient comes from the `CONTACT_TO` secret, so Din's personal inbox never lands in this public repo. `namespace_id` must differ from M3's limiter; check `grep namespace_id site/wrangler.jsonc` and pick the next free integer.

Add to `site/.dev.vars.example` (the real `.dev.vars` stays gitignored):

```
CONTACT_TO=din@dins.dev
TURNSTILE_SECRET_KEY=1x0000000000000000000000000000000AA
```

The site key for local and preview is Cloudflare's always-pass test key `1x00000000000000000000AA` (`PUBLIC_TURNSTILE_SITE_KEY`), shared with M3.

Then regenerate binding types: `pnpm --dir site exec wrangler types` (expected: `EMAIL`, `CONTACT_LIMITER` and `CONTACT_TO` appear in the generated `Env`).

- [ ] **Step 7: Run the checks**

Run: `./check.sh`
Expected: all green, including `astro check` on `contact.ts`.

- [ ] **Step 8: Commit**

```bash
git add site/src/lib/contact/handler.ts site/src/pages/api/contact.ts site/wrangler.jsonc site/.dev.vars.example site/tests/worker/contact.test.ts site/worker-configuration.d.ts
git add site/src/lib/turnstile.ts site/tests/unit/turnstile.test.ts 2>/dev/null || true
git commit -m "feat(site): /api/contact with Turnstile, rate limit and the send_email binding"
```

### Task 7: The plain letter (calm version) on home and `/contact`, plus the result pages

**Files:**
- Create: `site/src/components/home/letter/Letter.astro`, `site/src/components/home/letter/letter.css`
- Create: `site/src/lib/setpieces/letter/letter-enhance.ts` (plain behaviour only in this task)
- Create: `site/src/pages/contact/sent.astro`, `site/src/pages/contact/not-sent.astro`
- Modify: `site/src/pages/index.astro` (contact section uses `<Letter />`), `site/src/pages/contact.astro` (same component), the sitemap filter in `site/astro.config.mjs`
- Test: `site/tests/e2e/letter.spec.ts`

**Interfaces:**
- Consumes: `parseContact` (Task 5), `loadTurnstile()` (M3, or create `site/src/lib/turnstile-client.ts` with that signature: injects `https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit` once and resolves `window.turnstile`), `bootPiece` (Task 3).
- Produces: `Letter.astro` markup contract used by Task 22:
  - `<section id="contact" class="letter-section" data-piece="letter">` containing `<form class="letter" method="post" action="/api/contact" novalidate>`.
  - Fields: `<textarea name="message" id="letter-message" required maxlength="4000">` with a visible label "Message" (visually styled as the "Dear Din," salutation line, label kept for screen readers), `<fieldset class="reasons"><legend>What is it about?</legend>` with three `<input type="radio" name="reason" value="role|admissions|hi">` (role checked), `<input name="name" id="letter-name" autocomplete="name">` labelled "Your name", `<input name="email" id="letter-email" type="email" autocomplete="email" required>` labelled "Your email" (labels visually hidden behind the "From" row, never placeholder-only), a hidden honeypot `<div class="hp" aria-hidden="true"><label>Website <input name="website" tabindex="-1" autocomplete="off"></label></div>`, a `<div class="turnstile" data-sitekey={PUBLIC_TURNSTILE_SITE_KEY}>`, per-field error elements `#letter-message-error` and `#letter-email-error` wired with `aria-describedby`, a form-level `<p class="letter-status" role="status">`, and `<button type="submit" class="seal">Seal and send</button>`.
  - `<noscript><p>Sending needs JavaScript for a spam check. You can also write to <a href="mailto:din@dins.dev">din@dins.dev</a>.</p></noscript>`.
  - A success panel `<div class="letter-sent" hidden><h3 tabindex="-1">Sent. Thank you.</h3><p>I’ll reply to the email you gave.</p><button type="button" class="again">Write another</button></div>`.
- `letter-enhance.ts` exports `enhance(section: HTMLElement): void`, booted with `bootPiece(section, () => import(...), { needsFull: false })` (the form behaviour is needed in calm mode too).

- [ ] **Step 1: Write the failing e2e test**

```ts
// site/tests/e2e/letter.spec.ts
import { expect, test } from "@playwright/test";

test("the letter is a real labelled form", async ({ page }) => {
  await page.goto("/contact");
  await expect(page.getByLabel("Message")).toBeVisible();
  await expect(page.getByRole("group", { name: "What is it about?" })).toBeVisible();
  await expect(page.getByRole("radio", { name: "A role" })).toBeChecked();
  await expect(page.getByLabel("Your email")).toBeVisible();
  await expect(page.getByRole("button", { name: "Seal and send" })).toBeVisible();
});

test("shows field errors and focuses the first invalid field", async ({ page }) => {
  await page.goto("/contact");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page.getByText("Write a few words first.")).toBeVisible();
  await expect(page.getByLabel("Message")).toBeFocused();
  await expect(page.getByLabel("Message")).toHaveAttribute("aria-invalid", "true");
});

test("sends with JavaScript and announces success", async ({ page }) => {
  await page.route("**/api/contact", (r) => r.fulfill({ json: { ok: true } }));
  await page.goto("/contact");
  await page.getByLabel("Message").fill("Hi Din, a test letter.");
  await page.getByLabel("Your email").fill("ada@example.com");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page.getByRole("heading", { name: "Sent. Thank you." })).toBeFocused();
  await page.getByRole("button", { name: "Write another" }).click();
  await expect(page.getByLabel("Message")).toHaveValue("");
});

test("keeps the letter and explains when sending fails", async ({ page }) => {
  await page.route("**/api/contact", (r) => r.fulfill({ status: 502, json: { ok: false, code: "send" } }));
  await page.goto("/contact");
  await page.getByLabel("Message").fill("Hi Din.");
  await page.getByLabel("Your email").fill("ada@example.com");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page.locator(".letter-status")).toContainText("din@dins.dev");
  await expect(page.getByLabel("Message")).toHaveValue("Hi Din.");
});

test.describe("without JavaScript", () => {
  test.use({ javaScriptEnabled: false });
  test("still submits, and lands on the fallback page with Din's email", async ({ page }) => {
    await page.goto("/contact");
    await page.getByLabel("Message").fill("Hi Din, no JS here.");
    await page.getByLabel("Your email").fill("ada@example.com");
    await page.getByRole("button", { name: "Seal and send" }).click();
    await expect(page).toHaveURL(/\/contact\/not-sent\/$/);
    await expect(page.getByRole("link", { name: "din@dins.dev" })).toBeVisible();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site test:e2e tests/e2e/letter.spec.ts`
Expected: FAIL (labels and pages not found).

- [ ] **Step 3: Build the component, the enhancer's plain behaviour and the two pages**

`Letter.astro` renders the markup contract above with the sketch's paper look (surface card, ruled lines as a static background on the textarea, "Dear Din," in Fraunces at H3, "From" row) and no motion. `letter.css` uses tokens only; the reason radios are visually chips (the input is visually hidden but focusable; `:focus-visible + span` shows the teal ring; checked uses `--color-accent-soft` background and `--color-accent` text). Transitions are limited to `opacity` and `transform` (no `transition: all`).

`letter-enhance.ts` in this task:

```ts
// site/src/lib/setpieces/letter/letter-enhance.ts
import { parseContact, type ContactField } from "../../contact/parse";
import { loadTurnstile } from "../../turnstile-client";

export function enhance(section: HTMLElement): void {
  const form = section.querySelector<HTMLFormElement>("form.letter")!;
  const status = form.querySelector<HTMLElement>(".letter-status")!;
  const sentPanel = section.querySelector<HTMLElement>(".letter-sent")!;
  const box = form.querySelector<HTMLElement>(".turnstile")!;
  let widgetId: string | undefined;
  let busy = false;

  loadTurnstile()
    .then((ts) => { widgetId = ts.render(box, { sitekey: box.dataset.sitekey!, action: "contact", appearance: "interaction-only" }); })
    .catch(() => { status.textContent = "The spam check did not load. You can write to din@dins.dev instead."; });

  const fields: ContactField[] = ["message", "email", "name"];
  const showErrors = (errors: Partial<Record<ContactField, string>>) => {
    for (const f of fields) {
      const input = form.elements.namedItem(f) as HTMLInputElement | null;
      const err = section.querySelector<HTMLElement>(`#letter-${f}-error`);
      if (!input || !err) continue;
      err.textContent = errors[f] ?? "";
      if (errors[f]) input.setAttribute("aria-invalid", "true");
      else input.removeAttribute("aria-invalid");
    }
    const first = fields.find((f) => errors[f]);
    if (first) (form.elements.namedItem(first) as HTMLElement).focus();
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (busy) return;
    const data = new FormData(form);
    const parsed = parseContact(data);
    if (!parsed.ok) return showErrors(parsed.errors);
    showErrors({});
    busy = true;
    form.setAttribute("aria-busy", "true");
    status.textContent = "Sending.";
    try {
      const res = await fetch(form.action, { method: "POST", body: data, headers: { accept: "application/json" } });
      const body = (await res.json().catch(() => ({}))) as { ok?: boolean; errors?: Partial<Record<ContactField, string>> };
      if (res.ok && body.ok) {
        status.textContent = "";
        form.hidden = true;
        sentPanel.hidden = false;
        sentPanel.querySelector<HTMLElement>("h3")!.focus();
      } else if (body.errors) {
        status.textContent = "";
        showErrors(body.errors);
      } else {
        status.textContent = "That didn’t go through. Try again in a minute, or write to din@dins.dev.";
      }
    } catch {
      status.textContent = "That didn’t go through. Try again in a minute, or write to din@dins.dev.";
    } finally {
      busy = false;
      form.removeAttribute("aria-busy");
      if (widgetId !== undefined) window.turnstile?.reset(widgetId);
    }
  });

  sentPanel.querySelector(".again")!.addEventListener("click", () => {
    form.reset();
    sentPanel.hidden = true;
    form.hidden = false;
    (form.elements.namedItem("message") as HTMLElement).focus();
  });
}
```

Boot it from `Letter.astro`:

```astro
<script>
  import { bootPiece } from "../../../lib/setpieces/lazy";
  const el = document.querySelector<HTMLElement>('[data-piece="letter"]');
  if (el) bootPiece(el, () => import("../../../lib/setpieces/letter/letter-enhance"), { needsFull: false });
</script>
```

`sent.astro` ("Sent. Thank you." plus a link home) and `not-sent.astro` ("The letter didn’t go through. The spam check needs JavaScript, or something went wrong on my side. Write to me at din@dins.dev, or go back and try again." with a `mailto:` link) use the base layout with `<meta name="robots" content="noindex">`. Exclude both from the sitemap with the integration's `filter`.

The e2e "sends with JavaScript" test routes `/api/contact`, so it does not need Turnstile to pass; the Turnstile widget itself is exercised in Task 23 against the preview with the always-pass test key.

- [ ] **Step 4: Run the e2e test**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/letter.spec.ts`
Expected: PASS (5 tests).

- [ ] **Step 5: Run everything and commit**

Run: `./check.sh` (expected green, budget unchanged except the small letter stub).

```bash
git add site/src/components/home/letter site/src/lib/setpieces/letter/letter-enhance.ts site/src/pages/contact site/src/pages/index.astro site/src/pages/contact.astro site/astro.config.mjs site/tests/e2e/letter.spec.ts
git add site/src/lib/turnstile-client.ts 2>/dev/null || true
git commit -m "feat(site): the plain letter form on home and /contact"
```

- [ ] **Step 6: Foundation PR**

Ask Din for the go to push `feat/m4-set-pieces` and open the PR "M4 foundation and contact delivery". After Din has set `CONTACT_TO` with `pnpm --dir site exec wrangler secret put CONTACT_TO --env preview`, send one real letter on the preview and confirm it reaches Din's inbox. If Cloudflare returns `E_RECIPIENT_NOT_ALLOWED` for `din@dins.dev`, see Open question 2. Record the result in the ledger.

---

## Part C. Gate 1: the lens intro and the letter field

Set `RELEASES.lens = "preview"` at the start of Task 8 (and delete nothing yet).

### Task 8: Field words from the approved library

**Files:**
- Create: `site/src/lib/setpieces/field/words.ts`
- Test: `site/tests/unit/field-words.test.ts`

**Interfaces:**
- Produces: `extractFieldWords(texts: string[], opts?: { max?: number; minLength?: number; maxLength?: number }): string[]` (lowercase ASCII words, most frequent first, ties alphabetical, stop words and pure numbers removed, defaults `max 160`, `minLength 4`, `maxLength 14`).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/field-words.test.ts
import { describe, expect, it } from "vitest";
import { extractFieldWords } from "../../src/lib/setpieces/field/words";

describe("extractFieldWords", () => {
  it("ranks words by frequency, then alphabetically", () => {
    expect(extractFieldWords(["pipelines and evals", "evals with dbt and spark", "spark evals"]))
      .toEqual(["evals", "spark", "pipelines"]);
  });
  it("drops stop words, short words, numbers and long tokens", () => {
    const words = extractFieldWords(["this that with from 2026 sql abc supercalifragilistic retrieval"]);
    expect(words).toEqual(["retrieval"]);
  });
  it("keeps only ASCII so every glyph exists in the canvas atlas", () => {
    expect(extractFieldWords(["données pipelines"])).toEqual(["pipelines"]);
  });
  it("splits emails and URLs into plain words", () => {
    expect(extractFieldWords(["din@dins.dev https://github.com/dinsdev"])).toEqual(["dins", "dinsdev", "github"]);
  });
  it("caps the list", () => {
    const text = Array.from({ length: 300 }, (_, i) => `word${String.fromCharCode(97 + (i % 26))}${String.fromCharCode(97 + Math.floor(i / 26))}`).join(" ");
    expect(extractFieldWords([text], { max: 50 })).toHaveLength(50);
  });
  it("returns an empty list for an empty library", () => {
    expect(extractFieldWords([])).toEqual([]);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/field-words.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/setpieces/field/words.ts
// Words for the letter field, taken from Din's approved library at build time.
const STOP = new Set([
  "about", "after", "also", "been", "before", "being", "both", "could", "does", "each", "from", "have", "here",
  "into", "just", "like", "made", "make", "many", "more", "most", "much", "only", "other", "over", "same", "some",
  "such", "than", "that", "their", "them", "then", "there", "these", "they", "this", "those", "through", "very",
  "want", "were", "what", "when", "where", "which", "while", "will", "with", "would", "your", "https", "http",
]);

export function extractFieldWords(
  texts: string[],
  opts: { max?: number; minLength?: number; maxLength?: number } = {},
): string[] {
  const { max = 160, minLength = 4, maxLength = 14 } = opts;
  const counts = new Map<string, number>();
  for (const text of texts) {
    for (const w of text.toLowerCase().split(/[^a-z0-9À-ɏ]+/)) {
      if (w.length < minLength || w.length > maxLength) continue;
      if (!/^[a-z0-9]+$/.test(w) || /^\d+$/.test(w) || STOP.has(w)) continue;
      counts.set(w, (counts.get(w) ?? 0) + 1);
    }
  }
  return [...counts]
    .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
    .slice(0, max)
    .map(([w]) => w);
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/field-words.test.ts`
Expected: PASS (6 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/field/words.ts site/tests/unit/field-words.test.ts site/src/lib/setpieces/flags.ts
git commit -m "feat(site): letter field words from the approved library"
```

### Task 9: Letter field model (pure)

**Files:**
- Create: `site/src/lib/setpieces/field/model.ts`
- Test: `site/tests/unit/field-model.test.ts`

**Interfaces:**
- Produces:
  - `GLYPHS = "01{}[]<>/=+-*.:;abcdefghijklmnopqrstuvwxyz"`.
  - `mulberry32(seed: number): () => number`.
  - `layoutRows(words: string[], cols: number, rows: number, seed: number): string[]` (each row exactly `cols` long, words never split across rows, single spaces between words).
  - `interface Field { cols: number; rows: number; cell: number; glyphs: Uint8Array; heat: Float32Array; text: string[]; warm: Set<number> }`.
  - `createField(o: { width: number; height: number; cell: number; words: string[]; seed: number }): Field`.
  - `stepField(f: Field, input: { pointer: { x: number; y: number } | null; sweepX: number | null }, k?: number): number[]` (returns dirty cell indices; radius 130 px; sweep band 160 px).
  - `charAt(f: Field, i: number): string` (the word layer character when `heat > 0.08`, else the glyph).
  - `flicker(f: Field, rand: () => number, n: number): number[]`.
  - `advanceSweep(x: number | null, dtMs: number, width: number, active: boolean): number | null` (speed 1.5 px per ms; restarts at -200 while active; returns null once past `width + 200` when inactive).
  - `FLICKER_IDLE_MS = 5000`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/field-model.test.ts
import { describe, expect, it } from "vitest";
import { advanceSweep, charAt, createField, flicker, layoutRows, mulberry32, stepField } from "../../src/lib/setpieces/field/model";

const WORDS = ["pipelines", "evals", "retrieval", "spark", "schemas"];

describe("layoutRows", () => {
  it("fills each row to exactly cols with whole words", () => {
    const rows = layoutRows(WORDS, 40, 6, 1);
    expect(rows).toHaveLength(6);
    for (const r of rows) {
      expect(r).toHaveLength(40);
      for (const token of r.trim().split(/\s+/)) expect(WORDS).toContain(token);
    }
  });
  it("is deterministic for a seed", () => {
    expect(layoutRows(WORDS, 30, 3, 7)).toEqual(layoutRows(WORDS, 30, 3, 7));
  });
  it("gives blank rows when no word fits", () => {
    expect(layoutRows(["retrieval"], 5, 2, 1)).toEqual(["     ", "     "]);
    expect(layoutRows([], 5, 1, 1)).toEqual(["     "]);
  });
});

describe("stepField", () => {
  const make = () => createField({ width: 360, height: 180, cell: 18, words: WORDS, seed: 3 });

  it("warms cells near the pointer and leaves far cells alone", () => {
    const f = make();
    const dirty = stepField(f, { pointer: { x: 180, y: 90 }, sweepX: null });
    const center = 5 * f.cols + 10;
    expect(dirty).toContain(center);
    expect(f.heat[center]).toBeGreaterThan(0);
    expect(dirty).not.toContain(0);
  });
  it("shows word letters where the field is hot", () => {
    const f = make();
    for (let i = 0; i < 40; i++) stepField(f, { pointer: { x: 180, y: 90 }, sweepX: null });
    const center = 5 * f.cols + 10;
    expect(charAt(f, center)).toBe(f.text[5][10]);
  });
  it("cools down and goes quiet after the pointer leaves", () => {
    const f = make();
    for (let i = 0; i < 20; i++) stepField(f, { pointer: { x: 180, y: 90 }, sweepX: null });
    let dirty: number[] = [];
    for (let i = 0; i < 400; i++) dirty = stepField(f, { pointer: null, sweepX: null });
    expect(dirty).toEqual([]);
    expect(f.warm.size).toBe(0);
  });
  it("warms a vertical band during a sweep", () => {
    const f = make();
    const dirty = stepField(f, { pointer: null, sweepX: 90 });
    expect(dirty).toContain(0 * f.cols + 5);
    expect(dirty).toContain(9 * f.cols + 5);
  });
});

describe("flicker", () => {
  it("changes n glyphs and reports them dirty", () => {
    const f = createField({ width: 180, height: 90, cell: 18, words: WORDS, seed: 1 });
    expect(flicker(f, mulberry32(9), 6)).toHaveLength(6);
  });
});

describe("advanceSweep", () => {
  it("moves right at 1.5 px per ms", () => {
    expect(advanceSweep(0, 100, 1000, true)).toBe(150);
  });
  it("loops while retrieval is active and stops after the pass when not", () => {
    expect(advanceSweep(1199, 100, 1000, true)).toBe(-200);
    expect(advanceSweep(1199, 100, 1000, false)).toBeNull();
    expect(advanceSweep(null, 100, 1000, false)).toBeNull();
    expect(advanceSweep(null, 16, 1000, true)).toBe(-200);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/field-model.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/setpieces/field/model.ts
// The letter field: faint mono glyphs that resolve into real library words near
// the cursor and during Ottie's retrieval sweep. Pure, so it is tested without a canvas.
export const GLYPHS = "01{}[]<>/=+-*.:;abcdefghijklmnopqrstuvwxyz";
export const FLICKER_IDLE_MS = 5000;
const RADIUS = 130;
const BAND = 160;
const HOT = 0.08;

export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function layoutRows(words: string[], cols: number, rows: number, seed: number): string[] {
  const usable = words.filter((w) => w.length <= cols);
  const rand = mulberry32(seed);
  return Array.from({ length: rows }, () => {
    if (!usable.length) return " ".repeat(cols);
    let line = "";
    for (let tries = 0; tries < 8; tries++) {
      const w = usable[Math.floor(rand() * usable.length)];
      const next = line ? `${line} ${w}` : w;
      if (next.length > cols) continue;
      line = next;
      tries = -1;
    }
    return line.padEnd(cols, " ");
  });
}

export interface Field {
  cols: number; rows: number; cell: number;
  glyphs: Uint8Array; heat: Float32Array; text: string[]; warm: Set<number>;
}

export function createField(o: { width: number; height: number; cell: number; words: string[]; seed: number }): Field {
  const cols = Math.ceil(o.width / o.cell) + 1;
  const rows = Math.ceil(o.height / o.cell) + 1;
  const rand = mulberry32(o.seed);
  const glyphs = new Uint8Array(cols * rows).map(() => Math.floor(rand() * GLYPHS.length));
  return { cols, rows, cell: o.cell, glyphs, heat: new Float32Array(cols * rows), text: layoutRows(o.words, cols, rows, o.seed + 1), warm: new Set() };
}

export function stepField(
  f: Field,
  input: { pointer: { x: number; y: number } | null; sweepX: number | null },
  k = 0.12,
): number[] {
  const candidates = new Set(f.warm);
  const { pointer, sweepX } = input;
  if (pointer) {
    const x0 = Math.max(0, Math.floor((pointer.x - RADIUS) / f.cell)), x1 = Math.min(f.cols - 1, Math.ceil((pointer.x + RADIUS) / f.cell));
    const y0 = Math.max(0, Math.floor((pointer.y - RADIUS) / f.cell)), y1 = Math.min(f.rows - 1, Math.ceil((pointer.y + RADIUS) / f.cell));
    for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) candidates.add(y * f.cols + x);
  }
  if (sweepX !== null) {
    const x0 = Math.max(0, Math.floor((sweepX - BAND) / f.cell)), x1 = Math.min(f.cols - 1, Math.ceil((sweepX + BAND) / f.cell));
    for (let y = 0; y < f.rows; y++) for (let x = x0; x <= x1; x++) candidates.add(y * f.cols + x);
  }
  const dirty: number[] = [];
  for (const i of candidates) {
    const px = (i % f.cols) * f.cell, py = Math.floor(i / f.cols) * f.cell;
    let target = 0;
    if (pointer) { const d = Math.hypot(px - pointer.x, py - pointer.y); if (d < RADIUS) target = 1 - d / RADIUS; }
    if (sweepX !== null) { const d = Math.abs(px - sweepX); if (d < BAND) target = Math.max(target, (1 - d / BAND) * 0.8); }
    const before = f.heat[i];
    let after = before + (target - before) * k;
    if (target === 0 && after < 0.002) after = 0;
    f.heat[i] = after;
    if (after > 0) f.warm.add(i); else f.warm.delete(i);
    if (Math.abs(after - before) > 0.004 || (after === 0 && before !== 0) || (before <= HOT) !== (after <= HOT)) dirty.push(i);
  }
  return dirty;
}

export function charAt(f: Field, i: number): string {
  if (f.heat[i] > HOT) return f.text[Math.floor(i / f.cols)][i % f.cols];
  return GLYPHS[f.glyphs[i]];
}

export function flicker(f: Field, rand: () => number, n: number): number[] {
  const out: number[] = [];
  for (let k = 0; k < n; k++) {
    const i = Math.floor(rand() * f.glyphs.length);
    f.glyphs[i] = Math.floor(rand() * GLYPHS.length);
    out.push(i);
  }
  return out;
}

export function advanceSweep(x: number | null, dtMs: number, width: number, active: boolean): number | null {
  if (x === null) return active ? -200 : null;
  const next = x + dtMs * 1.5;
  if (next <= width + 200) return next;
  return active ? -200 : null;
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/field-model.test.ts`
Expected: PASS (10 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/field/model.ts site/tests/unit/field-model.test.ts
git commit -m "feat(site): letter field model with words, heat and sweep"
```

### Task 10: Letter field renderer and component

**Files:**
- Create: `site/src/lib/setpieces/field/renderer.ts`, `site/src/lib/setpieces/field/ask-bridge.ts`, `site/src/lib/setpieces/field/field-enhance.ts`
- Create: `site/src/components/home/LetterField.astro`, `site/src/components/home/letter-field.css`
- Modify: the hero component from M1 (render `<LetterField />` as the first child of the hero, behind the content)
- Test: `site/tests/e2e/setpieces-loading.spec.ts` (first two tests)

**Interfaces:**
- Consumes: `createField`, `stepField`, `charAt`, `flicker`, `advanceSweep`, `mulberry32`, `FLICKER_IDLE_MS` (Task 9); `extractFieldWords` (Task 8); `pieceEnabled("lens")` (Task 2); `bootPiece` (Task 3); `onMotionChange` (Task 1).
- Produces: `onAskState(fn: (phase: string) => void): () => void` in `ask-bridge.ts` (listens to `window` `ask:state`); `startField(canvas: HTMLCanvasElement, words: string[]): { stop(): void }` in `renderer.ts`; `enhance(section)` in `field-enhance.ts`.

Implementation notes (visual work; Din judges it in the preview):
- `LetterField.astro` frontmatter: `const enabled = pieceEnabled("lens")`; if false, render nothing. Else `getCollection("library", (e) => Boolean(e.data.approved_on) && !e.data.sample)`, `extractFieldWords(entries.map((e) => e.body ?? ""))`; if that yields fewer than 20 words, add words from published projects' `title` and `stack`. Render `<canvas class="letter-field" aria-hidden="true" data-piece="field" data-words={JSON.stringify(words)}></canvas>` positioned `absolute; inset: 0; pointer-events: none; z-index: 0` inside the hero (not fixed to the window), plus the boot script `bootPiece(el, () => import(".../field-enhance"))` (needs full motion).
- Calm version: no canvas script at all, so the hero shows plain paper. (A static faint field was considered; plain paper is calmer and costs nothing.)
- Renderer: wait for `document.fonts.load('500 12px "JetBrains Mono"')` (with a 1.5 s timeout, then the fallback mono). Build two glyph atlases (ink at 0.055 alpha base, accent) on an `OffscreenCanvas` when available, else a detached canvas, once per theme; rebuild on `data-theme` attribute changes and on the `prefers-color-scheme` media change. Cell 18 px on wide screens, 22 px under 760 px. DPR capped at 2. Each frame: `stepField`, plus `flicker(6)` only while the last pointer or touch was under `FLICKER_IDLE_MS` ago, then for each dirty index `clearRect` the cell and `drawImage` the glyph from the matching atlas with `globalAlpha = 0.08 + heat * 0.55` for hot cells. The loop stops itself (no `requestAnimationFrame`) when there is no recent input, no sweep and `warm` is empty, and restarts on `pointermove`, `pointerdown` or an `ask:state` "retrieving". An IntersectionObserver stops it when the hero is off screen; `visibilitychange` stops it in hidden tabs. `ResizeObserver` (debounced 150 ms) rebuilds the field and redraws everything once.
- Touch: a `pointerdown` with `pointerType === "touch"` sets the pointer for 1.2 s, then clears it, so the words bloom where the visitor tapped and fade.
- Sweep: `onAskState` sets `retrieving = phase === "retrieving"`; `advanceSweep` uses it as `active`, so the current pass finishes after retrieval ends.
- `onMotionChange`: switching to calm calls `stop()` and clears the canvas.
- Every draw happens inside `requestAnimationFrame`; no work in the `pointermove` handler beyond storing the coordinates.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// site/tests/e2e/setpieces-loading.spec.ts
import { expect, test } from "@playwright/test";

test("the letter field draws in full motion and is hidden from assistive tech", async ({ page }) => {
  await page.goto("/");
  const canvas = page.locator("canvas.letter-field");
  await expect(canvas).toHaveAttribute("aria-hidden", "true");
  await page.mouse.move(400, 300);
  await page.waitForTimeout(300);
  const painted = await canvas.evaluate((c: HTMLCanvasElement) => {
    const d = c.getContext("2d")!.getImageData(0, 0, c.width, c.height).data;
    for (let i = 3; i < d.length; i += 4) if (d[i] > 0) return true;
    return false;
  });
  expect(painted).toBe(true);
});

test("calm mode loads no field script", async ({ page }) => {
  const requested: string[] = [];
  page.on("request", (r) => requested.push(r.url()));
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("html")).toHaveAttribute("data-motion", "calm");
  expect(requested.some((u) => /field-enhance/.test(u))).toBe(false);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-loading.spec.ts`
Expected: FAIL (no canvas).

- [ ] **Step 3: Implement the renderer, the bridge, the enhancer and the component as described**

`ask-bridge.ts`:

```ts
// site/src/lib/setpieces/field/ask-bridge.ts
// M3's Ask island announces its phase on window as "ask:state". Only this file knows the name.
export function onAskState(fn: (phase: string) => void): () => void {
  const handler = (e: Event) => fn(String((e as CustomEvent<{ phase?: string }>).detail?.phase ?? ""));
  window.addEventListener("ask:state", handler);
  return () => window.removeEventListener("ask:state", handler);
}
```

- [ ] **Step 4: Run the e2e tests, the budget and the perf spec**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-loading.spec.ts && pnpm --dir site budget && pnpm --dir site test:e2e --grep @perf`
Expected: 2 e2e PASS; budget exits 0 (the field chunk is lazy but small; the boot stub is in the initial graph); perf PASS with no long tasks.

- [ ] **Step 5: Check the sweep by hand**

Run `pnpm --dir site dev`, open the home page, and in the console run `window.dispatchEvent(new CustomEvent("ask:state", { detail: { phase: "retrieving" } }))`, then the same with `"done"` after a few seconds. Expected: the teal band sweeps left to right and repeats while retrieving, then finishes its pass and stops. Once M3 has merged, ask a real question instead.

- [ ] **Step 6: Commit**

```bash
git add site/src/lib/setpieces/field site/src/components/home/LetterField.astro site/src/components/home/letter-field.css site/src/components site/tests/e2e/setpieces-loading.spec.ts
git commit -m "feat(site): letter field canvas behind the hero"
```

### Task 11: Lens intro, then Gate 1 review

**Files:**
- Create: `site/src/components/home/LensIntro.astro`, `site/src/components/home/lens-intro.css`
- Modify: `site/src/components/home/MotionHead.astro` (also set `data-intro="play"`), `site/src/layouts/BaseLayout.astro` (wrap page content in `<div class="page">` if M1 has no such wrapper), `site/src/pages/index.astro` (render `<LensIntro />` once)
- Test: `site/tests/e2e/setpieces-calm.spec.ts` (lens tests)

**Interfaces:**
- Consumes: `resolveMotion` (Task 1), `pieceEnabled("lens")` (Task 2), the lens marks `brand/logo/lens-light.svg` and `brand/logo/lens-dark.svg`.
- Produces: `<html data-intro="play">` while the intro runs (set before first paint only when motion is full, the lens piece is enabled, the page is the home page and `sessionStorage["dins:intro-seen"]` is unset); removed on `animationend` of the lens, after 1,600 ms at most, or at once on `keydown`, `wheel`, `touchstart` or `pointerdown`.

Implementation notes:
- `MotionHead.astro` takes a prop `intro: boolean` (true only on the home page and only when `pieceEnabled("lens")`); the inline script adds, inside the same try block: `if(${intro}&&mode==="full"){try{if(!sessionStorage.getItem("dins:intro-seen")){sessionStorage.setItem("dins:intro-seen","1");document.documentElement.dataset.intro="play"}}catch(e){}}`.
- `LensIntro.astro` renders `<div class="lens-intro" aria-hidden="true">` with both lens SVGs inline (light shown in light theme, dark shown in dark theme, never recolored), and an inline end script (`is:inline`, under 400 bytes) that removes `data-intro` on the events listed above.
- CSS, all under `:root[data-intro="play"]`: the lens fades and scales in (`opacity 0 to 1`, `scale(0.92) to scale(1)`, 420 ms), then scales to 26 through the right lens (`transform-origin: 73.3% 50%`, 950 ms, the sketch's `cubic-bezier(.7,0,.2,1)`), fading in its last 30 percent. The page wrapper starts at `opacity: 0.6; transform: scale(1.035)` and settles to `opacity: 1; transform: none` over 1,000 ms with the brand ease. No `filter`. The overlay never blocks input (`pointer-events: none`), so the Ask input works during the intro.
- First paint shows the hero content at 60 percent opacity at least, so Resume, Email, GitHub and LinkedIn are visible on first paint (PRD 2.2).
- Note for review: while the page wrapper has a transform, a fixed or sticky header inside it is positioned relative to the wrapper. The intro lasts about one second, so this is acceptable; if Din sees the nav jump, move the transform to `main` only.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// site/tests/e2e/setpieces-calm.spec.ts
import { expect, test } from "@playwright/test";

test("the lens intro plays once per session and ends on a key press", async ({ page }) => {
  await page.goto("/", { waitUntil: "commit" });
  await expect(page.locator("html")).toHaveAttribute("data-intro", "play");
  await page.keyboard.press("Tab");
  await expect(page.locator("html")).not.toHaveAttribute("data-intro", /.*/);
  await page.reload();
  await expect(page.locator("html")).not.toHaveAttribute("data-intro", /.*/);
});

test("no lens intro under reduced motion, Save-Data or ?calm", async ({ browser }) => {
  const reduced = await browser.newPage({ reducedMotion: "reduce" });
  await reduced.goto("/");
  await expect(reduced.locator("html")).not.toHaveAttribute("data-intro", /.*/);

  const saveData = await browser.newPage();
  await saveData.addInitScript(() => Object.defineProperty(navigator, "connection", { value: { saveData: true } }));
  await saveData.goto("/");
  await expect(saveData.locator("html")).toHaveAttribute("data-motion", "calm");
  await expect(saveData.locator("html")).not.toHaveAttribute("data-intro", /.*/);

  const calm = await browser.newPage();
  await calm.goto("/?calm");
  await expect(calm.locator("html")).not.toHaveAttribute("data-intro", /.*/);
});

test("the hero links are visible on first paint during the intro", async ({ page }) => {
  await page.goto("/");
  for (const name of ["Resume", "Email", "GitHub", "LinkedIn"])
    await expect(page.getByRole("link", { name }).first()).toBeVisible();
});

test("other pages never play the intro", async ({ page }) => {
  await page.goto("/work");
  await expect(page.locator("html")).not.toHaveAttribute("data-intro", /.*/);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-calm.spec.ts`
Expected: the first test FAILS (no `data-intro`).

- [ ] **Step 3: Implement the intro as described, then run the tests**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-calm.spec.ts && pnpm --dir site exec vitest run tests/unit/motion-properties.test.ts`
Expected: PASS (4 e2e, motion guard PASS).

- [ ] **Step 4: Commit**

```bash
git add site/src/components/home/LensIntro.astro site/src/components/home/lens-intro.css site/src/components/home/MotionHead.astro site/src/layouts/BaseLayout.astro site/src/pages/index.astro site/tests/e2e/setpieces-calm.spec.ts
git commit -m "feat(site): lens intro through Ottie's right lens"
```

- [ ] **Step 5: Gate 1 evidence**

Run: `./check.sh && pnpm --dir site test:e2e --grep @shots && pnpm --dir site test:e2e --grep @perf`
Expected: green; shots in `site/test-results/shots/lens/`; perf JSON with `longTasks: []`.

- [ ] **Step 6: Gate 1 PR (with Din's go)**

Push, open "M4 gate 1: lens intro and letter field", attach the lens shots (laptop and phone, light and dark, full and calm) and the perf JSON. Note in the PR body: the blur in the sketch is replaced by opacity and scale (Decisions).

- [ ] **Step 7: Din reviews the preview**

Din checks on the preview link: the intro on a fresh tab, the field near the cursor, the sweep while Ottie retrieves (once M3 is merged), `?calm`, a phone, and the 2020 laptop with DevTools Performance open (no red long-task markers while moving the mouse).

- [ ] **Step 8: Record the outcome**

If Din approves: set `RELEASES.lens = "full"`, delete the "ships with nothing full" test from Task 2, and add a ledger entry quoting Din. If Din asks for changes, make them on the same branch and repeat Steps 5 to 7.

```bash
git add site/src/lib/setpieces/flags.ts site/tests/unit/flags.test.ts docs/WORK_LEDGER.md
git commit -m "feat(site): lens and letter field approved by Din"
```

---

## Part D. Gate 2: windows (the project stage)

Set `RELEASES.windows = "preview"` at the start of Task 12.

### Task 12: Stage pose math (pure)

**Files:**
- Create: `site/src/lib/setpieces/stage/pose.ts`
- Test: `site/tests/unit/pose.test.ts`

**Interfaces:**
- Produces: `interface Pose { y: number; z: number; rx: number; ry: number; scale: number; opacity: number }` (`y` in percent of the window's height, `z` in px, angles in degrees); `DWELL = 0.12`; `windowPose(progress: number, index: number, count: number): Pose`; `activeIndex(progress: number, count: number): number`; `progressForIndex(index: number, count: number): number`; `poseToTransform(p: Pose): string`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/pose.test.ts
import { describe, expect, it } from "vitest";
import { activeIndex, DWELL, poseToTransform, progressForIndex, windowPose } from "../../src/lib/setpieces/stage/pose";

const identity = { y: 0, z: 0, rx: 0, ry: 0, scale: 1, opacity: 1 };

describe("windowPose", () => {
  it("shows the first window flat and in focus at the start", () => {
    expect(windowPose(0, 0, 3)).toEqual(identity);
  });
  it("holds the window still inside its dwell zone", () => {
    const nudge = (DWELL * 0.9) / 2; // progress units for 3 windows: one segment is 0.5
    expect(windowPose(0.5 + nudge, 1, 3)).toEqual(identity);
  });
  it("keeps the next window below, tilted and invisible", () => {
    const p = windowPose(0, 1, 3);
    expect(p.y).toBeGreaterThan(0);
    expect(p.rx).toBeGreaterThan(0);
    expect(p.opacity).toBe(0);
    expect(p.z).toBeLessThan(0);
  });
  it("sends the previous window up and away", () => {
    const p = windowPose(1, 1, 3);
    expect(p).toEqual(identity);
    const prev = windowPose(1, 0, 3);
    expect(prev.y).toBeLessThan(0);
    expect(prev.opacity).toBe(0);
  });
  it("clamps progress outside 0 to 1", () => {
    expect(windowPose(-1, 0, 3)).toEqual(windowPose(0, 0, 3));
    expect(windowPose(2, 2, 3)).toEqual(windowPose(1, 2, 3));
  });
  it("treats a single window as always in focus", () => {
    expect(windowPose(0.7, 0, 1)).toEqual(identity);
  });
  it("never returns negative zero", () => {
    for (const v of Object.values(windowPose(0, 0, 3))) expect(Object.is(v, -0)).toBe(false);
  });
});

describe("activeIndex and progressForIndex", () => {
  it("round-trip for every window", () => {
    for (const count of [2, 3, 4])
      for (let i = 0; i < count; i++) expect(activeIndex(progressForIndex(i, count), count)).toBe(i);
  });
  it("switches halfway between windows", () => {
    expect(activeIndex(0.24, 3)).toBe(0);
    expect(activeIndex(0.26, 3)).toBe(1);
  });
  it("is 0 for a single window", () => {
    expect(progressForIndex(0, 1)).toBe(0);
    expect(activeIndex(0.9, 1)).toBe(0);
  });
});

describe("poseToTransform", () => {
  it("writes one transform string", () => {
    expect(poseToTransform(identity)).toBe("translate3d(0, 0%, 0px) rotateX(0deg) rotateY(0deg) scale(1)");
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/pose.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/setpieces/stage/pose.ts
// Where each project window sits for a given scroll progress through the stage.
export interface Pose { y: number; z: number; rx: number; ry: number; scale: number; opacity: number }
export const DWELL = 0.12;

const clamp = (v: number, a: number, b: number) => Math.min(b, Math.max(a, v));
const z0 = (v: number) => (v === 0 ? 0 : v);
const r = (v: number) => z0(Math.round(v * 1000) / 1000);

export function windowPose(progress: number, index: number, count: number): Pose {
  if (count <= 1) return { y: 0, z: 0, rx: 0, ry: 0, scale: 1, opacity: 1 };
  const p = clamp(progress, 0, 1) * (count - 1);
  const raw = p - index;
  const d = Math.sign(raw) * Math.max(0, Math.abs(raw) - DWELL);
  const a = Math.abs(d);
  return {
    y: r(clamp(-d * 115, -140, 140)),
    z: r(-a * 260),
    rx: r(clamp(-d * 22, -30, 30)),
    ry: r(clamp(d * 12, -16, 16)),
    scale: r(1 - Math.min(a, 1) * 0.06),
    opacity: r(clamp(1.4 - a * 2.6, 0, 1)),
  };
}

export function activeIndex(progress: number, count: number): number {
  if (count <= 1) return 0;
  return clamp(Math.round(clamp(progress, 0, 1) * (count - 1)), 0, count - 1);
}

export function progressForIndex(index: number, count: number): number {
  return count <= 1 ? 0 : clamp(index / (count - 1), 0, 1);
}

export function poseToTransform(p: Pose): string {
  return `translate3d(0, ${p.y}%, ${p.z}px) rotateX(${p.rx}deg) rotateY(${p.ry}deg) scale(${p.scale})`;
}
```

Check against the "keeps the next window below" test: at progress 0, index 1, `raw = -1`, `d = -0.88`, so `y = 101.2` (below), `rx = 19.36` (tilted back), `opacity = 0` (1.4 minus 2.288 clamps to 0). This matches the sketch's camera.

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/pose.test.ts`
Expected: PASS (11 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/stage/pose.ts site/tests/unit/pose.test.ts site/src/lib/setpieces/flags.ts
git commit -m "feat(site): project stage pose math"
```

### Task 13: Windows markup, the GSAP enhancer and keyboard access

**Files:**
- Create: `site/src/components/home/WorkStage.astro`, `site/src/components/home/work-stage.css`
- Create: `site/src/lib/setpieces/stage/stage-enhance.ts`
- Modify: `site/src/pages/index.astro` (work section uses `<WorkStage />`), global styles (`overflow-x: clip` on `html, body` if missing)
- Test: `site/tests/e2e/setpieces-keyboard.spec.ts`, more cases in `site/tests/e2e/setpieces-loading.spec.ts`

**Interfaces:**
- Consumes: `windowPose`, `activeIndex`, `progressForIndex`, `poseToTransform` (Task 12); `{ gsap, ScrollTrigger }` (Task 3); `bootPiece` with `guardLayout: true` (Task 3); `onMotionChange` (Task 1); `pieceEnabled("windows")` (Task 2).
- Produces: the markup contract:
  - `<section id="work" class="stage" data-piece="windows" style="--n: N">` with an `<h2>` "Selected work", then `<ol class="stage-list">` of N `<li class="stage-item" data-i="i">`, each holding `<article>` with the caption (`<h3>` title, summary, tag list, `<a class="more" href="/work/<slug>">View project</a>`) and `<div class="win">` (window chrome with an `aria-hidden` `dins.dev/work/<slug>` address bar, and the stage capture: `<video muted playsinline loop preload="none" poster=... aria-label="<title> demo">` or `<img loading="lazy" decoding="async" width height alt="">`). The window is not `aria-hidden`, because the calm version's video has native controls and axe rejects focusable content inside `aria-hidden`.
  - A "Pause demos" toggle button (`aria-pressed`) shown only when any capture is a video.
  - The progress rail `<div class="rail" aria-hidden="true">` with N ticks.
  - Classes set by the enhancer: `.is-full` on the section, `.is-active` on the active `li`, `.is-on` on the active rail tick.

Data: `getCollection("projects", (p) => p.data.status === "published" && typeof p.data.featured === "number")`, sorted by `featured`, first 4. With 0 projects the component renders nothing (no heading, no empty section); with 1 project it renders the calm layout only and never boots the enhancer.

Layout:
- Calm (default, phones, reduced motion, JavaScript off, flag off): the `ol` is a plain list. On phones each item is the window (flat, 16:10) with the caption below it, stacked. On wider screens the calm list is two columns: caption left, window right, one row per project, with the sketch's hairline separators. Videos show their poster with native controls (no autoplay).
- Full (only `.stage.is-full`, which the enhancer adds; the CSS also requires `@media (min-width: 761px)`): the section's height becomes `calc(var(--n) * 90vh + 100vh)`; an inner `.stage-sticky` is `position: sticky; top: 0; height: 100vh`; the list items stack in place on a 2-column grid (captions absolutely positioned in the left column, windows absolutely positioned in a `perspective: 1800px` scene on the right). Non-active captions have `opacity: 0` and `transform: translateY(18px)` with a 500 ms transition on transform and opacity only; the active caption is `opacity: 1; transform: none`.
- Depth without blur: a window's opacity and scale come from `windowPose`; the inactive windows also get `.is-dim` (a static darker hairline and shadow, not animated).

Enhancer (`stage-enhance.ts`) outline:

```ts
// site/src/lib/setpieces/stage/stage-enhance.ts
import { gsap, ScrollTrigger } from "../gsap";
import { activeIndex, poseToTransform, progressForIndex, windowPose } from "./pose";

export function enhance(section: HTMLElement): void {
  const items = [...section.querySelectorAll<HTMLElement>(".stage-item")];
  const wins = items.map((li) => li.querySelector<HTMLElement>(".win")!);
  const ticks = [...section.querySelectorAll<HTMLElement>(".rail i")];
  const videos = items.map((li) => li.querySelector<HTMLVideoElement>("video"));
  const n = items.length;
  let paused = false;
  let active = -1;

  const mm = gsap.matchMedia();
  mm.add("(min-width: 761px) and (prefers-reduced-motion: no-preference)", () => {
    section.classList.add("is-full");
    ScrollTrigger.refresh();
    const state = { p: 0 };
    const apply = () => {
      wins.forEach((w, i) => {
        const pose = windowPose(state.p, i, n);
        w.style.transform = poseToTransform(pose);
        w.style.opacity = String(pose.opacity);
      });
      const a = activeIndex(state.p, n);
      if (a !== active) {
        active = a;
        items.forEach((li, i) => li.classList.toggle("is-active", i === a));
        ticks.forEach((t, i) => t.classList.toggle("is-on", i === a));
        videos.forEach((v, i) => { if (!v) return; if (i === a && !paused) v.play().catch(() => {}); else v.pause(); });
      }
    };
    const tween = gsap.to(state, {
      p: 1, ease: "none", onUpdate: apply,
      scrollTrigger: {
        trigger: section, start: "top top", end: "bottom bottom", scrub: 0.6,
        onToggle: (self) => { section.classList.toggle("is-live", self.isActive); if (!self.isActive) videos.forEach((v) => v?.pause()); },
      },
    });
    apply();
    // Keyboard: focusing a project's link brings that project into focus. No trap: Tab leaves normally.
    const onFocus = (e: FocusEvent) => {
      const li = (e.target as HTMLElement).closest<HTMLElement>(".stage-item");
      if (!li) return;
      const st = tween.scrollTrigger!;
      const y = st.start + (st.end - st.start) * progressForIndex(Number(li.dataset.i), n);
      window.scrollTo({ top: y, behavior: "instant" });
    };
    section.addEventListener("focusin", onFocus);
    return () => {
      section.removeEventListener("focusin", onFocus);
      tween.scrollTrigger?.kill();
      tween.kill();
      section.classList.remove("is-full", "is-live");
      items.forEach((li) => li.classList.remove("is-active"));
      wins.forEach((w) => { w.style.transform = ""; w.style.opacity = ""; });
      videos.forEach((v) => v?.pause());
      active = -1;
    };
  });

  section.querySelector<HTMLButtonElement>(".pause-demos")?.addEventListener("click", (e) => {
    paused = !paused;
    (e.currentTarget as HTMLElement).setAttribute("aria-pressed", String(paused));
    videos.forEach((v, i) => { if (!v) return; if (paused || i !== active) v.pause(); else v.play().catch(() => {}); });
  });
}
```

`gsap.matchMedia` reverts everything (the cleanup function) when the media query stops matching, which covers both a live reduced-motion switch and resizing to phone width. `bootPiece` (Task 3) keeps `data-motion` current.

`will-change: transform, opacity` is set only under `.stage.is-live .win` so the layers exist only while the stage is on screen.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// site/tests/e2e/setpieces-keyboard.spec.ts
import { expect, test } from "@playwright/test";

test("Tab reaches every project link in the pinned stage, each visible, and then leaves", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await page.keyboard.press("Escape");
  const links = page.locator("#work a.more");
  const count = await links.count();
  test.skip(count < 2, "needs at least two published featured projects");
  for (let i = 0; i < 80; i++) {
    await page.keyboard.press("Tab");
    if (await links.first().evaluate((el) => el === document.activeElement)) break;
  }
  for (let i = 0; i < count; i++) {
    const link = links.nth(i);
    await expect(link).toBeFocused();
    await page.waitForTimeout(700);
    await expect(link).toBeInViewport();
    expect(await link.evaluate((el) => Number(getComputedStyle(el.closest("article")!).opacity))).toBeGreaterThan(0.9);
    await page.keyboard.press("Tab");
  }
  expect(await page.evaluate(() => document.activeElement?.closest("#work") === null)).toBe(true);
});

test("Shift+Tab walks back through the stage too", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  const links = page.locator("#work a.more");
  const count = await links.count();
  test.skip(count < 2, "needs at least two published featured projects");
  await links.nth(count - 1).focus();
  for (let i = count - 2; i >= 0; i--) {
    await page.keyboard.press("Shift+Tab");
    await expect(links.nth(i)).toBeFocused();
  }
});
```

Add to `setpieces-loading.spec.ts`:

```ts
test("the stage script loads only near the stage", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const requested: string[] = [];
  page.on("request", (r) => requested.push(r.url()));
  await page.goto("/");
  await page.waitForLoadState("networkidle");
  expect(requested.some((u) => /stage-enhance/.test(u))).toBe(false);
  await page.locator("#work").scrollIntoViewIfNeeded();
  await expect.poll(() => requested.some((u) => /stage-enhance/.test(u))).toBe(true);
});

test("jumping past the stage before its script arrives keeps it calm (no jump)", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.route(/stage-enhance/, async (r) => { await new Promise((res) => setTimeout(res, 1500)); await r.continue(); });
  await page.goto("/#contact");
  const before = await page.evaluate(() => document.querySelector("#contact")!.getBoundingClientRect().top);
  await page.waitForTimeout(2500);
  const after = await page.evaluate(() => document.querySelector("#contact")!.getBoundingClientRect().top);
  expect(Math.abs(after - before)).toBeLessThan(1);
  await expect(page.locator("#work")).not.toHaveClass(/is-full/);
});

test("phones get the flat stack with no pinning", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.locator("#work").scrollIntoViewIfNeeded();
  await page.waitForTimeout(1000);
  await expect(page.locator("#work")).not.toHaveClass(/is-full/);
});

test("turning on reduced motion live returns the stage to the list", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  for (let y = 0; y < 6; y++) await page.mouse.wheel(0, 900);
  await expect(page.locator("#work")).toHaveClass(/is-full/);
  await page.emulateMedia({ reducedMotion: "reduce" });
  await expect(page.locator("#work")).not.toHaveClass(/is-full/);
  expect(await page.locator("#work .win").first().evaluate((w) => (w as HTMLElement).style.transform)).toBe("");
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-keyboard.spec.ts tests/e2e/setpieces-loading.spec.ts`
Expected: the new tests FAIL (no `.stage-item`, no `stage-enhance` chunk).

- [ ] **Step 3: Build the component, the CSS and the enhancer as described**

Boot from `WorkStage.astro` only when `pieceEnabled("windows")` and there are at least 2 projects:

```astro
<script>
  import { bootPiece } from "../../lib/setpieces/lazy";
  const el = document.querySelector<HTMLElement>('[data-piece="windows"]');
  if (el && el.dataset.enhance === "1") bootPiece(el, () => import("../../lib/setpieces/stage/stage-enhance"), { guardLayout: true });
</script>
```

(`data-enhance="1"` is rendered by the frontmatter when the flag is on and there are 2 or more projects.)

- [ ] **Step 4: Run the tests, the motion guard, axe and the budget**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-keyboard.spec.ts tests/e2e/setpieces-loading.spec.ts && pnpm --dir site exec vitest run tests/unit/motion-properties.test.ts && pnpm --dir site budget`
Expected: all PASS; budget prints the GSAP chunk under "lazy" only and exits 0. Run M1's axe spec on `/` and `/?calm` (expected zero violations).

Before M1's real projects exist, the e2e tests that need 2 projects skip; run them locally against M1's sample drafts by building with drafts visible if M1 provides that switch, and say so in the PR.

- [ ] **Step 5: Commit**

```bash
git add site/src/components/home/WorkStage.astro site/src/components/home/work-stage.css site/src/lib/setpieces/stage/stage-enhance.ts site/src/pages/index.astro site/src/styles site/tests/e2e
git commit -m "feat(site): scroll-driven project stage with a flat phone stack"
```

### Task 14: Gate 2 review

- [ ] **Step 1: Evidence**

Run: `./check.sh && pnpm --dir site test:e2e --grep @shots && pnpm --dir site test:e2e --grep @perf`
Expected: green; shots in `site/test-results/shots/windows/` at progress 0, 0.25, 0.5, 0.75 and 1; perf JSON with no long tasks.

- [ ] **Step 2: PR (with Din's go)**

Push and open "M4 gate 2: windows". Attach the shots and perf JSON. List the decisions to judge: no blur, no snap, dwell zone 12 percent, sticky instead of pin.

- [ ] **Step 3: Din reviews the preview**

On the 2020 laptop: scroll the stage with a trackpad and with the keyboard (Space, Page Down, Tab), watch the demo play only in the focused window, try "Pause demos". On a mid-range phone: the flat stack. With `?calm`: the two-column list.

- [ ] **Step 4: Record the outcome**

On approval: `RELEASES.windows = "full"`, a ledger entry quoting Din, commit `feat(site): project stage approved by Din`.

---

## Part E. Gate 3: paper (writing cards)

Set `RELEASES.paper = "preview"` at the start of Task 15.

### Task 15: Paper cards, the drift enhancer and empty states

**Files:**
- Create: `site/src/components/home/PaperStack.astro`, `site/src/components/home/PaperCard.astro`, `site/src/components/home/paper.css`
- Create: `site/src/lib/setpieces/paper/paper-enhance.ts`
- Modify: `site/src/pages/index.astro` (writing section uses `<PaperStack />`)
- Test: more cases in `site/tests/e2e/setpieces-loading.spec.ts`

**Interfaces:**
- Consumes: `{ gsap }` (Task 3), `bootPiece` with `guardLayout: true` (Task 3), `pieceEnabled("paper")` (Task 2).
- Produces: `<section id="writing" class="paper-section" data-piece="paper">` with `<h2>` "Behind the work", an "All writing" link, and `<ul class="papers">` of up to 3 `<li class="paper" style="--r: <deg>; --dy: <px>">` each wrapping `<a class="sheet" href="/writing/<slug>">` (motif, kind label, date in `<time>`, `<h3>` title, summary, "Read" with an `aria-hidden` arrow). If M1 already has a writing card component, `PaperCard.astro` wraps it instead of duplicating its markup.

Behaviour:
- Data: published `writing` entries sorted by `date` descending, first 3. 0 posts: the section is not rendered. 1 or 2 posts: rendered as-is with no empty slots.
- Fixed per-slot values so the layout is stable: `--r` is `-3.2deg`, `2.4deg`, `-1.6deg`; `--dy` is `140px`, `220px`, `170px`; slot 2 has `margin-top: 56px` and slot 3 `20px` on wide screens.
- Calm (default): cards sit in their settled pose (rotation `calc(var(--r) * 0.35)`) or flat on phones; hover and focus change only the border color and shadow to teal (static, no lift).
- Full (`.paper-section.is-full`, wide screens, full motion): each `li` gets `gsap.fromTo(li, { y: dy, rotate: r, opacity: 0 }, { y: 0, rotate: r * 0.35, opacity: 1, ease: "none", scrollTrigger: { trigger: section, start: "top bottom", end: \`top ${30 + i * 12}%\`, scrub: 0.5 } })`, so the three cards arrive at different speeds and settle. Hover (`@media (hover: hover)`) and `:focus-within` lift the inner `.sheet` with `transform: translateY(-10px) rotate(calc(var(--r) * -1)) scale(1.02)` and set the siblings to `opacity: 0.72; transform: scale(0.985)` (no blur), 600 ms spring on transform, 400 ms on opacity.
- `gsap.matchMedia` reverts the tweens on phone widths and under reduced motion.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// add to site/tests/e2e/setpieces-loading.spec.ts
test("paper cards settle once the section is in view", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  const cards = page.locator("#writing li.paper");
  test.skip((await cards.count()) === 0, "needs published writing");
  for (let y = 0; y < 30; y++) await page.mouse.wheel(0, 600);
  await page.locator("#writing").scrollIntoViewIfNeeded();
  await page.evaluate(() => window.scrollBy(0, window.innerHeight * 0.6));
  await page.waitForTimeout(1200);
  for (const t of await cards.evaluateAll((els) => els.map((e) => new DOMMatrix(getComputedStyle(e).transform).m42)))
    expect(Math.abs(t)).toBeLessThan(2);
});

test("the writing section is absent when nothing is published", async ({ page }) => {
  await page.goto("/");
  const count = await page.locator("#writing li.paper").count();
  if (count === 0) await expect(page.locator("#writing")).toHaveCount(0);
  else expect(count).toBeLessThanOrEqual(3);
});

test("keyboard focus on a card shows it like hover", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  const first = page.locator("#writing a.sheet").first();
  test.skip((await first.count()) === 0, "needs published writing");
  await first.focus();
  await expect(first).toBeFocused();
  expect(await first.evaluate((el) => getComputedStyle(el).outlineStyle)).not.toBe("none");
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-loading.spec.ts`
Expected: the new tests FAIL or fail on missing `#writing li.paper` structure.

- [ ] **Step 3: Build the component and the enhancer as described**

- [ ] **Step 4: Run the tests, the guard and the budget**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-loading.spec.ts && pnpm --dir site exec vitest run tests/unit/motion-properties.test.ts && pnpm --dir site budget`
Expected: PASS, budget exits 0.

- [ ] **Step 5: Commit**

```bash
git add site/src/components/home/PaperStack.astro site/src/components/home/PaperCard.astro site/src/components/home/paper.css site/src/lib/setpieces/paper site/src/pages/index.astro site/tests/e2e/setpieces-loading.spec.ts site/src/lib/setpieces/flags.ts
git commit -m "feat(site): floating paper cards for the latest writing"
```

### Task 16: Gate 3 review

- [ ] **Step 1:** Run `./check.sh`, the `@shots` (paper at 0, 0.5, 1) and `@perf` specs.
- [ ] **Step 2:** With Din's go, push and open "M4 gate 3: paper" with the shots and perf JSON.
- [ ] **Step 3:** Din reviews: the drift speeds and the settle on a laptop, hover and keyboard focus, the phone stack, `?calm`.
- [ ] **Step 4:** On approval: `RELEASES.paper = "full"`, ledger entry quoting Din, commit `feat(site): paper approved by Din`.

---

## Part F. Gate 4: the studio (about)

Set `RELEASES.studio = "preview"` at the start of Task 17.

### Task 17: Studio frame math, terminal lines and the studio palette (pure and tested)

**Files:**
- Create: `site/src/lib/setpieces/studio/frame.ts`
- Create: `site/src/components/home/studio/terminal.ts`
- Create: `site/src/components/home/studio/studio.css` (only the custom properties block in this task)
- Test: `site/tests/unit/studio-frame.test.ts`, `site/tests/unit/terminal-lines.test.ts`, `site/tests/unit/studio-tokens.test.ts`

**Interfaces:**
- Produces:
  - `interface StudioFrame { open: number; power: number; zoom: number; typed: number; head: number; cta: boolean }` (all 0 to 1 except `cta`); `studioFrame(p: number): StudioFrame` (`open = smooth((p - 0.1) / 0.32)`, `power = smooth((p - 0.3) / 0.14)`, `zoom = smooth((p - 0.6) / 0.3)`, `typed = clamp01((p - 0.38) / 0.3)`, `head = 1 - smooth((p - 0.08) / 0.16)`, `cta = p > 0.86`, with `smooth(x) = x * x * (3 - 2 * x)` on a clamped `x`).
  - `revealCounts(lengths: number[], typed: number): number[]` (characters visible per line; lines fill in order; `typed = 1` shows everything).
  - `interface TermLine { kind: "command" | "output" | "muted"; text: string }`; `PROMPT = "din@dins ~ % "`; `TERMINAL: readonly TermLine[]`; `MAX_COLS = 56`.
  - CSS custom properties in `studio.css`: `--studio-paper`, `--studio-surface`, `--studio-ink`, `--studio-muted`, `--studio-accent`.

- [ ] **Step 1: Write the failing tests**

```ts
// site/tests/unit/studio-frame.test.ts
import { describe, expect, it } from "vitest";
import { revealCounts, studioFrame } from "../../src/lib/setpieces/studio/frame";

describe("studioFrame", () => {
  it("starts closed, dark and wide", () => {
    expect(studioFrame(0)).toEqual({ open: 0, power: 0, zoom: 0, typed: 0, head: 1, cta: false });
  });
  it("ends open, lit, zoomed in, fully typed, with the call to action", () => {
    expect(studioFrame(1)).toEqual({ open: 1, power: 1, zoom: 1, typed: 1, head: 0, cta: true });
  });
  it("unfolds before it types and types before it zooms", () => {
    expect(studioFrame(0.42).open).toBe(1);
    expect(studioFrame(0.42).typed).toBeGreaterThan(0);
    expect(studioFrame(0.6).zoom).toBe(0);
    expect(studioFrame(0.68).typed).toBe(1);
  });
  it("is monotonic", () => {
    let prev = studioFrame(0);
    for (let p = 0.01; p <= 1; p += 0.01) {
      const f = studioFrame(p);
      for (const k of ["open", "power", "zoom", "typed"] as const) expect(f[k]).toBeGreaterThanOrEqual(prev[k]);
      prev = f;
    }
  });
});

describe("revealCounts", () => {
  it("shows nothing at 0 and everything at 1", () => {
    expect(revealCounts([3, 4], 0)).toEqual([0, 0]);
    expect(revealCounts([3, 4], 1)).toEqual([3, 4]);
  });
  it("fills lines in order", () => {
    expect(revealCounts([3, 4], 0.5)).toEqual([3, 0]);
    expect(revealCounts([3, 4], 0.75)).toEqual([3, 2]);
  });
  it("clamps outside 0 to 1", () => {
    expect(revealCounts([2], -1)).toEqual([0]);
    expect(revealCounts([2], 2)).toEqual([2]);
  });
});
```

```ts
// site/tests/unit/terminal-lines.test.ts
import { describe, expect, it } from "vitest";
import { MAX_COLS, PROMPT, TERMINAL } from "../../src/components/home/studio/terminal";

describe("terminal lines", () => {
  it("fit the screen without wrapping, prompt included", () => {
    for (const l of TERMINAL) expect((l.kind === "command" ? PROMPT : "").length + l.text.length).toBeLessThanOrEqual(MAX_COLS);
  });
  it("run whoami and cat about.txt", () => {
    const commands = TERMINAL.filter((l) => l.kind === "command").map((l) => l.text);
    expect(commands.slice(0, 2)).toEqual(["whoami", "cat about.txt"]);
  });
  it("follow the writing rules", () => {
    for (const l of TERMINAL) {
      expect(l.text).not.toMatch(/[\u2014\u2013]/);
      expect(l.text).not.toMatch(/\b(elevate|seamless|unleash|journey|tapestry|passionate)\b/i);
      expect(l.text).not.toMatch(/placeholder|lorem|todo/i);
    }
  });
});
```

```ts
// site/tests/unit/studio-tokens.test.ts
// The studio is always dark; its colors must stay the brand's dark tokens.
import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const css = readFileSync(new URL("../../src/components/home/studio/studio.css", import.meta.url), "utf8");
const tokens = JSON.parse(readFileSync(new URL("../../../brand/tokens/tokens.json", import.meta.url), "utf8"));

describe("studio palette", () => {
  for (const [prop, key] of [["--studio-paper", "paper"], ["--studio-surface", "surface"], ["--studio-ink", "ink"], ["--studio-muted", "muted"], ["--studio-accent", "accent"]]) {
    it(`${prop} equals the dark ${key} token`, () => {
      const m = new RegExp(`${prop}:\\s*([^;]+);`).exec(css);
      expect(m?.[1].trim().toLowerCase()).toBe(String(tokens.color.dark[key]).toLowerCase());
    });
  }
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site exec vitest run tests/unit/studio-frame.test.ts tests/unit/terminal-lines.test.ts tests/unit/studio-tokens.test.ts`
Expected: FAIL, modules and file missing.

- [ ] **Step 3: Write the implementations**

```ts
// site/src/lib/setpieces/studio/frame.ts
const clamp01 = (x: number) => Math.min(1, Math.max(0, x));
const smooth = (x: number) => { const c = clamp01(x); return c * c * (3 - 2 * c); };

export interface StudioFrame { open: number; power: number; zoom: number; typed: number; head: number; cta: boolean }

export function studioFrame(p: number): StudioFrame {
  return {
    open: smooth((p - 0.1) / 0.32),
    power: smooth((p - 0.3) / 0.14),
    zoom: smooth((p - 0.6) / 0.3),
    typed: clamp01((p - 0.38) / 0.3),
    head: 1 - smooth((p - 0.08) / 0.16),
    cta: p > 0.86,
  };
}

export function revealCounts(lengths: number[], typed: number): number[] {
  let left = Math.floor(clamp01(typed) * lengths.reduce((a, b) => a + b, 0));
  return lengths.map((n) => { const shown = Math.min(n, left); left -= shown; return shown; });
}
```

```ts
// site/src/components/home/studio/terminal.ts
// What the studio's terminal shows. Drafted from Din's approved library; Din approves the wording in the gate PR.
export interface TermLine { kind: "command" | "output" | "muted"; text: string }
export const PROMPT = "din@dins ~ % ";
export const MAX_COLS = 56;
export const TERMINAL: readonly TermLine[] = [
  { kind: "command", text: "whoami" },
  { kind: "output", text: "Din. Data and ML engineer." },
  { kind: "command", text: "cat about.txt" },
  { kind: "output", text: "I build pipelines that turn messy data into" },
  { kind: "output", text: "decisions, then put models on top of them." },
  { kind: "muted", text: "Languages: English, French. Also fluent in SQL." },
  { kind: "command", text: "open about" },
];
```

The lines above are a draft taken from the sketch. Before the gate PR, replace them with wording drawn from approved library entries (the master's plan line only if the library says it) and ask Din to approve the exact text in the PR.

```css
/* site/src/components/home/studio/studio.css */
/* The studio is always dark. These equal the dark tokens in brand/tokens/tokens.json (tested). */
.studio {
  --studio-paper: #1F1E1C;
  --studio-surface: #2A2926;
  --studio-ink: #ECE9E2;
  --studio-muted: #A29E95;
  --studio-accent: #5CBFB8;
}
```

- [ ] **Step 4: Run them to verify they pass**

Run: `pnpm --dir site exec vitest run tests/unit/studio-frame.test.ts tests/unit/terminal-lines.test.ts tests/unit/studio-tokens.test.ts`
Expected: PASS (7, 3 and 5 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/studio/frame.ts site/src/components/home/studio/terminal.ts site/src/components/home/studio/studio.css site/tests/unit/studio-frame.test.ts site/tests/unit/terminal-lines.test.ts site/tests/unit/studio-tokens.test.ts site/src/lib/setpieces/flags.ts
git commit -m "feat(site): studio frame math, terminal lines and the studio palette"
```

### Task 18: The studio set piece and `/about` opening on its screen

**Files:**
- Create: `site/src/components/home/studio/Studio.astro`, `site/src/components/home/studio/StudioScreen.astro`
- Modify: `site/src/components/home/studio/studio.css` (the rest of the styles)
- Create: `site/src/lib/setpieces/studio/studio-enhance.ts`
- Create: `site/src/styles/view-transitions.css` (imported by the base layout)
- Modify: `site/src/pages/index.astro` (about section uses `<Studio />`), `site/src/pages/about.astro` (renders `<StudioScreen />` as the page header, above M1's bio)
- Test: `site/tests/e2e/setpieces-calm.spec.ts` (studio cases)

**Interfaces:**
- Consumes: `studioFrame`, `revealCounts` (Task 17), `TERMINAL`, `PROMPT` (Task 17), `{ gsap }` (Task 3), `bootPiece` with `guardLayout: true`, `pieceEnabled("studio")`.
- Produces:
  - `StudioScreen.astro`: the terminal screen at its final state, `<div class="studio-screen" style="view-transition-name: studio-screen">` containing `<pre class="term">` with one `<span class="line" data-len="N">` per `TERMINAL` line (the prompt in a `.p` span for commands, muted lines in `.m`), each line followed by an `aria-hidden` `<span class="cover">`, and a cursor `<span class="cur" aria-hidden="true">`. On `/about` the screen is followed by the page `<h1>`.
  - `Studio.astro`: `<section id="about" class="studio" data-piece="studio">` with the heading (`<h2>` "Look closer." under an "About" label), the laptop (`.laptop > .lid > .face.front > StudioScreen` and `.face.back` with the lens mark, `.base` with keyboard and trackpad), and the link "Read the full story" to `/about` (a real `<a>`, always in the DOM).

Behaviour:
- Calm (default, reduced motion, JavaScript off, flag off): the section is one viewport tall and shows the screen state directly: the dark studio background with `StudioScreen` centered at full size, all text visible, "Read the full story" visible. No laptop transforms. This is the PRD's "About opening on the screen".
- Full (`.studio.is-full`, full motion; phones included, see Open question 9): the section is `340vh` (`240vh` under 760 px); `.studio-sticky` is sticky. The enhancer scrubs `state.p` from 0 to 1 over the section (`scrub: 0.5`) and on each update applies `studioFrame(state.p)`:
  - laptop: built at the final zoomed-in size (screen box filling the viewport) and scaled down: `scale = lerp(fitScale, 1, zoom)`, `rotateX = lerp(lerp(-50, -12, open), 0, zoom)`, `rotateY = lerp(lerp(-24, -14, open), 0, zoom)`, `translateY = lerp(-6vh, 0, zoom)`. Scaling down from the final size keeps the text sharp when the camera arrives.
  - lid: `rotateX = lerp(lerp(-89.5, 18, open), 0, zoom)`.
  - base: `opacity = 1 - zoom * 0.9`.
  - screen power: an overlay `.screen-off` in `--studio-paper` black with `opacity = 1 - (0.15 + power * 0.85)` (replaces the sketch's `filter: brightness`).
  - heading: `opacity = head`, `translateY = (1 - head) * -30px`.
  - typing: `revealCounts(lengths, typed)` gives characters per line; each line's `.cover` gets `transform: translateX(<count>ch)`. Each `.line` is `display: block; position: relative; overflow: hidden; white-space: pre`, and its cover is `position: absolute; inset: 0; background: var(--studio-paper)`, so sliding it right uncovers the characters from the left and the line clips it. The cursor moves with `transform: translate(<col>ch, <row * line-height>)`. Covers and cursor are `aria-hidden`; the text underneath is always complete, so screen readers and search see all of it.
  - "Read the full story": `.is-on` when `cta` (opacity and transform transition). It stays focusable at every progress; focusing it scrolls to progress 0.9 (no trap).
  - The cursor blinks 5 times after typing finishes and then stays solid (`animation-iteration-count: 5`, opacity only), to respect WCAG 2.2.2.
- `/about`: `StudioScreen` at the top in the same dark palette; with `@view-transition { navigation: auto; }` inside `@media (prefers-reduced-motion: no-preference)` in `view-transitions.css`, clicking "Read the full story" morphs the home screen into the `/about` header in browsers that support cross-document view transitions (Chrome and Safari 18.2 or later); others simply navigate. No JavaScript.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// add to site/tests/e2e/setpieces-calm.spec.ts
test("the calm studio opens on the screen with all its text", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/");
  const studio = page.locator("#about");
  await expect(studio.locator(".term")).toContainText("whoami");
  await expect(studio.locator(".term")).toContainText("cat about.txt");
  await expect(studio.getByRole("link", { name: "Read the full story" })).toBeVisible();
  expect(await studio.evaluate((s) => s.getBoundingClientRect().height)).toBeLessThanOrEqual(await page.evaluate(() => window.innerHeight * 1.2));
});

test("screen readers get the whole terminal text at any scroll position", async ({ page }) => {
  await page.goto("/");
  const text = await page.locator("#about .term").evaluate((el) => (el as HTMLElement).innerText);
  expect(text).toContain("cat about.txt");
  await expect(page.locator("#about .cover").first()).toHaveAttribute("aria-hidden", "true");
});

test("/about opens on the same screen", async ({ page }) => {
  await page.goto("/about");
  const screen = page.locator(".studio-screen").first();
  await expect(screen).toBeVisible();
  await expect(screen).toContainText("whoami");
  expect(await screen.evaluate((el) => getComputedStyle(el).viewTransitionName)).toBe("studio-screen");
});

test("the studio reaches its final frame at the end of the section", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  for (let y = 0; y < 12; y++) await page.mouse.wheel(0, 900);
  await expect(page.locator("#about")).toHaveClass(/is-full/);
  await page.evaluate(() => {
    const s = document.querySelector<HTMLElement>("#about")!;
    window.scrollTo({ top: s.offsetTop + s.offsetHeight - window.innerHeight, behavior: "instant" });
  });
  await page.waitForTimeout(900);
  await expect(page.locator("#about .studio-cta")).toHaveClass(/is-on/);
  const covers = await page.locator("#about .cover").evaluateAll((els) => els.map((e) => getComputedStyle(e).transform));
  expect(covers.every((t) => t !== "none")).toBe(true);
});
```

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-calm.spec.ts`
Expected: the studio tests FAIL.

- [ ] **Step 3: Build the components, CSS, enhancer and view transition as described**

The enhancer follows the same shape as `stage-enhance.ts`: `gsap.matchMedia().add("(prefers-reduced-motion: no-preference)", () => { section.classList.add("is-full"); ScrollTrigger.refresh(); ...; return cleanup; })`, where cleanup removes `.is-full`, kills the tween and clears every inline transform and opacity it set. Measure each line's length once from `data-len`. Use `gsap.quickSetter` for the per-frame laptop and lid transforms if a trace shows style recalculation cost; otherwise plain `style.transform` strings.

- [ ] **Step 4: Run the tests, guard, budget and perf**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/setpieces-calm.spec.ts && pnpm --dir site exec vitest run tests/unit && pnpm --dir site budget && pnpm --dir site test:e2e --grep @perf`
Expected: PASS; no long tasks while scrolling through the studio.

- [ ] **Step 5: Commit**

```bash
git add site/src/components/home/studio site/src/lib/setpieces/studio/studio-enhance.ts site/src/styles/view-transitions.css site/src/layouts/BaseLayout.astro site/src/pages/index.astro site/src/pages/about.astro site/tests/e2e/setpieces-calm.spec.ts
git commit -m "feat(site): the studio: laptop unfold, terminal and dolly into /about"
```

### Task 19: Gate 4 review

- [ ] **Step 1:** Run `./check.sh`, the `@shots` (studio at 0, 0.2, 0.45, 0.7, 1) and `@perf` specs.
- [ ] **Step 2:** With Din's go, push and open "M4 gate 4: studio" with the shots, the perf JSON and the exact terminal text for Din to approve.
- [ ] **Step 3:** Din reviews: the unfold, typing in step with the scroll (forwards and backwards), the sharpness of the text at the end of the dolly, "Read the full story" into `/about` with the view transition (Chrome and Safari), a mid-range phone (decide full or calm on phones), `?calm`.
- [ ] **Step 4:** On approval: `RELEASES.studio = "full"`, a ledger entry quoting Din (including the phone decision and the approved terminal text), commit `feat(site): studio approved by Din`.

---

## Part G. Gate 5: the letter (folding contact form)

Set `RELEASES.letter = "preview"` at the start of Task 20.

### Task 20: Letter state machine (pure)

**Files:**
- Create: `site/src/lib/setpieces/letter/machine.ts`
- Test: `site/tests/unit/letter-machine.test.ts`

**Interfaces:**
- Produces: `type Phase = "editing" | "sending" | "sealing" | "sent" | "failed"`; `interface LetterState { phase: Phase; error?: string }`; `type LetterEvent = { type: "submit" } | { type: "accepted" } | { type: "rejected"; error: string } | { type: "sealed" } | { type: "again" } | { type: "edit" }`; `INITIAL: LetterState`; `letterReducer(s: LetterState, e: LetterEvent): LetterState`; `phaseClasses(phase: Phase): string[]` (`editing` and `failed`: none; `sending`: `is-folding`, `is-tucked`; `sealing`: plus `is-closed`, `is-sealed`; `sent`: plus `is-away`); `FOLD_MS = 1050`, `SEAL_MS = 520`, `AWAY_MS = 900`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/letter-machine.test.ts
import { describe, expect, it } from "vitest";
import { INITIAL, letterReducer, phaseClasses, type LetterEvent, type LetterState } from "../../src/lib/setpieces/letter/machine";

const run = (events: LetterEvent[], s: LetterState = INITIAL) => events.reduce(letterReducer, s);

describe("letterReducer", () => {
  it("goes editing, sending, sealing, sent", () => {
    expect(run([{ type: "submit" }]).phase).toBe("sending");
    expect(run([{ type: "submit" }, { type: "accepted" }]).phase).toBe("sealing");
    expect(run([{ type: "submit" }, { type: "accepted" }, { type: "sealed" }]).phase).toBe("sent");
  });
  it("unfolds with an error when the server says no", () => {
    expect(run([{ type: "submit" }, { type: "rejected", error: "Try again." }])).toEqual({ phase: "failed", error: "Try again." });
  });
  it("can retry from failed, and editing clears the error", () => {
    const failed = run([{ type: "submit" }, { type: "rejected", error: "x" }]);
    expect(letterReducer(failed, { type: "submit" }).phase).toBe("sending");
    expect(letterReducer(failed, { type: "edit" })).toEqual({ phase: "editing" });
  });
  it("ignores a second submit while sending (no double send)", () => {
    const s = run([{ type: "submit" }]);
    expect(letterReducer(s, { type: "submit" })).toBe(s);
  });
  it("ignores events that do not fit the phase", () => {
    expect(letterReducer(INITIAL, { type: "accepted" })).toBe(INITIAL);
    expect(letterReducer(INITIAL, { type: "sealed" })).toBe(INITIAL);
  });
  it("writes another letter from sent", () => {
    expect(run([{ type: "submit" }, { type: "accepted" }, { type: "sealed" }, { type: "again" }])).toEqual(INITIAL);
  });
});

describe("phaseClasses", () => {
  it("adds fold steps in order", () => {
    expect(phaseClasses("editing")).toEqual([]);
    expect(phaseClasses("failed")).toEqual([]);
    expect(phaseClasses("sending")).toEqual(["is-folding", "is-tucked"]);
    expect(phaseClasses("sealing")).toEqual(["is-folding", "is-tucked", "is-closed", "is-sealed"]);
    expect(phaseClasses("sent")).toEqual(["is-folding", "is-tucked", "is-closed", "is-sealed", "is-away"]);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/letter-machine.test.ts`
Expected: FAIL, module not found.

- [ ] **Step 3: Write the implementation**

```ts
// site/src/lib/setpieces/letter/machine.ts
// The letter's phases. The fold starts while the request is in flight; the seal
// only stamps after the server accepts, and a refusal unfolds the letter again.
export type Phase = "editing" | "sending" | "sealing" | "sent" | "failed";
export interface LetterState { phase: Phase; error?: string }
export type LetterEvent =
  | { type: "submit" } | { type: "accepted" } | { type: "rejected"; error: string }
  | { type: "sealed" } | { type: "again" } | { type: "edit" };

export const INITIAL: LetterState = { phase: "editing" };
export const FOLD_MS = 1050;
export const SEAL_MS = 520;
export const AWAY_MS = 900;

export function letterReducer(s: LetterState, e: LetterEvent): LetterState {
  switch (s.phase) {
    case "editing":
      return e.type === "submit" ? { phase: "sending" } : s;
    case "failed":
      if (e.type === "submit") return { phase: "sending" };
      if (e.type === "edit") return { phase: "editing" };
      return s;
    case "sending":
      if (e.type === "accepted") return { phase: "sealing" };
      if (e.type === "rejected") return { phase: "failed", error: e.error };
      return s;
    case "sealing":
      return e.type === "sealed" ? { phase: "sent" } : s;
    case "sent":
      return e.type === "again" ? INITIAL : s;
  }
}

const STEPS = ["is-folding", "is-tucked", "is-closed", "is-sealed", "is-away"];
export function phaseClasses(phase: Phase): string[] {
  const n = { editing: 0, failed: 0, sending: 2, sealing: 4, sent: 5 }[phase];
  return STEPS.slice(0, n);
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/letter-machine.test.ts`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```bash
git add site/src/lib/setpieces/letter/machine.ts site/tests/unit/letter-machine.test.ts site/src/lib/setpieces/flags.ts
git commit -m "feat(site): letter phases for the fold and seal"
```

### Task 21: The folding letter, the envelope and Ottie

**Files:**
- Modify: `site/src/components/home/letter/Letter.astro` (envelope markup, a second Ottie mount), `site/src/components/home/letter/letter.css` (full-motion styles under `.letter-section.is-full`)
- Modify: `site/src/lib/setpieces/letter/letter-enhance.ts` (drive the phases)
- Create: `site/src/lib/setpieces/letter/ottie-bridge.ts`
- Test: more cases in `site/tests/e2e/letter.spec.ts`

**Interfaces:**
- Consumes: `letterReducer`, `phaseClasses`, `FOLD_MS`, `SEAL_MS`, `AWAY_MS` (Task 20); `parseContact` (Task 5); `currentMotion`, `onMotionChange` (Task 1); `pieceEnabled("letter")` (Task 2); M2's `cueOttie`, `prefetchOttie` and `<Ottie instance="letter" />`.
- Produces: `ottie-bridge.ts` exporting `pointAtLetter(): void`, `prefetchJump(): void`, `celebrateLetter(): void` (the only file that imports `site/src/ottie/events.ts`). Task 7's submit code is first refactored, with its tests still green, into helpers inside `letter-enhance.ts`: `send(data: FormData): Promise<{ ok: boolean; message: string; errors?: Partial<Record<ContactField, string>> }>`, `showStatus(text: string)`, `showErrors(errors)` and `showSentPanel()`; the calm and full paths both use them.

Markup additions (rendered only when `pieceEnabled("letter")`; the calm form from Task 7 is unchanged otherwise):
- `.envelope` around the form: `.env-back`, the form as `.sheet`, `.env-front` (static `clip-path` shape, never animated), `.env-flap` (rotated `rotateX(180deg)` open, `rotateX(0)` closed), `.wax` (the Ottie seal mark from `brand/logo/seal-light.svg` or `seal-dark.svg`, never recolored), all decorative parts `aria-hidden`.
- `<Ottie instance="letter" />` beside the envelope (M2's component; decorative, `aria-hidden`).

Motion (all transform and opacity):
- As the section rises into view (full motion only, guard with `canEnhance`): the sheet rises out of the envelope (`translateY(140px)` to `0`, scrubbed by ScrollTrigger over the section entering; GSAP is already loaded by earlier pieces or loads here).
- `is-folding`: the sheet `scaleY(0.36)` from `transform-origin: 50% 100%` with the crease overlay `opacity: 1` (650 ms); `is-tucked`: `translateY(236px) scaleY(0.36)` (400 ms); `is-closed`: the flap rotates closed (520 ms); `is-sealed`: the wax seal stamps (`scale(1.8)` and `opacity 0` to `scale(1)` and `opacity 1`, 520 ms spring); `is-away`: the envelope `translateX(80vw) translateY(-60px) rotate(9deg)` and `opacity: 0` (900 ms). While the letter is folded, the form's fields are `inert` so focus cannot land on a squashed field.
- The "Sent. Thank you." panel fades and rises in (`opacity`, `translateY(20px)` to `0`) and takes focus.

Enhancer flow (extends Task 7's submit handler; the calm path stays exactly as in Task 7):

```ts
// inside letter-enhance.ts, used only when the section has .is-full
let state = INITIAL;
const envelope = section.querySelector<HTMLElement>(".envelope")!;
const dispatch = (e: LetterEvent) => {
  state = letterReducer(state, e);
  envelope.classList.remove("is-folding", "is-tucked", "is-closed", "is-sealed", "is-away");
  envelope.classList.add(...phaseClasses(state.phase));
  form.inert = state.phase !== "editing" && state.phase !== "failed";
};
const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
// on a valid submit:
dispatch({ type: "submit" });
const [result] = await Promise.all([send(data), wait(FOLD_MS)]);
if (result.ok) {
  dispatch({ type: "accepted" });
  await wait(SEAL_MS);
  celebrateLetter();          // cueOttie("jump", { instance: "letter" })
  dispatch({ type: "sealed" });
  await wait(AWAY_MS);
  showSentPanel();            // same as Task 7: hide form, show panel, focus its heading
} else {
  dispatch({ type: "rejected", error: result.message });
  if (result.errors) showErrors(result.errors); else showStatus(result.message); // the form unfolds with the letter intact
  (form.elements.namedItem("message") as HTMLElement).focus();
}
```

Ottie cues: an IntersectionObserver (threshold 0.4) on the envelope calls `pointAtLetter()` once per page view; the first time the message is non-empty and the email passes `parseContact`'s check, `prefetchJump()` runs once (PRD section 4: the jump sheet is fetched when the letter is filled in); "Write another" resets the machine (`again`) and calls `pointAtLetter()` again. Ottie is quiet while someone types (M2's rule); the letter never shows a speech bubble of its own. "Carries it off": the envelope flies off while Ottie jumps (see Open question 3).

`onMotionChange` to calm: remove `.is-full`, clear all phase classes and inline transforms; a send in flight completes on the calm path.

- [ ] **Step 1: Write the failing e2e tests**

```ts
// add to site/tests/e2e/letter.spec.ts
test("full motion folds, seals and announces, and focus lands on the result", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.route("**/api/contact", async (r) => { await new Promise((res) => setTimeout(res, 300)); await r.fulfill({ json: { ok: true } }); });
  await page.goto("/");
  await page.locator("#contact").scrollIntoViewIfNeeded();
  await page.getByLabel("Message").fill("Hi Din, folding test.");
  await page.getByLabel("Your email").fill("ada@example.com");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page.locator(".envelope")).toHaveClass(/is-folding/);
  await expect(page.locator(".envelope")).toHaveClass(/is-sealed/);
  await expect(page.getByRole("heading", { name: "Sent. Thank you." })).toBeFocused();
});

test("a refused letter unfolds with the text intact", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.route("**/api/contact", (r) => r.fulfill({ status: 429, json: { ok: false, code: "rate" } }));
  await page.goto("/");
  await page.locator("#contact").scrollIntoViewIfNeeded();
  await page.getByLabel("Message").fill("Hi Din.");
  await page.getByLabel("Your email").fill("ada@example.com");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect(page.locator(".envelope")).not.toHaveClass(/is-folding/, { timeout: 3000 });
  await expect(page.getByLabel("Message")).toHaveValue("Hi Din.");
  await expect(page.getByLabel("Message")).toBeFocused();
});

test("Ottie is cued to point and then jump", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    (window as any).__cues = [];
    window.addEventListener("ottie:cue", (e) => (window as any).__cues.push((e as CustomEvent).detail.cue));
  });
  await page.route("**/api/contact", (r) => r.fulfill({ json: { ok: true } }));
  await page.goto("/");
  await page.locator("#contact").scrollIntoViewIfNeeded();
  await expect.poll(() => page.evaluate(() => (window as any).__cues)).toContain("point");
  await page.getByLabel("Message").fill("Hi Din.");
  await page.getByLabel("Your email").fill("ada@example.com");
  await page.getByRole("button", { name: "Seal and send" }).click();
  await expect.poll(() => page.evaluate(() => (window as any).__cues)).toContain("jump");
});
```

The last test relies on M2's `cueOttie` dispatching `ottie:cue` on `window` (as the M3 notes assume); if M2 picked another event, adjust the listener in the test only.

- [ ] **Step 2: Run them to verify they fail**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/letter.spec.ts`
Expected: the three new tests FAIL; the five Task 7 tests still PASS.

- [ ] **Step 3: Implement the envelope, the styles, the bridge and the enhancer flow as described**

- [ ] **Step 4: Run everything that touches the letter**

Run: `pnpm --dir site build && pnpm --dir site test:e2e tests/e2e/letter.spec.ts && pnpm --dir site exec vitest run tests/unit tests/worker && pnpm --dir site budget`
Expected: all PASS (8 e2e).

- [ ] **Step 5: Commit**

```bash
git add site/src/components/home/letter site/src/lib/setpieces/letter site/tests/e2e/letter.spec.ts
git commit -m "feat(site): the folding letter with the Ottie seal"
```

### Task 22: Gate 5 review and a real delivery

- [ ] **Step 1:** Run `./check.sh`, the `@shots` (letter at 0 and 1, plus a manual screenshot mid-fold) and `@perf` specs.
- [ ] **Step 2:** With Din's go, push and open "M4 gate 5: letter" with the shots and perf JSON.
- [ ] **Step 3:** On the preview (Turnstile test key, real `send_email`), Din sends one letter with JavaScript on and one with JavaScript off. Expected: the first arrives in Din's inbox with the visitor's address as reply-to and the right reason in the subject; the second lands on `/contact/not-sent/` and nothing is sent.
- [ ] **Step 4:** Din reviews the fold, seal and Ottie's point and jump on a laptop and a phone, a keyboard-only send, VoiceOver reading the success message once, and `?calm`.
- [ ] **Step 5:** On approval: `RELEASES.letter = "full"`, a ledger entry quoting Din with the delivery result, commit `feat(site): letter approved by Din`.

### Task 23: M4 close-out

**Files:**
- Modify: `docs/site/plans/M4-set-pieces.md` only to tick boxes (status lives in TASKS and the ledger, updated on merge as listed below)

- [ ] **Step 1: Whole-page checks with every approved piece on**

Run: `./check.sh && pnpm --dir site test:e2e && pnpm --dir site test:e2e --grep @perf`
Expected: green; the perf JSON for both profiles shows `longTasks: []`; the budget's initial total is at most 100 KB gzipped and lists no GSAP chunk.

- [ ] **Step 2: A full keyboard pass**

Run the keyboard spec plus one manual pass: Tab from the skip link to the footer on `/` in full motion and in calm; focus is always visible, never trapped, and never on a hidden element.

- [ ] **Step 3: Record the December 1 state**

On December 1, list each piece's release value in the ledger. Pieces still on `"preview"` ship calm in production with no code change; say so in the entry.

---

## Open questions for Din

1. **Contact form without JavaScript.** The PRD says the contact form still submits with JavaScript off, but Turnstile needs JavaScript, so the server cannot verify a no-JS post. This plan lets it submit and lands on `/contact/not-sent/` with a `mailto:din@dins.dev` link (and a `<noscript>` note on the form). The alternative is to accept unverified posts behind the honeypot and a stricter rate limit, which lets most spam bots through. Recommendation: the mailto fallback.
2. **Where the letters go.** On the free Workers plan, `send_email` only reaches verified destination addresses. `din@dins.dev` is a routing address, so Cloudflare may refuse it as a recipient (`E_RECIPIENT_NOT_ALLOWED`). The plan keeps the recipient in the `CONTACT_TO` secret, so if `din@dins.dev` is refused, the secret holds Din's verified personal inbox and nothing personal lands in the public repo. Task 7 Step 6 checks this with one real send.
3. **"Ottie carries it off."** Ottie has no carry state. The plan has the envelope fly off while Ottie jumps. Good enough for v1, or should a carry state be rendered after launch (like celebrate)?
4. **A second Ottie at the letter on the home page.** The hero Ottie is far away by the time the visitor reaches the letter. The plan mounts a second instance beside the envelope (only one is ever on screen). This needs M2's component to support two instances.
5. **What counts toward the 100 KB.** The plan gates the JavaScript loaded before any interaction (the initial module graph plus inline scripts) and reports the lazily loaded set-piece chunks (GSAP is about 45 KB gzipped of that) without gating them, since they load on scroll. If Din meant "everything the home page ever loads", the budget has to grow or GSAP has to go.
6. **Strict gates and the calendar.** Five sequential gates between November 13 and 29 leave about three days each, and each gate waits on Din's review. Recommendation: while Din reviews one piece, the next piece's pure-logic tasks (tests and math only, no visuals) may start. Is that within the "next starts after approval" rule?
7. **No blur.** The sketch's blurs (intro, out-of-focus windows, captions, unhovered cards) are replaced by opacity and scale to meet PRD section 6. Din judges whether the depth still reads in the preview.
8. **Lens intro once per session.** It plays once per browser session and not on every load. Should it instead play only on the first visit ever (like Ottie's run-in), or every time?
9. **The studio on phones.** The plan runs the full studio on phones (shorter, 240vh) and falls back to calm on phones if the mid-range phone trace drops frames. Din decides at Gate 4.
10. **Stage snap.** Off by default (dwell zones instead). Din can ask for snapping in the Gate 2 preview.

## Doc updates to apply on merge

- `docs/TASKS.md`: split 2.14 into rows with status: 2.14a foundation and contact delivery (`/api/contact`, plain letter), 2.14b lens and letter field, 2.14c windows, 2.14d paper, 2.14e studio, 2.14f letter. Each starts Planned; gates move to Accepted only on Din's word.
- `docs/site/PLAN.md` (M4): "`/api/contact` is built in M4's first PR (the contact endpoint is not a visual gate)"; "set pieces ship behind release flags in `site/src/lib/setpieces/flags.ts`; a piece not approved by December 1 stays on `preview`, which is calm in production"; "pinning uses CSS sticky with ScrollTrigger driving the timeline (no `pin`)".
- `docs/site/PLAN.md` (Dependencies on Din): add "Set the `CONTACT_TO` secret in preview and production (with M4's first PR)" and "Confirm one real letter arrives (end of M4's first PR)".
- `docs/WORK_LEDGER.md`: an entry for this plan's decisions (sticky over pin, blur replaced, Astro plus vanilla enhancers instead of Svelte islands for set pieces, release flags, contact first, intro once per session, transform-only typing) and the answers to the open questions.
- `docs/site/PRD.md`: no requirement changes proposed. If Din accepts Open question 1, section 6's failure-mode line could read "the contact form still submits, and without JavaScript it explains how to email Din directly". That wording change needs Din's approval.
- For M5's CSP work: the inline scripts from `MotionHead.astro` and `LensIntro.astro` need hashes; Turnstile needs `script-src` and `frame-src https://challenges.cloudflare.com`; the contact form posts to the same origin.
- For M1's sitemap: exclude `/contact/sent/` and `/contact/not-sent/`.
