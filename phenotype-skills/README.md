# Phenotype Skills

A dynamic skill registry and execution framework for composable agent capabilities across the Phenotype ecosystem.

## Overview

Phenotype Skills provides a unified system for defining, registering, discovering, and executing reusable capabilities in agent and automation contexts. Skills are composable, versioned units of work that can be combined to build complex agent workflows. The framework abstracts away common concerns like skill lifecycle management, input/output validation, error recovery, and observability integration.

## Technology Stack

- **Core**: Rust (skill definitions, registry, runtime)
- **Bindings**: Rust FFI + Language bridges (Python, TypeScript, Go)
- **Configuration**: TOML-based skill manifests with JSON Schema validation
- **Observability**: Integrated structured logging, span tracing, error reporting
- **Distribution**: Registry + package management (internal NexusOSS-compatible)

## Key Features

- **Skill Composition**: Chain skills declaratively; auto-resolve dependencies
- **Type-Safe Bindings**: FFI and native language bridges with compile-time validation
- **Dynamic Registration**: Load skills from TOML manifests at runtime
- **Input Validation**: JSON Schema-based input/output type checking
- **Error Recovery**: Built-in retry, fallback, and compensation logic
- **Observability**: Structured logs, distributed tracing, performance metrics
- **Versioning**: Semantic versioning with backward compatibility guarantees
- **Hot Reload**: Update skills without restarting agents

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/phenotype-skills.git
cd phenotype-skills

# Review CLAUDE.md for governance and workspace structure
cat CLAUDE.md

# Build the core library and language bindings
cargo build --all-features
cargo build --release

# Run tests
cargo test --all

# Generate skill bindings for Python/TypeScript
cargo run --bin skill-gen -- --lang python --output bindings/py/
cargo run --bin skill-gen -- --lang typescript --output bindings/ts/
```

## Project Structure

```
phenotype-skills/
  Cargo.toml                 # Workspace manifest
  crates/
    phenotype-skills-core/   # Core skill trait, registry, runtime
    phenotype-skills-derive/ # Macros for @[skill] annotations
    phenotype-skills-ffi/    # C FFI bindings for external runtimes
  bindings/
    python/                  # PyO3-based Python package
    typescript/              # WASM + TypeScript bindings
    go/                      # cgo-based Go integration
  examples/
    basic_skill.rs           # Minimal skill definition
    composed_workflow.rs      # Multi-skill composition example
  tests/
    integration_tests/       # End-to-end skill execution scenarios
```

## Related Phenotype Projects

- **[agileplus-agents](../agileplus-agents/)** — Agent task orchestration using skills; primary consumer
- **[PhenoKit](../PhenoKit/)** — Foundational Rust utilities; skill dependencies
- **[phenotype-ops-mcp](../phenotype-ops-mcp/)** — MCP integration exposing skills as model tools

## Governance & Contributing

- **CLAUDE.md** — Project-specific conventions and workspace rules
- **Functional Requirements**: [FUNCTIONAL_REQUIREMENTS.md](FUNCTIONAL_REQUIREMENTS.md)
- **Architecture**: [Architecture Decision Records](docs/adr/)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

For details on testing, spec traceability, and quality gates, see [AGENTS.md](AGENTS.md).

## License

MIT — see [LICENSE](./LICENSE).
