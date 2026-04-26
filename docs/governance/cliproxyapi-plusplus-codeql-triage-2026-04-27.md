# cliproxyapi-plusplus CodeQL Triage — 2026-04-27

**Repo:** KooshaPari/cliproxyapi-plusplus (fork, not archived, default `main`, pushed 2026-04-26)
**Scope:** open critical (4) + high (60) alerts. **API-only, no dismissals.**

## 4 Critical (path / rule)

| # | Rule | Path |
|---|------|------|
| 788 | `go/unsafe-quoting` | `pkg/llmproxy/executor/cursor_executor.go` |
| 787 | `go/unsafe-quoting` | `pkg/llmproxy/executor/cursor_executor.go` |
| 344 | `go/request-forgery` | `pkg/llmproxy/api/handlers/management/api_call.go` |
| 139 | `go/request-forgery` | `pkg/llmproxy/executor/antigravity_executor.go` |

All four are **first-party Go** (no vendored kiro/qwen/gemini/codex-rs/.archive paths). Two SSRF + two unsafe-quoting in cursor exec — real fixes required.

## Top High Clusters (60 total)

**Go SAST (33 alerts, all first-party):**
- `go/path-injection` ×13 — `sdk/auth/filestore.go` (5), `pkg/llmproxy/auth/base/token_storage.go` (3), `pkg/llmproxy/auth/vertex/vertex_credentials.go` (2), `internal/auth/codebuddy/token.go` (2), `pkg/llmproxy/auth/kiro/token.go` (1), `pkg/llmproxy/logging/request_logger.go` (1)
- `go/clear-text-logging` ×10 — `pkg/llmproxy/registry/model_registry.go` (4), `pkg/llmproxy/executor/cursor_executor.go` (3), `sdk/cliproxy/auth/conductor_helpers.go` (2), `pkg/llmproxy/api/middleware/response_writer.go` (1)
- `go/weak-sensitive-data-hashing` ×7 — spread across watcher/, executor/, auth/kiro/, sdk/cliproxy/
- `go/allocation-size-overflow` / `go/uncontrolled-allocation-size` ×3 — `sdk/api/handlers/handlers.go`, `internal/auth/cursor/proto/connect.go`, `pkg/llmproxy/api/handlers/management/alerts.go`

**Scorecard / OSSF supply-chain (27 alerts, repo-config not code):**
- `TokenPermissionsID` ×17 — every `.github/workflows/*.yml` lacks least-privilege `permissions:` block
- `BinaryArtifactsID` ×4 — `test.test`, `releasebatch`, `cli-proxy-api-plus-integration-test`, `boardsync` checked in
- `MaintainedID`, `CodeReviewID`, `BranchProtectionID`, `VulnerabilitiesID` ×1 each — repo-policy hygiene

## Vendor vs First-Party Split

- **Vendored / FP cluster: 0** — no hits in kiro/qwen/gemini/codex-rs/.archive subtrees. Memory note about vendored upstreams does not apply to current open alert set.
- **First-party Go code: 37** (4 crit + 33 high SAST)
- **Repo config (workflows / artifacts / policy): 27** — fixable via 1 PR (add `permissions: { contents: read }` defaults, gitignore binaries, branch-protection toggles)

## Recommended Sequence (no action taken)

1. Single PR: workflow `permissions:` hardening + binary artifact cleanup (clears 21/27 hygiene).
2. Critical PR: cursor_executor unsafe-quoting + 2 SSRF (4 alerts).
3. Path-injection sweep on auth token stores (13 alerts, mostly `filepath.Clean` + base-dir prefix check).
4. clear-text-logging audit on registry + executor (10 alerts).
5. Weak-hash MD5/SHA1 → SHA256 (7 alerts).
