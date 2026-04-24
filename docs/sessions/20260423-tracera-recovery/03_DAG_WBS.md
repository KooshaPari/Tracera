# DAG and WBS

## Current Recovery DAG

```text
R1 recover implementation tree
  -> R2 restore governance requirements
  -> R3 align observability contract
  -> R4 validate backend compile surface
  -> R5 validate frontend package/web surface
  -> R6 classify remaining lint and runtime bring-up backlog
  -> R7 full native stack bring-up
```

## Work Breakdown

| ID | Status | Work | Evidence |
| --- | --- | --- | --- |
| R1 | Done | Mirror recovered Go, Python, React, deploy, config, and tests into `Tracera` | `backend/`, `src/tracertm/`, `frontend/`, `deploy/`, `config/` present |
| R2 | Done | Restore missing `FR-TRAC-004` through `FR-TRAC-006` | `python3 validate_governance.py` passes 13/13 |
| R3 | Done | Move live docs and backend deploy manifest to shared OTLP/Tempo path | `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT=tracera-collector:4317` |
| R4 | Done | Confirm focused Go backend compile surface | `go test -run '^$' ./cmd/tracertm ./internal/services ./internal/server ./internal/config ./internal/tracing` |
| R5 | Done | Restore UI package dependencies and validate frontend build | `bun run typecheck`, `bunx turbo build --filter=@tracertm/web`, UI tests pass |
| R6 | Done | Separate compiler typecheck from experimental type-aware lint backlog | `lint:type-aware` is isolated from `typecheck` |
| R7 | In progress | Repair native Alloy/Tempo runtime contract | `alloy-if-not-running.sh`, `alloy-local.alloy`, and `tempo.yml` restored |
| R8 | In progress | Restore frontend lint/test gate determinism | `.oxlintrc.json` restored; package test imports normalized; Storybook setup restored |
| R9 | Pending | Bring up native/process-compose stack and validate health | Requires live service startup pass |

## Next Queue

1. Run a native stack bring-up using `process-compose.yml` or repo scripts and record service health.
2. Run full frontend monorepo tests after package-level import fixes.
3. Audit `lint:type-aware` diagnostics separately from TypeScript compile correctness.
4. Align AgilePlus and PhenoObservability to the same shared OTLP endpoint names.
5. Decide whether archived/generated docs should be scrubbed or explicitly marked archival.
6. Normalize the recovered implementation surface into a clean branch/commit boundary.
