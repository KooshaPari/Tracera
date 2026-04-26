# User-Story Batch 9: Repository State Checks — 2026-04-26

## Overview

Verification of three repository states per memory audit + cross-project reuse protocol:

| Repo | Status | Notes |
|------|--------|-------|
| `KooshaPari/phenoXddLib` | ARCHIVED | Confirmed via API; distinct from active `KooshaPari/phenoXdd` (xDD compendium) |
| `KooshaPari/phenotype-shared-secrets` | 404 (RENAMED) | Renamed to `phenotype-shared` per 2026-04-25 memory; no further audit needed |
| `KooshaPari/agentapi-plusplus` | ACTIVE | Last push 2026-04-26T02:51:37Z; Quick Start docs current |

---

## Detailed Findings

### 1. KooshaPari/phenoXddLib

**State:** ARCHIVED

```
archived:   true
description: Cross-cutting xDD utilities library: property testing, contract verification, mutation coverage
homepage:   (null)
```

**Action:** Skip in cleanup audits per archived-repos-locked reference. This repo contains xDD library code that was consolidated or superseded.

**Distinct from:** `KooshaPari/phenoXdd` (active, curated xDD compendium).

---

### 2. KooshaPari/phenotype-shared-secrets

**State:** 404 NOT FOUND

```
Response: {"message":"Not Found","documentation_url":"...","status":"404"}
```

**Resolution:** Repo was renamed to `phenotype-shared` (ID 1190541801) per session 2026-04-25 memory. GitHub redirects old name. This is expected behavior.

**Action:** No audit needed; update any cross-project references to point to `phenotype-shared` if they exist.

---

### 3. KooshaPari/agentapi-plusplus

**State:** ACTIVE (Just Updated)

```
pushed_at:         2026-04-26T02:51:37Z
default_branch:    main
description:       HTTP API for Claude Code, Goose, Aider, Gemini, Amp, and Codex
```

**Quick Start Status:**

- Binary download available for macOS/Linux (amd64, arm64)
- Server runs on port 3284
- OpenAPI schema: `http://localhost:3284/openapi.json`
- Chat interface: `http://localhost:3284/chat` (static HTML)
- Supports 10+ agent types (Claude Code, Cursor, Aider, Goose, Codex, Gemini, Copilot, Amp, Amazon Q, Auggie)
- Endpoints: `/messages`, `/message`, `/status`, `/events`, `/health`, `/version`, `/info`
- Default allowed host: `localhost` (configurable via `AGENTAPI_ALLOWED_HOSTS`)

**Key Note:** Requires explicit `--type` flag when running (e.g., `agentapi server --type claude -- claude`).

**Latest PRs (2026-04-26):**
- PR #466 & #467 both merged into main
- No new issues blocking deployment

---

## Cross-Project Reuse Implications

### Candidate Extractions
None identified in this batch. `phenoXddLib` (archived) and `phenotype-shared-secrets` (renamed) are not active development paths. `agentapi-plusplus` is a standalone tool repo with no obvious extraction candidates at this review scope.

### Related Shared Modules
- `phenotype-shared` (ID 1190541801) — 12 workspace members, 4 shared crates; consolidated alias for phenotype-shared-secrets
- `phenotype-infrakit/agent-orchestrator` — uses agentapi-plusplus for agent dispatch coordination

---

## Recommendations

1. **phenoXddLib:** Treat as archived reference; skip in active audits.
2. **phenotype-shared-secrets:** Update any cross-repo links to use `phenotype-shared` canonical name. GitHub redirects old name (no breakage).
3. **agentapi-plusplus:** Quick Start docs are current. Mark as "high priority" if planning a new agent control initiative (e.g., swarm orchestrator, multi-agent dispatch).

---

## Session Reference

- Memory: `reference_archived_repos_locked.md`, `reference_phenoshared_alias.md`
- Related repos: `phenotype-infrakit`, `agent-orchestrator`, `phenotype-shared`
- Batch scope: GitHub Contents API (8 calls; completed within cap)
