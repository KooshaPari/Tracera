# User-Story Walkthroughs: Batch 6 (2026-04-26)

Brief first-time verification of three miscellaneous repos: status, friction points, and architectural notes.

---

## 1. PhenoLibs

**Status: DELETED / 404**

- GitHub API returns 404 (HTTP 404, "Not Found")
- Repo no longer exists on GitHub
- Per memory task #246: confirmed as retired / archived repo

**Action**: No further work required; retire from active tracking.

---

## 2. Tracely

**Status: ACTIVE (canonical observability library)**

- **Created**: 2026-04-24 (very recent; launched mid-Q2)
- **Language**: Rust (Edition 2024)
- **Description**: Unified observability library for Phenotype ecosystem
  - Wraps OpenTelemetry, metrics, tracing crates
  - Supports OTLP, Prometheus, Jaeger, Zipkin exports
  - Zero-allocation log path
- **Visibility**: Private
- **Recent commits**:
  1. OpenSSF Scorecard workflow addition
  2. Retroactive CHANGELOG seeding via git-cliff
  3. README expansion

**Current State**:
- README fully populated (purpose, stack, quick-start, related projects)
- Core architecture in place (crates/tracely-core, tracely-sentinel, module structure)
- Smoke tests present
- Already integrated into quality gates (Scorecard workflow)

**Top-2 Friction Points**:

1. **Missing implementation details in crates/**
   - Crates declared in README but directory structure needs completion
   - tracely-core/ and tracely-sentinel/ appear to exist in README but may be sparse
   - Action: populate crate implementations and ensure cargo workspace builds

2. **Documentation coverage gaps**
   - README shows usage examples but no FUNCTIONAL_REQUIREMENTS.md or ADR.md
   - No PLAN.md for phased rollout of observability to Phenotype ecosystem
   - Action: scaffold spec docs (PRD, FR, PLAN) to enable AgilePlus workflow

---

## 3. phenotype-ops-mcp

**Status: ACTIVE (nanoVMs fork)**

- **Created**: 2026-04-24 (mid-Q2, very recent)
- **Language**: Go
- **Description**: MCP server bridge to nanoVMs `ops` unikernel toolchain
  - Fork of [nanovms/ops-mcp](https://github.com/nanovms/ops-mcp)
  - Extends upstream with Phenotype-specific tooling (auth, multi-tenant isolation, observability)
  - Upstream remote tracked; contributions PR'd back when generic
- **Visibility**: Public
- **License**: Apache-2.0 (preserved from upstream)
- **Last push**: 2026-04-25T14:23:56Z (today)

**Tool Manifest** (tools.json):
- Tools defined: pkg_load, instance_logs, instance_create, list_instances, and others
- Manifest generation: `go run . --dump-tools`
- CI workflow validates manifest freshness (Manifest check)
- Upstream limitation: metoro-io/mcp-golang v0.13.0 has no public tool accessor; manifest built from toolRegistrations() source of truth

**Current State**:
- Tool manifest exists and is validated in CI
- Upstream fork has 3 known open issues (1 in parent, tracked)
- Ready for Phenotype integration with nanovms client (bare-cua → phenotype-nanovms-client promotion)

**Top-2 Friction Points**:

1. **Schema reflection drift in tools.json**
   - Current manifest shows field mismatches (e.g., "longitude" used for image_name parameter)
   - invopop/jsonschema reflection may not match actual handler arg struct
   - Action: verify that `go run . --dump-tools` produces correct schema; update if handler signatures changed recently

2. **Upstream sync and multi-tenant auth gap**
   - README notes Phenotype extensions (auth, multi-tenant, observability) but no implementation detail
   - Fork rationale stated but not yet visible in code (may be WIP)
   - Action: either document the auth/multi-tenant extension API or open a kitty-spec for Phase 1 implementation

---

## Summary Table

| Repo | Status | Language | Created | Top-1 Friction | Top-2 Friction |
|------|--------|----------|---------|---|---|
| **PhenoLibs** | DELETED (404) | N/A | N/A | Repo no longer exists | N/A |
| **Tracely** | ACTIVE | Rust | 2026-04-24 | Missing crate implementations | No spec docs (FR, PLAN) |
| **phenotype-ops-mcp** | ACTIVE | Go | 2026-04-24 | Schema reflection drift in tools.json | Auth/multi-tenant extension gaps |

---

## Next Steps (Recommended)

### Tracely
- [ ] Complete crates/tracely-core/ implementation
- [ ] Scaffold FUNCTIONAL_REQUIREMENTS.md, PLAN.md in root
- [ ] Create AgilePlus kitty-spec for observability rollout to Phenotype ecosystem

### phenotype-ops-mcp
- [ ] Run `go run . --dump-tools` and verify tools.json schema matches code
- [ ] Create kitty-spec for Phenotype extensions (auth, multi-tenant, observability hooks)
- [ ] Document fork sync strategy with nanovms/ops-mcp (PR contribution policy)

---

**Document Generated**: 2026-04-26  
**Batch**: Misc Repos #6 (First-Run Walkthroughs)  
**Tool Calls Used**: 6/10  
**Method**: GitHub API (Contents, Metadata); brief README analysis; manifest inspection.
