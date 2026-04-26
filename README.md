# PhenoKits

**Multi-category artifact platform for the Phenotype software organization.**

## Overview

PhenoKits organizes artifacts into 12 distinct categories, each with clear mutability rules and agent interaction patterns.

## Categories

| # | Category | Purpose | Mutability |
|---|----------|---------|------------|
| 1 | [`templates/`](templates/) | Scaffolding for new projects | Editable |
| 2 | [`configs/`](configs/) | Parameterized configs | Parameters only |
| 3 | [`libs/`](libs/) | Multi-language libraries | Import/extend |
| 4 | [`secrets/`](secrets/) | Secret management patterns | Locked |
| 5 | [`governance/`](governance/) | ADRs, RFCs, standards | Varies |
| 6 | [`security/`](security/) | Scanning, policies, hardening | Locked |
| 7 | [`observability/`](observability/) | Logging, metrics, tracing | Configurable |
| 8 | [`docs/`](docs/) | API docs, runbooks, guides | Editable |
| 9 | [`scripts/`](scripts/) | Build, release, quality scripts | Executable |
| 10 | [`schemas/`](schemas/) | Type definitions, API specs | Locked |
| 11 | [`policies/`](policies/) | OPA, GitHub, compliance | Enforced |
| 12 | [`credentials/`](credentials/) | Auth configs, patterns | Locked |

## Quick Reference

### Agent Interaction Matrix

| Category | Agent Reads | Agent Writes | Agent Enforces |
|----------|-------------|--------------|----------------|
| Templates | Yes | Yes (instantiation) | No |
| Configs | Yes | Parameters only | Yes (validation) |
| Libs | Yes | No | No |
| Secrets | Yes | No | No |
| Governance | Yes | Yes (ADRs) | No |
| Security | Yes | Yes | Yes (scanning) |
| Observability | Yes | Yes | Yes (monitoring) |
| Docs | Yes | Yes | No |
| Scripts | Yes | Yes | No |
| Schemas | Yes | Yes (code gen) | Yes (type checking) |
| Policies | Yes | Yes | Yes (OPA, gates) |
| Credentials | Yes | No | Yes (rotation) |

## Directory Structure

```
PhenoKits/
├── templates/           # 1. Scaffolding
│   ├── hexagonal/      # Hexagonal architecture templates
│   ├── clean-rust/     # Clean architecture Rust template
│   └── phenotype-api/  # Phenotype API template
├── configs/            # 2. Parameterized configs
│   ├── tooling/        # Linters, formatters
│   ├── cicd/           # CI/CD pipelines
│   ├── infra/          # Docker, Kubernetes
│   └── observability/  # Prometheus, Grafana
├── libs/               # 3. Libraries
│   ├── rust/          # Canonical Rust cores
│   ├── python/        # Python bindings
│   ├── typescript/    # TypeScript bindings
│   └── go/            # Go bindings
├── secrets/            # 4. Secret management
├── governance/         # 5. ADRs, RFCs, standards
├── security/           # 6. Security configs
├── observability/      # 7. Logging, metrics
├── docs/               # 8. Documentation
├── scripts/            # 9. Automation scripts
├── schemas/            # 10. Type definitions
├── policies/           # 11. Enforcement policies
└── credentials/        # 12. Auth configs
```

## Quick Start

### For Agents

```bash
# 1. Clone PhenoKits
git clone https://github.com/KooshaPari/PhenoKits.git
cd PhenoKits

# 2. Read agent patterns
cat docs/AGENT_PATTERNS.md

# 3. Apply a config
python3 scripts/utility/parameterize.py \
    configs/params.example.json \
    configs/cicd/github-actions/ci.yml

# 4. Scaffold a project
pheno new --template hexagonal-rust --name my-service --org MyOrg
```

### For Developers

```bash
# 1. Apply org configs
cp -r configs/tooling/pre-commit/* .git/hooks/

# 2. Set up CI
cp configs/cicd/github-actions/* .github/workflows/

# 3. Configure observability
cp configs/observability/prometheus.yml ./
```

## Related

- [RESTRUCTURING_PLAN.md](docs/RESTRUCTURING_PLAN.md) - Full restructuring plan
- [RESTRUCTURING_ADR.md](docs/RESTRUCTURING_ADR.md) - Decision record
- [AGENT_PATTERNS.md](docs/AGENT_PATTERNS.md) - Agent consumption patterns
- [HexaKit/](HexaKit/) - Template CLI and registry
- [PhenoKit](https://github.com/KooshaPari/PhenoKit) - Core SDK
- [PhenoSpecs](https://github.com/KooshaPari/PhenoSpecs) - Specifications
