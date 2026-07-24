# Tracera parity and polyglot bootstrap

## Goal

Record the resumed frontend contract-alignment work and the Phase-2 Go sidecar
bootstrap so a fresh agent can continue without reconstructing terminal history.

## Success criteria

- Web client calls only the Rust-compatible contract surface.
- GET/POST smoke checks, route checks, build, and typecheck pass.
- Go sidecar scaffold builds and is disabled by default.
- Follow-up integration remains explicitly gated by contract tests.

## Current state

The frontend parity slice and Go bootstrap are implemented in the working tree.
The sidecar is heartbeat-only; it does not yet mutate Tracera data or proxy API
traffic.

## Verified release posture (2026-07-20)

- Release gates and dry-runs were green on head `892bea9` where GitHub-hosted
  runners were available; desktop/server archives carry provenance attestations.
- Pages rejects private/non-HTTPS production API origins. The configured
  Tailscale address is intentionally rejected; authenticated public ingress is
  not deployed.
- `crates/tracera-server/src/main.rs` remains above the 500-line mandate and is
  the next Rust decomposition slice.
