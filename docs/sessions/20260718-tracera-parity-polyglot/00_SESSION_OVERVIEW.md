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
