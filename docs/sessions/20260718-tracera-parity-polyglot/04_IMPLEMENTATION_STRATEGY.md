# Implementation strategy

The frontend remains a thin HTTP client and does not duplicate Rust business
logic. Contract smoke scripts run against a local mock so CI is deterministic.

The Go sidecar uses the standard library only. A small config package keeps
environment parsing testable and leaves the command entrypoint responsible only
for lifecycle and heartbeat scheduling. Integration with Rust is intentionally
deferred until read-only contract tests exist.
