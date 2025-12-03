# Architecture Decisions & Reviews - TraceRTM

**Date**: 2025-11-22  
**Version**: 1.0  
**Status**: APPROVED

---

## ADR-1: MONOREPO ARCHITECTURE

### Decision
Use Turborepo + Bun for monorepo management

### Context
- Need to manage multiple apps (web, api, docs, email, storybook)
- Need to share code (ui, types, config)
- Need fast builds and installs
- Need good developer experience

### Options Considered
1. **Turborepo + pnpm** (rejected)
   - Pros: Mature, widely used
   - Cons: Slower than Bun

2. **Turborepo + Bun** (selected)
   - Pros: Fast, modern, good DX
   - Cons: Newer ecosystem

3. **Nx** (rejected)
   - Pros: Powerful, feature-rich
   - Cons: Steep learning curve, overkill

### Decision
**Turborepo + Bun** for optimal speed and DX

### Consequences
- ✅ Fast builds (3-5x faster than pnpm)
- ✅ Fast installs (10-20x faster than npm)
- ✅ Good developer experience
- ⚠️ Smaller ecosystem than pnpm
- ⚠️ Requires Bun knowledge

---

## ADR-2: FRONTEND FRAMEWORK

### Decision
Use React 19 + Vite for frontend

### Context
- Need complex UI (16 views, 100+ components)
- Need real-time updates
- Need offline-first support
- Need large ecosystem

### Options Considered
1. **React 19 + Vite** (selected)
   - Pros: Largest ecosystem, best for complex UIs
   - Cons: Larger bundle

2. **Vue 3** (rejected)
   - Pros: Simpler syntax, smaller bundle
   - Cons: Smaller ecosystem

3. **Svelte** (rejected)
   - Pros: Smallest bundle, best DX
   - Cons: Very small ecosystem

4. **Flutter Web** (rejected)
   - Pros: Cross-platform
   - Cons: No shadcn/ui, no React Flow

### Decision
**React 19 + Vite** for optimal ecosystem and features

### Consequences
- ✅ Largest ecosystem (shadcn/ui, React Flow, etc.)
- ✅ Best for complex UIs
- ✅ Largest hiring pool
- ⚠️ Larger bundle (42KB)
- ⚠️ More boilerplate

---

## ADR-3: BACKEND FRAMEWORK

### Decision
Use Go + Echo for backend

### Context
- Need high performance (1000+ concurrent agents)
- Need real-time WebSocket support
- Need fast development
- Need easy deployment

### Options Considered
1. **Go + Echo** (selected)
   - Pros: High performance, simple, fast
   - Cons: Steeper learning curve

2. **Node.js + Express** (rejected)
   - Pros: Same language as frontend
   - Cons: Slower, higher memory usage

3. **Rust + Actix** (rejected)
   - Pros: Highest performance
   - Cons: Steep learning curve, slow development

### Decision
**Go + Echo** for optimal performance and simplicity

### Consequences
- ✅ High performance (950K req/s)
- ✅ Low memory usage (50MB)
- ✅ Fast development
- ✅ Easy deployment
- ⚠️ Different language from frontend

---

## ADR-4: DATABASE

### Decision
Use Supabase (PostgreSQL + pgvector)

### Context
- Need relational data (items, links, agents)
- Need vector search (semantic search)
- Need real-time subscriptions
- Need managed service (no DevOps)
- Need freemium tier

### Options Considered
1. **Supabase** (selected)
   - Pros: PostgreSQL, pgvector, Realtime, freemium
   - Cons: Vendor lock-in

2. **Firebase** (rejected)
   - Pros: Managed, freemium
   - Cons: No pgvector, limited querying

3. **Self-hosted PostgreSQL** (rejected)
   - Pros: Full control
   - Cons: DevOps overhead

### Decision
**Supabase** for optimal features and freemium tier

### Consequences
- ✅ PostgreSQL (powerful, reliable)
- ✅ pgvector (semantic search)
- ✅ Realtime subscriptions
- ✅ Freemium tier
- ⚠️ Vendor lock-in

---

## ADR-5: STATE MANAGEMENT

### Decision
Use Legend State + TanStack Query

### Context
- Need offline-first support
- Need real-time sync
- Need conflict resolution
- Need good performance
- Need simple API

### Options Considered
1. **Legend State + TanStack Query** (selected)
   - Pros: Offline-first, real-time, CRDT, simple
   - Cons: Newer ecosystem

2. **Redux + RTK Query** (rejected)
   - Pros: Mature, widely used
   - Cons: Boilerplate, not offline-first

3. **Zustand + SWR** (rejected)
   - Pros: Simple, lightweight
   - Cons: Not offline-first

### Decision
**Legend State + TanStack Query** for offline-first and real-time

### Consequences
- ✅ Offline-first support
- ✅ Real-time sync
- ✅ CRDT conflict resolution
- ✅ Simple API
- ⚠️ Newer ecosystem

---

## ADR-6: REAL-TIME ARCHITECTURE

### Decision
Use Supabase Realtime + Upstash Kafka + Inngest

### Context
- Need real-time updates (100ms latency)
- Need persistent message queue
- Need background jobs
- Need serverless (no infrastructure)
- Need freemium tier

### Options Considered
1. **Supabase Realtime + Upstash Kafka + Inngest** (selected)
   - Pros: Real-time, persistent, serverless, freemium
   - Cons: Multiple services

2. **NATS** (rejected)
   - Pros: High performance
   - Cons: Not serverless, requires infrastructure

3. **Socket.io** (rejected)
   - Pros: Simple
   - Cons: Not persistent, not serverless

### Decision
**Supabase Realtime + Upstash Kafka + Inngest** for serverless real-time

### Consequences
- ✅ Real-time updates (100ms)
- ✅ Persistent message queue
- ✅ Background jobs
- ✅ Serverless (no infrastructure)
- ✅ Freemium tier
- ⚠️ Multiple services to manage

---

## ADR-7: DEPLOYMENT

### Decision
Use Fly.io (backend) + Vercel (frontend)

### Context
- Need serverless deployment
- Need freemium tier
- Need global deployment
- Need easy scaling
- Need zero infrastructure

### Options Considered
1. **Fly.io + Vercel** (selected)
   - Pros: Serverless, freemium, global, easy
   - Cons: Vendor lock-in

2. **Railway + Vercel** (rejected)
   - Pros: Simpler setup
   - Cons: Costs $5/month

3. **AWS + Vercel** (rejected)
   - Pros: Powerful
   - Cons: Complex, expensive

### Decision
**Fly.io + Vercel** for optimal serverless and freemium

### Consequences
- ✅ Serverless deployment
- ✅ Freemium tier ($0/month)
- ✅ Global deployment
- ✅ Easy scaling
- ✅ Zero infrastructure
- ⚠️ Vendor lock-in

---

## ADR-8: AUTHENTICATION

### Decision
Use WorkOS AuthKit

### Context
- Need enterprise SSO (Okta, Azure AD, Google Workspace)
- Need OAuth 2.0 (Google, GitHub, Microsoft)
- Need SAML support
- Need organization management
- Need freemium tier

### Options Considered
1. **WorkOS AuthKit** (selected)
   - Pros: Enterprise SSO, OAuth, SAML, freemium
   - Cons: Vendor lock-in

2. **Supabase Auth** (rejected)
   - Pros: Integrated with Supabase
   - Cons: Limited enterprise features

3. **Auth0** (rejected)
   - Pros: Powerful, widely used
   - Cons: Expensive, overkill

### Decision
**WorkOS AuthKit** for enterprise authentication

### Consequences
- ✅ Enterprise SSO
- ✅ OAuth 2.0
- ✅ SAML support
- ✅ Organization management
- ✅ Freemium tier
- ⚠️ Vendor lock-in

---

## ARU-1: FRONTEND ARCHITECTURE REVIEW

### Component Structure
- ✅ Atomic design (atoms, molecules, organisms)
- ✅ Shared components in packages/ui
- ✅ View components in apps/web/src/pages
- ✅ Custom hooks in apps/web/src/hooks

### State Management
- ✅ Global state in Legend State
- ✅ Server state in TanStack Query
- ✅ Form state in React Hook Form
- ✅ UI state in local component state

### Performance
- ✅ Code splitting by route
- ✅ Lazy loading of components
- ✅ Memoization of expensive components
- ✅ Virtual scrolling for large lists

### Testing
- ✅ Unit tests with Vitest
- ✅ Component tests with Vitest + React Testing Library
- ✅ E2E tests with Playwright
- ✅ 80%+ code coverage

---

## ARU-2: BACKEND ARCHITECTURE REVIEW

### API Structure
- ✅ GraphQL for complex queries
- ✅ tRPC for simple operations
- ✅ REST for webhooks
- ✅ WebSocket for real-time

### Database
- ✅ PostgreSQL for relational data
- ✅ pgvector for semantic search
- ✅ GORM for ORM
- ✅ Migrations for schema management

### Performance
- ✅ Connection pooling
- ✅ Query optimization
- ✅ Caching with Upstash Redis
- ✅ Async processing with Inngest

### Testing
- ✅ Unit tests with testify
- ✅ Integration tests with testify
- ✅ Load testing with k6
- ✅ 80%+ code coverage

---

## ARU-3: REAL-TIME ARCHITECTURE REVIEW

### WebSocket
- ✅ gorilla/websocket for WebSocket server
- ✅ Connection pooling
- ✅ Heartbeat monitoring
- ✅ Graceful shutdown

### Subscriptions
- ✅ GraphQL subscriptions
- ✅ Supabase Realtime
- ✅ Event broadcasting
- ✅ Presence tracking

### Message Queue
- ✅ Upstash Kafka for persistent queue
- ✅ Event sourcing
- ✅ Retry logic
- ✅ Dead letter queue

### Sync
- ✅ CRDT for conflict resolution
- ✅ Event sourcing for history
- ✅ Offline-first support
- ✅ Automatic sync

---

## ARU-4: SECURITY ARCHITECTURE REVIEW

### Authentication
- ✅ WorkOS AuthKit for SSO
- ✅ JWT tokens for API
- ✅ Secure token storage
- ✅ Token refresh logic

### Authorization
- ✅ Role-based access control (RBAC)
- ✅ Organization-based access
- ✅ Resource-level permissions
- ✅ Audit logging

### Data Protection
- ✅ HTTPS/TLS encryption
- ✅ Database encryption at rest
- ✅ Sensitive data masking
- ✅ GDPR compliance

### API Security
- ✅ Rate limiting
- ✅ CORS configuration
- ✅ CSRF protection
- ✅ Input validation


