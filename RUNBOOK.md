# RUNBOOK

Day-2 operations for the local dev stack defined in `process-compose.yml`.
Process names referenced below (`postgres`, `redis`, `nats`, `trace-api`, `tracertm-web`,
plus the conceptual `gateway`) match the keys in that file.

## 1. Start / Stop

The user runs the dev TUI in their own terminal. Use these targets from a separate shell;
do not start or stop the full stack from here unless asked.

| Action          | Command            | Notes                                              |
| --------------- | ------------------ | -------------------------------------------------- |
| Start           | `make dev`         | Boots postgres, redis, nats, gateway, web, api.    |
| Stop            | `make dev-down`    | Tears the whole stack down cleanly.                |
| Status          | `make dev-status`  | Lists process health, PID, uptime per service.     |
| Tail logs       | `make dev-logs`    | Follows all service logs; Ctrl-C to detach.        |
| Restart one     | `make dev-restart <name>` | e.g. `make dev-restart trace-api`.         |

## 2. Logs

Per-service `docker logs` (compose runs each backing service in a container):

```bash
# Postgres
docker logs -f --tail 200 trace-postgres

# Redis
docker logs -f --tail 200 trace-redis

# NATS
docker logs -f --tail 200 trace-nats

# Gateway
docker logs -f --tail 200 trace-gateway

# Web (Vite dev server)
docker logs -f --tail 200 trace-web
```

For compose-managed services without `docker logs`, use `make dev-logs` and filter by
process name (`postgres`, `redis`, `nats`, `trace-api`, `tracertm-web`).

## 3. DB migrations

Alembic is the source of truth (`alembic/`, `alembic.ini`).

```bash
make db-migrate    # alembic upgrade head
make db-rollback   # alembic downgrade -1
make db-reset      # drop + recreate tracertm, then upgrade head (destructive)
make db-shell      # opens psql as user tracertm against db tracertm
```

Manual equivalent:

```bash
docker exec -it trace-postgres psql -U tracertm -d tracertm
```

## 4. Backups

Logical dump via `pg_dump`, restore via `psql`. The dev DB user/db are `tracertm`.

```bash
# Backup
pg_dump -U tracertm tracertm > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore (drops conflicting objects unless --clean is added to the dump)
psql -U tracertm tracertm < backup.sql
```

For point-in-time recovery, prefer the managed Postgres backup workflow in
`docs/operations/backups.md`; local `pg_dump` is fine for day-2 dev snapshots.

## 5. Scaling

Edit `process-compose.yml` and restart only the affected process.

| Service   | Knob                                                              |
| --------- | ----------------------------------------------------------------- |
| postgres  | `postgres.command` -- append `--max-connections=N` to the docker run args (e.g. `200`). |
| redis     | `redis.command` -- append `--maxmemory 2gb --maxmemory-policy allkeys-lru`. |
| nats      | `nats.command` -- add `-js` (already on) and increase `-m 8222` monitoring; scale JetStream via `NATS_STREAM_STORE_DIR=/data`. |
| trace-api | Run multiple replicas behind the gateway; set `--workers N` on the `air` command. |
| gateway   | Add `GATEWAY_WORKERS=N` env var or scale via compose replicas.    |

After editing, `make dev-restart <name>`.

## 6. Observability

| Surface           | Endpoint                  | Purpose                              |
| ----------------- | ------------------------- | ------------------------------------ |
| NATS dashboard    | http://localhost:8222     | Connections, JetStream, slow consumers. |
| Gateway metrics   | http://localhost:4000/metrics | Prometheus scrape (RPS, latency, errors). |
| OTLP gRPC         | localhost:4317            | Traces from trace-api / gateway.     |
| OTLP HTTP         | localhost:4318            | Trace fallback.                      |
| Health: postgres  | `pg_isready` exec probe   | See `process-compose.yml`.           |
| Health: redis     | `redis-cli ping`          | See `process-compose.yml`.           |
| Health: nats      | http_get :8222/healthz    | See `process-compose.yml`.           |

## 7. Common ops

**Rotate the DB password**

```bash
docker exec trace-postgres psql -U tracertm -d tracertm \
  -c "ALTER USER tracertm WITH PASSWORD '${DB_PASSWORD_NEW}';"
# then update .env / shell env and `make dev-restart postgres trace-api gateway`
```

**Revoke a user**

```bash
docker exec trace-postgres psql -U tracertm -d tracertm \
  -c "REVOKE ALL PRIVILEGES ON DATABASE tracertm FROM <user>;"
docker exec trace-postgres psql -U tracertm -d tracertm \
  -c "DROP USER <user>;"
```

**Add a new microservice**

1. Add a top-level `<name>:` block in `process-compose.yml` with `command`,
   `working_dir`, `environment`, `depends_on`, and a `readiness_probe`.
2. Add the service to the `make dev` target and to the gateway routing config.
3. Add its metrics port to the observability section in `docs/operations/observability.md`.

**Add a new frontend route**

1. Create the route file under `frontend/apps/web/src/routes/...` (TanStack Router file-based).
2. If the route needs API data, add the handler in `backend/...` and the typed client
   in `frontend/packages/api-client`.
3. Run `bun run typecheck` and `make dev-restart tracertm-web`.

## 8. Incident response

| Symptom                | First check                                          | Action                                          |
| ---------------------- | ---------------------------------------------------- | ----------------------------------------------- |
| Service stuck          | `make dev-status`                                    | `make dev-restart <name>`; if looping, `docker logs` then file a worklog entry. |
| Service OOM-killed     | `docker inspect <name> --format '{{.State.OOMKilled}}'` | Raise host RAM or scale the service; revisit section 5. |
| Disk full              | `df -h` and `du -sh /var/lib/docker`                | `./tooling/target-pruner --prune`; prune `docker system prune -a`. |
| Postgres won't start   | `docker logs trace-postgres`                         | Check `DB_PASSWORD` env, port 5432 conflicts, then `make dev-restart postgres`. |
| Redis won't start      | `docker logs trace-redis`                            | Check AOF/RDB volume perms, then `make dev-restart redis`. |
| NATS JetStream stuck   | http://localhost:8222/jsz                            | Inspect slow consumers; restart `nats`.         |
| Gateway 5xx storm      | `:4000/metrics`                                      | Roll back last deploy, then check upstream `trace-api` health. |
| Migration drift        | `make db-shell` then `\dt`                           | `make db-rollback` to last good rev, then `make db-migrate`. |

For anything not covered here, add an entry to
`docs/operations/incidents/<YYYY-MM-DD>-<slug>.md` so the next operator benefits.
