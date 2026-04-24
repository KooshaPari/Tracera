# Trace Documentation Methodology Guide

## Purpose

This directory (`.trace/`) contains structured trace documentation for TracerTM. Trace documentation captures the "why", "how", and "what" of implementation decisions, providing a persistent record of project evolution.

## Trace Document Types

| Prefix | Type | Purpose |
|--------|------|---------|
| `FEATURE-` | Feature Specification | Requirements and acceptance criteria |
| `TASK-` | Task Breakdown | Implementation steps and sub-tasks |
| `TEST_SUITE-` | Test Documentation | Test coverage and scenarios |
| `FILE-` | File Change Record | Individual file modifications |
| `PHASE_` | Phase Completion | Milestone documentation |
| `ADR_` | Architecture Decision | Technical decisions and rationale |
| `SUMMARY` | Summary Report | Consolidated status reports |
| `README_` | Index/Guide | Navigation documents |

## Naming Conventions

### Trace Documents
- Use uppercase with underscores: `FEATURE-2827.md`, `PHASE_2_DELIVERY_MANIFEST.md`
- Include version/status in filename when relevant
- Index files use `INDEX` suffix: `BUILD_COMPLETION_INDEX.md`

### Feature Documents
- `FEATURE-{id}.md` where id is the feature identifier from project tracking
- Example: `FEATURE-2827.md`

### Phase Documents
- `PHASE_{version}_{name}.md`
- Example: `PHASE_2_IMPLEMENTATION_SUMMARY.md`

## Document Structure

### Feature Specification (FEATURE-*)
```markdown
# Feature {id}: {Title}

## Overview
Brief description of the feature.

## Requirements
- List of functional requirements

## Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2

## Implementation Notes
Technical details and decisions.
```

### Phase Completion (PHASE_*)
```markdown
# Phase {N} Completion Report

## Deliverables
List of completed items.

## Status
- Component A: ✅ Complete
- Component B: ✅ Complete

## Next Steps
Upcoming phase items.
```

## Directory Organization

```
.trace/
├── README.md                    # This file
├── .meta/                       # Metadata
│   ├── designs.yaml            # Design references
│   └── links.yaml              # Cross-reference links
├── features/                   # (optional) Feature specs
├── tasks/                      # Task breakdowns
├── test_suites/                # Test documentation
└── *.md                        # Root-level trace documents
```

## Creating Trace Documents

1. **When to create trace docs:**
   - Starting a new feature or phase
   - Completing a milestone
   - Recording an architectural decision
   - Documenting test coverage
   - Summarizing implementation work

2. **What to include:**
   - Clear title and purpose
   - Relevant context and rationale
   - Status and completion state
   - Links to related documents
   - Timestamps (creation, updates)

3. **What NOT to include:**
   - Temporary debugging notes
   - TODO items that aren't yet decisions
   - Sensitive information
   - Duplicate content from other trace docs

## Integration with Development Workflow

Trace documents are created as part of:

1. **Feature development** → `FEATURE-{id}.md` documents requirements
2. **Task execution** → `TASK-{id}.md` breaks down work
3. **Testing** → `TEST_SUITE-{id}.md` captures coverage
4. **Code changes** → `FILE-{id}.md` records modifications
5. **Milestones** → `PHASE_*_SUMMARY.md` marks completion
6. **Decisions** → `ADR_*.md` captures rationale

## Linking and Cross-Reference

Link related documents using relative paths:
```markdown
See [Phase 2 Manifest](./PHASE_2_DELIVERY_MANIFEST.md) for details.
```

Use `.meta/links.yaml` to maintain cross-cutting references.

## Status Indicators

Use these indicators consistently:
- ✅ Complete / Done
- 🚧 In Progress
- ⏳ Pending / Blocked
- ❌ Failed / Rejected
- 📋 Planned
- 🔍 Under Review

## Maintenance

- Update status indicators when state changes
- Add completion timestamps when finishing items
- Archive outdated documents to `ARCHIVE/` subdirectory
- Keep index documents current with actual deliverables

## Style Guide

- Use Markdown formatting consistently
- Keep headings hierarchical (H1 → H2 → H3)
- Use tables for structured data
- Use bullet lists for multiple items
- Include code blocks with language tags
- Add horizontal rules (`---`) to separate major sections

---

**Last Updated**: 2026-04-07
**Version**: 1.0.0
