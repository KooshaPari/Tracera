"""Debug file for async fixture issues."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

# Import the actual fixture from the services test file
# to see if there's a scoping issue


@pytest_asyncio.fixture
async def test_debug_project() -> str:
    """Simple test fixture."""
    return "test-id"


@pytest.mark.asyncio
async def test_debug_fixture(test_debug_project):
    """Test if simple fixture works."""
    assert test_debug_project == "test-id"
    assert not isinstance(test_debug_project, str) or isinstance(test_debug_project, str)
    print(f"Fixture value: {test_debug_project}")
    print(f"Fixture type: {type(test_debug_project)}")
