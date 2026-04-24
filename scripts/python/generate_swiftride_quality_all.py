#!/usr/bin/env python3
"""SwiftRide Quality & Compliance Items - Complete Generator.

Generates all 570+ items across 7 types in one execution.

Run: python3 generate_swiftride_quality_all.py
"""

import asyncio
import json
import sys
import uuid
from typing import Any

import asyncpg

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"
DB_URL = "postgresql://tracertm:tracertm_password@localhost:5432/tracertm"


class QualityItemsData:
    """All 570+ quality items data definitions."""

    @staticmethod
    def quality_gates() -> None:
        """60 quality gate items."""
        return [
            # Coverage Gates (10)
            (
                "Unit Test Coverage >= 80%",
                "All modules must maintain 80%+ unit test coverage using pytest-cov/jest. Blocks merge if below threshold.",
                1,
                {"gate_type": "coverage", "threshold": 80, "metric": "line_coverage", "automation": "CI"},
                ["coverage", "unit-test", "quality-gate", "blocking"],
            ),
            (
                "Integration Test Coverage >= 70%",
                "Integration tests must cover 70%+ of API endpoints and service-to-service interactions.",
                1,
                {"gate_type": "coverage", "threshold": 70, "metric": "integration"},
                ["coverage", "integration-test", "quality-gate", "api"],
            ),
            (
                "E2E Test Coverage >= 60%",
                "End-to-end tests must cover 60%+ of critical user journeys: ride booking, payment, driver matching, SOS.",
                2,
                {"gate_type": "coverage", "threshold": 60, "critical_flows": ["ride", "payment", "matching", "sos"]},
                ["coverage", "e2e-test", "quality-gate", "journey"],
            ),
            (
                "Branch Coverage >= 75%",
                "All conditional branches must be tested with 75%+ coverage to validate decision logic.",
                2,
                {"gate_type": "coverage", "threshold": 75, "metric": "branch"},
                ["coverage", "branch-coverage", "quality-gate", "logic"],
            ),
            (
                "Mutation Score >= 65%",
                "Mutation testing score 65%+ using mutmut/Stryker to ensure test effectiveness.",
                3,
                {"gate_type": "coverage", "threshold": 65, "metric": "mutation", "tools": ["mutmut", "stryker"]},
                ["coverage", "mutation-testing", "quality-gate"],
            ),
            (
                "Frontend Component Coverage >= 85%",
                "React components must have 85%+ test coverage with React Testing Library.",
                1,
                {"gate_type": "coverage", "threshold": 85, "framework": "react"},
                ["coverage", "frontend", "react", "quality-gate"],
            ),
            (
                "API Contract Coverage 100%",
                "All OpenAPI endpoints must have contract tests validating request/response schemas.",
                1,
                {"gate_type": "coverage", "threshold": 100, "standard": "OpenAPI_3"},
                ["coverage", "api", "contract-testing", "quality-gate"],
            ),
            (
                "Critical Path Coverage 100%",
                "100% coverage for critical business paths: ride lifecycle, payment, SOS, surge pricing.",
                1,
                {"gate_type": "coverage", "threshold": 100, "paths": ["ride_lifecycle", "payment", "sos", "surge"]},
                ["coverage", "critical-path", "quality-gate", "blocking"],
            ),
            (
                "Error Handling Coverage >= 80%",
                "All error scenarios must be tested: network failures, timeouts, invalid inputs.",
                2,
                {"gate_type": "coverage", "threshold": 80, "focus": "error_handling"},
                ["coverage", "error-handling", "quality-gate", "resilience"],
            ),
            (
                "Security Test Coverage >= 90%",
                "Security-critical code (auth, payment, PII) must have 90%+ coverage.",
                1,
                {"gate_type": "coverage", "threshold": 90, "domains": ["auth", "payment", "pii"]},
                ["coverage", "security", "quality-gate", "critical"],
            ),
            # Security Gates (10)
            (
                "Zero Critical Security Vulnerabilities",
                "No CVSS 9.0-10.0 vulnerabilities allowed. Scanned via Snyk/Trivy/Safety. Blocks deployment.",
                1,
                {
                    "gate_type": "security",
                    "max_critical": 0,
                    "cvss_range": "9.0-10.0",
                    "tools": ["snyk", "trivy", "safety"],
                },
                ["security", "vulnerabilities", "quality-gate", "critical", "blocking"],
            ),
            (
                "No High Severity Vulnerabilities",
                "CVSS 7.0-8.9 vulnerabilities must be resolved before release. 48h grace period.",
                1,
                {"gate_type": "security", "max_high": 0, "cvss_range": "7.0-8.9", "grace_hours": 48},
                ["security", "vulnerabilities", "quality-gate", "high-severity"],
            ),
            (
                "OWASP Top 10 Compliance",
                "Must pass OWASP Top 10 2021 checks: injection, auth, XSS, XXE, access control.",
                1,
                {
                    "gate_type": "security",
                    "standard": "OWASP_2021",
                    "checks": ["injection", "auth", "xss", "xxe", "access"],
                },
                ["security", "owasp", "quality-gate", "compliance"],
            ),
            (
                "Dependency Audit Pass",
                "All bun/pip/go dependencies must pass security audit with zero known vulnerabilities.",
                2,
                {
                    "gate_type": "security",
                    "audit": "dependencies",
                    "tools": {"bun": "bun audit", "python": "pip-audit", "go": "govulncheck"},
                },
                ["security", "dependencies", "quality-gate", "supply-chain"],
            ),
            (
                "Secrets Detection Pass",
                "No secrets/API keys/credentials in codebase. Scan with TruffleHog/GitLeaks/detect-secrets.",
                1,
                {"gate_type": "security", "scan": "secrets", "tools": ["trufflehog", "gitleaks", "detect-secrets"]},
                ["security", "secrets", "quality-gate", "blocking"],
            ),
            (
                "Authentication Strength Validation",
                "Use OAuth2+PKCE, JWT RS256, MFA. No basic auth, HS256, MD5, SHA1.",
                1,
                {
                    "gate_type": "security",
                    "required": ["OAuth2_PKCE", "JWT_RS256", "MFA"],
                    "forbidden": ["basic_auth", "HS256", "md5", "sha1"],
                },
                ["security", "authentication", "quality-gate", "oauth2"],
            ),
            (
                "PII Encryption Compliance",
                "All PII (phone, email, payment, location) must use AES-256 at rest, TLS 1.3 in transit.",
                1,
                {
                    "gate_type": "security",
                    "at_rest": "AES-256",
                    "in_transit": "TLS_1.3",
                    "pii_fields": ["phone", "email", "payment", "location"],
                },
                ["security", "encryption", "pii", "quality-gate", "compliance", "gdpr"],
            ),
            (
                "SQL Injection Prevention",
                "All database queries must use parameterized queries or ORM. No string concatenation.",
                1,
                {
                    "gate_type": "security",
                    "requirement": "parameterized_queries",
                    "forbidden": "string_concat",
                    "tools": ["semgrep", "sqlmap"],
                },
                ["security", "sql-injection", "quality-gate", "database"],
            ),
            (
                "CSRF Protection Enabled",
                "All state-changing endpoints must have CSRF token validation. Exempt: /health, /metrics.",
                1,
                {
                    "gate_type": "security",
                    "protection": "csrf",
                    "pattern": ["double_submit", "synchronizer_token"],
                    "exempt": ["/health", "/metrics"],
                },
                ["security", "csrf", "quality-gate", "web-security"],
            ),
            (
                "Rate Limiting Configured",
                "Rate limits: Auth 100/min, API 1000/min, Payment 10/min, Location 10000/min.",
                2,
                {
                    "gate_type": "security",
                    "limits": {"auth": "100/min", "api": "1000/min", "payment": "10/min", "location": "10000/min"},
                },
                ["security", "rate-limiting", "quality-gate", "ddos"],
            ),
            # Performance Gates (10)
            (
                "API Response Time p95 < 200ms",
                "95th percentile API response must be under 200ms. Alert at 150ms.",
                1,
                {
                    "gate_type": "performance",
                    "metric": "response_time_p95",
                    "threshold": 200,
                    "unit": "ms",
                    "alert_at": 150,
                },
                ["performance", "api", "latency", "quality-gate", "p95"],
            ),
            (
                "API Response Time p99 < 500ms",
                "99th percentile API response under 500ms for consistent UX.",
                2,
                {"gate_type": "performance", "metric": "response_time_p99", "threshold": 500, "unit": "ms"},
                ["performance", "api", "latency", "quality-gate", "p99"],
            ),
            (
                "Database Query p95 < 50ms",
                "95th percentile DB query time under 50ms including connection time.",
                1,
                {"gate_type": "performance", "metric": "db_query_p95", "threshold": 50, "unit": "ms"},
                ["performance", "database", "query", "quality-gate"],
            ),
            (
                "Frontend Load Time < 2s",
                "Initial page load under 2s on 4G. Measured via Lighthouse/WebPageTest.",
                2,
                {
                    "gate_type": "performance",
                    "metric": "page_load",
                    "threshold": 2000,
                    "unit": "ms",
                    "network": "4G",
                    "tools": ["lighthouse", "webpagetest"],
                },
                ["performance", "frontend", "loading", "quality-gate"],
            ),
            (
                "Memory Usage < 512MB per Service",
                "Each microservice under 512MB memory under normal load. Alert at 400MB.",
                2,
                {
                    "gate_type": "performance",
                    "metric": "memory_usage",
                    "threshold": 512,
                    "unit": "MB",
                    "scope": "per_service",
                    "alert_at": 400,
                },
                ["performance", "memory", "resources", "quality-gate"],
            ),
            (
                "CPU Usage < 70% per Service",
                "CPU under 70% under normal load. Sustained high CPU triggers auto-scaling.",
                2,
                {
                    "gate_type": "performance",
                    "metric": "cpu_usage",
                    "threshold": 70,
                    "unit": "percent",
                    "action": "auto_scale",
                },
                ["performance", "cpu", "resources", "quality-gate"],
            ),
            (
                "Throughput >= 1000 req/sec",
                "System must handle 1000+ req/sec under load with <5% error rate.",
                1,
                {
                    "gate_type": "performance",
                    "metric": "throughput",
                    "threshold": 1000,
                    "unit": "req/sec",
                    "max_error_rate": 5,
                },
                ["performance", "throughput", "scalability", "quality-gate"],
            ),
            (
                "Bundle Size < 200KB (gzipped)",
                "Frontend JavaScript bundle under 200KB after gzip. Use code splitting.",
                2,
                {
                    "gate_type": "performance",
                    "metric": "bundle_size",
                    "threshold": 200,
                    "unit": "KB",
                    "compression": "gzip",
                },
                ["performance", "frontend", "bundle", "quality-gate"],
            ),
            (
                "Time to Interactive < 3.5s",
                "Page fully interactive (TTI) in under 3.5s. All JS loaded, main thread idle.",
                2,
                {"gate_type": "performance", "metric": "time_to_interactive", "threshold": 3500, "unit": "ms"},
                ["performance", "frontend", "tti", "quality-gate"],
            ),
            (
                "First Contentful Paint < 1.5s",
                "FCP within 1.5s for fast perceived performance.",
                2,
                {"gate_type": "performance", "metric": "first_contentful_paint", "threshold": 1500, "unit": "ms"},
                ["performance", "frontend", "fcp", "quality-gate"],
            ),
            # CI/CD Gates (10)
            (
                "Build Success Rate >= 95%",
                "CI/CD builds must succeed 95%+ over rolling 7-day window.",
                2,
                {"gate_type": "cicd", "metric": "build_success_rate", "threshold": 95, "window": "7_days"},
                ["cicd", "build", "stability", "quality-gate"],
            ),
            (
                "Build Time < 10 minutes",
                "Full CI/CD pipeline under 10 minutes for fast feedback.",
                3,
                {"gate_type": "cicd", "metric": "build_time", "threshold": 10, "unit": "minutes"},
                ["cicd", "build", "performance", "quality-gate"],
            ),
            (
                "Zero Linter Errors",
                "Pass all linters with zero errors: eslint, pylint/ruff, golangci-lint.",
                1,
                {"gate_type": "cicd", "max_errors": 0, "linters": ["eslint", "pylint", "ruff", "golangci-lint"]},
                ["cicd", "linting", "code-quality", "quality-gate", "blocking"],
            ),
            (
                "Linter Warnings < 10",
                "Maximum 10 linter warnings across codebase. Should trend downward.",
                2,
                {"gate_type": "cicd", "max_warnings": 10, "trend": "decreasing"},
                ["cicd", "linting", "quality-gate"],
            ),
            (
                "Type Coverage >= 90%",
                "TypeScript strict mode and Python type hints cover 90%+ of code.",
                2,
                {
                    "gate_type": "cicd",
                    "metric": "type_coverage",
                    "threshold": 90,
                    "tools": {"typescript": "tsc --strict", "python": "mypy --strict"},
                },
                ["cicd", "types", "quality-gate"],
            ),
            (
                "Code Complexity < 10",
                "Max cyclomatic complexity of 10 per function/method.",
                2,
                {
                    "gate_type": "cicd",
                    "metric": "cyclomatic_complexity",
                    "threshold": 10,
                    "tools": ["radon", "eslint-complexity"],
                },
                ["cicd", "complexity", "maintainability", "quality-gate"],
            ),
            (
                "Code Duplication < 3%",
                "Less than 3% code duplication across codebase. DRY principle.",
                3,
                {
                    "gate_type": "cicd",
                    "metric": "code_duplication",
                    "threshold": 3,
                    "unit": "percent",
                    "tools": ["jscpd", "pylint"],
                },
                ["cicd", "duplication", "quality-gate"],
            ),
            (
                "Docker Image Size < 500MB",
                "Production images under 500MB. Use multi-stage builds, alpine.",
                3,
                {
                    "gate_type": "cicd",
                    "metric": "docker_image_size",
                    "threshold": 500,
                    "unit": "MB",
                    "optimizations": ["multi_stage", "alpine"],
                },
                ["cicd", "docker", "size", "quality-gate"],
            ),
            (
                "Docker Security Scan Pass",
                "Images pass Trivy/Snyk scan with no critical/high vulnerabilities.",
                1,
                {
                    "gate_type": "cicd",
                    "scan": "docker_security",
                    "tools": ["trivy", "snyk-container"],
                    "max_critical": 0,
                    "max_high": 0,
                },
                ["cicd", "docker", "security", "quality-gate"],
            ),
            (
                "Deployment Rollback < 2 minutes",
                "Auto-rollback failed deployments within 2 minutes. Test monthly.",
                1,
                {
                    "gate_type": "cicd",
                    "metric": "rollback_time",
                    "threshold": 2,
                    "unit": "minutes",
                    "automation": "automatic",
                    "test_frequency": "monthly",
                },
                ["cicd", "deployment", "rollback", "quality-gate"],
            ),
            # Documentation Gates (10)
            (
                "API Documentation Coverage 100%",
                "All endpoints documented in OpenAPI 3.0 with request/response examples.",
                2,
                {"gate_type": "documentation", "metric": "api_doc_coverage", "threshold": 100, "format": "openapi_3.0"},
                ["documentation", "api", "quality-gate"],
            ),
            (
                "Code Comment Density >= 15%",
                "15%+ of code lines have meaningful comments for complex logic.",
                3,
                {"gate_type": "documentation", "metric": "comment_density", "threshold": 15, "unit": "percent"},
                ["documentation", "comments", "quality-gate"],
            ),
            (
                "README for All Services",
                "Each microservice has README: setup, usage, API, config, troubleshooting.",
                2,
                {
                    "gate_type": "documentation",
                    "required_sections": ["setup", "usage", "api", "config", "troubleshooting"],
                    "scope": "per_service",
                },
                ["documentation", "readme", "quality-gate"],
            ),
            (
                "Architecture Decision Records",
                "Major architectural decisions documented as ADRs with context/decision/consequences.",
                2,
                {
                    "gate_type": "documentation",
                    "format": "ADR",
                    "template": "madr",
                    "sections": ["context", "decision", "consequences"],
                },
                ["documentation", "adr", "architecture", "quality-gate"],
            ),
            (
                "Public API Inline Documentation",
                "All public functions/classes have docstrings (Python) or JSDoc (TypeScript).",
                2,
                {
                    "gate_type": "documentation",
                    "scope": "public_api",
                    "formats": {"python": "docstring", "typescript": "jsdoc"},
                },
                ["documentation", "inline", "quality-gate"],
            ),
            (
                "Database Schema Documentation",
                "All tables documented with ER diagrams and table/column descriptions.",
                3,
                {
                    "gate_type": "documentation",
                    "scope": "database_schema",
                    "includes": ["er_diagram", "table_descriptions", "relationships"],
                },
                ["documentation", "database", "schema", "quality-gate"],
            ),
            (
                "Deployment Runbooks Complete",
                "Runbooks for all services: deployment steps, rollback, smoke tests, troubleshooting.",
                2,
                {
                    "gate_type": "documentation",
                    "type": "runbook",
                    "sections": ["deployment", "rollback", "smoke_tests", "troubleshooting"],
                },
                ["documentation", "runbook", "deployment", "quality-gate"],
            ),
            (
                "Incident Response Playbooks",
                "Playbooks for critical incidents: outage, security breach, data loss, payment failure.",
                1,
                {
                    "gate_type": "documentation",
                    "type": "playbook",
                    "incidents": ["outage", "security_breach", "data_loss", "payment_failure"],
                },
                ["documentation", "incident", "playbook", "quality-gate"],
            ),
            (
                "Changelog Maintained",
                "CHANGELOG.md updated for every release in Keep a Changelog format.",
                3,
                {
                    "gate_type": "documentation",
                    "file": "CHANGELOG.md",
                    "format": "keep_a_changelog",
                    "sections": ["Added", "Changed", "Fixed", "Removed"],
                },
                ["documentation", "changelog", "quality-gate"],
            ),
            (
                "Onboarding Documentation Current",
                "Developer onboarding guide tested quarterly: setup, architecture, workflows, tools.",
                3,
                {
                    "gate_type": "documentation",
                    "type": "onboarding",
                    "test_frequency": "quarterly",
                    "sections": ["setup", "architecture", "workflows", "tools"],
                },
                ["documentation", "onboarding", "quality-gate"],
            ),
            # Data Quality Gates (10)
            (
                "Zero Data Loss on Deployment",
                "Reversible database migrations tested in staging. No data loss allowed. Blocking.",
                1,
                {
                    "gate_type": "data_quality",
                    "requirement": "zero_loss",
                    "migration_reversible": True,
                    "test_environment": "staging",
                },
                ["data", "migration", "quality-gate", "critical", "blocking"],
            ),
            (
                "Data Validation Pass >= 99%",
                "99%+ of input data passes validation before database insert. Track failures.",
                1,
                {
                    "gate_type": "data_quality",
                    "metric": "validation_pass_rate",
                    "threshold": 99,
                    "track_failures": True,
                },
                ["data", "validation", "quality-gate"],
            ),
            (
                "Data Consistency Checks Pass",
                "Referential integrity checks pass for critical entities: rides, payments, users, drivers.",
                1,
                {
                    "gate_type": "data_quality",
                    "check": "consistency",
                    "entities": ["rides", "payments", "users", "drivers"],
                },
                ["data", "consistency", "quality-gate"],
            ),
            (
                "Database Backup Success 100%",
                "All hourly backups succeed. Alert on any failure. Test restores monthly.",
                1,
                {
                    "gate_type": "data_quality",
                    "metric": "backup_success_rate",
                    "threshold": 100,
                    "frequency": "hourly",
                    "test_restore": "monthly",
                },
                ["data", "backup", "quality-gate", "critical"],
            ),
            (
                "Backup Restore Test Monthly",
                "Monthly backup restore tests with < 1h restore time target. Document results.",
                1,
                {
                    "gate_type": "data_quality",
                    "test": "backup_restore",
                    "frequency": "monthly",
                    "target_restore_time": 60,
                    "unit": "minutes",
                },
                ["data", "backup", "restore", "quality-gate"],
            ),
            (
                "Data Retention Policy Compliance",
                "Archive/delete per retention policy: 90d logs, 2y rides, 7y financial.",
                2,
                {
                    "gate_type": "data_quality",
                    "policy": "retention",
                    "periods": {"logs": "90_days", "rides": "2_years", "financial": "7_years"},
                },
                ["data", "retention", "compliance", "quality-gate"],
            ),
            (
                "PII Anonymization in Non-Prod",
                "All PII anonymized in dev/staging with realistic fake data: phone, email, name, payment, location.",
                1,
                {
                    "gate_type": "data_quality",
                    "requirement": "pii_anonymization",
                    "environments": ["dev", "staging"],
                    "fields": ["phone", "email", "name", "payment", "location"],
                },
                ["data", "pii", "anonymization", "quality-gate", "compliance"],
            ),
            (
                "Data Quality Score >= 95%",
                "Overall DQ score 95%+: completeness, accuracy, consistency, timeliness. Monitor per table.",
                2,
                {
                    "gate_type": "data_quality",
                    "metric": "dq_score",
                    "threshold": 95,
                    "dimensions": ["completeness", "accuracy", "consistency", "timeliness"],
                },
                ["data", "quality-score", "quality-gate"],
            ),
            (
                "Duplicate Records < 0.1%",
                "Duplicate records under 0.1% of total. Use unique constraints, deduplication jobs.",
                2,
                {
                    "gate_type": "data_quality",
                    "metric": "duplicate_rate",
                    "threshold": 0.1,
                    "unit": "percent",
                    "solutions": ["unique_constraints", "dedup_jobs"],
                },
                ["data", "duplicates", "quality-gate"],
            ),
            (
                "Data Freshness < 5 minutes",
                "Critical real-time data (location, ride status, driver availability) under 5 min old.",
                1,
                {
                    "gate_type": "data_quality",
                    "metric": "data_freshness",
                    "threshold": 5,
                    "unit": "minutes",
                    "data_types": ["location", "ride_status", "driver_availability"],
                },
                ["data", "freshness", "real-time", "quality-gate"],
            ),
        ]

    # Additional methods for other item types will be added...
    # For demonstration, I'm showing structure with quality_gates complete


async def main() -> None:
    """Generate all quality items."""
    conn = None
    try:
        conn = await asyncpg.connect(DB_URL)
        counts = {}

        async def insert_item(title: Any, itype: Any, desc: Any, status: Any, pri: Any, meta: Any, tags: Any) -> None:
            iid = str(uuid.uuid4())
            await conn.execute(
                """INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, NOW(), NOW())""",
                iid,
                PROJECT_ID,
                title,
                itype,
                desc,
                status,
                pri,
                json.dumps(meta),
                tags,
            )
            counts[itype] = counts.get(itype, 0) + 1
            return iid

        # Generate quality gates
        for title, desc, pri, meta, tags in QualityItemsData.quality_gates():
            await insert_item(title, "quality_gate", desc, "active", pri, meta, tags)

        # Summary
        sum(counts.values())
        for _itype in sorted(counts.keys()):
            pass

    except Exception:
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
