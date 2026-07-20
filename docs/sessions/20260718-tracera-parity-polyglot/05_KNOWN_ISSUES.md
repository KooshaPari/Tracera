# Known issues

## Current verification snapshot (2026-07-20)

- CI head `892bea9` is green across Pages, Vercel, frontend contracts, release-dist,
  crates, latency, dependency, Go sidecar, security, deployment capability, and secret
  provenance checks.
- `TRACERA_API_BASE` currently points at a private Tailscale HTTP address for local/tailnet
  use; production Pages rejects it until an authenticated public HTTPS ingress exists.
- `crates/tracera-server/src/main.rs` remains oversized because its private test module is
  tightly coupled; extraction is still pending a mechanical, fully validated move.

## Resolved

- **Frontend Bun build recursion (2026-07-19):** root `frontend` scripts used
  `npm run ... --prefix`, which Bun reinterpreted as recursive root invocations. Scripts now
  use `npm --prefix <workspace> run <script>` so the target package is explicit and bounded.

- The deployed Rust API does not implement every historical FastAPI endpoint;
  client calls must remain covered by the parity contract tests.
- The Go sidecar is not production-enabled and has no queue delivery or auth
  integration yet.
- Generated desktop bundles and dependency trees exceed repository file-size
  guidance but are build artifacts/dependencies, not maintained source modules.

## Current open risks (2026-07-20)

- CI release archives now carry GitHub provenance attestations with scoped job
  permissions; verified release gates were green on head `892bea9` where runners
  were available.
- Pages production is fail-closed unless `TRACERA_API_BASE` is a public HTTPS
  origin. The configured `http://100.112.14.98:8080` Tailscale address is private;
  authenticated public ingress and a managed secret remain required.
- `crates/tracera-server/src/main.rs` exceeds the 500-line module limit and needs
  cohesive router/runtime extraction.
