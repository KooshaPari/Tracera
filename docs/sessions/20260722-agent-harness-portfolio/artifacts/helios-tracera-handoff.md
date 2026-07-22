# Helios -> Tracera ingestion handoff

Date: 2026-07-22

## Contract

- Schema: `docs/sessions/20260722-agent-harness-portfolio/artifacts/benchmark_run.schema.json`
- Version: `1.0.0` (Draft 2020-12)
- Producer: `helios-cli/harness` `benchmark_envelope.add_envelope`
- Source snapshot: HeliosCLI local working branch; snapshot/airlock branch is pending because the host was resource-saturated.

## Event mapping

| Envelope event | Tracera record | Required links |
|---|---|---|
| `run_started` | run/session start | tenant, session, run, attempt causality |
| `checkpoint` | durable resume boundary | checkpoint ID, event sequence, artifact hash |
| `compaction` | context reduction | checkpoint ID, tokens before/after, retained/dropped event IDs |
| `heartbeat` / lease events | worker liveness | lease ID, owner, attempt |
| `tool_call` / `tool_result` | tool span | parent event, payload hash, policy decision |
| `retry` / `restart` | recovery attempt | retry/restart index and causal parent |
| `run_finished` | terminal outcome | status, failure class, replay hash |

## Artifact semantics

`result.artifacts` is content-addressed: each entry contains `kind`, `uri`, and SHA-256 `sha256`. Legacy Helios evidence is retained as `result.outcome_sha256` and a report artifact URI of the form `urn:helios:legacy-evidence:<digest>`. Tracera should preserve the URI/hash pair and reject mismatched content. `result.replay_hash` covers the normalized event stream and artifact hashes.

## Validation

Expected fastjsonschema command:

```sh
python3 - <<'PY'
import json, fastjsonschema
schema = json.load(open('docs/sessions/20260722-agent-harness-portfolio/artifacts/benchmark_run.schema.json'))
fastjsonschema.compile(schema)
print('fastjsonschema_pass')
PY
```

The strict envelope has already passed Draft 2020-12 validation in the Helios workspace. A direct fastjsonschema pass should be run in the target Tracera environment before enabling ingestion.

## Remaining caveats

- Host saturation caused intermittent `jsonschema` import and full pytest hangs; no full pytest claim is made.
- The current signature is an explicit placeholder and must be replaced by a configured signing key before compliance-grade ingestion.
- Unknown commit/model/hardware values remain explicit until pinned run metadata is available.
