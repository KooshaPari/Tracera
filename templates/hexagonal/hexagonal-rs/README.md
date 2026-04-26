# Hexagonal Architecture for Rust

A production-ready Hexagonal (Ports & Adapters) Architecture template for Rust applications.

## Features

- **Clean Architecture** - Domain, Application, Infrastructure layers
- **Ports & Adapters** - Hexagonal pattern implementation
- **SOLID Principles** - Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion
- **Event-Driven** - Domain events and event sourcing support
- **Async/Await** - Full async runtime support with Tokio

## Architecture

```
src/
├── domain/           # Core business logic (pure, no dependencies)
│   ├── entities/     # Aggregate roots, entities
│   ├── value_objects/# Immutable value types
│   ├── services/     # Domain services
│   └── events/       # Domain events
├── application/      # Use cases, ports
│   ├── ports/        # Input/Output interfaces (traits)
│   ├── usecases/     # Application services
│   └── dto/          # Data transfer objects
└── infrastructure/   # External adapters
    ├── persistence/   # Database adapters
    ├── api/          # HTTP/gRPC adapters
    └── messaging/    # Message queue adapters
```

## Quick Start

```bash
# Create new project from template
cargo new my-service --template hexagon-rs
cd my-service

# Run tests
cargo test

# Run with logging
RUST_LOG=debug cargo run
```

## Example: Order Entity

```rust
use crate::domain::entities::Entity;
use crate::domain::value_objects::Email;

pub struct Order {
    id: OrderId,
    customer_email: Email,
    items: Vec<OrderItem>,
    status: OrderStatus,
    total: Money,
}

impl Entity for Order {
    type Id = OrderId;

    fn id(&self) -> &Self::Id { &self.id }
}
}
```

## Example: Port (Trait)

```rust
// Input Port - Use Case
pub trait CreateOrderUseCase: Send + Sync {
    async fn execute(&self, cmd: CreateOrderCommand)
        -> Result<OrderId, UseCaseError>;
}

// Output Port - Repository
pub trait OrderRepository: Send + Sync {
    async fn save(&self, order: &Order) -> Result<(), RepositoryError>;
    async fn find_by_id(&self, id: &OrderId) -> Result<Option<Order>, RepositoryError>;
}
```

## Example: Adapter

```rust
pub struct PostgresOrderRepository {
    pool: PgPool,
}

impl OrderRepository for PostgresOrderRepository {
    async fn save(&self, order: &Order) -> Result<(), RepositoryError> {
        // Implementation
    }
}
```

## Methodologies Implemented

| Category | Practices |
|----------|-----------|
| Design | Hexagonal, Clean, SOLID, KISS, DRY, YAGNI |
| Process | TDD, BDD, ATDD, SDD, FDD |
| Architecture | Microservices, CQRS, Event Sourcing, Saga |
| Quality | XDD, Linting, Formatting, Security Scanning |

## Development

```bash
# Format code
cargo fmt

# Lint
cargo clippy -- -D warnings

# Test with coverage
cargo tarpaulin

# Security audit
cargo audit
```

## Crates Used

- `tokio` - Async runtime
- `thiserror` - Error handling
- `uuid` - Entity IDs
- `chrono` - Date/time
- `serde` - Serialization

## License

MIT OR Apache-2.0
