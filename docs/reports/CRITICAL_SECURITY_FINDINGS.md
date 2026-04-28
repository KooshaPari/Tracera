# Critical Security Findings - Phase 5 Maximum Strictness

**Status:** 🔴 ACTION REQUIRED
**Date:** 2026-02-07
**Source:** govulncheck, bandit, semgrep, pip-audit

---

## 🚨 P0 - IMMEDIATE ACTION REQUIRED

### GO-2026-4337: crypto/tls Session Resumption Vulnerability

**Severity:** CRITICAL (P0)
**CVE:** GO-2026-4337
**Component:** Go standard library `crypto/tls`
**Description:** Unexpected session resumption vulnerability in TLS implementation

**Current State:**
- **System Go version:** 1.25.6 (VULNERABLE)
- **go.mod requires:** 1.24.0
- **Fixed in:** Go 1.25.7

**Impact Traces (6 locations):**
1. `internal/nats/nats.go:178` - NATS event bus connections
2. `internal/server/server.go:122` - HTTP server (Echo framework)
3. `internal/handlers/test_helpers.go:54` - Test HTTP connections
4. `cmd/tracertm/preflight.go:30` - Preflight TLS checks
5. `internal/services/notification_service.go:291` - Redis pub/sub TLS
6. `internal/server/server.go:122` - TLS dialer

**Production Impact:**
- ✅ TLS connections may allow unexpected session resumption
- ✅ Potential security bypass in authenticated channels
- ✅ Affects: NATS messaging, HTTP API, Redis connections

**Action Required:**
1. **Upgrade system Go:** `brew upgrade go` or download Go 1.25.7+
2. **Update go.mod:** Change `go 1.24.0` to `go 1.25.7`
3. **Rebuild:** `cd backend && go mod tidy && go build ./...`
4. **Verify:** `govulncheck ./...` should report 0 vulnerabilities

**Priority:** 🔴 **CRITICAL - Upgrade within 24 hours**

---

## 🟡 P1 - HIGH PRIORITY

### Python Dependency Vulnerabilities (pip-audit)

**Finding:** 4sgm package not found on PyPI
```
ERROR: Dependency not found on PyPI and could not be audited: 4sgm (2.0.0)
```

**Impact:** Cannot verify CVEs for this dependency

**Action Required:**
1. Verify `4sgm` package source (is it a private package?)
2. If typo, fix in dependencies
3. If private, add to pip-audit exclude list
4. Consider replacing with vetted alternative

**Priority:** 🟡 **HIGH - Review within 1 week**

---

### Semgrep Security Findings (26 findings)

#### SQL Injection Risk - text() Usage (8 findings)

**Location:** `src/tracertm/api/handlers/links.py`

**Finding:** sqlalchemy.text() with f-string column names

**Status:** ✅ FALSE POSITIVE
- Column names are whitelisted via `_pick_link_column()`
- Data values use parameterized queries (`:project_id`, `:source_id`)
- No user input reaches column name construction

**Action:** Add semgrep ignore comment with justification

---

#### Logger Credential Leak (18 findings)

**Locations:**
- `src/tracertm/api/handlers/websocket.py:130`
- `src/tracertm/api/middleware.py:63`
- `src/tracertm/api/middleware/authentication_middleware.py` (multiple)

**Finding:** Logging error messages that may contain tokens/credentials

**Example:**
```python
logger.warning("WebSocket rejected: invalid token from %s: %s", websocket.client, exc)
```

**Risk:** Token values in exception messages may be logged

**Action Required:**
1. Sanitize exception messages before logging
2. Use `logger.warning("WebSocket rejected from %s: [token redacted]", websocket.client)`
3. Or use `repr(exc)` which may include sensitive data - review carefully

**Priority:** 🟡 **MEDIUM - Fix within 2 weeks**

---

## 🟢 P2 - MEDIUM PRIORITY

### Bandit Security Findings (177 findings from JSON)

**Top issues:**
- S608 (SQL injection): 8 findings (same as semgrep - false positives)
- S110 (try-except-pass): Exception swallowing (addressed by BLE001 fixes)
- S404/S603/S607 (subprocess): Controlled subprocess calls in scripts (documented)

**Action:** Review bandit JSON output, add documented exclusions for false positives

---

## External Tool Summary

### Go Tools Status

| Tool | Status | Findings | Action |
|------|--------|----------|--------|
| govulncheck | ✅ Installed | 1 CVE (CRITICAL) | Upgrade Go to 1.25.7 |
| go build -race | ✅ Built-in | Not yet run | Add to CI |
| staticcheck | ✅ Built-in | Not yet run | Add to CI |

### Python Tools Status

| Tool | Status | Findings | Action |
|------|--------|----------|--------|
| bandit | ✅ Installed | 177 findings | Review JSON, document exclusions |
| semgrep | ✅ Installed | 26 findings | Review, fix credential leaks |
| pip-audit | ✅ Installed | 1 finding | Investigate 4sgm package |
| interrogate | ✅ Installed | Not yet run | Add to CI |
| radon | ✅ Installed | Not yet run | Add to CI |
| import-linter | ✅ Installed | Not yet run | Add to CI |
| tach | ✅ Installed | Not yet run | Add to CI |
| vulture | ✅ Installed | Not yet run | Optional (weekly) |

### TypeScript Tools Status

| Tool | Status | Findings | Action |
|------|--------|----------|--------|
| knip | ✅ Installed | 231 unused files | Clean up examples/POCs |
| madge | ✅ Installed | 0 circular deps | ✅ PASS |
| tsc --noEmit | ✅ Built-in | Not yet run | Add to CI |
| type-coverage | ✅ Installed | Not yet run | Optional (weekly) |

---

## Action Plan

### Immediate (This Week)

1. **🔴 CRITICAL:** Upgrade Go to 1.25.7
   ```bash
   brew upgrade go  # or download from go.dev
   cd backend && go mod edit -go=1.25.7
   go mod tidy
   govulncheck ./...  # Verify 0 vulnerabilities
   ```

2. **🟡 HIGH:** Fix logger credential leaks
   - Sanitize token/password in log messages
   - Use `[REDACTED]` or hash for sensitive data

3. **🟡 HIGH:** Investigate 4sgm package
   - Check if it's a typo or private package
   - Document in dependencies or exclude from pip-audit

### Short-term (Weeks 2-3)

1. Add all external tools to CI (Makefile targets already created)
2. Review bandit findings, document false positives
3. Clean up 231 unused TypeScript files (knip findings)

### Medium-term (Weeks 4-8)

1. Continue agent swarm cleanup (agents currently running)
2. Track violation reduction weekly
3. Document patterns and anti-patterns

---

## Files Referenced

- **Baseline outputs:** `.quality/baselines/`
- **Go CVE details:** `.quality/baselines/go-govulncheck.txt`
- **Python security:** `.quality/baselines/python-bandit.json`
- **Python CVEs:** `.quality/baselines/python-pip-audit.json`
- **TypeScript dead code:** `.quality/baselines/typescript-knip.txt`

---

**Document Status:** 🔴 ACTIVE - IMMEDIATE ACTION REQUIRED
**Last Updated:** 2026-02-07
**Owner:** Security Team / Quality Implementation
**Next Review:** After Go upgrade (24 hours)
