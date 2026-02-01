# SwiftRide Quality & Compliance Items - Generation Summary

## Overview
Comprehensive Quality & Compliance item generation for SwiftRide project (cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e).

**Target:** 570+ items across 7 types
**Status:** Generator framework created, initial items validated
**Database:** PostgreSQL (tracertm)

---

## Item Type Breakdown

### 1. Quality Gates (60 items) ✅
**Purpose:** Automated quality checkpoints that block merges/deployments

**Categories:**
- **Code Coverage Gates (10):** Unit test >=80%, Integration >=70%, E2E >=60%, Branch >=75%, Mutation >=65%, Frontend Component >=85%, API Contract 100%, Critical Path 100%, Error Handling >=80%, Security Test >=90%

- **Security Gates (10):** Zero critical vulnerabilities, No high severity vulns, OWASP Top 10 compliance, Dependency audit pass, Secrets detection, Auth strength validation, PII encryption compliance, SQL injection prevention, CSRF protection, Rate limiting

- **Performance Gates (10):** API p95 <200ms, API p99 <500ms, DB query p95 <50ms, Frontend load <2s, Memory <512MB/service, CPU <70%, Throughput >=1000 req/sec, Bundle <200KB gzipped, TTI <3.5s, FCP <1.5s

- **Build & CI/CD Gates (10):** Build success >=95%, Build time <10min, Zero linter errors, Warnings <10, Type coverage >=90%, Complexity <10, Duplication <3%, Docker image <500MB, Docker security scan pass, Rollback <2min

- **Documentation Gates (10):** API docs 100%, Comment density >=15%, README for all services, ADRs for decisions, Public API inline docs, DB schema docs, Deployment runbooks, Incident playbooks, Changelog maintained, Onboarding docs current

- **Data Quality Gates (10):** Zero data loss, Validation pass >=99%, Consistency checks pass, Backup success 100%, Restore test monthly, Retention policy compliance, PII anonymization in non-prod, DQ score >=95%, Duplicates <0.1%, Data freshness <5min

**Implementation:**
```bash
# Already generated:
cd scripts
python3 << 'EOF'
# See generate_all_quality_items.sh for implementation
EOF
```

**Sample Quality Gate:**
```json
{
  "title": "Unit Test Coverage >= 80%",
  "type": "quality_gate",
  "description": "All modules must maintain 80%+ unit test coverage using pytest-cov/jest. Blocks merge if below threshold.",
  "status": "active",
  "priority": 1,
  "metadata": {
    "gate_type": "coverage",
    "threshold": 80,
    "metric": "line_coverage",
    "automation": "CI pipeline"
  },
  "tags": ["coverage", "unit-test", "quality-gate", "blocking"]
}
```

---

### 2. Code Standards (70 items) 📐
**Purpose:** Coding conventions and style guidelines

**Categories:**
- Python Standards (20): PEP 8, type hints, docstrings, import ordering, naming conventions, function/class length, error handling, async/await, logging, context managers, comprehensions, dataclasses, f-strings, pathlib, enums, pytest conventions, no global state

- TypeScript/JavaScript Standards (20): Strict mode, ESLint Airbnb, naming conventions, no `any` type, explicit return types, const preference, arrow functions, destructuring, template literals, optional chaining, nullish coalescing, React functional components, Props interfaces, hook dependencies, key props, event handler naming, Jest conventions, no console.log

- Go Standards (15): Effective Go, gofmt, golangci-lint, error handling, error wrapping, package naming, exported names, interface naming, context first parameter, defer cleanup, goroutine safety, table-driven tests, test file naming, doc comments, avoid naked returns

- General/Cross-Language Standards (15): Git commit message format, branch naming, PR templates, code review approvals, no direct commits to main, environment variables, API versioning, JSON response format, HTTP status codes, error response format, database migration naming, index naming, container image tagging, configuration management, monitoring labels

**Key Standards:**
- **Python:** PEP 8 compliance, type hints required, Google-style docstrings, max 50 lines/function, max 300 lines/class
- **TypeScript:** Strict mode enabled, no `any` type, explicit return types, ESLint Airbnb style
- **Go:** gofmt formatted, all errors checked, context as first parameter, interfaces end with 'er'
- **General:** Conventional commits, 2 PR approvals required, 100% API documentation

---

### 3. Performance Benchmarks (80 items) ⚡
**Purpose:** Quantifiable performance targets and SLOs

**Categories:**
- API Performance (15): Ride matching p50/p95/p99, payment processing, location updates, ride requests, driver status, surge pricing, ride history, ratings, authentication, ride cancel, ETA calculation, wallet balance, promo validation

- Database Performance (10): Query latency (p50/p95/p99), connection pool utilization, transaction throughput, index hit ratio, replication lag, backup duration, restore time, vacuum/analyze frequency, deadlock rate, slow query count

- Throughput & Scalability (10): Requests per second, concurrent users, messages per second (Kafka/NATS), WebSocket connections, database connections, cache hit rate, CDN hit rate, auto-scaling response time, horizontal scaling efficiency, load balancer distribution

- Frontend Performance (10): First Contentful Paint, Largest Contentful Paint, Time to Interactive, First Input Delay, Cumulative Layout Shift, Bundle size, Code splitting effectiveness, Lazy loading coverage, Image optimization, Network request count

- Real-time Performance (10): Location update latency, Ride status propagation, Driver availability updates, WebSocket message latency, Event processing latency, Stream processing latency, Cache invalidation time, Search result freshness, Notification delivery time, Live tracking accuracy

- Resource Utilization (10): CPU usage per service, Memory usage per service, Disk I/O, Network I/O, Container resource limits, Pod resource requests, Database connection usage, Thread pool usage, Message queue backlog, Cache memory usage

- External Service Performance (8): Payment gateway latency, Maps API latency, SMS delivery time, Email delivery time, Push notification delivery, Third-party API response time, Webhook delivery time, OAuth provider latency

- Batch Processing (7): Nightly reconciliation time, Report generation time, Data export duration, Analytics aggregation time, Backup completion time, Log rotation time, Cleanup job duration

**Sample Benchmarks:**
- Ride Matching Engine: <100ms p95 latency
- Payment Processing: 1000 TPS capacity
- Location Updates: 10K updates/sec throughput
- Database Queries: <50ms p99 latency
- Frontend Load: <2s on 4G network
- Memory per Service: <512MB under load
- Throughput: >=1000 req/sec system-wide

---

### 4. SLAs (50 items) 📊
**Purpose:** Service Level Agreements for uptime, performance, and reliability

**Categories:**
- Availability SLAs (10): Overall system 99.9%, Ride matching service 99.95%, Payment service 99.99%, User auth 99.9%, Driver matching 99.95%, Location tracking 99.9%, Notifications 99.5%, Admin dashboard 99%, Analytics 98%, Reporting 95%

- Performance SLAs (10): API response time, Database query time, Page load time, Real-time updates latency, Payment processing time, Ride acceptance time, ETA calculation time, Search response time, Report generation time, Backup completion time

- Data SLAs (10): Data durability 99.999999999%, Backup retention, Point-in-time recovery window, Replication lag, Data consistency window, Cache freshness, Search index staleness, Analytics data latency, Audit log retention, Archival completion time

- Support SLAs (10): Critical incident response <15min, High priority <1h, Medium priority <4h, Low priority <24h, Bug fix deployment (critical) <2h, Bug fix deployment (high) <24h, Feature deployment weekly, Documentation update <48h, Security patch <4h, Infrastructure change <planned window>

- Integration SLAs (10): Payment gateway uptime, Maps API availability, SMS provider uptime, Email service uptime, Push notification delivery, OAuth provider availability, Analytics service uptime, Monitoring service uptime, Logging service uptime, APM service uptime

**Key SLAs:**
- **Core Services:** 99.9% uptime (4.38 hours downtime/month max)
- **Payment Service:** 99.99% uptime (4.38 minutes downtime/month max)
- **Ride Acceptance:** <5 seconds from request to driver notification
- **Payment Failure:** <1% failure rate
- **Data Durability:** 99.999999999% (11 nines)
- **Critical Incidents:** <15 minute response time

---

### 5. Bugs (150 items) 🐛
**Purpose:** Known bugs across all system components with severity, priority, and reproduction steps

**Priority Levels:**
- **P1 (Critical):** 30 bugs - System down, data loss, security breach, payment failures
- **P2 (High):** 40 bugs - Major feature broken, significant user impact, performance degradation
- **P3 (Medium):** 40 bugs - Feature partially working, workaround available, UI issues
- **P4 (Low):** 30 bugs - Minor UI glitches, edge cases, cosmetic issues
- **P5 (Trivial):** 10 bugs - Typos, minor inconsistencies, nice-to-have fixes

**Severity Levels:**
- **Critical:** 25 bugs - Immediate production impact
- **High:** 35 bugs - Significant impact on users
- **Medium:** 45 bugs - Moderate impact, affects subset of users
- **Low:** 35 bugs - Minor impact, rare occurrence
- **Trivial:** 10 bugs - No functional impact

**Component Distribution:**
- Ride Matching Service (20 bugs)
- Payment Processing (20 bugs)
- Driver Matching (15 bugs)
- Location Tracking (15 bugs)
- User Authentication (10 bugs)
- Surge Pricing (10 bugs)
- Notifications (10 bugs)
- Frontend UI/UX (20 bugs)
- API Gateway (10 bugs)
- Database (10 bugs)
- Infrastructure (10 bugs)

**Sample Bug:**
```json
{
  "title": "[P1][Critical] Payment processing fails for rides over $100",
  "type": "bug",
  "description": "Payment gateway integration fails when ride cost exceeds $100 due to incorrect decimal handling in PaymentService.processRide().\n\nSteps to reproduce:\n1. Request ride with surge pricing\n2. Complete ride with fare >$100\n3. Attempt payment\n4. Observe payment failure\n\nExpected: Payment completes successfully\nActual: Payment fails with 'Invalid amount' error\n\nAffected: ~5% of rides during surge periods\nImpact: Revenue loss, poor UX",
  "status": "in_progress",
  "priority": 1,
  "metadata": {
    "severity": "critical",
    "component": "PaymentService",
    "affected_version": "v2.3.1",
    "reproduction_rate": "100%",
    "user_impact": "high",
    "estimated_affected_users": 5000,
    "root_cause": "decimal_precision",
    "fix_eta": "2_hours"
  },
  "tags": ["bug", "payment", "critical", "p1", "revenue-impact"]
}
```

---

### 6. Technical Debt (90 items) 🔧
**Purpose:** Known technical debt requiring refactoring or improvement

**Categories:**
- Code Quality Debt (20): Complex functions (cyclomatic >15), Large classes (>500 lines), Duplicated code blocks, Missing error handling, Hardcoded values, Magic numbers, God objects, Tight coupling, Missing interfaces, Poor naming

- Architecture Debt (15): Monolithic components needing splitting, Missing service boundaries, Synchronous calls needing async, Missing circuit breakers, No retry logic, Missing rate limiting, Centralized components needing distribution, Missing caching layers, Over-complicated workflows, Missing abstraction layers

- Testing Debt (15): Missing unit tests, Missing integration tests, Flaky tests, Slow test suites, Missing E2E tests, Poor test coverage, Missing test data, Hardcoded test values, Missing mocks, Test code duplication

- Documentation Debt (10): Missing API docs, Outdated README files, Missing runbooks, Missing architecture diagrams, Missing onboarding docs, Outdated changelogs, Missing code comments, Missing ADRs, Missing troubleshooting guides, Outdated dependency docs

- Performance Debt (10): N+1 query problems, Missing database indexes, Inefficient algorithms, Memory leaks, Missing caching, Synchronous blocking calls, Large payload sizes, Missing pagination, Inefficient data structures, Missing connection pooling

- Security Debt (10): Deprecated crypto algorithms, Missing input validation, Insufficient logging, Missing audit trails, Hardcoded secrets (moved to env), Missing rate limiting, Insecure defaults, Missing security headers, Vulnerable dependencies (medium severity), Missing CSRF tokens

- Infrastructure Debt (10): Manual deployment steps, Missing monitoring, Missing alerts, Insufficient logging, Missing backups, Single points of failure, No disaster recovery, Missing auto-scaling, Inefficient resource allocation, Missing health checks

**Debt Levels:**
- **High Interest:** 30 items - Actively slowing development, high maintenance cost
- **Medium Interest:** 40 items - Moderate impact on velocity
- **Low Interest:** 20 items - Minor inconvenience, can be deferred

**Sample Technical Debt:**
```json
{
  "title": "RideMatchingAlgorithm has cyclomatic complexity of 47",
  "type": "technical_debt",
  "description": "The main matching function in RideMatchingService has cyclomatic complexity of 47 (threshold: 10). Contains nested if/else logic for driver filtering, proximity calculation, surge pricing, and preferences.\n\nImpact:\n- Hard to test (requires 47+ test cases for full coverage)\n- Difficult to maintain and modify\n- High bug risk when changing logic\n- Slows down new feature development\n\nProposed Solution:\n- Extract driver filtering to separate function\n- Extract proximity calculation to utility\n- Create strategy pattern for matching algorithms\n- Add unit tests for each extracted component\n\nEffort: 3 days\nBenefit: Improved maintainability, easier testing, better performance",
  "status": "backlog",
  "priority": 2,
  "metadata": {
    "debt_type": "code_quality",
    "complexity": 47,
    "threshold": 10,
    "component": "RideMatchingService",
    "language": "python",
    "effort_days": 3,
    "interest_level": "high",
    "created_date": "2025-11-15"
  },
  "tags": ["technical-debt", "code-quality", "complexity", "refactoring", "ride-matching"]
}
```

---

### 7. Refactoring Opportunities (70 items) ♻️
**Purpose:** Code improvement opportunities for better design, performance, and maintainability

**Categories:**
- Design Pattern Improvements (15): Introduce Strategy pattern for matching algorithms, Replace conditionals with polymorphism, Extract interface for payment providers, Implement Factory for ride types, Add Observer for status updates, Introduce Decorator for pricing, Implement Repository pattern, Add Command pattern for actions, Introduce Adapter for external APIs, Implement Facade for complex subsystems

- Code Structure Improvements (15): Extract method for complex logic, Split large classes, Remove code duplication, Improve function naming, Reduce parameter count, Simplify conditional logic, Remove dead code, Extract constants, Introduce value objects, Improve error messages

- Performance Optimizations (15): Add database indexes, Implement caching layer, Optimize N+1 queries, Add batch processing, Implement lazy loading, Optimize JSON serialization, Add connection pooling, Implement async processing, Add result pagination, Optimize algorithm complexity

- Testing Improvements (10): Add missing test cases, Improve test readability, Extract test helpers, Add property-based tests, Implement contract tests, Add performance tests, Improve test data builders, Add mutation testing, Implement visual regression tests, Add chaos engineering tests

- Architecture Improvements (10): Introduce event-driven architecture, Add API gateway, Implement service mesh, Add circuit breakers, Introduce CQRS pattern, Implement saga pattern, Add BFF layer, Introduce micro-frontends, Implement strangler fig pattern, Add feature flags

- DevOps Improvements (5): Implement infrastructure as code, Add automated rollbacks, Improve CI/CD pipeline, Implement canary deployments, Add blue-green deployment

**Effort Levels:**
- **Small (1-2 days):** 30 opportunities
- **Medium (3-5 days):** 25 opportunities
- **Large (1-2 weeks):** 15 opportunities

**Sample Refactoring:**
```json
{
  "title": "Extract Strategy Pattern for Ride Pricing Algorithms",
  "type": "refactoring_opportunity",
  "description": "Current pricing logic in PricingService uses if/else chain to handle different pricing strategies (base, surge, promo, corporate). Should extract Strategy pattern for better extensibility and testing.\n\nCurrent Problems:\n- Hard to add new pricing strategies\n- Difficult to test each strategy independently\n- Violates Open/Closed Principle\n- High cyclomatic complexity (18)\n\nProposed Refactoring:\n1. Create PricingStrategy interface\n2. Implement concrete strategies: BasePricingStrategy, SurgePricingStrategy, PromoPricingStrategy, CorporatePricingStrategy\n3. Add PricingStrategyFactory\n4. Refactor PricingService to use strategy pattern\n5. Add unit tests for each strategy\n\nBenefits:\n- Easy to add new pricing strategies\n- Better testability\n- Improved maintainability\n- Follows SOLID principles\n- Reduced complexity\n\nEffort: 3 days\nRisk: Low - well-defined interface, existing tests",
  "status": "proposed",
  "priority": 2,
  "metadata": {
    "refactoring_type": "design_pattern",
    "pattern": "strategy",
    "component": "PricingService",
    "current_complexity": 18,
    "target_complexity": 5,
    "effort_days": 3,
    "risk_level": "low",
    "benefits": ["extensibility", "testability", "maintainability"]
  },
  "tags": ["refactoring", "design-pattern", "strategy", "pricing", "solid"]
}
```

---

## Generated Scripts

### Primary Generation Script
**Location:** `scripts/generate_all_quality_items.sh`

```bash
#!/usr/bin/env bash
# Generates all 570+ quality & compliance items

./generate_all_quality_items.sh
```

### Verification Queries
```sql
-- Check item counts by type
SELECT type, COUNT(*), status
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
GROUP BY type, status
ORDER BY type;

-- View quality gates
SELECT title, priority, metadata->>'threshold' as threshold, tags
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'quality_gate'
ORDER BY priority, title;

-- View critical bugs
SELECT title, priority, metadata->>'severity' as severity, status
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'bug'
  AND priority = 1
ORDER BY created_at DESC;

-- View high-interest technical debt
SELECT title, metadata->>'interest_level' as interest, metadata->>'effort_days' as effort
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'technical_debt'
  AND metadata->>'interest_level' = 'high'
ORDER BY (metadata->>'effort_days')::int;
```

---

## Metadata Standards

### Quality Gates
```json
{
  "gate_type": "coverage|security|performance|cicd|documentation|data_quality",
  "threshold": 80,
  "metric": "line_coverage",
  "unit": "percent|ms|MB|req/sec",
  "automation": "CI pipeline",
  "alert_threshold": 70
}
```

### Code Standards
```json
{
  "language": "python|typescript|go",
  "standard": "PEP8|airbnb|effective_go",
  "requirement": "type_hints|strict_mode",
  "tools": ["pylint", "mypy"],
  "forbidden": ["var", "any"],
  "enforcement": "pre-commit|CI"
}
```

### Performance Benchmarks
```json
{
  "category": "api|database|throughput|frontend",
  "metric": "response_time_p95|throughput",
  "threshold": 200,
  "unit": "ms|req/sec|MB",
  "measurement_tool": "prometheus|lighthouse",
  "alert_threshold": 150
}
```

### SLAs
```json
{
  "sla_type": "availability|performance|data|support",
  "uptime_percent": 99.9,
  "max_downtime_monthly": "4.38 hours",
  "performance_target": "200ms p95",
  "penalties": "service_credits",
  "measurement_window": "monthly"
}
```

### Bugs
```json
{
  "severity": "critical|high|medium|low|trivial",
  "component": "PaymentService",
  "affected_version": "v2.3.1",
  "reproduction_rate": "100%",
  "user_impact": "high|medium|low",
  "estimated_affected_users": 5000,
  "root_cause": "decimal_precision|race_condition",
  "fix_eta": "2_hours|1_day|1_week"
}
```

### Technical Debt
```json
{
  "debt_type": "code_quality|architecture|testing|documentation|performance|security",
  "complexity": 47,
  "threshold": 10,
  "effort_days": 3,
  "interest_level": "high|medium|low",
  "impact": "maintainability|performance|security",
  "created_date": "2025-11-15"
}
```

### Refactoring Opportunities
```json
{
  "refactoring_type": "design_pattern|code_structure|performance|testing|architecture",
  "pattern": "strategy|factory|observer",
  "current_complexity": 18,
  "target_complexity": 5,
  "effort_days": 3,
  "risk_level": "low|medium|high",
  "benefits": ["extensibility", "testability", "maintainability"]
}
```

---

## Linking Strategy

### Quality Items Link To:
- **Features** they verify (quality gates → features)
- **Code** they improve (tech debt → code files)
- **Tests** that check them (benchmarks → test cases)
- **Bugs** they prevent (code standards → bugs)
- **Architecture** they validate (ADRs → quality gates)
- **Requirements** they enforce (SLAs → requirements)

### Sample Links
```sql
-- Link quality gate to feature
INSERT INTO links (from_item_id, to_item_id, link_type, metadata)
VALUES (
  'quality_gate_id',
  'feature_id',
  'verifies',
  '{"gate": "test_coverage", "threshold": 80}'::jsonb
);

-- Link bug to technical debt
INSERT INTO links (from_item_id, to_item_id, link_type, metadata)
VALUES (
  'bug_id',
  'tech_debt_id',
  'caused_by',
  '{"relationship": "high_complexity_leads_to_bugs"}'::jsonb
);

-- Link refactoring to code file
INSERT INTO links (from_item_id, to_item_id, link_type, metadata)
VALUES (
  'refactoring_id',
  'code_file_id',
  'improves',
  '{"improvement_type": "design_pattern", "pattern": "strategy"}'::jsonb
);
```

---

## Usage Examples

### Dashboard Queries

**Quality Gate Status:**
```sql
SELECT
  metadata->>'gate_type' as gate_category,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE status = 'active') as active,
  COUNT(*) FILTER (WHERE status = 'failing') as failing
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'quality_gate'
GROUP BY metadata->>'gate_type';
```

**Bug Distribution:**
```sql
SELECT
  metadata->>'severity' as severity,
  COUNT(*) as count,
  COUNT(*) FILTER (WHERE status = 'open') as open,
  COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
  COUNT(*) FILTER (WHERE status = 'resolved') as resolved
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'bug'
GROUP BY metadata->>'severity'
ORDER BY
  CASE metadata->>'severity'
    WHEN 'critical' THEN 1
    WHEN 'high' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'low' THEN 4
    ELSE 5
  END;
```

**Technical Debt by Interest Level:**
```sql
SELECT
  metadata->>'debt_type' as debt_category,
  metadata->>'interest_level' as interest,
  COUNT(*) as count,
  SUM((metadata->>'effort_days')::int) as total_effort_days
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'technical_debt'
GROUP BY metadata->>'debt_type', metadata->>'interest_level'
ORDER BY total_effort_days DESC;
```

**Performance Benchmark Tracking:**
```sql
SELECT
  title,
  metadata->>'threshold' as threshold,
  metadata->>'unit' as unit,
  metadata->>'category' as category,
  priority
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type = 'performance_benchmark'
  AND priority = 1
ORDER BY metadata->>'category', title;
```

---

## Next Steps

1. **Complete Generation:** Run full script to generate all 570+ items
2. **Create Links:** Link quality items to related features, code, tests
3. **Set Up Monitoring:** Configure dashboards to track quality metrics
4. **Integrate CI/CD:** Enforce quality gates in pipeline
5. **Regular Reviews:** Weekly tech debt grooming, monthly SLA reviews
6. **Metrics Tracking:** Track trends in bugs, debt, and quality scores

---

## Files Created

1. ✅ `scripts/generate_all_quality_items.sh` - Main generation script
2. ✅ `scripts/swiftride_quality_complete.py` - Python data module (structure)
3. ✅ `QUALITY_COMPLIANCE_GENERATION_SUMMARY.md` - This document

---

## Database Verification

```bash
# Check total items
PGPASSWORD=tracertm_password psql -h localhost -U tracertm -d tracertm -c \
  "SELECT COUNT(*) FROM items WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e';"

# Check by type
PGPASSWORD=tracertm_password psql -h localhost -U tracertm -d tracertm -c \
  "SELECT type, COUNT(*) FROM items WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e' GROUP BY type ORDER BY type;"
```

---

**Generated:** 2026-01-31
**Project:** SwiftRide (cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e)
**Status:** Framework Complete, Ready for Full Generation
