# Validation

## Governance

- `python3 /Users/kooshapari/CodeProjects/Phenotype/repos/Tracera/validate_governance.py`
- Result: `13/13 passed, 0 failed`

## Observability

- Live docs now point to Grafana Alloy and Tempo as the default path
- Historical tracing references remain only in archival material
- Runtime backend deployment now exports traces through `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT`
- Native Alloy startup script and local Alloy config are restored
- Grafana Tempo datasource provisioning is restored as `shared-traces`
- APM guide and quick reference are restored

## Frontend

- `bun run typecheck` passes from `frontend/`
- `bun run typecheck` passes from `frontend/apps/web`
- `bunx turbo build --filter=@tracertm/web` passes from `frontend/`
- `bun run build && bun run test` passes from `frontend/packages/ui`
- UI package test result: 24 files and 222 tests passed

## Backend

- Focused compile gate passes:
  `go test -run '^$' ./cmd/tracertm ./internal/services ./internal/server ./internal/config ./internal/tracing`

## Open follow-up

- Clean the archived reference docs and historical ADRs if you want the repo to become
  fully free of historical tracing references in prose as well as runtime wiring
- Run native/process-compose stack bring-up and record endpoint health
- Treat `bun run check:type-aware` as a separate quality backlog until the
  `oxlint-tsgolint` diagnostics and panic are resolved
