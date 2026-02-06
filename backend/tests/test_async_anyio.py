import pytest
import anyio

@pytest.mark.anyio
async def test_simple_async_anyio():
    """Simple async test with anyio."""
    assert True
    
async def test_simple_async_auto_anyio():
    """Simple async test without marker (auto mode)."""
    assert True
