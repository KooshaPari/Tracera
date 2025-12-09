# Documentation Migration Quick Reference

## 📚 Key Documents

| Document | Purpose | Audience |
|----------|---------|----------|
| `DOCUMENTATION_MIGRATION_PLAN.md` | Overall strategy & architecture | Everyone |
| `FUMADOCS_SETUP_GUIDE.md` | Step-by-step Fumadocs setup | Developers |
| `OPENAPI_GENERATION_GUIDE.md` | API spec generation | Backend devs |
| `SWAGGER_REDOC_INTEGRATION_GUIDE.md` | Interactive API docs | Frontend devs |
| `DOCUMENTATION_STANDARDS.md` | Writing standards & examples | All writers |
| `IMPLEMENTATION_CHECKLIST.md` | Task tracking & progress | Project manager |

---

## 🚀 Quick Start

### 1. Setup Fumadocs (30 min)

```bash
# Create project
npx create-next-app@latest docs/fumadocs --typescript --tailwind --app

# Install dependencies
cd docs/fumadocs
npm install fumadocs-core fumadocs-ui fumadocs-openapi

# Copy configuration files
cp ../FUMADOCS_SETUP_GUIDE.md ./SETUP.md
```

### 2. Generate OpenAPI Spec (1 hour)

```bash
# Add swagger comments to Go handlers
# See OPENAPI_GENERATION_GUIDE.md for examples

# Generate spec
cd backend
go install github.com/swaggo/swag/cmd/swag@latest
swag init -g main.go

# Validate
npm install -D @redocly/cli
redocly lint docs/swagger.yaml
```

### 3. Integrate Swagger UI & ReDoc (1 hour)

```bash
# Install dependencies
npm install swagger-ui-dist redoc

# Copy integration files
# See SWAGGER_REDOC_INTEGRATION_GUIDE.md

# Test
npm run dev
# Visit http://localhost:3000/api-explorer
```

---

## 📝 Documentation Structure

```
docs/fumadocs/content/docs/
├── 00-getting-started/      # User onboarding
├── 01-user-guide/           # Feature guides
├── 02-api-reference/        # API endpoints
├── 03-guides/               # Best practices
├── 04-components/           # UI components
├── 05-architecture/         # System design
├── 06-development/          # Dev setup
├── 07-backend-internals/    # Backend details
├── 08-frontend-internals/   # Frontend details
└── 09-contributing/         # Contribution guide
```

---

## 🔧 Common Tasks

### Add a New API Endpoint

1. **Add Go handler with swagger comments:**
```go
// @Summary Get item by ID
// @Tags Items
// @Param id path string true "Item ID"
// @Success 200 {object} Item
// @Router /items/{id} [get]
func (h *ItemHandler) GetItem(c echo.Context) error {
    // Implementation
}
```

2. **Generate OpenAPI spec:**
```bash
cd backend && swag init -g main.go
```

3. **Spec auto-updates in Swagger UI & ReDoc**

### Add User Documentation

1. **Create MDX file:**
```bash
touch docs/fumadocs/content/docs/01-user-guide/new-feature.mdx
```

2. **Write content:**
```mdx
---
title: "Feature Name"
description: "Brief description"
---

# Feature Name

Content here...
```

3. **Add to navigation:**
```json
// content/meta.json
{
  "docs": [
    {
      "title": "User Guide",
      "items": [
        { "title": "Feature Name", "url": "/docs/user-guide/new-feature" }
      ]
    }
  ]
}
```

### Add Code Examples

```mdx
<Tabs items={["cURL", "JavaScript", "Go"]}>
  <Tabs.Tab>
    ```bash
    curl -X GET http://localhost:8080/api/v1/items/123
    ```
  </Tabs.Tab>

  <Tabs.Tab>
    ```typescript
    const item = await client.items.get('123')
    ```
  </Tabs.Tab>

  <Tabs.Tab>
    ```go
    item, _ := client.Items.Get(ctx, "123")
    ```
  </Tabs.Tab>
</Tabs>
```

---

## 📊 Progress Tracking

### Phase Completion

- [ ] **Phase 1** (Week 1): Setup & Infrastructure
- [ ] **Phase 2** (Week 2): Backend API Docs
- [ ] **Phase 3** (Week 2-3): Interactive Explorers
- [ ] **Phase 4** (Week 3-4): User Documentation
- [ ] **Phase 5** (Week 4-5): Developer Documentation
- [ ] **Phase 6** (Week 5): Component & Code Docs
- [ ] **Phase 7** (Week 6): Polish & Deployment

### Key Milestones

- [ ] Fumadocs site live
- [ ] OpenAPI spec complete
- [ ] Swagger UI working
- [ ] ReDoc working
- [ ] All endpoints documented
- [ ] All user guides written
- [ ] All dev guides written
- [ ] Production deployment

---

## 🎯 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| API Coverage | 100% | [ ] |
| Example Coverage | 100% | [ ] |
| Search Working | Yes | [ ] |
| Mobile Responsive | Yes | [ ] |
| Dark Mode | Yes | [ ] |
| Page Load Time | < 2s | [ ] |
| Uptime | 99.9% | [ ] |
| User Rating | > 4.5/5 | [ ] |

---

## 🔗 Useful Links

### Tools
- [Fumadocs](https://fumadocs.vercel.app/)
- [Swagger UI](https://swagger.io/tools/swagger-ui/)
- [ReDoc](https://redoc.ly/)
- [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0)

### Standards
- [Google Documentation Style Guide](https://developers.google.com/style)
- [Write the Docs](https://www.writethedocs.org/)
- [OpenAPI Best Practices](https://swagger.io/resources/articles/best-practices-in-api-design/)

### Examples
- [Stripe API Docs](https://stripe.com/docs/api)
- [GitHub API Docs](https://docs.github.com/en/rest)
- [Vercel API Docs](https://vercel.com/docs/api)

---

## 💡 Tips & Tricks

### Fumadocs
- Use `<Tabs>` for multi-language examples
- Use `<Callout>` for important notes
- Use `<CodeBlock>` for syntax highlighting
- Use `<Image>` for diagrams

### OpenAPI
- Use `$ref` for schema reuse
- Use `allOf` for composition
- Use `oneOf` for unions
- Use `discriminator` for polymorphism

### Swagger UI
- Use `requestInterceptor` for auth
- Use `responseInterceptor` for logging
- Use `presets` for customization
- Use `plugins` for extensions

### ReDoc
- Use `theme` for styling
- Use `sidebar` for navigation
- Use `expandSingleSchemaField` for UX
- Use `hideDownloadButton` for control

---

## 🐛 Troubleshooting

### Swagger UI not loading
```bash
# Check if OpenAPI spec is valid
redocly lint public/openapi.yaml

# Check if CORS is enabled
# Add to backend: c.Header("Access-Control-Allow-Origin", "*")
```

### ReDoc not rendering
```bash
# Check if spec URL is correct
# Check browser console for errors
# Try different theme settings
```

### Search not working
```bash
# Check if search API is running
# Check if content is indexed
# Check browser console for errors
```

### Dark mode not working
```bash
# Check if next-themes is installed
# Check if provider is in layout
# Check if CSS variables are defined
```

---

## 📞 Support

- **Questions?** Check the relevant guide document
- **Issues?** Check troubleshooting section
- **Stuck?** Review the implementation checklist
- **Feedback?** Create an issue on GitHub

---

**Version:** 1.0  
**Last Updated:** December 2, 2025  
**Next Update:** After Phase 1 completion

