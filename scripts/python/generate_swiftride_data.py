#!/usr/bin/env python3
"""SwiftRide Project Data Enhancement Generator.

Generates 2,000+ items and 5,000+ links for comprehensive ride-sharing platform dataset.
"""

import hashlib
import json
import uuid
from pathlib import Path

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"


class ItemGenerator:
    """ItemGenerator."""

    def __init__(self) -> None:
        """Initialize."""
        self.items = []
        self.links = []
        self.item_counter = {}
        self.base_uuid_int = int.from_bytes(hashlib.sha256(b"swiftride_v1").digest()[:16], "big")

    def gen_id(self, prefix: str) -> str:
        """Generate unique UUIDs using counter and prefix."""
        if prefix not in self.item_counter:
            self.item_counter[prefix] = 1
        else:
            self.item_counter[prefix] += 1

        counter = self.item_counter[prefix]
        # Create unique UUID by hashing prefix+counter
        seed = f"{prefix}_{counter}_{self.base_uuid_int}".encode()
        hash_bytes = hashlib.sha256(seed).digest()[:16]
        return str(uuid.UUID(bytes=hash_bytes))

    def add_item(
        self,
        item_type: str,
        title: str,
        description: str,
        status: str = "active",
        priority: int = 2,
        metadata: dict | None = None,
        tags: list | None = None,
        parent_id: str | None = None,
    ) -> str:
        """Add an item and return its ID."""
        item_id = self.gen_id(item_type)
        meta = json.dumps(metadata or {}).replace("'", "''")
        tags_str = "ARRAY[" + ",".join([f"'{tag}'" for tag in (tags or [])]) + "]"

        self.items.append({
            "id": item_id,
            "type": item_type,
            "title": title.replace("'", "''"),
            "description": description.replace("'", "''"),
            "status": status,
            "priority": priority,
            "metadata": meta,
            "tags": tags_str,
            "parent_id": parent_id,
        })

        return item_id

    def add_link(self, source_id: str, target_id: str, link_type: str, metadata: dict | None = None) -> None:
        """Add a link between items."""
        self.links.append({
            "source_id": source_id,
            "target_id": target_id,
            "link_type": link_type,
            "metadata": json.dumps(metadata or {}).replace("'", "''"),
        })

    def generate_sql(self) -> str:
        """Generate SQL INSERT statements."""
        sql = [
            "-- SwiftRide Project Enhancement - Auto-generated",
            "-- Total Items: " + str(len(self.items)),
            "-- Total Links: " + str(len(self.links)),
            "",
            "BEGIN;",
            "",
            "-- ITEMS",
        ]

        # Batch items by type for efficiency
        for item in self.items:
            parent_clause = f", '{item['parent_id']}'" if item["parent_id"] else ", NULL"
            sql.append(
                f"INSERT INTO items (id, project_id, type, title, description, status, priority, metadata, tags, parent_id) "
                f"VALUES ('{item['id']}', '{PROJECT_ID}', '{item['type']}', '{item['title']}', "
                f"'{item['description']}', '{item['status']}', {item['priority']}, '{item['metadata']}'::jsonb, "
                f"{item['tags']}{parent_clause});",
            )

        sql.extend(("", "-- LINKS"))

        sql.extend([
            f"INSERT INTO links (source_id, target_id, link_type, metadata) "
            f"VALUES ('{link['source_id']}', '{link['target_id']}', '{link['link_type']}', "
            f"'{link['metadata']}'::jsonb);"
            for link in self.links
        ])

        sql.extend(("", "COMMIT;"))

        return "\n".join(sql)


def generate_swiftride_data() -> None:
    """Generate comprehensive SwiftRide dataset."""
    gen = ItemGenerator()

    # ==========================================================================
    # BUSINESS LAYER (200 items)
    # ==========================================================================

    # Business Objectives (20)
    objectives = []
    obj_data = [
        (
            "Achieve Market Leadership",
            "Become #1 ride-sharing platform in top 50 US cities with 40% market share",
            {"target_date": "2027-12-31", "kpi": "market_share", "target": 40},
        ),
        (
            "Revenue Growth to $5B ARR",
            "Scale annual recurring revenue to $5 billion",
            {"target_date": "2027-12-31", "kpi": "arr", "target": 5000000000},
        ),
        (
            "Driver Satisfaction Above 4.5",
            "Maintain driver satisfaction at 4.5+ stars",
            {"target_date": "2026-12-31", "kpi": "driver_satisfaction", "target": 4.5},
        ),
        (
            "Carbon Neutral by 2028",
            "Achieve 100% carbon neutral rides",
            {"target_date": "2028-12-31", "kpi": "carbon_neutrality", "target": 100},
        ),
        (
            "Zero Safety Fatalities",
            "Eliminate all fatal accidents through technology and training",
            {"target_date": "2027-12-31", "kpi": "fatality_rate", "target": 0},
        ),
        (
            "Expand to 100 Cities",
            "Launch operations in 100 major metropolitan areas",
            {"target_date": "2027-06-30", "cities_current": 50, "cities_target": 100},
        ),
        (
            "Driver Fleet to 1M",
            "Grow active driver base to 1 million",
            {"target_date": "2028-12-31", "current": 125000, "target": 1000000},
        ),
        (
            "Customer LTV $2000",
            "Increase customer lifetime value through retention",
            {"target_date": "2026-12-31", "current": 850, "target": 2000},
        ),
    ]

    for title, desc, meta in obj_data:
        obj_id = gen.add_item("business_objective", title, desc, "in_progress", 1, meta, ["strategic", "growth"])
        objectives.append(obj_id)

    kpis = []
    kpi_data = [
        ("Gross Booking Value", "Total dollar value of all rides booked", "USD", "monthly", 500000000),
        ("Take Rate", "Commission percentage of GBV", "percent", "monthly", 25),
        ("Monthly Active Riders", "Unique riders per month", "count", "monthly", 15000000),
        ("Monthly Active Drivers", "Unique drivers per month", "count", "monthly", 500000),
        ("Rides Per Day", "Average completed rides daily", "count", "daily", 5000000),
        ("Average Wait Time", "Time from request to arrival", "seconds", "hourly", 240),
        ("Rider Rating", "Average star rating by riders", "stars", "daily", 4.8),
        ("Driver Rating", "Average star rating by drivers", "stars", "daily", 4.5),
        ("Cancellation Rate", "Percentage of canceled rides", "percent", "daily", 5),
        ("Driver Utilization", "Driver time with passengers", "percent", "daily", 60),
        ("Surge Events Per Day", "Number of surge activations", "count", "daily", 5000),
        ("Average Ride Distance", "Mean ride distance in miles", "miles", "daily", 5.2),
        ("Average Ride Duration", "Mean ride time in minutes", "minutes", "daily", 18),
        ("New User Sign-ups", "Daily new rider registrations", "count", "daily", 50000),
        ("Driver Sign-ups", "Daily new driver registrations", "count", "daily", 2000),
        ("Churn Rate - Riders", "Monthly rider churn percentage", "percent", "monthly", 8),
        ("Churn Rate - Drivers", "Monthly driver churn percentage", "percent", "monthly", 12),
        ("Support Ticket Volume", "Daily support requests", "count", "daily", 25000),
        ("First Response Time", "Average support response time", "minutes", "hourly", 15),
        ("Resolution Rate", "Percentage of resolved tickets", "percent", "daily", 85),
    ]

    for title, desc, unit, freq, target in kpi_data:
        kpi_id = gen.add_item(
            "kpi",
            title,
            desc,
            "active",
            1,
            {"unit": unit, "frequency": freq, "target": target},
            ["metrics", "operational"],
        )
        kpis.append(kpi_id)
        # Link KPIs to relevant objectives
        for obj_id in objectives[:3]:
            gen.add_link(obj_id, kpi_id, "measured_by", {"importance": "high"})

    # Market Segments (15)
    segments = []
    segment_data = [
        ("Daily Commuters", "Professionals using ride-sharing for work commutes", 8000000, 15, 450),
        ("Airport Travelers", "Travelers needing airport transportation", 3000000, 20, 65),
        ("Night Life & Entertainment", "Users going to bars, restaurants, events", 5000000, 10, 35),
        ("Corporate Accounts", "Businesses providing employee ride credits", 50000, 25, 25000),
        ("Seniors & Accessibility", "Elderly and disabled riders", 2000000, 30, 200),
        ("Students", "College students using for campus transportation", 4000000, 18, 150),
        ("Suburban Families", "Family rides for errands and activities", 3500000, 12, 280),
        ("Medical Transportation", "Non-emergency medical appointments", 1500000, 25, 320),
        ("Business Travelers", "Corporate travelers during business trips", 2500000, 15, 850),
        ("Event Attendees", "Concerts, sports, conferences", 3000000, 22, 45),
    ]

    for title, desc, size, growth, spend in segment_data:
        seg_id = gen.add_item(
            "market_segment",
            title,
            desc,
            "active",
            1,
            {"size": size, "growth_rate": growth, "avg_spend": spend},
            ["market", "segment"],
        )
        segments.append(seg_id)

    personas = []
    persona_data = [
        ("Sarah - Daily Commuter", "Marketing Manager, 32, twice daily for work", "rider", 32, 85000),
        ("Marcus - Part-Time Driver", "College student, 22, drives 20 hrs/week", "driver", 22, 25000),
        ("James - Full-Time Driver", "Professional driver, 45, 50+ hrs/week", "driver", 45, 55000),
        ("Emily - Corporate Admin", "HR Manager, 38, manages 500 employee accounts", "b2b", 38, 95000),
        ("Robert - Senior Rider", "Retired teacher, 72, medical appointments", "rider", 72, 35000),
        ("Lisa - Business Traveler", "Consultant, 35, frequent business trips", "rider", 35, 120000),
        ("David - Weekend Driver", "Teacher, 40, drives weekends for extra income", "driver", 40, 65000),
        ("Anna - Student Rider", "College student, 20, campus and social rides", "rider", 20, 15000),
        ("Tom - Accessibility User", "Wheelchair user, 55, requires WAV vehicles", "rider", 55, 45000),
        ("Maria - Night Shift Worker", "Nurse, 33, late-night hospital commutes", "rider", 33, 70000),
    ]

    for title, desc, ptype, age, income in persona_data:
        persona_id = gen.add_item(
            "persona",
            title,
            desc,
            "active",
            1,
            {"age": age, "income": income, "type": ptype},
            ["persona", ptype],
        )
        personas.append(persona_id)
        # Link personas to segments
        gen.add_link(segments[0], persona_id, "includes", {})

    # Business Rules (30)
    rules = []
    rule_data = [
        ("Surge Pricing Activation", "Activate surge when demand exceeds supply by 30%", 1),
        ("Driver Background Check Renewal", "Drivers must renew background check every 12 months", 1),
        ("Minimum Driver Rating", "Drivers below 4.0 get warning, below 3.8 deactivated", 1),
        ("Cancellation Fee Policy", "Charge $5 if rider cancels after 2 minutes", 2),
        ("Maximum Ride Duration", "Single rides cannot exceed 8 hours or 500 miles", 2),
        ("Driver Age Requirement", "Drivers must be 21+ years old", 1),
        ("Vehicle Age Limit", "Vehicles must be 10 years old or newer", 1),
        ("Insurance Verification", "Proof of insurance required for activation", 1),
        ("License Verification", "Valid driver's license required", 1),
        ("Maximum Consecutive Hours", "Drivers limited to 12 consecutive hours", 1),
        ("Surge Cap", "Surge multiplier capped at 3.0x base fare", 2),
        ("Minimum Fare", "All rides subject to $5 minimum fare", 2),
        ("Tip Maximum", "Tips capped at 100% of ride fare", 2),
        ("Referral Credit Expiry", "Referral credits expire after 30 days", 3),
        ("Account Inactivity", "Inactive accounts suspended after 12 months", 3),
    ]

    for title, desc, priority in rule_data:
        rule_id = gen.add_item(
            "business_rule",
            title,
            desc,
            "active",
            priority,
            {"enforcement": "automatic"},
            ["policy", "enforcement"],
        )
        rules.append(rule_id)

    # Compliance Requirements (25)
    compliance = []
    comp_data = [
        ("CCPA Data Privacy", "California Consumer Privacy Act compliance", "California", "privacy"),
        ("ADA Accessibility", "Americans with Disabilities Act requirements", "Federal", "accessibility"),
        ("PCI-DSS Payment Security", "Payment Card Industry Data Security Standard", "Global", "security"),
        ("City Transportation Permits", "Municipal operating permits", "Municipal", "operations"),
        ("GDPR EU Data Protection", "General Data Protection Regulation", "EU", "privacy"),
        ("SOC 2 Type II", "Security, availability, processing integrity", "Global", "security"),
        ("HIPAA Medical Transport", "Health insurance data protection", "Federal", "privacy"),
        ("Fair Labor Standards", "Employee classification and wages", "Federal", "labor"),
        ("Vehicle Safety Standards", "Federal motor vehicle safety requirements", "Federal", "safety"),
        ("Insurance Requirements", "Commercial auto insurance mandates", "State", "insurance"),
    ]

    for title, desc, jurisdiction, category in comp_data:
        comp_id = gen.add_item(
            "compliance",
            title,
            desc,
            "active",
            1,
            {"jurisdiction": jurisdiction, "category": category},
            ["legal", "compliance", category],
        )
        compliance.append(comp_id)

    # Revenue Models (10)
    revenue_models = []
    rev_data = [
        ("Per-Ride Commission", "Standard 25% commission on rides", 25, 1),
        ("Subscription Plans", "Monthly subscriptions for discounts", 15, 2),
        ("Cancellation Fees", "Late cancellation fees", 5, 3),
        ("Advertising Revenue", "In-app advertising", 10, 3),
        ("Data Analytics Products", "Anonymized mobility data sales", 5, 3),
        ("Premium Services", "Priority pickup and luxury vehicles", 8, 2),
        ("Corporate Contracts", "B2B enterprise agreements", 20, 1),
        ("Airport Surcharge", "Fixed airport pickup fee", 3, 2),
        ("Wait Time Fees", "Charges for extended wait times", 2, 3),
        ("Toll Pass Revenue", "Automated toll payments", 1, 3),
    ]

    for title, desc, percent, priority in rev_data:
        rev_id = gen.add_item(
            "revenue_model",
            title,
            desc,
            "active",
            priority,
            {"contribution_percent": percent},
            ["revenue", "business-model"],
        )
        revenue_models.append(rev_id)
        gen.add_link(objectives[1], rev_id, "contributes_to", {})

    # Pricing Strategies (15)
    pricing = []
    price_data = [
        ("Dynamic Surge Pricing", "Real-time pricing with 1.1x-3.0x multipliers", 1),
        ("Time-of-Day Pricing", "Lower prices during off-peak hours", 2),
        ("Distance-Based Pricing", "Base fare + per-mile + per-minute", 1),
        ("Promotional Discounts", "New user and referral discounts", 2),
        ("Corporate Flat Rate", "Fixed pricing for corporate accounts", 2),
        ("Zone-Based Pricing", "Different rates for different city zones", 2),
        ("Weather Premium", "Higher rates during severe weather", 3),
        ("Event Pricing", "Special rates for major events", 2),
        ("Loyalty Tier Pricing", "Discounts for frequent users", 2),
        ("Group Ride Discounts", "Lower per-person rates for shared rides", 2),
    ]

    for title, desc, priority in price_data:
        price_id = gen.add_item(
            "pricing_strategy",
            title,
            desc,
            "active",
            priority,
            {"dynamic": title.find("Dynamic") != -1},
            ["pricing", "strategy"],
        )
        pricing.append(price_id)

    # ==========================================================================
    # PRODUCT LAYER (400 items)
    # ==========================================================================

    epics = []
    epic_data = [
        (
            "Driver Onboarding & Verification",
            "Complete driver signup, background checks, vehicle inspection",
            "driver-platform",
        ),
        ("Real-Time Matching Engine", "Advanced algorithm for optimal rider-driver matching", "core-platform"),
        ("Dynamic Pricing & Surge System", "ML-based demand prediction and surge pricing", "pricing"),
        ("Payment Processing & Splits", "End-to-end payment with multi-party splits", "payments"),
        ("Safety & Trust Platform", "Emergency button, trip sharing, incident reporting", "safety"),
        ("Rating & Review System", "Bi-directional rating with quality enforcement", "quality"),
        ("Multi-Stop Ride Experience", "Multiple stops with optimized routing", "rider-experience"),
        ("Ride Scheduling System", "Schedule rides up to 30 days in advance", "scheduling"),
        ("Corporate Accounts Platform", "B2B platform with billing and reporting", "enterprise"),
        ("Accessibility Features", "Wheelchair accessible vehicles, senior-friendly UI", "accessibility"),
        ("Fraud Detection System", "ML-based fraud detection and prevention", "security"),
        ("Driver Earnings Dashboard", "Transparent earnings tracking and forecasting", "driver-experience"),
        ("Referral & Rewards Program", "User acquisition through referrals", "growth"),
        ("In-App Chat & Support", "Real-time communication between riders and drivers", "support"),
        ("Route Optimization Engine", "AI-powered route planning and traffic avoidance", "navigation"),
        ("Fleet Management Tools", "Tools for fleet operators and partners", "b2b"),
        ("Analytics & Reporting", "Business intelligence and operational analytics", "analytics"),
        ("Mobile App Performance", "App speed, reliability, and offline capability", "engineering"),
        ("Subscription Service", "Monthly subscription plans with benefits", "monetization"),
        ("Multi-Modal Transportation", "Integration with bikes, scooters, public transit", "expansion"),
    ]

    for title, desc, team in epic_data:
        epic_id = gen.add_item("epic", title, desc, "in_progress", 1, {"team": team, "effort": "large"}, ["epic", team])
        epics.append(epic_id)
        # Link epics to business objectives
        for obj_id in objectives[:3]:
            gen.add_link(epic_id, obj_id, "supports", {"alignment": "strategic"})

    features = []
    for i, epic_id in enumerate(epics):
        # Each epic gets 6 features
        for j in range(6):
            feat_id = gen.add_item(
                "feature",
                f"Feature {i + 1}.{j + 1}: {epic_data[i][0]} Component",
                f"Detailed feature implementation for {epic_data[i][0]} - component {j + 1}",
                "in_progress" if j < 3 else "planned",
                1 if j < 2 else 2,
                {"complexity": "medium", "estimate_days": 10 + j * 5},
                ["feature", epic_data[i][2]],
                epic_id,
            )
            features.append(feat_id)
            gen.add_link(feat_id, epic_id, "implements", {})

    # User Stories (240)
    stories = []
    for i, feat_id in enumerate(features):
        # Each feature gets 2 user stories
        for j in range(2):
            # Get the feature item dict
            feat_item = None
            for item in gen.items:
                if item["id"] == feat_id:
                    feat_item = item
                    break

            story_title = f"User Story: Feature {i + 1} - Scenario {j + 1}"
            if feat_item:
                story_title = f"User Story: {feat_item['title'][:30]}... - Scenario {j + 1}"

            story_id = gen.add_item(
                "user_story",
                story_title,
                f"As a user, I want to {['access', 'utilize'][j]} this feature so that I can achieve my goal",
                "in_progress" if j == 0 else "planned",
                2,
                {"story_points": 3 + j, "sprint": "current" if j == 0 else "next"},
                ["story", "user-facing"],
                feat_id,
            )
            stories.append(story_id)
            gen.add_link(story_id, feat_id, "refines", {})

    # Tasks (480 - 2 per story)
    tasks = []
    for i, story_id in enumerate(stories):
        for j in range(2):
            task_id = gen.add_item(
                "task",
                f"Task: Implement {['frontend', 'backend'][j]} for story {i + 1}",
                f"Technical implementation task for {['UI/UX', 'API/Database'][j]} components",
                "in_progress" if j == 0 and i < 50 else "planned",
                2,
                {"estimate_hours": 4 + j * 2, "assignee": f"dev_{i % 10}"},
                ["task", "engineering"],
                story_id,
            )
            tasks.append(task_id)
            gen.add_link(task_id, story_id, "implements", {})

    # Use Cases (50)
    use_cases = []
    use_case_data = [
        ("Request Ride Flow", "Complete flow from opening app to ride request"),
        ("Driver Accept Flow", "Driver receives and accepts ride request"),
        ("Navigation to Pickup", "Driver navigates to pickup location"),
        ("Passenger Pickup", "Driver confirms passenger pickup"),
        ("Navigate to Destination", "Driver follows route to destination"),
        ("Complete Ride", "End ride and process payment"),
        ("Rate Experience", "Both parties rate each other"),
        ("Schedule Future Ride", "Book ride for future date/time"),
        ("Cancel Ride", "Cancel ride before/after acceptance"),
        ("Add Multiple Stops", "Request ride with multiple destinations"),
    ] * 5  # Repeat to get 50

    for i, (title, desc) in enumerate(use_case_data[:50]):
        uc_id = gen.add_item(
            "use_case",
            f"{title} - Variant {i // 10 + 1}",
            desc,
            "active",
            2,
            {"actors": ["rider", "driver"], "preconditions": [], "postconditions": []},
            ["use-case", "scenario"],
        )
        use_cases.append(uc_id)
        # Link to relevant features
        gen.add_link(use_cases[i], features[i % len(features)], "validates", {})

    # Acceptance Criteria (120 - 1 per feature)
    for i, feat_id in enumerate(features):
        # Get the feature item dict
        feat_item = None
        for item in gen.items:
            if item["id"] == feat_id:
                feat_item = item
                break

        ac_title = f"AC: Feature {i + 1} must meet standards"
        if feat_item:
            ac_title = f"AC: {feat_item['title'][:40]}... must meet standards"

        ac_id = gen.add_item(
            "acceptance_criteria",
            ac_title,
            "Given the feature, when user interacts, then expected outcome occurs",
            "active",
            1,
            {"testable": True, "automated": True},
            ["acceptance-criteria", "quality"],
        )
        gen.add_link(feat_id, ac_id, "satisfies", {})

    # ==========================================================================
    # ARCHITECTURE LAYER (200 items)
    # ==========================================================================

    services = []
    service_data = [
        ("User Service", "User account management and authentication", "Python/FastAPI", 8080),
        ("Driver Service", "Driver profiles, onboarding, status", "Go/gRPC", 8081),
        ("Ride Service", "Ride lifecycle and state management", "Go/gRPC", 8082),
        ("Matching Service", "Real-time driver-rider matching algorithm", "Go/gRPC", 8083),
        ("Location Service", "Geospatial tracking and updates", "Go/gRPC", 8084),
        ("Pricing Service", "Dynamic pricing and fare calculation", "Python/FastAPI", 8085),
        ("Payment Service", "Payment processing and splits", "Python/FastAPI", 8086),
        ("Notification Service", "Push, SMS, email notifications", "Node.js", 8087),
        ("Rating Service", "Rating and review management", "Python/FastAPI", 8088),
        ("Analytics Service", "Real-time metrics and reporting", "Python/FastAPI", 8089),
        ("Fraud Detection Service", "ML-based fraud detection", "Python/FastAPI", 8090),
        ("Support Service", "Customer support ticketing", "Python/FastAPI", 8091),
        ("Dispatch Service", "Ride dispatch and queue management", "Go/gRPC", 8092),
        ("Route Service", "Route optimization and ETA", "Go/gRPC", 8093),
        ("Surge Service", "Surge pricing calculation", "Python/FastAPI", 8094),
        ("Corporate Service", "B2B account management", "Python/FastAPI", 8095),
        ("Safety Service", "Emergency features and incident tracking", "Go/gRPC", 8096),
        ("Document Service", "Document upload and verification", "Go/gRPC", 8097),
        ("Webhook Service", "External webhook management", "Node.js", 8098),
        ("Integration Service", "Third-party integrations", "Python/FastAPI", 8099),
    ]

    for title, desc, tech, port in service_data:
        svc_id = gen.add_item(
            "microservice",
            title,
            desc,
            "active",
            1,
            {"technology": tech, "port": port, "replicas": 3},
            ["microservice", "backend"],
        )
        services.append(svc_id)

    # API Endpoints (100 - 5 per service)
    endpoints = []
    http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    for i, svc_id in enumerate(services):
        for j in range(5):
            ep_id = gen.add_item(
                "api_endpoint",
                f"{http_methods[j % 5]} /api/v1/{service_data[i][0].lower().replace(' ', '-')}/{['list', 'create', 'update', 'delete', 'status'][j]}",
                f"API endpoint for {service_data[i][0]} - {['retrieve list', 'create new', 'update existing', 'delete item', 'get status'][j]}",
                "active",
                2,
                {"method": http_methods[j % 5], "auth_required": True, "rate_limit": 1000},
                ["api", "rest"],
                svc_id,
            )
            endpoints.append(ep_id)
            gen.add_link(svc_id, ep_id, "exposes", {})

    # Data Models (50)
    models = []
    model_data = [
        ("User", "User account and profile data"),
        ("Driver", "Driver profile and verification"),
        ("Vehicle", "Vehicle information and inspection"),
        ("Ride", "Ride request and completion data"),
        ("Location", "Geospatial location data"),
        ("Payment", "Payment transaction records"),
        ("Rating", "Rating and review data"),
        ("Notification", "Notification history"),
        ("SurgeZone", "Surge pricing zone data"),
        ("Promotion", "Promotional campaign data"),
    ] * 5

    for i, (title, desc) in enumerate(model_data[:50]):
        model_id = gen.add_item(
            "data_model",
            f"{title} Model - Version {i // 10 + 1}",
            desc,
            "active",
            2,
            {"schema_version": i // 10 + 1, "fields_count": 10 + i},
            ["model", "database"],
        )
        models.append(model_id)

    # Database Schemas (30)
    schemas = []
    for i in range(30):
        # Get the model item dict
        model_item = None
        for item in gen.items:
            if item["id"] == models[i]:
                model_item = item
                break

        schema_title = f"Schema: Model {i + 1} Table Definition"
        schema_desc = f"PostgreSQL table schema for model {i + 1}"
        if model_item:
            schema_title = f"Schema: {model_item['title']} Table Definition"
            schema_desc = f"PostgreSQL table schema for {model_item['title']}"

        schema_id = gen.add_item(
            "database_schema",
            schema_title,
            schema_desc,
            "active",
            2,
            {"database": "postgresql", "migration": f"00{i + 1}"},
            ["database", "schema"],
        )
        schemas.append(schema_id)
        gen.add_link(models[i], schema_id, "defines", {})

    # Integration Points (30)
    integrations = []
    int_data = [
        ("Stripe Payment Gateway", "Payment processing integration"),
        ("Twilio SMS", "SMS notification delivery"),
        ("SendGrid Email", "Email notification delivery"),
        ("Google Maps API", "Routing and geocoding"),
        ("AWS S3", "Document and image storage"),
        ("Checkr Background Checks", "Driver background verification"),
        ("Segment Analytics", "User behavior tracking"),
        ("Datadog Monitoring", "System monitoring and alerts"),
        ("PagerDuty Alerts", "Incident management"),
        ("Auth0 Authentication", "User authentication"),
    ] * 3

    for i, (title, desc) in enumerate(int_data[:30]):
        int_id = gen.add_item(
            "integration_point",
            f"{title} - Instance {i // 10 + 1}",
            desc,
            "active",
            2,
            {"type": "external", "protocol": "REST"},
            ["integration", "external"],
        )
        integrations.append(int_id)

    # Infrastructure Components (40)
    infra = []
    infra_data = [
        ("PostgreSQL Primary DB", "Main database cluster", "database"),
        ("PostgreSQL Read Replica", "Read-only database replica", "database"),
        ("Redis Cache Cluster", "In-memory cache", "cache"),
        ("NATS JetStream", "Message broker", "messaging"),
        ("Kubernetes Cluster", "Container orchestration", "orchestration"),
        ("Load Balancer", "Traffic distribution", "networking"),
        ("CDN", "Static content delivery", "cdn"),
        ("Object Storage", "File storage", "storage"),
        ("Elasticsearch Cluster", "Search and analytics", "search"),
        ("Prometheus", "Metrics collection", "monitoring"),
    ] * 4

    for i, (title, desc, category) in enumerate(infra_data[:40]):
        infra_id = gen.add_item(
            "infrastructure",
            f"{title} - {i // 10 + 1}",
            desc,
            "active",
            1,
            {"category": category, "environment": "production"},
            ["infrastructure", category],
        )
        infra.append(infra_id)

    # ==========================================================================
    # DEVELOPMENT LAYER (500 items)
    # ==========================================================================

    # Python Code Files (150)
    py_files = []
    for i, svc_id in enumerate(services[:15]):  # Python services
        for j in range(10):
            py_id = gen.add_item(
                "code_file",
                f"src/services/{service_data[i][0].lower().replace(' ', '_')}/{['models', 'routes', 'schemas', 'services', 'utils', 'validators', 'middleware', 'exceptions', 'config', 'tasks'][j]}.py",
                f"Python implementation file for {service_data[i][0]} - {['models', 'routes', 'schemas', 'services', 'utils', 'validators', 'middleware', 'exceptions', 'config', 'tasks'][j]} module",
                "active",
                2,
                {"language": "python", "lines": 200 + j * 50, "complexity": j + 1},
                ["code", "python"],
                svc_id,
            )
            py_files.append(py_id)
            gen.add_link(py_id, svc_id, "implements", {})

    # TypeScript Code Files (100)
    ts_files = []
    ts_modules = ["components", "hooks", "services", "utils", "types", "stores", "api", "routes", "config", "constants"]
    for i in range(100):
        ts_id = gen.add_item(
            "code_file",
            f"frontend/src/{ts_modules[i % 10]}/{['index', 'types', 'utils', 'hooks', 'components'][i % 5]}.tsx",
            "TypeScript React component/module for frontend",
            "active",
            2,
            {"language": "typescript", "lines": 150 + i * 10, "framework": "react"},
            ["code", "typescript", "frontend"],
        )
        ts_files.append(ts_id)

    # Go Code Files (100)
    go_files = []
    for i, svc_id in enumerate(services[15:]):  # Go services
        for j in range(20):
            go_id = gen.add_item(
                "code_file",
                f"services/{service_data[i + 15][0].lower().replace(' ', '_')}/internal/{['handler', 'service', 'repository', 'model', 'client'][j % 5]}/{['main', 'types', 'errors', 'utils', 'config'][j // 5]}.go",
                f"Go implementation file for {service_data[i + 15][0]}",
                "active",
                2,
                {"language": "go", "lines": 180 + j * 20, "package": service_data[i + 15][0].lower().replace(" ", "_")},
                ["code", "go"],
                svc_id,
            )
            go_files.append(go_id)
            gen.add_link(go_id, svc_id, "implements", {})

    # Database Migration Scripts (50)
    migrations = []
    for i in range(50):
        mig_id = gen.add_item(
            "migration",
            f"alembic/versions/{i + 1:03d}_add_{['users', 'drivers', 'rides', 'payments', 'ratings'][i % 5]}_table.py",
            f"Database migration for {['users', 'drivers', 'rides', 'payments', 'ratings'][i % 5]} schema changes",
            "active",
            2,
            {"version": f"{i + 1:03d}", "type": "schema"},
            ["migration", "database"],
        )
        migrations.append(mig_id)

    # Configuration Files (50)
    configs = []
    config_types = ["service", "kubernetes", "docker", "nginx", "environment"]
    for i in range(50):
        cfg_id = gen.add_item(
            "config_file",
            f"config/{config_types[i % 5]}/{['production', 'staging', 'development'][i % 3]}.{'yaml' if i % 2 == 0 else 'env'}",
            f"Configuration file for {config_types[i % 5]} in {['production', 'staging', 'development'][i % 3]} environment",
            "active",
            2,
            {"type": config_types[i % 5], "environment": ["production", "staging", "development"][i % 3]},
            ["config", config_types[i % 5]],
        )
        configs.append(cfg_id)

    # Deployment Scripts (50)
    scripts = []
    for i in range(50):
        script_id = gen.add_item(
            "script",
            f"scripts/{['deploy', 'rollback', 'backup', 'migrate', 'seed'][i % 5]}_{['production', 'staging'][i % 2]}.sh",
            f"Deployment automation script for {['deploy', 'rollback', 'backup', 'migrate', 'seed'][i % 5]} operations",
            "active",
            2,
            {"type": ["deploy", "rollback", "backup", "migrate", "seed"][i % 5], "shell": "bash"},
            ["script", "automation"],
        )
        scripts.append(script_id)

    # ==========================================================================
    # TESTING LAYER (400 items)
    # ==========================================================================

    # Unit Tests (200 - match code files)
    unit_tests = []
    all_code_files = py_files + go_files
    for i, code_id in enumerate(all_code_files[:200]):
        # Get the code file item dict
        code_item = None
        for item in gen.items:
            if item["id"] == code_id:
                code_item = item
                break

        test_filename = f"tests/unit/test_{i}.py"
        if code_item:
            test_filename = f"tests/unit/{code_item['title'].replace('src/', '').replace('.py', '_test.py').replace('.go', '_test.go')}"

        test_id = gen.add_item(
            "unit_test",
            test_filename,
            f"Unit tests for code file {i + 1}",
            "active",
            2,
            {"coverage": 85 + i % 15, "assertions": 10 + i % 20},
            ["test", "unit"],
        )
        unit_tests.append(test_id)
        gen.add_link(test_id, code_id, "tests", {})

    # Integration Tests (100)
    integration_tests = []
    for i, svc_id in enumerate(services):
        for j in range(5):
            int_test_id = gen.add_item(
                "integration_test",
                f"tests/integration/{service_data[i][0].lower().replace(' ', '_')}/{['api', 'database', 'cache', 'messaging', 'auth'][j]}_integration_test.py",
                f"Integration test for {service_data[i][0]} - {['API', 'Database', 'Cache', 'Messaging', 'Auth'][j]} integration",
                "active",
                2,
                {"duration_seconds": 5 + j, "dependencies": [service_data[i][0]]},
                ["test", "integration"],
            )
            integration_tests.append(int_test_id)
            gen.add_link(int_test_id, svc_id, "tests", {})

    # E2E Tests (50)
    e2e_tests = []
    for i, uc_id in enumerate(use_cases):
        # Get the use case item dict
        uc_item = None
        for item in gen.items:
            if item["id"] == uc_id:
                uc_item = item
                break

        e2e_filename = f"tests/e2e/scenarios/test_scenario_{i + 1}_e2e.spec.ts"
        e2e_desc = f"End-to-end test for scenario {i + 1} complete flow"
        if uc_item:
            e2e_filename = f"tests/e2e/scenarios/{uc_item['title'].lower().replace(' ', '_')}_e2e.spec.ts"
            e2e_desc = f"End-to-end test for {uc_item['title']} complete flow"

        e2e_id = gen.add_item(
            "e2e_test",
            e2e_filename,
            e2e_desc,
            "active",
            1,
            {"duration_seconds": 30 + i, "browser": "chromium"},
            ["test", "e2e", "playwright"],
        )
        e2e_tests.append(e2e_id)
        gen.add_link(e2e_id, uc_id, "verifies", {})

    # Performance Tests (30)
    perf_tests = []
    for i, ep_id in enumerate(endpoints[:30]):
        # Get the endpoint item dict
        ep_item = None
        for item in gen.items:
            if item["id"] == ep_id:
                ep_item = item
                break

        perf_filename = f"tests/performance/load_test_{i + 1}.py"
        perf_desc = f"Load test for endpoint {i + 1} - target 1000 RPS"
        if ep_item:
            perf_filename = f"tests/performance/load_{ep_item['title'].replace('/', '_')}_load_test.py"
            perf_desc = f"Load test for {ep_item['title']} - target 1000 RPS"

        perf_id = gen.add_item(
            "performance_test",
            perf_filename,
            perf_desc,
            "active",
            2,
            {"target_rps": 1000, "duration_minutes": 5, "p95_latency_ms": 200},
            ["test", "performance", "load"],
        )
        perf_tests.append(perf_id)
        gen.add_link(perf_id, ep_id, "tests", {})

    # Security Tests (20)
    sec_tests = []
    for i in range(20):
        sec_id = gen.add_item(
            "security_test",
            f"tests/security/{['auth', 'injection', 'xss', 'csrf'][i % 4]}_security_test.py",
            f"Security test for {['authentication', 'SQL injection', 'XSS attacks', 'CSRF protection'][i % 4]} vulnerabilities",
            "active",
            1,
            {"severity": ["critical", "high", "medium"][i % 3], "tool": "OWASP ZAP"},
            ["test", "security"],
        )
        sec_tests.append(sec_id)

    # ==========================================================================
    # OPERATIONS LAYER (200 items)
    # ==========================================================================

    # Monitoring Dashboards (40)
    dashboards = []
    for i in range(40):
        dash_id = gen.add_item(
            "dashboard",
            f"Dashboard: {['Service Health', 'Business Metrics', 'Infrastructure', 'Security'][i % 4]} - {i // 4 + 1}",
            f"Monitoring dashboard for {['Service Health', 'Business Metrics', 'Infrastructure', 'Security'][i % 4]} visualization",
            "active",
            2,
            {"tool": "Grafana", "panels": 8 + i % 12, "refresh": "30s"},
            ["monitoring", "dashboard"],
        )
        dashboards.append(dash_id)

    alerts = []
    alert_types = ["error_rate", "latency", "cpu", "memory", "disk", "network"]
    for i in range(60):
        # Get the service item dict
        svc_idx = i % len(services)
        svc_item = None
        for item in gen.items:
            if item["id"] == services[svc_idx]:
                svc_item = item
                break

        alert_title = f"Alert: {alert_types[i % 6].upper()} threshold exceeded - Service {svc_idx + 1}"
        alert_desc = f"Alert when {alert_types[i % 6]} exceeds threshold for service {svc_idx + 1}"
        if svc_item:
            alert_title = f"Alert: {alert_types[i % 6].upper()} threshold exceeded - {svc_item['title']}"
            alert_desc = f"Alert when {alert_types[i % 6]} exceeds threshold for {svc_item['title']}"

        alert_id = gen.add_item(
            "alert",
            alert_title,
            alert_desc,
            "active",
            1,
            {"threshold": 80 + i % 20, "severity": ["critical", "warning", "info"][i % 3]},
            ["alert", "monitoring"],
        )
        alerts.append(alert_id)
        gen.add_link(alert_id, services[svc_idx], "monitors", {})

    runbooks = []
    for i in range(40):
        runbook_id = gen.add_item(
            "runbook",
            f"Runbook: {['Service Degradation', 'Database Failover', 'Incident Response', 'Rollback'][i % 4]} Procedure",
            f"Standard operating procedure for {['service degradation', 'database failover', 'incident response', 'deployment rollback'][i % 4]}",
            "active",
            1,
            {"steps": 8 + i % 5, "estimated_time": "15-30min"},
            ["runbook", "operations"],
        )
        runbooks.append(runbook_id)

    # CI/CD Pipelines (30)
    pipelines = []
    for i in range(30):
        # Get the service item dict
        svc_idx = i % len(services)
        svc_item = None
        for item in gen.items:
            if item["id"] == services[svc_idx]:
                svc_item = item
                break

        pipeline_title = f"Pipeline: {['Build', 'Test', 'Deploy', 'Release'][i % 4]} - Service {svc_idx + 1}"
        pipeline_desc = f"CI/CD pipeline for {['build', 'test', 'deploy', 'release'][i % 4]} of service {svc_idx + 1}"
        if svc_item:
            pipeline_title = f"Pipeline: {['Build', 'Test', 'Deploy', 'Release'][i % 4]} - {svc_item['title']}"
            pipeline_desc = f"CI/CD pipeline for {['build', 'test', 'deploy', 'release'][i % 4]} of {svc_item['title']}"

        pipeline_id = gen.add_item(
            "ci_cd_pipeline",
            pipeline_title,
            pipeline_desc,
            "active",
            2,
            {"tool": "GitHub Actions", "duration_minutes": 5 + i % 10},
            ["cicd", "automation"],
        )
        pipelines.append(pipeline_id)
        gen.add_link(pipeline_id, services[svc_idx], "builds", {})

    # Infrastructure as Code (30)
    iac = []
    for i in range(30):
        # Get the infra item dict
        infra_item = None
        for item in gen.items:
            if item["id"] == infra[i]:
                infra_item = item
                break

        iac_title = (
            f"IaC: {['Kubernetes Manifests', 'Terraform', 'Helm Charts', 'Docker Compose'][i % 4]} - Infra {i + 1}"
        )
        iac_desc = f"Infrastructure as code definition for infrastructure component {i + 1}"
        if infra_item:
            iac_title = f"IaC: {['Kubernetes Manifests', 'Terraform', 'Helm Charts', 'Docker Compose'][i % 4]} - {infra_item['title']}"
            iac_desc = f"Infrastructure as code definition for {infra_item['title']}"

        iac_id = gen.add_item(
            "infrastructure_as_code",
            iac_title,
            iac_desc,
            "active",
            2,
            {"tool": ["kubectl", "terraform", "helm", "docker"][i % 4]},
            ["iac", "infrastructure"],
        )
        iac.append(iac_id)
        gen.add_link(iac_id, infra[i], "defines", {})

    # ==========================================================================
    # DOCUMENTATION LAYER (100 items)
    # ==========================================================================

    # Architecture Decision Records (30)
    adrs = []
    adr_topics = [
        "Microservices Architecture",
        "Event-Driven Communication",
        "PostgreSQL Database",
        "Redis Caching Strategy",
        "NATS Message Broker",
        "Kubernetes Orchestration",
        "RESTful API Design",
        "GraphQL vs REST",
        "Authentication with JWT",
        "Payment Provider Selection",
        "Geospatial Indexing",
        "Real-time Location Updates",
    ]
    for i in range(30):
        adr_id = gen.add_item(
            "adr",
            f"ADR-{i + 1:03d}: {adr_topics[i % len(adr_topics)]} Decision - {i // len(adr_topics) + 1}",
            f"Architecture decision record documenting {adr_topics[i % len(adr_topics)]} choice and rationale",
            "active",
            2,
            {"number": i + 1, "status": "accepted", "date": "2026-01-15"},
            ["adr", "architecture"],
        )
        adrs.append(adr_id)

    # API Documentation (30)
    api_docs = []
    for i, ep_id in enumerate(endpoints[:30]):
        # Get the endpoint item dict
        ep_item = None
        for item in gen.items:
            if item["id"] == ep_id:
                ep_item = item
                break

        doc_title = f"API Docs: Endpoint {i + 1} Specification"
        doc_desc = f"OpenAPI/Swagger documentation for endpoint {i + 1} with examples"
        if ep_item:
            doc_title = f"API Docs: {ep_item['title']} Specification"
            doc_desc = f"OpenAPI/Swagger documentation for {ep_item['title']} endpoint with examples"

        doc_id = gen.add_item(
            "api_documentation",
            doc_title,
            doc_desc,
            "active",
            2,
            {"format": "OpenAPI 3.0", "examples": True, "schemas": True},
            ["documentation", "api"],
        )
        api_docs.append(doc_id)
        gen.add_link(doc_id, ep_id, "documents", {})

    # User Guides (20)
    guides = []
    guide_topics = [
        "Getting Started as Rider",
        "Getting Started as Driver",
        "Request Your First Ride",
        "Become a Driver",
        "Schedule a Ride",
        "Add Payment Method",
        "Rate Your Experience",
        "Corporate Account Setup",
        "Understanding Surge Pricing",
        "Safety Features Guide",
    ]
    for i in range(20):
        guide_id = gen.add_item(
            "user_guide",
            f"User Guide: {guide_topics[i % len(guide_topics)]} - v{i // len(guide_topics) + 1}",
            f"Step-by-step user guide for {guide_topics[i % len(guide_topics)]}",
            "active",
            2,
            {"version": i // len(guide_topics) + 1, "screenshots": 5 + i % 10},
            ["documentation", "user-guide"],
        )
        guides.append(guide_id)

    # Technical Specifications (20)
    specs = []
    for i in range(20):
        # Get the service item dict
        svc_item = None
        for item in gen.items:
            if item["id"] == services[i]:
                svc_item = item
                break

        spec_title = f"Technical Spec: Service {i + 1} Implementation Details"
        spec_desc = f"Detailed technical specification for service {i + 1} architecture and implementation"
        if svc_item:
            spec_title = f"Technical Spec: {svc_item['title']} Implementation Details"
            spec_desc = f"Detailed technical specification for {svc_item['title']} architecture and implementation"

        spec_id = gen.add_item(
            "technical_spec",
            spec_title,
            spec_desc,
            "active",
            2,
            {"sections": ["overview", "architecture", "api", "data_model", "deployment"]},
            ["documentation", "technical"],
        )
        specs.append(spec_id)
        gen.add_link(spec_id, services[i], "documents", {})

    # ==========================================================================
    # CROSS-LAYER LINKS (Additional 3000+ links)
    # ==========================================================================

    len(gen.links)

    # Link features to requirements/objectives
    for feat_id in features[:50]:
        for obj_id in objectives[:3]:
            gen.add_link(feat_id, obj_id, "supports", {"importance": "high"})

    # Link code to features
    for i, code_id in enumerate((py_files + ts_files + go_files)[:200]):
        feat_idx = i % len(features)
        gen.add_link(code_id, features[feat_idx], "implements", {})

    # Link tests to code
    for i, test_id in enumerate(unit_tests[:150]):
        code_idx = i % len(py_files + go_files)
        gen.add_link(test_id, (py_files + go_files)[code_idx], "tests", {})

    # Link APIs to services (endpoints depend on other services)
    for i, ep_id in enumerate(endpoints[:50]):
        # Link to 2-3 random other services besides parent
        for j in range(2):
            svc_idx = (i + j + 1) % len(services)
            gen.add_link(ep_id, services[svc_idx], "depends_on", {})

    # Link infrastructure to services
    for svc_id in services:
        for infra_id in infra[:10]:
            gen.add_link(svc_id, infra_id, "uses", {})

    # Link compliance to features
    for comp_id in compliance:
        for feat_id in features[:20]:
            gen.add_link(feat_id, comp_id, "complies_with", {})

    # Link dashboards to services
    for dash_id in dashboards:
        for svc_id in services[:5]:
            gen.add_link(dash_id, svc_id, "monitors", {})

    # Link CI/CD to code
    for pipeline_id in pipelines:
        for code_id in (py_files + go_files)[:20]:
            gen.add_link(pipeline_id, code_id, "builds", {})

    # Link ADRs to services
    for adr_id in adrs:
        for svc_id in services[:3]:
            gen.add_link(adr_id, svc_id, "affects", {})

    # Additional cross-links for comprehensive traceability
    for i in range(min(len(stories), 100)):
        for j in range(0, min(len(tasks), 200), 10):
            gen.add_link(stories[i], tasks[j], "related_to", {})

    for i in range(min(len(features), 50)):
        for j in range(0, min(len(use_cases), 50), 5):
            gen.add_link(features[i], use_cases[j], "validates", {})

    # ==========================================================================
    # GENERATE SQL AND WRITE TO FILE
    # ==========================================================================
    sql_content = gen.generate_sql()

    out_path = Path(__file__).resolve().parent / "enhance_swiftride_full.sql"
    with out_path.open("w") as f:
        f.write(sql_content)

    type_counts = {}
    for item in gen.items:
        itype = item["type"]
        type_counts[itype] = type_counts.get(itype, 0) + 1

    for itype, _count in sorted(type_counts.items(), key=lambda x: -x[1]):
        pass


if __name__ == "__main__":
    generate_swiftride_data()
