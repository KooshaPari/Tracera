
# Phase 3: Prompts – Planning Document

## Overview

Phase 3 adds **MCP prompts** – canonical conversation templates that guide LLMs through TraceRTM workflows. Prompts combine system instructions, context, and example interactions.

**Status:** Planning (not implemented)

## Prompt Categories

### 1. Planning & Iteration (2 prompts)

#### tracertm.plan_iteration
**Purpose:** Guide iteration planning using TraceRTM data.

**System Prompt:**
```
You are a project planner using TraceRTM data. Your role is to:
1. Analyze the current project state (items, status, coverage)
2. Identify high-priority work (by status, priority, owner)
3. Propose a balanced iteration plan (features, tests, docs)
4. Flag risks (gaps, cycles, blocked items)
5. Suggest next steps

Use the project summary, trace matrix, and gap reports to inform your plan.
```

**Input Context:**
- Project summary (item counts, health)
- Trace matrix (coverage by view)
- Gap report (missing traceability)
- Activity log (recent changes)
- Open items (by status, priority)

**Output:**
```json
{
  "iteration_name": "Sprint 5",
  "duration_days": 10,
  "proposed_items": [
    {
      "item_id": "uuid",
      "title": "string",
      "view": "FEATURE",
      "priority": "high",
      "rationale": "string",
      "dependencies": ["uuid", ...]
    }
  ],
  "risks": [
    {
      "type": "gap|cycle|blocked|coverage",
      "description": "string",
      "affected_items": ["uuid", ...],
      "mitigation": "string"
    }
  ],
  "success_metrics": ["coverage > 90%", "all high-priority items done", ...]
}
```

**Use Case:** LLM helps plan the next iteration based on project state.

#### tracertm.groom_backlog
**Purpose:** Prioritize and tag backlog items.

**System Prompt:**
```
You are a backlog groomer using TraceRTM data. Your role is to:
1. Review open items (status=todo)
2. Assess priority (based on dependencies, coverage gaps, owner feedback)
3. Suggest tags/labels (e.g., "high-risk", "quick-win", "blocked")
4. Identify items ready for implementation
5. Flag items needing clarification

Use impact analysis and traceability gaps to inform prioritization.
```

**Input Context:**
- Open items (status=todo)
- Impact analysis (what depends on each item)
- Traceability gaps (what's missing)
- Item metadata (owner, priority, tags)

**Output:**
```json
{
  "groomed_items": [
    {
      "item_id": "uuid",
      "title": "string",
      "current_priority": "low",
      "suggested_priority": "high",
      "suggested_tags": ["quick-win", "high-impact"],
      "rationale": "string",
      "ready_for_implementation": true,
      "blockers": []
    }
  ],
  "items_needing_clarification": [
    {
      "item_id": "uuid",
      "title": "string",
      "questions": ["What is the acceptance criteria?", ...]
    }
  ]
}
```

**Use Case:** LLM helps prioritize backlog before sprint planning.

### 2. Risk & Quality Analysis (2 prompts)

#### tracertm.analyze_risk
**Purpose:** Identify and mitigate project risks.

**System Prompt:**
```
You are a risk analyst using TraceRTM data. Your role is to:
1. Identify risks (gaps, cycles, low coverage, blocked items)
2. Assess severity (impact × likelihood)
3. Suggest mitigations (trace missing items, break cycles, unblock)
4. Prioritize risks by severity
5. Recommend preventive measures

Use traceability matrix, cycle detection, and impact analysis.
```

**Input Context:**
- Trace matrix (coverage gaps)
- Cycle detection (circular dependencies)
- Impact analysis (high-impact items)
- Blocked items (status=blocked)
- Activity log (recent changes)

**Output:**
```json
{
  "risks": [
    {
      "id": "RISK-001",
      "title": "Low TEST coverage",
      "severity": "high",
      "likelihood": "high",
      "impact": "high",
      "affected_items": ["uuid", ...],
      "root_cause": "string",
      "mitigation_steps": ["Create test items for features X, Y, Z", ...],
      "owner": "string",
      "target_resolution_date": "ISO8601"
    }
  ],
  "preventive_measures": ["Enforce traceability in PR reviews", ...]
}
```

**Use Case:** LLM helps identify and mitigate project risks.

#### tracertm.assess_coverage
**Purpose:** Evaluate traceability coverage and suggest improvements.

**System Prompt:**
```
You are a quality analyst using TraceRTM data. Your role is to:
1. Assess traceability coverage (by view pair)
2. Identify critical gaps (high-priority items without tests/docs)
3. Suggest coverage improvements
4. Recommend coverage targets
5. Highlight over-tracing (unnecessary links)

Use the trace matrix and impact analysis.
```

**Input Context:**
- Trace matrix (all view pairs)
- Gap reports (by view pair)
- Item priorities (high-priority items without coverage)
- Link counts (over-tracing detection)

**Output:**
```json
{
  "coverage_summary": {
    "overall_coverage": "85%",
    "by_view_pair": {
      "FEATURE->CODE": "90%",
      "FEATURE->TEST": "70%",
      "CODE->DOC": "60%"
    }
  },
  "critical_gaps": [
    {
      "view_pair": "FEATURE->TEST",
      "gap_count": 5,
      "affected_priority": "high",
      "items": ["uuid", ...]
    }
  ],
  "improvement_suggestions": [
    {
      "action": "Create test items for features X, Y, Z",
      "expected_coverage_gain": "15%",
      "effort_estimate": "3 days"
    }
  ],
  "coverage_targets": {
    "FEATURE->CODE": "95%",
    "FEATURE->TEST": "90%",
    "CODE->DOC": "80%"
  }
}
```

**Use Case:** LLM helps improve traceability coverage.

### 3. Implementation Workflows (2 prompts)

#### tracertm.implement_feature_with_traceability
**Purpose:** Guide feature implementation with traceability setup.

**System Prompt:**
```
You are a feature implementation guide using TraceRTM. Your role is to:
1. Take a feature item as input
2. Guide creation of design, code, test, and doc items
3. Set up traceability links (FEATURE->DESIGN->CODE->TEST->DOC)
4. Validate coverage before marking done
5. Suggest next steps

Ensure all items are created and linked before marking the feature complete.
```

**Input Context:**
- Feature item (title, description, acceptance criteria)
- Project config (valid views, link types)
- Existing items (to avoid duplication)

**Output:**
```json
{
  "feature_id": "uuid",
  "feature_title": "string",
  "implementation_plan": [
    {
      "step": 1,
      "action": "Create DESIGN item",
      "item_type": "design_doc",
      "title": "Design for Feature X",
      "description": "...",
      "link_to_feature": "implements"
    },
    {
      "step": 2,
      "action": "Create CODE item",
      "item_type": "code_module",
      "title": "Implement Feature X",
      "description": "...",
      "link_from_design": "implements"
    },
    {
      "step": 3,
      "action": "Create TEST item",
      "item_type": "test_suite",
      "title": "Test Feature X",
      "description": "...",
      "link_from_code": "validates"
    },
    {
      "step": 4,
      "action": "Create DOC item",
      "item_type": "documentation",
      "title": "Document Feature X",
      "description": "...",
      "link_from_code": "documents"
    }
  ],
  "validation_checklist": [
    "All items created",
    "All links established",
    "Coverage complete",
    "No cycles detected"
  ]
}
```

**Use Case:** LLM guides feature implementation with full traceability.

#### tracertm.trace_existing_work
**Purpose:** Retroactively trace existing items (e.g., code without tests).

**System Prompt:**
```
You are a traceability specialist. Your role is to:
1. Identify items in one view without links to another (e.g., CODE without TEST)
2. Suggest matching items or creation of new items
3. Set up traceability links
4. Validate coverage improvement

Use impact analysis and gap reports to guide tracing.
```

**Input Context:**
- Source items (e.g., CODE items without TEST links)
- Target view (e.g., TEST)
- Existing items (to match/link)

**Output:**
```json
{
  "source_view": "CODE",
  "target_view": "TEST",
  "items_to_trace": [
    {
      "source_item_id": "uuid",
      "source_title": "string",
      "suggested_target_items": [
        {
          "target_item_id": "uuid",
          "target_title": "string",
          "match_confidence": "high|medium|low",
          "rationale": "string"
        }
      ],
      "create_new_item": {
        "title": "Test for X",
        "description": "...",
        "link_type": "validates"
      }
    }
  ],
  "coverage_improvement": {
    "before": "60%",
    "after": "85%",
    "items_traced": 10
  }
}
```

**Use Case:** LLM helps trace existing work retroactively.

### 4. Reporting & Communication (2 prompts)

#### tracertm.generate_status_report
**Purpose:** Generate a project status report for stakeholders.

**System Prompt:**
```
You are a project communicator. Your role is to:
1. Summarize project state (progress, risks, blockers)
2. Highlight achievements (items completed, coverage improved)
3. Flag concerns (gaps, cycles, blocked items)
4. Recommend actions
5. Format for stakeholder communication

Use project summary, activity log, and risk analysis.
```

**Input Context:**
- Project summary
- Activity log (last N days)
- Risk analysis
- Coverage metrics

**Output:**
```json
{
  "report_date": "ISO8601",
  "project_name": "string",
  "executive_summary": "string",
  "progress": {
    "items_completed": 10,
    "items_in_progress": 5,
    "items_blocked": 2,
    "completion_percentage": "67%"
  },
  "achievements": ["Feature X completed", "Coverage improved to 85%", ...],
  "concerns": ["5 items blocked", "Cycle detected in CODE view", ...],
  "recommendations": ["Unblock item Y", "Trace missing tests", ...],
  "next_steps": ["Sprint planning on Friday", ...]
}
```

**Use Case:** LLM generates stakeholder reports.

#### tracertm.suggest_improvements
**Purpose:** Suggest process and data improvements.

**System Prompt:**
```
You are a process improvement specialist. Your role is to:
1. Analyze project data (coverage, cycles, activity patterns)
2. Identify inefficiencies (over-tracing, missing views, poor naming)
3. Suggest improvements (process changes, data cleanup, new views)
4. Estimate impact
5. Prioritize recommendations

Use all available project data.
```

**Input Context:**
- Project summary
- Trace matrix
- Cycle detection
- Activity log
- Item metadata

**Output:**
```json
{
  "improvements": [
    {
      "id": "IMP-001",
      "title": "Add API view",
      "description": "Create API view to trace API contracts",
      "impact": "Improve coverage by 20%",
      "effort": "2 days",
      "priority": "high"
    }
  ],
  "data_cleanup": [
    {
      "issue": "Duplicate items in CODE view",
      "count": 5,
      "recommendation": "Merge or delete duplicates"
    }
  ],
  "process_improvements": [
    {
      "issue": "No traceability review in PR process",
      "recommendation": "Add traceability check to PR template"
    }
  ]
}
```

**Use Case:** LLM suggests process improvements.

## User Stories

### US-3.1: Plan Iteration Using TraceRTM Data
**As a** project manager
**I want to** use an LLM to plan the next iteration based on TraceRTM data
**So that** I can make data-driven decisions about what to work on.

**Acceptance Criteria:**
- tracertm.plan_iteration prompt available
- LLM can access project summary, trace matrix, gaps, activity log
- Output includes proposed items, risks, success metrics

### US-3.2: Groom Backlog with LLM Assistance
**As a** product owner
**I want to** use an LLM to prioritize and tag backlog items
**So that** the team can focus on high-impact work.

**Acceptance Criteria:**
- tracertm.groom_backlog prompt available
- LLM can access open items and impact analysis
- Output includes priority suggestions, tags, blockers

### US-3.3: Identify and Mitigate Risks
**As a** project lead
**I want to** use an LLM to identify project risks
**So that** I can proactively address issues.

**Acceptance Criteria:**
- tracertm.analyze_risk and tracertm.assess_coverage prompts available
- LLM can access trace matrix, cycles, impact analysis
- Output includes risk severity, mitigations, preventive measures

### US-3.4: Implement Features with Full Traceability
**As a** developer
**I want to** use an LLM to guide feature implementation with traceability
**So that** I create complete, traceable work.

**Acceptance Criteria:**
- tracertm.implement_feature_with_traceability prompt available
- LLM guides creation of design, code, test, doc items
- LLM sets up traceability links
- Output includes validation checklist

### US-3.5: Trace Existing Work Retroactively
**As a** tech lead
**I want to** use an LLM to trace existing code/tests retroactively
**So that** we improve coverage without re-implementing.

**Acceptance Criteria:**
- tracertm.trace_existing_work prompt available
- LLM suggests matching items or new items to create
- Output includes coverage improvement estimate

### US-3.6: Generate Status Reports
**As a** project manager
**I want to** use an LLM to generate status reports
**So that** I can communicate project state to stakeholders.

**Acceptance Criteria:**
- tracertm.generate_status_report prompt available
- LLM can access project summary, activity log, risks
- Output is formatted for stakeholder communication

### US-3.7: Suggest Process Improvements
**As a** process owner
**I want to** use an LLM to suggest improvements
**So that** we continuously improve our process.

**Acceptance Criteria:**
- tracertm.suggest_improvements prompt available
- LLM analyzes project data and suggests improvements
- Output includes impact, effort, priority

## Feature Requirements

| Feature | Priority | Effort | Notes |
|---------|----------|--------|-------|
| Plan iteration | High | 2 days | Combine summary + matrix + gaps |
| Groom backlog | High | 2 days | Combine open items + impact |
| Analyze risk | High | 2 days | Combine matrix + cycles + impact |
| Assess coverage | Medium | 1 day | Analyze trace matrix |
| Implement feature | High | 2 days | Guide multi-step workflow |
| Trace existing work | Medium | 2 days | Match items + create links |
| Generate status report | Medium | 1 day | Format project data |
| Suggest improvements | Low | 2 days | Analyze all project data |
| **Total** | | **14 days** | |

## Success Criteria

- [ ] All 8 prompts implemented and tested
- [ ] Each prompt has clear system instructions and context
- [ ] LLM can access resources and tools within prompts
- [ ] Output is structured JSON with clear schemas
- [ ] Prompts guide realistic TraceRTM workflows

