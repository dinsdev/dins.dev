# M0 Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

Status: Proposed (plan only, written 2026-10-21 for Din's review). Nothing here is built yet. Task 2.10 in `docs/TASKS.md`. Build branch: `feat/m0-foundation`.

**Goal:** A working, checked and deployable skeleton for dins.dev: the pnpm workspace, the Astro 7.4 app on Cloudflare Workers with brand tokens, self-hosted fonts and the Ottie sheets served, the `rag/` Python project, every test harness, `check.sh`, pre-commit with gitleaks, CI, Renovate and Workers Builds previews, so M1 to M5 can start on a known base.

**Architecture:** A root pnpm workspace with one package, `site/` (Astro, static by default, with on-demand routes running in the Worker through `@astrojs/cloudflare`). Repo-wide tooling (Prettier, ESLint, pre-commit, gitleaks, `check.sh`) lives at the root; the site owns its build, types and tests; `rag/` is a separate uv project. One `mise.toml` pins the toolchain for Din's machine and for CI, and Workers Builds builds `main` to production and every other branch to its own Preview (Cloudflare's `previews` block gives previews their own D1 and vars).

**Tech Stack:** Node 24 LTS, pnpm 12.14, Astro 7.4, @astrojs/cloudflare 14.4, Svelte 5.57 with @astrojs/svelte 9.1, TypeScript 6.0, wrangler 4.151, Vitest 4.1 with @cloudflare/vitest-plugin 1.4, Playwright 1.64 with @axe-core/playwright 4.14, Prettier 3.9, ESLint 10.13 with typescript-eslint 8.72, Python 3.12 with uv, pytest 9.1, Ruff 0.17, pre-commit 4.7, gitleaks 8.30, Renovate, GitHub Actions, Workers Builds, D1, fontTools 4.67.

**Spec:** `docs/site/PRD.md` (sections 5 and 6), `docs/site/PLAN.md` (M0 and Environments), `docs/BRAND.md` (Typography, Design tokens), the 2026-10-21 entries in `docs/WORK_LEDGER.md`.

## Global Constraints

- Versions checked on npm, PyPI and GitHub on 2026-10-21. Pin npm packages to minor with `~` ranges (patches through Renovate). Exact pins used below:
  - `astro ~7.4.1`, `@astrojs/cloudflare ~14.4.1`, `@astrojs/svelte ~9.1.0`, `svelte ~5.57.2`, `@astrojs/check ~0.9.11`, `svelte-check ~4.7.7`
  - `typescript ~6.0.3` (NOT 7: `@astrojs/check`, `@astrojs/svelte` and `svelte-check` need `^5 || ^6`, and `typescript-eslint` 8.72 needs `<6.1.0`)
  - `vitest ~4.1.12` (NOT 5, see Open question 1), `@cloudflare/vitest-plugin ~1.4.6`
  - `@playwright/test ~1.64.1`, `@axe-core/playwright ~4.14.0`, `wrangler ~4.151.3`, `@types/node ~24.19.2`
  - `prettier ~3.9.10`, `prettier-plugin-astro ~1.1.1`, `prettier-plugin-svelte ~4.1.1`, `eslint ~10.13.0`, `@eslint/js ~10.0.1`, `typescript-eslint ~8.72.0`, `eslint-plugin-astro ~3.2.1`, `eslint-plugin-svelte ~3.23.1`, `globals ~17.13.0`
  - `packageManager: pnpm@12.14.0`; Python `>=3.12`, `pytest~=9.1`, `ruff~=0.17.1`; mise tools `node 24`, `pnpm 12`, `uv 0.13`, `gitleaks 8.30`, `pre-commit 4.7`
- Node 24 LTS through mise (Din's setup). Workers Builds reads `.node-version`.
- Contract commands other plans rely on (defined exactly in Task 2 and Task 11): `pnpm --dir site dev|build|test|test:e2e|check`, `./check.sh` at the root (under 2 minutes without e2e), `uv run --project rag pytest`.
- Repo contract paths: `site/astro.config.mjs`, `site/wrangler.jsonc`, `site/src/{layouts,components,styles,ottie,lib}/`, `site/src/pages/api/`, `site/migrations/`, `site/tests/{unit,worker,e2e}/`, Ottie sheets served under `/ottie/`, `site/public/ask/` owned by M3 (never gitignored).
- Bindings are read with `import { env } from "cloudflare:workers"` (Astro 6+ removed `Astro.locals.runtime`).
- No cookies: Astro sessions are turned off (`session: false`), which also stops the adapter from provisioning a `SESSION` KV namespace.
- Fonts: WOFF2, subset to Latin plus French, self-hosted, two preloaded (Fraunces and Instrument Sans), metric-matched fallbacks (PRD section 6). All three are OFL.
- This repo is public: no secrets, tokens or account inventories. D1 database IDs are not secrets.
- Writing style in every file, comment and commit: no em dashes, no en dashes as separators, no AI buzzwords; refer to Din by name. Conventional Commits, no attribution trailers.
- Stop and ask Din before: downloading the two font files (Task 4), creating Cloudflare resources (Task 2, Task 13), pushing, opening PRs, connecting Workers Builds, installing the Renovate app.

## Review Focus

1. **Running from the wrong folder.** Din and agents run commands from the repo root, from `site/` and from CI. `./check.sh` must work from any working directory, and the `pnpm --dir site ...` scripts must not depend on the caller's cwd. Pinned by Task 11 Step 4 (running check.sh from `site/`).
2. **A fresh clone with no generated files.** `site/public/ottie/` and `site/worker-configuration.d.ts` are generated and gitignored; `dev`, `build`, `check` and the tests must create what they need. Pinned by Task 11 Step 5 (fresh clone run) and the scripts in Task 2.
3. **Dark mode.** tokens.css switches on `prefers-color-scheme` and `data-theme`. axe must pass in both schemes, not just light. Pinned by Task 7 (`starter.spec.ts` runs axe in light and dark).
4. **Fonts that fail to load.** A blocked or slow WOFF2 must leave readable text in a metric-matched fallback, not invisible text or a big shift. Pinned by Task 7 (fonts blocked test) and Task 4 (fallback metrics test).
5. **Previews touching production data.** A branch preview must use the preview D1 and preview vars, never production. Pinned by `/api/health` reporting `SITE_ENV` (Task 3) and the preview check in Task 13 Step 7.

---

## File map

| Path | Responsibility | Task |
|---|---|---|
| `mise.toml`, `.node-version` | Toolchain pins (local and CI; Workers Builds reads `.node-version`) | 1 |
| `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml` | Workspace root, repo-wide dev tooling, version catalog | 1 |
| `.gitignore`, `.editorconfig` | Ignore rules for build output and generated files; editor defaults | 1 |
| `site/package.json` | Site dependencies and the contract scripts | 2 |
| `site/astro.config.mjs`, `site/tsconfig.json`, `site/src/env.d.ts` | Astro, adapter, Svelte, TypeScript | 2 |
| `site/wrangler.jsonc` | Worker config: observability, assets, D1 `DB`, vars, `previews` | 2 |
| `site/src/worker.ts` | Custom Worker entry (Astro handler; M3 adds `scheduled`) | 2 |
| `site/.dev.vars.example` | Local vars template | 2 |
| `site/vitest.config.ts`, `site/vitest.unit.config.ts`, `site/vitest.worker.config.ts` | Unit and Workers-runtime test projects | 3 |
| `site/src/lib/health.ts`, `site/src/pages/api/health.ts` | Health endpoint (uptime monitor, preview isolation check) | 3 |
| `site/tests/unit/health.test.ts`, `site/tests/worker/health.test.ts`, `site/tests/worker/d1.test.ts` | Harness proofs | 3 |
| `site/tests/worker/entry.ts`, `site/tests/worker/apply-migrations.ts`, `site/tests/worker/tsconfig.json` | Worker test entry, D1 migrations setup, test types | 3 |
| `site/migrations/.gitkeep` | D1 migrations folder (M3 adds files) | 3 |
| `brand/tools/fonts.py`, `brand/tools/test_fonts.py` | Font subsetting, fallback metrics, `fonts.css` generation, tests | 4 |
| `brand/fonts/InstrumentSans-VF.ttf`, `brand/fonts/JetBrainsMono-VF.ttf`, `brand/fonts/OFL-InstrumentSans.txt`, `brand/fonts/OFL-JetBrainsMono.txt`, `brand/fonts/README.md` | Vendored font sources with licences | 4 |
| `brand/fonts/web/*.woff2`, `brand/fonts/web/fonts.css` | Generated web fonts (committed, like the other brand outputs) | 4 |
| `brand/tokens/tokens.json`, `brand/tokens/tokens.css` | Fallback family names added to the font stacks | 4 |
| `site/scripts/sync-brand.mjs`, `site/tests/unit/sync-brand.test.ts` | Copies `brand/ottie/dist` to `site/public/ottie` | 5 |
| `site/src/styles/global.css`, `site/src/layouts/BaseLayout.astro`, `site/src/components/BuildNote.svelte`, `site/src/pages/index.astro` | Base layout and starter page | 6 |
| `site/playwright.config.ts`, `site/tests/e2e/starter.spec.ts` | End-to-end and axe | 7 |
| `rag/pyproject.toml`, `rag/uv.lock`, `rag/.python-version`, `rag/src/dins_rag/__init__.py`, `rag/src/dins_rag/paths.py`, `rag/tests/test_paths.py`, `pytest.ini` | RAG project skeleton | 8 |
| `eslint.config.js`, `.prettierrc.json`, `.prettierignore` | Lint and format | 9 |
| `.pre-commit-config.yaml`, `.gitleaks.toml` | Commit hooks and secret scanning | 10 |
| `check.sh` | Every local check; CI runs it | 11 |
| `.github/workflows/ci.yml`, `renovate.json` | CI and dependency updates | 12 |
| `docs/site/workers-builds.md` | Workers Builds setup steps and preview checklist | 13 |

---

### Task 1: Toolchain and workspace root

**Files:**
- Create: `mise.toml`, `.node-version`, `package.json`, `pnpm-workspace.yaml`, `.editorconfig`
- Modify: `.gitignore`

**Interfaces:**
- Produces: root scripts `pnpm check` (runs `./check.sh`), `pnpm lint`, `pnpm format`, `pnpm format:check` (wired in Task 9). Catalog entries `svelte` and `typescript` used by `catalog:` in `site/package.json`.

- [ ] **Step 1: Write `mise.toml`**

```toml
# Toolchain for Din's machine and CI (jdx/mise-action reads this file).
# Workers Builds does not read mise; it reads .node-version and PNPM_VERSION.
[tools]
node = "24"
pnpm = "12"
uv = "0.13"
gitleaks = "8.30"
pre-commit = "4.7"
```

- [ ] **Step 2: Write `.node-version`**

```
24
```

- [ ] **Step 3: Write `pnpm-workspace.yaml`**

```yaml
packages:
  - site

# One version for packages used by both the root tooling and the site.
catalog:
  svelte: ~5.57.2
  typescript: ~6.0.3
```

- [ ] **Step 4: Write the root `package.json`** (devDependencies are added in Task 9; keep the list empty now so the install is fast)

```json
{
  "name": "dins",
  "private": true,
  "type": "module",
  "packageManager": "pnpm@12.14.0",
  "engines": {
    "node": ">=24 <25"
  },
  "scripts": {
    "check": "./check.sh",
    "lint": "eslint .",
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  },
  "devDependencies": {}
}
```

- [ ] **Step 5: Write `.editorconfig`**

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
indent_style = space
indent_size = 2
trim_trailing_whitespace = true

[*.py]
indent_size = 4

[*.md]
trim_trailing_whitespace = false
```

- [ ] **Step 6: Add the generated and local files to `.gitignore`** (append below the existing `__pycache__/` line; keep everything else)

```gitignore
.dev.vars
.dev.vars.*
!.dev.vars.example
site/worker-configuration.d.ts
site/public/ottie/
site/playwright-report/
site/test-results/
.pytest_cache/
.ruff_cache/
*.tsbuildinfo
```

The existing `dist/` rule already covers `site/dist/` and the existing `!brand/ottie/dist/` exception keeps the sheets tracked. `site/public/ask/` stays tracked (M3).

- [ ] **Step 7: Install the toolchain and check versions**

Run: `mise install && mise exec -- node -v && mise exec -- pnpm -v && mise exec -- gitleaks version && mise exec -- pre-commit --version`
Expected: `v24.x`, `12.14.0` (pnpm switches itself to the `packageManager` version), `8.30.x`, `pre-commit 4.7.x`.

- [ ] **Step 8: Commit**

```bash
git add mise.toml .node-version pnpm-workspace.yaml package.json .editorconfig .gitignore
git commit -m "build: add the pnpm workspace root and mise toolchain"
```

---

### Task 2: The `site/` app on the Cloudflare adapter

**Files:**
- Create: `site/package.json`, `site/astro.config.mjs`, `site/tsconfig.json`, `site/src/env.d.ts`, `site/src/worker.ts`, `site/wrangler.jsonc`, `site/.dev.vars.example`, `site/src/pages/index.astro` (temporary one-liner, replaced in Task 6)

**Interfaces:**
- Produces (the contract): `pnpm --dir site dev | build | serve | test | test:unit | test:worker | test:e2e | check | typegen | sync:brand`.
- Produces: Worker name `dins-site`; bindings `ASSETS` (static assets), `DB` (D1; production database `dins-site`, preview database `dins-site-preview`); var `SITE_ENV` (`production`, `preview`; `local` through `.dev.vars`).
- Produces: `site/src/worker.ts` default export `{ fetch }` built on `handle` from `@astrojs/cloudflare/handler`. M3 adds `scheduled` here.

- [ ] **Step 1: Write `site/package.json`**

```json
{
  "name": "site",
  "private": true,
  "type": "module",
  "scripts": {
    "sync:brand": "node scripts/sync-brand.mjs",
    "typegen": "wrangler types",
    "dev": "pnpm sync:brand && pnpm typegen && astro dev",
    "build": "pnpm sync:brand && pnpm typegen && astro build",
    "serve": "wrangler dev --port 8787 --ip 127.0.0.1",
    "check": "pnpm typegen && astro check && svelte-check --tsconfig ./tsconfig.json --fail-on-warnings",
    "test": "vitest run",
    "test:unit": "vitest run --project unit",
    "test:worker": "vitest run --project worker",
    "test:e2e": "pnpm build && playwright test"
  },
  "dependencies": {
    "@astrojs/cloudflare": "~14.4.1",
    "@astrojs/svelte": "~9.1.0",
    "astro": "~7.4.1",
    "svelte": "catalog:"
  },
  "devDependencies": {
    "@astrojs/check": "~0.9.11",
    "@axe-core/playwright": "~4.14.0",
    "@cloudflare/vitest-plugin": "~1.4.6",
    "@playwright/test": "~1.64.1",
    "@types/node": "~24.19.2",
    "svelte-check": "~4.7.7",
    "typescript": "catalog:",
    "vitest": "~4.1.12",
    "wrangler": "~4.151.3"
  }
}
```

`scripts/sync-brand.mjs` arrives in Task 5. Until then create a stub so `dev` and `build` run: `site/scripts/sync-brand.mjs` containing `// Replaced in Task 5.` on one line.

- [ ] **Step 2: Install and approve build scripts**

Run: `pnpm install`
Expected: install completes. If pnpm reports ignored build scripts, run `pnpm approve-builds` and approve only `esbuild`, `workerd` and `sharp` (whichever are listed), then run `pnpm install` again. Commit the resulting change to `pnpm-workspace.yaml`. Do not approve anything else without asking Din.

- [ ] **Step 3: Write `site/astro.config.mjs`**

```js
// @ts-check
import cloudflare from "@astrojs/cloudflare";
import svelte from "@astrojs/svelte";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://dins.dev",
  // Pages are prerendered; routes that export `prerender = false` run in the Worker.
  output: "static",
  // The site sets no cookies, so no sessions (and no SESSION KV namespace).
  session: false,
  adapter: cloudflare({
    // Optimize images at build time with sharp; no Images binding at runtime.
    imageService: "compile",
  }),
  integrations: [svelte()],
});
```

- [ ] **Step 4: Write `site/tsconfig.json`**

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": [".astro/types.d.ts", "worker-configuration.d.ts", "src/**/*", "scripts/**/*", "tests/unit/**/*", "tests/e2e/**/*", "*.config.*"],
  "exclude": ["dist", "tests/worker"],
  "compilerOptions": {
    "types": ["node"]
  }
}
```

`tests/worker` has its own tsconfig (Task 3) because it needs the Workers test types instead of Node's.

- [ ] **Step 5: Write `site/src/env.d.ts`**

```ts
/// <reference types="astro/client" />
```

- [ ] **Step 6: Write `site/src/worker.ts`**

```ts
// The Worker entry. Astro serves every request; M3 adds `scheduled` for the
// nightly question log cleanup.
import { handle } from "@astrojs/cloudflare/handler";

export default {
  fetch: handle,
} satisfies ExportedHandler<Env>;
```

- [ ] **Step 7: Ask Din, then create the two D1 databases**

Ask Din: "M0 needs two free D1 databases in your Cloudflare account, `dins-site` (production) and `dins-site-preview` (branch previews). OK to create them with wrangler?" If Din says yes:

Run: `pnpm --dir site exec wrangler d1 create dins-site` and `pnpm --dir site exec wrangler d1 create dins-site-preview`
Expected: each prints a `database_id` UUID. Use them in Step 8.

If Din wants to wait, use `00000000-0000-0000-0000-000000000000` for both IDs in Step 8 (local D1 and the test pool accept any ID) and replace them in Task 13 Step 1, before the first preview.

- [ ] **Step 8: Write `site/wrangler.jsonc`** (replace the two `database_id` values with the IDs from Step 7)

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "dins-site",
  "main": "./src/worker.ts",
  "compatibility_date": "2026-10-21",
  "compatibility_flags": ["nodejs_compat"],
  "upload_source_maps": true,
  "workers_dev": true,
  // Static files. The Astro adapter fills in the build output directory.
  "assets": { "binding": "ASSETS" },
  "observability": {
    "enabled": true,
    "logs": { "enabled": true, "invocation_logs": true },
    "traces": { "enabled": true }
  },
  "vars": { "SITE_ENV": "production" },
  // Budget counter and question log (M3 adds the migrations).
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "dins-site",
      "database_id": "PASTE_PRODUCTION_ID",
      "migrations_dir": "migrations"
    }
  ],
  // Branch previews (Workers Builds runs `wrangler preview`). Vars and storage
  // bindings are not inherited, so each one is redeclared here.
  "previews": {
    "vars": { "SITE_ENV": "preview" },
    "d1_databases": [
      {
        "binding": "DB",
        "database_name": "dins-site-preview",
        "database_id": "PASTE_PREVIEW_ID",
        "migrations_dir": "migrations"
      }
    ]
  }
}
```

The two `PASTE_..._ID` strings are execution-time values from Step 7, never committed as-is. Create `site/migrations/.gitkeep` (empty) now so `migrations_dir` exists.

- [ ] **Step 9: Write `site/.dev.vars.example`**

```
# Copy to .dev.vars for local work. Never commit .dev.vars.
SITE_ENV=local
```

Then run `cp site/.dev.vars.example site/.dev.vars`.

- [ ] **Step 10: Write a temporary `site/src/pages/index.astro`**

```astro
<h1>dins.dev</h1>
```

- [ ] **Step 11: Generate types and build**

Run: `pnpm --dir site typegen && pnpm --dir site build`
Expected: `worker-configuration.d.ts` appears with `DB: D1Database`, `ASSETS: Fetcher` and `SITE_ENV`; the build finishes with `dist/client/index.html` and `dist/server/wrangler.json`. The build log must NOT contain "Enabling sessions with Cloudflare KV". If Astro rejects `session: false`, stop and ask Din before changing it: the fallback makes the adapter provision a `SESSION` KV namespace.

- [ ] **Step 12: Run the built Worker under wrangler dev**

Run: `pnpm --dir site serve` in one terminal, then `curl -s http://127.0.0.1:8787/ | grep -c "dins.dev"`
Expected: `1`. `site/.wrangler/deploy/config.json` exists (the redirect the Cloudflare Vite plugin writes so wrangler uses the built config). If it does not, change `serve` to `wrangler dev --config dist/server/wrangler.json --port 8787 --ip 127.0.0.1` and note it in the ledger. Stop the server.

- [ ] **Step 13: Run the dev server**

Run: `pnpm --dir site dev`, open http://localhost:4321/
Expected: the heading shows; the log says the dev server runs in workerd. Stop it.

- [ ] **Step 14: Commit**

```bash
git add site pnpm-lock.yaml pnpm-workspace.yaml
git commit -m "feat(site): add the Astro app on the Cloudflare adapter"
```

---

### Task 3: Test harnesses (unit and Workers runtime) with the health route

**Files:**
- Create: `site/vitest.config.ts`, `site/vitest.unit.config.ts`, `site/vitest.worker.config.ts`, `site/tests/worker/tsconfig.json`, `site/tests/worker/entry.ts`, `site/tests/worker/apply-migrations.ts`, `site/src/lib/health.ts`, `site/src/pages/api/health.ts`
- Test: `site/tests/unit/health.test.ts`, `site/tests/worker/health.test.ts`, `site/tests/worker/d1.test.ts`

**Interfaces:**
- Consumes: `Env` from `worker-configuration.d.ts` (Task 2).
- Produces: `healthBody(siteEnv: string): { ok: true; service: "dins-site"; env: string }` and `healthResponse(siteEnv: string): Response` in `site/src/lib/health.ts`; `GET /api/health` returns that JSON with `cache-control: no-store`.
- Produces for M3: worker tests get `env.DB` with every migration in `site/migrations/` applied before each test file; `env.SITE_ENV` is `"test"`.

- [ ] **Step 1: Write the vitest configs**

`site/vitest.config.ts`:

```ts
import { defineConfig } from "vitest/config";

// Two projects: plain Node unit tests, and tests inside the Workers runtime.
export default defineConfig({
  test: {
    projects: ["./vitest.unit.config.ts", "./vitest.worker.config.ts"],
  },
});
```

`site/vitest.unit.config.ts`:

```ts
import { defineProject } from "vitest/config";

export default defineProject({
  test: {
    name: "unit",
    include: ["tests/unit/**/*.test.ts"],
    environment: "node",
  },
});
```

`site/vitest.worker.config.ts`:

```ts
import { cloudflareTest, readD1Migrations } from "@cloudflare/vitest-plugin";
import { defineProject } from "vitest/config";

const migrations = await readD1Migrations("./migrations");

export default defineProject({
  plugins: [
    cloudflareTest({
      // A tiny test entry instead of src/worker.ts, which needs Astro's build.
      main: "./tests/worker/entry.ts",
      wrangler: { configPath: "./wrangler.jsonc" },
      miniflare: {
        bindings: { SITE_ENV: "test", TEST_MIGRATIONS: migrations },
      },
    }),
  ],
  test: {
    name: "worker",
    include: ["tests/worker/**/*.test.ts"],
    setupFiles: ["./tests/worker/apply-migrations.ts"],
  },
});
```

- [ ] **Step 2: Write the worker test support files**

`site/tests/worker/entry.ts`:

```ts
// Test-only Worker entry. Tests import modules directly; this only has to exist.
export default {
  fetch: () => new Response("test entry"),
} satisfies ExportedHandler;
```

`site/tests/worker/apply-migrations.ts`:

```ts
import { applyD1Migrations } from "cloudflare:test";
import { env } from "cloudflare:workers";

declare module "cloudflare:workers" {
  interface ProvidedEnv {
    TEST_MIGRATIONS: import("cloudflare:test").D1Migration[];
  }
}

// Safe to run before every file: applied migrations are skipped.
await applyD1Migrations(env.DB, env.TEST_MIGRATIONS);
```

`site/tests/worker/tsconfig.json`:

```json
{
  "extends": "../../tsconfig.json",
  "include": ["./**/*.ts", "../../worker-configuration.d.ts", "../../src/**/*.ts"],
  "exclude": [],
  "compilerOptions": {
    "types": ["@cloudflare/vitest-plugin/types"]
  }
}
```

If TypeScript reports `ProvidedEnv` is unknown, check the plugin's `types/cloudflare-test.d.ts` for the interface name it extends and use that; the runtime behaviour does not depend on it.

- [ ] **Step 3: Write the failing unit test**

`site/tests/unit/health.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { healthBody, healthResponse } from "../../src/lib/health";

describe("health", () => {
  it("reports ok, the service and the environment", () => {
    expect(healthBody("preview")).toEqual({ ok: true, service: "dins-site", env: "preview" });
  });

  it("falls back to unknown when the environment is empty", () => {
    expect(healthBody("").env).toBe("unknown");
  });

  it("returns uncached JSON", async () => {
    const res = healthResponse("production");
    expect(res.status).toBe(200);
    expect(res.headers.get("content-type")).toBe("application/json; charset=utf-8");
    expect(res.headers.get("cache-control")).toBe("no-store");
    expect(await res.json()).toEqual({ ok: true, service: "dins-site", env: "production" });
  });
});
```

- [ ] **Step 4: Run it to verify it fails**

Run: `pnpm --dir site test:unit`
Expected: FAIL, cannot resolve `../../src/lib/health`.

- [ ] **Step 5: Implement `site/src/lib/health.ts`**

```ts
export type HealthBody = { ok: true; service: "dins-site"; env: string };

export function healthBody(siteEnv: string): HealthBody {
  return { ok: true, service: "dins-site", env: siteEnv || "unknown" };
}

export function healthResponse(siteEnv: string): Response {
  return new Response(JSON.stringify(healthBody(siteEnv)), {
    status: 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
```

- [ ] **Step 6: Run it to verify it passes**

Run: `pnpm --dir site test:unit`
Expected: 3 passed.

- [ ] **Step 7: Write the failing worker tests**

`site/tests/worker/health.test.ts`:

```ts
import { describe, expect, it } from "vitest";
import { GET } from "../../src/pages/api/health";

describe("GET /api/health inside workerd", () => {
  it("reads SITE_ENV from the Worker env", async () => {
    const res = await GET({} as Parameters<typeof GET>[0]);
    expect(await res.json()).toEqual({ ok: true, service: "dins-site", env: "test" });
  });
});
```

`site/tests/worker/d1.test.ts`:

```ts
import { env } from "cloudflare:workers";
import { describe, expect, it } from "vitest";

describe("D1 binding", () => {
  it("is bound as DB and answers queries", async () => {
    const row = await env.DB.prepare("select 1 as one").first<{ one: number }>();
    expect(row).toEqual({ one: 1 });
  });
});
```

- [ ] **Step 8: Run them to verify the health test fails**

Run: `pnpm --dir site test:worker`
Expected: `d1.test.ts` passes (proves the pool, wrangler config and migrations setup); `health.test.ts` FAILS, cannot resolve `../../src/pages/api/health`.

- [ ] **Step 9: Implement `site/src/pages/api/health.ts`**

```ts
import type { APIRoute } from "astro";
import { env } from "cloudflare:workers";
import { healthResponse } from "../../lib/health";

export const prerender = false;

export const GET: APIRoute = () => healthResponse(env.SITE_ENV);
```

- [ ] **Step 10: Run every site test**

Run: `pnpm --dir site test`
Expected: both projects run; 5 tests pass (3 unit, 2 worker).

- [ ] **Step 11: Check the route in the built Worker**

Run: `pnpm --dir site build && pnpm --dir site serve`, then `curl -s http://127.0.0.1:8787/api/health`
Expected: `{"ok":true,"service":"dins-site","env":"local"}` (from `.dev.vars`). Stop the server.

- [ ] **Step 12: Commit**

```bash
git add site
git commit -m "test(site): add unit and Workers runtime harnesses with a health route"
```

---

### Task 4: Self-hosted fonts (WOFF2, Latin plus French, metric-matched fallbacks)

Where the fonts come from (all SIL Open Font License 1.1, which allows bundling and subsetting; the licence text must travel with the files):

| Family | Source | Licence |
|---|---|---|
| Fraunces | Already vendored: `brand/fonts/Fraunces-VF.ttf` (axes opsz 9 to 144, wght 100 to 900, SOFT 0 to 100, WONK 0 to 1), from github.com/undercasetype/Fraunces | `brand/fonts/OFL.txt` |
| Instrument Sans | google/fonts `ofl/instrumentsans/InstrumentSans[wdth,wght].ttf` (194,336 bytes), upstream github.com/Instrument/instrument-sans | `ofl/instrumentsans/OFL.txt` |
| JetBrains Mono | google/fonts `ofl/jetbrainsmono/JetBrainsMono[wght].ttf` (187,208 bytes), upstream github.com/JetBrains/JetBrainsMono | `ofl/jetbrainsmono/OFL.txt` |

Web subsets pin what the brand never changes, which keeps them small (Fraunces measured at 70.5 KB on 2026-10-21): Fraunces SOFT 50, WONK 0, wght 400 to 600 (default 500), opsz kept; Instrument Sans wdth 100, wght 400 to 600; JetBrains Mono wght 400 to 500. Latin plus French covers Basic Latin, Latin-1 (French accents, guillemets), Œ œ Ÿ, curly quotes, the ellipsis, narrow no-break space, the euro and arrows.

**Files:**
- Create: `brand/tools/fonts.py`, `brand/tools/test_fonts.py`, `brand/fonts/InstrumentSans-VF.ttf`, `brand/fonts/JetBrainsMono-VF.ttf`, `brand/fonts/OFL-InstrumentSans.txt`, `brand/fonts/OFL-JetBrainsMono.txt`, `brand/fonts/README.md`, `brand/fonts/web/fraunces.woff2`, `brand/fonts/web/instrument-sans.woff2`, `brand/fonts/web/jetbrains-mono.woff2`, `brand/fonts/web/fonts.css`
- Modify: `brand/tokens/tokens.json` (font stacks), `brand/tokens/tokens.css` (regenerated), `README.md` (licence and regenerate lines)

**Interfaces:**
- Produces: `brand/fonts/web/fonts.css` with `@font-face` rules for `"Fraunces"`, `"Instrument Sans"`, `"JetBrains Mono"` and `"Fraunces Fallback"`, `"Instrument Sans Fallback"`, `"JetBrains Mono Fallback"` (local system fonts with overrides). Relative URLs to the WOFF2 files beside it.
- Produces: `--font-display`, `--font-text`, `--font-mono` in tokens.css include the fallback family second, for example `"Fraunces", "Fraunces Fallback", Georgia, ...`.
- Python: `LATIN_FR: list[int]`, `subset_font(src: Path, dst: Path, axes: dict[str, float | tuple[float, float, float]]) -> int` (bytes written), `fallback_metrics(web: Path, fallback: Path) -> dict[str, float]` with keys `size_adjust`, `ascent_override`, `descent_override`, `line_gap_override` (percent, 2 decimals), `font_css(...) -> str`.

- [ ] **Step 1: Ask Din, then download the two fonts and licences**

Ask Din: "Task 4 downloads Instrument Sans (InstrumentSans[wdth,wght].ttf, 194 KB) and JetBrains Mono (JetBrainsMono[wght].ttf, 187 KB) plus their OFL.txt files from github.com/google/fonts. OK?" If yes:

```bash
base=https://raw.githubusercontent.com/google/fonts/main/ofl
curl -fsSL "$base/instrumentsans/InstrumentSans%5Bwdth,wght%5D.ttf" -o brand/fonts/InstrumentSans-VF.ttf
curl -fsSL "$base/instrumentsans/OFL.txt" -o brand/fonts/OFL-InstrumentSans.txt
curl -fsSL "$base/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf" -o brand/fonts/JetBrainsMono-VF.ttf
curl -fsSL "$base/jetbrainsmono/OFL.txt" -o brand/fonts/OFL-JetBrainsMono.txt
```

Expected: the sizes match the table. Check the licences: `head -1 brand/fonts/OFL-*.txt` shows each project's copyright line.

- [ ] **Step 2: Write `brand/fonts/README.md`**

```markdown
# Fonts

The three brand families, all under the SIL Open Font License 1.1.

| File | Family | Source | Licence |
|---|---|---|---|
| `Fraunces-VF.ttf` | Fraunces | github.com/undercasetype/Fraunces | `OFL.txt` |
| `InstrumentSans-VF.ttf` | Instrument Sans | github.com/google/fonts (`ofl/instrumentsans`), upstream github.com/Instrument/instrument-sans | `OFL-InstrumentSans.txt` |
| `JetBrainsMono-VF.ttf` | JetBrains Mono | github.com/google/fonts (`ofl/jetbrainsmono`), upstream github.com/JetBrains/JetBrainsMono | `OFL-JetBrainsMono.txt` |

`web/` holds the site's subsets (WOFF2, Latin plus French) and `fonts.css`, generated by `brand/tools/fonts.py`. Do not edit them by hand. The wordmark tools use the full `Fraunces-VF.ttf`.
```

- [ ] **Step 3: Write the failing tests `brand/tools/test_fonts.py`**

```python
"""Tests for brand/tools/fonts.py and the committed web fonts."""

from pathlib import Path

from fontTools.ttLib import TTFont

import fonts

FRENCH = "àâæçéèêëîïôœùûüÿÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸ«»‘’“”…€ "
WEB = Path(__file__).resolve().parents[1] / "fonts" / "web"
BUDGET = {"fraunces.woff2": 80_000, "instrument-sans.woff2": 50_000, "jetbrains-mono.woff2": 45_000}


def test_latin_fr_covers_french():
    assert {ord(c) for c in FRENCH} <= set(fonts.LATIN_FR)


def test_fallback_metrics_of_a_font_against_itself():
    m = fonts.fallback_metrics(fonts.FRAUNCES_SRC, fonts.FRAUNCES_SRC)
    assert m["size_adjust"] == 100.0
    # Fraunces: hhea ascent 1956, descent -510, line gap 0, 2000 units per em.
    assert m["ascent_override"] == 97.8
    assert m["descent_override"] == 25.5
    assert m["line_gap_override"] == 0.0


def test_built_fonts_cover_french_and_fit_the_budget():
    for name, limit in BUDGET.items():
        path = WEB / name
        cmap = TTFont(path).getBestCmap()
        missing = [c for c in FRENCH if ord(c) not in cmap]
        assert not missing, f"{name} is missing {missing}"
        assert path.stat().st_size <= limit, f"{name} is {path.stat().st_size} bytes"


def test_fraunces_axes_are_pinned():
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue) for a in TTFont(WEB / "fraunces.woff2")["fvar"].axes}
    assert axes == {"opsz": (9.0, 9.0, 144.0), "wght": (400.0, 500.0, 600.0)}


def test_css_declares_each_family_and_its_fallback():
    css = (WEB / "fonts.css").read_text()
    for family in ("Fraunces", "Instrument Sans", "JetBrains Mono"):
        assert f'font-family: "{family}";' in css
        assert f'font-family: "{family} Fallback";' in css
    assert css.count("font-display: swap;") == 3
    assert "size-adjust:" in css
```

- [ ] **Step 4: Run them to verify they fail**

Run: `cd brand/tools && uv run --no-project --with fonttools~=4.67 --with brotli --with pytest pytest -q test_fonts.py; cd -`
Expected: FAIL with `ModuleNotFoundError: No module named 'fonts'`.

- [ ] **Step 5: Implement `brand/tools/fonts.py`**

```python
"""Build the site's web fonts: WOFF2 subsets (Latin plus French) and fonts.css.

Run from the repo root on macOS (the fallback metrics read the system fonts):
    uv run --no-project --with fonttools~=4.67 --with brotli python brand/tools/fonts.py
"""

from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

BRAND = Path(__file__).resolve().parents[1]
FONTS = BRAND / "fonts"
WEB = FONTS / "web"
FRAUNCES_SRC = FONTS / "Fraunces-VF.ttf"
SYSTEM = Path("/System/Library/Fonts/Supplemental")

# Basic Latin, Latin-1, dotless i, OE/oe, Y diaeresis, spacing accents, general
# punctuation (curly quotes, ellipsis, narrow no-break space), euro, trademark,
# arrows, minus.
LATIN_FR = sorted(
    {
        *range(0x20, 0x7F),
        *range(0xA0, 0x100),
        0x131,
        0x152,
        0x153,
        0x178,
        0x2C6,
        0x2DA,
        0x2DC,
        *range(0x2000, 0x2070),
        0x20AC,
        0x2122,
        *range(0x2190, 0x2194),
        0x2212,
    }
)

# (source, output, pinned axes, weight range, local fallback, fallback file)
FAMILIES = [
    ("Fraunces", FRAUNCES_SRC, "fraunces.woff2",
     {"SOFT": 50, "WONK": 0, "wght": (400, 500, 600)}, "400 600", "Georgia", SYSTEM / "Georgia.ttf"),
    ("Instrument Sans", FONTS / "InstrumentSans-VF.ttf", "instrument-sans.woff2",
     {"wdth": 100, "wght": (400, 400, 600)}, "400 600", "Arial", SYSTEM / "Arial.ttf"),
    ("JetBrains Mono", FONTS / "JetBrainsMono-VF.ttf", "jetbrains-mono.woff2",
     {"wght": (400, 400, 500)}, "400 500", "Courier New", SYSTEM / "Courier New.ttf"),
]


def subset_font(src: Path, dst: Path, axes: dict) -> int:
    font = instancer.instantiateVariableFont(TTFont(src), axes)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features += ["tnum", "case"]
    subsetter = subset.Subsetter(options)
    subsetter.populate(unicodes=LATIN_FR)
    subsetter.subset(font)
    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(dst)
    return dst.stat().st_size


def _average_width(font: TTFont) -> float:
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    widths = [hmtx[cmap[ord(c)]][0] for c in "abcdefghijklmnopqrstuvwxyz " if ord(c) in cmap]
    return sum(widths) / len(widths) / font["head"].unitsPerEm


def fallback_metrics(web: Path, fallback: Path) -> dict[str, float]:
    w, f = TTFont(web), TTFont(fallback)
    size = _average_width(w) / _average_width(f)
    upm = w["head"].unitsPerEm
    hhea = w["hhea"]
    return {
        "size_adjust": round(size * 100, 2),
        "ascent_override": round(hhea.ascent / upm / size * 100, 2),
        "descent_override": round(abs(hhea.descent) / upm / size * 100, 2),
        "line_gap_override": round(hhea.lineGap / upm / size * 100, 2),
    }


def _range(codes: list[int]) -> str:
    parts, start = [], codes[0]
    for prev, cur in zip(codes, codes[1:] + [None]):
        if cur != prev + 1:
            parts.append(f"U+{start:04X}" if start == prev else f"U+{start:04X}-{prev:04X}")
            start = cur
    return ", ".join(parts)


def font_css(family: str, file: str, weights: str, local: str, m: dict[str, float]) -> str:
    return (
        f'@font-face {{\n  font-family: "{family}";\n  src: url("./{file}") format("woff2");\n'
        f"  font-weight: {weights};\n  font-style: normal;\n  font-display: swap;\n"
        f"  unicode-range: {_range(LATIN_FR)};\n}}\n\n"
        f'@font-face {{\n  font-family: "{family} Fallback";\n  src: local("{local}");\n'
        f"  size-adjust: {m['size_adjust']}%;\n  ascent-override: {m['ascent_override']}%;\n"
        f"  descent-override: {m['descent_override']}%;\n  line-gap-override: {m['line_gap_override']}%;\n}}\n"
    )


def main() -> None:
    blocks = ["/* Generated by brand/tools/fonts.py. Do not edit by hand. */\n"]
    for family, src, out, axes, weights, local, local_file in FAMILIES:
        size = subset_font(src, WEB / out, axes)
        print(f"{out}: {size:,} bytes")
        blocks.append(font_css(family, out, weights, local, fallback_metrics(WEB / out, local_file)))
    (WEB / "fonts.css").write_text("\n".join(blocks))


if __name__ == "__main__":
    main()
```

Ruff will reformat the `FAMILIES` rows in Task 9; that is fine.

- [ ] **Step 6: Build the fonts**

Run: `uv run --no-project --with fonttools~=4.67 --with brotli python brand/tools/fonts.py`
Expected: three lines with sizes (Fraunces about 70,500 bytes) and `brand/fonts/web/fonts.css`.

- [ ] **Step 7: Run the tests to verify they pass**

Run: `cd brand/tools && uv run --no-project --with fonttools~=4.67 --with brotli --with pytest pytest -q test_fonts.py; cd -`
Expected: 5 passed. If a size budget fails, do not raise it silently: record the real sizes and ask Din (the budgets are Claude's estimates).

- [ ] **Step 8: Add the fallback families to the tokens** (see Open question 3)

In `brand/tokens/tokens.json`, change the three font stacks so the fallback family comes second:

- display: `"Fraunces", "Fraunces Fallback", Georgia, "Times New Roman", serif`
- text: `"Instrument Sans", "Instrument Sans Fallback", system-ui, -apple-system, "Segoe UI", sans-serif`
- mono: `"JetBrains Mono", "JetBrains Mono Fallback", ui-monospace, "SF Mono", Menlo, monospace`

Run: `python3 brand/tools/tokens.py && git diff --stat brand/tokens`
Expected: only the three `--font-*` lines change in `tokens.css`.

- [ ] **Step 9: Update `README.md`**

Add to the "Regenerating the logo files" block: `uv run --no-project --with fonttools~=4.67 --with brotli python brand/tools/fonts.py`. Change the License line to: "The Fraunces, Instrument Sans and JetBrains Mono fonts are under the SIL Open Font License (`brand/fonts/`)." Add `brand/fonts/` to the table as "The three brand fonts (OFL) and their web subsets".

- [ ] **Step 10: Commit**

```bash
git add brand/fonts brand/tools/fonts.py brand/tools/test_fonts.py brand/tokens README.md
git commit -m "feat(brand): add the web font subsets with metric-matched fallbacks"
```

---

### Task 5: Serve the Ottie sheets under `/ottie/`

**Files:**
- Create: `site/scripts/sync-brand.mjs` (replaces the Task 2 stub)
- Test: `site/tests/unit/sync-brand.test.ts`

**Interfaces:**
- Produces: `syncBrand({ repoRoot, siteDir }: { repoRoot: string; siteDir: string }): Promise<string[]>` returning the copied file names (sorted). It replaces `site/public/ottie/` with the `.webp` files and `manifest.json` from `brand/ottie/dist/` (not `manifest.js`, which only the preview uses).
- Produces for M2: `/ottie/manifest.json` and `/ottie/<state>.webp` in dev, preview and production. Long-term cache headers for `/ottie/*` belong to M2 or M5 (see Assumes).

- [ ] **Step 1: Write the failing test**

`site/tests/unit/sync-brand.test.ts`:

```ts
import { mkdir, mkdtemp, readdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, expect, it } from "vitest";
import { syncBrand } from "../../scripts/sync-brand.mjs";

async function fakeRepo() {
  const repoRoot = await mkdtemp(join(tmpdir(), "dins-sync-"));
  const dist = join(repoRoot, "brand/ottie/dist");
  await mkdir(dist, { recursive: true });
  for (const f of ["idle.webp", "wave.webp", "manifest.json", "manifest.js"]) {
    await writeFile(join(dist, f), f);
  }
  const siteDir = join(repoRoot, "site");
  await mkdir(join(siteDir, "public/ottie"), { recursive: true });
  await writeFile(join(siteDir, "public/ottie/stale.webp"), "old");
  return { repoRoot, siteDir };
}

describe("syncBrand", () => {
  it("copies the sheets and manifest.json, not manifest.js", async () => {
    const { repoRoot, siteDir } = await fakeRepo();
    expect(await syncBrand({ repoRoot, siteDir })).toEqual(["idle.webp", "manifest.json", "wave.webp"]);
  });

  it("removes files that are no longer in brand/ottie/dist", async () => {
    const { repoRoot, siteDir } = await fakeRepo();
    await syncBrand({ repoRoot, siteDir });
    expect((await readdir(join(siteDir, "public/ottie"))).sort()).toEqual(["idle.webp", "manifest.json", "wave.webp"]);
  });

  it("fails loudly when the sheets are missing", async () => {
    const repoRoot = await mkdtemp(join(tmpdir(), "dins-sync-empty-"));
    await expect(syncBrand({ repoRoot, siteDir: join(repoRoot, "site") })).rejects.toThrow(/brand\/ottie\/dist/);
  });
});
```

- [ ] **Step 2: Run it to verify it fails**

Run: `pnpm --dir site test:unit`
Expected: FAIL, `syncBrand` is not exported.

- [ ] **Step 3: Implement `site/scripts/sync-brand.mjs`**

```js
// Copies the Ottie sheets from brand/ottie/dist into site/public/ottie so the
// site serves them under /ottie/. Runs before dev and build.
import { copyFile, mkdir, readdir, rm } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

/** @param {{ repoRoot: string, siteDir: string }} dirs */
export async function syncBrand({ repoRoot, siteDir }) {
  const src = join(repoRoot, "brand/ottie/dist");
  const dst = join(siteDir, "public/ottie");
  let names;
  try {
    names = await readdir(src);
  } catch {
    throw new Error(`Ottie sheets not found in ${src} (expected brand/ottie/dist)`);
  }
  const wanted = names.filter((n) => n.endsWith(".webp") || n === "manifest.json").sort();
  await rm(dst, { recursive: true, force: true });
  await mkdir(dst, { recursive: true });
  await Promise.all(wanted.map((n) => copyFile(join(src, n), join(dst, n))));
  return wanted;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const siteDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
  const copied = await syncBrand({ repoRoot: resolve(siteDir, ".."), siteDir });
  console.log(`sync-brand: ${copied.length} Ottie files in public/ottie`);
}
```

Add `"allowJs": true` to `compilerOptions` in `site/tsconfig.json` only if `astro check` complains about the `.mjs` import; the JSDoc keeps it typed.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `pnpm --dir site test:unit`
Expected: 6 passed (3 health, 3 sync).

- [ ] **Step 5: Check the sheets are served by the built Worker**

Run: `pnpm --dir site build && pnpm --dir site serve`, then `curl -s http://127.0.0.1:8787/ottie/manifest.json | python3 -c "import json,sys; print(len(json.load(sys.stdin)['states']))"` and `curl -sI http://127.0.0.1:8787/ottie/idle.webp | grep -i content-type`
Expected: `12` and `content-type: image/webp`. Stop the server.

- [ ] **Step 6: Commit**

```bash
git add site/scripts/sync-brand.mjs site/tests/unit/sync-brand.test.ts
git commit -m "feat(site): serve the Ottie sheets under /ottie/"
```

---

### Task 6: Base layout and starter page

**Files:**
- Create: `site/src/styles/global.css`, `site/src/layouts/BaseLayout.astro`, `site/src/components/BuildNote.svelte`
- Modify: `site/src/pages/index.astro`

**Interfaces:**
- Produces: `BaseLayout` with props `{ title: string; description: string }` and a default slot inside `<main id="main">`. It loads tokens.css and fonts.css, preloads the Fraunces and Instrument Sans WOFF2 files, links the favicon, sets `lang="en"` and a skip link. M1 extends it (SEO head, nav, footer); M5 adds CSP.
- Produces: `.skip-link` class and the teal `:focus-visible` ring in `global.css`.

- [ ] **Step 1: Write `site/src/styles/global.css`**

```css
@import "../../../brand/tokens/tokens.css";
@import "../../../brand/fonts/web/fonts.css";

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  -webkit-text-size-adjust: 100%;
}

body {
  margin: 0;
  background: var(--color-paper);
  color: var(--color-ink);
  font-family: var(--font-text);
  font-size: var(--text-body);
  line-height: var(--text-body-lh);
}

a {
  color: var(--color-accent);
}

:focus-visible {
  outline: 2px solid var(--color-accent);
  outline-offset: 2px;
}

.skip-link {
  position: absolute;
  left: var(--space-4);
  top: var(--space-4);
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  color: var(--color-ink);
  border-radius: var(--radius-sm);
  transform: translateY(-200%);
}

.skip-link:focus-visible {
  transform: none;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- [ ] **Step 2: Write `site/src/layouts/BaseLayout.astro`**

```astro
---
import fraunces from "../../../brand/fonts/web/fraunces.woff2?url";
import instrumentSans from "../../../brand/fonts/web/instrument-sans.woff2?url";
import favicon from "../../../brand/logo/favicon.svg?url";
import "../styles/global.css";

interface Props {
  title: string;
  description: string;
}

const { title, description } = Astro.props;
---

<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="color-scheme" content="light dark" />
    <title>{title}</title>
    <meta name="description" content={description} />
    <link rel="icon" href={favicon} type="image/svg+xml" />
    <link rel="preload" href={fraunces} as="font" type="font/woff2" crossorigin />
    <link rel="preload" href={instrumentSans} as="font" type="font/woff2" crossorigin />
  </head>
  <body>
    <a class="skip-link" href="#main">Skip to content</a>
    <main id="main">
      <slot />
    </main>
  </body>
</html>
```

Check after the build that the preload `href` values equal the `url(...)` values in the built CSS (same hashed file). If Vite emits the font twice under different names, drop `?url` and preload by reading the built CSS path from `import.meta.glob("../../../brand/fonts/web/*.woff2", { query: "?url", import: "default", eager: true })`; record which one was used in the ledger.

- [ ] **Step 3: Write `site/src/components/BuildNote.svelte`** (server-rendered only, no client directive, so it ships no JavaScript; it proves the Svelte toolchain end to end)

```svelte
<script lang="ts">
  let { milestone }: { milestone: string } = $props();
</script>

<p class="t-label">Built on {milestone}</p>
```

- [ ] **Step 4: Replace `site/src/pages/index.astro`**

```astro
---
import BuildNote from "../components/BuildNote.svelte";
import BaseLayout from "../layouts/BaseLayout.astro";
---

<BaseLayout title="dins" description="Din’s portfolio is being built here.">
  <div class="starter">
    <h1 class="t-display">Hi, I’m Din.</h1>
    <p class="t-lead">This site is being built. Look closer soon.</p>
    <BuildNote milestone="M0" />
  </div>
</BaseLayout>

<style>
  .starter {
    max-width: var(--page-max);
    margin: 0 auto;
    padding: var(--space-9) var(--gutter);
  }
</style>
```

- [ ] **Step 5: Build and look**

Run: `pnpm --dir site build && pnpm --dir site serve`, open http://127.0.0.1:8787/ in light and dark
Expected: paper (light) or charcoal (dark) background, the Fraunces headline, the Instrument Sans lead in muted ink, the mono label "BUILT ON M0", the teal focus ring on Tab with the skip link appearing. Network panel: two preloaded WOFF2 files, JetBrains Mono fetched only when used, no JavaScript from the page. Din checks the look in the preview (Task 13); this step only confirms it renders. Stop the server.

- [ ] **Step 6: Commit**

```bash
git add site/src
git commit -m "feat(site): add the base layout and a starter page on the brand tokens"
```

---

### Task 7: Playwright with axe

**Files:**
- Create: `site/playwright.config.ts`
- Test: `site/tests/e2e/starter.spec.ts`

**Interfaces:**
- Consumes: `pnpm --dir site serve` (Task 2), the starter page (Task 6), `/api/health` (Task 3), `/ottie/` (Task 5).
- Produces for M1 to M5: `BASE_URL` env var points Playwright at any deployed site (no local server is started then); projects `chromium` only in M0 (M1 adds more if needed); the axe pattern in `starter.spec.ts` with tags `wcag2a`, `wcag2aa`, `wcag21aa`, `wcag22aa`.

- [ ] **Step 1: Write `site/playwright.config.ts`**

```ts
import { defineConfig, devices } from "@playwright/test";

const baseURL = process.env.BASE_URL ?? "http://127.0.0.1:8787";

export default defineConfig({
  testDir: "tests/e2e",
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  use: { baseURL, trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  // With BASE_URL set (a preview or production), test that site instead.
  webServer: process.env.BASE_URL
    ? undefined
    : {
        command: "pnpm serve",
        url: `${baseURL}/api/health`,
        reuseExistingServer: !process.env.CI,
        timeout: 60_000,
      },
});
```

- [ ] **Step 2: Write the test**

`site/tests/e2e/starter.spec.ts`:

```ts
import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

const AXE_TAGS = ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"];

for (const colorScheme of ["light", "dark"] as const) {
  test(`starter page has no axe violations in ${colorScheme}`, async ({ page }) => {
    await page.emulateMedia({ colorScheme });
    await page.goto("/");
    await expect(page.getByRole("heading", { level: 1 })).toHaveText("Hi, I’m Din.");
    const results = await new AxeBuilder({ page }).withTags(AXE_TAGS).analyze();
    expect(results.violations).toEqual([]);
  });
}

test("brand fonts load and the page logs no errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("console", (m) => m.type() === "error" && errors.push(m.text()));
  await page.goto("/");
  await page.evaluate(() => document.fonts.ready);
  expect(await page.evaluate(() => document.fonts.check('500 48px "Fraunces"'))).toBe(true);
  expect(await page.evaluate(() => document.fonts.check('400 16px "Instrument Sans"'))).toBe(true);
  expect(errors).toEqual([]);
});

test("text stays readable in the fallback when fonts are blocked", async ({ page }) => {
  await page.route("**/*.woff2", (route) => route.abort());
  await page.goto("/");
  const h1 = page.getByRole("heading", { level: 1 });
  await expect(h1).toBeVisible();
  const family = await h1.evaluate((el) => getComputedStyle(el).fontFamily);
  expect(family).toContain("Fraunces Fallback");
});

test("skip link moves focus to the main content", async ({ page }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  await page.keyboard.press("Enter");
  await expect(page).toHaveURL(/#main$/);
});

test("Ottie sheets and the health route are served", async ({ request }) => {
  const manifest = await request.get("/ottie/manifest.json");
  expect(manifest.ok()).toBe(true);
  expect(Object.keys((await manifest.json()).states)).toHaveLength(12);
  const sheet = await request.get("/ottie/idle.webp");
  expect(sheet.headers()["content-type"]).toBe("image/webp");
  const health = await request.get("/api/health");
  expect((await health.json()).ok).toBe(true);
});
```

- [ ] **Step 3: Install the browser and run**

Run: `pnpm --dir site exec playwright install chromium && pnpm --dir site test:e2e`
Expected: 6 passed. A failure here is a real defect in Tasks 2 to 6 (fix it there, then rerun); do not loosen the assertions.

- [ ] **Step 4: Commit**

```bash
git add site/playwright.config.ts site/tests/e2e
git commit -m "test(site): add Playwright with axe in light and dark"
```

---

### Task 8: The `rag/` uv project skeleton

**Files:**
- Create: `rag/pyproject.toml`, `rag/.python-version`, `rag/src/dins_rag/__init__.py`, `rag/src/dins_rag/paths.py`, `rag/README.md`, `pytest.ini`, `rag/uv.lock` (generated)
- Test: `rag/tests/test_paths.py`

**Interfaces:**
- Produces for M3: package `dins_rag` (import name), project name `dins-rag`; `dins_rag.paths.REPO_ROOT: Path`, `dins_rag.paths.SITE_ASK_DIR: Path` (`site/public/ask`). M3 adds dependencies, modules, `rag/evals/` and `rag/rag.toml`.
- Produces: `uv run --project rag pytest` works from the repo root (root `pytest.ini` points at `rag/tests`) and from `rag/`.

- [ ] **Step 1: Write `rag/pyproject.toml`**

```toml
[project]
name = "dins-rag"
version = "0.1.0"
description = "Ask Ottie's build-time pipeline: chunking, embeddings, the binary index and evals."
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = ["pytest~=9.1", "ruff~=0.17.1"]

[build-system]
requires = ["uv_build>=0.13,<0.14"]
build-backend = "uv_build"

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

- [ ] **Step 2: Write `rag/.python-version`** containing `3.12`, and `pytest.ini` at the repo root:

```ini
# Lets `uv run --project rag pytest` run from the repo root without collecting
# the brand tool tests, which need fontTools (check.sh runs those separately).
[pytest]
testpaths = rag/tests
```

- [ ] **Step 3: Write the failing test `rag/tests/test_paths.py`**

```python
from pathlib import Path

from dins_rag import paths


def test_repo_root_is_the_workspace_root():
    assert (paths.REPO_ROOT / "pnpm-workspace.yaml").is_file()


def test_index_goes_to_site_public_ask():
    assert paths.SITE_ASK_DIR.relative_to(paths.REPO_ROOT) == Path("site/public/ask")
```

- [ ] **Step 4: Run it to verify it fails**

Run: `uv run --project rag pytest`
Expected: uv creates `rag/.venv` and `rag/uv.lock`; the test FAILS with `ModuleNotFoundError: No module named 'dins_rag'`.

- [ ] **Step 5: Implement**

`rag/src/dins_rag/__init__.py`:

```python
"""Ask Ottie's build-time pipeline."""
```

`rag/src/dins_rag/paths.py`:

```python
"""Where the pipeline reads and writes, relative to the repo."""

from pathlib import Path

# rag/src/dins_rag/paths.py -> the repo root is three folders up.
REPO_ROOT = Path(__file__).resolve().parents[3]
SITE_ASK_DIR = REPO_ROOT / "site" / "public" / "ask"
```

`rag/README.md`:

```markdown
# rag

Ask Ottie's build-time pipeline (M3 fills it in). A uv project; Python 3.12 or later.

    uv run --project rag pytest
    uv run --project rag ruff check rag
```

- [ ] **Step 6: Run it to verify it passes, from both folders**

Run: `uv run --project rag pytest && (cd rag && uv run pytest)`
Expected: `2 passed` twice.

- [ ] **Step 7: Commit**

```bash
git add rag pytest.ini
git commit -m "feat(rag): add the uv project skeleton"
```

---

### Task 9: Prettier and ESLint at the root

**Files:**
- Create: `eslint.config.js`, `.prettierrc.json`, `.prettierignore`
- Modify: `package.json` (devDependencies), any files the formatter changes

**Interfaces:**
- Produces: `pnpm lint` and `pnpm format:check` from the root cover `site/` and the root config files. Markdown, `brand/`, `docs/` and `rag/` are not touched by Prettier (Ruff formats Python).

- [ ] **Step 1: Add the tooling**

Run: `pnpm add -D -w prettier@~3.9.10 prettier-plugin-astro@~1.1.1 prettier-plugin-svelte@~4.1.1 eslint@~10.13.0 @eslint/js@~10.0.1 typescript-eslint@~8.72.0 eslint-plugin-astro@~3.2.1 eslint-plugin-svelte@~3.23.1 globals@~17.13.0 svelte@catalog: typescript@catalog:`
Expected: root `package.json` lists them with `~` ranges (and `catalog:` for svelte and typescript, which the Svelte and TypeScript ESLint parsers need at the root under pnpm's strict layout).

- [ ] **Step 2: Write `.prettierrc.json`**

```json
{
  "printWidth": 100,
  "plugins": ["prettier-plugin-astro", "prettier-plugin-svelte"],
  "overrides": [{ "files": "*.astro", "options": { "parser": "astro" } }]
}
```

- [ ] **Step 3: Write `.prettierignore`**

```
# Generated, vendored or approved files
brand/
docs/
rag/
pnpm-lock.yaml
**/*.md
**/dist/
**/.astro/
**/.wrangler/
site/worker-configuration.d.ts
site/public/ottie/
site/public/ask/
site/playwright-report/
site/test-results/
```

- [ ] **Step 4: Write `eslint.config.js`**

```js
import js from "@eslint/js";
import astro from "eslint-plugin-astro";
import svelte from "eslint-plugin-svelte";
import { defineConfig } from "eslint/config";
import globals from "globals";
import tseslint from "typescript-eslint";

export default defineConfig(
  {
    ignores: [
      "**/dist/**",
      "**/.astro/**",
      "**/.wrangler/**",
      "**/node_modules/**",
      "brand/**",
      "docs/**",
      "rag/**",
      "site/worker-configuration.d.ts",
      "site/public/**",
      "site/playwright-report/**",
      "site/test-results/**",
    ],
  },
  js.configs.recommended,
  tseslint.configs.recommended,
  astro.configs.recommended,
  svelte.configs.recommended,
  {
    files: ["**/*.svelte", "**/*.svelte.ts"],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
  },
  { languageOptions: { globals: { ...globals.browser, ...globals.node } } },
);
```

- [ ] **Step 5: Format everything once and lint**

Run: `pnpm format && pnpm lint && pnpm format:check`
Expected: Prettier rewrites some files from earlier tasks (formatting only); ESLint reports 0 problems; `format:check` prints "All matched files use Prettier code style!". If ESLint flags a real issue in earlier code, fix the code, not the rule.

- [ ] **Step 6: Run the site tests again** (formatting must not change behaviour)

Run: `pnpm --dir site test`
Expected: 8 passed.

- [ ] **Step 7: Commit**

```bash
git add -A
git status --short   # check nothing unexpected is staged
git commit -m "build: add Prettier and ESLint for the workspace"
```

---

### Task 10: pre-commit with gitleaks, and the planted secret check

**Files:**
- Create: `.pre-commit-config.yaml`, `.gitleaks.toml`

**Interfaces:**
- Produces: hooks on every commit: basic file checks, Prettier, ESLint, Ruff (lint and format) and gitleaks on staged changes. Tool versions come from the lockfiles and mise, so hooks and `check.sh` never disagree.

- [ ] **Step 1: Write `.pre-commit-config.yaml`**

```yaml
# Install once per clone: pre-commit install
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-added-large-files
        args: ["--maxkb=600"]
      - id: check-merge-conflict
      - id: check-yaml
      - id: check-json
        exclude: \.jsonc$
      - id: end-of-file-fixer
        exclude: ^brand/
      - id: trailing-whitespace
        exclude: ^brand/|\.md$
  - repo: local
    hooks:
      - id: gitleaks
        name: gitleaks (staged changes)
        entry: gitleaks git --pre-commit --redact --staged --verbose
        language: system
        pass_filenames: false
      - id: prettier
        name: prettier
        entry: pnpm exec prettier --write --ignore-unknown
        language: system
        types_or: [javascript, ts, json, yaml, css, astro, svelte]
      - id: eslint
        name: eslint
        entry: pnpm exec eslint --fix --no-warn-ignored
        language: system
        files: \.(js|mjs|ts|astro|svelte)$
      - id: ruff-check
        name: ruff check
        entry: uv run --project rag ruff check --fix
        language: system
        types: [python]
      - id: ruff-format
        name: ruff format
        entry: uv run --project rag ruff format
        language: system
        types: [python]
```

The 600 KB limit lets an Ottie sheet (largest today 367 KB) through and stops accidental renders or models.

- [ ] **Step 2: Write `.gitleaks.toml`**

```toml
# Default gitleaks rules. Add narrow path allowlists here only for known test
# values (for example Cloudflare's published Turnstile test keys in M3).
[extend]
useDefault = true
```

- [ ] **Step 3: Install the hooks and run them on everything**

Run: `pre-commit install && pre-commit run --all-files`
Expected: every hook passes, or the fixers change files on the first run; then a second `pre-commit run --all-files` passes with no changes. If the Python hooks touch `brand/tools/*.py` files that predate M0, review the diff: formatting only is fine; anything else, revert it and add `exclude: ^brand/tools/(?!fonts)` to the two ruff hooks.

- [ ] **Step 4: Verify gitleaks blocks a planted secret** (never commit this file)

```bash
printf 'token = "ghp_%s"\n' "$(LC_ALL=C tr -dc 'A-Za-z0-9' </dev/urandom | head -c 36)" > leak-test.txt
git add leak-test.txt
git commit -m "test: planted secret" ; echo "exit=$?"
```

Expected: the gitleaks hook fails with a `github-pat` finding (value redacted) and `exit=1`; no commit is made (`git log -1` still shows the previous commit). Clean up:

```bash
git reset -q leak-test.txt && rm leak-test.txt && git status --short
```

Expected: `leak-test.txt` is gone and not staged. Record the result (rule id and exit code, never the value) for the ledger.

- [ ] **Step 5: Commit the hooks**

```bash
git add .pre-commit-config.yaml .gitleaks.toml
git commit -m "build: add pre-commit hooks with gitleaks"
```

Expected: the hooks run on this commit and pass.

---

### Task 11: `check.sh`

**Files:**
- Create: `check.sh` (executable)

**Interfaces:**
- Produces: `./check.sh` runs every check in order and stops at the first failure; `./check.sh --e2e` adds Playwright (using the build `check.sh` already made). Each step prints its time; the total must stay under 2 minutes without `--e2e`. Later milestones add steps (for example M3's retrieval evals, M4's JavaScript budget) by adding `step` lines.

- [ ] **Step 1: Write `check.sh`**

```bash
#!/usr/bin/env bash
# Every local check, in the order CI runs them. Usage: ./check.sh [--e2e]
set -euo pipefail
cd "$(dirname "$0")"

run_e2e=0
for arg in "$@"; do
  case "$arg" in
    --e2e) run_e2e=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

step() {
  local name="$1"
  shift
  local start=$SECONDS
  echo "==> $name"
  "$@"
  echo "    ok, $((SECONDS - start)) s"
}

py_files=(rag brand/tools/fonts.py brand/tools/test_fonts.py)
total=$SECONDS

step "secrets (gitleaks, full history)" gitleaks git --redact --no-banner .
step "format (prettier)" pnpm format:check
step "lint (eslint)" pnpm lint
step "python lint (ruff)" uv run --project rag ruff check "${py_files[@]}"
step "python format (ruff)" uv run --project rag ruff format --check "${py_files[@]}"
step "types (astro check, svelte-check)" pnpm --dir site check
step "site tests (vitest unit and worker)" pnpm --dir site test
step "rag tests (pytest)" uv run --project rag pytest
step "font tests (pytest)" uv run --no-project --with fonttools~=4.67 --with brotli --with pytest \
  pytest -q -p no:cacheprovider brand/tools/test_fonts.py
step "site build" pnpm --dir site build
if [ "$run_e2e" = 1 ]; then
  step "e2e (playwright, axe)" pnpm --dir site exec playwright test
fi

echo "All checks passed in $((SECONDS - total)) s."
```

The font tests import `fonts` from `brand/tools`; pytest's default rootdir insertion puts the test file's folder on `sys.path`, so this works from the repo root. If it does not, change the step to `(cd brand/tools && uv run ... pytest -q test_fonts.py)`.

- [ ] **Step 2: Make it executable and run it**

Run: `chmod +x check.sh && time ./check.sh`
Expected: every step prints `ok`, the last line is `All checks passed in N s.` with N under 120. If it is over, report the slowest steps to Din before moving anything to CI only.

- [ ] **Step 3: Run with e2e**

Run: `./check.sh --e2e`
Expected: also `e2e (playwright, axe)` ok, 6 tests passed.

- [ ] **Step 4: Run from another folder**

Run: `cd site && ../check.sh; cd ..`
Expected: the same result (the script changes to its own folder).

- [ ] **Step 5: Run on a fresh clone** (proves nothing depends on ignored local files)

```bash
tmp=$(mktemp -d) && git clone -q . "$tmp/dins" && cd "$tmp/dins" \
  && mise trust && mise install && pnpm install --frozen-lockfile && ./check.sh; cd - ; rm -rf "$tmp"
```

Expected: `All checks passed`. This is the only step allowed to delete what it created (`$tmp`).

- [ ] **Step 6: Commit**

```bash
git add check.sh
git commit -m "build: add check.sh to run every check"
```

---

### Task 12: GitHub Actions and Renovate

**Files:**
- Create: `.github/workflows/ci.yml`, `renovate.json`

**Interfaces:**
- Produces: CI jobs named `check` and `e2e` (stable names for required status checks); `e2e` uploads `playwright-report` on failure. No Cloudflare token in GitHub (PLAN.md Environments).
- Produces: Renovate PRs on Monday mornings, grouped; TypeScript held below 6.1 and Vitest below 5 until Din decides (Open question 1).

- [ ] **Step 1: Write `.github/workflows/ci.yml`**

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  check:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
        with:
          fetch-depth: 0 # gitleaks scans the full history
      - uses: jdx/mise-action@v5
      - run: pnpm install --frozen-lockfile
      - run: uv sync --project rag --locked
      - run: ./check.sh

  e2e:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v7
      - uses: jdx/mise-action@v5
      - run: pnpm install --frozen-lockfile
      - run: pnpm --dir site exec playwright install --with-deps chromium
      - run: pnpm --dir site test:e2e
      - if: failure()
        uses: actions/upload-artifact@v7
        with:
          name: playwright-report
          path: site/playwright-report
          retention-days: 7
```

`wrangler dev` in the e2e job runs fully locally and needs no Cloudflare login; there is no `.dev.vars` in CI, so `/api/health` reports `production` there, which the test does not check.

- [ ] **Step 2: Write `renovate.json`**

```json
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": ["config:recommended", ":semanticCommits"],
  "schedule": ["* 0-6 * * 1"],
  "rangeStrategy": "bump",
  "lockFileMaintenance": { "enabled": true, "schedule": ["* 0-6 * * 1"] },
  "packageRules": [
    {
      "groupName": "astro",
      "matchPackageNames": ["astro", "@astrojs/**", "prettier-plugin-astro", "eslint-plugin-astro"]
    },
    {
      "groupName": "svelte",
      "matchPackageNames": ["svelte", "svelte-check", "prettier-plugin-svelte", "eslint-plugin-svelte"]
    },
    {
      "groupName": "cloudflare",
      "matchPackageNames": ["wrangler", "@cloudflare/**"]
    },
    {
      "groupName": "test tools",
      "matchPackageNames": ["vitest", "@vitest/**", "@playwright/test", "@axe-core/playwright"]
    },
    {
      "groupName": "lint and format",
      "matchPackageNames": ["eslint", "@eslint/**", "typescript-eslint", "globals", "prettier"]
    },
    { "groupName": "python", "matchManagers": ["pep621"] },
    { "groupName": "toolchain", "matchManagers": ["mise", "nodenv"] },
    { "groupName": "github actions", "matchManagers": ["github-actions"] },
    {
      "description": "Major updates get their own PR and wait for Din's approval on the dashboard",
      "matchUpdateTypes": ["major"],
      "dependencyDashboardApproval": true
    },
    {
      "description": "Held: @astrojs/check, svelte-check and typescript-eslint do not support TypeScript 7 yet",
      "matchPackageNames": ["typescript"],
      "allowedVersions": "<6.1"
    },
    {
      "description": "Held at 4.1 until Din decides on Vitest 5 (see the M0 plan)",
      "matchPackageNames": ["vitest", "@vitest/**"],
      "allowedVersions": "<5"
    }
  ]
}
```

- [ ] **Step 3: Validate both files**

Run: `npx --yes --package renovate@latest -- renovate-config-validator renovate.json` (ask Din first: it downloads Renovate, about 100 MB; skip if Din says no and rely on Renovate's onboarding PR to validate) and `pre-commit run check-yaml --files .github/workflows/ci.yml`
Expected: "Config validated successfully" and the YAML check passes. The workflow itself is verified on the first push (Task 13).

- [ ] **Step 4: Commit**

```bash
git add .github renovate.json
git commit -m "ci: run check.sh and Playwright on every PR, add Renovate"
```

---

### Task 13: Workers Builds previews (Din in the dashboard) and the first preview link

Everything here waits for Din's go: pushing the branch, connecting Workers Builds and installing Renovate are outward-facing.

**Files:**
- Create: `docs/site/workers-builds.md`
- Modify: `site/wrangler.jsonc` (real D1 IDs, if Task 2 used the placeholder)

**Interfaces:**
- Produces: production Worker `dins-site` built from `main`; one Preview per branch at `<branch>-dins-site.<account-subdomain>.workers.dev` (Cloudflare's pattern `<preview-name>-<worker-name>.<subdomain>.workers.dev`), each on `dins-site-preview` and `SITE_ENV=preview`.

- [ ] **Step 1: Real D1 IDs**

If `site/wrangler.jsonc` still has the zero UUID, do Task 2 Step 7 now (with Din's OK), paste the IDs, run `pnpm --dir site test`, and commit: `git commit -am "build(site): point the D1 bindings at the real databases"`.

- [ ] **Step 2: Write `docs/site/workers-builds.md`** (the steps Din follows, and the checklist for later milestones)

```markdown
# Workers Builds setup

One-time setup by Din in the Cloudflare dashboard (Din is logged in; the `dins.dev` zone exists).

1. Workers and Pages, Create, Import a repository. Authorize the Cloudflare Workers and Pages GitHub app for the `dinsdev` organization, limited to the `dins.dev` repository.
2. Project name: `dins-site` (must match `name` in `site/wrangler.jsonc`).
3. Build settings:
   - Production branch: `main`
   - Root directory: `/` (the repo root, so pnpm sees the workspace lockfile)
   - Build command: `pnpm --dir site build`
   - Deploy command: `pnpm --dir site exec wrangler deploy`
   - Preview builds for non-production branches: on
   - Preview command: `pnpm --dir site exec wrangler preview`
   - Build variables: `PNPM_VERSION` = `12.14.0` (the image defaults to pnpm 10). Node comes from `.node-version`.
4. Save and deploy. The first production build deploys the starter page to `dins-site.<subdomain>.workers.dev`. The `dins.dev` custom domain is attached in M5.

Preview links: every push to a branch other than `main` builds a Preview at `<branch>-dins-site.<subdomain>.workers.dev`. Previews use the `previews` block in `site/wrangler.jsonc` (their own D1 and vars) and are public by default.

Preview secrets (M3 and later): `pnpm --dir site exec wrangler preview base-config secret put NAME` applies to every new Preview; `... preview secret put NAME --name <branch>` to one.

## Checking a preview

- `curl -s https://<branch>-dins-site.<subdomain>.workers.dev/api/health` shows `"env":"preview"`.
- `BASE_URL=https://<branch>-dins-site.<subdomain>.workers.dev pnpm --dir site exec playwright test` passes.
```

- [ ] **Step 3: Commit the doc**

```bash
git add docs/site/workers-builds.md
git commit -m "docs(site): add the Workers Builds setup and preview checklist"
```

- [ ] **Step 4: Ask Din to push and open the PR**

Ask Din: "M0 is ready. OK to push `feat/m0-foundation` and open a PR to `main`?" Only on yes: `git push -u origin feat/m0-foundation` and `gh pr create --base main --title "M0 Foundation" --body-file <summary>` (no attribution lines).
Expected: CI starts with jobs `check` and `e2e`.

- [ ] **Step 5: CI green**

Expected: both jobs pass on GitHub. If `check` takes much longer than locally, note the step times from the log for Din.

- [ ] **Step 6: Din connects Workers Builds**

Din follows `docs/site/workers-builds.md` steps 1 to 4 and pushes nothing new; then Claude (with Din's OK) pushes an empty commit to the branch to trigger a preview build: `git commit --allow-empty -m "chore: trigger the first preview build" && git push`.
Expected: the Workers Builds log shows Node 24 and pnpm 12.14.0, `astro build` succeeds and `wrangler preview` prints a Preview URL.

- [ ] **Step 7: Verify the preview**

Run: `curl -s https://feat-m0-foundation-dins-site.<subdomain>.workers.dev/api/health` (use the exact URL from the build log; branch names with `/` are normalized by Cloudflare) and `BASE_URL=<that URL> pnpm --dir site exec playwright test`
Expected: `{"ok":true,"service":"dins-site","env":"preview"}` and 6 Playwright tests pass against the preview. Din opens the link and checks the starter page in light and dark (the only visual sign-off in M0).

- [ ] **Step 8: Renovate**

Ask Din to install the Renovate GitHub app (Mend) on `dinsdev/dins.dev`. Expected: Renovate's onboarding PR lists the groups above; Din merges it or Claude closes it if `renovate.json` is already on `main`.

- [ ] **Step 9: Record the evidence**

Add a ledger entry (see "Doc updates to apply on merge") with: `check.sh` time, CI run links, the gitleaks result (rule id, exit 1), the preview URL and `/api/health` output, and anything that differed from this plan.

---

## Assumes (from other milestones)

- **M1** creates `site/src/content.config.ts` and the collections, the full SEO head in `BaseLayout` (canonical, social cards, structured data), nav and footer, the full icon set (`brand/logo/icons/*` into `public/`), `robots.txt`, `llms.txt`, `security.txt`, the 404, and replaces the starter copy. M0's starter text never reaches production after M1.
- **M2** reads `/ottie/manifest.json` and `/ottie/<state>.webp` as copied by `sync-brand.mjs` and owns the player in `site/src/ottie/`. If M2 needs the neutral still (`brand/reference/ottie-3d-neutral.webp`) under `/ottie/` too, M2 adds it to the `wanted` filter in `sync-brand.mjs` with a test. Long-term cache headers for `/ottie/*` are M2's or M5's (M0 adds no `_headers`).
- **M3** adds `scheduled` to `site/src/worker.ts`, D1 migrations in `site/migrations/` (the worker test setup already applies them), its vars and bindings in both the top level and `previews` of `wrangler.jsonc` (AI, rate limiting, `ASK_BACKEND`), `@anthropic-ai/sdk`, `rag/` modules and dependencies, and its steps in `check.sh` and CI. M3 writes `site/public/ask/`, which M0 leaves tracked.
- **M4** adds GSAP and the home JavaScript budget step (`pnpm --dir site budget`, per the M5 notes) to `check.sh`.
- **M5** owns security headers and CSP (`site/src/lib/security/headers.ts`, `_headers`), the custom domain, production secrets, required status checks on `main` and the uptime monitor (which can poll `/api/health`).
- Names other plans can rely on: Worker `dins-site`; D1 binding `DB`, databases `dins-site` and `dins-site-preview`; var `SITE_ENV`; CI jobs `check` and `e2e`; Playwright honours `BASE_URL`; Python package `dins_rag` with `dins_rag.paths.SITE_ASK_DIR`.

## Open questions for Din

1. **The Workers test package was renamed.** `@cloudflare/vitest-pool-workers` is deprecated on npm ("renamed to `@cloudflare/vitest-plugin`"); the new `@cloudflare/vitest-plugin` 1.4.6 supports Vitest 4.1 and 5. This plan uses `@cloudflare/vitest-plugin` and keeps Vitest 4.1 (no other change to the agreed stack; Renovate holds Vitest 5). The reason recorded in the ledger for pinning 4.1 no longer holds, so Vitest 5 could follow later as its own small upgrade. Recommendation: accept the package switch now, decide Vitest 5 after launch. The M3 plan session found the same thing.
2. **How previews get their own data.** Cloudflare's current mechanism is Worker Previews: a `previews` block in `wrangler.jsonc` (wrangler 4.135 or later), built by Workers Builds with `wrangler preview`, with redeclared vars and D1 per preview. The M5 notes assume a separate `env.preview` Worker instead. This plan uses the `previews` block (one Worker, branch-isolated Preview URLs, the documented path). Recommendation: keep `previews`; the M5 plan should adjust its runbook at merge.
3. **Fallback font names in the tokens.** Metric-matched fallbacks need a second family in each stack (`"Fraunces", "Fraunces Fallback", Georgia, ...`). Task 4 changes `brand/tokens/tokens.json` and regenerates `tokens.css`. The families and the brand rules do not change, but tokens are brand files, so this needs Din's OK and a ledger entry.
4. **Pinned font axes.** The web Fraunces is cut to SOFT 50, WONK 0 and weights 400 to 600 (headings 500, wordmark is SVG); Instrument Sans 400 to 600; JetBrains Mono 400 to 500. Any later need for another weight means rerunning `fonts.py`. The size budgets in `test_fonts.py` (80, 50 and 45 KB) are Claude's estimates from one measurement; Din may want different numbers.
5. **Production deploys before launch.** With Workers Builds connected, every merge to `main` deploys to `dins-site.<subdomain>.workers.dev` from M0 on. Recommendation: allow it (it is the real pipeline and has no custom domain until M5). The alternative is to leave production builds off until M5.
6. **Public previews.** Preview URLs are public by default; Cloudflare Access could require a sign-in. Recommendation: leave them public (public repo, fake answer backend on previews).
7. **pnpm 12.** pnpm 12.14 is the current release; the Workers Builds image defaults to pnpm 10.11, so the plan sets `PNPM_VERSION`. If Din prefers the more conservative pnpm 10 line, change `packageManager` and `mise.toml` before Task 2.

## Doc updates to apply on merge

- `docs/TASKS.md`: 2.10 to "Verified" once CI and the preview pass (Din sets Accepted after looking at the preview). Add rows for Din's one-time setup: "Connect Workers Builds" and "Install Renovate on `dinsdev/dins.dev`", status Done (Din) when done.
- `docs/site/PRD.md` section 5, Tooling row: "Vitest 4.1 (Cloudflare's Workers pool does not support 5 yet)" becomes "Vitest 4.1 with `@cloudflare/vitest-plugin` (the renamed Workers pool; Vitest 5 is a later upgrade)", if Din agrees to Open question 1.
- `docs/site/PLAN.md`: Repo layout shows `src/api/`; the routes live in `site/src/pages/api/` (Astro's convention, already in the shared contract). Environments table: Preview row "Workers Builds Preview per branch (`previews` block), preview D1 `dins-site-preview`".
- `docs/WORK_LEDGER.md`: a 2026-10 entry "M0 Foundation built" with the decisions (vitest-plugin, `previews` block, `session: false`, `imageService: "compile"`, fonts pinned axes and fallback names, custom `src/worker.ts`, root tooling with a pnpm catalog), the verification results from Task 13 Step 9, and Din's approvals.
- `AGENTS.md`: add a "Commands" section: `mise install`, `pnpm install`, `pre-commit install`, `pnpm --dir site dev`, `./check.sh` (`--e2e` for Playwright), `uv run --project rag pytest`; and to Layout: `site/`, `rag/`, `brand/fonts/web/` (generated by `brand/tools/fonts.py`).
- `README.md`: a short "Developing" section with the same commands (Task 4 already updates the fonts and licence lines).
- `docs/BRAND.md` Typography: note that the site uses subset WOFF2 files from `brand/fonts/web/` with metric-matched fallbacks, if Din accepts Open question 3.
