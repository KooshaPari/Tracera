# Local compute nodes (Coolify-style fleet)

Tracera treats any box you own — bare-metal OS install, VPS slice, homelab
machine — as a first-class deployment target. CI can publish services to the
whole fleet as easily as it deploys to Vercel.

## The pieces

| Piece                     | Location                                                          | Role                                                                                                                |
| ------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| Node daemon (sidecar)     | `sidecar/go/`                                                     | Runs on each node. Enrolls with the control plane, polls for desired state, runs `docker compose`, reports results. |
| Control plane             | `crates/tracera-edge/` (the CF Worker)                            | Registry + desired-state store, backed by Workers KV. Free tier.                                                    |
| CI hook                   | `.github/workflows/deploy-full-stack.yml` → `publish-fleet-state` | After a successful edge deploy, publishes the new image to all enrolled nodes.                                      |
| Per-node compose projects | `$TRACERA_NODE_STATE_DIR/<service>/docker-compose.yml`            | One minimal compose file per service, written by the daemon.                                                        |

## Node lifecycle

```
┌─────────┐    enroll(token)    ┌──────────────┐
│  node   │ ──────────────────▶ │ control plane │
│ (Go)    │                     │  (CF Worker)  │
│         │ ◀────────────────── │               │
│         │  desired(gen,svcs)  │               │
│         │                     │               │
│ docker  │    converge         │               │
│ compose │ ──────────────┐     │               │
│         │               ▼     │               │
│         │    report(ok|fail)  │               │
│         │ ──────────────────▶ │               │
└─────────┘                     └──────────────┘
```

1. **Enroll** — daemon POSTs node identity + caps + its enroll token.
   Rejected enrollment is fatal: the node runs nothing.
2. **Poll** — daemon GETs its desired state every
   `TRACERA_SIDE_CAR_POLL_INTERVAL`. No change (same generation) = no-op.
3. **Converge** — for each desired service, daemon writes a minimal compose
   project and runs `docker compose up -d --pull always`. An empty image
   means `compose down`. One service failing never blocks the others.
4. **Report** — daemon POSTs per-service results; control plane stores them
   and updates `last_seen`.

## Node configuration

| Env var                          | Required      | Default                 | Meaning                                                 |
| -------------------------------- | ------------- | ----------------------- | ------------------------------------------------------- |
| `TRACERA_SIDE_CAR_ENABLED`       | yes           | `false`                 | Master switch                                           |
| `TRACERA_CONTROL_PLANE_URL`      | for node mode | —                       | e.g. `https://tracera-edge.kooshapari.workers.dev`      |
| `TRACERA_NODE_ID`                | for node mode | —                       | Unique name, 1..=128 chars                              |
| `TRACERA_ENROLL_TOKEN`           | for node mode | —                       | Shared secret set as `FLEET_ENROLL_TOKEN` on the worker |
| `TRACERA_NODE_STATE_DIR`         | no            | `/var/lib/tracera-node` | Where compose projects live                             |
| `TRACERA_NODE_CONVERGE_TIMEOUT`  | no            | `5m`                    | Per-invocation docker timeout                           |
| `TRACERA_SIDE_CAR_POLL_INTERVAL` | no            | `5s`                    | Poll interval                                           |

If any of the three "node mode" vars are missing, the daemon falls back to
its original heartbeat-only behavior (inert, backward compatible).

## Run a node

```sh
# build once
cd sidecar/go && go build -o tracera-sidecar ./cmd/tracera-sidecar

# run as a service (systemd unit or similar)
TRACERA_SIDE_CAR_ENABLED=true \
TRACERA_CONTROL_PLANE_URL=https://tracera-edge.kooshapari.workers.dev \
TRACERA_NODE_ID=homelab-01 \
TRACERA_ENROLL_TOKEN=<from FLEET_ENROLL_TOKEN worker secret> \
./tracera-sidecar
```

The node needs Docker installed and the enroll token. That is the whole
requirements list — the goal is "install on any app/OS slice without a full
platform deploy".

## Deploying to the fleet

After the worker is deployed, set two GitHub values:

- repo **variable** `FLEET_BASE_URL` = the worker's public URL
- repo **secret** `FLEET_ENROLL_TOKEN` = the same token nodes use

Then `deploy-full-stack.yml` gains a final step: it PUTs the freshly built
`tracera-server:<sha>` image as desired state. Every enrolled node converges
within one poll interval. No manual SSH, no per-node runbook.

## Deliberately out of scope (v1)

- Per-node service assignment overrides (flat "all nodes get all services")
- A web dashboard (KV API is curl-able: `GET /fleet/nodes`)
- Rolling updates / canary weights
- Secrets distribution (use your platform's secrets manager)

## BytePort

BytePort is a separate deployable app in this ecosystem and is **not** part
of this fleet layer. The sidecar here is Tracera's own node agent; BytePort
keeps living at the app layer, installable per-app/OS like AgilePlus.
