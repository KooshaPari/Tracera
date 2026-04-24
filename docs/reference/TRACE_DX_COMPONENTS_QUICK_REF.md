> Historical note: this document preserves the pre-Phenotype observability stack. The active org path is the shared collector, Grafana Alloy, and Grafana Tempo. Treat Jaeger and Promtail references below as legacy context only.

# Trace Project-Specific DX Components - Quick Reference

**Source:** `docs/research/TRACE_PROJECT_SPECIFIC_DX_COMPONENTS.md` (1,904 lines)
**Date:** 2026-02-06
**Total Components:** 26 (10 agents + 12 skills + 4 hooks)

---

## ⚡ 8 Quick Wins (Deploy Today - 3-4 hours/week savings)

| Component | Type | Value | Time Savings |
|-----------|------|-------|--------------|
| Graph Visualization Expert | Agent | Gap 5.1, 5.7 GPU work | 30-40 min/task |
| API Testing Specialist | Agent | MSW blocker fixes | 30+ min/issue |
| Accessibility Testing Expert | Agent | Gap 5.5 E2E tests | 20 min/task |
| Performance Optimization Specialist | Agent | Proactive audits | 40 min/week |
| /add-graph-feature | Skill | Graph features workflow | 20-30 min/feature |
| /add-websocket-event | Skill | NATS pub/sub setup | 15 min/event |
| /fix-msw-setup | Skill | MSW debugging | 30+ min/issue |
| Graph Performance Gate | Hook | Prevent regressions | 1-2h rollback avoided |

**Deploy Priority:** Week 1

---

## 🤖 10 Domain Agents

### High Priority (Deploy Week 1)

#### 1. Graph Visualization Expert ⚡
**Domains:** Sigma.js, WebGL, GPU compute, force layouts
**Triggers:** "graph", "sigma", "webgl", "gpu layout"
**Value:** Gap 5.1 (visual regression), Gap 5.7 (GPU shaders)
**Performance Targets:** 10k nodes <100ms, 60 FPS

#### 2. API Testing Specialist ⚡
**Domains:** MSW setup, integration tests, mocking patterns
**Triggers:** "msw", "integration test", "api mock"
**Value:** Session 6 MSW blocker, Gap 5.3 integration tests
**Critical Fix:** MSW ESM/CommonJS resolution

#### 3. Accessibility Testing Expert ⚡
**Domains:** WCAG 2.1 AA, axe-core, keyboard nav
**Triggers:** "accessibility", "a11y", "wcag"
**Value:** Gap 5.5 E2E accessibility tests
**Standards:** WCAG 2.1 AA compliance, 0 violations

#### 4. Performance Optimization Specialist ⚡
**Domains:** React perf, DB queries, caching strategies
**Triggers:** "performance", "slow", "optimize"
**Value:** Proactive bottleneck detection
**Targets:** LCP <2.5s, FID <100ms, CLS <0.1

### Medium Priority (Deploy Weeks 2-3)

#### 5. Temporal Workflow Specialist
**Domains:** Activities, workflows, time-skipping tests
**Triggers:** "temporal", "workflow", "activity"
**Value:** Gap 5.4 snapshot workflow

#### 6. Neo4j Cypher Expert
**Domains:** Query optimization, EXPLAIN/PROFILE
**Triggers:** "neo4j", "cypher", "graph query"
**Value:** Query performance, cardinality tuning

#### 7. NATS Event Streaming Expert
**Domains:** JetStream, WebSocket bridge, pub/sub
**Triggers:** "nats", "websocket", "event"
**Value:** Phase 5.2 OAuth events

#### 8. Observability Engineer
**Domains:** Prometheus, Loki, Jaeger, dashboards
**Triggers:** "observability", "metrics", "tracing"
**Value:** Production monitoring

#### 9. Security Audit Specialist
**Domains:** OWASP Top 10, OAuth 2.0, XSS/CSRF
**Triggers:** "security", "oauth", "auth"
**Value:** Production readiness

#### 10. Database Migration Specialist
**Domains:** Alembic, zero-downtime, rollback
**Triggers:** "migration", "database schema"
**Value:** Dependency hardening Phase 2

---

## 🛠️ 12 Project Skills (Workflows)

### High Priority (Deploy Weeks 1-2)

#### Graph & Visualization
- **/add-graph-feature** ⚡ - WebGL shader + Sigma integration (20-30 min)
- **/performance-audit** ⚡ - Profile graph rendering, bottleneck report (15-20 min)

#### Testing
- **/add-e2e-test** - Playwright E2E with accessibility checks (25-30 min)
- **/fix-msw-setup** ⚡ - MSW diagnostics + auto-fix (10-15 min)
- **/add-temporal-test** - Unit + integration + replay tests (30-40 min)
- **/add-performance-test** - k6 load testing (20-25 min)

#### Backend
- **/temporal-activity** - Activity + workflow + tests (25-30 min)
- **/neo4j-migration** - Schema change with rollback (30-40 min)
- **/add-websocket-event** ⚡ - NATS pub/sub + tests (15-20 min)
- **/add-api-endpoint** - Handler + tests + OpenAPI (30-35 min)

#### Database
- **/add-cypher-query** - Optimized Neo4j query with EXPLAIN (20-25 min)
- **/add-oauth-handler** - OAuth flow + session + tests (40-50 min)

---

## 🎯 4 Project Hooks (Quality Gates)

### 1. Graph Performance Gate ⚡
**Event:** PostToolUse (Edit graph files)
**Checks:**
- FPS ≥30 for 10k nodes
- Layout computation <100ms
- Viewport culling accuracy ≥98%

**Action:** Fail build if thresholds violated

### 2. Cypher Complexity Gate
**Event:** PreToolUse (Edit .cypher files)
**Checks:**
- No unbounded variable-length patterns (`[*]`)
- EXPLAIN plan cost <1000
- Cardinality estimates <100k

**Action:** Warn and suggest optimization

### 3. WebSocket Event Schema Gate
**Event:** PreToolUse (Publish NATS event)
**Checks:**
- Token masking enforced
- Schema validation passes
- Event size <1MB

**Action:** Block invalid events

### 4. Temporal Workflow Versioning Gate
**Event:** PreCommit (workflow.py changes)
**Checks:**
- Version number incremented
- Replay test exists
- Backwards compatibility verified

**Action:** Fail commit if version issues

---

## 📅 6-Week Rollout Plan

| Week | Focus | Components | Effort |
|------|-------|------------|--------|
| 1 | Quick Wins | 4 agents + 3 skills + 1 hook | 8h |
| 2 | Testing & Graph | 2 agents + 4 skills | 6h |
| 3 | Backend & Data | 3 agents + 3 skills | 8h |
| 4 | Observability | 1 agent + 2 skills | 4h |
| 5 | Quality Gates | 3 hooks | 4h |
| 6 | Integration & Testing | Validation | 4h |
| **Total** | | **26 components** | **34h** |

**Expected ROI:** 3-4 hours/week × 26 weeks = 78-104 hours saved (2-3x return)

---

## 🎯 Alignment with Active Work

### Phase 5 Gaps
- **Gap 5.1** (WebGL visual) → Graph Visualization Expert
- **Gap 5.3** (Integration tests) → API Testing Specialist
- **Gap 5.4** (Temporal workflow) → Temporal Workflow Specialist
- **Gap 5.5** (Accessibility) → Accessibility Testing Expert
- **Gap 5.7** (GPU shaders) → Graph Visualization Expert
- **Gap 5.8** (Spatial indexing) → Graph Visualization Expert

### Session 6 MSW Blocker
- **Issue:** MSW ESM/CommonJS compatibility
- **Solution:** API Testing Specialist + /fix-msw-setup skill
- **Value:** Unblock 29 tests, 30+ min saved

### Dependency Hardening
- **Phase 2:** Database Migration Specialist
- **Security:** Security Audit Specialist + Cypher Complexity Gate

---

## 🚀 Pilot Deployment (Week 1)

**Install:**
1. Graph Visualization Expert agent
2. API Testing Specialist agent
3. Accessibility Testing Expert agent
4. /add-graph-feature skill
5. /fix-msw-setup skill
6. /add-websocket-event skill
7. Graph Performance Gate hook

**Test on Real Work:**
- Gap 5.7 GPU shader implementation
- Session 6 MSW blocker resolution
- Gap 5.5 accessibility tests

**Measure:**
- Time to complete tasks (before/after)
- Quality metrics (FPS, coverage, a11y violations)
- Developer satisfaction (1-10 scale)

**Success Criteria:**
- ≥30% time savings on measured tasks
- 0 regression in quality metrics
- ≥8/10 satisfaction score

If pilot successful → Full rollout Week 2-6

---

**Full Implementation Details:** `docs/research/TRACE_PROJECT_SPECIFIC_DX_COMPONENTS.md`
