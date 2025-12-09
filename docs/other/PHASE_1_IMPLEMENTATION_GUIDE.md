# Phase 1: Setup & Infrastructure - Implementation Guide

## ✅ Current Status

The Fumadocs project is **already initialized** at `docs-site/`. This is excellent progress!

**What's Already Done:**
- ✅ Next.js 16 + React 19 + TypeScript 5.7
- ✅ Fumadocs v16.2.1 (latest)
- ✅ Tailwind CSS 4.1
- ✅ Radix UI components
- ✅ Project structure created
- ✅ Static export configured
- ✅ Search API endpoint ready

---

## 🎯 Phase 1 Remaining Tasks (8-10 hours)

### Task 1: Verify & Test Current Setup (1 hour)

```bash
cd docs-site
npm install  # or bun install
npm run dev  # Start dev server
# Visit http://localhost:3000
```

**Checklist:**
- [ ] Dev server starts without errors
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Search endpoint responds

### Task 2: Setup OpenAPI Generation Infrastructure (2 hours)

**Install swag for Go:**
```bash
cd backend
go install github.com/swaggo/swag/cmd/swag@latest
```

**Create OpenAPI generation script:**
```bash
# In backend/scripts/generate-openapi.sh
swag init -g main.go -o docs/swagger
```

**Checklist:**
- [ ] swag installed
- [ ] Generation script created
- [ ] OpenAPI spec generates successfully
- [ ] Spec validates with @redocly/cli

### Task 3: Integrate Swagger UI (2 hours)

**Create Swagger UI page:**
```bash
# docs-site/app/api-explorer/page.tsx
# (See SWAGGER_REDOC_INTEGRATION_GUIDE.md for code)
```

**Checklist:**
- [ ] Swagger UI page created
- [ ] API endpoint configured
- [ ] Try-it-out functionality works
- [ ] Authentication support added

### Task 4: Integrate ReDoc (2 hours)

**Create ReDoc page:**
```bash
# docs-site/app/api-reference/page.tsx
# (See SWAGGER_REDOC_INTEGRATION_GUIDE.md for code)
```

**Checklist:**
- [ ] ReDoc page created
- [ ] Beautiful rendering
- [ ] Dark mode works
- [ ] Mobile responsive

### Task 5: Setup Documentation Structure (1 hour)

**Create content directories:**
```bash
mkdir -p docs-site/content/docs/{
  00-getting-started,
  01-user-guide,
  02-api-reference,
  03-guides,
  04-components,
  05-architecture,
  06-development,
  07-backend-internals,
  08-frontend-internals,
  09-contributing
}
```

**Checklist:**
- [ ] All directories created
- [ ] meta.json navigation updated
- [ ] Index pages created
- [ ] Navigation renders correctly

### Task 6: Deploy to Staging (1 hour)

**Build static export:**
```bash
cd docs-site
npm run build:static
```

**Deploy options:**
- Vercel (recommended)
- GitHub Pages
- Netlify
- Self-hosted

**Checklist:**
- [ ] Static build succeeds
- [ ] All pages accessible
- [ ] Search works
- [ ] Performance acceptable

### Task 7: Setup CI/CD Pipeline (1 hour)

**Create GitHub Actions workflow:**
```yaml
# .github/workflows/docs.yml
name: Build & Deploy Docs
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: cd docs-site && npm install && npm run build:static
      - uses: actions/upload-artifact@v3
```

**Checklist:**
- [ ] Workflow created
- [ ] Builds on push
- [ ] Artifacts generated
- [ ] Deployment automated

---

## 📋 Success Criteria

- ✅ Dev server runs without errors
- ✅ Fumadocs site accessible at localhost:3000
- ✅ OpenAPI spec generates from Go code
- ✅ Swagger UI functional with try-it-out
- ✅ ReDoc displays API beautifully
- ✅ Documentation structure organized
- ✅ Static build completes successfully
- ✅ Deployed to staging environment
- ✅ CI/CD pipeline working
- ✅ All pages load < 2s

---

## 🚀 Next Steps After Phase 1

1. **Phase 2:** Add OpenAPI annotations to Go handlers
2. **Phase 3:** Integrate Swagger UI & ReDoc
3. **Phase 4:** Write user documentation
4. **Phase 5:** Write developer documentation
5. **Phase 6:** Add component & code documentation
6. **Phase 7:** Polish & deploy to production

---

## 📚 Reference Documents

- `FUMADOCS_SETUP_GUIDE.md` - Detailed setup
- `OPENAPI_GENERATION_GUIDE.md` - API spec generation
- `SWAGGER_REDOC_INTEGRATION_GUIDE.md` - UI integration
- `DOCUMENTATION_STANDARDS.md` - Writing standards

---

## ⏱️ Time Estimate

**Total Phase 1:** 8-10 hours

- Task 1: 1 hour
- Task 2: 2 hours
- Task 3: 2 hours
- Task 4: 2 hours
- Task 5: 1 hour
- Task 6: 1 hour
- Task 7: 1 hour

---

## 💡 Tips

1. **Use Bun** for faster installs: `bun install`
2. **Watch mode** for development: `npm run dev`
3. **Static export** for offline viewing
4. **Service worker** for offline capability
5. **Dark mode** built-in with Fumadocs

---

**Status:** Ready to Execute  
**Created:** December 2, 2025  
**Next Review:** After Task 1 Completion

