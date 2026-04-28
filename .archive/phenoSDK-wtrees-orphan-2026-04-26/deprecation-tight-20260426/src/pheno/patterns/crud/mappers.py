"""CRUD Mappers.

Generic mappers for converting between DTOs, entities, and events. Standardizes data
transformation patterns across the application.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pheno.domain.entities.base import Entity
from pheno.domain.events.base import DomainEvent
from pydantic import BaseModel

logger = get_logger(__name__)

# Type variables
EntityType = TypeVar("EntityType", bound=Entity)
DTOType = TypeVar("DTOType", bound=BaseModel)
EventType = TypeVar("EventType", bound=DomainEvent)


class DTOMapper(ABC, Generic[EntityType, DTOType]):
    """Abstract base class for mapping between entities and DTOs.

    Provides standard patterns for:
    - Entity to DTO conversion
    - DTO to entity conversion
    - Field mapping and validation
    - Nested object handling
    """

    @abstractmethod
    def entity_to_dto(self, entity: EntityType) -> DTOType:
        """
        Convert entity to DTO.
        """

    @abstractmethod
    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convert DTO to entity.
        """

    def entities_to_dtos(self, entities: list[EntityType]) -> list[DTOType]:
        """
        Convert list of entities to DTOs.
        """
        return [self.entity_to_dto(entity) for entity in entities]

    def dtos_to_entities(self, dtos: list[DTOType]) -> list[EntityType]:
        """
        Convert list of DTOs to entities.
        """
        return [self.dto_to_entity(dto) for dto in dtos]

    def update_entity_from_dto(self, entity: EntityType, dto: DTOType) -> EntityType:
        """Update entity from DTO.

        Default implementation updates fields that are present in the DTO. Override for
        custom update logic.
        """
        dto_dict = dto.dict(exclude_unset=True)

        for field, value in dto_dict.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        return entity


class EntityMapper(Generic[EntityType, DTOType]):
    """Generic entity mapper using reflection.

    Automatically maps between entities and DTOs based on field names. Handles common
    patterns like ID conversion and nested objects.
    """

    def __init__(
        self,
        entity_type: type[EntityType],
        dto_type: type[DTOType],
        field_mapping: dict[str, str] | None = None,
        id_field: str = "id",
    ):
        """Initialize entity mapper.

        Args:
            entity_type: Entity class
            dto_type: DTO class
            field_mapping: Optional field name mapping
            id_field: Name of the ID field
        """
        self.entity_type = entity_type
        self.dto_type = dto_type
        self.field_mapping = field_mapping or {}
        self.id_field = id_field

    def entity_to_dto(self, entity: EntityType) -> DTOType:
        """
        Convert entity to DTO.
        """
        # Get entity data
        if hasattr(entity, "dict"):
            entity_data = entity.dict()
        else:
            entity_data = entity.__dict__.copy()

        # Apply field mapping
        dto_data = {}
        for entity_field, value in entity_data.items():
            dto_field = self.field_mapping.get(entity_field, entity_field)
            dto_data[dto_field] = self._convert_value(value)

        return self.dto_type(**dto_data)

    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convert DTO to entity.
        """
        # Get DTO data
        dto_data = dto.dict()

        # Apply reverse field mapping
        entity_data = {}
        for dto_field, value in dto_data.items():
            entity_field = self._get_entity_field(dto_field)
            entity_data[entity_field] = self._convert_value(value)

        return self.entity_type(**entity_data)

    def update_entity_from_dto(self, entity: EntityType, dto: DTOType) -> EntityType:
        """
        Update entity from DTO.
        """
        dto_data = dto.dict(exclude_unset=True)

        for dto_field, value in dto_data.items():
            entity_field = self._get_entity_field(dto_field)
            if hasattr(entity, entity_field):
                setattr(entity, entity_field, self._convert_value(value))

        return entity

    def _get_entity_field(self, dto_field: str) -> str:
        """
        Get entity field name from DTO field name.
        """
        # Reverse lookup in field mapping
        for entity_field, mapped_dto_field in self.field_mapping.items():
            if mapped_dto_field == dto_field:
                return entity_field
        return dto_field

    def _convert_value(self, value: Any) -> Any:
        """
        Convert value for mapping.
        """
        if value is None:
            return None

        # Handle common conversions
        if isinstance(value, str) and value.isdigit():
            return int(value)

        # Handle UUID strings
        if isinstance(value, str) and len(value) == 36 and value.count("-") == 4:
            try:
                from uuid import UUID

                return UUID(value)
            except ValueError:
                pass

        return value


class EventMapper(Generic[EntityType, EventType]):
    """Mapper for converting entities to domain events.

    Provides standard patterns for:
    - Entity to event conversion
    - Event data extraction
    - Event type mapping
    """

    def __init__(
        self,
        entity_type: type[EntityType],
        event_type: type[EventType],
        event_type_mapping: dict[str, str] | None = None,
    ):
        """Initialize event mapper.

        Args:
            entity_type: Entity class
            event_type: Event class
            event_type_mapping: Mapping of operations to event types
        """
        self.entity_type = entity_type
        self.event_type = event_type
        self.event_type_mapping = event_type_mapping or {
            "create": "created",
            "update": "updated",
            "delete": "deleted",
        }

    def entity_to_event(
        self,
        entity: EntityType,
        operation: str,
        event_data: dict[str, Any] | None = None,
    ) -> EventType:
        """Convert entity to domain event.

        Args:
            entity: Entity to convert
            operation: Operation that triggered the event
            event_data: Additional event data

        Returns:
            Domain event
        """
        # Get event type
        event_type = self.event_type_mapping.get(operation, operation)

        # Get entity data
        if hasattr(entity, "dict"):
            entity_data = entity.dict()
        else:
            entity_data = entity.__dict__.copy()

        # Prepare event data
        event_data = event_data or {}
        event_data.update(
            {
                "entity_id": str(entity_data.get("id", "")),
                "entity_type": self.entity_type.__name__,
                "operation": operation,
                "timestamp": entity_data.get("created_at") or entity_data.get("updated_at"),
            },
        )

        # Add entity-specific data
        event_data.update(self._extract_entity_event_data(entity))

        return self.event_type(
            type=event_type,
            data=event_data,
        )

    def _extract_entity_event_data(self, entity: EntityType) -> dict[str, Any]:
        """Extract event-specific data from entity.

        Override in subclasses for custom event data extraction.
        """
        if hasattr(entity, "dict"):
            entity_data = entity.dict()
        else:
            entity_data = entity.__dict__.copy()

        # Include relevant fields for events
        event_data = {}
        for field in ["id", "name", "email", "status", "created_at", "updated_at"]:
            if field in entity_data:
                event_data[field] = entity_data[field]

        return event_data


class CompositeMapper(Generic[EntityType, DTOType, EventType]):
    """Composite mapper that combines DTO and event mapping.

    Provides a single interface for all mapping operations.
    """

    def __init__(
        self,
        entity_type: type[EntityType],
        dto_type: type[DTOType],
        event_type: type[EventType],
        dto_mapper: DTOMapper[EntityType, DTOType] | None = None,
        event_mapper: EventMapper[EntityType, EventType] | None = None,
    ):
        """Initialize composite mapper.

        Args:
            entity_type: Entity class
            dto_type: DTO class
            event_type: Event class
            dto_mapper: Optional custom DTO mapper
            event_mapper: Optional custom event mapper
        """
        self.entity_type = entity_type
        self.dto_type = dto_type
        self.event_type = event_type

        # Use provided mappers or create default ones
        self.dto_mapper = dto_mapper or EntityMapper(entity_type, dto_type)
        self.event_mapper = event_mapper or EventMapper(entity_type, event_type)

    def entity_to_dto(self, entity: EntityType) -> DTOType:
        """
        Convert entity to DTO.
        """
        return self.dto_mapper.entity_to_dto(entity)

    def dto_to_entity(self, dto: DTOType) -> EntityType:
        """
        Convert DTO to entity.
        """
        return self.dto_mapper.dto_to_entity(dto)

    def update_entity_from_dto(self, entity: EntityType, dto: DTOType) -> EntityType:
        """
        Update entity from DTO.
        """
        return self.dto_mapper.update_entity_from_dto(entity, dto)

    def entity_to_event(
        self,
        entity: EntityType,
        operation: str,
        event_data: dict[str, Any] | None = None,
    ) -> EventType:
        """
        Convert entity to event.
        """
        return self.event_mapper.entity_to_event(entity, operation, event_data)

    def entities_to_dtos(self, entities: list[EntityType]) -> list[DTOType]:
        """
        Convert entities to DTOs.
        """
        return self.dto_mapper.entities_to_dtos(entities)

    def dtos_to_entities(self, dtos: list[DTOType]) -> list[EntityType]:
        """
        Convert DTOs to entities.
        """
        return self.dto_mapper.dtos_to_entities(dtos)
