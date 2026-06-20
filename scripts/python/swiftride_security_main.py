#!/usr/bin/env python3
"""Main execution script for SwiftRide Security Layer Generation.

Generates 450+ security items across 6 categories with comprehensive linking.
"""

import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

# Database setup
db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm")
if not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")
DATABASE_URL = db_url
PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

# Counters for item generation
counters = {
    "security_vulnerability": 0,
    "security_control": 0,
    "threat_model": 0,
    "security_test": 0,
    "encryption_requirement": 0,
    "access_control": 0,
}

# Item storage for linking
items_db: dict[str, list[tuple[str, str]]] = {  # type -> [(id, title)]
    "security_vulnerability": [],
    "security_control": [],
    "threat_model": [],
    "security_test": [],
    "encryption_requirement": [],
    "access_control": [],
}


async def create_item(
    session: AsyncSession,
    title: str,
    item_type: str,
    description: str,
    status: str = "todo",
    priority: str = "medium",
    metadata: dict | None = None,
) -> str:
    """Create a security item in the database."""
    item_id = str(uuid.uuid4())
    counters[item_type] += 1
    external_id = f"{item_type.upper().replace('_', '-')}-{counters[item_type]:03d}"

    now = datetime.now(UTC)

    query = text("""
        INSERT INTO items (
            id, project_id, type, external_id, title, description,
            status, priority, metadata, created_at, updated_at, version
        ) VALUES (
            :id, :project_id, :type, :external_id, :title, :description,
            :status, :priority, :metadata::jsonb, :created_at, :updated_at, 1
        )
    """)

    await session.execute(
        query,
        {
            "id": item_id,
            "project_id": PROJECT_ID,
            "type": item_type,
            "external_id": external_id,
            "title": title,
            "description": description,
            "status": status,
            "priority": priority,
            "metadata": json.dumps(metadata or {}),
            "created_at": now,
            "updated_at": now,
        },
    )

    items_db[item_type].append((item_id, title))
    return item_id


async def create_link(
    session: AsyncSession, source_id: str, target_id: str, link_type: str, metadata: dict | None = None
) -> None:
    """Create a link between items."""
    link_id = str(uuid.uuid4())

    query = text("""
        INSERT INTO links (
            id, project_id, source_id, target_id, type, metadata, created_at
        ) VALUES (
            :id, :project_id, :source_id, :target_id, :type, :metadata::jsonb, :created_at
        )
    """)

    await session.execute(
        query,
        {
            "id": link_id,
            "project_id": PROJECT_ID,
            "source_id": source_id,
            "target_id": target_id,
            "type": link_type,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now(UTC),
        },
    )


# === SECURITY VULNERABILITY DATA (80 items) ===
# Organized by category for comprehensive coverage

VULNERABILITIES = {
    "sql_injection": [
        (
            "SQL Injection in Driver Search Query",
            "critical",
            9.1,
            "Driver search endpoint vulnerable to SQL injection via unparameterized name filter",
            "Driver Search API (/api/v1/drivers/search)",
            "Use parameterized queries with SQLAlchemy ORM",
        ),
        (
            "SQL Injection in Ride History Filter",
            "critical",
            8.9,
            "Ride history endpoint constructs SQL queries using string concatenation",
            "Ride History API",
            "Migrate to ORM queries, implement input validation",
        ),
        (
            "Blind SQL Injection in Payment Search",
            "high",
            7.5,
            "Payment transaction search vulnerable to time-based blind SQL injection",
            "Payment Search API",
            "Use prepared statements, implement rate limiting",
        ),
        (
            "SQL Injection in Location Query",
            "high",
            8.2,
            "Geospatial queries vulnerable to injection via latitude/longitude parameters",
            "Location API",
            "Validate numeric inputs, use PostGIS parameterized functions",
        ),
        (
            "Second-Order SQL Injection in User Profile",
            "high",
            7.8,
            "Stored user profile data later used in unsafe SQL queries",
            "User Profile Service",
            "Sanitize stored data, use ORM for all queries",
        ),
        (
            "SQL Injection in Admin Reports",
            "critical",
            9.4,
            "Custom report generation uses dynamic SQL construction",
            "Admin Dashboard",
            "Use query builder, implement SQL injection WAF rules",
        ),
        (
            "NoSQL Injection in Driver Ratings",
            "high",
            7.2,
            "MongoDB queries vulnerable to operator injection via rating filters",
            "Driver Rating Service",
            "Sanitize MongoDB operators, use strict schema validation",
        ),
        (
            "SQL Injection in Promo Code Validation",
            "high",
            8.1,
            "Promotional code validation endpoint vulnerable to union-based injection",
            "Promo Code API",
            "Use parameterized queries, strict input validation",
        ),
    ],
    "xss": [
        (
            "Stored XSS in Ride Notes",
            "high",
            7.1,
            "Ride notes allow HTML input rendered without sanitization",
            "Ride Details UI",
            "Implement DOMPurify sanitization, use textContent",
        ),
        (
            "Reflected XSS in Search Results",
            "medium",
            6.1,
            "Search query parameter reflected in page without encoding",
            "Search UI",
            "Encode all output, implement CSP headers",
        ),
        (
            "DOM-Based XSS in Route Rendering",
            "high",
            7.4,
            "Client-side route rendering vulnerable to DOM XSS via URL parameters",
            "Map Route Renderer",
            "Use React safe rendering, validate URL parameters",
        ),
        (
            "Stored XSS in Driver Bio",
            "high",
            7.3,
            "Driver profile bio field stores and displays unescaped HTML",
            "Driver Profile",
            "Sanitize bio input, use markdown-only format",
        ),
        (
            "XSS in Chat Messages",
            "critical",
            8.2,
            "In-app chat allows JavaScript execution via malicious messages",
            "Chat Service",
            "Implement message sanitization, use safe rendering",
        ),
        (
            "XSS in Support Tickets",
            "medium",
            6.5,
            "Support ticket descriptions rendered without HTML encoding",
            "Support Dashboard",
            "Encode user-generated content, implement CSP",
        ),
        (
            "XSS via SVG Upload",
            "high",
            7.5,
            "Profile images allow SVG files with embedded JavaScript",
            "Image Upload",
            "Block SVG uploads or sanitize, serve from CDN",
        ),
        (
            "XSS in Email Templates",
            "medium",
            5.9,
            "Email templates render user data without HTML encoding",
            "Email Service",
            "Use email-safe templating with auto-escaping",
        ),
    ],
    "csrf": [
        (
            "CSRF in Payment Method Update",
            "high",
            7.1,
            "Payment method update endpoint lacks CSRF token validation",
            "Payment API",
            "Implement CSRF tokens, use SameSite cookies",
        ),
        (
            "CSRF in Account Settings",
            "high",
            6.8,
            "Email and phone changes vulnerable to CSRF attacks",
            "Account Settings",
            "Add CSRF protection, require password confirmation",
        ),
        (
            "CSRF in Ride Cancellation",
            "medium",
            5.4,
            "Ride cancellation endpoint can be triggered via CSRF",
            "Ride Management",
            "Implement CSRF tokens for state-changing operations",
        ),
        (
            "CSRF in Driver Application",
            "medium",
            5.8,
            "Driver application form vulnerable to automated CSRF submissions",
            "Driver Onboarding",
            "Add CSRF protection and CAPTCHA",
        ),
        (
            "CSRF in Rating Submission",
            "medium",
            5.3,
            "Driver/rider rating submission lacks CSRF protection",
            "Rating API",
            "Implement double-submit cookie pattern",
        ),
        (
            "CSRF in Emergency Contact Update",
            "high",
            6.5,
            "Emergency contact modification vulnerable to CSRF",
            "Safety Settings",
            "Add CSRF tokens, implement confirmation",
        ),
        (
            "CSRF in Account Deletion",
            "critical",
            8.1,
            "Account deletion can be triggered via CSRF attack",
            "Account Management",
            "CSRF protection with email confirmation required",
        ),
    ],
}

# Continue in next part...
