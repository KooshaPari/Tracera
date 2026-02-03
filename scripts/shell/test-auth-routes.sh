#!/bin/bash

echo "=== Auth Routes Verification ==="
echo ""

echo "1. Checking if auth route files exist..."
for route in login register logout callback; do
  file="frontend/apps/web/src/routes/auth.$route.tsx"
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file MISSING"
  fi
done

echo ""
echo "2. Checking WorkOS integration..."
grep -q "useAuth" frontend/apps/web/src/routes/auth.login.tsx && echo "  ✓ Login uses useAuth hook" || echo "  ✗ Login missing useAuth"
grep -q "signIn" frontend/apps/web/src/routes/auth.login.tsx && echo "  ✓ Login calls signIn()" || echo "  ✗ Login missing signIn"
grep -q "signUp" frontend/apps/web/src/routes/auth.register.tsx && echo "  ✓ Register calls signUp()" || echo "  ✗ Register missing signUp"
grep -q "signOut" frontend/apps/web/src/routes/auth.logout.tsx && echo "  ✓ Logout calls signOut()" || echo "  ✗ Logout missing signOut"

echo ""
echo "3. Checking TanStack Router integration..."
for route in login register logout callback; do
  file="frontend/apps/web/src/routes/auth.$route.tsx"
  grep -q "createFileRoute" "$file" && echo "  ✓ auth.$route uses createFileRoute" || echo "  ✗ auth.$route missing createFileRoute"
done

echo ""
echo "4. Checking auth store integration..."
grep -q "useAuthStore" frontend/apps/web/src/routes/auth.logout.tsx && echo "  ✓ Logout uses auth store" || echo "  ✗ Logout missing auth store"

echo ""
echo "5. Checking UI components..."
grep -q "Button" frontend/apps/web/src/routes/auth.login.tsx && echo "  ✓ Login has Button component" || echo "  ✗ Login missing Button"
grep -q "Loader2" frontend/apps/web/src/routes/auth.login.tsx && echo "  ✓ Login has loading state" || echo "  ✗ Login missing loading state"

echo ""
echo "=== Verification Complete ==="
