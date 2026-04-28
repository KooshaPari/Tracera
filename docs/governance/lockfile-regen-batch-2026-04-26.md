# Lockfile-Regen Batch — 2026-04-26

Repos where Dependabot alerts can be cleared by lockfile regeneration alone (no manifest version bumps required, all constraints already permit patched versions).

## Batch Members

| Repo | Lockfile | Alerts Cleared (est.) | Critical | Notes |
|------|----------|----------------------|----------|-------|
| QuadSGM | `uv.lock` | 36 / 37 | 2 (fastmcp, authlib) | `lupa` no patch — residual; `pyproject` has duplicate fastmcp constraint |

## Standard Procedure

For each repo:

1. Enter worktree: `repos/<repo>-wtrees/dep-lockfile-regen`
2. Run lockfile regen for the ecosystem:
   - `uv.lock` → `uv lock --upgrade`
   - `Cargo.lock` → `cargo update`
   - `package-lock.json` → `npm update --package-lock-only`
   - `pnpm-lock.yaml` → `pnpm update --lockfile-only`
   - `poetry.lock` → `poetry lock --no-update=false`
   - `go.sum` → `go get -u ./... && go mod tidy`
3. Commit: `chore(deps): regenerate <lockfile> to clear N dependabot alerts`
4. Push, verify alerts close via `gh api repos/<r>/dependabot/alerts?state=open`
5. Document residual unpatched advisories in repo `SECURITY.md` or governance worklog

## Per-Repo Triage Docs

- QuadSGM: [`quadsgm-37-alert-triage-2026-04-27.md`](./quadsgm-37-alert-triage-2026-04-27.md)
