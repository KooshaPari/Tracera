# Internal Architecture

## Service Topology

1. Go backend services (domain and API execution)
2. Frontend apps for UI and documentation surfaces
3. Integration services for observability, data, and workflow automation

## Quality Contract

- Architecture boundaries and dependency constraints must hold.
- Quality gates block merges on contract violations.
- Runtime operations require observability-first signals.
