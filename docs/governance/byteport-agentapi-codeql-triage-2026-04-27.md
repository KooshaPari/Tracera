# BytePort + agentapi-plusplus CodeQL Triage (2026-04-27)

API-only triage. Both repos active (not archived). No alerts dismissed.

## BytePort (11 high+critical)

| # | Sev | Rule | Path | Class |
|---|-----|------|------|-------|
| 16 | high | VulnerabilitiesID | (meta) | Scorecard meta — real (deps audit) |
| 13 | high | CodeReviewID | (meta) | Scorecard meta — process |
| 12 | high | BinaryArtifactsID | frontend/web/src-tauri/gen/android/gradle/wrapper/gradle-wrapper.jar | Vendor (Gradle wrapper) — accept |
| 11,10,9 | high | BinaryArtifactsID | backend/byteport/tmp/main(.exe~) | Build artifact — gitignore + remove |
| 8 | high | BinaryArtifactsID | backend/byteport/byteport | Build artifact — gitignore + remove |
| 7 | high | BranchProtectionID | (meta) | Process — fix protection rules |
| 6 | **critical** | go/request-forgery | backend/byteport/lib/apilink.go | **First-party — FIX** |
| 5 | high | go/clear-text-logging | backend/nvms/lib/awspin/network/alb.go | First-party — FIX |
| 4 | high | go/clear-text-logging | backend/nvms/lib/aws.go | First-party — FIX |

**Real first-party security defects: 3 (1 critical SSRF + 2 cleartext logging).** Remaining 8 are build artifacts, vendored binaries, or Scorecard process meta-alerts.

## agentapi-plusplus (36 high+critical)

| Group | Count | Class | Action |
|-------|-------|-------|--------|
| TokenPermissionsID on `.github/workflows/*.yml` | 20 | First-party CI hardening | Add top-level `permissions: {}` per workflow |
| BinaryArtifactsID under `docs/node_modules/**` | 6 | Vendor (committed node_modules) | Remove docs/node_modules + .gitignore |
| go/path-injection (lib/httpapi/embed.go × 2 paths) | 2 | First-party | **FIX** — sanitize path input |
| GHSA/CVE on `agentapi-plusplus/chat/bun.lock` | 4 (1 crit CVE-2025-55182, 3 high) | Dep upgrade in chat/ subproject | **FIX** — `bun update` |
| actions/code-injection/critical → pr-preview-release.yml | 1 | **First-party CI critical** | **FIX** — quote/escape PR title/body in run step |
| Scorecard meta (Vulnerabilities/CodeReview/BranchProtection) | 3 | Process | Branch protection + deps |

**Real first-party security defects: 27** (20 TokenPermissions + 2 path-injection + 4 deps + 1 critical workflow code-injection). 6 are vendored node_modules (should be uncommitted but not exploitable in repo). 3 are Scorecard process meta.

## Priority fix order

1. **agentapi-plusplus #63** — critical actions/code-injection in `pr-preview-release.yml` (RCE via PR title)
2. **agentapi-plusplus #1** — CVE-2025-55182 in chat/bun.lock
3. **BytePort #6** — critical go/request-forgery in apilink.go
4. agentapi-plusplus #61,62 path-injection in httpapi/embed.go
5. BytePort #4,5 cleartext-logging in nvms aws.go / alb.go
6. agentapi-plusplus #2,3,55 transitive bun.lock GHSAs (`bun update`)
7. agentapi-plusplus token-permissions sweep (20 workflows) — add `permissions: read-all` floor + per-job least-priv
8. Hygiene: remove `backend/byteport/tmp/*`, `backend/byteport/byteport`, `docs/node_modules/**` + .gitignore

## Constraints honored

- API-only (no checkout, no clone).
- No alerts dismissed/suppressed.
- Pre-flight archived check: both `false`.
