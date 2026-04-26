# HexaKit

**Comprehensive Hexagonal Architecture Toolkit for Phenotype**

HexaKit is a production-grade Rust workspace providing a complete implementation of hexagonal (ports-and-adapters) architecture patterns. It offers modular, reusable crates for building domain-driven applications with clear separation between business logic and infrastructure concerns.

## Overview

HexaKit packages the hexagon pattern reference into consumable libraries suitable for projects of any size. Each crate is independent, composable, and implements one specific port/adapter boundary. HexaKit eliminates boilerplate, reduces architectural drift, and enforces consistent port design across the Phenotype organization.

The toolkit is built on three principles: **modularity** (each crate stands alone), **clarity** (explicit contracts at every boundary), and **testability** (in-memory doubles built into every port).

## Technology Stack

- **Language**: Rust (edition 2021)
- **Build System**: cargo (workspace with 25+ crates)
- **Key Dependencies**: tokio (async), serde (serialization), thiserror (errors), sqlx (database)
- **Testing**: Criterion (benchmarks), proptest (property testing), in-memory mocks
- **CI**: GitHub Actions (Clippy, rustfmt, cargo test)

## Key Features

- **Port Abstractions**: Traits for storage, async execution, observability, configuration, secrets, messaging
- **Adapter Library**: Implementations for PostgreSQL, SQLite, Redis, HTTP clients, gRPC servers, S3, Kafka
- **Testing Toolkit**: In-memory stores, mock clients, fixture factories, test containers
- **Error Handling**: Unified error types with context, tracing, and recovery guidance
- **Configuration Management**: Unified config loader supporting environment, files, and feature flags
- **Observability**: Integrated tracing, metrics collection, and structured logging
- **Example Projects**: Full reference applications demonstrating port usage patterns

## Quick Start

```bash
# Clone the monorepo
git clone https://github.com/KooshaPari/phenotype-infrakit.git
cd phenotype-infrakit

# Review the HexaKit workspace structure
cat Cargo.toml | grep -A 30 "members ="

# Run all tests
cargo test --workspace

# Run with specific feature
cargo test --package hexakit-core --features postgres

# Build documentation
cargo doc --workspace --no-deps --open

# Review project governance
cat CLAUDE.md
```

## Project Structure

```
Cargo.toml                          # Workspace manifest
crates/
├── hexakit-core/                  # Core traits and abstractions
│   ├── src/
│   │   ├── port/                  # Port definitions
│   │   ├── adapter/               # Adapter traits
│   │   └── error.rs               # Unified error types
│   └── tests/                      # Integration tests
├── hexakit-storage/               # Storage port implementations
│   ├── postgres/                  # PostgreSQL adapter
│   ├── sqlite/                    # SQLite adapter
│   └── in-memory/                 # Test double
├── hexakit-async/                 # Async execution port
├── hexakit-observability/         # Tracing, metrics, logging
├── hexakit-config/                # Configuration management
├── hexakit-secrets/               # Secrets management
├── hexakit-messaging/             # Event/message handling
└── ...                             # 15+ more crates

docs/
├── ARCHITECTURE.md                # Design overview
├── GETTING_STARTED.md             # Setup and first adapter
├── PORT_CATALOG.md                # Index of all ports
└── examples/                      # Reference applications
```

## Related Phenotype Projects

- **hexagon** — Architectural reference library and pattern documentation
- **phenotype-infrakit** — Monorepo hosting HexaKit and other infrastructure
- **phenotype-shared** — Generic shared crates extracted from HexaKit
- **bifrost-extensions** — Consumer of HexaKit storage and observability ports

## Quality & Testing

All crates implement comprehensive test coverage with:
- Unit tests for individual components (in-crate `#[cfg(test)]`)
- Integration tests exercising port-adapter boundaries
- Property-based tests for stateful operations
- Example applications demonstrating realistic usage

Run full quality checks:
```bash
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
cargo doc --workspace --no-deps
```

## Governance

HexaKit is maintained as a shared resource across Phenotype. All changes must:
- Preserve backward compatibility (semver policy)
- Include comprehensive tests (test-first requirement)
- Document port contracts and adapter assumptions
- Reference related FR (Functional Requirement) in test comments

See `CLAUDE.md` for complete governance policies including AgilePlus integration, scripting language hierarchy, and CI/CD requirements.

---

**Version**: v0.2.0  
**Last Updated**: 2026-04-25
