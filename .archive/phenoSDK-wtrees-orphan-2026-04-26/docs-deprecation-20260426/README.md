# phenoSDK

Official Software Development Kit for building applications on the Phenotype platform. Provides idiomatic, multi-language SDKs that simplify integration with Phenotype services, APIs, and runtime environments.

## Overview

**phenoSDK** makes it as simple as a few lines of code to integrate with the entire Phenotype ecosystem. Native SDKs for TypeScript, Python, Rust, Go, and Java handle authentication, error management, pagination, retries, and resource CRUD operations—freeing developers to focus on business logic instead of platform integration details.

**Core Mission**: Provide the most developer-friendly SDK experience on the Phenotype platform, enabling rapid integration across all major languages with consistent, idiomatic patterns.

## Technology Stack

- **Multi-Language Support**: TypeScript/JavaScript, Python, Rust, Go, Java
- **Authentication**: API key, OAuth 2.0, token refresh, secure token storage
- **HTTP Client**: Async HTTP handling, connection pooling, timeouts, circuit breaking
- **Error Handling**: Typed errors, structured error details, retry suggestions
- **Features**: Type-safe resources, pagination, filtering, sorting, batch operations
- **Developer Experience**: Auto-generated docs, rich IDE autocomplete, logging integration

## Key Features

- **Language SDKs**: Idiomatic implementations for TypeScript, Python, Rust, Go, Java
- **Authentication**: API key, OAuth 2.0, token management, automatic refresh
- **Type Safety**: Generated type definitions from OpenAPI specs, runtime validation
- **Error Management**: Rich error types, structured details, automatic retry logic
- **Resource Operations**: Create, read, update, delete with filtering and pagination
- **Batch Operations**: Bulk create, update, delete with atomic guarantees
- **Streaming Support**: Server-sent events, WebSocket connections, real-time updates
- **Observability**: Request/response logging, tracing integration, metrics export

## Quick Start

```bash
# Clone and explore
git clone <repo-url>
cd phenoSDK

# Review governance and architecture
cat CLAUDE.md          # Project governance
cat PRD.md             # Product requirements
cat AGENTS.md          # Agent operating contract

# JavaScript/TypeScript SDK
npm install @phenotype/sdk
# Usage: import { PhenoClient } from '@phenotype/sdk'

# Python SDK
pip install phenotype-sdk
# Usage: from phenotype import PhenoClient

# Rust SDK
cargo add phenotype-sdk
// Usage: use phenotype_sdk::PhenoClient;

# Run tests for all SDKs
npm test               # JavaScript/TypeScript
pytest tests/          # Python
cargo test --workspace # Rust

# Build documentation
npm run docs           # Generate API docs
```

## Project Structure

```
phenoSDK/
├── ts/                        # TypeScript/JavaScript SDK
│   ├── src/
│   │   ├── client/            # HTTP client wrapper
│   │   ├── auth/              # Auth handlers (API key, OAuth)
│   │   ├── resources/         # Resource type definitions
│   │   └── errors/            # Error types
│   ├── package.json
│   ├── tsconfig.json
│   └── tests/
├── python/                    # Python SDK
│   ├── src/
│   │   ├── phenotype/
│   │   │   ├── client.py      # HTTP client
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── resources.py   # Resource models
│   │   │   └── errors.py      # Exception types
│   │   └── __init__.py
│   ├── pyproject.toml
│   ├── tests/
│   └── Makefile
├── rust/                      # Rust SDK
│   ├── Cargo.toml
│   ├── src/
│   │   ├── client.rs          # HTTP client
│   │   ├── auth.rs            # Auth implementation
│   │   ├── resources.rs       # Resource definitions
│   │   └── error.rs           # Error types
│   └── tests/
├── go/                        # Go SDK
│   ├── go.mod
│   ├── client.go              # HTTP client
│   ├── auth.go                # Auth handlers
│   ├── resources.go           # Resource types
│   └── error.go               # Error types
├── docs/
│   ├── ARCHITECTURE.md        # SDK design patterns
│   ├── AUTHENTICATION.md      # Auth flow documentation
│   ├── API_REFERENCE.md       # Detailed API docs
│   └── EXAMPLES.md            # Usage examples per language
├── openapi/
│   └── phenotype-api.yaml     # API specification
├── FUNCTIONAL_REQUIREMENTS.md
├── ADR.md
├── CLAUDE.md
└── Cargo.toml                 # Rust workspace (if applicable)
```

## Language-Specific Documentation

- **TypeScript**: `ts/README.md` — npm, ESM/CommonJS, TypeScript strict mode
- **Python**: `python/README.md` — pip, async/sync clients, type hints
- **Rust**: `rust/README.md` — Cargo, async Tokio, full type safety
- **Go**: `go/README.md` — go get, stdlib http, clean interfaces
- **Java**: `java/README.md` — Maven/Gradle, sync client, builder patterns

## Related Phenotype Projects

- **AuthKit**: Unified authentication backend (sdks consume AuthKit APIs)
- **PhenoLibs**: Shared data structures and serialization
- **AgilePlus**: Work tracking system (SDK development tracked here)
- **cloud**: Multi-tenant platform (primary SDK consumer)
- **Tracera**: Observability platform (SDK metrics and tracing)