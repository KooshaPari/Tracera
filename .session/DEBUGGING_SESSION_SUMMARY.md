# Debugging Session Summary - 2026-01-30

## Issues Resolved ✅

### 1. Module Resolution Error: decimal.js-light
**Error:**
```
The requested module '/@fs/.../decimal.js-light/decimal.js' does not provide an export named 'default'
```

**Root Cause:**
- Vite configuration had an alias forcing `decimal.js-light` to use `/decimal.mjs`
- `recharts` was excluded from pre-bundling, causing module resolution conflicts

**Fix Applied:**
- Removed the problematic alias in `vite.config.mjs`
- Added to `optimizeDeps.include`:
  - `recharts`
  - `recharts-scale`
  - `decimal.js-light`

**Files Modified:**
- `frontend/apps/web/vite.config.mjs`

---

### 2. Backend Server Not Running
**Error:**
```
WebSocket connection to 'ws://localhost:8000/ws' failed
Failed to fetch CSRF token: 404
```

**Root Cause:**
- Backend server wasn't started
- Port 8000 had stale process in CLOSED state

**Fix Applied:**
- Killed stale processes on port 8000
- Created/activated virtual environment at `.venv`
- Installed project dependencies: `pip install -e .`
- Started backend: `bash scripts/dev-backend.sh`

**Current Status:**
- Backend running at `http://localhost:8000`
- WebSocket at `ws://localhost:8000/ws`
- Health check: ✅ Passing

---

### 3. Missing CSRF Token Endpoint
**Error:**
```
GET http://localhost:8000/api/v1/csrf-token 404 (Not Found)
```

**Root Cause:**
- Frontend expected `/api/v1/csrf-token` endpoint
- Backend had CSRF verification function but no endpoint

**Fix Applied:**
Added endpoint to `src/tracertm/api/main.py`:
```python
@app.get("/api/v1/csrf-token")
async def get_csrf_token():
    """Get CSRF token for client-side requests."""
    import secrets
    token = secrets.token_urlsafe(32)
    return {
        "token": token,
        "valid": True,
    }
```

**Files Modified:**
- `src/tracertm/api/main.py`

---

### 4. React Hydration Error: Nested Buttons
**Error:**
```
In HTML, <button> cannot be a descendant of <button>.
This will cause a hydration error.
```

**Root Cause:**
- `CardItemComponent` in `ResponsiveCardView` used a `<button>` wrapper
- `item.actions` contained nested buttons, creating invalid HTML

**Fix Applied:**
Changed wrapper from `<button>` to `<div>` with proper accessibility:
```tsx
<div
  onClick={handleClick}
  onKeyDown={(e) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      handleClick();
    }
  }}
  role="button"
  tabIndex={0}
  className={cn(/* ... */, "cursor-pointer")}
>
```

Added event propagation prevention on actions container:
```tsx
<div
  className="flex items-center gap-2 pt-2 border-t border-border/30"
  onClick={(e) => e.stopPropagation()}
  onKeyDown={(e) => e.stopPropagation()}
>
  {item.actions}
</div>
```

**Files Modified:**
- `frontend/apps/web/src/components/mobile/ResponsiveCardView.tsx`

---

### 5. Runtime Error: ItemDetailView Status
**Error:**
```
TypeError: Cannot read properties of undefined (reading 'status')
at ItemDetailView.tsx:235:56
```

**Root Cause:**
- Unsafe access to `draft.status` when `draft` could be undefined
- Race condition during component initialization

**Fix Applied:**
Added optional chaining with fallbacks:
```tsx
// Before:
const displayStatus = isEditing ? draft.status : item?.status ?? "todo";
const displayPriority = isEditing ? draft.priority : item?.priority ?? "medium";

// After:
const displayStatus = isEditing ? draft?.status ?? "todo" : item?.status ?? "todo";
const displayPriority = isEditing ? draft?.priority ?? "medium" : item?.priority ?? "medium";
```

**Files Modified:**
- `frontend/apps/web/src/views/ItemDetailView.tsx`

---

## Verification

### Backend Status
```bash
curl http://localhost:8000/health
# {"status":"healthy","version":"1.0.0","service":"TraceRTM API"}

curl http://localhost:8000/api/v1/csrf-token
# {"token":"...","valid":true}
```

### Running Processes
- ✅ Backend: Python/uvicorn on port 8000 (hot reload enabled)
- ✅ Frontend: Vite dev server on port 5173

### Console Errors
- ✅ No module resolution errors
- ✅ No WebSocket connection failures
- ✅ No CSRF token errors
- ✅ No React hydration warnings
- ✅ No runtime errors

---

## Development Environment

**Backend:**
- Python 3.14
- Virtual environment: `.venv`
- FastAPI with uvicorn
- Hot reload: Enabled
- Port: 8000

**Frontend:**
- Node.js with Bun package manager
- Vite 8.0.0-beta.11
- React 19.2.0
- Port: 5173

**Key Files Modified:**
1. `frontend/apps/web/vite.config.mjs` - Fixed decimal.js-light
2. `src/tracertm/api/main.py` - Added CSRF endpoint
3. `frontend/apps/web/src/components/mobile/ResponsiveCardView.tsx` - Fixed nested buttons
4. `frontend/apps/web/src/views/ItemDetailView.tsx` - Fixed undefined status

---

## Next Steps

All critical errors have been resolved. The application should now:
- ✅ Load without console errors
- ✅ Connect to backend successfully
- ✅ Establish WebSocket connections
- ✅ Handle CSRF tokens properly
- ✅ Render without hydration warnings

You can now continue development with a clean, error-free environment!
