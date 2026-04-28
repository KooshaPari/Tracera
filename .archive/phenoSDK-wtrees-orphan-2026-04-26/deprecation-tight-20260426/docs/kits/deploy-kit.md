# Deploy Kit

## At a Glance
- **Purpose:** Automate vendoring of Pheno-SDK packages and generate deployment artifacts for common platforms.
- **Best For:** Teams deploying to Vercel, Docker, serverless functions, or orchestrators who want consistent packaging.
- **Key Building Blocks:** `PhenoVendor`, `DeployConfig`, platform clients (Vercel, Fly.io, AWS, GCP, Azure), NVMS runtime descriptors.

## Core Capabilities
- Detect which Pheno-SDK kits your project imports and vendor them into a `pheno_vendor/` directory.
- Produce platform-specific configurations (Vercel config, Dockerfiles, Railway manifests, serverless handlers).
- Validate vendored packages by executing import checks and dependency resolution.
- Provide CLI (`pheno-vendor`) and Python APIs for scripting.
- Manage local processes and cloud deployments with a unified configuration schema (NVMS).

## Getting Started

### Installation
```
pip install deploy-kit
# Extras for specific platforms
dependency examples: pip install "deploy-kit[vercel]" "deploy-kit[docker]"
```

### Minimal Example
```bash
pheno-vendor setup
```

```python
from deploy_kit import PhenoVendor

vendor = PhenoVendor(project_root=".")
vendor.vendor_all(auto_detect=True, validate=True)
```

## How It Works
- `PhenoVendor` scans your project for Pheno-SDK imports, downloads the corresponding packages, and copies them into `pheno_vendor/`.
- Vendoring metadata is stored in `vendor-lock.json` to keep builds reproducible.
- `DeployConfig` reads NVMS configuration (YAML or Python dictionaries) and can emit platform-specific manifests via `to_vercel_config()`, `to_dockerfile()`, etc.
- CLI commands wrap these APIs and add convenience prompts, validation, and logging.
- Hooks integrate with deploy pipelines by generating build scripts for GitHub Actions, Vercel, or Docker.

## Usage Recipes
- **Vendoring on CI:** run `pheno-vendor setup --validate` before packaging artifacts.
- **Generate Vercel config:** `pheno-vendor generate-hooks --platform vercel` to emit `vercel.json` and edge function handlers.
- **Multi-cloud deploy YAML:** author `deployment.yaml` describing services and run `DeployConfig.save_configs()` to produce environment-specific files.
- **Custom platform integration:** extend `deploy_kit.platforms.BasePlatform` to add new deployment targets and register them.

## Interoperability
- Works with config-kit to inject deployment credentials and secrets.
- Combine with workflow-kit to orchestrate staged rollouts and validation gates.
- Use observability-kit to report deployment metrics (duration, success/failure).
- Multi-cloud deploy kit builds on the same configuration primitives—see [multi-cloud deploy manual](multi-cloud-deploy-kit.md).

## Operations & Observability
- Vendoring emits structured logs and validates imports; pipe output into observability-kit loggers for aggregation.
- Collect metrics around vendoring duration and deployment successes using the built-in hooks.
- Store generated manifests in storage-kit buckets for audit trails.

## Testing & QA
- Use dry-run mode (`pheno-vendor setup --dry-run`) in tests to confirm configuration without writing files.
- Unit-test custom platform renderers by asserting generated config matches snapshots.
- Validate vendored packages by importing them inside a controlled virtual environment (see tests for fixtures).

## Troubleshooting
- **Package not found:** set `PHENO_SDK_ROOT` or provide `--include` flags to locate source packages.
- **Import validation failures:** ensure dependencies are installed in the environment used for validation.
- **Platform config mismatch:** inspect generated files; override values by passing explicit options to `DeployConfig`.

## Primary API Surface
- `PhenoVendor(project_root, output_dir="pheno_vendor")`
- `PhenoVendor.vendor_all(auto_detect=True, validate=True)`
- `PhenoVendor.clean()` to remove vendored packages
- `DeployConfig(project_root)`
- `DeployConfig.save_configs(platforms=None)`
- `DeployConfig.to_vercel_config()` / `.to_dockerfile()` / `.to_lambda_bundle()`
- CLI entrypoint: `pheno-vendor`

## Additional Resources
- Guides: `deploy-kit/VENDORING_GUIDE.md`, `deploy-kit/MIGRATION_GUIDE.md`
- Examples: `deploy-kit/examples/`
- Tests: `deploy-kit/tests/`
- Related concepts: [Operations](../guides/operations.md)
