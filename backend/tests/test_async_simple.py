import pytest

@pytest.mark.asyncio
async def test_simple_async():
    """Simple async test."""
    assert True

async def test_simple_async_auto():
    """Simple async test without marker (auto mode)."""
    assert True
