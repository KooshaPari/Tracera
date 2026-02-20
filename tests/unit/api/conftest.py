"""Configuration for API unit tests."""

import pytest


@pytest.fixture(scope="session")
def event_loop_policy() -> None:
    """Use default event loop policy for async tests."""
    import asyncio

    return asyncio.DefaultEventLoopPolicy()


@pytest.fixture(scope="session")
def test_user() -> None:
    """Create test user for validation tests.

    This fixture provides a test user with admin credentials
    for use in route validation tests.

    Returns:
        dict: Test user credentials with id and email
    """
    return {
        "email": "kooshapari@kooshapari.com",
        "id": "test-admin-user",
        "name": "Test Admin",
        "role": "admin",
        "password_hash": "test-hash-123",
    }


@pytest.fixture
def test_user_token() -> str:
    """Provide test JWT token for authenticated requests.

    Returns:
        str: Test bearer token for Authorization header
    """
    return "test-token-abc123"
