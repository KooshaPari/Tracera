# ADR-004: Artifact Categorization

**Status**: Proposed

**Date**: 2026-04-05

## Context

We need to categorize all existing artifacts in PhenoKits into the 12-category taxonomy to enable proper migration.

## Decision

### Artifact Classification Matrix

| Artifact | Category | Subcategory | Rationale |
|----------|----------|-------------|-----------|
| `HexaKit/` | TEMPLATES | scaffolding | Main template CLI & registry |
| `template-commons/` | TEMPLATES | utilities | Template utilities & shared patterns |
| `template-program-ops/` | TEMPLATES | ops | Ops scaffolding templates |
| `hexagon/` | TEMPLATES | domain | Domain-specific hexagon patterns |

### From template-commons (to be migrated)

| Artifact | Category | Subcategory | Rationale |
|----------|----------|-------------|-----------|
| `clean-rust/` | TEMPLATES | scaffolding | Clean architecture Rust template |
| `hexagonal-rs/` | TEMPLATES | scaffolding | Hexagonal architecture Rust template |
| `hexagonal-rust/` | TEMPLATES | scaffolding | Hexagonal Rust template (variant) |
| `hexagonal-python/` | TEMPLATES | scaffolding | Hexagonal Python template |
| `hexagonal-go/` | TEMPLATES | scaffolding | Hexagonal Go template |
| `hexagonal-typescript/` | TEMPLATES | scaffolding | Hexagonal TS template |
| `hexagonal-csharp/` | TEMPLATES | scaffolding | Hexagonal C# template |
| `hexagonal-cs/` | TEMPLATES | scaffolding | Hexagonal CS template (alias) |
| `hexagonal-zig/` | TEMPLATES | scaffolding | Hexagonal Zig template |
| `microservice-scaffold/` | TEMPLATES | scaffolding | Microservice template |
| `phenotype-api/` | TEMPLATES | scaffolding | API template |
| `phenotype-config/` | CONFIGS | app | Configuration template |
| `config-templates/` | CONFIGS | app | Config templates |
| `contracts/` | SCHEMAS | types | Type/contract definitions |
| `phenotype-logging/` | LIBS | shared | Logging library |
| `phenotype-testing/` | LIBS | shared | Testing utilities |
| `phenotype-toolkit/` | LIBS | shared | Shared toolkit |
| `phenotype-py-kit/` | LIBS | python | Python kit |
| `phenotype-id/` | LIBS | shared | ID generation lib |
| `phenotype-go-kit/` | LIBS | go | Go kit |
| `phenotype-go-cli/` | LIBS | go | Go CLI lib |
| `phenotype-go-config/` | LIBS | go | Go config lib |
| `phenotype-go-middleware/` | LIBS | go | Go middleware lib |
| `phenotype-go-auth/` | LIBS | go | Go auth lib |
| `plugin-typescript/` | LIBS | typescript | TS plugin lib |
| `workflows/` | CONFIGS | cicd | CI/CD workflows |
| `.github/` | CONFIGS | cicd | GitHub Actions configs |
| `.semgrep/` | CONFIGS | tooling | Semgrep rules |
| `scripts/` | SCRIPTS | utility | Utility scripts |
| `kitty-specs/` | GOVERNANCE | standards | Spec templates |
| `docs/` | DOCUMENTATION | guides | Documentation |
| `ADR*.md` | GOVERNANCE | adr | Architecture decisions |
| `codecov.yml` | CONFIGS | tooling | Code coverage config |
| `mypy.ini` | CONFIGS | tooling | Python type checking |
| `Dockerfile` | CONFIGS | infra | Container config |
| `justfile` | SCRIPTS | build | Build automation |

### Category Mapping Summary

```
TEMPLATES (scaffolding):
├── HexaKit/                    # Main template CLI
├── template-commons/
│   ├── clean-rust/
│   ├── hexagonal-*/            # Hexagonal templates by language
│   └── microservice-scaffold/
└── template-program-ops/

CONFIGS:
├── configs/                   # NEW: Parameterized configs
├── template-commons/
│   ├── config-templates/
│   ├── phenotype-config/
│   ├── workflows/
│   ├── .github/
│   ├── .semgrep/
│   ├── codecov.yml
│   ├── mypy.ini
│   └── Dockerfile

LIBS:
├── libs/                       # NEW: Multi-language libs
├── template-commons/
│   ├── phenotype-logging/
│   ├── phenotype-testing/
│   ├── phenotype-toolkit/
│   ├── phenotype-py-kit/
│   ├── phenotype-id/
│   ├── phenotype-go-*/
│   └── plugin-typescript/

SCHEMAS:
├── schemas/                    # NEW: Type definitions
└── template-commons/
    └── contracts/

GOVERNANCE:
├── governance/                 # NEW: ADRs, standards
└── template-commons/
    ├── ADR*.md
    └── kitty-specs/

DOCUMENTATION:
├── docs/                       # NEW: User docs
└── template-commons/
    └── docs/

SCRIPTS:
├── scripts/                    # NEW: Automation
└── template-commons/
    ├── scripts/
    └── justfile
```

## Consequences

### Positive
- Clear separation of artifact types
- Enables proper agent consumption patterns
- Supports org-locked vs editable distinction

### Negative
- Migration effort required
- Cross-references need updating
- CI/CD may need adjustment

## Migration Plan

1. Move artifacts to appropriate directories
2. Update Cargo.toml workspace
3. Update import paths
4. Update CI/CD references
5. Update documentation

## References

- [RESTRUCTURING_PLAN.md](./RESTRUCTURING_PLAN.md)
- [ADR-000: Architecture Decision Records](../governance/adr/ADR-000-template.md)
