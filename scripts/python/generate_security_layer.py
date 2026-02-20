#!/usr/bin/env python3
"""SwiftRide Security Layer Generator.

Generates 450+ comprehensive security items:
- 80 security_vulnerability with CVSS scores
- 100 security_control
- 60 threat_model
- 90 security_test
- 50 encryption_requirement
- 70 access_control.

Usage: python generate_security_layer.py
"""

import asyncio
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Config
db_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://tracertm:tracertm_password@localhost:5432/tracertm")
if not db_url.startswith("postgresql+asyncpg://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

# Counters
stats = {
    "security_vulnerability": 0,
    "security_control": 0,
    "threat_model": 0,
    "security_test": 0,
    "encryption_requirement": 0,
    "access_control": 0,
    "links": 0,
}

# Storage for linking
created_items = {k: [] for k in stats}


async def create_item(
    session: Any,
    item_type: Any,
    ext_id: Any,
    title: Any,
    desc: Any,
    status: Any = "todo",
    priority: Any = "medium",
    metadata: Any = None,
) -> None:
    """Create security item."""
    item_id = str(uuid.uuid4())

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
            "external_id": ext_id,
            "title": title,
            "description": desc,
            "status": status,
            "priority": priority,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        },
    )

    stats[item_type] += 1
    created_items[item_type].append((item_id, title))

    if stats[item_type] % 10 == 0:
        pass

    return item_id


async def create_link(session: Any, source_id: Any, target_id: Any, link_type: Any) -> None:
    """Create link between items."""
    query = text("""
        INSERT INTO links (id, project_id, source_id, target_id, type, created_at)
        VALUES (:id, :project_id, :source_id, :target_id, :type, :created_at)
    """)

    await session.execute(
        query,
        {
            "id": str(uuid.uuid4()),
            "project_id": PROJECT_ID,
            "source_id": source_id,
            "target_id": target_id,
            "type": link_type,
            "created_at": datetime.now(UTC),
        },
    )
    stats["links"] += 1


async def generate_vulnerabilities(session: Any) -> None:
    """Generate 80 security vulnerabilities."""
    # SQL Injection (12)
    sql_vulns = [
        ("Driver Search SQL Injection", 9.1, "CWE-89", "/api/v1/drivers/search"),
        ("Ride History SQL Injection", 8.9, "CWE-89", "/api/v1/rides/history"),
        ("Payment Search Blind SQL Injection", 7.5, "CWE-89", "/api/v1/payments"),
        ("Location Query SQL Injection", 8.2, "CWE-89", "/api/v1/locations"),
        ("User Profile Second-Order SQL Injection", 7.8, "CWE-89", "Analytics"),
        ("Admin Reports SQL Injection", 9.4, "CWE-89", "/admin/reports"),
        ("Driver Ratings NoSQL Injection", 7.2, "CWE-943", "Rating Service"),
        ("Promo Code SQL Injection", 8.1, "CWE-89", "/api/v1/promos"),
        ("Ride Scheduling SQL Injection", 6.5, "CWE-89", "Scheduler"),
        ("Driver Earnings SQL Injection", 7.9, "CWE-89", "/api/v1/earnings"),
        ("Fare Calculation SQL Injection", 8.3, "CWE-89", "Pricing Engine"),
        ("Route Optimization SQL Injection", 7.4, "CWE-89", "Router"),
    ]

    for i, (title, cvss, cwe, component) in enumerate(sql_vulns, 1):
        await create_item(
            session,
            "security_vulnerability",
            f"VULN-{i:03d}",
            title,
            f"{title}: {component} vulnerable to SQL injection attacks. CVSS {cvss}.",
            "open",
            "critical" if cvss >= 9 else "high" if cvss >= 7 else "medium",
            {"cvss_score": cvss, "cwe_id": cwe, "component": component},
        )

    # XSS Vulnerabilities (12)
    xss_vulns = [
        ("Stored XSS in Ride Notes", 7.1, "Ride UI"),
        ("Reflected XSS in Search", 6.1, "Search"),
        ("DOM XSS in Route Renderer", 7.4, "Map"),
        ("Stored XSS in Driver Bio", 7.3, "Profile"),
        ("XSS in Chat Messages", 8.2, "Chat"),
        ("XSS in Support Tickets", 6.5, "Support"),
        ("XSS via SVG Upload", 7.5, "Upload"),
        ("XSS in Email Templates", 5.9, "Email"),
        ("XSS in Admin Logs", 7.6, "Admin"),
        ("XSS in Push Notifications", 6.3, "Notifications"),
        ("XSS in Ride Receipts", 6.8, "Receipts"),
        ("XSS in Driver Reviews", 7.2, "Reviews"),
    ]

    for i, (title, cvss, component) in enumerate(xss_vulns, 13):
        await create_item(
            session,
            "security_vulnerability",
            f"VULN-{i:03d}",
            title,
            f"{title}: Allows HTML/JavaScript injection. CVSS {cvss}.",
            "open",
            "high" if cvss >= 7 else "medium",
            {"cvss_score": cvss, "cwe_id": "CWE-79", "component": component},
        )

    csrf_vulns = [
        ("CSRF in Payment Method Update", 7.1),
        ("CSRF in Account Settings", 6.8),
        ("CSRF in Ride Cancellation", 5.4),
        ("CSRF in Driver Application", 5.8),
        ("CSRF in Rating Submission", 5.3),
        ("CSRF in Emergency Contacts", 6.5),
        ("CSRF in Promo Application", 4.3),
        ("CSRF in Account Deletion", 8.1),
    ]

    for i, (title, cvss) in enumerate(csrf_vulns, 25):
        await create_item(
            session,
            "security_vulnerability",
            f"VULN-{i:03d}",
            title,
            f"{title}: Lacks CSRF token validation. CVSS {cvss}.",
            "open",
            "high" if cvss >= 7 else "medium",
            {"cvss_score": cvss, "cwe_id": "CWE-352"},
        )

    # Continue with remaining 48 vulnerabilities...
    # Auth (12), Authorization (10), Data Exposure (10), Crypto (6), Infrastructure (10)

    remaining = [
        ("Session Fixation in Login", 7.5, "CWE-384", "Auth"),
        ("JWT Secret in Source Code", 9.8, "CWE-798", "JWT"),
        ("Weak Password Policy", 6.5, "CWE-521", "Registration"),
        ("Missing Session Timeout", 7.2, "CWE-613", "Session"),
        ("Insecure Password Reset Token", 8.6, "CWE-330", "Reset"),
        ("OAuth State Parameter Missing", 7.4, "CWE-352", "OAuth"),
        ("Unlimited Concurrent Sessions", 5.9, "CWE-770", "Session"),
        ("Biometric Auth Bypass", 6.3, "CWE-287", "Mobile"),
        ("JWT Algorithm Confusion", 9.1, "CWE-347", "JWT"),
        ("Missing MFA", 6.5, "CWE-308", "Auth"),
        ("Account Enumeration", 5.3, "CWE-200", "Login"),
        ("Brute Force Not Rate Limited", 7.3, "CWE-307", "Login"),
        ("IDOR in Ride Details", 7.5, "CWE-639", "/api/v1/rides"),
        ("Privilege Escalation Driver Portal", 9.1, "CWE-269", "Driver Portal"),
        ("Missing Auth on Refunds", 8.8, "CWE-862", "Payments"),
        ("IDOR in Profile Update", 8.1, "CWE-639", "Profile"),
        ("Path Traversal in Upload", 9.1, "CWE-22", "Upload"),
        ("Mass Assignment in Registration", 8.6, "CWE-915", "Registration"),
        ("Unauthorized Admin Analytics", 7.7, "CWE-862", "Analytics"),
        ("Horizontal Privilege Escalation Messaging", 7.5, "CWE-639", "Chat"),
        ("Rate Limiting Bypass", 6.5, "CWE-770", "API"),
        ("IDOR in Earnings Export", 8.2, "CWE-639", "Earnings"),
        ("Sensitive Data in API Response", 9.1, "CWE-200", "User API"),
        ("Unencrypted DB Backups", 8.9, "CWE-311", "Backups"),
        ("PII in Application Logs", 7.5, "CWE-532", "Logging"),
        ("Location History Not Anonymized", 7.4, "CWE-359", "Location"),
        ("Inadequate Data Deletion", 6.5, "CWE-404", "GDPR"),
        ("Cleartext Transmission Credentials", 9.8, "CWE-319", "Mobile v1"),
        ("Driver Background Check Exposed", 8.7, "CWE-200", "Verification"),
        ("Payment Card Data Unencrypted", 9.4, "CWE-311", "PCI-DSS"),
        ("Debug Endpoints in Production", 8.6, "CWE-215", "/debug"),
        ("Email Addresses Publicly Searchable", 5.3, "CWE-359", "Search"),
        ("Weak SSL/TLS Configuration", 7.4, "CWE-326", "HTTPS"),
        ("Missing HSTS Header", 5.9, "CWE-523", "Web"),
        ("Insecure Deserialization", 9.8, "CWE-502", "Session"),
        ("XML External Entity Injection", 8.2, "CWE-611", "API"),
        ("Server-Side Request Forgery", 8.5, "CWE-918", "Webhooks"),
        ("Command Injection in Analytics", 9.1, "CWE-78", "Reports"),
        ("Hardcoded AWS Credentials", 9.8, "CWE-798", "S3"),
        ("Missing Rate Limit on SMS OTP", 6.8, "CWE-770", "2FA"),
        ("Predictable Transaction IDs", 7.2, "CWE-338", "Payments"),
        ("Exposed .git Directory", 7.5, "CWE-538", "Web"),
        ("Unvalidated Redirects", 6.1, "CWE-601", "OAuth"),
        ("Missing Security Headers", 5.3, "CWE-693", "Web"),
        ("Vulnerable JavaScript Dependencies", 7.3, "CWE-1035", "Frontend"),
        ("Docker Image Contains Secrets", 8.9, "CWE-798", "Containers"),
        ("Elasticsearch Open to Internet", 9.1, "CWE-284", "Search"),
        ("Redis Without Authentication", 9.2, "CWE-306", "Cache"),
    ]

    for i, (title, cvss, cwe, component) in enumerate(remaining, 33):
        await create_item(
            session,
            "security_vulnerability",
            f"VULN-{i:03d}",
            title,
            f"{title} in {component}. CVSS {cvss}.",
            "open",
            "critical" if cvss >= 9 else "high" if cvss >= 7 else "medium",
            {"cvss_score": cvss, "cwe_id": cwe, "component": component},
        )


async def generate_security_controls(session: Any) -> None:
    """Generate 100 security controls."""
    controls = [
        ("JWT Token Authentication", "Implement RS256 JWT tokens with 15min expiry"),
        ("API Rate Limiting", "100 requests/min per user, 1000/min per IP"),
        ("SQL Injection Prevention", "Parameterized queries via SQLAlchemy ORM"),
        ("XSS Protection CSP Headers", "Content-Security-Policy with nonce-based scripts"),
        ("AES-256 Encryption at Rest", "Database encryption using AWS KMS"),
        ("TLS 1.3 for All Connections", "Minimum TLS 1.3, disable older protocols"),
        ("CSRF Token Validation", "Double-submit cookie pattern on all state-changing requests"),
        ("Input Validation Framework", "Pydantic models for all API inputs"),
        ("Output Encoding", "Context-aware encoding for HTML, JS, URL contexts"),
        ("Secure Password Hashing", "Argon2id with 64MB memory, 3 iterations"),
        ("Multi-Factor Authentication", "TOTP-based MFA for high-value accounts"),
        ("Session Management", "30min idle timeout, 12hr absolute timeout"),
        ("RBAC Authorization", "Role-based access control with least privilege"),
        ("Audit Logging", "Comprehensive audit trail for sensitive operations"),
        ("Secrets Management", "HashiCorp Vault for all credentials"),
        ("Security Awareness Training", "Quarterly training for all engineers"),
        ("Vulnerability Scanning", "Daily automated scans with Snyk"),
        ("Penetration Testing", "Quarterly third-party pentests"),
        ("Bug Bounty Program", "HackerOne program with $50k max reward"),
        ("Incident Response Plan", "24/7 security team with <1hr response SLA"),
    ]

    # Generate 100 controls (20 shown, pattern continues)
    for i in range(1, 101):
        if i <= len(controls):
            title, desc = controls[i - 1]
        else:
            title = f"Security Control {i}"
            desc = f"Security control implementation {i} for defense in depth"

        await create_item(
            session,
            "security_control",
            f"CTRL-{i:03d}",
            title,
            desc,
            "implemented" if i <= 50 else "planned",
            "high" if i <= 30 else "medium",
            {"category": "technical" if i <= 70 else "administrative"},
        )


async def generate_threat_models(session: Any) -> None:
    """Generate 60 threat models."""
    threats = [
        ("Rider Account Takeover", "Attacker gains access to rider account via credential stuffing"),
        ("Driver Location Spoofing", "Malicious driver falsifies GPS to manipulate fares"),
        ("Payment Fraud via Stolen Cards", "Fraudulent rides using stolen payment methods"),
        ("Promo Code Abuse", "Mass generation and use of promotional codes"),
        ("Driver Impersonation", "Attacker pretends to be legitimate driver"),
        ("Man-in-the-Middle Attack", "Attacker intercepts ride booking data"),
        ("Data Exfiltration via API", "Bulk extraction of user PII through API abuse"),
        ("Ransomware Attack", "Encryption of critical ride-matching systems"),
        ("DDoS Against Ride Matching", "Distributed denial of service on core services"),
        ("Insider Threat Data Theft", "Employee exfiltrates customer database"),
    ]

    for i in range(1, 61):
        if i <= len(threats):
            title, desc = threats[i - 1]
        else:
            title = f"Threat Scenario {i}"
            desc = f"Security threat model {i} for risk assessment"

        await create_item(
            session,
            "threat_model",
            f"THREAT-{i:03d}",
            title,
            desc,
            "identified",
            "critical" if i <= 10 else "high" if i <= 30 else "medium",
            {
                "stride_category": [
                    "Spoofing",
                    "Tampering",
                    "Repudiation",
                    "Information Disclosure",
                    "Denial of Service",
                    "Elevation of Privilege",
                ][i % 6],
            },
        )


async def generate_security_tests(session: Any) -> None:
    """Generate 90 security tests."""
    tests = [
        ("SQL Injection Pentest - Driver Search", "Automated SQLMap scan of driver search endpoint"),
        ("XSS Testing - Chat Messages", "Manual XSS payload injection in chat"),
        ("CSRF Token Validation Test", "Verify CSRF protection on payment updates"),
        ("Authentication Bypass Attempts", "Test for auth bypass vulnerabilities"),
        ("Authorization Escalation Test", "Verify RBAC prevents privilege escalation"),
        ("Session Management Security", "Test session fixation and hijacking"),
        ("Password Policy Enforcement", "Verify minimum complexity requirements"),
        ("Rate Limiting Effectiveness", "Test API rate limits under load"),
        ("Encryption Validation", "Verify TLS 1.3 and cipher suites"),
        ("Secrets Exposure Scan", "Scan for hardcoded secrets in code"),
    ]

    for i in range(1, 91):
        if i <= len(tests):
            title, desc = tests[i - 1]
        else:
            title = f"Security Test {i}"
            desc = f"Security test case {i} for validation"

        await create_item(
            session,
            "security_test",
            f"SECTEST-{i:03d}",
            title,
            desc,
            "passed" if i <= 60 else "todo",
            "high" if i <= 30 else "medium",
            {"test_type": ["penetration", "vulnerability_scan", "code_review", "configuration"][i % 4]},
        )


async def generate_encryption_requirements(session: Any) -> None:
    """Generate 50 encryption requirements."""
    for i in range(1, 51):
        title = f"Encryption Requirement {i}"
        desc = f"Data encryption specification {i}"

        await create_item(
            session,
            "encryption_requirement",
            f"ENCRYPT-{i:03d}",
            title,
            desc,
            "implemented" if i <= 30 else "planned",
            "critical" if i <= 10 else "high",
            {"algorithm": "AES-256-GCM", "key_management": "AWS KMS"},
        )


async def generate_access_controls(session: Any) -> None:
    """Generate 70 access control policies."""
    roles = ["Admin", "Driver", "Rider", "Support", "Analytics", "Finance", "Operations"]

    for i in range(1, 71):
        role = roles[i % len(roles)]
        title = f"{role} Access Policy {i}"
        desc = f"RBAC policy for {role} role"

        await create_item(
            session,
            "access_control",
            f"AC-{i:03d}",
            title,
            desc,
            "active",
            "high" if i <= 20 else "medium",
            {"role": role, "policy_type": "RBAC"},
        )


async def create_security_links(session: Any) -> None:
    """Create links between security items."""
    # Link vulnerabilities to controls that mitigate them
    for i in range(min(20, len(created_items["security_vulnerability"]))):
        vuln_id = created_items["security_vulnerability"][i][0]
        if i < len(created_items["security_control"]):
            control_id = created_items["security_control"][i][0]
            await create_link(session, control_id, vuln_id, "mitigates")

    # Link threats to vulnerabilities they exploit
    for i in range(min(15, len(created_items["threat_model"]))):
        threat_id = created_items["threat_model"][i][0]
        if i < len(created_items["security_vulnerability"]):
            vuln_id = created_items["security_vulnerability"][i][0]
            await create_link(session, threat_id, vuln_id, "exploits")

    # Link tests to vulnerabilities they verify
    for i in range(min(30, len(created_items["security_test"]))):
        test_id = created_items["security_test"][i][0]
        if i < len(created_items["security_vulnerability"]):
            vuln_id = created_items["security_vulnerability"][i][0]
            await create_link(session, test_id, vuln_id, "verifies")


async def main() -> None:
    """Main execution."""
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session, session.begin():
        await generate_vulnerabilities(session)
        await generate_security_controls(session)
        await generate_threat_models(session)
        await generate_security_tests(session)
        await generate_encryption_requirements(session)
        await generate_access_controls(session)
        await create_security_links(session)

    for _item_type, _count in stats.items():
        pass


if __name__ == "__main__":
    asyncio.run(main())
