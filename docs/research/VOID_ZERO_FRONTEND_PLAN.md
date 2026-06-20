# Void Zero Toolchain – Research & Plan for TraceRTM Frontend

**Source**: [Gist – Migrate TypeScript Library to Void Zero Toolchain](https://gist.github.com/stooboo/9f8218eb05ee9dc12331b4c55e5827ad)  
**Scope**: Relevance to this codebase’s frontend (monorepo: apps + packages).

---

## 1. Gist summary

The gist describes migrating **TypeScript libraries** to a “Void Zero” toolchain:

| Tool     | Role                         | Gist recommendation      |
|----------|------------------------------|---------------------------|
| **TSDown** | Build + types (single tool) | Primary for libraries    |
| **Oxlint** | Lint                         | Optional (replace ESLint) |
| **Vitest** | Test                         | Optional (replace Jest)   |
| **Rolldown** | Advanced bundling            | Fallback if needed       |
| **Vite** | Legacy app/build             | Fallback                  |

Goals: 5–10× faster builds, 100× faster lint (with Oxlint), one tool for JS + declarations (TSDown).

**Important**: The guide is aimed at **libraries** (single/multi entry → `dist/` with ESM/CJS + `.d.ts`), not at full applications.

---

## 2. Current frontend setup (brief)

- **Layout**: Turbo monorepo; `apps/*` (web, docs, storybook, desktop), `packages/*` (api-client, config, env-manager, state, types, ui).
- **Root**: Oxlint, Oxfmt, Biome (optional), Stylelint, Vite 8 beta, Vitest 3, TypeScript 5.7.
- **Apps**:
  - **web**: Vite dev/build, Vitest, Playwright.
  - **docs**: Next.js (webpack under the hood).
  - **desktop**: electron-vite.
  - **storybook**: Storybook + Vite.
- **Packages**: All use `tsc --build` in script; **consumption is source-based** (`main`/`types`/`exports` point to `./src/...`), no `dist/` in the critical path for local dev.

So: **apps** are classic app stacks (Vite/Next/electron-vite). **Packages** are internal libraries consumed as TypeScript source via workspaces.

---

## 3. Relevance to this codebase

### 3.1 Already aligned

- **Oxlint**: Root lint is `oxlint .` — matches gist.
- **Vitest**: Used in `apps/web` and `packages/env-manager` — matches gist.
- **TypeScript**: Single, modern tsconfig; `moduleResolution: "bundler"`, strict — consistent with gist.

No change required for lint or test strategy to “match” the gist.

### 3.2 Apps (web, docs, desktop, storybook)

- **Not in scope for the gist**: It targets **library** build (dist with ESM/CJS + types), not app dev/serve/bundle.
- **Recommendation**: Keep current stack (Vite, Next.js, electron-vite, Storybook). Do **not** replace app bundlers with TSDown/Rolldown for the apps themselves.

### 3.3 Packages (api-client, config, env-manager, state, types, ui)

- **Current**: `tsc --build`; packages expose **source** (`./src/index.ts` etc.) to the monorepo; no published `dist/`.
- **Gist**: TSDown/Rolldown are for building **dist/** (ESM + CJS + `.d.ts`) for libraries.
- **Relevance**:
  - **If we keep source-based consumption**: Void Zero (TSDown/Rolldown) is **optional**; we could try it for speed or consistency but it’s not required.
  - **If we ever publish a package or move to dist-based consumption**: TSDown (or Rolldown) would be the right direction per the gist.

---

## 4. Recommended plan

### 4.1 Do nothing for apps

- Keep Vite for web/desktop/storybook, Next.js for docs.
- No migration of app build to TSDown/Rolldown.

### 4.2 Optional: pilot TSDown on one package

- **Goal**: Validate “Void Zero” library build (and possibly faster typecheck/build) in this repo.
- **Candidate**: Smallest, leaf package, e.g. `packages/types` or `packages/config`.
- **Steps** (aligned to gist, adapted to monorepo):
  1. In that package only: add `tsdown`, add `tsdown.config.js` (entry = `src/index.ts`, outDir = `dist`, format ESM+CJS, dts = true).
  2. Add `build` script: `tsdown` (and keep or remove `tsc --build` after validation).
  3. Point `main`/`module`/`types` and `exports` to `dist/` when using TSDown.
  4. In Turbo, keep `build` task outputs as `dist/**` so cache and dependents still work.
  5. Run `turbo build` and full frontend quality pipeline; fix any consumer imports if they assume source paths.
- **Decision**: If the pilot is successful and we want consistency, roll out TSDown to other packages; otherwise leave the rest on `tsc --build` and source exports.

### 4.3 Lint and test

- **Lint**: Keep Oxlint at root; no migration needed.
- **Test**: Keep Vitest where it’s already used; no migration needed.

### 4.4 Rolldown / Vite fallback

- **Rolldown**: Consider only if a package has complex bundling needs (e.g. many entry points, special plugins) that TSDown doesn’t cover.
- **Vite**: Already used for apps; no need for a separate “legacy library build” unless we explicitly want a Vite-based library build path.

---

## 5. Phased plan (DAG-friendly)

| Phase | Task | Depends on | Outcome |
|-------|------|------------|--------|
| 1 | Document current package build and consumption (source vs dist) | — | Clear baseline |
| 2 | (Optional) Add TSDown to one package (e.g. `types` or `config`), wire `build` and `exports` to `dist/` | Phase 1 | Pilot passing `turbo build` |
| 3 | (Optional) Run full frontend quality (lint, typecheck, test, build) and fix regressions | Phase 2 | Green pipeline |
| 4 | (Optional) Decide: roll out TSDown to other packages or revert pilot and keep `tsc` + source | Phase 3 | Decision and optional rollout |

---

## 6. Success criteria (if we adopt TSDown for packages)

- Build of the migrated package(s) succeeds with TSDown.
- `turbo build` and root `bun run build` still pass.
- No regression in lint (Oxlint) or test (Vitest/Playwright).
- If we switch to dist-based consumption, app builds and dev still resolve the package correctly.

---

## 7. References

- Gist: [Migrate TypeScript Library to Void Zero Toolchain](https://gist.github.com/stooboo/9f8218eb05ee9dc12331b4c55e5827ad)
- TSDown: single-tool build + types for TS libraries.
- Current frontend: `frontend/package.json`, `frontend/turbo.json`, `frontend/packages/*/package.json`.
