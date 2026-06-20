# Deployment Analysis - Vercel/Freemium Stack with WorkOS AuthKit

**Date**: 2025-11-22  
**Scope**: Vercel/Freemium deployment constraints, NATS alternatives, WorkOS integration

---

## PART 1: DEPLOYMENT ARCHITECTURE

### Current Stack Deployment

**Frontend**: Vercel (static files)
- ✅ React 19 + Vite SPA
- ✅ Vercel Edge Functions (optional)
- ✅ Freemium: $0/month

**Backend**: Railway or Fly.io (containerized)
- ✅ Go + Echo + gqlgen
- ✅ Freemium: $5-10/month
- ❌ NOT Vercel (Go not supported)

**Database**: Supabase (managed PostgreSQL)
- ✅ Freemium: $0/month (generous free tier)
- ✅ pgvector included
- ✅ Realtime included

**Cache**: Upstash Redis (serverless)
- ✅ Freemium: $0/month (10K commands/day)
- ✅ Serverless (no infrastructure)

**Message Queue**: NATS (problem!)
- ❌ NOT serverless
- ❌ Requires persistent connection
- ❌ Can't run on Vercel
- ❌ Can't run on Railway freemium

---

## PART 2: NATS PROBLEM & SOLUTIONS

### Why NATS Doesn't Work on Vercel/Freemium

**NATS Requirements**:
- ❌ Persistent connection (WebSocket/TCP)
- ❌ Stateful server
- ❌ Long-running process
- ❌ Not serverless-friendly

**Vercel Constraints**:
- ✅ Serverless functions (10s timeout)
- ✅ Stateless
- ✅ No persistent connections
- ❌ Can't run NATS

**Railway Freemium Constraints**:
- ✅ $5/month free tier
- ✅ Limited resources
- ❌ NATS requires dedicated server

### Solution 1: Upstash Kafka (Recommended) ✅

**What**: Serverless Kafka (managed)

**Advantages**:
- ✅ Serverless (no infrastructure)
- ✅ Freemium: $0/month (100K messages/month)
- ✅ Persistent (unlike NATS)
- ✅ Works with Vercel
- ✅ Works with Railway
- ✅ Works with Supabase

**Disadvantages**:
- ⚠️ Slightly higher latency than NATS
- ⚠️ Overkill for simple messaging

**Cost**:
- Free: 100K messages/month
- Paid: $0.20 per 1M messages

### Solution 2: Upstash Redis Streams ✅

**What**: Redis Streams (message queue)

**Advantages**:
- ✅ Serverless (no infrastructure)
- ✅ Freemium: $0/month (10K commands/day)
- ✅ Works with Vercel
- ✅ Works with Railway
- ✅ Lower latency than Kafka
- ✅ Simpler than Kafka

**Disadvantages**:
- ⚠️ Limited throughput (10K commands/day)
- ⚠️ Not ideal for high-volume messaging

**Cost**:
- Free: 10K commands/day
- Paid: $0.20 per 100K commands

### Solution 3: Inngest (Recommended for Background Jobs) ✅

**What**: Serverless background job queue

**Advantages**:
- ✅ Serverless (no infrastructure)
- ✅ Freemium: $0/month (generous free tier)
- ✅ Built for serverless
- ✅ Works with Vercel
- ✅ Works with Railway
- ✅ Durable functions (retry logic)
- ✅ Scheduling support

**Disadvantages**:
- ⚠️ Not real-time (for background jobs)
- ⚠️ Not ideal for agent coordination

**Cost**:
- Free: 1M function runs/month
- Paid: $0.50 per 1M runs

### Solution 4: Supabase Realtime (Already Included) ✅

**What**: WebSocket-based real-time messaging

**Advantages**:
- ✅ Already included with Supabase
- ✅ Freemium: $0/month
- ✅ Real-time (perfect for agent coordination)
- ✅ Works with Vercel
- ✅ Works with Railway
- ✅ Built-in to Supabase

**Disadvantages**:
- ⚠️ Not ideal for persistent queues
- ⚠️ Not ideal for background jobs

**Cost**:
- Free: Included with Supabase

### Verdict: Hybrid Approach

**For TraceRTM**:
- ✅ Supabase Realtime for real-time agent coordination
- ✅ Upstash Kafka for persistent event streaming
- ✅ Inngest for background jobs
- ❌ Remove NATS

---

## PART 3: WORKOS AUTHKIT INTEGRATION

### WorkOS AuthKit Overview

**What**: Enterprise authentication (SSO, OAuth, SAML)

**Advantages**:
- ✅ Enterprise SSO (Okta, Azure AD, Google Workspace)
- ✅ OAuth 2.0 (Google, GitHub, Microsoft)
- ✅ SAML support
- ✅ Organization management
- ✅ Freemium: $0/month (generous free tier)
- ✅ JWT tokens (standard)

**Disadvantages**:
- ⚠️ Not Supabase Auth
- ⚠️ Separate from database

### WorkOS AuthKit Integration with Go Backend

**Step 1: Frontend - Get Authorization URL**

```typescript
// React component
import { useWorkOS } from '@workos-inc/authkit-react';

export function LoginPage() {
  const { getAuthorizationUrl } = useWorkOS();

  const handleLogin = async () => {
    const authUrl = await getAuthorizationUrl({
      clientId: process.env.REACT_APP_WORKOS_CLIENT_ID,
      redirectUri: `${window.location.origin}/auth/callback`,
    });
    window.location.href = authUrl;
  };

  return <button onClick={handleLogin}>Sign In</button>;
}
```

**Step 2: Frontend - Handle Callback**

```typescript
// React component
import { useEffect } from 'react';
import { useWorkOS } from '@workos-inc/authkit-react';

export function AuthCallback() {
  const { authenticateWithCode } = useWorkOS();

  useEffect(() => {
    const code = new URLSearchParams(window.location.search).get('code');
    if (code) {
      authenticateWithCode(code);
    }
  }, []);

  return <div>Authenticating...</div>;
}
```

**Step 3: Backend - Verify JWT Token**

```go
import (
  "github.com/workos/workos-go/v4/pkg/workos"
  "github.com/workos/workos-go/v4/pkg/usermanagement"
)

func (h *Handler) VerifyToken(w http.ResponseWriter, r *http.Request) {
  // Get token from Authorization header
  token := r.Header.Get("Authorization")
  if token == "" {
    http.Error(w, "Missing token", 401)
    return
  }

  // Verify token with WorkOS
  client := usermanagement.NewClient(
    usermanagement.WithAPIKey(os.Getenv("WORKOS_API_KEY")),
  )

  user, err := client.ValidateSession(r.Context(), token)
  if err != nil {
    http.Error(w, "Invalid token", 401)
    return
  }

  // User is authenticated
  w.Header().Set("Content-Type", "application/json")
  json.NewEncoder(w).Encode(user)
}
```

**Step 4: GraphQL - Add Auth Middleware**

```go
func (h *Handler) AuthMiddleware(next http.Handler) http.Handler {
  return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    // Get token from Authorization header
    token := r.Header.Get("Authorization")
    if token == "" {
      http.Error(w, "Missing token", 401)
      return
    }

    // Verify token with WorkOS
    client := usermanagement.NewClient(
      usermanagement.WithAPIKey(os.Getenv("WORKOS_API_KEY")),
    )

    user, err := client.ValidateSession(r.Context(), token)
    if err != nil {
      http.Error(w, "Invalid token", 401)
      return
    }

    // Add user to context
    ctx := context.WithValue(r.Context(), "user", user)
    next.ServeHTTP(w, r.WithContext(ctx))
  })
}

// Use middleware
router.Use(h.AuthMiddleware)
```

**Step 5: GraphQL - Access User in Resolvers**

```go
func (r *queryResolver) Item(ctx context.Context, id string) (*Item, error) {
  // Get user from context
  user := ctx.Value("user").(*usermanagement.User)
  
  // Verify user has access to item
  item, err := r.db.GetItem(ctx, id)
  if err != nil {
    return nil, err
  }

  // Check permissions
  if item.OrganizationID != user.OrganizationID {
    return nil, fmt.Errorf("unauthorized")
  }

  return item, nil
}
```

### WorkOS AuthKit with Credentials

**From zen-mcp-server**:
```
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=project_...
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

**Environment Setup**:
```bash
# .env.local
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=project_...
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

---

## PART 4: COMPLETE FREEMIUM DEPLOYMENT STACK

### Frontend (Vercel)

```
Framework:      React 19 + TypeScript
Build Tool:     Vite 5.0 (SPA)
Deployment:     Vercel (static files)
Cost:           $0/month (freemium)

Features:
├─ Instant deployments
├─ Edge Functions (optional)
├─ Analytics
└─ Automatic HTTPS
```

### Backend (Railway or Fly.io)

```
Language:       Go 1.23+
Framework:      Echo + gqlgen
Deployment:     Railway or Fly.io
Cost:           $5-10/month (freemium)

Features:
├─ Containerized deployment
├─ Auto-scaling
├─ Environment variables
└─ Logs & monitoring
```

### Database (Supabase)

```
Database:       PostgreSQL + pgvector
Deployment:     Supabase (managed)
Cost:           $0/month (freemium)

Features:
├─ 500MB storage
├─ Realtime subscriptions
├─ pgvector (AI embeddings)
├─ JWT auth
└─ Storage (file uploads)
```

### Cache (Upstash Redis)

```
Cache:          Redis
Deployment:     Upstash (serverless)
Cost:           $0/month (freemium)

Features:
├─ 10K commands/day
├─ Serverless (no infrastructure)
├─ Automatic scaling
└─ Global edge locations
```

### Message Queue (Upstash Kafka + Inngest)

```
Queue:          Upstash Kafka + Inngest
Deployment:     Upstash + Inngest (serverless)
Cost:           $0/month (freemium)

Features:
├─ 100K messages/month (Kafka)
├─ 1M function runs/month (Inngest)
├─ Serverless (no infrastructure)
├─ Automatic scaling
└─ Durable functions (Inngest)
```

### Real-Time (Supabase Realtime)

```
Real-Time:      WebSocket
Deployment:     Supabase (included)
Cost:           $0/month (freemium)

Features:
├─ Real-time subscriptions
├─ Agent coordination
├─ Live updates
└─ Included with Supabase
```

### Auth (WorkOS AuthKit)

```
Auth:           WorkOS AuthKit
Deployment:     WorkOS (managed)
Cost:           $0/month (freemium)

Features:
├─ Enterprise SSO
├─ OAuth 2.0
├─ SAML support
├─ Organization management
└─ JWT tokens
```

---

## PART 5: COMPLETE FREEMIUM COST BREAKDOWN

```
Frontend (Vercel):              $0/month
Backend (Railway):              $5/month
Database (Supabase):            $0/month
Cache (Upstash Redis):          $0/month
Message Queue (Upstash Kafka):  $0/month
Background Jobs (Inngest):      $0/month
Real-Time (Supabase):           $0/month
Auth (WorkOS):                  $0/month

TOTAL:                          $5/month
```

---

## PART 6: UPDATED TECH STACK

### Backend Stack (Updated)

```
Language:       Go 1.23+

API Frameworks:
├─ GraphQL:     gqlgen (complex queries + subscriptions)
├─ tRPC:        Connect-RPC (simple operations)
└─ REST:        Echo (webhooks only)

Database:       Supabase (PostgreSQL + pgvector)
ORM:            GORM
Realtime:       Supabase Realtime (WebSocket)
Auth:           WorkOS AuthKit (JWT)
Storage:        Supabase Storage (signed URLs)
Message Queue:  Upstash Kafka (serverless)
Background Jobs: Inngest (serverless)
Cache:          Upstash Redis (serverless)
Async:          Goroutines
WebSocket:      gorilla/websocket
Validation:     go-playground/validator
Logging:        zap
Testing:        testify
Deployment:     Docker + Railway/Fly.io
```

### Frontend Stack (Updated)

```
Framework:      React 19 + TypeScript
Build Tool:     Vite 5.0 (SPA)
Routing:        React Router v7
State:          Legend State + TanStack Query v5
UI:             shadcn/ui + TailwindCSS
Forms:          React Hook Form + Zod
Tables:         TanStack Table v8
Graph:          Cytoscape.js
Node Editor:    React Flow
Code Editor:    Monaco Editor

API Clients:
├─ GraphQL:     Apollo Client (complex queries + subscriptions)
├─ tRPC:        @trpc/client (simple operations)
└─ REST:        openapi-fetch (file uploads via signed URLs)

Auth:           WorkOS AuthKit
Testing:        Vitest + Playwright
Deployment:     Vercel
```

---

## CONCLUSION

### ✅ COMPLETE FREEMIUM STACK

**Frontend**: Vercel ($0/month)
**Backend**: Railway ($5/month)
**Database**: Supabase ($0/month)
**Cache**: Upstash Redis ($0/month)
**Message Queue**: Upstash Kafka ($0/month)
**Background Jobs**: Inngest ($0/month)
**Real-Time**: Supabase Realtime ($0/month)
**Auth**: WorkOS AuthKit ($0/month)

**Total**: $5/month

**Key Changes**:
- ✅ Removed NATS (not serverless)
- ✅ Added Upstash Kafka (serverless message queue)
- ✅ Added Inngest (serverless background jobs)
- ✅ Replaced Supabase Auth with WorkOS AuthKit
- ✅ All services are freemium-friendly
- ✅ All services are serverless-friendly


