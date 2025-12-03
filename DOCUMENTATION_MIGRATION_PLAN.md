# TraceRTM: Complete Documentation Migration Plan
## MDX/Fumadocs + OpenAPI/Swagger/ReDoc

**Status:** Planning Phase  
**Target:** Comprehensive, user-facing + internal developer documentation  
**Timeline:** 4-6 weeks  
**Scope:** Backend API, Frontend Components, CLI, Desktop, Infrastructure

---

## 📋 Executive Summary

Migrate from scattered markdown files to a unified documentation system using:
- **Fumadocs** - Modern MDX-based documentation framework
- **OpenAPI 3.1** - API specification standard
- **Swagger UI** - Interactive API explorer
- **ReDoc** - Beautiful API documentation
- **TypeDoc** - TypeScript/JavaScript API docs
- **GoDoc** - Go package documentation

**Deliverables:**
1. Unified documentation site (Fumadocs)
2. Interactive API explorer (Swagger UI)
3. Beautiful API reference (ReDoc)
4. Code-generated documentation (TypeDoc, GoDoc)
5. Component library documentation (Storybook integration)
6. Internal developer guides
7. User guides and tutorials

---

## 🏗️ Architecture Overview

```
docs/
├── fumadocs/                    # Main documentation site
│   ├── app/                     # Next.js app
│   ├── content/                 # MDX content
│   │   ├── docs/               # User documentation
│   │   ├── guides/             # How-to guides
│   │   ├── api/                # API reference (generated)
│   │   ├── components/         # Component docs
│   │   └── architecture/       # Architecture docs
│   ├── public/                 # Static assets
│   └── package.json
│
├── openapi/                     # OpenAPI specifications
│   ├── backend.openapi.yaml    # Backend API spec
│   ├── schemas/                # Reusable schemas
│   └── paths/                  # Endpoint definitions
│
├── swagger-ui/                  # Swagger UI deployment
│   ├── index.html
│   └── swagger-config.js
│
├── redoc/                       # ReDoc deployment
│   ├── index.html
│   └── redoc-config.js
│
└── scripts/                     # Generation scripts
    ├── generate-openapi.ts     # Generate from Go code
    ├── generate-typedoc.ts     # Generate TypeScript docs
    └── generate-godoc.ts       # Generate Go docs
```

---

## 📚 Documentation Structure

### 1. **User-Facing Documentation** (Fumadocs)

```
docs/fumadocs/content/docs/
├── 00-getting-started/
│   ├── index.mdx               # Welcome
│   ├── installation.mdx        # Setup guide
│   ├── quick-start.mdx         # 5-minute tutorial
│   └── faq.mdx                 # Common questions
│
├── 01-user-guide/
│   ├── projects.mdx            # Managing projects
│   ├── items.mdx               # Working with items
│   ├── links.mdx               # Creating relationships
│   ├── search.mdx              # Search features
│   ├── graph.mdx               # Graph visualization
│   └── agents.mdx              # AI agents
│
├── 02-api-reference/
│   ├── index.mdx               # API overview
│   ├── authentication.mdx      # Auth guide
│   ├── projects.mdx            # Projects endpoints
│   ├── items.mdx               # Items endpoints
│   ├── links.mdx               # Links endpoints
│   ├── agents.mdx              # Agents endpoints
│   ├── search.mdx              # Search endpoints
│   └── errors.mdx              # Error handling
│
├── 03-guides/
│   ├── best-practices.mdx      # Best practices
│   ├── performance.mdx         # Performance tips
│   ├── security.mdx            # Security guide
│   ├── integrations.mdx        # Third-party integrations
│   └── troubleshooting.mdx     # Troubleshooting
│
├── 04-components/
│   ├── index.mdx               # Component library
│   ├── buttons.mdx             # Button components
│   ├── forms.mdx               # Form components
│   ├── layouts.mdx             # Layout components
│   └── visualizations.mdx      # Chart/graph components
│
└── 05-architecture/
    ├── overview.mdx            # Architecture overview
    ├── backend.mdx             # Backend architecture
    ├── frontend.mdx            # Frontend architecture
    ├── database.mdx            # Database design
    └── infrastructure.mdx      # Infrastructure
```

### 2. **Internal Developer Documentation**

```
docs/fumadocs/content/docs/
├── 06-development/
│   ├── setup.mdx               # Dev environment setup
│   ├── backend-setup.mdx       # Backend development
│   ├── frontend-setup.mdx      # Frontend development
│   ├── database.mdx            # Database development
│   ├── testing.mdx             # Testing guide
│   ├── ci-cd.mdx               # CI/CD pipeline
│   └── deployment.mdx          # Deployment guide
│
├── 07-backend-internals/
│   ├── handlers.mdx            # Handler patterns
│   ├── middleware.mdx          # Middleware system
│   ├── database-layer.mdx      # Database layer
│   ├── search-engine.mdx       # Search implementation
│   ├── graph-algorithms.mdx    # Graph algorithms
│   ├── events.mdx              # Event sourcing
│   ├── realtime.mdx            # Real-time system
│   └── caching.mdx             # Caching strategy
│
├── 08-frontend-internals/
│   ├── state-management.mdx    # State management
│   ├── components.mdx          # Component architecture
│   ├── hooks.mdx               # Custom hooks
│   ├── styling.mdx             # Styling system
│   ├── testing.mdx             # Frontend testing
│   └── performance.mdx         # Performance optimization
│
└── 09-contributing/
    ├── code-style.mdx          # Code style guide
    ├── commit-messages.mdx     # Commit conventions
    ├── pull-requests.mdx       # PR process
    ├── documentation.mdx       # Doc standards
    └── release-process.mdx     # Release process
```

---

## 🔌 API Documentation Strategy

### Phase 1: OpenAPI Specification

**Generate from Go code using:**
- `swaggo/swag` - Swagger comment annotations
- `getkin/kin-openapi` - OpenAPI generation
- Custom script to extract from Echo routes

**Structure:**
```yaml
openapi: 3.1.0
info:
  title: TraceRTM API
  version: 1.0.0
  description: Multi-view Requirements Traceability System
  contact:
    name: TraceRTM Team
  license:
    name: MIT

servers:
  - url: https://api.tracertm.com/api/v1
    description: Production
  - url: http://localhost:8080/api/v1
    description: Development

paths:
  /projects:
    get:
      summary: List projects
      tags: [Projects]
      parameters:
        - name: limit
          in: query
          schema: { type: integer, default: 20 }
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema: { $ref: '#/components/schemas/ProjectList' }
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/ServerError'

components:
  schemas:
    Project:
      type: object
      required: [id, name, created_at]
      properties:
        id: { type: string, format: uuid }
        name: { type: string, minLength: 1, maxLength: 255 }
        description: { type: string, nullable: true }
        created_at: { type: string, format: date-time }
        updated_at: { type: string, format: date-time }
```

### Phase 2: Swagger UI Integration

**Deploy at:** `/api/docs`

```typescript
// swagger-ui-config.ts
import SwaggerUI from 'swagger-ui-dist'

const ui = SwaggerUI.presets.apis
const SwaggerUIBundle = SwaggerUI.SwaggerUIBundle

const swaggerUI = SwaggerUIBundle({
  url: '/openapi.yaml',
  dom_id: '#swagger-ui',
  presets: [SwaggerUI.presets.apis, SwaggerUI.SwaggerUIStandalonePreset],
  layout: 'BaseLayout',
  deepLinking: true,
  requestInterceptor: (request) => {
    request.headers['Authorization'] = `Bearer ${getToken()}`
    return request
  },
})
```

### Phase 3: ReDoc Integration

**Deploy at:** `/api/reference`

```typescript
// redoc-config.ts
import RedocStandalone from 'redoc'

RedocStandalone.init(
  '/openapi.yaml',
  {
    pageTitle: 'TraceRTM API Reference',
    theme: {
      colors: {
        primary: { main: '#0066cc' },
      },
      typography: {
        fontFamily: 'Inter, sans-serif',
      },
    },
    hideDownloadButton: false,
    expandSingleSchemaField: true,
  },
  document.getElementById('redoc-container')
)
```

---

## 🛠️ Implementation Phases

### Phase 1: Setup (Week 1)
- [ ] Initialize Fumadocs project
- [ ] Setup OpenAPI generation pipeline
- [ ] Create documentation structure
- [ ] Setup Swagger UI
- [ ] Setup ReDoc

### Phase 2: Backend API Docs (Week 2)
- [ ] Add OpenAPI annotations to Go handlers
- [ ] Generate OpenAPI spec
- [ ] Document all endpoints
- [ ] Add request/response examples
- [ ] Document error codes

### Phase 3: User Documentation (Week 2-3)
- [ ] Getting started guide
- [ ] User guide for each feature
- [ ] Best practices guide
- [ ] Troubleshooting guide
- [ ] FAQ

### Phase 4: Developer Documentation (Week 3-4)
- [ ] Development setup guide
- [ ] Backend internals documentation
- [ ] Frontend internals documentation
- [ ] Database schema documentation
- [ ] Architecture documentation

### Phase 5: Component Documentation (Week 4)
- [ ] Integrate Storybook
- [ ] Document all components
- [ ] Add usage examples
- [ ] Add accessibility notes

### Phase 6: Polish & Deploy (Week 5-6)
- [ ] Search functionality
- [ ] Dark mode
- [ ] Mobile responsiveness
- [ ] Analytics integration
- [ ] Deploy to production

---

## 📦 Dependencies to Add

```json
{
  "devDependencies": {
    "fumadocs-core": "^12.0.0",
    "fumadocs-ui": "^12.0.0",
    "fumadocs-openapi": "^12.0.0",
    "next": "^15.0.0",
    "react": "^19.0.0",
    "swagger-ui-dist": "^5.0.0",
    "redoc": "^2.1.0",
    "@redocly/cli": "^1.0.0",
    "typedoc": "^0.25.0",
    "typedoc-plugin-markdown": "^4.0.0"
  }
}
```

---

## 🎯 Success Criteria

✅ Single unified documentation site  
✅ Interactive API explorer (Swagger)  
✅ Beautiful API reference (ReDoc)  
✅ Complete user guides  
✅ Complete developer guides  
✅ Component documentation  
✅ Search functionality  
✅ Mobile responsive  
✅ Dark mode support  
✅ Analytics tracking  

---

## 📊 Current State vs. Target

| Aspect | Current | Target |
|--------|---------|--------|
| Documentation Format | Scattered markdown | Unified MDX/Fumadocs |
| API Docs | Manual markdown | OpenAPI + Swagger + ReDoc |
| Code Examples | Static | Interactive + runnable |
| Search | None | Full-text search |
| Mobile | Not optimized | Fully responsive |
| Dark Mode | None | Supported |
| Versioning | Manual | Automated |
| Analytics | None | Integrated |

---

## 🚀 Next Steps

1. **Review this plan** with team
2. **Approve scope** and timeline
3. **Setup Fumadocs** project
4. **Begin Phase 1** implementation
5. **Iterate** based on feedback

---

**Document Version:** 1.0  
**Last Updated:** December 2, 2025  
**Next Review:** After Phase 1 completion

