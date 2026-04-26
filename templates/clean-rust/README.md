# Clean Architecture Rust Template

A production-ready Clean Architecture template for Rust projects with hexagonal principles.

## Architecture

```
clean-rust/
├── src/
│   ├── domain/                    # Core business logic (no external deps)
│   │   ├── entities/             # Domain models
│   │   ├── value_objects/        # Immutable value types
│   │   ├── ports/                # Interface definitions
│   │   ├── services/             # Domain services
│   │   └── errors/               # Domain errors
│   │
│   ├── application/               # Application layer
│   │   ├── commands/             # Write operations (CQRS)
│   │   ├── queries/              # Read operations (CQRS)
│   │   └── dtos/                 # Data transfer objects
│   │
│   ├── infrastructure/            # Infrastructure layer
│   │   ├── adapters/             # Database, cache adapters
│   │   ├── logging/              # Logging
│   │   └── config/               # Configuration
│   │
│   └── interfaces/                # Interface adapters
│       ├── api/                  # HTTP handlers
│       └── cli/                  # CLI commands
│
└── tests/
    ├── unit/                    # Unit tests
    └── integration/             # Integration tests
```

## Key Principles Applied

- **Rust Ownership Model**: Compile-time memory safety
- **Error Handling**: thiserror for domain errors, anyhow for application errors
- **Async/Await**: Tokio for async runtime
- **Trait Bounds**: Generics with constraints
- **Zero-Cost Abstractions**: No runtime overhead
- **CQRS**: Command Query Responsibility Segregation
- **Dependency Injection**: Via traits and composition

## Wrap-Over Pattern Applied

| Pattern | Library | Why |
|---------|---------|-----|
| Serialization | serde | Well-tested, handles edge cases |
| Database | sqlx | Compile-time queries, connection pooling |
| Logging | tracing | Structured, async-compatible |
| Validation | validator | Declarative validation |
| Error handling | thiserror | Ergonomic error types |

## Getting Started

```bash
# Generate a new project
cp -r clean-rust new-project
cd new-project

# Update Cargo.toml with your project name

# Build
cargo build

# Run tests
cargo test

# Run linter
cargo clippy
```

## Testing Strategy

- **Unit Tests**: Domain layer with pure functions
- **Mock Tests**: Use mockall for interface mocking
- **Integration Tests**: Test adapters with real dependencies

## See Also

- [xDD Methodologies Reference](../reference/xDD/XDD_METHODOLOGIES.md)
- [Rust Error Handling](https://doc.rust-lang.org/book/ch09-00-error-handling.html)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
