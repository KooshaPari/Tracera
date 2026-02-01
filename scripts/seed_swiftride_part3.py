#!/usr/bin/env python3
"""
SwiftRide seed data - Part 3: Operations, Documentation, Compliance categories
"""

import uuid
from typing import Dict, List
from tracertm.models.item import Item
from tracertm.models.link import Link
from sqlalchemy.orm import Session


def create_operations_items(session: Session, project_id: uuid.UUID) -> Dict[str, List[Item]]:
    """Create deployment environments, infrastructure, monitoring, runbooks."""

    items = {}

    # Deployment Environments
    environments = [
        {
            "title": "Production - US East",
            "description": "Primary production environment serving US East Coast (AWS us-east-1)",
            "metadata": {"region": "us-east-1", "cloud": "AWS", "kubernetes": "1.28", "nodes": 45, "traffic_pct": 0.40},
        },
        {
            "title": "Production - US West",
            "description": "Production environment serving US West Coast (AWS us-west-2)",
            "metadata": {"region": "us-west-2", "cloud": "AWS", "kubernetes": "1.28", "nodes": 38, "traffic_pct": 0.35},
        },
        {
            "title": "Staging",
            "description": "Pre-production staging environment for final validation",
            "metadata": {"region": "us-east-1", "cloud": "AWS", "kubernetes": "1.28", "nodes": 8, "purpose": "qa_validation"},
        },
    ]

    for data in environments:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="deployment_environment",
            item_type="deployment_environment",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("deployment_environment", []).append(item)

    # Infrastructure Resources
    infrastructure = [
        {
            "title": "RDS PostgreSQL Primary - rides database",
            "description": "Production PostgreSQL 15 instance for transactional data",
            "metadata": {"type": "RDS", "engine": "postgresql-15", "instance": "db.r6g.2xlarge", "storage_gb": 2000, "iops": 10000},
        },
        {
            "title": "ElastiCache Redis - session store",
            "description": "Redis cluster for session management and real-time driver locations",
            "metadata": {"type": "ElastiCache", "engine": "redis-7.0", "node_type": "cache.r6g.xlarge", "nodes": 6, "memory_gb": 192},
        },
        {
            "title": "EKS Cluster - microservices",
            "description": "Kubernetes cluster running all microservices",
            "metadata": {"type": "EKS", "version": "1.28", "node_groups": 3, "total_nodes": 45, "cpu_cores": 720, "memory_gb": 2880},
        },
    ]

    for data in infrastructure:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="infrastructure_resource",
            item_type="infrastructure_resource",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("infrastructure_resource", []).append(item)

    # Monitoring Metrics
    metrics = [
        {
            "title": "Ride acceptance rate",
            "description": "Percentage of ride requests accepted by drivers within timeout window",
            "metadata": {"type": "business", "target": 0.92, "current": 0.89, "alert_threshold": 0.85, "measurement": "1min_avg"},
        },
        {
            "title": "Matching service P99 latency",
            "description": "99th percentile latency for driver-rider matching algorithm",
            "metadata": {"type": "performance", "target_ms": 500, "current_ms": 385, "alert_threshold_ms": 1000},
        },
        {
            "title": "Payment success rate",
            "description": "Successful payment authorizations as percentage of attempts",
            "metadata": {"type": "business", "target": 0.98, "current": 0.975, "alert_threshold": 0.95},
        },
    ]

    for data in metrics:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="monitoring_metric",
            item_type="monitoring_metric",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("monitoring_metric", []).append(item)

    # Runbooks
    runbooks = [
        {
            "title": "Runbook: Database failover procedure",
            "description": "Step-by-step procedure for failing over to PostgreSQL replica during primary failure",
            "metadata": {"category": "incident", "rto_minutes": 15, "steps": 8, "required_role": "dba", "last_tested": "2024-12-01"},
        },
        {
            "title": "Runbook: Scaling during surge events",
            "description": "Procedure for horizontal scaling of matching service during demand spikes",
            "metadata": {"category": "operations", "auto_scale": True, "manual_override": True, "max_replicas": 50},
        },
    ]

    for data in runbooks:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="runbook",
            item_type="runbook",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("runbook", []).append(item)

    # Scaling Policies
    scaling_policies = [
        {
            "title": "Matching service horizontal autoscaling",
            "description": "Scale matching service pods based on CPU >70% or request queue depth >100",
            "metadata": {"triggers": ["cpu>0.70", "queue_depth>100"], "min_replicas": 5, "max_replicas": 50, "cooldown_seconds": 300},
        },
    ]

    for data in scaling_policies:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="scaling_policy",
            item_type="scaling_policy",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("scaling_policy", []).append(item)

    session.flush()
    return items


def create_documentation_items(session: Session, project_id: uuid.UUID) -> Dict[str, List[Item]]:
    """Create documentation items."""

    items = {}

    # Technical Specs
    tech_specs = [
        {
            "title": "Driver Matching Algorithm Specification",
            "description": "Detailed specification of geospatial matching algorithm, scoring function, and optimization constraints",
            "metadata": {"version": "2.1", "author": "Lead Engineer", "last_updated": "2024-11-15", "pages": 23},
        },
        {
            "title": "Surge Pricing Model Technical Specification",
            "description": "Mathematical model for dynamic pricing including demand prediction and price elasticity",
            "metadata": {"version": "1.5", "model_type": "XGBoost", "features": 47, "training_data": "6_months"},
        },
    ]

    for data in tech_specs:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="technical_spec",
            item_type="technical_spec",
            status="complete",
            priority=3,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("technical_spec", []).append(item)

    # API Documentation
    api_docs = [
        {
            "title": "Rider API v1 Documentation",
            "description": "Complete API reference for rider mobile app including authentication, ride booking, and payment",
            "metadata": {"version": "1.0", "format": "OpenAPI 3.0", "endpoints": 28, "authentication": "OAuth2"},
        },
        {
            "title": "Driver API v1 Documentation",
            "description": "API reference for driver app including ride acceptance, navigation, and earnings",
            "metadata": {"version": "1.0", "format": "OpenAPI 3.0", "endpoints": 22, "authentication": "Bearer"},
        },
    ]

    for data in api_docs:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="api_doc",
            item_type="api_doc",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("api_doc", []).append(item)

    # Tutorials
    tutorials = [
        {
            "title": "Getting Started: Rider App Tutorial",
            "description": "Step-by-step tutorial for new riders covering account setup, first ride, and payments",
            "metadata": {"audience": "riders", "duration_min": 5, "steps": 8, "completion_rate": 0.78},
        },
        {
            "title": "Driver Onboarding Tutorial",
            "description": "Complete onboarding guide for new drivers including background check, vehicle registration, and first ride",
            "metadata": {"audience": "drivers", "duration_min": 15, "steps": 12, "completion_rate": 0.92},
        },
    ]

    for data in tutorials:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="tutorial",
            item_type="tutorial",
            status="complete",
            priority=3,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("tutorial", []).append(item)

    # Troubleshooting Guides
    troubleshooting = [
        {
            "title": "Troubleshooting: Ride not matching with driver",
            "description": "Common issues and solutions when ride requests don't match with drivers",
            "metadata": {"category": "rider_support", "resolution_rate": 0.85, "avg_resolution_time_min": 3},
        },
        {
            "title": "Troubleshooting: Payment declined issues",
            "description": "Diagnostic steps and solutions for payment authorization failures",
            "metadata": {"category": "payment_support", "common_causes": ["insufficient_funds", "expired_card", "fraud_block"]},
        },
    ]

    for data in troubleshooting:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="troubleshooting_guide",
            item_type="troubleshooting_guide",
            status="complete",
            priority=3,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("troubleshooting_guide", []).append(item)

    session.flush()
    return items


def create_compliance_items(session: Session, project_id: uuid.UUID) -> Dict[str, List[Item]]:
    """Create compliance and legal items."""

    items = {}

    # Regulations
    regulations = [
        {
            "title": "GDPR - General Data Protection Regulation",
            "description": "EU data protection and privacy regulation affecting user data handling",
            "metadata": {"jurisdiction": "EU", "effective_date": "2018-05-25", "applies_to": ["EU_users"], "penalties": "4%_global_revenue"},
        },
        {
            "title": "CPRA - California Privacy Rights Act",
            "description": "California consumer privacy law extending CCPA requirements",
            "metadata": {"jurisdiction": "California", "effective_date": "2023-01-01", "applies_to": ["CA_residents"]},
        },
        {
            "title": "PCI DSS - Payment Card Industry Data Security Standard",
            "description": "Security standards for handling credit card information",
            "metadata": {"version": "4.0", "level": "1", "applies_to": ["payment_processing"], "audit_frequency": "annual"},
        },
    ]

    for data in regulations:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="regulation",
            item_type="regulation",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("regulation", []).append(item)

    # Compliance Requirements
    compliance_reqs = [
        {
            "title": "GDPR data retention policy compliance",
            "description": "Implement 7-year data retention with right to erasure and data portability",
            "metadata": {"regulation": "GDPR", "requirements": ["retention_limits", "right_to_erasure", "data_portability"], "status": "compliant"},
        },
        {
            "title": "PCI DSS secure payment tokenization",
            "description": "Implement PCI-compliant payment tokenization using Stripe",
            "metadata": {"regulation": "PCI DSS", "controls": ["tokenization", "encryption", "access_control"], "status": "compliant"},
        },
    ]

    for data in compliance_reqs:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="compliance_requirement",
            item_type="compliance_requirement",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("compliance_requirement", []).append(item)

    # Data Retention Rules
    retention_rules = [
        {
            "title": "Trip history retention: 7 years",
            "description": "Retain ride history for 7 years per tax and legal requirements, then anonymize",
            "metadata": {"retention_years": 7, "data_types": ["trips", "payments", "locations"], "post_retention": "anonymize"},
        },
        {
            "title": "Location data retention: 90 days",
            "description": "Retain detailed GPS traces for 90 days for dispute resolution, then aggregate",
            "metadata": {"retention_days": 90, "data_types": ["gps_traces"], "post_retention": "aggregate_only"},
        },
    ]

    for data in retention_rules:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="data_retention_rule",
            item_type="data_retention_rule",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("data_retention_rule", []).append(item)

    # Consent Requirements
    consent_reqs = [
        {
            "title": "Location tracking consent",
            "description": "Explicit user consent required for background location tracking",
            "metadata": {"consent_type": "explicit", "scope": "background_location", "withdrawal": "anytime", "granular": True},
        },
        {
            "title": "Marketing communications consent",
            "description": "Opt-in consent for promotional emails and push notifications",
            "metadata": {"consent_type": "opt_in", "channels": ["email", "push", "sms"], "default": False},
        },
    ]

    for data in consent_reqs:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="consent_requirement",
            item_type="consent_requirement",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("consent_requirement", []).append(item)

    session.flush()
    return items


def create_comprehensive_links(session: Session, project_id: uuid.UUID, all_items: Dict[str, List[Item]]) -> List[Link]:
    """Create rich traceability links between items."""

    links = []

    # Helper to get first item of type
    def get_item(item_type: str, index: int = 0) -> Item:
        return all_items.get(item_type, [])[index] if all_items.get(item_type) else None

    # Business objectives -> KPIs
    obj_1m_users = get_item("business_objective", 0)
    kpi_retention = get_item("kpi", 0)
    if obj_1m_users and kpi_retention:
        links.append(Link(
            project_id=project_id,
            source_item_id=obj_1m_users.id,
            target_item_id=kpi_retention.id,
            link_type="VALIDATES",
            link_metadata={"description": "Driver retention KPI validates 1M user growth objective"}
        ))

    # Business rules -> Microservices (implements)
    surge_rule = get_item("business_rule", 0)
    pricing_service = get_item("microservice", 4)
    if surge_rule and pricing_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=pricing_service.id,
            target_item_id=surge_rule.id,
            link_type="IMPLEMENTS",
            link_metadata={"description": "Pricing service implements surge pricing business rule"}
        ))

    # Architecture decisions -> Microservices
    adr_events = get_item("architecture_decision", 0)
    matching_service = get_item("microservice", 0)
    if adr_events and matching_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=matching_service.id,
            target_item_id=adr_events.id,
            link_type="IMPLEMENTS",
            link_metadata={"description": "Matching service implements event-driven architecture"}
        ))

    # Test plans -> Microservices (tests)
    ride_test_plan = get_item("test_plan", 0)
    if ride_test_plan and matching_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=ride_test_plan.id,
            target_item_id=matching_service.id,
            link_type="TESTS",
            link_metadata={"description": "Ride booking test plan tests matching service"}
        ))

    # API contracts -> Microservices (exposes)
    api_request_ride = get_item("api_contract", 0)
    if api_request_ride and matching_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=matching_service.id,
            target_item_id=api_request_ride.id,
            link_type="EXPOSES",
            link_metadata={"description": "Matching service exposes ride request API"}
        ))

    # Compliance requirements -> Data retention rules (IMPLEMENTS)
    gdpr_compliance = get_item("compliance_requirement", 0)
    retention_trips = get_item("data_retention_rule", 0)
    if gdpr_compliance and retention_trips:
        links.append(Link(
            project_id=project_id,
            source_item_id=retention_trips.id,
            target_item_id=gdpr_compliance.id,
            link_type="IMPLEMENTS",
            link_metadata={"description": "Trip retention rule implements GDPR compliance requirement"}
        ))

    # Regulations -> Compliance requirements (PARENT_OF)
    gdpr_reg = get_item("regulation", 0)
    if gdpr_reg and gdpr_compliance:
        links.append(Link(
            project_id=project_id,
            source_item_id=gdpr_reg.id,
            target_item_id=gdpr_compliance.id,
            link_type="PARENT_OF",
            link_metadata={"description": "GDPR regulation parent of compliance requirements"}
        ))

    # Security vulnerabilities -> Security controls
    vuln_location = get_item("security_vulnerability", 0)
    payment_service = get_item("microservice", 1)
    if vuln_location and payment_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=vuln_location.id,
            target_item_id=payment_service.id,
            link_type="RELATES_TO",
            link_metadata={"description": "Location spoofing vulnerability relates to payment service"}
        ))

    # Documentation -> Microservices (DOCUMENTS)
    api_doc_rider = get_item("api_doc", 0)
    if api_doc_rider and matching_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=api_doc_rider.id,
            target_item_id=matching_service.id,
            link_type="DOCUMENTS",
            link_metadata={"description": "Rider API documentation documents matching service"}
        ))

    # Infrastructure -> Microservices (DEPENDS_ON)
    postgres_db = get_item("infrastructure_resource", 0)
    if postgres_db and matching_service:
        links.append(Link(
            project_id=project_id,
            source_item_id=matching_service.id,
            target_item_id=postgres_db.id,
            link_type="DEPENDS_ON",
            link_metadata={"description": "Matching service depends on PostgreSQL database"}
        ))

    for link in links:
        session.add(link)

    session.flush()
    return links
