# July 2025 Redeye — Extract-or-Archive Audit (2026-04-27)

**Scope:** API-only audit of repos created 2025-06-15 → 2025-08-31 (July 2025 redeye era + adjacent weeks).
**Method:** `gh api users/KooshaPari/repos` filtered by `created_at`, README + root-listing probe, cross-reference vs current active Phenotype org repos.
**Total in window:** 11 repos.
**User stance:** Reference-only by default; surface only extractable value that overlaps current active work.

## Decision Bucket Counts

| Bucket | Count | Repos |
|--------|-------|-------|
| KEEP-AND-FINISH | 1 | GDK |
| EXTRACT-THEN-ARCHIVE | 5 | KaskMan, KlipDot, kwality, KWatch, vibe-kanban |
| ARCHIVE (no extractable value) | 5 | kmobile, KodeVibe, KodeVibeGo, KommandLineAutomation, RIP-Fitness-App |

Note: 10/11 are already `archived=true` on GitHub. GDK is the only active one.

## Per-Repo Decisions

### KEEP-AND-FINISH

#### GDK (Rust, 249 MB, created 2025-07-10, pushed 2026-04-26)
README: "Git Workflow Deep Knowledge system for AI agents with thread-based quality tracking — Enterprise-ready git workflow system for AI agents with infinite monkey theorem convergence"
**Decision: KEEP-AND-FINISH.** Active push as of 2026-04-26; full spec stack (PRD, FR, PLAN, ADR). Memory entry `argis_gdk_state_verify_2026_04_27.md` exists. Genuine ongoing value. No extraction needed.

### EXTRACT-THEN-ARCHIVE

#### KaskMan (JS, 36 MB, archived, created 2025-07-07)
README: persistent always-on R&D platform with CLI/API/MCP/dashboard.
**Extract:**
- `dashboard-tui.js` + `dashboard-server.js` + `dashboard-web.{html,css,js}` → reference for **Metron** health-dashboard work (`.worktrees/Metron/health-dashboard`).
- `architecture/` docs → **PhenoHandbook** R&D-platform reference.
- Skip: `claude-flow/` (superseded), `memory-storage.js` (superseded by AgentMCP).

#### KlipDot (Rust, 33 MB, archived, created 2025-07-08)
README: "Universal Terminal Image Interceptor" + kitty-graphics.
**Extract:**
- `src/` clipboard interception modules → potentially useful for **rich-cli skill** (kitty-graphics already mandated globally).
- `zsh-preview-integration.zsh` + `quick-preview.zsh` → **thegent/templates/** terminal integration examples.
- `SOTA.md` + `COMPREHENSIVE_TERMINAL_INTERCEPTION.md` → research index in `worklogs/RESEARCH.md`.
- Skip: full daemon (already in cliproxyapi/heliosLab).

#### kwality (Mixed/Make, 668 MB, archived, created 2025-07-07)
README: "LLM validation platform with DeepEval, Playwright MCP, and Neo4j knowledge graphs."
**Extract:**
- `engines/` LLM-validation harnesses → **PhenoMCP** or **cheap-llm-mcp** test infrastructure.
- `python-tests/` DeepEval harness → reference for **AgilePlus** spec-verification tests.
- `swarm-research-findings.json` → archive in `worklogs/RESEARCH.md`.
- `k8s/` + `nginx/` + docker compose → skip (superseded by phenotype-infrakit).

#### KWatch (Go, 103 MB, archived, created 2025-07-07)
README: "fast, lightweight project monitoring tool — TUI panel + HTTP API for AI agent polling."
**Extract:**
- `tui/` + `server/` real-time build-status API → directly overlaps **agent-orchestrator** disk_check + **FocalPoint** target-pruner observability surfaces.
- `mcp/` → reference for **McpKit** lightweight MCP server pattern.
- `runner/` file-watching loop → reference for **PhenoObservability** watcher fix work.

#### vibe-kanban (TS+Rust, 94 MB, archived, created 2025-07-16)
README explicitly: "FOR REFERENCE AND FEATURE INSPIRATION / RESEARCH ONLY DO NOT DEVELOP HERE."
**Extract:**
- `frontend/` kanban UI patterns → **AgilePlus dashboard** (already has `agileplus dashboard` command + Spec Kitty kanban skill).
- `backend/` Rust task-execution model → reference for **AgilePlus** work-package state machine.
- `crates/` → skim for reusable agent-orchestration primitives.
- Already self-marked as reference-only; this codifies the extraction targets.

### ARCHIVE (no extractable value)

| Repo | Lang | Size | Reason |
|------|------|------|--------|
| kmobile | Rust | 226 KB | Skeleton only (Cargo.toml + src/ + README); replaced by KDesktopVirt/KVirtualStage rebuild track (eco-011). |
| KodeVibe | Shell | 21 KB | Single binary + install.sh; superseded by KodeVibeGo (also archived) → consolidated into HexaKit. |
| KodeVibeGo | Go | 27 MB | README explicitly: "deprecated, consolidated into HexaKit." Already extracted upstream. |
| KommandLineAutomation | Rust | 41 KB | "Playwright equivalent for CLI recordings" — minimal, no production value vs asciinema/agg. |
| RIP-Fitness-App | Kotlin | 730 KB | Personal Android fitness app; zero overlap with Phenotype org. |

## Recommended Migration Order (when user approves)

1. **Tier-1 (high overlap, do first):** KWatch tui/server → agent-orchestrator + FocalPoint observability.
2. **Tier-1:** vibe-kanban frontend/backend kanban patterns → AgilePlus dashboard.
3. **Tier-2:** KaskMan dashboard → Metron health-dashboard worktree.
4. **Tier-2:** kwality engines/python-tests → PhenoMCP / AgilePlus spec verification.
5. **Tier-3:** KlipDot kitty-graphics + zsh integration → thegent templates / rich-cli skill.
6. **Final:** Pure-archive bucket (no action; already archived on GitHub).

## Constraints Honored

- API-only; no clones, no archive operations, no PRs.
- Read-only audit. User reviews before any extraction action.
- Decisions follow user's "reference-only by default" stance — KEEP-AND-FINISH used only for GDK which is genuinely active.
