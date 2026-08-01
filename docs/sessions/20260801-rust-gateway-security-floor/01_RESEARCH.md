# Rust gateway security floor research

## Scope

Bounded hardening of the Tracera Rust gateway: public listener safety and
datastore-backed readiness. No browser credential model or broad authentication
redesign is included in this packet.

## Evidence and decision

- `crates/tracera-server/src/main.rs` previously allowed a non-loopback
  `TRACERA_BIND_ADDR` after logging only a warning. The same router exposes
  unauthenticated mutating endpoints.
- `deploy/selfhost/Caddyfile` has only a commented authentication example, so a
  public compose run must not start by default until an ingress authentication
  directive is active.
- `crates/tracera-server/src/health.rs` previously reported `/ready` and
  `/readyz` from process uptime alone. Both supported stores can execute a
  minimal `SELECT 1` probe without leaking datastore errors to callers.

## Chosen contract

1. Loopback binding remains the default and needs no additional environment.
2. A non-loopback bind fails closed unless
   `TRACERA_PUBLIC_BIND_MODE=authenticated-proxy` is explicitly supplied.
   This is an acknowledgement gate, not an implementation of end-user auth;
   self-host ingress must still enforce authentication.
3. `/health` remains a process liveness endpoint. `/ready` and `/readyz` return
   HTTP 503 with a stable non-sensitive JSON status whenever the store probe
   fails.
