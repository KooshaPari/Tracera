# Schemas

Type definitions, API specs, and data models.

## Purpose
Provide canonical type definitions across languages.

## Mutability
Locked - Breaking changes require major version bump and migration guide.

## Structure
```
schemas/
├── types/              # Cross-language types
│   ├── rust/
│   │   └── src/lib.rs
│   ├── python/
│   │   └── pheno_types/
│   └── typescript/
│       └── packages/types/
├── api/                # API specs
│   ├── openapi/        # REST APIs
│   │   └── v1/
│   │       └── openapi.yaml
│   └── protobuf/        # gRPC APIs
│       └── v1/
│           └── api.proto
└── data/               # JSON Schema
    ├── config.json
    └── event.json
```

## Type Generation
| Source | Targets |
|--------|---------|
| Rust (canonical) | Python (PyO3), TypeScript (wasm-bindgen), Go |
| OpenAPI | Client SDKs |
| Protobuf | Multi-language stubs |

## Versioning
- Types: Semantic versioning (MAJOR.MINOR.PATCH)
- API Specs: Versioned paths (`/v1/`, `/v2/`)
- Schema changes: Backward compatible preferred

## Usage
```rust
// Use canonical types
use phenotype_types::{Config, Event};

// Derive for config
#[derive(Debug, Serialize, Deserialize)]
struct MyConfig {
    #[serde(flatten)]
    base: Config,
}
```

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Import types for type safety |
| Write | Generate types from spec |
| Enforce | Validate against schema |

## Related
- [libs/](../libs/) - Libraries implementing types
- [governance/](../governance/) - ADR for type decisions
