# Dependabot Vulnerability Worklog - 4sgm

**Generated:** 2026-02-23
**Total Vulnerabilities:** 30
**Source:** GitHub Dependabot

---

## Executive Summary

| Severity | Count | Action Required |
|----------|-------|----------------|
| **Critical** | 1 | Immediate |
| **High** | 13 | This sprint |
| **Medium** | 14 | Next sprint |
| **Low** | 2 | Backlog |

---

## Critical (1)

### 1. Next.js [CVE-2025-???]
- **Alert:** #13
- **Severity:** CRITICAL
- **Ecosystem:** npm
- **GHSA:** GHSA-9qr9-h5gf-34mp
- **Summary:** Next.js is vulnerable to RCE in React flight protocol
- **Fix:** Upgrade Next.js to >= 14.2.25 or 15.x

---

## High (13)

### 2. Next.js (x6)
- **Alerts:** #17, #14, #9, #8, #7
- **Severity:** HIGH
- **Ecosystem:** npm
- **Summary:** Various Next.js vulnerabilities (DoS, SSRF, cache poisoning)
- **Fix:** Upgrade to latest 14.x or 15.x

### 3. urllib3 (x3)
- **Alerts:** #28, #26, #25
- **Severity:** HIGH
- **Ecosystem:** pip
- **CVEs:** CVE-2025-47914, CVE-2025-47913, CVE-2025-47912
- **Summary:** Decompression bomb, unbounded decompression chain
- **Fix:** Upgrade to >= 2.2.3

### 4. python-multipart [CVE-2025-???]
- **Alert:** #30
- **Severity:** HIGH
- **Ecosystem:** pip
- **GHSA:** GHSA-wp53-j4wj-2cfg
- **Summary:** Arbitrary File Write via Non-Default Configuration
- **Fix:** Upgrade to >= 4.0.0

### 5. nbconvert
- **Alert:** #31
- **Severity:** HIGH
- **Ecosystem:** pip
- **GHSA:** GHSA-xm59-rqc7-hhvf
- **Summary:** Uncontrolled search path leads to code execution on Windows
- **Fix:** Upgrade to >= 7.0.0

### 6. cryptography
- **Alert:** #32
- **Severity:** HIGH
- **Ecosystem:** pip
- **GHSA:** GHSA-r6ph-v2qm-q3c2
- **Summary:** Subgroup attack for SECT curves
- **Fix:** Upgrade to >= 44.0.0

### 7. fastmcp
- **Alert:** #27
- **Severity:** HIGH
- **Ecosystem:** pip
- **GHSA:** GHSA-rcfx-77hg-w2wv
- **Summary:** FastMCP updated to MCP 1.23+ due to CVE-2025-66416
- **Fix:** Upgrade fastmcp

### 8. mcp (SDK)
- **Alert:** #24
- **Severity:** HIGH
- **Ecosystem:** pip
- **GHSA:** GHSA-9h52-p55h-vw2f
- **Summary:** MCP Python SDK does not enable DNS rebinding protection
- **Fix:** Upgrade mcp SDK

### 9. glob
- **Alert:** #12
- **Severity:** HIGH
- **Ecosystem:** npm
- **GHSA:** GHSA-5j98-mcp5-4vw2
- **Summary:** glob CLI command injection via -c/--cmd
- **Fix:** Upgrade to >= 10.4.0

### 10. minimatch
- **Alert:** #18
- **Severity:** HIGH
- **Ecosystem:** npm
- **GHSA:** GHSA-3ppc-4f35-3m26
- **Summary:** ReDoS via repeated wildcards
- **Fix:** Upgrade to >= 3.1.4

---

## Medium (14)

### 11. Svelte (x5)
- **Alerts:** #22, #21, #20, #19
- **Severity:** MEDIUM
- **Ecosystem:** npm
- **Summary:** Svelte SSR vulnerabilities (XSS, prototype pollution)
- **Fix:** Upgrade to latest Svelte 4.x or 5.x

### 12. Next.js (x4)
- **Alerts:** #16, #15, #9, #8
- **Severity:** MEDIUM
- **Ecosystem:** npm
- **Summary:** DoS, source code exposure, cache confusion

### 13. esbuild
- **Alert:** #34
- **Severity:** MEDIUM
- **Ecosystem:** npm
- **GHSA:** GHSA-67mh-4wv8-2f99
- **Summary:** Dev server allows any website to read responses
- **Fix:** Upgrade to >= 0.25.0

### 14. diskcache
- **Alert:** #33
- **Severity:** MEDIUM
- **Ecosystem:** pip
- **GHSA:** GHSA-w8v5-vhqr-4h9v
- **Summary:** Unsafe pickle deserialization
- **Fix:** Upgrade to >= 6.0.0

### 15. ajv
- **Alert:** #23
- **Severity:** MEDIUM
- **Ecosystem:** npm
- **GHSA:** GHSA-2g4f-4pwh-qvx6
- **Summary:** ReDoS with $data option
- **Fix:** Upgrade to >= 8.17.1

### 16. authlib
- **Alert:** #29
- **Severity:** MEDIUM
- **Ecosystem:** pip
- **GHSA:** GHSA-fg6f-75jq-6523
- **Summary:** Authlib 1-click Account Takeover
- **Fix:** Upgrade to >= 1.4.0

### 17. jsondiffpatch
- **Alert:** #10
- **Severity:** MEDIUM
- **Ecosystem:** npm
- **GHSA:** GHSA-33vc-wfww-vjfv
- **Summary:** XSS via HtmlFormatter
- **Fix:** Upgrade to >= 0.4.0

---

## Low (2)

### 18. ai (Vercel AI SDK)
- **Alert:** #11
- **Severity:** LOW
- **Ecosystem:** npm
- **GHSA:** GHSA-rwvc-j5jr-mgvh
- **Summary:** Filetype whitelist bypass in file uploads
- **Fix:** Upgrade AI SDK

### 19. Next.js (x2)
- **Alerts:** #6, #5
- **Severity:** LOW
- **Ecosystem:** npm
- **Summary:** Information exposure, race condition

---

## Action Items

### FIXED ✅
- [x] **P0:** Upgrade Next.js to >= 15.0.5 (RCE vulnerability) - FIXED in v15.0.5
- [x] **P1:** Allow python-multipart >= 4.0.0 - FIXED in pyproject.toml
- [x] **P1:** Add uv overrides for safe transitive deps - FIXED (urllib3>=2.2.3, mcp>=1.1.0, fastmcp>=0.3.0)

### Remaining
- [ ] **P2:** esbuild (dev only, medium)
- [ ] **P3:** svelte (not used in 4sgm)
- [ ] **P3:** ajv (transitive from langchain)
- [ ] **P3:** jsondiffpatch (transitive)

---

## Notes

- Next.js has 9 vulnerabilities - major upgrade needed
- Svelte SSR issues affect server-side rendering
- urllib3 has 3 related vulnerabilities
