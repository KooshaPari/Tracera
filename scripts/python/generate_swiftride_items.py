#!/usr/bin/env python3
"""Generate comprehensive Product Layer items for SwiftRide.

Targets: 50+ items per type with deep hierarchies and extensive linking.
"""

import asyncio
import sys
import uuid
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

# Item storage for linking
items_db: dict[str, list[str]] = {
    "initiative": [],
    "epic": [],
    "capability": [],
    "feature": [],
    "user_story": [],
    "use_case": [],
    "acceptance_criteria": [],
    "task": [],
}


# SwiftRide Product Data
INITIATIVES = [
    {
        "title": "International Expansion",
        "description": "Expand SwiftRide operations to 50+ new international markets across Europe, Asia, and Latin America",
        "priority": 10,
        "business_value": "Capture $5B+ TAM in new markets, establish global brand presence",
    },
    {
        "title": "Electric Vehicle Fleet Transition",
        "description": "Convert 80% of partner vehicle fleet to electric vehicles by 2026",
        "priority": 8,
        "business_value": "Reduce carbon footprint by 60%, lower operational costs, meet sustainability commitments",
    },
    {
        "title": "Autonomous Vehicles Integration",
        "description": "Deploy autonomous vehicle technology in controlled markets with regulatory approval",
        "priority": 8,
        "business_value": "Reduce per-ride costs by 40%, improve safety, lead industry innovation",
    },
    {
        "title": "Enterprise Business Solutions",
        "description": "Build comprehensive B2B platform for corporate transportation management",
        "priority": 8,
        "business_value": "Capture $2B enterprise market, increase average ride value by 3x",
    },
    {
        "title": "Multi-Modal Transportation Platform",
        "description": "Integrate bikes, scooters, public transit, and car-sharing into unified mobility platform",
        "priority": 5,
        "business_value": "Increase user engagement 2x, become one-stop mobility solution",
    },
    {
        "title": "Premium Tier Services",
        "description": "Launch luxury and executive ride tiers with concierge services",
        "priority": 5,
        "business_value": "Increase revenue per ride 5-10x, capture high-value customer segment",
    },
    {
        "title": "Driver Financial Services",
        "description": "Provide banking, lending, and insurance services tailored for gig economy drivers",
        "priority": 5,
        "business_value": "Improve driver retention 40%, create new revenue streams",
    },
    {
        "title": "AI-Powered Operations",
        "description": "Deploy ML/AI across matching, pricing, routing, fraud detection, and customer service",
        "priority": 10,
        "business_value": "Reduce operational costs 30%, improve margins, enhance user experience",
    },
    {
        "title": "Safety & Trust Platform",
        "description": "Build industry-leading safety features including real-time monitoring, emergency response, insurance",
        "priority": 10,
        "business_value": "Increase user trust, reduce incident costs, regulatory compliance",
    },
    {
        "title": "Accessibility & Inclusion",
        "description": "Make SwiftRide fully accessible to riders and drivers with disabilities",
        "priority": 8,
        "business_value": "Expand addressable market 15%, meet ADA compliance, social impact",
    },
]

# Add 40 more initiatives
# Priority mapping: critical=10, high=8, medium=5, low=3
ADDITIONAL_INITIATIVES = [
    ("Subscription Services", "Launch monthly subscription plans with unlimited rides and premium benefits", 8),
    ("Freight & Delivery", "Expand into same-day package delivery and freight services", 5),
    ("Healthcare Transportation", "Partner with healthcare providers for non-emergency medical transportation", 5),
    ("Smart City Integration", "Integrate with municipal traffic systems and smart city infrastructure", 5),
    ("Carbon Neutral Operations", "Achieve carbon neutrality across all operations by 2025", 8),
    ("Driver Education Platform", "Comprehensive training and certification programs for drivers", 5),
    ("Rewards & Loyalty Program", "Multi-tier loyalty program with points, benefits, and partnerships", 8),
    ("Real Estate Optimization", "Optimize pickup/dropoff zones, build waiting areas in high-traffic locations", 3),
    ("Insurance Innovation", "Launch proprietary insurance products for riders and drivers", 5),
    ("Data Monetization", "Create anonymized data products for urban planning and traffic analytics", 5),
    ("API Platform", "Public API for third-party integrations and white-label solutions", 5),
    ("Voice & Conversational UI", "Voice-first booking and support through smart speakers and assistants", 3),
    ("Blockchain & Web3", "Explore decentralized ride-sharing and crypto payment options", 3),
    ("Airport Partnerships", "Exclusive partnerships with major airports for designated pickup zones", 5),
    ("Event Transportation", "Specialized services for concerts, sports, conferences, and festivals", 5),
    ("Pet-Friendly Rides", "Dedicated service for riders traveling with pets", 3),
    ("Senior Mobility", "Specialized service with trained drivers for elderly passengers", 5),
    ("Kid Transportation", "Safe transportation for unaccompanied minors with parental monitoring", 5),
    ("Campus Solutions", "University and corporate campus transportation systems", 5),
    ("Rural Expansion", "Extend service to underserved rural and suburban markets", 5),
    ("Microtransit", "Shared van services for high-density routes", 5),
    ("Night Safety Program", "Enhanced safety features for late-night rides", 8),
    ("Driver Health & Wellness", "Health insurance, mental health support, fitness programs for drivers", 5),
    ("Green Routing", "Eco-friendly route optimization to minimize emissions", 3),
    ("Community Rides", "Subsidized transportation for low-income communities", 3),
    ("Dynamic Pricing 2.0", "Next-gen pricing with fairness algorithms and price guarantees", 8),
    ("Vehicle Marketplace", "Platform for drivers to buy/lease/finance vehicles", 5),
    ("Corporate Shuttle", "Managed shuttle services for businesses", 5),
    ("Tourism & Sightseeing", "Guided tour and sightseeing ride options", 3),
    ("Luggage Assistance", "Premium service with luggage handling and airport concierge", 3),
    ("Ride Pooling 2.0", "Advanced carpooling with AI-optimized matching", 5),
    ("Driver Community Platform", "Social network and support system for drivers", 3),
    ("Integrated Payments", "Support for 50+ payment methods including BNPL, crypto, local options", 8),
    ("Predictive Maintenance", "AI-powered vehicle maintenance prediction for partner fleet", 5),
    ("Weather Optimization", "Weather-aware routing, pricing, and driver safety alerts", 5),
    ("Referral Program 2.0", "Advanced referral system with multi-level rewards", 5),
    ("Business Analytics", "Self-serve analytics platform for drivers and fleet managers", 5),
    ("Partner Integrations", "Integrations with hotels, airlines, restaurants, events", 5),
    ("In-Ride Entertainment", "Streaming, gaming, and productivity features during rides", 3),
    ("Zero-Emissions Zones", "EV-only services in city centers and low-emission zones", 5),
    ("Autonomous Fleet Management", "Platform for managing autonomous vehicle operations", 8),
    ("Driver Retention Program", "Comprehensive retention strategies and benefits", 8),
    ("Regional Customization", "Localized features, payments, and services per market", 8),
    ("Quality Assurance", "Automated quality monitoring and driver performance management", 8),
    ("Incident Response", "Real-time incident detection and emergency response system", 10),
    ("Regulatory Compliance", "Automated compliance monitoring across 100+ jurisdictions", 10),
    ("Brand Partnerships", "Co-branded experiences with major consumer brands", 3),
    ("Virtual Queuing", "Digital queue management for airports, events, venues", 3),
    ("Driver Gamification", "Achievements, badges, and competitions to boost engagement", 3),
    ("Sustainable Cities", "Partner with cities on congestion, emissions, and mobility goals", 5),
]

for title, desc, priority in ADDITIONAL_INITIATIVES:
    INITIATIVES.append({
        "title": title,
        "description": desc,
        "priority": priority,
        "business_value": "Strategic initiative to enhance SwiftRide market position",
    })


EPICS = [
    # Core Platform Epics (Initiative 1-3)
    {
        "title": "Driver Onboarding Platform",
        "initiative_idx": 0,
        "description": "Complete digital onboarding system for driver acquisition",
        "duration_months": 6,
    },
    {
        "title": "Real-time Matching Engine",
        "initiative_idx": 7,
        "description": "ML-powered rider-driver matching with <5s average match time",
        "duration_months": 5,
    },
    {
        "title": "Payment Processing v2.0",
        "initiative_idx": 7,
        "description": "Next-generation payment platform with fraud detection",
        "duration_months": 4,
    },
    {
        "title": "Safety & Trust Platform",
        "initiative_idx": 8,
        "description": "Comprehensive safety features including real-time monitoring",
        "duration_months": 6,
    },
    {
        "title": "International Localization",
        "initiative_idx": 0,
        "description": "Multi-language, multi-currency, multi-region support",
        "duration_months": 5,
    },
    {
        "title": "EV Fleet Integration",
        "initiative_idx": 1,
        "description": "Electric vehicle onboarding, charging infrastructure integration",
        "duration_months": 4,
    },
    {
        "title": "Autonomous Vehicle SDK",
        "initiative_idx": 2,
        "description": "Software development kit for AV integration",
        "duration_months": 6,
    },
    {
        "title": "Enterprise Portal",
        "initiative_idx": 3,
        "description": "B2B platform for corporate account management",
        "duration_months": 5,
    },
    {
        "title": "Multi-Modal Integration",
        "initiative_idx": 4,
        "description": "Integration with bikes, scooters, public transit",
        "duration_months": 4,
    },
    {
        "title": "Premium Concierge",
        "initiative_idx": 5,
        "description": "White-glove service for luxury tier",
        "duration_months": 3,
    },
]

# Add 50+ more epics
EPIC_TEMPLATES = [
    ("Background Check Automation", "Automated verification of driver credentials and criminal background"),
    ("Real-time ETA Calculation", "ML-based arrival time prediction with 95% accuracy"),
    ("Surge Pricing Engine", "Dynamic pricing based on supply-demand with fairness controls"),
    ("Multi-Stop Routing", "Optimized routing for rides with multiple waypoints"),
    ("Driver Rating System", "Comprehensive rating and feedback system"),
    ("Rider Safety Score", "AI-based safety risk assessment for rides"),
    ("In-App Support Chat", "Real-time customer support with AI and human agents"),
    ("Trip Sharing", "Carpooling with optimized passenger matching"),
    ("Scheduled Rides", "Advance booking with guaranteed pickup"),
    ("Accessibility Features", "Wheelchair accessible vehicles and assistance features"),
    ("Lost & Found System", "Automated lost item reporting and recovery"),
    ("Driver Earnings Dashboard", "Real-time earnings tracking and analytics"),
    ("Referral Platform", "Viral referral system for riders and drivers"),
    ("Promo Code Engine", "Flexible promotion and discount management"),
    ("Corporate Billing", "Monthly invoicing for business accounts"),
    ("Driver Training Portal", "Online courses and certification"),
    ("Vehicle Inspection", "Digital vehicle safety inspection workflow"),
    ("Insurance Management", "Automated insurance verification and claims"),
    ("Geofencing Platform", "Service area and zone management"),
    ("Heat Maps & Demand Prediction", "Predictive analytics for driver positioning"),
    ("Driver Incentive Programs", "Bonus and reward systems"),
    ("Ride Receipt System", "Automated receipt generation and delivery"),
    ("Favorite Drivers", "Ability to request preferred drivers"),
    ("Ride History", "Complete trip history with search and filters"),
    ("Emergency SOS", "One-tap emergency assistance"),
    ("Live Location Sharing", "Share ride progress with contacts"),
    ("Quiet Mode", "Rider preference for silent rides"),
    ("Music Control", "In-ride music and temperature preferences"),
    ("Carbon Offsetting", "Automatic carbon offset purchases"),
    ("Subscription Management", "Monthly plan enrollment and management"),
    ("Airport Queue", "Virtual queue for airport pickups"),
    ("Event Integration", "Partner with Eventbrite, Ticketmaster"),
    ("Hotel Partnerships", "Direct booking from hotel concierge"),
    ("Flight Tracking", "Automatic pickup time adjustment for delays"),
    ("Weather Alerts", "Safety alerts and route changes"),
    ("Vehicle Preferences", "Ride type and vehicle selection"),
    ("Split Fare", "Multiple payment sources for one ride"),
    ("Tips & Gratuity", "In-app tipping system"),
    ("Driver Leaderboards", "Gamification and competitions"),
    ("City Guides", "Local recommendations integration"),
    ("Business Profile", "Separate personal and business rides"),
    ("Family Accounts", "Linked accounts for family members"),
    ("Student Verification", "Student discount eligibility"),
    ("Senior Support", "Assistance features for elderly"),
    ("Language Matching", "Match riders with drivers speaking preferred language"),
    ("Pet Transport", "Pet-friendly vehicle matching"),
    ("Luggage Capacity", "Vehicle selection based on luggage"),
    ("Child Seats", "Car seat availability and booking"),
    ("Long Distance", "Inter-city ride booking"),
    ("Route Optimization", "AI-powered fastest route selection"),
]

for idx, (title, desc) in enumerate(EPIC_TEMPLATES):
    initiative_idx = idx % len(INITIATIVES)
    EPICS.append({
        "title": title,
        "initiative_idx": initiative_idx,
        "description": desc,
        "duration_months": 3 + (idx % 4),
    })


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


async def create_link(session: AsyncSession, source_id: str, target_id: str, link_type: str = "implements") -> None:
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


async def generate_items() -> None:
    """Generate all items with deep hierarchies."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 1. Create Initiatives (50 items)
        for idx, init in enumerate(INITIATIVES[:50]):
            await create_item(
                session,
                "initiative",
                str(init["title"]),
                str(init["description"]),
                priority=int(init["priority"]) if isinstance(init.get("priority"), (int, float)) else 5,
            )
            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 2. Create Epics (60 items)
        for idx, epic in enumerate(EPICS[:60]):
            epic_id = await create_item(
                session,
                "epic",
                str(epic["title"]),
                str(epic["description"]),
                priority=8 if idx < 20 else 5,
            )

            # Link to initiative
            init_idx = int(epic["initiative_idx"]) if isinstance(epic.get("initiative_idx"), (int, float)) else idx
            initiative_id = items_db["initiative"][init_idx % len(items_db["initiative"])]
            await create_link(session, epic_id, initiative_id, "implements")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 3. Create Capabilities (50 items)
        capabilities = [
            "Real-time GPS Tracking",
            "Payment Processing",
            "Identity Verification",
            "Route Optimization",
            "Demand Forecasting",
            "Fraud Detection",
            "Dynamic Pricing",
            "Multi-language Support",
            "Push Notifications",
            "In-App Messaging",
            "Rating & Reviews",
            "Surge Management",
            "Driver Matching",
            "ETA Prediction",
            "Location Services",
            "Trip Recording",
            "Receipt Generation",
            "Fare Calculation",
            "Promo Management",
            "Referral Tracking",
            "Analytics Pipeline",
            "Real-time Data Sync",
            "Offline Mode",
            "Background Location",
            "Emergency Services",
            "Customer Support",
            "Driver Dashboard",
            "Rider Dashboard",
            "Admin Console",
            "Reporting System",
            "Audit Logging",
            "Compliance Monitoring",
            "API Gateway",
            "Rate Limiting",
            "Caching Layer",
            "CDN Integration",
            "Image Processing",
            "Video Streaming",
            "Document Scanner",
            "OCR Processing",
            "Voice Commands",
            "Biometric Auth",
            "Two-Factor Auth",
            "Session Management",
            "Token Refresh",
            "Data Encryption",
            "TLS/SSL",
            "DDoS Protection",
            "Load Balancing",
            "Auto-scaling",
        ]

        for idx, cap in enumerate(capabilities[:50]):
            cap_id = await create_item(
                session,
                "capability",
                cap,
                f"System capability for {cap.lower()}",
                priority=8 if idx < 15 else 5,
            )

            # Link to 2-3 epics
            for _ in range(2 + (idx % 2)):
                epic_id = items_db["epic"][(idx * 3) % len(items_db["epic"])]
                await create_link(session, cap_id, epic_id, "supports")

            if (idx + 1) % 10 == 0:
                pass

        await session.commit()

        # 4. Create Features (100 items)
        feature_counter = 0

        for epic_idx, epic_id in enumerate(items_db["epic"][:30]):  # First 30 epics
            # Each epic gets 3-4 features
            num_features = 3 + (epic_idx % 2)

            for f_idx in range(num_features):
                if feature_counter >= 100:
                    break

                feature_titles = [
                    "Background check verification API integration",
                    "Automated document upload and validation",
                    "Real-time status dashboard",
                    "Email and SMS notifications",
                    "Mobile app workflow",
                    "Admin approval interface",
                    "Compliance reporting",
                    "Audit trail logging",
                ]

                feature_id = await create_item(
                    session,
                    "feature",
                    feature_titles[f_idx % len(feature_titles)],
                    "Feature implementation for enhanced system capability",
                    priority=8 if feature_counter < 30 else 5,
                )

                # Link to epic
                await create_link(session, feature_id, epic_id, "implements")

                # Link to 1-2 capabilities
                for _ in range(1 + (feature_counter % 2)):
                    cap_id = items_db["capability"][feature_counter % len(items_db["capability"])]
                    await create_link(session, feature_id, cap_id, "refines")

                feature_counter += 1

                if feature_counter % 20 == 0:
                    pass

            if feature_counter >= 100:
                break

        await session.commit()

        # 5. Create User Stories (200 items)

        user_story_templates = [
            ("rider", "book a ride quickly", "I can get transportation when I need it"),
            ("rider", "see driver location in real-time", "I know when my ride will arrive"),
            ("rider", "rate my driver", "I can provide feedback on my experience"),
            ("rider", "schedule rides in advance", "I can plan my transportation ahead of time"),
            ("rider", "split fare with friends", "I can share ride costs"),
            ("driver", "see ride requests nearby", "I can accept profitable rides"),
            ("driver", "view my earnings daily", "I can track my income"),
            ("driver", "navigate to pickup location", "I can find riders efficiently"),
            ("driver", "receive tips", "I can earn additional income"),
            ("driver", "set my availability", "I can control my work schedule"),
            ("admin", "monitor system health", "I can ensure platform reliability"),
            ("admin", "review flagged rides", "I can maintain safety standards"),
            ("admin", "generate reports", "I can analyze business metrics"),
            ("support agent", "access ride details", "I can assist customers effectively"),
            ("support agent", "refund transactions", "I can resolve payment issues"),
        ]

        story_counter = 0
        for feature_id in items_db["feature"]:
            # Each feature gets 2 user stories
            for _ in range(2):
                if story_counter >= 200:
                    break

                persona, action, benefit = user_story_templates[story_counter % len(user_story_templates)]

                story_id = await create_item(
                    session,
                    "user_story",
                    f"As a {persona}, I want to {action}",
                    f"As a {persona}, I want to {action}, so that {benefit}",
                    priority=8 if story_counter < 50 else 5,
                )

                # Link to feature
                await create_link(session, story_id, feature_id, "implements")

                story_counter += 1

                if story_counter % 40 == 0:
                    pass

            if story_counter >= 200:
                break

        await session.commit()

        # 6. Create Use Cases (80 items)

        use_case_templates = [
            ("Successful Ride Booking", "Rider books, driver accepts, ride completes successfully"),
            ("Driver Cancellation", "Driver cancels ride, rider is rematched"),
            ("Payment Failure", "Payment fails, retry logic, fallback payment method"),
            ("GPS Signal Loss", "Handle location unavailability gracefully"),
            ("Surge Pricing Activation", "High demand triggers surge, riders notified"),
            ("Multi-Stop Ride", "Rider adds waypoints, route recalculated"),
            ("Lost Item Report", "Rider reports lost item, driver notified"),
            ("Safety Incident", "Emergency SOS triggered, authorities contacted"),
            ("Promotional Code", "Rider applies promo, discount calculated"),
            ("Driver Rating", "Rider rates driver, score updated"),
        ]

        for idx in range(80):
            title, desc = use_case_templates[idx % len(use_case_templates)]

            use_case_id = await create_item(
                session,
                "use_case",
                f"{title} - Scenario {idx + 1}",
                desc,
                priority=8 if idx < 20 else 5,
            )

            # Link to 1-2 features
            for _ in range(1 + (idx % 2)):
                feature_id = items_db["feature"][idx % len(items_db["feature"])]
                await create_link(session, use_case_id, feature_id, "validates")

            if (idx + 1) % 20 == 0:
                pass

        await session.commit()

        # 7. Create Acceptance Criteria (150 items)

        criteria_templates = [
            "System responds within 2 seconds",
            "Error messages are user-friendly",
            "Data is validated before submission",
            "Success confirmation is displayed",
            "Analytics event is logged",
            "Email notification is sent",
            "SMS notification is sent",
            "Push notification is sent",
            "Database transaction is atomic",
            "API returns 200 status code",
            "UI is responsive on mobile",
            "Accessibility standards are met",
            "Security headers are present",
            "Rate limiting is enforced",
            "Caching improves performance",
        ]

        for idx, story_id in enumerate(items_db["user_story"][:150]):
            criteria_text = criteria_templates[idx % len(criteria_templates)]

            ac_id = await create_item(
                session,
                "acceptance_criteria",
                f"AC: {criteria_text}",
                f"Acceptance criteria ensuring {criteria_text.lower()}",
                priority=8,
            )

            # Link to user story
            await create_link(session, ac_id, story_id, "validates")

            if (idx + 1) % 30 == 0:
                pass

        await session.commit()

        # 8. Create Tasks (300+ items) - 2-3 tasks per user story

        task_templates = [
            "Design database schema",
            "Implement API endpoint",
            "Create frontend component",
            "Write unit tests",
            "Write integration tests",
            "Update documentation",
            "Code review",
            "Deploy to staging",
            "QA testing",
            "Deploy to production",
        ]

        task_counter = 0
        for story_idx, story_id in enumerate(items_db["user_story"]):
            # Each story gets 2-3 tasks
            num_tasks = 2 + (story_idx % 2)

            for _t_idx in range(num_tasks):
                if task_counter >= 400:
                    break

                task_title = task_templates[task_counter % len(task_templates)]

                task_id = await create_item(
                    session,
                    "task",
                    f"{task_title} for story {story_idx + 1}",
                    f"Implementation task: {task_title.lower()}",
                    priority=5,
                    status="todo",
                )

                # Link to user story
                await create_link(session, task_id, story_id, "implements")

                # Store task ID
                items_db["task"].append(task_id)
                task_counter += 1

                if task_counter % 50 == 0:
                    pass

        await session.commit()

        # Final summary

        # Verify project
        result = await session.execute(
            text("SELECT COUNT(*) FROM items WHERE project_id = :project_id"),
            {"project_id": PROJECT_ID},
        )
        result.scalar()

        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(generate_items())
