# Hexagonal Architecture Template for C# (.NET)

A production-ready hexagonal (ports & adapters) architecture template for C# / .NET applications.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Application Core                        │
│  ┌─────────────────────────────────────────────────┐  │
│  │              Application Layer                      │  │
│  │  ┌──────────┐ ┌──────────────┐ ┌────────────┐  │  │
│  │  │  Ports  │ │   UseCases   │ │    DTOs   │  │  │
│  │  │(Interfaces)│ │(Business Logic)│ │   (Data)  │  │  │
│  │  └──────────┘ └──────────────┘ └────────────┘  │  │
│  └─────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────┐  │
│  │                 Domain Layer                      │  │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────────┐  │  │
│  │  │ Entities │ │ValueObjects│ │   Services  │  │  │
│  │  └──────────┘ └───────────┘ └──────────────┘  │  │
│  │  ┌────────────────────────────────────────┐   │  │
│  │  │           Domain Events                 │   │  │
│  │  └────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│  Persistence  │ │      API      │ │   Messaging   │
│   Adapter     │ │    Adapter    │ │    Adapter    │
└───────────────┘ └───────────────┘ └───────────────┘
```

## Project Structure

```
src/
├── Hexagon.CS.Domain/           # Core business logic (no dependencies)
│   ├── Entities/                # Domain entities with business rules
│   ├── ValueObjects/           # Immutable value types
│   ├── Services/               # Domain services
│   ├── Events/                # Domain events
│   └── Specifications/         # Specification pattern
│
├── Hexagon.CS.Application/     # Application services
│   ├── Ports/                 # Interface definitions (driving/driven)
│   ├── UseCases/              # Application use cases
│   └── DTOs/                 # Data transfer objects
│
├── Hexagon.CS.Infrastructure/ # External adapters
│   ├── Persistence/          # Database adapters (EF, Dapper)
│   ├── API/                  # API adapters (REST, GraphQL)
│   └── Messaging/            # Message broker adapters
│
└── Hexagon.CS.Api/           # API layer (presentation)
    └── Controllers/           # API endpoints
```

## Key Principles

### 1. Dependency Rule
- Domain layer has ZERO external dependencies
- Application layer depends ONLY on Domain
- Infrastructure implements Application ports
- Presentation depends on Application

### 2. Ports & Adapters
- **Driving Ports**: Interfaces defined in Application, implemented by Presentation
- **Driven Ports**: Interfaces defined in Application, implemented by Infrastructure

### 3. CQRS (Command Query Responsibility Segregation)
- Commands: Modify state (Create, Update, Delete)
- Queries: Read state without side effects

### 4. Domain Events
- Capture business events for audit trail
- Enable eventual consistency
- Decouple bounded contexts

## Usage

```bash
# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run tests
dotnet test

# Run application
dotnet run --project src/Hexagon.CS.Api
```

## Example: Creating an Order

```csharp
// 1. Create Order (Domain)
var order = Order.Create(
    customerId: Guid.NewGuid(),
    items: new List<OrderItem>
    {
        OrderItem.Create(productId, quantity, price)
    }
);

// 2. Use Case (Application)
var useCase = new CreateOrderUseCase(orderRepository, eventBus);
await useCase.ExecuteAsync(request);

// 3. Port Implementation (Infrastructure)
public class OrderRepository : IOrderRepository
{
    public async Task SaveAsync(Order order) { /* persistence */ }
}
```

## Testing Strategy

```csharp
[Fact]
public void Order_Create_WithValidData_Success()
{
    // Arrange
    var customerId = Guid.NewGuid();
    var items = new List<OrderItem> { OrderItem.Create(productId, 2, 100m) };

    // Act
    var order = Order.Create(customerId, items);

    // Assert
    Assert.NotNull(order);
    Assert.Equal(OrderStatus.Pending, order.Status);
}
```

## References

- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Onion Architecture](https://jeffreypalermo.com/2008/07/onion-architecture-part-1/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [.NET Microservices Architecture Guide](https://docs.microsoft.com/en-us/dotnet/architecture/microservices/)

## License

MIT
