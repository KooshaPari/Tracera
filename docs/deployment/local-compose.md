# Local desktop deployment

The local profile runs PostgreSQL, the Rust API, and the React dashboard as one
restartable Compose stack. The database and API stay private to the Compose
network; only the frontend is published, so browsers on the desktop or Tailnet
use one origin and do not need a Vercel or public API endpoint.

Create the ignored host environment file once. Do not commit it or paste its
value into shell history:

```sh
cp .env.example .env.local
# Replace POSTGRES_PASSWORD with a long random value in .env.local.
chmod 600 .env.local
docker compose --env-file .env.local -f docker-compose.local.yml up -d --build
curl --fail --silent http://127.0.0.1:18081/health
```

Run the read-only operational probe after startup or restart. It checks all
three Compose services, API liveness/readiness, and the frontend response; it
does not change service state. Set `TRACERA_TAILSCALE_URL` to additionally
probe the desktop URL from the host:

```sh
scripts/local-stack-health.sh
TRACERA_TAILSCALE_URL=http://100.112.14.98:18081 scripts/local-stack-health.sh
```

The same env file makes restarts deterministic. Restart only this Compose
project (the existing Grapheon service on port 8080 is unrelated):

```sh
docker compose --env-file .env.local -f docker-compose.local.yml restart
docker compose --env-file .env.local -f docker-compose.local.yml ps
curl --fail --silent http://127.0.0.1:18081/health
```

The default frontend bind is loopback-only. For deliberate Tailnet access,
bind to the desktop's Tailscale address explicitly (or to all interfaces only
when the host firewall is understood):

```sh
TRACERA_LOCAL_BIND_ADDR=100.112.14.98 \
  docker compose --env-file .env.local -f docker-compose.local.yml up -d
```

Then open `http://<desktop-tailscale-ip>:18081/` and check
`http://<desktop-tailscale-ip>:18081/health` from another Tailnet device.
Override the port with `TRACERA_LOCAL_PORT=18082` if 18081 is occupied. Do not
bind port 8080: it is reserved by the existing Grapheon service on the desktop.

Stop the stack with:

```sh
docker compose --env-file .env.local -f docker-compose.local.yml down
```

To inspect failures without exposing credentials, use `docker compose ... logs
--tail=100` and redact environment values before sharing output.

## Credential drift recovery

The PostgreSQL role password lives in the persistent volume. Updating
`POSTGRES_PASSWORD` in `.env.local` does not update that existing role, so a
stack can show all services as running while the API health check fails. The
health probe detects PostgreSQL authentication-failure log signatures and
prints a secret-free recovery hint. Repair the role in place using the value
already intended for the API; do not remove the volume or print the value:

```sh
docker compose --env-file .env.local -f docker-compose.local.yml exec postgres \
  psql -U tracera -d tracera -c \
  "ALTER ROLE tracera WITH PASSWORD '<value from .env.local>';"
docker compose --env-file .env.local -f docker-compose.local.yml restart tracera-server
scripts/local-stack-health.sh
```

The placeholder is deliberate. Never paste a real password into shared logs,
documentation, or shell history.
