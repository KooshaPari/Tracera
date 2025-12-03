# TraceRTM ↔ BMM ↔ OpenSpec Integration Analysis

## Current State

### TraceRTM (Requirements Traceability)
**What it does:**
- Multi-view project management (FEATURE, CODE, TEST, DESIGN, API, DOC, etc.)
- Bidirectional traceability linking (implements, tests, depends_on, etc.)
- Single Source of Truth (SSOT) for all items across views
- Graph-based dependency analysis (cycles, impact, shortest path)

**Enforcement mechanisms:**
- ✅ Link validation (both items must exist)
- ✅ Traceability matrix (coverage % by view pair)
- ✅ Gap detection (items without links)
- ✅ Impact analysis (downstream/upstream effects)
- ✅ Cycle detection (circular dependencies)
- ⚠️ **Missing:** Mandatory linking policies, workflow enforcement

### BMM (BMad Method Module)
**What it does:**
- AI-driven agile development workflows
- 12 specialized agents (TEA, DEV, QA, etc.)
- Test Architect workflow: requirements → tests → quality gate
- Traceability matrix generation (P0/P1/P2/P3 coverage)
- Quality gate decisions (PASS/CONCERNS/FAIL/WAIVED)

**Guidance mechanisms:**
- ✅ Markdown-based workflow instructions (.bmad/bmm/workflows/)
- ✅ Test priority matrix (P0/P1/P2/P3 risk framework)
- ✅ Risk governance (6 categories: TECH, SEC, PERF, DATA, BUS, OPS)
- ✅ Gate decision templates (trace-template.md)
- ✅ Agent personas and menus (.bmad/bmm/agents/)

### OpenSpec
**What it does:**
- Lightweight spec-driven development (TypeScript-based)
- Three commands: /openspec:proposal, /openspec:apply, /openspec:archive
- Specs directory (source of truth) + changes directory (proposals)
- Works with Claude, Copilot, Cursor, Gemini

**Guidance mechanisms:**
- ✅ CLI templates and prompts
- ✅ Spec → Plan → Tasks → Implement phases
- ⚠️ **Limited:** No traceability enforcement

---

## Integration Gaps

### 1. TraceRTM ↔ BMM Integration
**Current state:** Loose coupling
- BMM generates traceability matrices (via TEA workflow)
- TraceRTM stores items/links in database
- **Gap:** No bidirectional sync

**What's missing:**
- ❌ `rtm ingest bmad` command (import BMM artifacts)
- ❌ `rtm export bmad` command (export to BMM format)
- ❌ Automatic linking from BMM test design to TraceRTM items
- ❌ Quality gate decisions stored in TraceRTM

### 2. TraceRTM ↔ OpenSpec Integration
**Current state:** No integration
- OpenSpec specs directory exists but not connected to TraceRTM
- **Gap:** No spec ingestion or linking

**What's missing:**
- ❌ `rtm ingest openspec` command
- ❌ `rtm export openspec` command
- ❌ Automatic linking from OpenSpec specs to TraceRTM items
- ❌ Spec changes tracked in TraceRTM

### 3. BMM ↔ OpenSpec Integration
**Current state:** No integration
- Both exist in project but don't communicate
- **Gap:** No workflow coordination

**What's missing:**
- ❌ OpenSpec proposals → BMM workflows
- ❌ BMM decisions → OpenSpec archives
- ❌ Shared traceability context

---

## Enforcement Mechanisms (Current vs. Needed)

### TraceRTM Enforcement
**Current:**
- ✅ Link validation (items must exist)
- ✅ Traceability matrix (coverage %)
- ✅ Gap detection (missing links)

**Needed:**
- ❌ Mandatory linking policies (e.g., "all FEATURE items must link to CODE")
- ❌ Workflow enforcement (e.g., "can't mark FEATURE done without TEST link")
- ❌ Coverage thresholds (e.g., "FEATURE→TEST must be ≥90%")
- ❌ Approval workflows (e.g., "require QA sign-off before deployment")

### BMM Enforcement
**Current:**
- ✅ Quality gate decisions (PASS/CONCERNS/FAIL/WAIVED)
- ✅ P0/P1/P2/P3 priority enforcement
- ✅ Risk-based testing requirements

**Needed:**
- ❌ Integration with TraceRTM for persistent storage
- ❌ Automatic enforcement of gate decisions in deployment
- ❌ Traceability validation before gate decision

### OpenSpec Enforcement
**Current:**
- ✅ Spec versioning (specs/ vs. changes/)
- ✅ Proposal/apply/archive workflow

**Needed:**
- ❌ Traceability linking (specs → implementation → tests)
- ❌ Coverage validation (all specs must have implementation)
- ❌ Integration with BMM for quality gates

---

## Guidance & Prompts (Current vs. Needed)

### TraceRTM Guidance
**Current:**
- ✅ CLI commands (rtm create, rtm link, rtm query)
- ✅ User guide (docs/USER_GUIDE.md)
- ⚠️ **Limited:** No workflow guidance

**Needed (Phase 3 Prompts):**
- ❌ tracertm.plan_iteration – Iteration planning with traceability
- ❌ tracertm.groom_backlog – Backlog prioritization
- ❌ tracertm.analyze_risk – Risk identification
- ❌ tracertm.implement_feature_with_traceability – Feature implementation guide
- ❌ tracertm.trace_existing_work – Retroactive tracing

### BMM Guidance
**Current:**
- ✅ Markdown-based workflow instructions
- ✅ Test priority matrix (test-priorities-matrix.md)
- ✅ Risk governance (risk-governance.md)
- ✅ Gate decision templates (trace-template.md)
- ✅ Agent personas and menus

**Needed:**
- ❌ Integration with TraceRTM prompts
- ❌ Automatic prompt generation from TraceRTM data
- ❌ Feedback loop (gate decisions → TraceRTM updates)

### OpenSpec Guidance
**Current:**
- ✅ CLI templates
- ✅ Spec → Plan → Tasks → Implement phases

**Needed:**
- ❌ Traceability guidance (link specs to implementation)
- ❌ Integration with BMM workflows
- ❌ Integration with TraceRTM for persistent storage

---

## Proposed Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Server (tracertm-mcp)            │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Tools (21)                                       │   │
│  │ - Projects, Items, Links, Traceability, Graph   │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Resources (10) + BMM/OpenSpec Resources (5)      │   │
│  │ - Current project, summary, trace-matrix        │   │
│  │ - BMM gate decisions, OpenSpec specs            │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Prompts (8) + BMM/OpenSpec Prompts (6)          │   │
│  │ - Plan iteration, groom backlog, analyze risk   │   │
│  │ - BMM: quality gate, test design                │   │
│  │ - OpenSpec: spec review, implementation plan    │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│              TraceRTM Core (Database + Services)        │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Items (FEATURE, CODE, TEST, DESIGN, API, DOC)   │   │
│  │ Links (implements, tests, depends_on, etc.)     │   │
│  │ Events (audit trail)                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────┐
│         Integration Layer (NEW)                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │ BMM Integration                                  │   │
│  │ - Import test designs → TraceRTM TEST items     │   │
│  │ - Store gate decisions → TraceRTM metadata      │   │
│  │ - Export traceability matrix ← TraceRTM         │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ OpenSpec Integration                             │   │
│  │ - Import specs → TraceRTM DESIGN items          │   │
│  │ - Link specs to implementation                  │   │
│  │ - Track spec changes in audit trail             │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │ Enforcement Engine (NEW)                         │   │
│  │ - Mandatory linking policies                    │   │
│  │ - Workflow enforcement                          │   │
│  │ - Coverage thresholds                           │   │
│  │ - Approval workflows                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Recommended Next Steps

### Phase 2 Extensions (Resources)
Add BMM/OpenSpec resources:
- tracertm://project/{id}/bmm/gate-decisions
- tracertm://project/{id}/openspec/specs
- tracertm://project/{id}/enforcement/policies

### Phase 3 Extensions (Prompts)
Add BMM/OpenSpec prompts:
- tracertm.bmm_quality_gate – Quality gate decision
- tracertm.openspec_spec_review – Spec review
- tracertm.enforce_traceability – Enforcement validation

### Phase 4 Extensions (Production)
Add integration features:
- BMM ingestion service
- OpenSpec ingestion service
- Enforcement engine
- Bidirectional sync

---

## Summary

**Current State:**
- TraceRTM: Strong traceability, weak enforcement
- BMM: Strong guidance, weak persistence
- OpenSpec: Strong versioning, weak traceability

**Needed:**
- Bidirectional integration (TraceRTM ↔ BMM ↔ OpenSpec)
- Enforcement mechanisms (policies, workflows, thresholds)
- Unified guidance (prompts across all three systems)
- Persistent storage (gate decisions, spec changes in TraceRTM)

