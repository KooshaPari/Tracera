# Extended Views & Link Types - Comprehensive Research

## Additional View Types

### 1. Architecture View (C4 Model)
**Purpose**: Visualize system architecture at multiple levels

**Decomposition**:
```
System Context (Level 1)
  ├─ Container (Level 2)
  │   ├─ Component (Level 3)
  │   │   └─ Code (Level 4)
  │   └─ Component
  └─ Container
```

**Items**:
- **System**: External system or user
- **Container**: Application, database, file system
- **Component**: Module, service, library
- **Code**: Class, interface, function

**Links**:
- `uses` → System uses another system
- `contains` → Container contains components
- `depends_on` → Component depends on another
- `communicates_with` → Async communication

**Example**:
```
System: E-commerce Platform
  ├─ Container: Web Application (React)
  │   ├─ Component: Product Catalog
  │   ├─ Component: Shopping Cart
  │   └─ Component: Checkout
  ├─ Container: API Gateway (Node.js)
  ├─ Container: Auth Service (Go)
  └─ Container: Database (PostgreSQL)
```

### 2. Infrastructure View
**Purpose**: Track deployment infrastructure and configuration

**Decomposition**:
```
Cloud Provider
  ├─ Region
  │   ├─ Environment (dev/staging/prod)
  │   │   ├─ Cluster/VPC
  │   │   │   ├─ Service/Instance
  │   │   │   │   └─ Container/Process
  │   │   │   └─ Service
  │   │   └─ Database
  │   └─ Environment
  └─ Region
```

**Items**:
- **Cloud Provider**: AWS, Azure, GCP, On-prem
- **Region**: us-east-1, eu-west-1
- **Environment**: dev, staging, production
- **Cluster**: Kubernetes cluster, EC2 group
- **Service**: Deployment, StatefulSet, Lambda
- **Container**: Docker container, VM

**Links**:
- `deployed_to` → Code deployed to infrastructure
- `runs_on` → Service runs on cluster
- `connects_to` → Service connects to database
- `scales_with` → Auto-scaling relationship
- `backed_by` → Service backed by infrastructure

**Example**:
```
AWS
  ├─ us-east-1
  │   ├─ Production
  │   │   ├─ EKS Cluster
  │   │   │   ├─ API Service (3 replicas)
  │   │   │   ├─ Worker Service (5 replicas)
  │   │   │   └─ Cache (Redis)
  │   │   └─ RDS PostgreSQL
  │   └─ Staging
  │       └─ EKS Cluster
  └─ eu-west-1
      └─ Production (DR)
```

### 3. Data Flow View
**Purpose**: Track data movement through the system

**Decomposition**:
```
Data Source
  ├─ Data Pipeline
  │   ├─ Transformation
  │   │   └─ Step
  │   └─ Transformation
  └─ Data Sink
```

**Items**:
- **Data Source**: Database, API, File, Stream
- **Data Pipeline**: ETL job, Stream processor
- **Transformation**: Map, Filter, Aggregate
- **Data Sink**: Database, Cache, File, Queue

**Links**:
- `reads_from` → Pipeline reads from source
- `writes_to` → Pipeline writes to sink
- `transforms` → Transformation applied
- `depends_on_data` → Data dependency
- `triggers` → Data event triggers process

**Example**:
```
User Events (Kafka)
  ├─ Analytics Pipeline
  │   ├─ Filter invalid events
  │   ├─ Enrich with user data
  │   └─ Aggregate by session
  └─ Data Warehouse (Snowflake)
      └─ Analytics Dashboard
```

### 4. Security View
**Purpose**: Track security requirements and vulnerabilities

**Decomposition**:
```
Security Domain
  ├─ Security Requirement
  │   ├─ Control
  │   │   ├─ Implementation
  │   │   └─ Test
  │   └─ Control
  └─ Vulnerability
      └─ Remediation
```

**Items**:
- **Security Domain**: Authentication, Authorization, Encryption
- **Security Requirement**: OWASP requirement, compliance rule
- **Control**: Security control implementation
- **Vulnerability**: CVE, security issue
- **Remediation**: Fix, mitigation

**Links**:
- `requires_security` → Feature requires security control
- `implements_control` → Code implements control
- `tests_security` → Test validates security
- `mitigates` → Control mitigates vulnerability
- `exposes` → Code exposes vulnerability

**Example**:
```
Authentication Domain
  ├─ REQ-SEC-001: Multi-factor authentication
  │   ├─ CTRL-001: TOTP implementation
  │   │   ├─ auth/mfa.py
  │   │   └─ test_mfa.py
  │   └─ CTRL-002: Backup codes
  └─ CVE-2024-1234: Session fixation
      └─ FIX-001: Regenerate session on login
```

### 5. Performance View
**Purpose**: Track performance requirements and bottlenecks

**Decomposition**:
```
Performance Domain
  ├─ Performance Requirement
  │   ├─ Metric
  │   │   ├─ Measurement
  │   │   └─ Threshold
  │   └─ Bottleneck
  │       └─ Optimization
  └─ Load Test
```

**Items**:
- **Performance Domain**: Latency, Throughput, Resource Usage
- **Performance Requirement**: SLA, SLO, SLI
- **Metric**: Response time, QPS, CPU usage
- **Bottleneck**: Slow query, memory leak
- **Optimization**: Cache, index, algorithm change

**Links**:
- `has_performance_req` → Feature has performance requirement
- `measures` → Metric measures performance
- `identifies_bottleneck` → Profiling identifies bottleneck
- `optimizes` → Optimization improves performance
- `validates_performance` → Load test validates

**Example**:
```
API Latency Domain
  ├─ REQ-PERF-001: API response < 200ms (p95)
  │   ├─ METRIC-001: /api/users response time
  │   │   ├─ Current: 450ms (p95) ❌
  │   │   └─ Target: 200ms (p95)
  │   └─ BOTTLENECK-001: N+1 query in user endpoint
  │       └─ OPT-001: Add eager loading
  └─ LOAD-TEST-001: 1000 RPS load test
```

### 6. Monitoring/Observability View
**Purpose**: Track monitoring, metrics, logs, and traces

**Decomposition**:
```
Observability Domain
  ├─ Metric
  │   ├─ Dashboard
  │   └─ Alert
  ├─ Log
  │   └─ Log Query
  └─ Trace
      └─ Span
```

**Items**:
- **Metric**: Counter, Gauge, Histogram
- **Dashboard**: Grafana dashboard, Datadog board
- **Alert**: Threshold alert, anomaly detection
- **Log**: Application log, system log
- **Trace**: Distributed trace
- **Span**: Trace span

**Links**:
- `emits_metric` → Service emits metric
- `logs_to` → Service logs to destination
- `traces` → Service participates in trace
- `monitors` → Dashboard monitors service
- `alerts_on` → Alert triggers on condition

**Example**:
```
API Service Observability
  ├─ METRIC-001: api_requests_total (counter)
  │   ├─ Dashboard: API Overview
  │   └─ Alert: High error rate (> 5%)
  ├─ LOG-001: Application logs
  │   └─ Query: ERROR level logs
  └─ TRACE-001: /api/users request trace
      ├─ Span: API Gateway
      ├─ Span: Auth Service
      └─ Span: Database Query
```

### 7. Domain Model View (DDD)
**Purpose**: Track business domain model and bounded contexts

**Decomposition**:
```
Bounded Context
  ├─ Aggregate
  │   ├─ Entity
  │   │   └─ Value Object
  │   └─ Entity
  ├─ Domain Event
  └─ Domain Service
```

**Items**:
- **Bounded Context**: Logical boundary of domain
- **Aggregate**: Consistency boundary
- **Entity**: Domain object with identity
- **Value Object**: Immutable domain object
- **Domain Event**: Something that happened
- **Domain Service**: Stateless domain logic

**Links**:
- `belongs_to_context` → Entity belongs to bounded context
- `aggregates` → Aggregate contains entities
- `emits_event` → Aggregate emits domain event
- `handles_event` → Service handles event
- `collaborates_with` → Context collaborates with another

**Example**:
```
Order Management Context
  ├─ Order Aggregate
  │   ├─ Order (Entity)
  │   ├─ OrderLine (Entity)
  │   └─ Money (Value Object)
  ├─ OrderPlaced (Domain Event)
  └─ OrderService (Domain Service)

Payment Context
  ├─ Payment Aggregate
  └─ PaymentProcessed (Domain Event)
      → triggers → OrderFulfillment
```

### 8. User Journey View
**Purpose**: Track user flows and customer journeys

**Decomposition**:
```
User Persona
  ├─ Journey
  │   ├─ Stage
  │   │   ├─ Touchpoint
  │   │   │   ├─ Screen
  │   │   │   └─ Action
  │   │   └─ Touchpoint
  │   └─ Stage
  └─ Pain Point
```

**Items**:
- **User Persona**: Target user type
- **Journey**: End-to-end user journey
- **Stage**: Phase of journey (awareness, consideration, purchase)
- **Touchpoint**: Interaction point
- **Screen**: UI screen
- **Action**: User action
- **Pain Point**: User frustration

**Links**:
- `experiences_journey` → Persona experiences journey
- `includes_stage` → Journey includes stage
- `interacts_at` → User interacts at touchpoint
- `navigates_to` → Screen navigates to another
- `addresses_pain_point` → Feature addresses pain point

**Example**:
```
Persona: New User
  └─ Journey: First Purchase
      ├─ Stage: Discovery
      │   ├─ Touchpoint: Landing page
      │   └─ Touchpoint: Product search
      ├─ Stage: Evaluation
      │   ├─ Touchpoint: Product detail page
      │   └─ Touchpoint: Reviews
      └─ Stage: Purchase
          ├─ Touchpoint: Add to cart
          ├─ Touchpoint: Checkout
          └─ Touchpoint: Payment
```

### 9. Configuration View
**Purpose**: Track configuration across environments

**Decomposition**:
```
Configuration Domain
  ├─ Environment
  │   ├─ Config Group
  │   │   ├─ Config Item
  │   │   │   └─ Value
  │   │   └─ Config Item
  │   └─ Secret
  └─ Feature Flag
```

**Items**:
- **Environment**: dev, staging, production
- **Config Group**: Database, API, Feature flags
- **Config Item**: Individual configuration
- **Value**: Configuration value
- **Secret**: Sensitive configuration
- **Feature Flag**: Toggle feature on/off

**Links**:
- `configured_in` → Service configured in environment
- `uses_config` → Service uses configuration
- `overrides` → Environment overrides config
- `depends_on_flag` → Feature depends on flag
- `stores_secret` → Service stores secret

**Example**:
```
Production Environment
  ├─ Database Config
  │   ├─ host: prod-db.example.com
  │   ├─ port: 5432
  │   └─ pool_size: 20
  ├─ API Config
  │   └─ rate_limit: 1000/min
  └─ Feature Flags
      ├─ new_checkout: enabled
      └─ beta_dashboard: disabled
```

### 10. Dependency View
**Purpose**: Track all types of dependencies

**Decomposition**:
```
Dependency Domain
  ├─ Package Dependency
  │   └─ Version
  ├─ Service Dependency
  │   └─ API Contract
  └─ Data Dependency
      └─ Schema
```

**Items**:
- **Package Dependency**: npm, pip, cargo package
- **Version**: Semantic version
- **Service Dependency**: External service
- **API Contract**: API specification
- **Data Dependency**: Database, file, stream

**Links**:
- `depends_on_package` → Code depends on package
- `depends_on_service` → Service depends on another
- `depends_on_data` → Service depends on data
- `breaks_on_change` → Breaking change impact
- `compatible_with` → Version compatibility

**Example**:
```
API Service Dependencies
  ├─ Package Dependencies
  │   ├─ express@4.18.2
  │   ├─ pg@8.11.0
  │   └─ redis@4.6.5
  ├─ Service Dependencies
  │   ├─ Auth Service (v2 API)
  │   └─ Payment Service (v1 API)
  └─ Data Dependencies
      ├─ PostgreSQL (users table)
      └─ Redis (session cache)
```

## Extended Link Types

### Hierarchical Links
- `decomposes_to` → Parent breaks down into children
- `part_of` → Child is part of parent
- `contains` → Container contains items
- `belongs_to` → Item belongs to container
- `groups` → Logical grouping

### Dependency Links
- `depends_on` → Hard dependency
- `requires` → Prerequisite
- `blocks` → Blocking relationship
- `enables` → Enabling relationship
- `optional_dependency` → Soft dependency

### Implementation Links
- `implements` → Code implements specification
- `realizes` → Concrete realization of abstract
- `satisfies` → Satisfies requirement
- `fulfills` → Fulfills contract
- `provides` → Provides capability

### Testing Links
- `tests` → Test validates item
- `validates` → Validation relationship
- `verifies` → Verification relationship
- `covers` → Coverage relationship
- `exercises` → Test exercises code path

### Temporal Links
- `replaces` → New version replaces old
- `supersedes` → Evolution/improvement
- `derived_from` → Derived from original
- `spawned_from` → Created from parent
- `evolved_into` → Evolution path

### Conflict Links
- `conflicts_with` → Mutually exclusive
- `duplicates` → Potential duplicate
- `overlaps` → Partial overlap
- `contradicts` → Logical contradiction
- `competes_with` → Resource competition

### Communication Links
- `calls` → Synchronous call
- `publishes_to` → Async publish
- `subscribes_to` → Async subscribe
- `sends_to` → Message sending
- `receives_from` → Message receiving

### Data Links
- `reads_from` → Data read
- `writes_to` → Data write
- `transforms` → Data transformation
- `aggregates` → Data aggregation
- `filters` → Data filtering

### Deployment Links
- `deployed_to` → Deployment target
- `runs_on` → Runtime environment
- `hosted_by` → Hosting relationship
- `backed_by` → Infrastructure backing
- `scales_with` → Scaling relationship

### Security Links
- `authenticates_with` → Authentication
- `authorizes` → Authorization
- `encrypts` → Encryption
- `protects` → Protection relationship
- `exposes` → Security exposure
- `mitigates` → Risk mitigation

### Performance Links
- `optimizes` → Performance optimization
- `caches` → Caching relationship
- `indexes` → Database indexing
- `profiles` → Performance profiling
- `bottleneck_in` → Performance bottleneck

### Monitoring Links
- `monitors` → Monitoring relationship
- `alerts_on` → Alert trigger
- `logs_to` → Logging destination
- `traces` → Distributed tracing
- `emits_metric` → Metric emission

### Business Links
- `addresses_pain_point` → Solves user problem
- `enables_journey` → Enables user journey
- `supports_persona` → Supports user type
- `generates_revenue` → Revenue impact
- `reduces_cost` → Cost impact

## Complete View Matrix

| View | Primary Focus | Key Items | Common Links |
|------|---------------|-----------|--------------|
| **Feature** | Product capabilities | Epic, Story, Task | decomposes_to, implements, tests |
| **Code** | Implementation | File, Class, Function | implements, calls, depends_on |
| **Wireframe** | UI design | Screen, Component, Button | implements, navigates_to, contains |
| **API** | Service interfaces | Endpoint, Parameter | implements, calls, depends_on |
| **Test** | Validation | Suite, Case, Assertion | tests, validates, covers |
| **Database** | Data model | Table, Column, Index | reads_from, writes_to, indexes |
| **Architecture** | System structure | Container, Component | contains, depends_on, communicates_with |
| **Infrastructure** | Deployment | Cluster, Service, Container | deployed_to, runs_on, scales_with |
| **Data Flow** | Data movement | Pipeline, Transformation | reads_from, writes_to, transforms |
| **Security** | Security controls | Requirement, Control, Vulnerability | requires_security, implements_control, mitigates |
| **Performance** | Performance | Requirement, Metric, Bottleneck | has_performance_req, optimizes, measures |
| **Monitoring** | Observability | Metric, Log, Trace | monitors, emits_metric, traces |
| **Domain Model** | Business logic | Aggregate, Entity, Event | belongs_to_context, emits_event, handles_event |
| **User Journey** | User experience | Journey, Stage, Touchpoint | experiences_journey, interacts_at, addresses_pain_point |
| **Configuration** | Settings | Environment, Config, Flag | configured_in, uses_config, depends_on_flag |
| **Dependency** | Dependencies | Package, Service, Data | depends_on_package, depends_on_service, depends_on_data |

## Cross-View Navigation Examples

### Example 1: Feature → All Views
```
User Story: "User can login"
  ├─ Wireframe View
  │   └─ Login Screen → Login Form → Submit Button
  ├─ Code View
  │   ├─ LoginController.login()
  │   └─ AuthService.authenticate()
  ├─ API View
  │   └─ POST /api/auth/login
  ├─ Test View
  │   ├─ test_login_success
  │   └─ test_login_invalid_credentials
  ├─ Database View
  │   └─ users table (email, password_hash)
  ├─ Security View
  │   ├─ Password hashing (bcrypt)
  │   └─ Rate limiting
  ├─ Performance View
  │   └─ Login latency < 500ms
  ├─ Monitoring View
  │   ├─ login_attempts_total (metric)
  │   └─ login_errors (alert)
  └─ User Journey View
      └─ First-time user → Login → Dashboard
```

### Example 2: Code → All Views
```
File: auth/login.py
  ├─ Feature View
  │   ├─ STORY-101: User can login
  │   └─ STORY-102: Password reset
  ├─ API View
  │   └─ POST /api/auth/login (implements)
  ├─ Test View
  │   └─ tests/test_login.py (tested by)
  ├─ Database View
  │   ├─ users table (reads from)
  │   └─ sessions table (writes to)
  ├─ Architecture View
  │   └─ Auth Service → API Gateway
  ├─ Infrastructure View
  │   └─ Deployed to: prod-cluster/auth-service
  ├─ Security View
  │   ├─ Implements: Password hashing
  │   └─ Mitigates: CVE-2024-1234
  ├─ Performance View
  │   └─ Bottleneck: N+1 query (line 45)
  ├─ Monitoring View
  │   ├─ Emits: auth_login_duration
  │   └─ Logs to: CloudWatch
  └─ Dependency View
      ├─ bcrypt (package)
      └─ redis (service)
```

### Example 3: Infrastructure → All Views
```
Kubernetes Cluster: prod-us-east-1
  ├─ Feature View
  │   └─ All production features
  ├─ Code View
  │   └─ All services deployed here
  ├─ API View
  │   └─ All production APIs
  ├─ Database View
  │   └─ RDS PostgreSQL (connects to)
  ├─ Architecture View
  │   └─ Production Container (runs)
  ├─ Configuration View
  │   └─ Production config
  ├─ Security View
  │   ├─ Network policies
  │   └─ Pod security policies
  ├─ Performance View
  │   ├─ CPU/Memory limits
  │   └─ Auto-scaling rules
  ├─ Monitoring View
  │   ├─ Cluster metrics
  │   └─ Pod health checks
  └─ Dependency View
      └─ AWS EKS (runs on)
```

## CLI Commands for Extended Views

```bash
# Switch to extended views
rtm view architecture         # C4 architecture view
rtm view infrastructure       # Infrastructure/deployment view
rtm view dataflow            # Data flow view
rtm view security            # Security view
rtm view performance         # Performance view
rtm view monitoring          # Observability view
rtm view domain              # Domain model (DDD) view
rtm view journey             # User journey view
rtm view config              # Configuration view
rtm view dependency          # Dependency view

# Show with specific link types
rtm links STORY-101 --type implements
rtm links STORY-101 --type tests
rtm links STORY-101 --type depends_on

# Cross-view queries
rtm query "view:feature has:security missing:test"
rtm query "view:code has:bottleneck priority:>80"
rtm query "view:infrastructure environment:production"
rtm query "view:security status:vulnerable"
```

## Summary

**Total Views**: 16 comprehensive views
- Original: 6 (Feature, Code, Wireframe, API, Test, Database)
- Extended: 10 (Architecture, Infrastructure, Data Flow, Security, Performance, Monitoring, Domain Model, User Journey, Configuration, Dependency)

**Total Link Types**: 60+ link types across 12 categories
- Hierarchical, Dependency, Implementation, Testing
- Temporal, Conflict, Communication, Data
- Deployment, Security, Performance, Monitoring
- Business

**Key Benefits**:
- Complete project visibility from any angle
- Seamless navigation between all views
- Rich relationship modeling
- Comprehensive traceability

