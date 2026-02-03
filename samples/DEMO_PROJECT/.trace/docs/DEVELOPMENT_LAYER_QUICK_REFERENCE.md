# Development Layer - Quick Reference

**SwiftRide Development Layer** | 660 Items | 7 Types

---

## 📂 Item Types

| Type | Count | Location | Purpose |
|------|-------|----------|---------|
| **python_file** | 150 | `python_files/` | Backend services, models, repos, routes, workers |
| **typescript_file** | 150 | `typescript_files/` | React components, hooks, stores, API clients |
| **go_file** | 100 | `go_files/` | Microservices, handlers, models, middleware |
| **database_migration** | 80 | `database_migrations/` | Alembic schema migrations |
| **configuration** | 70 | `configurations/` | Service configs, env vars, infra |
| **background_job** | 60 | `background_jobs/` | Async task definitions |
| **scheduled_task** | 50 | `scheduled_tasks/` | Cron jobs, periodic tasks |

---

## 🐍 Python Files (150)

### Services (001-030)
```
PYTHON_FILE-001: services/matching_service.py
PYTHON_FILE-002: services/pricing_service.py
PYTHON_FILE-003: services/payment_service.py
...
PYTHON_FILE-030: services/ride_pooling_service.py
```

### Models (061-100)
```
PYTHON_FILE-061: models/driver.py
PYTHON_FILE-062: models/rider.py
PYTHON_FILE-063: models/trip.py
...
PYTHON_FILE-100: models/rider_preference.py
```

### Repositories (141-170)
```
PYTHON_FILE-141: repositories/driver_repository.py
PYTHON_FILE-142: repositories/rider_repository.py
...
PYTHON_FILE-170: repositories/user_repository.py
```

### API Routes (201-225)
```
PYTHON_FILE-201: api/routes/drivers.py
PYTHON_FILE-202: api/routes/riders.py
PYTHON_FILE-203: api/routes/trips.py
...
PYTHON_FILE-225: api/routes/search.py
```

### Workers (251-275)
```
PYTHON_FILE-251: workers/matching_worker.py
PYTHON_FILE-252: workers/notification_worker.py
...
PYTHON_FILE-275: workers/trip_archival_worker.py
```

**Links:**
- Services → `MICROSERVICE-001` (part_of), `ENDPOINT-004` (implements)
- Models → `TABLE-003` (maps_to)
- Repositories → `TABLE-003` (reads_from), `TABLE-004` (writes_to)
- Routes → `ENDPOINT-004` (implements)
- Workers → `BACKGROUND_JOB-001` (executes)

---

## ⚛️ TypeScript Files (150)

### Components (001-050)
```
TYPESCRIPT_FILE-001: components/DriverDashboard.tsx
TYPESCRIPT_FILE-002: components/RiderApp.tsx
TYPESCRIPT_FILE-003: components/RideRequest.tsx
...
TYPESCRIPT_FILE-050: components/AccessibilityOptions.tsx
```

### Hooks (101-140)
```
TYPESCRIPT_FILE-101: hooks/useRideStatus.ts
TYPESCRIPT_FILE-102: hooks/useDriverLocation.ts
TYPESCRIPT_FILE-103: hooks/usePayment.ts
...
TYPESCRIPT_FILE-140: hooks/useInfiniteScroll.ts
```

### Stores (181-210)
```
TYPESCRIPT_FILE-181: stores/rideStore.ts
TYPESCRIPT_FILE-182: stores/driverStore.ts
TYPESCRIPT_FILE-183: stores/authStore.ts
...
TYPESCRIPT_FILE-210: stores/favoriteStore.ts
```

### API Clients (241-270)
```
TYPESCRIPT_FILE-241: api/driversApi.ts
TYPESCRIPT_FILE-242: api/ridersApi.ts
TYPESCRIPT_FILE-243: api/tripsApi.ts
...
TYPESCRIPT_FILE-270: api/settingsApi.ts
```

**Links:**
- Components → `SCREEN-001` (implements)
- Hooks → `ENDPOINT-004` (calls)
- API Clients → `ENDPOINT-004` (calls)

---

## 🔷 Go Files (100)

### Services (001-025)
```
GO_FILE-001: services/matching/service.go
GO_FILE-002: services/pricing/calculator.go
GO_FILE-003: services/location/tracker.go
...
GO_FILE-025: services/referral/tracker.go
```

### Handlers (051-075)
```
GO_FILE-051: handlers/driver_handler.go
GO_FILE-052: handlers/rider_handler.go
GO_FILE-053: handlers/trip_handler.go
...
GO_FILE-075: handlers/webhook_handler.go
```

### Models (101-125)
```
GO_FILE-101: models/ride.go
GO_FILE-102: models/driver.go
GO_FILE-103: models/rider.go
...
GO_FILE-125: models/user.go
```

### Middleware (151-165)
```
GO_FILE-151: middleware/auth.go
GO_FILE-152: middleware/ratelimit.go
GO_FILE-153: middleware/cors.go
...
GO_FILE-165: middleware/throttle.go
```

### Utilities (181-190)
```
GO_FILE-181: utils/geo.go
GO_FILE-182: utils/distance.go
...
GO_FILE-190: utils/currency.go
```

**Links:**
- Services → `MICROSERVICE-001` (part_of)
- Handlers → `ENDPOINT-004` (implements)
- Models → `TABLE-003` (maps_to)

---

## 🗄️ Database Migrations (80)

### Core Tables (001-025)
```
DATABASE_MIGRATION-001: 001_create_users_table.py
DATABASE_MIGRATION-002: 002_create_drivers_table.py
DATABASE_MIGRATION-003: 003_create_riders_table.py
DATABASE_MIGRATION-004: 004_create_vehicles_table.py
DATABASE_MIGRATION-005: 005_create_trips_table.py
...
DATABASE_MIGRATION-025: 025_create_transactions_table.py
```

### Indexes (026-047)
```
DATABASE_MIGRATION-026: 026_add_users_indexes.py
DATABASE_MIGRATION-027: 027_add_trips_indexes.py
DATABASE_MIGRATION-028: 028_add_payments_indexes.py
...
DATABASE_MIGRATION-047: 047_add_full_text_search.py
```

### Extended Features (048-080)
```
DATABASE_MIGRATION-048: 048_create_vehicle_types_table.py
DATABASE_MIGRATION-049: 049_create_shifts_table.py
DATABASE_MIGRATION-050: 050_create_incentives_table.py
...
DATABASE_MIGRATION-080: 080_add_analytics_materialized_views.py
```

**Links:**
- All migrations → `TABLE-003` (creates)

---

## ⚙️ Configurations (70)

### Application (001-030)
```
CONFIGURATION-001: config/backend.env
CONFIGURATION-002: config/frontend.env
CONFIGURATION-003: config/matching-service.yaml
CONFIGURATION-004: config/pricing-service.yaml
...
CONFIGURATION-030: config/ratelimit.yaml
```

### Infrastructure (031-050)
```
CONFIGURATION-031: config/geofence.json
CONFIGURATION-032: config/surge-zones.json
CONFIGURATION-033: config/pricing-tiers.yaml
...
CONFIGURATION-050: config/localization.json
```

### Integration & Operations (051-070)
```
CONFIGURATION-051: config/timezone.yaml
CONFIGURATION-052: config/api-versions.yaml
CONFIGURATION-053: config/webhook-endpoints.yaml
...
CONFIGURATION-070: config/worker-pool.yaml
```

**Links:**
- All configs → `MICROSERVICE-001` (configures)

---

## 🔄 Background Jobs (60)

### Real-time (001-020)
```
BACKGROUND_JOB-001: match_driver_rider
BACKGROUND_JOB-002: send_push_notification
BACKGROUND_JOB-003: send_sms
BACKGROUND_JOB-004: send_email
BACKGROUND_JOB-005: process_payment
...
BACKGROUND_JOB-020: validate_payment_method
```

### Analytics (021-035)
```
BACKGROUND_JOB-021: aggregate_analytics
BACKGROUND_JOB-022: detect_fraud
BACKGROUND_JOB-023: update_ratings
...
BACKGROUND_JOB-035: update_vehicle_maintenance
```

### Maintenance (036-060)
```
BACKGROUND_JOB-036: cleanup_expired_sessions
BACKGROUND_JOB-037: cleanup_old_trips
BACKGROUND_JOB-038: backup_database
...
BACKGROUND_JOB-060: monitor_service_health
```

**Links:**
- All jobs → `PYTHON_FILE-126+` (executed_by workers)

---

## ⏰ Scheduled Tasks (50)

### Hourly (001-012)
```
SCHEDULED_TASK-002: hourly_surge_calculation (0 * * * *)
SCHEDULED_TASK-008: every_5min_driver_location_update (*/5 * * * *)
SCHEDULED_TASK-011: hourly_cache_warmup (15 * * * *)
...
```

### Daily (013-037)
```
SCHEDULED_TASK-001: daily_analytics_aggregation (0 0 * * *)
SCHEDULED_TASK-005: daily_database_backup (0 1 * * *)
SCHEDULED_TASK-007: daily_trip_archival (0 4 * * *)
...
```

### Weekly (038-045)
```
SCHEDULED_TASK-003: weekly_driver_payout (0 2 * * 1)
SCHEDULED_TASK-013: weekly_tax_document_generation (0 7 * * 0)
SCHEDULED_TASK-020: weekly_marketing_campaign (0 13 * * 2)
...
```

### Monthly (046-050)
```
SCHEDULED_TASK-004: monthly_compliance_report (0 3 1 * *)
SCHEDULED_TASK-014: monthly_invoice_generation (0 8 1 * *)
SCHEDULED_TASK-022: monthly_driver_incentive_calculation (0 15 1 * *)
...
```

**Links:**
- All tasks → `BACKGROUND_JOB-001+` (triggers)

---

## 🔗 Link Types Reference

| Link Type | Source → Target | Meaning |
|-----------|----------------|---------|
| `part_of` | Service → Microservice | Service belongs to microservice |
| `implements` | Route/Handler → Endpoint | Code implements API endpoint |
| `maps_to` | Model → Table | Code model maps to database table |
| `reads_from` | Repository → Table | Repository queries table |
| `writes_to` | Repository → Table | Repository modifies table |
| `executes` | Worker → Job | Worker executes background job |
| `triggers` | Task → Job | Scheduled task triggers job |
| `calls` | Hook/Client → Endpoint | Frontend calls backend endpoint |
| `configures` | Config → Microservice | Config applies to microservice |
| `creates` | Migration → Table | Migration creates/modifies table |

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Items | 660 |
| Total Links | ~1,980 |
| Python Files | 150 |
| TypeScript Files | 150 |
| Go Files | 100 |
| Database Migrations | 80 |
| Configurations | 70 |
| Background Jobs | 60 |
| Scheduled Tasks | 50 |

---

## 🔍 Search Examples

### Find all services
```bash
ls python_files/ | grep -E "PYTHON_FILE-0(0[1-9]|[12][0-9]|30)"
```

### Find all components
```bash
ls typescript_files/ | grep -E "TYPESCRIPT_FILE-0([0-4][0-9]|50)"
```

### Find all daily scheduled tasks
```bash
grep -l "0 .* \* \* \*" scheduled_tasks/*.md
```

### Find all table creation migrations
```bash
grep -l "create_.*_table" database_migrations/*.md
```

### Count items by priority
```bash
grep "^priority:" */PYTHON_FILE-*.md | cut -d: -f3 | sort | uniq -c
```

---

## 🚀 Quick Start

### View a Python service
```bash
cat python_files/PYTHON_FILE-001.md
```

### View a TypeScript component
```bash
cat typescript_files/TYPESCRIPT_FILE-001.md
```

### View a Go handler
```bash
cat go_files/GO_FILE-051.md
```

### View a database migration
```bash
cat database_migrations/DATABASE_MIGRATION-001.md
```

### View a scheduled task
```bash
cat scheduled_tasks/SCHEDULED_TASK-001.md
```

---

## 📝 Item Template

Each item follows this structure:

```yaml
---
created: '2026-02-01T03:22:40.102429'
external_id: PYTHON_FILE-001
id: <uuid>
links:
- target: MICROSERVICE-001
  type: part_of
- target: ENDPOINT-004
  type: implements
owner: null
parent: null
priority: high
status: todo
type: python_file
updated: '2026-02-01T03:22:40.102429'
version: 1
---

# <title>

## Description

<description>
```

---

**Last Updated:** 2026-01-31
**Total Items:** 660
**Status:** ✅ Complete
