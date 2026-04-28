# Pheno-SDK Hexagonal Architecture Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Layer Responsibilities](#layer-responsibilities)
3. [Directory Structure](#directory-structure)
4. [Design Patterns](#design-patterns)
5. [Implementation Examples](#implementation-examples)
6. [Testing Strategy](#testing-strategy)
7. [Best Practices](#best-practices)

---

## Architecture Overview

### Hexagonal Architecture (Ports & Adapters)

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRIMARY ADAPTERS                            │
│                        (Driving Side)                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   CLI    │  │ REST API │  │   MCP    │  │  Events  │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │               │
│       └─────────────┴─────────────┴─────────────┘               │
│                          │                                       │
│                   ┌──────▼──────┐                               │
│                   │   PRIMARY   │                               │
│                   │    PORTS    │                               │
│                   │ (Interfaces)│                               │
│                   └──────┬──────┘                               │
├──────────────────────────┼────────────────────────────────────┤
│                   ┌──────▼──────┐                               │
│                   │ APPLICATION │                               │
│                   │    LAYER    │                               │
│                   │  Use Cases  │                               │
│                   │    CQRS     │                               │
│                   └──────┬──────┘                               │
│                          │                                       │
│                   ┌──────▼──────┐                               │
│                   │   DOMAIN    │                               │
│                   │    LAYER    │                               │
│                   │  Entities   │                               │
│                   │ Value Objs  │                               │
│                   │   Events    │                               │
│                   └──────┬──────┘                               │
│                          │                                       │
│                   ┌──────▼──────┐                               │
│                   │  SECONDARY  │                               │
│                   │    PORTS    │                               │
│                   │ (Interfaces)│                               │
│                   └──────┬──────┘                               │
│                          │                                       │
│       ┌─────────────────┴─────────────────┐                    │
│       │             │             │        │                    │
│  ┌────▼─────┐  ┌───▼────┐  ┌────▼────┐  ┌▼──────┐            │
│  │ Database │  │External│  │  File   │  │ Cache │            │
│  │ Adapters │  │  APIs  │  │ System  │  │Logging│            │
│  └──────────┘  └────────┘  └─────────┘  └───────┘            │
│                                                                  │
│                    SECONDARY ADAPTERS                            │
│                      (Driven Side)                              │
└─────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Dependency Rule**: Dependencies point inward
   - Domain has NO dependencies
   - Application depends on Domain
   - Adapters depend on Application/Domain

2. **Port-Adapter Pattern**
   - Ports = Interfaces (Protocols/ABCs)
   - Adapters = Implementations
   - Business logic isolated from infrastructure

3. **CQRS (Command Query Responsibility Segregation)**
   - Commands: Change state
   - Queries: Read state
   - Separate models for read/write

---

## Layer Responsibilities

### 1. Domain Layer (`src/pheno/domain/`)

**Purpose**: Pure business logic, no infrastructure concerns

**Contains**:
- **Entities**: Objects with identity (e.g., User, Deployment)
- **Value Objects**: Immutable objects without identity (e.g., Email, Port)
- **Domain Events**: Things that happened (e.g., UserCreated, DeploymentStarted)
- **Domain Services**: Complex business logic spanning multiple entities
- **Domain Exceptions**: Business rule violations

**Rules**:
- ✅ NO external dependencies (only stdlib)
- ✅ NO I/O operations
- ✅ 100% unit testable
- ✅ Immutable where possible
- ✅ Type hints everywhere

**Example**:
```python
# src/pheno/domain/entities/user.py
from dataclasses import dataclass
from typing import Optional
from pheno.domain.value_objects import Email, UserId
from pheno.domain.events import UserCreated

@dataclass(frozen=True)
class User:
    """User entity with business logic."""
    id: UserId
    email: Email
    name: str
    is_active: bool = True

    @classmethod
    def create(cls, email: Email, name: str) -> tuple['User', UserCreated]:
        """Factory method that returns entity + event."""
        user_id = UserId.generate()
        user = cls(id=user_id, email=email, name=name)
        event = UserCreated(user_id=user_id, email=email, name=name)
        return user, event

    def deactivate(self) -> 'User':
        """Business logic: deactivate user."""
        if not self.is_active:
            raise UserAlreadyInactive(self.id)
        return dataclasses.replace(self, is_active=False)
```

---

### 2. Application Layer (`src/pheno/application/`)

**Purpose**: Orchestrate use cases, coordinate domain objects

**Contains**:
- **Use Cases**: Application-specific business rules
- **Commands**: Requests to change state
- **Queries**: Requests to read state
- **DTOs**: Data Transfer Objects for input/output
- **Application Events**: Cross-cutting concerns

**Rules**:
- ✅ Depends on Domain layer
- ✅ Uses Ports (interfaces) for infrastructure
- ✅ NO direct adapter dependencies
- ✅ Testable with mocked ports

**Example**:
```python
# src/pheno/application/use_cases/create_user.py
from dataclasses import dataclass
from pheno.domain.entities import User
from pheno.domain.value_objects import Email
from pheno.application.ports import UserRepository, EventPublisher

@dataclass
class CreateUserCommand:
    """Command to create a user."""
    email: str
    name: str

@dataclass
class CreateUserResult:
    """Result of creating a user."""
    user_id: str
    email: str
    name: str

class CreateUserUseCase:
    """Use case for creating a user."""

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher,
    ):
        self._user_repo = user_repository
        self._event_publisher = event_publisher

    async def execute(self, command: CreateUserCommand) -> CreateUserResult:
        """Execute the use case."""
        # Validate
        email = Email(command.email)

        # Check if user exists
        existing = await self._user_repo.find_by_email(email)
        if existing:
            raise UserAlreadyExists(email)

        # Create domain entity
        user, event = User.create(email=email, name=command.name)

        # Persist
        await self._user_repo.save(user)

        # Publish event
        await self._event_publisher.publish(event)

        # Return DTO
        return CreateUserResult(
            user_id=str(user.id),
            email=str(user.email),
            name=user.name,
        )
```

---

### 3. Ports Layer (`src/pheno/application/ports/`)

**Purpose**: Define interfaces for infrastructure

**Contains**:
- **Primary Ports**: Interfaces for driving adapters (CLI, API)
- **Secondary Ports**: Interfaces for driven adapters (DB, APIs)

**Rules**:
- ✅ Use Python `Protocol` for structural typing
- ✅ Use ABC for behavioral contracts
- ✅ Document contracts clearly

**Example**:
```python
# src/pheno/application/ports/repositories.py
from typing import Protocol, Optional
from pheno.domain.entities import User
from pheno.domain.value_objects import UserId, Email

class UserRepository(Protocol):
    """Port for user persistence."""

    async def save(self, user: User) -> None:
        """Save a user."""
        ...

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        ...

    async def find_by_email(self, email: Email) -> Optional[User]:
        """Find user by email."""
        ...

    async def delete(self, user_id: UserId) -> None:
        """Delete a user."""
        ...
```

---

### 4. Adapters Layer (`src/pheno/adapters/`)

**Purpose**: Implement ports, connect to external systems

**Contains**:
- **Primary Adapters**: CLI, REST API, MCP, Events
- **Secondary Adapters**: Database, External APIs, File System, Cache

**Rules**:
- ✅ Implement port interfaces
- ✅ Handle infrastructure concerns
- ✅ Testable with real/fake implementations

**Example**:
```python
# src/pheno/adapters/persistence/sqlalchemy_user_repository.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from pheno.domain.entities import User
from pheno.domain.value_objects import UserId, Email
from pheno.application.ports import UserRepository

class SQLAlchemyUserRepository:
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, user: User) -> None:
        """Save user to database."""
        user_model = UserModel(
            id=str(user.id),
            email=str(user.email),
            name=user.name,
            is_active=user.is_active,
        )
        self._session.add(user_model)
        await self._session.commit()

    async def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find user by ID."""
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == str(user_id))
        )
        user_model = result.scalar_one_or_none()
        if not user_model:
            return None
        return self._to_domain(user_model)

    def _to_domain(self, model: UserModel) -> User:
        """Convert ORM model to domain entity."""
        return User(
            id=UserId(model.id),
            email=Email(model.email),
            name=model.name,
            is_active=model.is_active,
        )
```

---

## Directory Structure

```
src/pheno/
├── domain/                      # Domain Layer (Pure Business Logic)
│   ├── __init__.py
│   ├── entities/                # Entities with identity
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── deployment.py
│   │   └── infrastructure.py
│   ├── value_objects/           # Immutable value objects
│   │   ├── __init__.py
│   │   ├── email.py
│   │   ├── port.py
│   │   └── config.py
│   ├── events/                  # Domain events
│   │   ├── __init__.py
│   │   ├── user_events.py
│   │   └── deployment_events.py
│   ├── services/                # Domain services
│   │   ├── __init__.py
│   │   └── deployment_service.py
│   └── exceptions/              # Domain exceptions
│       ├── __init__.py
│       └── user_exceptions.py
│
├── application/                 # Application Layer (Use Cases)
│   ├── __init__.py
│   ├── use_cases/               # Use case implementations
│   │   ├── __init__.py
│   │   ├── user/
│   │   │   ├── create_user.py
│   │   │   ├── update_user.py
│   │   │   └── delete_user.py
│   │   └── deployment/
│   │       ├── create_deployment.py
│   │       └── start_deployment.py
│   ├── commands/                # CQRS Commands
│   │   ├── __init__.py
│   │   └── user_commands.py
│   ├── queries/                 # CQRS Queries
│   │   ├── __init__.py
│   │   └── user_queries.py
│   ├── dtos/                    # Data Transfer Objects
│   │   ├── __init__.py
│   │   └── user_dtos.py
│   ├── events/                  # Application events
│   │   ├── __init__.py
│   │   └── event_handlers.py
│   └── ports/                   # Port interfaces
│       ├── __init__.py
│       ├── repositories.py      # Repository ports
│       ├── services.py          # Service ports
│       └── events.py            # Event ports
│
└── adapters/                    # Adapters Layer (Infrastructure)
    ├── __init__.py
    ├── cli/                     # CLI Adapter (Primary)
    │   ├── __init__.py
    │   ├── commands/
    │   └── handlers.py
    ├── api/                     # API Adapters (Primary)
    │   ├── rest/
    │   │   ├── __init__.py
    │   │   ├── routes/
    │   │   └── middleware.py
    │   └── graphql/
    ├── mcp/                     # MCP Adapter (Primary)
    │   ├── __init__.py
    │   └── server.py
    ├── events/                  # Event Adapters (Primary)
    │   ├── __init__.py
    │   └── listeners.py
    ├── persistence/             # Database Adapters (Secondary)
    │   ├── __init__.py
    │   ├── sqlalchemy/
    │   │   ├── repositories/
    │   │   └── models.py
    │   ├── mongodb/
    │   └── redis/
    ├── external/                # External Service Adapters (Secondary)
    │   ├── __init__.py
    │   ├── aws/
    │   ├── gcp/
    │   └── llm/
    ├── storage/                 # File System Adapters (Secondary)
    │   ├── __init__.py
    │   ├── local.py
    │   └── s3.py
    └── observability/           # Observability Adapters (Secondary)
        ├── __init__.py
        ├── logging.py
        ├── metrics.py
        └── tracing.py
```

---

## Design Patterns

### Creational Patterns

#### 1. Factory Pattern
```python
# src/pheno/application/factories/user_factory.py
class UserFactory:
    """Factory for creating users."""

    @staticmethod
    def create_from_dto(dto: CreateUserDTO) -> User:
        """Create user from DTO."""
        email = Email(dto.email)
        user, event = User.create(email=email, name=dto.name)
        return user
```

#### 2. Builder Pattern
```python
# src/pheno/application/builders/query_builder.py
class QueryBuilder:
    """Builder for complex queries."""

    def __init__(self):
        self._filters = []
        self._sorts = []
        self._limit = None

    def filter(self, field: str, value: Any) -> 'QueryBuilder':
        self._filters.append((field, value))
        return self

    def sort(self, field: str, desc: bool = False) -> 'QueryBuilder':
        self._sorts.append((field, desc))
        return self

    def limit(self, n: int) -> 'QueryBuilder':
        self._limit = n
        return self

    def build(self) -> Query:
        return Query(
            filters=self._filters,
            sorts=self._sorts,
            limit=self._limit,
        )
```

#### 3. Dependency Injection
```python
# src/pheno/infrastructure/di/container.py
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    """DI container for the application."""

    # Configuration
    config = providers.Configuration()

    # Database
    db_session = providers.Singleton(
        create_db_session,
        connection_string=config.database.url,
    )

    # Repositories
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=db_session,
    )

    # Use Cases
    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        user_repository=user_repository,
        event_publisher=event_publisher,
    )
```

---

## Testing Strategy

### 1. Unit Tests (Domain Layer)
```python
# tests/unit/domain/test_user.py
def test_user_creation():
    """Test user creation."""
    email = Email("test@example.com")
    user, event = User.create(email=email, name="Test User")

    assert user.email == email
    assert user.name == "Test User"
    assert user.is_active is True
    assert isinstance(event, UserCreated)

def test_user_deactivation():
    """Test user deactivation."""
    user = User(
        id=UserId.generate(),
        email=Email("test@example.com"),
        name="Test",
        is_active=True,
    )

    deactivated = user.deactivate()
    assert deactivated.is_active is False
```

### 2. Integration Tests (Application Layer)
```python
# tests/integration/application/test_create_user.py
@pytest.mark.asyncio
async def test_create_user_use_case():
    """Test create user use case."""
    # Arrange
    mock_repo = MockUserRepository()
    mock_publisher = MockEventPublisher()
    use_case = CreateUserUseCase(mock_repo, mock_publisher)
    command = CreateUserCommand(email="test@example.com", name="Test")

    # Act
    result = await use_case.execute(command)

    # Assert
    assert result.email == "test@example.com"
    assert mock_repo.saved_users
    assert mock_publisher.published_events
```

### 3. Adapter Tests
```python
# tests/adapters/test_sqlalchemy_user_repository.py
@pytest.mark.asyncio
async def test_save_user(db_session):
    """Test saving user to database."""
    repo = SQLAlchemyUserRepository(db_session)
    user = User(
        id=UserId.generate(),
        email=Email("test@example.com"),
        name="Test",
    )

    await repo.save(user)

    found = await repo.find_by_id(user.id)
    assert found == user
```

---

## Best Practices

### 1. Dependency Rule
- Domain → NO dependencies
- Application → Domain only
- Adapters → Application + Domain

### 2. Immutability
- Use `@dataclass(frozen=True)` for entities/value objects
- Return new instances instead of mutating

### 3. Type Hints
- 100% type coverage
- Use `mypy --strict`

### 4. Testing
- Domain: 100% coverage
- Application: 95% coverage
- Adapters: 85% coverage

### 5. Error Handling
- Domain exceptions for business rules
- Application exceptions for use case failures
- Adapter exceptions for infrastructure failures
