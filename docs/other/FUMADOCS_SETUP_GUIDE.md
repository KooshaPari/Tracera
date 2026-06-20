# Fumadocs Setup Guide

## Phase 1: Initial Setup

### 1. Create Fumadocs Project

```bash
# Create new Next.js app with Fumadocs
npx create-next-app@latest docs/fumadocs --typescript --tailwind --app

cd docs/fumadocs
```

### 2. Install Fumadocs Dependencies

```bash
npm install fumadocs-core fumadocs-ui fumadocs-openapi
npm install -D @fumadocs/cli
```

### 3. Project Structure

```
docs/fumadocs/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Home page
│   ├── docs/
│   │   ├── layout.tsx          # Docs layout
│   │   └── [[...slug]]/
│   │       └── page.tsx        # Dynamic docs pages
│   ├── api/
│   │   ├── docs/
│   │   │   └── route.ts        # OpenAPI endpoint
│   │   └── search/
│   │       └── route.ts        # Search endpoint
│   └── globals.css
│
├── content/
│   ├── docs/
│   │   ├── index.mdx
│   │   ├── getting-started/
│   │   ├── user-guide/
│   │   ├── api-reference/
│   │   ├── guides/
│   │   ├── components/
│   │   └── architecture/
│   └── meta.json               # Navigation structure
│
├── lib/
│   ├── source.ts               # Content source config
│   └── utils.ts
│
├── public/
│   ├── openapi.yaml            # Generated OpenAPI spec
│   └── images/
│
├── fumadocs.config.ts          # Fumadocs config
├── next.config.js
├── tailwind.config.ts
└── package.json
```

### 4. Configure Fumadocs

**fumadocs.config.ts:**
```typescript
import { defineConfig } from 'fumadocs-core/config'
import { remarkDocGen } from 'fumadocs-core/mdx-plugins'

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [remarkDocGen],
  },
})
```

### 5. Setup Content Source

**lib/source.ts:**
```typescript
import { loader } from 'fumadocs-core/source'
import { createMDXSource } from 'fumadocs-mdx'
import { icons } from 'lucide-react'

export const source = loader({
  baseUrl: '/docs',
  source: createMDXSource(
    new Map([
      [
        'docs',
        {
          title: 'Documentation',
          description: 'Learn how to use TraceRTM',
          icon: icons.book,
        },
      ],
    ]),
    {
      dir: './content/docs',
    }
  ),
})
```

### 6. Create Root Layout

**app/layout.tsx:**
```typescript
import type { Metadata } from 'next'
import { RootProvider } from 'fumadocs-ui/provider'
import './globals.css'

export const metadata: Metadata = {
  title: 'TraceRTM Documentation',
  description: 'Complete documentation for TraceRTM',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  )
}
```

### 7. Create Docs Layout

**app/docs/layout.tsx:**
```typescript
import { DocsLayout } from 'fumadocs-ui/layout'
import { source } from '@/lib/source'

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

### 8. Create Docs Page

**app/docs/[[...slug]]/page.tsx:**
```typescript
import { source } from '@/lib/source'
import { DocsPage, DocsBody } from 'fumadocs-ui/page'
import { notFound } from 'next/navigation'

export async function generateStaticParams() {
  return source.generateParams()
}

export async function generateMetadata(props: {
  params: Promise<{ slug?: string[] }>
}) {
  const params = await props.params
  const page = source.getPage(params.slug)
  if (!page) notFound()

  return {
    title: page.data.title,
    description: page.data.description,
  }
}

export default async function Page(props: {
  params: Promise<{ slug?: string[] }>
}) {
  const params = await props.params
  const page = source.getPage(params.slug)
  if (!page) notFound()

  return (
    <DocsPage toc={page.data.toc}>
      <DocsBody>{page.data.body}</DocsBody>
    </DocsPage>
  )
}
```

### 9. Setup Navigation

**content/meta.json:**
```json
{
  "docs": [
    {
      "title": "Getting Started",
      "url": "/docs/getting-started",
      "items": [
        { "title": "Installation", "url": "/docs/getting-started/installation" },
        { "title": "Quick Start", "url": "/docs/getting-started/quick-start" }
      ]
    },
    {
      "title": "User Guide",
      "url": "/docs/user-guide",
      "items": [
        { "title": "Projects", "url": "/docs/user-guide/projects" },
        { "title": "Items", "url": "/docs/user-guide/items" }
      ]
    },
    {
      "title": "API Reference",
      "url": "/docs/api-reference",
      "items": [
        { "title": "Authentication", "url": "/docs/api-reference/auth" },
        { "title": "Projects", "url": "/docs/api-reference/projects" }
      ]
    }
  ]
}
```

### 10. Add Search

**app/api/search/route.ts:**
```typescript
import { source } from '@/lib/source'
import { createSearchAPI } from 'fumadocs-core/search/server'

export const { GET } = createSearchAPI('advanced', {
  indexes: source.getPages().map((page) => ({
    title: page.data.title,
    description: page.data.description,
    url: page.url,
    structuredData: page.data,
  })),
})
```

### 11. Configure Next.js

**next.config.js:**
```javascript
import { withFumadocs } from 'fumadocs-core/next-plugin'

export default withFumadocs({
  reactStrictMode: true,
})
```

### 12. Add Scripts

**package.json:**
```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "generate:openapi": "node scripts/generate-openapi.ts",
    "generate:docs": "npm run generate:openapi"
  }
}
```

---

## Testing Setup

```bash
# Start development server
npm run dev

# Visit http://localhost:3000/docs
```

---

## Next Steps

1. Create initial MDX content files
2. Setup OpenAPI generation
3. Integrate Swagger UI
4. Integrate ReDoc
5. Add search functionality
6. Deploy to production

---

**Status:** Ready for Phase 2  
**Estimated Time:** 2-3 hours

