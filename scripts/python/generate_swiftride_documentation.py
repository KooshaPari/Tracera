#!/usr/bin/env python3
"""Generate comprehensive Documentation Layer for SwiftRide.

Target: 50+ items per type with deep linking to existing items.

Documentation Types:
1. architecture_decision (60 items) - ADRs with full context
2. technical_spec (80 items) - Detailed technical specifications
3. api_documentation (100 items) - OpenAPI specs, examples
4. user_guide (70 items) - End-user documentation
5. tutorial (60 items) - How-to guides, walkthroughs
6. troubleshooting_guide (70 items) - Common issues and solutions
7. release_note (80 items) - Version release notes
8. architecture_diagram (50 items) - System, sequence, deployment diagrams
"""

import asyncio
import json
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from typing import Any

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Database setup - use simple asyncpg URL without SSL params
DATABASE_URL = "postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm"
PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

# Storage for created items
items_db: dict[str, list[str]] = {
    "architecture_decision": [],
    "technical_spec": [],
    "api_documentation": [],
    "user_guide": [],
    "tutorial": [],
    "troubleshooting_guide": [],
    "release_note": [],
    "architecture_diagram": [],
}

# Storage for existing items to link to
existing_items: dict[str, list[str]] = {}


# ============================================================================
# 1. ARCHITECTURE DECISIONS (60 ADRs)
# ============================================================================

ARCHITECTURE_DECISIONS = [
    {
        "number": "ADR-001",
        "title": "Use PostgreSQL for Transactional Data",
        "status": "accepted",
        "context": "Need reliable ACID-compliant database for critical ride transactions, payments, and user data. Must support complex queries, relationships, and high concurrency.",
        "decision": "Adopt PostgreSQL 14+ as primary transactional database with read replicas for scalability. Use connection pooling (PgBouncer) and implement table partitioning for high-volume tables.",
        "consequences": "Strong consistency guarantees, mature ecosystem, excellent JSON support. Trade-off: vertical scaling limits require sharding strategy for future growth beyond 10M rides/day.",
        "tags": ["database", "infrastructure", "persistence"],
    },
    {
        "number": "ADR-002",
        "title": "Implement Event Sourcing for Trip State",
        "status": "accepted",
        "context": "Need complete audit trail of ride lifecycle for regulatory compliance, dispute resolution, and analytics. Traditional CRUD loses state transition history.",
        "decision": "Use event sourcing pattern for Trip aggregate. Store all state transitions as immutable events in event_store table. Rebuild current state via event replay. Snapshot every 50 events for performance.",
        "consequences": "Complete auditability, temporal queries, easy bug reproduction. Trade-off: increased storage (50GB/month), complex migration path, eventual consistency challenges.",
        "tags": ["architecture", "event-sourcing", "compliance"],
    },
    {
        "number": "ADR-003",
        "title": "Choose Go for Matching Service",
        "status": "accepted",
        "context": "Matching service is latency-critical (<100ms p99). Must handle 50k concurrent connections, minimal memory footprint, excellent concurrency primitives required.",
        "decision": "Implement matching engine in Go with goroutines for concurrent request handling. Use spatial indexes (PostGIS), in-memory caching (Redis), and gRPC for inter-service communication.",
        "consequences": "Exceptional performance (15ms p50, 80ms p99), low memory usage (512MB per instance). Trade-off: smaller talent pool, learning curve for team, fewer libraries vs Python/Node.",
        "tags": ["performance", "microservices", "golang"],
    },
    {
        "number": "ADR-004",
        "title": "Adopt Microservices Architecture",
        "status": "accepted",
        "context": "Monolithic architecture limits team velocity, deployment independence, and technology choices. Need ability to scale components independently.",
        "decision": "Decompose into domain-aligned microservices: rider, driver, matching, payment, notification, analytics. Use API Gateway (Kong), service mesh (Istio), and event bus (NATS).",
        "consequences": "Team autonomy, independent scaling, polyglot. Trade-off: operational complexity, distributed transactions, network latency, observability challenges.",
        "tags": ["architecture", "microservices", "scalability"],
    },
    {
        "number": "ADR-005",
        "title": "Use Redis for Real-time Location Tracking",
        "status": "accepted",
        "context": "Need to track 100k+ active drivers with sub-second location updates. Must support geospatial queries (find drivers within 5km) with <50ms latency.",
        "decision": "Use Redis geospatial indexes (GEOADD/GEORADIUS) with 30-second TTL. Update driver location every 5 seconds. Persist to PostgreSQL every 60 seconds for analytics.",
        "consequences": "Excellent read/write performance, built-in geo commands, simple TTL-based cleanup. Trade-off: data loss risk on crash (mitigated by frequent persistence), memory limits require sharding.",
        "tags": ["caching", "geospatial", "real-time"],
    },
    {
        "number": "ADR-006",
        "title": "Implement GraphQL API for Mobile Apps",
        "status": "accepted",
        "context": "Mobile apps need flexible data fetching to minimize network requests on slow connections. Different screens require different data subsets (over-fetching with REST).",
        "decision": "Expose GraphQL API via Apollo Server for mobile clients. Maintain REST API for internal services and legacy clients. Use DataLoader for N+1 query prevention.",
        "consequences": "Reduced bandwidth (40% fewer bytes), better mobile UX, client-driven queries. Trade-off: caching complexity, backend complexity, potential for expensive queries (mitigate with depth limits).",
        "tags": ["api", "graphql", "mobile"],
    },
    {
        "number": "ADR-007",
        "title": "Use Kubernetes for Container Orchestration",
        "status": "accepted",
        "context": "Need automated deployment, scaling, self-healing, and multi-cloud portability for 50+ microservices across dev/staging/production environments.",
        "decision": "Adopt Kubernetes (EKS on AWS) with Helm charts for deployment, Horizontal Pod Autoscaling (HPA) based on CPU/custom metrics, and Cluster Autoscaler for node scaling.",
        "consequences": "Automated operations, infrastructure-as-code, vendor neutrality. Trade-off: steep learning curve, operational overhead, potential resource over-provisioning, complexity for simple services.",
        "tags": ["infrastructure", "kubernetes", "devops"],
    },
    {
        "number": "ADR-008",
        "title": "Adopt Temporal for Workflow Orchestration",
        "status": "accepted",
        "context": "Complex multi-step workflows (driver onboarding, payment retry, trip lifecycle) require reliable execution, error handling, and state management across service boundaries.",
        "decision": "Use Temporal for durable workflow execution with automatic retries, compensation logic, and visibility. Replace custom state machines with Temporal workflows written in Go.",
        "consequences": "Simplified business logic, built-in reliability, excellent debugging. Trade-off: additional infrastructure component, vendor lock-in, team learning curve, resource overhead.",
        "tags": ["workflow", "orchestration", "reliability"],
    },
    {
        "number": "ADR-009",
        "title": "Implement OAuth 2.0 + JWT for Authentication",
        "status": "accepted",
        "context": "Need secure, scalable authentication supporting riders, drivers, admins, and third-party integrations. Must work across web, mobile, and API clients.",
        "decision": "Use OAuth 2.0 authorization framework with JWT access tokens (15min expiry) and refresh tokens (30 day). Auth service issues tokens, services validate via shared public key.",
        "consequences": "Industry standard, stateless validation, third-party integration ready. Trade-off: token size (JWT overhead), revocation challenges (mitigate with short expiry + refresh), clock skew issues.",
        "tags": ["security", "authentication", "oauth"],
    },
    {
        "number": "ADR-010",
        "title": "Use S3 for Document Storage",
        "status": "accepted",
        "context": "Need to store driver documents (license, insurance, vehicle photos), profile pictures, and receipts. Expect 10TB+ storage with 99.99% durability SLA.",
        "decision": "Use AWS S3 with lifecycle policies (archive to Glacier after 90 days), CloudFront CDN for delivery, and pre-signed URLs for secure upload/download. Encrypt at rest (AES-256).",
        "consequences": "Unlimited scalability, 99.999999999% durability, cost-effective. Trade-off: vendor lock-in (mitigate with S3-compatible interface), complexity with pre-signed URLs, eventual consistency.",
        "tags": ["storage", "aws", "scalability"],
    },
]

# Add 50 more ADRs
ADDITIONAL_ADRS = [
    ("ADR-011", "Implement Circuit Breaker Pattern", "Prevent cascade failures in microservices"),
    ("ADR-012", "Use Prometheus for Metrics Collection", "Unified metrics and monitoring"),
    ("ADR-013", "Adopt gRPC for Inter-Service Communication", "High-performance RPC framework"),
    ("ADR-014", "Implement API Rate Limiting", "Protect services from abuse and overload"),
    ("ADR-015", "Use WebSockets for Real-time Updates", "Push notifications and live tracking"),
    ("ADR-016", "Implement CQRS for Analytics", "Separate read and write models"),
    ("ADR-017", "Use CDC for Data Synchronization", "Real-time data pipeline with Debezium"),
    ("ADR-018", "Adopt ELK Stack for Logging", "Centralized logging and analysis"),
    ("ADR-019", "Implement Blue-Green Deployments", "Zero-downtime deployments"),
    ("ADR-020", "Use Kafka for Event Streaming", "Scalable event bus for analytics"),
    ("ADR-021", "Adopt OpenAPI 3.0 for API Documentation", "Standardized API specifications"),
    ("ADR-022", "Implement Content Security Policy", "XSS and injection attack prevention"),
    ("ADR-023", "Use HashiCorp Vault for Secrets Management", "Secure credential storage"),
    ("ADR-024", "Adopt React Native for Mobile Apps", "Cross-platform mobile development"),
    ("ADR-025", "Implement Database Sharding", "Horizontal scaling strategy"),
    ("ADR-026", "Use Elasticsearch for Search", "Full-text search and analytics"),
    ("ADR-027", "Adopt GitOps for Infrastructure", "Infrastructure as code with ArgoCD"),
    ("ADR-028", "Implement Chaos Engineering", "Proactive resilience testing"),
    ("ADR-029", "Use Terraform for IaC", "Multi-cloud infrastructure provisioning"),
    ("ADR-030", "Adopt Istio Service Mesh", "Advanced traffic management and security"),
    ("ADR-031", "Implement Distributed Tracing", "End-to-end request tracing with the shared OTLP collector and Tempo"),
    ("ADR-032", "Use GraphQL Federation", "Unified API across microservices"),
    ("ADR-033", "Adopt TypeScript for Frontend", "Type safety in JavaScript"),
    ("ADR-034", "Implement Multi-Region Deployment", "Global availability and low latency"),
    ("ADR-035", "Use Datadog for APM", "Application performance monitoring"),
    ("ADR-036", "Adopt Zero Trust Security", "Never trust, always verify"),
    ("ADR-037", "Implement Feature Flags", "Gradual rollouts and A/B testing"),
    ("ADR-038", "Use Stripe for Payment Processing", "PCI-compliant payment gateway"),
    ("ADR-039", "Adopt SemVer for API Versioning", "Semantic versioning strategy"),
    ("ADR-040", "Implement Data Retention Policies", "GDPR and compliance requirements"),
    ("ADR-041", "Use Twilio for SMS Notifications", "Reliable messaging service"),
    ("ADR-042", "Adopt Sentry for Error Tracking", "Real-time error monitoring"),
    ("ADR-043", "Implement Canary Deployments", "Gradual production rollouts"),
    ("ADR-044", "Use Firebase for Push Notifications", "Cross-platform mobile notifications"),
    ("ADR-045", "Adopt Protocol Buffers for Serialization", "Efficient binary encoding"),
    ("ADR-046", "Implement Database Connection Pooling", "Resource efficiency"),
    ("ADR-047", "Use Cloudflare for DDoS Protection", "Edge security and CDN"),
    ("ADR-048", "Adopt Docker for Containerization", "Consistent runtime environments"),
    ("ADR-049", "Implement Multi-Factor Authentication", "Enhanced security"),
    ("ADR-050", "Use PostGIS for Geospatial Queries", "Location-based features"),
    ("ADR-051", "Adopt React for Web Dashboard", "Component-based UI development"),
    ("ADR-052", "Implement Retry with Exponential Backoff", "Resilient service calls"),
    ("ADR-053", "Use Node.js for API Gateway", "High-throughput request routing"),
    ("ADR-054", "Adopt MongoDB for Session Storage", "Flexible session data model"),
    ("ADR-055", "Implement Idempotency Keys", "Safe retry of payments"),
    ("ADR-056", "Use GitHub Actions for CI/CD", "Automated build and deploy"),
    ("ADR-057", "Adopt NATS for Message Queue", "Lightweight pub/sub"),
    ("ADR-058", "Implement Database Migrations", "Version-controlled schema changes"),
    ("ADR-059", "Use Redis Pub/Sub for Real-time Events", "Low-latency event distribution"),
    ("ADR-060", "Adopt PostgreSQL Full-Text Search", "In-database search capabilities"),
]

for number, title, desc in ADDITIONAL_ADRS:
    ARCHITECTURE_DECISIONS.append({
        "number": number,
        "title": title,
        "status": "accepted" if "Implement" in title else "proposed",
        "context": f"Technical decision context: {desc}",
        "decision": f"Implement {title.lower()} to achieve {desc.lower()}",
        "consequences": f"Benefits of {desc.lower()} with associated trade-offs",
        "tags": ["architecture", "technical-decision"],
    })


# ============================================================================
# 2. TECHNICAL SPECIFICATIONS (80 items)
# ============================================================================

TECHNICAL_SPECS = [
    {
        "title": "Matching Algorithm Specification",
        "category": "algorithm",
        "description": "Detailed specification of the rider-driver matching algorithm including spatial indexing, scoring, and optimization strategies.",
        "content": """
## Overview
The matching algorithm pairs riders with optimal drivers using multi-factor scoring.

## Matching Criteria
1. **Distance**: Drivers within 5km radius, scored inversely by distance
2. **ETA**: Estimated time to pickup, must be <10 minutes
3. **Driver Score**: Rating (0-5) + acceptance rate (0-100%) + completion rate (0-100%)
4. **Vehicle Match**: Rider preferences (capacity, accessibility, vehicle type)
5. **Surge Priority**: Higher fare rides prioritized during surge

## Algorithm Steps
1. Query Redis GEORADIUS for drivers within 5km
2. Filter by availability, vehicle match, minimum rating (4.5+)
3. Calculate composite score: score = (1/distance) * 0.4 + driver_rating * 0.3 + acceptance_rate * 0.3
4. Sort by score descending, offer to top 3 drivers in sequence
5. Fallback: expand radius to 10km if no match in 30 seconds

## Performance Requirements
- p50 latency: <50ms
- p99 latency: <150ms
- Throughput: 10,000 matches/second
""",
    },
    {
        "title": "Payment Processing Flow Specification",
        "category": "payment",
        "description": "End-to-end payment processing including authorization, capture, refunds, and dispute handling.",
        "content": """
## Payment Lifecycle

### 1. Pre-Authorization (Ride Request)
- Validate payment method with $1 hold
- Check fraud score via Stripe Radar
- Reserve estimated fare amount
- Store authorization token

### 2. Ride Completion
- Calculate final fare (base + distance + time + surge + tolls)
- Capture authorized amount (or authorized + 20% if higher)
- Release unused hold within 5 minutes
- Issue receipt via email/SMS

### 3. Driver Payout
- Calculate driver earnings (fare - platform fee - payment processing)
- Aggregate to weekly payout batch
- Transfer via Stripe Connect (ACH/instant)
- Handle failed transfers with retry (3 attempts)

### 4. Refunds & Disputes
- Partial/full refund within 30 days
- Chargeback handling via Stripe
- Dispute resolution workflow with evidence submission

## Error Handling
- Payment declined: retry with backup payment method
- Capture failure: manual review queue
- Payout failure: email driver, retry next cycle
""",
    },
    {
        "title": "Real-time Location Tracking Specification",
        "category": "geolocation",
        "description": "GPS tracking, location updates, privacy, and accuracy requirements for rider and driver location services.",
        "content": """
## Location Update Protocol

### Driver Location
- Update frequency: Every 5 seconds while active
- Accuracy requirement: ±10 meters
- Battery optimization: Reduce to 15s when idle
- Storage: Redis (real-time) + PostgreSQL (historical)
- TTL: 60 seconds in Redis

### Rider Location
- Update frequency: On-demand during booking, every 10s during active ride
- Accuracy requirement: ±50 meters
- Privacy: Location not stored after ride completion

### Geofencing
- Service area boundaries defined in PostGIS
- Surge zones updated every 60 seconds
- Airport/event special zones

## Technical Implementation
- Client: iOS CoreLocation, Android FusedLocationProvider
- Transport: WebSocket for real-time, HTTP fallback
- Compression: Protocol Buffers for bandwidth efficiency
- Privacy: Encrypt location data at rest and in transit
""",
    },
]

# Generate 77 more technical specs
SPEC_CATEGORIES = [
    ("database", "Database Schema Design", "Table structures, indexes, and relationships"),
    ("api", "REST API Endpoint Specification", "HTTP methods, request/response schemas"),
    ("security", "Security Requirements", "Authentication, authorization, encryption"),
    ("performance", "Performance SLA", "Latency, throughput, and availability targets"),
    ("integration", "Third-party Integration", "External service integration specs"),
    ("data-model", "Data Model Definition", "Domain entity schemas and validation"),
    ("messaging", "Message Queue Schema", "Event and command message formats"),
    ("caching", "Caching Strategy", "Cache keys, TTL, and invalidation logic"),
    ("monitoring", "Monitoring & Alerting", "Metrics, logs, and alert thresholds"),
    ("deployment", "Deployment Specification", "Infrastructure and deployment process"),
]

for i in range(77):
    category, title_template, desc_template = SPEC_CATEGORIES[i % len(SPEC_CATEGORIES)]
    TECHNICAL_SPECS.append({
        "title": f"{title_template} - Component {i + 4}",
        "category": category,
        "description": f"{desc_template} for system component {i + 4}",
        "content": f"""
## Technical Specification

### Purpose
{desc_template} for SwiftRide component {i + 4}

### Requirements
1. Functional requirement {i + 1}
2. Non-functional requirement {i + 2}
3. Integration requirement {i + 3}

### Implementation Details
- Technology stack: Python/Go/TypeScript
- Dependencies: PostgreSQL, Redis, NATS
- Performance: <100ms p99 latency

### Testing Strategy
- Unit tests: 80%+ coverage
- Integration tests: Critical paths
- Load tests: 10x peak capacity
""",
    })


# ============================================================================
# 3. API DOCUMENTATION (100 items)
# ============================================================================

API_DOCS = [
    {
        "endpoint": "POST /api/v1/rides",
        "method": "POST",
        "title": "Request a Ride",
        "description": "Create a new ride request from a rider",
        "spec": {
            "request": {
                "pickup_location": {"lat": 37.7749, "lng": -122.4194},
                "dropoff_location": {"lat": 37.8049, "lng": -122.4094},
                "vehicle_type": "standard",
                "payment_method_id": "pm_123456",
                "rider_id": "rider_789",
            },
            "response": {
                "ride_id": "ride_abc123",
                "status": "searching",
                "estimated_fare": 15.50,
                "estimated_arrival": "5 minutes",
            },
            "errors": {
                "400": "Invalid location or payment method",
                "402": "Payment method declined",
                "404": "No drivers available",
            },
        },
    },
    {
        "endpoint": "GET /api/v1/drivers/{id}/earnings",
        "method": "GET",
        "title": "Get Driver Earnings Breakdown",
        "description": "Retrieve detailed earnings for a driver within a date range",
        "spec": {
            "path_params": {"id": "driver_uuid"},
            "query_params": {"start_date": "2025-01-01", "end_date": "2025-01-31"},
            "response": {
                "total_earnings": 4523.50,
                "total_rides": 187,
                "breakdown": {"base_fares": 3200.00, "surge": 450.50, "tips": 873.00, "bonuses": 0.00},
                "platform_fees": 1130.88,
                "net_earnings": 3392.62,
            },
        },
    },
    {
        "endpoint": "WebSocket /ws/rides/{id}",
        "method": "WebSocket",
        "title": "Real-time Ride Updates",
        "description": "Subscribe to real-time updates for an active ride",
        "spec": {
            "events": {
                "driver_assigned": {"driver_id": "drv_123", "eta": "4 mins"},
                "driver_arrived": {"timestamp": "2025-01-31T10:15:00Z"},
                "ride_started": {"timestamp": "2025-01-31T10:16:30Z"},
                "location_update": {"lat": 37.7849, "lng": -122.4094, "heading": 90},
                "ride_completed": {"fare": 15.50, "distance": 5.2, "duration": 18},
            },
        },
    },
]

# Generate 97 more API docs
API_ENDPOINTS = [
    ("GET", "/api/v1/riders/{id}", "Get Rider Profile", "Retrieve rider account information"),
    ("PUT", "/api/v1/riders/{id}", "Update Rider Profile", "Update rider account details"),
    ("GET", "/api/v1/drivers/{id}", "Get Driver Profile", "Retrieve driver account information"),
    ("POST", "/api/v1/drivers", "Register Driver", "Create new driver account"),
    ("GET", "/api/v1/rides/{id}", "Get Ride Details", "Retrieve ride information"),
    ("DELETE", "/api/v1/rides/{id}", "Cancel Ride", "Cancel an active ride"),
    ("POST", "/api/v1/rides/{id}/rating", "Rate Ride", "Submit ride rating and feedback"),
    ("GET", "/api/v1/rides", "List Rides", "Get paginated list of rides"),
    ("POST", "/api/v1/payment-methods", "Add Payment Method", "Add credit card or payment method"),
    ("GET", "/api/v1/payment-methods", "List Payment Methods", "Get saved payment methods"),
    ("DELETE", "/api/v1/payment-methods/{id}", "Remove Payment Method", "Delete payment method"),
    ("POST", "/api/v1/promos", "Apply Promo Code", "Apply promotional discount code"),
    ("GET", "/api/v1/surge-zones", "Get Surge Zones", "Retrieve current surge pricing zones"),
    ("POST", "/api/v1/support/tickets", "Create Support Ticket", "Submit support request"),
    ("GET", "/api/v1/support/tickets/{id}", "Get Support Ticket", "Retrieve ticket details"),
    ("GET", "/api/v1/estimates", "Get Fare Estimate", "Estimate ride fare"),
    ("POST", "/api/v1/rides/{id}/tip", "Add Tip", "Add tip after ride completion"),
    ("GET", "/api/v1/drivers/{id}/stats", "Get Driver Statistics", "Driver performance metrics"),
    ("POST", "/api/v1/vehicles", "Register Vehicle", "Add vehicle to driver account"),
    ("GET", "/api/v1/vehicles/{id}", "Get Vehicle Details", "Retrieve vehicle information"),
]

for i in range(97):
    if i < len(API_ENDPOINTS):
        method, endpoint, title, description = API_ENDPOINTS[i]
    else:
        idx = i % len(API_ENDPOINTS)
        method, endpoint, title, description = API_ENDPOINTS[idx]
        endpoint = f"{endpoint}/variant{i - len(API_ENDPOINTS)}"

    API_DOCS.append({
        "endpoint": endpoint,
        "method": method,
        "title": title,
        "description": description,
        "spec": {
            "request": {"example": "request body"},
            "response": {"example": "response body"},
            "auth": "Bearer token required",
        },
    })


# ============================================================================
# 4. USER GUIDES (70 items)
# ============================================================================

USER_GUIDES = [
    {
        "title": "Getting Started as a Rider",
        "category": "rider-onboarding",
        "audience": "new_rider",
        "content": """
# Getting Started with SwiftRide

## Download the App
1. Download SwiftRide from App Store (iOS) or Google Play (Android)
2. Open the app and tap "Sign Up"
3. Enter your phone number and verify with SMS code

## Set Up Your Account
1. Add your name and email address
2. Upload a profile photo (optional)
3. Add a payment method (credit card, debit card, or PayPal)

## Request Your First Ride
1. Enter your destination in the search box
2. Confirm your pickup location (or drag the pin)
3. Select vehicle type (Standard, Premium, XL)
4. Review fare estimate
5. Tap "Request Ride"

## During Your Ride
- Track your driver's arrival in real-time
- Driver's photo, name, and vehicle info displayed
- Share your trip with friends/family for safety
- Communicate with driver via in-app chat

## After Your Ride
- Rate your driver (1-5 stars)
- Add a tip if desired
- Receipt emailed automatically
- View ride history in app
""",
    },
    {
        "title": "How to Become a SwiftRide Driver",
        "category": "driver-onboarding",
        "audience": "new_driver",
        "content": """
# Become a SwiftRide Driver

## Requirements
- 21+ years old
- Valid driver's license (3+ years)
- Clean driving record
- Vehicle 2015 or newer
- Personal auto insurance
- Pass background check

## Application Process
1. Visit swiftride.com/drive
2. Enter your basic information
3. Upload required documents:
   - Driver's license
   - Vehicle registration
   - Proof of insurance
   - Vehicle photos

## Background Check
- Processing time: 3-5 business days
- Criminal background check
- Driving record review
- You'll receive email when approved

## Vehicle Inspection
- Schedule at SwiftRide partner location
- Or upload photos for virtual inspection
- Checks: tires, lights, brakes, cleanliness

## Start Driving
- Download the Driver app
- Complete in-app training (30 minutes)
- Go online and start accepting rides!
- Earnings deposited weekly (or instant pay)
""",
    },
    {
        "title": "Setting Up Payment Methods",
        "category": "payments",
        "audience": "rider",
        "content": """
# Managing Payment Methods

## Add a Payment Method
1. Open SwiftRide app
2. Tap Menu → Payment
3. Tap "Add Payment Method"
4. Choose type:
   - Credit/Debit Card
   - PayPal
   - Apple Pay / Google Pay
   - Business account (invoice)

## Credit Card
1. Enter card number, expiry, CVV
2. Add billing address
3. Tap "Save Card"
4. $1 verification charge (refunded immediately)

## Set Default Payment
1. Go to Payment Methods
2. Tap card you want as default
3. Toggle "Make Default"

## Payment Security
- All cards encrypted and PCI-compliant
- We never store CVV
- Stripe-powered secure processing
- Instant fraud detection
""",
    },
]

# Generate 67 more user guides
GUIDE_TOPICS = [
    ("rider", "How to Schedule a Ride in Advance", "Booking rides for future dates/times"),
    ("rider", "Sharing Your Trip with Friends", "Safety feature for sharing ride status"),
    ("rider", "Understanding Surge Pricing", "How and why prices increase during high demand"),
    ("rider", "Using Promo Codes", "Applying discounts and promotional offers"),
    ("rider", "Ride Preferences and Favorite Drivers", "Customizing your ride experience"),
    ("rider", "Accessibility Features", "Services for riders with disabilities"),
    ("rider", "Lost Item Recovery", "How to report and retrieve lost items"),
    ("rider", "Safety Features Overview", "Emergency SOS, share trip, safety toolkit"),
    ("rider", "Business Rides and Expensing", "Using SwiftRide for work travel"),
    ("driver", "Maximizing Your Earnings", "Tips for increasing driver income"),
    ("driver", "Understanding Driver Ratings", "How ratings work and tips to maintain high scores"),
    ("driver", "Handling Difficult Passengers", "Best practices for challenging situations"),
    ("driver", "Vehicle Maintenance Tips", "Keeping your car ride-ready"),
    ("driver", "Tax Information for Drivers", "Understanding 1099s and deductions"),
    ("driver", "Driver Rewards Program", "Earning bonuses and incentives"),
    ("driver", "Using the Driver App", "Complete guide to driver app features"),
    ("driver", "Safety Tips for Drivers", "Staying safe while driving"),
    ("admin", "Admin Dashboard Overview", "Using the SwiftRide admin console"),
    ("admin", "Managing Driver Applications", "Review and approve driver signups"),
    ("admin", "Handling Support Tickets", "Customer support workflow"),
]

for i in range(67):
    if i < len(GUIDE_TOPICS):
        audience, title, desc = GUIDE_TOPICS[i]
    else:
        idx = i % len(GUIDE_TOPICS)
        audience, title, desc = GUIDE_TOPICS[idx]
        title = f"{title} (Part {(i // len(GUIDE_TOPICS)) + 2})"

    USER_GUIDES.append({
        "title": title,
        "category": f"{audience}-guide",
        "audience": audience,
        "content": f"""
# {title}

## Overview
{desc}

## Step-by-Step Instructions
1. First step in the process
2. Second step with detailed explanation
3. Third step with screenshots
4. Final step and confirmation

## Tips and Best Practices
- Helpful tip 1
- Helpful tip 2
- Common mistake to avoid

## FAQ
**Q: Common question?**
A: Detailed answer

## Need Help?
Contact support: support@swiftride.com
""",
    })


# ============================================================================
# 5. TUTORIALS (60 items)
# ============================================================================

TUTORIALS = [
    {
        "title": "Your First Ride: Complete Walkthrough",
        "category": "getting-started",
        "difficulty": "beginner",
        "duration_minutes": 10,
        "content": """
# Tutorial: Request Your First Ride

## What You'll Learn
- How to request a ride
- Tracking your driver
- Completing your trip

## Prerequisites
- SwiftRide app installed
- Account created
- Payment method added

## Steps

### 1. Open the App (1 min)
- Launch SwiftRide
- Allow location permissions when prompted
- Your current location appears on map

### 2. Enter Destination (2 min)
- Tap "Where to?" search box
- Type your destination address
- Select from dropdown suggestions
- Review route on map

### 3. Choose Vehicle (1 min)
- See available vehicle types:
  - **Standard**: 4 seats, everyday rides
  - **Premium**: Luxury vehicles
  - **XL**: 6 seats, group rides
- Tap vehicle type to see price estimate

### 4. Request Ride (1 min)
- Review pickup location (drag pin if needed)
- Confirm payment method
- Tap "Request SwiftRide"
- See "Finding your driver..." message

### 5. Driver Matched (2 min)
- Driver's photo, name, and rating shown
- Vehicle make, model, and license plate
- Live tracking of driver's location
- Estimated arrival time updates

### 6. Driver Arrival (1 min)
- "Your driver has arrived" notification
- Walk to vehicle safely
- Verify license plate matches app
- Greet driver and confirm your name

### 7. During Ride (2 min)
- Watch route on map
- Track progress to destination
- Enjoy the ride!
- Chat with driver if needed

### 8. Ride Complete (1 min)
- Arrive at destination
- Fare automatically charged
- Rate your driver (1-5 stars)
- Receipt emailed instantly

## Congratulations!
You've completed your first SwiftRide. 🎉

## Next Steps
- Try scheduling a ride in advance
- Add a second payment method
- Invite friends with your referral code
""",
    },
    {
        "title": "Driver Onboarding: Start Earning in 48 Hours",
        "category": "driver-training",
        "difficulty": "beginner",
        "duration_minutes": 30,
        "content": """
# Tutorial: Become a SwiftRide Driver

## Timeline: 48 Hours to First Ride

### Day 1: Application (15 min)
1. Visit swiftride.com/drive
2. Fill out application form
3. Upload documents:
   - Driver's license photo (both sides)
   - Vehicle registration
   - Insurance card
   - 4 vehicle photos (front, back, both sides)

### Day 1-2: Background Check (24-48 hrs)
- Automated process
- Check email for status updates
- Average approval time: 36 hours

### Day 2: Vehicle Inspection (20 min)
**Option A: In-Person**
- Schedule at partner location
- Mechanic inspects safety items

**Option B: Virtual**
- Follow in-app photo guide
- Take 12 vehicle photos
- Instant approval for qualifying vehicles

### Day 2: App Training (30 min)
1. Download "SwiftRide Driver" app
2. Complete interactive tutorial:
   - Going online/offline
   - Accepting ride requests
   - Navigating to pickup
   - Starting and ending trips
   - Handling payments and tips

3. Pass quiz (10 questions, 80% to pass)

### Day 2: First Ride!
1. Tap "Go Online"
2. Receive ride request
3. Tap "Accept"
4. Navigate to pickup
5. Confirm passenger name
6. Start trip
7. Follow navigation
8. Complete trip
9. Rate passenger
10. Celebrate! 🎉

## Tips for Success
- Keep vehicle clean
- Offer phone chargers
- Know your city well
- Be friendly and professional
- Maintain 4.8+ rating

## Earnings Example
- 20 rides/week x $15 average = $300/week
- Peak hour bonuses: +$50/week
- Tips: $30-50/week
- **Total: ~$380-400/week**
""",
    },
]

# Generate 58 more tutorials
TUTORIAL_TOPICS = [
    ("Setting Up Scheduled Rides", "intermediate", 15),
    ("Using Business Profiles", "intermediate", 20),
    ("Maximizing Driver Earnings", "intermediate", 25),
    ("Understanding Surge Pricing Zones", "advanced", 30),
    ("Multi-Stop Ride Tutorial", "beginner", 10),
    ("Accessibility Features Walkthrough", "beginner", 15),
    ("Lost Item Recovery Process", "beginner", 10),
    ("Setting Up Family Accounts", "intermediate", 20),
    ("Using the Referral Program", "beginner", 10),
    ("Driver Tax Preparation Guide", "advanced", 45),
]

for i in range(58):
    idx = i % len(TUTORIAL_TOPICS)
    title, difficulty, duration = TUTORIAL_TOPICS[idx]
    TUTORIALS.append({
        "title": f"{title} {f'(Part {(i // len(TUTORIAL_TOPICS)) + 2})' if i >= len(TUTORIAL_TOPICS) else ''}",
        "category": "how-to",
        "difficulty": difficulty,
        "duration_minutes": duration,
        "content": f"""
# Tutorial: {title}

## Duration: {duration} minutes
## Difficulty: {difficulty.title()}

## What You'll Learn
- Key concept 1
- Key concept 2
- Key concept 3

## Prerequisites
- Basic SwiftRide account
- Payment method added

## Step-by-Step Guide
1. First major step
2. Second major step
3. Third major step

## Summary
You've learned how to {title.lower()}!
""",
    })


# ============================================================================
# 6. TROUBLESHOOTING GUIDES (70 items)
# ============================================================================

TROUBLESHOOTING_GUIDES = [
    {
        "title": "Unable to Request a Ride",
        "category": "booking-issues",
        "severity": "high",
        "common_causes": ["Payment method declined", "GPS not working", "No drivers available", "Account suspended"],
        "solution": """
## Problem: Cannot Request Ride

### Quick Checks
1. Check internet connection (WiFi or cellular data)
2. Verify location services enabled for SwiftRide
3. Confirm payment method is valid
4. Update app to latest version

### Solution Steps

#### If Payment Method Declined:
1. Open Menu → Payment
2. Verify card expiration date
3. Check billing address is correct
4. Try adding a different payment method
5. Contact your bank to authorize charges

#### If GPS Not Working:
**iOS:**
- Settings → Privacy → Location Services → SwiftRide → "While Using"

**Android:**
- Settings → Apps → SwiftRide → Permissions → Location → Allow

#### If No Drivers Available:
- High demand period (try again in 5 minutes)
- Outside service area (check coverage map)
- Scheduled rides: book 30+ minutes in advance

#### If Account Suspended:
- Check email for suspension notice
- Contact support: support@swiftride.com
- Review Terms of Service compliance

### Still Not Working?
- Clear app cache: Settings → Apps → SwiftRide → Clear Cache
- Reinstall app
- Contact 24/7 support: (800) SWIFTRIDE
""",
    },
    {
        "title": "Driver Not Showing Up",
        "category": "ride-issues",
        "severity": "high",
        "common_causes": ["Incorrect pickup location", "Driver lost", "Driver cancelled", "Communication issues"],
        "solution": """
## Problem: Driver Not Arriving

### Immediate Actions
1. Check driver's live location on map
2. Verify pickup pin is at correct location
3. Call driver using in-app phone button
4. Send message via in-app chat

### If Pickup Location Wrong:
- Tap "Edit Pickup" button
- Drag pin to correct location
- Driver will receive updated location

### If Driver Is Lost:
- Call driver and provide landmarks
- Example: "I'm at Starbucks on the corner"
- Move to well-lit, visible area
- Turn on phone flashlight

### If Wait Time Exceeds 10 Minutes:
1. Tap "Cancel Ride"
2. Choose "Driver no-show" reason
3. No cancellation fee charged
4. Request new ride

### If Driver Cancelled:
- You'll be auto-rematched with new driver
- No action needed
- Original ETA may change

### Prevention Tips:
- Double-check pickup pin before requesting
- Add pickup notes: "At northeast entrance"
- Call driver proactively if complex location
""",
    },
    {
        "title": "Payment Failed After Ride",
        "category": "payment-issues",
        "severity": "critical",
        "common_causes": ["Insufficient funds", "Card expired", "Bank security hold", "Technical error"],
        "solution": """
## Problem: Payment Processing Failed

### What Happens:
- You'll receive email notification
- Ride is recorded in history
- Payment will be retried automatically
- Account may be temporarily suspended

### Resolution Steps:

#### Option 1: Add Funds to Card
- Contact your bank
- Ensure sufficient balance for retry
- Payment retried in 24 hours

#### Option 2: Update Payment Method
1. Menu → Payment → Add Payment Method
2. Enter new card details
3. Set as default
4. Previous ride will be charged automatically

#### Option 3: Pay via App
1. Menu → Ride History
2. Find unpaid ride
3. Tap "Pay Now"
4. Select payment method
5. Complete payment

### Account Suspended?
- Add valid payment method
- Contact support to clear outstanding balance
- Account reinstated within 1 hour

### Prevent Future Issues:
- Keep backup payment method on file
- Enable payment method expiration reminders
- Use bank account alerts for low balance
""",
    },
]

# Generate 67 more troubleshooting guides
TROUBLESHOOTING_TOPICS = [
    ("App Crashes on Startup", "technical", "high"),
    ("GPS Location Inaccurate", "location", "medium"),
    ("Cannot Add Payment Method", "payment", "high"),
    ("Driver Rating Too Low", "driver-issues", "medium"),
    ("Fare Seems Incorrect", "billing", "high"),
    ("Promo Code Not Working", "promotions", "low"),
    ("Cannot Schedule Ride", "booking-issues", "medium"),
    ("Ride History Missing", "account-issues", "low"),
    ("Cannot Log In", "authentication", "critical"),
    ("Forgot Password", "authentication", "medium"),
    ("Two-Factor Authentication Issues", "security", "high"),
    ("Push Notifications Not Received", "notifications", "low"),
    ("Trip Receipt Not Received", "billing", "low"),
    ("Cannot Contact Support", "support", "medium"),
    ("Referral Credit Not Applied", "promotions", "medium"),
]

for i in range(67):
    idx = i % len(TROUBLESHOOTING_TOPICS)
    title, category, severity = TROUBLESHOOTING_TOPICS[idx]
    TROUBLESHOOTING_GUIDES.append({
        "title": f"{title} {f'(Variant {(i // len(TROUBLESHOOTING_TOPICS)) + 2})' if i >= len(TROUBLESHOOTING_TOPICS) else ''}",
        "category": category,
        "severity": severity,
        "common_causes": ["Cause 1", "Cause 2", "Cause 3"],
        "solution": f"""
## Problem: {title}

### Quick Fix
Try this first: [Quick solution step]

### Detailed Resolution
1. Diagnostic step 1
2. Fix step 2
3. Verification step 3

### If Still Not Resolved
Contact support with error code if shown.

### Prevention
Best practice to avoid this issue in the future.
""",
    })


# ============================================================================
# 7. RELEASE NOTES (80 items)
# ============================================================================

RELEASE_NOTES = [
    {
        "version": "4.2.0",
        "release_date": "2025-01-31",
        "title": "Multi-Stop Rides & Enhanced Safety",
        "type": "major",
        "highlights": [
            "Multi-stop rides: Add up to 3 waypoints",
            "Emergency SOS with 911 integration",
            "In-app safety center",
            "Ride preferences: quiet mode, temperature",
            "Performance improvements",
        ],
        "details": """
## What's New in SwiftRide 4.2.0

### 🎯 Multi-Stop Rides
Add up to 3 stops to your ride! Perfect for:
- Picking up friends
- Making quick errands
- Dropping off packages

**How to use:**
1. Enter destination
2. Tap "Add Stop"
3. Enter additional addresses
4. SwiftRide optimizes route automatically

### 🚨 Enhanced Safety Features
Your safety is our priority. New features:
- **Emergency SOS**: One-tap 911 calling with location share
- **Safety Center**: Tips, resources, and safety toolkit
- **Trusted Contacts**: Share trip automatically with up to 5 contacts
- **In-Trip Safety Check**: Proactive check-in if ride goes off-route

### 🎵 Ride Preferences
Customize your ride experience:
- **Quiet Mode**: Prefer minimal conversation
- **Temperature Control**: Request A/C or heat preference
- **Music Preference**: Share your vibe

### ⚡ Performance Improvements
- 40% faster app startup time
- 60% reduction in data usage
- Improved battery efficiency
- Smoother map animations

### 🐛 Bug Fixes
- Fixed issue where ETA would not update correctly
- Resolved crash when viewing ride history offline
- Fixed payment method deletion bug
- Improved location accuracy in urban canyons

### 🔧 Under the Hood
- Updated to latest React Native 0.73
- Enhanced security with certificate pinning
- Improved error logging and diagnostics
""",
    },
    {
        "version": "4.1.5",
        "release_date": "2025-01-15",
        "title": "Bug Fixes & Stability",
        "type": "patch",
        "highlights": ["Critical payment processing bug fix", "Improved GPS accuracy", "App stability improvements"],
        "details": """
## SwiftRide 4.1.5 - Hotfix Release

### 🔧 Critical Fixes
- **Payment Processing**: Fixed rare issue where payment would fail after ride completion
- **GPS Tracking**: Improved location accuracy in areas with poor signal
- **App Crashes**: Resolved crash on iPhone 12 devices when accessing ride history

### 🎯 Performance
- Reduced memory usage by 15%
- Faster map rendering
- Improved background location tracking

### 🔒 Security
- Updated TLS certificates
- Enhanced encryption for payment data
""",
    },
]

# Generate 78 more release notes
for i in range(78):
    version_parts = [4, 2 - (i // 20), i % 10]
    version = f"{version_parts[0]}.{version_parts[1]}.{version_parts[2]}"
    days_ago = i * 14  # Release every 2 weeks
    release_date = (datetime.now(UTC) - timedelta(days=days_ago)).strftime("%Y-%m-%d")

    release_type = "patch" if i % 3 == 0 else "minor" if i % 10 != 0 else "major"

    RELEASE_NOTES.append({
        "version": version,
        "release_date": release_date,
        "title": f"Release {version}",
        "type": release_type,
        "highlights": [f"Feature enhancement {i + 1}", f"Bug fix {i + 1}", f"Performance improvement {i + 1}"],
        "details": f"""
## SwiftRide {version}

### New Features
- Feature A: Description
- Feature B: Description

### Improvements
- Enhancement 1
- Enhancement 2

### Bug Fixes
- Fixed issue #123
- Fixed issue #456
""",
    })


# ============================================================================
# 8. ARCHITECTURE DIAGRAMS (50 items)
# ============================================================================

ARCHITECTURE_DIAGRAMS = [
    {
        "title": "High-Level System Architecture",
        "diagram_type": "system",
        "format": "mermaid",
        "description": "Overall SwiftRide platform architecture showing major components and data flow",
        "diagram": """
graph TB
    subgraph "Client Layer"
        RiderApp[Rider Mobile App]
        DriverApp[Driver Mobile App]
        WebDash[Web Dashboard]
    end

    subgraph "API Gateway"
        Gateway[Kong API Gateway]
        RateLimiter[Rate Limiter]
    end

    subgraph "Microservices"
        RiderSvc[Rider Service]
        DriverSvc[Driver Service]
        MatchSvc[Matching Service]
        PaymentSvc[Payment Service]
        NotifSvc[Notification Service]
        AnalyticsSvc[Analytics Service]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        S3[S3 Storage]
    end

    subgraph "Message Bus"
        NATS[NATS JetStream]
    end

    RiderApp --> Gateway
    DriverApp --> Gateway
    WebDash --> Gateway

    Gateway --> RateLimiter
    RateLimiter --> RiderSvc
    RateLimiter --> DriverSvc
    RateLimiter --> MatchSvc

    MatchSvc --> Redis
    RiderSvc --> PostgreSQL
    DriverSvc --> PostgreSQL
    PaymentSvc --> PostgreSQL

    MatchSvc --> NATS
    NotifSvc --> NATS
    AnalyticsSvc --> NATS

    DriverSvc --> S3
""",
    },
    {
        "title": "Ride Matching Sequence Diagram",
        "diagram_type": "sequence",
        "format": "mermaid",
        "description": "Sequence diagram showing rider-driver matching flow",
        "diagram": """
sequenceDiagram
    participant Rider
    participant API
    participant Matching
    participant Redis
    participant Driver

    Rider->>API: POST /rides (pickup, dropoff)
    API->>Matching: Create ride request
    Matching->>Redis: GEORADIUS (find drivers)
    Redis-->>Matching: List of nearby drivers

    Matching->>Matching: Score & rank drivers
    Matching->>Driver: Send ride offer (top driver)

    alt Driver Accepts
        Driver-->>Matching: Accept ride
        Matching-->>API: Match confirmed
        API-->>Rider: Driver assigned (ETA, details)
    else Driver Rejects
        Driver-->>Matching: Reject ride
        Matching->>Driver: Send to next driver
    else Timeout (15s)
        Matching->>Driver: Send to next driver
    end

    Matching->>Redis: Update driver status (busy)
""",
    },
    {
        "title": "Payment Processing Flow",
        "diagram_type": "sequence",
        "format": "mermaid",
        "description": "End-to-end payment processing including authorization and capture",
        "diagram": """
sequenceDiagram
    participant Rider
    participant API
    participant Payment
    participant Stripe
    participant DB

    Rider->>API: Request ride
    API->>Payment: Pre-authorize payment
    Payment->>Stripe: Create payment intent
    Stripe-->>Payment: Intent ID + auth
    Payment->>DB: Save authorization
    Payment-->>API: Payment authorized

    Note over Rider,DB: Ride in progress...

    API->>Payment: Capture payment (final fare)
    Payment->>Stripe: Capture amount
    Stripe-->>Payment: Payment confirmed
    Payment->>DB: Update transaction
    Payment-->>API: Payment complete
    API->>Payment: Schedule driver payout
    Payment->>Stripe: Transfer to driver (Connect)
""",
    },
]

# Generate 47 more diagrams
DIAGRAM_TOPICS = [
    ("Database Schema - Core Tables", "erd", "Entity relationship diagram"),
    ("Deployment Architecture - AWS", "deployment", "Infrastructure layout"),
    ("CI/CD Pipeline", "flow", "Build and deployment process"),
    ("Authentication Flow", "sequence", "OAuth 2.0 + JWT authentication"),
    ("Real-time Location Update Flow", "sequence", "GPS tracking data flow"),
    ("Surge Pricing Calculation", "flow", "Dynamic pricing algorithm"),
    ("Driver Onboarding Workflow", "flow", "Multi-step onboarding process"),
    ("Notification Service Architecture", "system", "Push notification system"),
    ("Analytics Data Pipeline", "flow", "Data ingestion and processing"),
    ("Service Mesh - Istio", "network", "Microservices communication"),
]

for i in range(47):
    idx = i % len(DIAGRAM_TOPICS)
    title, diagram_type, description = DIAGRAM_TOPICS[idx]
    ARCHITECTURE_DIAGRAMS.append({
        "title": f"{title} {f'v{(i // len(DIAGRAM_TOPICS)) + 2}' if i >= len(DIAGRAM_TOPICS) else ''}",
        "diagram_type": diagram_type,
        "format": "mermaid",
        "description": description,
        "diagram": """
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
    C --> D[Component D]
""",
    })


# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================


async def create_item(
    session: AsyncSession,
    item_type: str,
    title: str,
    description: str,
    priority: int = 5,
    status: str = "draft",
    **_kwargs: Any,
) -> str:
    """Create an item and return its ID.

    Args:
        priority: Integer 0-10 (0=lowest, 10=highest)
    """
    item_id = str(uuid.uuid4())

    query = text("""
        INSERT INTO items (
            id, project_id, type, title, description, priority, status, created_at, updated_at
        ) VALUES (
            :id, :project_id, :type, :title, :description, :priority, :status, NOW(), NOW()
        )
    """)

    await session.execute(
        query,
        {
            "id": item_id,
            "project_id": PROJECT_ID,
            "type": item_type,
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
        },
    )

    items_db[item_type].append(item_id)
    return item_id


async def create_adr_as_item(session: AsyncSession, adr_data: dict) -> str:
    """Create ADR as regular item (adrs table doesn't exist)."""
    description = f"""
## ADR: {adr_data["number"]}
**Status:** {adr_data["status"]}

### Context
{adr_data["context"]}

### Decision
{adr_data["decision"]}

### Consequences
{adr_data["consequences"]}

**Tags:** {", ".join(adr_data.get("tags", []))}
"""

    return await create_item(
        session,
        "architecture_decision",
        f"{adr_data['number']}: {adr_data['title']}",
        description.strip(),
        priority=8 if adr_data["status"] == "accepted" else 5,
        status="approved" if adr_data["status"] == "accepted" else "draft",
    )


async def create_link(session: AsyncSession, source_id: str, target_id: str, link_type: str = "documents") -> None:
    """Create a link between items."""
    link_id = str(uuid.uuid4())

    query = text("""
        INSERT INTO links (
            id, source_id, target_id, link_type, created_at
        ) VALUES (
            :id, :source_id, :target_id, :link_type, NOW()
        )
    """)

    await session.execute(
        query,
        {"id": link_id, "source_id": source_id, "target_id": target_id, "link_type": link_type},
    )


async def fetch_existing_items(session: AsyncSession) -> None:
    """Fetch existing items to link documentation to."""
    item_types = ["feature", "user_story", "epic", "capability", "task", "api_endpoint"]

    for item_type in item_types:
        query = text("""
            SELECT id FROM items
            WHERE project_id = :project_id AND type = :type
            LIMIT 200
        """)

        result = await session.execute(query, {"project_id": PROJECT_ID, "type": item_type})

        ids = [row[0] for row in result]
        existing_items[item_type] = ids


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================


async def generate_documentation() -> None:
    """Generate all documentation items with linking."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Fetch existing items for linking
        await fetch_existing_items(session)

        # 1. Architecture Decisions (60 items)
        for idx, adr in enumerate(ARCHITECTURE_DECISIONS):
            # Create ADR as item
            adr_id = await create_adr_as_item(session, adr)

            # Link to related epics/features
            if existing_items.get("epic"):
                epic_id = existing_items["epic"][idx % len(existing_items["epic"])]
                await create_link(session, adr_id, epic_id, "documents")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 2. Technical Specifications (80 items)
        for idx, spec in enumerate(TECHNICAL_SPECS):
            spec_id = await create_item(
                session,
                "technical_spec",
                spec["title"],
                f"{spec['description']}\n\n{spec['content'][:500]}...",
                priority=8 if idx < 20 else 5,
            )

            # Link to features
            if existing_items.get("feature"):
                feature_id = existing_items["feature"][idx % len(existing_items["feature"])]
                await create_link(session, spec_id, feature_id, "specifies")

            # Link to user stories
            if existing_items.get("user_story") and idx < len(existing_items["user_story"]):
                story_id = existing_items["user_story"][idx]
                await create_link(session, spec_id, story_id, "documents")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 3. API Documentation (100 items)
        for idx, api in enumerate(API_DOCS):
            api_id = await create_item(
                session,
                "api_documentation",
                f"{api['method']} {api['endpoint']}",
                f"{api['description']}\n\nSpec: {json.dumps(api['spec'], indent=2)[:500]}...",
                priority=10 if api["method"] == "POST" else 8,
            )

            # Link to features
            if existing_items.get("feature"):
                feature_id = existing_items["feature"][idx % len(existing_items["feature"])]
                await create_link(session, api_id, feature_id, "implements")

            # Link to technical specs
            if idx < len(items_db["technical_spec"]):
                spec_id = items_db["technical_spec"][idx % len(items_db["technical_spec"])]
                await create_link(session, api_id, spec_id, "documents")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 4. User Guides (70 items)
        for idx, guide in enumerate(USER_GUIDES):
            guide_id = await create_item(
                session,
                "user_guide",
                guide["title"],
                f"Category: {guide['category']}\nAudience: {guide['audience']}\n\n{guide['content'][:500]}...",
                priority=8 if "Getting Started" in guide["title"] else 5,
            )

            # Link to features
            if existing_items.get("feature"):
                feature_id = existing_items["feature"][idx % len(existing_items["feature"])]
                await create_link(session, guide_id, feature_id, "documents")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 5. Tutorials (60 items)
        for idx, tutorial in enumerate(TUTORIALS):
            content = tutorial.get("content", "")
            desc = f"Duration: {tutorial.get('duration_minutes', 0)} min | Difficulty: {tutorial.get('difficulty', '')}\n\n{(content[:500] if isinstance(content, str) else str(content)[:500])}..."
            tutorial_id = await create_item(
                session,
                "tutorial",
                str(tutorial.get("title", "")),
                desc,
                priority=8 if tutorial.get("difficulty") == "beginner" else 5,
            )

            # Link to user guides
            if idx < len(items_db["user_guide"]):
                guide_id = items_db["user_guide"][idx % len(items_db["user_guide"])]
                await create_link(session, tutorial_id, guide_id, "supplements")

            # Link to features
            if existing_items.get("feature"):
                feature_id = existing_items["feature"][idx % len(existing_items["feature"])]
                await create_link(session, tutorial_id, feature_id, "demonstrates")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 6. Troubleshooting Guides (70 items)
        for idx, guide in enumerate(TROUBLESHOOTING_GUIDES):
            solution = guide.get("solution", "")
            sol_str = solution[:500] if isinstance(solution, str) else str(solution)[:500]
            ts_id = await create_item(
                session,
                "troubleshooting_guide",
                str(guide.get("title", "")),
                f"Category: {guide.get('category', '')} | Severity: {guide.get('severity', '')}\n\n{sol_str}...",
                priority=10 if guide.get("severity") == "critical" else 8,
            )

            # Link to features
            if existing_items.get("feature"):
                feature_id = existing_items["feature"][idx % len(existing_items["feature"])]
                await create_link(session, ts_id, feature_id, "troubleshoots")

            # Link to API docs
            if idx < len(items_db["api_documentation"]):
                api_id = items_db["api_documentation"][idx % len(items_db["api_documentation"])]
                await create_link(session, ts_id, api_id, "documents")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 7. Release Notes (80 items)
        for idx, release in enumerate(RELEASE_NOTES):
            release_id = await create_item(
                session,
                "release_note",
                f"Release {release['version']} - {release['title']}",
                f"Type: {release['type']} | Date: {release['release_date']}\n\n{release['details'][:500]}...",
                priority=10 if release["type"] == "major" else 5,
            )

            # Link to features
            if existing_items.get("feature"):
                # Link to multiple features for this release
                for f_idx in range(3):
                    feature_id = existing_items["feature"][(idx * 3 + f_idx) % len(existing_items["feature"])]
                    await create_link(session, release_id, feature_id, "releases")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 8. Architecture Diagrams (50 items)
        for idx, diagram in enumerate(ARCHITECTURE_DIAGRAMS):
            diagram_id = await create_item(
                session,
                "architecture_diagram",
                diagram["title"],
                f"Type: {diagram['diagram_type']} | Format: {diagram['format']}\n\n{diagram['description']}\n\nDiagram:\n{diagram['diagram'][:300]}...",
                priority=8,
            )

            # Link to ADRs
            if idx < len(items_db["architecture_decision"]):
                adr_id = items_db["architecture_decision"][idx % len(items_db["architecture_decision"])]
                await create_link(session, diagram_id, adr_id, "visualizes")

            # Link to technical specs
            if idx < len(items_db["technical_spec"]):
                spec_id = items_db["technical_spec"][idx % len(items_db["technical_spec"])]
                await create_link(session, diagram_id, spec_id, "illustrates")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # Final summary

        # Verify counts
        result = await session.execute(
            text("SELECT COUNT(*) FROM items WHERE project_id = :project_id"),
            {"project_id": PROJECT_ID},
        )
        result.scalar()

        # Count links (project_id doesn't exist in links table - inferred through source item)
        result = await session.execute(
            text("""
                SELECT COUNT(*) FROM links l
                JOIN items i ON l.source_id = i.id
                WHERE i.project_id = :project_id
            """),
            {"project_id": PROJECT_ID},
        )
        result.scalar()

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(generate_documentation())
