# Domain Kit

## At a Glance
- **Purpose:** Supply domain-driven design primitives—entities, value objects, aggregates, and domain events.
- **Best For:** Modeling business logic with explicit boundaries and event-driven workflows.
- **Key Building Blocks:** `Entity`, `ValueObject`, `AggregateRoot`, `DomainEvent`, `AggregateRepository` helpers.

## Core Capabilities
- Immutable value objects with structural equality.
- Entity base class with identity management and change tracking.
- Aggregate roots that collect domain events and support rehydration from history.
- Domain event base type and dispatcher utilities.
- Snapshotting helpers for event-sourced aggregates.

## Getting Started

### Installation
```
pip install domain-kit
```

### Minimal Example
```python
from domain_kit import ValueObject, AggregateRoot, DomainEvent
from dataclasses import dataclass

@dataclass(frozen=True)
class Email(ValueObject):
    address: str

    def __post_init__(self) -> None:
        if "@" not in self.address:
            raise ValueError("invalid email")

@dataclass
class UserRegistered(DomainEvent):
    email: str

@dataclass
class User(AggregateRoot):
    email: Email

    @classmethod
    def register(cls, email: Email) -> "User":
        user = cls(email=email)
        user.add_event(UserRegistered(email=email.address))
        return user
```

## How It Works
- Base classes live in `domain_kit.base` and enforce equality semantics.
- Aggregates track pending events via `add_event()`/`clear_events()`; integrate with workflow-kit or event-kit to publish them.
- Entities use UUID-backed identifiers by default; override `generate_id` for domain-specific IDs.
- Repositories (see adapter-kit) persist aggregates while translating between domain objects and persistence models.

## Usage Recipes
- Wrap aggregate state changes in methods that emit domain events.
- Use db-kit repositories to persist aggregates and replay events during rehydration.
- Apply value objects for primitives (Email, Money, Address) to centralize validation.
- Combine with workflow-kit sagas to coordinate domain events across services.

## Interoperability
- Adapter-kit repositories are the persistence layer for aggregates.
- Event-kit publishes domain events to external subscribers.
- Observability-kit can log domain events for auditing.

## Operations & Observability
- Emit metrics on event counts (`domain_events_total`) for monitoring business activity.
- Log state transitions with domain-specific context (aggregate ID, version).
- Use process-monitor-sdk to expose aggregate health (e.g., backlog sizes).

## Testing & QA
- Instantiate aggregates directly and assert resulting events.
- Use in-memory repositories to test domain logic without a database.
- Snapshot state and events to compare expected outcomes in regression tests.

## Troubleshooting
- **Missing events:** ensure `add_event` is called before returning from command handlers.
- **Equality issues:** double-check that value objects are frozen dataclasses or implement `__hash__`/`__eq__` properly.
- **ID collisions:** override `AggregateRoot.generate_id` with deterministic ID generation if needed.

## Primary API Surface
- `ValueObject` (subclass via frozen dataclasses)
- `Entity` / `AggregateRoot`
- `DomainEvent`
- `AggregateRoot.add_event(event)` / `clear_events()`
- `AggregateRoot.rehydrate(events)`

## Additional Resources
- Examples: `domain-kit/examples/`
- Tests: `domain-kit/tests/`
- Related concepts: [Architecture](../concepts/architecture.md)
