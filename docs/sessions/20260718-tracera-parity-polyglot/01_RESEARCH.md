# Research

- Rust server exposes `/health` and `/evidence`; frontend parity scripts use
  those endpoints plus the documented compatibility routes.
- `frontend/apps/web/src/services/traceraClient.js` is the single client
  surface for contract calls.
- Existing repository work established Go, Zig, and Mojo as optional polyglot
  lanes; this session advances Go first because it has the lowest integration
  risk. Zig/Mojo remain benchmark-gated.
- No external dependency or credential is required for the sidecar bootstrap.

## Rust HTTP boundary audit (2026-07-18)

- The server already defaults to loopback; explicit non-loopback binds now emit
  a startup warning requiring an authenticated TLS reverse proxy operationally.
- `DefaultBodyLimit` is set globally to 8 MiB before JSON/form extraction,
  bounding parser memory use while preserving existing request schemas.
- Responses add `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and
  `Referrer-Policy: no-referrer` when callers do not provide those headers.
- Evidence: `~/.cargo/bin/cargo check -p tracera-server` passes after the
  change; only pre-existing dead-code warnings remain.
