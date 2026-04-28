"""
Utilities for generating repeatable test data.
"""

import re
import uuid as uuid_lib
from datetime import datetime
from typing import Any


class DataGenerator:
    """
    Generate test data for entities with guaranteed uniqueness.
    """

    @staticmethod
    def timestamp() -> str:
        """
        Generate timestamp string for unique identifiers.
        """
        return datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]

    @staticmethod
    def unique_id(prefix: str = "") -> str:
        """
        Generate unique identifier with optional prefix.
        """
        ts = DataGenerator.timestamp()
        return f"{prefix}{ts}" if prefix else ts

    @staticmethod
    def uuid() -> str:
        """
        Generate a random UUID string.
        """
        return str(uuid_lib.uuid4())

    @staticmethod
    def slug_from_uuid(prefix: str = "") -> str:
        """
        Generate a slug-safe unique identifier.
        """
        unique_slug = str(uuid_lib.uuid4())[:8]
        unique_slug = re.sub(r"[^a-z0-9-]", "", unique_slug.lower())
        if not unique_slug or not unique_slug[0].isalpha():
            unique_slug = f"{prefix or 'test'}{unique_slug}"
        elif prefix:
            unique_slug = f"{prefix}-{unique_slug}"
        return unique_slug

    @staticmethod
    def organization_data(name: str | None = None) -> dict[str, Any]:
        """
        Generate organization test data with valid slug.
        """
        unique_slug = DataGenerator.slug_from_uuid("org")
        return {
            "name": name or f"Test Org {unique_slug}",
            "slug": unique_slug,
            "description": "Automated test organization",
            "type": "team",
        }

    @staticmethod
    def project_data(
        name: str | None = None,
        organization_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate project test data.
        """
        unique_slug = DataGenerator.slug_from_uuid("proj")
        data = {
            "name": name or f"Test Project {unique_slug}",
            "slug": unique_slug,
            "description": "Automated test project",
        }
        if organization_id:
            data["organization_id"] = organization_id
        return data

    @staticmethod
    def document_data(
        name: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate document test data.
        """
        unique_slug = DataGenerator.slug_from_uuid("doc")
        data = {
            "name": name or f"Test Document {unique_slug}",
            "slug": unique_slug,
            "description": "Automated test document",
            "type": "specification",
        }
        if project_id:
            data["project_id"] = project_id
        return data

    @staticmethod
    def requirement_data(
        name: str | None = None,
        document_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate requirement test data.
        """
        unique = DataGenerator.unique_id()
        data = {
            "name": name or f"REQ-TEST-{unique}",
            "description": "Automated test requirement",
            "priority": "medium",
            "status": "active",
        }
        if document_id:
            data["document_id"] = document_id
        return data

    @staticmethod
    def test_data(
        title: str | None = None,
        project_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Generate test case data.
        """
        unique = DataGenerator.unique_id()
        data = {
            "title": title or f"Test Case {unique}",
            "description": "Automated test case",
            "status": "pending",
            "priority": "medium",
        }
        if project_id:
            data["project_id"] = project_id
        return data

    @staticmethod
    def batch_data(
        entity_type: str,
        count: int = 3,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """
        Generate batch test data for a given entity type.
        """
        generators = {
            "organization": DataGenerator.organization_data,
            "project": DataGenerator.project_data,
            "document": DataGenerator.document_data,
            "requirement": DataGenerator.requirement_data,
            "test": DataGenerator.test_data,
        }
        generator = generators.get(entity_type)
        if not generator:
            return []
        return [generator(**kwargs) for _ in range(count)]


__all__ = ["DataGenerator"]
