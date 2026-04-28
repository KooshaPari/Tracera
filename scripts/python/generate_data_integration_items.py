#!/usr/bin/env python3
"""Generate comprehensive Data & Integration items for SwiftRide project.

Creates 440+ items across 7 types:
- database_schema (60 items)
- external_api (80 items)
- webhook (70 items)
- data_pipeline (60 items)
- cache_strategy (50 items)
- queue_definition (70 items)
- stream_processor (50 items)
"""

import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Project configuration
PROJECT_ID = "40b0a8d1-af95-4b97-a52c-9b891b6ea3db"
PROJECT_DIR = Path(__file__).parent.parent / "samples" / "DEMO_PROJECT" / ".trace"


def generate_item_frontmatter(
    external_id: str,
    item_type: str,
    priority: str = "medium",
    status: str = "todo",
    links: list[dict[str, str]] | None = None,
    parent: str | None = None,
    owner: str | None = None,
) -> dict[str, Any]:
    """Generate YAML frontmatter for an item."""
    now = datetime.now(UTC).isoformat()
    return {
        "created": now,
        "external_id": external_id,
        "id": str(uuid.uuid4()),
        "links": links or [],
        "owner": owner,
        "parent": parent,
        "priority": priority,
        "status": status,
        "type": item_type,
        "updated": now,
        "version": 1,
    }


def create_item_file(
    directory: str,
    external_id: str,
    item_type: str,
    title: str,
    description: str,
    priority: str = "medium",
    status: str = "todo",
    links: list[dict[str, str]] | None = None,
    metadata: dict[str, Any] | None = None,
) -> Path:
    """Create an item markdown file with frontmatter."""
    # Create directory if it doesn't exist
    item_dir = PROJECT_DIR / directory
    item_dir.mkdir(parents=True, exist_ok=True)

    # Generate frontmatter
    frontmatter = generate_item_frontmatter(
        external_id=external_id,
        item_type=item_type,
        priority=priority,
        status=status,
        links=links,
    )

    # Build content
    content = "---\n"
    content += yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    content += "---\n\n"
    content += f"# {title}\n\n"
    content += f"## Description\n\n{description}\n\n"

    # Add metadata section if provided
    if metadata:
        content += "## Metadata\n\n"
        for key, value in metadata.items():
            if isinstance(value, list):
                content += f"**{key}:**\n"
                for item in value:
                    content += f"- {item}\n"
            elif isinstance(value, dict):
                content += f"**{key}:**\n```json\n{yaml.dump(value, default_flow_style=False)}```\n"
            else:
                content += f"**{key}:** {value}\n\n"

    # Write file
    filepath = item_dir / f"{external_id}.md"
    filepath.write_text(content)
    return filepath


# ============================================================================
# DATABASE SCHEMA DEFINITIONS (60 items)
# ============================================================================


def generate_database_schemas() -> list[Path]:
    """Generate 60 database schema items."""
    schemas = []
    counter = 1

    # Core User & Auth Tables (10)
    user_schemas = [
        (
            "users",
            "Core user account table. Stores authentication details, profile info, created timestamps.",
            {
                "columns": [
                    "id",
                    "email",
                    "password_hash",
                    "phone",
                    "first_name",
                    "last_name",
                    "created_at",
                    "updated_at",
                ],
                "indexes": ["email_idx", "phone_idx"],
            },
        ),
        (
            "user_profiles",
            "Extended user profile data. Stores avatar, bio, preferences, language settings.",
            {
                "columns": ["user_id", "avatar_url", "bio", "date_of_birth", "language", "timezone"],
                "indexes": ["user_id_idx"],
            },
        ),
        (
            "user_sessions",
            "Active user sessions. Tracks JWT tokens, device info, expiry times.",
            {
                "columns": ["id", "user_id", "token_hash", "device_id", "ip_address", "expires_at", "created_at"],
                "indexes": ["user_id_idx", "token_hash_idx"],
            },
        ),
        (
            "user_devices",
            "Registered user devices. Stores device tokens for push notifications.",
            {
                "columns": ["id", "user_id", "device_token", "platform", "app_version", "last_active", "created_at"],
                "indexes": ["user_id_idx", "device_token_idx"],
            },
        ),
        (
            "user_settings",
            "User preferences and settings. JSON storage for flexible configuration.",
            {
                "columns": ["user_id", "notification_prefs", "privacy_settings", "payment_defaults", "updated_at"],
                "indexes": ["user_id_idx"],
            },
        ),
        (
            "user_verification",
            "Identity verification records. KYC/background check status.",
            {
                "columns": ["id", "user_id", "verification_type", "status", "provider", "verified_at", "expires_at"],
                "indexes": ["user_id_idx", "status_idx"],
            },
        ),
        (
            "user_roles",
            "User role assignments. Supports rider, driver, admin roles.",
            {"columns": ["id", "user_id", "role", "granted_at", "granted_by"], "indexes": ["user_id_idx", "role_idx"]},
        ),
        (
            "password_resets",
            "Password reset tokens. Time-limited recovery tokens.",
            {
                "columns": ["id", "user_id", "token_hash", "expires_at", "used_at", "created_at"],
                "indexes": ["user_id_idx", "token_hash_idx"],
            },
        ),
        (
            "oauth_connections",
            "Third-party OAuth connections. Google, Apple, Facebook auth.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "provider",
                    "provider_user_id",
                    "access_token_hash",
                    "refresh_token_hash",
                    "connected_at",
                ],
                "indexes": ["user_id_idx", "provider_idx"],
            },
        ),
        (
            "user_audit_log",
            "User action audit trail. Tracks login, profile changes, security events.",
            {
                "columns": ["id", "user_id", "action", "ip_address", "user_agent", "metadata", "created_at"],
                "indexes": ["user_id_idx", "action_idx", "created_at_idx"],
            },
        ),
    ]

    for name, desc, meta in user_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="critical" if counter <= 3 else "high",
                metadata=meta,
            ),
        )
        counter += 1

    # Driver Tables (8)
    driver_schemas = [
        (
            "drivers",
            "Driver profiles. Stores license info, vehicle details, earnings account.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "license_number",
                    "license_expiry",
                    "status",
                    "approval_date",
                    "rating",
                    "total_trips",
                ],
                "indexes": ["user_id_idx", "status_idx"],
            },
        ),
        (
            "driver_vehicles",
            "Driver vehicle records. Make, model, year, license plate, insurance.",
            {
                "columns": [
                    "id",
                    "driver_id",
                    "make",
                    "model",
                    "year",
                    "color",
                    "license_plate",
                    "insurance_expires",
                    "status",
                ],
                "indexes": ["driver_id_idx", "license_plate_idx"],
            },
        ),
        (
            "driver_documents",
            "Driver uploaded documents. License, insurance, registration scans.",
            {
                "columns": ["id", "driver_id", "document_type", "file_url", "status", "expires_at", "uploaded_at"],
                "indexes": ["driver_id_idx", "status_idx"],
            },
        ),
        (
            "driver_locations",
            "Real-time driver location tracking. GPS coordinates, heading, speed.",
            {
                "columns": ["driver_id", "latitude", "longitude", "heading", "speed", "accuracy", "timestamp"],
                "indexes": ["driver_id_idx", "timestamp_idx"],
            },
        ),
        (
            "driver_availability",
            "Driver availability schedule. Online/offline status, shift times.",
            {
                "columns": ["id", "driver_id", "status", "available_from", "available_until", "updated_at"],
                "indexes": ["driver_id_idx", "status_idx"],
            },
        ),
        (
            "driver_earnings",
            "Driver earnings records. Per-trip earnings, tips, bonuses.",
            {
                "columns": [
                    "id",
                    "driver_id",
                    "ride_id",
                    "base_fare",
                    "distance_fare",
                    "time_fare",
                    "surge_multiplier",
                    "tips",
                    "total",
                ],
                "indexes": ["driver_id_idx", "ride_id_idx"],
            },
        ),
        (
            "driver_payouts",
            "Driver payout transactions. Weekly/daily payout batches.",
            {
                "columns": [
                    "id",
                    "driver_id",
                    "period_start",
                    "period_end",
                    "total_amount",
                    "fee",
                    "net_amount",
                    "status",
                    "paid_at",
                ],
                "indexes": ["driver_id_idx", "status_idx"],
            },
        ),
        (
            "driver_ratings",
            "Individual rating records. Per-ride ratings from riders.",
            {
                "columns": ["id", "driver_id", "ride_id", "rider_id", "rating", "comment", "created_at"],
                "indexes": ["driver_id_idx", "ride_id_idx"],
            },
        ),
    ]

    for name, desc, meta in driver_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Rider Tables (5)
    rider_schemas = [
        (
            "riders",
            "Rider profiles. Preferences, favorite locations, payment methods.",
            {
                "columns": ["id", "user_id", "rating", "total_rides", "default_payment_method_id", "created_at"],
                "indexes": ["user_id_idx"],
            },
        ),
        (
            "rider_favorites",
            "Saved favorite locations. Home, work, frequent destinations.",
            {
                "columns": ["id", "rider_id", "name", "address", "latitude", "longitude", "created_at"],
                "indexes": ["rider_id_idx"],
            },
        ),
        (
            "rider_ratings",
            "Rider ratings from drivers. Per-ride feedback.",
            {
                "columns": ["id", "rider_id", "ride_id", "driver_id", "rating", "comment", "created_at"],
                "indexes": ["rider_id_idx", "ride_id_idx"],
            },
        ),
        (
            "rider_preferences",
            "Rider preferences. Quiet mode, temperature, music preferences.",
            {
                "columns": [
                    "rider_id",
                    "quiet_mode",
                    "temperature_pref",
                    "music_allowed",
                    "chat_preference",
                    "updated_at",
                ],
                "indexes": ["rider_id_idx"],
            },
        ),
        (
            "rider_emergency_contacts",
            "Emergency contact information. ICE contacts, medical info.",
            {
                "columns": ["id", "rider_id", "contact_name", "phone", "relationship", "created_at"],
                "indexes": ["rider_id_idx"],
            },
        ),
    ]

    for name, desc, meta in rider_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Ride & Trip Tables (10)
    ride_schemas = [
        (
            "rides",
            "Core ride records. Trip details, status, pricing, timestamps.",
            {
                "columns": [
                    "id",
                    "rider_id",
                    "driver_id",
                    "status",
                    "pickup_lat",
                    "pickup_lng",
                    "dropoff_lat",
                    "dropoff_lng",
                    "requested_at",
                    "accepted_at",
                    "started_at",
                    "completed_at",
                ],
                "indexes": ["rider_id_idx", "driver_id_idx", "status_idx", "created_at_idx"],
            },
        ),
        (
            "ride_routes",
            "Calculated ride routes. Polyline data, distance, estimated duration.",
            {
                "columns": ["ride_id", "route_polyline", "distance_meters", "duration_seconds", "calculated_at"],
                "indexes": ["ride_id_idx"],
            },
        ),
        (
            "ride_tracking",
            "Real-time ride tracking points. GPS breadcrumbs during trip.",
            {
                "columns": ["id", "ride_id", "latitude", "longitude", "speed", "heading", "timestamp"],
                "indexes": ["ride_id_idx", "timestamp_idx"],
            },
        ),
        (
            "ride_pricing",
            "Ride pricing breakdown. Base fare, distance, time, surge, taxes.",
            {
                "columns": [
                    "ride_id",
                    "base_fare",
                    "distance_fare",
                    "time_fare",
                    "surge_multiplier",
                    "taxes",
                    "fees",
                    "total",
                ],
                "indexes": ["ride_id_idx"],
            },
        ),
        (
            "ride_estimates",
            "Pre-ride pricing estimates. Cached estimates for common routes.",
            {
                "columns": [
                    "id",
                    "pickup_lat",
                    "pickup_lng",
                    "dropoff_lat",
                    "dropoff_lng",
                    "estimated_fare",
                    "estimated_duration",
                    "expires_at",
                ],
                "indexes": ["pickup_lat_lng_idx", "expires_at_idx"],
            },
        ),
        (
            "ride_cancellations",
            "Ride cancellation records. Reason, cancelled by, fees.",
            {
                "columns": ["id", "ride_id", "cancelled_by", "reason", "cancellation_fee", "cancelled_at"],
                "indexes": ["ride_id_idx"],
            },
        ),
        (
            "ride_schedules",
            "Scheduled future rides. Advance booking records.",
            {
                "columns": [
                    "id",
                    "rider_id",
                    "pickup_address",
                    "dropoff_address",
                    "scheduled_time",
                    "status",
                    "created_at",
                ],
                "indexes": ["rider_id_idx", "scheduled_time_idx", "status_idx"],
            },
        ),
        (
            "ride_promotions",
            "Applied ride promotions. Discount codes, referral credits.",
            {
                "columns": ["id", "ride_id", "promotion_id", "discount_amount", "applied_at"],
                "indexes": ["ride_id_idx", "promotion_id_idx"],
            },
        ),
        (
            "ride_feedback",
            "Post-ride feedback. Issues, compliments, suggestions.",
            {
                "columns": ["id", "ride_id", "user_id", "feedback_type", "message", "created_at"],
                "indexes": ["ride_id_idx", "user_id_idx"],
            },
        ),
        (
            "ride_receipts",
            "Generated ride receipts. PDF URLs, email delivery status.",
            {"columns": ["ride_id", "receipt_url", "emailed_at", "generated_at"], "indexes": ["ride_id_idx"]},
        ),
    ]

    for name, desc, meta in ride_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="critical" if name == "rides" else "high",
                metadata=meta,
            ),
        )
        counter += 1

    # Payment Tables (8)
    payment_schemas = [
        (
            "payment_methods",
            "User payment methods. Credit cards, debit, digital wallets.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "type",
                    "provider",
                    "last_four",
                    "expiry_month",
                    "expiry_year",
                    "is_default",
                    "created_at",
                ],
                "indexes": ["user_id_idx"],
            },
        ),
        (
            "transactions",
            "All payment transactions. Charges, refunds, payouts.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "ride_id",
                    "amount",
                    "currency",
                    "status",
                    "payment_method_id",
                    "provider_transaction_id",
                    "created_at",
                ],
                "indexes": ["user_id_idx", "ride_id_idx", "status_idx"],
            },
        ),
        (
            "refunds",
            "Refund records. Full/partial refunds, reason, status.",
            {
                "columns": ["id", "transaction_id", "amount", "reason", "status", "processed_at", "created_at"],
                "indexes": ["transaction_id_idx", "status_idx"],
            },
        ),
        (
            "wallet_balances",
            "User wallet balances. Credits, promotional balance.",
            {"columns": ["user_id", "balance", "currency", "updated_at"], "indexes": ["user_id_idx"]},
        ),
        (
            "wallet_transactions",
            "Wallet transaction ledger. Debits, credits, descriptions.",
            {
                "columns": ["id", "user_id", "amount", "type", "description", "balance_after", "created_at"],
                "indexes": ["user_id_idx", "created_at_idx"],
            },
        ),
        (
            "payment_disputes",
            "Payment dispute cases. Chargeback handling.",
            {
                "columns": ["id", "transaction_id", "reason", "status", "evidence_url", "resolved_at", "created_at"],
                "indexes": ["transaction_id_idx", "status_idx"],
            },
        ),
        (
            "payment_holds",
            "Pre-authorization holds. Temporary card authorizations.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "ride_id",
                    "amount",
                    "payment_method_id",
                    "captured_at",
                    "released_at",
                    "created_at",
                ],
                "indexes": ["ride_id_idx", "user_id_idx"],
            },
        ),
        (
            "payout_accounts",
            "Driver payout bank accounts. Bank details, verification status.",
            {
                "columns": [
                    "id",
                    "driver_id",
                    "account_type",
                    "account_number_hash",
                    "routing_number_hash",
                    "status",
                    "verified_at",
                ],
                "indexes": ["driver_id_idx"],
            },
        ),
    ]

    for name, desc, meta in payment_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="critical" if counter <= 35 else "high",
                metadata=meta,
            ),
        )
        counter += 1

    # Location & Geocoding Tables (5)
    location_schemas = [
        (
            "places",
            "Geocoded place cache. Common addresses, POIs, airports.",
            {
                "columns": ["id", "address", "latitude", "longitude", "place_id", "place_type", "created_at"],
                "indexes": ["place_id_idx", "lat_lng_idx"],
            },
        ),
        (
            "service_areas",
            "Active service areas. Geofenced regions, surge zones.",
            {"columns": ["id", "name", "polygon", "status", "created_at"], "indexes": ["status_idx"]},
        ),
        (
            "surge_zones",
            "Dynamic surge pricing zones. Demand multipliers by area.",
            {
                "columns": [
                    "id",
                    "service_area_id",
                    "polygon",
                    "surge_multiplier",
                    "effective_from",
                    "effective_until",
                ],
                "indexes": ["service_area_id_idx", "effective_from_idx"],
            },
        ),
        (
            "geocode_cache",
            "Reverse geocode cache. Lat/lng to address lookups.",
            {
                "columns": ["lat_lng_hash", "address", "place_name", "cached_at", "expires_at"],
                "indexes": ["lat_lng_hash_idx", "expires_at_idx"],
            },
        ),
        (
            "eta_cache",
            "ETA calculation cache. Pre-calculated travel times.",
            {
                "columns": [
                    "from_lat_lng_hash",
                    "to_lat_lng_hash",
                    "eta_seconds",
                    "distance_meters",
                    "cached_at",
                    "expires_at",
                ],
                "indexes": ["from_to_idx", "expires_at_idx"],
            },
        ),
    ]

    for name, desc, meta in location_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Notification & Communication Tables (4)
    notification_schemas = [
        (
            "notifications",
            "User notifications. In-app alerts, badges, deep links.",
            {
                "columns": ["id", "user_id", "type", "title", "message", "data", "read_at", "created_at"],
                "indexes": ["user_id_idx", "read_at_idx"],
            },
        ),
        (
            "push_notifications",
            "Push notification queue. FCM/APNS delivery tracking.",
            {
                "columns": [
                    "id",
                    "notification_id",
                    "device_token",
                    "status",
                    "sent_at",
                    "delivered_at",
                    "failed_at",
                    "error",
                ],
                "indexes": ["notification_id_idx", "status_idx"],
            },
        ),
        (
            "sms_messages",
            "SMS message log. Twilio delivery tracking.",
            {
                "columns": ["id", "user_id", "phone", "message", "status", "provider_id", "sent_at", "delivered_at"],
                "indexes": ["user_id_idx", "status_idx"],
            },
        ),
        (
            "emails",
            "Email delivery log. Sendgrid tracking.",
            {
                "columns": [
                    "id",
                    "user_id",
                    "to_email",
                    "subject",
                    "template",
                    "status",
                    "sent_at",
                    "opened_at",
                    "clicked_at",
                ],
                "indexes": ["user_id_idx", "status_idx"],
            },
        ),
    ]

    for name, desc, meta in notification_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Promotion & Marketing Tables (5)
    promo_schemas = [
        (
            "promotions",
            "Marketing promotions. Discount codes, referral programs.",
            {
                "columns": [
                    "id",
                    "code",
                    "type",
                    "discount_amount",
                    "discount_percent",
                    "max_uses",
                    "uses_count",
                    "valid_from",
                    "valid_until",
                ],
                "indexes": ["code_idx", "valid_from_idx"],
            },
        ),
        (
            "promotion_redemptions",
            "Promotion usage records. User redemption tracking.",
            {
                "columns": ["id", "promotion_id", "user_id", "ride_id", "discount_applied", "redeemed_at"],
                "indexes": ["promotion_id_idx", "user_id_idx"],
            },
        ),
        (
            "referrals",
            "Referral program tracking. Referrer, referee, rewards.",
            {
                "columns": [
                    "id",
                    "referrer_id",
                    "referee_id",
                    "code",
                    "status",
                    "reward_amount",
                    "completed_at",
                    "created_at",
                ],
                "indexes": ["referrer_id_idx", "referee_id_idx", "code_idx"],
            },
        ),
        (
            "campaigns",
            "Marketing campaigns. Email blasts, push campaigns.",
            {
                "columns": [
                    "id",
                    "name",
                    "type",
                    "status",
                    "target_segment",
                    "scheduled_at",
                    "sent_at",
                    "completed_at",
                ],
                "indexes": ["status_idx", "scheduled_at_idx"],
            },
        ),
        (
            "campaign_analytics",
            "Campaign performance metrics. Opens, clicks, conversions.",
            {
                "columns": [
                    "campaign_id",
                    "sent_count",
                    "delivered_count",
                    "opened_count",
                    "clicked_count",
                    "converted_count",
                    "revenue",
                ],
                "indexes": ["campaign_id_idx"],
            },
        ),
    ]

    for name, desc, meta in promo_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Analytics & Reporting Tables (5)
    analytics_schemas = [
        (
            "ride_analytics",
            "Aggregated ride metrics. Daily/hourly ride statistics.",
            {
                "columns": [
                    "date",
                    "hour",
                    "total_rides",
                    "completed_rides",
                    "cancelled_rides",
                    "total_revenue",
                    "avg_ride_duration",
                ],
                "indexes": ["date_hour_idx"],
            },
        ),
        (
            "driver_analytics",
            "Driver performance metrics. Acceptance rate, completion rate.",
            {
                "columns": [
                    "driver_id",
                    "date",
                    "rides_completed",
                    "acceptance_rate",
                    "cancellation_rate",
                    "avg_rating",
                    "total_earnings",
                ],
                "indexes": ["driver_id_date_idx"],
            },
        ),
        (
            "revenue_analytics",
            "Revenue reporting data. Daily revenue breakdowns.",
            {
                "columns": [
                    "date",
                    "gross_revenue",
                    "net_revenue",
                    "driver_payouts",
                    "platform_fees",
                    "refunds",
                    "disputes",
                ],
                "indexes": ["date_idx"],
            },
        ),
        (
            "user_analytics",
            "User behavior analytics. Retention, churn, lifetime value.",
            {
                "columns": [
                    "user_id",
                    "first_ride_date",
                    "last_ride_date",
                    "total_rides",
                    "lifetime_value",
                    "churn_risk_score",
                ],
                "indexes": ["user_id_idx"],
            },
        ),
        (
            "event_logs",
            "Application event tracking. User actions, system events.",
            {
                "columns": ["id", "event_type", "user_id", "session_id", "properties", "created_at"],
                "indexes": ["event_type_idx", "user_id_idx", "created_at_idx"],
            },
        ),
    ]

    for name, desc, meta in analytics_schemas:
        schemas.append(
            create_item_file(
                "database_schemas",
                f"DB_SCHEMA-{counter:03d}",
                "database_schema",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    return schemas


# ============================================================================
# EXTERNAL API INTEGRATIONS (80 items)
# ============================================================================


def generate_external_apis() -> list[Path]:
    """Generate 80 external API integration items."""
    apis = []
    counter = 1

    # Stripe Payment APIs (12)
    stripe_apis = [
        (
            "Stripe Create Customer",
            "Create a new Stripe customer for user payment management.",
            {"endpoint": "POST /v1/customers", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Create Payment Method",
            "Attach payment method (card) to customer account.",
            {"endpoint": "POST /v1/payment_methods", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Create Payment Intent",
            "Create payment intent for ride charge authorization.",
            {"endpoint": "POST /v1/payment_intents", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Confirm Payment Intent",
            "Confirm and capture authorized payment.",
            {"endpoint": "POST /v1/payment_intents/:id/confirm", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Cancel Payment Intent",
            "Cancel uncaptured payment authorization.",
            {"endpoint": "POST /v1/payment_intents/:id/cancel", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Create Refund",
            "Process full or partial refund for completed payment.",
            {"endpoint": "POST /v1/refunds", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Create Payout",
            "Initiate payout to driver bank account.",
            {"endpoint": "POST /v1/payouts", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Create Connected Account",
            "Create Stripe Connect account for driver earnings.",
            {"endpoint": "POST /v1/accounts", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Get Balance",
            "Retrieve account balance for payout calculations.",
            {"endpoint": "GET /v1/balance", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe List Payment Methods",
            "Retrieve all payment methods for customer.",
            {"endpoint": "GET /v1/customers/:id/payment_methods", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Retrieve Charge",
            "Get charge details for transaction record.",
            {"endpoint": "GET /v1/charges/:id", "provider": "Stripe", "auth": "Bearer Token"},
        ),
        (
            "Stripe Handle Webhook",
            "Process Stripe webhook events (payment success, failure, dispute).",
            {"endpoint": "POST /webhooks/stripe", "provider": "Stripe", "auth": "Webhook Signature"},
        ),
    ]

    for name, desc, meta in stripe_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Google Maps APIs (15)
    gmaps_apis = [
        (
            "Google Maps Geocoding",
            "Convert address to latitude/longitude coordinates.",
            {"endpoint": "GET /maps/api/geocode/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Reverse Geocoding",
            "Convert coordinates to formatted address.",
            {"endpoint": "GET /maps/api/geocode/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Directions",
            "Calculate optimal route between two points.",
            {"endpoint": "GET /maps/api/directions/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Distance Matrix",
            "Calculate travel distance and time for multiple destinations.",
            {"endpoint": "GET /maps/api/distancematrix/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Places Autocomplete",
            "Provide address suggestions as user types.",
            {"endpoint": "GET /maps/api/place/autocomplete/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Place Details",
            "Retrieve detailed information about a place.",
            {"endpoint": "GET /maps/api/place/details/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Nearby Search",
            "Find nearby points of interest (restaurants, gas stations).",
            {"endpoint": "GET /maps/api/place/nearbysearch/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Static Map",
            "Generate static map image for ride receipt.",
            {"endpoint": "GET /maps/api/staticmap", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Street View",
            "Retrieve street view image for location verification.",
            {"endpoint": "GET /maps/api/streetview", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Snap to Roads",
            "Snap GPS coordinates to nearest road.",
            {"endpoint": "GET /maps/api/roads/snapToRoads", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Speed Limits",
            "Get speed limit data for route.",
            {"endpoint": "GET /maps/api/roads/speedLimits", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Timezone",
            "Determine timezone for given coordinates.",
            {"endpoint": "GET /maps/api/timezone/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Elevation",
            "Get elevation data for coordinates (routing optimization).",
            {"endpoint": "GET /maps/api/elevation/json", "provider": "Google Maps", "auth": "API Key"},
        ),
        (
            "Google Maps Traffic",
            "Get real-time traffic data for route optimization.",
            {
                "endpoint": "GET /maps/api/directions/json?departure_time=now",
                "provider": "Google Maps",
                "auth": "API Key",
            },
        ),
        (
            "Google Maps Geofencing",
            "Check if location is within service area polygon.",
            {"endpoint": "Internal calculation using Maps SDK", "provider": "Google Maps", "auth": "API Key"},
        ),
    ]

    for name, desc, meta in gmaps_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Twilio Communication APIs (12)
    twilio_apis = [
        (
            "Twilio Send SMS",
            "Send SMS notification to user (ride updates, OTP).",
            {
                "endpoint": "POST /2010-04-01/Accounts/:AccountSid/Messages.json",
                "provider": "Twilio",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio Send Voice Call",
            "Initiate voice call for emergency or verification.",
            {
                "endpoint": "POST /2010-04-01/Accounts/:AccountSid/Calls.json",
                "provider": "Twilio",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio Verify Send",
            "Send OTP for phone number verification.",
            {
                "endpoint": "POST /v2/Services/:ServiceSid/Verifications",
                "provider": "Twilio Verify",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio Verify Check",
            "Verify OTP code entered by user.",
            {
                "endpoint": "POST /v2/Services/:ServiceSid/VerificationCheck",
                "provider": "Twilio Verify",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio Get Message Status",
            "Check SMS delivery status.",
            {
                "endpoint": "GET /2010-04-01/Accounts/:AccountSid/Messages/:MessageSid.json",
                "provider": "Twilio",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio List Messages",
            "Retrieve message history for user.",
            {
                "endpoint": "GET /2010-04-01/Accounts/:AccountSid/Messages.json",
                "provider": "Twilio",
                "auth": "Basic Auth",
            },
        ),
        (
            "Twilio Lookup Phone",
            "Validate and format phone number.",
            {"endpoint": "GET /v1/PhoneNumbers/:PhoneNumber", "provider": "Twilio Lookup", "auth": "Basic Auth"},
        ),
        (
            "Twilio Voice TwiML",
            "Generate TwiML response for automated voice messages.",
            {"endpoint": "Internal TwiML generation", "provider": "Twilio", "auth": "N/A"},
        ),
        (
            "Twilio Status Callback",
            "Receive SMS/call status updates via webhook.",
            {"endpoint": "POST /webhooks/twilio/status", "provider": "Twilio", "auth": "Webhook Signature"},
        ),
        (
            "Twilio Incoming SMS Webhook",
            "Handle incoming SMS messages from users.",
            {"endpoint": "POST /webhooks/twilio/sms", "provider": "Twilio", "auth": "Webhook Signature"},
        ),
        (
            "Twilio Incoming Call Webhook",
            "Handle incoming voice calls.",
            {"endpoint": "POST /webhooks/twilio/voice", "provider": "Twilio", "auth": "Webhook Signature"},
        ),
        (
            "Twilio Programmable Chat",
            "Enable in-app chat between rider and driver.",
            {"endpoint": "POST /v2/Services/:ServiceSid/Channels", "provider": "Twilio Chat", "auth": "Basic Auth"},
        ),
    ]

    for name, desc, meta in twilio_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # AWS S3 Storage APIs (8)
    s3_apis = [
        (
            "S3 Upload Driver Photo",
            "Upload driver profile photo to S3 bucket.",
            {"endpoint": "PUT /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Upload Vehicle Photo",
            "Upload vehicle photos for verification.",
            {"endpoint": "PUT /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Upload Document",
            "Upload driver documents (license, insurance).",
            {"endpoint": "PUT /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Generate Presigned URL",
            "Generate temporary URL for direct upload from mobile app.",
            {"endpoint": "Internal SDK call", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Get Object",
            "Retrieve uploaded file from S3.",
            {"endpoint": "GET /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Delete Object",
            "Remove file from S3 (user account deletion).",
            {"endpoint": "DELETE /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 List Objects",
            "List all files for a user/driver.",
            {"endpoint": "GET /:bucket?prefix=:prefix", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
        (
            "S3 Copy Object",
            "Copy file between S3 buckets or keys.",
            {"endpoint": "PUT /:bucket/:key", "provider": "AWS S3", "auth": "AWS Signature V4"},
        ),
    ]

    for name, desc, meta in s3_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # SendGrid Email APIs (8)
    sendgrid_apis = [
        (
            "SendGrid Send Transactional Email",
            "Send ride receipt email to user.",
            {"endpoint": "POST /v3/mail/send", "provider": "SendGrid", "auth": "Bearer Token"},
        ),
        (
            "SendGrid Send Welcome Email",
            "Send welcome email to new users.",
            {"endpoint": "POST /v3/mail/send", "provider": "SendGrid", "auth": "Bearer Token"},
        ),
        (
            "SendGrid Send Password Reset",
            "Send password reset link via email.",
            {"endpoint": "POST /v3/mail/send", "provider": "SendGrid", "auth": "Bearer Token"},
        ),
        (
            "SendGrid Send Marketing Campaign",
            "Send promotional emails to user segment.",
            {"endpoint": "POST /v3/marketing/singlesends", "provider": "SendGrid", "auth": "Bearer Token"},
        ),
        (
            "SendGrid Track Email Opens",
            "Track when users open emails.",
            {"endpoint": "Webhook event", "provider": "SendGrid", "auth": "Webhook Signature"},
        ),
        (
            "SendGrid Track Email Clicks",
            "Track link clicks in emails.",
            {"endpoint": "Webhook event", "provider": "SendGrid", "auth": "Webhook Signature"},
        ),
        (
            "SendGrid Handle Bounce",
            "Process email bounce events.",
            {"endpoint": "POST /webhooks/sendgrid", "provider": "SendGrid", "auth": "Webhook Signature"},
        ),
        (
            "SendGrid Manage Suppression List",
            "Add/remove emails from suppression list.",
            {"endpoint": "POST /v3/asm/suppressions", "provider": "SendGrid", "auth": "Bearer Token"},
        ),
    ]

    for name, desc, meta in sendgrid_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # OneSignal Push Notification APIs (8)
    onesignal_apis = [
        (
            "OneSignal Create Notification",
            "Send push notification to user devices.",
            {"endpoint": "POST /notifications", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal Register Device",
            "Register device token for push notifications.",
            {"endpoint": "POST /players", "provider": "OneSignal", "auth": "App ID"},
        ),
        (
            "OneSignal Update Device",
            "Update device metadata (language, timezone).",
            {"endpoint": "PUT /players/:id", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal Create Segment",
            "Create user segment for targeted notifications.",
            {"endpoint": "POST /apps/:app_id/segments", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal View Notification",
            "Get notification delivery statistics.",
            {"endpoint": "GET /notifications/:id", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal Cancel Notification",
            "Cancel scheduled notification.",
            {"endpoint": "DELETE /notifications/:id", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal Track Event",
            "Track custom in-app events for targeting.",
            {"endpoint": "POST /players/:id/on_session", "provider": "OneSignal", "auth": "REST API Key"},
        ),
        (
            "OneSignal Export Data",
            "Export notification analytics data.",
            {"endpoint": "GET /notifications/:id/export", "provider": "OneSignal", "auth": "REST API Key"},
        ),
    ]

    for name, desc, meta in onesignal_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Checkr Background Check APIs (6)
    checkr_apis = [
        (
            "Checkr Create Candidate",
            "Create candidate profile for background check.",
            {"endpoint": "POST /v1/candidates", "provider": "Checkr", "auth": "Bearer Token"},
        ),
        (
            "Checkr Create Invitation",
            "Send background check invitation to driver.",
            {"endpoint": "POST /v1/invitations", "provider": "Checkr", "auth": "Bearer Token"},
        ),
        (
            "Checkr Request Report",
            "Request background check report (criminal, DMV).",
            {"endpoint": "POST /v1/reports", "provider": "Checkr", "auth": "Bearer Token"},
        ),
        (
            "Checkr Get Report",
            "Retrieve completed background check report.",
            {"endpoint": "GET /v1/reports/:id", "provider": "Checkr", "auth": "Bearer Token"},
        ),
        (
            "Checkr List Reports",
            "List all reports for a candidate.",
            {"endpoint": "GET /v1/reports", "provider": "Checkr", "auth": "Bearer Token"},
        ),
        (
            "Checkr Webhook Handler",
            "Receive report completion webhooks.",
            {"endpoint": "POST /webhooks/checkr", "provider": "Checkr", "auth": "Webhook Signature"},
        ),
    ]

    for name, desc, meta in checkr_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Plaid Bank Verification APIs (6)
    plaid_apis = [
        (
            "Plaid Create Link Token",
            "Generate token for Plaid Link flow.",
            {"endpoint": "POST /link/token/create", "provider": "Plaid", "auth": "client_id + secret"},
        ),
        (
            "Plaid Exchange Public Token",
            "Exchange public token for access token.",
            {"endpoint": "POST /item/public_token/exchange", "provider": "Plaid", "auth": "client_id + secret"},
        ),
        (
            "Plaid Get Bank Accounts",
            "Retrieve linked bank account details.",
            {"endpoint": "POST /accounts/get", "provider": "Plaid", "auth": "access_token"},
        ),
        (
            "Plaid Verify Bank Account",
            "Verify bank account ownership via micro-deposits.",
            {"endpoint": "POST /auth/get", "provider": "Plaid", "auth": "access_token"},
        ),
        (
            "Plaid Create Processor Token",
            "Create token for Stripe bank account integration.",
            {
                "endpoint": "POST /processor/stripe/bank_account_token/create",
                "provider": "Plaid",
                "auth": "access_token",
            },
        ),
        (
            "Plaid Webhook Handler",
            "Receive account verification status updates.",
            {"endpoint": "POST /webhooks/plaid", "provider": "Plaid", "auth": "Webhook Verification"},
        ),
    ]

    for name, desc, meta in plaid_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Weather API (5)
    weather_apis = [
        (
            "OpenWeather Current Weather",
            "Get current weather conditions for route planning.",
            {"endpoint": "GET /data/2.5/weather", "provider": "OpenWeather", "auth": "API Key"},
        ),
        (
            "OpenWeather Forecast",
            "Get weather forecast for scheduled rides.",
            {"endpoint": "GET /data/2.5/forecast", "provider": "OpenWeather", "auth": "API Key"},
        ),
        (
            "OpenWeather Alerts",
            "Get severe weather alerts for service area.",
            {"endpoint": "GET /data/2.5/onecall", "provider": "OpenWeather", "auth": "API Key"},
        ),
        (
            "OpenWeather Historical",
            "Get historical weather data for analytics.",
            {"endpoint": "GET /data/2.5/timemachine", "provider": "OpenWeather", "auth": "API Key"},
        ),
        (
            "OpenWeather Air Quality",
            "Get air quality data for eco-conscious users.",
            {"endpoint": "GET /data/2.5/air_pollution", "provider": "OpenWeather", "auth": "API Key"},
        ),
    ]

    for name, desc, meta in weather_apis:
        apis.append(
            create_item_file(
                "external_apis",
                f"EXT_API-{counter:03d}",
                "external_api",
                name,
                desc,
                priority="low",
                metadata=meta,
            ),
        )
        counter += 1

    return apis


# ============================================================================
# WEBHOOK DEFINITIONS (70 items)
# ============================================================================


def generate_webhooks() -> list[Path]:
    """Generate 70 webhook endpoint items."""
    webhooks = []
    counter = 1

    # Stripe Webhooks (15)
    stripe_webhooks = [
        (
            "payment_intent.succeeded",
            "Payment successfully captured for ride.",
            {"event": "payment_intent.succeeded", "provider": "Stripe"},
        ),
        (
            "payment_intent.payment_failed",
            "Payment failed - notify user and cancel ride.",
            {"event": "payment_intent.payment_failed", "provider": "Stripe"},
        ),
        (
            "payment_intent.canceled",
            "Payment cancelled - release hold.",
            {"event": "payment_intent.canceled", "provider": "Stripe"},
        ),
        (
            "charge.refunded",
            "Refund processed - update transaction status.",
            {"event": "charge.refunded", "provider": "Stripe"},
        ),
        (
            "charge.dispute.created",
            "Payment dispute initiated by cardholder.",
            {"event": "charge.dispute.created", "provider": "Stripe"},
        ),
        (
            "charge.dispute.closed",
            "Payment dispute resolved.",
            {"event": "charge.dispute.closed", "provider": "Stripe"},
        ),
        (
            "payout.paid",
            "Driver payout successfully transferred to bank.",
            {"event": "payout.paid", "provider": "Stripe"},
        ),
        (
            "payout.failed",
            "Driver payout failed - notify driver and support.",
            {"event": "payout.failed", "provider": "Stripe"},
        ),
        ("account.updated", "Stripe Connect account updated.", {"event": "account.updated", "provider": "Stripe"}),
        ("customer.created", "New customer created in Stripe.", {"event": "customer.created", "provider": "Stripe"}),
        ("customer.deleted", "Customer deleted from Stripe.", {"event": "customer.deleted", "provider": "Stripe"}),
        (
            "payment_method.attached",
            "Payment method attached to customer.",
            {"event": "payment_method.attached", "provider": "Stripe"},
        ),
        (
            "payment_method.detached",
            "Payment method removed from customer.",
            {"event": "payment_method.detached", "provider": "Stripe"},
        ),
        (
            "transfer.created",
            "Transfer created for driver earnings.",
            {"event": "transfer.created", "provider": "Stripe"},
        ),
        ("balance.available", "Account balance updated.", {"event": "balance.available", "provider": "Stripe"}),
    ]

    for name, desc, meta in stripe_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Twilio Webhooks (10)
    twilio_webhooks = [
        ("SMS Delivered", "SMS successfully delivered to user.", {"event": "message.delivered", "provider": "Twilio"}),
        (
            "SMS Failed",
            "SMS delivery failed - try alternative method.",
            {"event": "message.failed", "provider": "Twilio"},
        ),
        (
            "SMS Received",
            "Incoming SMS from user - parse for commands.",
            {"event": "message.received", "provider": "Twilio"},
        ),
        ("Call Initiated", "Outbound call initiated.", {"event": "call.initiated", "provider": "Twilio"}),
        ("Call Answered", "Call answered by recipient.", {"event": "call.answered", "provider": "Twilio"}),
        (
            "Call Completed",
            "Call completed - log duration and status.",
            {"event": "call.completed", "provider": "Twilio"},
        ),
        ("Call No Answer", "Call not answered - trigger fallback.", {"event": "call.no-answer", "provider": "Twilio"}),
        (
            "Verification Started",
            "OTP verification initiated.",
            {"event": "verification.started", "provider": "Twilio Verify"},
        ),
        (
            "Verification Approved",
            "OTP verified successfully.",
            {"event": "verification.approved", "provider": "Twilio Verify"},
        ),
        (
            "Verification Failed",
            "OTP verification failed - max attempts reached.",
            {"event": "verification.failed", "provider": "Twilio Verify"},
        ),
    ]

    for name, desc, meta in twilio_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # SendGrid Webhooks (10)
    sendgrid_webhooks = [
        (
            "Email Delivered",
            "Email successfully delivered to recipient.",
            {"event": "delivered", "provider": "SendGrid"},
        ),
        ("Email Opened", "User opened email - track engagement.", {"event": "open", "provider": "SendGrid"}),
        ("Email Clicked", "User clicked link in email.", {"event": "click", "provider": "SendGrid"}),
        ("Email Bounced", "Email bounced - hard bounce or soft bounce.", {"event": "bounce", "provider": "SendGrid"}),
        ("Email Spam Report", "User marked email as spam.", {"event": "spamreport", "provider": "SendGrid"}),
        (
            "Email Unsubscribe",
            "User unsubscribed from marketing emails.",
            {"event": "unsubscribe", "provider": "SendGrid"},
        ),
        (
            "Email Dropped",
            "Email dropped before delivery (suppression list).",
            {"event": "dropped", "provider": "SendGrid"},
        ),
        (
            "Email Deferred",
            "Email temporarily deferred by recipient server.",
            {"event": "deferred", "provider": "SendGrid"},
        ),
        ("Email Processed", "Email processed by SendGrid.", {"event": "processed", "provider": "SendGrid"}),
        (
            "Group Unsubscribe",
            "User unsubscribed from specific email group.",
            {"event": "group_unsubscribe", "provider": "SendGrid"},
        ),
    ]

    for name, desc, meta in sendgrid_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Checkr Webhooks (8)
    checkr_webhooks = [
        ("Report Completed", "Background check report completed.", {"event": "report.completed", "provider": "Checkr"}),
        ("Report Pending", "Report pending additional information.", {"event": "report.pending", "provider": "Checkr"}),
        ("Report Clear", "Report clear - driver approved.", {"event": "report.clear", "provider": "Checkr"}),
        ("Report Consider", "Report flagged for manual review.", {"event": "report.consider", "provider": "Checkr"}),
        (
            "Report Suspended",
            "Report suspended - candidate action required.",
            {"event": "report.suspended", "provider": "Checkr"},
        ),
        (
            "Invitation Completed",
            "Driver completed background check invitation.",
            {"event": "invitation.completed", "provider": "Checkr"},
        ),
        (
            "Invitation Expired",
            "Background check invitation expired.",
            {"event": "invitation.expired", "provider": "Checkr"},
        ),
        ("Candidate Created", "New candidate profile created.", {"event": "candidate.created", "provider": "Checkr"}),
    ]

    for name, desc, meta in checkr_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Plaid Webhooks (7)
    plaid_webhooks = [
        (
            "Item Login Required",
            "User needs to re-authenticate with bank.",
            {"event": "ITEM_LOGIN_REQUIRED", "provider": "Plaid"},
        ),
        (
            "Webhook Verification Status",
            "Bank account verification status updated.",
            {"event": "WEBHOOK_VERIFICATION_STATUS", "provider": "Plaid"},
        ),
        ("Auth Verification Status", "Auth verification completed.", {"event": "DEFAULT_UPDATE", "provider": "Plaid"}),
        ("Item Error", "Error accessing bank account data.", {"event": "ERROR", "provider": "Plaid"}),
        ("Item Updated", "Bank account information updated.", {"event": "DEFAULT_UPDATE", "provider": "Plaid"}),
        ("Item Removed", "User revoked bank account access.", {"event": "ITEM_REMOVED", "provider": "Plaid"}),
        ("Transactions Updated", "New transactions available.", {"event": "TRANSACTIONS_REMOVED", "provider": "Plaid"}),
    ]

    for name, desc, meta in plaid_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # OneSignal Webhooks (5)
    onesignal_webhooks = [
        ("Notification Sent", "Push notification sent to device.", {"event": "sent", "provider": "OneSignal"}),
        (
            "Notification Delivered",
            "Push notification delivered to device.",
            {"event": "delivered", "provider": "OneSignal"},
        ),
        ("Notification Clicked", "User clicked push notification.", {"event": "clicked", "provider": "OneSignal"}),
        ("Notification Failed", "Push notification delivery failed.", {"event": "failed", "provider": "OneSignal"}),
        (
            "Device Unsubscribed",
            "User unsubscribed from push notifications.",
            {"event": "unsubscribed", "provider": "OneSignal"},
        ),
    ]

    for name, desc, meta in onesignal_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Internal App Webhooks (15)
    internal_webhooks = [
        ("Ride Requested", "New ride request created.", {"event": "ride.requested", "provider": "Internal"}),
        ("Ride Accepted", "Driver accepted ride request.", {"event": "ride.accepted", "provider": "Internal"}),
        ("Ride Started", "Driver started ride.", {"event": "ride.started", "provider": "Internal"}),
        ("Ride Completed", "Ride completed successfully.", {"event": "ride.completed", "provider": "Internal"}),
        ("Ride Cancelled", "Ride cancelled by rider or driver.", {"event": "ride.cancelled", "provider": "Internal"}),
        (
            "Driver Location Updated",
            "Driver GPS location updated.",
            {"event": "driver.location_updated", "provider": "Internal"},
        ),
        ("Driver Online", "Driver went online.", {"event": "driver.online", "provider": "Internal"}),
        ("Driver Offline", "Driver went offline.", {"event": "driver.offline", "provider": "Internal"}),
        ("User Registered", "New user account created.", {"event": "user.registered", "provider": "Internal"}),
        ("User Verified", "User phone/email verified.", {"event": "user.verified", "provider": "Internal"}),
        (
            "Payment Completed",
            "Payment successfully processed.",
            {"event": "payment.completed", "provider": "Internal"},
        ),
        (
            "Promotion Applied",
            "Promotion code applied to ride.",
            {"event": "promotion.applied", "provider": "Internal"},
        ),
        ("Rating Submitted", "User submitted ride rating.", {"event": "rating.submitted", "provider": "Internal"}),
        ("SOS Triggered", "Emergency SOS button triggered.", {"event": "sos.triggered", "provider": "Internal"}),
        ("Surge Activated", "Surge pricing activated in zone.", {"event": "surge.activated", "provider": "Internal"}),
    ]

    for name, desc, meta in internal_webhooks:
        webhooks.append(
            create_item_file(
                "webhooks",
                f"WEBHOOK-{counter:03d}",
                "webhook",
                name,
                desc,
                priority="high" if "sos" in name.lower() or "ride" in name.lower() else "medium",
                metadata=meta,
            ),
        )
        counter += 1

    return webhooks


# ============================================================================
# DATA PIPELINE DEFINITIONS (60 items)
# ============================================================================


def generate_data_pipelines() -> list[Path]:
    """Generate 60 data pipeline items."""
    pipelines = []
    counter = 1

    # Real-time Ride Tracking Pipelines (10)
    ride_pipelines = [
        (
            "Real-time Driver Location Stream",
            "Stream driver GPS coordinates to Redis for live tracking.",
            {"source": "Mobile App GPS", "sink": "Redis", "frequency": "1 second", "format": "JSON"},
        ),
        (
            "Ride Matching Engine",
            "Match available drivers to ride requests based on location and availability.",
            {"source": "Ride Requests Queue", "sink": "Matching Service", "frequency": "Real-time", "format": "Event"},
        ),
        (
            "ETA Calculation Pipeline",
            "Calculate real-time ETA based on driver location and traffic.",
            {
                "source": "Driver Location + Google Maps",
                "sink": "WebSocket",
                "frequency": "5 seconds",
                "format": "JSON",
            },
        ),
        (
            "Ride Status Event Stream",
            "Stream ride status changes to all connected clients.",
            {"source": "Ride Service", "sink": "WebSocket", "frequency": "Real-time", "format": "Event"},
        ),
        (
            "Surge Pricing Calculator",
            "Calculate dynamic surge multiplier based on supply/demand.",
            {
                "source": "Active Rides + Available Drivers",
                "sink": "Pricing Service",
                "frequency": "1 minute",
                "format": "Aggregation",
            },
        ),
        (
            "Driver Proximity Search",
            "Query drivers within radius of pickup location.",
            {
                "source": "Redis Geospatial",
                "sink": "Matching Service",
                "frequency": "Real-time",
                "format": "Geospatial Query",
            },
        ),
        (
            "Route Optimization Pipeline",
            "Optimize multi-stop routes for shared rides.",
            {"source": "Ride Requests", "sink": "Routing Service", "frequency": "Real-time", "format": "Algorithm"},
        ),
        (
            "Live Ride Tracking Broadcast",
            "Broadcast driver location to rider's app.",
            {"source": "Driver Location Stream", "sink": "Rider WebSocket", "frequency": "2 seconds", "format": "JSON"},
        ),
        (
            "Ride Completion Trigger",
            "Trigger post-ride workflows when ride completes.",
            {
                "source": "Ride Status",
                "sink": "Payment + Rating + Receipt Services",
                "frequency": "Event-driven",
                "format": "Event",
            },
        ),
        (
            "Ride Metrics Aggregation",
            "Aggregate real-time ride metrics for dashboards.",
            {"source": "Ride Events", "sink": "Analytics DB", "frequency": "10 seconds", "format": "Time-series"},
        ),
    ]

    for name, desc, meta in ride_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Driver Earnings Pipelines (8)
    earnings_pipelines = [
        (
            "Driver Earnings Calculator",
            "Calculate per-ride earnings including base, distance, time, surge.",
            {"source": "Completed Rides", "sink": "Earnings Table", "frequency": "Real-time", "format": "Calculation"},
        ),
        (
            "Weekly Payout Aggregator",
            "Aggregate weekly earnings for driver payouts.",
            {"source": "Earnings Table", "sink": "Payout Service", "frequency": "Weekly", "format": "Batch"},
        ),
        (
            "Earnings Tax Calculator",
            "Calculate tax withholding for driver earnings.",
            {"source": "Payout Amounts", "sink": "Tax Service", "frequency": "Weekly", "format": "Calculation"},
        ),
        (
            "Tips Distribution Pipeline",
            "Distribute rider tips to driver earnings.",
            {"source": "Tip Transactions", "sink": "Earnings Table", "frequency": "Real-time", "format": "ETL"},
        ),
        (
            "Incentive Bonus Calculator",
            "Calculate driver incentive bonuses (quest completions, guarantees).",
            {"source": "Driver Activity", "sink": "Bonus Table", "frequency": "Daily", "format": "Batch"},
        ),
        (
            "Earnings Statement Generator",
            "Generate weekly earnings statements for drivers.",
            {"source": "Earnings + Payouts", "sink": "S3 PDF Storage", "frequency": "Weekly", "format": "Report"},
        ),
        (
            "Referral Bonus Distributor",
            "Distribute referral bonuses to drivers.",
            {"source": "Referral Completions", "sink": "Earnings Table", "frequency": "Event-driven", "format": "ETL"},
        ),
        (
            "Payout Reconciliation",
            "Reconcile Stripe payouts with internal earnings records.",
            {
                "source": "Stripe Webhooks + Earnings DB",
                "sink": "Accounting System",
                "frequency": "Daily",
                "format": "Reconciliation",
            },
        ),
    ]

    for name, desc, meta in earnings_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Analytics Aggregation Pipelines (12)
    analytics_pipelines = [
        (
            "Hourly Ride Metrics",
            "Aggregate ride counts, revenue, cancellations by hour.",
            {"source": "Rides Table", "sink": "Analytics Warehouse", "frequency": "Hourly", "format": "Time-series"},
        ),
        (
            "Daily Revenue Rollup",
            "Roll up daily revenue by city, service type.",
            {
                "source": "Transactions Table",
                "sink": "Revenue Analytics",
                "frequency": "Daily",
                "format": "Aggregation",
            },
        ),
        (
            "Driver Performance Metrics",
            "Calculate driver acceptance rate, cancellation rate, ratings.",
            {"source": "Ride Events", "sink": "Driver Analytics", "frequency": "Daily", "format": "Batch"},
        ),
        (
            "User Cohort Analysis",
            "Track user retention, lifetime value by signup cohort.",
            {"source": "User Activity", "sink": "Cohort Analytics", "frequency": "Weekly", "format": "Cohort Analysis"},
        ),
        (
            "Geographic Heatmap Data",
            "Generate ride density heatmap data.",
            {
                "source": "Ride Locations",
                "sink": "Heatmap Service",
                "frequency": "Hourly",
                "format": "Geospatial Aggregation",
            },
        ),
        (
            "Churn Prediction Model",
            "Predict user/driver churn probability.",
            {
                "source": "User Activity + ML Model",
                "sink": "Churn Scores Table",
                "frequency": "Daily",
                "format": "ML Pipeline",
            },
        ),
        (
            "Demand Forecasting",
            "Forecast ride demand by location and time.",
            {
                "source": "Historical Rides + Weather",
                "sink": "Forecasting Service",
                "frequency": "Daily",
                "format": "ML Pipeline",
            },
        ),
        (
            "Operational KPI Dashboard",
            "Real-time KPI metrics for operations team.",
            {"source": "Multiple Sources", "sink": "Dashboard API", "frequency": "1 minute", "format": "Aggregation"},
        ),
        (
            "Marketing Attribution",
            "Track ride conversions from marketing campaigns.",
            {"source": "Campaign Data + Rides", "sink": "Attribution Table", "frequency": "Daily", "format": "ETL"},
        ),
        (
            "Customer Support Metrics",
            "Track support ticket resolution time, satisfaction.",
            {"source": "Support Tickets", "sink": "Support Analytics", "frequency": "Hourly", "format": "Aggregation"},
        ),
        (
            "Fraud Detection Signals",
            "Calculate fraud risk signals for transactions.",
            {
                "source": "User Behavior + Transactions",
                "sink": "Fraud Scores Table",
                "frequency": "Real-time",
                "format": "ML Pipeline",
            },
        ),
        (
            "App Performance Metrics",
            "Track app crashes, errors, API latency.",
            {"source": "App Logs", "sink": "APM Dashboard", "frequency": "Real-time", "format": "Log Aggregation"},
        ),
    ]

    for name, desc, meta in analytics_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Fraud Detection Pipelines (10)
    fraud_pipelines = [
        (
            "Account Takeover Detection",
            "Detect suspicious login patterns (new device, location).",
            {"source": "Login Events", "sink": "Fraud Alerts", "frequency": "Real-time", "format": "Rule Engine"},
        ),
        (
            "Payment Fraud Detector",
            "Detect fraudulent payment patterns (stolen cards, velocity).",
            {"source": "Transactions", "sink": "Fraud Scores", "frequency": "Real-time", "format": "ML Pipeline"},
        ),
        (
            "Fake Ride Detection",
            "Detect driver-rider collusion for fake rides.",
            {
                "source": "Ride Patterns",
                "sink": "Investigation Queue",
                "frequency": "Daily",
                "format": "Anomaly Detection",
            },
        ),
        (
            "Referral Fraud Detector",
            "Detect fake referral accounts.",
            {"source": "Referral Data", "sink": "Fraud Alerts", "frequency": "Daily", "format": "Rule Engine"},
        ),
        (
            "Promo Abuse Detector",
            "Detect promotional code abuse patterns.",
            {"source": "Promotion Usage", "sink": "Fraud Alerts", "frequency": "Real-time", "format": "Rule Engine"},
        ),
        (
            "Driver Identity Fraud",
            "Detect driver account sharing or identity theft.",
            {
                "source": "Driver Behavior + Selfie Checks",
                "sink": "Investigation Queue",
                "frequency": "Daily",
                "format": "ML Pipeline",
            },
        ),
        (
            "GPS Spoofing Detection",
            "Detect GPS coordinate manipulation.",
            {
                "source": "Driver Locations",
                "sink": "Fraud Alerts",
                "frequency": "Real-time",
                "format": "Anomaly Detection",
            },
        ),
        (
            "Chargeback Predictor",
            "Predict likelihood of payment chargebacks.",
            {
                "source": "Transaction History",
                "sink": "Chargeback Scores",
                "frequency": "Real-time",
                "format": "ML Pipeline",
            },
        ),
        (
            "Multi-Account Detection",
            "Detect users with multiple accounts.",
            {
                "source": "User Metadata",
                "sink": "Investigation Queue",
                "frequency": "Daily",
                "format": "Graph Analysis",
            },
        ),
        (
            "Velocity Fraud Rules",
            "Detect abnormal transaction velocity.",
            {"source": "Transaction Stream", "sink": "Fraud Alerts", "frequency": "Real-time", "format": "Rule Engine"},
        ),
    ]

    for name, desc, meta in fraud_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Data Export & Compliance Pipelines (8)
    compliance_pipelines = [
        (
            "GDPR Data Export",
            "Export all user data for GDPR compliance.",
            {"source": "All User Tables", "sink": "S3 Encrypted", "frequency": "On-demand", "format": "JSON"},
        ),
        (
            "CCPA Data Deletion",
            "Delete user data per CCPA right to deletion.",
            {"source": "Deletion Requests", "sink": "All User Tables", "frequency": "Daily", "format": "Batch Delete"},
        ),
        (
            "Tax Document Generator",
            "Generate 1099-K forms for drivers.",
            {"source": "Earnings Data", "sink": "Tax Service", "frequency": "Annual", "format": "PDF"},
        ),
        (
            "Audit Log Archive",
            "Archive audit logs to cold storage.",
            {"source": "Audit Logs", "sink": "S3 Glacier", "frequency": "Monthly", "format": "Compressed JSON"},
        ),
        (
            "Data Retention Enforcer",
            "Delete old data per retention policy.",
            {"source": "Aged Records", "sink": "Delete Queue", "frequency": "Weekly", "format": "Batch Delete"},
        ),
        (
            "PII Masking Pipeline",
            "Mask PII in analytics database.",
            {
                "source": "Production Tables",
                "sink": "Analytics Warehouse",
                "frequency": "Daily",
                "format": "ETL + Masking",
            },
        ),
        (
            "Regulatory Report Generator",
            "Generate regulatory compliance reports.",
            {"source": "Transaction Data", "sink": "Compliance Team", "frequency": "Monthly", "format": "CSV"},
        ),
        (
            "Backup & Recovery Pipeline",
            "Full database backup to S3.",
            {"source": "PostgreSQL", "sink": "S3 Backup", "frequency": "Daily", "format": "Encrypted Dump"},
        ),
    ]

    for name, desc, meta in compliance_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Integration Sync Pipelines (12)
    sync_pipelines = [
        (
            "Stripe Customer Sync",
            "Sync user accounts with Stripe customers.",
            {"source": "Users Table", "sink": "Stripe API", "frequency": "Real-time", "format": "API Call"},
        ),
        (
            "Sendgrid Contact Sync",
            "Sync user emails to SendGrid for marketing.",
            {"source": "Users Table", "sink": "SendGrid API", "frequency": "Daily", "format": "Batch"},
        ),
        (
            "OneSignal Device Sync",
            "Sync device tokens to OneSignal.",
            {"source": "User Devices", "sink": "OneSignal API", "frequency": "Real-time", "format": "API Call"},
        ),
        (
            "Google Analytics Events",
            "Stream app events to Google Analytics.",
            {"source": "Event Logs", "sink": "GA4 API", "frequency": "Real-time", "format": "Event Stream"},
        ),
        (
            "Mixpanel User Sync",
            "Sync user profiles to Mixpanel.",
            {"source": "Users + Activity", "sink": "Mixpanel API", "frequency": "Daily", "format": "Batch"},
        ),
        (
            "Segment Event Forwarding",
            "Forward events to Segment for routing.",
            {"source": "Event Stream", "sink": "Segment API", "frequency": "Real-time", "format": "Event"},
        ),
        (
            "Salesforce Lead Sync",
            "Sync high-value users to Salesforce CRM.",
            {"source": "User Analytics", "sink": "Salesforce API", "frequency": "Daily", "format": "Batch"},
        ),
        (
            "Zendesk Ticket Sync",
            "Create support tickets from in-app feedback.",
            {"source": "Feedback Queue", "sink": "Zendesk API", "frequency": "Real-time", "format": "API Call"},
        ),
        (
            "Slack Alert Pipeline",
            "Send critical alerts to Slack channels.",
            {"source": "Alert Queue", "sink": "Slack Webhook", "frequency": "Real-time", "format": "Webhook"},
        ),
        (
            "PagerDuty Incident Sync",
            "Create PagerDuty incidents for critical errors.",
            {"source": "Error Monitoring", "sink": "PagerDuty API", "frequency": "Real-time", "format": "API Call"},
        ),
        (
            "Datadog Metrics Sync",
            "Stream application metrics to Datadog.",
            {"source": "App Metrics", "sink": "Datadog API", "frequency": "10 seconds", "format": "Metric"},
        ),
        (
            "ElasticSearch Log Sync",
            "Index application logs in ElasticSearch.",
            {"source": "App Logs", "sink": "ElasticSearch", "frequency": "Real-time", "format": "Log Stream"},
        ),
    ]

    for name, desc, meta in sync_pipelines:
        pipelines.append(
            create_item_file(
                "data_pipelines",
                f"PIPELINE-{counter:03d}",
                "data_pipeline",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    return pipelines


# ============================================================================
# CACHE STRATEGY DEFINITIONS (50 items)
# ============================================================================


def generate_cache_strategies() -> list[Path]:
    """Generate 50 cache strategy items."""
    caches = []
    counter = 1

    # User & Session Caching (8)
    user_caches = [
        (
            "User Session Cache",
            "Cache active user sessions with JWT tokens.",
            {"key_pattern": "session:{token_hash}", "ttl": "24 hours", "eviction": "LRU"},
        ),
        (
            "User Profile Cache",
            "Cache user profile data to reduce DB queries.",
            {"key_pattern": "user:{user_id}:profile", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "User Preferences Cache",
            "Cache user settings and preferences.",
            {"key_pattern": "user:{user_id}:prefs", "ttl": "6 hours", "eviction": "LRU"},
        ),
        (
            "User Roles Cache",
            "Cache user role assignments.",
            {"key_pattern": "user:{user_id}:roles", "ttl": "30 minutes", "eviction": "LRU"},
        ),
        (
            "Auth Token Blacklist",
            "Cache invalidated JWT tokens.",
            {"key_pattern": "blacklist:{token_hash}", "ttl": "24 hours", "eviction": "TTL"},
        ),
        (
            "Password Reset Tokens",
            "Cache password reset tokens with expiry.",
            {"key_pattern": "reset:{token}", "ttl": "15 minutes", "eviction": "TTL"},
        ),
        (
            "OTP Verification Cache",
            "Cache OTP codes for phone verification.",
            {"key_pattern": "otp:{phone}:{code}", "ttl": "5 minutes", "eviction": "TTL"},
        ),
        (
            "User Device Cache",
            "Cache registered user devices.",
            {"key_pattern": "user:{user_id}:devices", "ttl": "12 hours", "eviction": "LRU"},
        ),
    ]

    for name, desc, meta in user_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="critical" if "session" in name.lower() else "high",
                metadata=meta,
            ),
        )
        counter += 1

    # Driver Location & Availability Caching (7)
    driver_caches = [
        (
            "Driver Location Cache",
            "Cache real-time driver GPS coordinates with geospatial indexing.",
            {"key_pattern": "geo:drivers", "ttl": "30 seconds", "eviction": "TTL", "type": "Geospatial"},
        ),
        (
            "Driver Availability Cache",
            "Cache driver online/offline status.",
            {"key_pattern": "driver:{driver_id}:available", "ttl": "1 minute", "eviction": "TTL"},
        ),
        (
            "Driver Profile Cache",
            "Cache driver profile, vehicle, rating.",
            {"key_pattern": "driver:{driver_id}:profile", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Driver Earnings Cache",
            "Cache current week earnings for quick retrieval.",
            {"key_pattern": "driver:{driver_id}:earnings:week", "ttl": "5 minutes", "eviction": "LRU"},
        ),
        (
            "Driver Documents Cache",
            "Cache driver verification document status.",
            {"key_pattern": "driver:{driver_id}:docs", "ttl": "30 minutes", "eviction": "LRU"},
        ),
        (
            "Nearby Drivers Cache",
            "Cache drivers within radius of location.",
            {"key_pattern": "nearby:{lat}:{lng}:{radius}", "ttl": "10 seconds", "eviction": "TTL"},
        ),
        (
            "Driver Queue Position",
            "Cache driver position in ride request queue.",
            {"key_pattern": "queue:{service_area}:drivers", "ttl": "1 minute", "eviction": "TTL"},
        ),
    ]

    for name, desc, meta in driver_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Ride & Pricing Caching (10)
    ride_caches = [
        (
            "Active Ride Cache",
            "Cache active ride details for quick access.",
            {"key_pattern": "ride:{ride_id}:active", "ttl": "Until completion", "eviction": "Manual"},
        ),
        (
            "Ride Estimate Cache",
            "Cache pricing estimates for common routes.",
            {"key_pattern": "estimate:{pickup_hash}:{dropoff_hash}", "ttl": "5 minutes", "eviction": "LRU"},
        ),
        (
            "Surge Multiplier Cache",
            "Cache current surge pricing by zone.",
            {"key_pattern": "surge:{zone_id}", "ttl": "1 minute", "eviction": "TTL"},
        ),
        (
            "Ride History Cache",
            "Cache recent ride history for user.",
            {"key_pattern": "user:{user_id}:rides:recent", "ttl": "15 minutes", "eviction": "LRU"},
        ),
        (
            "Ride Matching Queue",
            "Cache pending ride requests awaiting driver match.",
            {"key_pattern": "queue:pending_rides", "ttl": "5 minutes", "eviction": "FIFO"},
        ),
        (
            "Route Cache",
            "Cache calculated routes with polyline data.",
            {"key_pattern": "route:{pickup_hash}:{dropoff_hash}", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "ETA Cache",
            "Cache ETA calculations.",
            {"key_pattern": "eta:{from_hash}:{to_hash}", "ttl": "2 minutes", "eviction": "TTL"},
        ),
        (
            "Ride Receipt Cache",
            "Cache generated ride receipts.",
            {"key_pattern": "receipt:{ride_id}", "ttl": "7 days", "eviction": "LRU"},
        ),
        (
            "Scheduled Rides Cache",
            "Cache upcoming scheduled rides.",
            {"key_pattern": "scheduled:{rider_id}", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Ride Cancellation Reasons",
            "Cache cancellation reason options.",
            {"key_pattern": "config:cancel_reasons", "ttl": "24 hours", "eviction": "LRU"},
        ),
    ]

    for name, desc, meta in ride_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="critical" if "active" in name.lower() or "surge" in name.lower() else "high",
                metadata=meta,
            ),
        )
        counter += 1

    # Payment & Transaction Caching (6)
    payment_caches = [
        (
            "Payment Method Cache",
            "Cache user's default payment method.",
            {"key_pattern": "user:{user_id}:payment_method", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Transaction Status Cache",
            "Cache recent transaction status for quick lookup.",
            {"key_pattern": "transaction:{txn_id}", "ttl": "5 minutes", "eviction": "LRU"},
        ),
        (
            "Wallet Balance Cache",
            "Cache user wallet balance.",
            {"key_pattern": "wallet:{user_id}:balance", "ttl": "1 minute", "eviction": "LRU"},
        ),
        (
            "Promotion Validation Cache",
            "Cache valid promotion codes.",
            {"key_pattern": "promo:{code}:valid", "ttl": "10 minutes", "eviction": "LRU"},
        ),
        (
            "Payment Hold Cache",
            "Cache active payment authorization holds.",
            {"key_pattern": "hold:{ride_id}", "ttl": "1 hour", "eviction": "TTL"},
        ),
        (
            "Refund Status Cache",
            "Cache refund processing status.",
            {"key_pattern": "refund:{refund_id}", "ttl": "10 minutes", "eviction": "LRU"},
        ),
    ]

    for name, desc, meta in payment_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Geocoding & Location Caching (7)
    geo_caches = [
        (
            "Geocode Cache",
            "Cache address to lat/lng conversions.",
            {"key_pattern": "geocode:{address_hash}", "ttl": "7 days", "eviction": "LRU"},
        ),
        (
            "Reverse Geocode Cache",
            "Cache lat/lng to address conversions.",
            {"key_pattern": "reverse_geocode:{lat}:{lng}", "ttl": "7 days", "eviction": "LRU"},
        ),
        (
            "Place Autocomplete Cache",
            "Cache address autocomplete results.",
            {"key_pattern": "autocomplete:{query_hash}", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Service Area Cache",
            "Cache active service area boundaries.",
            {"key_pattern": "service_areas:active", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Popular Destinations Cache",
            "Cache frequently requested destination addresses.",
            {"key_pattern": "popular:destinations:{city}", "ttl": "24 hours", "eviction": "LFU"},
        ),
        (
            "Favorite Locations Cache",
            "Cache user's saved favorite locations.",
            {"key_pattern": "user:{user_id}:favorites", "ttl": "30 minutes", "eviction": "LRU"},
        ),
        (
            "Traffic Conditions Cache",
            "Cache current traffic conditions for routes.",
            {"key_pattern": "traffic:{route_hash}", "ttl": "5 minutes", "eviction": "TTL"},
        ),
    ]

    for name, desc, meta in geo_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Configuration & Static Data Caching (6)
    config_caches = [
        (
            "App Configuration Cache",
            "Cache app feature flags and configuration.",
            {"key_pattern": "config:app", "ttl": "10 minutes", "eviction": "LRU"},
        ),
        (
            "Pricing Rules Cache",
            "Cache pricing calculation rules.",
            {"key_pattern": "config:pricing_rules", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Service Types Cache",
            "Cache available service types (standard, premium, shared).",
            {"key_pattern": "config:service_types", "ttl": "6 hours", "eviction": "LRU"},
        ),
        (
            "Vehicle Types Cache",
            "Cache vehicle type configurations.",
            {"key_pattern": "config:vehicle_types", "ttl": "6 hours", "eviction": "LRU"},
        ),
        (
            "Translation Cache",
            "Cache app translations by locale.",
            {"key_pattern": "i18n:{locale}", "ttl": "24 hours", "eviction": "LRU"},
        ),
        (
            "Rate Limit Counter",
            "Cache API rate limit counters per user.",
            {"key_pattern": "ratelimit:{user_id}:{endpoint}", "ttl": "1 minute", "eviction": "TTL"},
        ),
    ]

    for name, desc, meta in config_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Analytics & Aggregation Caching (6)
    analytics_caches = [
        (
            "Real-time Dashboard Metrics",
            "Cache current hour's KPI metrics.",
            {"key_pattern": "metrics:realtime", "ttl": "30 seconds", "eviction": "TTL"},
        ),
        (
            "Driver Performance Cache",
            "Cache driver stats for leaderboards.",
            {"key_pattern": "driver:{driver_id}:stats", "ttl": "15 minutes", "eviction": "LRU"},
        ),
        (
            "Hourly Ride Count Cache",
            "Cache ride counts by hour for charts.",
            {"key_pattern": "analytics:rides:hourly", "ttl": "5 minutes", "eviction": "LRU"},
        ),
        (
            "Revenue Summary Cache",
            "Cache daily/weekly revenue summaries.",
            {"key_pattern": "analytics:revenue:{period}", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "User Segment Cache",
            "Cache user segmentation for targeting.",
            {"key_pattern": "segment:{segment_id}:users", "ttl": "1 hour", "eviction": "LRU"},
        ),
        (
            "Popular Routes Cache",
            "Cache most common pickup/dropoff pairs.",
            {"key_pattern": "analytics:popular_routes", "ttl": "6 hours", "eviction": "LRU"},
        ),
    ]

    for name, desc, meta in analytics_caches:
        caches.append(
            create_item_file(
                "cache_strategies",
                f"CACHE-{counter:03d}",
                "cache_strategy",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    return caches


# ============================================================================
# QUEUE DEFINITIONS (70 items)
# ============================================================================


def generate_queue_definitions() -> list[Path]:
    """Generate 70 message queue topic items."""
    queues = []
    counter = 1

    # Ride Management Queues (12)
    ride_queues = [
        (
            "ride.requested",
            "New ride request event.",
            {"type": "Topic", "consumers": ["Matching Service", "Analytics"], "retention": "7 days"},
        ),
        (
            "ride.matched",
            "Ride matched to driver event.",
            {"type": "Topic", "consumers": ["Notification Service", "Analytics"], "retention": "7 days"},
        ),
        (
            "ride.accepted",
            "Driver accepted ride event.",
            {"type": "Topic", "consumers": ["Notification Service", "ETA Calculator"], "retention": "7 days"},
        ),
        (
            "ride.rejected",
            "Driver rejected ride event.",
            {"type": "Topic", "consumers": ["Matching Service", "Analytics"], "retention": "7 days"},
        ),
        (
            "ride.started",
            "Ride started event.",
            {"type": "Topic", "consumers": ["Tracking Service", "Payment Service"], "retention": "7 days"},
        ),
        (
            "ride.completed",
            "Ride completed event.",
            {"type": "Topic", "consumers": ["Payment Service", "Rating Service", "Analytics"], "retention": "30 days"},
        ),
        (
            "ride.cancelled",
            "Ride cancelled event.",
            {
                "type": "Topic",
                "consumers": ["Payment Service", "Notification Service", "Analytics"],
                "retention": "30 days",
            },
        ),
        (
            "ride.location_updated",
            "Driver location update event.",
            {"type": "Topic", "consumers": ["ETA Service", "Rider App"], "retention": "1 day"},
        ),
        (
            "ride.eta_updated",
            "ETA recalculated event.",
            {"type": "Topic", "consumers": ["Rider App", "Notification Service"], "retention": "1 day"},
        ),
        (
            "ride.rating_submitted",
            "Ride rating submitted event.",
            {"type": "Topic", "consumers": ["Driver Analytics", "User Analytics"], "retention": "90 days"},
        ),
        (
            "ride.scheduled",
            "Future ride scheduled event.",
            {"type": "Topic", "consumers": ["Scheduler Service", "Notification Service"], "retention": "30 days"},
        ),
        (
            "ride.sos_triggered",
            "Emergency SOS button pressed.",
            {"type": "Priority Queue", "consumers": ["Safety Service", "Support Team"], "retention": "365 days"},
        ),
    ]

    for name, desc, meta in ride_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Driver Management Queues (10)
    driver_queues = [
        (
            "driver.registered",
            "New driver registration event.",
            {"type": "Topic", "consumers": ["Verification Service", "Welcome Email"], "retention": "90 days"},
        ),
        (
            "driver.verified",
            "Driver background check completed.",
            {"type": "Topic", "consumers": ["Driver Onboarding", "Notification Service"], "retention": "90 days"},
        ),
        (
            "driver.online",
            "Driver went online event.",
            {"type": "Topic", "consumers": ["Matching Service", "Analytics"], "retention": "7 days"},
        ),
        (
            "driver.offline",
            "Driver went offline event.",
            {"type": "Topic", "consumers": ["Matching Service", "Analytics"], "retention": "7 days"},
        ),
        (
            "driver.location_updated",
            "Driver GPS location update.",
            {"type": "Topic", "consumers": ["Location Service", "Matching Service"], "retention": "1 day"},
        ),
        (
            "driver.earnings_calculated",
            "Driver earnings calculated for ride.",
            {"type": "Topic", "consumers": ["Payout Service", "Tax Service"], "retention": "365 days"},
        ),
        (
            "driver.payout_requested",
            "Driver requested payout.",
            {"type": "Queue", "consumers": ["Payout Service"], "retention": "90 days"},
        ),
        (
            "driver.document_uploaded",
            "Driver uploaded verification document.",
            {"type": "Queue", "consumers": ["Document Verification"], "retention": "90 days"},
        ),
        (
            "driver.suspended",
            "Driver account suspended.",
            {"type": "Topic", "consumers": ["Notification Service", "Matching Service"], "retention": "365 days"},
        ),
        (
            "driver.reactivated",
            "Driver account reactivated.",
            {"type": "Topic", "consumers": ["Notification Service", "Matching Service"], "retention": "365 days"},
        ),
    ]

    for name, desc, meta in driver_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # User Management Queues (8)
    user_queues = [
        (
            "user.registered",
            "New user account created.",
            {"type": "Topic", "consumers": ["Welcome Email", "Analytics", "CRM Sync"], "retention": "90 days"},
        ),
        (
            "user.verified",
            "User phone/email verified.",
            {"type": "Topic", "consumers": ["Notification Service", "Analytics"], "retention": "90 days"},
        ),
        (
            "user.profile_updated",
            "User profile information updated.",
            {"type": "Topic", "consumers": ["Cache Invalidation", "CRM Sync"], "retention": "30 days"},
        ),
        (
            "user.deleted",
            "User account deletion requested.",
            {"type": "Queue", "consumers": ["GDPR Compliance Service"], "retention": "365 days"},
        ),
        (
            "user.password_reset_requested",
            "Password reset requested.",
            {"type": "Queue", "consumers": ["Email Service"], "retention": "7 days"},
        ),
        (
            "user.payment_method_added",
            "Payment method added to account.",
            {"type": "Topic", "consumers": ["Stripe Sync", "Analytics"], "retention": "90 days"},
        ),
        (
            "user.referral_completed",
            "User completed referral requirement.",
            {"type": "Topic", "consumers": ["Referral Bonus Service", "Analytics"], "retention": "90 days"},
        ),
        (
            "user.session_expired",
            "User session expired.",
            {"type": "Topic", "consumers": ["Cache Cleanup"], "retention": "1 day"},
        ),
    ]

    for name, desc, meta in user_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Payment Processing Queues (12)
    payment_queues = [
        (
            "payment.initiated",
            "Payment process initiated for ride.",
            {"type": "Queue", "consumers": ["Payment Service"], "retention": "90 days"},
        ),
        (
            "payment.authorized",
            "Payment authorized (hold placed).",
            {"type": "Topic", "consumers": ["Ride Service", "Analytics"], "retention": "90 days"},
        ),
        (
            "payment.captured",
            "Payment successfully captured.",
            {"type": "Topic", "consumers": ["Receipt Service", "Accounting", "Analytics"], "retention": "365 days"},
        ),
        (
            "payment.failed",
            "Payment processing failed.",
            {"type": "Topic", "consumers": ["Retry Service", "Notification Service"], "retention": "90 days"},
        ),
        (
            "payment.refund_requested",
            "Refund requested for transaction.",
            {"type": "Queue", "consumers": ["Refund Service"], "retention": "365 days"},
        ),
        (
            "payment.refund_completed",
            "Refund successfully processed.",
            {"type": "Topic", "consumers": ["Notification Service", "Accounting"], "retention": "365 days"},
        ),
        (
            "payment.dispute_created",
            "Payment dispute/chargeback filed.",
            {"type": "Priority Queue", "consumers": ["Dispute Service", "Support Team"], "retention": "365 days"},
        ),
        (
            "payment.payout_scheduled",
            "Driver payout scheduled.",
            {"type": "Queue", "consumers": ["Payout Service"], "retention": "365 days"},
        ),
        (
            "payment.payout_completed",
            "Driver payout completed.",
            {"type": "Topic", "consumers": ["Notification Service", "Accounting"], "retention": "365 days"},
        ),
        (
            "payment.payout_failed",
            "Driver payout failed.",
            {"type": "Priority Queue", "consumers": ["Retry Service", "Support Team"], "retention": "365 days"},
        ),
        (
            "payment.wallet_credited",
            "User wallet credited.",
            {"type": "Topic", "consumers": ["Notification Service", "Cache Update"], "retention": "90 days"},
        ),
        (
            "payment.wallet_debited",
            "User wallet debited.",
            {"type": "Topic", "consumers": ["Notification Service", "Cache Update"], "retention": "90 days"},
        ),
    ]

    for name, desc, meta in payment_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Notification Queues (10)
    notification_queues = [
        (
            "notification.push.send",
            "Send push notification to device.",
            {"type": "Queue", "consumers": ["OneSignal Service"], "retention": "7 days"},
        ),
        (
            "notification.sms.send",
            "Send SMS message to user.",
            {"type": "Queue", "consumers": ["Twilio Service"], "retention": "30 days"},
        ),
        (
            "notification.email.send",
            "Send email to user.",
            {"type": "Queue", "consumers": ["SendGrid Service"], "retention": "30 days"},
        ),
        (
            "notification.in_app.create",
            "Create in-app notification.",
            {"type": "Queue", "consumers": ["In-App Notification Service"], "retention": "7 days"},
        ),
        (
            "notification.delivered",
            "Notification successfully delivered.",
            {"type": "Topic", "consumers": ["Analytics"], "retention": "30 days"},
        ),
        (
            "notification.failed",
            "Notification delivery failed.",
            {"type": "Topic", "consumers": ["Retry Service", "Analytics"], "retention": "30 days"},
        ),
        (
            "notification.clicked",
            "User clicked notification.",
            {"type": "Topic", "consumers": ["Analytics"], "retention": "30 days"},
        ),
        (
            "notification.batch.send",
            "Send batch notifications (marketing).",
            {"type": "Queue", "consumers": ["Batch Notification Service"], "retention": "30 days"},
        ),
        (
            "notification.preference_updated",
            "User notification preferences updated.",
            {"type": "Topic", "consumers": ["Notification Service Config"], "retention": "90 days"},
        ),
        (
            "notification.unsubscribe",
            "User unsubscribed from notifications.",
            {"type": "Topic", "consumers": ["Suppression List Manager"], "retention": "90 days"},
        ),
    ]

    for name, desc, meta in notification_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Analytics & Reporting Queues (8)
    analytics_queues = [
        (
            "analytics.event_tracked",
            "Application event tracked.",
            {"type": "Topic", "consumers": ["Event Analytics Service", "Data Warehouse"], "retention": "90 days"},
        ),
        (
            "analytics.ride_completed",
            "Ride completion metrics.",
            {"type": "Topic", "consumers": ["Ride Analytics", "Revenue Analytics"], "retention": "90 days"},
        ),
        (
            "analytics.user_behavior",
            "User behavior tracking event.",
            {"type": "Topic", "consumers": ["User Analytics", "ML Pipeline"], "retention": "90 days"},
        ),
        (
            "analytics.performance_metric",
            "App performance metric recorded.",
            {"type": "Topic", "consumers": ["APM Service", "Dashboard"], "retention": "30 days"},
        ),
        (
            "analytics.fraud_signal",
            "Fraud detection signal.",
            {"type": "Priority Queue", "consumers": ["Fraud Detection Service"], "retention": "365 days"},
        ),
        (
            "analytics.daily_rollup",
            "Daily metrics rollup trigger.",
            {"type": "Queue", "consumers": ["Batch Analytics Service"], "retention": "30 days"},
        ),
        (
            "analytics.report_generated",
            "Scheduled report generated.",
            {"type": "Topic", "consumers": ["Report Distribution Service"], "retention": "30 days"},
        ),
        (
            "analytics.export_requested",
            "Data export requested.",
            {"type": "Queue", "consumers": ["Export Service"], "retention": "30 days"},
        ),
    ]

    for name, desc, meta in analytics_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # System & Infrastructure Queues (10)
    system_queues = [
        (
            "system.error_logged",
            "Application error logged.",
            {"type": "Topic", "consumers": ["Error Tracking Service", "Alerting"], "retention": "30 days"},
        ),
        (
            "system.alert_triggered",
            "System alert triggered.",
            {"type": "Priority Queue", "consumers": ["PagerDuty", "Slack", "On-Call Engineer"], "retention": "90 days"},
        ),
        (
            "system.health_check",
            "Service health check result.",
            {"type": "Topic", "consumers": ["Monitoring Dashboard"], "retention": "7 days"},
        ),
        (
            "system.cache_invalidated",
            "Cache invalidation event.",
            {"type": "Topic", "consumers": ["Cache Service"], "retention": "1 day"},
        ),
        (
            "system.config_updated",
            "Configuration updated.",
            {"type": "Topic", "consumers": ["All Services"], "retention": "30 days"},
        ),
        (
            "system.deployment_completed",
            "Service deployment completed.",
            {"type": "Topic", "consumers": ["Monitoring", "Slack"], "retention": "90 days"},
        ),
        (
            "system.backup_completed",
            "Database backup completed.",
            {"type": "Topic", "consumers": ["Backup Verification Service"], "retention": "90 days"},
        ),
        (
            "system.audit_log",
            "Audit log event.",
            {"type": "Topic", "consumers": ["Audit Storage", "Compliance Service"], "retention": "365 days"},
        ),
        (
            "system.rate_limit_exceeded",
            "API rate limit exceeded.",
            {"type": "Topic", "consumers": ["Security Service", "Analytics"], "retention": "30 days"},
        ),
        (
            "system.dead_letter",
            "Failed message moved to dead letter queue.",
            {"type": "Dead Letter Queue", "consumers": ["Manual Review"], "retention": "90 days"},
        ),
    ]

    for name, desc, meta in system_queues:
        queues.append(
            create_item_file(
                "queue_definitions",
                f"QUEUE-{counter:03d}",
                "queue_definition",
                name,
                desc,
                priority="medium" if "dead_letter" not in name.lower() else "high",
                metadata=meta,
            ),
        )
        counter += 1

    return queues


# ============================================================================
# STREAM PROCESSOR DEFINITIONS (50 items)
# ============================================================================


def generate_stream_processors() -> list[Path]:
    """Generate 50 real-time stream processor items."""
    processors = []
    counter = 1

    # Real-time Ride Processing (10)
    ride_processors = [
        (
            "Real-time Ride Matcher",
            "Match incoming ride requests with available drivers in real-time.",
            {"input": "ride.requested stream", "output": "ride.matched events", "window": "1 second"},
        ),
        (
            "ETA Calculator Stream",
            "Calculate and update ETA continuously based on driver location.",
            {"input": "driver.location_updated stream", "output": "ride.eta_updated events", "window": "5 seconds"},
        ),
        (
            "Ride Status Aggregator",
            "Aggregate real-time ride status for dashboards.",
            {"input": "ride.* events", "output": "Real-time metrics", "window": "10 seconds tumbling"},
        ),
        (
            "Surge Pricing Engine",
            "Calculate dynamic surge multipliers based on supply/demand.",
            {"input": "driver.online + ride.requested", "output": "surge.updated events", "window": "1 minute sliding"},
        ),
        (
            "Driver Proximity Ranker",
            "Rank drivers by proximity and availability for ride matching.",
            {"input": "driver.location_updated stream", "output": "Ranked driver list", "window": "Real-time"},
        ),
        (
            "Ride Completion Aggregator",
            "Aggregate completed rides by region for capacity planning.",
            {"input": "ride.completed stream", "output": "Regional capacity metrics", "window": "5 minute tumbling"},
        ),
        (
            "Multi-ride Optimizer",
            "Optimize driver route for multiple concurrent rides (pool/shared).",
            {"input": "ride.requested stream", "output": "Optimized route", "window": "Real-time"},
        ),
        (
            "Cancellation Pattern Detector",
            "Detect abnormal cancellation patterns in real-time.",
            {"input": "ride.cancelled stream", "output": "Fraud alerts", "window": "10 minute sliding"},
        ),
        (
            "Wait Time Monitor",
            "Monitor rider wait times and trigger alerts for long waits.",
            {"input": "ride.requested + ride.matched", "output": "Wait time alerts", "window": "Real-time"},
        ),
        (
            "Ride Revenue Aggregator",
            "Aggregate ride revenue in real-time.",
            {"input": "payment.captured stream", "output": "Real-time revenue", "window": "1 minute tumbling"},
        ),
    ]

    for name, desc, meta in ride_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Driver Analytics Streams (8)
    driver_processors = [
        (
            "Driver Acceptance Rate Calculator",
            "Calculate rolling driver acceptance rate.",
            {
                "input": "ride.matched + ride.accepted + ride.rejected",
                "output": "Acceptance rate metric",
                "window": "1 hour sliding",
            },
        ),
        (
            "Driver Earnings Aggregator",
            "Aggregate driver earnings in real-time.",
            {"input": "driver.earnings_calculated stream", "output": "Current earnings", "window": "Real-time"},
        ),
        (
            "Driver Activity Monitor",
            "Track driver online/offline patterns.",
            {"input": "driver.online + driver.offline", "output": "Activity patterns", "window": "24 hour sliding"},
        ),
        (
            "Driver Rating Aggregator",
            "Calculate rolling average driver rating.",
            {"input": "ride.rating_submitted stream", "output": "Current rating", "window": "100 rides"},
        ),
        (
            "Driver Utilization Calculator",
            "Calculate driver utilization rate (active vs. available).",
            {
                "input": "ride.started + ride.completed + driver.online",
                "output": "Utilization rate",
                "window": "1 hour tumbling",
            },
        ),
        (
            "Driver Heatmap Generator",
            "Generate driver location heatmap data.",
            {"input": "driver.location_updated stream", "output": "Heatmap aggregates", "window": "5 minute tumbling"},
        ),
        (
            "Driver Incentive Tracker",
            "Track progress toward driver incentive goals.",
            {"input": "ride.completed stream", "output": "Incentive progress", "window": "Daily/Weekly"},
        ),
        (
            "Driver Churn Predictor",
            "Predict driver churn risk in real-time.",
            {"input": "driver.* events", "output": "Churn risk scores", "window": "7 day sliding"},
        ),
    ]

    for name, desc, meta in driver_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # User Behavior & Analytics Streams (8)
    user_processors = [
        (
            "User Session Aggregator",
            "Aggregate user session duration and actions.",
            {"input": "analytics.event_tracked stream", "output": "Session metrics", "window": "Session window"},
        ),
        (
            "User Lifetime Value Calculator",
            "Calculate rolling user LTV.",
            {"input": "payment.captured stream", "output": "LTV metric", "window": "Lifetime"},
        ),
        (
            "User Churn Predictor",
            "Predict user churn based on activity patterns.",
            {"input": "user.* + ride.* events", "output": "Churn risk scores", "window": "30 day sliding"},
        ),
        (
            "User Cohort Analyzer",
            "Analyze user cohorts by signup date.",
            {"input": "user.registered + ride.completed", "output": "Cohort metrics", "window": "Monthly"},
        ),
        (
            "User Engagement Scorer",
            "Calculate user engagement score.",
            {"input": "analytics.event_tracked stream", "output": "Engagement scores", "window": "7 day sliding"},
        ),
        (
            "User Segment Updater",
            "Update user segmentation in real-time.",
            {"input": "user.* + ride.* events", "output": "Segment assignments", "window": "Real-time"},
        ),
        (
            "Referral Conversion Tracker",
            "Track referral program conversions.",
            {
                "input": "user.registered + user.referral_completed",
                "output": "Conversion metrics",
                "window": "Real-time",
            },
        ),
        (
            "User Retention Calculator",
            "Calculate user retention rates by cohort.",
            {"input": "user.registered + ride.* events", "output": "Retention rates", "window": "Monthly"},
        ),
    ]

    for name, desc, meta in user_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    # Fraud Detection Streams (8)
    fraud_processors = [
        (
            "Payment Fraud Detector",
            "Detect fraudulent payment patterns in real-time.",
            {"input": "payment.* events", "output": "Fraud alerts", "window": "Real-time + ML model"},
        ),
        (
            "Velocity Fraud Detector",
            "Detect abnormal transaction velocity.",
            {"input": "payment.initiated stream", "output": "Velocity alerts", "window": "1 minute sliding"},
        ),
        (
            "Account Takeover Detector",
            "Detect suspicious login patterns.",
            {"input": "user.* events", "output": "ATO alerts", "window": "Real-time"},
        ),
        (
            "GPS Spoofing Detector",
            "Detect GPS coordinate manipulation.",
            {"input": "driver.location_updated stream", "output": "Spoofing alerts", "window": "Real-time"},
        ),
        (
            "Fake Ride Detector",
            "Detect collusion patterns for fake rides.",
            {"input": "ride.* events", "output": "Collusion alerts", "window": "24 hour sliding"},
        ),
        (
            "Promo Abuse Detector",
            "Detect promotional code abuse.",
            {"input": "payment.* + user.* events", "output": "Promo abuse alerts", "window": "Real-time"},
        ),
        (
            "Multi-Account Detector",
            "Detect users with multiple accounts.",
            {"input": "user.* events", "output": "Multi-account alerts", "window": "Real-time"},
        ),
        (
            "Chargeback Predictor",
            "Predict chargeback likelihood.",
            {"input": "payment.* + user.* events", "output": "Chargeback risk scores", "window": "Real-time + ML"},
        ),
    ]

    for name, desc, meta in fraud_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="critical",
                metadata=meta,
            ),
        )
        counter += 1

    # Operational Monitoring Streams (8)
    ops_processors = [
        (
            "Service Health Monitor",
            "Monitor service health metrics in real-time.",
            {"input": "system.health_check stream", "output": "Health status", "window": "1 minute tumbling"},
        ),
        (
            "Error Rate Calculator",
            "Calculate error rates by service.",
            {"input": "system.error_logged stream", "output": "Error rate metrics", "window": "5 minute sliding"},
        ),
        (
            "API Latency Monitor",
            "Monitor API endpoint latency.",
            {"input": "analytics.performance_metric stream", "output": "Latency alerts", "window": "1 minute sliding"},
        ),
        (
            "Queue Depth Monitor",
            "Monitor message queue depths.",
            {"input": "Queue metrics", "output": "Queue alerts", "window": "Real-time"},
        ),
        (
            "Database Performance Monitor",
            "Monitor database query performance.",
            {"input": "DB metrics stream", "output": "Performance alerts", "window": "1 minute sliding"},
        ),
        (
            "Cache Hit Rate Calculator",
            "Calculate cache hit rates.",
            {"input": "Cache metrics stream", "output": "Hit rate metrics", "window": "5 minute tumbling"},
        ),
        (
            "Resource Utilization Monitor",
            "Monitor CPU/memory/disk utilization.",
            {"input": "System metrics stream", "output": "Resource alerts", "window": "1 minute sliding"},
        ),
        (
            "SLA Compliance Checker",
            "Check SLA compliance in real-time.",
            {"input": "Service metrics stream", "output": "SLA breach alerts", "window": "Real-time"},
        ),
    ]

    for name, desc, meta in ops_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="high",
                metadata=meta,
            ),
        )
        counter += 1

    # Business Intelligence Streams (8)
    bi_processors = [
        (
            "Revenue Stream Aggregator",
            "Aggregate revenue by multiple dimensions.",
            {"input": "payment.captured stream", "output": "Revenue cube", "window": "1 hour tumbling"},
        ),
        (
            "Market Share Calculator",
            "Calculate market share by region.",
            {"input": "ride.completed stream", "output": "Market share metrics", "window": "Daily"},
        ),
        (
            "Customer Acquisition Cost",
            "Calculate CAC by channel.",
            {"input": "user.registered + marketing.* events", "output": "CAC metrics", "window": "Weekly"},
        ),
        (
            "Conversion Funnel Analyzer",
            "Analyze conversion rates through funnel.",
            {"input": "analytics.event_tracked stream", "output": "Funnel metrics", "window": "Session window"},
        ),
        (
            "Peak Hour Identifier",
            "Identify peak demand hours by region.",
            {"input": "ride.requested stream", "output": "Peak hour patterns", "window": "1 hour tumbling"},
        ),
        (
            "Popular Route Analyzer",
            "Identify most popular routes.",
            {"input": "ride.completed stream", "output": "Route popularity", "window": "Daily"},
        ),
        (
            "Service Type Distribution",
            "Analyze service type (standard/premium) distribution.",
            {"input": "ride.requested stream", "output": "Service mix", "window": "1 hour tumbling"},
        ),
        (
            "Promotion Effectiveness Tracker",
            "Track promotion code effectiveness.",
            {"input": "payment.* + promotion.* events", "output": "Promotion ROI", "window": "Campaign duration"},
        ),
    ]

    for name, desc, meta in bi_processors:
        processors.append(
            create_item_file(
                "stream_processors",
                f"STREAM-{counter:03d}",
                "stream_processor",
                name,
                desc,
                priority="medium",
                metadata=meta,
            ),
        )
        counter += 1

    return processors


# ============================================================================
# MAIN EXECUTION
# ============================================================================


def update_project_counters(counters: dict[str, int]) -> None:
    """Update project.yaml with new counters."""
    project_file = PROJECT_DIR / "project.yaml"

    with Path(project_file).open(encoding="utf-8") as f:
        project_data = yaml.safe_load(f)

    # Update counters
    for key, value in counters.items():
        project_data["counters"][key] = value

    with Path(project_file).open("w", encoding="utf-8") as f:
        yaml.dump(project_data, f, default_flow_style=False, sort_keys=False)


def main() -> None:
    """Generate all data & integration items."""
    # Generate all item types
    schemas = generate_database_schemas()
    apis = generate_external_apis()
    webhooks = generate_webhooks()
    pipelines = generate_data_pipelines()
    caches = generate_cache_strategies()
    queues = generate_queue_definitions()
    processors = generate_stream_processors()

    # Calculate totals
    (len(schemas) + len(apis) + len(webhooks) + len(pipelines) + len(caches) + len(queues) + len(processors))

    # Update project counters
    update_project_counters({
        "database_schema": 60,
        "external_api": 80,
        "webhook": 70,
        "data_pipeline": 60,
        "cache_strategy": 50,
        "queue_definition": 70,
        "stream_processor": 50,
    })


if __name__ == "__main__":
    main()
