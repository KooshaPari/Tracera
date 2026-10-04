# Next deployable release gate — Tracera

Date: 2026-10-04

## Target topology

- Static/web frontend: Vercel Hobby.
- Stateful Rust backend and databases: owner's desktop.
- Public backend ingress: Cloudflare Tunnel; no inbound router port required.
- Reverse proxy/security boundary: Caddy.
- Incremental hosting spend: $0.

The existing Vercel catch-all can proxy to `TRACERA_BACKEND_URL`. The desktop
self-host stack already contains tracera-server, Caddy and cloudflared.

## Release definition

The next deployed release is not “a Vercel URL renders.” It requires:

1. production frontend build succeeds on Hobby limits;
2. frontend points to the live authenticated backend/proxy, not fallback stubs;
3. desktop backend survives restart and has persistent data;
4. strict public deployment security gate passes;
5. Cloudflare Tunnel health/readiness passes;
6. HJ-PRE-001 product open/select closes in the deployed environment;
7. HJ-PRE-002 inventory closes;
8. HJ-PRE-003 unified graph renders correct fixture truth;
9. no fallback-to-stub response is presented as real product data;
10. backup/restore and rollback instructions are executable.

## Time-to-release estimate

Assuming focused work, desktop availability, and no newly discovered browser
regression:

- private/operator remote alpha: **1–2 working days**;
- useful authenticated cloud alpha covering HJ-PRE-001..003: **3–5 working days**;
- broader recovered-product alpha covering HJ-PRE-001..008: **7–12 working days**.

These are engineering estimates, not completion claims. Historical executable
parity and 10K+ graph optimization are not prerequisites for the first cloud
alpha; correctness of the journeys shipped in that alpha is.
