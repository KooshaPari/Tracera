# Documentation

Human-readable documentation for projects and APIs.

## Purpose
Provide clear, accessible documentation for users and developers.

## Structure
```
docs/
├── api/                # API documentation
│   └── openapi/        # OpenAPI specs
├── runbooks/           # Operational runbooks
│   ├── incident-response.md
│   └── deployment.md
└── guides/             # User guides
    ├── getting-started.md
    └── troubleshooting.md
```

## Documentation Types
| Type | Audience | Format |
|------|----------|--------|
| README | All users | Markdown |
| API Docs | Developers | OpenAPI/Swagger |
| Runbooks | Operators | Markdown + procedures |
| Guides | End users | Markdown |
| ADRs | Architects | Markdown |

## Frontmatter Standard
```markdown
---
title: Document Title
description: Brief description
category: getting-started|guides|api|runbooks
---

# Document Title
```

## Agent Pattern
| Action | Pattern |
|--------|---------|
| Read | Fetch documentation for context |
| Write | Update docs with feature changes |
| Enforce | Require docs for new features |

## Related
- [governance/](../governance/) - ADR documentation
- [schemas/api/](../schemas/api/) - API specs for docs generation
