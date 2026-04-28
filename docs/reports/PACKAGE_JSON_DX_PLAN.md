# Package.json run scripts – research, audit, and plan

**Source:** `../../clean/deploy/atoms.tech` (atoms.tech)  
**Target:** Trace root `package.json` and developer experience.

---

## 1. Research – atoms.tech script inventory

atoms.tech is a single-app Next.js + Supabase + Vitest + Playwright repo. Scripts are grouped by concern and use consistent naming.

### 1.1 Dev

| Script | Command | Purpose |
|--------|---------|--------|
| `dev` | `bunx next dev` | Start Next dev server |
| `dev:server` | `bunx tsx server.ts` | Custom server |
| `dev:log` | `bun run dev 2>&1 \| tee -a logs/server.log` | Dev with log capture |
| `dev:clean` | `rm -rf .next && bunx next dev` | Clean build + dev |
| `dev:functions:setup` | `bash scripts/setup-edge-function-secrets.sh` | Edge function setup |
| `dev:functions` | env + `bunx supabase functions serve ...` | Serve one function |
| `dev:functions:all` | `bunx supabase functions serve --no-verify-jwt` | Serve all functions |

### 1.2 Build / start

| Script | Command |
|--------|---------|
| `build` | `bunx next build` |
| `build:analyze` | `ANALYZE=true bunx next build` |
| `start` | `bunx next start` |

### 1.3 Database (Supabase)

| Script | Command |
|--------|---------|
| `migrate` | `bunx supabase migration up` |
| `db:migrate` | same |
| `db:status` | echo cloud URL |
| `db:schema` … `db:indexes` | echo links to Supabase UI |
| `db:dump:schema` | echo `bunx supabase db pull` |

### 1.4 Lint

| Script | Command |
|--------|---------|
| `lint` | `bunx eslint .` |
| `lint:strict` | `bunx eslint . --max-warnings=0` |
| `lint:fix` | `bunx eslint . --fix` |

### 1.5 Type-check

| Script | Command |
|--------|---------|
| `type-check` | `bunx tsgo --noEmit --skipLibCheck` |
| `type-check:full` | `bunx tsgo --noEmit` |
| `type-check:files` | `bun run scripts/type-check-files.ts` |
| `type-check:skip` | echo skip message |

### 1.6 Format

| Script | Command |
|--------|---------|
| `format` | `bunx prettier --write .` |
| `format:check` | `bunx prettier --check .` |
| `format:fix` | `bun run format` |

### 1.7 Test

| Script | Purpose |
|--------|---------|
| `test` | Orchestrator script |
| `test:run` | `bunx vitest run` |
| `test:coverage` | vitest with coverage |
| `test:all` | test --force |
| `test:dry` | test --dry-run |
| `test:unit` | vitest run + coverage + verbose |
| `test:unit:watch` | vitest watch |
| `test:unit:ui` | vitest UI |
| `test:e2e` | playwright test (with env) |
| `test:e2e:ui`, `test:e2e:debug`, `test:e2e:codegen` | Playwright UI/debug/codegen |
| `test:api`, `test:db`, `test:agent`, `test:workflows`, `test:components`, `test:ct`, `test:rls` | Scoped E2E |
| `test:stress`, `test:chaos`, `test:resilience:all`, `test:mutation`, `test:fuzz` | Non-functional |
| `test:ci` | coverage + api + components + workflows |
| `test:fr:*` | Feature-area shortcuts (auth, documents, …) |
| `test:pm`, `test:graph`, `test:governance`, `test:coverage:dist`, `test:audit`, `test:new` | Tooling / meta |

### 1.8 Coverage / security / monitor / clean

| Script | Purpose |
|--------|---------|
| `coverage:check`, `coverage:report`, `coverage:all`, `coverage:analyze` | Coverage |
| `security:scan`, `security:report`, `security:workos`, `security:workos:fix` | Security |
| `monitor:redis` | Redis monitor script |
| `clean` | rm .next, node_modules/.cache |
| `clean:all` | rm .next, caches, node_modules + reinstall |
| `prepare` | husky |
| `postinstall` | fix-next-cache |
| `email:dev` | email preview server |

### 1.9 DX patterns (to borrow)

- **Grouped names:** `dev`, `dev:server`, `dev:log`; `test`, `test:unit`, `test:e2e`, `test:ci`.
- **Strict/fix variants:** `lint`, `lint:strict`, `lint:fix`; `format`, `format:check`, `format:fix`.
- **Discoverability:** Many granular scripts so `bun run <tab>` is useful.
- **Single entry points:** `test` = orchestrator; `lint` = primary linter.
- **DB/ops:** `db:migrate`, `db:status`, `db:schema`-style names even when they only echo or delegate.

---

## 2. Audit – Trace root today

Trace root `package.json` currently has:

| Script | Delegation |
|--------|------------|
| `quality` | `make quality` |
| `check` | `make check` (= quality) |
| `lint` | `make lint` |
| `test` | `cd frontend && bun test` (frontend only) |
| `generate:openapi:python` | script |
| `generate:openapi:go` | script |
| `generate:openapi` | both |
| `generate:openapi:gateway` | node script |
| `generate:types` | script |
| `generate:client` | script |
| `generate:all` | script |
| `generate:grpc` | buf / script |

**Gaps vs atoms.tech-style DX:**

1. No root `dev` – dev is `make dev` or `rtm dev start`; not discoverable via `bun run dev`.
2. No `build`, `start` at root – build/start live in Makefile and frontend.
3. No `lint:fix` or `lint:strict` – only `lint`.
4. No `type-check` at root – it’s `make type-check`.
5. No `format` / `format:check` at root – it’s `make format`.
6. No `test:unit`, `test:e2e`, `test:go`, `test:python` at root – only `test` (frontend).
7. No `clean` at root – it’s `make clean`.
8. No `db:*` at root – db is `make db-migrate`, `make db-reset`, etc.
9. No `dev:down`, `dev:logs`, etc. at root.
10. No `security:*`, `coverage:*`, or `monitor:*` at root (make has some).

Trace is a **workspace**: backend (Go + Python) via Makefile, frontend via `frontend/` with its own scripts. We do **not** duplicate frontend scripts at root; we add root scripts that **delegate** to `make` or `cd frontend && bun run X` so one can stay at repo root and use atoms-style names.

---

## 3. Plan – What to add at Trace root

### 3.1 Principle

- Root scripts = **aliases** to existing behavior (make or frontend).
- Same **naming and grouping** as atoms.tech where it fits.
- No new Makefile targets required for the first pass; only wire existing targets into `package.json`.

### 3.2 Mapping (atoms.tech-style name → Trace)

| Root script | Delegation | Note |
|-------------|-------------|------|
| `dev` | `make dev` | Full stack dev (or document `rtm dev start`) |
| `dev:tui` | `make dev-tui` | TUI dashboard |
| `dev:down` | `make dev-down` | Stop services |
| `dev:logs` | `make dev-logs` | Show logs |
| `dev:status` | `make dev-status` | Service status |
| `build` | `make build` if present, else `cd frontend && bun run build` | Prefer make if it exists |
| `lint` | (existing) `make lint` | Keep |
| `lint:fix` | `make format` | Closest “fix” (format); or add `make lint-fix` later |
| `type-check` | `make type-check` | |
| `format` | `make format` | |
| `format:check` | `make lint-python` | Includes ruff format --check |
| `test` | (existing) frontend tests; consider `make test` for full backend | Align with intent |
| `test:unit` | `make test-unit` | |
| `test:e2e` | `make test-e2e` | |
| `test:go` | `make test-go` | |
| `test:python` | `make test-python` | |
| `test:integration` | `make test-integration` | |
| `clean` | `make clean` | |
| `db:migrate` | `make db-migrate` | |
| `db:rollback` | `make db-rollback` | |
| `db:reset` | `make db-reset` | |
| `db:shell` | `make db-shell` | |
| `quality` | (existing) `make quality` | Keep |
| `check` | (existing) `make check` | Keep |
| `generate:*` | (existing) | Keep |

### 3.3 Out of scope (for this pass)

- Frontend-only scripts stay in `frontend/package.json` (e.g. `dev:docs`, `figma:*`).
- New Makefile targets (e.g. dedicated `lint-fix`) – optional follow-up.
- lint-staged / prepare / postinstall at root – optional; trace may not use husky at root.
- Security/coverage/monitor scripts – add later if/when we have matching make targets or scripts.

### 3.4 Implementation order

1. Add **dev**, **build**, **clean**, **format**, **type-check**, **db:*** scripts that delegate to existing make targets.
2. Add **test:*** variants that delegate to make (test-unit, test-e2e, test-go, test-python, test-integration).
3. Add **lint:fix** (→ `make format` for now) and **format:check** (→ `make lint-python` or a small inline ruff command).
4. Keep **test** semantics clear: either “full backend tests” (`make test`) or “frontend tests” (current); recommend `make test` at root and add `test:frontend` = `cd frontend && bun test` if we want both.

---

## 4. Implementation status

**Done.** Root `package.json` scripts delegate to Make or frontend as below.

| Script | Delegation |
|--------|------------|
| `dev`, `dev:tui`, `dev:down`, `dev:logs`, `dev:status` | make dev, dev-tui, dev-down, dev-logs, dev-status |
| `build` | cd frontend && bun run build |
| `quality`, `check` | make quality, make check |
| `lint`, `lint:fix` | make lint, make format |
| `type-check`, `format`, `format:check` | make type-check, make format, make lint-python |
| `test`, `test:frontend`, `test:unit`, `test:e2e`, `test:go`, `test:python`, `test:integration` | make test / frontend / make test-* |
| `clean` | make clean |
| `db:migrate`, `db:rollback`, `db:reset`, `db:shell` | make db-migrate, db-rollback, db-reset, db-shell |
| `generate:*` | existing scripts |

**Quick reference (from repo root):**

- `bun run dev` — full stack dev
- `bun run lint` — Go + Python lint
- `bun run format` — format Python + Go
- `bun run test` — backend tests; `bun run test:frontend` — frontend tests
- `bun run db:migrate` — run migrations; `bun run db:rollback` — rollback last

See also **Go/Py DX plan:** `docs/reports/GO_PY_DX_PLAN.md` (lint:go, lint:python, format:python, format:go, test:coverage, type-check variants).

---

## 5. Reference

- **atoms.tech:** `../../clean/deploy/atoms.tech/package.json`
- **Trace Makefile:** `Makefile` (help, dev, quality, lint, format, type-check, test-*, db-*, clean)
- **Trace frontend:** `frontend/package.json` (dev, build, test, lint, format, typecheck, etc.)
