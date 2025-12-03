# 🚀 Quick Reference Guide

## Documentation Structure at a Glance

### 📍 Main Sections

| Section | Pages | Purpose | URL |
|---------|-------|---------|-----|
| **Getting Started** | 6 | Onboarding & basics | `/docs/getting-started/` |
| **Wiki** | 27 | Knowledge base | `/docs/wiki/` |
| **API Reference** | 44 | Technical reference | `/docs/api-reference/` |
| **Development** | 30 | Internal knowledge | `/docs/development/` |
| **Changelog** | 3+ | Version history | `/docs/changelog/` |

## Common URLs

### Getting Started
- `/docs/getting-started/installation/`
- `/docs/getting-started/quick-start/`
- `/docs/getting-started/core-concepts/`

### Wiki
- `/docs/wiki/concepts/traceability/`
- `/docs/wiki/guides/cli-guide/`
- `/docs/wiki/examples/basic-workflow/`
- `/docs/wiki/use-cases/software-development/`

### API Reference
- `/docs/api-reference/authentication/api-keys/`
- `/docs/api-reference/rest-api/projects/`
- `/docs/api-reference/cli/installation/`
- `/docs/api-reference/sdks/python/quickstart/`
- `/docs/api-reference/sdks/javascript/quickstart/`
- `/docs/api-reference/sdks/go/quickstart/`

### Development
- `/docs/development/architecture/system-design/`
- `/docs/development/setup/local-development/`
- `/docs/development/contributing/code-style/`
- `/docs/development/internals/backend-handlers/`
- `/docs/development/deployment/docker/`

## File Structure

```
content/docs/
├── 00-getting-started/
├── 01-wiki/
│   ├── 01-concepts/
│   ├── 02-guides/
│   ├── 03-examples/
│   └── 04-use-cases/
├── 02-api-reference/
│   ├── 01-authentication/
│   ├── 02-rest-api/
│   ├── 03-cli/
│   └── 04-sdks/
├── 03-development/
│   ├── 01-architecture/
│   ├── 02-setup/
│   ├── 03-contributing/
│   ├── 04-internals/
│   └── 05-deployment/
└── 04-changelog/
```

## Key Features

✅ **Hierarchical Navigation** - Collapsible tree structure
✅ **Progressive Disclosure** - Simple → Complex
✅ **Unlimited Nesting** - Scalable architecture
✅ **Static Generation** - Fast performance
✅ **Responsive Design** - Mobile-friendly

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# View structure
find content/docs -type d | head -50
```

## Content Population

Each MDX file has this structure:

```mdx
---
title: Page Title
description: Brief description
---

# Page Title

Your content here...
```

## Navigation Tips

1. **Sidebar**: Click sections to expand/collapse
2. **Breadcrumbs**: Coming soon
3. **Search**: Coming soon
4. **Previous/Next**: Coming soon

## Statistics

- **Total Pages**: 110+
- **Total MDX Files**: 127
- **Nesting Levels**: 3-5
- **Build Time**: ~30 seconds
- **Static Pages**: 129

## Support

For questions about the structure, see:
- `IMPLEMENTATION_COMPLETE.md` - Detailed checklist
- `DOCUMENTATION_TREE_STRUCTURE.md` - Full tree
- `STATUS_REPORT.md` - Current status

---

**Last Updated**: December 3, 2025

