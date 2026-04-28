"""CRUD Decorators.

Decorators for standardizing use cases, routes, validation, error handling, and event
publishing.
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError

from pheno.domain.exceptions.base import DomainException
from pheno.observability.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from pheno.application.ports.events import EventPublisher

logger = get_logger(__name__)

# Type variables
T = TypeVar("T")
UseCaseType = TypeVar("UseCaseType")
DTOType = TypeVar("DTOType", bound=BaseModel)


def use_case(
    entity_name: str,
    operation: str,
    log_execution: bool = True,
    publish_events: bool = True,
):
    """Decorator for use case methods.

    Provides:
    - Execution logging
    - Error handling
    - Event publishing
    - Performance monitoring

    Args:
        entity_name: Name of the entity (e.g., "User", "Deployment")
        operation: Operation name (e.g., "create", "update", "get")
        log_execution: Whether to log execution details
        publish_events: Whether to publish events
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            execution_id = str(uuid4())
            start_time = asyncio.get_event_loop().time()

            if log_execution:
                logger.info(
                    f"Executing {entity_name} {operation}",
                    extra={
                        "execution_id": execution_id,
                        "entity": entity_name,
                        "operation": operation,
                        "args": str(args)[:100] if args else None,
                        "kwargs": str(kwargs)[:100] if kwargs else None,
                    },
                )

            try:
                result = await func(*args, **kwargs)

                if log_execution:
                    duration = asyncio.get_event_loop().time() - start_time
                    logger.info(
                        f"Completed {entity_name} {operation}",
                        extra={
                            "execution_id": execution_id,
                            "entity": entity_name,
                            "operation": operation,
                            "duration": duration,
                            "success": True,
                        },
                    )

                return result

            except DomainException as e:
                if log_execution:
                    duration = asyncio.get_event_loop().time() - start_time
                    logger.warning(
                        f"Domain error in {entity_name} {operation}",
                        extra={
                            "execution_id": execution_id,
                            "entity": entity_name,
                            "operation": operation,
                            "duration": duration,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )
                raise

            except Exception as e:
                if log_execution:
                    duration = asyncio.get_event_loop().time() - start_time
                    logger.exception(
                        f"Unexpected error in {entity_name} {operation}",
                        extra={
                            "execution_id": execution_id,
                            "entity": entity_name,
                            "operation": operation,
                            "duration": duration,
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )
                raise

        return wrapper

    return decorator


def crud_route(
    entity_name: str,
    operation: str,
    success_status: int = status.HTTP_200_OK,
    error_mapping: dict[type[Exception], int] | None = None,
):
    """Decorator for CRUD API routes.

    Provides:
    - Standard error handling
    - HTTP status code mapping
    - Request/response logging
    - OpenAPI documentation

    Args:
        entity_name: Name of the entity
        operation: Operation name
        success_status: HTTP status code for success
        error_mapping: Mapping of exceptions to HTTP status codes
    """
    if error_mapping is None:
        error_mapping = {
            ValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
            DomainException: status.HTTP_400_BAD_REQUEST,
        }

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            request_id = str(uuid4())
            start_time = asyncio.get_event_loop().time()

            logger.info(
                f"API request: {entity_name} {operation}",
                extra={
                    "request_id": request_id,
                    "entity": entity_name,
                    "operation": operation,
                    "endpoint": func.__name__,
                },
            )

            try:
                result = await func(*args, **kwargs)

                duration = asyncio.get_event_loop().time() - start_time
                logger.info(
                    f"API response: {entity_name} {operation}",
                    extra={
                        "request_id": request_id,
                        "entity": entity_name,
                        "operation": operation,
                        "duration": duration,
                        "status_code": success_status,
                    },
                )

                return result

            except Exception as e:
                duration = asyncio.get_event_loop().time() - start_time

                # Map exception to HTTP status code
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                for exc_type, code in error_mapping.items():
                    if isinstance(e, exc_type):
                        status_code = code
                        break

                logger.exception(
                    f"API error: {entity_name} {operation}",
                    extra={
                        "request_id": request_id,
                        "entity": entity_name,
                        "operation": operation,
                        "duration": duration,
                        "status_code": status_code,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                )

                raise HTTPException(
                    status_code=status_code,
                    detail=str(e),
                )

        return wrapper

    return decorator


def validate_dto(dto_type: type[DTOType], validate_business_rules: bool = True):
    """Decorator for DTO validation.

    Provides:
    - Pydantic validation
    - Business rule validation
    - Validation error handling

    Args:
        dto_type: DTO type to validate
        validate_business_rules: Whether to validate business rules
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            dto_param, dto_value = _find_dto_parameter(func, dto_type, args, kwargs)

            if dto_value is not None:
                validated_dto = _validate_dto_instance(dto_value, dto_type)
                validated_dto = _validate_business_rules(validated_dto, validate_business_rules)
                args, kwargs = _replace_dto_in_arguments(
                    args, kwargs, dto_param, validated_dto, func,
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def _find_dto_parameter(
    func: Callable, dto_type: type, args: tuple, kwargs: dict,
) -> tuple[str | None, Any | None]:
    """
    Find DTO parameter in function signature and get its value.
    """
    sig = inspect.signature(func)

    # Try keyword arguments first
    for param_name, param in sig.parameters.items():
        if param.annotation == dto_type:
            dto_value = kwargs.get(param_name)
            if dto_value is not None:
                return param_name, dto_value

    # Try positional arguments
    for i, (param_name, param) in enumerate(sig.parameters.items()):
        if param.annotation == dto_type and i < len(args):
            return param_name, args[i]

    return None, None


def _validate_dto_instance(dto_value: Any, dto_type: type) -> Any:
    """
    Validate and convert DTO instance.
    """
    if isinstance(dto_value, dto_type):
        return dto_value

    try:
        if hasattr(dto_value, "dict"):
            return dto_type(**dto_value.dict())
        return dto_type(**dto_value)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )


def _validate_business_rules(dto_value: Any, validate_business_rules: bool) -> Any:
    """
    Validate business rules if requested.
    """
    if not validate_business_rules or not hasattr(dto_value, "validate_business_rules"):
        return dto_value

    try:
        dto_value.validate_business_rules()
        return dto_value
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Business rule validation error: {e}",
        )


def _replace_dto_in_arguments(
    args: tuple, kwargs: dict, dto_param: str, validated_dto: Any, func: Callable,
) -> tuple[tuple, dict]:
    """
    Replace DTO in function arguments.
    """
    if dto_param in kwargs:
        kwargs[dto_param] = validated_dto
        return args, kwargs

    # Replace in positional arguments
    sig = inspect.signature(func)
    for i, (param_name, _param) in enumerate(sig.parameters.items()):
        if param_name == dto_param:
            args_list = list(args)
            args_list[i] = validated_dto
            return tuple(args_list), kwargs

    return args, kwargs


def handle_errors(
    error_mapping: dict[type[Exception], Callable[[Exception], HTTPException]] | None = None,
    default_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
):
    """Decorator for error handling.

    Provides:
    - Custom error mapping
    - Standard error responses
    - Error logging

    Args:
        error_mapping: Mapping of exceptions to HTTP exceptions
        default_status: Default HTTP status code
    """
    if error_mapping is None:
        error_mapping = {
            ValidationError: lambda e: HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Validation error: {e}",
            ),
            DomainException: lambda e: HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            ),
        }

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                # Find matching error handler
                for exc_type, handler in error_mapping.items():
                    if isinstance(e, exc_type):
                        raise handler(e)

                # Default error handling
                logger.exception(
                    f"Unhandled error in {func.__name__}",
                    extra={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "args": str(args)[:100] if args else None,
                        "kwargs": str(kwargs)[:100] if kwargs else None,
                    },
                )

                raise HTTPException(
                    status_code=default_status,
                    detail="Internal server error",
                )

        return wrapper

    return decorator


def publish_events(
    event_publisher: EventPublisher | None = None,
    event_types: list[str] | None = None,
):
    """Decorator for event publishing.

    Provides:
    - Automatic event publishing
    - Event type filtering
    - Event publishing error handling

    Args:
        event_publisher: Event publisher instance
        event_types: List of event types to publish (None for all)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            result = await func(*args, **kwargs)

            # Publish events if publisher is available
            if event_publisher:
                try:
                    # Look for entities with domain events in the result
                    entities_to_publish = []

                    if hasattr(result, "domain_events"):
                        entities_to_publish.append(result)
                    elif isinstance(result, list):
                        for item in result:
                            if hasattr(item, "domain_events"):
                                entities_to_publish.append(item)

                    # Publish events
                    for entity in entities_to_publish:
                        if hasattr(entity, "domain_events"):
                            for event in entity.domain_events:
                                if event_types is None or event.type in event_types:
                                    await event_publisher.publish(event)
                            entity.clear_events()

                except Exception as e:
                    logger.exception(
                        f"Error publishing events in {func.__name__}",
                        extra={
                            "error": str(e),
                            "error_type": type(e).__name__,
                        },
                    )

            return result

        return wrapper

    return decorator
