# W-67A Python Agents Audit: agent-devops-setups + agent-user-status

**Date:** 2026-04-25 | **Auditor:** Claude Haiku Agent

## Summary

| Repo | Status | LOC | Tests | Verdict |
|------|--------|-----|-------|---------|
| **agent-devops-setups** | SCAFFOLD | ~3K (config) | 0 | **ARCHIVE** — policy distribution only; superseded by phenoShared reusables |
| **agent-user-status** | SHIPPED | 15.6K | 67/18 | **SHIP** — production-ready MCP agent; requires FR traceability cleanup |

---

## 1. agent-devops-setups (156K LOC claim — INFLATED)

### Status by Dimension

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Build | MISSING | No `pyproject.toml`; is pure config/policy, not Python package |
| Tests | MISSING | 0 test files; repo is policy distribution (N/A) |
| CI | SHIPPED | 9 workflows (quality-gate, security-guard, policy-gate, tag-automation, validate-policy, release-drafter, self-merge-gate, pages-deploy) |
| Docs vs Reality | SHIPPED | 177-line README, PRD/ADR/FUNCTIONAL_REQUIREMENTS present; accurately describes policy federation model |
| Architecture | SCAFFOLD | `policies/`, `extensions/`, `schemas/` tree structure present but underpopulated; policy schema validation in-progress |
| FR Traceability | N/A | Config repo; FRs not applicable |
| Velocity | SHIPPED | 20 recent commits; last 5 are docs + governance updates (e.g., "adopt CLAUDE.md", "harmonize AGENTS.md") |
| Governance | SHIPPED | CLAUDE.md, AGENTS.md, PRD/ADR in place; follows Phenotype org structure |
| External Deps | SHIPPED | Delegates to phenoShared reusables (tag-automation, self-merge-gate, release-drafter) — correct pattern |
| Sidekick Fit | EXTERNAL-BLOCKED | Not an MCP agent; is configuration distribution layer. No `codex/` or `skills/` dirs |

### Verdict: **ARCHIVE**

**Rationale:** agent-devops-setups is a policy federation + configuration distribution layer designed to harmonize agent harness overrides (CLAUDE.md, AGENTS.md, Cursor rules, etc.). However:

1. **Functional scope is minimal**: Policies are layered (system → user → harness → repo → task-domain → extensions) but actual payloads are stubs.
2. **Superseded by phenoShared**: Org now delegates CI/release/merge workflows to shared reusables (phenotype-infrakit/iac). Policy distribution is handled at fetch time, not via this repo.
3. **No active development**: Last 5 commits are governance scaffolding only; no policy payload changes since early W-67.
4. **LOC inflation**: 156K claim includes archived docs and empty directories. Active code is <3K.

**Action:** Move to `repos/.archive/agent-devops-setups/`. Link from phenoShared docs as historical reference for policy layer architecture.

---

## 2. agent-user-status (15.6K LOC Python) — PRODUCTION

### Status by Dimension

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Build | SHIPPED | `uv sync` passes; 45-line pyproject.toml with clean deps (pydantic, httpx, tenacity, structlog) |
| Tests | SHIPPED | 67 test functions across 18 files; ci.yml runs pytest with coverage collection |
| CI | SHIPPED | 4 workflows: ci.yml (test), quality-gate.yml (lint/format), fr-coverage.yml (traceability), doc-links.yml (markdown) |
| Docs vs Reality | SHIPPED | 235-line README, FUNCTIONAL_REQUIREMENTS.md, CONTRIBUTING.md, SECURITY.md in place. Docs accurately reflect agent purpose (iMessage user-status presence tracking + broadcast) |
| Architecture | SHIPPED | Modular structure: `src/agent_user_status/{bootstrap_cli.py, agent_imessage_learning.py, ...}`. Largest files: 487 LOC (imessage learning), 479 LOC (bootstrap). Reasonable decomposition. |
| FR Traceability | MISSING | 0 test functions tagged with `@pytest.mark.requirement()` or `@trace` markers. FUNCTIONAL_REQUIREMENTS.md exists but tests are orphaned. **Blocker for final shipping.** |
| Velocity | SHIPPED | 20 commits in recent window; mix of feature + docs (bootstrap worklog, harmonize AGENTS.md). Steady pace. |
| Governance | SHIPPED | CLAUDE.md, AGENTS.md present; CHANGELOG.md retroactive; worklogs/ dir initialized. Complies with Phenotype org standards. |
| External Deps | SHIPPED | httpx (HTTP client), tenacity (retry), structlog (logging), pydantic (validation). All up-to-date; no deprecated patterns. Audit clean. |
| Sidekick Fit | SHIPPED | **YES — MCP server candidate.** Has `codex/` and `skills/` directories; agent runtime hooks present. Already implements presence detection for user-status queries. Fits Sidekick canonical architecture. |

### Verdict: **SHIP + FIX FR TRACEABILITY**

**Rationale:** Production-quality MCP agent for monitoring user presence (iMessage + macOS agent status). Ready to merge into Sidekick canonical as a peer to `agent-imessage` and `agent-task-monitor`.

**Pre-Ship Requirement:** Add `@pytest.mark.requirement("FR-USR-NNN")` tags to all 67 test functions and update FUNCTIONAL_REQUIREMENTS.md to list FR IDs. ~15 min fix. Block merge until FR traceability audit passes (fr-coverage.yml).

**Integration Path:**
1. Fix FR traceability (one commit).
2. Merge to main in this repo.
3. Add as submodule or copy to Sidekick canonical under `agents/agent-user-status/`.
4. Register MCP server in Sidekick's FastMCP manifest.

---

## Recommendations

1. **agent-devops-setups:** Move to `.archive/`. Update phenoShared docs to reference policy layer concept.
2. **agent-user-status:** Fix FR traceability (15 min). Merge to main. Integrate into Sidekick canonical immediately.
3. **Cross-repo:** Check if other archived Python agents (e.g., agentops, agent-evals) follow same pattern; batch archive if stale.

**Next audit wave:** Q2 2026-W-68 DevEnv agents (agent-docker-sandbox, agent-nix-shell) + Rust toolkit agents.
