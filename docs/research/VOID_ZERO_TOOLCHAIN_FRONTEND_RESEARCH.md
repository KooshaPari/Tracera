# Void Zero Toolchain – Research & Plan for Frontend

**Source:** [Gist: Migrate TypeScript Library to Void Zero Toolchain](https://gist.github.com/stooboo/9f8218eb05ee9dc12331b4c55e5827ad)  
**Scope:** `frontend/` monorepo (apps + packages).  
**Date:** 2025-02-02.

---

## 1. Gist summary

The gist describes migrating a **TypeScript library** to the “Void Zero” toolchain:

| Tool     | Role in gist                         | Expected benefit              |
|----------|--------------------------------------|-------------------------------|
| **TSDown** | Primary: **build + TypeScript declarations** for libraries (one tool) | 5–10× faster builds, single command |
| **Oxlint** | Linting (optional migration from ESLint) | ~100× faster linting           |
| **Vitest** | Testing (optional, can keep existing)    | —                             |
| **Vite**   | Legacy fallback for apps / dev         | —                             |
| **Rolldown** | Optional advanced bundling             | When Vite isn’t enough        |

**Main idea:** For **libraries**, use **TSDown** for both JS bundling and `.d.ts` emission instead of separate bundler + `tsc`/declaration steps.

---

## 2. Current frontend setup (auto-analysis)

### 2.1 Structure

- **Monorepo:** Turbo, Bun, workspaces `apps/*`, `packages/*`.
- **Apps:** `web`, `docs`, `storybook`, `desktop` (Vite for dev/build where applicable).
- **Packages:** `@tracertm/ui`, `@tracertm/api-client`, `@tracertm/state`, `@tracertm/types`, `@tracertm/config`, `@tracertm/env-manager`.

### 2.2 Current tools

| Concern   | Current tool(s)        | Notes                                      |
|-----------|------------------------|--------------------------------------------|
| **Lint**  | Oxlint, oxfmt, Biome, Stylelint | Oxlint already in use (Void Zero aligned). |
| **Test**  | Vitest (apps), Playwright (e2e) | Vitest already in use.                     |
| **App build** | Vite 8 (e.g. `apps/web`: `tsc --build && vite build`) | No change suggested by gist for apps.      |
| **Package build** | `tsc --build` only       | No dist/; packages expose **source** (`main`/`types`/`exports` → `./src/index.ts`). |

### 2.3 Package consumption model

- All listed packages use **source-based** consumption:
  - `"main": "./src/index.ts"`, `"types": "./src/index.ts"`, `"exports": { ".": "./src/index.ts" }`.
- No `dist/` or published tarballs; apps (and other packages) resolve workspace packages as TypeScript source; **Vite bundles** everything at app level.
- So today: **no library “build product”**; only `tsc --build` for typecheck/emit where needed (e.g. project references).

### 2.4 Entry points and config

- **Apps:** e.g. `apps/web`: Vite entry, TanStack Router, React, Vitest, Playwright.
- **Packages:** entry = `src/index.ts` (and/or component subpaths for UI).
- **TypeScript:** Root `tsconfig.json` with `noEmit: true`, project references to packages; packages have their own `tsconfig.json`.

---

## 3. Relevance to this codebase

### 3.1 Already aligned with the gist

- **Oxlint** for linting (and oxfmt for format) → no migration needed.
- **Vitest** for unit/integration tests → no migration needed.
- **Vite** for app dev/build → gist keeps Vite as legacy/primary for apps; no change required.

### 3.2 Where the gist applies: **library build** (packages)

- The gist is aimed at **TypeScript libraries** that **produce a built artifact** (e.g. `dist/` with ESM, CJS, and `.d.ts`).
- **Current frontend:** Packages do **not** produce such artifacts; they are consumed as source. So:
  - **TSDown is optional** for this repo unless you:
    - Plan to **publish** packages to npm (or another registry), or
    - Want **pre-built dist/** for faster installs/CI or for consumers that don’t use a TypeScript-aware bundler.

### 3.3 Rolldown

- Rolldown is suggested for “advanced” or “complex” bundling.
- Current app bundling is Vite (Rollup under the hood). Rolldown would only be relevant if you decide to replace Vite for app builds (e.g. for speed); **not required** by the gist for your current setup.

---

## 4. Recommended plan (phased)

### Phase 1: Document and keep current setup (no code change)

- **Action:** Treat this doc as the single place for “Void Zero vs our frontend” decisions.
- **Outcome:** Clear mapping: we already use Oxlint + Vitest + Vite; TSDown/Rolldown are optional and conditional.

### Phase 2: Optional – introduce TSDown only if you need library builds

**Trigger:** You decide to either **publish** any of `@tracertm/*` or **ship dist/** (e.g. for faster CI or non-TS consumers).

**Steps (per the gist, adapted to this repo):**

1. **Per-package (e.g. `packages/ui`, `packages/api-client`):**
   - Add **TSDown** and use it as the single tool for:
     - Bundling (ESM/CJS) and
     - Emitting `.d.ts`.
   - Add a minimal `tsdown.config.ts` (or equivalent) per package; keep existing `tsconfig.json` for editor/typecheck or simplify as needed.
2. **Package.json (per package):**
   - Replace `"build": "tsc --build"` with a TSDown-based build (e.g. `tsdown` or `bun run build` that runs TSDown).
   - Point `main`/`types`/`exports` to `dist/` outputs (e.g. `./dist/index.js`, `./dist/index.d.ts`) instead of `./src/index.ts`.
3. **Root/CI:**
   - Keep Turbo; ensure `turbo build` runs the new package build scripts.
   - Keep app builds as-is (`tsc --build && vite build` for `apps/web` etc.).

**Do not:**

- Migrate **apps** off Vite to TSDown (gist targets **libraries**; apps stay on Vite).
- Add Rolldown unless you have a concrete need to replace Vite for app bundling.

### Phase 3: Optional – Rolldown only if replacing Vite for apps

- **Trigger:** You need faster or different app bundling and decide to try Rolldown instead of Vite.
- **Scope:** App build only (e.g. `apps/web`); not required by the gist for your current architecture.

---

## 5. Success criteria (from gist, mapped to us)

| Criterion | Current / after Phase 1 | After Phase 2 (if applied) |
|-----------|--------------------------|-----------------------------|
| Oxlint for linting | ✅ Already | ✅ |
| Vitest for tests | ✅ Already | ✅ |
| Vite for app build | ✅ Already | ✅ |
| Single build command for packages | N/A (source-only) | ✅ TSDown one command |
| Package exports ESM + CJS + .d.ts | N/A (source-only) | ✅ If you adopt TSDown |
| 5–10× faster **library** build | N/A | ✅ If you adopt TSDown |
| Lint &lt; 50 ms (Oxlint) | ✅ Already | ✅ |

---

## 6. Decision matrix

| Question | Recommendation |
|----------|----------------|
| Migrate app build (Vite → Rolldown)? | **No** – keep Vite for apps. |
| Migrate lint to Oxlint? | **Done** – already using Oxlint. |
| Migrate tests to Vitest? | **Done** – already using Vitest. |
| Add TSDown for packages? | **Only if** you publish or ship `dist/`; otherwise keep source-only + `tsc --build`. |
| Add Rolldown? | **Only if** you later decide to replace Vite for app bundling. |

---

## 7. Rolldown and @vitejs/plugin-react-swc

### 7.1 Rolldown (full app dev/build)

**Yes – Rolldown is meant to improve frontend dev and build speed.** When Vite uses Rolldown for the full pipeline (not just deps), you get faster cold start and HMR (dev) and faster production bundles.

**Current state:** Vite 8 already uses Rolldown for **deps optimization** (`optimizeDeps` → `rolldownOptions: {}` in `apps/web/vite.config.mjs`). The rest of the pipeline (dev transform, production bundle) is still esbuild/Rollup.

**Recommendation:**

- **Short term:** Stay on Vite 8 as-is. You already get Rolldown for pre-bundling deps.
- **When to go further:** When **Rolldown Vite** (or Vite’s full Rolldown mode) is stable and your plugins are compatible (TanStack Router, Sentry, image optimizer, etc.), try it in a branch. Then switch if dev/build times improve and nothing breaks.

### 7.2 @vitejs/plugin-react-swc

**plugin-react-swc** replaces Babel with SWC in dev; in production it uses SWC + Oxc (or Oxc only). That gives faster transforms and often faster cold start and HMR, especially with custom plugins that have an SWC equivalent.

**Current state:** `apps/web` uses **@vitejs/plugin-react** (Babel) so it can use **React Compiler** (`babel-plugin-react-compiler`) when `ENABLE_REACT_COMPILER === "true"` in production. React Compiler is Babel-only today.

**Recommendation:**

| If you… | Then |
|--------|------|
| **Want to keep React Compiler** | Stay on **@vitejs/plugin-react** (Babel) until React Compiler has an SWC plugin or you drop the compiler. |
| **Don’t need React Compiler** (or it’s optional) | Switch to **@vitejs/plugin-react-swc** for faster dev and prod transforms; you lose React Compiler unless/until there’s an SWC version. |

So: **Use plugin-react-swc if you’re okay without React Compiler** (or only use it in a separate Babel-based build). **Stay on plugin-react if React Compiler is required.**

---

## 8. Vite Performance Guide (Lightning CSS and other techniques)

**Source:** [Vite – Performance](https://main.vite.dev/guide/performance) (and [Markdown version](https://main.vite.dev/guide/performance.md)).

The following items are added to the plan so the frontend can adopt them where relevant.

### 8.1 Browser and dev server

| Technique | Action / status |
|-----------|------------------|
| **Dev profile** | Use a browser profile without extensions (or incognito) when running Vite dev to avoid slow startup/reload. |
| **Disable cache** | Do **not** enable “Disable cache” in DevTools while using the Vite dev server; it hurts startup and full reload. |

### 8.2 Plugin audit

| Technique | Action / status |
|-----------|------------------|
| **Dynamic import for heavy plugins** | Lazy-load large dependencies used only in certain cases to reduce Node startup time (see [vite-plugin-react#212](https://github.com/vitejs/vite-plugin-react/pull/212), [vite-pwa#224](https://github.com/vite-pwa/vite-pwa/pull/244)). |
| **Fast config hooks** | Avoid long work in `buildStart`, `config`, and `configResolved`; they block dev server startup. |
| **Lean transform hooks** | In `resolveId` / `load` / `transform`, do cheap checks (e.g. keyword in `code`, extension in `id`) before full transform. |
| **Profiling** | Use `vite --profile`, then `p + enter` in the terminal to record a `.cpuprofile`; inspect with [speedscope](https://www.speedscope.app). |
| **Transform timing** | Use `vite --debug plugin-transform` or [vite-plugin-inspect](https://github.com/antfu/vite-plugin-inspect) to see which transforms are slow. |

### 8.3 Resolve and imports

| Technique | Action / status |
|-----------|------------------|
| **Explicit import paths** | Prefer `import './Component.jsx'` (or `.tsx`) instead of `import './Component'` to cut down resolve filesystem checks. |
| **TypeScript** | Use `"moduleResolution": "bundler"` and `"allowImportingTsExtensions": true` so you can use `.ts`/`.tsx` in imports. **Current:** ✅ Already set in root `tsconfig.json`. |
| **resolve.extensions** | Optionally narrow the list if your codebase doesn’t need all defaults; must still work for `node_modules`. |

### 8.4 Barrel files

| Technique | Action / status |
|-----------|------------------|
| **Avoid barrel files** | Prefer `import { slash } from './utils/slash.js'` over `import { slash } from './utils'` so only needed files are loaded and transformed. Add to coding guidelines; refactor hot paths if needed. |

### 8.5 Warmup

| Technique | Action / status |
|-----------|------------------|
| **server.warmup** | Pre-transform frequently used files via [`server.warmup.clientFiles`](https://main.vite.dev/config/server-options#server-warmup) so they’re ready on first request. **Current:** ✅ `apps/web/vite.config.mjs` already uses `warmup`. |
| **server.open / --open** | Use `server.open` or `vite --open` so Vite warms up the entry (or opened URL). |

### 8.6 Lesser / native tooling (Lightning CSS and related)

| Technique | Action / status |
|-----------|------------------|
| **CSS instead of Sass/Less/Stylus** | Use plain CSS when possible; nesting can be handled by PostCSS or Lightning CSS. **Current:** ✅ Vite apps use Tailwind + Lightning CSS; no Sass/Less/Stylus. |
| **Lightning CSS** | Vite’s Lightning CSS support for faster CSS parsing/transforms and modern features. **Done:** ✅ `apps/web` and `apps/desktop` (renderer) use `css.transformer: "lightningcss"`, `build.cssMinify: "lightningcss"`, and `@tailwindcss/vite` (no PostCSS). `apps/docs` (Next.js) remains on PostCSS. |
| **SVGs** | Import SVGs as URLs or strings instead of transforming them into React/Vue components, to reduce transform work. **Plan:** Prefer `import iconUrl from './icon.svg?url'` (or `?raw`) unless you need component API. |
| **@vitejs/plugin-react without Babel** | If you use `@vitejs/plugin-react`, avoid Babel options when possible so the build uses only Oxc and stays fast. **Current:** Babel is used only for React Compiler when `ENABLE_REACT_COMPILER === "true"`; otherwise consider `@vitejs/plugin-react-swc` (see §7.2). |

### 8.7 Plan summary (what to do)

- **Already in place:** TypeScript `moduleResolution`/`allowImportingTsExtensions`, Tailwind + Lightning CSS in Vite apps (`apps/web`, `apps/desktop` renderer), `server.warmup` and `resolve.extensions` in `apps/web`, no PostCSS in Vite apps.
- **Add to backlog / evaluate:** Explicit import extensions in hot paths, reduce barrel usage, plugin lazy-loading and transform cost.
- **Optional tooling:** `vite --profile`, `vite --debug plugin-transform`, vite-plugin-inspect for profiling and tuning.
- **Note:** `apps/docs` (Next.js) uses PostCSS + Tailwind; Lightning CSS applies only to Vite-based builds.

---

## 9. References

- Gist: [Migrate any TypeScript Library to the Void Zero Toolchain](https://gist.github.com/stooboo/9f8218eb05ee9dc12331b4c55e5827ad)
- Frontend root: `frontend/` (Turbo, Bun, Oxlint, Vite, Vitest)
- Packages: `frontend/packages/*` (source-only; `tsc --build`)
- Apps: `frontend/apps/web`, `docs`, `storybook`, `desktop`
