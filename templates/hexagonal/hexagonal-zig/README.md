# Hexagonal Architecture for Zig (hexagonal-zig)

A Hexagonal Architecture (Ports & Adapters) template for Zig, implementing Clean Architecture principles with SOLID design.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  HTTP API    │  │  Persistence │  │   Messaging  │   │
│  │  Adapter     │  │  Adapter     │  │   Adapter    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                    │                  │
          ▼                    ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Ports (Interfaces)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ OrderPort    │  │RepositoryPort│  │ PublisherPort│   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
└─────────┼──────────────────┼──────────────────┼────────────┘
          │                    │                  │
          ▼                    ▼                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                            │
│  ┌─────────────────────────────────────────────────────┐     │
│  │                   Use Cases                             │     │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │     │
│  │   │CreateOrder │ │GetOrder    │ │CancelOrder │  │     │
│  │   └─────────────┘ └─────────────┘ └─────────────┘  │     │
│  └─────────────────────────────────────────────────────┘     │
│  ┌─────────────────────────────────────────────────────┐     │
│  │               DTOs (Data Transfer Objects)           │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Domain Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Entities   │  │Value Objects │  │   Services  │   │
│  │  - Order    │  │ - Email     │  │ - Domain    │   │
│  │  - Customer │  │ - Money     │  │   Services  │   │
│  │  - Product  │  │ - Address   │  │             │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌─────────────────────────────────────────────────┐     │
│  │                   Domain Events                    │     │
│  │  OrderCreated | OrderCancelled | PaymentReceived │     │
│  └─────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
hexagonal-zig/
├── src/
│   ├── domain/
│   │   ├── entities.zig      # Core business entities
│   │   ├── value_objects.zig   # Immutable value types
│   │   ├── services.zig        # Domain services
│   │   ├── events.zig          # Domain events
│   │   └── errors.zig           # Domain errors
│   ├── application/
│   │   ├── ports.zig           # Interface definitions
│   │   ├── usecases.zig        # Application use cases
│   │   └── dto.zig              # Data transfer objects
│   ├── infrastructure/
│   │   ├── adapters.zig        # Port implementations
│   │   ├── persistence/        # Database adapters
│   │   ├── api/                # HTTP/gRPC adapters
│   │   └── messaging/           # Message queue adapters
│   └── main.zig               # Entry point
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/           # Integration tests
├── docs/
│   └── ARCHITECTURE.md        # Architecture docs
├── build.zig                  # Build configuration
└── README.md
```

## Key Concepts

### Domain Layer (Core)
- **Entities**: Objects with identity (Order, Customer, Product)
- **Value Objects**: Immutable objects defined by attributes (Email, Money, Address)
- **Domain Services**: Operations without identity
- **Domain Events**: Significant business events

### Application Layer
- **Ports**: Interfaces defining contracts (Input/Output ports)
- **Use Cases**: Application services implementing business logic
- **DTOs**: Data structures for layer communication

### Infrastructure Layer
- **Adapters**: Implementations of ports
- **Persistence**: Database adapters (SQL, NoSQL, etc.)
- **API**: HTTP, gRPC, GraphQL adapters
- **Messaging**: Event bus, message queue adapters

## Design Principles Applied

- **Single Responsibility**: Each module has one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes substitutable for base types
- **Interface Segregation**: Specific interfaces over general ones
- **Dependency Inversion**: Depend on abstractions, not concretions

## Building

```bash
zig build
```

## Testing

```bash
zig build test
```

## Examples

### Creating an Order

```zig
const allocator = std.heap.page_allocator;

// Create domain entities
const customer = Customer.create("cust-123", "john@example.com");
const product = Product.create("prod-456", "Widget", Money.create(999, "USD"));
const order = try Order.create(customer, &.{product});

// Create infrastructure adapters
var repo = InMemoryOrderRepository.init(allocator);
defer repo.deinit();

// Create and execute use case
const use_case = CreateOrderUseCase.init(&repo);
const result = try use_case.execute(order);
```

### Testing with Mock Adapters

```zig
const testing = std.testing;
const MockOrderRepository = struct {
    // Mock implementation for tests
};

test "Create order use case" {
    var mock_repo = MockOrderRepository{};
    var use_case = CreateOrderUseCase.init(&mock_repo);

    const order = try Order.create(...);
    const result = try use_case.execute(order);

    try testing.expect(result.isOk());
}
```

## License

MIT OR Apache-2.0
