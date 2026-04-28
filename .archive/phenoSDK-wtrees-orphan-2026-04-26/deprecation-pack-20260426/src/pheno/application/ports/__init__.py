"""
Application Ports - Interface Definitions

Ports define the contracts between the application layer and adapters.
They use Python Protocols for structural typing and ABCs for behavioral contracts.

Port Types:
    - Primary Ports: Driving/inbound adapters (CLI, API, MCP, Events, Tasks)
    - Repository Ports: Data persistence interfaces
    - Service Ports: External service interfaces
    - Event Ports: Event publishing/subscribing interfaces
    - Query Ports: Read-only data access interfaces

Example:
    >>> from pheno.application.ports import UserRepository
    >>>
    >>> class SQLAlchemyUserRepository:
    ...     async def save(self, user: User) -> None:
    ...         # Implementation
    ...         pass
"""

from pheno.application.ports.comprehensive_database_port import (
    ComprehensiveDatabasePort,
)
from pheno.application.ports.database_port import DatabasePort
from pheno.application.ports.events import (
    EventBus,
    EventPublisher,
    EventSubscriber,
)
from pheno.application.ports.primary import (
    APIHandler,
    CLIHandler,
    CommandHandler,
    EventListenerHandler,
    MCPServerHandler,
    ScheduledTaskHandler,
)
from pheno.application.ports.queries import (
    DeploymentQuery,
    QueryHandler,
    ServiceQuery,
    UserQuery,
)
from pheno.application.ports.repositories import (
    ConfigurationRepository,
    DeploymentRepository,
    Repository,
    ServiceRepository,
    UserRepository,
)
from pheno.application.ports.services import (
    EmailService,
    MetricsService,
    NotificationService,
)

__all__ = [
    "APIHandler",
    "CLIHandler",
    # Primary ports (driving/inbound)
    "CommandHandler",
    "ComprehensiveDatabasePort",
    "ConfigurationRepository",
    # Database ports
    "DatabasePort",
    "DeploymentQuery",
    "DeploymentRepository",
    # Service ports (secondary/outbound)
    "EmailService",
    "EventBus",
    "EventListenerHandler",
    # Event ports (secondary/outbound)
    "EventPublisher",
    "EventSubscriber",
    "MCPServerHandler",
    "MetricsService",
    "NotificationService",
    # Query ports (CQRS)
    "QueryHandler",
    # Repository ports (secondary/outbound)
    "Repository",
    "ScheduledTaskHandler",
    "ServiceQuery",
    "ServiceRepository",
    "UserQuery",
    "UserRepository",
]
