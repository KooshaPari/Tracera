# Governance

Architecture decisions, policies, and organizational standards.

## Purpose
Document decisions, standards, and RFCs for organizational alignment.

## Structure
```
governance/
├── adr/                    # Architecture Decision Records
│   ├── ADR-000-template.md
│   ├── index.md
│   └── records/
├── rfc/                    # Requests for Comments
│   └── rfc-000-template.md
└── standards/              # Coding standards
    ├── rust.md
    ├── python.md
    ├── typescript.md
    └── go.md
```

## ADR Lifecycle
```
┌─────────┐    ┌─────────┐    ┌───────────┐    ┌──────────┐
│ PROPOSE │ -> │ DISCUSS │ -> │ ACCEPTED  │ -> │ SUPERSED │
└─────────┘    └─────────┘    └───────────┘    └──────────┘
                                    │
                                    v
                              ┌───────────┐
                              │ REJECTED  │
                              └───────────┘
```

## ADR Format
```markdown
# ADR-XXX: Title

## Status
Accepted | Deprecated | Superseded

## Context
What is the issue?

## Decision
What is the change?

## Consequences
What becomes easier/difficult?
```

## Standards
Each language standard covers:
- Formatting conventions
- Naming conventions
- Testing requirements
- Documentation expectations
- CI/CD integration

## Related
- [policies/](../policies/) - Enforcement policies
- [scripts/utility/](../scripts/utility/) - Governance validation scripts
