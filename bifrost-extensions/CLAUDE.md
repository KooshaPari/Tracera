# CLAUDE.md — bifrost-extensions

Extended functionality and integrations for the Bifrost service mesh. Rust + Go + WASM.

## Stack

| Layer | Technology |
|-------|------------|
| Core extensions | Rust (edition 2021) |
| Control plane | Go 1.21+ |
| Filters | WASM |
| Deployment | Kubernetes-native (CRDs) |
| Observability | OpenTelemetry, Prometheus, Grafana, Jaeger |
| License | Internal (Phenotype platform) |

## Key Directories

```
routing/            # Advanced traffic routing
circuit-breaker/    # Circuit breaker implementation
rate-limiter/       # Rate limiting
auth/               # JWT, mTLS authentication
authz/              # RBAC authorization
observability/      # Tracing, metrics
load-balancer/      # Advanced LB algorithms
retry/              # Retry logic
wasm/               # WASM filter support
```

## Quality Gates

```bash
# Full quality check
cargo fmt && cargo clippy --workspace -- -D warnings && cargo test --workspace

# Build everything
cargo build --workspace --release

# Integration tests (requires k8s)
./scripts/integration-tests.sh
```

## Performance Requirements

- P99 latency overhead: <5ms
- Memory overhead: <10MB per extension
- CPU overhead: <5% at p99

## Test-First Mandate

- **New extensions**: tests MUST exist before implementation
- **Bug fixes**: failing test MUST be written before the fix
- **Refactors**: existing tests must pass before AND after

## Extension Interface

Extensions must implement:
- `Extension` trait (Rust) or `Extension` interface (Go)
- Configuration validation
- Health check endpoint
- Graceful shutdown handler

## CRD Configuration

```yaml
apiVersion: bifrost.phenotype.dev/v1
kind: CircuitBreaker
metadata:
  name: my-circuit-breaker
spec:
  failureThreshold: 5
  timeout: 30s
```

## Governance

- Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- Specs: `AgilePlus/kitty-specs/<feature-id>/`
- Worklog: `AgilePlus/.work-audit/worklog.md`
- Key docs: `PLAN.md`, `ADR.md`, `CHARTER.md`, `PRD.md`, `SPEC.md`, `docs/`

## UTF-8 Encoding

All markdown files must use UTF-8. Validate with:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus validate-encoding --all --fix
```

## Note

This is a Tracera monorepo subdirectory. All work is committed via the Tracera worktree (`/Users/kooshapari/CodeProjects/Phenotype/repos/`), not a standalone repo.
