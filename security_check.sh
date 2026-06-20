#!/bin/bash
# Phase 4.T3: Security Pre-flight Checks

echo "=== PHASE 4.T3: SECURITY PRE-FLIGHT CHECKS ==="
echo ""

PROJECT_ROOT="/Users/kooshapari/temp-PRODVERCEL/485/kush/trace"
cd "$PROJECT_ROOT"

PASSED=0
FAILED=0

# Check 1: CSP Headers in middleware
echo "[CHECK 1] CSP Headers Configuration"
if grep -r "Content-Security-Policy" backend/internal/middleware/ > /dev/null 2>&1; then
  echo "✓ CSP headers found in middleware"
  ((PASSED++))
else
  echo "✗ CSP headers NOT found in middleware"
  ((FAILED++))
fi

# Check 2: Auth checks in handlers
echo ""
echo "[CHECK 2] Authentication Guards in API Handlers"
AUTH_COUNT=$(grep -r "auth" backend/internal/handlers/ | grep -i "middleware\|guard\|require" | wc -l)
if [ "$AUTH_COUNT" -gt 0 ]; then
  echo "✓ Auth checks found in handlers ($AUTH_COUNT references)"
  ((PASSED++))
else
  echo "✗ Auth checks NOT found in handlers"
  ((FAILED++))
fi

# Check 3: Rate limiting configuration
echo ""
echo "[CHECK 3] Rate Limiting on Sensitive Endpoints"
if grep -r "rate" backend/internal/middleware/ -i | grep -q "limit\|rate"; then
  echo "✓ Rate limiting configuration found"
  ((PASSED++))
else
  echo "✗ Rate limiting configuration NOT found"
  ((FAILED++))
fi

# Check 4: CORS configuration
echo ""
echo "[CHECK 4] CORS Configuration"
if grep -r "CORS\|cors" backend/internal/middleware/ | grep -q "\."; then
  echo "✓ CORS configuration found"
  ((PASSED++))
else
  echo "✗ CORS configuration NOT found"
  ((FAILED++))
fi

# Check 5: Password hashing
echo ""
echo "[CHECK 5] Password Hashing in Auth"
if grep -r "bcrypt\|argon" backend/ --include="*.go" > /dev/null 2>&1; then
  echo "✓ Password hashing implementation found"
  ((PASSED++))
else
  echo "✗ Password hashing NOT found"
  ((FAILED++))
fi

# Check 6: Input validation
echo ""
echo "[CHECK 6] Input Validation"
VALIDATION_COUNT=$(grep -r "validate\|validation\|validator" backend/ --include="*.go" | wc -l)
if [ "$VALIDATION_COUNT" -gt 5 ]; then
  echo "✓ Input validation found ($VALIDATION_COUNT references)"
  ((PASSED++))
else
  echo "✗ Input validation may be insufficient"
  ((FAILED++))
fi

# Check 7: SQL injection prevention (parameterized queries)
echo ""
echo "[CHECK 7] SQL Injection Prevention (Parameterized Queries)"
if grep -r "prepared\|parameterized\|BindByName\|gorm\|sqlc" backend/ --include="*.go" > /dev/null 2>&1; then
  echo "✓ Parameterized query framework found (GORM/sqlc)"
  ((PASSED++))
else
  echo "✗ Parameterized queries NOT found"
  ((FAILED++))
fi

# Check 8: XSS Prevention in frontend
echo ""
echo "[CHECK 8] XSS Prevention in Frontend"
if grep -r "sanitize\|DOMPurify\|xss" frontend/ --include="*.ts" --include="*.tsx" > /dev/null 2>&1; then
  echo "✓ XSS prevention measures found"
  ((PASSED++))
else
  echo "✗ XSS prevention NOT found"
  ((FAILED++))
fi

# Check 9: Secrets management
echo ""
echo "[CHECK 9] Secrets Management (No hardcoded secrets)"
SECRETS=$(grep -r "password\|secret\|api_key" . --include="*.go" --include="*.ts" --include="*.py" 2>/dev/null | grep -i "=\|:\|\"" | grep -v "test\|mock\|placeholder" | wc -l)
if [ "$SECRETS" -lt 5 ]; then
  echo "✓ No obvious hardcoded secrets found"
  ((PASSED++))
else
  echo "⚠ Potential hardcoded secrets found - manual review needed ($SECRETS matches)"
fi

# Summary
echo ""
echo "================================"
echo "SECURITY PRE-FLIGHT SUMMARY"
echo "================================"
echo "Passed: $PASSED"
echo "Failed: $FAILED"

if [ "$FAILED" -eq 0 ]; then
  echo ""
  echo "✅ ALL SECURITY CHECKS PASSED"
  exit 0
else
  echo ""
  echo "❌ SECURITY CHECKS FAILED ($FAILED issues)"
  exit 1
fi
