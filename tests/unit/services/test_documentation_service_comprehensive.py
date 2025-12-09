"""
Comprehensive tests for DocumentationService.

Tests all methods: register_endpoint, get_endpoint, list_endpoints,
register_schema, get_schema, list_schemas, add_example, get_examples,
generate_openapi_spec, generate_markdown_docs, get_documentation_stats.

Coverage target: 85%+
"""

import pytest
from tracertm.services.documentation_service import DocumentationService


class TestRegisterEndpoint:
    """Test register_endpoint method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return DocumentationService()

    def test_register_simple_endpoint(self, service):
        """Test registering simple endpoint."""
        result = service.register_endpoint(
            path="/api/items",
            method="GET",
            description="Get all items",
            parameters=[],
            response_schema={"type": "array"},
        )

        assert result["path"] == "/api/items"
        assert result["method"] == "GET"
        assert result["description"] == "Get all items"
        assert "registered_at" in result

    def test_register_endpoint_with_parameters(self, service):
        """Test registering endpoint with parameters."""
        params = [
            {"name": "id", "type": "string", "description": "Item ID"},
            {"name": "limit", "type": "integer", "description": "Max results"},
        ]

        result = service.register_endpoint(
            path="/api/items/{id}",
            method="GET",
            description="Get item by ID",
            parameters=params,
            response_schema={"type": "object"},
        )

        assert result["parameters"] == params

    def test_register_multiple_endpoints(self, service):
        """Test registering multiple endpoints."""
        service.register_endpoint(
            "/api/items", "GET", "List items", [], {}
        )
        service.register_endpoint(
            "/api/items", "POST", "Create item", [], {}
        )
        service.register_endpoint(
            "/api/items/{id}", "GET", "Get item", [], {}
        )

        assert len(service.endpoints) == 3


class TestGetEndpoint:
    """Test get_endpoint method."""

    @pytest.fixture
    def service(self):
        """Create service instance with endpoint."""
        svc = DocumentationService()
        svc.register_endpoint("/api/users", "GET", "List users", [], {})
        return svc

    def test_get_existing_endpoint(self, service):
        """Test getting existing endpoint."""
        result = service.get_endpoint("/api/users", "GET")

        assert result is not None
        assert result["path"] == "/api/users"
        assert result["method"] == "GET"

    def test_get_nonexistent_endpoint(self, service):
        """Test getting nonexistent endpoint."""
        result = service.get_endpoint("/api/nonexistent", "GET")
        assert result is None

    def test_get_wrong_method(self, service):
        """Test getting endpoint with wrong method."""
        result = service.get_endpoint("/api/users", "POST")
        assert result is None


class TestListEndpoints:
    """Test list_endpoints method."""

    @pytest.fixture
    def service(self):
        """Create service with multiple endpoints."""
        svc = DocumentationService()
        svc.register_endpoint("/api/items", "GET", "List", [], {})
        svc.register_endpoint("/api/items", "POST", "Create", [], {})
        svc.register_endpoint("/api/users", "GET", "List users", [], {})
        return svc

    def test_list_all_endpoints(self, service):
        """Test listing all endpoints."""
        result = service.list_endpoints()
        assert len(result) == 3

    def test_filter_by_method(self, service):
        """Test filtering by method."""
        result = service.list_endpoints(method="GET")
        assert len(result) == 2

    def test_filter_nonexistent_method(self, service):
        """Test filtering by nonexistent method."""
        result = service.list_endpoints(method="DELETE")
        assert len(result) == 0


class TestRegisterSchema:
    """Test register_schema method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        return DocumentationService()

    def test_register_schema(self, service):
        """Test registering schema."""
        schema = {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
            },
        }

        result = service.register_schema("Item", schema, "Item model")

        assert result["name"] == "Item"
        assert result["schema"] == schema
        assert result["description"] == "Item model"
        assert "registered_at" in result

    def test_register_multiple_schemas(self, service):
        """Test registering multiple schemas."""
        service.register_schema("Item", {"type": "object"}, "Item")
        service.register_schema("User", {"type": "object"}, "User")

        assert len(service.schemas) == 2


class TestGetSchema:
    """Test get_schema method."""

    @pytest.fixture
    def service(self):
        """Create service with schema."""
        svc = DocumentationService()
        svc.register_schema("Item", {"type": "object"}, "Item model")
        return svc

    def test_get_existing_schema(self, service):
        """Test getting existing schema."""
        result = service.get_schema("Item")

        assert result is not None
        assert result["name"] == "Item"

    def test_get_nonexistent_schema(self, service):
        """Test getting nonexistent schema."""
        result = service.get_schema("Nonexistent")
        assert result is None


class TestListSchemas:
    """Test list_schemas method."""

    @pytest.fixture
    def service(self):
        """Create service with schemas."""
        svc = DocumentationService()
        svc.register_schema("Item", {}, "Item")
        svc.register_schema("User", {}, "User")
        return svc

    def test_list_schemas(self, service):
        """Test listing all schemas."""
        result = service.list_schemas()
        assert len(result) == 2

    def test_list_empty_schemas(self):
        """Test listing with no schemas."""
        service = DocumentationService()
        result = service.list_schemas()
        assert result == []


class TestAddExample:
    """Test add_example method."""

    @pytest.fixture
    def service(self):
        """Create service instance."""
        svc = DocumentationService()
        svc.register_endpoint("/api/items", "POST", "Create item", [], {})
        return svc

    def test_add_example(self, service):
        """Test adding example."""
        result = service.add_example(
            endpoint_path="/api/items",
            method="POST",
            example_name="Create basic item",
            request={"title": "New Item"},
            response={"id": "123", "title": "New Item"},
        )

        assert result["name"] == "Create basic item"
        assert result["request"] == {"title": "New Item"}
        assert result["response"]["id"] == "123"

    def test_add_multiple_examples(self, service):
        """Test adding multiple examples."""
        service.add_example("/api/items", "POST", "Example 1", {}, {})
        service.add_example("/api/items", "POST", "Example 2", {}, {})

        examples = service.get_examples("/api/items", "POST")
        assert len(examples) == 2


class TestGetExamples:
    """Test get_examples method."""

    @pytest.fixture
    def service(self):
        """Create service with examples."""
        svc = DocumentationService()
        svc.add_example("/api/items", "GET", "Example", {}, {"items": []})
        return svc

    def test_get_existing_examples(self, service):
        """Test getting existing examples."""
        result = service.get_examples("/api/items", "GET")
        assert len(result) == 1

    def test_get_nonexistent_examples(self, service):
        """Test getting examples for nonexistent endpoint."""
        result = service.get_examples("/api/nonexistent", "GET")
        assert result == []


class TestGenerateOpenAPISpec:
    """Test generate_openapi_spec method."""

    @pytest.fixture
    def service(self):
        """Create service with endpoints and schemas."""
        svc = DocumentationService()
        svc.register_endpoint(
            "/api/items",
            "GET",
            "List all items",
            [{"name": "limit", "in": "query", "type": "integer"}],
            {"type": "array"},
        )
        svc.register_endpoint(
            "/api/items/{id}",
            "GET",
            "Get item by ID",
            [{"name": "id", "in": "path", "type": "string"}],
            {"type": "object"},
        )
        svc.register_schema("Item", {"type": "object", "properties": {}}, "Item")
        return svc

    def test_spec_structure(self, service):
        """Test OpenAPI spec has correct structure."""
        result = service.generate_openapi_spec()

        assert result["openapi"] == "3.0.0"
        assert "info" in result
        assert "paths" in result
        assert "components" in result

    def test_spec_info(self, service):
        """Test spec info section."""
        result = service.generate_openapi_spec()

        assert result["info"]["title"] == "TraceRTM API"
        assert result["info"]["version"] == "1.0.0"

    def test_spec_paths(self, service):
        """Test spec paths section."""
        result = service.generate_openapi_spec()

        assert "/api/items" in result["paths"]
        assert "/api/items/{id}" in result["paths"]
        assert "get" in result["paths"]["/api/items"]

    def test_spec_components(self, service):
        """Test spec components section."""
        result = service.generate_openapi_spec()

        assert "Item" in result["components"]["schemas"]

    def test_empty_spec(self):
        """Test spec with no endpoints."""
        service = DocumentationService()
        result = service.generate_openapi_spec()

        assert result["paths"] == {}


class TestGenerateMarkdownDocs:
    """Test generate_markdown_docs method."""

    @pytest.fixture
    def service(self):
        """Create service with endpoints."""
        svc = DocumentationService()
        svc.register_endpoint(
            "/api/items",
            "GET",
            "List all items",
            [{"name": "limit", "type": "integer", "description": "Max results"}],
            {"type": "array"},
        )
        return svc

    def test_markdown_header(self, service):
        """Test markdown has title."""
        result = service.generate_markdown_docs()

        assert "# TraceRTM API Documentation" in result

    def test_markdown_endpoints_section(self, service):
        """Test markdown has endpoints section."""
        result = service.generate_markdown_docs()

        assert "## Endpoints" in result

    def test_markdown_endpoint_details(self, service):
        """Test markdown includes endpoint details."""
        result = service.generate_markdown_docs()

        assert "### GET /api/items" in result
        assert "List all items" in result

    def test_markdown_parameters(self, service):
        """Test markdown includes parameters."""
        result = service.generate_markdown_docs()

        assert "**Parameters:**" in result
        assert "`limit`" in result
        assert "Max results" in result

    def test_markdown_response(self, service):
        """Test markdown includes response schema."""
        result = service.generate_markdown_docs()

        assert "**Response:**" in result

    def test_empty_docs(self):
        """Test docs with no endpoints."""
        service = DocumentationService()
        result = service.generate_markdown_docs()

        assert "# TraceRTM API Documentation" in result
        assert "## Endpoints" in result


class TestGetDocumentationStats:
    """Test get_documentation_stats method."""

    @pytest.fixture
    def service(self):
        """Create service with content."""
        svc = DocumentationService()
        svc.register_endpoint("/api/items", "GET", "List", [], {})
        svc.register_endpoint("/api/items", "POST", "Create", [], {})
        svc.register_schema("Item", {}, "Item")
        svc.add_example("/api/items", "GET", "Example 1", {}, {})
        svc.add_example("/api/items", "GET", "Example 2", {}, {})
        return svc

    def test_stats_total_endpoints(self, service):
        """Test stats include total endpoints."""
        result = service.get_documentation_stats()
        assert result["total_endpoints"] == 2

    def test_stats_total_schemas(self, service):
        """Test stats include total schemas."""
        result = service.get_documentation_stats()
        assert result["total_schemas"] == 1

    def test_stats_total_examples(self, service):
        """Test stats include total examples."""
        result = service.get_documentation_stats()
        assert result["total_examples"] == 2

    def test_stats_methods(self, service):
        """Test stats include methods list."""
        result = service.get_documentation_stats()
        assert "GET" in result["methods"]
        assert "POST" in result["methods"]

    def test_empty_stats(self):
        """Test stats with no content."""
        service = DocumentationService()
        result = service.get_documentation_stats()

        assert result["total_endpoints"] == 0
        assert result["total_schemas"] == 0
        assert result["total_examples"] == 0
        assert result["methods"] == []


class TestServiceInit:
    """Test service initialization."""

    def test_init_creates_empty_collections(self):
        """Test initialization creates empty collections."""
        service = DocumentationService()

        assert service.endpoints == {}
        assert service.schemas == {}
        assert service.examples == {}
