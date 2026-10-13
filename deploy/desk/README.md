Authored by Instinct.

# Tracera desk deploy (Windows desk + Fedora WSL podman)

Replaces the hand-run `run.bat` with scheduled tasks and a podman data plane. Podman only, no Docker Desktop.

| File | Purpose |
|---|---|
| compose.yml | Postgres 17 + Redis 7 (adopts the running containers); Neo4j behind `--profile graph`, enabled after the PG+Redis cutover |
| install.ps1 | Registers `TraceraServer` (at startup, restart on failure) and `TraceraBackup` (03:30); `-Staging` binds 127.0.0.1:18080 on `tracera_staging` |
| run-tracera.ps1 | Service entry point, reads untracked `tracera.env` |
| backup.ps1 | pg_dump / sqlite copy to C: and G:, SHA256, 14-day retention; R2 free tier offsite (7 newest), skipped if unconfigured |
| verify.ps1 | API, project count, no-HTML-for-unknown-API, PG row counts; non-zero exit on failure |
| sqlite2pg.py | sqlite -> Postgres COPY loader (shared columns; truncates target) |
| cutover.ps1 | backup, stop, final load, switch, start, verify; rolls back to sqlite on failure |

Order: `install.ps1 -Backend postgres -Staging` -> `verify.ps1 -Url http://127.0.0.1:18080` -> approved window -> `cutover.ps1`.
Requires a build that has migrations 0011/0012 (canonical graph), i.e. PR #1099 or later.
Secrets (DB password, R2 keys) never live in git; the DB URL is composed from the container env at install time.
