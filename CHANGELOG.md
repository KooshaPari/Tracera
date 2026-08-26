# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- In-memory rate limiting via tower-governor for the Rust server (#964)
- CSRF protection middleware for state-mutating requests (#883, #964)
- `/metrics` endpoint with OpenTelemetry and Sentry hooks (#964)
- Endpoint regression ADR + install scripts (Chocolatey, NSIS template, irm|iex) (#945)
- `irm|iex` install/uninstall scripts, `INSTALL.md`, Chocolatey package, and NSIS installer template (#922)
- Five MCP tools wired into `tracertm-mcp` crate (#897)
- `TRACERA_AUTH_TOKEN` documented in `.env.example`

### Fixed

- CI: disable Prettier lifecycle scripts (#859)
- CI: restore Mergify schema (#891)
- CI: restrict required context permissions (#893)
- CI: use supported cargo coverage text output (#896)
- CI: reconcile Pages contracts with native frontend typecheck (#902)
- CI: scope coverage concurrency by ref (#903)
- CI: repair current coverage workflow contract (#906)
- CI: keep native typechecks non-mutating (#900)
- Pages: run API base contract from frontend root (#899)
- Server: remove `tower_http::timeout` import (feature not enabled) (#890)
- Server: remove `tower_governor` rate limiting (v0.4 does not exist on crates.io) (#889)
- Server: revert to `tower_governor` (correct crate name) (#888)
- Deps: restore tracertm MCP lock resolution (#907)
- CLI: make WSL compose argv coverage deterministic (#908)

### Changed

- Bump vite from 8.1.3 to 8.2.1 (#874)
- Bump `@xyflow/react` (#872)
- Bump `@trpc/server` (#871)
- Bump zod from 4.3.6 to 4.4.3 (#870)
- Bump storybook (#869)
- Bump `@playwright/test` (#867)
- Bump `@storybook/addon-coverage` (#866)
- Bump react-ecosystem group (#865)
- Bump thiserror from 2.0.19 to 2.0.20 (#864)

---

## [2.3.0] - 2026-08-21

### Added

- Native Rust server: 20 Axum endpoints (`tracera-server`) (#677)
- Native Rust MCP: `tracertm-mcp` crate with 5 MCP tools (#678)
- Cloudflare Worker edge layer: `tracera-edge` (#680)
- Desktop app migration from Electron to Electrobun (Phenotype org standard) (#716)
- CLI binary with cross-platform compile support (`tracera-cli`)
- `release-dist` workflow: build both server and CLI binaries for cross-platform release
- `cargo-dist` config for release automation (#683)
- crates.io publish workflow for `tracera-server` and `tracertm-mcp` (#690, #691)
- Nightly + E2E workflows with iteration loop (#693)
- Self-host deployment stack: Docker Compose + Caddy + Cloudflare Tunnel (#688, #692)
- KV read-through cache on `/org-intel/metrics` + reproducible KV provisioning (#708)
- Store trait + SQLite on-device tier alongside Postgres (#713)
- Postgres persistence restored for evidence/sprints/stories/teams (#709)
- Real GitHub/Jira issue ingest via Store trait (#717)
- Infisical integration workflow
- `cargo-llvm-cov` coverage workflow (#881)
- Vercel deployment workflow and `vercel.json` configuration
- Observability ledger consumer fixture (#771)
- `phenodag` absorption: atomic claim, heartbeat, lifecycle, dedup, SQLite, scanner, export (#723, #725, #727)

### Changed

- Axum upgrade from 0.7.9 to 0.8.9 (#755)
- tower-http upgrade from 0.6.11 to 0.7.0 (#770)
- sha2 upgrade from 0.10.9 to 0.11.0 (#760)
- thiserror upgrade from 2.0.18 to 2.0.19 (#763)
- uuid upgrade from 1.23.4 to 1.24.0 (#765)
- tokio upgrade from 1.52.3 to 1.53.1 (#767)
- serde upgrade from 1.0.228 to 1.0.229 (#757)
- base64 upgrade from 0.22.1 to 0.23.0 (#777)
- http upgrade from 1.4.2 to 1.5.0 (#778)
- which upgrade from 7.0.3 to 8.0.5 (#779)
- regex upgrade from 1.12.4 to 1.13.1 (#753)
- rand upgrade from 0.8.7 to 0.10.2 (#751)
- worker upgrade from 0.4.2 to 0.8.5 (#769)
- recharts upgrade from 2.15.4 to 3.10.1 (#817)
- immer upgrade from 10.2.0 to 11.1.16 (#815)
- web-vitals upgrade from 4.2.4 to 6.0.1 (#759)
- `.mailmap` canonicalizing bot identities to KooshaPari

### Fixed

- Server: migrate `:param` to `{param}` route syntax for Axum 0.8 (#878, #879, #880)
- CLI: default REST client to rich gateway (#806)
- Frontend: preserve dashboard artifact markers (#841)
- Frontend: clean up preflight check logic for configured API URL
- Frontend: synchronize Bun lockfile with workspace manifests (#774, #802, #840)
- Compose: require local API auth token (#821)
- Compose: use same-origin frontend API (#796)
- Self-host: wire protected API to Postgres (#799)
- Web: define client core backend URL (#833)
- Web: type form array default items (#834)
- Web: omit absent Gherkin className prop (#835)
- Web: align test run mutation optionality (#836)
- Web: align tRPC v11 dependencies (#805)
- Web: reduce strict typecheck errors (#793)
- CLI: cross-platform compile fixes for tracera-cli
- Desktop: default bundled local URL and auto-start stack on launch
- Desktop: add postbundle step to build pipeline
- CI: make nightly smoke self-contained and secret-safe (#776)
- CI: fetch full history for gitleaks (#830)
- CI: surface Turbo build logs (#831)
- Deps: use cargo-deny LGPL identifier (#832)

---

## [2.1.2] - 2026-07-02

### Fixed

- Release-dist Windows archive path handling (#702)

---

## [2.1.1] - 2026-07-02

### Fixed

- Release-dist tar command paths for cross-platform builds (#701)

---

## [2.1.0] - 2026-07-02

### Added

- Release-dist workflow for cross-platform binary artifacts (#700)
- Vite+React real dashboard replacing placeholder (#696)
- CI: nightly + E2E workflows (iteration loop) (#693)
- Self-host deployment stack: Compose + Caddy + Cloudflare Tunnel (#692)
- crates.io publish for `tracera-server`, `tracertm-mcp` (#690, #691)
- `cargo-dist` release config (#683)
- Self-host stack: Compose + Caddy + Cloudflare (#688)
- Kubernetes chart + PWA manifest (#687)
- Observability/perf/data hardening docs (#686)
- Security + governance hardening docs (#685)
- De-bloat workflow (filter-repo on CI)
- Release-drafter workflow (#262)
- `process-compose` configuration for local dev stack (#214)
- Health endpoints: `/healthz` and `/readyz` (#625)
- TypeScript SDK client for tracera endpoints (#628)
- Tracera Electrobun desktop client (step-1, live-service) (#654)
- `tracera-core`: entity model, matrix ops, impact analysis, pagination, health, cache, notification, rate_limit, layered config (#547, #550, #576, #577, #584)
- Gene-dag absorption: dedup, SQLite, scanner, export, beads, status, init (#727)

### Changed

- Renamed `agileplus-specs`, `claude-commands`, `dispatch-mcp`, `mcp-tool-chest`, `Tracertm-rs` archived/cleaned up

### Fixed

- Vercel deployment: configure frontend build and output directory (#698, #699)
- Workspace members: remove non-existent `tracera-core` crate (#694)
- Tracera deploy unblock: Dockerfile + alembic + route parity (#665)
- Wire missing Tracera routers: endpoint parity vs oracle (#661)
- Restore `account_repository` to repair FastAPI import regression (#660)
- CI check triage + repair (#658)
- Duplicate `filterwarnings` key in `pyproject.toml` (#645)
- Silence starlette/httpx deprecation warnings + pure-ASGI middleware (#641)
- Release-plz gated on `CARGO_REGISTRY_TOKEN` presence (#639)
- Remove corrupted git trace lines from `__init__.py` (#638)
- Resolve MDX TypeScript type errors in docs app (#633)
- Align README with Go backend + TypeScript/React frontend reality (#358)
- Fix VitePress Pages asset base (#335)
- Resolve Vite 8 beta + rolldown build failures (#251)
- Resolve TypeScript compilation and production build issues

### Security

- Adopt MIT OR Apache-2.0 dual-license (#341)
- Pin floating external actions to SHAs in ci.yml, secret-scans.yml, security-scans.yml (#351, #352, #353)
- Add OpenSSF Scorecard workflow (#354)
- Replace dead phenoShared reusable workflow calls with inline equivalents (#695)

---

## [2.0.0] - 2026-02-23

### Added

- VitePress Pages pipeline and role-based docsets
- CI: GitHub Pages setup in VitePress workflow
- Agent swarm quality campaign: 99.2% lint violation reduction (42,761 violations fixed)
- Quality: Phase 5 maximum strictness, auto-fix 1,022 files
- Achieved 100/100 quality score — all tests passing
- OpenTelemetry Python backend instrumentation
- CI coverage regression detection
- Comprehensive test validation Makefile targets and GitHub Actions CI/CD
- Route validation E2E tests with CORS header verification
- WebSocket CORS validation tests
- Python route validation tests
- Go route validation tests
- Docker layer optimization (Task #63)
- Dependency caching in GitHub Actions workflows
- Parallelized process-compose startup (60s to 30s)

### Changed

- TypeScript compilation and production build resolved
- Phase 1 linting hardening enforcement
- AI-strict oxlint configuration activated
- Complexity limits added to ruff configuration
- Pre-commit hooks optimized for Phase 1 linting
- Filebase reorganized: 572 historical files archived, root cleaned up

### Fixed

- Shell injection vulnerability in `complete_setup.py`
- Go mutex copy warning in embeddings indexer
- TypeScript module errors for enterprise-table and loading-skeleton
- `kwargs` type annotations (ANN003) across 117+ violations
- Router type annotations completed
- Naming explosion violations eliminated

---

## [1.1.0] - 2026-01-31

### Added

- Monitoring exporters layer
- Workflow and monitoring layer
- Infrastructure layer for process-compose
- Virtual scrolling in ItemsTableView (400-600% performance improvement)
- Viewport frustum culling for graph performance (Phase 1)
- Progressive edge loading for all graph components
- Cross-perspective search implementation with advanced features
- Comprehensive accessibility improvements: keyboard navigation, focus management, ARIA landmarks
- Production release documentation suite
- Native process orchestration design and implementation plan
- 525+ new tests across CLI, API, services, TUI, repository, and core layers
- Test coverage escalation from 20.85% to 85%+ (1,200+ tests)

### Changed

- Migrated graph components from Dagre to ELKjs for ESM compatibility
- API client updated with proper typing and fixed regex syntax errors
- Filebase reorganized: 326 archived `.md` files removed from root

### Fixed

- Map snake_case API response to camelCase for link rendering
- TaskError/TaskResult type snake_case naming mismatch in cancelTask
- 22+ performance test failures with async/mock fixes
- 22 mypy type errors in `src/tracertm/api/client.py`
- 50 mypy type errors in `src/tracertm/api/client.py`
- All 50 mypy type errors in service stubs and widgets
- 30+ mypy type errors in service stubs and widgets
- Failing Header and useLinks tests
- Test fixture issues and mock isolation problems
- Mock-related test failures in bulk operations and sync client

---

## [1.0.0] - 2025-12-03

### Added

- Initial stable release of Tracera
- Hexagonal trace-link matrix for agentic and LLM observability
- Rust core with domain + adapters architecture
- Web frontend with Vite + React
- GitHub Actions CI/CD pipeline
- CodeQL security analysis
- Dependabot dependency management
- Alembic database migrations
- OpenAPI specification
- Evidence gallery with lightbox
- Geist dark theme with hover-expand tooltips and clickable timeline
- Performance benchmarks and topo-sort unit tests
- Documentation site (VitePress)
- Architecture Decision Records (ADRs)
- MIT OR Apache-2.0 dual license
- Process-compose for local dev stack

---

## [0.1.2] - 2026-06-30

### Fixed

- Workspace members: remove non-existent `tracera-core` crate (#694)

### Changed

- Version bump to 0.1.2

---

## [0.1.1] - 2026-06-29

### Added

- Self-host deployment stack: Docker Compose + Caddy + Cloudflare Tunnel (#692)
- Nightly + E2E workflows (#693)
- crates.io publish workflows (#690, #691)

### Fixed

- Tracera deploy unblock: Dockerfile + alembic + route parity (#665)
- Wire missing Tracera routers (#661)

---

## [0.1.0] - 2026-03-29

### Added

- Rust workspace restructuring: `tracera-server`, `tracertm-mcp`, `tracera-edge`, `tracera-cli`
- Native Axum server with 20 endpoints
- Native Rust MCP implementation
- Cloudflare Worker edge layer
- Cargo workspace with shared dependencies
- `cargo-deny` license auditing
- `release-plz` for automated releases
- `cliff` for changelog generation
- `mise` and `justfile` for task running
- `SSOT.md` source of truth document
- Security documentation and governance gates
- Tracera migration ADR set (MADR) (#648)
- FR/NFR oracle and acceptance features (#649)
- Per-component migration map (#650)
- TS SDK client spec (#651)
- Agent-media + docs-proof pipeline (#652)
- Tracera release + hourly/nightly CI (#653)
