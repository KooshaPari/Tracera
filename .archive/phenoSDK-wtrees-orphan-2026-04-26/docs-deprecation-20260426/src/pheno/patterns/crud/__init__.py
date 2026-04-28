"""CRUD Pipeline Standardisation.

Generic base classes and decorators for repository access, DTO mapping, event
publishing, and route wiring. Standardizes common CRUD patterns across use cases and
FastAPI routes.
"""

from .base import (
    BaseActionUseCase,
    BaseCreateUseCase,
    BaseDeleteUseCase,
    BaseGetUseCase,
    BaseListUseCase,
    BaseUpdateUseCase,
    BaseUseCase,
)
from .decorators import (
    crud_route,
    handle_errors,
    publish_events,
    use_case,
    validate_dto,
)
from .mappers import (
    DTOMapper,
    EntityMapper,
    EventMapper,
)
from .scaffold import (
    CRUDScaffold,
    RepositoryScaffold,
    RouteScaffold,
    UseCaseScaffold,
)
from .validators import (
    BusinessRuleValidator,
    DTOValidator,
)

__all__ = [
    "BaseActionUseCase",
    "BaseCreateUseCase",
    "BaseDeleteUseCase",
    "BaseGetUseCase",
    "BaseListUseCase",
    "BaseUpdateUseCase",
    # Base use cases
    "BaseUseCase",
    "BusinessRuleValidator",
    # Scaffolds
    "CRUDScaffold",
    # Mappers
    "DTOMapper",
    # Validators
    "DTOValidator",
    "EntityMapper",
    "EventMapper",
    "RepositoryScaffold",
    "RouteScaffold",
    "UseCaseScaffold",
    "crud_route",
    "handle_errors",
    "publish_events",
    # Decorators
    "use_case",
    "validate_dto",
]
