# PhenoSchema

Schema management, evolution, and validation for data contracts across the Phenotype ecosystem.

## Overview

PhenoSchema provides a unified schema system for defining, versioning, and validating data structures across services. It supports multiple formats (JSON Schema, Protobuf, Avro, OpenAPI), schema evolution with backward/forward compatibility checking, and validation against evolving schemas. Schema registry integration enables discovery and enforcement of data contracts across Phenotype applications.

## Technology Stack

- **Core**: Rust with serde for serialization
- **Schema Formats**: JSON Schema (Draft 2020-12), Protocol Buffers, Avro, OpenAPI 3.1
- **Registry**: In-house schema registry (compatible with Confluent Schema Registry API)
- **Validation**: jsonschema crate + custom validators
- **Evolution**: Semantic versioning with compatibility checks (breaking, compatible, minor)
- **Code Generation**: Derive macros for Rust types, code generators for other languages

## Key Features

- **Multi-Format Support**: JSON Schema, Protobuf, Avro in unified abstraction
- **Schema Registry**: Centralized schema storage with versioning and discovery
- **Evolution Checking**: Automatic detection of breaking changes across versions
- **Validation**: JSON Schema validation with detailed error reporting
- **Code Generation**: Derive macros for Rust; CLI generators for TypeScript, Python, Go
- **Documentation**: Auto-generated API docs from schemas
- **Compatibility Matrix**: Forward, backward, and transitive compatibility analysis
- **Governance**: Schema ownership, approval workflows, naming conventions

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/PhenoSchema.git
cd PhenoSchema

# Review workspace conventions
cat CLAUDE.md

# Build schema tools and CLI
cargo build --all-features
cargo build --release

# Run tests (includes schema validation and evolution tests)
cargo test --all

# Validate a schema file
cargo run --bin pheno-schema -- validate schemas/user.json

# Check compatibility between schema versions
cargo run --bin pheno-schema -- check-compat \
  schemas/user-v1.json schemas/user-v2.json

# Generate Rust types from schema
cargo run --bin pheno-schema -- codegen \
  --lang rust --input schemas/user.json --output src/models/
```

## Project Structure

```
PhenoSchema/
  Cargo.toml                     # Workspace manifest
  crates/
    phenotype-schema-core/       # Schema trait, validator trait
    phenotype-schema-json/       # JSON Schema implementation
    phenotype-schema-protobuf/   # Protocol Buffers support
    phenotype-schema-avro/       # Avro format support
    phenotype-schema-registry/   # Central schema registry
    phenotype-schema-codegen/    # Code generation for multiple languages
  schemas/
    user.json                    # Example user entity schema
    event.json                   # Event schema with versioning
  examples/
    validate_data.rs             # Validate JSON against schema
    evolve_schema.rs             # Handle schema evolution
    codegen_types.rs             # Generate types from schema
  tests/
    validation_tests/
    evolution_tests/
    codegen_tests/
```

## Related Phenotype Projects

- **[PhenoEvents](../PhenoEvents/)** — Uses PhenoSchema for event schema management
- **[DataKit](../DataKit/)** — Schema validation in ETL pipelines
- **[phenotype-shared](../phenotype-shared/)** — Event sourcing schema contracts

## Governance & Contributing

- **CLAUDE.md** — Schema design principles, versioning policy
- **Schema Catalog**: [docs/schemas/](docs/schemas/)
- **Evolution Guide**: [docs/evolution/](docs/evolution/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

For validation testing and spec traceability, see [AGENTS.md](AGENTS.md).
