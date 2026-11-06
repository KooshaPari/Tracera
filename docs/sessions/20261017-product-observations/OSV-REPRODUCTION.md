# OSV scanner execution investigation

Subject: `2f1d36dc5264e0b36811036913ed9b47083ef968`, observed 2026-10-17.
Security gate remains **UNACCEPTED**. No workflow repair is claimed.

The preserved four-line `GOTOOLCHAIN=go1.25.13` candidate was disproved using
`ghcr.io/google/osv-scanner-action:v2.0.2`. Its Go 1.24.2 rejected the sidecar
under `GOTOOLCHAIN=local`. Setting the candidate variable downloaded Go 1.25.13,
but the embedded govulncheck still rejected Go 1.25 packages because the analyzer
was built with Go 1.24. This is an actual failed reproduction, not a valid fix.

Primary source inspected: osv-scanner v2.0.2 commit
`a2a23858b9650035f019219937f91ae615474b4d`, `internal/sourceanalysis/go.go:166`
inherits the environment. `exit_code_redirect.sh` maps scanner general error 127
to success. One initial invalid local bind mount demonstrated that masking;
it was rejected as verification and replaced with copied files in owned containers.

A newer scanner v2.7.0 was inspected through its action commit
`b1d267aea5211fa648d9d442fa64b90dbdcbdd36` and Docker source (Go 1.27.1).
The image digest and source-input hashes are in `osv-reproduction/receipt.json`.
Direct invocation of `/root/osv-scanner` preserves native exit codes. A missing
manifest returned 127. A full scan of the original three manifests with explicit
`--call-analysis=go --all-vulns` returned 1 and reported 11 vulnerabilities.
The Bun lockfile was copied to `bun.lock` in the isolated container; its bytes
match the recorded `frontend/bun.lock` digest. No repository inputs were changed.

**Limitation:** that scan used `GOTOOLCHAIN=auto`, not the sidecar bootstrap's
explicit Go 1.25.13 (`.github/workflows/sidecar-bootstrap-checks.yml`). Therefore
zero Go findings in that result do not establish Go 1.25.13 security. A follow-up
exact-toolchain invocation could not execute: local Colima context/socket had
become unavailable; Windows Docker Desktop's Linux-engine pipe was absent and
no WSL distribution was running. No shared daemon was started or configured.
The proposed workflow edit is intentionally left uncommitted pending this proof.

## Findings preserved, without suppression

The full raw scanner result is `osv-reproduction/new-scanner-auto-full.log`.
Reachability is **UNKNOWN** for these findings; this scan is dependency evidence,
not proof of exploitation or of an accepted waiver.

| Package        | Version | Finding IDs                                   | Scanner fixed version         |
| -------------- | ------- | --------------------------------------------- | ----------------------------- |
| backoff        | 0.4.0   | RUSTSEC-2025-0012                             | none reported                 |
| instant        | 0.1.13  | RUSTSEC-2024-0384                             | none reported                 |
| paste          | 1.0.15  | RUSTSEC-2024-0436                             | none reported                 |
| quinn-proto    | 0.11.15 | RUSTSEC-2026-0338, -0339, -0340, -0341, -0342 | 0.11.18 covers reported fixes |
| rustls-pemfile | 2.2.0   | RUSTSEC-2025-0134                             | none reported                 |
| braces         | 3.0.3   | GHSA-vfj7-8cjw-p6xm                           | none reported                 |
| sprintf-js     | 1.0.3   | GHSA-hp3w-g68c-fv3c                           | none reported                 |

First five rows are crates.io / Cargo.lock; last two are npm / frontend/bun.lock.
No broad dependency update, waiver, manifest downgrade, hosted rerun, paid-service
change, merge, or production change was made. Next: qualify the exact target Go
runtime with the new scanner, then independently disposition each finding.

## Service-free native fallback

The official v2.7.0 Darwin ARM64 asset was downloaded in an owned temporary
directory and matched the published SHA256SUMS entry:
`d4926ef8da134332543be276dff157e4c170f99ad91fc48e89448a8816bdf70b`.
It reports commit `bfe2f84abd2f09fe0b83ba7f6dad40d296762f40`, built Go 1.27.0.
The installed target toolchain independently reports Go 1.25.13. Running the
scanner with `GOTOOLCHAIN=go1.25.13 GOOS=linux GOARCH=amd64`, explicit Go call
analysis and all vulnerabilities returned 0 but an **empty results array**,
despite reporting one extracted package. Explicit lockfile/all-package variants
repeated that result. This does not prove govulncheck ran or establish target
stdlib coverage. The newer extraction/query behavior remains unresolved.

The exact native JSON and diagnostics are preserved alongside this record.
Native Darwin execution is not equivalent to the Linux image execution; neither
the runtime-target obligation nor the workflow repair is accepted by this result.
No additional infrastructure pursuit or broad dependency changes were made.

## Independent instrumented review

An independent read-only evaluator repeated the official native scan with
`--call-analysis=go --all-vulns --all-packages --format=json` and
`GOTOOLCHAIN=go1.25.13`. Its PATH Go wrapper recorded zero calls (no call-log
file was created), while the scanner exited 0 and returned `results: []`.
The original receipt, stdout, stderr and wrapper are preserved unchanged under
`osv-reproduction/independent-native-review/`; byte hashes are recorded in the
parent receipt. The wrapper retains its original temporary output path as
evidence and is not a repository execution tool.

Absence of PATH-wrapper calls is not global process-observation proof. Conditional
analysis may explain the lack of invocation; this is not necessarily a scanner
bug. Actual govulncheck coverage remains **UNPROVEN**, and neither scanner
execution acceptance nor the intended target-runtime security gate is earned.
The workflow candidate remains uncommitted and unchanged.
