# Zod 4 + TanStack Router Compatibility Fix

**Date**: 2026-01-30
**Status**: ✅ RESOLVED
**Solution**: Runtime patch for router-generator

---

## Problem

TanStack Router v1.157 uses Zod v3 API internally:
```javascript
z.function().returns(z.string())  // Zod v3 API
```

Zod v4 changed the API to:
```javascript
z.function(z.tuple([]), z.string())  // Zod v4 API
```

**Error**:
```
TypeError: z.function(...).returns is not a function
```

---

## Solution Applied

### 1. Runtime Patch Script

**File**: `scripts/patch-router-zod4.js`

Automatically patches `@tanstack/router-generator` after install:
- Finds `z.function().returns()` calls
- Replaces with `z.function(z.tuple([]), ...)` (Zod 4 syntax)
- Runs after every `bun install`

### 2. Package.json Hook

Added postinstall script:
```json
{
  "scripts": {
    "postinstall": "node scripts/patch-router-zod4.js"
  }
}
```

### 3. Workspace Zod Version

Updated `/frontend/package.json`:
```json
{
  "zod": "4.3.6"  // Latest Zod 4
}
```

---

## Result

✅ **Both Zod 4 and TanStack Router work together**
✅ **Dev server starts successfully**
✅ **Route tree generates automatically**
✅ **No manual intervention needed after initial setup**

---

## Why This Works

1. **Patch runs automatically** - postinstall hook ensures patch is applied after every dependency install
2. **Non-breaking** - Patch only affects internal router-generator, not your app code
3. **Temporary** - Can be removed when TanStack Router v2 releases with native Zod 4 support

---

## Verification

```bash
bun run dev
# Output:
# ✅ Patched @tanstack/router-generator for Zod 4 compatibility
# VITE v8.0.0-beta.11  ready in 2851 ms
# ➜  Local:   http://localhost:5173/
```

---

## When to Remove This Patch

Monitor TanStack Router releases for Zod 4 support:
- Watch: https://github.com/TanStack/router/issues/6138
- When router v2 or v1.158+ supports Zod 4 natively
- Remove patch script and postinstall hook

---

## References

Research sources:
- [Issue #6138](https://github.com/TanStack/router/issues/6138) - Can't use zod v4
- [Issue #4322](https://github.com/TanStack/router/issues/4322) - Zod 4 support
- [Discussion #4092](https://github.com/TanStack/router/discussions/4092) - Feature request

---

**Status**: ✅ Zod 4 + TanStack Router working together with minimal patch
