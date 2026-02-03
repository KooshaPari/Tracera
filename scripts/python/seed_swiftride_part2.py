#!/usr/bin/env python3
"""
SwiftRide seed data - Part 2: Architecture, Development, Testing categories
"""

import uuid

from sqlalchemy.orm import Session

from tracertm.models.item import Item


def create_architecture_items(session: Session, project_id: uuid.UUID) -> dict[str, list[Item]]:
    """Create architecture decisions, microservices, APIs, data models."""

    items = {}

    # Architecture Decisions (ADR format)
    adrs = [
        {
            "title": "ADR-001: Use event-driven architecture for matching service",
            "description": """**Status**: Accepted
**Context**: Need real-time matching with high throughput and fault tolerance
**Decision**: Implement event-driven architecture using NATS Jetstream
**Consequences**: +Scalability +Fault tolerance -Complexity -Eventual consistency""",
            "metadata": {
                "adr_number": 1,
                "status": "accepted",
                "decided_date": "2024-06-15",
                "stakeholders": ["CTO", "Lead Architect"],
            },
        },
        {
            "title": "ADR-002: PostgreSQL for transactional data, Redis for caching",
            "description": """**Status**: Accepted
**Context**: Need ACID guarantees for payments/bookings, low latency for driver locations
**Decision**: PostgreSQL primary datastore, Redis for session/location cache
**Consequences**: +Data integrity +Performance -Operational complexity""",
            "metadata": {"adr_number": 2, "status": "accepted", "decided_date": "2024-05-20"},
        },
        {
            "title": "ADR-003: gRPC for internal service communication",
            "description": """**Status**: Accepted
**Context**: Need efficient, type-safe inter-service communication
**Decision**: Use gRPC with Protobuf for all internal APIs
**Consequences**: +Performance +Type safety -Learning curve""",
            "metadata": {"adr_number": 3, "status": "accepted", "decided_date": "2024-07-10"},
        },
    ]

    for data in adrs:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="architecture_decision",
            item_type="architecture_decision",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("architecture_decision", []).append(item)

    # Microservices
    microservices = [
        {
            "title": "Matching Service",
            "description": "Real-time driver-rider matching engine using geospatial algorithms and demand prediction",
            "metadata": {
                "language": "Go",
                "framework": "none",
                "team": "matching",
                "dependencies": ["location-service", "pricing-service"],
                "sla": "99.9%",
            },
        },
        {
            "title": "Payment Processing Service",
            "description": "PCI-compliant payment processing with Stripe, fraud detection, and chargeback handling",
            "metadata": {
                "language": "Python",
                "framework": "FastAPI",
                "team": "payments",
                "pci_compliant": True,
                "integrations": ["Stripe", "PayPal"],
            },
        },
        {
            "title": "Location Service",
            "description": "GPS tracking, geofencing, ETA calculation, and route optimization",
            "metadata": {
                "language": "Go",
                "framework": "none",
                "team": "core",
                "update_frequency": "5s",
                "accuracy": "10m",
            },
        },
        {
            "title": "Notification Service",
            "description": "Multi-channel notifications via push, SMS, email with delivery tracking",
            "metadata": {
                "language": "Python",
                "framework": "FastAPI",
                "channels": ["FCM", "Twilio", "SendGrid"],
                "daily_volume": 500000,
            },
        },
        {
            "title": "Pricing Service",
            "description": "Dynamic pricing engine with surge calculation, promotions, and fare estimation",
            "metadata": {
                "language": "Python",
                "framework": "FastAPI",
                "ml_model": "XGBoost",
                "features": ["surge", "promotions", "tipping"],
            },
        },
    ]

    for data in microservices:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="microservice",
            item_type="microservice",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("microservice", []).append(item)

    # API Contracts
    api_contracts = [
        {
            "title": "POST /v1/rides - Request Ride",
            "description": "Create new ride request with pickup/dropoff locations, payment method, and preferences",
            "metadata": {
                "method": "POST",
                "path": "/v1/rides",
                "request_schema": {
                    "pickup": "LatLng",
                    "dropoff": "LatLng",
                    "payment_method_id": "string",
                    "rider_id": "uuid",
                },
                "response_schema": {"ride_id": "uuid", "eta_seconds": "int", "estimated_fare": "decimal"},
                "auth": "Bearer",
                "rate_limit": "10/minute",
            },
        },
        {
            "title": "GET /v1/drivers/nearby - Find Nearby Drivers",
            "description": "Query drivers within radius of location, filtered by vehicle type and availability",
            "metadata": {
                "method": "GET",
                "path": "/v1/drivers/nearby",
                "params": {"lat": "float", "lng": "float", "radius_km": "float", "vehicle_type": "string"},
                "response": "Driver[]",
                "cache_ttl": 30,
            },
        },
        {
            "title": "PUT /v1/rides/{id}/accept - Driver Accept Ride",
            "description": "Driver accepts ride request, locks in driver-rider match",
            "metadata": {"method": "PUT", "path": "/v1/rides/{id}/accept", "auth": "driver_token", "idempotency": True},
        },
    ]

    for data in api_contracts:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="api_contract",
            item_type="api_contract",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("api_contract", []).append(item)

    # Data Models
    data_models = [
        {
            "title": "Ride Entity",
            "description": "Core ride/trip entity with status machine, locations, pricing, and participant references",
            "metadata": {
                "fields": [
                    "id:uuid",
                    "rider_id:uuid",
                    "driver_id:uuid",
                    "status:enum",
                    "pickup_location:point",
                    "dropoff_location:point",
                    "fare:decimal",
                ],
                "relationships": ["rider->User", "driver->Driver", "payment->Payment"],
                "indexes": ["rider_id", "driver_id", "status", "created_at"],
            },
        },
        {
            "title": "Driver Entity",
            "description": "Driver profile with vehicle info, ratings, availability, and compliance status",
            "metadata": {
                "fields": [
                    "id:uuid",
                    "user_id:uuid",
                    "vehicle_id:uuid",
                    "rating:decimal",
                    "status:enum",
                    "location:point",
                ],
                "relationships": ["user->User", "vehicle->Vehicle", "rides->Ride[]"],
            },
        },
    ]

    for data in data_models:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="data_model",
            item_type="data_model",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("data_model", []).append(item)

    # Domain Events
    events = [
        {
            "title": "RideRequested",
            "description": "Published when rider creates new ride request",
            "metadata": {
                "topic": "rides.requested",
                "schema": {"ride_id": "uuid", "rider_id": "uuid", "pickup": "LatLng", "timestamp": "datetime"},
            },
        },
        {
            "title": "RideMatched",
            "description": "Published when driver is matched to ride",
            "metadata": {"topic": "rides.matched", "schema": {"ride_id": "uuid", "driver_id": "uuid", "eta": "int"}},
        },
        {
            "title": "RideCompleted",
            "description": "Published when ride ends successfully",
            "metadata": {
                "topic": "rides.completed",
                "schema": {"ride_id": "uuid", "distance_km": "float", "duration_seconds": "int", "fare": "decimal"},
            },
        },
    ]

    for data in events:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="event",
            item_type="event",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("event", []).append(item)

    session.flush()
    return items


def create_testing_items(session: Session, project_id: uuid.UUID) -> dict[str, list[Item]]:
    """Create test plans, scenarios, cases, and quality items."""

    items = {}

    # Test Plans
    test_plans = [
        {
            "title": "Ride Booking Flow Test Plan",
            "description": "Comprehensive test plan for ride request, matching, tracking, and completion flow",
            "metadata": {
                "scope": ["unit", "integration", "e2e"],
                "priority": "P0",
                "test_count": 47,
                "coverage_target": 0.90,
            },
        },
        {
            "title": "Payment Processing Test Plan",
            "description": "Test plan for payment methods, tokenization, charges, refunds, and fraud detection",
            "metadata": {"scope": ["integration", "e2e", "security"], "pci_requirements": True, "test_count": 32},
        },
    ]

    for data in test_plans:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="test_plan",
            item_type="test_plan",
            status="complete",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("test_plan", []).append(item)

    # Test Scenarios
    test_scenarios = [
        {
            "title": "Happy path: Rider books ride, driver accepts, completes trip",
            "description": "End-to-end scenario covering successful ride from request to payment",
            "metadata": {
                "type": "e2e",
                "steps": 12,
                "duration": "8min",
                "preconditions": ["active_driver_nearby", "valid_payment_method"],
            },
        },
        {
            "title": "Edge case: Ride request timeout (no drivers available)",
            "description": "Test behavior when no drivers accept ride within timeout window",
            "metadata": {"type": "integration", "timeout": 300, "expected_outcome": "ride_cancelled", "refund": "full"},
        },
        {
            "title": "Error case: Payment failure mid-ride",
            "description": "Handle payment authorization failure during active ride",
            "metadata": {
                "type": "integration",
                "trigger": "card_decline",
                "expected_outcome": "prompt_alternative_payment",
            },
        },
    ]

    for data in test_scenarios:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="test_scenario",
            item_type="test_scenario",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("test_scenario", []).append(item)

    # Performance Benchmarks
    benchmarks = [
        {
            "title": "Matching engine: 10K concurrent ride requests",
            "description": "Load test matching service with 10,000 simultaneous ride requests",
            "metadata": {
                "rps": 10000,
                "p95_latency_target": 500,
                "p99_latency_target": 1000,
                "success_rate_target": 0.999,
            },
        },
        {
            "title": "API gateway: 50K req/sec sustained load",
            "description": "Sustained load test on API gateway across all endpoints",
            "metadata": {"rps": 50000, "duration_minutes": 30, "cpu_target": 0.70, "error_rate_target": 0.001},
        },
    ]

    for data in benchmarks:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="performance_benchmark",
            item_type="performance_benchmark",
            status="complete",
            priority=4,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("performance_benchmark", []).append(item)

    # Security Vulnerabilities
    vulnerabilities = [
        {
            "title": "CVE-2024-XXXX: Location spoofing via GPS manipulation",
            "description": "Drivers can manipulate GPS coordinates to game surge pricing zones",
            "metadata": {
                "severity": "HIGH",
                "cvss": 7.5,
                "status": "MITIGATED",
                "mitigation": "GPS validation + accelerometer cross-check",
            },
        },
        {
            "title": "Payment token exposure in client logs",
            "description": "Sensitive payment tokens logged in plaintext on mobile apps",
            "metadata": {
                "severity": "CRITICAL",
                "cvss": 9.1,
                "status": "FIXED",
                "fix_version": "v2.3.1",
                "pci_violation": True,
            },
        },
    ]

    for data in vulnerabilities:
        item = Item(
            project_id=project_id,
            title=data["title"],
            description=data["description"],
            view="security_vulnerability",
            item_type="security_vulnerability",
            status="complete" if (isinstance(data.get("metadata"), dict) and (m := data["metadata"]) and m.get("status") == "FIXED") else "in_progress",
            priority=5,
            item_metadata=data["metadata"],
        )
        session.add(item)
        items.setdefault("security_vulnerability", []).append(item)

    session.flush()
    return items
