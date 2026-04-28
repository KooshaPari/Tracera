#!/usr/bin/env python3
"""Comprehensive seed script for TraceRTM with rich, authentic mock data.

Creates 50+ projects, items, links, and other entities with realistic data.
"""

import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tracertm.models.agent import Agent
from tracertm.models.agent_event import AgentEvent
from tracertm.models.base import Base
from tracertm.models.graph import Graph
from tracertm.models.item import Item
from tracertm.models.link import Link
from tracertm.models.project import Project


def get_database_url() -> str:
    """Get database URL from environment or use default."""
    import os

    return os.getenv("DATABASE_URL", "postgresql://localhost/tracertm")


# Rich mock data templates
PROJECT_DOMAINS = [
    "E-Commerce Platform",
    "Healthcare Management System",
    "Financial Trading Platform",
    "IoT Device Management",
    "Content Management System",
    "Learning Management System",
    "Customer Relationship Management",
    "Supply Chain Management",
    "Project Management Tool",
    "Social Media Platform",
    "Video Streaming Service",
    "Cloud Infrastructure",
    "Mobile Banking App",
    "Real Estate Platform",
    "Food Delivery Service",
    "Ride Sharing App",
    "Fitness Tracking App",
    "Weather Monitoring System",
    "Smart Home Automation",
    "Blockchain Wallet",
    "AI Model Training Platform",
    "Data Analytics Dashboard",
    "API Gateway",
    "Microservices Orchestration",
    "DevOps Pipeline",
    "Security Monitoring",
    "Compliance Management",
    "Document Management",
    "Collaboration Tool",
    "Code Review Platform",
    "Test Automation Framework",
    "Performance Testing",
    "Load Balancing",
    "Database Migration Tool",
    "Backup & Recovery",
    "Disaster Recovery",
    "Network Monitoring",
    "Log Aggregation",
    "Error Tracking",
    "Feature Flagging",
    "A/B Testing",
    "User Analytics",
    "Marketing Automation",
    "Email Campaign",
    "Customer Support",
    "Inventory Management",
    "Order Processing",
    "Payment Gateway",
    "Shipping Integration",
    "Tax Calculation",
    "Reporting System",
]

VIEWS = ["requirements", "features", "code", "tests", "api", "docs", "deployment", "monitoring"]
STATUSES = ["todo", "in_progress", "review", "complete", "blocked", "archived"]
PRIORITIES = ["low", "medium", "high", "critical"]
OWNERS = [
    "product_team",
    "backend_dev",
    "frontend_dev",
    "qa_team",
    "devops_team",
    "security_team",
    "data_team",
    "mobile_team",
    "design_team",
    "api_team",
]

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

AGENT_TYPES = ["analyzer", "coordinator", "monitor", "linker", "validator", "optimizer"]
AGENT_CAPABILITIES = [
    ["code_analysis", "pattern_detection"],
    ["link_discovery", "impact_analysis"],
    ["test_coverage", "code_quality"],
    ["performance_monitoring", "error_tracking"],
    ["security_scanning", "vulnerability_detection"],
    ["documentation_generation", "api_spec_generation"],
]


def generate_project_name(domain: str, index: int) -> str:
    """Generate realistic project name."""
    prefixes = ["NextGen", "Smart", "Advanced", "Enterprise", "Cloud", "AI", "Secure", "Modern"]
    suffixes = ["Platform", "System", "Suite", "Hub", "Workspace", "Studio", "Lab"]
    prefix = random.choice(prefixes) if index % 3 == 0 else ""
    suffix = random.choice(suffixes) if index % 2 == 0 else ""
    return f"{prefix} {domain} {suffix}".strip()


def generate_item_title(view: str, item_type: str, index: int) -> str:
    """Generate realistic item title."""
    if view == "requirements":
        titles = [
            f"User Authentication Requirement {index}",
            f"Data Privacy Compliance {index}",
            f"Performance Benchmark {index}",
            f"Security Standard {index}",
            f"Accessibility Requirement {index}",
        ]
    elif view == "features":
        titles = [
            f"User Dashboard Feature {index}",
            f"Search Functionality {index}",
            f"Notification System {index}",
            f"Export Capability {index}",
            f"Import Feature {index}",
        ]
    elif view == "code":
        extensions = {
            "python_file": ".py",
            "typescript_file": ".ts",
            "javascript_file": ".js",
            "go_file": ".go",
            "rust_file": ".rs",
            "java_file": ".java",
        }
        ext = extensions.get(item_type, ".py")
        paths = [
            f"services/auth{ext}",
            f"api/endpoints/user{ext}",
            f"models/data{ext}",
            f"utils/helpers{ext}",
            f"middleware/auth{ext}",
        ]
        return random.choice(paths)
    elif view == "tests":
        return f"test_{item_type.replace('_test', '')}_{index}.py"
    elif view == "api":
        methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        paths = ["/api/users", "/api/auth", "/api/data", "/api/analytics", "/api/reports"]
        return f"{random.choice(methods)} {random.choice(paths)}/{index}"
    elif view == "docs":
        return f"{item_type.replace('_', ' ').title()} {index}"
    elif view == "deployment":
        return f"{item_type.replace('_', ' ').title()} Configuration {index}"
    else:
        return f"{view.title()} Item {index}"

    return random.choice(titles) if isinstance(titles, list) else titles


def generate_description(view: str, _item_type: str) -> str:
    """Generate realistic description."""
    descriptions = {
        "requirements": [
            "Ensures secure user authentication with multi-factor support",
            "Complies with GDPR and data protection regulations",
            "Maintains response time under 200ms for 95th percentile",
            "Implements OWASP security best practices",
            "Provides WCAG 2.1 AA accessibility compliance",
        ],
        "features": [
            "Comprehensive user dashboard with real-time updates",
            "Advanced search with filters and sorting",
            "Real-time notification system with preferences",
            "Export data in multiple formats (CSV, JSON, PDF)",
            "Bulk import with validation and error handling",
        ],
        "code": [
            "Authentication service with JWT token management",
            "RESTful API endpoint with request validation",
            "Data model with relationships and constraints",
            "Utility functions for common operations",
            "Middleware for authentication and authorization",
        ],
        "tests": [
            "Unit tests covering all edge cases",
            "Integration tests for API endpoints",
            "End-to-end tests for critical user flows",
            "Performance tests for load scenarios",
            "Security tests for vulnerability detection",
        ],
        "api": [
            "RESTful endpoint with OpenAPI documentation",
            "GraphQL query with nested resolvers",
            "WebSocket connection for real-time updates",
            "RPC endpoint with gRPC protocol",
            "Webhook endpoint for external integrations",
        ],
        "docs": [
            "Comprehensive API documentation with examples",
            "User guide with step-by-step instructions",
            "Technical specification with architecture diagrams",
            "Architecture decision record (ADR)",
            "Runbook for operational procedures",
        ],
        "deployment": [
            "Docker containerization configuration",
            "Kubernetes deployment manifests",
            "Terraform infrastructure as code",
            "CI/CD pipeline configuration",
            "Infrastructure monitoring setup",
        ],
        "monitoring": [
            "Real-time dashboard with key metrics",
            "Alert configuration for critical events",
            "Custom metric collection and aggregation",
            "Centralized log aggregation setup",
            "Distributed tracing configuration",
        ],
    }
    return random.choice(descriptions.get(view, ["Item description"]))


def generate_metadata(view: str, item_type: str) -> dict:
    """Generate rich metadata."""
    base_metadata = {}

    if view == "requirements":
        base_metadata.update({
            "acceptance_criteria": [
                f"Criterion {i}: Must meet standard {random.randint(1, 10)}" for i in range(1, random.randint(3, 6))
            ],
            "stakeholders": random.sample(
                ["product_manager", "tech_lead", "qa_lead", "security_team"],
                random.randint(2, 4),
            ),
            "compliance": random.choice(["GDPR", "HIPAA", "SOC2", "PCI-DSS", "ISO27001", None]),
        })
    elif view == "features":
        base_metadata.update({
            "sprint": f"Sprint {random.randint(1, 20)}",
            "story_points": random.choice([1, 2, 3, 5, 8, 13]),
            "epic": f"Epic {random.randint(1, 10)}",
            "user_persona": random.choice(["end_user", "admin", "developer", "analyst"]),
        })
    elif view == "code":
        base_metadata.update({
            "file_path": f"src/{random.choice(['services', 'api', 'models', 'utils'])}/file_{random.randint(1, 100)}.py",
            "lines_of_code": random.randint(50, 2000),
            "coverage": random.randint(60, 100),
            "complexity": random.choice(["low", "medium", "high"]),
            "language": item_type.replace("_file", "").replace("_", "").title(),
        })
    elif view == "tests":
        base_metadata.update({
            "file_path": f"tests/{random.choice(['unit', 'integration', 'e2e'])}/test_file_{random.randint(1, 100)}.py",
            "test_count": random.randint(5, 50),
            "passing": random.randint(5, 50),
            "failing": random.randint(0, 5),
            "coverage": random.randint(70, 100),
        })
    elif view == "api":
        method, path = generate_item_title("api", item_type, 0).split(" ", 1)
        base_metadata.update({
            "method": method,
            "path": path,
            "request_body": {"field1": "string", "field2": "number"},
            "response": {"status": 200, "data": "object"},
            "rate_limit": random.randint(100, 10000),
        })
    elif view == "docs":
        base_metadata.update({
            "format": random.choice(["markdown", "html", "pdf", "confluence"]),
            "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
            "last_reviewed": (datetime.now(UTC) - timedelta(days=random.randint(1, 90))).isoformat(),
        })
    elif view == "deployment":
        base_metadata.update({
            "environment": random.choice(["development", "staging", "production"]),
            "region": random.choice(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]),
            "version": f"v{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
        })
    elif view == "monitoring":
        base_metadata.update({
            "metric_type": random.choice(["counter", "gauge", "histogram", "summary"]),
            "alert_threshold": random.randint(50, 100),
            "dashboard_url": f"https://monitoring.example.com/dashboards/{random.randint(1, 20)}",
        })

    return base_metadata


def create_projects(session: Session, count: int = 50) -> list[str]:
    """Create multiple projects."""
    project_ids = []

    for i in range(count):
        domain = random.choice(PROJECT_DOMAINS)
        project = Project(
            name=generate_project_name(domain, i),
            description=f"Comprehensive {domain.lower()} solution with modern architecture and best practices",
            project_metadata={
                "domain": domain,
                "team_size": random.randint(3, 20),
                "methodology": random.choice(["Agile", "Scrum", "Kanban", "Waterfall", "DevOps"]),
                "tech_stack": random.sample(
                    ["Python", "TypeScript", "React", "PostgreSQL", "Docker", "Kubernetes"],
                    random.randint(3, 6),
                ),
                "start_date": (datetime.now(UTC) - timedelta(days=random.randint(30, 365))).isoformat(),
                "status": random.choice(["active", "planning", "maintenance", "archived"]),
            },
        )
        session.add(project)
        project_ids.append(project.id)

        if (i + 1) % 10 == 0:
            session.flush()

    session.flush()
    return project_ids


def create_graphs(session: Session, project_ids: list[str]) -> dict[str, str]:
    """Create default graph for each project."""
    graph_map = {}

    for project_id in project_ids:
        graph = Graph(
            project_id=project_id,
            name="default",
            graph_type="traceability",
            graph_metadata={
                "description": "Default traceability graph",
                "auto_link": True,
                "link_confidence_threshold": 0.7,
            },
        )
        session.add(graph)
        session.flush()
        graph_map[project_id] = graph.id

    return graph_map


def create_items(session: Session, project_ids: list[str], items_per_project: int = 50) -> dict[str, list[Item]]:
    """Create items for each project."""
    project_items = {pid: [] for pid in project_ids}
    len(project_ids) * items_per_project

    item_count = 0
    for project_id in project_ids:
        items = []
        items_per_view = items_per_project // len(VIEWS)

        for view in VIEWS:
            item_types = ITEM_TYPES_BY_VIEW.get(view, ["item"])

            for i in range(items_per_view):
                item_type = random.choice(item_types)
                item = Item(
                    project_id=project_id,
                    title=generate_item_title(view, item_type, i),
                    description=generate_description(view, item_type),
                    view=view,
                    item_type=item_type,
                    status=random.choice(STATUSES),
                    priority=random.choice(PRIORITIES),
                    owner=random.choice(OWNERS),
                    item_metadata=generate_metadata(view, item_type),
                )
                session.add(item)
                items.append(item)
                item_count += 1

                if item_count % 100 == 0:
                    session.flush()

        session.flush()
        project_items[project_id] = items

    return project_items


def create_links(
    session: Session,
    project_ids: list[str],
    graph_map: dict[str, str],
    project_items: dict[str, list[Item]],
    links_per_project: int = 50,
) -> None:
    """Create links between items."""
    len(project_ids) * links_per_project

    link_count = 0
    for project_id in project_ids:
        items = project_items[project_id]
        if len(items) < 2:
            continue

        graph_id = graph_map[project_id]

        for _ in range(links_per_project):
            source = random.choice(items)
            target = random.choice(items)

            # Avoid self-links
            if source.id == target.id:
                continue

            link = Link(
                project_id=project_id,
                graph_id=graph_id,
                source_item_id=source.id,
                target_item_id=target.id,
                link_type=random.choice(LINK_TYPES),
                link_metadata={
                    "confidence": round(random.uniform(0.6, 1.0), 2),
                    "created_by": random.choice(["agent", "user", "auto"]),
                    "verified": random.choice([True, False]),
                },
            )
            session.add(link)
            link_count += 1

            if link_count % 100 == 0:
                session.flush()

        session.flush()


def create_agents(session: Session, project_ids: list[str], agents_per_project: int = 3) -> dict[str, list[Agent]]:
    """Create agents for each project."""
    project_agents = {pid: [] for pid in project_ids}
    len(project_ids) * agents_per_project

    agent_count = 0
    for project_id in project_ids:
        agents = []
        for i in range(agents_per_project):
            agent_type = random.choice(AGENT_TYPES)
            capabilities = random.choice(AGENT_CAPABILITIES)

            agent = Agent(
                project_id=project_id,
                name=f"{agent_type.title()} Agent {i + 1}",
                agent_type=agent_type,
                status=random.choice(["active", "idle", "error"]),
                agent_metadata={
                    "capabilities": capabilities,
                    "version": f"{random.randint(1, 5)}.{random.randint(0, 9)}",
                    "performance": {
                        "avg_processing_time": random.randint(10, 500),
                        "success_rate": round(random.uniform(0.85, 1.0), 2),
                    },
                },
                last_activity_at=(datetime.now(UTC) - timedelta(minutes=random.randint(1, 1440))).isoformat(),
            )
            session.add(agent)
            agents.append(agent)
            agent_count += 1

        session.flush()
        project_agents[project_id] = agents

    return project_agents


def create_events(
    session: Session,
    project_ids: list[str],
    project_agents: dict[str, list[Agent]],
    project_items: dict[str, list[Item]],
    events_per_project: int = 20,
) -> None:
    """Create agent events."""
    len(project_ids) * events_per_project

    event_count = 0
    event_types = ["item_created", "link_created", "item_updated", "coordination", "analysis_complete"]

    for project_id in project_ids:
        agents = project_agents.get(project_id, [])
        items = project_items.get(project_id, [])

        if not agents or not items:
            continue

        for _ in range(events_per_project):
            agent = random.choice(agents)
            item = random.choice(items) if items else None

            event = AgentEvent(
                project_id=project_id,
                agent_id=agent.id,
                event_type=random.choice(event_types),
                item_id=item.id if item else None,
                event_data={
                    "action": random.choice(["analyzed", "linked", "updated", "validated", "optimized"]),
                    "timestamp": (datetime.now(UTC) - timedelta(minutes=random.randint(1, 10080))).isoformat(),
                    "details": {
                        "confidence": round(random.uniform(0.7, 1.0), 2),
                        "impact": random.choice(["low", "medium", "high"]),
                    },
                },
            )
            session.add(event)
            event_count += 1

            if event_count % 100 == 0:
                session.flush()

        session.flush()


def seed_database() -> None:
    """Main seeding function."""
    database_url = get_database_url()

    engine = create_engine(database_url)

    # Create all tables (if not exists)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        try:
            # Check if data already exists
            existing_count = session.query(Project).count()
            if existing_count > 0:
                response = input(f"Found {existing_count} existing projects. Clear and reseed? (yes/no): ")
                if response.lower() != "yes":
                    return
                session.query(AgentEvent).delete()
                session.query(Agent).delete()
                session.query(Link).delete()
                session.query(Item).delete()
                session.query(Graph).delete()
                session.query(Project).delete()
                session.commit()

            # Create data
            project_ids = create_projects(session, count=50)

            graph_map = create_graphs(session, project_ids)

            project_items = create_items(session, project_ids, items_per_project=50)

            create_links(session, project_ids, graph_map, project_items, links_per_project=50)

            project_agents = create_agents(session, project_ids, agents_per_project=3)

            create_events(session, project_ids, project_agents, project_items, events_per_project=20)

            session.commit()

            # Summary

        except Exception:
            session.rollback()
            import traceback

            traceback.print_exc()
            raise


if __name__ == "__main__":
    seed_database()
