# MCP Repos Re-Verification — 2026-04-26

**Audit Date:** 2026-04-26  
**Prior Audits:** `userstory-mcpkit-firstrun-2026-04-26.md`, `userstory-phenomcp-firstrun-2026-04-26.md`  
**Verification Scope:** PR #485/#494 (McpKit), PR #499/#12 (PhenoMCP)

---

## 1. McpKit (KooshaPari/McpKit)

**Status**: Fixed since last audit

PR #21 (Quick Start docs fix) and PR #22 (submodule re-pin) have merged successfully. The Quick Start section in README.md now contains concrete, actionable steps: clone, explore governance files (CLAUDE.md/AGENTS.md/PRD.md), and language-specific build examples with real commands. The submodule reference to `python/pheno-mcp` has been re-pinned to a reachable SHA, unblocking local development workflows. 

Last commit: `2026-04-26T01:44:30Z` (PR #22 merged). Open issues: 0. No outstanding blockers.

**Top Finding**: The Quick Start now correctly directs users to read governance-first (CLAUDE.md, AGENTS.md) before exploring language stacks—aligning with policy that all feature work requires AgilePlus spec. However, no inline links to AgilePlus or the spec-kitty dashboard; consider adding `See AgilePlus/kitty-specs/<feature>` pointers in governance sections.

---

## 2. PhenoMCP (KooshaPari/PhenoMCP)

**Status**: Fixed since last audit

PR #12 (replaced fictional README content) merged cleanly at `2026-04-26T01:49:06Z`. The README now contains honest, pre-foundational status language: describes core MCP server wiring, tool/resource/auth components, and accurate project structure. No more aspirational feature claims. Quick Start section is concrete: clone, review CLAUDE.md and architecture docs, build with cargo, run tests, start server, and verify via mcp-inspector.

Last commit: `2026-04-26T01:49:06Z`. Open issues: 0. CI pipeline (Scorecard, CodeQL, dependencies) passing.

**Top Finding**: README now accurately reflects pre-foundational state and removes all fictional implementations (no longer claims "pre-built MCP servers for common Phenotype services" as delivered). However, example invocation `mcp-inspector --url stdio:///path/to/server` is generic; recommend adding a tagged example in docs/examples/ with actual pheno-mcp server config to reduce friction for first-time users.

---

## Summary

| Repo | Status | Last Commit | Key Merge | Finding |
|------|--------|-------------|-----------|---------|
| **McpKit** | Fixed | 2026-04-26T01:44:30Z | PR #22 submodule re-pin | Quick Start valid; add AgilePlus spec links |
| **PhenoMCP** | Fixed | 2026-04-26T01:49:06Z | PR #12 honest README | README de-fictionalized; add concrete examples |

Both repos have cleared audit gaps. Recommendations are polish-tier (documentation links and examples), not blocking issues.
