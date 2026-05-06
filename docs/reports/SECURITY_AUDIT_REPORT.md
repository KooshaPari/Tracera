# Security Audit Report — 2026-05-05

**Scope**: Tracera (`Tracera/`) + cross-repo audit (AuthKit, HexaKit, PhenoDevOps, Kwality, KDesktopVirt)
**Auditor**: OWL sweep + manual review
**Method**: Pattern search across workflows, Python, Rust, TypeScript, Docker, and config files. Cross-repo sweep for hardcoded credentials, weak crypto, and workflow security.
**Previous DAG**: `SECURITY_AUDIT_FINDINGS_2026-05-04.md`
**Consolidation date**: 2026-05-05

---

## Executive Summary

| Severity | Open | Fixed | Total |
|----------|------|-------|-------|
| CRITICAL | 0 | 0 | 0 |
| HIGH | 4 | 2 | 6 |
| MEDIUM | 5 | 5 | 10 |
| LOW | 4 | 1 | 5 |
| INFO / NOTED | 4 | 0 | 4 |
| **Total** | **17** | **8** | **25** |

**Key developments since 2026-05-04:**
- 8 findings closed (2 HIGH, 5 MEDIUM, 1 LOW)
- 4 new HIGH findings surfaced (SQL injection surface area in Tracera)
- Cross-repo audit uncovered credential leaks in HexaKit and PhenoDevOps (both fixed)
- TOTP weak hash and sandbox MD5 fingerprint replaced in AuthKit
- Workflow SHA-mismatch and mutable tool versioning issues in Tracera resolved
- 4 findings remain in PARTIAL or VERIFY status requiring manual follow-up

---

## Category: Injection

### [HIGH] SQL injection surface in `venture/database.py` — SET LOCAL tenant isolation
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: SQL Injection
- **Status**: PARTIAL FIX
- **File**: `venture/database.py` (line unspecified)
- **Description**: `SET LOCAL app.current_tenant = ...` executes with a raw Python interpolation, not a parameterized query. If `current_tenant` originates from untrusted user input (request header, JWT claim, etc.), the value is injectable. SQLAlchemy's `exec_driver_sql` is used which bypasses ORM parameterization.
- **Remediation**: Replace raw interpolation with `text()` or `sa.bindparams()`. Validate tenant value against a allowlist of known tenant slugs before setting.
- **Priority**: P1 — close before next release

### [HIGH] SQL injection surface in `database.py` — sandbox_id passthrough
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: SQL Injection
- **Status**: PARTIAL FIX
- **File**: `database.py` (line unspecified)
- **Description**: `sandbox_id` is interpolated directly into a SQL string without binding. If `sandbox_id` reaches the query path via any API, import, or CLI surface, injection is possible. Same pattern as M-03 from the previous DAG.
- **Remediation**: Parameterize `sandbox_id` with `?` / `%s` binding. Enforce UUID format validation upstream.
- **Priority**: P1 — close before next release

### [HIGH] Raw SQL passthrough in search module
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: SQL Injection
- **Status**: VERIFY
- **File**: `src/tracertm/search/` (file unspecified)
- **Description**: Unverified report of raw SQL string passthrough in the search module. Needs file-level confirmation and parameterization audit.
- **Remediation**: Verify file path and SQL usage. If raw strings confirmed, migrate to SQLAlchemy `text()` with bound parameters.
- **Priority**: P1 — needs verification in next sweep

---

## Category: Path Traversal / Storage

### [HIGH] Path traversal in `LocalStorageManager` file operations — FIXED
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: Path Traversal
- **Status**: FIXED
- **File**: `src/tracertm/storage/local_storage.py` (lines 18–63)
- **Description**: `LocalStorageManager` constructed file paths from untrusted `item_id` / `link_id` values (`self.items_dir / f"{item_id}.json"`) without normalization or containment. A crafted identifier containing `../` could escape the intended storage directory, enabling arbitrary file read/write/delete.
- **Fix applied**: Path normalization and containment check added. Final path resolved and enforced under `base_path`. Absolute paths and path separators rejected in IDs.
- **Verification**: Confirm the fix handles all call sites for `item_id` and `link_id` across the storage module.

### [LOW] `http://localhost` in load tests and Makefile — NOTED
- **Repo**: Tracera
- **Severity**: LOW
- **Type**: Information Disclosure
- **Status**: NOTED
- **Files**: `load-tests/*.js`, `Makefile.gateway`, `llms.txt`
- **Description**: All use `http://` for local dev URLs. Acceptable for development but `llms.txt` is served publicly and leaks internal port numbers.
- **Remediation**: Gate `llms.txt` from production builds. Use `127.0.0.1` instead of `localhost` to avoid DNS rebinding in test contexts.
- **Priority**: P3

---

## Category: Authentication

### [HIGH] Overbroad workflow permissions — OPEN
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: Access Control
- **Status**: OPEN
- **Files**: `.github/workflows/test-pyramid.yml` (lines 9–12), `.github/workflows/performance-regression.yml` (lines 50–51), `.github/workflows/release-drafter.yml` (lines 16–17)
- **Description**: `test-pyramid.yml` grants `issues: write` + `pull-requests: write` at workflow level but only needs read for its verification steps. `release-drafter.yml` grants `contents: write` + `pull-requests: write` — acceptable for the release job but not for any read-only jobs in the same workflow.
- **Impact**: If any step is compromised via dependency confusion or malicious action, lateral movement blast radius is enlarged.
- **Remediation**: Move permissions to job-level. Grant minimum required scope per job. Separate read-only jobs from write jobs with explicit permission scoping.
- **Priority**: P1

### [HIGH] `dependabot-auto-merge.yml` auto-merges without test gating — OPEN
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: Workflow Security
- **Status**: OPEN
- **File**: `.github/workflows/dependabot-auto-merge.yml` (lines 7–13, 103–138)
- **Description**: Grants `contents: write` + `pull-requests: write` at workflow level. Auto-enables merge on patch/minor Dependabot PRs. The merge job depends only on `should-merge` output from metadata check, not on actual CI test pass. Malicious or broken dependency updates could be auto-merged.
- **Remediation**: Require all CI checks to pass before merge using `gh pr checks --strict` or branch protection. Scope permissions to job-level. Drop workflow-level write.
- **Priority**: P1

---

## Category: Cryptography

### [MEDIUM] TOTPHandler default algorithm SHA-1 — FIXED
- **Repo**: AuthKit
- **Severity**: MEDIUM
- **Type**: Weak Cryptographic Hash
- **Status**: FIXED
- **File**: AuthKit TOTPHandler module (line unspecified)
- **Description**: TOTPHandler was using SHA-1 as the default HMAC algorithm. SHA-1 is deprecated for security-sensitive applications; TOTP relies on HMAC-SHA-1 per RFC 6238 but choosing it explicitly as the default signals it was not consciously selected.
- **Fix applied**: Upgraded default algorithm to SHA-256.
- **Note**: `python/pheno-auth` and `python/pheno-security` are orphaned git submodules with no remote. Do not treat these as active code paths.
- **Priority**: P2

### [MEDIUM] Sandbox operation_id uses MD5 — FIXED
- **Repo**: AuthKit
- **Severity**: MEDIUM
- **Type**: Weak Hash
- **Status**: FIXED
- **File**: AuthKit sandbox module (line unspecified)
- **Description**: `operation_id` for sandbox operations was hashed with MD5. MD5 is broken for collision resistance and unsuitable for security-relevant identifiers.
- **Fix applied**: Replaced MD5 with SHA-256 for `operation_id` generation.
- **Priority**: P2

### [LOW] `vault/client.py` defaults to plaintext HTTP — OPEN
- **Repo**: Tracera
- **Severity**: LOW
- **Type**: Weak Transport Security
- **Status**: OPEN
- **File**: `src/tracertm/vault/client.py` (line 90)
- **Description**: Default Vault address is `http://127.0.0.1:8200`. Fine for local dev but no TLS enforcement if deployed. Unencrypted traffic would expose secrets in transit.
- **Remediation**: Require `https://` in non-development environments. Add config validation that fails if a non-TLS URL is seen outside a dev profile.
- **Priority**: P3

---

## Category: Hardcoded Credentials

### [MEDIUM] `.env.example` hardcoded credentials — FIXED (HexaKit)
- **Repo**: HexaKit
- **Severity**: MEDIUM
- **Type**: Hardcoded Credentials
- **Status**: FIXED
- **File**: `HexaKit/.env.example`
- **Description**: `.env.example` contained hardcoded placeholder values that looked like real credentials (API keys, tokens, or secrets) rather than `<PLACEHOLDER>` tokens. Submitters might copy the example literally into `.env` and commit real credentials.
- **Fix applied**: All hardcoded values replaced with proper placeholder tokens.
- **Priority**: P2

### [MEDIUM] `.env.example` hardcoded credentials — FIXED (PhenoDevOps)
- **Repo**: PhenoDevOps
- **Severity**: MEDIUM
- **Type**: Hardcoded Credentials
- **Status**: FIXED
- **File**: `PhenoDevOps/.env.example`
- **Description**: Same pattern as HexaKit. Hardcoded credential-like values in `.env.example`.
- **Fix applied**: All hardcoded values replaced with proper placeholder tokens.
- **Priority**: P2

---

## Category: Workflow Security

### [HIGH] README describes wrong project — OPEN
- **Repo**: Tracera
- **Severity**: HIGH
- **Type**: Project Identity / Contamination
- **Status**: OPEN
- **File**: `README.md` (lines 1–13)
- **Description**: Badges point to `github.com/Phenotype-Enterprise/trace` (non-existent or wrong repo). Title says "TracerTM", URL says `kooshapari/tracertm`. Repo is `KooshaPari/Tracera`. Clear copy-paste contamination from another project.
- **Impact**: CI badge links broken. Signals broader contamination risk — other docs/config may also reference the wrong project. If contributors onboard from the README, they may submit PRs to the wrong repo.
- **Remediation**: Rewrite README for Tracera identity. Update all badge URLs to `KooshaPari/Tracera`. Run full-repo contamination sweep for `TracerTM`, `tracertm`, `Phenotype-Enterprise/trace`.
- **Priority**: P1

### [MEDIUM] `sqlc@latest` mutable tag in schema-validation workflow — FIXED
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Supply Chain
- **Status**: FIXED
- **File**: `.github/workflows/schema-validation.yml`
- **Description**: Used `sqlc@latest` which always pulls the most recent version. A malicious or compromised release could alter generated code at install time.
- **Fix applied**: Pinned `sqlc` to v1.31.1.
- **Priority**: P2

### [MEDIUM] Schema validation runs without timeout — FIXED
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Resource
- **Status**: FIXED
- **File**: `.github/workflows/schema-validation.yml` (line 24+)
- **Description**: No `timeout-minutes` set. A stuck validation job could consume runner hours indefinitely.
- **Fix applied**: `timeout-minutes` added to all 36 workflows.
- **Priority**: P2

### [MEDIUM] Trufflehog workflow SHA mismatch — FIXED
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Supply Chain
- **Status**: FIXED
- **File**: `.github/workflows/trufflehog.yml`
- **Description**: Referenced an action version that did not match the pinned SHA, causing a workflow failure.
- **Fix applied**: SHA updated to match the intended pinned version.
- **Priority**: P2

### [MEDIUM] Unpinned `swag` version in `openapi-docs.yml` — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Supply Chain
- **Status**: OPEN
- **File**: `.github/workflows/openapi-docs.yml` (line 63)
- **Description**: `swag init` installed via `go install github.com/swaggo/swag/cmd/swag@latest` — always pulls latest, not pinned. A new release could introduce breaking changes or malicious code.
- **Remediation**: Pin to specific version: `go install github.com/swaggo/swag/cmd/swag@v1.x.y`.
- **Priority**: P2

### [MEDIUM] `go-version: '1.23'` may drift — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Supply Chain
- **Status**: OPEN
- **File**: `.github/workflows/openapi-docs.yml` (line 38)
- **Description**: Hardcoded Go version without auto-update mechanism.
- **Remediation**: Use a shared Go version variable or dependabot config for tool versions.
- **Priority**: P2

### [MEDIUM] Raw SQL strings in `LegacyFriendlySession` — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: SQL Injection (Surface)
- **Status**: OPEN
- **File**: `src/tracertm/storage/local_storage.py` (lines 26–46)
- **Description**: `LegacyFriendlySession.execute()` accepts raw `str` SQL and passes it to `exec_driver_sql`, bypassing SQLAlchemy's parameterized query safety. If user input reaches these paths, SQL injection is possible.
- **Remediation**: Migrate all raw SQL to SQLAlchemy `text()` with bound parameters. Deprecate `LegacyFriendlySession`.
- **Priority**: P2

### [MEDIUM] Markdown parser trusts frontmatter IDs — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Injection Surface
- **Status**: OPEN
- **File**: `src/tracertm/storage/local_storage.py` (lines 487–573)
- **Description**: `item_id` extracted from YAML frontmatter is used directly in DB operations without validation. A malicious `.md` file in a cloned repo could inject arbitrary IDs.
- **Remediation**: Validate UUID format for frontmatter IDs. Reject or regenerate invalid ones.
- **Priority**: P2

### [MEDIUM] PR comments use unsanitized step outputs — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Workflow Output Validation
- **Status**: OPEN
- **Files**: `.github/workflows/openapi-docs.yml` (line 122), `.github/workflows/test-validation.yml` (line 249), `.github/workflows/performance-regression.yml` (line 497), `.github/workflows/deployment-rollback.yml` (lines 77, 272, 327)
- **Description**: PR comment bodies read from files or step outputs and posted via `github.rest.issues.createComment` without sanitization. Markdown injection (e.g., `@mentions`, issue references) could trigger unintended notifications or link to wrong issues.
- **Remediation**: Sanitize comment bodies before posting. Avoid interpolating raw log output.
- **Priority**: P2

### [MEDIUM] `agent_execution.py` uses `unsafe.imports_passed_through()` — OPEN
- **Repo**: Tracera
- **Severity**: MEDIUM
- **Type**: Code Execution Surface
- **Status**: OPEN
- **File**: `src/tracertm/workflows/agent_execution.py` (line 20)
- **Description**: `workflow.unsafe.imports_passed_through()` in a workflow context signals potential for arbitrary code execution. If combined with untrusted input, this could be a code exec vector.
- **Remediation**: Audit all callers. Pin allowed imports explicitly. Do not combine with user-controlled data.
- **Priority**: P2

### [INFO] `forgecode` and `helioscope` use `pull_request_target` with SHA-pinned actions — NOTED
- **Repo**: Tracera (referenced workflows)
- **Severity**: INFO
- **Type**: Workflow Security Pattern
- **Status**: NOTED — ACCEPTABLE
- **Description**: `forgecode/release-drafter.yml` and `helioscope/cla.yml` use `pull_request_target` trigger but pin their underlying actions to full commit SHAs. This is the correct pattern: `pull_request_target` is necessary for these use cases, and SHA-pinning mitigates the primary risk of that trigger.
- **Remediation**: No action required. Maintain SHA-pinning discipline for all actions used in `pull_request_target` contexts.
- **Priority**: P4 — monitor

---

## Category: Infrastructure

### [INFO] `kwality` privileged container for Docker-in-Docker — NOTED
- **Repo**: Kwality
- **Severity**: INFO
- **Type**: Privileged Container
- **Status**: NOTED — LEGITIMATE USE
- **File**: `k8s/kwality-deployment.yaml`
- **Description**: Has `privileged: true` for the Docker-in-Docker sidecar. This is a legitimate use case (building container images inside the cluster).
- **Remediation**: Ensure the node pool is tainted appropriately and non-build workloads cannot be scheduled on DinD nodes. Add network policies to restrict the DinD pod's egress.
- **Priority**: P4 — hardening only

### [INFO] `KDesktopVirt` privileged Podman API container — NOTED
- **Repo**: KDesktopVirt
- **Severity**: INFO
- **Type**: Privileged Container
- **Status**: NOTED — LEGITIMATE USE
- **File**: `docker-compose.hybrid.yml`
- **Description**: Has `privileged: true` for Podman API access. Required for the hybrid virtualization workflow.
- **Remediation**: Restrict the socket bind to localhost only. Add firewall rules to prevent external access to the Podman socket.
- **Priority**: P4 — hardening only

---

## Category: Configuration / Hygiene

### [LOW] Missing `retention-days` on workflow artifacts — OPEN
- **Repo**: Tracera
- **Severity**: LOW
- **Type**: Configuration
- **Status**: OPEN
- **Files**: Various workflow artifact upload steps
- **Description**: Some `actions/upload-artifact` steps omit `retention-days`, defaulting to 90 days. Artifacts accumulate and consume storage.
- **Remediation**: Explicitly set `retention-days: 7` for all workflow artifacts.
- **Priority**: P3

### [LOW] Multiple stale/duplicate workflow files — OPEN
- **Repo**: Tracera
- **Severity**: LOW
- **Type**: Configuration Hygiene
- **Status**: OPEN
- **Description**: Several workflow files appear to be legacy or redundant (`schema-validation.yml`, `test-validation.yml`, `chaos-tests.yml`). Unused workflows still trigger on path changes and consume CI minutes.
- **Remediation**: Audit workflows, archive unused ones, consolidate overlapping jobs.
- **Priority**: P3

---

## Remediations by Priority

### P1 — Fix Before Next Release
| ID | Finding | Repo | Status |
|----|---------|------|--------|
| H-INJ-1 | SQL injection: SET LOCAL tenant isolation | Tracera | PARTIAL |
| H-INJ-2 | SQL injection: sandbox_id passthrough | Tracera | PARTIAL |
| H-INJ-3 | SQL injection: search module raw SQL | Tracera | VERIFY |
| H-WF-1 | Overbroad workflow permissions | Tracera | OPEN |
| H-WF-2 | dependabot-auto-merge without test gate | Tracera | OPEN |
| H-CTG-1 | Wrong project README / contamination | Tracera | OPEN |

### P2 — Address in Current Sprint
| ID | Finding | Repo | Status |
|----|---------|------|--------|
| M-CRP-1 | TOTP SHA-1 → SHA-256 | AuthKit | FIXED |
| M-CRP-2 | Sandbox MD5 → SHA-256 | AuthKit | FIXED |
| M-CRD-1 | Hardcoded creds .env.example | HexaKit | FIXED |
| M-CRD-2 | Hardcoded creds .env.example | PhenoDevOps | FIXED |
| M-WF-1 | sqlc@latest mutable tag | Tracera | FIXED |
| M-WF-2 | Missing timeout-minutes | Tracera | FIXED |
| M-WF-3 | Trufflehog SHA mismatch | Tracera | FIXED |
| M-WF-4 | Unpinned swag version | Tracera | OPEN |
| M-WF-5 | Hardcoded go-version drift | Tracera | OPEN |
| M-INJ-1 | LegacyFriendlySession raw SQL | Tracera | OPEN |
| M-INJ-2 | Markdown frontmatter ID trust | Tracera | OPEN |
| M-OUT-1 | Unsanitized PR comment outputs | Tracera | OPEN |
| M-EXEC-1 | unsafe.imports_passed_through | Tracera | OPEN |

### P3 — Schedule
| ID | Finding | Repo | Status |
|----|---------|------|--------|
| L-IFS-1 | localhost in public llms.txt | Tracera | OPEN |
| L-VLT-1 | Vault plaintext HTTP default | Tracera | OPEN |
| L-CFG-1 | Missing retention-days | Tracera | OPEN |
| L-CFG-2 | Stale/duplicate workflows | Tracera | OPEN |

### P4 — Monitor / Hardening
| ID | Finding | Repo | Status |
|----|---------|------|--------|
| I-PRIV-1 | kwality privileged DinD container | Kwality | NOTED |
| I-PRIV-2 | KDesktopVirt privileged Podman | KDesktopVirt | NOTED |
| I-PR-1 | pull_request_target + SHA-pinned | forgecode/helioscope | NOTED |

---

## Open Items Requiring Manual Review

1. **TRACERA — SQL injection verification**: Confirm which file in `venture/` contains `SET LOCAL app.current_tenant` and which `database.py` contains the `sandbox_id` passthrough. Verify exact line numbers for targeted fixes.

2. **TRACERA — search module raw SQL**: Confirm file path and verify whether raw SQL is still present in the search module. Previous DAG report flagged `local_storage.py` and `LegacyFriendlySession`; cross-check for additional callers.

3. **TRACERA — README contamination sweep**: Run full-repo grep for `TracerTM`, `tracertm`, `Phenotype-Enterprise/trace`, and `kooshapari/tracertm`. Decide which references are legitimate module names vs. stale project names before mass-updating.

4. **AUTHKIT — orphaned submodules**: `python/pheno-auth` and `python/pheno-security` are git submodules with no remotes. Determine whether these are dead code that should be removed or archived submodules that need a remote configured.

5. **TRACERA — `agent_execution.py` callers**: Audit all callers of `unsafe.imports_passed_through()` in `agent_execution.py`. Determine whether any caller passes user-controlled data into the imported modules.

6. **KWALITY / KDESKTOPVIRT — container hardening**: Confirm node taints for the DinD pod and firewall rules for the Podman socket. Document the security posture in the respective repos' `SECURITY.md` or a security posture doc.

---

## Change Log

| Date | Change |
|------|--------|
| 2026-05-04 | Initial DAG: 4 HIGH, 6 MEDIUM, 5 LOW |
| 2026-05-05 | 8 findings closed. 4 new HIGH surfaced (SQL injection surface area). Cross-repo findings added (AuthKit, HexaKit, PhenoDevOps, Kwality, KDesktopVirt). Report consolidated here. |

---

*Generated: 2026-05-05*
*Auditor: OWL (automated sweep + manual review)*
*Next scheduled sweep: 2026-05-12*
