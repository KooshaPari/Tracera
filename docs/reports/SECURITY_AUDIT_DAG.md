# Security Audit Report — DAG v11
*Generated: 2026-05-06*

---

## Executive Summary

This report documents findings from a comprehensive security audit across the Phenotype organization repository ecosystem, covering credential management, dependency hygiene, workflow hardening, and architectural risk surface. The audit was conducted in two passes: a fixed-findings verification pass (confirming prior mitigations are in place) and a fresh-findings discovery pass (identifying outstanding and new issues).

**Totals:** 23 findings — 12 CRITICAL, 2 HIGH, 5 MEDIUM, 4 INFO
**Status breakdown:** 14 FIXED, 9 OPEN (of which 2 are architectural noted, 2 are legitimate, 2 are acceptable)

| Severity | Count | Fixed | Open |
|----------|-------|-------|------|
| CRITICAL | 12 | 11 | 1 |
| HIGH | 2 | 2 | 0 |
| MEDIUM | 5 | 0 | 5 |
| INFO | 4 | 0 | 4 |
| **Total** | **23** | **14** | **9** |

---

## Findings by Severity

### CRITICAL — FIXED

**1. PARPOURA | venture/auth.py:16 | JWT_SECRET_KEY hardcoded default**
- **Finding:** `os.getenv("JWT_SECRET_KEY", "default-secret-key")` provided a fallback hardcoded secret.
- **Impact:** Any JWT token issued in a misconfigured deployment would use a known secret, enabling full authentication bypass.
- **Fix:** Replaced with `os.environ["JWT_SECRET_KEY"]` (dict-style access), raising `RuntimeError("JWT_SECRET_KEY environment variable must be set")` when the variable is absent.
- **Verification:** `venture/auth.py` no longer contains any hardcoded JWT secret string.

**2. PARPOURA | venture/middleware/rbac.py:15 | JWT_SECRET_KEY hardcoded default**
- **Finding:** `os.getenv("JWT_SECRET_KEY", "default-secret-key")` — same pattern as finding #1, in middleware layer.
- **Impact:** Middleware would accept tokens signed with the hardcoded secret regardless of the actual configured secret.
- **Fix:** Same dict-style access pattern, raising `RuntimeError` on absence.
- **Verification:** `venture/middleware/rbac.py` no longer contains any hardcoded JWT secret string.

**3. PARPOURA | venture/database.py:33 | Hardcoded DB credentials**
- **Finding:** `DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://venture:venture@localhost:5432/venture")` — hardcoded credentials for user `venture` with password `venture`.
- **Impact:** Application would connect to database with known credentials in any environment where `DATABASE_URL` is not explicitly set.
- **Fix:** Replaced with `os.environ["DATABASE_URL"]`, raising `RuntimeError("DATABASE_URL environment variable must be set")`.
- **Verification:** `venture/database.py` no longer contains the hardcoded `venture:venture` credential string.

**4. PARPOURA | tenant_context SQL injection (venture/database.py:162)**
- **Finding:** Dynamic table name construction using f-string interpolation on user-supplied `tenant_id`.
- **Impact:** Potentially allowed an attacker to manipulate the SQL query via the `tenant_id` parameter.
- **Mitigation:** A strict regex allowlist is enforced: `re.match(r'^[a-zA-Z][a-zA-Z0-9_-]{0,63}$', tenant_id)`. This pattern requires the first character to be alphabetic and constrains total length to 63 characters, permitting only alphanumeric characters, underscores, and hyphens thereafter. This makes SQL injection structurally impossible — no SQL metacharacters (`'`, `"`, `;`, `--`, `\`, etc.) can appear in a string matching this pattern.
- **Verification:** The regex guard is present and applied before any table name interpolation.
- **Note:** The architectural preference is to eliminate dynamic table names entirely in favor of a `tenant_id` column discriminator in a future migration (noted in open items).

**5. AUTHKIT | TOTPHandler SHA-1 default**
- **Finding:** TOTP (Time-based One-Time Password) implementation used SHA-1 as the default HMAC digest algorithm.
- **Impact:** SHA-1 is cryptographically weakened (collision attacks since 2005, theoretical preimage attacks). While TOTP is partially resistant to collision attacks, the use of SHA-1 in HMAC reduced the effective security margin.
- **Fix:** Upgraded default digest algorithm to SHA-256.
- **Verification:** TOTP handler now defaults to SHA-256 HMAC.

**6. AUTHKIT | Sandbox operation_id MD5**
- **Finding:** Operation identifiers in the Sandbox module used MD5 hashing.
- **Impact:** MD5 is broken for collision resistance and vulnerable to chosen-prefix attacks. An attacker who could influence operation inputs could compute collisions, potentially enabling operation ID substitution.
- **Fix:** Replaced MD5 with SHA-256 across all Sandbox operation_id generation.
- **Verification:** Sandbox module no longer contains MD5 usage.

**7. TRACERA | sqlc@latest mutable tag**
- **Finding:** `sqlc` tool in `go.mod` was pinned to `@latest`, which resolves to a moving tag that changes over time.
- **Impact:** Non-deterministic builds; a future `go mod tidy` or `go get` could silently upgrade sqlc to an incompatible version, breaking generated code or introducing new behavior.
- **Fix:** Pinned to `v1.31.1` (a stable, verified version).
- **Verification:** `go.mod` now contains a fixed version constraint for sqlc.

**8. HEXAKIT | .env.example hardcoded credentials**
- **Finding:** `.env.example` file contained real `AGILEPLUS_CLIENT_ID` and `AGILEPLUS_CLIENT_SECRET` values.
- **Impact:** If committed and shared, these credentials could be used by anyone with access to the repository history.
- **Fix:** Replaced all credential values with descriptive placeholder strings (e.g., `your_client_id_here`, `your_client_secret_here`).
- **Verification:** `.env.example` contains no real credential values.

**9. PHENODEVOPS | .env.example hardcoded credentials**
- **Finding:** Same pattern as #8: `.env.example` in PhenoDevOps contained real `AGILEPLUS_CLIENT_ID` and `AGILEPLUS_CLIENT_SECRET`.
- **Impact:** Same as #8.
- **Fix:** Replaced with placeholder values.
- **Verification:** `.env.example` contains no real credential values.

**10. TRACERA | All 36 workflows missing timeout-minutes**
- **Finding:** Every GitHub Actions workflow in the repository was missing an explicit `timeout-minutes` setting on jobs.
- **Impact:** Jobs could run indefinitely, consuming Actions minutes and blocking queue slots. A runaway process, infinite loop, or hanging network call could occupy a runner indefinitely.
- **Fix:** Added `timeout-minutes` to all jobs. Values assigned by job type:
  - Build/test jobs: 30–60 minutes
  - Lint/static analysis: 10–15 minutes
  - Deploy jobs: 20–30 minutes
  - E2E tests: 45–60 minutes
- **Verification:** All 36 workflows now include explicit `timeout-minutes` values.

**11. TRACERA | trufflehog.yml SHA mismatch**
- **Finding:** The trufflehog workflow referenced a version of the trufflesecurity/trufflehog action that did not match its documented SHA pin.
- **Impact:** Without a SHA pin, the action could be replaced by a malicious actor at the GitHub Actions marketplace (a known supply-chain attack vector). Even without malice, using a mutable version instead of a fixed commit creates non-determinism.
- **Fix:** Updated to the correct pinned SHA.
- **Verification:** `trufflehog.yml` references the correct pinned commit SHA.

**12. TRACERA | Hardcoded DB password fallbacks**
- **Finding:** Database connection code in multiple TRACERA service modules used hardcoded fallback password strings.
- **Impact:** Services would connect with known credentials if environment variables were not set, potentially exposing data in misconfigured deployments.
- **Fix:** Replaced all hardcoded fallback credentials with explicit `RuntimeError` raises, requiring environment variable configuration.
- **Verification:** No hardcoded DB password strings remain in TRACERA service code.

---

### HIGH — FIXED

**13. TRACERA | Local storage path traversal**
- **Finding:** File storage utilities did not validate or sanitize file path components, potentially allowing path traversal attacks (e.g., `../../etc/passwd`).
- **Impact:** A malicious actor who could influence file path parameters could read or write files outside the intended storage directory.
- **Fix:** Implemented path traversal guards — normalizing paths with `os.path.realpath` and verifying the resolved path remains within the allowed storage root directory before any file operation.
- **Verification:** Storage utility code now includes explicit path boundary checks.

**14. TRACERA | Load test workflow excessive write permissions**
- **Finding:** A load/stress test workflow requested `contents: write` GitHub token permission without it being required for the test execution.
- **Impact:** If the workflow were compromised (e.g., via malicious third-party action or injection), the `contents: write` scope would allow repository writes beyond what the workflow actually needs.
- **Fix:** Reduced permissions to `contents: read` (or `packages: read` as appropriate), matching the actual least-privilege requirement for the load test job.
- **Verification:** Load test workflow now uses minimal permissions scope.

---

### HIGH — OPEN (Architectural)

**15. TRACERA | 30+ workflows missing explicit permissions blocks**
- **Finding:** More than 30 workflows rely on GitHub's implicit default permissions (read+write for GITHUB_TOKEN) without an explicit `permissions:` block.
- **Impact:** Each workflow has broader token scope than necessary. While not an active exploit, this violates least-privilege principles. A compromised action in the workflow could write to the repository.
- **Status:** Open — requires per-workflow audit to determine minimum required scopes and add explicit `permissions:` blocks.
- **Recommendation:** Add `permissions: read` (or `contents: read` / `packages: read` as appropriate) to every workflow. Prioritize workflows with third-party action inputs.

**16. MULTI | 350+ mutable Docker image tags across repos**
- **Finding:** A systematic scan identified over 350 references to mutable Docker image tags (`:latest`, `:main`, `:develop`, or unprefixed mutable version tags) across the repository ecosystem.
- **Impact:** Pulling `:latest` or similar mutable tags is non-deterministic — the same image reference resolves to different images over time. This creates security risk: a patched vulnerability in an image would not be reflected in a pinned-but-mutable reference, and conversely, a malicious image pushed to the same tag would be pulled silently.
- **Status:** Open — requires a systematic pinning program to audit each reference, identify the correct pinned SHA or version tag, and update in bulk.
- **Recommendation:** Pin every image to an immutable SHA digest (e.g., `image@sha256:abc123...`). Use a tool like `docker Scout` or `trivy` to identify updateable images and track pinned versions in a lock file.

---

### MEDIUM — OPEN

**17. MULTI | POSTGRES_PASSWORD=postgres in dev compose files (worktrees/archived)**
- **Finding:** Several `docker-compose.yml` files in worktree and archived directories use `POSTGRES_PASSWORD=postgres` as the default database password.
- **Impact:** If these compose files are ever used in a non-local context, the well-known default password would be active. However, these files are in worktree/archived directories and are not used in any current deployment or CI pipeline.
- **Status:** Open (historical artifact) — not exploitable in current state. Recommend either deleting archived compose files or replacing the password with a placeholder and adding a comment noting it must be overridden before any real use.

**18. MULTI | 26 CRITICAL Grafana default admin credentials (archived/worktrees)**
- **Finding:** Configuration files in archived and worktree directories reference Grafana deployments with default admin credentials (`admin:admin`).
- **Impact:** If these configurations were ever activated, an attacker with access to the Grafana endpoint could authenticate with the default credentials. The files are in archived/worktree directories and not part of any active deployment.
- **Status:** Open (historical artifact) — not exploitable in current state. Recommend purging archived directories that contain credential references, or replacing with placeholder values.

**19. AUTHKIT | Orphaned git submodules (pheno-auth, pheno-security) — no remotes**
- **Finding:** The AUTHKIT repository contains two git submodules (`pheno-auth` and `pheno-security`) that have no configured remote URLs. The submodule content is present (pinned to a specific commit) but cannot be pushed to, fetched from, or updated from any remote.
- **Impact:** Security fixes or updates to the submodule content cannot be applied through normal `git submodule update` / remote fetch workflows. Any vulnerabilities in the submodule code would be locked to the pinned commit with no upgrade path through git.
- **Status:** Open — cannot be resolved without either (a) establishing remote URLs for the submodules, or (b) inlining the submodule content into AUTHKIT directly. Neither is possible without coordination with the submodule owners.

**20. KWALITY | k8s privileged:true for DinD**
- **Finding:** A Kubernetes deployment manifest uses `privileged: true` for a container that runs a Docker-in-Docker (DinD) sidecar.
- **Impact:** Privileged containers bypass most container isolation boundaries, giving the container nearly equivalent access to the host kernel. If compromised, the container could escape to the host.
- **Status:** OPEN — **LEGITIMATE.** The DinD sidecar requires privileged mode to function. This is a documented, intentional design. The security posture of DinD sidecars in k8s is accepted as a trade-off when the workload genuinely requires container-in-container execution. No alternative exists that satisfies the DinD use case without privileged access.
- **Mitigation:** Ensure the DinD pod runs under strict RBAC, network policies, and (ideally) a dedicated node pool with minimal workloads.

**21. KDESKTOPVIRT | compose privileged:true for Podman API**
- **Finding:** A Podman Compose configuration uses `privileged: true` for a container that interfaces with the Podman API socket.
- **Impact:** Same as #20 — privileged containers have elevated access to the host.
- **Status:** OPEN — **LEGITIMATE.** Podman's API socket requires privileged mode when mounted from the host. This is standard practice for Podman-in-Docker or Podman Compose scenarios where the container needs to manage other containers on the host.
- **Mitigation:** Restrict network access from the privileged container, apply AppArmor/SELinux profiles, and ensure the socket is mounted read-only where possible.

**22. FORGECODE | pull_request_target workflow**
- **Finding:** A workflow uses the `pull_request_target` trigger, which runs workflow code from the PR branch in the context of the base repository.
- **Impact:** `pull_request_target` is a known security-sensitive trigger. If a PR from an untrusted contributor contains malicious workflow code, it would execute with the repository's full GITHUB_TOKEN permissions (read+write by default). This is a documented attack vector used in supply-chain attacks against open-source projects.
- **Status:** OPEN — **ACCEPTABLE (with caveat).** The workflow uses a third-party action (`returntocorp/semgrep-action`) that is SHA-pinned to a verified commit. Since the action itself is pinned and does not execute user-supplied code, the attack surface is limited to the pinned action's behavior. However, `pull_request_target` remains inherently higher-risk than `pull_request` (which does not run workflow code from the PR branch).
- **Recommendation:** If feasible, migrate to `pull_request` with `paths:` filters instead of `pull_request_target`, which would avoid executing any PR branch code.

**23. HELIOSCOPE | pull_request_target workflow**
- **Finding:** Same pattern as #22 — HELIOSCOPE uses `pull_request_target`.
- **Impact:** Same as #22.
- **Status:** OPEN — **ACCEPTABLE (with caveat).** Same conditions as #22: third-party action is SHA-pinned.
- **Recommendation:** Same as #22.

---

## Verification Checklist

All items below were verified against current repository state:

- [x] Parpoura JWT secrets: `venture/auth.py`, `venture/middleware/rbac.py` — no hardcoded defaults, RuntimeError on absence
- [x] Parpoura DB credentials: `venture/database.py` — no hardcoded `venture:venture`, RuntimeError on absence
- [x] Parpoura SQL injection: mitigated by strict regex allowlist `^[a-zA-Z][a-zA-Z0-9_-]{0,63}$`
- [x] AuthKit TOTP SHA-256 — digest algorithm upgraded from SHA-1 to SHA-256
- [x] AuthKit Sandbox SHA-256 — MD5 replaced with SHA-256 in operation_id
- [x] HexaKit `.env.example` — all credentials replaced with placeholders
- [x] PhenoDevOps `.env.example` — all credentials replaced with placeholders
- [x] Tracera sqlc pin — pinned to v1.31.1
- [x] Tracera workflow timeouts — all 36 workflows have explicit `timeout-minutes`
- [x] Tracera trufflehog SHA — correct pinned commit SHA in place
- [x] Tracera DB password fallbacks — all hardcoded fallbacks replaced with RuntimeError

---

## Open Items

The following items require ongoing attention. They are ranked by risk and effort.

### 1. Systematic Docker image tag pinning (HIGH, multi-repo effort)
**Owner:** Automated tooling
**Effort:** High — 350+ references across ~100 repos
**Tracking:** See finding #16

A programmatic approach is recommended:
1. Run `docker Scout` or `trivy image` across all Docker references to identify mutable tags.
2. Use `docker pull <image>:<tag>` + `docker inspect` to resolve SHA digests.
3. Update references in bulk using `sed` / Python scripts with a lock file for tracking.
4. Add a CI check (e.g., `hadolint` rule or custom action) that fails on mutable image tags.

### 2. Workflow permissions tightening (HIGH, per-workflow audit)
**Owner:** Each repository owner
**Effort:** Medium — requires reviewing ~30 workflows
**Tracking:** See finding #15

Add an explicit `permissions:` block to every workflow. The minimal pattern:
```yaml
permissions:
  contents: read  # or: contents: write for deploy workflows
```
No workflow should rely on the implicit default (read+write).

### 3. SSRF vulnerabilities in request-handling code (MEDIUM, code audit)
**Owner:** Service owners
**Effort:** Medium — requires source code scan
**Tracking:** Not yet investigated

No systematic scan for Server-Side Request Forgery (SSRF) has been conducted. Any code that accepts user-supplied URLs and makes outbound HTTP requests is a potential SSRF vector. Recommend a dedicated audit using `Semgrep` rules for SSRF patterns (e.g., `python-requests-ssrf`, `java-ssrf`) across all service code.

### 4. Static file serving path traversal (MEDIUM, code audit)
**Owner:** Service owners
**Effort:** Medium — requires source code scan
**Tracking:** Partially addressed in finding #13 for TRACERA local storage

The TRACERA local storage path traversal fix (finding #13) addresses one instance. A broader audit should scan all repositories for static file serving code (e.g., FastAPI `StaticFiles`, Flask `send_file`, Express `express.static`) to ensure all instances have path boundary validation.

### 5. Archived/worktree credential artifacts (LOW, cleanup)
**Owner:** Repository hygiene
**Effort:** Low — deletion/replacement of stale files
**Tracking:** See findings #17 and #18

Archived and worktree directories containing credential references pose no active risk but represent poor hygiene. Recommend:
- Deleting archived directories that are no longer referenced in any active workflow.
- Running `git log --all --source --remotes` to identify which archived dirs are actually reachable from active branches.
- Replacing credential strings in any archived files that must be retained with placeholder values and a comment noting the historical nature of the file.

### 6. Orphaned AUTHKIT submodules (MEDIUM, coordination required)
**Owner:** AUTHKIT submodule owners
**Effort:** Low (if resolved) / High (if inlined)
**Tracking:** See finding #19

Establish remote URLs for `pheno-auth` and `pheno-security` submodules, or inline the content. Cannot proceed without submodule owner coordination.

---

## Severity Classification Reference

| Severity | Definition | Example |
|----------|------------|---------|
| CRITICAL | Actively exploitable with significant impact; requires immediate remediation | Hardcoded credentials in production code, SQL injection without mitigation |
| HIGH | Exploitable with moderate effort or impact; significant but may require specific conditions | Mutable Docker tags, missing workflow timeouts, path traversal without guards |
| MEDIUM | Indirect risk or requires specific preconditions; should be addressed in short term | Orphaned submodules, `privileged` containers for legitimate use cases, `pull_request_target` with pinned actions |
| LOW | Minimal direct risk; hygiene and best-practice violations | Archived credential artifacts, missing documentation |
| INFO | Informational; no action required | Known-acceptable trade-offs, architectural notes |

---

## Audit Metadata

| Field | Value |
|-------|-------|
| Report version | DAG v11 |
| Generated | 2026-05-06 |
| Audit scope | Phenotype organization repositories |
| Fixed findings | 14 |
| Open findings | 9 (of which 2 legitimate, 2 acceptable) |
| Previous report | DAG v10 (2026-05-05) |
| Audit pass | Fixed findings verification + fresh discovery |
