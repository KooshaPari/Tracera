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

The same env file makes restarts deterministic. Restart only this Compose
project (the existing Grapheon service on port 8080 is unrelated):

```sh
docker compose --env-file .env.local -f docker-compose.local.yml restart
docker compose --env-file .env.local -f docker-compose.local.yml ps
curl --fail --silent http://127.0.0.1:18081/health
```

From another Tailnet device, open `http://<desktop-tailscale-ip>:18081/` and
check `http://<desktop-tailscale-ip>:18081/health`.
Override the port with `TRACERA_LOCAL_PORT=18082` if 18081 is occupied. Do not
bind port 8080: it is reserved by the existing Grapheon service on the desktop.

Stop the stack with:

```sh
docker compose --env-file .env.local -f docker-compose.local.yml down
```

To inspect failures without exposing credentials, use `docker compose ... logs
--tail=100` and redact environment values before sharing output.
