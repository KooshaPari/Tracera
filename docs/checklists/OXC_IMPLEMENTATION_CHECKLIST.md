# OXC / Oxlint Implementation Checklist

Use this checklist to verify and maintain the full OXC (Oxidation Compiler) setup: parser, resolver, multi-file analysis, and type-aware linting. Reference: [OXC Quick Reference](../reference/OXC_QUICK_REFERENCE.md).

## 1. Dependencies

- [ ] From repo root: `cd frontend && bun install`
- [ ] Confirm `oxlint` and `oxlint-tsgolint` in `frontend/package.json` devDependencies
- [ ] Confirm `oxfmt` in devDependencies (formatting)

## 2. Config files

- [ ] `frontend/.oxlintrc.json` exists with:
  - [ ] `$schema` pointing to `./node_modules/oxlint/configuration_schema.json`
  - [ ] `plugins` includes at least: `eslint`, `typescript`, `unicorn`, `oxc`, `import`
  - [ ] Multi-file: `import/no-cycle` (e.g. `["error", { "maxDepth": 3 }]`) and at least one other `import/*` rule
  - [ ] Type-aware rules under `typescript/*` (e.g. `typescript/no-floating-promises`, `typescript/no-unsafe-assignment`)
  - [ ] `ignorePatterns` for `node_modules`, `dist`, `.turbo`, generated files
- [ ] `frontend/apps/web/.oxlintrc.json` exists and extends `../../.oxlintrc.json` (or equivalent)

## 3. Scripts (frontend/package.json)

- [ ] `lint` → `oxlint .`
- [ ] `lint:fix` → `oxlint --fix .`
- [ ] `lint:report-unused-disable` → `oxlint --report-unused-disable-directives .`
- [ ] `typecheck` → `oxlint --type-check --type-aware .`
- [ ] `typecheck:type-aware-only` → `oxlint --type-aware .` (type-aware rules only, no TS errors)
- [ ] `typecheck:report-unused-disable` → `oxlint --type-check --type-aware --report-unused-disable-directives .`
- [ ] `format` → `oxfmt .`
- [ ] `format:check` → `oxfmt --check .`
- [ ] `quality` runs lint, lint:stylelint, typecheck, build, test

## 4. Multi-file analysis

- [ ] `import` plugin enabled in `.oxlintrc.json`
- [ ] At least one `import/*` rule configured (e.g. `import/no-cycle`, `import/no-duplicates`)
- [ ] From `frontend/`: `bun run lint` completes without errors (or known baseline)
- [ ] TypeScript path aliases: `tsconfig.json` has `compilerOptions.paths`; oxlint discovers it automatically for `import/*` rules

## 5. Type-aware linting

- [ ] `oxlint-tsgolint` installed in frontend
- [ ] From `frontend/`: `bun run typecheck` runs `oxlint --type-check --type-aware .`
- [ ] If slow or OOM: run `OXC_LOG=debug bun run typecheck` and check "Program created with N source files"; fix tsconfig `include`/`exclude` so N is reasonable (hundreds, not tens of thousands)
- [ ] Monorepos: run `bun run build` (or build referenced packages) before typecheck so `.d.ts` exist

## 6. Makefile integration

- [ ] `make lint-frontend` runs `cd frontend && bun run lint` (oxlint)
- [ ] `make quality-frontend` runs `cd frontend && bun run quality` (lint + typecheck + build + test)
- [ ] `make quality-fe-lint` → `cd frontend && bun run lint`
- [ ] `make quality-fe-type` → `cd frontend && bun run typecheck`

## 7. Verification commands

Run from repo root:

```bash
# Lint only (no type-aware)
make lint-frontend
# or: cd frontend && bun run lint

# Typecheck (type-aware + type errors)
make quality-fe-type
# or: cd frontend && bun run typecheck

# Format check
cd frontend && bun run format:check

# Full frontend quality
make quality-frontend
# or: cd frontend && bun run quality
```

## 8. Troubleshooting

- **Lint fails:** Run `cd frontend && bun run lint:fix`; fix remaining issues by rule.
- **Type-aware slow/hangs:** See [OXC Quick Reference — Type-aware: performance and troubleshooting](../reference/OXC_QUICK_REFERENCE.md#type-aware-performance-and-troubleshooting-deep). Narrow tsconfig `include`/`exclude`; run `oxlint --type-aware ./apps/web` from `frontend/` to limit scope.
- **Unused disable comments:** Run `bun run lint:report-unused-disable` or `bun run typecheck:report-unused-disable` and remove or fix disables.

## 9. CI

- [ ] CI runs frontend lint and typecheck (e.g. `cd frontend && bun run lint && bun run typecheck` or `make quality-frontend`).
- [ ] If type-aware is too slow in CI, run `oxlint .` only (no `--type-aware`) until tsconfig/tooling is optimized; then re-enable.

## 10. Remediation (optional)

If `bun run lint` or `bun run typecheck` report many errors:

- Run `bun run lint:fix` to auto-fix safe issues.
- Use [docs/guides/FRONTEND_OXLINT_IMPLEMENTATION_GUIDE.md](../guides/FRONTEND_OXLINT_IMPLEMENTATION_GUIDE.md) if present for phased remediation.
- Narrow scope temporarily: `oxlint ./apps/web` or adjust `.oxlintrc.json` overrides for tests/storybook.
