# SwiftRide Item Types Quick Reference

## Overview

SwiftRide demo project includes **74 item types** across 8 categories, demonstrating comprehensive traceability from business strategy to operational compliance.

## Quick Lookup by Category

### 🎯 Business & Strategy (7 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `business_objective` | Strategic goals | "Achieve 1M active users by Q4 2026" |
| `kpi` | Performance metrics | "Driver retention rate >80%" |
| `market_segment` | Target markets | "Urban commuters 25-45" |
| `persona` | User archetypes | "Daily Commuter Sarah" |
| `business_rule` | Business logic | "Surge pricing max 3x base rate" |
| `compliance_requirement` | Regulatory needs | "GDPR data retention compliance" |
| `policy` | Organizational rules | "Driver background check policy" |

### 📊 Product Management (5 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `initiative` | Strategic efforts | "International expansion" |
| `epic` | Large features | "Multi-modal transportation" |
| `capability` | System abilities | "Real-time ride tracking" |
| `value_stream` | Value flows | "Rider acquisition to retention" |
| `roadmap_item` | Planned features | "Q2 2026: Launch bike-sharing" |

### 🏗️ Architecture & Design (8 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `architecture_decision` | ADRs | "ADR-001: Event-driven architecture for matching" |
| `system_component` | Major components | "Ride Matching System" |
| `microservice` | Services | "Payment Processing Service" |
| `api_contract` | API specs | "POST /v1/rides - Request Ride" |
| `data_model` | Entities | "Ride Entity", "Driver Entity" |
| `integration_point` | External APIs | "Stripe Payment Gateway" |
| `event` | Domain events | "RideRequested", "RideCompleted" |
| `message_queue` | Queue topics | "rides.requested" |

### 💻 Development (12 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `backend_service` | Backend code | "Matching Engine Go Service" |
| `frontend_component` | UI components | "RideRequestForm React Component" |
| `database_table` | DB tables | "rides", "drivers", "payments" |
| `database_index` | Performance indexes | "idx_rides_status_created_at" |
| `api_endpoint` | REST endpoints | "GET /v1/drivers/nearby" |
| `graphql_resolver` | GraphQL resolvers | "Query.nearbyDrivers" |
| `background_job` | Async jobs | "MatchRideWithDriver job" |
| `scheduled_task` | Cron tasks | "Daily driver payout calculation" |
| `configuration` | Service config | "Matching service config.yaml" |
| `environment_variable` | Env vars | "SURGE_MAX_MULTIPLIER" |
| `dependency` | External packages | "stripe-python v5.0" |

### 🧪 Testing & Quality (14 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `test_plan` | Test coverage plans | "Ride Booking Flow Test Plan" |
| `test_strategy` | Testing approach | "E2E Testing Strategy" |
| `test_scenario` | Test scenarios | "Happy path: Ride booking" |
| `test_case` | Specific tests | "Test surge pricing calculation" |
| `test_step` | Individual steps | "1. Request ride with valid pickup" |
| `acceptance_test` | UAT tests | "Rider can complete first ride" |
| `regression_test` | Regression suites | "Payment processing regression suite" |
| `performance_benchmark` | Perf targets | "10K concurrent ride requests" |
| `load_test_scenario` | Load tests | "Black Friday surge scenario" |
| `security_vulnerability` | Security issues | "CVE-2024-XXXX: GPS spoofing" |
| `security_control` | Security measures | "GPS validation + accelerometer check" |
| `accessibility_requirement` | A11y needs | "WCAG 2.1 AA compliance" |
| `wcag_criterion` | WCAG standards | "1.4.3 Contrast Minimum" |

### 🚀 Operations & Deployment (10 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `deployment_environment` | Environments | "Production - US East (AWS us-east-1)" |
| `infrastructure_resource` | Cloud resources | "RDS PostgreSQL db.r6g.2xlarge" |
| `monitoring_metric` | Observability | "Ride acceptance rate" |
| `alert_rule` | Alerting | "P99 latency >1000ms" |
| `runbook` | Operational docs | "Database failover procedure" |
| `incident_response_plan` | IR playbooks | "Payment gateway outage response" |
| `backup_strategy` | Backup procedures | "RDS automated backups + snapshots" |
| `disaster_recovery_plan` | DR procedures | "Multi-region failover plan" |
| `scaling_policy` | Auto-scaling | "Matching service HPA policy" |
| `capacity_plan` | Capacity planning | "Q2 2026 infrastructure scaling" |

### 📚 Documentation (10 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `technical_spec` | Tech specs | "Driver Matching Algorithm Spec" |
| `api_doc` | API documentation | "Rider API v1 Documentation" |
| `user_manual` | User guides | "Rider App User Guide" |
| `tutorial` | Step-by-step guides | "Getting Started: First Ride" |
| `architecture_diagram` | System diagrams | "SwiftRide System Architecture" |
| `sequence_diagram` | Interaction flows | "Ride Request Flow Sequence" |
| `release_note` | Release notes | "v2.5.0 Release Notes" |
| `changelog_entry` | Changelog items | "Added shared ride feature" |
| `troubleshooting_guide` | Support docs | "Payment declined troubleshooting" |
| `faq_item` | FAQ entries | "How do I add a payment method?" |

### ⚖️ Compliance & Legal (8 types)

| Item Type | Purpose | Example |
|-----------|---------|---------|
| `regulation` | Legal regulations | "GDPR", "PCI DSS v4.0" |
| `legal_requirement` | Legal obligations | "California AB5 driver classification" |
| `audit_requirement` | Audit needs | "Annual PCI DSS audit" |
| `control` | Control implementations | "Payment data encryption control" |
| `privacy_policy_clause` | Privacy clauses | "Location data usage clause" |
| `terms_of_service_clause` | ToS sections | "Cancellation policy clause" |
| `data_retention_rule` | Retention policies | "Trip history: 7 years" |
| `consent_requirement` | User consent | "Background location tracking consent" |

## Common Link Types

| Link Type | Usage | Example |
|-----------|-------|---------|
| `IMPLEMENTS` | Implementation | `Pricing Service` → `IMPLEMENTS` → `Surge pricing rule` |
| `TESTS` | Testing | `Ride test plan` → `TESTS` → `Matching Service` |
| `DEPENDS_ON` | Dependencies | `Matching Service` → `DEPENDS_ON` → `PostgreSQL` |
| `VALIDATES` | Validation | `Business Objective` → `VALIDATES` → `KPI` |
| `DOCUMENTS` | Documentation | `API Doc` → `DOCUMENTS` → `Matching Service` |
| `EXPOSES` | API exposure | `Service` → `EXPOSES` → `API Contract` |
| `PARENT_OF` | Hierarchy | `GDPR` → `PARENT_OF` → `GDPR Compliance Req` |
| `RELATES_TO` | Association | `Vulnerability` → `RELATES_TO` → `Service` |

## Metadata Examples

### Business Objective
```yaml
metadata:
  target: 1000000
  current: 250000
  deadline: "2026-Q4"
  owner: "CPO"
  metrics: ["MAU", "retention_rate"]
```

### KPI
```yaml
metadata:
  type: "retention"
  target: 0.80
  current: 0.83
  measurement: "90_day_active"
  frequency: "weekly"
```

### Microservice
```yaml
metadata:
  language: "Go"
  team: "matching"
  dependencies: ["location-service", "pricing-service"]
  sla: "99.9%"
```

### API Contract
```yaml
metadata:
  method: "POST"
  path: "/v1/rides"
  auth: "Bearer"
  rate_limit: "10/minute"
  request_schema: {...}
  response_schema: {...}
```

### Security Vulnerability
```yaml
metadata:
  severity: "HIGH"
  cvss: 7.5
  status: "MITIGATED"
  mitigation: "GPS validation + accelerometer cross-check"
```

### Infrastructure Resource
```yaml
metadata:
  type: "RDS"
  engine: "postgresql-15"
  instance: "db.r6g.2xlarge"
  storage_gb: 2000
  iops: 10000
```

## Usage Tips

### Creating New Items
```bash
# Use .trace file format
# Example: .trace/business_objectives/BIZ-OBJ-001.md

---
type: business_objective
status: in_progress
priority: 5
---

# Achieve 1M active users by Q4 2026

Grow user base from 250K to 1M monthly active users.

## Metadata
- target: 1000000
- current: 250000
- deadline: 2026-Q4
```

### Linking Items
```yaml
# In .trace/.meta/links.yaml
links:
  - source: pricing-service
    target: surge-pricing-rule
    type: IMPLEMENTS

  - source: ride-test-plan
    target: matching-service
    type: TESTS
```

## Seed Script Usage

```bash
# Set database connection
export DATABASE_URL="postgresql://user:pass@localhost/tracertm"

# Run comprehensive seed
python scripts/seed_swiftride_comprehensive.py

# Expected output
Creating business objectives and KPIs...
Creating market segments and personas...
Creating architecture items...
...
Total items: 70+
Total item types: 25+
```

## Benefits

- **Complete Lifecycle Coverage**: From strategy to operations
- **Realistic Examples**: Domain-specific SwiftRide context
- **Rich Traceability**: Multi-directional links across all layers
- **Production Metadata**: Real SLAs, metrics, and targets
- **Compliance Ready**: GDPR, PCI DSS, and regulatory examples

## Next Steps

1. Run seed script to populate database
2. Explore items in TraceRTM UI
3. View traceability links in graph visualization
4. Add custom item types for your domain
5. Extend with more examples (target: 20-50 per type)
