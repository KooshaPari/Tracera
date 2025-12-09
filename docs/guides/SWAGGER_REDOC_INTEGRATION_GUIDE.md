# Swagger UI & ReDoc Integration Guide

## Phase 3: Interactive API Documentation

### 1. Setup Swagger UI

**docs/fumadocs/app/api/docs/route.ts:**

```typescript
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    url: '/openapi.yaml',
  })
}
```

**docs/fumadocs/app/api/swagger/route.ts:**

```typescript
import { readFileSync } from 'fs'
import { join } from 'path'
import { NextResponse } from 'next/server'
import yaml from 'yaml'

export async function GET() {
  try {
    const filePath = join(process.cwd(), 'public/openapi.yaml')
    const fileContent = readFileSync(filePath, 'utf-8')
    const spec = yaml.parse(fileContent)
    return NextResponse.json(spec)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to load OpenAPI spec' },
      { status: 500 }
    )
  }
}
```

### 2. Create Swagger UI Page

**docs/fumadocs/app/api-explorer/page.tsx:**

```typescript
'use client'

import { useEffect } from 'react'
import SwaggerUI from 'swagger-ui-dist'
import 'swagger-ui-dist/swagger-ui.css'

export default function SwaggerPage() {
  useEffect(() => {
    const ui = SwaggerUI({
      url: '/api/swagger',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUI.presets.apis,
        SwaggerUI.SwaggerUIStandalonePreset,
      ],
      layout: 'BaseLayout',
      deepLinking: true,
      requestInterceptor: (request) => {
        // Add auth token if available
        const token = localStorage.getItem('authToken')
        if (token) {
          request.headers['Authorization'] = `Bearer ${token}`
        }
        return request
      },
      responseInterceptor: (response) => {
        console.log('API Response:', response)
        return response
      },
      onComplete: () => {
        console.log('Swagger UI loaded')
      },
    })

    return () => {
      // Cleanup
    }
  }, [])

  return (
    <div className="min-h-screen bg-white">
      <div id="swagger-ui" />
    </div>
  )
}
```

### 3. Setup ReDoc

**docs/fumadocs/app/api-reference/page.tsx:**

```typescript
'use client'

import { useEffect } from 'react'
import dynamic from 'next/dynamic'

const Redoc = dynamic(() => import('redoc').then((mod) => mod.Redoc), {
  ssr: false,
})

export default function ReDocPage() {
  return (
    <div className="min-h-screen bg-white">
      <Redoc
        specUrl="/api/swagger"
        options={{
          pageTitle: 'TraceRTM API Reference',
          theme: {
            colors: {
              primary: {
                main: '#0066cc',
              },
              success: {
                main: '#10b981',
              },
              warning: {
                main: '#f59e0b',
              },
              error: {
                main: '#ef4444',
              },
            },
            typography: {
              fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
              fontSize: '14px',
              lineHeight: '1.5',
            },
            sidebar: {
              width: '250px',
              backgroundColor: '#f9fafb',
            },
          },
          hideDownloadButton: false,
          expandSingleSchemaField: true,
          sortPropsAlphabetically: true,
          sortEnumValuesAlphabetically: true,
          showExtensions: true,
          disableSearch: false,
          nativeScrollbars: true,
          pathInMiddlePanel: true,
          suppressWarnings: false,
          hideHostname: false,
          hideSchemes: false,
          hideInfo: false,
          hideModels: false,
          hideLoading: false,
          hideDownloadButton: false,
          downloadFileName: 'tracertm-api.json',
          onlyRequiredInSamples: false,
          enumSkipQuotes: false,
          jsonSampleExpandLevel: 2,
          unstable_ignoreMimeTypesOrder: false,
        }}
      />
    </div>
  )
}
```

### 4. Add Navigation Links

**docs/fumadocs/app/docs/layout.tsx:**

```typescript
import { DocsLayout } from 'fumadocs-ui/layout'
import { source } from '@/lib/source'
import Link from 'next/link'

export default function Layout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: 'TraceRTM',
        url: '/',
        links: [
          {
            text: 'API Explorer',
            url: '/api-explorer',
            icon: '🔍',
          },
          {
            text: 'API Reference',
            url: '/api-reference',
            icon: '📚',
          },
        ],
      }}
      sidebar={{
        collapsible: true,
      }}
    >
      {children}
    </DocsLayout>
  )
}
```

### 5. Add Styling

**docs/fumadocs/app/globals.css:**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Swagger UI customization */
.swagger-ui {
  --topbar-bg: #ffffff;
  --topbar-text-color: #3f3f46;
  --base-bg: #f9fafb;
  --base-text-color: #1f2937;
  --code-bg: #f3f4f6;
  --code-text-color: #1f2937;
}

.swagger-ui .topbar {
  background-color: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.swagger-ui .info .title {
  color: #1f2937;
  font-size: 28px;
  font-weight: 700;
}

.swagger-ui .btn {
  border-radius: 6px;
  font-weight: 500;
}

.swagger-ui .btn-primary {
  background-color: #0066cc;
  border-color: #0066cc;
}

.swagger-ui .btn-primary:hover {
  background-color: #0052a3;
  border-color: #0052a3;
}

/* ReDoc customization */
.redoc-container {
  font-family: Inter, -apple-system, BlinkMacSystemFont, sans-serif;
}

.redoc-container h1,
.redoc-container h2,
.redoc-container h3 {
  color: #1f2937;
}

.redoc-container code {
  background-color: #f3f4f6;
  color: #1f2937;
  border-radius: 4px;
  padding: 2px 6px;
}

.redoc-container pre {
  background-color: #1f2937;
  color: #f3f4f6;
  border-radius: 6px;
  padding: 12px;
}
```

### 6. Add Dark Mode Support

**docs/fumadocs/app/api-explorer/page.tsx (updated):**

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useTheme } from 'next-themes'
import SwaggerUI from 'swagger-ui-dist'
import 'swagger-ui-dist/swagger-ui.css'

export default function SwaggerPage() {
  const { theme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return

    const ui = SwaggerUI({
      url: '/api/swagger',
      dom_id: '#swagger-ui',
      presets: [
        SwaggerUI.presets.apis,
        SwaggerUI.SwaggerUIStandalonePreset,
      ],
      layout: 'BaseLayout',
      deepLinking: true,
      theme: theme === 'dark' ? 'dark' : 'light',
      requestInterceptor: (request) => {
        const token = localStorage.getItem('authToken')
        if (token) {
          request.headers['Authorization'] = `Bearer ${token}`
        }
        return request
      },
    })

    return () => {
      // Cleanup
    }
  }, [theme, mounted])

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-white dark:bg-slate-950">
      <div id="swagger-ui" />
    </div>
  )
}
```

### 7. Add Authentication Support

**docs/fumadocs/lib/auth.ts:**

```typescript
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem('authToken')
}

export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return
  localStorage.setItem('authToken', token)
}

export function clearAuthToken(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem('authToken')
}

export function isAuthenticated(): boolean {
  return !!getAuthToken()
}
```

**docs/fumadocs/app/api-explorer/auth-dialog.tsx:**

```typescript
'use client'

import { useState } from 'react'
import { setAuthToken, getAuthToken } from '@/lib/auth'

export function AuthDialog() {
  const [token, setToken] = useState(getAuthToken() || '')
  const [open, setOpen] = useState(false)

  const handleSave = () => {
    setAuthToken(token)
    setOpen(false)
  }

  return (
    <div className="fixed top-4 right-4 z-50">
      <button
        onClick={() => setOpen(!open)}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
      >
        🔐 Auth
      </button>

      {open && (
        <div className="absolute top-12 right-0 bg-white dark:bg-slate-900 border border-gray-200 dark:border-slate-700 rounded-lg p-4 w-80 shadow-lg">
          <h3 className="font-semibold mb-2">API Token</h3>
          <textarea
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="Paste your JWT token here"
            className="w-full h-24 p-2 border border-gray-300 dark:border-slate-600 rounded text-sm font-mono"
          />
          <div className="flex gap-2 mt-3">
            <button
              onClick={handleSave}
              className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Save
            </button>
            <button
              onClick={() => setOpen(false)}
              className="flex-1 px-3 py-2 bg-gray-200 dark:bg-slate-700 rounded hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
```

### 8. Update package.json

```json
{
  "dependencies": {
    "swagger-ui-dist": "^5.0.0",
    "redoc": "^2.1.0",
    "next-themes": "^0.2.1"
  },
  "devDependencies": {
    "@redocly/cli": "^1.0.0"
  }
}
```

---

## Testing

```bash
# Start dev server
npm run dev

# Visit:
# - http://localhost:3000/api-explorer (Swagger UI)
# - http://localhost:3000/api-reference (ReDoc)
```

---

## Deployment

### Vercel

```bash
# Deploy automatically on push
vercel deploy
```

### Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

---

## Next Steps

1. Add authentication to API explorer
2. Add request/response examples
3. Add API testing capabilities
4. Add API versioning support
5. Deploy to production

---

**Status:** Ready for Phase 4  
**Estimated Time:** 3-4 hours

