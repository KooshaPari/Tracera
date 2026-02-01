# use-sync-external-store Error Fix

## Problem
The dev server was failing with:
```
The requested module 'use-sync-external-store/shim/with-selector.js' does not provide an export named 'default'
```

This occurred because:
- `use-sync-external-store/shim/with-selector.js` uses CommonJS (`module.exports`)
- Zustand's ESM build (`zustand/esm/traditional.mjs`) tries to import it with ESM default import
- Vite 8 with Rolldown couldn't automatically handle this CJS->ESM conversion

## Solution Applied

### 1. Created ESM Shim
**File**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/src/lib/use-sync-external-store-with-selector-shim.ts`

This shim:
- Imports the CJS module
- Re-exports it with proper ESM default export
- Provides both named and default exports for compatibility

### 2. Updated Vite Config
**File**: `vite.config.mjs`

Changes:
- Added aliases to redirect imports to the shim (lines 68-76)
- Added `use-sync-external-store` to dedupe list (line 91)
- Added SSR noExternal config to prevent pre-bundling issues (lines 93-96)
- Fixed optimizeDeps entries to exclude test directories (line 152)

### 3. Clean Installation
```bash
rm -rf node_modules .vite dist
cd ../..
rm -rf node_modules
bun install
cd apps/web
bun run dev
```

## Result
Dev server now starts successfully:
```
VITE v8.0.0-beta.11  ready in 979 ms
➜  Local:   http://localhost:5174/
```

No `use-sync-external-store` errors.

## Files Modified
1. `src/lib/use-sync-external-store-with-selector-shim.ts` - ESM shim for CJS module
2. `vite.config.mjs` - Alias configuration and SSR settings

## Technical Details

The root cause was a mismatch between:
- **Package format**: `use-sync-external-store` uses CJS
- **Consumer format**: `zustand` ESM build expects ESM default import
- **Bundler behavior**: Vite 8 with Rolldown doesn't auto-convert this specific case

The shim acts as a bridge, importing the CJS module and re-exporting it in ESM format with both named and default exports.
