# PhenoKit

**Unified Toolkit Aggregator & Component Library Index**

## Overview

PhenoKit is the canonical toolkit aggregator and meta-index for all Phenotype component libraries. It provides unified installation, discovery, and cross-project dependency resolution for 30+ specialized kits (ResilienceKit, ValidationKit, TestingKit, HexaKit, etc.), with package management integration and version coordination across the entire ecosystem.

**Core Mission**: Centralize toolkit discovery, version management, and cross-kit dependency resolution; enable users to discover and compose Phenotype libraries without fragmentation.

## Technology Stack

- **Package Managers**: npm (JavaScript/TypeScript), cargo (Rust), pip (Python), go get (Go)
- **Monorepo Orchestration**: Cargo workspaces, pnpm/npm workspaces, Zig/Go module management
- **Dependency Resolution**: cargo-audit, npm audit, pip check for vulnerability scanning
- **Meta-Index**: TOML registry (kit name, version, language, description, repository), markdown docindex
- **CLI Tool**: Rust-based `phenokit` CLI with subcommands for discovery, installation, version management
- **Documentation**: VitePress docsite aggregating all kit READMEs, quick-starts, and API references

## Key Features

- **Unified Toolkit Discovery** — Search and browse 30+ specialized kits by language, category, and maturity
- **Cross-Language Package Installation** — Single `phenokit install <kit-name>` command for Rust, JavaScript, Python, Go
- **Version Coordination** — Automatic dependency resolution and version pinning across multi-language projects
- **Toolkit Composition** — Define composite toolkits (e.g., "web-stack" = HexaKit + Httpora + rich-cli-kit)
- **Dependency Graph Visualization** — Mermaid diagrams showing cross-kit dependencies and relationships
- **Changelog Aggregation** — Unified changelog across all kits with filtering by version, category, and breaking changes
- **Registry Search** — Keyword-based search (e.g., "retry", "validation", "testing") across all kits
- **CLI Integration** — Shell completions (bash, zsh, fish) for discovery and installation subcommands

## Quick Start

```bash
# Install phenokit CLI
cargo install phenokit
# or: npm install -g @phenotype/phenokit
# or: pip install phenokit

# Discover available toolkits
phenokit search testing
phenokit list --category "observability"

# Install a specific kit
phenokit install ResilienceKit --language rust
phenokit install ValidationKit --language python

# Show kit details and dependencies
phenokit info TestingKit
phenokit deps HexaKit --graph mermaid

# Create a composite toolkit project
phenokit new myproject --with HexaKit,ValidationKit,Httpora
cd myproject && phenokit build

# Check for updates and vulnerabilities
phenokit audit
phenokit upgrade --all
```

## Project Structure

```
cli/
  ├─ src/
  │  ├─ registry.rs       # Toolkit registry loading and searching
  │  ├─ install.rs        # Multi-language package installation logic
  │  ├─ search.rs         # Full-text search across toolkit metadata
  │  ├─ deps.rs           # Dependency resolution and graph generation
  │  └─ audit.rs          # Vulnerability scanning and SemVer compatibility
  └─ tests/               # Integration tests for CLI commands

registry/
  ├─ kits.toml            # Master registry: name, version, language, description, repo
  └─ categories.json      # Categorization and tagging (testing, validation, observability, etc.)

docs/
  ├─ kits/                # Individual kit documentation aggregated from source repos
  ├─ guide.md             # Getting started and composition guide
  └─ api.md               # CLI API reference and shell completion

index/
  ├─ dependency-graph.md  # Mermaid visualization of all cross-kit dependencies
  └─ changelog.md         # Aggregated changelog across all kits
```

## Core Toolkits Indexed

| Kit | Language | Purpose | Words |
|-----|----------|---------|-------|
| **HexaKit** | Rust | Hexagonal architecture patterns | 310 |
| **ResilienceKit** | Rust/Go/Python | Retry, circuit breakers, bulkheads | 317 |
| **ValidationKit** | Rust/Python/Go | Schema-driven validation | 380 |
| **TestingKit** | Multi-lang | Unified testing framework | 420 |
| **ObservabilityKit** | Multi-lang | OpenTelemetry SDKs | 390 |
| **PlatformKit** | Multi-lang | Cross-platform abstractions | 542 |
| **AuthKit** | Multi-lang | Unified authentication | 280 |
| **McpKit** | Multi-lang | Model Context Protocol SDKs | 252 |

**Plus 22+ additional kits** covering data, config, HTTP, persistence, plugin systems, and more.

## Status

**Active Development** — Registry complete with 30+ kits indexed; CLI in public beta.

- ✓ Registry metadata and search
- ✓ Rust kit installation
- ✓ Python kit installation
- ✓ Dependency graph visualization
- WIP: JavaScript/TypeScript kit installer
- WIP: Go module integration
- WIP: Composite toolkit templates

## Related Phenotype Projects

- **All Phenotype Kits** — 30+ specialized toolkit projects (see registry/kits.toml)
- **phenotype-shared** — Shared Rust infrastructure crates (dependency base)
- **PlatformKit** — Cross-platform abstraction layer (foundational kit)

## Governance & Architecture

- **Documentation**: See `CLAUDE.md` for development setup and registry management
- **Registry Source**: `registry/kits.toml` — Authoritative toolkit inventory
- **Installation Guides**: `docs/kits/*/README.md` — Per-kit quick-starts
- **API Reference**: `docs/api.md` — CLI command reference and shell completions

---

**Maintained by**: Phenotype Toolkit Committee  
**Last Updated**: 2026-04-25
