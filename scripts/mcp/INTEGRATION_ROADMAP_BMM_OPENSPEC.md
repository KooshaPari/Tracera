# Integration Roadmap: TraceRTM ↔ BMM ↔ OpenSpec

## Phase 2 Extensions: Resources + BMM/OpenSpec Integration

### New Resources (5 additional)

#### tracertm://project/{id}/bmm/gate-decisions
**Purpose:** Access BMM quality gate decisions from TraceRTM

**Output Schema:**
```json
{
  "project_id": "uuid",
  "gate_decisions": [
    {
      "decision_id": "uuid",
      "story_id": "string",
      "decision": "PASS|CONCERNS|FAIL|WAIVED",
      "coverage_percentage": "float",
      "p0_coverage": "float",
      "p1_coverage": "float",
      "critical_gaps": ["item_id", ...],
      "created_at": "ISO8601",
      "created_by": "string"
    }
  ]
}
```

**Use Case:** LLM sees quality gate decisions alongside traceability data.

#### tracertm://project/{id}/openspec/specs
**Purpose:** Access OpenSpec specs from TraceRTM

**Output Schema:**
```json
{
  "project_id": "uuid",
  "specs": [
    {
      "spec_id": "string",
      "title": "string",
      "description": "string",
      "status": "active|archived",
      "linked_items": ["item_id", ...],
      "coverage": "float",
      "last_updated": "ISO8601"
    }
  ]
}
```

**Use Case:** LLM sees specs and their traceability to implementation.

#### tracertm://project/{id}/enforcement/policies
**Purpose:** View enforcement policies and violations

**Output Schema:**
```json
{
  "project_id": "uuid",
  "policies": [
    {
      "policy_id": "string",
      "name": "string",
      "rule": "FEATURE→CODE coverage ≥90%",
      "severity": "warning|error",
      "violations": [
        {
          "item_id": "uuid",
          "item_title": "string",
          "violation": "Coverage 60% < 90%"
        }
      ]
    }
  ]
}
```

**Use Case:** LLM identifies policy violations and suggests fixes.

#### tracertm://project/{id}/bmm/test-designs
**Purpose:** Access BMM test designs linked to TraceRTM items

**Output Schema:**
```json
{
  "project_id": "uuid",
  "test_designs": [
    {
      "design_id": "uuid",
      "feature_id": "uuid",
      "feature_title": "string",
      "test_cases": [
        {
          "test_id": "string",
          "priority": "P0|P1|P2|P3",
          "type": "unit|integration|e2e",
          "status": "designed|implemented|passed|failed"
        }
      ]
    }
  ]
}
```

**Use Case:** LLM sees test designs and their implementation status.

#### tracertm://project/{id}/openspec/changes
**Purpose:** Access OpenSpec change proposals

**Output Schema:**
```json
{
  "project_id": "uuid",
  "changes": [
    {
      "change_id": "string",
      "spec_id": "string",
      "title": "string",
      "description": "string",
      "status": "proposed|applied|archived",
      "linked_items": ["item_id", ...],
      "created_at": "ISO8601"
    }
  ]
}
```

**Use Case:** LLM sees spec changes and their impact on implementation.

---

## Phase 3 Extensions: Prompts + BMM/OpenSpec Workflows

### New Prompts (6 additional)

#### tracertm.bmm_quality_gate
**Purpose:** Guide quality gate decision using TraceRTM data

**System Prompt:**
```
You are a quality gate decision maker using TraceRTM and BMM data.
Your role is to:
1. Analyze traceability coverage (FEATURE→CODE→TEST)
2. Review test priorities (P0/P1/P2/P3)
3. Assess risk (using BMM risk framework)
4. Make gate decision (PASS/CONCERNS/FAIL/WAIVED)
5. Recommend actions

Use traceability matrix, gap reports, and test designs.
```

**Input Context:**
- Traceability matrix (coverage %)
- Gap report (missing links)
- Test designs (P0/P1/P2/P3)
- Risk assessment (6 categories)

**Output:**
```json
{
  "decision": "PASS|CONCERNS|FAIL|WAIVED",
  "coverage": {"FEATURE→CODE": "95%", "FEATURE→TEST": "85%"},
  "p0_status": "✅ ALL PASS|❌ FAILED",
  "critical_gaps": ["item_id", ...],
  "risk_assessment": {"TECH": "low", "SEC": "medium", ...},
  "recommendations": ["Add test for X", "Fix cycle in Y", ...],
  "waiver_justification": "string (if WAIVED)"
}
```

**Use Case:** LLM makes quality gate decisions with full traceability context.

#### tracertm.openspec_spec_review
**Purpose:** Review OpenSpec specs for completeness and traceability

**System Prompt:**
```
You are a spec reviewer using TraceRTM and OpenSpec data.
Your role is to:
1. Review spec completeness (all required sections)
2. Check traceability (spec → implementation → tests)
3. Identify gaps (missing implementation or tests)
4. Suggest improvements
5. Recommend approval or revision

Use spec content, linked items, and coverage data.
```

**Input Context:**
- Spec content (title, description, requirements)
- Linked items (implementation, tests)
- Coverage (% of spec covered by implementation)

**Output:**
```json
{
  "spec_id": "string",
  "completeness": "90%",
  "traceability": "85%",
  "recommendation": "APPROVE|REVISE|REJECT",
  "gaps": ["Missing error handling spec", ...],
  "improvements": ["Add performance requirements", ...],
  "implementation_status": {"designed": 5, "implemented": 3, "tested": 2}
}
```

**Use Case:** LLM reviews specs for completeness and traceability.

#### tracertm.enforce_traceability
**Purpose:** Validate traceability policies and suggest fixes

**System Prompt:**
```
You are a traceability enforcer using TraceRTM policies.
Your role is to:
1. Check traceability policies (mandatory linking rules)
2. Identify violations (items not meeting policies)
3. Assess impact (what breaks if not fixed)
4. Suggest fixes (create missing links or items)
5. Prioritize by severity

Use policies, items, links, and impact analysis.
```

**Input Context:**
- Policies (mandatory linking rules)
- Items (current state)
- Links (current traceability)
- Impact analysis (downstream effects)

**Output:**
```json
{
  "violations": [
    {
      "policy": "FEATURE→CODE coverage ≥90%",
      "violation_count": 5,
      "affected_items": ["item_id", ...],
      "severity": "error",
      "fix": "Create CODE items for features X, Y, Z"
    }
  ],
  "impact": {"deployment_blocked": true, "reason": "P0 gaps"},
  "recommended_actions": ["Create 5 CODE items", "Link to FEATURE", ...]
}
```

**Use Case:** LLM enforces traceability policies and suggests fixes.

#### tracertm.bmm_test_design
**Purpose:** Design tests using BMM framework and TraceRTM data

**System Prompt:**
```
You are a test designer using BMM and TraceRTM data.
Your role is to:
1. Analyze feature requirements (from TraceRTM)
2. Identify test priorities (P0/P1/P2/P3 using BMM)
3. Design test cases (unit, integration, e2e)
4. Link tests to features (create TEST items)
5. Validate coverage

Use feature items, acceptance criteria, and BMM risk framework.
```

**Input Context:**
- Feature item (title, description, AC)
- Risk assessment (BMM 6 categories)
- Existing tests (if any)

**Output:**
```json
{
  "feature_id": "uuid",
  "test_design": [
    {
      "test_id": "string",
      "title": "string",
      "type": "unit|integration|e2e",
      "priority": "P0|P1|P2|P3",
      "acceptance_criteria": ["AC1", "AC2", ...],
      "risk_coverage": ["TECH", "SEC", ...]
    }
  ],
  "coverage": "95%",
  "gaps": ["Missing error path test", ...]
}
```

**Use Case:** LLM designs tests with BMM priorities and TraceRTM traceability.

#### tracertm.openspec_implementation_plan
**Purpose:** Create implementation plan from OpenSpec specs

**System Prompt:**
```
You are an implementation planner using OpenSpec and TraceRTM.
Your role is to:
1. Parse OpenSpec specs
2. Create implementation items (CODE, API, DATABASE)
3. Link to specs (DESIGN→CODE)
4. Plan test items (TEST)
5. Validate traceability

Use spec content and TraceRTM multi-view model.
```

**Input Context:**
- Spec content (requirements, design)
- Existing items (avoid duplication)

**Output:**
```json
{
  "spec_id": "string",
  "implementation_plan": [
    {
      "step": 1,
      "action": "Create CODE item",
      "item_type": "code_module",
      "title": "string",
      "link_to_spec": "implements"
    }
  ],
  "traceability": "SPEC→CODE→TEST→DOC",
  "estimated_effort": "5 days"
}
```

**Use Case:** LLM creates implementation plans from specs.

#### tracertm.bmm_risk_assessment
**Purpose:** Assess risk using BMM framework and TraceRTM data

**System Prompt:**
```
You are a risk assessor using BMM and TraceRTM data.
Your role is to:
1. Analyze items and links (from TraceRTM)
2. Assess risk (using BMM 6 categories)
3. Identify high-risk areas (gaps, cycles, low coverage)
4. Recommend mitigations
5. Prioritize by severity

Use traceability matrix, gap reports, and cycle detection.
```

**Input Context:**
- Traceability matrix (coverage %)
- Gap report (missing links)
- Cycle detection (circular dependencies)
- Item priorities

**Output:**
```json
{
  "risks": [
    {
      "category": "TECH|SEC|PERF|DATA|BUS|OPS",
      "risk": "Low TEST coverage",
      "severity": "high",
      "affected_items": ["item_id", ...],
      "mitigation": "Add tests for X, Y, Z"
    }
  ],
  "overall_risk": "medium",
  "recommendations": ["Increase TEST coverage to 90%", ...]
}
```

**Use Case:** LLM assesses risk using BMM framework.

---

## Phase 4 Extensions: Production Features + Integration

### New Features (5 additional)

#### 1. BMM Integration Service
**Purpose:** Bidirectional sync with BMM workflows

**Features:**
- Import test designs → TraceRTM TEST items
- Store gate decisions → TraceRTM metadata
- Export traceability matrix ← TraceRTM
- Sync test results ← BMM CI/CD

**Effort:** 5 days

#### 2. OpenSpec Integration Service
**Purpose:** Bidirectional sync with OpenSpec

**Features:**
- Import specs → TraceRTM DESIGN items
- Link specs to implementation
- Track spec changes in audit trail
- Export implementation status ← TraceRTM

**Effort:** 5 days

#### 3. Enforcement Engine
**Purpose:** Enforce traceability policies

**Features:**
- Define mandatory linking policies
- Validate policies on item creation/update
- Block operations that violate policies
- Generate violation reports

**Effort:** 3 days

#### 4. Workflow Enforcement
**Purpose:** Enforce workflow rules

**Features:**
- Define workflow states (e.g., "can't mark FEATURE done without TEST link")
- Validate state transitions
- Block invalid transitions
- Generate workflow violation reports

**Effort:** 3 days

#### 5. Approval Workflows
**Purpose:** Require approvals for critical operations

**Features:**
- Define approval rules (e.g., "require QA sign-off before deployment")
- Route approvals to designated users
- Track approval history
- Block operations without approvals

**Effort:** 4 days

---

## Implementation Timeline

| Phase | Features | Duration | Dependencies |
|-------|----------|----------|--------------|
| 2 | 5 resources (BMM/OpenSpec) | 5 days | Phase 1 complete |
| 3 | 6 prompts (BMM/OpenSpec) | 7 days | Phase 2 complete |
| 4 | 5 features (integration) | 20 days | Phase 3 complete |
| **Total** | **16 features** | **32 days** | |

---

## Success Criteria

- [ ] BMM gate decisions stored in TraceRTM
- [ ] OpenSpec specs linked to implementation
- [ ] Traceability policies enforced
- [ ] Workflow rules enforced
- [ ] Approval workflows working
- [ ] Bidirectional sync with BMM/OpenSpec
- [ ] All integration prompts working
- [ ] Integration tests passing

