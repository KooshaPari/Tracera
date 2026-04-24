#!/usr/bin/env python3
"""normalize_todo_graph_slugs module."""

import os

import psycopg2

POSTGRES_URL = os.environ.get(
    "TRACERTM_DATABASE_URL",
    "postgresql://kooshapari@localhost:5432/agent_api",
)

PROJECT_ID = "proj_todo_graph_001"

SLUG_MAP = {
    "user_requirements": "user-requirements",
    "technical_requirements": "technical-requirements",
    "ui_components": "ui-components",
    "data_model": "data-model",
    "journey": "journey",
    "qa": "qa",
    "infra": "infra",
    "security": "security",
    "performance": "performance",
    "analytics": "analytics",
    "compliance": "compliance",
    "localization": "localization",
    "ops": "ops",
    "accessibility": "accessibility",
    "mapping": "mapping",
}


def main() -> None:
    """Main."""
    conn = psycopg2.connect(POSTGRES_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Update views
            for old, new in SLUG_MAP.items():
                cur.execute(
                    "update views set name = %s where project_id = %s and name = %s",
                    (new, PROJECT_ID, old),
                )
            # Update items.view
            for old, new in SLUG_MAP.items():
                cur.execute(
                    "update items set view = %s where project_id = %s and view = %s",
                    (new, PROJECT_ID, old),
                )
            # Update graphs.graph_type and name to match slug
            for old, new in SLUG_MAP.items():
                cur.execute(
                    "update graphs set graph_type = %s, name = %s where project_id = %s and graph_type = %s",
                    (new, f"{new} graph", PROJECT_ID, old),
                )
            conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
