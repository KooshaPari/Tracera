"""
Unit tests for User entity.
"""

import pytest

from pheno.domain.entities import User
from pheno.domain.events import UserCreated, UserDeactivated, UserUpdated
from pheno.domain.exceptions import (
    UserInactiveError,
    ValidationError,
)
from pheno.domain.value_objects import Email, UserId


class TestUserCreation:
    """
    Tests for User creation.
    """

    def test_create_user(self):
        """
        Test creating a new user.
        """
        email = Email("user@example.com")
        user, event = User.create(email=email, name="John Doe")

        assert user.email == email
        assert user.name == "John Doe"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_create_user_emits_event(self):
        """
        Test that user creation emits UserCreated event.
        """
        email = Email("user@example.com")
        user, event = User.create(email=email, name="John Doe")

        assert isinstance(event, UserCreated)
        assert event.user_id == str(user.id)
        assert event.email == str(email)
        assert event.name == "John Doe"

    def test_create_user_with_empty_name_raises_error(self):
        """
        Test that creating user with empty name raises ValidationError.
        """
        email = Email("user@example.com")

        with pytest.raises(ValidationError, match="User name cannot be empty"):
            User.create(email=email, name="")

    def test_create_user_with_whitespace_name_raises_error(self):
        """
        Test that creating user with whitespace name raises ValidationError.
        """
        email = Email("user@example.com")

        with pytest.raises(ValidationError, match="User name cannot be empty"):
            User.create(email=email, name="   ")

    def test_create_user_trims_name(self):
        """
        Test that user creation trims whitespace from name.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="  John Doe  ")

        assert user.name == "John Doe"


class TestUserUpdateName:
    """
    Tests for updating user name.
    """

    def test_update_name(self):
        """
        Test updating user name.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        updated_user = user.update_name("Jane Doe")

        assert updated_user.name == "Jane Doe"
        assert updated_user.email == email
        assert updated_user.id == user.id

    def test_update_name_emits_event(self):
        """
        Test that updating name emits UserUpdated event.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        updated_user = user.update_name("Jane Doe")
        events = updated_user.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, UserUpdated)
        assert event.user_id == str(user.id)
        assert event.field == "name"
        assert event.old_value == "John Doe"
        assert event.new_value == "Jane Doe"

    def test_update_name_with_empty_name_raises_error(self):
        """
        Test that updating to empty name raises ValidationError.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        with pytest.raises(ValidationError, match="User name cannot be empty"):
            user.update_name("")

    def test_update_name_on_inactive_user_raises_error(self):
        """
        Test that updating name on inactive user raises UserInactiveError.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")
        inactive_user = user.deactivate()

        with pytest.raises(UserInactiveError):
            inactive_user.update_name("Jane Doe")

    def test_update_name_trims_whitespace(self):
        """
        Test that updating name trims whitespace.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        updated_user = user.update_name("  Jane Doe  ")

        assert updated_user.name == "Jane Doe"


class TestUserUpdateEmail:
    """
    Tests for updating user email.
    """

    def test_update_email(self):
        """
        Test updating user email.
        """
        old_email = Email("old@example.com")
        new_email = Email("new@example.com")
        user, _ = User.create(email=old_email, name="John Doe")

        updated_user = user.update_email(new_email)

        assert updated_user.email == new_email
        assert updated_user.name == "John Doe"
        assert updated_user.id == user.id

    def test_update_email_emits_event(self):
        """
        Test that updating email emits UserUpdated event.
        """
        old_email = Email("old@example.com")
        new_email = Email("new@example.com")
        user, _ = User.create(email=old_email, name="John Doe")

        updated_user = user.update_email(new_email)
        events = updated_user.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, UserUpdated)
        assert event.field == "email"
        assert event.old_value == str(old_email)
        assert event.new_value == str(new_email)

    def test_update_email_on_inactive_user_raises_error(self):
        """
        Test that updating email on inactive user raises UserInactiveError.
        """
        email = Email("user@example.com")
        new_email = Email("new@example.com")
        user, _ = User.create(email=email, name="John Doe")
        inactive_user = user.deactivate()

        with pytest.raises(UserInactiveError):
            inactive_user.update_email(new_email)


class TestUserDeactivation:
    """
    Tests for user deactivation.
    """

    def test_deactivate_user(self):
        """
        Test deactivating a user.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        deactivated_user = user.deactivate()

        assert deactivated_user.is_active is False
        assert deactivated_user.id == user.id

    def test_deactivate_user_emits_event(self):
        """
        Test that deactivating user emits UserDeactivated event.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        deactivated_user = user.deactivate()
        events = deactivated_user.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, UserDeactivated)
        assert event.user_id == str(user.id)

    def test_deactivate_already_inactive_user_raises_error(self):
        """
        Test that deactivating already inactive user raises ValidationError.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")
        inactive_user = user.deactivate()

        with pytest.raises(ValidationError, match="already inactive"):
            inactive_user.deactivate()


class TestUserActivation:
    """
    Tests for user activation.
    """

    def test_activate_user(self):
        """
        Test activating a user.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")
        inactive_user = user.deactivate()

        activated_user = inactive_user.activate()

        assert activated_user.is_active is True
        assert activated_user.id == user.id

    def test_activate_user_emits_event(self):
        """
        Test that activating user emits UserUpdated event.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")
        inactive_user = user.deactivate()

        activated_user = inactive_user.activate()
        events = activated_user.clear_events()

        assert len(events) == 1
        event = events[0]
        assert isinstance(event, UserUpdated)
        assert event.field == "is_active"
        assert event.old_value is False
        assert event.new_value is True

    def test_activate_already_active_user_raises_error(self):
        """
        Test that activating already active user raises ValidationError.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        with pytest.raises(ValidationError, match="already active"):
            user.activate()


class TestUserImmutability:
    """
    Tests for user immutability.
    """

    def test_user_operations_return_new_instance(self):
        """
        Test that user operations return new instances.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        updated_user = user.update_name("Jane Doe")

        assert user is not updated_user
        assert user.name == "John Doe"
        assert updated_user.name == "Jane Doe"


class TestUserEquality:
    """
    Tests for user equality.
    """

    def test_users_with_same_id_are_equal(self):
        """
        Test that users with same ID are equal.
        """
        user_id = UserId.generate()
        email = Email("user@example.com")

        user1 = User(id=user_id, email=email, name="John Doe")
        user2 = User(id=user_id, email=email, name="Jane Doe")

        assert user1 == user2

    def test_users_with_different_ids_are_not_equal(self):
        """
        Test that users with different IDs are not equal.
        """
        email = Email("user@example.com")
        user1, _ = User.create(email=email, name="John Doe")
        user2, _ = User.create(email=email, name="John Doe")

        assert user1 != user2


class TestUserStringRepresentation:
    """
    Tests for user string representation.
    """

    def test_user_str(self):
        """
        Test user string representation.
        """
        email = Email("user@example.com")
        user, _ = User.create(email=email, name="John Doe")

        user_str = str(user)

        assert "User" in user_str
        assert str(user.id) in user_str
        assert str(email) in user_str
        assert "John Doe" in user_str
