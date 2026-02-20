# Neo4j local dev – debug and plan

## What’s going on

- **`brew services start neo4j`** (no sudo) can fail with:
  - `launchctl bootstrap gui/501 ... exited with 5` (service not starting under your user).
- **`sudo brew services start neo4j`** can start Neo4j but:
  - Changes ownership of Neo4j paths to root; Homebrew warns “neo4j must be run as non-root to start at user login”.
- **`rtm dev start`** auto-start can “hang” because:
  - The script calls `brew services start neo4j` first; that call can block or fail in a way that doesn’t return quickly.
  - Only later does it try `neo4j start` (CLI).

So: launchd/brew services is brittle for Neo4j on this setup; the Neo4j CLI (`neo4j start`) is the reliable, non-root path.

## Plan (script behavior)

1. **Prefer Neo4j CLI over brew services**
   - If `neo4j` (or `$(brew --prefix neo4j)/bin/neo4j`) is available, use **only** `neo4j start` and wait for port 7687.
   - Do **not** call `brew services start neo4j` when the CLI is available (avoids launchctl and hang).
2. **Use brew services only when CLI is missing**
   - If Neo4j CLI is not found, then try `brew services start neo4j` with a **short timeout** (e.g. 15s) so the script never blocks indefinitely.
3. **Clear failure message**
   - If Neo4j never listens on 7687, tell the user to run `neo4j start` or `neo4j console` (to see errors) and then `rtm dev start` again.

## Manual recovery

If auto-start still doesn’t get Neo4j up:

1. **Start Neo4j as your user (recommended)**  
   ```bash
   neo4j start
   # or: $(brew --prefix neo4j)/bin/neo4j start
   ```
   Wait until port 7687 is listening (~20–40s), then run `rtm dev start`.

2. **See why it’s failing**  
   ```bash
   neo4j console
   ```
   Fix Java/config errors if any, then use `neo4j start` and `rtm dev start`.

3. **Avoid sudo for normal dev**  
   Prefer fixing permissions or using `neo4j start` so you don’t need `sudo brew services start neo4j` for daily use.

## References

- Script: `scripts/start-services.sh` → `start_neo4j`
- Preflight: `src/tracertm/preflight.py` → dev checks for `NEO4J_URI` (port 7687)
