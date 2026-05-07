# Security Audit Findings — 2026-05-04

**Scope**: Tracera repo (`/Users/kooshapari/CodeProjects/Phenotype/repos/Tracera`)
**Auditor**: OWL (automated sweep + manual review)
**Method**: Pattern search across workflows, Python, Rust, TypeScript, Docker, and config files.
**Constraint**: No worktree-based subagents (Disk pressure on this machine); all findings from direct in-repo reads and rg/grep.

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | 4     |
| MEDIUM   | 6     |
| LOW      | 5     |

---

## HIGH

### H-01: Path traversal in `LocalStorageManager` file operations
- **File**: `src/tracertm/storage/local_storage.py` (lines 18–63 in `__init__.py` legacy; same class in `local_storage.py`)
- **Issue**: `LocalStorageManager` constructs file paths directly from untrusted `item_id` / `link_id` values (`self.items_dir / f"{item_id}.json"`) without any normalization or containment check. A crafted identifier containing `../` can escape the intended storage directory.
- **Impact**: Arbitrary file read/write/delete outside storage root if attacker controls item/link IDs via API, import, or CLI.
- **Fix**: Resolve final path and enforce it stays under `base_path`. Reject absolute paths and path separators in IDs. Prefer server-generated opaque IDs.

### H-02: README describes wrong project (TracerTM / Phenotype-Enterprise/trace)
- **File**: `README.md` (lines 1–13)
- **Issue**: Badges point to `github.com/Phenotype-Enterprise/trace` (non-existent or wrong repo). Title says "TracerTM", URL says `kooshapari/tracertm`. Repo is `KooshaPari/Tracera`. Clear copy-paste contamination from another project.
- **Impact**: Confuses contributors, CI badge links broken, signals broader contamination risk — other docs/config may also be stale or wrong-project.
- **Fix**: Rewrite README to reflect Tracera. Update badge URLs to `KooshaPari/Tracera`. Audit all `.md` files for wrong-project references.

### H-03: `dependabot-auto-merge.yml` auto-merges without adequate test gating
- **File**: `.github/workflows/dependabot-auto-merge.yml` (lines 7–13, 103–138)
- **Issue**: Grants `contents: write` + `pull-requests: write` at workflow level. Auto-enables merge on patch/minor Dependabot PRs. The `verify-tests` job has conditional setup steps but no explicit test-execution step before merge. The merge job depends only on `should-merge` output from metadata check, not on actual test pass.
- **Impact**: Malicious or broken dependency updates could be auto-merged.
- **Fix**: Require all CI checks to pass before merge. Use `gh pr checks --strict` or branch protection. Scope permissions to job-level, drop workflow-level write.

### H-04: Overbroad workflow permissions (multiple files)
- **Files**: `test-pyramid.yml` (lines 9–12), `performance-regression.yml` (lines 50–51), `release-drafter.yml` (lines 16–17)
- **Issue**: `test-pyramid.yml` grants `issues: write` + `pull-requests: write` at workflow level — but only needs read for verification. `release-drafter.yml` grants `contents: write` + `pull-requests: write` — acceptable for the release job but not for any read-only jobs in the same workflow.
- **Impact**: Lateral movement if a step is compromised; broader blast radius.
- **Fix**: Move permissions to job-level. Grant minimum required permissions per job.

---

## MEDIUM

### M-01: Unpinned Go version in `openapi-docs.yml`
- **File**: `.github/workflows/openapi-docs.yml` (line 63)
- **Issue**: `swag init` installed via `go install github.com/swaggo/swag/cmd/swag@latest` — always pulls latest, not pinned.
- **Fix**: Pin to specific version: `go install github.com/swaggo/swag/cmd/swag@v1.x.y`.

### M-02: Schema validation runs without timeout
- **File**: `.github/workflows/schema-validation.yml` (lines 24+)
- **Issue**: No `timeout-minutes` set — a stuck validation can consume runner hours.
- **Fix**: Add `timeout-minutes: 15`.

### M-03: Raw SQL strings passed through `LegacyFriendlySession`
- **File**: `src/tracertm/storage/local_storage.py` (lines 26–46)
- **Issue**: `LegacyFriendlySession.execute()` accepts raw `str` SQL and passes it to `exec_driver_sql`. This bypasses SQLAlchemy's parameterized query safety, risking SQL injection if any user input reaches these paths.
- **Fix**: Migrate all raw SQL to SQLAlchemy `text()` with bound parameters. Deprecate `LegacyFriendlySession`.

### M-04: `.trace/` markdown parser trusts frontmatter IDs
- **File**: `src/tracertm/storage/local_storage.py` (lines 487–573)
- **Issue**: `item_id` extracted from YAML frontmatter is used directly in DB operations without validation. A malicious `.md` file in a cloned repo could inject arbitrary IDs.
- **Fix**: Validate UUID format for frontmatter IDs. Reject or regenerate invalid ones.

### M-05: Multiple workflows write PR comments using unsanitized step outputs
- **Files**: `openapi-docs.yml` (line 122), `test-validation.yml` (line 249), `performance-regression.yml` (line 497), `deployment-rollback.yml` (lines 77, 272, 327)
- **Issue**: PR comment bodies read from files or step outputs and post via `github.rest.issues.createComment`. If output contains markdown injection (e.g., `@mentions`, issue references), it could trigger unintended notifications or link to wrong issues.
- **Fix**: Sanitize comment bodies before posting. Avoid interpolating raw log output.

### M-06: `LLM` / `agent_execution.py` uses `unsafe.imports_passed_through()`
- **File**: `src/tracertm/workflows/agent_execution.py` (line 20)
- **Issue**: `workflow.unsafe.imports_passed_through()` in a workflow context signals potential for arbitrary code execution. If combined with untrusted input, this could be a code exec vector.
- **Fix**: Audit all callers. Pin allowed imports explicitly. Do not combine with user-controlled data.

---

## LOW

### L-01: `http://localhost` in load tests and Makefile
- **Files**: `load-tests/*.js`, `Makefile.gateway`, `llms.txt`
- **Issue**: All use `http://` for local development URLs — acceptable for dev but `llms.txt` is served publicly and leaks internal port numbers.
- **Fix**: Remove or gate `llms.txt` from production builds. Use `127.0.0.1` instead of `localhost` to avoid DNS rebinding.

### L-02: `go-version: '1.23'` in `openapi-docs.yml` may drift
- **File**: `.github/workflows/openapi-docs.yml` (line 38)
- **Issue**: Hardcoded Go version without auto-update mechanism.
- **Fix**: Use a shared Go version variable or dependabot config for tool versions.

### L-03: Missing `retention-days` on some artifacts
- **Files**: Various workflow artifact upload steps
- **Issue**: Some `actions/upload-artifact` steps omit `retention-days`, defaulting to 90 days.
- **Fix**: Explicitly set `retention-days: 7` for all workflow artifacts.

### L-04: `vault/client.py` defaults to plaintext HTTP
- **File**: `src/tracertm/vault/client.py` (line 90)
- **Issue**: Default Vault addr is `http://127.0.0.1:8200` — fine for local dev but no TLS enforcement. If deployed, traffic would be unencrypted.
- **Fix**: Require `https://` in non-development environments. Add config validation.

### L-05: Multiple stale/duplicate workflow files
- **Observation**: Several workflow files appear to be legacy or redundant (`schema-validation.yml`, `test-validation.yml`, `chaos-tests.yml`). Unused workflows still trigger on paths and consume CI minutes.
- **Fix**: Audit workflows, archive unused ones, consolidate overlapping jobs.

---

## Contamination / Project Identity Issues

| File | Issue |
|------|-------|
| `README.md` | Badges point to `Phenotype-Enterprise/trace`; title says "TracerTM" |
| `docs/` (various) | Some docs reference "TracerTM" or "trace" instead of "Tracera" |
| `llms.txt` | References `tracertm` paths and ports |
| `python_loc_audit.txt` | References "API Layer (`src/tracertm/api/`)" — structure mismatch |

**Recommendation**: Run a full-repo grep for `TracerTM`, `tracertm`, `Phenotype-Enterprise/trace`, and `kooshapari/tracertm`. Decide which references are legitimate module names vs. stale project names, then mass-update.

---

## DAG Extension — New Tasks to Track

| ID | Task | Priority |
|----|------|----------|
| A-01 | Fix path traversal in `LocalStorageManager` | HIGH |
| A-02 | Rewrite README.md for Tracera identity | HIGH |
| A-03 | Add test-gate to `dependabot-auto-merge.yml` | HIGH |
| A-04 | Scope workflow permissions to job-level (5 files) | HIGH |
| A-05 | Pin `swag` version in `openapi-docs.yml` | MEDIUM |
| A-06 | Add `timeout-minutes` to `schema-validation.yml` | MEDIUM |
| A-07 | Deprecate `LegacyFriendlySession` raw SQL passthrough | MEDIUM |
| A-08 | Validate frontmatter IDs in markdown indexer | MEDIUM |
| A-09 | Sanitize PR comment bodies in 5 workflows | MEDIUM |
| A-10 | Audit `agent_execution.py` unsafe imports | MEDIUM |
| A-11 | Full-repo contamination sweep (wrong-project refs) | HIGH |

---

*Generated: 2026-05-04T00:00:00Z*
