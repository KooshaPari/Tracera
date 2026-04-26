# ADR-002: Hexagonal Architecture Pattern Standardization

**Status**: Accepted  
**Date**: 2026-04-04  
**Deciders**: Phenotype Architecture Team  
**Related**: HEXAGON-SPEC-001, HEXAGON-ADR-001

## Context

Hexagonal architecture, while conceptually consistent across languages, requires language-specific adaptations to remain idiomatic and effective. The Phenotype ecosystem needed a standardized approach to hexagonal patterns that respects language differences while maintaining architectural coherence.

### Problem Statement

1. **Pattern Variation**: Each language community has developed slightly different hexagonal implementations
2. **Learning Curve**: Developers switching languages must relearn hexagonal patterns
3. **Consistency vs Idiom**: Balancing cross-language consistency with language-specific best practices
4. **Tooling Gaps**: Limited tooling support for hexagonal scaffolding
5. **Testing Patterns**: No standardized approach to testing hexagonal systems across languages

## Decision Drivers

| Driver | Weight | Description |
|--------|--------|-------------|
| Portability | High | Domain logic should be conceptually portable across languages |
| Idiomatic | High | Must feel native to each language |
| Testability | High | Easy to test at all layers |
| Clarity | High | Clear separation of concerns |
| Performance | Medium | Minimal overhead from abstractions |
| Tooling | Medium | Support for code generation and IDE integration |

## Decisions

### Decision 1: Four-Layer Hexagonal Structure

**Decision**: Standardize on four-layer structure across all language templates.

```
┌─────────────────────────────────────────┐
│           Primary Adapters                │
│  (CLI, HTTP, Messaging, Schedulers)     │
├─────────────────────────────────────────┤
│           Application Layer             │
│  (Use Cases, DTOs, Handlers)             │
├─────────────────────────────────────────┤
│              Ports Layer                │
│  (InputPort, OutputPort interfaces)    │
├─────────────────────────────────────────┤
│             Domain Layer                │
│  (Entities, ValueObjects, DomainEvents) │
├─────────────────────────────────────────┤
│           Infrastructure Layer          │
│  (DB, External APIs, File System)        │
└─────────────────────────────────────────┘
```

**Layer Responsibilities**:

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| Domain | Pure business logic | None (stdlib only) |
| Application | Use case orchestration | Domain, Ports |
| Ports | Interface definitions | Domain |
| Infrastructure | External integrations | Ports |
| Primary Adapters | Input handling | Application, Ports |

**Rationale**:
- Clear separation of concerns
- Dependency direction inward toward domain
- Testable at each layer
- Consistent across languages

**Consequences**:
- (+) Clear mental model
- (+) Testability at all layers
- (+) Consistent structure across languages
- (-) More files/directories than simple projects
- (-) Learning curve for new developers

### Decision 2: Port Interface Standardization

**Decision**: Define two primary port categories with language-specific implementations.

**Port Categories**:
```
Ports/
├── InputPort/          # Driving ports (application boundary)
│   ├── CommandPort     # State-changing operations
│   └── QueryPort       # Read-only operations
└── OutputPort/         # Driven ports (infrastructure boundary)
    ├── RepositoryPort  # Persistence abstraction
    ├── EventPort       # Event publishing
    └── ExternalPort    # External service integration
```

**Language Implementations**:

**Go**:
```go
// Port marker interfaces
type InputPort interface { isInputPort() }
type OutputPort interface { isOutputPort() }

// Command port
type CommandPort[I, O any] interface {
    InputPort
    Execute(ctx context.Context, input I) (O, error)
}

// Repository port
type RepositoryPort[T any] interface {
    OutputPort
    Save(ctx context.Context, entity T) (T, error)
    FindByID(ctx context.Context, id string) (T, error)
}
```

**Rust**:
```rust
// Port traits
pub trait InputPort: Send + Sync {}
pub trait OutputPort: Send + Sync {}

// Command port
#[async_trait]
pub trait CommandPort<I, O>: InputPort {
    async fn execute(&self, input: I) -> Result<O, DomainError>;
}

// Repository port
#[async_trait]
pub trait RepositoryPort<T>: OutputPort {
    async fn save(&self, entity: T) -> Result<T, RepositoryError>;
    async fn find_by_id(&self, id: &str) -> Result<Option<T>, RepositoryError>;
}
```

**Elixir**:
```elixir
# Port behaviours
defmodule Hexagon.Ports.InputPort do
  @type t :: module()
end

defmodule Hexagon.Ports.CommandPort do
  @callback execute(input :: term()) :: {:ok, term()} | {:error, term()}
end

defmodule Hexagon.Ports.RepositoryPort do
  @callback save(entity :: term()) :: {:ok, term()} | {:error, term()}
  @callback find_by_id(id :: String.t()) :: {:ok, term()} | {:error, :not_found}
end
```

**Rationale**:
- Consistent port taxonomy across languages
- Language-idiomatic implementations
- Clear contract definitions
- Framework-agnostic

**Consequences**:
- (+) Consistent vocabulary across languages
- (+) Clear interface boundaries
- (+) Enables code generation
- (-) Requires language-specific knowledge
- (-) Some languages need adapter patterns

### Decision 3: Domain Entity Standards

**Decision**: Standardize domain entity characteristics across languages.

**Entity Requirements**:

| Characteristic | Requirement | Rationale |
|----------------|-------------|-----------|
| Identity | Every entity has unique ID | Distinguishes entities from value objects |
| Immutability | Entities mutable only through methods | Encapsulation, invariant protection |
| Validation | Construction validates invariants | Fail fast, domain integrity |
| Equality | Based on ID, not attributes | Identity-based comparison |
| String representation | Debug-friendly format | Logging, debugging |

**Language-Specific Patterns**:

**Go**:
```go
type User struct {
    id    EntityID
    email Email
    name  string
}

func NewUser(id EntityID, email Email, name string) (*User, error) {
    if !email.IsValid() {
        return nil, ErrInvalidEmail
    }
    if name == "" {
        return nil, ErrEmptyName
    }
    return &User{id: id, email: email, name: name}, nil
}

func (u *User) ID() EntityID { return u.id }

func (u *User) ChangeEmail(newEmail Email) error {
    if !newEmail.IsValid() {
        return ErrInvalidEmail
    }
    u.email = newEmail
    return nil
}
```

**Rust**:
```rust
pub struct User {
    id: EntityId,
    email: Email,
    name: String,
}

impl User {
    pub fn new(id: EntityId, email: Email, name: String) -> Result<Self, DomainError> {
        if !email.is_valid() {
            return Err(DomainError::InvalidEmail);
        }
        if name.is_empty() {
            return Err(DomainError::EmptyName);
        }
        Ok(Self { id, email, name })
    }
    
    pub fn id(&self) -> &EntityId { &self.id }
    
    pub fn change_email(&mut self, new_email: Email) -> Result<(), DomainError> {
        if !new_email.is_valid() {
            return Err(DomainError::InvalidEmail);
        }
        self.email = new_email;
        Ok(())
    }
}
```

**Rationale**:
- Consistent entity behavior across languages
- Language-idiomatic implementations
- Clear construction and modification rules

**Consequences**:
- (+) Predictable entity behavior
- (+) Easier testing
- (+) Consistent domain modeling
- (-) Boilerplate in some languages
- (-) Steeper learning curve

### Decision 4: Value Object Pattern

**Decision**: Mandate value objects for concepts without identity.

**Value Object Characteristics**:
- No identity (compared by value)
- Immutable
- Self-validating
- Side-effect free operations

**Language Implementations**:

**Go**:
```go
type Money struct {
    amount   decimal.Decimal
    currency string
}

func (m Money) Equals(other ValueObject) bool {
    if o, ok := other.(Money); ok {
        return m.amount.Equal(o.amount) && m.currency == o.currency
    }
    return false
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, ErrCurrencyMismatch
    }
    return Money{
        amount:   m.amount.Add(other.amount),
        currency: m.currency,
    }, nil
}
```

**Rust**:
```rust
#[derive(Debug, Clone, PartialEq)]
pub struct Money {
    amount: Decimal,
    currency: Currency,
}

impl Money {
    pub fn add(&self, other: &Self) -> Result<Self, DomainError> {
        if self.currency != other.currency {
            return Err(DomainError::CurrencyMismatch);
        }
        Ok(Self {
            amount: self.amount + other.amount,
            currency: self.currency,
        })
    }
}
```

**Rationale**:
- Prevents primitive obsession
- Encapsulates domain concepts
- Immutable by design
- Rich behavior

**Consequences**:
- (+) Rich domain model
- (+) Type safety
- (+) Business logic co-location
- (-) More types to learn
- (-) Serialization complexity

### Decision 5: Error Handling Strategy

**Decision**: Standardize on structured errors with domain/application distinction.

**Error Hierarchy**:
```
Error
├── DomainError          # Business rule violations
│   ├── ValidationError  # Invalid input
│   ├── InvariantError   # State violations
│   └── NotFoundError    # Missing entity
├── ApplicationError     # Use case failures
│   ├── UnauthorizedError
│   ├── ConflictError
│   └── TimeoutError
└── InfrastructureError  # External failures
    ├── RepositoryError
    ├── ExternalServiceError
    └── NetworkError
```

**Language Implementations**:

**Go**:
```go
type DomainError struct {
    Code    string
    Message string
    Err     error
}

func (e DomainError) Error() string { return e.Message }

var (
    ErrInvalidEmail = DomainError{Code: "INVALID_EMAIL", Message: "email format invalid"}
    ErrNotFound     = DomainError{Code: "NOT_FOUND", Message: "entity not found"}
)
```

**Rust**:
```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DomainError {
    #[error("invalid email: {0}")]
    InvalidEmail(String),
    #[error("entity not found: {0}")]
    NotFound(String),
    #[error("validation failed: {0}")]
    Validation(String),
}
```

**Rationale**:
- Structured errors for programmatic handling
- Clear error categorization
- Proper error wrapping
- API-friendly error codes

**Consequences**:
- (+) Consistent error handling
- (+) API-friendly responses
- (+) Testable error scenarios
- (-) More error types to manage
- (-) Potential for over-engineering

### Decision 6: Testing Strategy

**Decision**: Standardize three-layer testing with language-specific frameworks.

**Testing Pyramid**:
```
         ▲
        /_\        E2E Tests (Critical paths)
       /___\       
      /_____\     Integration Tests (Adapters)
     /_______\
    /_________\   Unit Tests (Domain + Application)
   /___________\
```

**Test Categories**:

| Layer | Focus | Speed | Count | Tools |
|-------|-------|-------|-------|-------|
| Unit | Domain logic | Fast | Many | Language-native |
| Integration | Adapters | Medium | Some | Test containers |
| E2E | Full scenarios | Slow | Few | Selenium/Playwright |

**Test File Naming**:
```
tests/
├── unit/
│   ├── domain/
│   │   ├── test_user.py              # Python
│   │   ├── user_test.go              # Go
│   │   └── user_tests.rs             # Rust
│   └── application/
├── integration/
│   ├── test_postgres_repository.py
│   └── test_http_adapter.py
└── e2e/
    └── test_user_workflow.py
```

**Rationale**:
- Fast feedback for domain logic
- Integration verification for adapters
- End-to-end confidence
- Language-idiomatic testing

**Consequences**:
- (+) Confidence at all levels
- (+) Fast domain development
- (+) Catches integration issues early
- (-) More tests to maintain
- (-) CI time increases

## Alternatives Considered

### Alternative 1: Three-Layer Architecture (Clean Architecture)

**Approach**: Entities, Use Cases, Interface Adapters, Frameworks

**Rejection**: Four-layer provides clearer separation between application and infrastructure concerns.

### Alternative 2: Onion Architecture

**Approach**: Core domain with layers wrapping outward

**Rejection**: Conceptually similar but less explicit about ports/adapters terminology.

### Alternative 3: DDD-Only Approach

**Approach**: Focus only on DDD tactical patterns without hexagonal

**Rejection**: Hexagonal provides necessary infrastructure isolation.

## Consequences Summary

### Positive

1. **Consistent Vocabulary**: Same terms across all languages
2. **Portable Knowledge**: Learn once, apply to any language
3. **Testable Design**: Clear boundaries enable testing
4. **Evolution Support**: Easy to swap implementations
5. **Code Generation**: Standard patterns enable automation

### Negative

1. **Learning Curve**: New concepts for many developers
2. **Boilerplate**: More files than simple approaches
3. **Performance**: Interface/trait dispatch overhead
4. **Complexity**: More abstractions to understand

### Mitigations

| Concern | Mitigation |
|---------|------------|
| Learning curve | Comprehensive documentation, examples |
| Boilerplate | Code generation, templates |
| Performance | Benchmarks, optimization guides |
| Complexity | Progressive disclosure, layered learning |

## Implementation Verification

### Checklist

- [ ] Domain layer has no external dependencies
- [ ] Ports are interfaces/traits/behaviours
- [ ] Infrastructure implements ports
- [ ] Application orchestrates use cases
- [ ] Primary adapters are thin
- [ ] Errors are structured
- [ ] Tests exist at all layers

### Tooling

```bash
# Verify hexagonal structure
hexagon verify templates/go/
hexagon verify templates/rust/
hexagon verify templates/zig/

# Generate compliance report
hexagon report --format markdown
```

## References

- [Hexagonal Architecture by Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://www.domainlanguage.com/ddd/)

## Traceability

/// @trace HEXAGON-ADR-002
/// @trace HEXAGON-SPEC-002
