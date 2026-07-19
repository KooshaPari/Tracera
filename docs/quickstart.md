# Tracera Quickstart

## 1) Bootstrap

The shipped API is the Rust `tracera-server` binary in
`crates/tracera-server`. The historical Python `tracertm` service is not the
runtime used by the web dashboard.

```bash
cargo build --release -p tracera-server
```

## 2) Configure runtime security inputs

```bash
export TRACERA_BIND_ADDR=127.0.0.1:8080
export TRACERA_DB_PATH=/tmp/tracera-quickstart.db
```

## 3) Start API

```bash
./target/release/tracera-server
```

## 4) Verify hardening points

```bash
curl -i http://127.0.0.1:8080/health
curl -i http://127.0.0.1:8080/ready
curl -i http://127.0.0.1:8080/evidence
```

Expected behavior:

- `/health` and `/ready` return 200 without auth (public probes).
- Evidence and governance endpoints are currently unauthenticated; expose the
  server only behind the authenticated Caddy/WorkOS boundary described in
  [`deploy/selfhost/README.md`](../deploy/selfhost/README.md).

## 5) Deployment authentication

Authentication is enforced at the Caddy/WorkOS ingress in the self-hosted
deployment. Do not expose port 8080 directly. After configuring the ingress,
repeat the checks above through the public HTTPS hostname.

## 6) API surface checks

- Review stubs and route coverage in [`API_REFERENCE.md`](API_REFERENCE.md).
- Confirm FR→endpoint mapping in
  [`docs/governance/policy/endpoint_traceability_map.md`](governance/policy/endpoint_traceability_map.md).
