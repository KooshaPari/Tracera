# WP-01: Source Register & Pinned Dependencies

> **Work Package:** WP-01 — Refresh source identities and existing evaluation mapping
> **Captured:** 2026-09-17T04:31Z (UTC-7)
> **Branch:** main
> **Repository:** [KooshaPari/Tracera](https://github.com/kooshapari/Tracera)

---

## 1. Current Immutable Refs

### Git

| Ref | Value |
|-----|-------|
| HEAD commit | `1f55ff952b5ea4a0b31ae589db8070efd919c7d6` |
| Default branch | `main` |
| Last push (remote) | `2026-09-17T03:13:32Z` |

### Rust Toolchain

| Component | Version |
|-----------|---------|
| rustc | 1.98.0 (88d9e12ae 2026-08-18) |
| cargo | 1.98.0 (797e8a9bc 2026-08-05) |
| rust-toolchain.toml | `stable` channel, target `wasm32-unknown-unknown` |
| MSRV (workspace) | 1.82 |
| Edition | 2021 |

### Node / Bun / Frontend Toolchain

| Component | Version |
|-----------|---------|
| Bun | 1.4.0 |
| Node (CI) | 22 (via `actions/setup-node@v4`) |
| TypeScript | 5.9.3 |
| Vite | ^8.2.1 |
| Vitest | ^4.1.10 |

### CI Runners

| Workflow | Runner |
|----------|--------|
| ci.yml | `ubuntu-latest` (default) / Blacksmith variants (`2vcpu`, `4vcpu`) for manual dispatch |
| dtolnay/rust-toolchain | pinned to `6bed0761d98439e5a578e2877258200ad565ba87` (stable) |
| actions/setup-node | pinned to `49933ea5288caeca8642d1e84afbd3f7d6820020` (v4) |

### Key Rust Dependency Versions (from Cargo.lock)

| Dependency | Locked Version | Workspace Spec |
|------------|---------------|----------------|
| axum | 0.8.9 | — (per-crate) |
| tokio | 1.53.1 | `"1"` (full) |
| sqlx | 0.9.0 | — (per-crate) |
| reqwest | 0.12.28 / 0.13.1 | — (per-crate) |
| serde | 1.0.229 | `"1"` (derive) |
| serde_json | 1.0.151 | `"1"` |
| chrono | 0.4.45 | `"0.4"` (serde) |
| uuid | 1.26.0 | `"1"` (serde, v4, v5) |
| tower | 0.5.3 | — |
| hyper | 1.10.1 | — |
| tracing | 0.1.44 | `"0.1"` |
| tracing-subscriber | 0.3.23 | `"0.3"` (env-filter) |
| anyhow | 1.0.104 | — |
| thiserror | 2.0.20 | `"2"` |
| clap | 4.6.6 | — (per-crate) |
| indexmap | 2.14.2 | `"2"` (serde) |
| base64 | 0.23.1 | `"0.23"` |
| sha2 | 0.10.9 / 0.11.0 | `"0.11"` |
| tempfile | 3.27.0 | `"3"` |
| proptest | — | `"1"` |
| deadpool | 0.9.5 | — (sqlx pool) |
| ring | 0.17.14 | — (crypto) |
| clickhouse | 0.15.2 | — (events) |

### Key Frontend Dependency Versions (from package.json)

| Dependency | Declared Version |
|------------|-----------------|
| react / react-dom | ^19.3.0 |
| @tanstack/react-router | ^1.170.35 |
| @tanstack/react-query | ^5.102.8 |
| @xyflow/react | ^12.11.3 |
| zod | ^4.4.3 |
| @legendapp/state | ^3.0.0-alpha.40 |
| framer-motion | ^11.11.17 |
| @sentry/react | ^10.74.0 |
| @workos-inc/authkit-react | ^0.16.0 |
| tailwindcss | ^4.1.17 |
| lucide-react | ^0.563.0 |
| recharts | ^2.13.3 |
| cytoscape | ^3.30.4 |
| graphology | ^0.26.0 |
| sigma | ^3.0.2 |
| monaco-editor | ^0.56.0 |
| msw | ^2.12.7 |
| @playwright/test | ^1.63.0 |
| storybook | 10.6.0 |

---

## 2. Workspace Inventory

### Rust Workspace Crates

> Workspace members defined in root `Cargo.toml` (resolver v2).

| Crate | Version | Description | Files | Lines | Status |
|-------|---------|-------------|-------|-------|--------|
| `tracera-server` | 0.1.3 | Core Tracera server — Store trait, routing, domain logic | 77 | ~10,118 | **active** |
| `tracera-atlas` | 0.1.0 | Atlas ALM: WorkItem delegation, SDLC observability, agent-of-record, CI bridge | 6 | ~2,924 | **active** |
| `tracera-workos` | 0.1.0 | WorkOS integration: AuthKit, webhooks, directory sync, audit log ingest | 8 | ~2,603 | **active** |
| `tracera-events` | 0.1.0 | ClickHouse-backed ingest: agent_runs, decisions, deploys, traces, llm_calls | 7 | ~1,573 | **active** |
| `tracera-cli` | 0.1.0 | CLI for managing bundled/local Tracera Compose stack (docker, podman, WSL2) | 5 | ~1,120 | **active** |
| `tracera-mcp` | 0.1.0 | MCP server over stdio — SWEE graph read/write/navigate/propose tools | 3 | ~754 | **active** |
| `tracertm-mcp` | 0.1.0 | MCP stdio server (native Rust, replaces python -m tracertm.mcp) | 1 | ~319 | **active** |
| `tracera-edge` | 0.1.0 | Cloudflare Worker edge API for Tracera | 1 | ~314 | **active** |
| `mock-agcord` | — | Mock AgCord server: returns AgCord-compatible JSON for /ingest/agileplus | 1 | ~138 | **active** (test helper) |

### Non-Workspace Crates (present in crates/ but NOT in workspace members)

| Crate | Files | Lines | Notes |
|-------|-------|-------|-------|
| `tracera-graphql` | 8 | ~2,421 | Not in workspace; may be experimental or archived |
| `tracera-ml` | 6 | ~2,208 | Not in workspace; ML pipeline crate |
| `tracera-neo4j` | 4 | ~247 | Not in workspace; Neo4j integration |

### Frontend Packages

| Package | Name | Version | Description |
|---------|------|---------|-------------|
| `apps/web` | @tracertm/web | 0.1.0 | Main web application (React 19, Vite 8, TanStack Router) |
| `apps/desktop` | — | — | Electrobun desktop shell |
| `apps/tauri-desktop` | — | — | Tauri-based desktop app |
| `apps/os-service` | — | — | OS service (Rust, Cargo.toml) |
| `packages/api-client` | @tracertm/api-client | 0.1.0 | Generated OpenAPI client |
| `packages/config` | @tracertm/config | 0.1.0 | Shared configuration |
| `packages/env-manager` | @tracertm/env-manager | 1.0.0 | Environment variable manager |
| `packages/state` | @tracertm/state | 0.1.0 | State management (Legend State) |
| `packages/tokens` | @tracera/tokens | 1.0.0 | Design tokens (WCAG 2.2 AA) |
| `packages/types` | @tracertm/types | 0.1.0 | Shared TypeScript types |
| `packages/ui` | @tracertm/ui | 0.1.0 | Shared UI components (Radix + shadcn pattern) |

### Phenotype Shared Dependencies (PhenoInfra)

Pinned to git rev `dd040ed1` from [KooshaPari/PhenoInfra](https://github.com/KooshaPari/PhenoInfra):

| Crate | Status |
|-------|--------|
| phenotype-crypto | **pinned** (rev dd040ed1) |
| phenotype-telemetry | **pinned** (rev dd040ed1) |
| phenotype-git-core | **pinned** (rev dd040ed1) |
| phenotype-health | **pinned** (rev dd040ed1) |
| phenotype-observability | **pinned** (rev dd040ed1) |

> **Note:** `digest` is patched to v0.10.7 via `patch.crates-io` to avoid a breaking API change in the RustCrypto ecosystem that breaks hmac + sha2 core_api paths (WorkOS webhook HMAC).

---

## 3. Dependency Classification

### Rust Dependencies

| Dependency | Version | Classification | Notes |
|------------|---------|----------------|-------|
| axum | 0.8.9 | **confirmed** | Active; latest 0.8.x line |
| tokio | 1.53.1 | **confirmed** | Active; current stable |
| sqlx | 0.9.0 | **confirmed** | Active; 0.9.x current line |
| reqwest | 0.12.28 / 0.13.1 | **confirmed** | Two versions resolved; 0.13.x is newer |
| serde / serde_json | 1.0.229 / 1.0.151 | **confirmed** | Active; stable API |
| chrono | 0.4.45 | **confirmed** | Active; 0.4 line stable |
| uuid | 1.26.0 | **confirmed** | Active; current |
| tower | 0.5.3 | **confirmed** | Active |
| hyper | 1.10.1 | **confirmed** | Active; 1.x line |
| tracing | 0.1.44 | **confirmed** | Active; stable |
| anyhow | 1.0.104 | **confirmed** | Active; widely used |
| thiserror | 2.0.20 | **confirmed** | Active; 2.x current |
| clap | 4.6.6 | **confirmed** | Active; 4.x current |
| base64 | 0.23.1 | **confirmed** | Active |
| clickhouse | 0.15.2 | **confirmed** | Active; used by tracera-events |
| deadpool | 0.9.5 | **confirmed** | Active; sqlx connection pooling |
| ring | 0.17.14 | **confirmed** | Active; crypto primitives |
| digest (patched) | 0.10.7 | **blocked** | Pinned via patch.crates-io; blocks sha2 0.11 + hmac upgrade |
| Phenotype crates | rev dd040ed1 | **pinned** | Shared infra; pinned to specific PhenoInfra rev |
| proptest | — | **confirmed** | Workspace dep; property testing |

### Frontend Dependencies

| Dependency | Version | Classification | Notes |
|------------|---------|----------------|-------|
| react / react-dom | ^19.3.0 | **confirmed** | Current stable |
| @tanstack/react-router | ^1.170.35 | **confirmed** | Active; file-based routing |
| @tanstack/react-query | ^5.102.8 | **confirmed** | Active; v5 current |
| @xyflow/react | ^12.11.3 | **confirmed** | Active; graph visualization |
| zod | ^4.4.3 | **confirmed** | Active; v4 current |
| @legendapp/state | ^3.0.0-alpha.40 | **stale** | Alpha release; tracking upstream |
| framer-motion | ^11.11.17 | **confirmed** | Active |
| @sentry/react | ^10.74.0 | **confirmed** | Active; error monitoring |
| @workos-inc/authkit-react | ^0.16.0 | **confirmed** | Active; auth integration |
| tailwindcss | ^4.1.17 | **confirmed** | Active; v4 current |
| lucide-react | ^0.563.0 | **confirmed** | Active; icon library |
| cytoscape | ^3.30.4 | **confirmed** | Active; graph library |
| graphology | ^0.26.0 | **confirmed** | Active; graph analytics |
| sigma | ^3.0.2 | **confirmed** | Active; WebGL graph renderer |
| monaco-editor | ^0.56.0 | **confirmed** | Active; code editor |
| msw | ^2.12.7 | **confirmed** | Active; API mocking for tests |
| @playwright/test | ^1.63.0 | **confirmed** | Active; E2E testing |
| storybook | 10.6.0 | **confirmed** | Active; component development |

---

## 4. Observation Classification

### CI/CD Workflows

| Workflow | Classification | Notes |
|----------|----------------|-------|
| `ci.yml` | **confirmed** | Unified multi-language pipeline (Rust, Python, Go, TS); runs on push/PR/merge_group |
| `ci-agents.yml` | **unknown** | Not yet inspected |
| `coverage.yml` | **confirmed** | Rust code coverage; runs on push/PR to main |
| `mutants.yml` | **confirmed** | cargo-mutants; runs on PR + weekly Sunday cron |
| `scorecard.yml` | **confirmed** | OpenSSF Scorecard; runs weekly Monday + on main push |
| `codeql.yml` | **blocked** | Disabled — uses GitHub default CodeQL setup instead |
| `dependency-audit.yml` | **confirmed** | Runs on Cargo.lock/package.json changes |
| `e2e.yml` | **unknown** | Not yet inspected |
| `build-push-image.yml` | **unknown** | Not yet inspected |
| `deploy-cloudflare.yml` | **unknown** | Not yet inspected |
| `deploy-full-stack.yml` | **unknown** | Not yet inspected |
| `deploy-render.yml` | **unknown** | Not yet inspected |
| `deploy-vercel.yml` | **unknown** | Not yet inspected |
| `deploy-pages.yml` | **unknown** | Not yet inspected |
| `release.yml` | **unknown** | Not yet inspected |
| `release-crates.yml` | **unknown** | Not yet inspected |
| `release-dist.yml` | **unknown** | Not yet inspected |
| `release-desktop.yml` | **unknown** | Not yet inspected |
| `release-desktop-sign.yml` | **unknown** | Not yet inspected |
| `release-macos.yml` | **unknown** | Not yet inspected |
| `nightly.yml` | **unknown** | Not yet inspected |
| `trunk-check.yml` | **unknown** | Not yet inspected |
| `runtime-latency-smoke.yml` | **unknown** | Not yet inspected |
| `frontend-contract-checks.yml` | **unknown** | Not yet inspected |
| `deployment-capability-checks.yml` | **unknown** | Not yet inspected |
| `sidecar-bootstrap-checks.yml` | **unknown** | Not yet inspected |
| `secret-provenance.yml` | **unknown** | Not yet inspected |
| `security-guard-hook-audit.yml` | **unknown** | Not yet inspected |
| `audit-sla.yml` | **unknown** | Not yet inspected |
| `alert-sync-issues.yml` | **unknown** | Not yet inspected |
| `review-fanout.yml` | **unknown** | Not yet inspected |
| `infisical.yml` | **unknown** | Not yet inspected |
| `retroactive-sweep.yml` | **unknown** | Not yet inspected |
| `debloat-history.yml` | **unknown** | Not yet inspected |

### Test Suites

| Suite | Classification | Notes |
|-------|----------------|-------|
| Rust unit/integration tests (`cargo test`) | **unknown** | Not yet run against HEAD |
| `vitest run` (frontend) | **unknown** | Not yet run against HEAD |
| Playwright E2E (`test:e2e`) | **unknown** | Not yet run against HEAD |
| Playwright Visual (`test:visual`) | **unknown** | Not yet run against HEAD |
| Accessibility tests (`test:a11y`) | **unknown** | Not yet run against HEAD |
| Security tests (`test:security`) | **unknown** | Not yet run against HEAD |
| Performance benchmarks (`test:performance`) | **unknown** | Not yet run against HEAD |
| Contract tests (`test:contracts`) | **unknown** | Not yet run against HEAD |
| Storybook tests | **unknown** | Not yet run against HEAD |
| Chromatic visual regression | **unknown** | Not yet run against HEAD |

### Audit Tools

| Tool | Classification | Notes |
|------|----------------|-------|
| OpenSSF Scorecard | **confirmed** | Weekly automated; output in GitHub Security tab |
| CodeQL | **blocked** | Custom workflow disabled; using GitHub default setup |
| cargo-mutants | **confirmed** | Baseline mode on PRs; weekly full run |
| cargo-audit (dependency-audit.yml) | **confirmed** | Triggered on lock file changes |
| Rust code coverage | **confirmed** | Automated on push/PR |

---

## 5. Native Audit/Ledger Mapping

### Existing Audit Tools and Their Output Formats

| Tool | Output Format | What Tracera Assessment Consumes |
|------|---------------|----------------------------------|
| OpenSSF Scorecard | JSON (SARIF) + badge | Supply-chain security posture score; maps to `security_posture` dimension |
| CodeQL | SARIF | Vulnerability findings; maps to `vulnerability_count`, `severity_distribution` |
| cargo-mutants | Text report + baseline diff | Mutation score; maps to `test_effectiveness` dimension |
| cargo-audit | Table / JSON | Dependency vulnerabilities; maps to `dependency_risk` dimension |
| Rust code coverage (tarpaulin/llvm-cov) | LCOV / HTML | Line/branch coverage %; maps to `coverage_pct` dimension |
| Vitest coverage (frontend) | LCOV / JSON | JS/TS coverage; maps to `frontend_coverage_pct` |
| Playwright test results | JSON reporter | E2E pass/fail; maps to `e2e_pass_rate` |
| Chromatic | Web dashboard + JSON | Visual regression delta; maps to `visual_regression_score` |
| Lighthouse | JSON | Performance, a11y, SEO scores; maps to `lighthouse_*` dimensions |
| Storybook test runner | JSON | Component test pass rate |

### Schema Gaps

1. **No unified assessment schema exists yet.** Each tool outputs in its own format. WP-02/03 will need to define a common assessment ingestion format (likely JSON-lines or a structured Rust enum).

2. **Mutation score not automatically exported.** cargo-mutants outputs to stdout/logs; no machine-readable artifact is currently persisted.

3. **Lighthouse results are ephemeral.** Playwright-based Lighthouse runs produce JSON but it is not stored or versioned.

4. **Chromatic results are Cloud-hosted.** Visual regression deltas live in Chromatic's dashboard, not in-repo artifacts.

5. **Coverage reports are generated but not aggregated.** Rust and frontend coverage exist separately; no cross-language rollup.

6. **No provenance attestation for dependencies.** The `secret-provenance.yml` workflow exists but its output format and coverage are not yet characterized.

7. **PhenoInfra dependencies lack version metadata.** Pinned by git rev only; no Cargo.lock version tracking for shared crates (they inherit from PhenoInfra's own lock).

---

## 6. Summary Statistics

| Metric | Value |
|--------|-------|
| Workspace Rust crates | 9 (active) + 3 (non-workspace) |
| Total Rust source files | ~119 |
| Total Rust source lines | ~24,508 |
| Frontend packages | 7 (packages) + 4 (apps) |
| CI/CD workflows | 34 |
| Key Rust deps pinned | 25+ |
| Key frontend deps pinned | 20+ |
| Shared Phenotype crates | 5 (all pinned to PhenoInfra rev) |
| Audit tools in CI | 5 (Scorecard, CodeQL-default, cargo-mutants, cargo-audit, coverage) |

---

*This register captures the baseline state. WP-02 will use these refs to establish assessment dimensions and WP-03 will build the ingestion pipeline against these output formats.*
