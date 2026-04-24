#!/usr/bin/env python3
"""Script to create 5 dense, complete projects with comprehensive data.

Works with both PostgreSQL and SQLite.

Usage:
    python scripts/create_dense_projects.py
    # Or with psql:
    psql -d your_database -f scripts/create-dense-projects.sql
"""

import logging
import os
import pathlib
import sys
import uuid
from datetime import datetime, timedelta
from random import choice, randint

logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, pathlib.Path(pathlib.Path(pathlib.Path(__file__).resolve()).parent).parent)

import contextlib

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

# Database connection
database_url = os.getenv("DATABASE_URL") or "sqlite:///./tracertm.db"
engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

# Project configurations
PROJECTS = [
    {
        "name": "E-Commerce Platform",
        "description": "Full-featured online shopping platform with payment integration, inventory management, and order processing",
        "domain": "fullstack",
        "item_count": 500,
        "link_count": 300,
    },
    {
        "name": "Healthcare Management System",
        "description": "HIPAA-compliant patient records, appointment scheduling, and medical billing system",
        "domain": "backend",
        "item_count": 500,
        "link_count": 300,
    },
    {
        "name": "Real-Time Analytics Dashboard",
        "description": "Data visualization platform with real-time streaming, ML predictions, and interactive charts",
        "domain": "data",
        "item_count": 500,
        "link_count": 300,
    },
    {
        "name": "Mobile Banking App",
        "description": "Secure mobile banking application with biometric auth, transfers, bill pay, and investment tracking",
        "domain": "mobile",
        "item_count": 500,
        "link_count": 300,
    },
    {
        "name": "DevOps Automation Platform",
        "description": "CI/CD pipeline automation, infrastructure as code, monitoring, and deployment orchestration",
        "domain": "devops",
        "item_count": 500,
        "link_count": 300,
    },
]

ITEM_TYPES = ["requirement", "feature", "code", "test", "api", "database", "wireframe", "documentation", "deployment"]
STATUSES = ["pending", "in_progress", "completed", "blocked"]
PRIORITIES = ["low", "medium", "high", "critical"]
LINK_TYPES = ["implements", "tests", "depends_on", "relates_to", "validates", "blocks"]

ITEM_TITLES = {
    "requirement": [
        "User authentication",
        "Payment processing",
        "Data encryption",
        "API rate limiting",
        "Real-time notifications",
    ],
    "feature": ["User dashboard", "Search functionality", "Export reports", "Bulk operations", "Dark mode"],
    "code": lambda i: f"src/modules/module_{i}.ts",
    "test": ["Unit test", "Integration test", "E2E test", "Performance test", "Security test"],
    "api": [
        "GET /api/v1/users",
        "POST /api/v1/orders",
        "PUT /api/v1/products",
        "DELETE /api/v1/cart",
        "PATCH /api/v1/profile",
    ],
    "database": ["users table", "orders table", "products table", "payments table", "inventory table"],
    "wireframe": ["Login screen", "Dashboard", "Product page", "Checkout flow", "Settings page"],
    "documentation": ["API documentation", "User guide", "Architecture diagram", "Deployment guide", "Troubleshooting"],
    "deployment": ["Production", "Staging", "Development", "CI/CD pipeline", "Monitoring"],
}


def create_project(session: Session, config: dict) -> str:
    """Create a project and return its ID."""
    import json

    project_id = str(uuid.uuid4())
    created_at = datetime.now() - timedelta(days=randint(30, 90))

    # Store description in metadata since projects table doesn't have description column
    metadata = {"domain": config["domain"], "priority": "high", "description": config["description"]}

    # Generate slug from name
    slug = config["name"].lower().replace(" ", "-").replace("'", "").replace(",", "")

    # Temporarily disable the trigger to avoid project_members issues
    try:
        session.execute(text("ALTER TABLE projects DISABLE TRIGGER ALL"))
    except Exception:  # Trigger might not exist or already disabled
        pass

    try:
        session.execute(
            text("""
                INSERT INTO projects (id, name, slug, metadata, status, created_at, updated_at)
                VALUES (:id, :name, :slug, CAST(:metadata AS jsonb), 'active', :created_at, :updated_at)
            """),
            {
                "id": project_id,
                "name": config["name"],
                "slug": slug,
                "metadata": json.dumps(metadata),
                "created_at": created_at,
                "updated_at": datetime.now(),
            },
        )
    finally:
        with contextlib.suppress(Exception):
            session.execute(text("ALTER TABLE projects ENABLE TRIGGER ALL"))
    session.commit()
    return project_id


def create_items(session: Session, project_id: str, count: int) -> None:
    """Create items for a project."""
    items = []
    for i in range(1, count + 1):
        item_type = choice(ITEM_TYPES)
        status = choice(STATUSES)
        priority = choice(PRIORITIES)
        item_id = str(uuid.uuid4())

        # Generate title based on type
        if item_type == "code":
            code_gen = ITEM_TITLES.get("code")
            title = code_gen(i) if callable(code_gen) else f"CODE-{i}"
        else:
            titles_for_type = ITEM_TITLES.get(item_type, ["Item"])
            title_base = choice(titles_for_type) if isinstance(titles_for_type, list) and titles_for_type else "Item"
            if item_type == "requirement":
                title = f"REQ-{i}: {title_base}"
            elif item_type == "feature":
                title = f"Feature {i}: {title_base}"
            elif item_type == "test":
                title = f"Test {i}: {title_base}"
            elif item_type == "api":
                title = f"API {i}: {title_base}"
            elif item_type == "database":
                title = f"DB Schema {i}: {title_base}"
            elif item_type == "wireframe":
                title = f"Wireframe {i}: {title_base}"
            elif item_type == "documentation":
                title = f"Doc {i}: {title_base}"
            else:
                title = f"Deploy {i}: {title_base}"

        created_at = datetime.now() - timedelta(days=randint(1, 30))
        updated_at = created_at + timedelta(days=randint(0, 7))

        # Map priority string to integer (0=low, 1=medium, 2=high, 3=critical)
        priority_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        priority_int = priority_map.get(priority, 1)

        # Map status to database values
        status_map = {"pending": "open", "in_progress": "in_progress", "completed": "closed", "blocked": "blocked"}
        db_status = status_map.get(status, "open")

        session.execute(
            text("""
                INSERT INTO items (
                    id, project_id, title, description, type, status, priority,
                    created_at, updated_at
                ) VALUES (
                    :id, :project_id, :title, :description, :type, :status, :priority,
                    :created_at, :updated_at
                )
            """),
            {
                "id": item_id,
                "project_id": project_id,
                "title": title,
                "description": f"Comprehensive {item_type} implementation for project requirements. Includes detailed specifications, implementation notes, and testing considerations.",
                "type": item_type,
                "status": db_status,
                "priority": priority_int,
                "created_at": created_at,
                "updated_at": updated_at,
            },
        )
        items.append(item_id)

        if i % 100 == 0:
            session.commit()

    session.commit()
    return items


def create_links(session: Session, _project_id: str, item_ids: list, count: int) -> None:
    """Create traceability links between items."""
    links_created = 0
    for _ in range(count):
        source_id = choice(item_ids)
        target_id = choice([id for id in item_ids if id != source_id])
        link_type = choice(LINK_TYPES)
        link_id = str(uuid.uuid4())

        created_at = datetime.now() - timedelta(days=randint(1, 20))

        try:
            session.execute(
                text("""
                    INSERT INTO links (
                        id, source_id, target_id, link_type, metadata,
                        created_at
                    ) VALUES (
                        :id, :source_id, :target_id, :link_type, CAST(:metadata AS jsonb),
                        :created_at
                    )
                """),
                {
                    "id": link_id,
                    "source_id": source_id,
                    "target_id": target_id,
                    "link_type": link_type,
                    "metadata": "{}",
                    "created_at": created_at,
                },
            )
            links_created += 1

            if links_created % 100 == 0:
                session.commit()
        except Exception as e:
            # Skip duplicate or invalid links
            logger.debug("Skip link: %s", e)
            continue

    session.commit()
    return links_created


def main() -> None:
    """Main function to create 5 dense projects."""
    session = SessionLocal()

    try:
        for config in PROJECTS:
            # Create project
            project_id = create_project(session, config)

            # Create items
            item_count = int(config["item_count"]) if isinstance(config.get("item_count"), (int, str)) else 500
            link_count = int(config["link_count"]) if isinstance(config.get("link_count"), (int, str)) else 300
            item_ids = create_items(session, project_id, item_count)

            # Create links
            create_links(session, project_id, item_ids, link_count)

        # Summary

        result = session.execute(
            text("""
                SELECT
                    p.name as project_name,
                    COUNT(DISTINCT i.id) as item_count,
                    COUNT(DISTINCT l.id) as link_count,
                    COUNT(DISTINCT CASE WHEN i.status = 'closed' THEN i.id END) as completed_items
                FROM projects p
                LEFT JOIN items i ON i.project_id = p.id
                LEFT JOIN links l ON l.source_id = i.id OR l.target_id = i.id
                WHERE p.name IN (
                    'E-Commerce Platform',
                    'Healthcare Management System',
                    'Real-Time Analytics Dashboard',
                    'Mobile Banking App',
                    'DevOps Automation Platform'
                )
                GROUP BY p.id, p.name
                ORDER BY p.name
            """),
        )

        for _row in result:
            pass

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
