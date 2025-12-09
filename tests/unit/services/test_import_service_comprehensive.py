"""
Comprehensive tests for ImportService.

Tests all methods: import_from_json, import_items_from_csv, validate_import_data.

Coverage target: 85%+
"""

import json
import pytest
from unittest.mock import Mock, AsyncMock, patch

from tracertm.services.import_service import ImportService


class TestImportFromJson:
    """Test import_from_json method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = ImportService(session)
        service.projects = AsyncMock()
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_import_creates_project_when_not_exists(self, service):
        """Test import creates project when it doesn't exist."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=None)
        service.projects.create = AsyncMock(return_value=project)

        json_data = json.dumps({
            "project": {"name": "New Project", "description": "Test"},
            "items": [],
            "links": [],
        })

        result = await service.import_from_json(json_data)

        service.projects.create.assert_called_once()
        assert result["project_id"] == "proj-1"

    @pytest.mark.asyncio
    async def test_import_uses_existing_project(self, service):
        """Test import uses existing project."""
        project = Mock()
        project.id = "existing-proj"
        service.projects.get_by_name = AsyncMock(return_value=project)

        json_data = json.dumps({
            "project": {"name": "Existing Project"},
            "items": [],
            "links": [],
        })

        result = await service.import_from_json(json_data)

        service.projects.create.assert_not_called()
        assert result["project_id"] == "existing-proj"

    @pytest.mark.asyncio
    async def test_import_creates_items(self, service):
        """Test import creates items."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=project)

        item1 = Mock()
        item1.id = "new-item-1"
        item2 = Mock()
        item2.id = "new-item-2"
        service.items.create = AsyncMock(side_effect=[item1, item2])

        json_data = json.dumps({
            "project": {"name": "Project"},
            "items": [
                {"id": "old-1", "title": "Item 1", "view": "REQ", "type": "requirement"},
                {"id": "old-2", "title": "Item 2", "view": "DESIGN", "type": "design"},
            ],
            "links": [],
        })

        result = await service.import_from_json(json_data)

        assert result["items_imported"] == 2
        assert service.items.create.call_count == 2

    @pytest.mark.asyncio
    async def test_import_creates_links(self, service):
        """Test import creates links."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=project)

        item1 = Mock()
        item1.id = "new-1"
        item2 = Mock()
        item2.id = "new-2"
        service.items.create = AsyncMock(side_effect=[item1, item2])

        json_data = json.dumps({
            "project": {"name": "Project"},
            "items": [
                {"id": "orig-1", "title": "Item 1", "view": "REQ"},
                {"id": "orig-2", "title": "Item 2", "view": "DESIGN"},
            ],
            "links": [
                {"source_id": "orig-1", "target_id": "orig-2", "type": "traces_to"},
            ],
        })

        result = await service.import_from_json(json_data)

        assert result["links_imported"] == 1
        service.links.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_import_skips_links_with_missing_items(self, service):
        """Test import skips links when item not found."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=project)

        item1 = Mock()
        item1.id = "new-1"
        service.items.create = AsyncMock(return_value=item1)

        json_data = json.dumps({
            "project": {"name": "Project"},
            "items": [
                {"id": "orig-1", "title": "Item 1", "view": "REQ"},
            ],
            "links": [
                {"source_id": "orig-1", "target_id": "missing", "type": "traces_to"},
            ],
        })

        await service.import_from_json(json_data)

        service.links.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_import_uses_default_link_type(self, service):
        """Test import uses default link type."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=project)

        item1 = Mock()
        item1.id = "new-1"
        item2 = Mock()
        item2.id = "new-2"
        service.items.create = AsyncMock(side_effect=[item1, item2])

        json_data = json.dumps({
            "project": {"name": "Project"},
            "items": [
                {"id": "orig-1", "title": "Item 1", "view": "REQ"},
                {"id": "orig-2", "title": "Item 2", "view": "DESIGN"},
            ],
            "links": [
                {"source_id": "orig-1", "target_id": "orig-2"},  # No type
            ],
        })

        await service.import_from_json(json_data)

        call_kwargs = service.links.create.call_args.kwargs
        assert call_kwargs["link_type"] == "relates_to"

    @pytest.mark.asyncio
    async def test_import_passes_item_fields(self, service):
        """Test import passes all item fields."""
        project = Mock()
        project.id = "proj-1"
        service.projects.get_by_name = AsyncMock(return_value=project)

        item = Mock()
        item.id = "new-1"
        service.items.create = AsyncMock(return_value=item)

        json_data = json.dumps({
            "project": {"name": "Project"},
            "items": [
                {
                    "id": "orig-1",
                    "title": "Item Title",
                    "view": "REQ",
                    "type": "requirement",
                    "status": "approved",
                    "description": "Description text",
                },
            ],
            "links": [],
        })

        await service.import_from_json(json_data)

        call_kwargs = service.items.create.call_args.kwargs
        assert call_kwargs["title"] == "Item Title"
        assert call_kwargs["view"] == "REQ"
        assert call_kwargs["item_type"] == "requirement"
        assert call_kwargs["status"] == "approved"
        assert call_kwargs["description"] == "Description text"


class TestImportItemsFromCsv:
    """Test import_items_from_csv method."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked repositories."""
        session = AsyncMock()
        service = ImportService(session)
        service.projects = AsyncMock()
        service.items = AsyncMock()
        service.links = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_import_csv_basic(self, service):
        """Test basic CSV import."""
        item = Mock()
        item.id = "new-1"
        service.items.create = AsyncMock(return_value=item)

        csv_data = """Title,View,Type,Status,Description
Item 1,REQ,requirement,draft,First item
Item 2,DESIGN,design,approved,Second item"""

        result = await service.import_items_from_csv("proj-1", csv_data)

        assert result["items_imported"] == 2
        assert service.items.create.call_count == 2

    @pytest.mark.asyncio
    async def test_import_csv_passes_fields(self, service):
        """Test CSV import passes correct fields."""
        item = Mock()
        service.items.create = AsyncMock(return_value=item)

        csv_data = """Title,View,Type,Status,Description
My Title,TEST,test_case,active,Test description"""

        await service.import_items_from_csv("proj-1", csv_data)

        call_kwargs = service.items.create.call_args.kwargs
        assert call_kwargs["project_id"] == "proj-1"
        assert call_kwargs["title"] == "My Title"
        assert call_kwargs["view"] == "TEST"
        assert call_kwargs["item_type"] == "test_case"
        assert call_kwargs["status"] == "active"
        assert call_kwargs["description"] == "Test description"

    @pytest.mark.asyncio
    async def test_import_csv_empty(self, service):
        """Test CSV import with empty data."""
        csv_data = """Title,View,Type,Status,Description"""

        result = await service.import_items_from_csv("proj-1", csv_data)

        assert result["items_imported"] == 0
        service.items.create.assert_not_called()


class TestValidateImportData:
    """Test validate_import_data method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        session = AsyncMock()
        return ImportService(session)

    @pytest.mark.asyncio
    async def test_validate_invalid_json(self, service):
        """Test validation with invalid JSON."""
        result = await service.validate_import_data("not valid json")

        assert len(result) == 1
        assert "Invalid JSON" in result[0]

    @pytest.mark.asyncio
    async def test_validate_missing_project(self, service):
        """Test validation with missing project."""
        json_data = json.dumps({"items": [], "links": []})

        result = await service.validate_import_data(json_data)

        assert "Missing 'project' section" in result

    @pytest.mark.asyncio
    async def test_validate_missing_project_name(self, service):
        """Test validation with missing project name."""
        json_data = json.dumps({
            "project": {"description": "No name"},
            "items": [],
            "links": [],
        })

        result = await service.validate_import_data(json_data)

        assert "Project name is required" in result

    @pytest.mark.asyncio
    async def test_validate_item_missing_title(self, service):
        """Test validation with item missing title."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "view": "REQ"},
            ],
            "links": [],
        })

        result = await service.validate_import_data(json_data)

        assert "Item 0: title is required" in result

    @pytest.mark.asyncio
    async def test_validate_item_missing_view(self, service):
        """Test validation with item missing view."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "title": "Item"},
            ],
            "links": [],
        })

        result = await service.validate_import_data(json_data)

        assert "Item 0: view is required" in result

    @pytest.mark.asyncio
    async def test_validate_link_invalid_source(self, service):
        """Test validation with invalid link source."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "title": "Item", "view": "REQ"},
            ],
            "links": [
                {"source_id": "invalid", "target_id": "1"},
            ],
        })

        result = await service.validate_import_data(json_data)

        assert "Link 0: source_id 'invalid' not found in items" in result

    @pytest.mark.asyncio
    async def test_validate_link_invalid_target(self, service):
        """Test validation with invalid link target."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "title": "Item", "view": "REQ"},
            ],
            "links": [
                {"source_id": "1", "target_id": "invalid"},
            ],
        })

        result = await service.validate_import_data(json_data)

        assert "Link 0: target_id 'invalid' not found in items" in result

    @pytest.mark.asyncio
    async def test_validate_valid_data(self, service):
        """Test validation with valid data."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "title": "Item 1", "view": "REQ"},
                {"id": "2", "title": "Item 2", "view": "DESIGN"},
            ],
            "links": [
                {"source_id": "1", "target_id": "2"},
            ],
        })

        result = await service.validate_import_data(json_data)

        assert result == []

    @pytest.mark.asyncio
    async def test_validate_multiple_errors(self, service):
        """Test validation with multiple errors."""
        json_data = json.dumps({
            "project": {"name": "Test"},
            "items": [
                {"id": "1", "view": "REQ"},  # Missing title
                {"id": "2", "title": "Item"},  # Missing view
            ],
            "links": [],
        })

        result = await service.validate_import_data(json_data)

        assert len(result) == 2


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_repositories(self):
        """Test initialization creates repositories."""
        session = AsyncMock()
        service = ImportService(session)

        assert service.session == session
        assert service.projects is not None
        assert service.items is not None
        assert service.links is not None
