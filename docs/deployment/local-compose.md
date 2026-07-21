# Local desktop deployment

The local profile runs PostgreSQL, the Rust API, and the React dashboard as one
restartable Compose stack. The database and API stay private to the Compose
network; only the frontend is published, so browsers on the desktop or Tailnet
use one origin and do not need a Vercel or public API endpoint.

```sh
export POSTGRES_PASSWORD='use-a-local-only-password'
docker compose -f docker-compose.local.yml up -d --build
curl http://127.0.0.1:18081/health
```

From another Tailnet device, open `http://<desktop-tailscale-ip>:18081/`.
Override the port with `TRACERA_LOCAL_PORT=18082` if 18081 is occupied. Do not
bind port 8080: it is reserved by the existing Grapheon service on the desktop.

Stop the stack with `docker compose -f docker-compose.local.yml down`.
