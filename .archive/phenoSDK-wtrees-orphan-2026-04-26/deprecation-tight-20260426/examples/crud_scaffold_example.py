"""CRUD Scaffold Example.

Demonstrates how to use the CRUD scaffold library to create standardized use cases and
routes with minimal boilerplate.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI

from pheno.application.dtos.user import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
    UserFilterDTO,
)
from pheno.application.ports.events import EventPublisher
from pheno.application.ports.repositories import UserRepository
from pheno.domain.entities.user import User
from pheno.domain.exceptions.user import UserNotFoundError
from pheno.domain.value_objects.common import UserId
from pheno.patterns.crud import CompositeMapper, CRUDScaffold, EntityMapper
from pheno.patterns.crud.decorators import (
    crud_route,
    handle_errors,
    use_case,
    validate_dto,
)


# Example: Refactored User Use Cases using CRUD Scaffold
class UserCRUDScaffold:
    """
    Example of using CRUD scaffold for User entity.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher | None = None,
    ):
        """
        Initialize user CRUD scaffold.
        """
        self.user_repository = user_repository
        self.event_publisher = event_publisher

        # Create CRUD scaffold
        self.scaffold = CRUDScaffold(
            entity_name="User",
            entity_type=User,
            create_dto_type=CreateUserDTO,
            update_dto_type=UpdateUserDTO,
            response_dto_type=UserDTO,
            filter_dto_type=UserFilterDTO,
            entity_id_type=UserId,
            not_found_exception=UserNotFoundError,
            repository=user_repository,
            event_publisher=event_publisher,
        )

        # Create mappers
        self.mapper = CompositeMapper(
            entity_type=User,
            dto_type=UserDTO,
            event_type=None,  # Will be set when events are implemented
        )

    def create_use_cases(self):
        """
        Create all user use cases.
        """
        return self.scaffold.create_use_cases()

    def create_routes(self, router: APIRouter):
        """
        Create all user routes.
        """
        self.scaffold.create_routes(router, prefix="/api/v1")

    def create_dependencies(self):
        """
        Create dependency injection functions.
        """
        return self.scaffold.create_dependencies()


# Example: Custom Use Case with Decorators
class CustomUserUseCase:
    """
    Example of custom use case with decorators.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher | None = None,
    ):
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    @use_case("User", "create", log_execution=True, publish_events=True)
    @validate_dto(CreateUserDTO, validate_business_rules=True)
    @handle_errors()
    async def create_user(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a new user with custom logic.
        """
        # Custom business logic
        if dto.email and "@" not in dto.email:
            raise ValueError("Invalid email format")

        # Create user entity
        user = User.create(dto.email, dto.name)
        if isinstance(user, tuple):
            user = user[0]

        # Save to repository
        await self.user_repository.save(user)

        # Publish events
        if self.event_publisher and hasattr(user, "domain_events"):
            for event in user.domain_events:
                await self.event_publisher.publish(event)
            user.clear_events()

        return UserDTO.from_entity(user)

    @use_case("User", "get", log_execution=True)
    @handle_errors()
    async def get_user(self, user_id: str) -> UserDTO:
        """
        Get user by ID with custom logic.
        """
        user = await self.user_repository.find_by_id(UserId(user_id))
        if not user:
            raise UserNotFoundError(user_id)

        # Custom logic (e.g., add audit trail)
        # ...

        return UserDTO.from_entity(user)


# Example: Custom Route with Decorators
class CustomUserRoutes:
    """
    Example of custom routes with decorators.
    """

    def __init__(self, use_case: CustomUserUseCase):
        self.use_case = use_case

    def add_routes(self, router: APIRouter):
        """
        Add custom user routes.
        """

        @router.post("/users/custom", response_model=UserDTO, status_code=201)
        @crud_route("User", "create", 201)
        @handle_errors()
        @validate_dto(CreateUserDTO)
        async def create_user_custom(dto: CreateUserDTO) -> UserDTO:
            """
            Create user with custom endpoint.
            """
            return await self.use_case.create_user(dto)

        @router.get("/users/{user_id}/custom", response_model=UserDTO)
        @crud_route("User", "get")
        @handle_errors()
        async def get_user_custom(user_id: str) -> UserDTO:
            """
            Get user with custom endpoint.
            """
            return await self.use_case.get_user(user_id)


# Example: Complete Application Setup
def create_user_app(
    user_repository: UserRepository,
    event_publisher: EventPublisher | None = None,
) -> FastAPI:
    """
    Create FastAPI application with user CRUD operations.
    """

    app = FastAPI(title="User API", version="1.0.0")
    router = APIRouter()

    # Create CRUD scaffold
    user_crud = UserCRUDScaffold(user_repository, event_publisher)

    # Add scaffold routes
    user_crud.create_routes(router)

    # Create custom use case and routes
    custom_use_case = CustomUserUseCase(user_repository, event_publisher)
    custom_routes = CustomUserRoutes(custom_use_case)
    custom_routes.add_routes(router)

    # Include router in app
    app.include_router(router)

    return app


# Example: Using Mappers
class UserMapperExample:
    """
    Example of using mappers for data transformation.
    """

    def __init__(self):
        self.mapper = EntityMapper(
            entity_type=User,
            dto_type=UserDTO,
            field_mapping={
                "id": "user_id",
                "email": "email_address",
                "name": "full_name",
            },
        )

    def convert_user_to_dto(self, user: User) -> UserDTO:
        """
        Convert user entity to DTO.
        """
        return self.mapper.entity_to_dto(user)

    def convert_dto_to_user(self, dto: UserDTO) -> User:
        """
        Convert DTO to user entity.
        """
        return self.mapper.dto_to_entity(dto)

    def update_user_from_dto(self, user: User, dto: UserDTO) -> User:
        """
        Update user from DTO.
        """
        return self.mapper.update_entity_from_dto(user, dto)


# Example: Using Validators
class UserValidatorExample:
    """
    Example of using validators for data validation.
    """

    def __init__(self):
        from pheno.patterns.crud.validators import CompositeValidator, FieldValidator

        self.validator = CompositeValidator()

        # Add field validators
        self.validator.add_dto_validator(FieldValidator())

    async def validate_user_creation(self, dto: CreateUserDTO) -> None:
        """
        Validate user creation.
        """
        await self.validator.validate(
            dto,
            context={"operation": "create"},
            validate_dto=True,
            validate_business_rules=True,
        )


if __name__ == "__main__":
    # Example usage
    print("CRUD Scaffold Example")
    print("====================")
    print()
    print("This example demonstrates:")
    print("1. Using CRUD scaffold for standard operations")
    print("2. Custom use cases with decorators")
    print("3. Custom routes with error handling")
    print("4. Data mappers for transformation")
    print("5. Validators for data validation")
    print()
    print("See the code for implementation details.")
