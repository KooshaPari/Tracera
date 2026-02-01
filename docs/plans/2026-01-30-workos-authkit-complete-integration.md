# WorkOS AuthKit Complete Integration - Execution Plan

**Date:** 2026-01-30
**Strategy:** DAG-based hybrid execution with 3-4 concurrent agents
**Total Tasks:** 21 tasks across 5 phases

## Execution Model

- **Phase 0:** Research (blocking, produces decisions)
- **Phases 1-4:** Feature-level tasks in mini-waves
- **Concurrency:** 3-4 agents running simultaneously
- **Flow:** New agent launches immediately when any completes
- **Tracking:** TaskCreate/TaskUpdate for progress

## Dependency DAG

```
R1 (Research Foundation)
├─── Wave 1 ───┐
│   F1, F2, F3 │ Frontend routes (parallel after R1)
│   B1, B2     │ Backend basics (parallel after R1)
└──────────────┘
     │
├─── Wave 2 ───┐
│   F4         │ Depends on F3 (token storage)
│   B3, B4     │ B3→R1, B4→B1 (CSRF + user sync)
└──────────────┘
     │
├─── Wave 3 ───┐
│   B5         │ Depends on B1-B4 (integration tests)
│   E1         │ Depends on F1-F4 (frontend env)
│   E2         │ Depends on B1-B5 (backend env)
└──────────────┘
     │
├─── Wave 4 ───┐
│   E3         │ Depends on E1, E2 (docker config)
│   D1, D2     │ Depends on E1, E2 (setup guides)
└──────────────┘
     │
├─── Wave 5 ───┐
│   D3, D4     │ D3→all impl, D4→D1-D3 (final docs)
└──────────────┘
```

## Phase 0: Research Foundation

### Task R1: Research & Decide
**Agent:** general-purpose
**Depends on:** None (blocks all)
**Files:** Create `docs/decisions/workos-auth-decisions.md`

**Objectives:**
1. Research token storage best practices (WorkOS docs, OWASP, web security)
   - localStorage vs HttpOnly cookies
   - XSS mitigation strategies
   - WorkOS SDK default behavior
   - Decision: Choose and document

2. Research user sync strategies
   - Database sync vs direct WorkOS API calls
   - Performance implications
   - Data consistency approaches
   - Decision: Choose and document

3. Research CSRF protection patterns
   - Double-submit cookie pattern
   - Synchronizer token pattern
   - SPA + API best practices
   - Decision: Keep current or add endpoint

**Deliverable:** `docs/decisions/workos-auth-decisions.md` with clear decisions

**Verification:**
- All 3 questions answered
- Decisions documented with reasoning
- File committed to git

---

## Phase 1: Frontend Routes (4 tasks)

### Task F1: Simplify Login Route
**Agent:** general-purpose
**Depends on:** R1
**Files:** `frontend/apps/web/src/routes/auth.login.tsx`

**Objectives:**
1. Remove custom login UI
2. Implement immediate redirect to WorkOS hosted UI
3. Keep loading state for authenticated users

**Implementation:**
```typescript
// Remove custom form, keep only:
useEffect(() => {
  if (isAuthenticated) {
    window.location.href = "/";
  } else {
    signIn(); // Immediate redirect
  }
}, [isAuthenticated, signIn]);

return <div>Redirecting to sign in...</div>;
```

**Verification:**
- Visit /auth/login → immediately redirects to WorkOS
- No custom form visible
- After auth, redirects back to app

---

### Task F2: Simplify Register Route
**Agent:** general-purpose
**Depends on:** R1
**Files:** `frontend/apps/web/src/routes/auth.register.tsx`

**Objectives:**
1. Remove custom registration UI
2. Implement immediate redirect using signUp()
3. Keep loading state for authenticated users

**Implementation:**
```typescript
// Same pattern as login but use signUp()
useEffect(() => {
  if (isAuthenticated) {
    window.location.href = "/";
  } else {
    signUp(); // Immediate redirect to signup
  }
}, [isAuthenticated, signUp]);

return <div>Redirecting to sign up...</div>;
```

**Verification:**
- Visit /auth/register → immediately redirects to WorkOS signup
- No custom form visible
- After registration, redirects back to app

---

### Task F3: Implement Token Storage Strategy
**Agent:** general-purpose
**Depends on:** R1 (needs storage decision)
**Files:**
- `frontend/apps/web/src/lib/auth-utils.ts`
- `frontend/apps/web/src/components/auth/AuthKitSync.tsx`
- `frontend/apps/web/src/stores/authStore.ts` (if needed)

**Objectives:**
1. Implement storage strategy from R1 decision
2. Add XSS mitigation (CSP headers or HttpOnly cookies)
3. Update token retrieval logic throughout app

**Implementation depends on R1 decision:**
- **If HttpOnly cookies:** Update backend to set cookies, remove localStorage
- **If localStorage + CSP:** Add CSP headers, keep localStorage
- **If WorkOS default:** Document and verify default behavior

**Verification:**
- Tokens stored per R1 decision
- XSS mitigation in place
- Login persists across page reloads
- Tokens accessible to API client

---

### Task F4: Update Protected Route Logic
**Agent:** general-purpose
**Depends on:** F3 (needs token storage working)
**Files:**
- `frontend/apps/web/src/components/auth/ProtectedRoute.tsx`
- `frontend/apps/web/src/api/client.ts`

**Objectives:**
1. Update token retrieval to use new storage strategy
2. Ensure API client gets tokens correctly
3. Test protected routes with new auth flow

**Implementation:**
```typescript
// Update wherever tokens are retrieved
const token = getTokenFromNewStorage(); // Based on F3 implementation
```

**Verification:**
- Protected routes work with new token storage
- API calls include correct Bearer token
- Unauthorized access redirects to login

---

## Phase 2: Backend Endpoints (5 tasks)

### Task B1: Implement Real /auth/me Endpoint
**Agent:** general-purpose
**Depends on:** R1 (needs user sync decision)
**Files:**
- `src/tracertm/api/routers/auth.py`
- `src/tracertm/models/user.py` (if DB sync chosen)

**Objectives:**
1. Implement real user fetch (DB or WorkOS API per R1)
2. Verify JWT token properly
3. Return actual user data (not hardcoded)

**Implementation (if DB sync):**
```python
@router.get("/me", response_model=MeResponse)
async def get_current_user(
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db)
):
    user_id = claims.get("sub")
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return MeResponse(
        user=user.dict(),
        claims=claims,
        account=user.account.dict() if user.account else None
    )
```

**Verification:**
- GET /api/v1/auth/me with valid token returns real user
- Invalid token returns 401
- User data matches WorkOS profile

---

### Task B2: Fix /auth/logout Endpoint
**Agent:** general-purpose
**Depends on:** R1
**Files:** `src/tracertm/api/routers/auth.py`

**Objectives:**
1. Verify correct dependency usage (should use get_db)
2. Implement token invalidation if needed per R1
3. Return success response

**Implementation:**
```python
@router.post("/logout", response_model=LogoutResponse)
async def logout(
    claims: dict = Depends(auth_guard),
    db: AsyncSession = Depends(get_db)  # Correct dependency
):
    # If token invalidation needed (per R1):
    # - Add token to blocklist
    # - Or mark session as expired
    return LogoutResponse(success=True)
```

**Verification:**
- POST /api/v1/auth/logout returns success
- No 422 dependency errors
- Token invalidation works if implemented

---

### Task B3: CSRF Token Endpoint (conditional)
**Agent:** general-purpose
**Depends on:** R1 (needs CSRF decision)
**Files:** `src/tracertm/api/routers/auth.py` or new `csrf.py`

**Objectives:**
1. Implement ONLY if R1 determines it's needed
2. If not needed, document why and remove redundant code
3. Ensure CSRF protection is adequate

**Implementation (if needed):**
```python
@router.get("/csrf-token")
async def get_csrf_token():
    token = secrets.token_urlsafe(32)
    # Store in session or return signed token
    return {"csrf_token": token}
```

**Verification:**
- If implemented: CSRF tokens generated and validated
- If removed: Double-submit cookie pattern working
- CSRF protection prevents attacks

---

### Task B4: User Database Sync (conditional)
**Agent:** general-purpose
**Depends on:** B1 (needs /me implementation)
**Files:**
- `src/tracertm/services/workos_auth.py`
- `src/tracertm/models/user.py`

**Objectives:**
1. Implement ONLY if R1 chose DB sync strategy
2. Sync user from WorkOS to database on login
3. Keep user data up to date

**Implementation (if needed):**
```python
async def sync_user_from_workos(workos_user: dict, db: AsyncSession):
    user = await db.get(User, workos_user["id"])
    if not user:
        user = User(id=workos_user["id"], ...)
        db.add(user)
    else:
        # Update existing user
        user.email = workos_user["email"]
        # ... other fields
    await db.commit()
```

**Verification:**
- Users sync to database on login
- User data stays current
- No duplicate user records

---

### Task B5: Backend Integration Tests
**Agent:** general-purpose
**Depends on:** B1, B2, B3, B4 (needs all endpoints working)
**Files:** Create `src/tracertm/tests/integration/test_auth_flow.py`

**Objectives:**
1. Test complete auth flow E2E
2. Verify all endpoints work together
3. Test error cases

**Test Cases:**
```python
async def test_auth_flow():
    # 1. Get user without token → 401
    # 2. Login with valid token → 200 + user data
    # 3. Access protected endpoint → 200
    # 4. Logout → 200
    # 5. Access protected endpoint → 401
```

**Verification:**
- All integration tests pass
- Auth flow works end-to-end
- Error handling correct

---

## Phase 3: Environment Configuration (3 tasks)

### Task E1: Frontend Environment Setup
**Agent:** general-purpose
**Depends on:** F1, F2, F3, F4 (frontend complete)
**Files:**
- `frontend/apps/web/.env.local.example`
- `frontend/apps/web/README.md`

**Objectives:**
1. Document all required VITE_* variables
2. Add setup instructions
3. Document WorkOS dashboard configuration

**Content:**
```bash
# .env.local.example
VITE_WORKOS_CLIENT_ID=client_01XXXXX
VITE_API_URL=http://localhost:4000
VITE_WS_URL=ws://localhost:4000
# DO NOT set VITE_WORKOS_API_HOSTNAME unless using custom domain
```

**Verification:**
- Clear environment variable documentation
- Setup instructions in README
- Example file committed

---

### Task E2: Backend Environment Setup
**Agent:** general-purpose
**Depends on:** B1, B2, B3, B4, B5 (backend complete)
**Files:**
- `.env.python-backend.example`
- Backend README or docs

**Objectives:**
1. Document WORKOS_API_KEY and all auth variables
2. Add WorkOS dashboard setup steps
3. Document optional configuration

**Content:**
```bash
# .env.python-backend.example
WORKOS_CLIENT_ID=client_01XXXXX
WORKOS_API_KEY=sk_test_XXXXX

# Optional
# WORKOS_JWKS_CACHE_TTL=900
# WORKOS_JWT_ISSUER=https://api.workos.com/
```

**Verification:**
- Complete backend env documentation
- WorkOS dashboard configuration steps
- Example file committed

---

### Task E3: Docker & Deployment Config
**Agent:** general-purpose
**Depends on:** E1, E2 (env docs complete)
**Files:**
- `docker-compose.yml`
- Dockerfiles
- Deployment scripts

**Objectives:**
1. Add environment variables to containers
2. Update deployment configurations
3. Verify auth works in Docker

**Implementation:**
```yaml
# docker-compose.yml
services:
  backend:
    environment:
      - WORKOS_CLIENT_ID=${WORKOS_CLIENT_ID}
      - WORKOS_API_KEY=${WORKOS_API_KEY}
```

**Verification:**
- Auth works in Docker containers
- Environment variables pass through correctly
- Deployment configs updated

---

## Phase 4: Documentation & Testing (4 tasks)

### Task D1: WorkOS Setup Guide
**Agent:** general-purpose
**Depends on:** E1, E2 (env setup complete)
**Files:** Create `docs/guides/WORKOS_AUTHKIT_SETUP.md`

**Objectives:**
1. Complete dashboard configuration walkthrough
2. Step-by-step integration instructions
3. Troubleshooting section

**Content Outline:**
1. Prerequisites
2. WorkOS Dashboard Setup
3. Environment Configuration
4. Testing the Integration
5. Common Issues

**Verification:**
- Complete setup guide
- Someone can follow from scratch
- Guide committed to docs/guides/

---

### Task D2: Troubleshooting Guide
**Agent:** general-purpose
**Depends on:** D1 (setup guide complete)
**Files:** Create `docs/guides/AUTH_TROUBLESHOOTING.md`

**Objectives:**
1. Document common issues and solutions
2. Debug checklist
3. Error message reference

**Content Outline:**
1. Login redirect not working
2. Token validation fails
3. Protected routes not working
4. CORS issues
5. Debug checklist

**Verification:**
- Covers all known edge cases
- Clear solutions for each issue
- Guide committed to docs/guides/

---

### Task D3: E2E Auth Flow Tests
**Agent:** general-purpose
**Depends on:** All F* and B* tasks (implementation complete)
**Files:** Create `frontend/apps/web/e2e/auth-complete-flow.spec.ts`

**Objectives:**
1. Test complete login → protected route → logout flow
2. Test token refresh mechanism
3. Test error cases

**Test Cases:**
```typescript
test('complete auth flow', async ({ page }) => {
  // 1. Visit login → redirects to WorkOS
  // 2. Mock WorkOS callback → redirects to app
  // 3. Access protected route → works
  // 4. Logout → clears state
  // 5. Access protected route → redirects to login
});
```

**Verification:**
- All E2E tests pass
- Coverage for all user journeys
- Tests committed and running in CI

---

### Task D4: Update Main README
**Agent:** general-purpose
**Depends on:** D1, D2, D3 (all docs complete)
**Files:**
- `README.md`
- `docs/INDEX.md`

**Objectives:**
1. Add authentication section to main README
2. Link to setup guides
3. Update docs index

**Content:**
```markdown
## Authentication

TracerTM uses WorkOS AuthKit for authentication.

- [Setup Guide](docs/guides/WORKOS_AUTHKIT_SETUP.md)
- [Troubleshooting](docs/guides/AUTH_TROUBLESHOOTING.md)
```

**Verification:**
- Auth properly documented in main docs
- Links work
- Index updated

---

## Execution Timeline

**Estimated Duration:** 2-3 hours (vs 5-6 hours sequential)

1. **Phase 0:** 15-20 minutes (R1 research)
2. **Wave 1:** 30-40 minutes (F1, F2, F3 + B1, B2)
3. **Wave 2:** 20-30 minutes (F4 + B3, B4)
4. **Wave 3:** 30-40 minutes (B5 + E1, E2)
5. **Wave 4:** 20-30 minutes (E3 + D1, D2)
6. **Wave 5:** 30-40 minutes (D3, D4)

## Success Criteria

✅ All 21 tasks marked completed in TaskList
✅ E2E test (D3) passes
✅ Documentation complete and accurate
✅ Auth works in dev and Docker environments
✅ No security vulnerabilities introduced

## Rollback Plan

Each task is atomic and can be reverted independently:
- Frontend changes don't break existing auth
- Backend changes are additive
- Documentation is non-breaking
- Tests can be disabled if needed

## Notes

- Maintain 3-4 concurrent agents throughout execution
- Launch next agent immediately when any completes
- Use TaskCreate/TaskUpdate for progress tracking
- Report status after each wave completion
