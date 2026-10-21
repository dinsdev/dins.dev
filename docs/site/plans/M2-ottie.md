# M2 Ottie on the site: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

Status: Proposed (plan only, 2026-10-21). Nothing here is built yet. Task 2.12 in `docs/TASKS.md`. Amended the same day to match the shared contract in `docs/site/plans/README.md` ("Ottie (owner M2)"); where this plan and the contract differ, the contract wins.

**Goal:** Put the accepted 3D Ottie on dins.dev as a small, framework-free canvas player that plays the twelve states on their triggers, loads lazily without layout shift or long tasks, and gives M3 and M4 a tiny event interface to drive it.

**Architecture:** A TypeScript port of the approved preview player (`brand/ottie/preview/index.html`) split into pure, unit-tested modules (manifest geometry, the playback timeline, draw operations, the sheet loader, bubble rules, preferences and a "director" that turns cues and timers into commands) and a thin browser shell (canvas renderer, rAF loop, observers, DOM bubble). An Astro component renders the reserved box, the inline neutral still and the Quiet Ottie toggle; one bundled script boots the player. Other milestones talk to Ottie only through `site/src/ottie/events.ts`, which dispatches `ottie:cue` events on `window`.

**Tech Stack:** Astro 7.4 (component, `astro:assets` for the still), TypeScript 6.0, Canvas 2D, `createImageBitmap`, Vitest 4.1 (unit), Playwright 1.64 with `@axe-core/playwright` (end to end, performance), Cloudflare Workers static assets (`_headers` for caching). No new runtime dependencies.

**Spec:** `docs/site/PRD.md` section 4 (Ottie on the site) plus sections 6 and 7; `docs/site/PLAN.md` M2; `brand/ottie/README.md` (manifest fields); `docs/BRAND.md` (Ottie's voice, motion tokens). Decisions behind them: `docs/WORK_LEDGER.md`, 2026-10-21 entries.

## Global Constraints

- Versions pinned by the shared contract: Astro 7.4, TypeScript 6.0, Vitest 4.1, Playwright 1.64, Node 24 LTS, pnpm. The player adds no npm dependency.
- The player lives in `site/src/ottie/`, framework-free TypeScript; pure logic is separate from drawing and is written test first.
- Sheets come from `brand/ottie/dist/` and are served under `/ottie/` (set up by M0). Total 2,404,446 bytes; budget 2,500 KB with each sheet at most 400 KB (ledger, 2026-10-20).
- A typical visit loads about 0.6 to 0.9 MB of Ottie, not the full 2.4 MB.
- Ottie is about 25 to 30 percent of the hero's height and never the headline.
- Never in the way: Ottie never covers the input or the answer and stays silent while someone types or an answer streams.
- Bubbles: at most 90 characters, at most one every 20 seconds, from a reviewed lines file in the repo, never generated live.
- Tips: after about 20 seconds without interaction, one helpful line, at most 3 per visit. Nap after a minute with nothing happening, or lots of background clicking. Phones: smaller, below the questions, no tips or naps.
- "Quiet Ottie" toggle, remembered in `localStorage`: on screen but silent and still.
- Reduced motion: a still pose that changes with gentle crossfades. Save-Data or low-memory devices get the still Ottie.
- Decorative to screen readers (`aria-hidden`); anything useful Ottie says also exists in the real UI.
- Eyes do not follow the cursor.
- Smoothness: no layout shift, animate only transform, opacity and canvas, no main-thread task over 50 ms, at most 100 KB gzipped of first-party JavaScript on the home page before interaction (Ottie's share is capped at 15 KB gzipped by this plan).
- Failure modes: readable with JavaScript off; the still Ottie when a sheet fails.
- Writing: no em dashes, no en dashes as separators, no buzzwords (elevate, seamless, unleash, journey, tapestry, "not just X but Y"); Ottie talks about Din, never as Din; curly apostrophes in Ottie's lines.
- Commits: Conventional Commits, local only, no `Co-Authored-By` or any attribution line. Pushing, PRs and deploys need Din's go.

## Review Focus

The five conditions most likely to bite a visitor that the spec implies but does not spell out. Each has a test in the task named.

1. **Storage is blocked** (Safari private mode, strict privacy settings): Ottie still works, never greets on every page and never throws. Pinned in Task 8 (throwing storage) and Task 14 (pre-paint script).
2. **A sheet fails or is slow** (offline, flaky phone network): Ottie never vanishes or goes blank; the still shows, and on a first visit the hidden still comes back within 4 seconds. Pinned in Task 5 (loader failure), Task 12 (fallbacks) and Task 14 (aborted `run-in.webp`).
3. **Rapid repeated input** (poke spam, submit while an answer streams, a burst of cues): no stuck state, at most one bubble per 20 seconds, Ottie returns to idle. Pinned in Task 3 (play spam) and Task 9 (poke spam).
4. **JavaScript off or the player script fails**: the still keeps its reserved box, the Quiet toggle stays hidden. Pinned in Task 14 (`javaScriptEnabled: false`).
5. **Narrow or dense screens** (375 px, zoom, device pixel ratio 3): no horizontal scroll from the run-in canvas, Ottie never overlaps `[data-ottie-avoid]`, canvas stays sharp. Pinned in Task 14 (layout checks at 375 and 1280 px with `deviceScaleFactor: 3`).

Also pinned: a tab hidden for minutes never fast-forwards Ottie or fires a nap the moment it returns (Task 3 `advance` cap, Task 10 tick cap).

---

## Decisions made in this plan

These are Claude's calls to make the PRD buildable. Each is cheap to change; the ones that touch requirements are repeated under "Open questions for Din".

1. **Cues, not states, are the public interface.** M3 and M4 say what happened (`ask:submit`, `letter:sent`); the director decides what Ottie does. All the PRD rules (silent while typing, Quiet Ottie, reduced motion, phones) live in one tested module instead of being repeated by every caller.
2. **Sheet URLs carry a content version** (`/ottie/idle.webp?v=<8 hex>`, an FNV-1a hash of the manifest's state data, which includes every sheet's byte size), so `/ottie/*` can be cached for a year as `immutable` while keeping M0's plain `/ottie/` paths.
3. **The manifest is bundled** (about 10 KB, roughly 1.5 KB gzipped) rather than fetched, so the reserved box is computed at build time and there is no extra request.
4. **The inline still is aligned by measurement.** `brand/reference/ottie-3d-neutral.webp` is 720 x 880 at 2x the sheet's frame pixels (alpha bounding box 166,89 to 572,849 against idle drawing 0's 9,4 to 212,384), so its ground point is about (371.94, 823.18). It is resized at build time by `astro:assets` to 270 and 360 px wide (about 180 CSS px at size 1).
5. **First visits hide the still before paint** (a 6-line inline script sets `data-ottie-enter` on `<html>`), so run-in does not start with a duplicate Ottie already standing there. A CSS animation reveals the still after 4 seconds regardless, so a failed script can never hide Ottie for good.
6. **Greeting is per session:** the first session ever gets run-in, wave and "Hi, I’m Ottie."; a later session gets the wave on its first Ottie page; other pages in the same session start in idle. The 404 page opens with a shrug instead. Only a page with a greeting Ottie (home, project or devlog) marks the visit, so a visit that starts on `/contact` or the 404 page still gets the full greeting on the first greeting page. Decided (Din, 2026-10-21, open questions 2 and 8).
7. **Load order on a first visit is run-in, wave, idle** (decided by Din, 2026-10-21, open question 1) (the visitor sees nothing move until run-in is ready); otherwise idle, then wave, as the PRD says. Both stay under 0.9 MB (868 KB and 610 KB).
8. **Prefetch versus decode.** "Prefetch" only fetches bytes into memory; a sheet is decoded (off the main thread with `createImageBitmap`) only when it is about to play, and at most 4 decoded sheets are kept (idle always), so phones do not hold 90 MB of bitmaps.
9. **Thresholds** (constants, tuned by Din in the preview): tip after 20 s of quiet, talk prefetched at 15 s, nap prefetched at 45 s and played at 60 s, "lots of background clicking" is 6 clicks on non-interactive areas within 4 s, typing silences bubbles for 2 s after the last keystroke, one tip per quiet stretch.
10. **Reduced motion uses key poses**, one drawing per state (table in `poses.ts`, Din picks the final drawings in the lab): run-in, poke, talk and wake have no pose and are skipped; idle is the still image itself, so reduced motion never loads the idle sheet.
11. **Point is drawn toward screen right only** (ledger, 2026-10-20). The player can mirror it, but mirroring stays off (`MIRROR_POINT_APPROVED = false`) until Din approves it.
12. **A lab page** at `/lab/ottie` (plus `/project`, `/contact`, `/devlog`, `/404`, `/blank`) hosts the end-to-end tests and Din's review. It is built unless the shared build-time deploy (contract, "Build-time deploy") is `production`, with a `DINS_LABS` override.
13. **More than one Ottie on a page** (Din, 2026-10-21, M4 decision 4, in the contract): home has the hero Ottie (`context="home"`) and the letter Ottie in `#contact` (`context="contact"`); `/contact` has only the letter Ottie. One page controller runs every host: `ask:*` cues go to `home` and `project` hosts, `letter:*` cues to `contact` hosts; only the page's first host greets, and a `contact` host always starts in idle; all hosts share one loader; at most one host animates at a time (the one most in view), and the others show their still. A second host starts (and prefetches) only when it first becomes the active host, so home's first-visit network order stays run-in, wave, idle.
14. **No `style` attributes** (M5's CSP drops them): the component's sizes come from a build-time `<style>` element (hashed by Astro's CSP) and from classes; runtime positions (the bubble) are set from JavaScript, which the CSP allows.
15. **`<html data-motion="calm">`** (M4's review switch and calm mode) counts as reduced motion.

## The public interface (for M3, M4 and anyone else)

One file, `site/src/ottie/events.ts`, about 40 lines with no imports. Importing it adds nothing else to a bundle, and calling it on a page without Ottie (or with Quiet Ottie on) does nothing.

```ts
import { cueOttie } from "../ottie/events";

cueOttie("ask:focus");                 // question box focused: fetch think
cueOttie("ask:typing");                // each input event: Ottie goes silent
cueOttie("ask:submit");                // question sent: think
cueOttie("ask:stream");                // first streamed token: fetch nod, point, shrug
cueOttie("ask:answer", { sources: 3 }); // answer complete: nod, then point if sources > 0
cueOttie("ask:unknown");               // "don't know" path: shrug
cueOttie("ask:resting");               // budget spent or API down: shrug
cueOttie("ask:error");                 // network or server error: shrug
cueOttie("ask:reset");                 // conversation cleared: idle
cueOttie("letter:open");               // letter in view: point at it
cueOttie("letter:ready");              // form filled in: fetch jump
cueOttie("letter:sent");               // sent: jump
```

| Name | Kind | Contract |
|---|---|---|
| `cueOttie(type, extra?)` | function | Dispatches `new CustomEvent("ottie:cue", { detail: { type, ...extra } })` on `window`. Safe during SSR (no `window`: no-op). |
| `onOttieCue(handler)` | function | Subscribes to cues; returns an unsubscribe function. Used by the player. |
| `onOttieState(handler)` | function | Subscribes to `ottie:state` (`detail.state` is the state Ottie just entered, or a reduced-motion pose; `detail.context` is the host's context, added so a page with two Otties can tell them apart). Handler signature: `(state: string, context: PageContext) => void`. For M4's letter: wait for `idle` after `jump` **with `context === "contact"`** before the envelope flies off, otherwise the hero Ottie's idle could arrive first. |
| `[data-ottie-avoid]` | attribute | Put it on the question input, the answer panel and the letter. Bubbles never overlap these elements; the e2e tests check Ottie's box never does either. |
| `[data-ottie-host]` | attribute | Ottie's reserved box, with `data-ottie-context` (`home`, `project`, `contact`, `devlog`, `404`). A page may have more than one (home: hero and letter). M4 may move the contact host with `transform`; it must not change its size. |
| Routing | rule | `ask:*` cues reach `home` and `project` hosts; `letter:*` cues reach `contact` hosts. A cue for a context the page does not have does nothing. |

Unknown cue types are ignored. M3's planning note assumed state-named cues (`cueOttie("think")`); the mapping is: `think` = `ask:submit`, `nod` then `point` = `ask:answer` with sources, `shrug` = `ask:unknown`, `ask:resting` or `ask:error`, `idle` = `ask:reset`. M3's "talk while streaming" is not adopted: the PRD keeps talk for speech bubbles, so Ottie thinks until the answer lands.

## File structure

| File | Responsibility | Tested by |
|---|---|---|
| `site/src/ottie/events.ts` | Public cue and state events | `tests/unit/ottie/events.test.ts` |
| `site/src/ottie/manifest.ts` | Types, `STATE_NAMES`, validation, stage geometry | `manifest.test.ts` |
| `site/src/ottie/manifest-data.ts` | The one import of `brand/ottie/dist/manifest.json` | `manifest.test.ts` |
| `site/src/ottie/timeline.ts` | Playback state machine ported from the preview: ticks, holds, loops, `loop_start`, exits, crossfades, `exit_via`, `enter_from`, queue | `timeline.test.ts` |
| `site/src/ottie/frames.ts` | Draw operations (source rect, offset, shift, fade, mirror) and the reduced-motion pose plan | `frames.test.ts` |
| `site/src/ottie/poses.ts` | Key pose per state, `MIRROR_POINT_APPROVED` | `frames.test.ts` |
| `site/src/ottie/assets.ts` | Sheet URLs with content version | `loader.test.ts` |
| `site/src/ottie/loader.ts` | Serial prefetch queue, decode on demand, LRU of decoded sheets, failure memory | `loader.test.ts` |
| `site/src/ottie/lines.json` | Ottie's reviewed lines (Din reviews) | `lines.test.ts` |
| `site/src/ottie/lines.ts` | Line types, `pickLine`, `lintLine` | `lines.test.ts` |
| `site/src/ottie/bubble.ts` | 20 s gate, bubble duration, placement that avoids `[data-ottie-avoid]` | `bubble.test.ts` |
| `site/src/ottie/prefs.ts` | Safe storage, Quiet Ottie, visit kind, tips count, mode (full, reduced, still) | `prefs.test.ts` |
| `site/src/ottie/director.ts` | Rules for one host: openers, cues, poke, tips, nap, wake, silence | `director.test.ts`, `director-quiet.test.ts` |
| `site/src/ottie/hosts.ts` | Rules across hosts on a page: cue and interaction routing, which host greets, which host is active | `hosts.test.ts` |
| `site/src/ottie/layout.ts` | Build-time sizes of the box, canvas and still as CSS (no `style` attributes) | `layout.test.ts` |
| `site/src/ottie/still.ts` | Measured size and ground point of the inline still | Din's lab overlay check |
| `site/src/ottie/source.ts` | Browser fetch and `createImageBitmap` decode | e2e |
| `site/src/ottie/renderer.ts` | Canvas sizing and painting | e2e, Din |
| `site/src/ottie/actor.ts` | One host in the browser: renderer, timeline, director, rAF loop, bubble DOM, reduced-motion poses | e2e |
| `site/src/ottie/player.ts` | The page controller: shared loader and prefs, listeners, routing, the active host, pausing | e2e |
| `site/src/ottie/boot.ts` | Entry: finds every host, Quiet toggle, starts the player | e2e |
| `site/src/components/Ottie.astro` | Reserved box, inline still, canvas, bubble, Quiet toggle, pre-paint script, styles | e2e, Din |
| `site/src/lib/lab.ts` | Whether lab pages are built (from M0's shared deploy) | `tests/unit/lab.test.ts` |
| `site/src/pages/lab/ottie/[...slug].astro` | Ottie lab (tests and Din's review) | e2e |
| `site/public/_headers` | Long-term caching for `/ottie/*` | curl on the preview |
| `site/tests/unit/ottie/fixtures.ts` | Synthetic manifests and helpers for tests | n/a |
| `site/tests/e2e/ottie.spec.ts` | Behaviour, network order, two Otties, a11y, resilience, layout | Playwright |
| `site/tests/e2e/ottie-routes.spec.ts` | Ottie on the right routes, the hero size, phones (after M1) | Playwright |
| `site/tests/e2e/ottie-perf.spec.ts` | Long tasks, layout shift, trace, JavaScript cost | Playwright (Chromium) |

Modified: `site/astro.config.mjs` (one `vite.define` for the `DINS_LABS` override), `site/src/env.d.ts` (one `declare const`), and in Task 16 the pages that use M1's `OttieSlot.astro` (which Task 16 deletes) and their e2e specs.

## Order and dependencies

- Tasks 1 to 11 are pure TypeScript and need only M0's Vitest setup. Task 1 should land first and early so M3 and M4 can import `events.ts`.
- Tasks 12 to 15 need M0's Astro app, base layout and Playwright setup.
- Task 16 needs M1's pages merged.
- Tasks 17 and 18 are Din's; Task 19 closes the milestone.
- Calendar (PLAN.md M2, November 2 to 12): Tasks 1 to 11 by about November 5, 12 to 15 by November 9, 16 once M1 lands, Din's review November 10 to 12.

Unit test command used throughout: `pnpm --dir site exec vitest run <file>`. All unit tests: `pnpm --dir site test`. End to end: `pnpm --dir site test:e2e`.

---
## Tasks

### Task 1: The public cue interface

**Files:**
- Create: `site/src/ottie/events.ts`
- Test: `site/tests/unit/ottie/events.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `OTTIE_CUE = "ottie:cue"`, `OTTIE_STATE = "ottie:state"`, `type OttieCueType`, `interface OttieCueDetail { type: OttieCueType; sources?: number }`, `cueOttie(type: OttieCueType, extra?: { sources?: number }): void`, `onOttieCue(handler: (cue: OttieCueDetail) => void): () => void`, `interface OttieStateDetail { state: string; context: string }`, `onOttieState(handler: (state: string, context: string) => void): () => void`, `isCueType(value: unknown): value is OttieCueType`.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/events.test.ts
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cueOttie, isCueType, onOttieCue, onOttieState, OTTIE_STATE } from "../../../src/ottie/events";

describe("ottie events", () => {
  beforeEach(() => vi.stubGlobal("window", new EventTarget()));
  afterEach(() => vi.unstubAllGlobals());

  it("dispatches a cue on window with its detail", () => {
    const seen: unknown[] = [];
    const off = onOttieCue((cue) => seen.push(cue));
    cueOttie("ask:answer", { sources: 2 });
    cueOttie("ask:submit");
    off();
    cueOttie("ask:reset");
    expect(seen).toEqual([{ type: "ask:answer", sources: 2 }, { type: "ask:submit" }]);
  });

  it("reports state changes with the host's context", () => {
    const seen: string[] = [];
    const off = onOttieState((s, ctx) => seen.push(`${ctx}:${s}`));
    window.dispatchEvent(new CustomEvent(OTTIE_STATE, { detail: { state: "jump", context: "contact" } }));
    off();
    expect(seen).toEqual(["contact:jump"]);
  });

  it("knows which cue types exist", () => {
    expect(isCueType("letter:sent")).toBe(true);
    expect(isCueType("think")).toBe(false);
    expect(isCueType(42)).toBe(false);
  });

  it("does nothing without a window (server render)", () => {
    vi.unstubAllGlobals();
    expect(() => cueOttie("ask:focus")).not.toThrow();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/events.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/events".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/events.ts
// The only Ottie module other milestones import. Callers say what happened;
// the player decides how Ottie reacts (or ignores it when Ottie is absent or quiet).

export const OTTIE_CUE = "ottie:cue";
export const OTTIE_STATE = "ottie:state";

const CUE_TYPES = [
  "ask:focus", "ask:typing", "ask:submit", "ask:stream", "ask:answer",
  "ask:unknown", "ask:resting", "ask:error", "ask:reset",
  "letter:open", "letter:ready", "letter:sent",
] as const;

export type OttieCueType = (typeof CUE_TYPES)[number];
export interface OttieCueDetail { type: OttieCueType; sources?: number }
export interface OttieStateDetail { state: string; context: string }

export function isCueType(value: unknown): value is OttieCueType {
  return typeof value === "string" && (CUE_TYPES as readonly string[]).includes(value);
}

export function cueOttie(type: OttieCueType, extra: { sources?: number } = {}): void {
  if (typeof window === "undefined") return;
  window.dispatchEvent(new CustomEvent<OttieCueDetail>(OTTIE_CUE, { detail: { type, ...extra } }));
}

export function onOttieCue(handler: (cue: OttieCueDetail) => void): () => void {
  const listener = (e: Event) => handler((e as CustomEvent<OttieCueDetail>).detail);
  window.addEventListener(OTTIE_CUE, listener);
  return () => window.removeEventListener(OTTIE_CUE, listener);
}

// A page can have two Otties (home: hero and letter), so check the context.
export function onOttieState(handler: (state: string, context: string) => void): () => void {
  const listener = (e: Event) => {
    const { state, context } = (e as CustomEvent<OttieStateDetail>).detail;
    handler(state, context);
  };
  window.addEventListener(OTTIE_STATE, listener);
  return () => window.removeEventListener(OTTIE_STATE, listener);
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/events.test.ts`
Expected: PASS, 4 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/events.ts site/tests/unit/ottie/events.test.ts
git commit -m "feat(ottie): add the cue interface other milestones use to drive Ottie"
```

### Task 2: Manifest types, validation, geometry and the sheet budget

**Files:**
- Create: `site/src/ottie/manifest.ts`, `site/src/ottie/manifest-data.ts`, `site/tests/unit/ottie/fixtures.ts`
- Test: `site/tests/unit/ottie/manifest.test.ts`

**Interfaces:**
- Consumes: `brand/ottie/dist/manifest.json` (fields in `brand/ottie/README.md`).
- Produces: `STATE_NAMES`, `type StateName`, `type Point = [number, number]`, `interface FrameSpec`, `interface StateSpec`, `interface Manifest`, `interface Box { l; r; t; b }`, `interface Geometry { anchor: Record<StateName, Point>; stage: Box; body: Box; stageSize: Point; bodySize: Point }`, `validateManifest(m): string[]`, `geometry(m): Geometry`, `offsetOf(g, name): Point`, `shiftOf(spec, i): Point`, `MANIFEST: Manifest`. Test helpers `spec(count, overrides)` and `manifestOf(overrides)`.

- [ ] **Step 1: Write the test fixtures**

```ts
// site/tests/unit/ottie/fixtures.ts
import { STATE_NAMES, type Manifest, type StateName, type StateSpec } from "../../../src/ottie/manifest";

export function spec(count: number, opts: Partial<StateSpec> & { d?: number } = {}): StateSpec {
  const { d = 1, ...rest } = opts;
  return {
    file: "x.webp", frame: [100, 200], cols: 8, count, loop: false, tickrate: 24, exits: [0],
    frames: Array.from({ length: count }, () => ({ d, ground: [50, 190] as [number, number] })),
    bytes: 1000,
    ...rest,
  };
}

// Every state present, 4 drawings each, one tick per drawing; override what a test needs.
export function manifestOf(over: Partial<Record<StateName, StateSpec>> = {}): Manifest {
  const loops = new Set<StateName>(["idle", "think", "talk", "nap"]);
  const states = Object.fromEntries(
    STATE_NAMES.map((n) => [n, spec(4, { loop: loops.has(n), file: `${n}.webp` })]),
  ) as Record<StateName, StateSpec>;
  states.nap = { ...states.nap, exit_via: "wake" };
  states.wake = { ...states.wake, enter_from: "nap" };
  return { version: 2, display_scale: 0.5, total_bytes: 0, states: { ...states, ...over } };
}

export function deferred<T>() {
  let resolve!: (v: T) => void;
  let reject!: (e: unknown) => void;
  const promise = new Promise<T>((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
}

export const flush = () => new Promise((r) => setTimeout(r, 0));
```

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/unit/ottie/manifest.test.ts
import { statSync } from "node:fs";
import { describe, expect, it } from "vitest";
import { geometry, offsetOf, STATE_NAMES, validateManifest } from "../../../src/ottie/manifest";
import { MANIFEST } from "../../../src/ottie/manifest-data";
import { manifestOf, spec } from "./fixtures";

const DIST = new URL("../../../../brand/ottie/dist/", import.meta.url);

describe("manifest", () => {
  it("the shipped manifest is valid and has all twelve states", () => {
    expect(validateManifest(MANIFEST)).toEqual([]);
    expect(Object.keys(MANIFEST.states).sort()).toEqual([...STATE_NAMES].sort());
  });

  it("stays inside the sheet budget and matches the files on disk", () => {
    let total = 0;
    for (const name of STATE_NAMES) {
      const s = MANIFEST.states[name];
      expect(s.bytes, name).toBeLessThanOrEqual(400_000);
      expect(statSync(new URL(s.file, DIST)).size, name).toBe(s.bytes);
      total += s.bytes;
    }
    expect(total).toBe(MANIFEST.total_bytes);
    expect(total).toBeLessThanOrEqual(2_500_000);
  });

  it("reports broken manifests", () => {
    const bad = manifestOf({
      nod: spec(3, { exits: [] }),
      shrug: { ...spec(2), count: 3 },
      nap: spec(4, { loop: true, loop_start: 9, exit_via: "wake" }),
    });
    const problems = validateManifest(bad).join("\n");
    expect(problems).toMatch(/nod: exits/);
    expect(problems).toMatch(/shrug: 2 frames for count 3/);
    expect(problems).toMatch(/nap: loop_start/);
  });

  it("computes the stage and body boxes the preview uses", () => {
    const g = geometry(MANIFEST);
    expect(g.stage.l).toBeCloseTo(172.97, 2);
    expect(g.stage.r).toBeCloseTo(643.76, 2);
    expect(g.stage.t).toBeCloseTo(460.03, 2);
    expect(g.stage.b).toBeCloseTo(30.91, 2);
    expect(g.stageSize[0]).toBeCloseTo(816.73, 2);
    expect(g.stageSize[1]).toBeCloseTo(490.94, 2);
    expect(g.bodySize[0]).toBeCloseTo(317, 2);
    expect(g.bodySize[1]).toBeCloseTo(405, 2);
  });

  it("places every state by its ground point", () => {
    const g = geometry(MANIFEST);
    const [x, y] = offsetOf(g, "idle");
    expect(x).toBeCloseTo(61, 2);     // 172.97 - 111.97
    expect(y).toBeCloseTo(88.94, 2);  // 460.03 - 371.09
  });
});
```

- [ ] **Step 3: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/manifest.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/manifest".

- [ ] **Step 4: Write the implementation**

```ts
// site/src/ottie/manifest.ts
export const STATE_NAMES = [
  "idle", "wave", "run-in", "think", "nod", "point", "shrug", "poke", "jump", "nap", "wake", "talk",
] as const;
export type StateName = (typeof STATE_NAMES)[number];
export type Point = [number, number];

export interface FrameSpec { d: number; ground?: Point; shift?: Point }
export interface StateSpec {
  file: string; frame: Point; cols: number; count: number; loop: boolean; tickrate: number;
  drawings_per_second?: number; exits: number[]; frames: FrameSpec[];
  loop_start?: number; exit_via?: StateName; enter_from?: StateName; bytes: number; quality?: number;
}
export interface Manifest { version: number; display_scale: number; total_bytes: number; states: Record<StateName, StateSpec> }
export interface Box { l: number; r: number; t: number; b: number }
export interface Geometry { anchor: Record<StateName, Point>; stage: Box; body: Box; stageSize: Point; bodySize: Point }

const isState = (v: string): v is StateName => (STATE_NAMES as readonly string[]).includes(v);

export function validateManifest(m: Manifest): string[] {
  const problems: string[] = [];
  for (const name of STATE_NAMES) {
    const s = m.states[name];
    if (!s) { problems.push(`${name}: missing`); continue; }
    if (s.frames.length !== s.count) problems.push(`${name}: ${s.frames.length} frames for count ${s.count}`);
    if (s.frames.some((f) => !Number.isInteger(f.d) || f.d < 1)) problems.push(`${name}: hold d must be a whole number of ticks`);
    if (!s.exits.length || s.exits.some((e) => e < 0 || e >= s.count)) problems.push(`${name}: exits missing or out of range`);
    if (s.loop_start !== undefined && (s.loop_start < 0 || s.loop_start >= s.count)) problems.push(`${name}: loop_start out of range`);
    for (const ref of [s.exit_via, s.enter_from]) if (ref !== undefined && !isState(ref)) problems.push(`${name}: unknown state ${ref}`);
    if (s.cols < 1 || s.tickrate <= 0 || s.frame[0] <= 0 || s.frame[1] <= 0) problems.push(`${name}: bad sheet layout`);
  }
  return problems;
}

export const shiftOf = (s: StateSpec, i: number): Point => s.frames[i]?.shift ?? [0, 0];

// Ported from the preview: every state is placed by its ground point, and the
// stage is big enough for every shifted drawing (run-in travel, jump height).
// The body box ignores shifts: it is the space Ottie takes when standing still.
export function geometry(m: Manifest): Geometry {
  const stage: Box = { l: 0, r: 0, t: 0, b: 0 };
  const body: Box = { l: 0, r: 0, t: 0, b: 0 };
  const anchor = {} as Record<StateName, Point>;
  for (const name of STATE_NAMES) {
    const s = m.states[name];
    const g: Point = s.frames[0].ground ?? [s.frame[0] / 2, s.frame[1]];
    anchor[name] = g;
    body.l = Math.max(body.l, g[0]); body.r = Math.max(body.r, s.frame[0] - g[0]);
    body.t = Math.max(body.t, g[1]); body.b = Math.max(body.b, s.frame[1] - g[1]);
    for (let i = 0; i < s.count; i++) {
      const [dx, dy] = shiftOf(s, i);
      stage.l = Math.max(stage.l, g[0] - dx); stage.r = Math.max(stage.r, s.frame[0] - g[0] + dx);
      stage.t = Math.max(stage.t, g[1] - dy); stage.b = Math.max(stage.b, s.frame[1] - g[1] + dy);
    }
  }
  return { anchor, stage, body, stageSize: [stage.l + stage.r, stage.t + stage.b], bodySize: [body.l + body.r, body.t + body.b] };
}

export const offsetOf = (g: Geometry, name: StateName): Point => [g.stage.l - g.anchor[name][0], g.stage.t - g.anchor[name][1]];
```

```ts
// site/src/ottie/manifest-data.ts
// The single place the site reads the sheet manifest. If M0 exposes brand/ottie/dist
// through an alias instead of a relative path, change only this import.
import raw from "../../../brand/ottie/dist/manifest.json";
import type { Manifest } from "./manifest";

export const MANIFEST = raw as unknown as Manifest;
```

- [ ] **Step 5: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/manifest.test.ts`
Expected: PASS, 5 tests. If the JSON import fails with a Vite `fs.allow` error, M0's workspace root setting is missing; see "Assumes".

- [ ] **Step 6: Commit**

```bash
git add site/src/ottie/manifest.ts site/src/ottie/manifest-data.ts site/tests/unit/ottie/fixtures.ts site/tests/unit/ottie/manifest.test.ts
git commit -m "feat(ottie): read and check the sheet manifest and compute Ottie's stage"
```

### Task 3: The playback timeline (port of the preview's state logic)

**Files:**
- Create: `site/src/ottie/timeline.ts`
- Test: `site/tests/unit/ottie/timeline.test.ts`

**Interfaces:**
- Consumes: `Manifest`, `StateName`, `StateSpec` (Task 2).
- Produces: `MAX_WAIT = 12`, `FADE = 3`, `MAX_DT = 0.1`, `interface Fade { state: StateName; drawing: number; left: number }`, `interface Snapshot { state: StateName; drawing: number; fade: Fade | null }`, `interface Timeline { readonly current: StateName; play(...names: StateName[]): void; tick(): void; advance(seconds: number): boolean; snapshot(): Snapshot; onEnter(cb: (name: StateName) => void): void }`, `createTimeline(manifest, rest = "idle"): Timeline`.

Behaviour ported from `brand/ottie/preview/index.html` (Din accepted it): each drawing is held for `frames[i].d` ticks at `tickrate`; a loop wraps to `loop_start`; asking for a new state from a loop waits for the next drawing in `exits` if it is at most 12 ticks away, otherwise it switches now with a 3-tick crossfade (no crossfade when the next state's first drawing has a `shift`, which is an entrance from off stage); one-shots always finish; `exit_via` is played on the way out (nap leaves through wake). Two deliberate changes from the preview, both tested: a state whose `enter_from` is not the current state is dropped (wake is never played cold), and asking for the current loop again cancels a pending exit. The preview's chain demo (`chaining`, `wrapped`) is not ported.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/timeline.test.ts
import { describe, expect, it } from "vitest";
import { createTimeline } from "../../../src/ottie/timeline";
import { MANIFEST } from "../../../src/ottie/manifest-data";
import type { StateName } from "../../../src/ottie/manifest";
import { manifestOf, spec } from "./fixtures";

const ticks = (tl: { tick(): void }, n: number) => { for (let i = 0; i < n; i++) tl.tick(); };
const farIdle = { idle: spec(30, { loop: true }) }; // the next exit is 30 ticks away

describe("timeline", () => {
  it("starts at rest on drawing 0", () => {
    expect(createTimeline(manifestOf()).snapshot()).toEqual({ state: "idle", drawing: 0, fade: null });
  });

  it("holds each drawing for d ticks", () => {
    const tl = createTimeline(manifestOf({ idle: spec(3, { loop: true, d: 2 }) }));
    tl.tick();
    expect(tl.snapshot().drawing).toBe(0);
    tl.tick();
    expect(tl.snapshot().drawing).toBe(1);
  });

  it("wraps a loop to loop_start", () => {
    const m = manifestOf({ nap: spec(5, { loop: true, loop_start: 3, exits: [3], exit_via: "wake" }) });
    const tl = createTimeline(m, "nap");
    ticks(tl, 5);
    expect(tl.snapshot().drawing).toBe(3);
  });

  it("waits for a near exit, plays a one-shot, then returns to rest", () => {
    const tl = createTimeline(manifestOf({ idle: spec(4, { loop: true }) }));
    tl.play("nod");
    ticks(tl, 3);
    expect(tl.snapshot()).toMatchObject({ state: "idle", drawing: 3 });
    tl.tick();
    expect(tl.snapshot()).toEqual({ state: "nod", drawing: 0, fade: null });
    ticks(tl, 4);
    expect(tl.snapshot()).toMatchObject({ state: "idle", drawing: 0 });
  });

  it("cuts a far exit now with a 3 tick crossfade", () => {
    const tl = createTimeline(manifestOf(farIdle));
    tl.play("nod");
    expect(tl.snapshot()).toEqual({ state: "nod", drawing: 0, fade: { state: "idle", drawing: 0, left: 3 } });
    ticks(tl, 2);
    expect(tl.snapshot().fade?.left).toBe(1);
    tl.tick();
    expect(tl.snapshot().fade).toBeNull();
  });

  it("does not crossfade into an entrance from off stage", () => {
    const runIn = spec(4);
    runIn.frames = runIn.frames.map((f, i) => (i === 0 ? { ...f, shift: [100, 0] } : f));
    const tl = createTimeline(manifestOf({ ...farIdle, "run-in": runIn }));
    tl.play("run-in");
    expect(tl.snapshot()).toEqual({ state: "run-in", drawing: 0, fade: null });
  });

  it("lets a one-shot finish before the next state", () => {
    const tl = createTimeline(manifestOf(farIdle));
    tl.play("nod");
    tl.play("shrug");
    ticks(tl, 3);
    expect(tl.current).toBe("nod");
    tl.tick();
    expect(tl.current).toBe("shrug");
    ticks(tl, 4);
    expect(tl.current).toBe("idle");
  });

  it("plays a sequence in order, then rests", () => {
    const tl = createTimeline(manifestOf(farIdle));
    const seen: StateName[] = [];
    tl.onEnter((s) => seen.push(s));
    tl.play("nod", "point");
    ticks(tl, 8);
    expect(seen).toEqual(["nod", "point", "idle"]);
  });

  it("leaves nap through wake", () => {
    const tl = createTimeline(manifestOf(farIdle));
    const seen: StateName[] = [];
    tl.onEnter((s) => seen.push(s));
    tl.play("nap");
    tl.play("idle");
    ticks(tl, 8);
    expect(seen).toEqual(["nap", "wake", "idle"]);
  });

  it("never plays wake cold", () => {
    const tl = createTimeline(manifestOf());
    const seen: StateName[] = [];
    tl.onEnter((s) => seen.push(s));
    tl.play("wake");
    ticks(tl, 8);
    expect(seen).toEqual([]);
  });

  it("asking for the current loop again cancels a pending exit", () => {
    const tl = createTimeline(manifestOf({ idle: spec(4, { loop: true }) }));
    tl.play("think");
    ticks(tl, 4);
    expect(tl.current).toBe("think");
    tl.play("idle");
    tl.play("think");
    ticks(tl, 8);
    expect(tl.current).toBe("think");
  });

  it("survives play spam and still ends at rest", () => {
    const tl = createTimeline(manifestOf(farIdle));
    for (const s of ["poke", "poke", "think", "nod", "shrug", "poke"] as StateName[]) { tl.play(s); tl.tick(); }
    ticks(tl, 40);
    expect(tl.current).toBe("idle");
  });

  it("turns seconds into ticks and caps long gaps", () => {
    const tl = createTimeline(manifestOf({ idle: spec(100, { loop: true }) }));
    expect(tl.advance(0.5)).toBe(true);
    expect(tl.snapshot().drawing).toBe(12);
    tl.advance(30); // a hidden tab coming back: at most 0.1 s worth (2 ticks)
    expect(tl.snapshot().drawing).toBe(14);
    expect(tl.advance(0)).toBe(false);
  });

  it("runs the real sheets through an answer and a nap", () => {
    const tl = createTimeline(MANIFEST);
    const seen: StateName[] = [];
    tl.onEnter((s) => seen.push(s));
    const run = (seconds: number) => { for (let i = 0; i < seconds * 60; i++) tl.advance(1 / 60); };
    tl.play("think"); run(3);
    tl.play("nod", "point"); run(5);
    tl.play("nap"); run(5);
    tl.play("idle"); run(5);
    expect(seen).toEqual(["think", "nod", "point", "idle", "nap", "wake", "idle"]);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/timeline.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/timeline".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/timeline.ts
// Playback state, ported from brand/ottie/preview/index.html (accepted by Din).
// No DOM here: the player calls advance() each frame and draws snapshot().
import type { Manifest, StateName, StateSpec } from "./manifest";

export const MAX_WAIT = 12; // ticks: leave a loop at a clean exit if one is this close
export const FADE = 3;      // ticks of crossfade when cutting out of a loop
export const MAX_DT = 0.1;  // seconds: a long pause never fast-forwards

export interface Fade { state: StateName; drawing: number; left: number }
export interface Snapshot { state: StateName; drawing: number; fade: Fade | null }
export interface Timeline {
  readonly current: StateName;
  play(...names: StateName[]): void;
  tick(): void;
  advance(seconds: number): boolean;
  snapshot(): Snapshot;
  onEnter(cb: (name: StateName) => void): void;
}

export function createTimeline(manifest: Manifest, rest: StateName = "idle"): Timeline {
  const states = manifest.states;
  let current: StateName = rest;
  let drawing = 0, tickInDrawing = 0, acc = 0;
  let queue: StateName[] = [];
  let exitRequested = false;
  let fade: Fade | null = null;
  let entered: (name: StateName) => void = () => {};

  const loopStart = (s: StateSpec) => s.loop_start ?? 0;
  const nextIndex = (s: StateSpec, i: number) => (i + 1 < s.count ? i + 1 : loopStart(s));

  function ticksToExit(): number {
    const s = states[current];
    let t = s.frames[drawing].d - tickInDrawing;
    let i = nextIndex(s, drawing);
    for (let n = 0; n < s.count; n++) {
      if (s.exits.includes(i)) return t;
      t += s.frames[i].d;
      i = nextIndex(s, i);
    }
    return Infinity;
  }

  function switchTo(name: StateName) {
    current = name; drawing = 0; tickInDrawing = 0; exitRequested = false;
    entered(name);
  }

  function requestExit() {
    if (!queue.length) return;
    const via = states[current].exit_via;
    if (via && queue[0] !== via) queue.unshift(via);
    if (!states[current].loop || ticksToExit() <= MAX_WAIT) { exitRequested = true; return; }
    const next = queue.shift()!;
    if (!states[next].frames[0].shift) fade = { state: current, drawing, left: FADE };
    switchTo(next);
  }

  function play(...names: StateName[]) {
    const wanted = names.filter((n) => !states[n].enter_from || states[n].enter_from === current);
    if (!wanted.length) return;
    if (wanted.length === 1 && wanted[0] === current && states[current].loop) {
      queue = []; exitRequested = false;
      return;
    }
    queue = wanted;
    requestExit();
  }

  function tick() {
    const s = states[current];
    if (fade && --fade.left <= 0) fade = null;
    if (++tickInDrawing < s.frames[drawing].d) return;
    tickInDrawing = 0;
    drawing++;
    if (drawing >= s.count) {
      if (!s.loop) {
        switchTo(queue.length ? queue.shift()! : rest);
        if (queue.length) requestExit();
        return;
      }
      drawing = loopStart(s);
    }
    if (s.loop && exitRequested && queue.length && s.exits.includes(drawing)) {
      switchTo(queue.shift()!);
      if (queue.length) exitRequested = true;
    }
  }

  const key = () => `${current}|${drawing}|${fade?.left ?? 0}`;

  function advance(seconds: number): boolean {
    const before = key();
    acc += Math.min(Math.max(seconds, 0), MAX_DT) * states[current].tickrate;
    while (acc >= 1 - 1e-6) { acc -= 1; tick(); }
    return key() !== before;
  }

  return {
    get current() { return current; },
    play, tick, advance,
    snapshot: () => ({ state: current, drawing, fade: fade ? { ...fade } : null }),
    onEnter(cb) { entered = cb; },
  };
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/timeline.test.ts`
Expected: PASS, 14 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/timeline.ts site/tests/unit/ottie/timeline.test.ts
git commit -m "feat(ottie): port the preview's playback state machine with tests"
```

### Task 4: Draw operations, key poses and the reduced-motion plan

**Files:**
- Create: `site/src/ottie/frames.ts`, `site/src/ottie/poses.ts`
- Test: `site/tests/unit/ottie/frames.test.ts`

**Interfaces:**
- Consumes: `geometry`, `offsetOf`, `shiftOf`, `Manifest`, `StateName` (Task 2); `FADE`, `Snapshot` (Task 3).
- Produces: `interface DrawOp { state: StateName; sx; sy; sw; sh; dx; dy: number; alpha: number; mirror: boolean }` (all in stage frame pixels), `sourceRect(spec, i): [number, number, number, number]`, `drawOps(m, g, snap, opts: { mirrorPoint: boolean }): DrawOp[]`, `interface PoseStep { state: StateName | "still"; drawing: number; holdMs: number }`, `reducedPlan(m, states): PoseStep[]`, `MIN_POSE_MS = 1200`; from `poses.ts`: `KEY_POSE: Partial<Record<StateName, number>>`, `MIRROR_POINT_APPROVED = false`.

The key poses below are first guesses from the hold lengths in the manifest; Din picks the final drawings in the lab (Task 18).

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/frames.test.ts
import { describe, expect, it } from "vitest";
import { drawOps, reducedPlan, sourceRect } from "../../../src/ottie/frames";
import { geometry } from "../../../src/ottie/manifest";
import { MANIFEST } from "../../../src/ottie/manifest-data";

const g = geometry(MANIFEST);

describe("draw operations", () => {
  it("finds a drawing on its sheet", () => {
    expect(sourceRect(MANIFEST.states["run-in"], 9)).toEqual([317, 402, 317, 402]);
  });

  it("places a drawing by its ground point plus its shift", () => {
    const [op] = drawOps(MANIFEST, g, { state: "run-in", drawing: 0, fade: null }, { mirrorPoint: false });
    expect(op.dx).toBeCloseTo(499.73, 2);
    expect(op.dy).toBeCloseTo(69.22, 2);
    expect(op.alpha).toBe(1);
  });

  it("adds the fading drawing on top", () => {
    const ops = drawOps(MANIFEST, g, { state: "think", drawing: 0, fade: { state: "idle", drawing: 5, left: 3 } }, { mirrorPoint: false });
    expect(ops.map((o) => [o.state, o.alpha])).toEqual([["think", 1], ["idle", 0.75]]);
    expect(ops[1].dx).toBeCloseTo(61, 2);
  });

  it("mirrors only point, and only when allowed", () => {
    const point = { state: "point" as const, drawing: 3, fade: null };
    expect(drawOps(MANIFEST, g, point, { mirrorPoint: true })[0].mirror).toBe(true);
    expect(drawOps(MANIFEST, g, point, { mirrorPoint: false })[0].mirror).toBe(false);
    expect(drawOps(MANIFEST, g, { state: "nod", drawing: 0, fade: null }, { mirrorPoint: true })[0].mirror).toBe(false);
  });
});

describe("reduced-motion plan", () => {
  it("holds key poses for each one-shot, then the still", () => {
    expect(reducedPlan(MANIFEST, ["nod", "point"])).toEqual([
      { state: "nod", drawing: 5, holdMs: 1200 },
      { state: "point", drawing: 8, holdMs: 2000 },
      { state: "still", drawing: 0, holdMs: Infinity },
    ]);
  });

  it("skips travel, hops, talking and wake", () => {
    expect(reducedPlan(MANIFEST, ["run-in", "wave"])).toEqual([
      { state: "wave", drawing: 12, holdMs: 2000 },
      { state: "still", drawing: 0, holdMs: Infinity },
    ]);
    expect(reducedPlan(MANIFEST, ["poke", "talk"])).toEqual([{ state: "still", drawing: 0, holdMs: Infinity }]);
    expect(reducedPlan(MANIFEST, ["idle"])).toEqual([{ state: "still", drawing: 0, holdMs: Infinity }]);
  });

  it("holds a loop pose until the next cue", () => {
    expect(reducedPlan(MANIFEST, ["think"])).toEqual([{ state: "think", drawing: 21, holdMs: Infinity }]);
    expect(reducedPlan(MANIFEST, ["nap"])).toEqual([{ state: "nap", drawing: 14, holdMs: Infinity }]);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/frames.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/frames".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/poses.ts
import type { StateName } from "./manifest";

// One drawing per state for reduced motion. First guesses from the manifest's
// longest holds; Din confirms each in the lab (?ottie-mode=reduced).
// No entry means the state has no still form: run-in (travel), poke (hop),
// talk (mouth), wake (comes back to the still) and idle (the still itself).
export const KEY_POSE: Partial<Record<StateName, number>> = {
  wave: 12, think: 21, nod: 5, point: 8, shrug: 7, jump: 8, nap: 14,
};

// Point is drawn toward screen right. Mirroring it for targets on Ottie's left
// is built but stays off until Din approves it in the lab (Din, 2026-10-21).
export const MIRROR_POINT_APPROVED = false;
```

```ts
// site/src/ottie/frames.ts
import { offsetOf, shiftOf, type Geometry, type Manifest, type StateName, type StateSpec } from "./manifest";
import { KEY_POSE } from "./poses";
import { FADE, type Snapshot } from "./timeline";

export interface DrawOp {
  state: StateName;
  sx: number; sy: number; sw: number; sh: number; // source rect on the sheet
  dx: number; dy: number;                          // top-left on the stage, frame pixels
  alpha: number;
  mirror: boolean;                                 // flip around the rest ground point
}
export interface PoseStep { state: StateName | "still"; drawing: number; holdMs: number }
export const MIN_POSE_MS = 1200;

export function sourceRect(s: StateSpec, i: number): [number, number, number, number] {
  return [(i % s.cols) * s.frame[0], Math.floor(i / s.cols) * s.frame[1], s.frame[0], s.frame[1]];
}

export function drawOps(m: Manifest, g: Geometry, snap: Snapshot, opts: { mirrorPoint: boolean }): DrawOp[] {
  const op = (state: StateName, drawing: number, alpha: number): DrawOp => {
    const s = m.states[state];
    const [ox, oy] = offsetOf(g, state);
    const [shx, shy] = shiftOf(s, drawing);
    const [sx, sy, sw, sh] = sourceRect(s, drawing);
    return { state, sx, sy, sw, sh, dx: ox + shx, dy: oy + shy, alpha, mirror: opts.mirrorPoint && state === "point" };
  };
  const ops = [op(snap.state, snap.drawing, 1)];
  if (snap.fade) ops.push(op(snap.fade.state, snap.fade.drawing, snap.fade.left / (FADE + 1)));
  return ops;
}

export function reducedPlan(m: Manifest, states: StateName[]): PoseStep[] {
  const steps: PoseStep[] = [];
  for (const name of states) {
    const pose = KEY_POSE[name];
    if (pose === undefined) continue;
    const s = m.states[name];
    if (s.loop) return [...steps, { state: name, drawing: pose, holdMs: Infinity }];
    const ms = (s.frames.reduce((t, f) => t + f.d, 0) / s.tickrate) * 1000;
    steps.push({ state: name, drawing: pose, holdMs: Math.max(MIN_POSE_MS, ms) });
  }
  return [...steps, { state: "still", drawing: 0, holdMs: Infinity }];
}
```


- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/frames.test.ts`
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/frames.ts site/src/ottie/poses.ts site/tests/unit/ottie/frames.test.ts
git commit -m "feat(ottie): compute draw operations and the reduced-motion pose plan"
```

### Task 5: Sheet URLs and the loader

**Files:**
- Create: `site/src/ottie/assets.ts`, `site/src/ottie/loader.ts`
- Test: `site/tests/unit/ottie/loader.test.ts`

**Interfaces:**
- Consumes: `Manifest`, `StateName` (Task 2); `deferred`, `flush` (fixtures).
- Produces: `SHEET_BASE = "/ottie/"`, `fnv1a(text): string`, `sheetVersion(m): string`, `sheetUrl(m, name, version?): string`; `interface Decoded { close?(): void }`, `interface SheetSource<T extends Decoded> { fetchBlob(url: string): Promise<Blob>; decode(blob: Blob, url: string): Promise<T> }`, `interface Loader<T> { prefetch(names: StateName[]): void; ensure(name: StateName): Promise<T>; get(name: StateName): T | undefined; touch(name: StateName): void; failed(name: StateName): boolean; dispose(): void }`, `createLoader(urlFor, source, opts = { maxDecoded: 4, keep: ["idle"] }): Loader<T>`.

Rules: `prefetch` fetches bytes one sheet at a time in the order asked (so the network order is predictable and sheets never compete with page content); `ensure` jumps the queue, fetches if needed and decodes once; decoded sheets beyond `maxDecoded` are closed least recently used first, never one in `keep` and never the one just decoded; a sheet that failed is not retried on that page.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/loader.test.ts
import { describe, expect, it } from "vitest";
import { fnv1a, sheetUrl, sheetVersion } from "../../../src/ottie/assets";
import { createLoader } from "../../../src/ottie/loader";
import { MANIFEST } from "../../../src/ottie/manifest-data";
import type { StateName } from "../../../src/ottie/manifest";
import { deferred, flush } from "./fixtures";

function fakeSource() {
  const started: string[] = [];
  const pending = new Map<string, ReturnType<typeof deferred<Blob>>>();
  const closed: string[] = [];
  let decodes = 0;
  const source = {
    fetchBlob: (url: string) => { started.push(url); const d = deferred<Blob>(); pending.set(url, d); return d.promise; },
    decode: async (_b: Blob, url: string) => { decodes++; return { url, close: () => closed.push(url) }; },
  };
  const finish = async (url: string) => { pending.get(url)!.resolve(new Blob()); await flush(); };
  return { source, started, closed, finish, decodes: () => decodes, pending };
}
const urlFor = (n: StateName) => n;

describe("sheet urls", () => {
  it("serves sheets under /ottie/ with a content version", () => {
    expect(sheetUrl(MANIFEST, "idle")).toMatch(/^\/ottie\/idle\.webp\?v=[0-9a-f]{8}$/);
  });
  it("changes the version when any sheet changes", () => {
    const changed = structuredClone(MANIFEST);
    changed.states.nod.bytes += 1;
    expect(sheetVersion(changed)).not.toBe(sheetVersion(MANIFEST));
    expect(fnv1a("ottie")).toBe(fnv1a("ottie"));
  });
});

describe("loader", () => {
  it("prefetches one sheet at a time, in order", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source);
    loader.prefetch(["run-in", "wave", "idle"]);
    expect(f.started).toEqual(["run-in"]);
    await f.finish("run-in");
    expect(f.started).toEqual(["run-in", "wave"]);
    await f.finish("wave");
    expect(f.started).toEqual(["run-in", "wave", "idle"]);
  });

  it("never fetches a sheet twice", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source);
    loader.prefetch(["idle", "idle"]);
    loader.prefetch(["idle"]);
    void loader.ensure("idle");
    expect(f.started).toEqual(["idle"]);
  });

  it("lets ensure jump the queue", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source);
    loader.prefetch(["idle", "wave", "think"]);
    void loader.ensure("think");
    expect(f.started).toEqual(["idle", "think"]);
    await f.finish("idle");
    expect(f.started).toEqual(["idle", "think", "wave"]);
  });

  it("decodes once and caches the result", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source);
    const a = loader.ensure("idle");
    const b = loader.ensure("idle");
    await f.finish("idle");
    expect(await a).toBe(await b);
    expect(loader.get("idle")).toBe(await a);
    expect(f.decodes()).toBe(1);
  });

  it("remembers a failed sheet and does not retry it", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source);
    const p = loader.ensure("shrug");
    f.pending.get("shrug")!.reject(new Error("offline"));
    await expect(p).rejects.toThrow("offline");
    expect(loader.failed("shrug")).toBe(true);
    await expect(loader.ensure("shrug")).rejects.toThrow();
    expect(f.started).toEqual(["shrug"]);
  });

  it("keeps a few decoded sheets, closing the least recently used", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source, { maxDecoded: 3, keep: [] });
    for (const n of ["nod", "point", "shrug"] as StateName[]) { const p = loader.ensure(n); await f.finish(n); await p; }
    loader.touch("nod");
    const p = loader.ensure("jump"); await f.finish("jump"); await p;
    expect(f.closed).toEqual(["point"]);
    expect(loader.get("point")).toBeUndefined();
    expect(loader.get("nod")).toBeDefined();
  });

  it("never evicts kept sheets", async () => {
    const f = fakeSource();
    const loader = createLoader(urlFor, f.source, { maxDecoded: 1, keep: ["idle"] });
    for (const n of ["idle", "wave"] as StateName[]) { const p = loader.ensure(n); await f.finish(n); await p; }
    expect(loader.get("idle")).toBeDefined();
    loader.dispose();
    expect(f.closed.sort()).toEqual(["idle", "wave"]);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/loader.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/assets".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/assets.ts
import type { Manifest, StateName } from "./manifest";

export const SHEET_BASE = "/ottie/";

export function fnv1a(text: string): string {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) { h ^= text.charCodeAt(i); h = Math.imul(h, 0x01000193); }
  return (h >>> 0).toString(16).padStart(8, "0");
}

// The manifest lists every sheet's byte size, so rebuilding any sheet changes
// the version and the year-long immutable cache never serves a stale sheet.
export const sheetVersion = (m: Manifest): string => fnv1a(JSON.stringify(m.states));

export const sheetUrl = (m: Manifest, name: StateName, version = sheetVersion(m)): string =>
  `${SHEET_BASE}${m.states[name].file}?v=${version}`;
```

```ts
// site/src/ottie/loader.ts
import type { StateName } from "./manifest";

export interface Decoded { close?(): void }
export interface SheetSource<T extends Decoded> {
  fetchBlob(url: string): Promise<Blob>;
  decode(blob: Blob, url: string): Promise<T>;
}
export interface LoaderOptions { maxDecoded: number; keep: StateName[] }
export interface Loader<T> {
  prefetch(names: StateName[]): void;
  ensure(name: StateName): Promise<T>;
  get(name: StateName): T | undefined;
  touch(name: StateName): void;
  failed(name: StateName): boolean;
  dispose(): void;
}

export function createLoader<T extends Decoded>(
  urlFor: (name: StateName) => string,
  source: SheetSource<T>,
  opts: LoaderOptions = { maxDecoded: 4, keep: ["idle"] },
): Loader<T> {
  const blobs = new Map<StateName, Promise<Blob>>();
  const decoded = new Map<StateName, T>(); // insertion order is recency order
  const decoding = new Map<StateName, Promise<T>>();
  const failedSet = new Set<StateName>();
  const queue: StateName[] = [];
  let pumping = false;

  function fetchOnce(name: StateName): Promise<Blob> {
    let p = blobs.get(name);
    if (!p) {
      p = source.fetchBlob(urlFor(name));
      p.catch(() => failedSet.add(name));
      blobs.set(name, p);
    }
    return p;
  }

  async function pump() {
    if (pumping) return;
    pumping = true;
    while (queue.length) {
      const name = queue.shift()!;
      try { await fetchOnce(name); } catch { /* remembered in failedSet */ }
    }
    pumping = false;
  }

  function touch(name: StateName) {
    const v = decoded.get(name);
    if (v) { decoded.delete(name); decoded.set(name, v); }
  }

  function evict(justAdded: StateName) {
    for (const [name, v] of decoded) {
      if (decoded.size <= opts.maxDecoded) break;
      if (name === justAdded || opts.keep.includes(name)) continue;
      v.close?.();
      decoded.delete(name);
    }
  }

  return {
    prefetch(names) {
      for (const n of names) if (!blobs.has(n) && !queue.includes(n)) queue.push(n);
      void pump();
    },
    ensure(name) {
      const hit = decoded.get(name);
      if (hit) { touch(name); return Promise.resolve(hit); }
      let p = decoding.get(name);
      if (!p) {
        const i = queue.indexOf(name);
        if (i >= 0) queue.splice(i, 1);
        p = fetchOnce(name)
          .then((blob) => source.decode(blob, urlFor(name)))
          .then(
            (img) => { decoding.delete(name); decoded.set(name, img); evict(name); return img; },
            (err) => { decoding.delete(name); failedSet.add(name); throw err; },
          );
        decoding.set(name, p);
      }
      return p;
    },
    get: (name) => decoded.get(name),
    touch,
    failed: (name) => failedSet.has(name),
    dispose() {
      queue.length = 0;
      for (const v of decoded.values()) v.close?.();
      decoded.clear();
    },
  };
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/loader.test.ts`
Expected: PASS, 9 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/assets.ts site/src/ottie/loader.ts site/tests/unit/ottie/loader.test.ts
git commit -m "feat(ottie): load sheets in order, decode on demand and cache them"
```

### Task 6: Ottie's lines file and line rules

**Files:**
- Create: `site/src/ottie/lines.json`, `site/src/ottie/lines.ts`
- Test: `site/tests/unit/ottie/lines.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `type PageContext = "home" | "project" | "contact" | "devlog" | "404"`, `interface Lines { greeting: string[]; notFound: string[]; poke: string[]; tips: Record<PageContext, string[]> }`, `LINES: Lines`, `MAX_LINE_CHARS = 90`, `lintLine(line): string[]`, `pickLine(list, rng, used: Set<string>): string | undefined`.

The lines below are **drafts in Ottie's voice** (first person, short, warm, a little nerdy, honest, about Din and never as Din). They are copy: Din reviews and rewrites them in Task 17 before anything ships. The greeting is fixed by the PRD.

- [ ] **Step 1: Write the lines file**

```json
{
  "greeting": ["Hi, I’m Ottie."],
  "notFound": [
    "I looked closer. This page isn’t here.",
    "Nothing at this address. The links above still work."
  ],
  "poke": [
    "That tickles. Ask me something about Din instead?",
    "Still here. Glasses on, index loaded.",
    "I’m mostly fur and a small search index.",
    "I only know what Din has written down, but I know it well.",
    "Careful, these glasses are load bearing.",
    "If I don’t know something, I’ll say so and point you to Din."
  ],
  "tips": {
    "home": [
      "Try one of the suggested questions. I’ll show where each answer came from.",
      "Under every answer, “how this answer was made” lists the sources I used.",
      "In a hurry? Din’s resume and email are right at the top."
    ],
    "project": [
      "Ask me about this project. I’ll only search its own sources.",
      "The numbers on this page are real. Ask me how Din got them."
    ],
    "contact": [
      "Pick a reason and write a line. Din reads every letter.",
      "No account needed. A name, an email and a few words are enough."
    ],
    "devlog": [
      "Questions about this devlog? Ask me on the home page.",
      "Din writes these while building, mistakes included."
    ],
    "404": [
      "The home page is a good place to start over.",
      "Everything Din has published is on the work page."
    ]
  }
}
```

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/unit/ottie/lines.test.ts
import { describe, expect, it } from "vitest";
import { LINES, lintLine, pickLine, type PageContext } from "../../../src/ottie/lines";

const all = [...LINES.greeting, ...LINES.notFound, ...LINES.poke, ...Object.values(LINES.tips).flat()];

describe("Ottie's lines", () => {
  it("every line passes the rules", () => {
    for (const line of all) expect(lintLine(line), line).toEqual([]);
  });

  it("has the fixed greeting and enough lines for each place", () => {
    expect(LINES.greeting).toEqual(["Hi, I’m Ottie."]);
    expect(LINES.poke.length).toBeGreaterThanOrEqual(4);
    for (const ctx of ["home", "project", "contact", "devlog", "404"] as PageContext[]) {
      expect(LINES.tips[ctx].length, ctx).toBeGreaterThanOrEqual(2);
    }
    expect(new Set(all).size).toBe(all.length);
  });

  it("flags what the rules forbid", () => {
    expect(lintLine("x".repeat(91))).toContain("longer than 90 characters");
    expect(lintLine("Look \u2014 here")).toContain("dash used as a separator");
    expect(lintLine("Wow!")).toContain("exclamation mark");
    expect(lintLine("I'm here")).toContain("straight apostrophe (use ’)");
    expect(lintLine("A seamless answer")).toContain("buzzword: seamless");
    expect(lintLine(" padded")).toContain("leading or trailing space");
  });

  it("picks without repeating until the list runs out", () => {
    const used = new Set<string>();
    const rng = () => 0;
    expect(pickLine(["a", "b"], rng, used)).toBe("a");
    expect(pickLine(["a", "b"], rng, used)).toBe("b");
    expect(pickLine(["a", "b"], rng, used)).toBeUndefined();
  });
});
```

- [ ] **Step 3: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/lines.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/lines".

- [ ] **Step 4: Write the implementation**

```ts
// site/src/ottie/lines.ts
// Ottie's words come only from lines.json, which Din reviews. Nothing is generated live.
import data from "./lines.json";

export type PageContext = "home" | "project" | "contact" | "devlog" | "404";
export interface Lines { greeting: string[]; notFound: string[]; poke: string[]; tips: Record<PageContext, string[]> }

export const LINES: Lines = data;
export const MAX_LINE_CHARS = 90;
const BUZZWORDS = ["elevate", "seamless", "unleash", "journey", "tapestry"];

export function lintLine(line: string): string[] {
  const problems: string[] = [];
  if (!line.trim()) problems.push("empty");
  if (line !== line.trim()) problems.push("leading or trailing space");
  if ([...line].length > MAX_LINE_CHARS) problems.push(`longer than ${MAX_LINE_CHARS} characters`);
  if (/[\u2013\u2014]/.test(line)) problems.push("dash used as a separator");
  if (line.includes("!")) problems.push("exclamation mark");
  if (line.includes("'")) problems.push("straight apostrophe (use ’)");
  for (const word of BUZZWORDS) if (line.toLowerCase().includes(word)) problems.push(`buzzword: ${word}`);
  return problems;
}

export function pickLine(list: readonly string[], rng: () => number, used: Set<string>): string | undefined {
  const fresh = list.filter((l) => !used.has(l));
  if (!fresh.length) return undefined;
  const line = fresh[Math.floor(rng() * fresh.length)];
  used.add(line);
  return line;
}
```

- [ ] **Step 5: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/lines.test.ts`
Expected: PASS, 4 tests.

- [ ] **Step 6: Commit**

```bash
git add site/src/ottie/lines.json site/src/ottie/lines.ts site/tests/unit/ottie/lines.test.ts
git commit -m "feat(ottie): add the draft lines file with length and style checks"
```

### Task 7: Bubble rules

**Files:**
- Create: `site/src/ottie/bubble.ts`
- Test: `site/tests/unit/ottie/bubble.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `BUBBLE_GAP_MS = 20_000`, `createBubbleGate(gapMs?): { canSpeak(now: number): boolean; spoke(now: number): void }`, `bubbleMs(text): number` (2.5 s plus 45 ms per character, at most 6 s), `interface Rect { x; y; w; h: number }`, `overlaps(a, b): boolean`, `type BubbleSide = "left" | "right"`, `placeBubble(ottie: Rect, size: { w; h }, avoid: Rect[], viewport: { w; h }, gap = 8): { side: BubbleSide; rect: Rect } | null`.

Placement: above Ottie's box, first to the left (the bubble's right edge at 70 percent of Ottie's width, as in the home sketch), then to the right (left edge at 30 percent). A spot is rejected if it leaves the viewport or overlaps any `[data-ottie-avoid]` rect. No spot means no bubble.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/bubble.test.ts
import { describe, expect, it } from "vitest";
import { bubbleMs, createBubbleGate, overlaps, placeBubble } from "../../../src/ottie/bubble";

const ottie = { x: 1000, y: 400, w: 160, h: 200 };
const size = { w: 220, h: 60 };
const viewport = { w: 1280, h: 800 };

describe("bubbles", () => {
  it("allow one bubble every 20 seconds", () => {
    const gate = createBubbleGate();
    expect(gate.canSpeak(0)).toBe(true);
    gate.spoke(1_000);
    expect(gate.canSpeak(20_999)).toBe(false);
    expect(gate.canSpeak(21_000)).toBe(true);
  });

  it("stay up long enough to read, but not forever", () => {
    expect(bubbleMs("Hi, I’m Ottie.")).toBe(3130);
    expect(bubbleMs("x".repeat(90))).toBe(6000);
  });

  it("detect overlap, but not touching edges", () => {
    expect(overlaps({ x: 0, y: 0, w: 10, h: 10 }, { x: 5, y: 5, w: 10, h: 10 })).toBe(true);
    expect(overlaps({ x: 0, y: 0, w: 10, h: 10 }, { x: 10, y: 0, w: 10, h: 10 })).toBe(false);
  });

  it("sit above Ottie on the left when there is room", () => {
    expect(placeBubble(ottie, size, [], viewport)).toEqual({ side: "left", rect: { x: 892, y: 332, w: 220, h: 60 } });
  });

  it("move right when the left spot covers the input, and give up when both do", () => {
    const input = { x: 700, y: 320, w: 300, h: 80 };
    expect(placeBubble(ottie, size, [input], viewport)?.side).toBe("right");
    const wide = { x: 600, y: 300, w: 680, h: 120 };
    expect(placeBubble(ottie, size, [wide], viewport)).toBeNull();
  });

  it("never leave the viewport", () => {
    expect(placeBubble({ ...ottie, y: 20 }, size, [], viewport)).toBeNull();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/bubble.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/bubble".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/bubble.ts
export const BUBBLE_GAP_MS = 20_000;

export function createBubbleGate(gapMs = BUBBLE_GAP_MS) {
  let last = -Infinity;
  return {
    canSpeak: (now: number) => now - last >= gapMs,
    spoke: (now: number) => { last = now; },
  };
}

export const bubbleMs = (text: string): number => Math.min(6000, 2500 + 45 * [...text].length);

export interface Rect { x: number; y: number; w: number; h: number }
export type BubbleSide = "left" | "right";

export const overlaps = (a: Rect, b: Rect): boolean =>
  a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;

const inside = (r: Rect, vp: { w: number; h: number }) => r.x >= 0 && r.y >= 0 && r.x + r.w <= vp.w && r.y + r.h <= vp.h;

export function placeBubble(
  ottie: Rect, size: { w: number; h: number }, avoid: Rect[], viewport: { w: number; h: number }, gap = 8,
): { side: BubbleSide; rect: Rect } | null {
  const y = ottie.y - size.h - gap;
  const spots: { side: BubbleSide; rect: Rect }[] = [
    { side: "left", rect: { x: ottie.x + ottie.w * 0.7 - size.w, y, w: size.w, h: size.h } },
    { side: "right", rect: { x: ottie.x + ottie.w * 0.3, y, w: size.w, h: size.h } },
  ];
  return spots.find((s) => inside(s.rect, viewport) && !avoid.some((a) => overlaps(s.rect, a))) ?? null;
}
```

Check of the numbers in the test: left spot x = 1000 + 112 - 220 = 892, y = 400 - 60 - 8 = 332. The input rect (700 to 1000, 320 to 400) overlaps the left spot (892 to 1112) but not the right spot (1048 to 1268).

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/bubble.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/bubble.ts site/tests/unit/ottie/bubble.test.ts
git commit -m "feat(ottie): add bubble timing and placement that avoids the input and answer"
```

### Task 8: Preferences, visits and modes

**Files:**
- Create: `site/src/ottie/prefs.ts`
- Test: `site/tests/unit/ottie/prefs.test.ts`

**Interfaces:**
- Consumes: nothing.
- Produces: `KEYS = { quiet: "dins.ottie.quiet", seen: "dins.ottie.seen", session: "dins.ottie.session", tips: "dins.ottie.tips" }`, `PHONE_MAX_PX = 639`, `LOW_MEMORY_GB = 2`, `type Mode = "full" | "reduced" | "still"`, `type Visit = "first" | "returning" | "session"`, `interface StorageLike { getItem; setItem; removeItem }`, `interface SafeStorage { readonly ok: boolean; getItem(k): string | null; setItem(k, v): void }`, `safe(get: () => StorageLike | undefined): SafeStorage`, `localStore()`, `sessionStore()`, `readQuiet(ls)`, `writeQuiet(ls, on)`, `visitKind(ls, ss): Visit`, `markVisit(ls, ss, now?)`, `tipsShown(ss): number`, `recordTip(ss)`, `interface DeviceHints { reducedMotion: boolean; calm: boolean; saveData: boolean; deviceMemory?: number; phone: boolean }`, `deviceHints(): DeviceHints` (browser only; `calm` is `<html data-motion="calm">`, set before paint by M4's `MotionHead.astro`), `modeFor(quiet, hints): Mode`.

Rules: when storage is blocked, the visit counts as `"session"` (no run-in, no greeting), so a visitor in private mode is never greeted on every page. The pre-paint script in Task 13 must agree with `visitKind` and `modeFor`; Task 14 checks that end to end.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/prefs.test.ts
import { describe, expect, it } from "vitest";
import {
  KEYS, markVisit, modeFor, readQuiet, recordTip, safe, tipsShown, visitKind, writeQuiet, type StorageLike,
} from "../../../src/ottie/prefs";

function mem(): StorageLike {
  const m = new Map<string, string>();
  return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => void m.set(k, v), removeItem: (k) => void m.delete(k) };
}
const broken: StorageLike = {
  getItem: () => { throw new Error("SecurityError"); },
  setItem: () => { throw new Error("QuotaExceededError"); },
  removeItem: () => { throw new Error("SecurityError"); },
};

describe("visits", () => {
  it("first, then session within the tab, then returning in a new session", () => {
    const local = mem();
    const ls = safe(() => local), ss = safe(() => mem());
    expect(visitKind(ls, ss)).toBe("first");
    markVisit(ls, ss, 123);
    expect(visitKind(ls, ss)).toBe("session");
    expect(local.getItem(KEYS.seen)).toBe("123");
    expect(visitKind(safe(() => local), safe(() => mem()))).toBe("returning");
  });

  it("treats blocked storage as a session visit and never throws", () => {
    const ls = safe(() => broken), ss = safe(() => broken);
    expect(ls.ok).toBe(false);
    expect(visitKind(ls, ss)).toBe("session");
    expect(() => { markVisit(ls, ss); writeQuiet(ls, true); recordTip(ss); }).not.toThrow();
    expect(readQuiet(ls)).toBe(false);
    expect(tipsShown(ss)).toBe(0);
    expect(safe(() => undefined).ok).toBe(false);
  });
});

describe("quiet and tips", () => {
  it("remembers Quiet Ottie", () => {
    const ls = safe(() => mem());
    expect(readQuiet(ls)).toBe(false);
    writeQuiet(ls, true);
    expect(readQuiet(ls)).toBe(true);
    writeQuiet(ls, false);
    expect(readQuiet(ls)).toBe(false);
  });

  it("counts tips per visit", () => {
    const ss = safe(() => mem());
    recordTip(ss); recordTip(ss);
    expect(tipsShown(ss)).toBe(2);
  });
});

describe("modes", () => {
  const hints = { reducedMotion: false, calm: false, saveData: false, deviceMemory: 8, phone: false };
  it("picks still, reduced or full", () => {
    expect(modeFor(false, hints)).toBe("full");
    expect(modeFor(true, hints)).toBe("still");
    expect(modeFor(false, { ...hints, saveData: true })).toBe("still");
    expect(modeFor(false, { ...hints, deviceMemory: 2 })).toBe("still");
    expect(modeFor(false, { ...hints, deviceMemory: undefined })).toBe("full");
    expect(modeFor(false, { ...hints, reducedMotion: true })).toBe("reduced");
    expect(modeFor(true, { ...hints, reducedMotion: true })).toBe("still");
  });
  it("treats M4's calm switch like reduced motion", () => {
    expect(modeFor(false, { ...hints, calm: true })).toBe("reduced");
    expect(modeFor(false, { ...hints, calm: true, saveData: true })).toBe("still");
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/prefs.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/prefs".

- [ ] **Step 3: Write the implementation**

```ts
// site/src/ottie/prefs.ts
// Storage keys are also read by the pre-paint script in components/Ottie.astro.
export const KEYS = {
  quiet: "dins.ottie.quiet",
  seen: "dins.ottie.seen",
  session: "dins.ottie.session",
  tips: "dins.ottie.tips",
} as const;
export const PHONE_MAX_PX = 639;
export const LOW_MEMORY_GB = 2;

export type Mode = "full" | "reduced" | "still";
export type Visit = "first" | "returning" | "session";

export interface StorageLike { getItem(k: string): string | null; setItem(k: string, v: string): void; removeItem(k: string): void }
export interface SafeStorage { readonly ok: boolean; getItem(k: string): string | null; setItem(k: string, v: string): void }

export function safe(get: () => StorageLike | undefined): SafeStorage {
  let ok = false;
  try {
    const s = get();
    if (s) { s.setItem("dins.ottie.probe", "1"); s.removeItem("dins.ottie.probe"); ok = true; }
  } catch { ok = false; }
  return {
    ok,
    getItem: (k) => { if (!ok) return null; try { return get()!.getItem(k); } catch { return null; } },
    setItem: (k, v) => { if (!ok) return; try { get()!.setItem(k, v); } catch { /* full or blocked */ } },
  };
}

export const localStore = () => safe(() => globalThis.localStorage);
export const sessionStore = () => safe(() => globalThis.sessionStorage);

export const readQuiet = (ls: SafeStorage) => ls.getItem(KEYS.quiet) === "1";
export const writeQuiet = (ls: SafeStorage, on: boolean) => ls.setItem(KEYS.quiet, on ? "1" : "0");

export function visitKind(ls: SafeStorage, ss: SafeStorage): Visit {
  if (!ls.ok || !ss.ok || ss.getItem(KEYS.session)) return "session";
  return ls.getItem(KEYS.seen) ? "returning" : "first";
}

export function markVisit(ls: SafeStorage, ss: SafeStorage, now = Date.now()) {
  ss.setItem(KEYS.session, "1");
  if (!ls.getItem(KEYS.seen)) ls.setItem(KEYS.seen, String(now));
}

export const tipsShown = (ss: SafeStorage) => Number(ss.getItem(KEYS.tips)) || 0;
export const recordTip = (ss: SafeStorage) => ss.setItem(KEYS.tips, String(tipsShown(ss) + 1));

export interface DeviceHints { reducedMotion: boolean; calm: boolean; saveData: boolean; deviceMemory?: number; phone: boolean }

export function deviceHints(): DeviceHints {
  const nav = navigator as Navigator & { connection?: { saveData?: boolean }; deviceMemory?: number };
  return {
    reducedMotion: matchMedia("(prefers-reduced-motion: reduce)").matches,
    // M4's MotionHead sets data-motion before first paint (calm for ?calm, reduced motion, Save-Data, low memory).
    calm: document.documentElement.dataset.motion === "calm",
    saveData: Boolean(nav.connection?.saveData),
    deviceMemory: nav.deviceMemory,
    phone: matchMedia(`(max-width: ${PHONE_MAX_PX}px)`).matches,
  };
}

export function modeFor(quiet: boolean, h: DeviceHints): Mode {
  if (quiet || h.saveData || (h.deviceMemory !== undefined && h.deviceMemory <= LOW_MEMORY_GB)) return "still";
  return h.reducedMotion || h.calm ? "reduced" : "full";
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/prefs.test.ts`
Expected: PASS, 6 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/prefs.ts site/tests/unit/ottie/prefs.test.ts
git commit -m "feat(ottie): remember Quiet Ottie and visits, and pick the playback mode"
```

### Task 9: The director, part 1: openers, cues, poke and silence

**Files:**
- Create: `site/src/ottie/director.ts`
- Modify: `site/tests/unit/ottie/fixtures.ts` (append director helpers)
- Test: `site/tests/unit/ottie/director.test.ts`

**Interfaces:**
- Consumes: `StateName` (Task 2), `OttieCueDetail` (Task 1), `createBubbleGate`, `bubbleMs` (Task 7), `Lines`, `PageContext`, `pickLine` (Task 6), `Mode`, `Visit` (Task 8).
- Produces: `interface DirectorEnv { mode: Mode; phone: boolean; context: PageContext; visit: Visit; tipsShown: number }`, `type Command = { kind: "prefetch"; states: StateName[] } | { kind: "play"; states: StateName[] } | { kind: "say"; text: string; ms: number; tip: boolean } | { kind: "hush" }`, `type Interaction = "pointer" | "key" | "scroll" | "background-click" | "poke"`, `interface Director { start(now): Command[]; entered(state: StateName, now): Command[]; cue(cue: OttieCueDetail, now): Command[]; interact(kind: Interaction, now): Command[]; tick(now): Command[]; bubbleDone(now): Command[] }`, `createDirector(env, lines, rng = Math.random): Director`, and the timing constants used in Task 10.

The director is pure: it gets times as numbers and returns commands; the player (Task 12) runs them. Within one returned list, a `play` always comes before the `say` it belongs to, so if the bubble cannot be placed the player's `bubbleDone` can cancel the talk loop. Openers (decisions 6 and 7):

| Visit and page | Prefetch (in order) | Play |
|---|---|---|
| First visit, full motion | run-in, wave, idle | run-in, wave, then "Hi, I’m Ottie." when wave starts |
| Returning (new session) | idle, wave | wave |
| Same session | idle, wave | nothing |
| 404 page | idle, shrug | shrug, with a not-found line |
| Contact host (the letter Ottie, on home and `/contact`) | idle, point | nothing: it starts in idle, never greets, and points on `letter:open` |
| Reduced motion | only the opener's states, never idle or run-in | key poses |
| Still mode (Quiet, Save-Data, low memory) | nothing | nothing |

The visit a director sees comes from the page controller (`hostVisit` in Task 11, wired in Task 12): the page's first host gets the real visit, every other host gets `session`, so only the first host can greet.

Cues: `ask:focus` prefetches think; `ask:typing` silences bubbles for 2 s; `ask:submit` hushes and plays think; `ask:stream` prefetches nod, point and shrug; `ask:answer` plays nod then point (nod alone without sources); `ask:unknown`, `ask:resting`, `ask:error` play shrug; `ask:reset` plays idle; `letter:open` prefetches and plays point; `letter:ready` prefetches jump; `letter:sent` plays jump. No bubble ever starts while typing or streaming.

- [ ] **Step 1: Append the director helpers to the fixtures**

```ts
// append to site/tests/unit/ottie/fixtures.ts
import { createDirector, type Command, type Director, type DirectorEnv } from "../../../src/ottie/director";
import type { Lines } from "../../../src/ottie/lines";

export const testLines: Lines = {
  greeting: ["Hi, I’m Ottie."],
  notFound: ["nf1", "nf2"],
  poke: ["p1", "p2", "p3"],
  tips: { home: ["t1", "t2", "t3", "t4"], project: ["tp1", "tp2"], contact: ["tc1", "tc2"], devlog: ["td1", "td2"], "404": ["tn1", "tn2"] },
};
export const envOf = (o: Partial<DirectorEnv> = {}): DirectorEnv =>
  ({ mode: "full", phone: false, context: "home", visit: "returning", tipsShown: 0, ...o });
export function director(o: Partial<DirectorEnv> = {}): { d: Director; opener: Command[] } {
  const d = createDirector(envOf(o), testLines, () => 0);
  return { d, opener: d.start(0) };
}
export const says = (cmds: Command[]) => cmds.filter((c) => c.kind === "say");
```

(Move the two new `import` lines to the top of `fixtures.ts` with the others.)

- [ ] **Step 2: Write the failing test**

```ts
// site/tests/unit/ottie/director.test.ts
import { describe, expect, it } from "vitest";
import { director, says } from "./fixtures";

const play = (...states: string[]) => ({ kind: "play", states });
const prefetch = (...states: string[]) => ({ kind: "prefetch", states });

describe("director openers", () => {
  it("does nothing at all in still mode", () => {
    const { d, opener } = director({ mode: "still", visit: "first" });
    expect(opener).toEqual([]);
    expect(d.cue({ type: "ask:submit" }, 1)).toEqual([]);
    expect(d.interact("poke", 2)).toEqual([]);
    expect(d.tick(60_000)).toEqual([]);
  });

  it("greets a first visit with run-in, wave and a hello", () => {
    const { d, opener } = director({ visit: "first" });
    expect(opener).toEqual([prefetch("run-in", "wave", "idle"), play("run-in", "wave")]);
    expect(d.entered("run-in", 100)).toEqual([]);
    expect(d.entered("wave", 2300)).toEqual([{ kind: "say", text: "Hi, I’m Ottie.", ms: 3130, tip: false }]);
    expect(d.bubbleDone(5430)).toEqual([]);
  });

  it("waves at returning visitors without a line", () => {
    const { d, opener } = director({ visit: "returning" });
    expect(opener).toEqual([prefetch("idle", "wave"), play("wave")]);
    expect(d.entered("wave", 100)).toEqual([]);
  });

  it("starts in idle on later pages of the same session", () => {
    expect(director({ visit: "session" }).opener).toEqual([prefetch("idle", "wave")]);
  });

  it("uses key poses and skips idle and run-in under reduced motion", () => {
    expect(director({ mode: "reduced", visit: "first" }).opener).toEqual([prefetch("wave"), play("wave")]);
    expect(director({ mode: "reduced", visit: "session" }).opener).toEqual([]);
  });

  it("greets first visits on project and devlog pages too", () => {
    for (const context of ["project", "devlog"] as const) {
      const { d, opener } = director({ context, visit: "first" });
      expect(opener).toEqual([prefetch("run-in", "wave", "idle"), play("run-in", "wave")]);
      expect(says(d.entered("wave", 2300))).toHaveLength(1);
    }
  });

  it("shrugs on the 404 page", () => {
    const { d, opener } = director({ context: "404", visit: "first" });
    expect(opener).toEqual([prefetch("idle", "shrug"), play("shrug")]);
    expect(says(d.entered("shrug", 500))).toEqual([expect.objectContaining({ text: "nf1" })]);
  });

  it("starts the letter Ottie in idle with point ready, and never greets", () => {
    const { d, opener } = director({ context: "contact", visit: "first" });
    expect(opener).toEqual([prefetch("idle", "point")]);
    expect(d.entered("wave", 100)).toEqual([]);
    expect(director({ context: "contact", mode: "reduced", visit: "first" }).opener).toEqual([]);
  });
});

describe("director cues", () => {
  it("follows a question through to the answer", () => {
    const { d } = director();
    expect(d.cue({ type: "ask:focus" }, 1000)).toEqual([prefetch("think")]);
    expect(d.cue({ type: "ask:submit" }, 2000)).toEqual([play("think")]);
    expect(d.cue({ type: "ask:stream" }, 2500)).toEqual([prefetch("nod", "point", "shrug")]);
    expect(d.cue({ type: "ask:answer", sources: 2 }, 4000)).toEqual([play("nod", "point")]);
    d.cue({ type: "ask:submit" }, 5000);
    expect(d.cue({ type: "ask:answer", sources: 0 }, 6000)).toEqual([play("nod")]);
  });

  it("shrugs for don't know, resting and errors, and resets to idle", () => {
    const { d } = director();
    for (const type of ["ask:unknown", "ask:resting", "ask:error"] as const) {
      d.cue({ type: "ask:submit" }, 1000);
      expect(d.cue({ type }, 2000)).toEqual([play("shrug")]);
    }
    expect(d.cue({ type: "ask:reset" }, 3000)).toEqual([play("idle")]);
  });

  it("hushes the greeting when a question is sent", () => {
    const { d } = director({ visit: "first" });
    d.entered("wave", 2300);
    expect(d.cue({ type: "ask:submit" }, 2500)).toEqual([{ kind: "hush" }, play("think")]);
  });

  it("stays silent while an answer streams", () => {
    const { d } = director({ visit: "first" });
    d.cue({ type: "ask:submit" }, 100);
    expect(d.entered("wave", 2300)).toEqual([]);
    expect(d.interact("poke", 3000)).toEqual([]);
  });

  it("drives the letter", () => {
    const { d } = director({ context: "contact" });
    expect(d.cue({ type: "letter:open" }, 1000)).toEqual([prefetch("point"), play("point")]);
    expect(d.cue({ type: "letter:ready" }, 2000)).toEqual([prefetch("jump")]);
    expect(d.cue({ type: "letter:sent" }, 3000)).toEqual([play("jump")]);
  });
});

describe("director poke", () => {
  it("hops and says a line, then goes back to idle", () => {
    const { d } = director();
    expect(d.interact("poke", 1000)).toEqual([play("poke", "talk"), { kind: "say", text: "p1", ms: 2590, tip: false }]);
    expect(d.bubbleDone(3590)).toEqual([play("idle")]);
  });

  it("only hops while the 20 second gate is closed, and does not repeat lines", () => {
    const { d } = director();
    d.interact("poke", 1000);
    d.bubbleDone(3590);
    expect(d.interact("poke", 5000)).toEqual([play("poke")]);
    expect(says(d.interact("poke", 21_000))).toEqual([expect.objectContaining({ text: "p2" })]);
  });

  it("survives poke spam with one bubble", () => {
    const { d } = director();
    const all = Array.from({ length: 20 }, (_, i) => d.interact("poke", 1000 + i * 100)).flat();
    expect(says(all)).toHaveLength(1);
  });

  it("stops talking when someone starts typing", () => {
    const { d } = director();
    d.interact("poke", 1000);
    expect(d.cue({ type: "ask:typing" }, 1500)).toEqual([{ kind: "hush" }, play("idle")]);
  });
});
```

- [ ] **Step 3: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/director.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/director".

- [ ] **Step 4: Write the implementation**

```ts
// site/src/ottie/director.ts
// Ottie's behaviour rules (PRD section 4) as a pure function of cues, interactions
// and time. The player runs the commands; nothing here touches the DOM.
import { bubbleMs, createBubbleGate } from "./bubble";
import type { OttieCueDetail } from "./events";
import { greetsIn } from "./hosts";
import { pickLine, type Lines, type PageContext } from "./lines";
import type { StateName } from "./manifest";
import type { Mode, Visit } from "./prefs";

export const TIP_AFTER_MS = 20_000;
export const TALK_PREFETCH_MS = 15_000;
export const NAP_PREFETCH_MS = 45_000;
export const NAP_AFTER_MS = 60_000;
export const MAX_TIPS = 3;
export const TYPING_HOLD_MS = 2_000;
export const CLICK_BURST = 6;
export const CLICK_WINDOW_MS = 4_000;
export const MAX_TICK_MS = 2_000;

export interface DirectorEnv { mode: Mode; phone: boolean; context: PageContext; visit: Visit; tipsShown: number }
export type Command =
  | { kind: "prefetch"; states: StateName[] }
  | { kind: "play"; states: StateName[] }
  | { kind: "say"; text: string; ms: number; tip: boolean }
  | { kind: "hush" };
export type Interaction = "pointer" | "key" | "scroll" | "background-click" | "poke";
export interface Director {
  start(now: number): Command[];
  entered(state: StateName, now: number): Command[];
  cue(cue: OttieCueDetail, now: number): Command[];
  interact(kind: Interaction, now: number): Command[];
  tick(now: number): Command[];
  bubbleDone(now: number): Command[];
}

export function createDirector(env: DirectorEnv, lines: Lines, rng: () => number = Math.random): Director {
  const still = env.mode === "still";
  const reduced = env.mode === "reduced";
  const gate = createBubbleGate();
  let lastTick: number | null = null;
  let quietMs = 0;
  let typingUntil = -Infinity;
  let streaming = false, asleep = false, talking = false, bubbleUp = false;
  let tipThisStretch = false, tipsShown = env.tipsShown;
  let greetingPending = false, notFoundPending = false, talkPrefetched = false, napPrefetched = false;
  let clicks: number[] = [];
  const usedPokes = new Set<string>(), usedTips = new Set<string>(), usedNotFound = new Set<string>();

  const play = (...states: StateName[]): Command => ({ kind: "play", states });
  const prefetch = (...states: StateName[]): Command => ({ kind: "prefetch", states });
  const canSpeak = (now: number) => !bubbleUp && !streaming && now >= typingUntil && gate.canSpeak(now);

  function say(text: string, now: number, tip = false): Command {
    gate.spoke(now);
    bubbleUp = true;
    return { kind: "say", text, ms: bubbleMs(text), tip };
  }
  function hush(idleAfter: boolean): Command[] {
    if (!bubbleUp) return [];
    bubbleUp = false;
    const out: Command[] = [{ kind: "hush" }];
    if (talking) { talking = false; if (idleAfter) out.push(play("idle")); }
    return out;
  }
  function activity() { quietMs = 0; tipThisStretch = false; }
  function wake(): Command[] {
    if (!asleep) return [];
    asleep = false;
    return [play("idle")]; // the timeline leaves nap through wake (exit_via)
  }

  return {
    start(now) {
      if (still) return [];
      lastTick = now;
      const notFound = env.context === "404";
      const letter = env.context === "contact"; // the letter Ottie starts in idle and never greets
      const opener: StateName[] = notFound ? ["shrug"]
        : letter ? []
        : env.visit === "first" ? (reduced ? ["wave"] : ["run-in", "wave"])
        : env.visit === "returning" ? ["wave"] : [];
      greetingPending = greetsIn(env.context) && env.visit === "first";
      notFoundPending = notFound;
      const order: StateName[] = reduced ? [...opener]
        : greetingPending ? ["run-in", "wave", "idle"]
        : letter ? ["idle", "point"]
        : ["idle", notFound ? "shrug" : "wave"];
      const out: Command[] = [];
      if (order.length) out.push(prefetch(...order));
      if (opener.length) out.push(play(...opener));
      return out;
    },

    entered(state, now) {
      if (still) return [];
      if (state === "wave" && greetingPending) {
        greetingPending = false;
        return canSpeak(now) ? [say(lines.greeting[0], now)] : [];
      }
      if (state === "shrug" && notFoundPending) {
        notFoundPending = false;
        const text = pickLine(lines.notFound, rng, usedNotFound);
        return text && canSpeak(now) ? [say(text, now)] : [];
      }
      return [];
    },

    cue(cue, now) {
      if (still) return [];
      activity();
      switch (cue.type) {
        case "ask:focus": return [...wake(), prefetch("think")];
        case "ask:typing": typingUntil = now + TYPING_HOLD_MS; return [...wake(), ...hush(true)];
        case "ask:submit": asleep = false; streaming = true; return [...hush(false), play("think")];
        case "ask:stream": return [prefetch("nod", "point", "shrug")];
        case "ask:answer":
          asleep = false; streaming = false;
          return [(cue.sources ?? 0) > 0 ? play("nod", "point") : play("nod")];
        case "ask:unknown": case "ask:resting": case "ask:error":
          asleep = false; streaming = false;
          return [play("shrug")];
        case "ask:reset": asleep = false; streaming = false; return [...hush(false), play("idle")];
        case "letter:open": asleep = false; return [prefetch("point"), play("point")];
        case "letter:ready": return [...wake(), prefetch("jump")];
        case "letter:sent": asleep = false; return [...hush(false), play("jump")];
      }
    },

    interact(kind, now) {
      if (still) return [];
      if (kind === "background-click") return []; // Task 10
      activity();
      if (kind === "scroll") return [];
      if (kind === "poke") {
        if (streaming) return [];
        if (asleep) return wake();
        if (!canSpeak(now)) return [play("poke")];
        let text = pickLine(lines.poke, rng, usedPokes);
        if (!text) { usedPokes.clear(); text = pickLine(lines.poke, rng, usedPokes); }
        if (!text) return [play("poke")];
        talking = true;
        return [play("poke", "talk"), say(text, now)];
      }
      return wake();
    },

    tick(_now) {
      return []; // Task 10
    },

    bubbleDone(_now) {
      bubbleUp = false;
      if (!talking) return [];
      talking = false;
      return [play("idle")];
    },
  };
}
```

The variables `lastTick`, `quietMs`, `clicks`, `tipsShown`, `tipThisStretch`, `talkPrefetched`, `napPrefetched` and `usedTips` are used by Task 10; if the linter flags them as unused in this commit, that is expected and fixed by Task 10.

- [ ] **Step 5: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/director.test.ts`
Expected: PASS, 17 tests. (Task 9 imports `greetsIn` from Task 11's `hosts.ts`; if Task 11 is not written yet, write its `GREETING_CONTEXTS` and `greetsIn` lines first, with their test, and finish Task 11 in its turn.)

- [ ] **Step 6: Commit**

```bash
git add site/src/ottie/director.ts site/tests/unit/ottie/director.test.ts site/tests/unit/ottie/fixtures.ts
git commit -m "feat(ottie): add the director for openers, answer cues, poke and silence"
```

### Task 10: The director, part 2: tips, nap, wake and background clicks

**Files:**
- Modify: `site/src/ottie/director.ts` (the `tick` method and the `background-click` branch of `interact`)
- Test: `site/tests/unit/ottie/director-quiet.test.ts`

**Interfaces:**
- Consumes: Task 9's director and helpers.
- Produces: the complete `Director`. No new names.

Rules: quiet time grows only while nothing is going on (no bubble, no typing, no streaming) and by at most 2 s per tick, so a tab hidden for minutes does not come back asleep. Talk is prefetched at 15 s of quiet; a tip shows at 20 s (one per quiet stretch, at most 3 per visit, gate permitting); nap is prefetched at 45 s and played at 60 s. Six background clicks within 4 s also send Ottie to nap. Phones get neither tips nor naps. A real interaction (pointer on something interactive, a key, a cue, a poke) wakes Ottie; scrolling resets the quiet timer but does not wake Ottie.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/director-quiet.test.ts
import { describe, expect, it } from "vitest";
import type { Command, Director } from "../../../src/ottie/director";
import { director, says } from "./fixtures";

type Log = { t: number; cmds: Command[] }[];
function run(d: Director, from: number, to: number, before?: (t: number) => void): Log {
  const log: Log = [];
  for (let t = from; t <= to; t += 1000) {
    before?.(t);
    const cmds = d.tick(t);
    if (cmds.length) log.push({ t, cmds });
  }
  return log;
}
const at = (log: Log, kind: string, state?: string) =>
  log.filter((e) => e.cmds.some((c) => c.kind === kind && (!state || ("states" in c && c.states.includes(state as never))))).map((e) => e.t);

describe("tips", () => {
  it("prefetches talk at 15 s and shows a tip at 20 s of quiet", () => {
    const { d } = director();
    const log = run(d, 1000, 20_000);
    expect(log).toEqual([
      { t: 15_000, cmds: [{ kind: "prefetch", states: ["talk"] }] },
      { t: 20_000, cmds: [{ kind: "play", states: ["talk"] }, { kind: "say", text: "t1", ms: 2590, tip: true }] },
    ]);
  });

  it("shows one tip per quiet stretch, then naps 60 s after the bubble closes", () => {
    const { d } = director();
    const log = run(d, 1000, 90_000, (t) => { if (t === 25_000) d.bubbleDone(t); });
    expect(at(log, "say")).toEqual([20_000]);
    expect(at(log, "prefetch", "nap")).toEqual([69_000]);
    expect(at(log, "play", "nap")).toEqual([84_000]);
  });

  it("starts a new stretch after an interaction, up to 3 tips per visit", () => {
    const { d } = director({ tipsShown: 2 });
    const log = run(d, 1000, 120_000, (t) => {
      if (t % 30_000 === 0) d.interact("pointer", t);
      if (t === 25_000) d.bubbleDone(t);
    });
    expect(at(log, "say")).toEqual([20_000]);
  });

  it("waits while someone types", () => {
    const { d } = director();
    const log = run(d, 1000, 60_000, (t) => {
      if (t === 19_000) d.cue({ type: "ask:typing" }, t);
      if (t === 45_000) d.bubbleDone(t);
    });
    expect(at(log, "say")).toEqual([40_000]);
  });

  it("never shows tips or naps on phones", () => {
    const { d } = director({ phone: true });
    expect(run(d, 1000, 180_000)).toEqual([]);
  });
});

describe("nap and wake", () => {
  const sleepy = () => {
    const { d } = director({ tipsShown: 3 });
    const log = run(d, 1000, 60_000);
    return { d, log };
  };

  it("naps after a minute of quiet", () => {
    const { log } = sleepy();
    expect(log).toEqual([
      { t: 45_000, cmds: [{ kind: "prefetch", states: ["nap", "wake"] }] },
      { t: 60_000, cmds: [{ kind: "play", states: ["nap"] }] },
    ]);
  });

  it("keeps sleeping through scrolling and wakes on a real interaction", () => {
    const { d } = sleepy();
    expect(d.tick(61_000)).toEqual([]);
    expect(d.interact("scroll", 62_000)).toEqual([]);
    expect(d.interact("pointer", 63_000)).toEqual([{ kind: "play", states: ["idle"] }]);
  });

  it("wakes for cues", () => {
    const a = sleepy().d;
    expect(a.cue({ type: "ask:focus" }, 61_000)).toEqual([{ kind: "play", states: ["idle"] }, { kind: "prefetch", states: ["think"] }]);
    const b = sleepy().d;
    expect(b.cue({ type: "ask:submit" }, 61_000)).toEqual([{ kind: "play", states: ["think"] }]);
  });

  it("naps after a burst of background clicks", () => {
    const { d } = director();
    for (let i = 0; i < 5; i++) expect(d.interact("background-click", 1000 + i * 500)).toEqual([]);
    expect(d.interact("background-click", 3600)).toEqual([
      { kind: "prefetch", states: ["nap", "wake"] }, { kind: "play", states: ["nap"] },
    ]);
  });

  it("ignores slow clicking and clicking on phones", () => {
    const slow = director().d;
    for (let i = 0; i < 12; i++) expect(slow.interact("background-click", 1000 + i * 1000)).toEqual([]);
    const phone = director({ phone: true }).d;
    for (let i = 0; i < 12; i++) expect(phone.interact("background-click", 1000 + i * 100)).toEqual([]);
  });

  it("does not count a hidden tab's gap as quiet time", () => {
    const { d } = director({ tipsShown: 3 });
    d.tick(1000);
    expect(d.tick(300_000)).toEqual([]);
    expect(d.tick(301_000)).toEqual([]);
  });

  it("never naps while an answer streams", () => {
    const { d } = director({ tipsShown: 3 });
    d.cue({ type: "ask:submit" }, 500);
    expect(at(run(d, 1000, 120_000), "play", "nap")).toEqual([]);
  });
});
```

Check of the numbers: the tip "t1" has 2 characters, so it shows for 2,590 ms. In the typing test, typing at 19 s resets quiet time and holds it until 21 s, so the tip lands at 21 + 19 = 40 s (quiet reaches 20 s on the tick at 40 s, the first tick after 21 s adds one second).

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/director-quiet.test.ts`
Expected: FAIL, the tip and nap tests receive `[]` from `tick` (for example "expected [] to deeply equal [ { t: 15000, ... } ]").

- [ ] **Step 3: Replace `tick` and the background-click branch**

In `site/src/ottie/director.ts`, replace the line `if (kind === "background-click") return []; // Task 10` with:

```ts
      if (kind === "background-click") {
        clicks = clicks.filter((t) => now - t < CLICK_WINDOW_MS);
        clicks.push(now);
        if (env.phone || asleep || streaming || clicks.length < CLICK_BURST) return [];
        clicks = [];
        asleep = true;
        napPrefetched = true;
        return [...hush(false), prefetch("nap", "wake"), play("nap")];
      }
```

and replace the `tick(_now) { return []; // Task 10 }` method with:

```ts
    tick(now) {
      if (still) return [];
      const dt = lastTick === null ? 0 : Math.min(Math.max(now - lastTick, 0), MAX_TICK_MS);
      lastTick = now;
      if (asleep) return [];
      if (streaming || bubbleUp || now < typingUntil) { quietMs = 0; return []; }
      quietMs += dt;
      if (env.phone) return [];
      const out: Command[] = [];
      const tipsLeft = tipsShown < MAX_TIPS && !tipThisStretch;
      if (tipsLeft && !talkPrefetched && quietMs >= TALK_PREFETCH_MS) {
        talkPrefetched = true;
        out.push(prefetch("talk"));
      }
      if (tipsLeft && quietMs >= TIP_AFTER_MS && canSpeak(now)) {
        const text = pickLine(lines.tips[env.context], rng, usedTips);
        if (text) {
          tipThisStretch = true;
          tipsShown++;
          talking = true;
          out.push(play("talk"), say(text, now, true));
          return out;
        }
      }
      if (!napPrefetched && quietMs >= NAP_PREFETCH_MS) {
        napPrefetched = true;
        out.push(prefetch("nap", "wake"));
      }
      if (quietMs >= NAP_AFTER_MS) {
        asleep = true;
        out.push(play("nap"));
      }
      return out;
    },
```

Delete the "Task 10" note under the director code if one was left in a comment.

- [ ] **Step 4: Run both director suites**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/director.test.ts tests/unit/ottie/director-quiet.test.ts`
Expected: PASS, 17 and 12 tests.

- [ ] **Step 5: Run the whole unit suite and the type check**

Run: `pnpm --dir site test && pnpm --dir site check`
Expected: all unit tests pass; `astro check` reports 0 errors.

- [ ] **Step 6: Commit**

```bash
git add site/src/ottie/director.ts site/tests/unit/ottie/director-quiet.test.ts
git commit -m "feat(ottie): add tips, naps and waking to the director"
```

### Task 11: Several Otties on one page: routing and the active host

**Files:**
- Create: `site/src/ottie/hosts.ts`
- Test: `site/tests/unit/ottie/hosts.test.ts`

**Interfaces:**
- Consumes: `OttieCueType` (Task 1), `PageContext` (Task 6), `Visit` (Task 8), `Interaction` (Task 9).
- Produces: `GREETING_CONTEXTS`, `greetsIn(context: PageContext): boolean`, `marksVisit(contexts: PageContext[]): boolean`, `cueTargets(type: OttieCueType, contexts: PageContext[]): number[]`, `interactionTargets(kind: Interaction, count: number, active: number | null, poked: number | null): number[]`, `hostVisit(index: number, visit: Visit): Visit`, `pickActive(ratios: number[], current: number | null): number | null`.

The contract's multi-host rules (Din, 2026-10-21, M4 decision 4) as pure functions, so the page controller in Task 12 only wires them up:
- `ask:*` cues reach `home` and `project` hosts; `letter:*` cues reach `contact` hosts.
- A poke goes to the Ottie that was clicked; a background click to the active host; pointer, key and scroll activity to every host (it resets their quiet timers and wakes them).
- The page's first host gets the real visit; every other host gets `session`, so only the first host can greet. Only `home`, `project` and `devlog` hosts greet (`greetsIn`); the letter Ottie and the 404 Ottie never do.
- A page marks the visit (`markVisit`) only if it has a greeting host (`marksVisit`), so landing on `/contact` or a 404 first leaves the visit unmarked and the first greeting page still gets the full first-visit greeting (Din, 2026-10-21, open question 8).
- The active host is the one with the largest visible share (IntersectionObserver ratio). Ties keep the current host, so two fully visible Otties do not flicker; nothing visible means no active host.

- [ ] **Step 1: Write the failing test**

```ts
// site/tests/unit/ottie/hosts.test.ts
import { describe, expect, it } from "vitest";
import { cueTargets, greetsIn, hostVisit, interactionTargets, marksVisit, pickActive } from "../../../src/ottie/hosts";
import { markVisit, safe, visitKind, type StorageLike } from "../../../src/ottie/prefs";

describe("cue routing", () => {
  it("sends ask cues to home and project hosts and letter cues to contact hosts", () => {
    expect(cueTargets("ask:submit", ["home", "contact"])).toEqual([0]);
    expect(cueTargets("letter:open", ["home", "contact"])).toEqual([1]);
    expect(cueTargets("ask:answer", ["project"])).toEqual([0]);
    expect(cueTargets("ask:focus", ["contact"])).toEqual([]);
    expect(cueTargets("letter:sent", ["404"])).toEqual([]);
  });
});

describe("interaction routing", () => {
  it("pokes the clicked Ottie, counts background clicks on the active one, tells everyone about activity", () => {
    expect(interactionTargets("poke", 2, 0, 1)).toEqual([1]);
    expect(interactionTargets("background-click", 2, 1, null)).toEqual([1]);
    expect(interactionTargets("background-click", 2, null, null)).toEqual([]);
    expect(interactionTargets("pointer", 2, 0, null)).toEqual([0, 1]);
    expect(interactionTargets("scroll", 1, null, null)).toEqual([0]);
  });
});

describe("greeting and visits", () => {
  it("greets only on home, project and devlog Otties", () => {
    expect(["home", "project", "devlog"].every((c) => greetsIn(c as never))).toBe(true);
    expect(greetsIn("contact")).toBe(false);
    expect(greetsIn("404")).toBe(false);
  });

  it("marks the visit only on pages with a greeting Ottie", () => {
    expect(marksVisit(["home", "contact"])).toBe(true);
    expect(marksVisit(["project"])).toBe(true);
    expect(marksVisit(["contact"])).toBe(false);
    expect(marksVisit(["404"])).toBe(false);
    expect(marksVisit([])).toBe(false);
  });

  it("keeps a first visit first after landing on /contact", () => {
    const mem = (): StorageLike => {
      const m = new Map<string, string>();
      return { getItem: (k) => m.get(k) ?? null, setItem: (k, v) => void m.set(k, v), removeItem: (k) => void m.delete(k) };
    };
    const ls = safe(() => mem()), ss = safe(() => mem());
    const visitPage = (contexts: Parameters<typeof marksVisit>[0]) => {
      const v = visitKind(ls, ss);
      if (marksVisit(contexts)) markVisit(ls, ss);
      return v;
    };
    expect(visitPage(["contact"])).toBe("first");
    expect(visitPage(["404"])).toBe("first");
    expect(visitPage(["home", "contact"])).toBe("first");
    expect(visitPage(["home", "contact"])).toBe("session");
  });
});

describe("hosts", () => {
  it("lets only the first host see the real visit", () => {
    expect(hostVisit(0, "first")).toBe("first");
    expect(hostVisit(1, "first")).toBe("session");
    expect(hostVisit(1, "returning")).toBe("session");
  });

  it("animates the host most in view, keeps it on ties, and none when nothing shows", () => {
    expect(pickActive([1, 0], null)).toBe(0);
    expect(pickActive([0.5, 0.75], 0)).toBe(1);
    expect(pickActive([1, 1], 1)).toBe(1);
    expect(pickActive([1, 1], null)).toBe(0);
    expect(pickActive([0, 0.25], 0)).toBe(1);
    expect(pickActive([0, 0], 1)).toBeNull();
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/hosts.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/hosts".

- [ ] **Step 3: Write the implementation**

`hosts.ts` imports only types from `director.ts`, so `director.ts` can import `greetsIn` from it without a runtime cycle.

```ts
// site/src/ottie/hosts.ts
// Rules for pages with more than one Ottie (home: the hero and the letter).
import type { Interaction } from "./director";
import type { OttieCueType } from "./events";
import type { PageContext } from "./lines";
import type { Visit } from "./prefs";

const ASK_HOSTS: readonly PageContext[] = ["home", "project"];
const LETTER_HOSTS: readonly PageContext[] = ["contact"];
export const GREETING_CONTEXTS: readonly PageContext[] = ["home", "project", "devlog"];

// The letter Ottie and the 404 Ottie never greet.
export const greetsIn = (context: PageContext): boolean => GREETING_CONTEXTS.includes(context);

// Only a page with a greeting Ottie marks the visit, so the first greeting page
// still gets the full first-visit greeting (Din, 2026-10-21).
export const marksVisit = (contexts: PageContext[]): boolean => contexts.some(greetsIn);

export function cueTargets(type: OttieCueType, contexts: PageContext[]): number[] {
  const wanted = type.startsWith("ask:") ? ASK_HOSTS : LETTER_HOSTS;
  return contexts.flatMap((c, i) => (wanted.includes(c) ? [i] : []));
}

export function interactionTargets(kind: Interaction, count: number, active: number | null, poked: number | null): number[] {
  if (kind === "poke") return poked === null ? [] : [poked];
  if (kind === "background-click") return active === null ? [] : [active];
  return Array.from({ length: count }, (_, i) => i);
}

export const hostVisit = (index: number, visit: Visit): Visit => (index === 0 ? visit : "session");

export function pickActive(ratios: number[], current: number | null): number | null {
  let best: number | null = null;
  ratios.forEach((r, i) => { if (r > 0 && (best === null || r > ratios[best])) best = i; });
  if (best === null) return null;
  if (current !== null && ratios[current] > 0 && ratios[current] >= ratios[best]) return current;
  return best;
}
```

- [ ] **Step 4: Run it to verify it passes**

Run: `pnpm --dir site exec vitest run tests/unit/ottie/hosts.test.ts`
Expected: PASS, 7 tests.

- [ ] **Step 5: Commit**

```bash
git add site/src/ottie/hosts.ts site/tests/unit/ottie/hosts.test.ts
git commit -m "feat(ottie): route cues between several Otties and pick the one that animates"
```

### Task 12: The browser shell: source, renderer, actors, player and boot

**Files:**
- Create: `site/src/ottie/source.ts`, `site/src/ottie/renderer.ts`, `site/src/ottie/actor.ts`, `site/src/ottie/player.ts`, `site/src/ottie/boot.ts`
- Test: covered end to end in Task 14 (these modules only wire DOM APIs to the tested logic).

**Interfaces:**
- Consumes: everything from Tasks 1 to 11.
- Produces: `browserSource: SheetSource<Sheet>` where `type Sheet = CanvasImageSource & Decoded`; `createRenderer(canvas, m, g, mirrorPoint): { resize(): void; paint(ops: DrawOp[], get: (n: StateName) => Sheet | undefined): void; poses(from, to, t, get): void }`; `interface Shared { loader: Loader<Sheet>; geometry: Geometry; mode: Mode; phone: boolean; ss: SafeStorage; now: () => number; mirrorPoint: boolean }`; `interface Actor { readonly context: PageContext; readonly host: HTMLElement; readonly started: boolean; start(): void; setActive(on: boolean): void; cue(c: OttieCueDetail): void; interact(kind: Interaction): void; tick(): void; dispose(): void }`; `createActor(host, visit, shared): Actor`; `interface PlayerOptions { hosts: HTMLElement[]; quiet: boolean; forceMode?: Mode; mirrorPoint(host: HTMLElement): boolean }`; `startOttie(opts): () => void` (returns a stop function); `whenIdle(cb)`.

DOM contract (rendered by Task 13): each `[data-ottie-host]` (with `data-ottie-context`, and `data-ottie-greets` on greeting contexts) holds `[data-ottie-still]`, `[data-ottie-canvas]` and `[data-ottie-bubble]`; the page has at most one `[data-ottie-quiet]` button. Each host gets `is-live` while its canvas shows Ottie, `data-ottie-mode`, and `data-ottie-running="true|false"` (true only for the active host); the e2e tests read these.

What the shell does:
1. **Page controller (`player.ts`)**: reads Quiet Ottie and the device hints once, picks the mode, reads the visit and marks it only if the page has a greeting Ottie (`marksVisit`), builds one loader shared by every host, and one actor per host (`hostVisit` gives the first host the real visit). In still mode it shows every still, clears `data-ottie-enter` and stops.
2. After `load` and an idle callback, the first host's actor starts (runs `director.start()`; in full mode it then asks for idle, so the request order is run-in, wave, idle on a first visit and idle, wave otherwise). Any other host starts the first time it becomes the active host, so the letter Ottie's sheets are only requested when the visitor gets there.
3. The active host comes from `pickActive` over IntersectionObserver ratios; with the tab hidden there is none. Only the active actor runs its frame loop and its 1 s director tick; the others show their still. Clicking an Ottie makes it the active host.
4. Cues go through `cueTargets`, interactions through `interactionTargets` (pointer, key and scroll listeners are passive and on capture).
5. **Actor (`actor.ts`)**, one per host: runs its director's commands. `prefetch` goes to the shared loader; `play` waits for the sheets it needs (plus the current state's `exit_via`), then calls `timeline.play` (a newer play cancels an older one still waiting); `say` places the bubble with `placeBubble` and hides it after `ms`; `hush` hides it.
6. Each animation frame (full mode, active host only): nothing happens until the current state's sheet is decoded (the still stays up and the timeline does not move); then the timeline advances and the canvas repaints only when the picture changed. The first painted frame and the `is-live` class change happen in the same frame, so the still hands over with no flash.
7. Reduced mode: plays `reducedPlan` steps with a 400 ms crossfade (`--motion-slow`), the still standing in for idle.
8. On a first visit, if the greeting host's run-in has not started within 4 s, it drops run-in, shows the still and plays the wave.
9. Emits `ottie:state` with `{ state, context }` on every state entered (and every reduced-motion pose).

- [ ] **Step 1: Write the sheet source**

```ts
// site/src/ottie/source.ts
import type { Decoded, SheetSource } from "./loader";

export type Sheet = CanvasImageSource & Decoded;

export const browserSource: SheetSource<Sheet> = {
  async fetchBlob(url) {
    const res = await fetch(url, { priority: "low" } as RequestInit);
    if (!res.ok) throw new Error(`ottie sheet ${res.status} ${url}`);
    return res.blob();
  },
  async decode(blob, url) {
    // createImageBitmap decodes off the main thread. The fallback reuses the
    // cached URL (no blob: URLs, so the CSP needs nothing extra).
    if (typeof createImageBitmap === "function") {
      try { return await createImageBitmap(blob); } catch { /* fall through */ }
    }
    const img = new Image();
    img.src = url;
    await img.decode();
    return img;
  },
};
```

- [ ] **Step 2: Write the renderer**

```ts
// site/src/ottie/renderer.ts
import { drawOps, type DrawOp } from "./frames";
import type { Geometry, Manifest, StateName } from "./manifest";
import type { Sheet } from "./source";

type Get = (name: StateName) => Sheet | undefined;
export interface Pose { state: StateName; drawing: number }

export function createRenderer(canvas: HTMLCanvasElement, m: Manifest, g: Geometry, mirrorPoint: boolean) {
  const ctx = canvas.getContext("2d")!;
  let k = 1;

  // Sheets are drawn at 2x display size, so a device pixel ratio above 2 gains nothing.
  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
    const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    k = w / g.stageSize[0];
  }

  function paint(ops: DrawOp[], get: Get) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    for (const op of ops) {
      const img = get(op.state);
      if (!img) continue;
      ctx.globalAlpha = op.alpha;
      if (op.mirror) ctx.setTransform(-k, 0, 0, k, 2 * g.stage.l * k, 0);
      else ctx.setTransform(k, 0, 0, k, 0, 0);
      ctx.drawImage(img, op.sx, op.sy, op.sw, op.sh, op.dx, op.dy, op.sw, op.sh);
    }
    ctx.globalAlpha = 1;
  }

  function poses(from: Pose | null, to: Pose | null, t: number, get: Get) {
    const one = (p: Pose, alpha: number) =>
      drawOps(m, g, { state: p.state, drawing: p.drawing, fade: null }, { mirrorPoint }).map((o) => ({ ...o, alpha }));
    paint([...(from ? one(from, 1 - t) : []), ...(to ? one(to, t) : [])], get);
  }

  resize();
  return { resize, paint, poses };
}
```

- [ ] **Step 3: Write the actor (one per Ottie on the page)**

```ts
// site/src/ottie/actor.ts
import { placeBubble, type Rect } from "./bubble";
import { createDirector, type Command, type Interaction } from "./director";
import { OTTIE_STATE, type OttieCueDetail } from "./events";
import { drawOps, reducedPlan, type PoseStep } from "./frames";
import { LINES, type PageContext } from "./lines";
import type { Loader } from "./loader";
import type { Geometry, StateName } from "./manifest";
import { MANIFEST } from "./manifest-data";
import { recordTip, tipsShown, type Mode, type SafeStorage, type Visit } from "./prefs";
import { createRenderer, type Pose } from "./renderer";
import type { Sheet } from "./source";
import { createTimeline } from "./timeline";

const FIRST_ENTER_TIMEOUT_MS = 4000;
const POSE_FADE_MS = 400;

export interface Shared {
  loader: Loader<Sheet>; geometry: Geometry; mode: Mode; phone: boolean; ss: SafeStorage; now: () => number; mirrorPoint: boolean;
}
export interface Actor {
  readonly context: PageContext;
  readonly host: HTMLElement;
  readonly started: boolean;
  start(): void;
  setActive(on: boolean): void;
  cue(c: OttieCueDetail): void;
  interact(kind: Interaction): void;
  tick(): void;
  dispose(): void;
}

const toRect = (r: DOMRect): Rect => ({ x: r.x, y: r.y, w: r.width, h: r.height });

export function createActor(host: HTMLElement, visit: Visit, shared: Shared): Actor {
  const { loader, mode, now } = shared;
  const root = document.documentElement;
  const context = (host.dataset.ottieContext ?? "home") as PageContext;
  const canvas = host.querySelector<HTMLCanvasElement>("[data-ottie-canvas]")!;
  const bubble = host.querySelector<HTMLElement>("[data-ottie-bubble]")!;
  const renderer = createRenderer(canvas, MANIFEST, shared.geometry, shared.mirrorPoint);
  const timeline = createTimeline(MANIFEST, "idle");
  const director = createDirector({ mode, phone: shared.phone, context, visit, tipsShown: tipsShown(shared.ss) }, LINES);
  let started = false, active = false, disposed = false, ranIn = false, dirty = true, last = 0;
  let playToken = 0, bubbleTimer = 0, poseTimer = 0, rafId = 0, fadeId = 0, enterTimer = 0;
  let pose: Pose | null = null;
  host.dataset.ottieRunning = "false";

  const setLive = (live: boolean) => {
    host.classList.toggle("is-live", live);
    if (live && host.dataset.ottieGreets !== undefined) delete root.dataset.ottieEnter;
  };
  const announce = (state: string) => window.dispatchEvent(new CustomEvent(OTTIE_STATE, { detail: { state, context } }));

  timeline.onEnter((state) => {
    if (state === "run-in") ranIn = true;
    announce(state);
    exec(director.entered(state, now()));
  });

  function exec(cmds: Command[]) {
    for (const c of cmds) {
      if (c.kind === "prefetch") loader.prefetch(c.states);
      else if (c.kind === "play") (mode === "reduced" ? playPoses : playStates)(c.states);
      else if (c.kind === "say") say(c.text, c.ms, c.tip);
      else hideBubble();
    }
  }

  function playStates(states: StateName[]) {
    const token = ++playToken;
    const via = MANIFEST.states[timeline.current].exit_via;
    const needed = [...new Set<StateName>([...(via ? [via] : []), ...states])];
    const ready = Promise.all(needed.map((n) => loader.ensure(n)));
    void loader.ensure("idle").catch(() => {}); // after the opener, so first visits load run-in, wave, idle
    ready.then(
      () => { if (token === playToken && !disposed) { timeline.play(...states); dirty = true; } },
      () => {
        if (token !== playToken || disposed || !states.includes("run-in")) return;
        delete root.dataset.ottieEnter;
        playStates(states.filter((n) => n !== "run-in"));
      },
    );
  }

  function playPoses(states: StateName[]) {
    const token = ++playToken;
    clearTimeout(poseTimer);
    const steps = reducedPlan(MANIFEST, states);
    const needed = steps.flatMap((s) => (s.state === "still" ? [] : [s.state]));
    Promise.all(needed.map((n) => loader.ensure(n))).then(
      () => { if (token === playToken && !disposed) stepPoses(steps, 0, token); },
      () => {},
    );
  }

  function stepPoses(steps: PoseStep[], i: number, token: number) {
    if (token !== playToken || disposed || i >= steps.length) return;
    const step = steps[i];
    const next: Pose | null = step.state === "still" ? null : { state: step.state, drawing: step.drawing };
    if (active) fadePose(pose, next);
    pose = next;
    announce(step.state === "still" ? "idle" : step.state);
    if (step.state !== "still") exec(director.entered(step.state, now()));
    if (Number.isFinite(step.holdMs)) poseTimer = window.setTimeout(() => stepPoses(steps, i + 1, token), step.holdMs);
  }

  // Pose to pose fades on the canvas; to and from the still, CSS fades the two layers.
  function fadePose(from: Pose | null, to: Pose | null) {
    cancelAnimationFrame(fadeId);
    if (!to) { setLive(false); return; }
    if (!from) { renderer.poses(null, to, 1, loader.get); setLive(true); return; }
    const begin = now();
    const step = () => {
      const t = Math.min(1, (now() - begin) / POSE_FADE_MS);
      renderer.poses(from, to, t, loader.get);
      if (t < 1) fadeId = requestAnimationFrame(step);
    };
    fadeId = requestAnimationFrame(step);
  }

  function say(text: string, ms: number, tip: boolean) {
    hideBubble();
    if (!active) { exec(director.bubbleDone(now())); return; } // only the Ottie in view speaks
    bubble.textContent = text;
    bubble.hidden = false;
    const hostRect = host.getBoundingClientRect();
    const avoid = [...document.querySelectorAll("[data-ottie-avoid]")].map((el) => toRect(el.getBoundingClientRect()));
    const spot = placeBubble(toRect(hostRect), { w: bubble.offsetWidth, h: bubble.offsetHeight }, avoid,
      { w: document.documentElement.clientWidth, h: window.innerHeight });
    if (!spot) { bubble.hidden = true; exec(director.bubbleDone(now())); return; }
    bubble.style.left = `${spot.rect.x - hostRect.x}px`; // CSSOM writes are allowed by the CSP
    bubble.style.top = `${spot.rect.y - hostRect.y}px`;
    bubble.dataset.side = spot.side;
    requestAnimationFrame(() => bubble.classList.add("is-shown"));
    if (tip) recordTip(shared.ss);
    bubbleTimer = window.setTimeout(() => { hideBubble(); exec(director.bubbleDone(now())); }, ms);
  }

  function hideBubble() {
    clearTimeout(bubbleTimer);
    bubble.classList.remove("is-shown");
    bubble.hidden = true;
  }

  function frame(t: number) {
    rafId = 0;
    if (!active || disposed) return;
    if (!loader.get(timeline.current)) {
      setLive(false); // the still covers until this state's sheet is decoded
      if (started && !loader.failed(timeline.current)) void loader.ensure(timeline.current).catch(() => {}); // after an eviction
      last = 0;
      rafId = requestAnimationFrame(frame);
      return;
    }
    const dt = last ? (t - last) / 1000 : 0;
    last = t;
    if (timeline.advance(dt)) dirty = true;
    if (dirty) {
      const snap = timeline.snapshot();
      renderer.paint(drawOps(MANIFEST, shared.geometry, snap, { mirrorPoint: shared.mirrorPoint }), loader.get);
      loader.touch(snap.state);
      if (snap.fade) loader.touch(snap.fade.state);
      setLive(true);
      dirty = false;
    }
    rafId = requestAnimationFrame(frame);
  }

  const ro = new ResizeObserver(() => { renderer.resize(); dirty = true; if (active && pose) renderer.poses(null, pose, 1, loader.get); });
  ro.observe(canvas);

  return {
    context,
    host,
    get started() { return started; },
    start() {
      if (started || disposed) return;
      started = true;
      exec(director.start(now()));
      if (mode === "full") void loader.ensure("idle").catch(() => {});
      if (visit === "first" && mode === "full" && host.dataset.ottieGreets !== undefined && root.dataset.ottieEnter !== undefined) {
        enterTimer = window.setTimeout(() => {
          if (ranIn || disposed) return;
          delete root.dataset.ottieEnter;
          playStates(["wave"]);
        }, FIRST_ENTER_TIMEOUT_MS);
      }
    },
    setActive(on) {
      if (on === active || disposed) return;
      active = on;
      host.dataset.ottieRunning = String(on);
      if (on) {
        last = 0;
        dirty = true;
        if (mode === "full") rafId = requestAnimationFrame(frame);
        else if (pose) { renderer.poses(null, pose, 1, loader.get); setLive(true); }
      } else {
        cancelAnimationFrame(rafId);
        cancelAnimationFrame(fadeId);
        setLive(false);
        if (!bubble.hidden) { hideBubble(); exec(director.bubbleDone(now())); }
      }
    },
    cue: (c) => exec(director.cue(c, now())),
    interact: (kind) => exec(director.interact(kind, now())),
    tick: () => exec(director.tick(now())),
    dispose() {
      disposed = true;
      playToken++;
      cancelAnimationFrame(rafId);
      cancelAnimationFrame(fadeId);
      clearTimeout(poseTimer);
      clearTimeout(enterTimer);
      hideBubble();
      ro.disconnect();
      setLive(false);
      host.dataset.ottieRunning = "false";
    },
  };
}
```

- [ ] **Step 4: Write the page controller**

```ts
// site/src/ottie/player.ts
// One controller per page: shared loader and preferences, routing between Otties,
// and which Ottie is active (the only one that animates).
import { createActor, type Actor } from "./actor";
import { sheetUrl, sheetVersion } from "./assets";
import type { Interaction } from "./director";
import { isCueType, onOttieCue } from "./events";
import { cueTargets, hostVisit, interactionTargets, marksVisit, pickActive } from "./hosts";
import type { PageContext } from "./lines";
import { createLoader } from "./loader";
import { geometry } from "./manifest";
import { MANIFEST } from "./manifest-data";
import { deviceHints, localStore, markVisit, modeFor, sessionStore, visitKind, type Mode } from "./prefs";
import { browserSource, type Sheet } from "./source";

const INTERACTIVE = "a, button, input, textarea, select, label, summary, [role='button'], [contenteditable]";

export interface PlayerOptions { hosts: HTMLElement[]; quiet: boolean; forceMode?: Mode; mirrorPoint(host: HTMLElement): boolean }

export function whenIdle(cb: () => void): void {
  const go = () => {
    if ("requestIdleCallback" in window) requestIdleCallback(() => cb(), { timeout: 2000 });
    else setTimeout(cb, 200);
  };
  if (document.readyState === "complete") go();
  else addEventListener("load", go, { once: true });
}

export function startOttie(opts: PlayerOptions): () => void {
  const { hosts } = opts;
  const root = document.documentElement;
  const ls = localStore(), ss = sessionStore();
  const hints = deviceHints();
  const mode = opts.forceMode ?? modeFor(opts.quiet, hints);
  const contexts = hosts.map((h) => (h.dataset.ottieContext ?? "home") as PageContext);
  const visit = visitKind(ls, ss);
  if (marksVisit(contexts)) markVisit(ls, ss); // /contact or a 404 alone leaves the visit unmarked
  for (const h of hosts) h.dataset.ottieMode = mode;
  if (visit !== "first" || mode !== "full") delete root.dataset.ottieEnter;
  if (mode === "still") {
    for (const h of hosts) { h.classList.remove("is-live"); h.dataset.ottieRunning = "false"; }
    return () => {};
  }

  performance.mark("ottie:boot");
  const version = sheetVersion(MANIFEST);
  const loader = createLoader<Sheet>((n) => sheetUrl(MANIFEST, n, version), browserSource);
  const base = { loader, geometry: geometry(MANIFEST), mode, phone: hints.phone, ss, now: () => performance.now() };
  const actors: Actor[] = hosts.map((host, i) => createActor(host, hostVisit(i, visit), { ...base, mirrorPoint: opts.mirrorPoint(host) }));
  const ratios = actors.map(() => 0);
  let active: number | null = null, tickTimer = 0, booted = false;

  function activate(next: number | null) {
    if (next === active) return;
    active = next;
    actors.forEach((a, i) => a.setActive(i === active));
    clearInterval(tickTimer);
    if (active === null) return;
    const a = actors[active];
    if (booted) a.start();
    tickTimer = window.setInterval(() => a.tick(), 1000);
  }
  const update = () => activate(document.hidden ? null : pickActive(ratios, active));

  const io = new IntersectionObserver((entries) => {
    for (const e of entries) ratios[hosts.indexOf(e.target as HTMLElement)] = e.isIntersecting ? e.intersectionRatio : 0;
    update();
  }, { threshold: [0, 0.25, 0.5, 0.75, 1] });
  for (const h of hosts) io.observe(h);
  document.addEventListener("visibilitychange", update);

  const send = (kind: Interaction, poked: number | null) => {
    for (const i of interactionTargets(kind, actors.length, active, poked)) actors[i].interact(kind);
  };
  const onPointer = (e: PointerEvent) => {
    const target = e.target instanceof Element ? e.target : null;
    const poked = target ? hosts.findIndex((h) => h.contains(target)) : -1;
    if (poked >= 0) { activate(poked); send("poke", poked); return; }
    send(target?.closest(INTERACTIVE) ? "pointer" : "background-click", null);
  };
  const onKey = () => send("key", null);
  let lastScroll = 0;
  const onScroll = () => {
    const t = performance.now();
    if (t - lastScroll < 1000) return;
    lastScroll = t;
    send("scroll", null);
  };
  document.addEventListener("pointerdown", onPointer, { capture: true, passive: true });
  document.addEventListener("keydown", onKey, { capture: true });
  addEventListener("scroll", onScroll, { passive: true });
  const offCue = onOttieCue((cue) => {
    if (!isCueType(cue.type)) return;
    for (const i of cueTargets(cue.type, contexts)) actors[i].cue(cue);
  });

  whenIdle(() => {
    booted = true;
    actors[0]?.start();
    if (active !== null) actors[active].start();
  });

  return () => {
    activate(null);
    io.disconnect();
    document.removeEventListener("visibilitychange", update);
    document.removeEventListener("pointerdown", onPointer, { capture: true });
    document.removeEventListener("keydown", onKey, { capture: true });
    removeEventListener("scroll", onScroll);
    offCue();
    for (const a of actors) a.dispose();
    loader.dispose();
  };
}
```

- [ ] **Step 5: Write the boot entry**

```ts
// site/src/ottie/boot.ts
// Bundled once per page by the <script> in components/Ottie.astro, however many Otties the page has.
import { startOttie } from "./player";
import { MIRROR_POINT_APPROVED } from "./poses";
import { localStore, readQuiet, writeQuiet, type Mode } from "./prefs";

const MODES: Mode[] = ["full", "reduced", "still"];
const hosts = [...document.querySelectorAll<HTMLElement>("[data-ottie-host]")];

if (hosts.length) {
  const ls = localStore();
  const toggle = document.querySelector<HTMLButtonElement>("[data-ottie-quiet]");
  const lab = hosts.some((h) => h.dataset.ottieLab !== undefined);
  const asked = lab ? new URLSearchParams(location.search).get("ottie-mode") : null;
  const forceMode = MODES.find((m) => m === asked);
  let quiet = readQuiet(ls);
  const start = () => startOttie({
    hosts,
    quiet,
    forceMode,
    mirrorPoint: (h) => MIRROR_POINT_APPROVED && h.dataset.ottiePoint === "left",
  });
  let stop = start();
  if (toggle) {
    toggle.hidden = false;
    toggle.setAttribute("aria-pressed", String(quiet));
    toggle.addEventListener("click", () => {
      quiet = !quiet;
      writeQuiet(ls, quiet);
      toggle.setAttribute("aria-pressed", String(quiet));
      stop();
      stop = start();
    });
  }
}
```

- [ ] **Step 6: Type check**

Run: `pnpm --dir site check`
Expected: 0 errors. (If `priority` is missing from `RequestInit` in TypeScript 6's DOM types, the cast in `source.ts` covers it; remove the cast if the type already has it.)

- [ ] **Step 7: Commit**

```bash
git add site/src/ottie/source.ts site/src/ottie/renderer.ts site/src/ottie/actor.ts site/src/ottie/player.ts site/src/ottie/boot.ts
git commit -m "feat(ottie): add the canvas player for one or more Otties on a page"
```

### Task 13: The Ottie component, the inline still and the lab page

**Files:**
- Create: `site/src/ottie/still.ts`, `site/src/ottie/layout.ts`, `site/src/components/Ottie.astro`, `site/src/lib/lab.ts`, `site/src/pages/lab/ottie/[...slug].astro`
- Modify: `site/astro.config.mjs` (add `__DINS_LABS_OVERRIDE__` to `vite.define`), `site/src/env.d.ts` (declare it)
- Test: `site/tests/unit/ottie/layout.test.ts`, `site/tests/unit/lab.test.ts`; the component is checked end to end in Task 14 and by Din.

**Interfaces:**
- Consumes: `geometry`, `MANIFEST` (Task 2), `PageContext` (Task 6), `KEYS` (Task 8, mirrored in the inline script), `boot.ts` (Task 12); from M0: `type Deploy` (`site/src/lib/deploy.ts`), `DEPLOY` (`site/src/lib/deploy-env.ts`), `BaseLayout.astro`.
- Produces: `<Ottie context={PageContext} pointToward?: "left" | "right" toggle?: boolean lab?: boolean class?: string />` (`toggle={false}` on a page's second Ottie); `STILL = { width: 720, height: 880, scale: 2, ground: [371.94, 823.18] }`; `ottieLayoutCss(m, still): string`; `labEnabled(deploy: Deploy, override?: string): boolean`; lab routes `/lab/ottie` (hero Ottie plus the letter Ottie in `#contact`, like home), `/lab/ottie/project`, `/lab/ottie/contact`, `/lab/ottie/devlog`, `/lab/ottie/404`, `/lab/ottie/blank` (no Ottie, the baseline for Task 15's JavaScript cost).

Layout numbers at size 1 (desktop), from the geometry and the still measurement: the reserved box is 158.5 x 202.5 CSS px (the body box at `display_scale` 0.5, about 28 percent of a 720 px hero); the canvas covers the full stage, 408.4 x 245.5 CSS px, starting at the box's left edge and 43 px above it (run-in travels in from the right, jumps rise above); the still is 180 x 220 CSS px, offset by about (-6.5, -18.8) px so its ground point meets the box's. Phones (up to 639 px wide) use `--ottie-size: 0.75`.

- [ ] **Step 1: Re-measure the still against idle drawing 0**

Run from the repo root, writing only to a scratch folder outside the repo:

```bash
mkdir -p /tmp/ottie-measure
dwebp -quiet brand/reference/ottie-3d-neutral.webp -pam -o /tmp/ottie-measure/n.pam
dwebp -quiet brand/ottie/dist/idle.webp -pam -o /tmp/ottie-measure/i.pam
python3 -I - /tmp/ottie-measure/n.pam /tmp/ottie-measure/i.pam <<'EOF'
import sys
def bbox(path, w, h):
    data = open(path, "rb").read(); head, _, px = data.partition(b"ENDHDR\n")
    W = int([l for l in head.split(b"\n") if l.startswith(b"WIDTH")][0].split()[1])
    xs, ys = [], []
    for y in range(h):
        for x in range(w):
            if px[(y * W + x) * 4 + 3] > 8: xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)
n = bbox(sys.argv[1], 720, 880); i = bbox(sys.argv[2], 219, 390)
scale = (n[2] - n[0]) / (i[2] - i[0])
print("neutral", n, "idle0", i, "scale", round(scale, 3))
print("ground", round(n[0] + (111.97 - i[0]) * scale, 2), round(n[1] + (371.09 - i[1]) * scale, 2))
EOF
rm -rf /tmp/ottie-measure
```

Expected (measured 2026-10-21): `neutral (166, 89, 572, 849) idle0 (9, 4, 212, 384) scale 2.0`, ground about `371.94 823.18`. If the sheets or the still were re-rendered and the numbers differ, use the new ones in Step 2.

- [ ] **Step 2: Write the failing layout test**

The box sizes are build-time numbers, but M5's CSP drops `style="…"` attributes, so they reach the page as one small `<style>` element (Astro's `security.csp` hashes it) instead of a `style` attribute.

```ts
// site/tests/unit/ottie/layout.test.ts
import { describe, expect, it } from "vitest";
import { ottieLayoutCss } from "../../../src/ottie/layout";
import { MANIFEST } from "../../../src/ottie/manifest-data";
import { STILL } from "../../../src/ottie/still";

describe("Ottie layout CSS", () => {
  const css = ottieLayoutCss(MANIFEST, STILL);
  it("sizes the box, the canvas and the still from the manifest", () => {
    expect(css).toMatch(/^\.ottie\{[^{}]+\}$/);
    expect(css).toContain("--ottie-w:158.50px");
    expect(css).toContain("--ottie-h:202.50px");
    expect(css).toContain("--ottie-stage-x:0.00px");
    expect(css).toContain("--ottie-stage-y:-42.97px");
    expect(css).toContain("--ottie-still-w:180.00px");
    expect(css).toContain("--ottie-still-x:-6.50px");
    expect(css).toContain("--ottie-still-y:-18.75px");
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/ottie/layout.test.ts`
Expected: FAIL, "Failed to resolve import ../../../src/ottie/still".

- [ ] **Step 3: Write the still constants and the layout CSS**

```ts
// site/src/ottie/still.ts
// brand/reference/ottie-3d-neutral.webp is idle drawing 0 rendered at 2x the
// sheet's frame pixels. Measured 2026-10-21 from the alpha bounding boxes
// (neutral 166,89 to 572,849; idle drawing 0 9,4 to 212,384); re-measure with
// the script in docs/site/plans/M2-ottie.md (Task 13) if either file changes.
export const STILL = { width: 720, height: 880, scale: 2, ground: [371.94, 823.18] } as const;
```

```ts
// site/src/ottie/layout.ts
// Sizes for components/Ottie.astro, rendered into a <style> element at build time
// (the CSP forbids style attributes). All hosts share the same numbers.
import { geometry, type Manifest } from "./manifest";

export interface StillSpec { width: number; height: number; scale: number; ground: readonly [number, number] }

export function ottieLayoutCss(m: Manifest, still: StillSpec): string {
  const g = geometry(m);
  const s = m.display_scale;
  const px = (n: number) => `${(Math.abs(n) < 0.005 ? 0 : n).toFixed(2)}px`;
  const vars: Record<string, string> = {
    "--ottie-w": px(g.bodySize[0] * s),
    "--ottie-h": px(g.bodySize[1] * s),
    "--ottie-stage-w": px(g.stageSize[0] * s),
    "--ottie-stage-h": px(g.stageSize[1] * s),
    "--ottie-stage-x": px((g.body.l - g.stage.l) * s),
    "--ottie-stage-y": px((g.body.t - g.stage.t) * s),
    "--ottie-still-w": px((still.width / still.scale) * s),
    "--ottie-still-x": px((g.body.l - still.ground[0] / still.scale) * s),
    "--ottie-still-y": px((g.body.t - still.ground[1] / still.scale) * s),
  };
  return `.ottie{${Object.entries(vars).map(([k, v]) => `${k}:${v}`).join(";")}}`;
}
```

Run: `pnpm --dir site exec vitest run tests/unit/ottie/layout.test.ts`
Expected: PASS, 1 test.

- [ ] **Step 4: Gate the lab pages on the shared deploy (test first)**

M0 owns the build-time deploy (`site/src/lib/deploy.ts`, `deploy-env.ts` exporting `DEPLOY`, contract "Build-time deploy"). Lab pages are built unless the deploy is `production`; `DINS_LABS=0` or `1` overrides it.

```ts
// site/tests/unit/lab.test.ts
import { describe, expect, it } from "vitest";
import { labEnabled } from "../../src/lib/lab";

describe("lab pages", () => {
  it("are built locally and on previews, never in production", () => {
    expect(labEnabled("local")).toBe(true);
    expect(labEnabled("preview")).toBe(true);
    expect(labEnabled("production")).toBe(false);
  });
  it("can be forced either way with DINS_LABS", () => {
    expect(labEnabled("local", "0")).toBe(false);
    expect(labEnabled("production", "1")).toBe(true);
    expect(labEnabled("preview", "")).toBe(true);
  });
});
```

Run: `pnpm --dir site exec vitest run tests/unit/lab.test.ts`
Expected: FAIL, "Failed to resolve import ../../src/lib/lab".

```ts
// site/src/lib/lab.ts
// Lab pages (/lab/...) are for tests and Din's reviews, never for production.
import type { Deploy } from "./deploy";

export function labEnabled(deploy: Deploy, override = ""): boolean {
  if (override === "0") return false;
  if (override === "1") return true;
  return deploy !== "production";
}
```

In `site/astro.config.mjs`, add the override next to M0's `__DINS_DEPLOY__` define:

```js
vite: {
  define: {
    // ...M0's __DINS_DEPLOY__ stays as it is...
    __DINS_LABS_OVERRIDE__: JSON.stringify(process.env.DINS_LABS ?? ""),
  },
},
```

In `site/src/env.d.ts` add:

```ts
declare const __DINS_LABS_OVERRIDE__: string;
```

Run: `pnpm --dir site exec vitest run tests/unit/lab.test.ts`
Expected: PASS, 2 tests.

- [ ] **Step 5: Write the component**

```astro
---
// site/src/components/Ottie.astro
// Ottie's reserved box with the neutral still (works with JavaScript off),
// the canvas the player draws on, the bubble and (once per page) the Quiet Ottie toggle.
// A page may hold several (home: the hero and the letter); one script runs them all.
import { Image } from "astro:assets";
import neutral from "../../../brand/reference/ottie-3d-neutral.webp";
import { ottieLayoutCss } from "../ottie/layout";
import type { PageContext } from "../ottie/lines";
import { MANIFEST } from "../ottie/manifest-data";
import { STILL } from "../ottie/still";

interface Props { context: PageContext; pointToward?: "left" | "right"; toggle?: boolean; lab?: boolean; class?: string }
const { context, pointToward = "right", toggle = true, lab = false, class: className } = Astro.props;

const layoutCss = ottieLayoutCss(MANIFEST, STILL);
// home, project and devlog hosts may greet; the letter Ottie and the 404 Ottie never do.
const greets = context === "home" || context === "project" || context === "devlog";
---
<style is:inline set:html={layoutCss}></style>
{greets && (
  <script is:inline>
    (() => {
      try {
        const d = document.documentElement, ls = localStorage, ss = sessionStorage, c = navigator.connection;
        if (d.querySelector("[data-ottie-greets]")) return; // only the page's first Ottie greets
        const still = ls.getItem("dins.ottie.quiet") === "1" || (c && c.saveData) || (navigator.deviceMemory && navigator.deviceMemory <= 2);
        const calm = d.dataset.motion === "calm" || matchMedia("(prefers-reduced-motion: reduce)").matches;
        const first = !ls.getItem("dins.ottie.seen") && !ss.getItem("dins.ottie.session");
        if (first && !still && !calm) d.dataset.ottieEnter = "";
      } catch {}
    })();
  </script>
)}
<div
  class:list={["ottie", className]}
  aria-hidden="true"
  data-ottie-host
  data-ottie-context={context}
  data-ottie-point={pointToward}
  data-ottie-greets={greets ? "" : undefined}
  data-ottie-lab={lab ? "" : undefined}
>
  <Image
    src={neutral}
    alt=""
    widths={[270, 360]}
    sizes="(max-width: 639px) 135px, 180px"
    loading={context === "home" ? "eager" : "lazy"}
    decoding="async"
    class="ottie__still"
    data-ottie-still
  />
  <canvas class="ottie__canvas" data-ottie-canvas></canvas>
  <p class="ottie__bubble" data-ottie-bubble hidden></p>
</div>
{toggle && <button type="button" class="ottie-quiet" data-ottie-quiet aria-pressed="false" hidden>Quiet Ottie</button>}

<script>
  import "../ottie/boot";
</script>

<style>
  .ottie {
    --ottie-size: 1;
    position: relative;
    inline-size: calc(var(--ottie-w) * var(--ottie-size));
    block-size: calc(var(--ottie-h) * var(--ottie-size));
    flex: none;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
    user-select: none;
  }
  @media (max-width: 639px) {
    .ottie { --ottie-size: 0.75; }
  }
  .ottie :global(.ottie__still),
  .ottie__canvas {
    position: absolute;
    pointer-events: none;
  }
  .ottie :global(.ottie__still) {
    left: calc(var(--ottie-still-x) * var(--ottie-size));
    top: calc(var(--ottie-still-y) * var(--ottie-size));
    inline-size: calc(var(--ottie-still-w) * var(--ottie-size));
    block-size: auto;
    max-inline-size: none;
  }
  .ottie__canvas {
    left: calc(var(--ottie-stage-x) * var(--ottie-size));
    top: calc(var(--ottie-stage-y) * var(--ottie-size));
    inline-size: calc(var(--ottie-stage-w) * var(--ottie-size));
    block-size: calc(var(--ottie-stage-h) * var(--ottie-size));
    opacity: 0;
  }
  .ottie.is-live .ottie__canvas { opacity: 1; }
  .ottie.is-live :global(.ottie__still) { opacity: 0; }
  .ottie[data-ottie-mode="reduced"] :global(.ottie__still),
  .ottie[data-ottie-mode="reduced"] .ottie__canvas {
    transition: opacity var(--motion-slow) var(--motion-ease);
  }
  /* First visit: the greeting Ottie's still waits for run-in, but never longer than 4 s, even if the script fails. */
  :global(:root[data-ottie-enter]) .ottie[data-ottie-greets]:not(.is-live) :global(.ottie__still) {
    animation: ottie-still-reveal 1ms 4s both;
  }
  @keyframes ottie-still-reveal {
    from { visibility: hidden; }
    to { visibility: visible; }
  }
  .ottie.is-overlay :global(.ottie__still) { opacity: 0.5; visibility: visible; animation: none; }
  .ottie__bubble {
    position: absolute;
    margin: 0;
    inline-size: max-content;
    max-inline-size: 230px;
    padding: 9px 13px;
    border-radius: 14px 14px 4px 14px;
    background: var(--color-ink);
    color: var(--color-paper);
    font: 400 var(--text-small) / 1.4 var(--font-sans);
    text-align: left;
    pointer-events: none;
    opacity: 0;
    transform: scale(0.6);
    transform-origin: 90% 100%;
    transition: transform var(--motion-slow) var(--motion-ease), opacity var(--motion-base) var(--motion-ease);
  }
  .ottie__bubble[data-side="right"] { border-radius: 14px 14px 14px 4px; transform-origin: 10% 100%; }
  .ottie__bubble.is-shown { opacity: 1; transform: none; }
  @media (prefers-reduced-motion: reduce) {
    .ottie__bubble { transform: none; transition: opacity var(--motion-base) var(--motion-ease); }
  }
  :global(:root[data-motion="calm"]) .ottie__bubble { transform: none; }
  .ottie-quiet {
    display: block;
    margin-block-start: 4px;
    padding: 2px 6px;
    border: 0;
    background: none;
    color: var(--color-muted);
    font: 500 var(--text-label) / 1.4 var(--font-mono);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    cursor: pointer;
  }
  .ottie-quiet[aria-pressed="true"] { color: var(--color-accent); }
</style>
```

Notes:
- No `style` attribute anywhere: build-time sizes come from the `<style>` element, runtime positions (the bubble) from JavaScript.
- Token names (`--color-ink`, `--color-paper`, `--color-muted`, `--color-accent`, `--text-small`, `--text-label`, `--font-sans`, `--font-mono`, `--motion-*`) must match `brand/tokens/tokens.css`; check with `grep -n -- "--color-\|--text-\|--font-\|--motion-" brand/tokens/tokens.css` and rename here if a token is spelled differently. The bubble uses ink on paper in both themes because the tokens swap with the theme.
- The still is rendered by the `<Image>` component, so its selectors use `:global(.ottie__still)` inside `.ottie` (Astro's scoped styles do not reach into child components).
- On a page with two Otties, pass `toggle={false}` to the second one so there is one Quiet Ottie button.

- [ ] **Step 6: Write the lab page**

The default lab page mirrors home: the hero Ottie at the top, and the letter Ottie in a `#contact` section far below, so the two-Ottie rules can be tested. The other slugs have one Ottie each; `/blank` has none.

```astro
---
// site/src/pages/lab/ottie/[...slug].astro
// Ottie lab: the e2e tests' fixture and Din's review page. Never built for production.
import Ottie from "../../../components/Ottie.astro";
import BaseLayout from "../../../layouts/BaseLayout.astro";
import { labEnabled } from "../../../lib/lab";
import { DEPLOY } from "../../../lib/deploy-env";
import type { PageContext } from "../../../ottie/lines";

export function getStaticPaths() {
  if (!labEnabled(DEPLOY, __DINS_LABS_OVERRIDE__)) return [];
  return [undefined, "project", "contact", "devlog", "404", "blank"].map((slug) => ({ params: { slug } }));
}

const slug = Astro.params.slug;
const context: PageContext = slug === "project" || slug === "contact" || slug === "devlog" || slug === "404" ? slug : "home";
const twoOtties = slug === undefined;
const cues: Array<[string, number?]> = [
  ["ask:submit"], ["ask:stream"], ["ask:answer", 2], ["ask:answer", 0], ["ask:unknown"], ["ask:resting"],
  ["ask:error"], ["ask:reset"], ["letter:open"], ["letter:ready"], ["letter:sent"],
];
---
<BaseLayout title={`Ottie lab (${context})`} description="Ottie lab" card={null} noindex>
  <main class="lab">
    <section class="lab__hero" id="top">
      <div class="lab__ask">
        <label for="lab-q">Ask Ottie about Din</label>
        <input id="lab-q" type="text" data-ottie-avoid />
        <div class="lab__answer" data-ottie-avoid>Answers appear here.</div>
      </div>
      {slug !== "blank" && <Ottie context={context} pointToward="left" lab class="lab__ottie" />}
    </section>
    <section class="lab__controls" aria-label="Ottie cues">
      {cues.map(([type, sources]) => (
        <button type="button" data-cue={type} data-sources={sources}>{type}{sources !== undefined && ` (${sources} sources)`}</button>
      ))}
      <button type="button" id="lab-reset">Reset visit</button>
      <label><input type="checkbox" id="lab-overlay" /> Still overlay</label>
      <p>Modes: <a href="?ottie-mode=full">full</a>, <a href="?ottie-mode=reduced">reduced</a>, <a href="?ottie-mode=still">still</a></p>
    </section>
    <div class="lab__spacer"></div>
    {twoOtties && (
      <section class="lab__letter" id="contact">
        <div class="lab__sheet" data-ottie-avoid>Dear Din,</div>
        <Ottie context="contact" pointToward="left" toggle={false} lab />
      </section>
    )}
    <div class="lab__spacer"></div>
  </main>
  <script is:inline>
    const send = (type, sources) =>
      window.dispatchEvent(new CustomEvent("ottie:cue", { detail: sources === undefined ? { type } : { type, sources } }));
    for (const b of document.querySelectorAll("[data-cue]")) {
      b.addEventListener("click", () => send(b.dataset.cue, b.dataset.sources === undefined ? undefined : Number(b.dataset.sources)));
    }
    const q = document.getElementById("lab-q");
    q.addEventListener("focus", () => send("ask:focus"));
    q.addEventListener("input", () => send("ask:typing"));
    document.getElementById("lab-reset").addEventListener("click", () => {
      for (const k of ["dins.ottie.seen", "dins.ottie.quiet"]) localStorage.removeItem(k);
      sessionStorage.clear();
      location.reload();
    });
    document.getElementById("lab-overlay").addEventListener("change", (e) => {
      for (const h of document.querySelectorAll("[data-ottie-host]")) h.classList.toggle("is-overlay", e.target.checked);
    });
  </script>
</BaseLayout>

<style>
  .lab { max-width: 1200px; margin: 0 auto; padding: 24px 16px; overflow-x: clip; }
  .lab__hero { display: grid; grid-template-columns: 1fr auto; align-items: end; gap: 24px; min-height: 720px; }
  .lab__ask { display: grid; gap: 12px; align-self: center; max-width: 640px; }
  .lab__ask input { font: inherit; padding: 12px 16px; border-radius: 14px; border: 1px solid var(--color-hairline); }
  .lab__answer, .lab__sheet { min-height: 120px; padding: 16px; border-radius: 14px; background: var(--color-surface); }
  .lab__controls { display: flex; flex-wrap: wrap; gap: 8px; margin-block: 24px; }
  .lab__letter { display: grid; grid-template-columns: minmax(0, 36rem) auto; align-items: end; gap: 24px; min-height: 600px; }
  .lab__spacer { height: 150vh; }
  @media (max-width: 639px) {
    .lab__hero, .lab__letter { grid-template-columns: 1fr; min-height: auto; }
  }
</style>
```

The lab's controls use an inline script on purpose, so the lab adds no bundled JavaScript and the `/blank` page is a fair baseline. `BaseLayout`'s props follow M1's `SeoProps` (`card: null` means no social card).

- [ ] **Step 7: Run the dev server and look**

Run: `pnpm --dir site dev`, open `http://localhost:4321/lab/ottie`.
Expected: Ottie runs in from the right on the first load, waves with "Hi, I’m Ottie.", then idles; scrolling down to the letter section, the hero Ottie shows its still and the letter Ottie starts moving (idle), and the Network panel shows `point.webp` only then; the Quiet Ottie button (one on the page) toggles both; "Still overlay" shows the still over the canvas at half opacity with no visible offset; the browser console has no errors. Stop the server.

- [ ] **Step 8: Check that production builds have no lab**

Run: `WORKERS_CI=1 WORKERS_CI_BRANCH=main pnpm --dir site build && find site/dist -path '*lab*' -name '*.html'`
Expected: the build succeeds and `find` prints nothing.

- [ ] **Step 9: Commit**

```bash
git add site/src/ottie/still.ts site/src/ottie/layout.ts site/src/components/Ottie.astro site/src/lib/lab.ts "site/src/pages/lab/ottie/[...slug].astro" site/astro.config.mjs site/src/env.d.ts site/tests/unit/ottie/layout.test.ts site/tests/unit/lab.test.ts
git commit -m "feat(ottie): add the Ottie component with an inline still, and the Ottie lab page"
```

### Task 14: End-to-end behaviour, loading order, accessibility and resilience

**Files:**
- Create: `site/tests/e2e/ottie.spec.ts`
- Test: this file is the test.

**Interfaces:**
- Consumes: the lab routes and DOM contract from Tasks 12 and 13; `ottie:state` events (Task 1).
- Produces: nothing new.

These run in M0's Playwright setup: the web server is `pnpm build && pnpm serve` (wrangler dev), a `local` deploy, so lab pages are built; the specs land in the default `chromium` project (contract, "Tests").

- [ ] **Step 1: Write the tests**

```ts
// site/tests/e2e/ottie.spec.ts
import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const LAB = "/lab/ottie";
const SHEET = /\/ottie\/([\w-]+)\.webp/;

function trackSheets(page: Page) {
  const names: string[] = [];
  const bytes = new Map<string, number>();
  page.on("request", (r) => { const m = SHEET.exec(r.url()); if (m) names.push(m[1]); });
  page.on("response", async (r) => {
    const m = SHEET.exec(r.url());
    if (m && r.ok()) bytes.set(m[1], (await r.body()).length);
  });
  return { names, bytes };
}
async function trackStates(page: Page) {
  await page.addInitScript(() => {
    const w = window as unknown as { __ottie: { state: string; context: string }[] };
    w.__ottie = [];
    addEventListener("ottie:state", (e) => w.__ottie.push((e as CustomEvent<{ state: string; context: string }>).detail));
  });
}
// States entered by the Otties of one context (the lab's home page has "home" and "contact").
const states = (page: Page, context = "home") => page.evaluate(
  (ctx) => (window as unknown as { __ottie: { state: string; context: string }[] }).__ottie.filter((e) => e.context === ctx).map((e) => e.state),
  context,
);
const seedReturning = (page: Page) => page.addInitScript(() => localStorage.setItem("dins.ottie.seen", "1"));
const host = (page: Page) => page.locator("[data-ottie-host]").first();
const letterHost = (page: Page) => page.locator('[data-ottie-host][data-ottie-context="contact"]');
const cue = (page: Page, type: string) =>
  page.evaluate((t) => dispatchEvent(new CustomEvent("ottie:cue", { detail: { type: t } })), type);
const live = (page: Page) => expect(host(page)).toHaveClass(/is-live/, { timeout: 15_000 });
// With a fake clock, frames only run when the clock moves; sheets still arrive in real time.
async function liveWithClock(page: Page) {
  for (let i = 0; i < 150; i++) {
    if (await host(page).evaluate((el) => el.classList.contains("is-live"))) return;
    await page.clock.runFor(100);
    await page.waitForTimeout(100);
  }
  throw new Error("Ottie never went live under the fake clock");
}

test.describe("loading order", () => {
  test("first visit loads run-in, wave, idle and stays under 0.9 MB", async ({ page }) => {
    const sheets = trackSheets(page);
    await trackStates(page);
    await page.goto(LAB);
    expect(await page.evaluate(() => "ottieEnter" in document.documentElement.dataset)).toBe(true);
    await expect.poll(() => states(page), { timeout: 15_000 }).toEqual(["run-in", "wave", "idle"]);
    await page.waitForTimeout(2000);
    expect(sheets.names).toEqual(["run-in", "wave", "idle"]);
    expect([...sheets.bytes.values()].reduce((a, b) => a + b, 0)).toBeLessThanOrEqual(900_000);
  });

  test("returning visitors load idle, then wave, and just wave", async ({ page }) => {
    const sheets = trackSheets(page);
    await trackStates(page);
    await seedReturning(page);
    await page.goto(LAB);
    expect(await page.evaluate(() => "ottieEnter" in document.documentElement.dataset)).toBe(false);
    await expect.poll(() => states(page), { timeout: 15_000 }).toEqual(["wave", "idle"]);
    expect(sheets.names).toEqual(["idle", "wave"]);
  });

  test("later pages in the same session start in idle with no greeting", async ({ page }) => {
    await trackStates(page);
    await seedReturning(page);
    await page.goto(LAB);
    await expect.poll(() => states(page), { timeout: 15_000 }).toContain("idle");
    await page.goto(`${LAB}/project`);
    await live(page);
    await page.waitForTimeout(3000);
    expect(await states(page)).toEqual([]);
  });

  test("landing on /contact first keeps the full greeting for home", async ({ page }) => {
    await trackStates(page);
    await page.goto(`${LAB}/contact`);
    await page.waitForTimeout(3000);
    expect(await page.evaluate(() => [localStorage.getItem("dins.ottie.seen"), sessionStorage.getItem("dins.ottie.session")]))
      .toEqual([null, null]);
    await page.goto(LAB);
    expect(await page.evaluate(() => "ottieEnter" in document.documentElement.dataset)).toBe(true);
    await expect.poll(() => states(page), { timeout: 15_000 }).toEqual(["run-in", "wave", "idle"]);
    expect(await page.evaluate(() => localStorage.getItem("dins.ottie.seen"))).not.toBeNull();
  });

  test("other sheets load just before their triggers", async ({ page }) => {
    const sheets = trackSheets(page);
    await trackStates(page);
    await seedReturning(page);
    await page.goto(LAB);
    await live(page);
    await page.waitForTimeout(3000);
    expect(sheets.names).toEqual(["idle", "wave"]);
    await page.focus("#lab-q");
    await expect.poll(() => sheets.names).toContain("think");
    await page.click('[data-cue="ask:submit"]');
    await expect.poll(() => states(page)).toContain("think");
    expect(sheets.names).not.toContain("nod");
    await page.click('[data-cue="ask:stream"]');
    await expect.poll(() => sheets.names).toEqual(expect.arrayContaining(["nod", "point", "shrug"]));
    await page.click('[data-cue="ask:answer"][data-sources="2"]');
    await expect.poll(() => states(page), { timeout: 10_000 }).toEqual(expect.arrayContaining(["nod", "point"]));
    await expect.poll(async () => (await states(page)).at(-1), { timeout: 10_000 }).toBe("idle");
  });
});

test.describe("modes", () => {
  test("Quiet Ottie is still, silent, remembered, and loads nothing", async ({ page }) => {
    await seedReturning(page);
    await page.goto(LAB);
    const toggle = page.getByRole("button", { name: "Quiet Ottie" });
    await toggle.click();
    await expect(toggle).toHaveAttribute("aria-pressed", "true");
    expect(await page.evaluate(() => localStorage.getItem("dins.ottie.quiet"))).toBe("1");
    const sheets = trackSheets(page);
    await page.reload();
    await page.waitForTimeout(5000);
    await expect(host(page)).not.toHaveClass(/is-live/);
    await expect(host(page)).toHaveAttribute("data-ottie-mode", "still");
    expect(sheets.names).toEqual([]);
  });

  test("Save-Data gets the still Ottie", async ({ page }) => {
    await page.addInitScript(() => Object.defineProperty(navigator, "connection", { value: { saveData: true } }));
    const sheets = trackSheets(page);
    await page.goto(LAB);
    await page.waitForTimeout(5000);
    await expect(host(page)).toHaveAttribute("data-ottie-mode", "still");
    expect(sheets.names).toEqual([]);
  });

  test.describe("reduced motion", () => {
    test.use({ reducedMotion: "reduce" });
    test("no run-in, no idle sheet, a wave pose and back to the still", async ({ page }) => {
      const sheets = trackSheets(page);
      await trackStates(page);
      await page.goto(LAB);
      expect(await page.evaluate(() => "ottieEnter" in document.documentElement.dataset)).toBe(false);
      await expect.poll(() => states(page), { timeout: 15_000 }).toEqual(["wave", "idle"]);
      await expect(host(page)).not.toHaveClass(/is-live/);
      expect(sheets.names).toEqual(["wave"]);
    });
  });
});

test.describe("resilience", () => {
  test("a failed run-in sheet still gets a visible Ottie and a wave", async ({ page }) => {
    await page.route("**/ottie/run-in.webp*", (r) => r.abort());
    await trackStates(page);
    await page.goto(LAB);
    await page.waitForTimeout(4500);
    const visible = await page.locator("[data-ottie-still]").evaluate((el) =>
      getComputedStyle(el).visibility === "visible" || el.closest(".is-live") !== null);
    expect(visible).toBe(true);
    await expect.poll(() => states(page), { timeout: 15_000 }).toContain("wave");
  });

  test("blocked storage never throws and never greets on every page", async ({ page }) => {
    await page.addInitScript(() => {
      const deny = () => { throw new DOMException("blocked", "SecurityError"); };
      Object.defineProperty(window, "localStorage", { get: deny });
      Object.defineProperty(window, "sessionStorage", { get: deny });
    });
    const errors: string[] = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await trackStates(page);
    await page.goto(LAB);
    await live(page);
    await page.waitForTimeout(3000);
    expect(await states(page)).toEqual([]);
    expect(errors).toEqual([]);
  });

  test.describe("JavaScript off", () => {
    test.use({ javaScriptEnabled: false });
    test("the still holds its box and the toggle stays hidden", async ({ page }) => {
      await page.goto(LAB);
      const box = await host(page).boundingBox();
      expect(box?.width).toBeCloseTo(158.5, 0);
      expect(box?.height).toBeCloseTo(202.5, 0);
      await expect(page.locator("[data-ottie-still]")).toBeVisible();
      await expect(page.locator("[data-ottie-quiet]")).toBeHidden();
    });
  });
});

test.describe("accessibility and layout", () => {
  test("axe finds nothing and Ottie is decorative", async ({ page }) => {
    await seedReturning(page);
    await page.goto(LAB);
    await live(page);
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
    await expect(host(page)).toHaveAttribute("aria-hidden", "true");
    expect(await host(page).locator("a, button, input, [tabindex]").count()).toBe(0);
    const toggle = page.getByRole("button", { name: "Quiet Ottie" });
    await toggle.focus();
    await expect(toggle).toBeFocused();
  });

  for (const width of [375, 1280]) {
    test.describe(`at ${width} px`, () => {
      test.use({ viewport: { width, height: 800 }, deviceScaleFactor: 3 });
      test("no horizontal scroll, no box change, never over the input or answer", async ({ page }) => {
        await page.goto(LAB);
        const before = await host(page).boundingBox();
        await page.waitForTimeout(1500); // during run-in
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
        await live(page);
        expect(await host(page).boundingBox()).toEqual(before);
        const overlap = await page.evaluate(() => {
          const o = document.querySelector("[data-ottie-host]")!.getBoundingClientRect();
          return [...document.querySelectorAll("[data-ottie-avoid]")].some((el) => {
            const a = el.getBoundingClientRect();
            return o.left < a.right && a.left < o.right && o.top < a.bottom && a.top < o.bottom;
          });
        });
        expect(overlap).toBe(false);
        if (width === 375) expect(before!.width).toBeCloseTo(158.5 * 0.75, 0);
        const canvas = await page.locator("[data-ottie-canvas]").evaluate((c: HTMLCanvasElement) => [c.width, c.clientWidth]);
        expect(canvas[0]).toBe(Math.round(canvas[1] * 2)); // DPR 3 is capped at 2
      });
    });
  }
});

test.describe("bubbles, pausing and timers", () => {
  test("a poke shows one short bubble that avoids the input, then no more for 20 s", async ({ page }) => {
    await seedReturning(page);
    await page.addInitScript(() => {
      const w = window as unknown as { __bubbles: string[] };
      w.__bubbles = [];
      new MutationObserver(() => {
        const b = document.querySelector<HTMLElement>("[data-ottie-bubble]");
        if (b && !b.hidden && b.textContent && w.__bubbles.at(-1) !== b.textContent) w.__bubbles.push(b.textContent);
      }).observe(document, { subtree: true, attributes: true, childList: true, characterData: true });
    });
    await page.goto(LAB);
    await live(page);
    await page.waitForTimeout(3000);
    for (let i = 0; i < 6; i++) { await host(page).click(); await page.waitForTimeout(1500); }
    const bubbles = await page.evaluate(() => (window as unknown as { __bubbles: string[] }).__bubbles);
    expect(bubbles).toHaveLength(1);
    expect([...bubbles[0]].length).toBeLessThanOrEqual(90);
  });

  test("pauses off screen and in hidden tabs", async ({ page }) => {
    await seedReturning(page);
    await page.goto(LAB);
    await live(page);
    await expect(host(page)).toHaveAttribute("data-ottie-running", "true");
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await expect(host(page)).toHaveAttribute("data-ottie-running", "false");
    await page.evaluate(() => window.scrollTo(0, 0));
    await expect(host(page)).toHaveAttribute("data-ottie-running", "true");
    await page.evaluate(() => {
      Object.defineProperty(document, "hidden", { value: true, configurable: true });
      document.dispatchEvent(new Event("visibilitychange"));
    });
    await expect(host(page)).toHaveAttribute("data-ottie-running", "false");
  });

  test("a tip after 20 s and a nap after a minute on desktop", async ({ page }) => {
    await seedReturning(page);
    await page.clock.install();
    const sheets = trackSheets(page);
    await trackStates(page);
    await page.goto(LAB);
    await liveWithClock(page);
    await page.clock.runFor(21_000);
    await expect(page.locator("[data-ottie-bubble]")).toBeVisible();
    await page.clock.runFor(80_000);
    await expect.poll(() => states(page)).toContain("nap");
    expect(sheets.names).toEqual(expect.arrayContaining(["talk", "nap", "wake"]));
  });

  test.describe("phones", () => {
    test.use({ viewport: { width: 375, height: 800 } });
    test("no tips and no naps", async ({ page }) => {
      await seedReturning(page);
      await page.clock.install();
      const sheets = trackSheets(page);
      await page.goto(LAB);
      await liveWithClock(page);
      await page.clock.runFor(120_000);
      await expect(page.locator("[data-ottie-bubble]")).toBeHidden();
      expect(sheets.names).not.toContain("nap");
      expect(sheets.names).not.toContain("talk");
    });
  });
});

test.describe("two Otties on one page", () => {
  test("only the Ottie most in view animates; the other shows its still", async ({ page }) => {
    await seedReturning(page);
    await page.goto(LAB);
    await live(page);
    await expect(host(page)).toHaveAttribute("data-ottie-running", "true");
    await expect(letterHost(page)).toHaveAttribute("data-ottie-running", "false");
    await expect(letterHost(page)).not.toHaveClass(/is-live/);
    await letterHost(page).scrollIntoViewIfNeeded();
    await expect(letterHost(page)).toHaveAttribute("data-ottie-running", "true");
    await expect(letterHost(page)).toHaveClass(/is-live/, { timeout: 15_000 });
    await expect(host(page)).toHaveAttribute("data-ottie-running", "false");
    await expect(host(page)).not.toHaveClass(/is-live/);
  });

  test("only the hero greets; the letter Ottie starts in idle and loads point when reached", async ({ page }) => {
    const sheets = trackSheets(page);
    await trackStates(page);
    await page.goto(LAB);
    await expect.poll(() => states(page), { timeout: 15_000 }).toEqual(["run-in", "wave", "idle"]);
    expect(sheets.names).not.toContain("point");
    await letterHost(page).scrollIntoViewIfNeeded();
    await expect.poll(() => sheets.names, { timeout: 10_000 }).toContain("point");
    await page.waitForTimeout(2000);
    expect(await states(page, "contact")).toEqual([]);
    expect(new Set(sheets.names).size).toBe(sheets.names.length); // one shared loader: nothing fetched twice
  });

  test("ask cues move the hero and letter cues move the letter Ottie", async ({ page }) => {
    await seedReturning(page);
    await trackStates(page);
    await page.goto(LAB);
    await live(page);
    await cue(page, "ask:submit");
    await expect.poll(() => states(page)).toContain("think");
    await letterHost(page).scrollIntoViewIfNeeded();
    await cue(page, "letter:open");
    await expect.poll(() => states(page, "contact"), { timeout: 10_000 }).toContain("point");
    await cue(page, "letter:sent");
    await expect.poll(() => states(page, "contact"), { timeout: 10_000 }).toEqual(expect.arrayContaining(["point", "jump"]));
    expect(await states(page)).not.toContain("point");
    expect(await states(page, "contact")).not.toContain("think");
  });

  test("one Quiet Ottie button quiets both", async ({ page }) => {
    await seedReturning(page);
    await page.goto(LAB);
    await expect(page.getByRole("button", { name: "Quiet Ottie" })).toHaveCount(1);
    await page.getByRole("button", { name: "Quiet Ottie" }).click();
    await expect(page.locator('[data-ottie-host][data-ottie-mode="still"]')).toHaveCount(2);
  });
});
```

Note on the clock tests: `page.clock.install()` fakes timers, `requestAnimationFrame` and `requestIdleCallback`, but sheet fetches still take real time, which is why `liveWithClock` alternates fake and real time.

- [ ] **Step 2: Run them**

Run: `pnpm --dir site test:e2e -- tests/e2e/ottie.spec.ts`
Expected: all pass. Typical first failures and what they mean: a wrong network order means a `prefetch` or `ensure` call moved in `player.ts`; a horizontal scrollbar at 375 px means the hero container needs `overflow-x: clip` (see "Assumes", M1); axe failures about contrast on the bubble mean the token names in Task 13 do not match `tokens.css`.

- [ ] **Step 3: Commit**

```bash
git add site/tests/e2e/ottie.spec.ts
git commit -m "test(ottie): cover loading order, modes, two Otties, resilience, layout and timers end to end"
```

### Task 15: Performance trace, JavaScript cost and long-term caching

**Files:**
- Create: `site/tests/e2e/ottie-perf.spec.ts`, `site/public/_headers` (or add a block to it if M0 or M5 already created it)
- Test: this spec, plus curl against the preview.

**Interfaces:**
- Consumes: the lab routes (Task 13), the `ottie:boot` performance mark (Task 12).
- Produces: a saved Chromium trace for Din, and the caching rule for `/ottie/*`.

- [ ] **Step 1: Write the performance and cost tests**

```ts
// site/tests/e2e/ottie-perf.spec.ts
import { gzipSync } from "node:zlib";
import { expect, test } from "@playwright/test";

const LAB = "/lab/ottie";

test("Ottie adds no long tasks and no layout shift at 4x CPU slowdown", async ({ page, browserName }, info) => {
  test.skip(browserName !== "chromium", "CPU throttling and tracing are Chromium only");
  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Emulation.setCPUThrottlingRate", { rate: 4 });
  await page.addInitScript(() => {
    const w = window as unknown as { __long: { start: number; dur: number }[]; __cls: number };
    w.__long = [];
    w.__cls = 0;
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) w.__long.push({ start: e.startTime, dur: e.duration });
    }).observe({ type: "longtask", buffered: true });
    new PerformanceObserver((list) => {
      for (const e of list.getEntries() as unknown as { value: number; hadRecentInput: boolean }[]) {
        if (!e.hadRecentInput) w.__cls += e.value;
      }
    }).observe({ type: "layout-shift", buffered: true });
  });
  const browser = page.context().browser()!;
  await browser.startTracing(page, { path: info.outputPath("ottie-trace.json"), screenshots: true });
  await page.goto(LAB); // first visit: run-in, wave, idle
  await page.waitForTimeout(8000);
  for (const cue of ['[data-cue="ask:submit"]', '[data-cue="ask:stream"]', '[data-cue="ask:answer"][data-sources="2"]']) {
    await page.click(cue);
    await page.waitForTimeout(1500);
  }
  await page.waitForTimeout(3000);
  await browser.stopTracing();
  const boot = await page.evaluate(() => performance.getEntriesByName("ottie:boot")[0]?.startTime ?? 0);
  const long = await page.evaluate(() => (window as unknown as { __long: { start: number; dur: number }[] }).__long);
  expect(long.filter((t) => t.start >= boot)).toEqual([]);
  expect(await page.evaluate(() => (window as unknown as { __cls: number }).__cls)).toBe(0);
  await info.attach("ottie-trace", { path: info.outputPath("ottie-trace.json"), contentType: "application/json" });
});

test("Ottie's JavaScript costs at most 15 KB gzipped", async ({ page, request }) => {
  test.skip(process.env.E2E_DEV === "1", "dev server scripts are unbundled");
  const scriptsOn = async (path: string) => {
    await page.goto(path);
    await page.waitForLoadState("networkidle");
    return page.evaluate(() => performance.getEntriesByType("resource").map((e) => e.name).filter((n) => n.endsWith(".js")));
  };
  const withOttie = await scriptsOn(LAB);
  const without = await scriptsOn(`${LAB}/blank`);
  let bytes = 0;
  for (const url of withOttie.filter((u) => !without.includes(u))) bytes += gzipSync(await (await request.get(url)).body()).length;
  expect(bytes).toBeGreaterThan(0);
  expect(bytes).toBeLessThanOrEqual(15_000);
});
```

- [ ] **Step 2: Run them**

Run: `pnpm --dir site test:e2e -- tests/e2e/ottie-perf.spec.ts`
Expected: PASS. The trace is saved under `site/test-results/` and attached to the HTML report; open it in Chrome DevTools (Performance panel, "Load profile") to see Ottie's frames. If a long task shows up, look at what it is in the trace before changing anything: decode work on the main thread means `createImageBitmap` fell back to `Image.decode()`; a long paint means the canvas is larger than expected (check the DPR cap).

- [ ] **Step 3: Add the caching rule**

```text
# site/public/_headers (Cloudflare Workers static assets)
# Sheet URLs carry ?v=<content version> (src/ottie/assets.ts), so they can be immutable.
/ottie/*
  Cache-Control: public, max-age=31536000, immutable
```

M5's build-time headers integration merges `site/public/_headers` into the final file and keeps this rule (contract, "Security headers and CSP"), so it stays here even after M5 lands.

- [ ] **Step 4: Commit**

```bash
git add site/tests/e2e/ottie-perf.spec.ts site/public/_headers
git commit -m "test(ottie): check long tasks, layout shift and script cost; cache sheets for a year"
```

- [ ] **Step 5: After the branch has a preview link (needs Din's go to push)**

Run: `curl -sI "<preview-url>/ottie/idle.webp?v=check" | grep -i cache-control`
Expected: `cache-control: public, max-age=31536000, immutable`. (Any `v` value works for the header check; the real version is in the page's requests.) Record the result in the ledger.

### Task 16: Put Ottie on the site's pages (needs M1 merged)

**Files:**
- Modify (M1's files, which use M1's placeholder `OttieSlot.astro` today): `site/src/pages/index.astro` (hero, and the `#contact` section), `site/src/pages/work/[id].astro`, `site/src/pages/writing/[id].astro`, `site/src/pages/contact/index.astro`, `site/src/pages/404.astro`; M1's specs that look for `.ottie-slot`: `site/tests/e2e/home.spec.ts`, `case-study.spec.ts`, `writing.spec.ts`, `misc.spec.ts`.
- Delete: `site/src/components/OttieSlot.astro` (contract, "Pages and markup").
- Create: `site/tests/e2e/ottie-routes.spec.ts`

**Interfaces:**
- Consumes: `<Ottie>` (Task 13); M1's markup hooks: `#top` (`data-setpiece="lens"`), `#contact` (`data-setpiece="letter"`), `article.project-card`, the sample posts `/writing/sample-devlog/` and `/writing/sample-note/` (built with M1's `DINS_SHOW_DRAFTS=1` in the e2e server), `DRAFTS_SHOWN` from M1's `site/tests/e2e/helpers.ts`.
- Produces: Ottie on exactly the routes in PRD section 4, plus the letter Ottie on home (Din, 2026-10-21, M4 decision 4).

Placement (PRD section 4 and the contract):

| Where | Replace | With |
|---|---|---|
| Home hero (`#top`) | `<OttieSlot placement="hero" />` | `<Ottie context="home" pointToward="left" class="hero__ottie" />` |
| Home `#contact` section | nothing yet | `<Ottie context="contact" pointToward="left" toggle={false} />` beside `<ContactForm />` |
| Case study (`work/[id].astro`) | `<OttieSlot placement="project" />` | `<Ottie context="project" pointToward="left" />` |
| Devlog posts (`writing/[id].astro`) | `{isDevlog && <OttieSlot placement="devlog" />}` | `{isDevlog && <Ottie context="devlog" />}` |
| `/contact` | `<OttieSlot placement="contact" />` | `<Ottie context="contact" pointToward="left" />` (the only Ottie there, so it keeps the toggle) |
| 404 | `<OttieSlot placement="404" state="shrug" />` | `<Ottie context="404" />` (the director opens with a shrug) |

Not on About, the writing list or formal pages. M4 builds the folding letter around the home `#contact` form later and does not mount another Ottie (contract, M4 amendments).

- [ ] **Step 1: Write the failing route test**

```ts
// site/tests/e2e/ottie-routes.spec.ts
import { expect, test, type Page } from "@playwright/test";
import { DRAFTS_SHOWN } from "./helpers";

const otties = (page: Page) => page.locator("[data-ottie-host]");

test("home has the hero Ottie and the letter Ottie, with one Quiet Ottie button", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator('#top [data-ottie-host][data-ottie-context="home"]')).toHaveCount(1);
  await expect(page.locator('#contact [data-ottie-host][data-ottie-context="contact"]')).toHaveCount(1);
  await expect(otties(page)).toHaveCount(2);
  await expect(page.getByRole("button", { name: "Quiet Ottie" })).toHaveCount(1);
});

test("contact, 404 and case studies have one Ottie each", async ({ page }) => {
  await page.goto("/contact/");
  await expect(page.locator('[data-ottie-host][data-ottie-context="contact"]')).toHaveCount(1);
  await expect(otties(page)).toHaveCount(1);
  await page.goto("/no-such-page/");
  await expect(page.locator('[data-ottie-host][data-ottie-context="404"]')).toHaveCount(1);
  await page.goto("/work/");
  const project = await page.locator("article.project-card a").first().getAttribute("href");
  test.skip(!project, "needs a project");
  await page.goto(project!);
  await expect(page.locator('[data-ottie-host][data-ottie-context="project"]')).toHaveCount(1);
});

test("devlog posts get Ottie, other posts and formal pages do not", async ({ page }) => {
  test.skip(!DRAFTS_SHOWN, "needs the sample posts");
  await page.goto("/writing/sample-devlog/");
  await expect(page.locator('[data-ottie-host][data-ottie-context="devlog"]')).toHaveCount(1);
  for (const path of ["/writing/sample-note/", "/writing/", "/about/", "/work/", "/privacy/"]) {
    await page.goto(path);
    await expect(otties(page), path).toHaveCount(0);
  }
});

test("the hero Ottie is about a quarter of the hero's height and clear of the questions", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/");
  const { ratio, overlaps } = await page.evaluate(() => {
    const o = document.querySelector('#top [data-ottie-host]')!.getBoundingClientRect();
    const hero = document.querySelector("#top")!.getBoundingClientRect();
    const ask = document.querySelector("#top .ask-slot")!.getBoundingClientRect();
    return {
      ratio: o.height / hero.height,
      overlaps: o.left < ask.right && ask.left < o.right && o.top < ask.bottom && ask.top < o.bottom,
    };
  });
  expect(ratio).toBeGreaterThanOrEqual(0.2);
  expect(ratio).toBeLessThanOrEqual(0.32);
  expect(overlaps).toBe(false);
});

test("on phones the hero Ottie sits below the questions", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 800 });
  await page.goto("/");
  const below = await page.evaluate(() => {
    const o = document.querySelector('#top [data-ottie-host]')!.getBoundingClientRect();
    const ask = document.querySelector("#top .ask-slot")!.getBoundingClientRect();
    return o.top >= ask.bottom;
  });
  expect(below).toBe(true);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true);
});
```

Run: `pnpm --dir site test:e2e -- tests/e2e/ottie-routes.spec.ts`
Expected: FAIL, no `[data-ottie-host]` on any route yet.

- [ ] **Step 2: Swap the placeholders and update M1's specs**

Make the replacements in the table (each file imports `Ottie from "../components/Ottie.astro"` at the right depth instead of `OttieSlot`). In the home `#contact` section, wrap the form and the letter Ottie so they sit side by side on wide screens and stack on phones:

```astro
<section class="section wrap" id="contact" data-setpiece="letter" aria-labelledby="contact-h">
  <span class="t-label eyebrow">Contact</span>
  <h2 id="contact-h" class="t-h1">Write to me.</h2>
  <p class="t-lead">Roles, admissions questions, or just a hello. It lands in my inbox.</p>
  <div class="letter-row">
    <ContactForm />
    <Ottie context="contact" pointToward="left" toggle={false} />
  </div>
</section>
```

and in `index.astro`'s `<style>`:

```css
.letter-row { display: flex; gap: var(--space-7); align-items: flex-end; flex-wrap: wrap; }
.letter-row > :first-child { flex: 1 1 32rem; min-width: 0; }
.hero { overflow-x: clip; } /* run-in starts off to the right */
@media (max-width: 639px) {
  .hero-text { order: 1; }
  .hero :global(.hero__ottie) { order: 2; margin-inline: auto; }
}
```

Then `git rm site/src/components/OttieSlot.astro` and update M1's specs (same intent, new hooks):

| Spec | Old | New |
|---|---|---|
| `home.spec.ts` | `.ottie-slot[data-ottie-placement="hero"]` has `aria-hidden` | `#top [data-ottie-host][data-ottie-context="home"]` has `aria-hidden="true"` |
| `case-study.spec.ts` | `.ottie-slot[data-ottie-placement="project"]` count 1 | `[data-ottie-host][data-ottie-context="project"]` count 1 |
| `writing.spec.ts` | `.ottie-slot[data-ottie-placement="devlog"]` count 1, `.ottie-slot` count 0 | `[data-ottie-host][data-ottie-context="devlog"]` count 1, `[data-ottie-host]` count 0 |
| `misc.spec.ts` | `.ottie-slot[data-ottie-placement="404"]` has `data-ottie-state="shrug"` | `[data-ottie-host][data-ottie-context="404"]` count 1 |

Run: `grep -rn "OttieSlot\|ottie-slot\|data-ottie-placement" site/`
Expected: no output.

- [ ] **Step 3: Run the route tests and the whole e2e suite**

Run: `pnpm --dir site test:e2e`
Expected: all pass, including M1's route, axe and no-JS specs (the still is in the HTML, so the no-JS pages still show Ottie).

- [ ] **Step 4: Commit**

```bash
git add site/src site/tests/e2e
git commit -m "feat(ottie): replace the Ottie placeholders with the player on home, letter, project, contact, 404 and devlog"
```

### Task 17 (Din): Review Ottie's lines

**Files:** `site/src/ottie/lines.json` (reviewed in the branch's PR or in a preview).

Ottie's lines are copy, and the PRD requires a reviewed file. The drafts in Task 6 are a starting point in Ottie's voice from `docs/BRAND.md` (first person, short, warm, a little nerdy, honest; talks about Din, never as Din; no exclamation spam). A few of them, to set the tone:

- Greeting (fixed by the PRD): "Hi, I’m Ottie."
- Poke: "That tickles. Ask me something about Din instead?"
- Poke: "I only know what Din has written down, but I know it well."
- Home tip: "Try one of the suggested questions. I’ll show where each answer came from."
- Project tip: "Ask me about this project. I’ll only search its own sources."
- Contact tip: "Pick a reason and write a line. Din reads every letter."
- 404: "I looked closer. This page isn’t here."

- [ ] Din edits, cuts or approves each line (every line must still pass `pnpm --dir site exec vitest run tests/unit/ottie/lines.test.ts`).
- [x] French lines: English only in v1 (Din, 2026-10-21). A `fr` block is a post-launch follow-up.
- [ ] Claude records "Lines reviewed (Din, date)" in the ledger.

### Task 18 (Din): Approve Ottie in the preview

Needs Din's go to push the branch so Workers Builds makes a preview link.

Checklist for Din, on the preview's `/lab/ottie` pages and (after Task 16) the real pages, on the 2020 laptop and a mid-range phone:

- [ ] First visit (use "Reset visit"): Ottie runs in, waves with "Hi, I’m Ottie.", settles into idle. No duplicate Ottie, no jump when the still hands over to the canvas. Why: the first impression on the hero.
- [ ] Reload: just a wave. New page in the same tab: just idle. Why: Ottie should not repeat the greeting.
- [ ] Focus the box, send, stream, answer: think, then nod and point; "don't know": shrug. Why: the answer flow M3 drives.
- [ ] Click Ottie: a hop and a line; clicking again within 20 s: hop only. Why: speaking sparingly.
- [ ] Wait 20 s: one tip; wait a minute more: nap; click something: wake. On a phone: neither. Why: the idle behaviours and their thresholds (tune in `director.ts` if they feel wrong).
- [ ] Two Otties on home: scroll from the hero to the letter; only the Ottie in view moves, the other holds its still; the letter Ottie points when the letter comes into view and jumps when it is sent. Why: Din's M4 decision 4.
- [ ] Quiet Ottie: still and silent (both Otties), remembered after a reload; the label and its spot under the hero Ottie feel right.
- [ ] `?calm` (M4's review switch): Ottie uses the reduced-motion poses.
- [ ] Reduced motion (system setting, or `?ottie-mode=reduced`): poses with gentle crossfades; pick the key pose for each state (wave, think, nod, point, shrug, jump, nap) and tell Claude the drawing numbers to put in `poses.ts`.
- [ ] Still overlay: the still and the canvas line up.
- [ ] Point direction: in the lab, turn the mirrored point on locally (`MIRROR_POINT_APPROVED = true` in a scratch build) and judge it next to the right-facing point. Only Din's approval turns it on for the site; if Din rejects it, choose between placing Ottie left of what it points at or a left-pointing render (decision 3).
- [ ] Land on `/lab/ottie/contact` in a fresh window, then open `/lab/ottie`: the full first-visit greeting plays there.
- [ ] Chrome DevTools, Performance panel, 4x CPU slowdown, record 10 s on the home page: no red long tasks from Ottie, no layout shift. Network panel: sheets in the order run-in, wave, idle on a first visit; each later sheet only when its trigger is near.
- [ ] Claude records Din's approval (or the changes asked for) in the ledger; Din sets task 2.12 to Accepted.

### Task 19: Close the milestone in the docs

**Files:**
- Modify: `docs/TASKS.md` (2.12 status and verification), `docs/WORK_LEDGER.md` (decisions, test results, trace and network evidence, Din's approval), `docs/site/PLAN.md` (M2 section: the lab page and any threshold changes), `brand/ottie/README.md` (one line: the site's player is `site/src/ottie/`, and the preview stays the reference).

- [ ] **Step 1: Run everything**

Run: `./check.sh && pnpm --dir site test:e2e`
Expected: green. Paste the test counts into the ledger entry.

- [ ] **Step 2: Update the documents** with what was built, how it was verified (unit and e2e counts, the trace result, the network order, the curl header check) and what is still waiting for Din. Keep Implemented, Verified and Accepted distinct.

- [ ] **Step 3: Commit**

```bash
git add docs/TASKS.md docs/WORK_LEDGER.md docs/site/PLAN.md brand/ottie/README.md
git commit -m "docs: record M2 Ottie on the site results"
```

---

## Assumes

What this plan relies on from the other milestones. If one turns out differently, adapt at merge and note it in the ledger.

**M0 (Foundation)**
- `site/` is the Astro 7.4 app (Worker `dins-site`) with TypeScript 6.0 (`resolveJsonModule` on, strict), the Cloudflare adapter, and `astro:assets` able to resize images at build time (the adapter's default compile-time image service with sharp).
- `/ottie/<file>.webp` serves `brand/ottie/dist/` in dev, preview and production (copy or alias), and Vite may import files from the repo root (`brand/...`), which the pnpm workspace root normally allows.
- Vitest 4.1 picks up `site/tests/unit/**/*.test.ts` in a Node environment (Node 24 has `EventTarget`, `CustomEvent`, `Blob` and `structuredClone`); `pnpm --dir site test`, `test:e2e`, `check` and `./check.sh` exist. M3's note says `@cloudflare/vitest-pool-workers` is deprecated in favour of `@cloudflare/vitest-plugin`; nothing here depends on that choice.
- Playwright 1.64 with `@axe-core/playwright`: M0's web server (`pnpm build && pnpm serve`, wrangler dev, waiting on `/api/health`) is a `local` deploy, so lab pages exist and scripts are bundled; M2's specs run in the default `chromium` project.
- `site/src/layouts/BaseLayout.astro` (M0 creates it, M1 fills it) takes M1's `SeoProps` (`title`, `description`, `card`, `noindex`) and loads `brand/tokens/tokens.css` and the fonts.
- The shared build-time deploy (contract, "Build-time deploy"): `site/src/lib/deploy.ts` (`type Deploy`, `deployFromEnv`), `site/src/lib/deploy-env.ts` (`DEPLOY`), the `__DINS_DEPLOY__` define in `site/astro.config.mjs` and its declaration in `site/src/env.d.ts`. Task 13 adds `__DINS_LABS_OVERRIDE__` beside it.

**M1 (Pages and content)**
- The routes in PRD section 2 exist with M1's hooks: `#top` (`data-setpiece="lens"`) holding `.ask-slot` and `<OttieSlot placement="hero">`, `#contact` (`data-setpiece="letter"`) holding `<ContactForm />`, `article.project-card`, `<OttieSlot>` on the case study, `/contact`, 404 and devlog posts, the sample posts `/writing/sample-devlog/` and `/writing/sample-note/`, and `DRAFTS_SHOWN` in `site/tests/e2e/helpers.ts`. Task 16 swaps every `OttieSlot` and deletes it.
- Task 16 adds `overflow-x: clip` to the hero so run-in can start off screen without a scrollbar; M1 or M4 should keep it if they restyle the hero.

**M3 (Ask Ottie)**
- The Ask island calls `cueOttie` as in "The public interface": `ask:focus` on focus, `ask:typing` on input, `ask:submit` on send, `ask:stream` on the first token, `ask:answer` with the number of sources when the answer is complete, `ask:unknown`, `ask:resting` and `ask:error` for those paths, `ask:reset` when cleared.
- The question input and the answer panel (and the project Ask bar) carry `data-ottie-avoid`.

**M4 (Set pieces)**
- The letter calls `letter:open` when it comes into view, `letter:ready` when the form is filled in and `letter:sent` after sending; the letter carries `data-ottie-avoid`.
- M4 does not mount an Ottie; Task 16 places `<Ottie context="contact">` in the home `#contact` section and on `/contact`. The envelope flies off after `onOttieState` reports `idle` following `jump` for `context === "contact"` (the hero Ottie's states carry `context: "home"`). If M4 moves the letter Ottie, it does so with `transform` only.
- M4's `MotionHead.astro` sets `<html data-motion="full|calm">` before first paint; Ottie reads it (calm means reduced).
- The lens intro and the set pieces leave Ottie's box where Task 16 puts it (no layout changes after load).

**M5 (Hardening and launch)**
- The production CSP allows the Ottie component's inline pre-paint `<script>` and its layout `<style>` element by hash (Astro's `security.csp`, per the contract; M5's CSP sweep shows it if not) and `connect-src 'self'` for the sheet fetches. Ottie renders no `style` attribute; the bubble's position is set from JavaScript (CSSOM), which the CSP allows. No `blob:` source is needed.
- M5's headers integration keeps the `/ottie/*` caching rule from `site/public/_headers` (Task 15) when it merges.
- The VoiceOver pass and the real-phone check cover Ottie's pages (Ottie should be silent to VoiceOver; the Quiet Ottie toggle should be announced as a toggle button).

## Open questions for Din (all decided 2026-10-21)

Din answered all eight with "Go with your recommendations" (2026-10-21). Each question is kept as asked, with the decision under it.

1. **First-visit load order.** The PRD says idle loads first, then wave. On a first visit nothing moves until run-in arrives, so this plan loads run-in, wave, then idle (868 KB, inside the 0.6 to 0.9 MB target). Returning visits follow the PRD (idle, then wave, 610 KB). OK to note this in PRD section 4?
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** run-in, wave, idle on a first visit; it goes into PRD section 4 on merge.
2. **What counts as a visit.** The plan greets once per browser session: run-in, wave and "Hi, I’m Ottie." the first time ever, just the wave on the first Ottie page of later sessions, and nothing on other pages of the same session. The PRD does not say how often a returning visitor gets the wave.
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** once per browser session, as planned.
3. **Point direction.** Point is drawn toward screen right only. On the home hero Ottie sits at the right with the answer and sources to its left, so it would point away from them. Options: mirror point when the target is on the left (built, behind `MIRROR_POINT_APPROVED`; the glasses and lighting flip too), place Ottie to the left of what it points at, or render a left-pointing state in the private `dins-ottie` repo.
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** build the mirrored point as planned, behind `MIRROR_POINT_APPROVED = false`. Din judges it in the lab (Task 18), and it is turned on only with Din's approval. If Din rejects the mirror, the other two options stay as fallbacks.
4. **"Lots of background clicking" sends Ottie to nap.** The plan reads it as 6 clicks on non-interactive areas within 4 seconds, and background clicks alone do not wake Ottie. Is that the behaviour you meant?
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** yes, 6 background clicks within 4 seconds, and background clicks alone do not wake Ottie.
5. **Talk while streaming.** M3's planning note suggested talk while an answer streams. The PRD keeps talk for speech bubbles and silence while streaming, so this plan keeps think until the answer lands. Confirm.
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** no talk while streaming; think until the answer lands.
6. **Quiet Ottie toggle.** Placed as a small mono "Quiet Ottie" button under the page's first Ottie (one per page; it quiets both Otties on home), visible only with JavaScript. Quiet means the still pose with no state changes at all (not even reduced-motion poses). Is that spot and meaning right, or should it live in the footer?
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** under the page's first Ottie, with that meaning.
7. **French lines** (PRD section 9): English only in v1 unless you say otherwise.
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** English only in v1.
8. **Landing on `/contact` first.** Per the contract the letter Ottie never greets, so a first visit that lands on `/contact` gets no run-in or "Hi, I’m Ottie.", and the visit is still marked, so the home page later just waves. Fine, or should the greeting wait for the first page that has a greeting Ottie?
   **Decided (Din, 2026-10-21, "Go with your recommendations"):** the greeting waits for the first page that has a greeting Ottie. A page whose Otties never greet (`/contact`, the 404 page) does not mark the visit, so a later home page still gets the full first-visit greeting. Built in Task 11 (`greetsIn`, `marksVisit`, unit tested), used by Task 9's director and Task 12's player, and covered end to end in Task 14 (lab `/contact`, then lab home).

## Doc updates to apply on merge

For whoever merges this plan (not done here, per the planning rules):

- `docs/TASKS.md`, row 2.12: link this plan (`docs/site/plans/M2-ottie.md`) and add rows 2.12a "Review Ottie's lines (Din)" and 2.12b "Approve Ottie in the preview (Din)", both Planned.
- `docs/WORK_LEDGER.md`: an entry "M2 plan written (Claude, 2026-10-21)" listing the decisions in "Decisions made in this plan", the public cue interface, and the eight questions with Din's decisions.
- `docs/site/PLAN.md`, M2 section: mention the lab page (`/lab/ottie`, never built for production), the cue interface file (`site/src/ottie/events.ts`) that M3 and M4 use, the second (letter) Ottie on home, and that M2's Task 16 waits for M1's pages.
- `docs/site/plans/README.md`: mark the M2 amendments as applied, and add `detail.context` on `ottie:state` to the "Ottie (owner M2)" section.
- `docs/site/PRD.md` section 4 (Din decided these on 2026-10-21): a first visit loads run-in, wave, then idle; the greeting plays once per browser session, on the first page with a greeting Ottie (a visit that starts on `/contact` or a 404 still gets it later); 6 background clicks within 4 seconds send Ottie to nap and do not wake it; no talk while an answer streams; Ottie's lines are English only in v1; point is mirrored only if Din approves it in the lab.
- `docs/WORK_LEDGER.md`: record Din's answers to the eight M2 questions ("Go with your recommendations", 2026-10-21).
