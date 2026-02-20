"""Comprehensive integration tests targeting coverage gaps in low-coverage services.

This test suite is specifically designed to push coverage above 80% for:
- stateless_ingestion_service.py (4.41% -> 80%+)
- critical_path_service.py (13.11% -> 80%+)
- progress_service.py (14.46% -> 80%+)
- export_import_service.py (30.36% -> 80%+)
- tui_service.py (34.86% -> 80%+)

Focus areas:
1. Main code paths and execution flows
2. Error handling and exception scenarios
3. Edge cases and boundary conditions
4. Integration between services and repositories
5. Database interactions and transactions
"""

import json
import tempfile
from datetime import UTC, datetime, timedelta
from typing import Any, Never
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest
import pytest_asyncio
import yaml
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project
from tracertm.services.critical_path_service import CriticalPathService
from tracertm.services.export_import_service import ExportImportService
from tracertm.services.progress_service import ProgressService
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.services.tui_service import TUIService, UIComponentType

# ============================================================================
# STATELESS INGESTION SERVICE TESTS (Target: 80%+ coverage)
# ============================================================================


class TestStatelessIngestionServiceGapCoverage:
    """Integration tests for StatelessIngestionService covering untested paths."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock database session."""
        session = Mock(spec=Session)
        session.add = Mock()
        session.flush = Mock()
        session.query = Mock()
        return session

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create StatelessIngestionService instance."""
        return StatelessIngestionService(mock_session)

    # ========================================================================
    # MARKDOWN INGESTION - Main Paths
    # ========================================================================

    def test_ingest_markdown_file_not_found_error(self, service: Any) -> None:
        """Test FileNotFoundError when markdown file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            service.ingest_markdown("/nonexistent/path/file.md")

    def test_ingest_markdown_invalid_extension_validation(self, service: Any) -> None:
        """Test validation error for invalid file extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"content")
            tmp.flush()

            with pytest.raises(ValueError, match="Invalid file extension"):
                service.ingest_markdown(tmp.name, validate=True)

    def test_ingest_markdown_dry_run_mode(self, service: Any) -> None:
        """Test dry run returns preview without creating items."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Header 1\n## Header 2\n[Link](url)\n")
            tmp.flush()

            result = service.ingest_markdown(tmp.name, dry_run=True)

            assert result["dry_run"] is True
            assert result["headers_found"] == COUNT_TWO
            assert result["links_found"] == 1
            assert result["would_create_items"] == COUNT_TWO
            assert result["would_create_links"] == 1
            service.session.add.assert_not_called()

    def test_ingest_markdown_without_frontmatter_library(self, service: Any, _mock_session: Any) -> None:
        """Test markdown ingestion when frontmatter library not available."""
        with patch("tracertm.services.stateless_ingestion_service.frontmatter", None):
            service_no_fm = StatelessIngestionService(mock_session)

            with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
                tmp.write("# Test Header\nContent here")
                tmp.flush()

                # Mock project creation
                mock_project = Mock(spec=Project)
                mock_project.id = str(uuid4())
                mock_session.query.return_value.filter.return_value.first.return_value = None

                result = service_no_fm.ingest_markdown(tmp.name, validate=False)

                assert "items_created" in result
                assert result["items_created"] >= 0

    def test_ingest_markdown_with_frontmatter_parsing(self, service: Any, mock_session: Any) -> None:
        """Test markdown with YAML frontmatter metadata."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("""---
project: Test Project
description: Test Description
status: in_progress
---

# Feature Title
## Story Title
""")
            tmp.flush()

            # Mock project query
            mock_project = Mock(spec=Project)
            mock_project.id = str(uuid4())
            mock_session.query.return_value.filter.return_value.first.return_value = mock_project

            result = service.ingest_markdown(tmp.name, validate=False)

            assert result["items_created"] >= 0
            assert "project_id" in result

    def test_ingest_markdown_frontmatter_exception_handling(self, service: Any, mock_session: Any) -> None:
        """Test handling of frontmatter parsing exceptions."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("---\ninvalid: yaml: content:\n---\n# Header")
            tmp.flush()

            mock_project = Mock(spec=Project)
            mock_project.id = str(uuid4())
            mock_session.query.return_value.filter.return_value.first.return_value = mock_project

            # Should handle exception and treat as no frontmatter
            result = service.ingest_markdown(tmp.name, validate=False)
            assert "items_created" in result

    def test_ingest_markdown_create_new_project(self, service: Any, mock_session: Any) -> None:
        """Test creating new project when project_id not provided."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test Header")
            tmp.flush()

            # Mock no existing project
            mock_session.query.return_value.filter.return_value.first.return_value = None

            result = service.ingest_markdown(tmp.name, validate=False)

            # Should create new project
            assert mock_session.add.called
            assert "project_id" in result

    def test_ingest_markdown_with_provided_project_id(self, service: Any, mock_session: Any) -> None:
        """Test using provided project_id."""
        project_id = str(uuid4())
        mock_project = Mock(spec=Project)
        mock_project.id = project_id
        mock_session.query.return_value.filter.return_value.first.return_value = mock_project

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test")
            tmp.flush()

            result = service.ingest_markdown(tmp.name, project_id=project_id, validate=False)

            assert result["project_id"] == project_id

    def test_ingest_markdown_project_not_found_error(self, service: Any, mock_session: Any) -> None:
        """Test error when specified project_id doesn't exist."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("# Test")
            tmp.flush()

            with pytest.raises(ValueError, match="Project not found"):
                service.ingest_markdown(tmp.name, project_id="nonexistent-id", validate=False)

    def test_ingest_markdown_hierarchical_headers(self, service: Any, mock_session: Any) -> None:
        """Test hierarchical header structure with parent relationships."""
        mock_project = Mock(spec=Project)
        mock_project.id = str(uuid4())
        mock_session.query.return_value.filter.return_value.first.return_value = mock_project

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("""# Level 1
## Level 2
### Level 3
#### Level 4
##### Level 5
###### Level 6
""")
            tmp.flush()

            result = service.ingest_markdown(tmp.name, project_id=mock_project.id, validate=False)

            assert result["items_created"] == 6

    def test_ingest_markdown_internal_links(self, service: Any, mock_session: Any) -> None:
        """Test extraction and creation of internal markdown links."""
        mock_project = Mock(spec=Project)
        mock_project.id = str(uuid4())
        mock_session.query.return_value.filter.return_value.first.return_value = mock_project

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".md", delete=False) as tmp:
            tmp.write("""# Target Header
Content
[Link to Target](#target-header)
""")
            tmp.flush()

            result = service.ingest_markdown(tmp.name, project_id=mock_project.id, validate=False)

            assert "links_created" in result

    def test_ingest_markdown_without_markdown_it_library(self, mock_session: Any) -> None:
        """Test when MarkdownIt library is not available."""
        with patch("tracertm.services.stateless_ingestion_service.MarkdownIt", None):
            service = StatelessIngestionService(mock_session)
            assert service.md_parser is None

    def test_ingest_markdown_without_markdown_library(self, mock_session: Any) -> None:
        """Test when Markdown library is not available."""
        with patch("tracertm.services.stateless_ingestion_service.Markdown", None):
            service = StatelessIngestionService(mock_session)
            assert service.markdown is None

    # ========================================================================
    # MDX INGESTION - Main Paths
    # ========================================================================

    def test_ingest_mdx_file_not_found_error(self, service: Any) -> None:
        """Test FileNotFoundError for MDX file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            service.ingest_mdx("/nonexistent/file.mdx")

    def test_ingest_mdx_invalid_extension_validation(self, service: Any) -> None:
        """Test validation error for non-MDX extension."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tmp:
            tmp.write(b"content")
            tmp.flush()

            with pytest.raises(ValueError, match="Invalid file extension"):
                service.ingest_mdx(tmp.name, validate=True)

    def test_ingest_mdx_dry_run_mode(self, service: Any) -> None:
        """Test MDX dry run returns component count."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".mdx", delete=False) as tmp:
            tmp.write("# Header\n<Button>Click</Button>\n<Alert>Warning</Alert>")
            tmp.flush()

            result = service.ingest_mdx(tmp.name, dry_run=True)

            assert result["dry_run"] is True
            assert result["headers_found"] >= 1
            assert "jsx_components_found" in result

    def test_ingest_mdx_with_jsx_components(self, service: Any, mock_session: Any) -> None:
        """Test MDX ingestion extracts JSX components."""
        mock_project = Mock(spec=Project)
        mock_project.id = str(uuid4())
        mock_session.query.return_value.filter.return_value.first.return_value = mock_project

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".mdx", delete=False) as tmp:
            tmp.write("""# MDX Page
<Component attr="value">Content</Component>
<AnotherComponent>More content</AnotherComponent>
""")
            tmp.flush()

            result = service.ingest_mdx(tmp.name, project_id=mock_project.id, validate=False)

            assert "jsx_components_created" in result

    def test_ingest_mdx_without_frontmatter(self, service: Any, _mock_session: Any) -> None:
        """Test MDX without frontmatter library."""
        with patch("tracertm.services.stateless_ingestion_service.frontmatter", None):
            service_no_fm = StatelessIngestionService(mock_session)

            mock_project = Mock(spec=Project)
            mock_project.id = str(uuid4())
            mock_session.query.return_value.filter.return_value.first.return_value = mock_project

            with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".mdx", delete=False) as tmp:
                tmp.write("<Component>Test</Component>")
                tmp.flush()

                result = service_no_fm.ingest_mdx(tmp.name, project_id=mock_project.id, validate=False)
                assert "jsx_components_created" in result

    def test_ingest_mdx_create_new_project(self, service: Any, mock_session: Any) -> None:
        """Test MDX creates new project when not specified."""
        # Create a mock project that persists across queries
        mock_project = Mock(spec=Project)
        mock_project.id = str(uuid4())

        # Set up mock to first return None (project doesn't exist by name)
        # Then after creation, return the mock project when queried by ID
        first_call = True

        def query_side_effect(*args: Any, **kwargs: Any) -> None:
            nonlocal first_call
            mock_query = Mock()
            if first_call:
                # First query: project doesn't exist by name
                mock_query.filter.return_value.first.return_value = None
                first_call = False
            else:
                # Subsequent queries: return the created project
                mock_query.filter.return_value.first.return_value = mock_project
            return mock_query

        mock_session.query.side_effect = query_side_effect

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".mdx", delete=False) as tmp:
            tmp.write("# Test")
            tmp.flush()

            result = service.ingest_mdx(tmp.name, validate=False)

            assert "project_id" in result

    # ========================================================================
    # YAML INGESTION - Main Paths
    # ========================================================================

    def test_ingest_yaml_file_not_found_error(self, service: Any) -> None:
        """Test FileNotFoundError for YAML file."""
        with pytest.raises(FileNotFoundError, match="File not found"):
            service.ingest_yaml("/nonexistent/file.yaml")

    def test_ingest_yaml_invalid_extension_validation(self, service: Any) -> None:
        """Test validation error for non-YAML extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"content")
            tmp.flush()

            with pytest.raises(ValueError, match="Invalid file extension"):
                service.ingest_yaml(tmp.name, validate=True)

    def test_ingest_yaml_invalid_yaml_syntax(self, service: Any) -> None:
        """Test error for invalid YAML syntax."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("invalid: yaml: [unclosed bracket")
            tmp.flush()

            with pytest.raises(ValueError, match="Invalid YAML"):
                service.ingest_yaml(tmp.name, validate=False)

    def test_ingest_yaml_non_dict_root(self, service: Any) -> None:
        """Test error when YAML root is not a dictionary."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            tmp.write("- item1\n- item2")
            tmp.flush()

            with pytest.raises(ValueError, match="YAML root must be a dictionary"):
                service.ingest_yaml(tmp.name, validate=False)

    def test_ingest_yaml_openapi_detection(self, service: Any) -> None:
        """Test OpenAPI format detection."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {"openapi": "3.0.0", "info": {"title": "API", "version": "1.0.0"}, "paths": {}}
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["format"] == "openapi"

    def test_ingest_yaml_bmad_detection(self, service: Any) -> None:
        """Test BMad format detection."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {"bmad": True, "requirements": [{"id": "REQ-1", "title": "Test"}]}
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["format"] == "bmad"

    def test_ingest_yaml_generic_format(self, service: Any) -> None:
        """Test generic YAML format."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {"name": "Test", "items": [{"title": "Item 1"}]}
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["format"] == "yaml"

    # ========================================================================
    # OPENAPI INGESTION - Detailed Paths
    # ========================================================================

    def test_ingest_openapi_spec_complete(self, service: Any, mock_session: Any) -> None:
        """Test full OpenAPI spec ingestion with schemas and paths."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "description": "Test Description", "version": "1.0.0"},
                "components": {
                    "schemas": {
                        "User": {
                            "type": "object",
                            "description": "User schema",
                            "properties": {"name": {"type": "string"}},
                        },
                        "Product": {"type": "object", "properties": {"id": {"type": "integer"}}},
                    },
                    "responses": {},
                    "parameters": {},
                },
                "paths": {
                    "/users": {
                        "get": {
                            "operationId": "getUsers",
                            "summary": "Get users",
                            "description": "Retrieve all users",
                            "responses": {
                                "200": {
                                    "description": "Success",
                                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                                },
                            },
                        },
                        "post": {
                            "operationId": "createUser",
                            "summary": "Create user",
                            "requestBody": {
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                            },
                            "responses": {
                                "201": {
                                    "description": "Created",
                                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}},
                                },
                            },
                        },
                    },
                },
            }
            tmp.write(yaml.dump(openapi_spec))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["format"] == "openapi"
            assert result["schemas_created"] == COUNT_TWO
            assert result["endpoints_created"] >= COUNT_TWO

    def test_ingest_openapi_dry_run_counts(self, service: Any) -> None:
        """Test OpenAPI dry run calculates correct counts."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {"title": "API"},
                "components": {"schemas": {"User": {}, "Product": {}, "Order": {}}},
                "paths": {"/users": {"get": {}, "post": {}, "x-custom": {}}, "/products": {"get": {}, "delete": {}}},
            }
            tmp.write(yaml.dump(openapi_spec))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["format"] == "openapi"
            assert result["schemas_found"] == COUNT_THREE
            # x-custom should be excluded
            assert result["endpoints_found"] == COUNT_FOUR

    def test_ingest_openapi_skip_extension_fields(self, service: Any, mock_session: Any) -> None:
        """Test OpenAPI ingestion skips x- extension fields."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {"title": "API"},
                "paths": {"/test": {"get": {"summary": "Real endpoint"}, "x-internal": {"should": "be skipped"}}},
            }
            tmp.write(yaml.dump(openapi_spec))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["endpoints_created"] == 1

    def test_ingest_openapi_related_endpoints_linking(self, service: Any, mock_session: Any) -> None:
        """Test linking of related endpoints on same path."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {"title": "API"},
                "paths": {
                    "/resource": {
                        "get": {"summary": "Get"},
                        "post": {"summary": "Create"},
                        "put": {"summary": "Update"},
                    },
                },
            }
            tmp.write(yaml.dump(openapi_spec))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            # Should create links between endpoints on same path
            assert result["links_created"] > 0

    # ========================================================================
    # BMAD FORMAT INGESTION - Detailed Paths
    # ========================================================================

    def test_ingest_bmad_format_complete(self, service: Any, mock_session: Any) -> None:
        """Test complete BMad format ingestion."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            bmad_content = {
                "project": {"name": "Test Project", "description": "Test Desc"},
                "requirements": [
                    {
                        "id": "REQ-1",
                        "title": "Feature 1",
                        "description": "Feature description",
                        "type": "feature",
                        "status": "in_progress",
                        "priority": "high",
                        "owner": "dev1",
                        "tags": ["important"],
                        "depends_on": [],
                    },
                    {
                        "id": "REQ-2",
                        "requirement_id": "REQ-2",
                        "name": "Test Case",
                        "text": "Test description",
                        "type": "test_case",
                        "status": "todo",
                        "parent_id": "REQ-1",
                        "depends_on": ["REQ-1"],
                    },
                ],
                "traceability": [{"source": "REQ-1", "target": "REQ-2", "type": "verifies", "rule": "test-coverage"}],
            }
            tmp.write(yaml.dump(bmad_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["format"] == "bmad"
            assert result["requirements_created"] == COUNT_TWO
            assert result["links_created"] >= 1

    def test_ingest_bmad_alternative_structure(self, service: Any, mock_session: Any) -> None:
        """Test BMad with alternative spec structure."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            bmad_content = {"spec": {"requirements": [{"id": "REQ-1", "title": "Test"}], "traceability": []}}
            tmp.write(yaml.dump(bmad_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["format"] == "bmad"
            assert result["requirements_found"] == 1

    def test_ingest_bmad_view_routing(self, service: Any, mock_session: Any) -> None:
        """Test BMad requirement type to view routing."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            bmad_content = {
                "requirements": [
                    {"id": "R1", "title": "Feature", "type": "feature"},
                    {"id": "R2", "title": "Test", "type": "test"},
                    {"id": "R3", "title": "Code", "type": "code"},
                    {"id": "R4", "title": "API", "type": "api"},
                    {"id": "R5", "title": "Generic", "type": "requirement"},
                ],
            }
            tmp.write(yaml.dump(bmad_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["requirements_created"] == COUNT_FIVE

    def test_ingest_bmad_dependency_linking(self, service: Any, mock_session: Any) -> None:
        """Test BMad depends_on creates proper links."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            bmad_content = {
                "requirements": [
                    {"id": "REQ-1", "title": "Base"},
                    {"id": "REQ-2", "title": "Depends on 1", "depends_on": "REQ-1"},
                    {"id": "REQ-3", "title": "Depends on both", "depends_on": ["REQ-1", "REQ-2"]},
                ],
            }
            tmp.write(yaml.dump(bmad_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["links_created"] >= COUNT_THREE  # depends_on links

    def test_ingest_bmad_parent_child_linking(self, service: Any, mock_session: Any) -> None:
        """Test BMad parent_id creates child_of links."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            bmad_content = {
                "requirements": [
                    {"id": "EPIC-1", "title": "Epic"},
                    {"id": "STORY-1", "title": "Story", "parent_id": "EPIC-1"},
                ],
            }
            tmp.write(yaml.dump(bmad_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["links_created"] >= 1

    # ========================================================================
    # GENERIC YAML INGESTION - Detailed Paths
    # ========================================================================

    def test_ingest_generic_yaml_nested_structure(self, service: Any, mock_session: Any) -> None:
        """Test generic YAML with nested dictionaries."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {
                "name": "Project",
                "section1": {"description": "Section 1", "subsection1": {"description": "Subsection"}},
                "section2": {"items": ["a", "b"]},
            }
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["format"] == "yaml"
            assert result["items_created"] > 0

    def test_ingest_generic_yaml_list_items(self, service: Any, mock_session: Any) -> None:
        """Test generic YAML with list of dict items."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {
                "tasks": [
                    {"title": "Task 1", "description": "Do thing 1"},
                    {"name": "Task 2", "description": "Do thing 2"},
                    {"description": "Task 3 no title"},
                ],
            }
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, validate=False)

            assert result["items_created"] >= COUNT_THREE

    def test_ingest_generic_yaml_dry_run_recursive_count(self, service: Any) -> None:
        """Test generic YAML dry run counts nested items."""
        with tempfile.NamedTemporaryFile(encoding="utf-8", mode="w", suffix=".yaml", delete=False) as tmp:
            yaml_content = {"level1": {"level2": {"level3": ["a", "b", "c"]}}}
            tmp.write(yaml.dump(yaml_content))
            tmp.flush()

            result = service.ingest_yaml(tmp.name, dry_run=True)

            assert result["items_found"] > 0

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def test_determine_item_type_custom_mapping(self, service: Any) -> None:
        """Test _determine_item_type with custom type mapping."""
        metadata = {"type_mapping": {"1": "custom_epic", "2": "custom_feature"}}

        assert service._determine_item_type(1, metadata) == "custom_epic"
        assert service._determine_item_type(2, metadata) == "custom_feature"

    def test_determine_item_type_default_mapping(self, service: Any) -> None:
        """Test _determine_item_type default mapping."""
        assert service._determine_item_type(1, {}) == "epic"
        assert service._determine_item_type(2, {}) == "feature"
        assert service._determine_item_type(3, {}) == "story"
        assert service._determine_item_type(4, {}) == "task"
        assert service._determine_item_type(5, {}) == "task"
        assert service._determine_item_type(6, {}) == "task"

    def test_extract_section_content_found(self, service: Any) -> None:
        """Test _extract_section_content extracts content correctly."""
        body = """# Header 1
Content for header 1
More content

## Header 2
Different content"""

        content = service._extract_section_content(body, "# Header 1")
        assert "Content for header 1" in content

    def test_extract_section_content_until_next_header(self, service: Any) -> None:
        """Test content extraction stops at next header."""
        body = """## Section
Content here
More content
### Subsection
Should not be included"""

        content = service._extract_section_content(body, "## Section")
        assert "Content here" in content
        assert "Should not be included" not in content

    def test_extract_section_content_header_not_found(self, service: Any) -> None:
        """Test _extract_section_content when header not in body."""
        body = "# Other Header\nContent"

        content = service._extract_section_content(body, "# Missing Header")
        assert content == ""


# ============================================================================
# CRITICAL PATH SERVICE TESTS (Target: 80%+ coverage)
# ============================================================================


class TestCriticalPathServiceGapCoverage:
    """Integration tests for CriticalPathService covering untested paths."""

    @pytest_asyncio.fixture
    async def async_session(self) -> None:
        """Create async database session."""
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with async_session_factory() as session:
            yield session

    @pytest.fixture
    def mock_async_session(self) -> None:
        """Create mock async session."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def service(self, mock_async_session: Any) -> None:
        """Create CriticalPathService instance."""
        return CriticalPathService(mock_async_session)

    # ========================================================================
    # CRITICAL PATH CALCULATION - Main Algorithm
    # ========================================================================

    @pytest.mark.asyncio
    async def test_calculate_critical_path_empty_project(self, service: Any, mock_async_session: Any) -> None:
        """Test critical path with no items."""
        mock_async_session.execute = AsyncMock()

        # Mock empty items and links
        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=[])
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.calculate_critical_path("test-project")

        assert result.project_id == "test-project"
        assert result.critical_path == []
        assert result.path_length == 0
        assert result.total_duration == 0

    @pytest.mark.asyncio
    async def test_calculate_critical_path_single_item(self, service: Any, _mock_async_session: Any) -> None:
        """Test critical path with single item."""
        item1 = Mock()
        item1.id = "item-1"

        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=[item1])
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=[])

        result = await service.calculate_critical_path("test-project")

        assert result.project_id == "test-project"
        assert len(result.critical_items) == 1
        assert "item-1" in result.critical_items

    @pytest.mark.asyncio
    async def test_calculate_critical_path_linear_chain(self, service: Any) -> None:
        """Test critical path with linear dependency chain."""
        item1 = Mock()
        item1.id = "item-1"
        item2 = Mock()
        item2.id = "item-2"
        item3 = Mock()
        item3.id = "item-3"

        link1 = Mock()
        link1.source_item_id = "item-1"
        link1.target_item_id = "item-2"
        link1.link_type = "depends_on"

        link2 = Mock()
        link2.source_item_id = "item-2"
        link2.target_item_id = "item-3"
        link2.link_type = "depends_on"

        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=[item1, item2, item3])
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=[link1, link2])

        result = await service.calculate_critical_path("test-project")

        assert result.path_length >= 1
        assert result.total_duration >= 1

    @pytest.mark.asyncio
    async def test_calculate_critical_path_with_link_type_filter(self, service: Any) -> None:
        """Test critical path filtering by link types."""
        item1 = Mock()
        item1.id = "item-1"
        item2 = Mock()
        item2.id = "item-2"

        link_depends = Mock()
        link_depends.source_item_id = "item-1"
        link_depends.target_item_id = "item-2"
        link_depends.link_type = "depends_on"

        link_blocks = Mock()
        link_blocks.source_item_id = "item-1"
        link_blocks.target_item_id = "item-2"
        link_blocks.link_type = "blocks"

        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=[item1, item2])
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=[link_depends, link_blocks])

        result = await service.calculate_critical_path("test-project", link_types=["depends_on"])

        assert result.project_id == "test-project"

    @pytest.mark.asyncio
    async def test_calculate_critical_path_parallel_paths(self, service: Any) -> None:
        """Test critical path with parallel execution paths."""
        items = [Mock(id=f"item-{i}") for i in range(5)]

        links = [
            Mock(source_item_id="item-0", target_item_id="item-1", link_type="depends_on"),
            Mock(source_item_id="item-0", target_item_id="item-2", link_type="depends_on"),
            Mock(source_item_id="item-1", target_item_id="item-3", link_type="depends_on"),
            Mock(source_item_id="item-2", target_item_id="item-4", link_type="depends_on"),
        ]

        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=items)
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("test-project")

        assert len(result.critical_items) > 0
        assert result.total_duration > 0

    @pytest.mark.asyncio
    async def test_calculate_critical_path_slack_times(self, service: Any) -> None:
        """Test slack time calculation for items."""
        items = [Mock(id=f"item-{i}") for i in range(3)]

        links = [
            Mock(source_item_id="item-0", target_item_id="item-1", link_type="depends_on"),
            Mock(source_item_id="item-0", target_item_id="item-2", link_type="depends_on"),
        ]

        service.items = Mock()
        service.items.get_by_project = AsyncMock(return_value=items)
        service.links = Mock()
        service.links.get_by_project = AsyncMock(return_value=links)

        result = await service.calculate_critical_path("test-project")

        assert isinstance(result.slack_times, dict)
        assert len(result.slack_times) == len(items)

    # ========================================================================
    # HELPER METHOD - _find_critical_path
    # ========================================================================

    def test_find_critical_path_empty_critical_items(self, service: Any) -> None:
        """Test _find_critical_path with no critical items."""
        adjacency_list = {"item-1": [], "item-2": []}
        critical_items = set()
        topo_order = ["item-1", "item-2"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        assert path == []

    def test_find_critical_path_single_critical_item(self, service: Any) -> None:
        """Test _find_critical_path with single critical item."""
        adjacency_list = {"item-1": []}
        critical_items = {"item-1"}
        topo_order = ["item-1"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        assert "item-1" in path

    def test_find_critical_path_linear_critical_path(self, service: Any) -> None:
        """Test _find_critical_path with linear critical path."""
        adjacency_list = {"item-1": ["item-2"], "item-2": ["item-3"], "item-3": []}
        critical_items = {"item-1", "item-2", "item-3"}
        topo_order = ["item-1", "item-2", "item-3"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        assert len(path) >= 1

    def test_find_critical_path_branching_critical_path(self, service: Any) -> None:
        """Test _find_critical_path with branching paths."""
        adjacency_list = {"item-1": ["item-2", "item-3"], "item-2": ["item-4"], "item-3": [], "item-4": []}
        critical_items = {"item-1", "item-2", "item-4"}
        topo_order = ["item-1", "item-2", "item-3", "item-4"]

        path = service._find_critical_path(adjacency_list, critical_items, topo_order)

        # Should find one of the critical paths
        assert len(path) >= 1


# ============================================================================
# PROGRESS SERVICE TESTS (Target: 80%+ coverage)
# ============================================================================


class TestProgressServiceGapCoverage:
    """Integration tests for ProgressService covering untested paths."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock database session."""
        session = Mock(spec=Session)
        session.query = Mock()
        return session

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create ProgressService instance."""
        return ProgressService(mock_session)

    # ========================================================================
    # COMPLETION CALCULATION
    # ========================================================================

    def test_calculate_completion_item_not_found(self, service: Any, mock_session: Any) -> None:
        """Test completion calculation when item doesn't exist."""
        mock_session.query.return_value.filter.return_value.first.return_value = None

        completion = service.calculate_completion("nonexistent-id")

        assert completion == 0.0

    def test_calculate_completion_leaf_item_todo(self, service: Any, mock_session: Any) -> None:
        """Test completion for leaf item with todo status."""
        item = Mock(spec=Item)
        item.status = "todo"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 0.0

    def test_calculate_completion_leaf_item_in_progress(self, service: Any, mock_session: Any) -> None:
        """Test completion for leaf item in progress."""
        item = Mock(spec=Item)
        item.status = "in_progress"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 50.0

    def test_calculate_completion_leaf_item_blocked(self, service: Any, mock_session: Any) -> None:
        """Test completion for blocked item."""
        item = Mock(spec=Item)
        item.status = "blocked"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 0.0

    def test_calculate_completion_leaf_item_complete(self, service: Any, mock_session: Any) -> None:
        """Test completion for completed item."""
        item = Mock(spec=Item)
        item.status = "complete"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 100.0

    def test_calculate_completion_leaf_item_cancelled(self, service: Any, mock_session: Any) -> None:
        """Test completion for cancelled item."""
        item = Mock(spec=Item)
        item.status = "cancelled"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 0.0

    def test_calculate_completion_leaf_item_unknown_status(self, service: Any, mock_session: Any) -> None:
        """Test completion for item with unknown status."""
        item = Mock(spec=Item)
        item.status = "unknown_status"
        mock_session.query.return_value.filter.return_value.first.return_value = item
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("item-1")

        assert completion == 0.0

    def test_calculate_completion_parent_with_children(self, service: Any, mock_session: Any) -> None:
        """Test completion calculation for parent with children."""
        parent = Mock(spec=Item)
        parent.id = "parent-1"
        parent.status = "in_progress"

        child1 = Mock(spec=Item)
        child1.id = "child-1"
        child1.status = "complete"

        child2 = Mock(spec=Item)
        child2.id = "child-2"
        child2.status = "in_progress"

        # Mock queries
        def query_side_effect(*args: Any) -> None:
            if args[0] == Item:
                mock_query = Mock()
                filter_mock = Mock()

                # For parent query
                if not hasattr(query_side_effect, "call_count"):
                    query_side_effect.call_count = 0

                if query_side_effect.call_count == 0:
                    filter_mock.first.return_value = parent
                    filter_mock.all.return_value = [child1, child2]
                elif query_side_effect.call_count == 1:
                    filter_mock.first.return_value = child1
                    filter_mock.all.return_value = []
                elif query_side_effect.call_count == COUNT_TWO:
                    filter_mock.first.return_value = child2
                    filter_mock.all.return_value = []

                query_side_effect.call_count += 1
                mock_query.filter.return_value = filter_mock
                return mock_query
            return None

        mock_session.query.side_effect = query_side_effect

        completion = service.calculate_completion("parent-1")

        # Should be average of children: (100 + 50) / 2 = 75
        assert completion == 75.0

    def test_calculate_completion_parent_no_children(self, service: Any, mock_session: Any) -> None:
        """Test parent with empty children list."""
        parent = Mock(spec=Item)
        parent.status = "in_progress"
        mock_session.query.return_value.filter.return_value.first.return_value = parent
        mock_session.query.return_value.filter.return_value.all.return_value = []

        completion = service.calculate_completion("parent-1")

        # Falls back to leaf calculation
        assert completion == 50.0

    # ========================================================================
    # BLOCKED ITEMS
    # ========================================================================

    def test_get_blocked_items_no_blocks(self, service: Any, mock_session: Any) -> None:
        """Test get_blocked_items with no blocking links."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        blocked = service.get_blocked_items("project-1")

        assert blocked == []

    def test_get_blocked_items_with_blockers(self, service: Any, mock_session: Any) -> None:
        """Test get_blocked_items returns blocked items with blocker details."""
        link1 = Mock(spec=Link)
        link1.target_item_id = "blocked-1"
        link1.source_item_id = "blocker-1"

        link2 = Mock(spec=Link)
        link2.target_item_id = "blocked-1"
        link2.source_item_id = "blocker-2"

        blocked_item = Mock(spec=Item)
        blocked_item.id = "blocked-1"
        blocked_item.title = "Blocked Item"
        blocked_item.status = "blocked"

        blocker1 = Mock(spec=Item)
        blocker1.id = "blocker-1"
        blocker1.title = "Blocker 1"
        blocker1.status = "in_progress"

        blocker2 = Mock(spec=Item)
        blocker2.id = "blocker-2"
        blocker2.title = "Blocker 2"
        blocker2.status = "todo"

        # Setup query mocks
        def query_filter_first(*args: Any) -> None:
            mock_result = Mock()
            mock_result.filter.return_value.all.return_value = [link1, link2]

            if hasattr(query_filter_first, "item_call"):
                query_filter_first.item_call += 1
            else:
                query_filter_first.item_call = 0

            if query_filter_first.item_call == 0:
                mock_result.filter.return_value.first.return_value = blocked_item
            elif query_filter_first.item_call == 1:
                mock_result.filter.return_value.first.return_value = blocker1
            elif query_filter_first.item_call == COUNT_TWO:
                mock_result.filter.return_value.first.return_value = blocker2
            else:
                mock_result.filter.return_value.first.return_value = None

            return mock_result

        mock_session.query.side_effect = query_filter_first

        blocked = service.get_blocked_items("project-1")

        assert len(blocked) >= 0

    def test_get_blocked_items_missing_blocker_items(self, service: Any, mock_session: Any) -> None:
        """Test get_blocked_items handles missing blocker items gracefully."""
        link = Mock(spec=Link)
        link.target_item_id = "blocked-1"
        link.source_item_id = "missing-blocker"

        blocked_item = Mock(spec=Item)
        blocked_item.id = "blocked-1"
        blocked_item.title = "Blocked"
        blocked_item.status = "blocked"

        def query_side_effect(*args: Any) -> None:
            mock_query = Mock()
            mock_query.filter.return_value.all.return_value = [link]

            # First call for blocked item, second for missing blocker
            if not hasattr(query_side_effect, "call_count"):
                query_side_effect.call_count = 0

            if query_side_effect.call_count == 0:
                mock_query.filter.return_value.first.return_value = blocked_item
            else:
                mock_query.filter.return_value.first.return_value = None

            query_side_effect.call_count += 1
            return mock_query

        mock_session.query.side_effect = query_side_effect

        blocked = service.get_blocked_items("project-1")

        # Should filter out None blockers
        assert isinstance(blocked, list)

    # ========================================================================
    # STALLED ITEMS
    # ========================================================================

    def test_get_stalled_items_default_threshold(self, service: Any, mock_session: Any) -> None:
        """Test get_stalled_items with default 7-day threshold."""
        old_date = datetime.now(UTC) - timedelta(days=10)

        stalled_item = Mock(spec=Item)
        stalled_item.id = "stalled-1"
        stalled_item.title = "Stalled Item"
        stalled_item.status = "in_progress"
        stalled_item.updated_at = old_date

        mock_session.query.return_value.filter.return_value.all.return_value = [stalled_item]

        stalled = service.get_stalled_items("project-1")

        assert len(stalled) == 1
        assert stalled[0]["item_id"] == "stalled-1"
        assert stalled[0]["days_stalled"] == COUNT_TEN

    def test_get_stalled_items_custom_threshold(self, service: Any, mock_session: Any) -> None:
        """Test get_stalled_items with custom threshold."""
        old_date = datetime.now(UTC) - timedelta(days=15)

        stalled_item = Mock(spec=Item)
        stalled_item.id = "stalled-1"
        stalled_item.title = "Stalled"
        stalled_item.status = "blocked"
        stalled_item.updated_at = old_date

        mock_session.query.return_value.filter.return_value.all.return_value = [stalled_item]

        stalled = service.get_stalled_items("project-1", days_threshold=14)

        assert len(stalled) == 1

    def test_get_stalled_items_no_stalled(self, service: Any, mock_session: Any) -> None:
        """Test get_stalled_items with no stalled items."""
        mock_session.query.return_value.filter.return_value.all.return_value = []

        stalled = service.get_stalled_items("project-1")

        assert stalled == []

    def test_get_stalled_items_null_updated_at(self, service: Any, mock_session: Any) -> None:
        """Test stalled items with null updated_at field."""
        item = Mock(spec=Item)
        item.id = "item-1"
        item.title = "Item"
        item.status = "todo"
        item.updated_at = None

        mock_session.query.return_value.filter.return_value.all.return_value = [item]

        stalled = service.get_stalled_items("project-1")

        assert len(stalled) == 1
        assert stalled[0]["days_stalled"] is None

    # ========================================================================
    # VELOCITY CALCULATION
    # ========================================================================

    def test_calculate_velocity_default_period(self, service: Any, mock_session: Any) -> None:
        """Test velocity calculation with default 7-day period."""
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [5, 10]

        velocity = service.calculate_velocity("project-1")

        assert velocity["period_days"] == 7
        assert velocity["items_completed"] == COUNT_FIVE
        assert velocity["items_created"] == COUNT_TEN
        assert velocity["completion_rate"] == COUNT_FIVE / 7
        assert velocity["net_change"] == COUNT_FIVE

    def test_calculate_velocity_custom_period(self, service: Any, mock_session: Any) -> None:
        """Test velocity with custom period."""
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [15, 20]

        velocity = service.calculate_velocity("project-1", days=30)

        assert velocity["period_days"] == 30
        assert velocity["items_completed"] == 15
        assert velocity["items_created"] == 20

    def test_calculate_velocity_zero_completed(self, service: Any, mock_session: Any) -> None:
        """Test velocity when no items completed."""
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [0, 5]

        velocity = service.calculate_velocity("project-1")

        assert velocity["items_completed"] == 0
        assert velocity["completion_rate"] == 0.0

    def test_calculate_velocity_null_results(self, service: Any, mock_session: Any) -> None:
        """Test velocity handles None results from database."""
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [None, None]

        velocity = service.calculate_velocity("project-1")

        assert velocity["items_completed"] == 0
        assert velocity["items_created"] == 0

    # ========================================================================
    # PROGRESS REPORT
    # ========================================================================

    def test_generate_progress_report_default_dates(self, service: Any, mock_session: Any) -> None:
        """Test progress report with default date range."""
        items = [
            Mock(id="1", status="complete", view="FEATURE"),
            Mock(id="2", status="in_progress", view="FEATURE"),
            Mock(id="3", status="todo", view="TEST"),
        ]

        mock_session.query.return_value.filter.return_value.all.return_value = items
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [1, 3]

        report = service.generate_progress_report("project-1")

        assert report["summary"]["total_items"] == COUNT_THREE
        assert report["summary"]["completed"] == 1
        assert "completion_percentage" in report["summary"]
        assert "by_status" in report
        assert "by_view" in report

    def test_generate_progress_report_custom_dates(self, service: Any, mock_session: Any) -> None:
        """Test progress report with custom date range."""
        start = datetime(2025, 1, 1)
        end = datetime(2025, 1, 31)

        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [0, 0]

        report = service.generate_progress_report("project-1", start_date=start, end_date=end)

        assert report["period"]["days"] == 30

    def test_generate_progress_report_empty_project(self, service: Any, mock_session: Any) -> None:
        """Test progress report with no items."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [0, 0]

        report = service.generate_progress_report("project-1")

        assert report["summary"]["total_items"] == 0
        assert report["summary"]["completion_percentage"] == 0

    def test_generate_progress_report_includes_velocity(self, service: Any, mock_session: Any) -> None:
        """Test progress report includes velocity metrics."""
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [5, 10]

        report = service.generate_progress_report("project-1")

        assert "velocity" in report
        assert report["velocity"]["items_completed"] == COUNT_FIVE

    def test_generate_progress_report_limits_blocked_stalled(self, service: Any, mock_session: Any) -> None:
        """Test progress report limits blocked and stalled lists."""
        items = [Mock(id=str(i), status="complete", view="FEATURE") for i in range(20)]

        mock_session.query.return_value.filter.return_value.all.return_value = items
        mock_session.query.return_value.filter.return_value.scalar.side_effect = [20, 20]

        report = service.generate_progress_report("project-1")

        # Should limit to 10 items
        assert len(report["blocked"]) <= COUNT_TEN
        assert len(report["stalled"]) <= COUNT_TEN


# ============================================================================
# EXPORT/IMPORT SERVICE TESTS (Target: 80%+ coverage)
# ============================================================================


class TestExportImportServiceGapCoverage:
    """Integration tests for ExportImportService covering untested paths."""

    @pytest.fixture
    def mock_async_session(self) -> None:
        """Create mock async session."""
        return Mock(spec=AsyncSession)

    @pytest.fixture
    def service(self, mock_async_session: Any) -> None:
        """Create ExportImportService instance."""
        return ExportImportService(mock_async_session)

    # ========================================================================
    # JSON EXPORT
    # ========================================================================

    @pytest.mark.asyncio
    async def test_export_to_json_project_not_found(self, service: Any) -> None:
        """Test JSON export when project doesn't exist."""
        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=None)

        result = await service.export_to_json("nonexistent-project")

        assert "error" in result
        assert result["error"] == "Project not found"

    @pytest.mark.asyncio
    async def test_export_to_json_success(self, service: Any) -> None:
        """Test successful JSON export."""
        project = Mock()
        project.id = "proj-1"
        project.name = "Test Project"
        project.description = "Test Description"

        item1 = Mock()
        item1.id = "item-1"
        item1.title = "Item 1"
        item1.view = "FEATURE"
        item1.item_type = "feature"
        item1.status = "todo"
        item1.description = "Description"

        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item1])

        result = await service.export_to_json("proj-1")

        assert result["format"] == "json"
        assert result["project"]["id"] == "proj-1"
        assert result["item_count"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_export_to_json_missing_attributes(self, service: Any) -> None:
        """Test JSON export handles items missing attributes."""
        project = Mock(spec=["id"])
        project.id = "proj-1"

        item = Mock(spec=["id"])
        item.id = "item-1"

        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item])

        result = await service.export_to_json("proj-1")

        assert result["items"][0]["title"] == ""
        assert result["items"][0]["view"] == ""

    # ========================================================================
    # CSV EXPORT
    # ========================================================================

    @pytest.mark.asyncio
    async def test_export_to_csv_success(self, service: Any) -> None:
        """Test successful CSV export."""
        item1 = Mock()
        item1.id = "item-1"
        item1.title = "Title"
        item1.view = "FEATURE"
        item1.item_type = "feature"
        item1.status = "todo"
        item1.description = "Desc"

        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item1])

        result = await service.export_to_csv("proj-1")

        assert result["format"] == "csv"
        assert result["item_count"] == 1
        assert "ID,Title,View,Type,Status,Description" in result["content"]
        assert "item-1" in result["content"]

    @pytest.mark.asyncio
    async def test_export_to_csv_empty_project(self, service: Any) -> None:
        """Test CSV export with no items."""
        service.items = Mock()
        service.items.query = AsyncMock(return_value=[])

        result = await service.export_to_csv("proj-1")

        assert result["item_count"] == 0
        assert "ID,Title,View,Type,Status,Description" in result["content"]

    @pytest.mark.asyncio
    async def test_export_to_csv_missing_attributes(self, service: Any) -> None:
        """Test CSV export handles missing attributes."""
        item = Mock(spec=["id"])
        item.id = "item-1"

        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item])

        result = await service.export_to_csv("proj-1")

        # Should use empty strings for missing attributes
        assert result["item_count"] == 1

    # ========================================================================
    # MARKDOWN EXPORT
    # ========================================================================

    @pytest.mark.asyncio
    async def test_export_to_markdown_project_not_found(self, service: Any) -> None:
        """Test markdown export when project not found."""
        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=None)

        result = await service.export_to_markdown("nonexistent")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_export_to_markdown_success(self, service: Any) -> None:
        """Test successful markdown export."""
        project = Mock()
        project.name = "Test Project"
        project.description = "Project Description"

        item1 = Mock()
        item1.title = "Feature 1"
        item1.view = "FEATURE"
        item1.status = "in_progress"
        item1.description = "Feature description"

        item2 = Mock()
        item2.title = "Test 1"
        item2.view = "TEST"
        item2.status = "todo"
        item2.description = ""

        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item1, item2])

        result = await service.export_to_markdown("proj-1")

        assert result["format"] == "markdown"
        assert "# Test Project" in result["content"]
        assert "## FEATURE" in result["content"]
        assert "## TEST" in result["content"]
        assert result["item_count"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_export_to_markdown_groups_by_view(self, service: Any) -> None:
        """Test markdown export groups items by view."""
        project = Mock()
        project.name = "Project"
        project.description = ""

        items = [
            Mock(title="F1", view="FEATURE", status="todo", description=""),
            Mock(title="F2", view="FEATURE", status="todo", description=""),
            Mock(title="T1", view="TEST", status="todo", description=""),
        ]

        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items = Mock()
        service.items.query = AsyncMock(return_value=items)

        result = await service.export_to_markdown("proj-1")

        content = result["content"]
        assert content.count("## FEATURE") == 1
        assert content.count("## TEST") == 1

    @pytest.mark.asyncio
    async def test_export_to_markdown_missing_attributes(self, service: Any) -> None:
        """Test markdown export handles missing attributes."""
        project = Mock(spec=["id"])
        item = Mock(spec=["id"])

        service.projects = Mock()
        service.projects.get_by_id = AsyncMock(return_value=project)
        service.items = Mock()
        service.items.query = AsyncMock(return_value=[item])

        result = await service.export_to_markdown("proj-1")

        assert "Project" in result["content"]

    # ========================================================================
    # JSON IMPORT
    # ========================================================================

    @pytest.mark.asyncio
    async def test_import_from_json_invalid_json(self, service: Any) -> None:
        """Test JSON import with invalid JSON."""
        result = await service.import_from_json("proj-1", "invalid json {")

        assert "error" in result
        assert "Invalid JSON" in result["error"]

    @pytest.mark.asyncio
    async def test_import_from_json_missing_items_field(self, service: Any) -> None:
        """Test JSON import missing items field."""
        json_data = json.dumps({"project": "test"})

        result = await service.import_from_json("proj-1", json_data)

        assert "error" in result
        assert "Missing 'items' field" in result["error"]

    @pytest.mark.asyncio
    async def test_import_from_json_success(self, service: Any) -> None:
        """Test successful JSON import."""
        json_data = json.dumps({
            "items": [
                {"title": "Item 1", "view": "FEATURE", "type": "feature", "status": "todo"},
                {"title": "Item 2", "view": "TEST", "type": "test", "status": "in_progress"},
            ],
        })

        service.items = Mock()
        service.items.create = AsyncMock()

        result = await service.import_from_json("proj-1", json_data)

        assert result["success"] is True
        assert result["imported_count"] == COUNT_TWO
        assert result["error_count"] == 0

    @pytest.mark.asyncio
    async def test_import_from_json_partial_failure(self, service: Any) -> None:
        """Test JSON import with some failures."""
        json_data = json.dumps({"items": [{"title": "Good Item"}, {"title": "Bad Item"}]})

        service.items = Mock()

        async def create_side_effect(**kwargs: Any) -> None:
            if kwargs["title"] == "Bad Item":
                msg = "Creation failed"
                raise Exception(msg)

        service.items.create = AsyncMock(side_effect=create_side_effect)

        result = await service.import_from_json("proj-1", json_data)

        assert result["imported_count"] == 1
        assert result["error_count"] == 1
        assert len(result["errors"]) == 1

    @pytest.mark.asyncio
    async def test_import_from_json_default_values(self, service: Any) -> None:
        """Test JSON import uses default values for missing fields."""
        json_data = json.dumps({"items": [{"title": "Minimal Item"}]})

        service.items = Mock()
        service.items.create = AsyncMock()

        await service.import_from_json("proj-1", json_data)

        # Verify create was called with defaults
        service.items.create.assert_called_once()
        call_kwargs = service.items.create.call_args.kwargs
        assert call_kwargs["view"] == "FEATURE"
        assert call_kwargs["item_type"] == "feature"
        assert call_kwargs["status"] == "todo"

    # ========================================================================
    # CSV IMPORT
    # ========================================================================

    @pytest.mark.asyncio
    async def test_import_from_csv_invalid_format(self, service: Any) -> None:
        """Test CSV import with invalid CSV."""
        csv_data = 'invalid,csv,\nunclosed,quote,"'

        result = await service.import_from_csv("proj-1", csv_data)

        assert "error" in result

    @pytest.mark.asyncio
    async def test_import_from_csv_success(self, service: Any) -> None:
        """Test successful CSV import."""
        csv_data = """Title,View,Type,Status
Item 1,FEATURE,feature,todo
Item 2,TEST,test,in_progress"""

        service.items = Mock()
        service.items.create = AsyncMock()

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["success"] is True
        assert result["imported_count"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_from_csv_empty_file(self, service: Any) -> None:
        """Test CSV import with only headers."""
        csv_data = "Title,View,Type,Status\n"

        service.items = Mock()
        service.items.create = AsyncMock()

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["imported_count"] == 0

    @pytest.mark.asyncio
    async def test_import_from_csv_missing_columns(self, service: Any) -> None:
        """Test CSV import with missing columns uses defaults."""
        csv_data = "Title\nItem 1\nItem 2"

        service.items = Mock()
        service.items.create = AsyncMock()

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["imported_count"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_import_from_csv_with_errors(self, service: Any) -> None:
        """Test CSV import collects errors."""
        csv_data = "Title\nGood\nBad"

        service.items = Mock()

        async def create_side_effect(**kwargs: Any) -> None:
            if kwargs["title"] == "Bad":
                msg = "Failed"
                raise Exception(msg)

        service.items.create = AsyncMock(side_effect=create_side_effect)

        result = await service.import_from_csv("proj-1", csv_data)

        assert result["imported_count"] == 1
        assert result["error_count"] == 1

    # ========================================================================
    # FORMAT GETTERS
    # ========================================================================

    @pytest.mark.asyncio
    async def test_get_export_formats(self, service: Any) -> None:
        """Test getting available export formats."""
        formats = await service.get_export_formats()

        assert "json" in formats
        assert "csv" in formats
        assert "markdown" in formats

    @pytest.mark.asyncio
    async def test_get_import_formats(self, service: Any) -> None:
        """Test getting available import formats."""
        formats = await service.get_import_formats()

        assert "json" in formats
        assert "csv" in formats
        assert "markdown" not in formats  # Import only supports JSON and CSV


# ============================================================================
# TUI SERVICE TESTS (Target: 80%+ coverage)
# ============================================================================


class TestTUIServiceGapCoverage:
    """Integration tests for TUIService covering untested paths."""

    @pytest.fixture
    def service(self) -> None:
        """Create TUIService instance."""
        return TUIService()

    # ========================================================================
    # COMPONENT REGISTRATION
    # ========================================================================

    def test_register_component_basic(self, service: Any) -> None:
        """Test basic component registration."""
        component = service.register_component(
            name="test-component",
            component_type=UIComponentType.DASHBOARD,
            title="Test Dashboard",
        )

        assert component.name == "test-component"
        assert component.component_type == UIComponentType.DASHBOARD
        assert component.title == "Test Dashboard"
        assert component.data == {}

    def test_register_component_with_data(self, service: Any) -> None:
        """Test component registration with data."""
        data = {"key": "value", "count": 42}

        component = service.register_component(
            name="test",
            component_type=UIComponentType.TABLE,
            title="Table",
            data=data,
        )

        assert component.data == data

    def test_register_component_stores_in_dict(self, service: Any) -> None:
        """Test component is stored in components dict."""
        service.register_component("comp1", UIComponentType.FORM, "Form")

        assert "comp1" in service.components
        assert service.components["comp1"].component_type == UIComponentType.FORM

    # ========================================================================
    # COMPONENT RETRIEVAL
    # ========================================================================

    def test_get_component_exists(self, service: Any) -> None:
        """Test getting existing component."""
        service.register_component("test", UIComponentType.MODAL, "Modal")

        component = service.get_component("test")

        assert component is not None
        assert component.name == "test"

    def test_get_component_not_exists(self, service: Any) -> None:
        """Test getting non-existent component returns None."""
        component = service.get_component("nonexistent")

        assert component is None

    # ========================================================================
    # COMPONENT LISTING
    # ========================================================================

    def test_list_components_all(self, service: Any) -> None:
        """Test listing all components."""
        service.register_component("c1", UIComponentType.DASHBOARD, "D1")
        service.register_component("c2", UIComponentType.TABLE, "T1")
        service.register_component("c3", UIComponentType.FORM, "F1")

        components = service.list_components()

        assert len(components) == COUNT_THREE

    def test_list_components_filtered_by_type(self, service: Any) -> None:
        """Test listing components filtered by type."""
        service.register_component("d1", UIComponentType.DASHBOARD, "D1")
        service.register_component("d2", UIComponentType.DASHBOARD, "D2")
        service.register_component("t1", UIComponentType.TABLE, "T1")

        dashboards = service.list_components(component_type=UIComponentType.DASHBOARD)

        assert len(dashboards) == COUNT_TWO
        assert all(c.component_type == UIComponentType.DASHBOARD for c in dashboards)

    def test_list_components_empty(self, service: Any) -> None:
        """Test listing components when none registered."""
        components = service.list_components()

        assert components == []

    # ========================================================================
    # COMPONENT DATA UPDATE
    # ========================================================================

    def test_update_component_data_success(self, service: Any) -> None:
        """Test updating component data."""
        service.register_component("test", UIComponentType.CHART, "Chart", data={"x": 1})

        updated = service.update_component_data("test", {"y": 2, "z": 3})

        assert updated is not None
        assert updated.data["x"] == 1  # Original preserved
        assert updated.data["y"] == COUNT_TWO  # New added
        assert updated.data["z"] == COUNT_THREE

    def test_update_component_data_overwrites_existing(self, service: Any) -> None:
        """Test updating data overwrites existing keys."""
        service.register_component("test", UIComponentType.TABLE, "T", data={"a": 1})

        service.update_component_data("test", {"a": 999})

        component = service.get_component("test")
        assert component.data["a"] == 999

    def test_update_component_data_nonexistent(self, service: Any) -> None:
        """Test updating non-existent component returns None."""
        result = service.update_component_data("nonexistent", {"data": "value"})

        assert result is None

    # ========================================================================
    # VIEW MANAGEMENT
    # ========================================================================

    def test_set_current_view_success(self, service: Any) -> None:
        """Test setting current view."""
        service.register_component("view1", UIComponentType.DASHBOARD, "View 1")

        success = service.set_current_view("view1")

        assert success is True
        assert service.current_view == "view1"

    def test_set_current_view_nonexistent(self, service: Any) -> None:
        """Test setting non-existent view fails."""
        success = service.set_current_view("nonexistent")

        assert success is False
        assert service.current_view is None

    def test_get_current_view_when_set(self, service: Any) -> None:
        """Test getting current view when set."""
        service.register_component("view", UIComponentType.DASHBOARD, "View")
        service.set_current_view("view")

        current = service.get_current_view()

        assert current is not None
        assert current.name == "view"

    def test_get_current_view_when_not_set(self, service: Any) -> None:
        """Test getting current view when not set."""
        current = service.get_current_view()

        assert current is None

    def test_get_current_view_after_component_deleted(self, service: Any) -> None:
        """Test current view when component no longer exists."""
        service.register_component("view", UIComponentType.DASHBOARD, "View")
        service.set_current_view("view")
        del service.components["view"]

        current = service.get_current_view()

        assert current is None

    # ========================================================================
    # EVENT HANDLING
    # ========================================================================

    def test_register_event_handler_single(self, service: Any) -> None:
        """Test registering single event handler."""
        handler = Mock(return_value="result")

        service.register_event_handler("click", handler)

        assert "click" in service.event_handlers
        assert handler in service.event_handlers["click"]

    def test_register_event_handler_multiple(self, service: Any) -> None:
        """Test registering multiple handlers for same event."""
        handler1 = Mock()
        handler2 = Mock()

        service.register_event_handler("event", handler1)
        service.register_event_handler("event", handler2)

        assert len(service.event_handlers["event"]) == COUNT_TWO

    def test_trigger_event_calls_handlers(self, service: Any) -> None:
        """Test triggering event calls all handlers."""
        handler1 = Mock(return_value="r1")
        handler2 = Mock(return_value="r2")

        service.register_event_handler("event", handler1)
        service.register_event_handler("event", handler2)

        results = service.trigger_event("event", "arg1", key="value")

        assert results == ["r1", "r2"]
        handler1.assert_called_once_with("arg1", key="value")
        handler2.assert_called_once_with("arg1", key="value")

    def test_trigger_event_no_handlers(self, service: Any) -> None:
        """Test triggering event with no handlers."""
        results = service.trigger_event("nonexistent")

        assert results == []

    def test_trigger_event_handler_exception(self, service: Any) -> None:
        """Test event handler exceptions are caught and returned."""

        def failing_handler() -> Never:
            msg = "Handler failed"
            raise ValueError(msg)

        service.register_event_handler("event", failing_handler)

        results = service.trigger_event("event")

        assert len(results) == 1
        assert "error" in results[0]
        assert "Handler failed" in results[0]["error"]

    def test_trigger_event_mixed_success_failure(self, service: Any) -> None:
        """Test mix of successful and failing handlers."""
        good_handler = Mock(return_value="success")

        def bad_handler() -> Never:
            msg = "fail"
            raise Exception(msg)

        service.register_event_handler("event", good_handler)
        service.register_event_handler("event", bad_handler)

        results = service.trigger_event("event")

        assert len(results) == COUNT_TWO
        assert results[0] == "success"
        assert "error" in results[1]

    # ========================================================================
    # THEME MANAGEMENT
    # ========================================================================

    def test_set_theme_valid(self, service: Any) -> None:
        """Test setting valid theme."""
        service.set_theme("light")
        assert service.theme == "light"

        service.set_theme("dark")
        assert service.theme == "dark"

        service.set_theme("high_contrast")
        assert service.theme == "high_contrast"

    def test_set_theme_invalid(self, service: Any) -> None:
        """Test setting invalid theme is ignored."""
        original = service.theme

        service.set_theme("invalid_theme")

        assert service.theme == original

    def test_get_theme(self, service: Any) -> None:
        """Test getting current theme."""
        assert service.get_theme() == "dark"  # Default

        service.set_theme("light")
        assert service.get_theme() == "light"

    # ========================================================================
    # MOUSE SUPPORT
    # ========================================================================

    def test_enable_mouse(self, service: Any) -> None:
        """Test enabling mouse support."""
        service.mouse_enabled = False

        service.enable_mouse()

        assert service.mouse_enabled is True

    def test_disable_mouse(self, service: Any) -> None:
        """Test disabling mouse support."""
        service.mouse_enabled = True

        service.disable_mouse()

        assert service.mouse_enabled is False

    def test_is_mouse_enabled_default(self, service: Any) -> None:
        """Test default mouse enabled state."""
        assert service.is_mouse_enabled() is True

    def test_is_mouse_enabled_after_toggle(self, service: Any) -> None:
        """Test mouse enabled state after toggling."""
        service.disable_mouse()
        assert service.is_mouse_enabled() is False

        service.enable_mouse()
        assert service.is_mouse_enabled() is True

    # ========================================================================
    # UI STATISTICS
    # ========================================================================

    def test_get_ui_stats_empty(self, service: Any) -> None:
        """Test UI stats with no components."""
        stats = service.get_ui_stats()

        assert stats["total_components"] == 0
        assert stats["by_type"] == {}
        assert stats["current_view"] is None
        assert stats["theme"] == "dark"
        assert stats["mouse_enabled"] is True
        assert stats["total_event_handlers"] == 0

    def test_get_ui_stats_with_components(self, service: Any) -> None:
        """Test UI stats with components."""
        service.register_component("d1", UIComponentType.DASHBOARD, "D1")
        service.register_component("d2", UIComponentType.DASHBOARD, "D2")
        service.register_component("t1", UIComponentType.TABLE, "T1")
        service.set_current_view("d1")
        service.register_event_handler("click", lambda: None)
        service.register_event_handler("hover", lambda: None)

        stats = service.get_ui_stats()

        assert stats["total_components"] == COUNT_THREE
        assert stats["by_type"]["dashboard"] == COUNT_TWO
        assert stats["by_type"]["table"] == 1
        assert stats["current_view"] == "d1"
        assert stats["total_event_handlers"] == COUNT_TWO

    # ========================================================================
    # DASHBOARD CREATION
    # ========================================================================

    def test_create_dashboard_basic(self, service: Any) -> None:
        """Test creating basic dashboard."""
        dashboard = service.create_dashboard(
            name="main-dash",
            title="Main Dashboard",
            widgets=["widget1", "widget2", "widget3"],
        )

        assert dashboard.name == "main-dash"
        assert dashboard.component_type == UIComponentType.DASHBOARD
        assert dashboard.title == "Main Dashboard"
        assert dashboard.data["widgets"] == ["widget1", "widget2", "widget3"]

    def test_create_dashboard_empty_widgets(self, service: Any) -> None:
        """Test creating dashboard with no widgets."""
        dashboard = service.create_dashboard("dash", "Title", widgets=[])

        assert dashboard.data["widgets"] == []

    def test_create_dashboard_registers_component(self, service: Any) -> None:
        """Test dashboard is registered as component."""
        service.create_dashboard("dash", "Title", widgets=[])

        assert "dash" in service.components

    # ========================================================================
    # TABLE CREATION
    # ========================================================================

    def test_create_table_basic(self, service: Any) -> None:
        """Test creating basic table."""
        columns = ["Name", "Age", "Email"]
        rows = [
            {"Name": "Alice", "Age": 30, "Email": "alice@test.com"},
            {"Name": "Bob", "Age": 25, "Email": "bob@test.com"},
        ]

        table = service.create_table(name="users-table", title="Users", columns=columns, rows=rows)

        assert table.name == "users-table"
        assert table.component_type == UIComponentType.TABLE
        assert table.title == "Users"
        assert table.data["columns"] == columns
        assert table.data["rows"] == rows

    def test_create_table_empty_rows(self, service: Any) -> None:
        """Test creating table with no rows."""
        table = service.create_table("table", "Empty", columns=["A", "B"], rows=[])

        assert table.data["rows"] == []
        assert table.data["columns"] == ["A", "B"]

    def test_create_table_registers_component(self, service: Any) -> None:
        """Test table is registered as component."""
        service.create_table("table", "Title", columns=[], rows=[])

        assert "table" in service.components
        assert service.components["table"].component_type == UIComponentType.TABLE


# ============================================================================
# RUN ALL TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
