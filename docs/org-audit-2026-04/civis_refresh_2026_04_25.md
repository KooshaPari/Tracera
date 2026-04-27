# Civis Metadata Refresh (2026-04-25)

**Status:** KEEP-DEFERRED (governance complete, implementation pending W-67)

## Quick Facts

- **Purpose:** Deterministic simulation, policy-driven architecture, civil/civic infrastructure design workspace
- **Stack:** Rust (Edition 2024) + PostgreSQL + Axum + VitePress
- **Recent Activity:** 10 commits in last wave (2026-02 → 2026-04) focused on governance setup (CLAUDE.md, AGENTS.md, worklog, CI workflows)
- **Last Release:** None (no tags; pre-v1, scaffolding phase)
- **CHANGELOG Status:** Minimal ("Unreleased" with placeholder)

## CI & Workflows

- **Count:** 19 workflows in `.github/workflows/`
  - Standard enforcement: codeql, quality-gate, policy-gate, legacy-tooling-gate, fr-coverage
  - Documentation: docs-site, pages-deploy, pages, doc-links
  - Alert/admin: alert-sync-issues

## Cross-Repository References

Civis mentioned in Phenotype org catalog context:
- AgilePlus spec (019-private-repo-catalog): Task T031/T032 to "Audit Civis: civic data tools, gaps" and "Complete Civis: data processing pipelines, visualization, export"
- Duplication audit: 50+ LOC duplicated pattern shared with BytePort, Dino, Eidolon, FocalPoint (governance/config boilerplate)

## Verdict

**KEEP-DEFERRED** — Governance complete (CLAUDE.md, AGENTS.md, CI pipelines, worklog scaffold), awaiting user W-67 ("skip civis/parpour"). Implementation priority depends on Phenotype org roadmap. No blockers; cleanly parked.

---

**Duration:** ~2min | **Timestamp:** 2026-04-25T14:00Z
