#!/usr/bin/env python3
"""Seed database with sample data for TraceRTM.

This script creates a sample project with items, links, agents, and events
to demonstrate the TraceRTM system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.base import Base
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    import os

    return os.getenv("DATABASE_URL", "postgresql://localhost/tracertm")


def create_sample_project(session: Session) -> str:
    """Create a sample project."""
    project = Project(
        name="Sample TraceRTM Project",
        description="A demonstration project showing TraceRTM capabilities",
        project_metadata={"domain": "Software Engineering", "team_size": 5, "methodology": "Agile"},
    )
    session.add(project)
    session.flush()
    return str(project.id)


def create_sample_items(session: Session, project_id: str) -> dict:
    """Create sample items across different views."""
    items = {}

    # Requirements
    req1 = Item(
        project_id=project_id,
        title="User Authentication System",
        description="Implement secure user login and registration",
        view="requirements",
        item_type="functional_requirement",
        status="approved",
        priority="high",
        owner="product_team",
        item_metadata={
            "acceptance_criteria": [
                "Users can register with email",
                "Users can login securely",
                "Password reset functionality",
            ],
        },
    )
    items["req1"] = req1
    session.add(req1)

    req2 = Item(
        project_id=project_id,
        title="Performance Requirements",
        description="System must handle 1000 concurrent users",
        view="requirements",
        item_type="non_functional_requirement",
        status="approved",
        priority="high",
        owner="product_team",
        item_metadata={"metrics": {"concurrent_users": 1000, "response_time": "< 200ms"}},
    )
    items["req2"] = req2
    session.add(req2)

    # Features
    feature1 = Item(
        project_id=project_id,
        title="Login Feature",
        description="User login functionality with OAuth support",
        view="features",
        item_type="feature",
        status="in_progress",
        priority="high",
        owner="dev_team",
        item_metadata={"sprint": "Sprint 3", "story_points": 8},
    )
    items["feature1"] = feature1
    session.add(feature1)

    feature2 = Item(
        project_id=project_id,
        title="Registration Feature",
        description="New user registration with email verification",
        view="features",
        item_type="feature",
        status="todo",
        priority="high",
        owner="dev_team",
        item_metadata={"sprint": "Sprint 4", "story_points": 5},
    )
    items["feature2"] = feature2
    session.add(feature2)

    # Code
    code1 = Item(
        project_id=project_id,
        title="auth/login.py",
        description="Login authentication logic",
        view="code",
        item_type="python_file",
        status="complete",
        priority="high",
        owner="backend_dev",
        item_metadata={"file_path": "backend/auth/login.py", "lines_of_code": 150, "coverage": 85},
    )
    items["code1"] = code1
    session.add(code1)

    code2 = Item(
        project_id=project_id,
        title="auth/oauth.py",
        description="OAuth integration module",
        view="code",
        item_type="python_file",
        status="in_progress",
        priority="medium",
        owner="backend_dev",
        item_metadata={"file_path": "backend/auth/oauth.py", "lines_of_code": 200, "coverage": 70},
    )
    items["code2"] = code2
    session.add(code2)

    # Tests
    test1 = Item(
        project_id=project_id,
        title="test_login.py",
        description="Unit tests for login functionality",
        view="tests",
        item_type="unit_test",
        status="complete",
        priority="high",
        owner="qa_team",
        item_metadata={"file_path": "tests/auth/test_login.py", "test_count": 15, "passing": 15, "failing": 0},
    )
    items["test1"] = test1
    session.add(test1)

    test2 = Item(
        project_id=project_id,
        title="test_oauth.py",
        description="Unit tests for OAuth integration",
        view="tests",
        item_type="unit_test",
        status="in_progress",
        priority="medium",
        owner="qa_team",
        item_metadata={"file_path": "tests/auth/test_oauth.py", "test_count": 10, "passing": 7, "failing": 3},
    )
    items["test2"] = test2
    session.add(test2)

    # API
    api1 = Item(
        project_id=project_id,
        title="POST /api/auth/login",
        description="Login endpoint",
        view="api",
        item_type="rest_endpoint",
        status="complete",
        priority="high",
        owner="api_team",
        item_metadata={
            "method": "POST",
            "path": "/api/auth/login",
            "request_body": {"email": "string", "password": "string"},
            "response": {"token": "string", "user": "object"},
        },
    )
    items["api1"] = api1
    session.add(api1)

    api2 = Item(
        project_id=project_id,
        title="POST /api/auth/register",
        description="Registration endpoint",
        view="api",
        item_type="rest_endpoint",
        status="todo",
        priority="high",
        owner="api_team",
        item_metadata={
            "method": "POST",
            "path": "/api/auth/register",
            "request_body": {"email": "string", "password": "string", "name": "string"},
        },
    )
    items["api2"] = api2
    session.add(api2)

    session.flush()
    return items


def create_sample_links(session: Session, project_id: str, items: dict) -> None:
    """Create sample links between items."""
    links = [
        # Feature implements Requirement
        Link(
            project_id=project_id,
            source_item_id=items["feature1"].id,
            target_item_id=items["req1"].id,
            link_type="implements",
            link_metadata={"confidence": 0.95},
        ),
        Link(
            project_id=project_id,
            source_item_id=items["feature2"].id,
            target_item_id=items["req1"].id,
            link_type="implements",
            link_metadata={"confidence": 0.90},
        ),
        # Code implements Feature
        Link(
            project_id=project_id,
            source_item_id=items["code1"].id,
            target_item_id=items["feature1"].id,
            link_type="implements",
            link_metadata={"confidence": 0.98},
        ),
        Link(
            project_id=project_id,
            source_item_id=items["code2"].id,
            target_item_id=items["feature1"].id,
            link_type="implements",
            link_metadata={"confidence": 0.85},
        ),
        # Tests verify Code
        Link(
            project_id=project_id,
            source_item_id=items["test1"].id,
            target_item_id=items["code1"].id,
            link_type="tests",
            link_metadata={"coverage": 85},
        ),
        Link(
            project_id=project_id,
            source_item_id=items["test2"].id,
            target_item_id=items["code2"].id,
            link_type="tests",
            link_metadata={"coverage": 70},
        ),
        # API exposes Code
        Link(
            project_id=project_id,
            source_item_id=items["api1"].id,
            target_item_id=items["code1"].id,
            link_type="exposes",
            link_metadata={},
        ),
        # Dependencies
        Link(
            project_id=project_id,
            source_item_id=items["code2"].id,
            target_item_id=items["code1"].id,
            link_type="depends_on",
            link_metadata={"dependency_type": "import"},
        ),
    ]

    for link in links:
        session.add(link)


def create_sample_agents(session: Session, project_id: str) -> dict:
    """Create sample agents."""
    agents = {}

    agent1 = Agent(
        project_id=project_id,
        name="Code Analyzer Agent",
        agent_type="analyzer",
        status="active",
        agent_metadata={"capabilities": ["code_analysis", "pattern_detection"], "language": "python"},
        last_activity_at=datetime.now(UTC).isoformat(),
    )
    agents["agent1"] = agent1
    session.add(agent1)

    agent2 = Agent(
        project_id=project_id,
        name="Traceability Agent",
        agent_type="coordinator",
        status="active",
        agent_metadata={"capabilities": ["link_discovery", "impact_analysis"], "scope": "all_views"},
        last_activity_at=datetime.now(UTC).isoformat(),
    )
    agents["agent2"] = agent2
    session.add(agent2)

    agent3 = Agent(
        project_id=project_id,
        name="Quality Metrics Agent",
        agent_type="monitor",
        status="active",
        agent_metadata={
            "capabilities": ["test_coverage", "code_quality"],
            "metrics": ["coverage", "complexity", "test_pass_rate"],
        },
        last_activity_at=datetime.now(UTC).isoformat(),
    )
    agents["agent3"] = agent3
    session.add(agent3)

    session.flush()
    return agents


def create_sample_events(session: Session, project_id: str, agents: dict, items: dict) -> None:
    """Create sample agent events."""
    events = [
        AgentEvent(
            project_id=project_id,
            agent_id=agents["agent1"].id,
            event_type="item_created",
            item_id=items["code1"].id,
            event_data={
                "action": "analyzed_code",
                "findings": {"complexity": "low", "patterns": ["authentication", "validation"]},
            },
        ),
        AgentEvent(
            project_id=project_id,
            agent_id=agents["agent2"].id,
            event_type="link_created",
            item_id=items["code1"].id,
            event_data={
                "action": "discovered_link",
                "source": items["code1"].id,
                "target": items["feature1"].id,
                "link_type": "implements",
                "confidence": 0.98,
            },
        ),
        AgentEvent(
            project_id=project_id,
            agent_id=agents["agent3"].id,
            event_type="item_updated",
            item_id=items["test1"].id,
            event_data={
                "action": "calculated_coverage",
                "metrics": {"coverage": 85, "tests_passing": 15, "tests_total": 15},
            },
        ),
        AgentEvent(
            project_id=project_id,
            agent_id=agents["agent2"].id,
            event_type="coordination",
            event_data={
                "action": "impact_analysis",
                "analyzed_item": items["req1"].id,
                "impacted_items": [items["feature1"].id, items["feature2"].id, items["code1"].id],
                "impact_level": "high",
            },
        ),
    ]

    for event in events:
        session.add(event)


def seed_database() -> None:
    """Main seeding function."""
    database_url = get_database_url()

    engine = create_engine(database_url)

    # Create all tables (if not exists)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        try:
            # Check if data already exists
            existing_project = session.query(Project).filter_by(name="Sample TraceRTM Project").first()

            if existing_project:
                return

            project_id = create_sample_project(session)

            items = create_sample_items(session, project_id)

            create_sample_links(session, project_id, items)

            agents = create_sample_agents(session, project_id)

            create_sample_events(session, project_id, agents, items)

            session.commit()

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_database()
