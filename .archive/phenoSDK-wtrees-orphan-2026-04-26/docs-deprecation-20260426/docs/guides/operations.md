# Operations Playbook

Pheno-SDK ships with production-grade tooling. This guide captures operational practices for running the platform in staging and production.

## Deployment Strategy

### Single Service Deployments
- Use [deploy-kit](../kits/deploy-kit.md) for Python services targeting Docker, serverless functions, or container orchestrators.
- For Vercel/Supabase stacks, rely on the YAML workflow described in [multi-cloud-deploy-kit](../kits/multi-cloud-deploy-kit.md).
- Keep deployment manifests in `deploy/` and version them with your code.

### Multi-Service Pipelines
- Leverage workflow-kit to orchestrate rollouts (database migrations → warmup → traffic shift).
- Use orchestrator-kit to coordinate cross-service actions (e.g., cache invalidations, event replay).

## Observability

1. **Logging** – Configure `StructuredLogger` sinks (stdout, JSON file, log aggregation). Tag logs with `service`, `environment`, and `tenant`.
2. **Metrics** – Expose Prometheus metrics using the exporters from observability-kit. Use dashboards to monitor latency, throughput, and error rates.
3. **Tracing** – Enable OpenTelemetry exporters. Propagate trace contexts via HTTP headers (`traceparent`) and messaging metadata.
4. **Health Checks** – Combine process-monitor-sdk liveness endpoints with workflow-kit status signals.

## Configuration & Secrets Management
- Store runtime configuration through config-kit loaders pulling from environment variables, secret managers, or remote config stores.
- Rotate credentials regularly and reload via config-kit hot-reload hooks.

## Failure Recovery
- Event-kit and workflow-kit provide retry and compensation policies—configure them per operation.
- Use stream-kit with replayable message buffers to recover clients after transient outages.
- Maintain run books for each kit’s failure scenarios (see the *Troubleshooting* section in individual manuals).

## Security Considerations
- auth adapters handle token verification, refresh flows, and session hygiene.
- db-kit enforces row-level security when tokens are provided; ensure policies exist for every table.
- Validate configuration with typed models to avoid injection or misconfiguration.
- Log sensitive operations with anonymized metadata to satisfy auditing requirements.

## Release Management
- Run `build-analyzer-kit` to validate compatibility before tagging releases.
- Use semantic versioning: `MAJOR` for breaking API changes, `MINOR` for new features, `PATCH` for bug fixes.
- Update kit manuals and `llms.txt` for user-facing changes.
- Tag Git releases and publish to PyPI using deploy-kit’s release automation.

## Incident Response
- Set up alerting on metrics such as error rate, queue backlog, and memory usage.
- Use orchestrator-kit to trigger remediation workflows (e.g., restart services, flush caches).
- Document incidents and link postmortems to the relevant kit manuals or operational guides.

## Checklist for Production Readiness
- [ ] Configuration validated in staging
- [ ] Observability (logs, metrics, traces) hooked into dashboards
- [ ] Health checks responding correctly
- [ ] Workflows have compensation steps defined
- [ ] Backups configured for storage-kit providers
- [ ] Security policies verified (RLS, authentication, authorization)
- [ ] Runbooks live in the repository under `docs/guides/runbooks/**`

## CLI Helpers

The bundled `pheno` CLI exposes ops-focused commands:

| Command | Purpose |
|---------|---------|
| `./pheno schema check` | Compare Supabase schema snapshots with the live database (requires Supabase credentials) |
| `./pheno schema update` | Refresh the local snapshot after applying migrations |
| `./pheno deploy --target vercel` | Run deployment readiness checks (verifies `vercel.json`, build scripts, git cleanliness) |
| `./pheno embeddings --entity-types …` | Backfill embeddings using the shared progressive vector pipeline |

Run each command with `--help` to review optional flags and environment requirements.

Operations evolve with the platform—when you add new tooling or patterns, extend this guide and cross-link the appropriate kit manuals.
