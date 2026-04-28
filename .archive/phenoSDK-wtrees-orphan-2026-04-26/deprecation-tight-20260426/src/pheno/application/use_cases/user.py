"""
User use cases.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pheno.application.dtos.user import (
    CreateUserDTO,
    UpdateUserDTO,
    UserDTO,
    UserFilterDTO,
)
from pheno.domain.entities.user import User
from pheno.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError

if TYPE_CHECKING:
    from pheno.application.ports.events import EventPublisher
    from pheno.application.ports.repositories import UserRepository


class CreateUserUseCase:
    """
    Use case for creating a new user.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher,
    ):
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    async def execute(self, dto: CreateUserDTO) -> UserDTO:
        """
        Create a new user.
        """
        # Check if user already exists
        email, name = dto.to_domain_params()
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(email.value)

        # Create user entity
        user = User.create(email, name)
        if isinstance(user, tuple):  # legacy factories may return (entity, event)
            user = user[0]

        # Save to repository
        await self.user_repository.save(user)

        # Publish domain events
        for event in user.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        user.clear_events()

        return UserDTO.from_entity(user)


class UpdateUserUseCase:
    """
    Use case for updating a user.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher,
    ):
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    async def execute(self, dto: UpdateUserDTO) -> UserDTO:
        """
        Update a user.
        """
        # Find user
        user_id = dto.get_user_id()
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise UserNotFoundError(str(user_id.value))

        # Update user
        if dto.name:
            user = user.update_name(dto.name)
        if dto.email:
            email = dto.get_email()
            if email:
                user = user.update_email(email)

        # Save to repository
        await self.user_repository.save(user)

        # Publish domain events
        for event in user.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        user.clear_events()

        return UserDTO.from_entity(user)


class GetUserUseCase:
    """
    Use case for getting a user by ID.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str) -> UserDTO:
        """
        Get a user by ID.
        """
        from pheno.domain.value_objects.common import UserId

        user = await self.user_repository.find_by_id(UserId(user_id))
        if not user:
            raise UserNotFoundError(user_id)

        return UserDTO.from_entity(user)


class ListUsersUseCase:
    """
    Use case for listing users.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, filter_dto: UserFilterDTO) -> list[UserDTO]:
        """
        List users with optional filters.
        """
        users = await self.user_repository.find_all(
            limit=filter_dto.limit,
            offset=filter_dto.offset,
        )
        return [UserDTO.from_entity(user) for user in users]


class DeactivateUserUseCase:
    """
    Use case for deactivating a user.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        event_publisher: EventPublisher,
    ):
        self.user_repository = user_repository
        self.event_publisher = event_publisher

    async def execute(self, user_id: str) -> UserDTO:
        """
        Deactivate a user.
        """
        from pheno.domain.value_objects.common import UserId

        # Find user
        user = await self.user_repository.find_by_id(UserId(user_id))
        if not user:
            raise UserNotFoundError(user_id)

        # Deactivate user
        user = user.deactivate()

        # Save to repository
        await self.user_repository.save(user)

        # Publish domain events
        for event in user.domain_events:
            await self.event_publisher.publish(event)

        # Clear domain events
        user.clear_events()

        return UserDTO.from_entity(user)
