# Common Patterns

> Design patterns and best practices for Pheno-SDK applications

---

## Table of Contents

- [Repository Pattern](#repository-pattern)
- [Saga Pattern](#saga-pattern)
- [Event-Driven Architecture](#event-driven-architecture)
- [Multi-Tenancy](#multi-tenancy)
- [Dependency Injection](#dependency-injection)
- [CQRS Pattern](#cqrs-pattern)
- [Circuit Breaker](#circuit-breaker)
- [Retry Pattern](#retry-pattern)

---

## Repository Pattern

Abstracts data access logic from business logic.

### Basic Implementation

```python
from adapter_kit import Repository
from db_kit import Database
from typing import Optional, List, Dict, Any

class UserRepository(Repository[User, str]):
    """Repository for User entities."""

    def __init__(self, db: Database):
        self.db = db

    async def get_by_id(self, id: str) -> Optional[User]:
        """Get user by ID."""
        data = await self.db.get_single("users", filters={"id": id})
        return User(**data) if data else None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        data = await self.db.get_single("users", filters={"email": email})
        return User(**data) if data else None

    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[User]:
        """List users with filtering."""
        data = await self.db.query("users", filters=filters, limit=limit, offset=offset)
        return [User(**row) for row in data]

    async def save(self, user: User) -> User:
        """Save user (create or update)."""
        if user.id:
            # Update existing
            await self.db.update(
                "users",
                data=user.dict(exclude={"id"}),
                filters={"id": user.id}
            )
        else:
            # Create new
            result = await self.db.insert("users", user.dict(exclude={"id"}))
            user.id = result["id"]
        return user

    async def delete(self, id: str) -> bool:
        """Delete user by ID."""
        count = await self.db.delete("users", filters={"id": id})
        return count > 0
```

### Usage

```python
from adapter_kit import Container

# Configure DI
container = Container()
container.register_instance(Database, db)
container.register(UserRepository, UserRepository)

# Resolve repository
user_repo = container.resolve(UserRepository)

# Use repository
user = await user_repo.get_by_email("alice@example.com")
users = await user_repo.list(filters={"active": True})
await user_repo.save(new_user)
```

**Benefits:**
- Centralized data access logic
- Easy to test with in-memory implementations
- Consistent interface across different data sources
- Business logic independent of data layer

---

## Saga Pattern

Manages distributed transactions with automatic compensation.

### Implementation

```python
from workflow_kit import Saga, SagaExecutor

async def checkout_saga():
    """Checkout saga with automatic compensation."""
    saga = Saga("checkout")

    # Step 1: Reserve inventory
    saga.add_step(
        name="reserve_inventory",
        action=lambda ctx: inventory.reserve(
            items=ctx["items"],
            order_id=ctx["order_id"]
        ),
        compensation=lambda ctx: inventory.release(
            order_id=ctx["order_id"]
        )
    )

    # Step 2: Charge payment
    saga.add_step(
        name="charge_payment",
        action=lambda ctx: payment.charge(
            amount=ctx["amount"],
            customer_id=ctx["customer_id"]
        ),
        compensation=lambda ctx: payment.refund(
            transaction_id=ctx["transaction_id"]
        )
    )

    # Step 3: Create shipment
    saga.add_step(
        name="create_shipment",
        action=lambda ctx: shipping.create(
            order_id=ctx["order_id"],
            address=ctx["shipping_address"]
        ),
        compensation=lambda ctx: shipping.cancel(
            shipment_id=ctx["shipment_id"]
        )
    )

    # Step 4: Send confirmation
    saga.add_step(
        name="send_confirmation",
        action=lambda ctx: email.send_confirmation(
            email=ctx["email"],
            order_id=ctx["order_id"]
        ),
        compensation=lambda ctx: email.send_cancellation(
            email=ctx["email"],
            order_id=ctx["order_id"]
        )
    )

    # Execute saga
    executor = SagaExecutor()
    context = {
        "order_id": "order-123",
        "items": [{"sku": "WIDGET-1", "quantity": 2}],
        "amount": 99.99,
        "customer_id": "cust-456",
        "shipping_address": "123 Main St",
        "email": "customer@example.com"
    }

    try:
        result = await executor.execute(saga, context)
        return {"success": True, "order_id": context["order_id"]}
    except Exception as e:
        # Saga automatically compensates on failure
        logger.error("Checkout failed, compensating", exc_info=e)
        return {"success": False, "error": str(e)}
```

**Benefits:**
- Automatic rollback on failure
- Consistent state management
- Distributed transaction handling
- Clear compensation logic

---

## Event-Driven Architecture

Decouple components using events.

### Event Bus Pattern

```python
from event_kit import EventBus

bus = EventBus()

# Event handlers
@bus.on("user.created")
async def send_welcome_email(event):
    """Send welcome email when user is created."""
    await email.send(
        to=event.data["email"],
        subject="Welcome!",
        template="welcome"
    )

@bus.on("user.created")
async def create_user_profile(event):
    """Create user profile."""
    await profile.create(
        user_id=event.data["user_id"],
        defaults={"theme": "light"}
    )

@bus.on("user.created")
async def track_registration(event):
    """Track registration in analytics."""
    await analytics.track(
        user_id=event.data["user_id"],
        event="user_registered"
    )

# Publish events
async def register_user(email: str, password: str):
    """Register new user."""
    # Create user
    user = await db.insert("users", {"email": email})

    # Publish event
    await bus.publish("user.created", {
        "user_id": user["id"],
        "email": email,
        "timestamp": datetime.utcnow().isoformat()
    })

    return user
```

### Event Sourcing

```python
from event_kit import EventStore

store = EventStore()

# Append events
await store.append(
    event_type="OrderPlaced",
    aggregate_id="order-123",
    aggregate_type="Order",
    data={"items": [...], "total": 99.99}
)

await store.append(
    event_type="PaymentReceived",
    aggregate_id="order-123",
    aggregate_type="Order",
    data={"amount": 99.99, "method": "card"}
)

# Replay events to rebuild state
events = await store.get_stream("order-123")
order = Order()
for event in events:
    order.apply(event)
```

**Benefits:**
- Loose coupling between components
- Easy to add new behaviors
- Audit trail of all events
- Temporal queries (replay events)

---

## Multi-Tenancy

Isolate data by tenant.

### Tenant Context Pattern

```python
from db_kit import Database
from fastapi import Request, Depends

async def get_tenant_id(request: Request) -> str:
    """Extract tenant ID from request."""
    # From subdomain: tenant1.api.example.com
    host = request.headers.get("host", "")
    subdomain = host.split(".")[0]

    # Or from header
    # tenant_id = request.headers.get("X-Tenant-ID")

    # Or from JWT
    # token = request.headers.get("Authorization")
    # tenant_id = decode_jwt(token)["tenant_id"]

    return subdomain

async def get_tenant_db(tenant_id: str = Depends(get_tenant_id)) -> Database:
    """Get database scoped to tenant."""
    db = Database.supabase()

    # Use tenant context for automatic filtering
    async with db.tenant_context(tenant_id) as tenant_db:
        yield tenant_db

# Use in routes
@app.get("/users")
async def list_users(db: Database = Depends(get_tenant_db)):
    """List users for current tenant."""
    # Automatically filtered by tenant_id
    users = await db.query("users", filters={"active": True})
    return users
```

### Row-Level Security (RLS)

```python
from db_kit import Database

async def get_user_db(user_token: str) -> Database:
    """Get database with user context for RLS."""
    db = Database.supabase()
    db.set_access_token(user_token)

    # All queries now respect RLS policies
    return db

# Supabase RLS policy example:
"""
CREATE POLICY "Users can only see own data"
ON users
FOR SELECT
USING (auth.uid() = user_id);
"""

# Usage
@app.get("/profile")
async def get_profile(db: Database = Depends(get_user_db)):
    """Get user profile (RLS ensures only own data)."""
    profile = await db.get_single("profiles", filters={"user_id": current_user_id})
    return profile
```

**Benefits:**
- Data isolation between tenants
- Single application instance
- Efficient resource usage
- Simplified deployment

---

## Dependency Injection

Manage dependencies cleanly.

### Container Pattern

```python
from adapter_kit import Container
from abc import ABC, abstractmethod

# Define interfaces
class IEmailService(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str): pass

class INotificationService(ABC):
    @abstractmethod
    async def notify(self, user_id: str, message: str): pass

# Implementations
class SendGridEmail(IEmailService):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def send(self, to: str, subject: str, body: str):
        # SendGrid implementation
        pass

class PushNotificationService(INotificationService):
    async def notify(self, user_id: str, message: str):
        # Push notification implementation
        pass

# Configure container
container = Container()
container.register(
    IEmailService,
    lambda: SendGridEmail(api_key=config.sendgrid_api_key),
    singleton=True
)
container.register(
    INotificationService,
    PushNotificationService,
    singleton=True
)

# Service using dependencies
class UserService:
    def __init__(self, email: IEmailService, notifications: INotificationService):
        self.email = email
        self.notifications = notifications

    async def register_user(self, email: str):
        # Use injected dependencies
        await self.email.send(email, "Welcome", "...")
        await self.notifications.notify(user_id, "Welcome!")

# Register service
container.register(UserService, UserService)

# Resolve with automatic injection
user_service = container.resolve(UserService)
```

**Benefits:**
- Loose coupling
- Easy testing (inject mocks)
- Configurable dependencies
- Clear dependency graph

---

## CQRS Pattern

Separate reads and writes.

### Implementation

```python
from dataclasses import dataclass
from typing import List

# Commands (writes)
@dataclass
class CreateUserCommand:
    email: str
    name: str
    password: str

@dataclass
class UpdateUserCommand:
    user_id: str
    name: str

# Command handlers
class UserCommandHandler:
    def __init__(self, db: Database, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle_create_user(self, cmd: CreateUserCommand) -> str:
        """Handle user creation command."""
        # Validate
        if await self.db.query("users", filters={"email": cmd.email}):
            raise ValueError("Email already exists")

        # Execute
        user = await self.db.insert("users", {
            "email": cmd.email,
            "name": cmd.name,
            "password_hash": hash_password(cmd.password)
        })

        # Publish event
        await self.event_bus.publish("user.created", {
            "user_id": user["id"],
            "email": cmd.email
        })

        return user["id"]

    async def handle_update_user(self, cmd: UpdateUserCommand):
        """Handle user update command."""
        await self.db.update(
            "users",
            data={"name": cmd.name},
            filters={"id": cmd.user_id}
        )

        await self.event_bus.publish("user.updated", {
            "user_id": cmd.user_id
        })

# Queries (reads)
@dataclass
class GetUserQuery:
    user_id: str

@dataclass
class ListUsersQuery:
    active_only: bool = True
    limit: int = 100

# Query handlers
class UserQueryHandler:
    def __init__(self, db: Database):
        self.db = db

    async def handle_get_user(self, query: GetUserQuery) -> dict:
        """Handle get user query."""
        return await self.db.get_single("users", filters={"id": query.user_id})

    async def handle_list_users(self, query: ListUsersQuery) -> List[dict]:
        """Handle list users query."""
        filters = {"active": True} if query.active_only else None
        return await self.db.query("users", filters=filters, limit=query.limit)

# Usage
@app.post("/users")
async def create_user(
    email: str,
    name: str,
    password: str,
    handler: UserCommandHandler = Depends()
):
    """Create user (command)."""
    cmd = CreateUserCommand(email=email, name=name, password=password)
    user_id = await handler.handle_create_user(cmd)
    return {"user_id": user_id}

@app.get("/users/{user_id}")
async def get_user(
    user_id: str,
    handler: UserQueryHandler = Depends()
):
    """Get user (query)."""
    query = GetUserQuery(user_id=user_id)
    user = await handler.handle_get_user(query)
    return user
```

**Benefits:**
- Optimized reads and writes
- Clear separation of concerns
- Scalable architecture
- Event sourcing friendly

---

## Circuit Breaker

Prevent cascading failures.

### Implementation

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timedelta(seconds=timeout_seconds)
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time < self.timeout:
                raise Exception("Circuit breaker is OPEN")
            else:
                self.state = CircuitState.HALF_OPEN
                self.successes = 0

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call."""
        self.failures = 0

        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
payment_circuit = CircuitBreaker(failure_threshold=3, timeout_seconds=30)

async def charge_payment(amount: float):
    """Charge payment with circuit breaker."""
    try:
        result = await payment_circuit.call(
            payment_service.charge,
            amount=amount
        )
        return result
    except Exception as e:
        logger.error("Payment failed", exc_info=e)
        # Fallback logic
        await queue.add_to_retry(amount)
        raise
```

**Benefits:**
- Prevent cascading failures
- Automatic recovery testing
- System stability
- Graceful degradation

---

## Retry Pattern

Handle transient failures.

### Implementation

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry(
    func: Callable[..., T],
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
) -> T:
    """Retry function with exponential backoff."""
    last_exception = None

    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as e:
            last_exception = e

            if attempt < max_attempts - 1:
                wait_time = delay * (backoff ** attempt)
                logger.warning(
                    f"Attempt {attempt + 1} failed, retrying in {wait_time}s",
                    exc_info=e
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"All {max_attempts} attempts failed", exc_info=e)

    raise last_exception

# Usage
async def fetch_external_data():
    """Fetch data with retries."""
    return await retry(
        lambda: httpx.get("https://api.example.com/data"),
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(httpx.RequestError, httpx.TimeoutException)
    )
```

### Decorator Version

```python
from functools import wraps

def with_retry(max_attempts=3, delay=1.0, backoff=2.0):
    """Decorator for retry logic."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                delay=delay,
                backoff=backoff
            )
        return wrapper
    return decorator

# Usage
@with_retry(max_attempts=3, delay=1.0)
async def fetch_user_data(user_id: str):
    """Fetch user data with automatic retries."""
    response = await http_client.get(f"/users/{user_id}")
    return response.json()
```

**Benefits:**
- Handle transient failures
- Configurable retry logic
- Exponential backoff
- Reduces manual error handling

---

## Summary

These patterns help you build robust, scalable applications with Pheno-SDK:

1. **Repository** - Clean data access
2. **Saga** - Distributed transactions
3. **Event-Driven** - Loose coupling
4. **Multi-Tenancy** - Data isolation
5. **Dependency Injection** - Flexible dependencies
6. **CQRS** - Optimized reads/writes
7. **Circuit Breaker** - Failure isolation
8. **Retry** - Transient failure handling

Use these patterns as building blocks for your applications! 🏗️
