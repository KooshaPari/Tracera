# Phase 1: Technical Implementation Details

## Task 1: Verify Current Setup

### Quick Verification Script

```bash
#!/bin/bash
cd docs-site

echo "🔍 Checking Node.js..."
node --version

echo "🔍 Checking npm..."
npm --version

echo "🔍 Checking dependencies..."
npm list fumadocs-core fumadocs-ui next react

echo "🔍 Starting dev server..."
npm run dev &
DEV_PID=$!

sleep 5

echo "🔍 Testing homepage..."
curl -s http://localhost:3000 | head -20

echo "🔍 Testing search API..."
curl -s http://localhost:3000/api/search | head -20

kill $DEV_PID
echo "✅ Verification complete!"
```

---

## Task 2: OpenAPI Generation Setup

### Step 1: Install swag

```bash
cd backend
go install github.com/swaggo/swag/cmd/swag@latest

# Verify
which swag
swag --version
```

### Step 2: Add Swagger Comments to main.go

```go
// @title TraceRTM API
// @version 1.0
// @description TraceRTM Backend API
// @host localhost:8080
// @basePath /api/v1
// @schemes http https
// @securityDefinitions.apikey Bearer
// @in header
// @name Authorization
func main() {
    // ...
}
```

### Step 3: Generate OpenAPI Spec

```bash
cd backend
swag init -g main.go -o docs/swagger

# Output: docs/swagger/swagger.json
```

### Step 4: Validate Spec

```bash
npm install -g @redocly/cli
redocly lint docs/swagger/swagger.json
```

---

## Task 3: Swagger UI Integration

### Create: `docs-site/app/api-explorer/page.tsx`

```typescript
'use client'

import { useEffect } from 'react'
import SwaggerUI from 'swagger-ui-dist'
import 'swagger-ui-dist/swagger-ui.css'

export default function SwaggerPage() {
  useEffect(() => {
    const ui = SwaggerUI({
      url: '/api/swagger.json',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUI.presets.apis,
        SwaggerUI.SwaggerUIStandalonePreset,
      ],
      layout: 'BaseLayout',
      deepLinking: true,
      requestInterceptor: (request) => {
        const token = localStorage.getItem('authToken')
        if (token) {
          request.headers['Authorization'] = `Bearer ${token}`
        }
        return request
      },
    })
  }, [])

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <div id="swagger-ui" />
    </div>
  )
}
```

### Install Dependencies

```bash
cd docs-site
npm install swagger-ui-dist
```

---

## Task 4: ReDoc Integration

### Create: `docs-site/app/api-reference/page.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import dynamic from 'next/dynamic'

const ReDocStandalone = dynamic(
  () => import('redoc').then((mod) => mod.ReDocStandalone),
  { ssr: false }
)

export default function ReDocPage() {
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains('dark'))
  }, [])

  return (
    <div className="min-h-screen">
      <ReDocStandalone
        specUrl="/api/swagger.json"
        options={{
          theme: {
            colors: {
              primary: {
                main: isDark ? '#3b82f6' : '#2563eb',
              },
            },
            typography: {
              fontFamily: 'system-ui, -apple-system, sans-serif',
            },
          },
        }}
      />
    </div>
  )
}
```

### Install Dependencies

```bash
cd docs-site
npm install redoc
```

---

## Task 5: Documentation Structure

### Create Directories

```bash
cd docs-site
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

### Create Index Files

Each directory needs `index.mdx`:

```mdx
---
title: Getting Started
description: Get up and running with TraceRTM
---

# Getting Started

Welcome to TraceRTM documentation!

## Quick Links

- [Installation](/docs/getting-started/installation)
- [Configuration](/docs/getting-started/configuration)
- [First Steps](/docs/getting-started/first-steps)
```

### Update Navigation: `content/meta.json`

```json
{
  "docs": [
    {
      "title": "Getting Started",
      "url": "/docs/getting-started"
    },
    {
      "title": "User Guide",
      "url": "/docs/user-guide"
    },
    {
      "title": "API Reference",
      "url": "/docs/api-reference"
    }
  ]
}
```

---

## Task 6: Static Build

### Build Command

```bash
cd docs-site
npm run build:static
```

### Verify Output

```bash
ls -la out/
# Should contain:
# - index.html
# - _next/
# - api/
# - docs/
# - 404.html
```

---

## Task 7: Deployment Options

### Vercel (Recommended)

```bash
npm install -g vercel
cd docs-site
vercel --prod
```

### GitHub Pages

1. Push to GitHub
2. Settings → Pages
3. Source: `docs-site/out`
4. Deploy

### Self-Hosted

```bash
cd docs-site/out
python3 -m http.server 8000
# Visit http://localhost:8000
```

---

## Task 8: CI/CD Pipeline

### Create: `.github/workflows/docs-build.yml`

```yaml
name: Build & Deploy Docs

on:
  push:
    branches: [main]
    paths:
      - 'docs-site/**'
      - 'backend/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: cd docs-site && npm install
      
      - name: Build static site
        run: cd docs-site && npm run build:static
      
      - name: Deploy to Vercel
        run: npx vercel deploy --prod --token ${{ secrets.VERCEL_TOKEN }}
```

---

## 🔧 Troubleshooting

### Issue: Port 3000 already in use

```bash
# Find process
lsof -i :3000

# Kill process
kill -9 <PID>

# Or use different port
npm run dev -- -p 3001
```

### Issue: Build fails

```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

### Issue: OpenAPI spec not found

```bash
# Verify file exists
ls -la backend/docs/swagger/swagger.json

# Check permissions
chmod 644 backend/docs/swagger/swagger.json
```

---

## ✅ Verification Checklist

- [ ] Dev server runs on port 3000
- [ ] Homepage loads
- [ ] Navigation works
- [ ] Search API responds
- [ ] OpenAPI spec generates
- [ ] Swagger UI loads
- [ ] ReDoc renders
- [ ] Static build succeeds
- [ ] All pages accessible
- [ ] Performance < 2s

---

**Status:** Ready to Implement  
**Estimated Time:** 8-10 hours  
**Next:** Execute tasks in order

