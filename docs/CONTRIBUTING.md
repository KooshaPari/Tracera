# Contributing to Tracera

Contributor guide for the Tracera trace/observability ledger — a polyglot repo
(Rust workspace + bun/Turborepo frontend + Go sidecar + Python migration
material) over a 27-service local dev stack. Start with
`docs/ARCHITECTURE.md` for the component map, and `docs/governance/` for ADRs.

## 1. Development Environment

| Tool | Version / Source | Notes |
|------|------------------|-------|
| Rust | `rust-toolchain.toml`; MSRV 1.82 (`Cargo.toml` `rust-version`) | workspace edition 2021 |
| bun | `frontend/bun.lock`, `frontend/bunfig.toml` | package manager + runtime for the frontend |
| Node | for tooling invoked via `bun x` | Turborepo, Vite, Playwright, Storybook |
| Go | `sidecar/go/go.mod` | only for `tracera-sidecar` |
| Python | >= 3.10 (`pyproject.toml`) | migration/legacy material + formatting via ruff |
| Container runtime | docker compose / podman-compose | see `Taskfile.yml` host notes |
| task | `Taskfile.yml` | **canonical** entrypoint (make is a forwarder) |

Bootstrap:

```bash
cargo build --workspace                 # Rust workspace
cd frontend && bun install              # installs workspace packages + patches
task stack                              # bring up the local dev compose stack
task stack-seed                         # seed fixtures
```

> **Host note:** `Taskfile.yml` records that on some machines the verified
> container runtime is rootful `podman-compose` inside WSL
> (`FedoraLinux-44`); the host Docker Desktop socket and `podman-machine`
> may be broken. Prefer `task stack` over raw `docker compose` there.

## 2. Build

```bash
# Rust (canonical)
cargo build --workspace
cargo check --workspace
make build            # same as: cargo build --workspace
make check            # same as: cargo check --workspace

# Frontend (bun + Turborepo)
cd frontend && bun run build              # turbo build --filter=@tracertm/web
cd frontend && bun run build:parallel     # turbo build --parallel --concurrency=8
cd frontend && bun run dev                # apps/web dev server
cd frontend && bun run dev:desktop        # desktop shell

# Runtime
task run-server       # cargo run -p tracera-server   (:8080)
task mcp-server       # cargo run -p tracera-mcp --bin mcp-server
task tunnel           # expose local server (Tailnet-first, CF fallback)
task prod             # stack + run-server + tunnel
```

## 3. Test

```bash
cargo test --workspace                      # Rust workspace tests
make test                                   # same as above
cargo test -p tracera-server                # single crate

cd frontend && bun run test                 # turbo test --concurrency=4
cd frontend && bun run test:unit            # apps/web unit tests (Vitest)
cd frontend && bun run test:a11y            # accessibility tests
cd frontend && bun run test:perf            # performance test suite
cd frontend && bun run test:client-server-parity
```

Specialized suites and gates:
- Mutation testing: `cargo-mutants.toml` + `.github/workflows/mutants.yml`.
- Coverage: `.github/workflows/coverage.yml`; policy in
  `docs/governance/ADR-TEST-001-test-coverage-policy.md` and
  `ADR-TEST-002-mutation-testing.md`.
- E2E: `.github/workflows/e2e.yml` (Playwright).
- Python: `uv run pytest` (see `pyproject.toml` dev extras: pytest, pytest-cov,
  coverage, mypy).
- Go sidecar: `cd sidecar/go && go test ./...`.

## 4. Lint & Format

```bash
# Rust
cargo fmt --all
cargo clippy --workspace --all-targets -- -D warnings
make fmt && make clippy

# Frontend (oxlint + oxfmt + stylelint)
cd frontend && bun run check          # lint + format:check + typecheck
cd frontend && bun run lint:fix
cd frontend && bun run format:check
cd frontend && bun run typecheck

# Python
uv run ruff format --check <files>
uv run ruff check
```

`ruff.toml` selects `E, F, W, I, N, UP, B, C4, SIM` (E501 ignored).
`lefthook.yml` (+ `.lefthook/`) runs rustfmt/clippy on Rust, prettier on
frontend assets, ruff-format on Python, and commit-msg validation.

## 5. Code Style

- **Rust**: hexagonal layering (domain vs adapters) per
  `docs/governance/ADR-ARCH-001-hexagonal-architecture.md`. Keep the dual-store
  strategy intact (`ADR-DATA-001-dual-store-strategy.md`): SQLite for local,
  Postgres for hosted — do not bypass the `Store` trait.
- **TypeScript/Svelte**: oxlint + oxfmt conventions; typed API access goes
  through `packages/api-client` with types generated from the OpenAPI spec
  (`bun run generate:types`). Don't hand-edit `src/api/schema.ts`.
- **Python**: ruff-format; treat as migration material, not the supported runtime.
- Keep files cohesive and decompose large modules (the repo has precedent:
  `main.rs` was decomposed into handler modules; stores split into domain
  modules).

## 6. Commit / PR Conventions

Conventional Commits (`type(scope): subject`); types used in this repo include
`feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.
Use the ` [skip ci]` suffix only for doc-only / non-buildable changes.

Every commit carries immutable-ledger trailers (repo norm):

```text
subject: type(scope): description

tx-agent:     jcode|codex|forge|human
tx-task:      <task/issue reference>
tx-validated: lint|test|build|manual|none
tx-scope:     <affected components>
tx-intent:    <one-line purpose>
```

PR flow:

1. Branch from `main`; keep changes scoped (CI uses a `detect-changes` job to
   route rust/go/python/typescript lanes).
2. Run local gates: `cargo fmt --all && cargo clippy --workspace --all-targets
   -- -D warnings && cargo test --workspace` plus `cd frontend && bun run check`.
3. Open the PR; required checks come from `.github/workflows/ci.yml`
   (`required-ci-lint`, `required-ci-test`, `ci`) plus coverage, e2e,
   dependency-review, and trunk-check.
4. Branch protection requires signed commits
   (`ADR-GOV-003-signed-commits-branch-protection.md`). Never force-push shared
   branches.

## 7. Documentation

- Session-scoped work documents live in `docs/sessions/<YYYYMMDD>-<slug>/`
  (existing set spans `20260718-tracera-parity-polyglot` through
  `20260810-tracera-cli-rich-gateway`).
- Architecture decisions are recorded in `docs/governance/` as numbered ADRs.
- Canonical guides: `docs/01-getting-started/`, `docs/04-guides/`,
  `docs/06-api-reference/`, and `docs/API_REFERENCE.md` (audit target contract).
- Keep the endpoint mount matrix in
  `docs/governance/policy/endpoint_traceability_map.md` accurate — it is the
  source of truth for which routes are actually deployed.

## 8. Security

- No secrets in code or docs; `.env.example` documents required vars.
- Secret scanning and provenance checks run in CI
  (`.github/workflows/secret-provenance.yml`, `security-guard-hook-audit.yml`).
- Report vulnerabilities per `SECURITY.md`.
- `task deploy` triggers the Render fallback only when the local box is offline
  long-term; `task prod` is the canonical local go-live path.