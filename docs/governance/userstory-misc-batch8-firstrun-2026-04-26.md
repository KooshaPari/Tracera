# User-Story Walkthroughs: Misc Tier-3 Repos — Batch 8

**Date:** 2026-04-26  
**Scope:** Brief Contents API status checks + truth-state summaries for 4 tier-3 repos  
**Total Calls:** 8 (gh api × 4 repos, 2 per repo)

---

## Summary Table

| Repo | Status | ID | Archived | Stack | Truth-State |
|------|--------|-----|----------|-------|------------|
| **phenodocs** | ✅ EXISTS | 1202025236 | No | VitePress + Bun + Python | Active docs federation hub; VitePress portal for Phenotype ecosystem aggregation |
| **Pyron** | ❌ **404** | — | — | — | Not found in KooshaPari GitHub; no redirect; archived or deleted |
| **FixitRs** | ❌ **404** | — | — | — | Not found in KooshaPari GitHub; no redirect; archived or deleted |
| **PhenoAgent** | ✅ EXISTS | 1220444508 | No | Rust + Go | Extracted agent core/daemon/CLI framework; multi-workspace; grpc + skills + multi-model routing |

---

## Repository Details

### 1. phenodocs — ACTIVE

**ID:** 1202025236 | **Archived:** No | **Private:** No

**Purpose:**  
VitePress federation hub — aggregates documentation from multiple Phenotype projects into a unified searchable portal. Serves as the documentation aggregation layer for the org.

**Tech Stack:**
- VitePress 1.x (static docs)
- Bun 1.x (package manager)
- Python 3.14+ (tooling, doc generation)
- GitHub Pages deployment

**Current State:**
- README present and up-to-date (federation concept, live demo link, features documented)
- CLAUDE.md present (AgilePlus-tracked, standard repo governance)
- Full-turn delivery documented in `docs/guides/full-turn-delivery.md`
- Deployment workflow active (GitHub Pages badge green)

**Assessment:**  
Healthy, active tier-3 documentation coordination project. Core purpose is clear: unified docs portal. No critical gaps observed. Tracking via AgilePlus as required.

---

### 2. Pyron — **NOT FOUND (404)**

**API Response:** `{"message":"Not Found","documentation_url":"...","status":"404"}`

**Findings:**
- No repository under `KooshaPari/Pyron` in GitHub
- No redirect or archived marker
- Not listed in org-wide archive batch (archive sweep 2026-04-25 was separate operation)

**Possible States:**
- Deleted explicitly
- Never pushed to GitHub (local-only prototype)
- Renamed without migration

**Action Required:**
- Confirm if this was intentional cleanup, archived locally, or migration in progress
- If abandoned, document in memory or archive tracker
- If active elsewhere (renamed), update references

---

### 3. FixitRs — **NOT FOUND (404)**

**API Response:** `{"message":"Not Found","documentation_url":"...","status":"404"}`

**Findings:**
- No repository under `KooshaPari/FixitRs` in GitHub
- No redirect or archived marker
- Memory task #75 flagged as 404; confirmed

**Possible States:**
- Deleted explicitly
- Renamed to a different slug
- Archived as tier-4 / deprecated

**Action Required:**
- Confirm if this was intentional archival, delete, or rename
- If task #75 correctly identified as 404, mark resolved
- If rename occurred, update all cross-project references

---

### 4. PhenoAgent — ACTIVE

**ID:** 1220444508 | **Archived:** No | **Private:** No

**Purpose:**  
Distributed agent orchestration framework with plugin architecture, skill system, and multi-model routing. Extracted from phenotype-infra as dedicated agent core/daemon/CLI.

**Tech Stack:**
- **Core:** Rust (agent daemon, policy enforcement)
- **API Gateway:** Go (CLI, HTTP API)
- **IPC:** gRPC + Protocol Buffers
- **Skills:** Registry with MCP-compatible tool adapters
- **Models:** Multi-model routing (Claude, GPT-4, Gemini, Ollama)
- **Storage:** Event-sourced SQLite backend
- **Async Runtime:** Tokio (Rust), Go concurrency

**Current State:**
- README present (framework overview, tech stack, features, quick start)
- CLAUDE.md present (governance, project structure, local quality checks)
- Multi-workspace Rust project with separate modules:
  - `phenotype-agent-core/` — Core runtime & traits
  - `phenotype-daemon/` — Daemon lifecycle & sockets
  - `agentapi/` — HTTP API gateway (Go, abstracted from CLIProxyAPI)
  - `pheno-cli/` — CLI interface
  - `docs/` — Architecture, runbooks, integrations
- Specs documented (ADR.md, PLAN.md, FUNCTIONAL_REQUIREMENTS.md)
- Agents.md and worklog.md present

**Assessment:**  
Healthy, actively maintained tier-3 framework project. Core abstraction extracted cleanly from parent. Skill system, multi-model routing, and daemon architecture well-scoped. Integration path with broader Phenotype ecosystem clear. No critical gaps.

---

## 404 Analysis

**Pyron** and **FixitRs** are confirmed missing from KooshaPari GitHub:
- Both return HTTP 404 from Contents API
- No archived repositories found under similar names
- No cross-repo references discovered in active repos (phenodocs, PhenoAgent)

**Recommendation:**
1. If these were intentionally archived/deleted in prior sessions, update memory reference list
2. If they represent abandoned prototypes, note in governance/archive tracker
3. If they were renamed, verify new slug and update all references in worklogs/memory

---

## Next Steps

- **phenodocs:** Continue standard AgilePlus-tracked workflow. Ready for integration work.
- **PhenoAgent:** Continue standard workflow. Multi-model routing and skill system expansion candidates for future phases.
- **Pyron & FixitRs:** Awaiting user confirmation on intent (archive, delete, rename). Once confirmed, update cross-project reference records.

---

**Session:** pre-extract/tracera-sprawl-commit  
**Verified:** 2026-04-26 via `gh api repos/KooshaPari/{phenodocs,Pyron,FixitRs,PhenoAgent}`
