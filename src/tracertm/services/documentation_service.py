"""Service for API documentation and reference.

Functional Requirements: FR-AI-010
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class DocumentationService:
    """Service for managing API documentation."""

    def __init__(self) -> None:
        """Initialize."""
        self.endpoints: dict[str, dict[str, Any]] = {}
        self.schemas: dict[str, dict[str, Any]] = {}
        self.examples: dict[str, list[dict[str, Any]]] = {}

    def register_endpoint(
        self,
        path: str,
        method: str,
        description: str,
        parameters: list[dict[str, Any]],
        response_schema: dict[str, Any],
    ) -> dict[str, Any]:
        """Register an API endpoint."""
        endpoint_key = f"{method} {path}"

        endpoint = {
            "path": path,
            "method": method,
            "description": description,
            "parameters": parameters,
            "response_schema": response_schema,
            "registered_at": datetime.now(UTC).isoformat(),
        }

        self.endpoints[endpoint_key] = endpoint
        return endpoint

    def get_endpoint(self, path: str, method: str) -> dict[str, Any] | None:
        """Get endpoint documentation."""
        endpoint_key = f"{method} {path}"
        return self.endpoints.get(endpoint_key)

    def list_endpoints(self, method: str | None = None) -> list[dict[str, Any]]:
        """List all endpoints."""
        endpoints = list(self.endpoints.values())

        if method:
            endpoints = [e for e in endpoints if e["method"] == method]

        return endpoints

    def register_schema(
        self,
        name: str,
        schema: dict[str, Any],
        description: str,
    ) -> dict[str, Any]:
        """Register a data schema."""
        schema_def = {
            "name": name,
            "schema": schema,
            "description": description,
            "registered_at": datetime.now(UTC).isoformat(),
        }

        self.schemas[name] = schema_def
        return schema_def

    def get_schema(self, name: str) -> dict[str, Any] | None:
        """Get schema definition."""
        return self.schemas.get(name)

    def list_schemas(self) -> list[dict[str, Any]]:
        """List all schemas."""
        return list(self.schemas.values())

    def add_example(
        self,
        endpoint_path: str,
        method: str,
        example_name: str,
        request: dict[str, Any],
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """Add example for endpoint."""
        endpoint_key = f"{method} {endpoint_path}"

        if endpoint_key not in self.examples:
            self.examples[endpoint_key] = []

        example = {
            "name": example_name,
            "request": request,
            "response": response,
        }

        self.examples[endpoint_key].append(example)
        return example

    def get_examples(self, endpoint_path: str, method: str) -> list[dict[str, Any]]:
        """Get examples for endpoint."""
        endpoint_key = f"{method} {endpoint_path}"
        return self.examples.get(endpoint_key, [])

    def generate_openapi_spec(self) -> dict[str, Any]:
        """Generate OpenAPI specification."""
        paths: dict[str, Any] = {}

        for endpoint in self.endpoints.values():
            path = endpoint["path"]
            method = endpoint["method"].lower()

            if path not in paths:
                paths[path] = {}

            paths[path][method] = {
                "summary": endpoint["description"],
                "parameters": endpoint["parameters"],
                "responses": {
                    "200": {
                        "description": "Success",
                        "schema": endpoint["response_schema"],
                    },
                },
            }

        return {
            "openapi": "3.0.0",
            "info": {
                "title": "TraceRTM API",
                "version": "1.0.0",
                "description": "Traceability Requirements Management API",
            },
            "paths": paths,
            "components": {"schemas": {name: schema["schema"] for name, schema in self.schemas.items()}},
        }

    def generate_markdown_docs(self) -> str:
        """Generate Markdown documentation."""
        md = "# TraceRTM API Documentation\n\n"
        md += "## Endpoints\n\n"

        for endpoint in self.endpoints.values():
            md += f"### {endpoint['method']} {endpoint['path']}\n\n"
            md += f"{endpoint['description']}\n\n"

            if endpoint["parameters"]:
                md += "**Parameters:**\n\n"
                for param in endpoint["parameters"]:
                    name = param.get("name", "unknown")
                    ptype = param.get("type", "unknown")
                    desc = param.get("description", "")
                    md += f"- `{name}` ({ptype}): {desc}\n"
                md += "\n"

            md += "**Response:**\n\n"
            md += f"```json\n{endpoint['response_schema']}\n```\n\n"

        return md

    def get_documentation_stats(self) -> dict[str, Any]:
        """Get documentation statistics."""
        return {
            "total_endpoints": len(self.endpoints),
            "total_schemas": len(self.schemas),
            "total_examples": sum(len(e) for e in self.examples.values()),
            "methods": list({e["method"] for e in self.endpoints.values()}),
        }
