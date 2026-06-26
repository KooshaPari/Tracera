# Tracera Documentation Recovery Catalog

**Scan date:** 2026-06-26  
**Repository:** [KooshaPari/Tracera](https://github.com/KooshaPari/Tracera)  
**Recovery branch:** `docs/tracera-recovery-v2`  
**Source commit for restored content:** `9e78f48dd^` (parent of bulk deletion in `9e78f48dd`)

## Summary

| Metric | Count |
|--------|------:|
| `docs/**/*.md` files deleted since 2025-12-01 | **2,789** |
| High-value pages selected for restoration | **6** |
| Pages restored on recovery branch | **6** |
| Current mounted `/api/v1` routes (June 2026) | **17** |
| Contract-only unmounted routes | **8** |
| Operational probes | **2** (`/health`, `/ready`) |

## How the regression was detected

```bash
git log --all --since="2025-12-01" --diff-filter=D --name-only -- 'docs/' \
  | grep -iE '\.md$' | sort -u
```

This surfaced ~2,789 deleted markdown paths under `docs/`, including entire numbered trees
(`docs/00-overview/` … `docs/08-reference/`), `docs/guides/` (hundreds of files), and legacy docsets.

Recent `docs/` activity (post-Dec 2025) is dominated by audit/harmonization passes (#655–#662) on the
**slim** docs set now on `main`, not by restoring the pre-consolidation corpus.

## Deletion event

| Field | Value |
|-------|-------|
| Commit | `9e78f48dd` |
| Message | `fix(security): require secrets from env, drop hardcoded dev fallbacks (#554)` |
| Effect | Removed large pre-consolidation documentation trees alongside security cleanup |
| Recovery SHA | `9e78f48dd^` (`git show 9e78f48dd^:<path>`) |

## What existed (representative high-value paths)

These categories were present before consolidation and are **not** on current `main`:

| Category | Example paths | Status on `main` before recovery |
|----------|---------------|----------------------------------|
| Getting started | `docs/01-getting-started/README.md`, `CLI_TUTORIAL.md`, `START_HERE.md` | Missing |
| Guides | `docs/04-guides/DEVELOPER_GUIDE.md`, `DEPLOYMENT_GUIDE.md`, `mcp-cli-api-matrix.md` | Missing |
| API reference hub | `docs/06-api-reference/README.md` (+ sibling `api-documentation.md`) | Missing (stub `docs/API_REFERENCE.md` only) |
| Overview / planning | `docs/00-overview/*`, `docs/03-planning/*` | Missing (not restored — superseded by audit docs) |
| Mass guide library | `docs/guides/*` (~700+ files) | Missing (not restored — high noise) |

## What regressed (user-facing impact)

1. **Onboarding gap** — no `docs/01-getting-started/` entrypoint; `docs/index.md` links to pages that
   moved or never returned (`SECURITY.md` at root vs `docs/security/SECURITY.md`).
2. **Developer / deployment guides removed** — `docs/04-guides/` workflow and ops content gone.
3. **API hub broken** — `docs/06-api-reference/README.md` pointed at deleted siblings; only
   `docs/API_REFERENCE.md` (June 2026 stub) remained.
4. **Client matrix lost** — MCP/CLI/API capability doc removed despite still-relevant offline/online model.

## Pages restored (this branch)

| Restored path | Type | Source | Light updates applied |
|---------------|------|--------|------------------------|
| [`01-getting-started/README.md`](../01-getting-started/README.md) | Getting started | `9e78f48dd^` | Repointed links to `quickstart.md`, `API_REFERENCE.md`, `ARCHITECTURE.md` |
| [`01-getting-started/CLI_TUTORIAL.md`](../01-getting-started/CLI_TUTORIAL.md) | Tutorial | `9e78f48dd^` | Recovery banner; note on 17 mounted HTTP routes |
| [`04-guides/DEVELOPER_GUIDE.md`](../04-guides/DEVELOPER_GUIDE.md) | Guide | `9e78f48dd^` | Recovery banner; governance/API cross-links |
| [`04-guides/DEPLOYMENT_GUIDE.md`](../04-guides/DEPLOYMENT_GUIDE.md) | Guide | `9e78f48dd^` | Added `TRACERA_JWT_*` env vars; mounted-route note |
| [`06-api-reference/README.md`](../06-api-reference/README.md) | API hub | Rewritten | Replaced dead links with current contract + traceability map |
| [`04-guides/mcp-cli-api-matrix.md`](../04-guides/mcp-cli-api-matrix.md) | API / clients | `9e78f48dd^` | Mounted-route counts; JWT auth note |

### Intentionally not restored

| Path | Reason |
|------|--------|
| `docs/01-getting-started/START_HERE.md` | 500+ line research delivery doc; superseded by audit/architecture docs on `main` |
| `docs/00-overview/*`, `docs/guides/*` | Volume/noise; many stale links; covered partially by `FEATURE_INVENTORY.md` + audit parts |
| `docs/06-api-reference/api-documentation.md` | Superseded by [`API_REFERENCE.md`](../API_REFERENCE.md) + endpoint traceability map |

## Current API reality (June 2026)

Authoritative source: [`governance/policy/endpoint_traceability_map.md`](../governance/policy/endpoint_traceability_map.md)

**Mounted (17):** auth, evidence (×3), impact POST, coverage-matrix, spec-check, confidence,
org-intel (×3), sdlc-pm (×4).

**Unmounted (8):** code-trace, impact forward/reverse, blast-radius, ingest github/jira, comments (×3).

**Probes (2):** `/health`, `/ready`.

## Follow-up recommendations

1. Update [`index.md`](../index.md) to link restored getting-started and guide paths.
2. Add redirect stubs for common broken index targets (`SECURITY.md`, old `02-architecture/` paths).
3. Decide whether to recover `docs/04-guides/config-precedence.md` (referenced historically, still missing).
4. Keep `API_REFERENCE.md` as SSOT for paths; use `06-api-reference/README.md` as navigation hub only.

## Recovery commands (for auditors)

```bash
# List deleted docs since Dec 2025
git log --all --since="2025-12-01" --diff-filter=D --name-only -- 'docs/' \
  | grep -iE '\.md$' | sort -u | wc -l

# Show last version before deletion
git show '9e78f48dd^:docs/04-guides/DEVELOPER_GUIDE.md' | head

# Verify restored files on recovery branch
git diff main...docs/tracera-recovery-v2 -- docs/
```

---

_Generated by docs regression recovery pass — do not auto-edit; update manually when restoring additional pages._
