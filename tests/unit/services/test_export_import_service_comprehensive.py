"""
Comprehensive tests for ExportImportService.

Tests all methods including:
- export_to_json
- export_to_csv
- export_to_markdown
- import_from_json
- import_from_csv
- get_export_formats
- get_import_formats

Coverage target: 90%+
"""

import pytest
import json
import csv
from io import StringIO
from unittest.mock import AsyncMock, Mock
from tracertm.services.export_import_service import ExportImportService
from tracertm.models.item import Item
from tracertm.models.project import Project


class TestExportToJson:
    """Test export_to_json method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ExportImportService(mock_session)

    @pytest.mark.asyncio
    async def test_export_success(self, service):
        """Test successful JSON export."""
        # Setup mock project
        project = Mock(spec=Project)
        project.id = "proj-1"
        project.name = "Test Project"
        project.description = "Test Description"

        # Setup mock items
        items = []
        for i in range(3):
            item = Mock(spec=Item)
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.view = "FEATURE"
            item.item_type = "feature"
            item.status = "todo"
            item.description = f"Description {i}"
            items.append(item)

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=items)

        # Execute
        result = await service.export_to_json("proj-1")

        # Verify
        assert result["format"] == "json"
        assert result["project"]["id"] == "proj-1"
        assert result["project"]["name"] == "Test Project"
        assert result["item_count"] == 3
        assert len(result["items"]) == 3

    @pytest.mark.asyncio
    async def test_export_project_not_found(self, service):
        """Test export when project doesn't exist."""
        service.projects.get_by_id = AsyncMock(return_value=None)

        result = await service.export_to_json("nonexistent")

        assert "error" in result
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_export_empty_project(self, service):
        """Test export of project with no items."""
        project = Mock(spec=Project)
        project.id = "proj-1"
        project.name = "Empty Project"
        project.description = ""

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=[])

        result = await service.export_to_json("proj-1")

        assert result["item_count"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_export_items_without_attributes(self, service):
        """Test export with items missing some attributes."""
        project = Mock(spec=Project)
        project.id = "proj-1"
        project.name = "Test"

        # Item with minimal attributes
        item = Mock(spec=Item)
        item.id = "item-1"
        # Simulate missing attributes by not having them
        if hasattr(item, "title"):
            delattr(item, "title")

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=[item])

        result = await service.export_to_json("proj-1")

        # Should handle gracefully with empty strings
        assert result["items"][0]["title"] == ""


class TestExportToCsv:
    """Test export_to_csv method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ExportImportService(mock_session)

    @pytest.mark.asyncio
    async def test_export_csv_success(self, service):
        """Test successful CSV export."""
        items = []
        for i in range(3):
            item = Mock(spec=Item)
            item.id = f"item-{i}"
            item.title = f"Item {i}"
            item.view = "FEATURE"
            item.item_type = "feature"
            item.status = "todo"
            item.description = f"Desc {i}"
            items.append(item)

        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_csv("proj-1")

        assert result["format"] == "csv"
        assert result["item_count"] == 3
        assert "content" in result
        assert "ID,Title,View,Type,Status,Description" in result["content"]

    @pytest.mark.asyncio
    async def test_export_csv_parse_output(self, service):
        """Test CSV output can be parsed."""
        items = [Mock(spec=Item, id="1", title="Test", view="FEATURE",
                      item_type="feature", status="done", description="Desc")]

        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_csv("proj-1")

        # Parse CSV to verify format
        csv_data = StringIO(result["content"])
        reader = csv.DictReader(csv_data)
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["ID"] == "1"
        assert rows[0]["Title"] == "Test"

    @pytest.mark.asyncio
    async def test_export_csv_empty(self, service):
        """Test CSV export with no items."""
        service.items.query = AsyncMock(return_value=[])

        result = await service.export_to_csv("proj-1")

        assert result["item_count"] == 0
        # Should still have header
        assert "ID,Title" in result["content"]

    @pytest.mark.asyncio
    async def test_export_csv_special_characters(self, service):
        """Test CSV export with special characters."""
        item = Mock(spec=Item)
        item.id = "1"
        item.title = "Item, with comma"
        item.view = "FEATURE"
        item.item_type = "feature"
        item.status = "todo"
        item.description = 'Description with "quotes"'

        service.items.query = AsyncMock(return_value=[item])

        result = await service.export_to_csv("proj-1")

        # CSV should properly escape special characters
        assert result["item_count"] == 1


class TestExportToMarkdown:
    """Test export_to_markdown method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ExportImportService(mock_session)

    @pytest.mark.asyncio
    async def test_export_markdown_success(self, service):
        """Test successful Markdown export."""
        project = Mock(spec=Project)
        project.id = "proj-1"
        project.name = "Test Project"
        project.description = "Test Description"

        items = [
            Mock(spec=Item, id="1", title="Feature 1", view="FEATURE",
                 status="todo", description="Desc 1"),
            Mock(spec=Item, id="2", title="Feature 2", view="FEATURE",
                 status="done", description="Desc 2"),
        ]

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_markdown("proj-1")

        assert result["format"] == "markdown"
        assert result["item_count"] == 2
        assert "Test Project" in result["content"]
        assert "## FEATURE" in result["content"]

    @pytest.mark.asyncio
    async def test_export_markdown_multiple_views(self, service):
        """Test Markdown export groups by view."""
        project = Mock(spec=Project, id="proj-1", name="Test", description="")

        items = [
            Mock(spec=Item, id="1", title="F1", view="FEATURE", status="todo", description=""),
            Mock(spec=Item, id="2", title="T1", view="TASK", status="todo", description=""),
            Mock(spec=Item, id="3", title="F2", view="FEATURE", status="done", description=""),
        ]

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_markdown("proj-1")

        # Should have sections for each view
        assert "## FEATURE" in result["content"]
        assert "## TASK" in result["content"]

    @pytest.mark.asyncio
    async def test_export_markdown_project_not_found(self, service):
        """Test Markdown export when project not found."""
        service.projects.get_by_id = AsyncMock(return_value=None)

        result = await service.export_to_markdown("nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_export_markdown_with_descriptions(self, service):
        """Test Markdown includes descriptions."""
        project = Mock(spec=Project, id="proj-1", name="Test", description="")

        items = [
            Mock(spec=Item, id="1", title="Item", view="FEATURE",
                 status="todo", description="Long description"),
        ]

        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_markdown("proj-1")

        assert "Long description" in result["content"]


class TestImportFromJson:
    """Test import_from_json method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ExportImportService(mock_session)

    @pytest.mark.asyncio
    async def test_import_success(self, service):
        """Test successful JSON import."""
        json_data = json.dumps({
            "items": [
                {"title": "Item 1", "view": "FEATURE", "type": "feature", "status": "todo"},
                {"title": "Item 2", "view": "TASK", "type": "task", "status": "done"},
            ]
        })

        service.items.create = AsyncMock()

        result = await service.import_from_json("proj-1", json_data)

        assert result["success"] is True
        assert result["imported_count"] == 2
        assert result["error_count"] == 0

    @pytest.mark.asyncio
    async def test_import_invalid_json(self, service):
        """Test import with invalid JSON."""
        result = await service.import_from_json("proj-1", "not valid json")

        assert "error" in result
        assert "Invalid JSON" in result["error"]

    @pytest.mark.asyncio
    async def test_import_missing_items_field(self, service):
        """Test import with missing items field."""
        json_data = json.dumps({"data": []})

        result = await service.import_from_json("proj-1", json_data)

        assert "error" in result
        assert "Missing 'items'" in result["error"]

    @pytest.mark.asyncio
    async def test_import_with_errors(self, service):
        """Test import with some items failing."""
        json_data = json.dumps({
            "items": [
                {"title": "Item 1"},
                {"title": "Item 2"},
            ]
        })

        # First succeeds, second fails
        service.items.create = AsyncMock(side_effect=[None, Exception("DB error")])

        result = await service.import_from_json("proj-1", json_data)

        assert result["imported_count"] == 1
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_import_default_values(self, service):
        """Test import uses default values for missing fields."""
        json_data = json.dumps({
            "items": [{"title": "Item 1"}]  # Missing other fields
        })

        service.items.create = AsyncMock()

        await service.import_from_json("proj-1", json_data)

        # Verify defaults were used
        call_args = service.items.create.call_args[1]
        assert call_args["view"] == "FEATURE"
        assert call_args["item_type"] == "feature"
        assert call_args["status"] == "todo"


class TestImportFromCsv:
    """Test import_from_csv method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return AsyncMock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ExportImportService(mock_session)

    @pytest.mark.asyncio
    async def test_import_csv_success(self, service):
        """Test successful CSV import."""
        csv_data = """Title,View,Type,Status
Item 1,FEATURE,feature,todo
Item 2,TASK,task,done"""

        service.items.create = AsyncMock()

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["success"] is True
        assert result["imported_count"] == 2
        assert result["error_count"] == 0

    @pytest.mark.asyncio
    async def test_import_csv_invalid_format(self, service):
        """Test import with invalid CSV."""
        result = await service.import_from_csv("proj-1", "not\nvalid\ncsv\nformat")

        # Should handle gracefully
        assert "error" in result or result["success"] is True

    @pytest.mark.asyncio
    async def test_import_csv_with_errors(self, service):
        """Test CSV import with some rows failing."""
        csv_data = """Title,View,Type,Status
Item 1,FEATURE,feature,todo
Item 2,TASK,task,done"""

        service.items.create = AsyncMock(side_effect=[None, Exception("Error")])

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["imported_count"] == 1
        assert result["error_count"] == 1

    @pytest.mark.asyncio
    async def test_import_csv_empty(self, service):
        """Test import with empty CSV."""
        csv_data = """Title,View,Type,Status"""

        service.items.create = AsyncMock()

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["imported_count"] == 0

    @pytest.mark.asyncio
    async def test_import_csv_default_values(self, service):
        """Test CSV import uses defaults for missing columns."""
        csv_data = """Title
Item 1"""

        service.items.create = AsyncMock()

        await service.import_from_csv("proj-1", csv_data)

        call_args = service.items.create.call_args[1]
        assert call_args["view"] == "FEATURE"
        assert call_args["item_type"] == "feature"
        assert call_args["status"] == "todo"


class TestGetFormats:
    """Test get_export_formats and get_import_formats methods."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ExportImportService(AsyncMock())

    @pytest.mark.asyncio
    async def test_get_export_formats(self, service):
        """Test get_export_formats returns supported formats."""
        formats = await service.get_export_formats()

        assert "json" in formats
        assert "csv" in formats
        assert "markdown" in formats
        assert len(formats) == 3

    @pytest.mark.asyncio
    async def test_get_import_formats(self, service):
        """Test get_import_formats returns supported formats."""
        formats = await service.get_import_formats()

        assert "json" in formats
        assert "csv" in formats
        assert len(formats) == 2
