# Dependency Alert Remediation Session - 2026-04-26

## Goal

Reduce live Tracera dependency alerts without letting the task become a broad
repo cleanup.

## SIZE-DEP: Keep Dependency Remediation Finishable

- **Cap:** one runtime/test dependency surface per PR unless alerts share the
  same lockfile.
- **Current size:** one Tracera PR branch; GitPython `uv.lock` hotfix in scope;
  broader Python lower-bound cleanup, Go Docker module alerts, frontend alerts,
  and archived npm snapshots are out of this patch.
- **Stop rule:** merge a PR that updates GitPython to the patched lockfile
  version and fixes the invalid project metadata required for `uv lock`.
- **Spillover:** create separate WBS items for Python lower-bound cleanup, Go
  Docker module investigation, frontend package bumps, and archive manifest
  quarantine.

## Alert Buckets

| Bucket | Scope | Action |
|---|---|---|
| GitPython | `uv.lock` | Patch in this lane. |
| Other Python | `pyproject.toml`, `uv.lock` | Separate Python dependency cleanup lane. |
| Go Docker module | `backend/**/go.mod` | Defer until a published fixed module tag or replacement module path is confirmed. |
| Frontend npm | `frontend/**` | Separate frontend dependency lane. |
| Archived npm snapshots | `ARCHIVE/CONFIG/default/**/package.json` | Separate archive quarantine task. |

## Validation Targets

```bash
uv lock --locked
uv run python -m compileall -q src
git diff --check
```
