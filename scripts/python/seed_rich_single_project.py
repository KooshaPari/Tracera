#!/usr/bin/env python3
"""Seed one project in tracertm schema with rich, varied data: 50+ items per type,.

50+ links per link type, agents, events, milestones, sprints. Uses tracertm schema
and existing columns only (links: source_id, target_id, link_type; no project_id/graph_id).
"""

import json
import os
import random
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Your account (from RLS mapping)
ACCOUNT_ID = "7f3c8d2a-1b4e-4a9c-9e2d-6f1a8b0c3d4e"

VIEWS = ["requirements", "features", "code", "tests", "api", "docs", "deployment", "monitoring"]
STATUSES = ["open", "todo", "in_progress", "review", "complete", "blocked", "archived"]
PRIORITIES = [0, 1, 2, 3, 4, 5]

ITEM_TYPES_BY_VIEW = {
    "requirements": [
        "functional_requirement",
        "non_functional_requirement",
        "business_rule",
        "user_story",
        "acceptance_criteria",
    ],
    "features": ["feature", "epic", "user_story", "enhancement", "bug_fix"],
    "code": [
        "python_file",
        "typescript_file",
        "javascript_file",
        "go_file",
        "rust_file",
        "java_file",
        "service",
        "module",
        "component",
    ],
    "tests": ["unit_test", "integration_test", "e2e_test", "performance_test", "security_test"],
    "api": ["rest_endpoint", "graphql_endpoint", "websocket_endpoint", "rpc_endpoint", "webhook"],
    "docs": ["api_documentation", "user_guide", "technical_spec", "architecture_doc", "runbook"],
    "deployment": ["dockerfile", "kubernetes_config", "terraform_config", "ci_cd_pipeline", "infrastructure"],
    "monitoring": ["dashboard", "alert", "metric", "log_aggregator", "tracing_config"],
}

LINK_TYPES = [
    "implements",
    "tests",
    "depends_on",
    "exposes",
    "uses",
    "validates",
    "refines",
    "decomposes",
    "related_to",
    "blocks",
    "replaces",
    "migrates_to",
]

PER_TYPE = 50
PER_LINK_TYPE = 55
NUM_AGENTS = 8
NUM_EVENTS = 200


def get_engine() -> Engine:
    """Get engine."""
    url = os.getenv("DATABASE_URL", "postgresql://tracertm:tracertm_password@localhost:5432/tracertm")
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql", 1)
    return create_engine(url, pool_pre_ping=True)


def generate_title(view: str, item_type: str, index: int) -> str:
    """Generate title."""
    if view == "requirements":
        return random.choice([
            f"User Authentication Requirement {index}",
            f"Data Privacy Compliance {index}",
            f"Performance Benchmark {index}",
            f"Security Standard {index}",
            f"Accessibility Requirement {index}",
        ])
    if view == "features":
        return random.choice([
            f"User Dashboard Feature {index}",
            f"Search Functionality {index}",
            f"Notification System {index}",
            f"Export Capability {index}",
            f"Import Feature {index}",
        ])
    if view == "code":
        ext = {".py", ".ts", ".js", ".go", ".rs", ".java"}.intersection({item_type})
        ext = ".py" if not ext else "." + item_type.replace("_file", "").replace("_", "")
        return random.choice([
            f"services/auth{ext}",
            f"api/endpoints/user{ext}",
            f"models/data{ext}",
            f"utils/helpers{ext}",
            f"middleware/auth{ext}",
        ])
    if view == "tests":
        return f"test_{item_type.replace('_test', '')}_{index}.py"
    if view == "api":
        return f"{random.choice(['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])} {random.choice(['/api/users', '/api/auth', '/api/data'])}/{index}"
    return f"{item_type.replace('_', ' ').title()} {index}"


def generate_description(_view: str) -> str:
    """Generate description."""
    opts = [
        "Ensures secure authentication with multi-factor support.",
        "Complies with data protection regulations.",
        "Maintains response time under 200ms p95.",
        "Implements OWASP security best practices.",
        "Comprehensive dashboard with real-time updates.",
        "RESTful endpoint with request validation.",
        "Unit tests covering edge cases.",
        "Docker containerization configuration.",
    ]
    return random.choice(opts)


def generate_metadata(view: str, _item_type: str) -> dict:
    """Generate metadata."""
    m: dict = {}
    if view == "requirements":
        m["acceptance_criteria"] = [f"Criterion {i}" for i in range(1, random.randint(3, 6))]
        m["stakeholders"] = random.sample(["product_manager", "tech_lead", "qa_lead"], random.randint(2, 3))
    elif view == "features":
        m["story_points"] = random.choice([1, 2, 3, 5, 8, 13])
        m["epic"] = f"Epic {random.randint(1, 10)}"
    elif view == "code":
        m["file_path"] = f"src/{random.choice(['services', 'api', 'models'])}/file_{random.randint(1, 100)}"
        m["lines_of_code"] = random.randint(50, 2000)
    elif view == "tests":
        m["test_count"] = random.randint(5, 50)
        m["coverage"] = random.randint(70, 100)
    elif view == "api":
        m["rate_limit"] = random.randint(100, 10000)
    return m


def run() -> None:
    """Run."""
    engine = get_engine()
    project_id = uuid.uuid4()
    project_name = "Platform In-Progress — Trace & Requirements"
    project_desc = "Single seed project with rich items, links, agents, and events for walkthrough."

    with engine.connect() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        conn.commit()

    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        # 1. Project
        conn.execute(
            text("""
                INSERT INTO projects (id, name, description, metadata, created_at, updated_at, account_id)
                VALUES (:id, :name, :description, '{}', NOW(), NOW(), :account_id)
            """),
            {"id": project_id, "name": project_name, "description": project_desc, "account_id": ACCOUNT_ID},
        )

    item_ids: list[uuid.UUID] = []
    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        for view in VIEWS:
            types_list = ITEM_TYPES_BY_VIEW.get(view, ["item"])
            for item_type in types_list:
                for i in range(PER_TYPE):
                    item_id = uuid.uuid4()
                    title = generate_title(view, item_type, i)
                    desc = generate_description(view)
                    status = random.choice(STATUSES)
                    priority = random.choice(PRIORITIES)
                    meta = generate_metadata(view, item_type)
                    conn.execute(
                        text("""
                            INSERT INTO items (id, project_id, title, description, type, status, priority, metadata, created_at, updated_at)
                            VALUES (:id, :project_id, :title, :description, :type, :status, :priority, CAST(:metadata AS jsonb), NOW(), NOW())
                        """),
                        {
                            "id": item_id,
                            "project_id": project_id,
                            "title": title[:255],
                            "description": desc,
                            "type": item_type,
                            "status": status,
                            "priority": priority,
                            "metadata": json.dumps(meta),
                        },
                    )
                    item_ids.append(item_id)

    link_count = 0
    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        for link_type in LINK_TYPES:
            for _ in range(PER_LINK_TYPE):
                src = random.choice(item_ids)
                tgt = random.choice(item_ids)
                if src == tgt:
                    continue
                conn.execute(
                    text("""
                        INSERT INTO links (id, source_id, target_id, link_type, metadata, created_at)
                        VALUES (:id, :source_id, :target_id, :link_type, '{}', NOW())
                    """),
                    {
                        "id": uuid.uuid4(),
                        "source_id": src,
                        "target_id": tgt,
                        "link_type": link_type,
                    },
                )
                link_count += 1

    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        agent_ids = []
        for i in range(NUM_AGENTS):
            agent_id = uuid.uuid4()
            conn.execute(
                text("""
                    INSERT INTO agents (id, project_id, name, status, metadata, created_at, updated_at)
                    VALUES (:id, :project_id, :name, :status, '{}', NOW(), NOW())
                """),
                {
                    "id": agent_id,
                    "project_id": project_id,
                    "name": f"Agent {random.choice(['Analyzer', 'Coordinator', 'Monitor', 'Linker', 'Validator'])} {i + 1}",
                    "status": random.choice(["active", "idle"]),
                },
            )
            agent_ids.append(agent_id)

    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        for _ in range(NUM_EVENTS):
            entity_id = random.choice(item_ids)
            conn.execute(
                text("""
                    INSERT INTO events (id, project_id, entity_type, entity_id, event_type, data, metadata, version, created_at)
                    VALUES (:id, :project_id, 'item', :entity_id, :event_type, CAST(:data AS jsonb), '{}', 1, NOW())
                """),
                {
                    "id": uuid.uuid4(),
                    "project_id": project_id,
                    "entity_id": entity_id,
                    "event_type": random.choice(["item_created", "link_created", "item_updated", "analysis_complete"]),
                    "data": json.dumps({
                        "action": random.choice(["created", "updated", "linked"]),
                        "at": datetime.now(UTC).isoformat(),
                    }),
                },
            )

    # Milestones and sprints (no owner_id / profile required)
    with engine.begin() as conn:
        conn.execute(text("SET search_path TO tracertm"))
        milestone_names = ["MVP", "Beta", "GA", "Phase 2", "Release"]
        milestone_status = ["in_progress", "not_started", "not_started", "not_started", "not_started"]
        milestone_health = ["green", "yellow", "unknown", "unknown", "unknown"]
        for i in range(1, 6):
            mid = uuid.uuid4()
            conn.execute(
                text("""
                    INSERT INTO milestones (id, project_id, name, slug, description, target_date, status, health, risk_score, created_at, updated_at)
                    VALUES (:id, :project_id, :name, :slug, :description, :target_date, :status, :health, 0, NOW(), NOW())
                """),
                {
                    "id": mid,
                    "project_id": project_id,
                    "name": f"Milestone {i}: {milestone_names[i - 1]}",
                    "slug": f"m{i}",
                    "description": f"Target for milestone {i}.",
                    "target_date": (datetime.now(UTC) + timedelta(days=30 * i)).replace(tzinfo=None),
                    "status": milestone_status[i - 1],
                    "health": milestone_health[i - 1],
                },
            )
        for i in range(1, 6):
            conn.execute(
                text("""
                    INSERT INTO sprints (id, project_id, name, slug, goal, start_date, end_date, status, health, planned_points, completed_points, remaining_points, added_points, removed_points, created_at, updated_at)
                    VALUES (:id, :project_id, :name, :slug, :goal, :start, :end, :status, :health, 50, :done, :rem, 0, 0, NOW(), NOW())
                """),
                {
                    "id": uuid.uuid4(),
                    "project_id": project_id,
                    "name": f"Sprint {i}",
                    "slug": f"sprint-{i}",
                    "goal": f"Sprint {i} goals.",
                    "start": (datetime.now(UTC) - timedelta(days=14 * (6 - i))).replace(tzinfo=None),
                    "end": (datetime.now(UTC) - timedelta(days=14 * (5 - i))).replace(tzinfo=None),
                    "status": "completed" if i < 4 else "active" if i == 4 else "planning",
                    "health": "green" if i != 3 else "yellow",
                    "done": 48 if i == 1 else 45 if i == 2 else 42 if i == 3 else 20 if i == 4 else 0,
                    "rem": 0 if i < 4 else 30 if i == 4 else 50,
                },
            )


if __name__ == "__main__":
    run()
