# Patterns & Best Practices

This guide captures the core paradigms that repeat across Pheno-SDK kits. Use it as a checklist when designing new modules or integrating the SDK with an existing system.

## Configuration & Secrets
- Use `config_kit.loaders` to merge environment variables, `.env` files, and explicit overrides.
- Represent configuration as Pydantic models to benefit from validation and typed access.
- Store secrets in environment variables or secret managers; never bake them into code.
- Version your configuration schemas alongside the services that consume them.

## Dependency Management
- Register expensive resources (database pools, clients) as singletons in the DI container.
- Register lightweight services per-request or per-workflow to keep state isolated.
- Provide factory callables for objects that depend on request-level context (e.g. tenant ID).

## Asynchronous Pipelines
- Schedule long running jobs using [workflow-kit](../kits/workflow-kit.md) sagas or orchestrator pipelines.
- Use stream-kit channels for real-time feedback and event-kit for durable fan-out.
- Keep CPU-bound work off the event loop—wrap with `anyio.to_thread` or external worker queues.

## Observability First
- Add structured logging contexts early (request IDs, tenant IDs, workflow IDs).
- Emit metrics with labels that match your dashboards (`service`, `environment`, `tenant`).
- Propagate trace contexts through HTTP headers, message metadata, and background tasks.
- Use `process-monitor-sdk` to expose health, readiness, and liveness probes.

## Error Handling
- Convert third-party errors into kit-specific exceptions before they cross boundaries.
- Use workflow compensation handlers to revert intermediate steps.
- Prefer retry policies with exponential backoff using event-kit or stream-kit middleware.

## Testing Strategy
- Use in-memory adapters (db-kit, storage-kit, event-kit) for fast unit tests.
- Rely on contract tests around adapters and middleware to validate provider integrations.
- Use `mcp-QA` pipelines for system-level validation of MCP-enabled features.
- Validate docs by running the examples in CI (each README example should be runnable).

## Versioning & Releases
- Keep kit versions in sync; update changelog entries in `docs/guides/operations.md`.
- Run `build-analyzer-kit` validation scripts before publishing to PyPI.
- Document breaking changes in kit manuals and mention migration paths.

## Contribution Etiquette
- Update the relevant kit manual whenever APIs change.
- Update cross-cutting concept docs when patterns evolve.
- Use the pull request checklist in [Contributing](../guides/contributing.md) before requesting review.

## Anti-Patterns to Avoid
- Global singletons without DI container involvement.
- Hard-coded environment IDs or tenant identifiers.
- Direct database access from interface layers without going through repositories.
- Missing observability due to ad-hoc logging or metrics.
- Ignoring backpressure signals in streaming and evented systems.

Keep your implementations aligned with these patterns to maintain consistency across the ecosystem.
