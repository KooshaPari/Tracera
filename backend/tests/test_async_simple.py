import pytest


@pytest.mark.asyncio
async def test_simple_async() -> None:
    """Simple async test."""
    assert True


async def test_simple_async_auto() -> None:
    """Simple async test without marker (auto mode)."""
    assert True
