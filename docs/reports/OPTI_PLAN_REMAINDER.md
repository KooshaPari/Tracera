# Opti Plan Remainder

**Date**: 2026-01-31  
**Context**: Post graph-performance / consolidation work; items left to close the “opti plan” loop.

---

## Summary

| Item | Description | Status |
|------|-------------|--------|
| **Story 10** | Task #10 (DocIndex test coverage) is **completed** (`.trace/task-10-test-coverage.md`). If “Story 10” refers to a different backlog story (e.g. “Fix Swagger bundling” or another #10), track it in your backlog. | Clarify which story |
| **Swagger bundling** | Production build failed due to `swagger-ui-react` (or its deps) requesting `lodash-es/fp/assocPath` and `lodash-es/fp/set`; `lodash-es` does not ship an `fp` build. | **Done** (lodash + Vite aliases; see below) |

---

## 1. Story 10

- **Task #10 (DocIndex test coverage)**  
  - Completed. See `.trace/task-10-test-coverage.md` (105 tests, 45.3% coverage, parser ~90%).
- If “Story 10” means something else (e.g. a Jira/Linear story, or “Story 10: Fix Swagger bundling”), treat that as the remaining story and mark it done when Swagger bundling is fixed.

---

## 2. Swagger bundling

**Problem**

- Build error:
  - `[UNLOADABLE_DEPENDENCY] Error: Could not load lodash-es/fp/assocPath`
  - `[UNLOADABLE_DEPENDENCY] Error: Could not load lodash-es/fp/set`
- Cause: A dependency (e.g. from `swagger-ui-react`) resolves `lodash` → `lodash-es` via Vite alias, then requests `lodash-es/fp/*`. The installed `lodash-es` does not provide an `fp` subpath.

**Fix (implemented)**

- Added `lodash` as a dependency in `frontend/apps/web/package.json` (so `lodash/fp/*` exists).
- In `frontend/apps/web/vite.config.mjs`:
  - Preserve `lodash/fp/*` (rule first) so the general `lodash` → `lodash-es` alias does not rewrite it.
  - Alias `lodash-es/fp/assocPath` and `lodash-es/fp/set` (and `lodash-es/fp/*`) → `lodash/fp/*`.
- Also fixed `prop-types-shim.ts`: added `checkPropTypes` export so `react-tabs` (and other deps) resolve; build now completes with `bun run build:fast`.

**Alternatives (if needed later)**

- Replace `swagger-ui-react` with an ESM-native API docs component (e.g. `@scalar/api-reference`) per `.trace/CJS_ESM_INTEROP_ANALYSIS.md`.
- Or pre-bundle `swagger-ui-react` in `optimizeDeps.include` and ensure its dependency tree can resolve (may still require the fp aliases above).

---

## 3. Other remainder (from session summary)

- **TypeScript**: Many pre-existing TS errors across the repo (e.g. `exactOptionalPropertyTypes`, index signatures, missing modules). Unrelated to graph perf or Swagger; address in a dedicated pass.
- **Storybook**: Migration / dependency issues; `turbo build` excludes Storybook; use `build:storybook` when Storybook is needed.

---

## Next steps

1. **Story 10**: Confirm whether it’s Task #10 (done) or another story; if another, add to backlog and link to “Swagger bundling” if they’re the same.
2. **Swagger bundling**: Apply the Vite + lodash fix, run `bun run build:fast` (or full build), and confirm the UNLOADABLE_DEPENDENCY errors are gone.
3. **TypeScript / Storybook**: Plan separately when prioritised.
