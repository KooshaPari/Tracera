# Installing Tracera

Tracera is a connector-first, end-to-end screen-time platform: an ElectroBun desktop
client plus a Go/Python server stack backed by Postgres, Redis, and NATS. This guide
walks through installing the full system on macOS, Windows, and Linux.

## TL;DR (one-click desktop install)

For most users, the fastest path is the packaged desktop client. A future Homebrew
tap will provide a one-liner:

`brew install tracertm`

Until that lands, grab the latest build from
<https://github.com/KooshaPari/Tracera/releases>:

- macOS: `TraceRTM-mac.dmg` (universal, Apple Silicon + Intel)
- Windows: `TraceRTM-win.exe` (NSIS installer, x64 + arm64)
- Linux: `TraceRTM-linux.AppImage` (x64) or `TraceRTM-linux.deb`

Double-click the installer, launch TraceRTM, and sign in. The desktop client bundles
a local gateway and talks to Tracera Cloud by default. To point it at your own server,
open Settings -> Gateway and enter your `http://localhost:4000` (or remote) URL.

## macOS

Native services are preferred over Docker where possible. The whole stack is wired
up by `make dev`, which uses `process-compose.yml` to start Postgres, Redis, NATS,
the Go API, the Python gateway, and the Bun web app together.

Install the host prerequisites with Homebrew:

`brew install bun postgresql@16 redis nats docker`

Then clone and boot:

`git clone https://github.com/KooshaPari/Tracera`

`cd Tracera && bun install`

`make dev`

On first run, `make dev` provisions the Postgres role and database, applies Alembic
migrations, seeds dev fixtures, and prints the web/gateway URLs. Add
`eval "$(brew services start postgresql@16)"` (or start it via the macOS Control
Plane app) if you want Postgres to survive reboots; otherwise the process-compose
supervisor handles it for the lifetime of the dev session.

## Windows

Windows is fully supported via WSL2 or native tooling. The recommended path uses
`winget` to install Node, Bun, and Docker Desktop:

`winget install OpenJS.NodeJS.LTS oven-sh.Bun Docker.DockerDesktop`

Reboot after the Docker Desktop install so the WSL2 kernel updates. Then, in a
PowerShell or Windows Terminal window:

`git clone https://github.com/KooshaPari/Tracera`

`cd Tracera; bun install; make dev`

If you prefer WSL2 (Ubuntu 22.04+), follow the Linux section inside the WSL distro
instead -- `make dev` works identically. WSL2 is required for the Postgres/Redis/NATS
sidecars when running native; Docker Desktop's WSL2 backend is the only Windows
host that supports the Linux-native server stack reliably.

## Linux (Ubuntu 22.04+)

Tracera runs cleanly on Ubuntu 22.04 LTS and newer. Install Bun via the official
script, then add Postgres and Redis from the system repos:

`curl -fsSL https://bun.sh/install | bash`

`sudo apt install postgresql-16 redis-server`

NATS is shipped as a static binary fetched by `make dev`'s process-compose
manifest, so no system package is required. Clone and boot:

`git clone https://github.com/KooshaPari/Tracera`

`cd Tracera && bun install`

`make dev`

For Fedora/Arch, swap the package manager calls for the equivalent `dnf` or
`pacman` packages (`postgresql16-server`, `redis`, `bun` from the AUR). Docker is
optional on Linux: `make dev` will use the system `postgres` and `redis-server`
processes when present and only fall back to the Docker sidecars if they are
missing.

## Without desktop (server only)

If you only want the server stack -- for example, to host a shared Tracera
instance or develop against the API from a remote machine -- you do not need the
ElectroBun client. `make dev` brings up Postgres, Redis, NATS, the Go API on
:3000, the Python gateway on :4000, and the Bun web app on :5173 via
`process-compose.yml`.

After `make dev` reports healthy, you can connect to:

- Web UI: <http://localhost:5173>
- HTTP API: <http://localhost:3000>
- Gateway (WebSocket + REST): <ws://localhost:4000> / <http://localhost:4000>
- Postgres: `localhost:5432` (user `tracera`, db `tracera`)
- Redis: `localhost:6379`
- NATS: `localhost:4222`

To run only the server pieces without the web app, use `make dev:server`. To run
just the database sidecars (for IDE integration), use `make dev:infra`.

## Verify install

Smoke-test the gateway health endpoint once `make dev` reports all services
healthy:

`curl http://localhost:4000/healthz`

Expected response:

`{"ok": true}`

A 200 with `{"ok": true}` means Postgres, Redis, and NATS are reachable from the
Python gateway. Then check the Go API:

`curl http://localhost:3000/healthz`

which should also return `{"ok": true}` with a `version` field. If either endpoint
returns non-2xx, jump to the Troubleshooting section below.

## Uninstall

Stop the dev stack and remove the Docker sidecars (only relevant if you opted
into the Docker-backed mode on Linux):

`make dev-down && docker rm -f trace-postgres trace-redis trace-nats`

`make dev-down` terminates the process-compose supervisor, kills the Go, Python,
and Bun processes, and stops any local Postgres/Redis/NATS processes it started.
It does not delete the Postgres data directory; remove it with
`rm -rf .data/pg` if you want a clean slate.

To uninstall the desktop client, drag `TraceRTM.app` from `/Applications` to
the Trash on macOS, use "Apps & Features" on Windows, or `sudo apt remove
tracertm` / delete the AppImage on Linux. The packaged client stores per-user
state under `~/Library/Application Support/TraceRTM` (macOS),
`%APPDATA%\TraceRTM` (Windows), and `~/.config/tracertm` (Linux); remove those
directories to wipe local caches and credentials.

## Troubleshooting

**Port 3000 or 4000 already in use.** Another service is bound to the port.
Stop it, or override the ports via env vars before `make dev`: `API_PORT=3001
GATEWAY_PORT=4001 make dev`. Update the desktop client's Settings -> Gateway URL
to match.

**Docker not running (Linux).** The Docker-backed sidecars require the daemon.
Start it with `sudo systemctl start docker` and re-run `make dev`. To avoid
Docker entirely, install native `postgresql-16` and `redis-server` -- `make dev`
will auto-detect them and skip the Docker fallback.

**`brew` permission denied on macOS.** Don't `sudo brew`. Fix the ownership of
`/usr/local` (Intel) or `/opt/homebrew` (Apple Silicon):
`sudo chown -R $(whoami) $(brew --prefix)`. On Apple Silicon, also ensure your
shell PATH includes `$(brew --prefix)/bin`.

**`bun: command not found` after install.** The Bun installer writes to
`~/.bun/bin`. Add `export PATH="$HOME/.bun/bin:$PATH"` to your shell rc and
re-source it, or log out and back in.

**`make dev` hangs on "waiting for postgres".** The Postgres sidecar may have
failed to initialize. Check `docker logs trace-postgres` (Docker mode) or
`tail -f .data/pg/logfile` (native mode). Common cause: a stale data directory
from a previous run -- delete `.data/pg` and retry.

**WebSocket connection refused at `:4000`.** The Python gateway depends on
NATS; if NATS failed to start, the gateway will exit immediately. Run
`make dev:infra` in isolation and check `nats-server --version` is at least
2.10.

**Health check returns `{"ok": false, "deps": {"postgres": "down"}}`.** The
gateway can reach its own port but not the database. Verify
`pg_isready -h localhost -p 5432` and `redis-cli ping`. If either is down,
`make dev-down` and `make dev` again to re-provision.

For issues not covered here, file a bug at
<https://github.com/KooshaPari/Tracera/issues> with the output of
`make doctor` (a diagnostic target that dumps version, port, and dependency
status into a redacted report).
