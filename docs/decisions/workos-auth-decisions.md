# WorkOS AuthKit Implementation Decisions

**Date:** 2026-01-30
**Status:** Approved
**Author:** Research Task R1

---

## Executive Summary

This document outlines three critical architectural decisions for WorkOS AuthKit integration in TracerTM. All decisions prioritize production security best practices while maintaining developer experience and system performance.

**Key Decisions:**
1. **Token Storage:** HttpOnly cookies (production standard)
2. **User Data Sync:** Hybrid approach (minimal DB cache + WorkOS API)
3. **CSRF Protection:** Keep current double-submit cookie pattern

---

## Decision 1: Token Storage Strategy

### Chosen Approach: HttpOnly Cookies

**Production Implementation:**
- Refresh tokens stored in secure HttpOnly cookies (SameSite=Lax, Secure=true)
- Access tokens managed by WorkOS SDK (automatic refresh)
- No localStorage usage in production environment

**Development Mode Exception:**
- Allow `devMode={true}` on AuthKitProvider for localhost development
- localStorage usage permitted ONLY when custom authentication domain is not configured
- Clear documentation that this is development-only configuration

### Reasoning

**Security Considerations:**

1. **XSS Protection:**
   - HttpOnly cookies are inaccessible to JavaScript, preventing token theft via XSS attacks
   - OWASP guidance: "Any CSRF protection is null and void given the presence of XSS" - therefore preventing XSS is paramount
   - WorkOS official recommendation: "The HttpOnly flag makes cookies inaccessible to JavaScript, reducing the risk of XSS attacks"

2. **WorkOS Best Practices:**
   - WorkOS documentation explicitly states: "The access token should be stored as a secure cookie in the user's browser and validated by the backend on each request"
   - Default AuthKit configuration uses `httpOnly: true, secure: true, sameSite: "lax"`
   - Production-grade applications require custom authentication domains (e.g., auth.yourdomain.com)

3. **Industry Standards:**
   - Auth0 recommends storing tokens in browser memory as most secure option
   - localStorage vulnerable to XSS: "Storing tokens in browser local storage allows attackers to retrieve tokens if they can achieve running JavaScript through a cross-site scripting (XSS) attack"
   - Backend-for-Frontend (BFF) pattern recommended by OAuth for Browser-Based Apps

**Trade-offs Accepted:**

- **Mobile App Compatibility:** HttpOnly cookies require webview configuration; acceptable for web-first SPA
- **Implementation Complexity:** Requires backend cookie handling; mitigated by WorkOS SDK automation
- **Development Friction:** devMode flag provides escape hatch for local development without custom domains

### Implementation Impact

**Frontend Changes Required:**

1. Configure AuthKitProvider with production settings:
```typescript
<AuthKitProvider
  clientId={WORKOS_CLIENT_ID}
  apiHostname={PRODUCTION_AUTH_DOMAIN} // Required for production
  // devMode={true} only in local development without custom domain
>
```

2. Remove any localStorage token management code
3. Rely on WorkOS SDK's `getAccessToken()` for automatic token refresh
4. Use `credentials: 'include'` for all API calls (already implemented)

**Backend Changes Required:**

1. Configure CORS to allow credentials:
```python
# Already implemented in main.py
CORSMiddleware(
    app,
    allow_credentials=True,
    allow_origins=[FRONTEND_URL],
)
```

2. Set secure cookie attributes in responses:
```python
# Cookies set by WorkOS SDK should have:
# - HttpOnly=true
# - Secure=true (HTTPS only)
# - SameSite=Lax (CSRF protection)
```

3. Validate access tokens on each request (already implemented via `auth_guard`)

**Environment Configuration:**

- `WORKOS_CLIENT_ID` - Required
- `WORKOS_API_KEY` - Required for backend verification
- `WORKOS_AUTH_DOMAIN` - Custom domain (e.g., auth.tracertm.com) for production
- `FRONTEND_URL` - For CORS configuration

### References

- [WorkOS: JWT Storage Best Practices](https://workos.com/blog/secure-jwt-storage)
- [WorkOS: Session Management for Frontend Apps](https://workos.com/blog/session-management-for-frontend-apps-with-authkit)
- [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP: Cross-Site Scripting (XSS) Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [WorkOS Docs: AuthKit Sessions](https://workos.com/docs/authkit/sessions)
- [Auth0: Token Storage Security Guidance](https://auth0.com/docs/secure/security-guidance/data-security/token-storage)

---

## Decision 2: User Data Sync Strategy

### Chosen Approach: Hybrid (Minimal DB Cache + WorkOS API)

**Architecture:**

1. **Session Data:** WorkOS is source of truth for authentication state
2. **User Profile Cache:** Store minimal user metadata in PostgreSQL for application-specific features
3. **Real-time Sync:** Use WorkOS Events API for user data updates
4. **Validation Pattern:** Verify access tokens on each request, cache user lookups

**Database Schema:**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    workos_user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50),
    metadata JSONB,
    last_synced_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_workos_id ON users(workos_user_id);
CREATE INDEX idx_users_email ON users(email);
```

### Reasoning

**Performance Considerations:**

1. **API Rate Limits:**
   - WorkOS allows 6,000 general requests per minute
   - Free tier: 1 million MAUs included
   - Rate limit errors (429) require exponential backoff
   - Caching reduces unnecessary API calls

2. **Latency Optimization:**
   - Local DB query: ~5-10ms
   - WorkOS API call: ~50-200ms (network + processing)
   - Caching improves perceived performance for user-facing operations

3. **Offline Scenarios:**
   - Database cache allows graceful degradation during WorkOS API outages
   - Application can continue with stale data while WorkOS recovers
   - Events API ensures eventual consistency

**Data Consistency:**

1. **WorkOS Events API:**
   - WorkOS recommends Events API over webhooks for data synchronization
   - Process events synchronously in order they occurred
   - Use `updated_at` timestamps to prevent overwrites
   - Single worker pattern ensures serial processing

2. **User Events to Monitor:**
   - `user.created` - Create local user record
   - `user.updated` - Update cached profile data
   - `user.deleted` - Mark user as deleted (soft delete)

3. **Separation of Concerns:**
   - Database handles application-specific user data (project memberships, preferences)
   - WorkOS handles authentication and identity verification
   - Clear boundary: WorkOS is authoritative for auth, DB is cache

**Scalability:**

- WorkOS pricing: Free up to 1M MAUs, then $2,500/month per additional 1M
- Database scales independently from auth provider
- Events API designed for high-throughput applications
- Single worker processing prevents race conditions

### Implementation Impact

**What Needs to Be Built:**

1. **User Repository (Backend):**
```python
class UserRepository:
    async def create_from_workos(self, workos_user_data: dict) -> User:
        """Create local user record from WorkOS user data"""

    async def update_from_workos(self, workos_user_id: str, updates: dict) -> User:
        """Update cached user data from WorkOS event"""

    async def get_by_workos_id(self, workos_user_id: str) -> Optional[User]:
        """Retrieve cached user by WorkOS ID"""
```

2. **Events API Integration (Backend):**
```python
class WorkOSEventHandler:
    async def sync_user_events(self):
        """Poll WorkOS Events API for user events"""
        events = workos_client.events.list_events(
            events=["user.created", "user.updated", "user.deleted"]
        )
        for event in events:
            await self.process_event(event)

    async def process_event(self, event: dict):
        """Process individual user event"""
        if event["event"] == "user.created":
            await user_repo.create_from_workos(event["data"])
        elif event["event"] == "user.updated":
            await user_repo.update_from_workos(
                event["data"]["id"],
                event["data"]
            )
```

3. **Auth Guard Enhancement (Backend):**
```python
async def auth_guard(request: Request) -> dict:
    """Verify token and return user claims"""
    token = extract_token(request)

    # Verify token with WorkOS (fast, cached by SDK)
    claims = workos_auth_service.verify_access_token(token)

    # Optional: Enrich claims with cached user data
    user = await user_repo.get_by_workos_id(claims["sub"])
    if user:
        claims["user_metadata"] = user.metadata

    return claims
```

4. **Frontend User Store (Optional Enhancement):**
```typescript
// Current: useAuth hook provides WorkOS user data
// Enhancement: Merge with application-specific metadata
export function useEnhancedUser() {
    const { user: workosUser } = useAuth();
    const { data: appMetadata } = useQuery({
        queryKey: ['user-metadata', workosUser?.id],
        queryFn: () => api.getUserMetadata(workosUser.id),
        enabled: !!workosUser,
        staleTime: 5 * 60 * 1000, // 5 minute cache
    });

    return {
        ...workosUser,
        ...appMetadata,
    };
}
```

**Database Changes:**

- Add `users` table with WorkOS ID reference
- Add `user_project_roles` table for application-specific permissions
- Migration script to backfill existing WorkOS users (if any)

**Operational Considerations:**

- Events API polling: Run every 30-60 seconds via background job
- Monitor sync lag between WorkOS and local DB
- Implement replay mechanism for missed events
- Log sync failures for investigation

### References

- [WorkOS: Data Syncing with Events API](https://workos.com/docs/events/data-syncing)
- [WorkOS: Sync Data Using Events API](https://workos.com/docs/events/data-syncing/events-api)
- [WorkOS: API Reference (Rate Limits)](https://workos.com/docs/reference)
- [WorkOS Pricing](https://workos.com/pricing)
- [Authentication with WorkOS in Next.js Guide](https://www.nirtamir.com/articles/authentication-with-workos-in-next-js-a-comprehensive-guide/)

---

## Decision 3: CSRF Protection Strategy

### Chosen Approach: Keep Current Double-Submit Cookie Pattern

**Current Implementation:**
- Frontend: Double-submit cookie pattern (csrf.ts)
- Backend: CSRF token endpoint at `/api/v1/csrf-token`
- State-changing requests include `X-CSRF-Token` header

**Maintain as-is with minor enhancements:**
- Keep existing `/api/v1/csrf-token` endpoint
- Continue using double-submit cookie pattern
- Add SameSite cookie attributes for defense-in-depth
- Document that this complements WorkOS token security

### Reasoning

**Security Assessment:**

1. **SPA Security Model:**
   - OWASP guidance: SPAs use custom headers (X-CSRF-Token) for CSRF protection
   - Server validates token from header matches token from cookie
   - SameSite cookies provide additional protection layer

2. **WorkOS Authentication Flow:**
   - WorkOS tokens provide authentication but not CSRF protection
   - CSRF attacks can occur even with valid authentication tokens
   - Example: Malicious site tricks authenticated user into unwanted API call

3. **Defense-in-Depth Principle:**
   - Multiple security layers are better than single point of failure
   - Double-submit cookies protect against CSRF
   - HttpOnly cookies protect against XSS
   - WorkOS tokens verify identity
   - Together: comprehensive security model

4. **OWASP Recommendations:**
   - "Cross-Site Scripting (XSS) can defeat all CSRF mitigation techniques"
   - Therefore: Prevent XSS (HttpOnly cookies) AND prevent CSRF (double-submit pattern)
   - SameSite=Lax provides CSRF protection for top-level navigations
   - Custom header verification catches same-site attacks

**Why Not Remove CSRF Protection:**

1. **WorkOS Tokens Alone Insufficient:**
   - Tokens prove user identity, not request legitimacy
   - Attacker with user's browser can trigger authenticated requests
   - CSRF protection ensures requests originated from legitimate frontend

2. **Cookie-Based Sessions Need CSRF Protection:**
   - Even though using WorkOS, cookies are still in play (refresh tokens)
   - SameSite=Lax helps but not foolproof (same-site attacks possible)
   - Custom header requirement (X-CSRF-Token) prevents cross-origin attacks

3. **Low Implementation Cost:**
   - Already implemented and working
   - Minimal performance overhead (~5-10ms per request)
   - Removal would save negligible resources while reducing security

**Why Not Add Synchronizer Token Pattern:**

1. **Current Pattern Sufficient:**
   - Double-submit cookies meet OWASP guidelines for SPAs
   - `/api/v1/csrf-token` endpoint provides token generation
   - Frontend manages token lifecycle (csrf.ts)

2. **Synchronizer Pattern Adds Complexity:**
   - Requires server-side session storage (Redis/DB)
   - Token validation on every request increases latency
   - State management across multiple backend instances
   - Not meaningfully more secure than current approach

3. **Modern Alternatives:**
   - SameSite cookies provide partial CSRF protection
   - Custom headers (X-CSRF-Token) prevent simple CSRF attacks
   - Combined approach is industry standard for SPAs

### Implementation Impact

**What Stays:**
- `/api/v1/csrf-token` endpoint (already exists at line 676 in main.py)
- csrf.ts token management utilities
- X-CSRF-Token header injection in API client
- Double-submit cookie validation pattern

**What Changes:**

1. **Backend Cookie Attributes (Enhancement):**
```python
@app.get("/api/v1/csrf-token")
async def get_csrf_token(response: Response):
    """Get CSRF token for client-side requests."""
    import secrets
    token = secrets.token_urlsafe(32)

    # Set cookie with secure attributes
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # Frontend needs to read this
        secure=True,     # HTTPS only
        samesite="lax",  # CSRF protection
        max_age=3600,    # 1 hour
    )

    return {
        "token": token,
        "valid": True,
    }
```

2. **Documentation Updates:**
   - Document why CSRF protection is needed alongside WorkOS
   - Explain defense-in-depth security model
   - Add security architecture diagram

3. **Testing:**
   - Verify CSRF protection blocks cross-origin requests
   - Test that legitimate requests include correct token
   - Validate cookie attributes in production environment

**What Gets Removed:**
- Nothing. Keep all existing CSRF infrastructure.

**Environment Variables:**
- No new environment variables required
- Existing CORS configuration sufficient

### References

- [OWASP: Cross-Site Request Forgery Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Okta: Defend Your SPA from CSRF and XSS](https://developer.okta.com/blog/2022/07/08/spa-web-security-csrf-xss)
- [Medium: Modern CSRF Mitigation in SPAs](https://medium.com/tresorit-engineering/modern-csrf-mitigation-in-single-page-applications-695bcb538eec)
- [Curity: OAuth for Single Page Applications Best Practices](https://curity.io/resources/learn/spa-best-practices/)
- [OWASP: Cross-Site Request Forgery (CSRF)](https://owasp.org/www-community/attacks/csrf)

---

## Implementation Priorities

### Phase 1: Security Foundations (Week 1)
1. Configure HttpOnly cookies for WorkOS refresh tokens
2. Verify CSRF token endpoint functionality
3. Test authentication flow end-to-end

### Phase 2: User Data Sync (Week 2)
1. Create users table and repository
2. Implement WorkOS Events API integration
3. Build user sync background job

### Phase 3: Production Readiness (Week 3)
1. Set up custom authentication domain (auth.tracertm.com)
2. Configure production environment variables
3. Run security audit (penetration testing)
4. Document security architecture

---

## Success Metrics

**Security:**
- Zero XSS vulnerabilities in token storage
- Zero successful CSRF attacks in testing
- 100% of tokens stored in HttpOnly cookies (production)

**Performance:**
- User profile lookups < 50ms (95th percentile)
- WorkOS API calls reduced by 70% via caching
- Events API sync lag < 60 seconds

**Reliability:**
- 99.9% authentication success rate
- Graceful degradation during WorkOS outages
- Zero token-related user logout issues

---

## Rollback Plan

If any decision proves problematic in production:

**Token Storage:**
- Emergency rollback: Enable devMode flag temporarily
- Mitigation: Add aggressive XSS protection (CSP headers)
- Long-term: Migrate to Backend-for-Frontend pattern

**User Data Sync:**
- Emergency: Disable Events API polling, use WorkOS API directly
- Mitigation: Increase cache TTL to reduce API load
- Long-term: Implement read-through cache pattern

**CSRF Protection:**
- Emergency: Add rate limiting to prevent brute force
- Mitigation: Implement request origin validation
- Long-term: Upgrade to synchronizer token pattern if needed

---

## Appendix: Security Layers

**Defense-in-Depth Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                     Security Layers                          │
├─────────────────────────────────────────────────────────────┤
│ 1. XSS Prevention                                           │
│    - HttpOnly cookies (refresh tokens)                      │
│    - Content Security Policy (CSP)                          │
│    - Input sanitization                                     │
├─────────────────────────────────────────────────────────────┤
│ 2. CSRF Protection                                          │
│    - Double-submit cookie pattern                           │
│    - SameSite cookie attributes                            │
│    - Custom header validation                               │
├─────────────────────────────────────────────────────────────┤
│ 3. Authentication                                            │
│    - WorkOS AuthKit (OAuth/OIDC)                           │
│    - JWT access token validation                           │
│    - Automatic token refresh                                │
├─────────────────────────────────────────────────────────────┤
│ 4. Transport Security                                        │
│    - HTTPS only (Secure flag)                              │
│    - TLS 1.2+ required                                      │
│    - HSTS headers                                           │
├─────────────────────────────────────────────────────────────┤
│ 5. Rate Limiting                                            │
│    - Per-IP rate limits                                     │
│    - Per-user rate limits                                   │
│    - WorkOS API rate limit handling                         │
└─────────────────────────────────────────────────────────────┘
```

---

**Document Version:** 1.0
**Last Updated:** 2026-01-30
**Next Review:** 2026-02-28 (30 days)
