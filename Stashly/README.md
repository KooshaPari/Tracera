# Stashly

**Credential & Secret Management Toolkit for Phenotype**

Stashly provides secure credential storage, rotation, and distribution for Phenotype services. It integrates with HashiCorp Vault and supports environment-based credential injection, reducing hardcoded secrets and simplifying credential lifecycle management.

## Overview

Stashly acts as a credential broker between services and secret stores. Services request credentials by name; Stashly retrieves, caches, and automatically rotates them. The toolkit supports multiple secret backends (Vault, AWS Secrets Manager, Kubernetes Secrets) and provides language-specific SDKs with transparent credential refresh.

## Technology Stack

- **Languages**: Rust (core), Go (CLI), Python (SDK)
- **Secret Backends**:
  - **HashiCorp Vault** — primary backend
  - **AWS Secrets Manager** — AWS environments
  - **Kubernetes Secrets** — K8s native deployments
  - **Environment Variables** — local development
- **Key Features**: Credential caching, TTL-based refresh, rotation hooks, audit logging
- **Dependencies**: reqwest (HTTP), tokio (async), serde (serialization)

## Key Features

- **Unified Credential API**: Single interface for all credential types (database, API keys, certificates)
- **Automatic Rotation**: TTL-based credential refresh without application restart
- **Caching**: In-memory cache with configurable TTL and refresh strategies
- **Audit Trail**: Log all credential access for security and compliance
- **Multi-Backend**: Support Vault, AWS Secrets Manager, Kubernetes, environment variables
- **Rotation Hooks**: Execute custom actions (update connection pools, notify services) on rotation
- **Type-Safe**: Strongly-typed credentials (database, TLS, API key, OAuth token)
- **Performance**: <5ms credential retrieval from cache; configurable refresh windows
- **Local Development**: Mock backend for offline development without Vault

## Quick Start

```bash
# Clone the repository
git clone https://github.com/KooshaPari/Stashly.git
cd Stashly

# Review credential management patterns
cat docs/CREDENTIAL_MANAGEMENT.md

# Configure Vault backend (example)
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=dev-token

# Run example service with credential injection
cargo run --example web-service

# Test credential retrieval
curl http://localhost:3000/health  # Uses Stashly for any needed credentials

# Run tests
cargo test --workspace
```

## Project Structure

```
Stashly/
├── src/
│   ├── credential/                # Credential types and traits
│   │   ├── database.rs            # Database connection credentials
│   │   ├── api_key.rs             # API key credentials
│   │   ├── tls.rs                 # TLS certificate credentials
│   │   └── oauth.rs               # OAuth token credentials
│   ├── store/                     # Secret store implementations
│   │   ├── vault.rs               # HashiCorp Vault backend
│   │   ├── aws.rs                 # AWS Secrets Manager backend
│   │   ├── k8s.rs                 # Kubernetes Secrets backend
│   │   ├── env.rs                 # Environment variable backend
│   │   └── mock.rs                # In-memory mock for testing
│   ├── cache/                     # Credential caching
│   │   ├── memory.rs              # In-memory cache with TTL
│   │   └── refresh.rs             # Automatic refresh strategy
│   ├── client/                    # Client library
│   │   ├── builder.rs             # Client configuration
│   │   ├── rotation_hook.rs       # Callback on credential rotation
│   │   └── metrics.rs             # Cache/retrieval metrics
│   └── audit/                     # Audit logging
├── examples/
│   ├── web-service/               # Service using Stashly
│   ├── database-pool/             # Connection pool with rotation
│   ├── multi-backend/             # Using multiple backends
│   └── local-development/         # Mock backend example
├── tests/
│   ├── integration/               # Vault integration tests
│   ├── rotation/                  # Credential rotation tests
│   └── performance/               # Cache performance benchmarks
├── go/
│   ├── stashly/                   # Go client library
│   ├── cli/                       # Command-line tool (stashly-cli)
│   └── tests/
├── python/
│   ├── stashly/                   # Python SDK
│   └── tests/
└── docs/
    ├── CREDENTIAL_MANAGEMENT.md   # Patterns and best practices
    ├── VAULT_SETUP.md             # Vault configuration
    ├── ROTATION_POLICY.md         # Rotation strategies
    ├── AUDIT_LOGGING.md           # Compliance and audit
    └── BACKENDS.md                # Supported secret stores
```

## Related Phenotype Projects

- **PhenoDevOps** — Orchestrates Vault and credential distribution
- **AgilePlus** — Uses Stashly for database and external service credentials
- **HexaKit** — Secrets port implemented via Stashly
- **AuthKit** — OAuth token management via Stashly

## Quality & Testing

Comprehensive testing across backends and rotation scenarios:
- Unit tests for credential types and parsing
- Integration tests with Vault (testcontainers)
- Rotation tests simulating TTL expiry and refresh
- Performance benchmarks for cache hit rates
- Mock backend for offline testing

```bash
cargo test --workspace --all-features
pytest tests/ -v
go test ./...

# Run Vault integration tests (requires Vault running)
cargo test --test integration -- --include-integration
```

## Credential Types

Stashly supports:
- **Database**: Username/password/connection string
- **API Key**: Static keys with optional scopes
- **TLS**: Certificates and private keys
- **OAuth**: Access tokens with refresh capability
- **Custom**: User-defined credential types

Each type has automatic serialization, validation, and rotation support.

## Security Best Practices

1. **Never log credentials** — Stashly redacts credentials from logs
2. **Rotate regularly** — Set TTL policies in Vault for automatic rotation
3. **Audit access** — Review audit logs for credential usage patterns
4. **Minimize scope** — Grant services access to only needed credentials
5. **Use TLS** — All communication with Vault and secret stores encrypted

## Governance

All work tracked in AgilePlus. Changes must:
- Maintain credential type backward compatibility
- Include audit logging tests
- Document rotation behavior
- Support all configured backends

---

**Version**: v0.1.0  
**Last Updated**: 2026-04-25
