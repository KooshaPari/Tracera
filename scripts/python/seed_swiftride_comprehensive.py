#!/usr/bin/env python3
"""Comprehensive seed script for SwiftRide rideshare platform with 60+ item types.

Creates realistic items across all categories:
- Business & Strategy (7 types)
- Product Management (5 types)
- Architecture & Design (8 types)
- Development (12 types)
- Testing & Quality (14 types)
- Operations & Deployment (10 types)
- Documentation (10 types)
- Compliance & Legal (8 types)
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tracertm.models.item import Item
from tracertm.models.project import Project


def get_database_url() -> str:
    """Get database url."""
    import os

    return os.getenv("DATABASE_URL", "postgresql://localhost/tracertm")


# Item type definitions
ITEM_TYPES = {
    # Business & Strategy
    "business_objective": "Business Objectives",
    "kpi": "Key Performance Indicators",
    "market_segment": "Market Segments",
    "persona": "User Personas",
    "business_rule": "Business Rules",
    "compliance_requirement": "Compliance Requirements",
    "policy": "Policies",
    # Product Management
    "initiative": "Strategic Initiatives",
    "epic": "Epics",
    "capability": "System Capabilities",
    "value_stream": "Value Streams",
    "roadmap_item": "Roadmap Items",
    # Architecture & Design
    "architecture_decision": "Architecture Decision Records",
    "system_component": "System Components",
    "microservice": "Microservices",
    "api_contract": "API Contracts",
    "data_model": "Data Models",
    "integration_point": "Integration Points",
    "event": "Domain Events",
    "message_queue": "Message Queues",
    # Development
    "backend_service": "Backend Services",
    "frontend_component": "Frontend Components",
    "database_table": "Database Tables",
    "database_index": "Database Indexes",
    "api_endpoint": "API Endpoints",
    "graphql_resolver": "GraphQL Resolvers",
    "background_job": "Background Jobs",
    "scheduled_task": "Scheduled Tasks",
    "configuration": "Configurations",
    "environment_variable": "Environment Variables",
    "dependency": "Dependencies",
    # Testing & Quality
    "test_plan": "Test Plans",
    "test_strategy": "Test Strategies",
    "test_scenario": "Test Scenarios",
    "test_case": "Test Cases",
    "test_step": "Test Steps",
    "acceptance_test": "Acceptance Tests",
    "regression_test": "Regression Tests",
    "performance_benchmark": "Performance Benchmarks",
    "load_test_scenario": "Load Test Scenarios",
    "security_vulnerability": "Security Vulnerabilities",
    "security_control": "Security Controls",
    "accessibility_requirement": "Accessibility Requirements",
    "wcag_criterion": "WCAG Criteria",
    # Operations & Deployment
    "deployment_environment": "Deployment Environments",
    "infrastructure_resource": "Infrastructure Resources",
    "monitoring_metric": "Monitoring Metrics",
    "alert_rule": "Alert Rules",
    "runbook": "Runbooks",
    "incident_response_plan": "Incident Response Plans",
    "backup_strategy": "Backup Strategies",
    "disaster_recovery_plan": "Disaster Recovery Plans",
    "scaling_policy": "Scaling Policies",
    "capacity_plan": "Capacity Plans",
    # Documentation
    "technical_spec": "Technical Specifications",
    "api_doc": "API Documentation",
    "user_manual": "User Manuals",
    "tutorial": "Tutorials",
    "architecture_diagram": "Architecture Diagrams",
    "sequence_diagram": "Sequence Diagrams",
    "release_note": "Release Notes",
    "changelog_entry": "Changelog Entries",
    "troubleshooting_guide": "Troubleshooting Guides",
    "faq_item": "FAQ Items",
    # Compliance & Legal
    "regulation": "Regulations",
    "legal_requirement": "Legal Requirements",
    "audit_requirement": "Audit Requirements",
    "control": "Controls",
    "privacy_policy_clause": "Privacy Policy Clauses",
    "terms_of_service_clause": "Terms of Service Clauses",
    "data_retention_rule": "Data Retention Rules",
    "consent_requirement": "Consent Requirements",
}


def create_swiftride_items(session: Session, project_id: uuid.UUID) -> dict[str, list[Item]]:
    """Create comprehensive SwiftRide items across all types."""
    items_by_type = {}

    # Business Objectives
    business_objectives = [
        {
            "title": "Achieve 1M active users by Q4 2026",
            "description": "Grow user base from 250K to 1M monthly active users through improved retention and acquisition strategies",
            "status": "in_progress",
            "priority": 5,
            "metadata": {
                "target": 1000000,
                "current": 250000,
                "deadline": "2026-Q4",
                "owner": "CPO",
                "metrics": ["MAU", "retention_rate"],
            },
        },
        {
            "title": "Expand to 15 new cities by end of 2026",
            "description": "Geographic expansion into tier-2 cities with population over 500K",
            "status": "in_progress",
            "priority": 5,
            "metadata": {
                "target_cities": 15,
                "current_cities": 8,
                "criteria": ["population>500K", "smartphone_penetration>60%"],
            },
        },
        {
            "title": "Reduce customer acquisition cost by 30%",
            "description": "Optimize marketing spend and referral programs to improve CAC from $15 to $10.50",
            "status": "todo",
            "priority": 4,
            "metadata": {
                "current_cac": 15.0,
                "target_cac": 10.50,
                "strategies": ["referral_bonus", "organic_growth", "partnership"],
            },
        },
        {
            "title": "Achieve profitability in top 5 markets",
            "description": "Optimize unit economics to reach positive contribution margin in NYC, LA, SF, Chicago, Boston",
            "status": "in_progress",
            "priority": 5,
            "metadata": {"markets": ["NYC", "LA", "SF", "CHI", "BOS"], "current_margin": -0.05, "target_margin": 0.15},
        },
        {
            "title": "Launch corporate accounts program",
            "description": "Introduce B2B offering for employee transportation with centralized billing and reporting",
            "status": "todo",
            "priority": 3,
            "metadata": {"target_customers": 100, "revenue_target": 5000000, "launch_date": "2026-Q2"},
        },
    ]

    # KPIs
    kpis = [
        {
            "title": "Driver retention rate >80%",
            "description": "Percentage of drivers active after 90 days from first ride",
            "status": "complete",
            "priority": 5,
            "metadata": {
                "type": "retention",
                "target": 0.80,
                "current": 0.83,
                "measurement": "90_day_active",
                "frequency": "weekly",
            },
        },
        {
            "title": "Average ride acceptance time <45 seconds",
            "description": "Time from ride request to driver acceptance",
            "status": "complete",
            "priority": 4,
            "metadata": {"target": 45, "current": 38, "unit": "seconds", "p95": 52, "p99": 78},
        },
        {
            "title": "Rider satisfaction score >4.5/5",
            "description": "Post-ride survey rating average",
            "status": "in_progress",
            "priority": 5,
            "metadata": {"target": 4.5, "current": 4.3, "response_rate": 0.42, "sample_size": 15000},
        },
        {
            "title": "Surge pricing frequency <15% of rides",
            "description": "Percentage of rides with surge multiplier >1.0x",
            "status": "complete",
            "priority": 3,
            "metadata": {"target": 0.15, "current": 0.12, "max_multiplier": 3.0, "avg_multiplier": 1.08},
        },
        {
            "title": "Payment failure rate <2%",
            "description": "Failed payment attempts as percentage of total transactions",
            "status": "complete",
            "priority": 5,
            "metadata": {
                "target": 0.02,
                "current": 0.015,
                "retry_success": 0.65,
                "top_reasons": ["insufficient_funds", "expired_card"],
            },
        },
    ]

    # Save business objectives and KPIs
    for data in business_objectives:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="business_objective",
            item_type="business_objective",
            status=data["status"],
            priority=data["priority"],
            item_metadata=data["metadata"],
        )
        session.add(item)
        items_by_type.setdefault("business_objective", []).append(item)

    for data in kpis:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="kpi",
            item_type="kpi",
            status=data["status"],
            priority=data["priority"],
            item_metadata=data["metadata"],
        )
        session.add(item)
        items_by_type.setdefault("kpi", []).append(item)

    session.flush()  # Get IDs

    return items_by_type


def create_market_segments_personas(session: Session, project_id: uuid.UUID) -> dict[str, list[Item]]:
    """Create market segments and personas."""
    items = {}

    # Market Segments
    segments = [
        {
            "title": "Urban commuters 25-45",
            "description": "Daily office commuters in metropolitan areas, price-sensitive, value reliability",
            "metadata": {
                "age_range": "25-45",
                "frequency": "5+ rides/week",
                "avg_fare": 18,
                "income": "50K-90K",
                "size": 420000,
            },
        },
        {
            "title": "Airport travelers",
            "description": "Business and leisure travelers needing airport transportation",
            "metadata": {
                "frequency": "occasional",
                "avg_fare": 45,
                "price_sensitivity": "low",
                "luggage_needs": "high",
                "size": 180000,
            },
        },
        {
            "title": "Late-night partiers",
            "description": "Weekend evening riders, bar/restaurant patrons, safety-focused",
            "metadata": {
                "peak_hours": "22:00-02:00",
                "days": "Fri-Sat",
                "avg_fare": 22,
                "safety_priority": "high",
                "size": 95000,
            },
        },
    ]

    for data in segments:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="market_segment",
            item_type="market_segment",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("market_segment", []).append(item)

    # Personas
    personas = [
        {
            "title": "Daily Commuter Sarah",
            "description": "29-year-old marketing manager, uses SwiftRide for daily commute to avoid parking costs",
            "metadata": {
                "age": 29,
                "occupation": "Marketing Manager",
                "income": 75000,
                "goals": ["Save time", "Avoid parking hassle", "Predictable costs"],
                "pain_points": ["Surge pricing during rush hour", "Inconsistent pickup times"],
                "tech_savvy": "high",
                "loyalty": "high",
            },
        },
        {
            "title": "Business Traveler Michael",
            "description": "42-year-old executive, frequent airport rides, values premium service",
            "metadata": {
                "age": 42,
                "occupation": "VP Sales",
                "income": 150000,
                "goals": ["Professional service", "Reliable airport pickup", "Expense reporting"],
                "pain_points": ["Driver unprofessionalism", "Vehicle cleanliness"],
                "preferred_tier": "premium",
                "expensed": True,
            },
        },
        {
            "title": "Student Alex",
            "description": "22-year-old college student, occasional rider, extremely price-sensitive",
            "metadata": {
                "age": 22,
                "occupation": "Student",
                "income": 15000,
                "goals": ["Cheapest option", "Split fares with friends", "Late-night safety"],
                "pain_points": ["High prices", "Minimum fares"],
                "preferred_features": ["shared_rides", "promo_codes"],
                "frequency": "2-3 rides/month",
            },
        },
    ]

    for data in personas:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="persona",
            item_type="persona",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("persona", []).append(item)

    session.flush()
    return items


def create_business_rules_policies(session: Session, project_id: uuid.UUID) -> dict[str, list[Item]]:
    """Create business rules and policies."""
    items = {}

    # Business Rules
    rules = [
        {
            "title": "Surge pricing maximum 3x base rate",
            "description": "Dynamic pricing multiplier cannot exceed 3.0x even during peak demand",
            "metadata": {
                "max_multiplier": 3.0,
                "applies_to": "all_tiers",
                "exceptions": "none",
                "effective_date": "2024-01-01",
            },
        },
        {
            "title": "Cancellation fee after 5 minutes",
            "description": "Riders charged $5 cancellation fee if they cancel >5min after driver accepts",
            "metadata": {"grace_period_seconds": 300, "fee_amount": 5.0, "driver_compensation": 3.0},
        },
        {
            "title": "Driver rating threshold 4.6 for platform access",
            "description": "Drivers with rating below 4.6 over last 100 rides are deactivated pending review",
            "metadata": {
                "min_rating": 4.6,
                "sample_size": 100,
                "review_process": "quality_team",
                "appeal_window_days": 14,
            },
        },
    ]

    for data in rules:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="business_rule",
            item_type="business_rule",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("business_rule", []).append(item)

    # Policies
    policies = [
        {
            "title": "Driver background check policy",
            "description": "All drivers must pass criminal background check, DMV record check, and vehicle inspection before activation",
            "metadata": {
                "checks_required": ["criminal_background", "dmv_record", "vehicle_inspection"],
                "renewal_period_days": 365,
                "disqualifying_offenses": ["DUI", "violent_crime", "sexual_offense"],
                "vendor": "Checkr",
            },
        },
        {
            "title": "Data retention policy",
            "description": "User data retained for 7 years per regulatory requirements, then anonymized or deleted",
            "metadata": {
                "retention_years": 7,
                "applies_to": ["trip_history", "payment_data", "location_data"],
                "anonymization_method": "hashing",
            },
        },
    ]

    for data in policies:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="policy",
            item_type="policy",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("policy", []).append(item)

    session.flush()
    return items


def main() -> None:
    """Main seed function."""
    # Import additional item creators
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).parent))

    try:
        from seed_swiftride_part2 import create_architecture_items, create_testing_items
        from seed_swiftride_part3 import (
            create_compliance_items,
            create_comprehensive_links,
            create_documentation_items,
            create_operations_items,
        )
    except ImportError:
        create_architecture_items = None
        create_testing_items = None
        create_operations_items = None
        create_documentation_items = None
        create_compliance_items = None
        create_comprehensive_links = None

    engine = create_engine(get_database_url())

    with Session(engine) as session:
        # Create SwiftRide project
        project = Project(
            name="SwiftRide",
            description="On-demand rideshare platform connecting riders with drivers",
            project_metadata={
                "industry": "Transportation",
                "business_model": "Marketplace",
                "markets": ["USA", "Canada"],
                "cities": 8,
                "drivers": 45000,
                "riders": 250000,
                "daily_rides": 85000,
            },
        )
        session.add(project)
        session.flush()

        # Create all item types
        all_items = {}

        all_items.update(create_swiftride_items(session, project.id))

        all_items.update(create_market_segments_personas(session, project.id))

        all_items.update(create_business_rules_policies(session, project.id))

        if create_architecture_items:
            all_items.update(create_architecture_items(session, project.id))

        if create_testing_items:
            all_items.update(create_testing_items(session, project.id))

        if create_operations_items:
            all_items.update(create_operations_items(session, project.id))

        if create_documentation_items:
            all_items.update(create_documentation_items(session, project.id))

        if create_compliance_items:
            all_items.update(create_compliance_items(session, project.id))

        # Create links
        if create_comprehensive_links:
            create_comprehensive_links(session, project.id, all_items)

        # Commit all
        session.commit()

        # Print summary
        for _item_type, _items in sorted(all_items.items()):
            pass


if __name__ == "__main__":
    main()
