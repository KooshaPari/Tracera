# Port Definitions

This document records the canonical ports (interfaces) exposed by `pheno-sdk` for
integrating with external systems. Each port lives in `pheno.ports` and is designed to
be implemented by adapters that wrap specific providers while keeping the application
core independent from the concrete client libraries.

## Database (PostgreSQL, Redis)

- **Module**: `pheno.ports.database`
- **Key contracts**:
  - `SQLDatabasePort` / `SQLTransactionPort` — async SQL access with streaming, health
    checks, and explicit transaction management. Intended for adapters using asyncpg,
    SQLAlchemy cores, or serverless PostgreSQL endpoints.
  - `KeyValueStorePort` — Redis-compatible cache, coordination, and pub/sub semantics,
    including sorted-set helpers and distributed locking.
- **Typical adapters**: `pheno.database.adapters.postgres.PostgreSQLAdapter`,
  Redis-backed task stores, Supabase or Neon database clients. Adapters map their query
  primitives to the `Query` and `ExecutionResult` dataclasses.

## Messaging (NATS)

- **Module**: `pheno.ports.messaging`
- **Key contract**: `MessageBusPort` orchestrates publish/subscribe operations,
  request/reply flows, and connection lifecycle. Messages are exchanged through the
  `OutboundMessage` and `InboundMessage` dataclasses with optional headers and delivery
  guarantees.
- **Typical adapters**: wrappers around `nats-py` (core connection) and JetStream
  consumers (durable or queue subscriptions).

## ML Inference (Ollama, MLX, vLLM)

- **Module**: `pheno.ports.inference`
- **Key contract**: `TextInferencePort` standardises text generation, streaming,
  embedding creation, and runtime health checks. It relies on `GenerationRequest`,
  `GenerationResponse`, `GenerationChunk`, and `EmbeddingResponse` to abstract the HTTP
  payloads used by local runtimes.
- **Typical adapters**: clients wrapping the Ollama HTTP API, `mlx_lm serve`, or vLLM's
  OpenAI-compatible endpoint. Adapters can also surface model catalog metadata via
  `ModelInfo`.

## Tunneling (cloudflared)

- **Module**: `pheno.ports.tunneling`
- **Key contract**: `TunnelManagerPort` covers lifecycle management for cloudflared
  tunnels, DNS synchronization, orphan cleanup, and credential rotation using the
  `TunnelConfig`, `TunnelStatus`, and `TunnelEndpoint` data structures.
- **Typical adapters**: orchestrators that shell out to the cloudflared CLI, leverage
  the Cloudflare API, or coordinate tunnels running inside container environments.

## Authentication (OAuth, API keys)

- **Module**: `pheno.ports.authentication`
- **Key contracts**:
  - `OAuthProviderPort` — wraps authorization URL creation, code exchange, refresh,
    introspection, and userinfo retrieval for OAuth2/OIDC providers. Works alongside
    the existing classes in `pheno.ports.auth.providers`.
  - `APIKeyValidatorPort` — validates, issues, revokes, and rotates API keys while
    returning an `APIKeyIdentity`.
  - `AuthSessionStorePort` — persistence contract for caching authentication outcomes
    such as OAuth tokens or MFA session state.
- **Typical adapters**: Auth0 or Cognito clients, internal OAuth gateways, API key
  vaults, and encrypted session stores.

## Monitoring / Observability

- **Module**: `pheno.ports.observability`
- **Key contracts**: structured logging (`Logger`/`LoggerFactory`), distributed tracing
  (`Tracer`, `Span`, `SpanContext`), metrics instrumentation (`Meter`, `Counter`,
  `Histogram`, `Gauge`, `MeterProvider`), and health probe execution (`HealthCheck`).
- **Typical adapters**: OpenTelemetry SDKs, Datadog or Prometheus exporters, and custom
  health-check registries used by the control plane.

Each port stays under 200 lines and can be extended independently as new integrations
are introduced. Adapters should return domain-level dataclasses wherever possible to
keep downstream callers insulated from library-specific responses.
