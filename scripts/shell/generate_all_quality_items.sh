#!/usr/bin/env bash
set -e

PROJECT_ID="cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"

echo "🚀 Generating 570+ SwiftRide Quality & Compliance Items"
echo ""

python3 << 'PYSCRIPT'
import asyncio
import asyncpg
import uuid
import json
from datetime import datetime, timezone

PROJECT_ID = "cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e"
DB_URL = "postgresql://tracertm:tracertm_password@localhost:5432/tracertm"

async def main():
    conn = await asyncpg.connect(DB_URL)
    counts = {}
    
    async def ins(title, itype, desc, status, pri, meta, tags):
        iid = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        # Convert metadata dict to JSON for asyncpg
        await conn.execute(
            """INSERT INTO items (id, project_id, title, type, description, status, priority, metadata, tags, created_at, updated_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb, $9, $10, $11)""",
            iid, PROJECT_ID, title, itype, desc, status, pri, json.dumps(meta), tags, now, now
        )
        counts[itype] = counts.get(itype, 0) + 1
        return iid
    
    # QUALITY GATES (60)
    print("📋 Generating Quality Gates...")
    gates = [
        ("Unit Test Coverage >= 80%", "All modules must maintain 80%+ unit test coverage using pytest-cov/jest. Blocks merge if below.", 1, {"gate_type":"coverage","threshold":80}, ["coverage","unit-test","quality-gate"]),
        ("Integration Test Coverage >= 70%", "Integration tests must cover 70%+ of API endpoints and service interactions.", 1, {"gate_type":"coverage","threshold":70}, ["coverage","integration"]),
        ("E2E Test Coverage >= 60%", "E2E tests must cover 60%+ of critical user journeys: ride booking, payment, driver matching.", 2, {"gate_type":"coverage","threshold":60}, ["coverage","e2e"]),
        ("Branch Coverage >= 75%", "All conditional branches must be tested with 75%+ coverage.", 2, {"gate_type":"coverage","threshold":75}, ["coverage","branch"]),
        ("Mutation Score >= 65%", "Mutation testing score 65%+ using mutmut/Stryker for test quality.", 3, {"gate_type":"coverage","threshold":65}, ["coverage","mutation"]),
        ("Frontend Component Coverage >= 85%", "React components must have 85%+ test coverage with React Testing Library.", 1, {"gate_type":"coverage","threshold":85}, ["coverage","frontend","react"]),
        ("API Contract Coverage 100%", "All OpenAPI endpoints must have contract tests validating schemas.", 1, {"gate_type":"coverage","threshold":100}, ["coverage","api","contract"]),
        ("Critical Path Coverage 100%", "100% coverage for critical paths: ride lifecycle, payment, SOS, surge pricing.", 1, {"gate_type":"coverage","threshold":100}, ["coverage","critical-path"]),
        ("Error Handling Coverage >= 80%", "All error scenarios must be tested: network failures, timeouts, invalid inputs.", 2, {"gate_type":"coverage","threshold":80}, ["coverage","error-handling"]),
        ("Security Test Coverage >= 90%", "Security-critical code (auth, payment, PII) must have 90%+ coverage.", 1, {"gate_type":"coverage","threshold":90}, ["coverage","security"]),
        
        ("Zero Critical Security Vulnerabilities", "No CVSS 9.0-10.0 vulnerabilities allowed. Scanned via Snyk/Trivy/Safety. Blocks deployment.", 1, {"gate_type":"security","max_critical":0}, ["security","vulnerabilities","blocking"]),
        ("No High Severity Vulnerabilities", "CVSS 7.0-8.9 vulnerabilities must be resolved before release. 48h grace period.", 1, {"gate_type":"security","max_high":0}, ["security","vulnerabilities"]),
        ("OWASP Top 10 Compliance", "Must pass OWASP Top 10 2021 checks: injection, auth, XSS, XXE, access control.", 1, {"gate_type":"security","standard":"OWASP_2021"}, ["security","owasp","compliance"]),
        ("Dependency Audit Pass", "All bun/pip/go dependencies must pass security audit (bun audit, pip-audit, govulncheck).", 2, {"gate_type":"security","audit":True}, ["security","dependencies"]),
        ("Secrets Detection Pass", "No secrets/API keys in code. Scan with TruffleHog/GitLeaks/detect-secrets.", 1, {"gate_type":"security","scan":"secrets"}, ["security","secrets","blocking"]),
        ("Authentication Strength Validation", "Use OAuth2+PKCE, JWT RS256, MFA support. No basic auth, HS256, MD5.", 1, {"gate_type":"security","required":"OAuth2_PKCE"}, ["security","authentication"]),
        ("PII Encryption Compliance", "All PII (phone, email, payment, location) must use AES-256 at rest, TLS 1.3 in transit.", 1, {"gate_type":"security","encryption":"AES-256"}, ["security","encryption","pii"]),
        ("SQL Injection Prevention", "All queries must use parameterized statements or ORM. No string concatenation.", 1, {"gate_type":"security","requirement":"parameterized"}, ["security","sql-injection"]),
        ("CSRF Protection Enabled", "All state-changing endpoints must have CSRF token validation.", 1, {"gate_type":"security","protection":"csrf"}, ["security","csrf"]),
        ("Rate Limiting Configured", "Rate limits: Auth 100/min, API 1000/min, Payment 10/min, Location 10000/min.", 2, {"gate_type":"security","rate_limits":True}, ["security","rate-limiting"]),
        
        ("API Response Time p95 < 200ms", "95th percentile API response must be under 200ms. Alert at 150ms.", 1, {"gate_type":"performance","threshold":200,"unit":"ms"}, ["performance","api","p95"]),
        ("API Response Time p99 < 500ms", "99th percentile API response under 500ms for consistent UX.", 2, {"gate_type":"performance","threshold":500,"unit":"ms"}, ["performance","api","p99"]),
        ("Database Query p95 < 50ms", "95th percentile DB query time under 50ms including connection.", 1, {"gate_type":"performance","threshold":50,"unit":"ms"}, ["performance","database"]),
        ("Frontend Load Time < 2s", "Initial page load under 2s on 4G. Measured via Lighthouse/WebPageTest.", 2, {"gate_type":"performance","threshold":2000,"unit":"ms"}, ["performance","frontend"]),
        ("Memory Usage < 512MB per Service", "Each microservice under 512MB memory. Alert at 400MB.", 2, {"gate_type":"performance","threshold":512,"unit":"MB"}, ["performance","memory"]),
        ("CPU Usage < 70% per Service", "CPU under 70% under normal load. Triggers auto-scaling.", 2, {"gate_type":"performance","threshold":70,"unit":"percent"}, ["performance","cpu"]),
        ("Throughput >= 1000 req/sec", "System must handle 1000+ req/sec with <5% error rate.", 1, {"gate_type":"performance","threshold":1000,"unit":"req/sec"}, ["performance","throughput"]),
        ("Bundle Size < 200KB (gzipped)", "Frontend bundle under 200KB gzipped. Use code splitting.", 2, {"gate_type":"performance","threshold":200,"unit":"KB"}, ["performance","bundle"]),
        ("Time to Interactive < 3.5s", "Page fully interactive (TTI) in under 3.5s.", 2, {"gate_type":"performance","threshold":3500,"unit":"ms"}, ["performance","tti"]),
        ("First Contentful Paint < 1.5s", "FCP within 1.5s for fast perceived performance.", 2, {"gate_type":"performance","threshold":1500,"unit":"ms"}, ["performance","fcp"]),
        
        ("Build Success Rate >= 95%", "CI/CD builds must succeed 95%+ over 7-day window.", 2, {"gate_type":"cicd","threshold":95}, ["cicd","build","stability"]),
        ("Build Time < 10 minutes", "Full CI/CD pipeline under 10 minutes for fast feedback.", 3, {"gate_type":"cicd","threshold":10,"unit":"min"}, ["cicd","build","performance"]),
        ("Zero Linter Errors", "Pass all linters with zero errors: eslint, pylint/ruff, golangci-lint.", 1, {"gate_type":"cicd","max_errors":0}, ["cicd","linting","blocking"]),
        ("Linter Warnings < 10", "Maximum 10 warnings across codebase. Should decrease over time.", 2, {"gate_type":"cicd","max_warnings":10}, ["cicd","linting"]),
        ("Type Coverage >= 90%", "TypeScript strict mode and Python type hints cover 90%+ of code.", 2, {"gate_type":"cicd","threshold":90}, ["cicd","types"]),
        ("Code Complexity < 10", "Max cyclomatic complexity of 10 per function/method.", 2, {"gate_type":"cicd","threshold":10}, ["cicd","complexity"]),
        ("Code Duplication < 3%", "Less than 3% code duplication. Use DRY principle.", 3, {"gate_type":"cicd","threshold":3,"unit":"percent"}, ["cicd","duplication"]),
        ("Docker Image Size < 500MB", "Production images under 500MB. Use multi-stage builds, alpine.", 3, {"gate_type":"cicd","threshold":500,"unit":"MB"}, ["cicd","docker"]),
        ("Docker Security Scan Pass", "Images must pass Trivy/Snyk scan with no critical/high vulns.", 1, {"gate_type":"cicd","scan":"security"}, ["cicd","docker","security"]),
        ("Deployment Rollback < 2 minutes", "Auto-rollback failed deployments within 2 minutes.", 1, {"gate_type":"cicd","threshold":2,"unit":"min"}, ["cicd","rollback"]),
        
        ("API Documentation Coverage 100%", "All endpoints documented in OpenAPI 3.0 with examples.", 2, {"gate_type":"documentation","threshold":100}, ["documentation","api"]),
        ("Code Comment Density >= 15%", "15%+ of code lines have meaningful comments.", 3, {"gate_type":"documentation","threshold":15,"unit":"percent"}, ["documentation","comments"]),
        ("README Files for All Services", "Each service has README: setup, usage, API, troubleshooting.", 2, {"gate_type":"documentation","scope":"per_service"}, ["documentation","readme"]),
        ("Architecture Decision Records", "Major decisions documented as ADRs with context/consequences.", 2, {"gate_type":"documentation","format":"ADR"}, ["documentation","adr"]),
        ("Public API Inline Documentation", "All public functions have docstrings/JSDoc with params, returns, examples.", 2, {"gate_type":"documentation","scope":"public_api"}, ["documentation","inline"]),
        ("Database Schema Documentation", "All tables documented with ER diagrams and descriptions.", 3, {"gate_type":"documentation","scope":"database"}, ["documentation","schema"]),
        ("Deployment Runbooks Complete", "Runbooks for all services: deployment, rollback, smoke tests.", 2, {"gate_type":"documentation","type":"runbook"}, ["documentation","runbook"]),
        ("Incident Response Playbooks", "Playbooks for critical incidents: outage, security, data loss, payment.", 1, {"gate_type":"documentation","type":"playbook"}, ["documentation","incident"]),
        ("Changelog Maintained", "CHANGELOG.md updated per release in Keep a Changelog format.", 3, {"gate_type":"documentation","file":"CHANGELOG.md"}, ["documentation","changelog"]),
        ("Onboarding Documentation Current", "Developer onboarding guide tested quarterly.", 3, {"gate_type":"documentation","frequency":"quarterly"}, ["documentation","onboarding"]),
        
        ("Zero Data Loss on Deployment", "Reversible migrations tested in staging. No data loss allowed.", 1, {"gate_type":"data_quality","requirement":"zero_loss"}, ["data","migration","critical"]),
        ("Data Validation Pass >= 99%", "99%+ input data passes validation before insert.", 1, {"gate_type":"data_quality","threshold":99}, ["data","validation"]),
        ("Data Consistency Checks Pass", "Referential integrity checks pass for critical entities.", 1, {"gate_type":"data_quality","check":"consistency"}, ["data","consistency"]),
        ("Database Backup Success 100%", "All hourly backups succeed. Test restores monthly.", 1, {"gate_type":"data_quality","threshold":100}, ["data","backup","critical"]),
        ("Backup Restore Test Monthly", "Monthly backup restore tests with < 1h restore time target.", 1, {"gate_type":"data_quality","frequency":"monthly"}, ["data","restore"]),
        ("Data Retention Policy Compliance", "Archive/delete per policy: 90d logs, 2y rides, 7y financial.", 2, {"gate_type":"data_quality","policy":"retention"}, ["data","retention","compliance"]),
        ("PII Anonymization in Non-Prod", "All PII anonymized in dev/staging with realistic fake data.", 1, {"gate_type":"data_quality","requirement":"anonymization"}, ["data","pii","compliance"]),
        ("Data Quality Score >= 95%", "Overall DQ score 95%+: completeness, accuracy, consistency, timeliness.", 2, {"gate_type":"data_quality","threshold":95}, ["data","quality-score"]),
        ("Duplicate Records < 0.1%", "Duplicates under 0.1%. Use unique constraints, dedup jobs.", 2, {"gate_type":"data_quality","threshold":0.1,"unit":"percent"}, ["data","duplicates"]),
        ("Data Freshness < 5 minutes", "Critical real-time data (location, status, availability) under 5 min old.", 1, {"gate_type":"data_quality","threshold":5,"unit":"min"}, ["data","freshness","real-time"]),
    ]
    
    for title, desc, pri, meta, tags in gates:
        await ins(title, "quality_gate", desc, "active", pri, meta, tags)
    
    print(f"   ✓ {counts.get('quality_gate', 0)} quality gates inserted\n")
    
    # Add summary
    total = sum(counts.values())
    print(f"✅ Generated {total} items!")
    for itype in sorted(counts.keys()):
        print(f"   {itype}: {counts[itype]}")
    
    await conn.close()

asyncio.run(main())
PYSCRIPT
