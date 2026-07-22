# Rich dashboard oracle smoke contract

`scripts/rich-oracle-smoke.py` is the preflight for the approved rich frontend
snapshot (`36b6055fa`). It does not import frontend code, mutate containers, or
assume that the Python oracle is running.

## Contract

- `VITE_API_BASE` (or `--base-url`) must be an origin on gateway port `18000`.
- The default static mode validates the origin and records the seven core read
  paths without network access.
- `--live` performs read-only GET requests with a 0.1--10 second per-request
  timeout. A stopped gateway is reported as `skipped`; 404 is `unavailable`.
  Auth-protected responses (401/403) are `reachable`, not a fake success.
- Port `8080` is never accepted because Grapheon owns it.

Examples:

```sh
python3 scripts/rich-oracle-smoke.py
python3 scripts/rich-oracle-smoke.py --live --base-url http://127.0.0.1:18000
python3 scripts/rich-oracle-smoke.py --live --json > /tmp/rich-oracle-smoke.json
```

This is an integration gate only; it does not replace authenticated browser
tests once the isolated Python/Go gateway is deployed.
