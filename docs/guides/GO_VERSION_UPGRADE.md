# Go Version Upgrade - CVE Mitigation

**Status:** 🔴 URGENT - CVE GO-2026-4337 Mitigation
**Priority:** P0 - Complete within 24 hours
**Issue:** crypto/tls unexpected session resumption vulnerability

---

## Vulnerability Details

**CVE:** GO-2026-4337
**Component:** Go standard library `crypto/tls`
**Severity:** CRITICAL
**Description:** Unexpected session resumption in TLS handshake

**Current State:**
- System Go: 1.25.6 (VULNERABLE ❌)
- go.mod: 1.25.7 (UPDATED ✅)
- Fixed in: Go 1.25.7+

**Production Impact:**
- TLS connections (NATS, HTTP, Redis) may allow unexpected session resumption
- Potential security bypass in authenticated channels
- Affects 6 code paths through production services

---

## Upgrade Steps

### macOS (Homebrew)

```bash
# 1. Check current version
go version  # Should show go1.25.6

# 2. Upgrade Go
brew upgrade go

# 3. Verify upgrade
go version  # Should show go1.25.7 or higher

# 4. Rebuild backend
cd backend
go mod tidy
go build ./...

# 5. Verify CVE fixed
govulncheck ./...  # Should report 0 vulnerabilities
```

**Expected Output:**
```
Scanning your code and 123 packages across 456 dependent modules for known vulnerabilities...

No vulnerabilities found.
```

---

### Linux (Manual Install)

```bash
# 1. Download Go 1.25.7+
wget https://go.dev/dl/go1.25.7.linux-amd64.tar.gz

# 2. Remove old version
sudo rm -rf /usr/local/go

# 3. Extract new version
sudo tar -C /usr/local -xzf go1.25.7.linux-amd64.tar.gz

# 4. Verify
go version  # Should show go1.25.7

# 5. Rebuild and verify (same as macOS steps 4-5)
```

---

### Windows (Manual Install)

```powershell
# 1. Download Go 1.25.7+ MSI installer from go.dev/dl

# 2. Run installer (will replace existing version)

# 3. Verify in new terminal
go version  # Should show go1.25.7

# 4. Rebuild and verify
cd backend
go mod tidy
go build ./...
govulncheck ./...
```

---

## Verification Checklist

After upgrading, verify the following:

- [ ] `go version` shows 1.25.7 or higher
- [ ] `cd backend && go mod tidy` completes without errors
- [ ] `cd backend && go build ./...` completes without errors
- [ ] `cd backend && govulncheck ./...` reports 0 vulnerabilities
- [ ] `cd backend && go test -race -short ./...` passes (race detection still works)
- [ ] `make dev` starts successfully
- [ ] `make test` passes

---

## Rollback Plan

If upgrade causes issues:

```bash
# 1. Check if old version is available
brew list --versions go

# 2. Rollback to previous version (example)
brew switch go 1.25.6

# 3. Revert go.mod change
cd backend
git checkout go.mod
go mod tidy

# 4. Document issue and investigate
```

---

## Related Changes

**Files Modified:**
- `backend/go.mod` - Updated go directive from 1.24.0 to 1.25.7

**Why This Matters:**
- Closes security vulnerability in TLS layer
- Affects all HTTPS connections (API, NATS, Redis)
- Required for production deployment

---

## CVE Trace Locations

The vulnerability affects these production code paths:

1. **NATS Event Bus** (`internal/nats/nats.go:178`)
   - Impact: Message queue TLS connections
   - Risk: Session resumption in event publishing

2. **HTTP Server** (`internal/server/server.go:122`)
   - Impact: Main API server HTTPS
   - Risk: Session bypass in authenticated endpoints

3. **Redis Pub/Sub** (`internal/services/notification_service.go:291`)
   - Impact: Real-time notification TLS
   - Risk: Session hijacking in push notifications

4. **Preflight Checks** (`cmd/tracertm/preflight.go:30`)
   - Impact: Startup TLS validation
   - Risk: False positive health checks

5. **Test Helpers** (`internal/handlers/test_helpers.go:54`)
   - Impact: Integration test TLS
   - Risk: Test suite security (lower priority)

6. **TLS Dialer** (`internal/server/server.go:122`)
   - Impact: Outbound TLS connections
   - Risk: Man-in-the-middle on external APIs

---

## Post-Upgrade Actions

After successful upgrade:

1. ✅ Commit go.sum changes: `git add backend/go.sum && git commit -m "chore: update go.sum after Go 1.25.7 upgrade"`
2. ✅ Update CI/CD to use Go 1.25.7+ in build images
3. ✅ Document upgrade in CHANGELOG.md
4. ✅ Run full test suite to verify compatibility
5. ✅ Deploy to staging for validation

---

**Priority:** 🔴 **CRITICAL - Upgrade within 24 hours**

**Last Updated:** 2026-02-07
**Next Action:** Run `brew upgrade go` and verify
