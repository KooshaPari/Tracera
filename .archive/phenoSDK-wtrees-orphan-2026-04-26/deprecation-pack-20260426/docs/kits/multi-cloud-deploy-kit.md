# Multi-Cloud Deploy Kit

## At a Glance
- **Purpose:** Define cloud-agnostic deployment manifests (YAML) and execute them across providers using deploy-kit internals.
- **Best For:** Teams operating the same workload across Vercel, Supabase, Neon, Fly.io, AWS, or custom infrastructures.
- **Key Building Blocks:** YAML schema (`deployment.yaml`), `Deployer` facade, provider adapters.

## Core Capabilities
- Parse declarative deployment definitions describing services, runtimes, and secrets.
- Map definitions to platform-specific API calls via deploy-kit clients.
- Support staged rollouts (`deploy_all`, `deploy_service`, `teardown`).
- Provide hooks for pre/post deployment actions (migrations, cache warming, health verification).

## Getting Started

### Installation
```
pip install multi-cloud-deploy-kit
```

### Minimal Example
```yaml
# deployment.yaml
services:
  api:
    platform: vercel
    runtime: python3.11
    entry: api/main.py
  database:
    platform: supabase
    project: my-project
```

```python
from deploy_kit import Deployer

deployer = Deployer.from_yaml("deployment.yaml")
await deployer.deploy_all()
```

## How It Works
- YAML definitions are converted into `ServiceSpec` objects.
- Each spec selects a provider adapter (`deploy_kit.platforms.vercel`, `supabase`, `aws`, etc.).
- `Deployer` orchestrates create/update flows, invoking hooks for validation and post-deploy tasks.
- Secrets and environment variables can be referenced via config-kit or environment overlays.

## Usage Recipes
- Maintain separate YAML files per environment (e.g., `deployment.staging.yaml`, `deployment.prod.yaml`).
- Run `deploy_service("api")` for targeted redeployments.
- Chain deployments within workflow-kit to include migrations and smoke tests.
- Publish deployment events through event-kit for auditing.

## Interoperability
- Reuses deploy-kit clients; configure authentication with config-kit.
- Observability-kit collects deployment metrics when hooks are instrumented.
- Combine with orchestrator-kit to coordinate multi-region rollouts.

## Operations & Observability
- Store generated manifests in source control for traceability.
- Enable dry-run mode to preview changes without executing them.
- Emit structured logs per service deployment, including timestamps and statuses.

## Testing & QA
- Validate YAML schemas using `Deployer.validate_yaml(path)` in CI.
- Mock provider clients to assert that expected API calls are made.
- Use integration tests against staging projects before production rollouts.

## Troubleshooting
- **Authentication errors:** confirm provider credentials are available to deploy-kit clients.
- **Partial failures:** use `deploy_service` to retry individual services or run `teardown` before reapplying.
- **Schema mismatches:** keep YAML in sync with the latest schema (see tests for fixtures).

## Primary API Surface
- `Deployer.from_yaml(path)` / `Deployer.from_dict(data)`
- `await Deployer.deploy_all()`
- `await Deployer.deploy_service(name)`
- `await Deployer.teardown()`
- `Deployer.validate_yaml(path)`

## Additional Resources
- Examples: `multi-cloud-deploy-kit/README.md`
- Related kits: [deploy-kit](deploy-kit.md), [operations guide](../guides/operations.md)
