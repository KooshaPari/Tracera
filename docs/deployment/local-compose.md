# Local desktop deployment

The canonical local profile is `docker-compose.yml`. It runs PostgreSQL and
the Rust server as one restartable Compose stack; the Rust image contains the
approved rich React dashboard and serves it from the same origin as the API.
The database stays private to the Compose network and only the loopback
gateway is published at `127.0.0.1:18000`, so browsers on the desktop use one
origin and do not need a Vercel or public API endpoint.

Create the ignored host environment file once. Do not commit it or paste its
value into shell history:

```sh
cp .env.example .env.local
# Replace POSTGRES_PASSWORD with a long random value in .env.local.
chmod 600 .env.local
docker compose --env-file .env.local -f docker-compose.yml up -d --build
curl --fail --silent http://127.0.0.1:18000/health
```

Run the read-only operational probe after startup or restart. By default it
checks the canonical `postgres` and `tracera-server` services, API
liveness/readiness, and the rich frontend response on `:18000`; it does not
change service state. Set `TRACERA_TAILSCALE_URL` to additionally probe the
desktop URL from the host:

```sh
scripts/local-stack-health.sh
TRACERA_TAILSCALE_URL=http://100.112.14.98:18000 scripts/local-stack-health.sh
```

The same env file makes restarts deterministic. Restart only this Compose
project (the existing Grapheon service on port 8080 is unrelated):

```sh
docker compose --env-file .env.local -f docker-compose.yml restart
docker compose --env-file .env.local -f docker-compose.yml ps
curl --fail --silent http://127.0.0.1:18000/health
```

The canonical Compose file intentionally binds loopback only. For deliberate
Tailnet access, set the bind address and keep the public host port at `:18000`;
do not replace the service's internal `:8080` listener:

```sh
TRACERA_LOCAL_BIND_ADDR=100.112.14.98 TRACERA_LOCAL_PORT=18000 \
  docker compose --env-file .env.local -f docker-compose.yml up -d
```

Then open
`http://<desktop-tailscale-ip>:18000/` and check
`http://<desktop-tailscale-ip>:18000/health` from another Tailnet device.

## Explicit legacy split-frontend stack

Older developer installs may still use `docker-compose.local.yml`, which
publishes a separate nginx frontend on `:18081`. This is not the canonical
dashboard path and must be selected explicitly:

```sh
TRACERA_LEGACY_LOCAL_STACK=1 \
  docker compose --env-file .env.local -f docker-compose.local.yml up -d --build
TRACERA_LEGACY_LOCAL_STACK=1 scripts/local-stack-health.sh
```

The legacy stack's default is loopback-only. Set `TRACERA_LOCAL_PORT=18082`
only when its `:18081` publication is occupied. Do not bind port `8080`.

Stop the stack with:

```sh
docker compose --env-file .env.local -f docker-compose.yml down
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
docker compose --env-file .env.local -f docker-compose.yml exec postgres \
  psql -U tracera -d tracera -c \
  "ALTER ROLE tracera WITH PASSWORD '<value from .env.local>';"
docker compose --env-file .env.local -f docker-compose.yml restart tracera-server
scripts/local-stack-health.sh
```

The placeholder is deliberate. Never paste a real password into shared logs,
documentation, or shell history.
