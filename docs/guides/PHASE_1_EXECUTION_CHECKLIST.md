# Phase 1: Setup & Infrastructure - Execution Checklist

## 🎯 Quick Start (Do This First)

```bash
# 1. Navigate to docs/site
cd docs/site

# 2. Install dependencies
npm install
# or faster with bun:
bun install

# 3. Start dev server
npm run dev

# 4. Open browser
# Visit http://localhost:3000
```

---

## ✅ Phase 1 Tasks Checklist

### [ ] Task 1: Verify Current Setup (1 hour)

**Steps:**
- [ ] `cd docs/site && npm install` completes without errors
- [ ] `npm run dev` starts server on port 3000
- [ ] Homepage loads at http://localhost:3000
- [ ] Navigation menu appears
- [ ] Search functionality works
- [ ] No console errors in browser

**Verification:**
```bash
# Check if dev server is running
curl http://localhost:3000
```

---

### [ ] Task 2: Setup OpenAPI Generation (2 hours)

**Backend Setup:**
```bash
cd backend

# Install swag
go install github.com/swaggo/swag/cmd/swag@latest

# Verify installation
swag --version

# Generate OpenAPI spec
swag init -g main.go -o docs/swagger

# Validate spec
npm install -g @redocly/cli
redocly lint docs/swagger/swagger.json
```

**Checklist:**
- [ ] swag installed successfully
- [ ] `swag init` generates swagger.json
- [ ] swagger.json is valid OpenAPI 3.0
- [ ] No validation errors

---

### [ ] Task 3: Create Swagger UI Page (2 hours)

**File:** `docs/site/app/api-explorer/page.tsx`

**Steps:**
- [ ] Create directory: `mkdir -p app/api-explorer`
- [ ] Create page.tsx with Swagger UI component
- [ ] Add API endpoint configuration
- [ ] Test at http://localhost:3000/api-explorer
- [ ] Verify try-it-out works
- [ ] Add authentication support

**Checklist:**
- [ ] Page loads without errors
- [ ] Swagger UI renders
- [ ] API spec loads
- [ ] Try-it-out functional
- [ ] Mobile responsive

---

### [ ] Task 4: Create ReDoc Page (2 hours)

**File:** `docs/site/app/api-reference/page.tsx`

**Steps:**
- [ ] Create directory: `mkdir -p app/api-reference`
- [ ] Create page.tsx with ReDoc component
- [ ] Configure dark mode
- [ ] Test at http://localhost:3000/api-reference
- [ ] Verify responsive design
- [ ] Add download spec button

**Checklist:**
- [ ] Page loads without errors
- [ ] ReDoc renders beautifully
- [ ] Dark mode toggle works
- [ ] Mobile responsive
- [ ] Download button works

---

### [ ] Task 5: Setup Documentation Structure (1 hour)

**Create directories:**
```bash
cd docs/site
mkdir -p content/docs/{
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

**Create index files:**
- [ ] Create `index.mdx` in each directory
- [ ] Add frontmatter with title & description
- [ ] Update `content/meta.json` navigation
- [ ] Test navigation in dev server

**Checklist:**
- [ ] All directories created
- [ ] Index files exist
- [ ] Navigation renders
- [ ] Links work correctly

---

### [ ] Task 6: Build Static Export (1 hour)

**Steps:**
```bash
cd docs/site

# Build static site
npm run build:static

# Verify output
ls -la out/
```

**Checklist:**
- [ ] Build completes without errors
- [ ] `out/` directory created
- [ ] `out/index.html` exists
- [ ] All pages exported
- [ ] Static files optimized

---

### [ ] Task 7: Deploy to Staging (1 hour)

**Option A: Vercel (Recommended)**
```bash
npm install -g vercel
vercel --prod
```

**Option B: GitHub Pages**
- [ ] Push to GitHub
- [ ] Enable Pages in settings
- [ ] Set source to `docs/site/out`

**Option C: Self-hosted**
```bash
cd docs/site/out
python3 -m http.server 8000
# Visit http://localhost:4000
```

**Checklist:**
- [ ] Site deployed
- [ ] Accessible via URL
- [ ] All pages load
- [ ] Search works
- [ ] Performance acceptable

---

### [ ] Task 8: Setup CI/CD Pipeline (1 hour)

**Create:** `.github/workflows/docs-build.yml`

**Checklist:**
- [ ] Workflow file created
- [ ] Triggers on push
- [ ] Builds successfully
- [ ] Artifacts generated
- [ ] Deployment automated

---

## 📊 Progress Tracking

| Task | Status | Hours | Notes |
|------|--------|-------|-------|
| 1. Verify Setup | [ ] | 1h | |
| 2. OpenAPI Gen | [ ] | 2h | |
| 3. Swagger UI | [ ] | 2h | |
| 4. ReDoc | [ ] | 2h | |
| 5. Doc Structure | [ ] | 1h | |
| 6. Static Build | [ ] | 1h | |
| 7. Deploy | [ ] | 1h | |
| 8. CI/CD | [ ] | 1h | |
| **TOTAL** | | **11h** | |

---

## 🚀 Success Criteria

- ✅ Dev server runs without errors
- ✅ Fumadocs site accessible
- ✅ OpenAPI spec generates
- ✅ Swagger UI functional
- ✅ ReDoc displays beautifully
- ✅ Documentation organized
- ✅ Static build succeeds
- ✅ Deployed to staging
- ✅ CI/CD working
- ✅ All pages load < 2s

---

## 📞 Troubleshooting

**Dev server won't start:**
```bash
rm -rf node_modules .next
npm install
npm run dev
```

**OpenAPI spec not generating:**
```bash
cd backend
go mod tidy
swag init -g main.go -o docs/swagger
```

**Build fails:**
```bash
npm run build -- --debug
```

---

## 📚 Reference Guides

- `FUMADOCS_SETUP_GUIDE.md` - Detailed setup
- `OPENAPI_GENERATION_GUIDE.md` - API spec
- `SWAGGER_REDOC_INTEGRATION_GUIDE.md` - UI integration
- `DOCUMENTATION_STANDARDS.md` - Writing standards

---

**Status:** Ready to Execute  
**Estimated Duration:** 8-10 hours  
**Next Phase:** Phase 2 - Backend API Documentation

