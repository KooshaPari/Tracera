# AgilePlus Methodology Specification for TracerTM

**Project**: TracerTM  
**Status**: Active  
**Last Updated**: 2026-03-31

---

## 1. Overview

AgilePlus is the specification-driven development methodology implemented in the TracerTM ecosystem. It provides a structured yet lightweight framework for capturing, tracking, and evolving feature specifications through a file-based spec management system. AgilePlus bridges traditional specification rigor with agile delivery practices, enabling both human and AI agents to maintain consistent, traceable development workflows.

In TracerTM, AgilePlus serves as the primary mechanism for translating high-level requirements (from PRD, ADRs, and user feedback) into concrete, implementable feature specifications with clear ownership, status tracking, and task decomposition.

---

## 2. Core Principles

### 2.1 Specification-First Development

Every feature, enhancement, or significant change begins with a specification. This ensures:

- **Clarity**: Requirements are explicitly stated before implementation begins
- **Traceability**: Each spec can be traced back to source requirements and forward to implementation
- **Accountability**: Specs have clear ownership and status
- **Reviewability**: Specifications provide focused discussion points for review

### 2.2 Lightweight Structure

AgilePlus avoids heavy documentation overhead. Specs are:

- **Atomic**: One spec per feature/enhancement
- **Self-contained**: Each spec includes all necessary context
- **Actionable**: Clear tasks enable immediate implementation
- **Versioned**: Spec changes are tracked through file history

### 2.3 Human + AI Collaborative

AgilePlus is designed for mixed human-AI development environments:

- Humans provide strategic direction and review
- AI agents consume specs for implementation
- Both can update spec status and progress

---

## 3. Directory Structure

AgilePlus specs reside in the `.agileplus/specs/` directory within the TracerTM repository:

```
.agileplus/
└── specs/
    └── <feature-id>/
        ├── spec.md      # Feature description and requirements
        ├── meta.json    # Metadata (id, title, status, timestamps)
        └── tasks.md     # Work package breakdown
```

### Example Structure

```
.agileplus/
└── specs/
    └── FR-AUTH-001/
        ├── spec.md      # "Implement OAuth2 SSO via WorkOS"
        ├── meta.json    # {"id": "FR-AUTH-001", "title": "...", "status": "in_progress"}
        └── tasks.md     # # Implementation Tasks\n- [ ] Task 1...
```

---

## 4. Spec Components

### 4.1 spec.md (Feature Specification)

The primary specification document containing:

```markdown
# <Feature Title>

## Summary
Brief description of the feature.

## Motivation
Why this feature is needed (links to PRD/ADR if applicable).

## Requirements
- Requirement 1
- Requirement 2

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Out of Scope
Items explicitly excluded from this spec.

## Dependencies
- Other specs or systems this depends on

## Risks
Known risks and mitigation strategies.
```

### 4.2 meta.json (Metadata)

JSON metadata for tooling and tracking:

```json
{
  "id": "FR-AUTH-001",
  "title": "Implement OAuth2 SSO via WorkOS",
  "status": "in_progress",
  "created_at": "2026-03-15T10:00:00Z",
  "updated_at": "2026-03-20T14:30:00Z",
  "owner": "auth-team",
  "priority": "high",
  "phase": 1,
  "tags": ["authentication", "security", "sso"]
}
```

**Status Values**:

| Status | Description |
|--------|-------------|
| `draft` | Initial specification, not yet approved |
| `review` | Under review by stakeholders |
| `approved` | Approved for implementation |
| `in_progress` | Actively being implemented |
| `testing` | Implementation complete, under verification |
| `shipped` | Deployed to production |
| `deprecated` | Superseded by another spec |

### 4.3 tasks.md (Work Package Breakdown)

Task-level work packages for implementation:

```markdown
# Work Package: FR-AUTH-001

## Implementation Tasks

### Phase 1: Foundation
- [ ] Configure WorkOS dashboard credentials
- [ ] Implement auth service scaffold
- [ ] Add OAuth2 callback handler

### Phase 2: Integration
- [ ] Connect to Python backend auth service
- [ ] Implement session management
- [ ] Add WebSocket auth events

### Phase 3: Testing & Verification
- [ ] Write unit tests for auth service
- [ ] Integration test with WorkOS
- [ ] Security review

## Time Estimate
~3 agent-days (parallel implementation)

## Verification
All acceptance criteria in spec.md must pass.
```

---

## 5. AgilePlus CLI Commands

AgilePlus provides CLI commands for spec management:

### 5.1 specify

Create a new specification:

```bash
cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus
agileplus specify <feature-id> [--title "Title"] [--template default|experimental]
```

This initializes:
1. The spec directory structure
2. The `meta.json` with generated ID and timestamps
3. The `spec.md` from template
4. The `tasks.md` from template

### 5.2 status

Update or query spec status:

```bash
agileplus status <feature-id> [--status in_progress] [--owner team-name]
agileplus status list [--filter status=draft]
```

### 5.3 Additional Commands

| Command | Description |
|---------|-------------|
| `agileplus list` | List all specs with status |
| `agileplus diff` | Show changes since last status |
| `agileplus export` | Export specs to JSON/CSV |
| `agileplus link` | Link spec to PRD/ADR requirement |

---

## 6. AgilePlus in TracerTM Workflow

### 6.1 Spec Lifecycle

```
draft → review → approved → in_progress → testing → shipped
                ↓
            deprecated
```

### 6.2 Integration with Development Workflow

1. **Requirement Arrives** (PRD update, ADR decision, user feedback)
2. **Spec Creation**: `agileplus specify FR-<CATEGORY>-<NNN>`
3. **Review**: Stakeholders review `spec.md`, status → `review`
4. **Approval**: Status → `approved`, implementation begins
5. **Implementation**: Status → `in_progress`, tasks completed in `tasks.md`
6. **Verification**: Status → `testing`, acceptance criteria validated
7. **Shipment**: Status → `shipped`, feature deployed
8. **Maintenance**: Deprecation when superseded

### 6.3 TracerTM-Specific Usage

TracerTM uses AgilePlus for:

| Use Case | Spec Pattern |
|----------|--------------|
| New Feature | `FR-<CATEGORY>-<NNN>` |
| Technical Change | `TC-<AREA>-<NNN>` |
| Bug Fix | `BF-<COMPONENT>-<NNN>` |
| Research Spike | `SP-<TOPIC>-<NNN>` |

### 6.4 Multi-Agent Coordination

AgilePlus specs enable parallel agent work:

1. **Plan Agent**: Creates spec from PRD requirements
2. **Implement Agents**: Consume spec, update tasks, report status
3. **Review Agent**: Validates implementation against acceptance criteria
4. **Coordination Agent**: Monitors spec status, escalates blockers

---

## 7. Integration Points

### 7.1 PRD Integration

AgilePlus specs reference PRD requirements:

```markdown
## Motivation

Implements FR-AUTH-001 from [PRD.md](./PRD.md#feature-1-authentication)
```

### 7.2 ADR Integration

Architecture decisions link to specs:

```markdown
## Decisions

- ADR-0013: AI Agent Coordination - [Spec FR-AI-001](./specs/FR-AI-001/)
```

### 7.3 Traceability Matrix Integration

TracerTM's core RTM functionality tracks:

- **Spec → Code**: Which files implement each spec
- **Spec → Tests**: Test coverage per spec
- **Spec → Deployment**: Shipment status per spec

### 7.4 CI/CD Integration

Automated workflows respond to spec status:

| Trigger | Action |
|---------|--------|
| `spec.md` updated | Notify review channel |
| Status → `testing` | Run test suite |
| Status → `shipped` | Deploy to staging |
| All specs shipped | Trigger release |

---

## 8. Best Practices

### 8.1 Spec Writing

- **Be Specific**: Avoid vague requirements; use concrete acceptance criteria
- **Keep Atomic**: One spec, one feature. Split large features into multiple specs
- **Link Everything**: Reference PRD items, ADRs, and related specs
- **Update Proactively**: Reflect implementation changes in spec status

### 8.2 Task Management

- **Break Down Fully**: Tasks should be implementable without further clarification
- **Estimate Honestly**: Use past velocity to improve future estimates
- **Mark Progress**: Check off tasks as completed, update spec status

### 8.3 Review Process

- **Review spec.md before spec.md**: Approve specification before implementation
- **Involve Stakeholders**: Include relevant domain experts in review
- **Document Decisions**: Record rationale for controversial decisions

---

## 9. Tooling Support

### 9.1 Claude Integration

From `claude.md`:

```markdown
## Spec Management

Use AgilePlus: `agileplus specify` and `agileplus status`

Specs are stored in `.agileplus/specs/<feature-id>/`:
- `.agileplus/specs/<feature-id>/spec.md` - feature description
- `.agileplus/specs/<feature-id>/meta.json` - id, title, status
- `.agileplus/specs/<feature-id>/tasks.md` - work packages

Reference: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
CLI: `cd /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus && agileplus <command>`
```

### 9.2 MCP Tools

TracerTM's MCP server provides tools for spec interaction:

- `get_spec_by_id()`: Retrieve spec details
- `update_spec_status()`: Update spec status
- `list_specs_by_status()`: Query specs by status
- `get_spec_tasks()`: Retrieve work packages

---

## 10. Governance

### 10.1 Spec Approval

| Spec Priority | Approval Required |
|---------------|-------------------|
| Critical | 2+ stakeholder sign-offs |
| High | 1 stakeholder sign-off |
| Medium | Self-approved by owner |
| Low | No approval required |

### 10.2 Status Transitions

| Transition | Pre-condition | Post-action |
|------------|---------------|-------------|
| draft → review | spec.md complete | Notify reviewers |
| review → approved | All comments resolved | Lock spec.md |
| approved → in_progress | tasks.md broken down | Assign owner |
| in_progress → testing | All tasks complete | Run verification |
| testing → shipped | All criteria pass | Trigger deploy |
| any → deprecated | Deprecation reason logged | Link to replacement |

---

## 11. Migration Notes

For TracerTM's existing spec-like documents, convert to AgilePlus format:

1. Identify feature specs in `docs/plans/`
2. Create `.agileplus/specs/<feature-id>/` structure
3. Extract requirements to `spec.md`
4. Create `meta.json` with appropriate status
5. Decompose into `tasks.md` work packages
6. Update docs to reference new spec location

---

## 12. Reference

- **AgilePlus CLI**: `/Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus`
- **TracerTM PRD**: [`PRD.md`](./PRD.md)
- **TracerTM Plan**: [`docs/plans/PLAN.md`](./PLAN.md)
- **BMM Methodology**: See `.archive/.bmad/bmm/` for scale-adaptive planning

---

**End of Specification**
