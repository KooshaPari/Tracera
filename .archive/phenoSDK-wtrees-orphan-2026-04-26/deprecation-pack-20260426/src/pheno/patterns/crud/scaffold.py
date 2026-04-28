"""CRUD Scaffold Library.

Generic scaffold classes that generate complete CRUD implementations for entities,
reducing boilerplate and ensuring consistency.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from fastapi import APIRouter, Depends, status
from pheno.domain.entities.base import Entity
from pydantic import BaseModel

from pheno.observability.logging import get_logger
from pheno.patterns.crud.base import BaseCRUDUseCase
from pheno.patterns.crud.decorators import crud_route, handle_errors, validate_dto

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import Repository
    from pheno.domain.exceptions.base import DomainException

logger = get_logger(__name__)

# Type variables
EntityType = TypeVar("EntityType", bound=Entity)
CreateDTOType = TypeVar("CreateDTOType", bound=BaseModel)
UpdateDTOType = TypeVar("UpdateDTOType", bound=BaseModel)
ResponseDTOType = TypeVar("ResponseDTOType", bound=BaseModel)
FilterDTOType = TypeVar("FilterDTOType", bound=BaseModel)
EntityIdType = TypeVar("EntityIdType")


class CRUDScaffold(
    Generic[EntityType, CreateDTOType, UpdateDTOType, ResponseDTOType, FilterDTOType, EntityIdType],
):
    """Complete CRUD scaffold for an entity.

    Generates use cases, routes, and dependencies for a complete CRUD API with minimal
    boilerplate.
    """

    def __init__(
        self,
        entity_name: str,
        entity_type: type[EntityType],
        create_dto_type: type[CreateDTOType],
        update_dto_type: type[UpdateDTOType],
        response_dto_type: type[ResponseDTOType],
        filter_dto_type: type[FilterDTOType],
        entity_id_type: type[EntityIdType],
        not_found_exception: type[DomainException],
        repository: Repository[EntityType, EntityIdType],
        event_publisher: EventPublisher | None = None,
    ):
        """Initialize CRUD scaffold.

        Args:
            entity_name: Name of the entity (e.g., "User", "Deployment")
            entity_type: Entity class
            create_dto_type: Create DTO class
            update_dto_type: Update DTO class
            response_dto_type: Response DTO class
            filter_dto_type: Filter DTO class
            entity_id_type: Entity ID type
            not_found_exception: Exception to raise when entity not found
            repository: Repository instance
            event_publisher: Optional event publisher
        """
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.create_dto_type = create_dto_type
        self.update_dto_type = update_dto_type
        self.response_dto_type = response_dto_type
        self.filter_dto_type = filter_dto_type
        self.entity_id_type = entity_id_type
        self.not_found_exception = not_found_exception
        self.repository = repository
        self.event_publisher = event_publisher

        # Create use case scaffold
        self.use_case_scaffold = UseCaseScaffold(
            entity_name=entity_name,
            entity_type=entity_type,
            create_dto_type=create_dto_type,
            update_dto_type=update_dto_type,
            response_dto_type=response_dto_type,
            filter_dto_type=filter_dto_type,
            entity_id_type=entity_id_type,
            not_found_exception=not_found_exception,
            repository=repository,
            event_publisher=event_publisher,
        )

        # Create route scaffold
        self.route_scaffold = RouteScaffold(
            entity_name=entity_name,
            use_case_scaffold=self.use_case_scaffold,
        )

    def create_use_cases(self) -> dict[str, Any]:
        """
        Create all use cases for the entity.
        """
        return self.use_case_scaffold.create_all_use_cases()

    def create_routes(self, router: APIRouter, prefix: str = "") -> None:
        """
        Create all routes for the entity.
        """
        self.route_scaffold.add_routes(router, prefix)

    def create_dependencies(self) -> dict[str, Any]:
        """
        Create dependency injection functions.
        """
        return self.route_scaffold.create_dependencies()


class UseCaseScaffold(
    Generic[EntityType, CreateDTOType, UpdateDTOType, ResponseDTOType, FilterDTOType, EntityIdType],
):
    """Scaffold for generating use cases.

    Creates standard use cases (create, update, get, list, delete) with minimal
    configuration.
    """

    def __init__(
        self,
        entity_name: str,
        entity_type: type[EntityType],
        create_dto_type: type[CreateDTOType],
        update_dto_type: type[UpdateDTOType],
        response_dto_type: type[ResponseDTOType],
        filter_dto_type: type[FilterDTOType],
        entity_id_type: type[EntityIdType],
        not_found_exception: type[DomainException],
        repository: Repository[EntityType, EntityIdType],
        event_publisher: EventPublisher | None = None,
    ):
        """
        Initialize use case scaffold.
        """
        self.entity_name = entity_name
        self.entity_type = entity_type
        self.create_dto_type = create_dto_type
        self.update_dto_type = update_dto_type
        self.response_dto_type = response_dto_type
        self.filter_dto_type = filter_dto_type
        self.entity_id_type = entity_id_type
        self.not_found_exception = not_found_exception
        self.repository = repository
        self.event_publisher = event_publisher

    def create_all_use_cases(self) -> dict[str, Any]:
        """
        Create all use cases.
        """
        return {
            "create": self.create_use_case(),
            "update": self.update_use_case(),
            "get": self.get_use_case(),
            "list": self.list_use_case(),
            "delete": self.delete_use_case(),
        }

    def create_use_case(self) -> Any:
        """
        Create use case.
        """

        class CreateUseCase(
            BaseCRUDUseCase[
                EntityType,
                CreateDTOType,
                UpdateDTOType,
                ResponseDTOType,
                FilterDTOType,
                EntityIdType,
            ],
        ):
            def _create_entity_from_dto(self, dto: CreateDTOType) -> EntityType:
                # Try to find a create method on the entity
                if hasattr(self.entity_type, "create"):
                    entity = self.entity_type.create(dto)
                    if isinstance(entity, tuple):
                        return entity[0]
                    return entity
                # Fallback to constructor
                return self.entity_type(**dto.dict())

            def _update_entity_from_dto(self, entity: EntityType, dto: UpdateDTOType) -> EntityType:
                # Try to find an update method on the entity
                if hasattr(entity, "update"):
                    return entity.update(dto)
                # Fallback to field updates
                for field, value in dto.dict(exclude_unset=True).items():
                    if hasattr(entity, field):
                        setattr(entity, field, value)
                return entity

            def _get_entity_id_from_dto(self, dto: UpdateDTOType) -> EntityIdType:
                # Try to find an ID field
                if hasattr(dto, "id"):
                    return self.entity_id_type(dto.id)
                if hasattr(dto, "entity_id"):
                    return self.entity_id_type(dto.entity_id)
                raise ValueError("Update DTO must have 'id' or 'entity_id' field")

            def _get_not_found_exception(self) -> type[DomainException]:
                return self.not_found_exception

            def _to_dto(self, entity: EntityType) -> ResponseDTOType:
                # Try to find a to_dto method on the entity
                if hasattr(entity, "to_dto"):
                    return entity.to_dto()
                if hasattr(self.response_dto_type, "from_entity"):
                    return self.response_dto_type.from_entity(entity)
                # Fallback to constructor
                return self.response_dto_type(
                    **entity.dict() if hasattr(entity, "dict") else entity.__dict__,
                )

        return CreateUseCase(self.repository, self.event_publisher)

    def update_use_case(self) -> Any:
        """
        Create update use case.
        """
        return self.create_use_case()  # Same implementation

    def get_use_case(self) -> Any:
        """
        Create get use case.
        """
        return self.create_use_case()  # Same implementation

    def list_use_case(self) -> Any:
        """
        Create list use case.
        """
        return self.create_use_case()  # Same implementation

    def delete_use_case(self) -> Any:
        """
        Create delete use case.
        """
        return self.create_use_case()  # Same implementation


class RouteScaffold(
    Generic[EntityType, CreateDTOType, UpdateDTOType, ResponseDTOType, FilterDTOType, EntityIdType],
):
    """Scaffold for generating API routes.

    Creates standard REST API routes with proper error handling, validation, and
    documentation.
    """

    def __init__(
        self,
        entity_name: str,
        use_case_scaffold: UseCaseScaffold[
            EntityType, CreateDTOType, UpdateDTOType, ResponseDTOType, FilterDTOType, EntityIdType,
        ],
    ):
        """
        Initialize route scaffold.
        """
        self.entity_name = entity_name
        self.use_case_scaffold = use_case_scaffold

    def add_routes(self, router: APIRouter, prefix: str = "") -> None:
        """
        Add all routes to the router.
        """
        entity_name_lower = self.entity_name.lower()
        entity_name_plural = f"{entity_name_lower}s"

        # Create dependencies
        dependencies = self.create_dependencies()

        # Create routes
        @router.post(
            f"/{entity_name_plural}",
            response_model=self.use_case_scaffold.response_dto_type,
            status_code=status.HTTP_201_CREATED,
        )
        @crud_route(self.entity_name, "create", status.HTTP_201_CREATED)
        @handle_errors()
        @validate_dto(self.use_case_scaffold.create_dto_type)
        async def create_entity(
            dto: self.use_case_scaffold.create_dto_type,
            use_case: Any = Depends(dependencies["create_use_case"]),
        ) -> self.use_case_scaffold.response_dto_type:
            """
            Create a new {self.entity_name}.
            """
            return await use_case.create(dto)

        @router.get(
            f"/{entity_name_plural}/{{entity_id}}",
            response_model=self.use_case_scaffold.response_dto_type,
        )
        @crud_route(self.entity_name, "get")
        @handle_errors()
        async def get_entity(
            entity_id: str,
            use_case: Any = Depends(dependencies["get_use_case"]),
        ) -> self.use_case_scaffold.response_dto_type:
            """
            Get a {self.entity_name} by ID.
            """
            return await use_case.get(self.use_case_scaffold.entity_id_type(entity_id))

        @router.put(
            f"/{entity_name_plural}/{{entity_id}}",
            response_model=self.use_case_scaffold.response_dto_type,
        )
        @crud_route(self.entity_name, "update")
        @handle_errors()
        @validate_dto(self.use_case_scaffold.update_dto_type)
        async def update_entity(
            entity_id: str,
            dto: self.use_case_scaffold.update_dto_type,
            use_case: Any = Depends(dependencies["update_use_case"]),
        ) -> self.use_case_scaffold.response_dto_type:
            """
            Update a {self.entity_name}.
            """
            # Override entity_id from path
            dto_dict = dto.dict()
            dto_dict["id"] = entity_id
            updated_dto = self.use_case_scaffold.update_dto_type(**dto_dict)
            return await use_case.update(updated_dto)

        @router.delete(
            f"/{entity_name_plural}/{{entity_id}}", status_code=status.HTTP_204_NO_CONTENT,
        )
        @crud_route(self.entity_name, "delete", status.HTTP_204_NO_CONTENT)
        @handle_errors()
        async def delete_entity(
            entity_id: str,
            use_case: Any = Depends(dependencies["delete_use_case"]),
        ) -> None:
            """
            Delete a {self.entity_name}.
            """
            await use_case.delete(self.use_case_scaffold.entity_id_type(entity_id))

        @router.get(
            f"/{entity_name_plural}", response_model=list[self.use_case_scaffold.response_dto_type],
        )
        @crud_route(self.entity_name, "list")
        @handle_errors()
        async def list_entities(
            use_case: Any = Depends(dependencies["list_use_case"]),
            limit: int = 100,
            offset: int = 0,
        ) -> list[self.use_case_scaffold.response_dto_type]:
            """
            List {entity_name_plural} with pagination.
            """
            filter_dto = self.use_case_scaffold.filter_dto_type(limit=limit, offset=offset)
            return await use_case.list(filter_dto)

    def create_dependencies(self) -> dict[str, Any]:
        """
        Create dependency injection functions.
        """
        use_cases = self.use_case_scaffold.create_all_use_cases()

        def get_create_use_case() -> Any:
            return use_cases["create"]

        def get_update_use_case() -> Any:
            return use_cases["update"]

        def get_get_use_case() -> Any:
            return use_cases["get"]

        def get_list_use_case() -> Any:
            return use_cases["list"]

        def get_delete_use_case() -> Any:
            return use_cases["delete"]

        return {
            "create_use_case": get_create_use_case,
            "update_use_case": get_update_use_case,
            "get_use_case": get_get_use_case,
            "list_use_case": get_list_use_case,
            "delete_use_case": get_delete_use_case,
        }


class RepositoryScaffold(Generic[EntityType, EntityIdType]):
    """Scaffold for generating repository implementations.

    Creates standard repository methods with common patterns.
    """

    def __init__(
        self,
        entity_type: type[EntityType],
        entity_id_type: type[EntityIdType],
        base_repository: Repository[EntityType, EntityIdType],
    ):
        """
        Initialize repository scaffold.
        """
        self.entity_type = entity_type
        self.entity_id_type = entity_id_type
        self.base_repository = base_repository

    def create_repository(self) -> Repository[EntityType, EntityIdType]:
        """
        Create a repository with standard methods.
        """
        return self.base_repository  # For now, just return the base repository
