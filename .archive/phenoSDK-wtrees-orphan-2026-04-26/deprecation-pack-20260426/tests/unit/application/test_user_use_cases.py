"""
Unit tests for user use cases.
"""

import pytest

from pheno.application.dtos.user import (
    CreateUserDTO,
    UpdateUserDTO,
    UserFilterDTO,
)
from pheno.domain.exceptions.user import UserAlreadyExistsError, UserNotFoundError


@pytest.mark.unit
@pytest.mark.application
class TestCreateUserUseCase:
    """
    Test CreateUserUseCase.
    """

    @pytest.mark.asyncio
    async def test_create_user_success(
        self, create_user_use_case, user_repository, event_publisher,
    ):
        """
        Test successfully creating a user.
        """
        dto = CreateUserDTO(email="test@example.com", name="Test User")

        result = await create_user_use_case.execute(dto)

        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.is_active is True

        # Verify user was saved
        users = await user_repository.find_all()
        assert len(users) == 1

        # Verify events were published
        events = event_publisher.get_published_events()
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, create_user_use_case):
        """
        Test creating a user with duplicate email raises error.
        """
        dto = CreateUserDTO(email="test@example.com", name="Test User")

        # Create first user
        await create_user_use_case.execute(dto)

        # Try to create duplicate
        with pytest.raises(UserAlreadyExistsError):
            await create_user_use_case.execute(dto)


@pytest.mark.unit
@pytest.mark.application
class TestUpdateUserUseCase:
    """
    Test UpdateUserUseCase.
    """

    @pytest.mark.asyncio
    async def test_update_user_name(self, update_user_use_case, created_user):
        """
        Test updating user name.
        """
        dto = UpdateUserDTO(user_id=created_user.id, name="Updated Name")

        result = await update_user_use_case.execute(dto)

        assert result.name == "Updated Name"
        assert result.email == created_user.email

    @pytest.mark.asyncio
    async def test_update_user_email(self, update_user_use_case, created_user):
        """
        Test updating user email.
        """
        dto = UpdateUserDTO(user_id=created_user.id, email="new@example.com")

        result = await update_user_use_case.execute(dto)

        assert result.email == "new@example.com"
        assert result.name == created_user.name

    @pytest.mark.asyncio
    async def test_update_nonexistent_user(self, update_user_use_case):
        """
        Test updating a nonexistent user raises error.
        """
        dto = UpdateUserDTO(user_id="00000000-0000-0000-0000-000000000000", name="Updated Name")

        with pytest.raises(UserNotFoundError):
            await update_user_use_case.execute(dto)


@pytest.mark.unit
@pytest.mark.application
class TestGetUserUseCase:
    """
    Test GetUserUseCase.
    """

    @pytest.mark.asyncio
    async def test_get_user_success(self, get_user_use_case, created_user):
        """
        Test successfully getting a user.
        """
        result = await get_user_use_case.execute(created_user.id)

        assert result.id == created_user.id
        assert result.email == created_user.email
        assert result.name == created_user.name

    @pytest.mark.asyncio
    async def test_get_nonexistent_user(self, get_user_use_case):
        """
        Test getting a nonexistent user raises error.
        """
        with pytest.raises(UserNotFoundError):
            await get_user_use_case.execute("00000000-0000-0000-0000-000000000000")


@pytest.mark.unit
@pytest.mark.application
class TestListUsersUseCase:
    """
    Test ListUsersUseCase.
    """

    @pytest.mark.asyncio
    async def test_list_users_empty(self, list_users_use_case):
        """
        Test listing users when none exist.
        """
        filter_dto = UserFilterDTO()

        result = await list_users_use_case.execute(filter_dto)

        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_users_with_data(self, list_users_use_case, created_user):
        """
        Test listing users with data.
        """
        filter_dto = UserFilterDTO()

        result = await list_users_use_case.execute(filter_dto)

        assert len(result) == 1
        assert result[0].id == created_user.id

    @pytest.mark.asyncio
    async def test_list_users_pagination(
        self,
        list_users_use_case,
        create_user_use_case,
    ):
        """
        Test listing users with pagination.
        """
        # Create multiple users
        for i in range(5):
            dto = CreateUserDTO(email=f"user{i}@example.com", name=f"User {i}")
            await create_user_use_case.execute(dto)

        # Test limit
        filter_dto = UserFilterDTO(limit=2)
        result = await list_users_use_case.execute(filter_dto)
        assert len(result) == 2

        # Test offset
        filter_dto = UserFilterDTO(limit=2, offset=2)
        result = await list_users_use_case.execute(filter_dto)
        assert len(result) == 2


@pytest.mark.unit
@pytest.mark.application
class TestDeactivateUserUseCase:
    """
    Test DeactivateUserUseCase.
    """

    @pytest.mark.asyncio
    async def test_deactivate_user_success(
        self,
        deactivate_user_use_case,
        created_user,
        event_publisher,
    ):
        """
        Test successfully deactivating a user.
        """
        result = await deactivate_user_use_case.execute(created_user.id)

        assert result.is_active is False

        # Verify event was published
        events = event_publisher.get_published_events()
        assert len(events) > 0

    @pytest.mark.asyncio
    async def test_deactivate_nonexistent_user(self, deactivate_user_use_case):
        """
        Test deactivating a nonexistent user raises error.
        """
        with pytest.raises(UserNotFoundError):
            await deactivate_user_use_case.execute("00000000-0000-0000-0000-000000000000")
