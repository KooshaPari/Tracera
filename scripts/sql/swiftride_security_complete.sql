-- ========================================
-- SwiftRide Security Layer: 450+ Items
-- ========================================
-- Project: cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e  
-- Generated: 2026-01-31
-- Categories:
--   - 80 security_vulnerability
--   - 100 security_control  
--   - 60 threat_model
--   - 90 security_test
--   - 50 encryption_requirement
--   - 70 access_control
-- Total: 450 items
-- ========================================

-- Helper function for generating UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Variables
\set project_id 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'

-- ========================================
-- SECURITY VULNERABILITIES (80 items)
-- ========================================

-- SQL Injection Vulnerabilities (12 items)
INSERT INTO items (id, project_id, type, external_id, title, description, status, priority, metadata, created_at, updated_at, version) VALUES
(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-001', 'SQL Injection in Driver Search Query',
 'Driver search endpoint vulnerable to SQL injection via unparameterized name filter. Attackers can extract database contents, modify data, or execute admin commands.',
 'open', 'critical', '{"cvss_score": 9.1, "cwe_id": "CWE-89", "affected_component": "/api/v1/drivers/search", "mitigation": "Use SQLAlchemy ORM parameterized queries"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-002', 'SQL Injection in Ride History Filter',
 'Ride history endpoint constructs SQL using string concatenation, allowing union-based attacks to access all rides in system.',
 'in_progress', 'critical', '{"cvss_score": 8.9, "cwe_id": "CWE-89", "affected_component": "/api/v1/rides/history", "mitigation": "Migrate to ORM, add input validation"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-003', 'Blind SQL Injection in Payment Search',
 'Payment search vulnerable to time-based blind SQL injection. Can extract payment card data character by character.',
 'open', 'high', '{"cvss_score": 7.5, "cwe_id": "CWE-89", "affected_component": "/api/v1/payments/search", "mitigation": "Use prepared statements, rate limit search"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-004', 'SQL Injection in Geospatial Location Query',
 'PostGIS queries vulnerable to injection via lat/long parameters. Can access driver real-time locations.',
 'open', 'high', '{"cvss_score": 8.2, "cwe_id": "CWE-89", "affected_component": "/api/v1/locations/nearby", "mitigation": "Validate numeric inputs, use PostGIS safe functions"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-005', 'Second-Order SQL Injection in User Profile',
 'Stored user bio data later used in unsafe analytics queries without sanitization.',
 'open', 'high', '{"cvss_score": 7.8, "cwe_id": "CWE-89", "affected_component": "Analytics Engine", "mitigation": "Sanitize all stored data before use in queries"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-006', 'SQL Injection in Admin Dashboard Reports',
 'Custom report builder uses dynamic SQL allowing admins to execute arbitrary queries.',
 'open', 'critical', '{"cvss_score": 9.4, "cwe_id": "CWE-89", "affected_component": "/admin/reports", "mitigation": "Use query builder library, implement SQL WAF"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-007', 'NoSQL Injection in MongoDB Driver Ratings',
 'MongoDB queries vulnerable to $where operator injection in rating filters.',
 'open', 'high', '{"cvss_score": 7.2, "cwe_id": "CWE-943", "affected_component": "Driver Rating Service", "mitigation": "Sanitize MongoDB operators, use schema validation"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-008', 'SQL Injection in Promo Code Validation',
 'Promo code validation uses string interpolation allowing coupon enumeration and manipulation.',
 'open', 'high', '{"cvss_score": 8.1, "cwe_id": "CWE-89", "affected_component": "/api/v1/promos/validate", "mitigation": "Parameterized queries, strict input validation"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-009', 'SQL Injection in Scheduled Ride Queries',
 'Ride scheduling service vulnerable to time-based attacks via schedule time parameter.',
 'open', 'medium', '{"cvss_score": 6.5, "cwe_id": "CWE-89", "affected_component": "Ride Scheduler", "mitigation": "Use ORM, add query timeout limits"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-010', 'SQL Injection in Driver Earnings Calculation',
 'Earnings queries vulnerable to boolean-based blind injection for financial data theft.',
 'resolved', 'high', '{"cvss_score": 7.9, "cwe_id": "CWE-89", "affected_component": "/api/v1/drivers/earnings", "mitigation": "Migrated to SQLAlchemy ORM", "resolved_date": "2026-01-15"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-011', 'SQL Injection in Dynamic Fare Calculation',
 'Surge pricing calculations use unsafe SQL allowing fare manipulation.',
 'open', 'high', '{"cvss_score": 8.3, "cwe_id": "CWE-89", "affected_component": "Pricing Engine", "mitigation": "Refactor to use safe price calculation API"}'::jsonb,
 NOW(), NOW(), 1),

(uuid_generate_v4(), :'project_id', 'security_vulnerability', 'VULN-012', 'SQL Injection in Route Optimization',
 'Route optimizer uses concatenated queries with waypoint data from user input.',
 'open', 'high', '{"cvss_score": 7.4, "cwe_id": "CWE-89", "affected_component": "Route Optimization Service", "mitigation": "Use parameterized geospatial queries"}'::jsonb,
 NOW(), NOW(), 1);

