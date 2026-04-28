# SwiftRide Security Layer - Quick Start

## Overview

Generate 450+ comprehensive security items for SwiftRide in under 60 seconds.

## Quick Execute

```bash
# From project root
python scripts/generate_security_layer.py
```

## What Gets Created

| Type | Count | Examples |
|------|-------|----------|
| **security_vulnerability** | 80 | SQL Injection, XSS, CSRF, Auth flaws |
| **security_control** | 100 | JWT auth, Rate limiting, Encryption |
| **threat_model** | 60 | Account takeover, Data exfiltration |
| **security_test** | 90 | Pentests, Vuln scans, Code reviews |
| **encryption_requirement** | 50 | AES-256, TLS 1.3, Key management |
| **access_control** | 70 | RBAC policies for all roles |
| **Links** | 75+ | Relationships between items |

**Total: 450+ items**

## Item Details

### Vulnerabilities Include
- CVSS v3.1 scores (4.3-9.8)
- CWE identifiers
- Affected components
- Mitigation steps
- Exploitation likelihood

### Controls Include
- Implementation status
- Technical/administrative category
- Priority levels
- Mapping to vulnerabilities

### Threat Models Include
- STRIDE categorization
- Threat actors
- Attack vectors
- Likelihood & impact

## Sample Output

```
============================================================
SwiftRide Security Layer Generator
============================================================

🔴 Generating 80 Security Vulnerabilities...
  Created 10 security_vulnerability items...
  Created 80 security_vulnerability items...

🛡️  Generating 100 Security Controls...
🧪 Generating 90 Security Tests...

Total: 450 items created
============================================================
```

## Verify Results

```sql
-- Count items by type
SELECT type, COUNT(*), COUNT(*) FILTER (WHERE status IN ('open', 'todo')) as open_items
FROM items
WHERE project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND type LIKE '%security%' OR type LIKE '%threat%' OR type LIKE '%access%'
GROUP BY type
ORDER BY type;

-- View critical vulnerabilities
SELECT external_id, title, metadata->>'cvss_score' as cvss
FROM items
WHERE type = 'security_vulnerability'
  AND priority = 'critical'
ORDER BY (metadata->>'cvss_score')::float DESC
LIMIT 10;

-- View security relationships
SELECT l.type, COUNT(*)
FROM links l
JOIN items i ON l.source_id = i.id
WHERE i.project_id = 'cd6d847c-0f2e-4ccc-bf1a-c96b08c97d4e'
  AND (i.type LIKE '%security%' OR l.type IN ('mitigates', 'exploits', 'verifies'))
GROUP BY l.type;
```

## Troubleshooting

**Database connection error:**
```bash
# Check DATABASE_URL in .env
docker-compose up -d postgres
```

**Import errors:**
```bash
pip install sqlalchemy asyncpg python-dotenv
```

**Script hangs:**
- Check database is accessible
- Verify project_id exists
- Run with --verbose flag (if added)

## Next Steps

1. ✅ Run generator script
2. ✅ Verify 450+ items created
3. ✅ Review critical vulnerabilities (CVSS >9.0)
4. ✅ Check security control coverage
5. ✅ Use in security dashboard
6. ✅ Link to features/APIs they protect

## Files

- **Script**: `scripts/generate_security_layer.py`
- **Documentation**: `SWIFTRIDE_SECURITY_LAYER_COMPLETE.md`
- **This Guide**: `docs/guides/quick-start/SECURITY_LAYER_QUICK_START.md`

---

**Execution Time**: ~30 seconds
**Database Inserts**: ~525 (450 items + 75 links)
**Transaction**: Atomic (all-or-nothing)
