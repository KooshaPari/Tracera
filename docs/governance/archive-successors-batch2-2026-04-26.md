# Archive Successors — Batch 2 (2026-04-26)

Deprecation status checks for 3 archived repos. Completed via GitHub Contents API; no modifications made to archived repos.

---

## 1. KaskMan (OpenClaw R&D predecessor)

**Original Purpose:** Persistent, always-on, self-improving utility and R&D platform (Node.js) with CLI, REST API, MCP server, web dashboard, and advanced security (JWT, rate limiting, CORS).

**Stack:** Node.js 18+, npm, PostgreSQL, Redis

**Current Status:** Archived 2026-04-06. Last activity: 2026-04-06.

**Successor:** No direct successor documented. This was an idealistic multi-interface R&D experiment. Functionality has been superseded by:
- **MCP Servers**: phenotype-infrakit/phenotype-mcp (canonical MCP server platform)
- **REST APIs**: Individual service APIs across phenotype repos (AgilePlus, thegent, etc.)
- **CLI Tools**: Rust-based CLI tooling (clap + anyhow stack, per scripting policy)

**Recommended Action:** Preserve as-is. No deprecation banner needed (already archived and marked inactive). If inbound links exist, update them to point to phenotype-mcp or relevant phenotype service. Not a candidate for immediate deletion — represents significant R&D investment.

---

## 2. KodeVibeGo (Go linter consolidated into HexaKit)

**Original Purpose:** Go code quality linter and scanning component within Phenotype ecosystem.

**Stack:** Go

**Current Status:** Archived and explicitly marked "STRICTLY DO NOT DELETE NOR UNARCHIVE" in README. Last activity: 2026-04-25. Documented successor: KooshaPari/HexaKit.

**Successor:** **KooshaPari/HexaKit** (verified live, not archived)
- KodeVibeGo functionality consolidated into phenotype-infrakit (the actual canonical repo for infrastructure libs)
- HexaKit is an alias or refactor of phenotype-infrakit

**Recommended Action:** Deprecation banner NEEDED. Add to repo's README:

```markdown
## Status: ARCHIVED & DEPRECATED

This repository has been archived. Its functionality has been consolidated into:

**[KooshaPari/HexaKit](https://github.com/KooshaPari/HexaKit)** (Phenotype Infrastructure Kit)

For Go linting and code quality scanning, see:
- phenotype-infrakit Go scanning module (TBD: exact path)
- KooshaPari/HexaKit for active development

This repo is preserved for historical reference only. Do not unarchive.
```

---

## 3. worktree-manager (git worktree automation)

**Original Purpose:** Git worktree automation and management toolkit with hexagonal architecture. Provides CLI (wtm) for listing, creating, removing, locking, and cleaning worktrees.

**Stack:** Rust (hexagonal architecture; SOLID/DRY/KISS principles)

**Current Status:** Archived 2026-04-26. Last activity: 2026-04-26 (very recent archival). Marked with `deprecated` topic.

**Successor:** No direct successor identified. Worktree management functionality is now handled by:
- **EnterWorktree / ExitWorktree** — native tools in Claude Code harness (system-level worktree APIs)
- **Project worktree wrappers** — each phenotype repo uses `.claude/worktree-manage.sh` or equivalent (if any)

Reason for archival: Project-specific worktree logic is now embedded in Claude Code harness and per-project scripts. The standalone wtm CLI became redundant as worktree orchestration was integrated into the local development workflow.

**Recommended Action:** Preserve as-is (already archived). If teams reference wtm, redirect them to:
- Claude Code's EnterWorktree tool (native support)
- Per-project worktree management scripts (check CLAUDE.md for project-specific patterns)

Candidate for future deletion (no active dependencies known), but preserve for now as a reference for worktree design patterns.

---

## Summary Table

| Repo | Purpose | Status | Successor | Action |
|------|---------|--------|-----------|--------|
| **KaskMan** | Always-on R&D platform (Node.js, multi-interface) | Archived | phenotype-mcp, service APIs | Preserve; update inbound links if any |
| **KodeVibeGo** | Go linter consolidation | Archived, explicit "DO NOT UNARCHIVE" | KooshaPari/HexaKit (phenotype-infrakit) | **Add deprecation banner to README** |
| **worktree-manager** | Git worktree CLI toolkit | Archived (very recent) | Claude Code EnterWorktree, project scripts | Preserve; redirect to native tools |

---

## Next Steps

- [ ] Update KodeVibeGo README with deprecation banner (includes link to HexaKit)
- [ ] Scan phenotype-infrakit/phenotype-mcp for any inbound links to archived repos; update if found
- [ ] Update governance docs if any reference KaskMan's multi-interface pattern or worktree-manager's design
