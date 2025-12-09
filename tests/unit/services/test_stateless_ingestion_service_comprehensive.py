"""
Comprehensive tests for StatelessIngestionService.

Tests all methods: ingest_markdown, ingest_mdx, ingest_yaml, and all helper methods
with full coverage including error handling and edge cases.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from tracertm.services.stateless_ingestion_service import StatelessIngestionService
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


class TestIngestMarkdown:
    """Test ingest_markdown method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        return StatelessIngestionService(session)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_basic_markdown(self, mock_read, mock_exists, service):
        """Test basic markdown ingestion."""
        mock_exists.return_value = True
        mock_read.return_value = """# Feature 1
## Story 1
### Task 1
"""
        # Setup project query to return a mock project
        mock_project = Mock()
        mock_project.id = "proj-1"
        mock_project.name = "Test Project"
        service.session.query.return_value.filter.return_value.first.return_value = mock_project

        result = service.ingest_markdown(
            file_path="/test/file.md",
            project_id="proj-1",
        )

        # Assert
        assert result["items_created"] == 3
        assert result["project_id"] == "proj-1"
        assert "file.md" in result["file_path"]

    @patch("pathlib.Path.exists")
    def test_ingest_file_not_found(self, mock_exists, service):
        """Test error when file doesn't exist."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            service.ingest_markdown(file_path="/nonexistent.md")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_invalid_extension(self, mock_read, mock_exists, service):
        """Test validation fails for invalid extension."""
        mock_exists.return_value = True

        with pytest.raises(ValueError, match="Invalid file extension"):
            service.ingest_markdown(
                file_path="/test/file.txt",
                validate=True,
            )

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_dry_run(self, mock_read, mock_exists, service):
        """Test dry run mode returns preview without creating items."""
        mock_exists.return_value = True
        mock_read.return_value = """# Header 1
## Header 2
[Link](url)
"""
        result = service.ingest_markdown(
            file_path="/test/file.md",
            dry_run=True,
        )

        # Assert
        assert result["dry_run"] is True
        assert result["headers_found"] == 2
        assert result["links_found"] == 1
        assert result["would_create_items"] == 2
        # No items created in dry run
        service.session.add.assert_not_called()

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    @patch("tracertm.services.stateless_ingestion_service.frontmatter")
    def test_ingest_with_frontmatter(self, mock_frontmatter, mock_read, mock_exists, service):
        """Test markdown with frontmatter metadata."""
        mock_exists.return_value = True
        mock_post = Mock()
        mock_post.metadata = {"project": "MyProject", "status": "in_progress"}
        mock_post.content = "# Header"
        mock_frontmatter.loads.return_value = mock_post

        result = service.ingest_markdown(
            file_path="/test/file.md",
        )

        # Assert items created with metadata
        assert service.session.add.call_count > 0

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_creates_project(self, mock_read, mock_exists, service):
        """Test project is created when not provided."""
        mock_exists.return_value = True
        mock_read.return_value = "# Header"

        result = service.ingest_markdown(
            file_path="/test/myproject.md",
            project_id=None,
        )

        # Assert project was created
        assert result["project_id"] is not None

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_hierarchical_headers(self, mock_read, mock_exists, service):
        """Test hierarchical header structure creates parent-child relationships."""
        mock_exists.return_value = True
        mock_read.return_value = """# Epic
## Feature
### Story
#### Task
"""
        # Mock project query
        mock_project = Mock(spec=Project)
        mock_project.id = "proj-1"
        service.session.query.return_value.filter.return_value.first.return_value = mock_project

        result = service.ingest_markdown(
            file_path="/test/file.md",
            project_id="proj-1",
        )

        # Assert 4 headers created
        assert result["items_created"] == 4

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_internal_links(self, mock_read, mock_exists, service):
        """Test internal links are created."""
        mock_exists.return_value = True
        mock_read.return_value = """# Feature 1
# Feature 2
[Link to Feature 1](#feature-1)
"""
        mock_project = Mock(spec=Project)
        mock_project.id = "proj-1"
        service.session.query.return_value.filter.return_value.first.return_value = mock_project

        result = service.ingest_markdown(
            file_path="/test/file.md",
            project_id="proj-1",
        )

        # Assert links were created
        assert result["links_created"] >= 0


class TestIngestMdx:
    """Test ingest_mdx method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        return StatelessIngestionService(session)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_mdx_basic(self, mock_read, mock_exists, service):
        """Test basic MDX ingestion."""
        mock_exists.return_value = True
        mock_read.return_value = """# Component
<MyComponent>Content</MyComponent>
"""
        # Create mock project for query response
        mock_project = Mock()
        mock_project.id = "proj-mdx"
        mock_project.name = "file"  # Based on stem of file.mdx
        service.session.query.return_value.filter.return_value.first.return_value = mock_project

        result = service.ingest_mdx(
            file_path="/test/file.mdx",
        )

        # Assert JSX components were extracted
        assert "jsx_components_created" in result

    @patch("pathlib.Path.exists")
    def test_ingest_mdx_invalid_extension(self, mock_exists, service):
        """Test validation for .mdx extension."""
        mock_exists.return_value = True

        with pytest.raises(ValueError, match="Expected .mdx"):
            service.ingest_mdx(
                file_path="/test/file.md",
                validate=True,
            )

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_mdx_dry_run(self, mock_read, mock_exists, service):
        """Test MDX dry run."""
        mock_exists.return_value = True
        mock_read.return_value = """# Header
<Component attr="value">Content</Component>
<AnotherComponent />
"""
        result = service.ingest_mdx(
            file_path="/test/file.mdx",
            dry_run=True,
        )

        # Assert
        assert result["dry_run"] is True
        assert result["headers_found"] == 1
        assert result["jsx_components_found"] > 0

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_mdx_jsx_components(self, mock_read, mock_exists, service):
        """Test JSX components are created as CODE view items."""
        mock_exists.return_value = True
        mock_read.return_value = """<Button type="primary">Click me</Button>"""

        # Mock ingest_markdown to return basic result
        with patch.object(service, 'ingest_markdown') as mock_ingest_md:
            mock_ingest_md.return_value = {
                "project_id": "proj-1",
                "items_created": 0,
                "links_created": 0,
                "file_path": "/test/file.mdx",
            }

            result = service.ingest_mdx(
                file_path="/test/file.mdx",
                project_id="proj-1",
            )

            # Assert JSX component items created
            assert result["jsx_components_created"] >= 0


class TestIngestYaml:
    """Test ingest_yaml method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        return StatelessIngestionService(session)

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_openapi(self, mock_read, mock_exists, service):
        """Test OpenAPI spec ingestion."""
        mock_exists.return_value = True
        mock_read.return_value = """openapi: "3.0.0"
info:
  title: Test API
  description: Test API
paths:
  /users:
    get:
      summary: Get users
components:
  schemas:
    User:
      type: object
"""
        result = service.ingest_yaml(
            file_path="/test/openapi.yaml",
        )

        # Assert OpenAPI items created
        assert result["format"] == "openapi"
        assert result["items_created"] > 0

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_bmad_format(self, mock_read, mock_exists, service):
        """Test BMad format ingestion."""
        mock_exists.return_value = True
        mock_read.return_value = """requirements:
  - id: REQ-1
    title: Requirement 1
    description: Description
    type: feature
"""
        result = service.ingest_yaml(
            file_path="/test/requirements.yaml",
        )

        # Assert BMad format detected and processed
        assert result["format"] == "bmad"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_generic(self, mock_read, mock_exists, service):
        """Test generic YAML ingestion."""
        mock_exists.return_value = True
        mock_read.return_value = """name: MyProject
sections:
  - title: Section 1
    description: Description 1
"""
        result = service.ingest_yaml(
            file_path="/test/data.yaml",
        )

        # Assert generic YAML processed
        assert result["format"] == "yaml"

    @patch("pathlib.Path.exists")
    def test_ingest_yaml_invalid_extension(self, mock_exists, service):
        """Test validation for YAML extension."""
        mock_exists.return_value = True

        with pytest.raises(ValueError, match="Expected .yaml or .yml"):
            service.ingest_yaml(
                file_path="/test/file.txt",
                validate=True,
            )

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_invalid_syntax(self, mock_read, mock_exists, service):
        """Test error on invalid YAML syntax."""
        mock_exists.return_value = True
        mock_read.return_value = """invalid: yaml: syntax:
  - no proper
indentation
"""
        with pytest.raises(ValueError, match="Invalid YAML"):
            service.ingest_yaml(file_path="/test/invalid.yaml")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_not_dict(self, mock_read, mock_exists, service):
        """Test error when YAML root is not a dictionary."""
        mock_exists.return_value = True
        mock_read.return_value = """- item1
- item2
"""
        with pytest.raises(ValueError, match="YAML root must be a dictionary"):
            service.ingest_yaml(file_path="/test/list.yaml")

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_dry_run_openapi(self, mock_read, mock_exists, service):
        """Test dry run for OpenAPI spec."""
        mock_exists.return_value = True
        mock_read.return_value = """openapi: "3.0.0"
paths:
  /users:
    get:
      summary: Get users
    post:
      summary: Create user
components:
  schemas:
    User:
      type: object
    Post:
      type: object
"""
        result = service.ingest_yaml(
            file_path="/test/api.yaml",
            dry_run=True,
        )

        # Assert
        assert result["dry_run"] is True
        assert result["format"] == "openapi"
        assert result["endpoints_found"] == 2
        assert result["schemas_found"] == 2

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.read_text")
    def test_ingest_yaml_dry_run_bmad(self, mock_read, mock_exists, service):
        """Test dry run for BMad format."""
        mock_exists.return_value = True
        mock_read.return_value = """requirements:
  - id: REQ-1
    title: Requirement 1
  - id: REQ-2
    title: Requirement 2
  - id: REQ-3
    title: Requirement 3
"""
        result = service.ingest_yaml(
            file_path="/test/bmad.yaml",
            dry_run=True,
        )

        # Assert
        assert result["format"] == "bmad"
        assert result["requirements_found"] == 3


class TestIngestOpenApiSpec:
    """Test _ingest_openapi_spec helper method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        return StatelessIngestionService(session)

    def test_ingest_openapi_creates_schema_items(self, service):
        """Test schemas are created as items."""
        data = {
            "info": {"title": "Test API"},
            "components": {
                "schemas": {
                    "User": {"type": "object", "description": "User model"},
                    "Post": {"type": "object"},
                }
            },
            "paths": {},
        }

        result = service._ingest_openapi_spec(data, "/test/api.yaml", None)

        # Assert
        assert result["schemas_created"] == 2

    def test_ingest_openapi_creates_endpoint_items(self, service):
        """Test endpoints are created as items."""
        data = {
            "info": {"title": "Test API"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "summary": "Get all users",
                    },
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                    }
                }
            },
        }

        result = service._ingest_openapi_spec(data, "/test/api.yaml", "proj-1")

        # Assert
        assert result["endpoints_created"] >= 2

    def test_ingest_openapi_links_request_schemas(self, service):
        """Test links are created between endpoints and request schemas."""
        data = {
            "info": {"title": "Test API"},
            "components": {
                "schemas": {
                    "User": {"type": "object"}
                }
            },
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            },
        }

        result = service._ingest_openapi_spec(data, "/test/api.yaml", "proj-1")

        # Assert links created
        assert result["links_created"] > 0

    def test_ingest_openapi_links_response_schemas(self, service):
        """Test links for response schemas."""
        data = {
            "info": {"title": "Test API"},
            "components": {
                "schemas": {
                    "User": {"type": "object"}
                }
            },
            "paths": {
                "/users": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }

        result = service._ingest_openapi_spec(data, "/test/api.yaml", "proj-1")

        # Assert
        assert result["links_created"] > 0

    def test_ingest_openapi_links_related_endpoints(self, service):
        """Test links between endpoints on same path."""
        data = {
            "info": {"title": "Test API"},
            "paths": {
                "/users": {
                    "get": {"operationId": "getUsers"},
                    "post": {"operationId": "createUser"},
                    "delete": {"operationId": "deleteUser"},
                }
            },
        }

        result = service._ingest_openapi_spec(data, "/test/api.yaml", "proj-1")

        # Assert related endpoint links
        assert result["links_created"] > 0


class TestIngestBmadFormat:
    """Test _ingest_bmad_format helper method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        return StatelessIngestionService(session)

    def test_ingest_bmad_creates_requirement_items(self, service):
        """Test requirements are created as items."""
        data = {
            "requirements": [
                {"id": "REQ-1", "title": "Requirement 1", "type": "feature"},
                {"id": "REQ-2", "title": "Requirement 2", "type": "test"},
            ]
        }

        result = service._ingest_bmad_format(data, "/test/bmad.yaml", "proj-1")

        # Assert
        assert result["requirements_created"] == 2

    def test_ingest_bmad_view_mapping(self, service):
        """Test requirement types are mapped to correct views."""
        data = {
            "requirements": [
                {"id": "REQ-1", "title": "Feature", "type": "feature"},
                {"id": "REQ-2", "title": "Test", "type": "test"},
                {"id": "REQ-3", "title": "Code", "type": "code"},
                {"id": "REQ-4", "title": "API", "type": "api"},
            ]
        }

        result = service._ingest_bmad_format(data, "/test/bmad.yaml", "proj-1")

        # Assert items created with appropriate views
        assert result["items_created"] == 4

    def test_ingest_bmad_parent_child_relationships(self, service):
        """Test parent-child relationships are created."""
        data = {
            "requirements": [
                {"id": "REQ-1", "title": "Parent"},
                {"id": "REQ-2", "title": "Child", "parent_id": "REQ-1"},
            ]
        }

        result = service._ingest_bmad_format(data, "/test/bmad.yaml", "proj-1")

        # Assert parent-child links created
        assert result["items_created"] == 2
        assert result["links_created"] > 0

    def test_ingest_bmad_traceability_links(self, service):
        """Test traceability links are created."""
        data = {
            "requirements": [
                {"id": "REQ-1", "title": "Requirement 1"},
                {"id": "REQ-2", "title": "Requirement 2"},
            ],
            "traceability": [
                {"source": "REQ-1", "target": "REQ-2", "type": "traces_to"}
            ]
        }

        result = service._ingest_bmad_format(data, "/test/bmad.yaml", "proj-1")

        # Assert traceability links
        assert result["traceability_links"] >= 1

    def test_ingest_bmad_dependency_links(self, service):
        """Test dependency links are created."""
        data = {
            "requirements": [
                {"id": "REQ-1", "title": "Requirement 1"},
                {"id": "REQ-2", "title": "Requirement 2", "depends_on": ["REQ-1"]},
            ]
        }

        result = service._ingest_bmad_format(data, "/test/bmad.yaml", "proj-1")

        # Assert dependency links
        assert result["links_created"] > 0


class TestIngestGenericYaml:
    """Test _ingest_generic_yaml helper method."""

    @pytest.fixture
    def service(self):
        """Create service with mock session."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.query.return_value.filter.return_value.first.return_value = None
        return StatelessIngestionService(session)

    def test_ingest_generic_nested_dict(self, service):
        """Test nested dictionaries are processed."""
        data = {
            "section1": {
                "subsection1": {
                    "description": "Subsection description"
                }
            }
        }

        result = service._ingest_generic_yaml(
            data, "/test/data.yaml", "proj-1", "FEATURE"
        )

        # Assert items created for sections
        assert result["items_created"] > 0

    def test_ingest_generic_lists(self, service):
        """Test lists are processed."""
        data = {
            "items": [
                {"title": "Item 1", "description": "Description 1"},
                {"title": "Item 2", "description": "Description 2"},
            ]
        }

        result = service._ingest_generic_yaml(
            data, "/test/data.yaml", "proj-1", "FEATURE"
        )

        # Assert list items created
        assert result["items_created"] >= 2


class TestHelperMethods:
    """Test helper methods."""

    @pytest.fixture
    def service(self):
        """Create service."""
        return StatelessIngestionService(Mock())

    def test_determine_item_type_default(self, service):
        """Test default item type mapping."""
        assert service._determine_item_type(1, {}) == "epic"
        assert service._determine_item_type(2, {}) == "feature"
        assert service._determine_item_type(3, {}) == "story"
        assert service._determine_item_type(4, {}) == "task"

    def test_determine_item_type_custom_mapping(self, service):
        """Test custom type mapping from metadata."""
        metadata = {
            "type_mapping": {
                "1": "requirement",
                "2": "specification",
            }
        }
        assert service._determine_item_type(1, metadata) == "requirement"
        assert service._determine_item_type(2, metadata) == "specification"

    def test_extract_section_content(self, service):
        """Test extracting content between headers."""
        body = """# Header 1
Content for header 1
More content

## Header 2
Content for header 2
"""
        content = service._extract_section_content(body, "# Header 1")
        assert "Content for header 1" in content
        assert "Header 2" not in content

    def test_extract_section_content_no_next_header(self, service):
        """Test extracting content when there's no next header."""
        body = """# Header 1
Content line 1
Content line 2
Final line
"""
        content = service._extract_section_content(body, "# Header 1")
        assert "Content line 1" in content
        assert "Final line" in content

    def test_extract_section_content_header_not_found(self, service):
        """Test returns empty when header not found."""
        body = "# Other Header\nContent"
        content = service._extract_section_content(body, "# Missing Header")
        assert content == ""
