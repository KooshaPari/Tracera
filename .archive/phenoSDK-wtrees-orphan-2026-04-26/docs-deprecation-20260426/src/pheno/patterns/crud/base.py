"""Base CRUD Use Cases.

Generic base classes that standardize common CRUD patterns across use cases, reducing
boilerplate and ensuring consistency.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from pheno.domain.entities.base import Entity

if TYPE_CHECKING:
    import builtins

    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import Repository
    from pheno.domain.exceptions.base import DomainException

# Type variables
EntityType = TypeVar("EntityType", bound=Entity)
CreateDTOType = TypeVar("CreateDTOType")
UpdateDTOType = TypeVar("UpdateDTOType")
ResponseDTOType = TypeVar("ResponseDTOType")
FilterDTOType = TypeVar("FilterDTOType")
EntityIdType = TypeVar("EntityIdType")


class BaseUseCase(ABC, Generic[EntityType, ResponseDTOType]):
    """Base use case with common functionality.

    Provides standard patterns for:
    - Entity retrieval and validation
    - Event publishing
    - Error handling
    - DTO conversion
    """

    def __init__(
        self,
        repository: Repository[EntityType, EntityIdType],
        event_publisher: EventPublisher | None = None,
    ):
        """Initialize base use case.

        Args:
            repository: Repository for entity access
            event_publisher: Optional event publisher
        """
        self.repository = repository
        self.event_publisher = event_publisher

    async def _find_entity(
        self,
        entity_id: EntityIdType,
        not_found_exception: type[DomainException],
    ) -> EntityType:
        """Find entity by ID, raising exception if not found.

        Args:
            entity_id: Entity ID
            not_found_exception: Exception to raise if not found

        Returns:
            Found entity

        Raises:
            DomainException: If entity not found
        """
        entity = await self.repository.find_by_id(entity_id)
        if not entity:
            raise not_found_exception(str(entity_id))
        return entity

    async def _publish_events(self, entity: EntityType) -> None:
        """Publish domain events for an entity.

        Args:
            entity: Entity with domain events
        """
        if self.event_publisher and hasattr(entity, "domain_events"):
            for event in entity.domain_events:
                await self.event_publisher.publish(event)
            entity.clear_events()

    async def _save_and_publish(
        self,
        entity: EntityType,
        publish_events: bool = True,
    ) -> EntityType:
        """Save entity and publish events.

        Args:
            entity: Entity to save
            publish_events: Whether to publish events

        Returns:
            Saved entity
        """
        # Save entity
        saved_entity = await self.repository.save(entity)

        # Publish events if requested
        if publish_events:
            await self._publish_events(saved_entity)

        return saved_entity


class BaseCreateUseCase(
    BaseUseCase[EntityType, ResponseDTOType],
    Generic[EntityType, CreateDTOType, ResponseDTOType, EntityIdType],
):
    """
    Base use case for creating entities.
    """

    @abstractmethod
    async def execute(self, dto: CreateDTOType) -> ResponseDTOType:
        """
        Execute the create use case.
        """

    async def _create_entity(
        self,
        dto: CreateDTOType,
        entity_factory: callable,
    ) -> EntityType:
        """Create entity from DTO using factory.

        Args:
            dto: Create DTO
            entity_factory: Function to create entity from DTO

        Returns:
            Created entity
        """
        entity = entity_factory(dto)

        # Handle legacy factories that return (entity, event)
        if isinstance(entity, tuple):
            entity = entity[0]

        return entity


class BaseUpdateUseCase(
    BaseUseCase[EntityType, ResponseDTOType],
    Generic[EntityType, UpdateDTOType, ResponseDTOType, EntityIdType],
):
    """
    Base use case for updating entities.
    """

    @abstractmethod
    async def execute(self, dto: UpdateDTOType) -> ResponseDTOType:
        """
        Execute the update use case.
        """

    async def _update_entity(
        self,
        entity: EntityType,
        dto: UpdateDTOType,
        update_method: callable,
    ) -> EntityType:
        """Update entity using DTO and update method.

        Args:
            entity: Entity to update
            dto: Update DTO
            update_method: Method to update entity

        Returns:
            Updated entity
        """
        return update_method(entity, dto)


class BaseGetUseCase(
    BaseUseCase[EntityType, ResponseDTOType],
    Generic[EntityType, ResponseDTOType, EntityIdType],
):
    """
    Base use case for getting entities by ID.
    """

    @abstractmethod
    async def execute(self, entity_id: EntityIdType) -> ResponseDTOType:
        """
        Execute the get use case.
        """


class BaseListUseCase(
    BaseUseCase[EntityType, list[ResponseDTOType]],
    Generic[EntityType, ResponseDTOType, FilterDTOType],
):
    """
    Base use case for listing entities.
    """

    @abstractmethod
    async def execute(self, filter_dto: FilterDTOType) -> list[ResponseDTOType]:
        """
        Execute the list use case.
        """


class BaseDeleteUseCase(
    BaseUseCase[EntityType, ResponseDTOType],
    Generic[EntityType, ResponseDTOType, EntityIdType],
):
    """
    Base use case for deleting entities.
    """

    @abstractmethod
    async def execute(self, entity_id: EntityIdType) -> ResponseDTOType:
        """
        Execute the delete use case.
        """


class BaseActionUseCase(
    BaseUseCase[EntityType, ResponseDTOType],
    Generic[EntityType, ResponseDTOType, EntityIdType],
):
    """
    Base use case for entity actions (start, stop, complete, etc.).
    """

    @abstractmethod
    async def execute(self, entity_id: EntityIdType, *args, **kwargs) -> ResponseDTOType:
        """
        Execute the action use case.
        """

    async def _execute_action(
        self,
        entity_id: EntityIdType,
        action_method: callable,
        not_found_exception: type[DomainException],
        *args,
        **kwargs,
    ) -> ResponseDTOType:
        """Execute action on entity.

        Args:
            entity_id: Entity ID
            action_method: Method to execute on entity
            not_found_exception: Exception to raise if not found
            *args: Additional arguments for action method
            **kwargs: Additional keyword arguments for action method

        Returns:
            Action result
        """
        # Find entity
        entity = await self._find_entity(entity_id, not_found_exception)

        # Execute action
        if args or kwargs:
            updated_entity = action_method(entity, *args, **kwargs)
        else:
            updated_entity = action_method(entity)

        # Save and publish events
        saved_entity = await self._save_and_publish(updated_entity)

        # Convert to DTO
        return self._to_dto(saved_entity)

    def _to_dto(self, entity: EntityType) -> ResponseDTOType:
        """Convert entity to DTO.

        Override in subclasses.
        """
        if hasattr(entity, "to_dto"):
            return entity.to_dto()
        raise NotImplementedError("_to_dto method must be implemented")


class BaseCRUDUseCase(
    BaseCreateUseCase[EntityType, CreateDTOType, ResponseDTOType, EntityIdType],
    BaseUpdateUseCase[EntityType, UpdateDTOType, ResponseDTOType, EntityIdType],
    BaseGetUseCase[EntityType, ResponseDTOType, EntityIdType],
    BaseListUseCase[EntityType, ResponseDTOType, FilterDTOType],
    BaseDeleteUseCase[EntityType, ResponseDTOType, EntityIdType],
    Generic[EntityType, CreateDTOType, UpdateDTOType, ResponseDTOType, FilterDTOType, EntityIdType],
):
    """Complete CRUD use case with all operations.

    Combines create, update, get, list, and delete operations into a single use case
    class.
    """

    # Create operation
    async def create(self, dto: CreateDTOType) -> ResponseDTOType:
        """
        Create entity from DTO.
        """
        entity = await self._create_entity(dto, self._create_entity_from_dto)
        saved_entity = await self._save_and_publish(entity)
        return self._to_dto(saved_entity)

    # Update operation
    async def update(self, dto: UpdateDTOType) -> ResponseDTOType:
        """
        Update entity from DTO.
        """
        entity_id = self._get_entity_id_from_dto(dto)
        entity = await self._find_entity(entity_id, self._get_not_found_exception())
        updated_entity = await self._update_entity(entity, dto, self._update_entity_from_dto)
        saved_entity = await self._save_and_publish(updated_entity)
        return self._to_dto(saved_entity)

    # Get operation
    async def get(self, entity_id: EntityIdType) -> ResponseDTOType:
        """
        Get entity by ID.
        """
        entity = await self._find_entity(entity_id, self._get_not_found_exception())
        return self._to_dto(entity)

    # List operation
    async def list(self, filter_dto: FilterDTOType) -> builtins.list[ResponseDTOType]:
        """
        List entities with filters.
        """
        entities = await self._find_entities(filter_dto)
        return [self._to_dto(entity) for entity in entities]

    # Delete operation
    async def delete(self, entity_id: EntityIdType) -> ResponseDTOType:
        """
        Delete entity by ID.
        """
        entity = await self._find_entity(entity_id, self._get_not_found_exception())
        deleted_entity = await self._delete_entity(entity)
        return self._to_dto(deleted_entity)

    # Abstract methods to be implemented by subclasses
    @abstractmethod
    def _create_entity_from_dto(self, dto: CreateDTOType) -> EntityType:
        """
        Create entity from create DTO.
        """

    @abstractmethod
    def _update_entity_from_dto(self, entity: EntityType, dto: UpdateDTOType) -> EntityType:
        """
        Update entity from update DTO.
        """

    @abstractmethod
    def _get_entity_id_from_dto(self, dto: UpdateDTOType) -> EntityIdType:
        """
        Get entity ID from update DTO.
        """

    @abstractmethod
    def _get_not_found_exception(self) -> type[DomainException]:
        """
        Get the not found exception for this entity type.
        """

    @abstractmethod
    def _to_dto(self, entity: EntityType) -> ResponseDTOType:
        """
        Convert entity to response DTO.
        """

    async def _find_entities(self, filter_dto: FilterDTOType) -> builtins.list[EntityType]:
        """
        Find entities with filters.
        """
        # Default implementation - override in subclasses
        return await self.repository.find_all()

    async def _delete_entity(self, entity: EntityType) -> EntityType:
        """Delete entity.

        Override in subclasses for soft delete.
        """
        await self.repository.delete(entity)
        return entity
