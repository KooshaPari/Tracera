# ValidationKit

**Schema Validation & Data Quality Framework for Phenotype**

ValidationKit is a multi-language validation framework providing schema-based data quality checks, format validation, and business rule enforcement. It enables consistent data validation across services, APIs, and pipelines without embedding validation logic in application code.

## Overview

ValidationKit decouples validation logic from business logic through declarative schemas. Services define validation rules once in TOML/JSON; ValidationKit then enforces these rules across all integration points—APIs, databases, message queues, and file ingestion. The framework automatically generates OpenAPI schemas, error responses, and validation documentation.

## Technology Stack

- **Languages**: Rust (core), Python (rules engine), TypeScript (CLI)
- **Core Concepts**: Schema-driven validation, composable rules, rule inheritance
- **Key Dependencies**: 
  - **serde** (Rust) — data serialization and schema generation
  - **jsonschema** (Rust/Python) — JSON Schema validation
  - **pydantic** (Python) — data validation and coercion
  - **zod** (TypeScript) — runtime schema validation
- **Output**: OpenAPI specs, error reports, audit logs

## Key Features

- **Declarative Schemas**: Define validation rules in TOML/JSON, reuse across projects
- **Schema Composition**: Inherit, extend, and combine schemas for complex domains
- **Async Validation**: Built-in support for remote validation (phone verification, email confirmation)
- **Custom Rules**: Embed Lua or WASM rules for domain-specific validation logic
- **Error Messages**: Automatic, user-friendly error messages with fix suggestions
- **OpenAPI Generation**: Auto-generate OpenAPI specs from validation schemas
- **Audit Trail**: Log all validations with results for compliance and debugging
- **Multi-Language**: Enforce identical validation rules across Rust, Python, Go, TypeScript services
- **Performance**: Zero-copy validation for large datasets; streaming validation for 100GB+ files

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/ValidationKit.git
cd ValidationKit

# Review the schema language and specification
cat docs/SCHEMA_LANGUAGE.md

# Define a validation schema (example)
cat examples/schemas/user-profile.toml

# Run validation on example data
validation-cli validate examples/schemas/user-profile.toml examples/data/user.json

# Generate OpenAPI schema
validation-cli openapi examples/schemas/user-profile.toml > /tmp/user-api.yaml

# Run tests and quality checks
cargo test --workspace
task quality
```

## Project Structure

```
ValidationKit/
├── src/
│   ├── schema/                    # Schema parser and type system
│   ├── validator/                 # Validation engine
│   ├── rules/                     # Built-in rule implementations
│   │   ├── string.rs              # String format rules (email, URL, UUID, etc.)
│   │   ├── numeric.rs             # Numeric constraints (min, max, range)
│   │   ├── collection.rs          # Array/object size and content rules
│   │   └── custom.rs              # Custom rule registration
│   ├── error/                     # Error messages and reporting
│   └── openapi/                   # OpenAPI spec generation
├── examples/
│   ├── schemas/
│   │   ├── user-profile.toml      # User validation schema
│   │   ├── address.toml           # Nested address schema
│   │   └── payment.toml           # PCI-DSS compliant payment schema
│   └── data/                      # Example JSON data files
├── tests/
│   ├── integration/               # End-to-end validation tests
│   ├── performance/               # Benchmarks for large datasets
│   └── fixtures/                  # Test schemas and data
├── cli/
│   └── validation-cli/            # Command-line validation tool
└── docs/
    ├── SCHEMA_LANGUAGE.md         # Schema syntax and semantics
    ├── RULE_CATALOG.md            # All built-in validation rules
    ├── CUSTOM_RULES.md            # How to write custom rules
    └── PERFORMANCE.md             # Optimization and benchmarking
```

## Related Phenotype Projects

- **DataKit** — Uses ValidationKit for ETL data quality checks
- **PhenoPlugins** — Validation rules as extensible plugins
- **bifrost-extensions** — API schema validation via ValidationKit
- **ResilienceKit** — Fallback handling when validation fails

## Quality & Testing

All validation rules are comprehensively tested:
- Unit tests for each rule type (format, range, constraint)
- Property-based tests using proptest for rule composition
- Performance benchmarks for streaming and batch validation
- Integration tests validating end-to-end error reporting

```bash
cargo test --workspace --all-features
task quality                  # clippy, fmt, docs
cargo bench --workspace       # benchmarks
```

## Governance

All work tracked in AgilePlus. Each schema and rule update requires:
- Specification in AgilePlus
- Test coverage (>90% required)
- Documentation for new rule types
- Backward compatibility verification

See `CLAUDE.md` for complete policies.

---

**Version**: v0.1.0  
**Last Updated**: 2026-04-25
