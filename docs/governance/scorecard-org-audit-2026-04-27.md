# OSSF Scorecard Org Audit — 2026-04-27

API-only sweep across 82 active KooshaPari repos via `code-scanning/alerts?tool=Scorecard`. 59 repos surfaced open Scorecard alerts; 23 returned `no analysis found`. **Total open alerts: 2,055.**

## Top repos by alert count

| Repo | Alerts | Notes |
|---|---|---|
| Tokn, PolicyStack, Planify, Dino | 100 (capped) | per_page=100; likely more |
| FocalPoint | 97 | known FP cluster (assets/audio binaries) |
| agentapi-plusplus | 93 | docs/node_modules vendored bins |
| heliosApp | 86 | DangerousWorkflow + 64 PinnedDeps |
| Stashly, argis-extensions, Tasken, nanovms, vibeproxy | 67–83 | |
| PhenoProject, Apisync, hwLedger, phenodocs, Tracera | 41–58 | Tracera = baseline FP repo |

## Top rule clusters (org-wide)

| Rule | Total | Repos |
|---|---|---|
| PinnedDependenciesID | 1,312 | 48 |
| TokenPermissionsID | 265 | 40 |
| CIIBestPracticesID | 57 | 57 |
| CodeReviewID | 57 | 57 |
| FuzzingID | 55 | 55 |
| BranchProtectionID | 54 | 54 |
| MaintainedID | 52 | 52 |
| SASTID | 49 | 49 |
| BinaryArtifactsID | **31** | **8** |
| VulnerabilitiesID | 21 | 21 |
| DangerousWorkflowID | 1 | 1 (heliosApp) |

## BinaryArtifacts FP-cluster candidates (priority for `.scorecard.yml` exemptions / cleanup)

| Repo | Count | Path pattern | FP type |
|---|---|---|---|
| **Dino** | 12 | `src/Tools/AssetPipelineRust/target/release/**`, `__pycache__/*.pyc` | Rust build artifacts + Python bytecode — should be `.gitignore`d |
| **agentapi-plusplus** | 6 | `docs/node_modules/**` (esbuild, rollup, fsevents, onig.wasm) | committed `node_modules` — needs purge + ignore |
| **Tracera** | 3 | `backend/vault.test`, `backend/tracertm-setup`, `tsgolint` darwin-arm64 | Go test binaries + vendored toolchain (baseline) |
| **FocalPoint** | 2 | `assets/audio/test_synth`, `assets/audio/gen_cues` | known archive FP (already triaged) |
| **PolicyStack** | 1 | `wrappers/go/policy-wrapper` | committed Go binary |
| **argis-extensions** | 1 | `slm-server/slm-server` | committed binary |
| **vibeproxy** | 1 | `src/Sources/Resources/cli-proxy-api-plus` | vendored CLI |
| **BytePort** | 10 | `backend/byteport/tmp/main*`, `gradle-wrapper.jar`, src-tauri gen | tmp build outputs + Tauri gen |

## Repo-policy gaps (universal — appear in 50+ repos)

`CIIBestPracticesID`, `CodeReviewID`, `FuzzingID`, `BranchProtectionID`, `MaintainedID`, `SASTID` each fire in ~52–57 repos with count=1. These are **org-policy gaps**, not per-file FPs. Single fix: add CodeQL workflow + branch protection ruleset + CII badge config via org template.

## Recommended next batch

1. **BinaryArtifacts cleanup wave** — Dino (12), agentapi-plusplus (6), BytePort (10): purge `node_modules`/`target/`/`tmp/` from history, add `.gitignore` + `.scorecard.yml` exemption for legit vendored binaries (Tracera tsgolint, vibeproxy cli-proxy-api-plus, PolicyStack go-wrapper). Mirrors Tracera/FocalPoint precedent.
2. **PinnedDependencies blanket sweep** — 1,312 alerts across 48 repos = pin GHA actions to SHAs via `pin-github-action` or `stepsecurity/secure-repo`. Single PR-template fix.
3. **TokenPermissions blanket** — 265 alerts: add `permissions: contents: read` to all workflows.
4. **Org-policy bootstrap** — branch protection + CodeQL + SECURITY.md across 50+ repos via phenotype-infra ruleset restoration (billing-blocked rulesets reference).
5. **heliosApp DangerousWorkflow** — single alert, investigate isolated.

## Coverage gaps

23 repos returned `no analysis found` (no Scorecard workflow yet): Conft, AgentMCP, eyetracker, byteport-landing, agileplus-landing, others. Bootstrap Scorecard workflow next batch.

---
Source: `gh api repos/KooshaPari/<r>/code-scanning/alerts` parallel sweep, P=25, ~90s wall.
