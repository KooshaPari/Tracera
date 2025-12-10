# TraceRTM Documentation Architecture Plan

## Executive Summary

This document outlines a comprehensive documentation architecture for TraceRTM that follows Fumadocs best practices, implements proper client type separation with combobox navigation, and establishes a scalable content structure for multi-audience documentation.

---

## Table of Contents

1. [Current State Analysis](#1-current-state-analysis)
2. [Target Architecture](#2-target-architecture)
3. [Fumadocs Integration](#3-fumadocs-integration)
4. [Document Type Separation](#4-document-type-separation)
5. [Navigation Implementation](#5-navigation-implementation)
6. [MDX Components](#6-mdx-components)
7. [File Structure](#7-file-structure)
8. [Search and Indexing](#8-search-and-indexing)
9. [Migration Strategy](#9-migration-strategy)
10. [Implementation Phases](#10-implementation-phases)

---

## 1. Current State Analysis

### Existing Infrastructure

**Technology Stack:**
- Next.js 16 with React 19
- Fumadocs Core v16.2.1, Fumadocs MDX v14.0.4, Fumadocs UI v16.2.1
- Fumadocs OpenAPI v10.1.0 (for API docs generation)
- Tailwind CSS with custom design tokens
- Mermaid for diagrams
- Static export enabled

**Current Structure Issues:**
1. **Flat navigation hierarchy** - All docs in a single sidebar without audience separation
2. **Manual structure.ts mapping** - Custom routing instead of Fumadocs conventions
3. **No source.ts configuration** - Missing Fumadocs content source setup
4. **Placeholder content** - MDX files have generic template content
5. **Missing MDX component library** - Limited rich content components
6. **No search implementation** - Search infrastructure not configured
7. **No OpenAPI integration** - API docs not auto-generated from OpenAPI spec

**Existing Assets:**
- OpenAPI spec at `/frontend/apps/web/public/specs/openapi.json`
- Python CLI built with Typer
- React frontend at `/frontend/apps/web/`
- Desktop app (Tauri) at `/frontend/apps/desktop/`
- Component library at `/frontend/packages/ui/`

---

## 2. Target Architecture

### Multi-Audience Documentation Model

```
                    +---------------------------+
                    |    Documentation Portal   |
                    |    (docs.tracertm.com)    |
                    +---------------------------+
                              |
            +-----------------+-----------------+
            |                 |                 |
    +-------v------+  +-------v------+  +-------v------+
    |  User Docs   |  | Developer    |  |  API/SDK     |
    |  (Business)  |  |    Docs      |  |    Docs      |
    +-------+------+  +-------+------+  +-------+------+
            |                 |                 |
    +-------v------+  +-------v------+  +-------v------+
    | - Getting    |  | - Setup      |  | - REST API   |
    |   Started    |  | - Arch.      |  | - GraphQL    |
    | - Concepts   |  | - Backend    |  | - Python SDK |
    | - Guides     |  | - CLI Dev    |  | - JS SDK     |
    | - Use Cases  |  | - Frontend   |  | - Go SDK     |
    | - FAQ        |  | - Internals  |  | - CLI Ref    |
    +--------------+  +--------------+  +--------------+
```

### URL Structure

```
/docs/                          # Landing page with doc type selector
/docs/user/                     # User documentation root
/docs/user/getting-started/
/docs/user/concepts/
/docs/user/guides/
/docs/user/use-cases/
/docs/user/faq/

/docs/developer/                # Developer documentation root
/docs/developer/setup/
/docs/developer/architecture/
/docs/developer/backend/
/docs/developer/frontend/
/docs/developer/cli/
/docs/developer/internals/
/docs/developer/contributing/

/docs/api/                      # API reference root
/docs/api/rest/                 # Auto-generated from OpenAPI
/docs/api/graphql/
/docs/api/authentication/

/docs/sdk/                      # SDK documentation root
/docs/sdk/python/
/docs/sdk/javascript/
/docs/sdk/go/

/docs/clients/                  # Client-specific guides
/docs/clients/web-ui/
/docs/clients/cli/
/docs/clients/desktop/
```

---

## 3. Fumadocs Integration

### 3.1 Source Configuration

Create `/docs-site/lib/source.ts`:

```typescript
import { docs, meta } from '@/.source';
import { loader } from 'fumadocs-core/source';
import { createMDXSource } from 'fumadocs-mdx';
import { createOpenAPI } from 'fumadocs-openapi/server';

// Define document sources for each audience
export const userDocs = loader({
  baseUrl: '/docs/user',
  rootDir: 'user',
  source: createMDXSource(docs, meta),
});

export const developerDocs = loader({
  baseUrl: '/docs/developer',
  rootDir: 'developer',
  source: createMDXSource(docs, meta),
});

export const apiDocs = loader({
  baseUrl: '/docs/api',
  rootDir: 'api',
  source: createMDXSource(docs, meta),
});

export const sdkDocs = loader({
  baseUrl: '/docs/sdk',
  rootDir: 'sdk',
  source: createMDXSource(docs, meta),
});

export const clientDocs = loader({
  baseUrl: '/docs/clients',
  rootDir: 'clients',
  source: createMDXSource(docs, meta),
});

// Combined source for search
export const allDocs = loader({
  baseUrl: '/docs',
  source: createMDXSource(docs, meta),
});

// OpenAPI integration
export const openAPISource = createOpenAPI({
  documentPath: './public/specs/openapi.json',
});
```

### 3.2 MDX Configuration

Update `/docs-site/source.config.ts`:

```typescript
import { defineConfig, defineDocs } from 'fumadocs-mdx/config';
import { rehypeCode, remarkGfm, remarkHeading } from 'fumadocs-core/mdx-plugins';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { transformerTwoslash } from 'fumadocs-twoslash';
import { createFileSystemTypesCache } from 'fumadocs-twoslash/cache';

export const { docs, meta } = defineDocs({
  dir: 'content/docs',
});

export default defineConfig({
  mdxOptions: {
    remarkPlugins: [
      remarkGfm,
      remarkHeading,
      remarkMath,
    ],
    rehypePlugins: (defaults) => [
      ...defaults,
      [rehypeCode, {
        themes: {
          light: 'github-light',
          dark: 'github-dark',
        },
        transformers: [
          transformerTwoslash({
            cache: createFileSystemTypesCache(),
          }),
        ],
      }],
      rehypeKatex,
    ],
  },
});
```

### 3.3 Next.js Configuration Update

Update `/docs-site/next.config.ts`:

```typescript
import { createMDX } from 'fumadocs-mdx/next';
import type { NextConfig } from 'next';

const withMDX = createMDX();

const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Remove static export for full Fumadocs features
  // output: 'export',
  images: {
    remotePatterns: [
      { hostname: 'api.tracertm.com' },
    ],
  },
};

export default withMDX(nextConfig);
```

### 3.4 Frontmatter Schema

Standard frontmatter for all MDX files:

```yaml
---
title: "Page Title"
description: "SEO and preview description"
icon: "IconName"  # Optional Lucide icon
keywords:
  - keyword1
  - keyword2
  - keyword3
version: "1.0.0"  # API version for breaking changes
audience: "user" | "developer" | "api" | "sdk" | "client"
client: "web" | "cli" | "desktop" | "all"  # For client-specific content
difficulty: "beginner" | "intermediate" | "advanced"
toc: true  # Show table of contents
index: false  # Exclude from search (for index pages)
updated: "2025-01-15"
---
```

---

## 4. Document Type Separation

### 4.1 User Documentation

**Target Audience:** Business analysts, project managers, QA engineers, compliance officers

**Content Categories:**

```
content/docs/user/
├── meta.json                    # Navigation metadata
├── index.mdx                    # User docs landing
├── getting-started/
│   ├── meta.json
│   ├── index.mdx               # Overview
│   ├── what-is-tracertm.mdx    # Product introduction
│   ├── quick-start.mdx         # 5-minute setup
│   ├── installation.mdx        # Detailed installation
│   └── first-matrix.mdx        # Create first traceability matrix
├── concepts/
│   ├── meta.json
│   ├── index.mdx
│   ├── traceability.mdx        # Core traceability concepts
│   ├── matrix.mdx              # Traceability matrix explained
│   ├── artifacts.mdx           # Items, requirements, etc.
│   ├── relationships.mdx       # Link types and semantics
│   ├── workflows.mdx           # Status and workflow management
│   └── versioning.mdx          # Version control concepts
├── guides/
│   ├── meta.json
│   ├── index.mdx
│   ├── creating-requirements.mdx
│   ├── linking-items.mdx
│   ├── generating-reports.mdx
│   ├── impact-analysis.mdx
│   ├── compliance-reporting.mdx
│   ├── team-collaboration.mdx
│   └── import-export.mdx
├── use-cases/
│   ├── meta.json
│   ├── index.mdx
│   ├── software-development.mdx
│   ├── medical-devices.mdx
│   ├── automotive.mdx
│   ├── aerospace.mdx
│   └── regulatory-compliance.mdx
├── best-practices/
│   ├── meta.json
│   ├── index.mdx
│   ├── naming-conventions.mdx
│   ├── matrix-organization.mdx
│   ├── linking-strategies.mdx
│   └── audit-preparation.mdx
└── faq/
    ├── meta.json
    ├── index.mdx
    ├── general.mdx
    ├── troubleshooting.mdx
    └── migration.mdx
```

### 4.2 Developer Documentation

**Target Audience:** Software engineers, DevOps, contributors

**Content Categories:**

```
content/docs/developer/
├── meta.json
├── index.mdx
├── setup/
│   ├── meta.json
│   ├── index.mdx
│   ├── prerequisites.mdx       # System requirements
│   ├── local-development.mdx   # Dev environment setup
│   ├── docker.mdx              # Container-based setup
│   ├── database.mdx            # Database configuration
│   └── environment.mdx         # Environment variables
├── architecture/
│   ├── meta.json
│   ├── index.mdx
│   ├── overview.mdx            # High-level architecture
│   ├── system-design.mdx       # System design decisions
│   ├── data-flow.mdx           # Request/data flow
│   ├── database-schema.mdx     # Database design
│   └── security.mdx            # Security architecture
├── backend/
│   ├── meta.json
│   ├── index.mdx
│   ├── api-structure.mdx       # FastAPI project structure
│   ├── models.mdx              # Data models
│   ├── repositories.mdx        # Repository pattern
│   ├── services.mdx            # Business logic layer
│   ├── events.mdx              # Event sourcing
│   └── testing.mdx             # Backend testing
├── frontend/
│   ├── meta.json
│   ├── index.mdx
│   ├── project-structure.mdx   # Monorepo structure
│   ├── components.mdx          # Component library
│   ├── state-management.mdx    # Zustand stores
│   ├── api-integration.mdx     # API client usage
│   └── testing.mdx             # Frontend testing
├── cli/
│   ├── meta.json
│   ├── index.mdx
│   ├── project-structure.mdx   # CLI architecture
│   ├── commands.mdx            # Adding commands
│   ├── tui.mdx                 # TUI development
│   └── testing.mdx             # CLI testing
├── internals/
│   ├── meta.json
│   ├── index.mdx
│   ├── traceability-engine.mdx
│   ├── query-engine.mdx
│   ├── caching.mdx
│   ├── indexing.mdx
│   └── plugin-system.mdx
├── deployment/
│   ├── meta.json
│   ├── index.mdx
│   ├── docker.mdx
│   ├── kubernetes.mdx
│   ├── aws.mdx
│   ├── azure.mdx
│   ├── gcp.mdx
│   └── monitoring.mdx
└── contributing/
    ├── meta.json
    ├── index.mdx
    ├── guidelines.mdx
    ├── code-style.mdx
    ├── pull-requests.mdx
    ├── testing.mdx
    └── documentation.mdx
```

### 4.3 API Documentation

**Target Audience:** API consumers, integration developers

**Content Categories:**

```
content/docs/api/
├── meta.json
├── index.mdx
├── overview/
│   ├── meta.json
│   ├── index.mdx
│   ├── introduction.mdx        # API overview
│   ├── base-url.mdx            # Endpoints and versioning
│   ├── rate-limiting.mdx       # Rate limits
│   └── errors.mdx              # Error codes
├── authentication/
│   ├── meta.json
│   ├── index.mdx
│   ├── api-keys.mdx
│   ├── oauth2.mdx
│   ├── jwt.mdx
│   └── scopes.mdx
├── rest/
│   ├── meta.json
│   ├── index.mdx
│   ├── [[...slug]].mdx         # Auto-generated from OpenAPI
├── graphql/
│   ├── meta.json
│   ├── index.mdx
│   ├── schema.mdx
│   ├── queries.mdx
│   ├── mutations.mdx
│   └── subscriptions.mdx
└── webhooks/
    ├── meta.json
    ├── index.mdx
    ├── events.mdx
    ├── payloads.mdx
    └── security.mdx
```

### 4.4 SDK Documentation

**Target Audience:** SDK users by language

**Content Categories:**

```
content/docs/sdk/
├── meta.json
├── index.mdx
├── python/
│   ├── meta.json
│   ├── index.mdx
│   ├── installation.mdx
│   ├── quickstart.mdx
│   ├── authentication.mdx
│   ├── items.mdx
│   ├── links.mdx
│   ├── analysis.mdx
│   ├── async.mdx
│   └── examples.mdx
├── javascript/
│   ├── meta.json
│   ├── index.mdx
│   ├── installation.mdx
│   ├── quickstart.mdx
│   ├── authentication.mdx
│   ├── items.mdx
│   ├── links.mdx
│   ├── analysis.mdx
│   ├── react-hooks.mdx
│   └── examples.mdx
└── go/
    ├── meta.json
    ├── index.mdx
    ├── installation.mdx
    ├── quickstart.mdx
    ├── authentication.mdx
    ├── items.mdx
    ├── links.mdx
    ├── analysis.mdx
    └── examples.mdx
```

### 4.5 Client Documentation

**Target Audience:** Users of specific TraceRTM clients

**Content Categories:**

```
content/docs/clients/
├── meta.json
├── index.mdx
├── web-ui/
│   ├── meta.json
│   ├── index.mdx
│   ├── navigation.mdx          # With screenshots
│   ├── dashboard.mdx
│   ├── matrix-view.mdx
│   ├── graph-view.mdx
│   ├── search.mdx
│   ├── reports.mdx
│   ├── settings.mdx
│   └── keyboard-shortcuts.mdx
├── cli/
│   ├── meta.json
│   ├── index.mdx
│   ├── installation.mdx
│   ├── configuration.mdx
│   ├── commands/
│   │   ├── meta.json
│   │   ├── index.mdx
│   │   ├── items.mdx
│   │   ├── links.mdx
│   │   ├── projects.mdx
│   │   ├── analyze.mdx
│   │   ├── export.mdx
│   │   └── sync.mdx
│   ├── scripting.mdx
│   └── tui.mdx
└── desktop/
    ├── meta.json
    ├── index.mdx
    ├── installation.mdx
    ├── features.mdx
    ├── offline-mode.mdx
    ├── sync.mdx
    └── preferences.mdx
```

---

## 5. Navigation Implementation

### 5.1 Combobox Navigation Component

Create `/docs-site/components/docs/DocTypeSelector.tsx`:

```tsx
'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Command } from 'cmdk';
import {
  Users, Code, Zap, Package, Monitor,
  ChevronDown, Check
} from 'lucide-react';
import { cn } from '@/lib/utils';

const DOC_TYPES = [
  {
    id: 'user',
    label: 'User Docs',
    description: 'For business users & analysts',
    icon: Users,
    basePath: '/docs/user',
  },
  {
    id: 'developer',
    label: 'Developer Docs',
    description: 'For engineers & contributors',
    icon: Code,
    basePath: '/docs/developer',
  },
  {
    id: 'api',
    label: 'API Reference',
    description: 'REST & GraphQL documentation',
    icon: Zap,
    basePath: '/docs/api',
  },
  {
    id: 'sdk',
    label: 'SDK Docs',
    description: 'Python, JavaScript, Go SDKs',
    icon: Package,
    basePath: '/docs/sdk',
  },
  {
    id: 'clients',
    label: 'Client Guides',
    description: 'Web UI, CLI, Desktop apps',
    icon: Monitor,
    basePath: '/docs/clients',
  },
] as const;

type DocType = typeof DOC_TYPES[number]['id'];

export function DocTypeSelector() {
  const [open, setOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  // Determine current doc type from URL
  const currentType = DOC_TYPES.find(
    (type) => pathname.startsWith(type.basePath)
  ) || DOC_TYPES[0];

  const handleSelect = (type: typeof DOC_TYPES[number]) => {
    setOpen(false);
    router.push(type.basePath);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 rounded-lg',
          'bg-muted hover:bg-muted/80 transition-colors',
          'text-sm font-medium w-full'
        )}
      >
        <currentType.icon className="w-4 h-4" />
        <span className="flex-1 text-left">{currentType.label}</span>
        <ChevronDown className={cn(
          'w-4 h-4 transition-transform',
          open && 'rotate-180'
        )} />
      </button>

      {open && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50">
          <Command className="rounded-lg border shadow-md bg-popover">
            <Command.List>
              {DOC_TYPES.map((type) => (
                <Command.Item
                  key={type.id}
                  value={type.id}
                  onSelect={() => handleSelect(type)}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 cursor-pointer',
                    'hover:bg-accent rounded-md mx-1 my-0.5',
                    currentType.id === type.id && 'bg-accent'
                  )}
                >
                  <type.icon className="w-4 h-4" />
                  <div className="flex-1">
                    <div className="font-medium">{type.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {type.description}
                    </div>
                  </div>
                  {currentType.id === type.id && (
                    <Check className="w-4 h-4 text-primary" />
                  )}
                </Command.Item>
              ))}
            </Command.List>
          </Command>
        </div>
      )}
    </div>
  );
}
```

### 5.2 Dynamic Sidebar

Create `/docs-site/components/docs/DocsSidebar.tsx`:

```tsx
'use client';

import { usePathname } from 'next/navigation';
import { DocsNavigation } from 'fumadocs-ui/components/docs-navigation';
import { DocTypeSelector } from './DocTypeSelector';
import {
  userDocs, developerDocs, apiDocs, sdkDocs, clientDocs
} from '@/lib/source';

function getSourceForPath(pathname: string) {
  if (pathname.startsWith('/docs/user')) return userDocs;
  if (pathname.startsWith('/docs/developer')) return developerDocs;
  if (pathname.startsWith('/docs/api')) return apiDocs;
  if (pathname.startsWith('/docs/sdk')) return sdkDocs;
  if (pathname.startsWith('/docs/clients')) return clientDocs;
  return userDocs; // Default
}

export function DocsSidebar() {
  const pathname = usePathname();
  const source = getSourceForPath(pathname);
  const tree = source.pageTree;

  return (
    <aside className="w-64 border-r h-screen sticky top-0 overflow-y-auto">
      <div className="p-4 border-b">
        <DocTypeSelector />
      </div>
      <DocsNavigation tree={tree} />
    </aside>
  );
}
```

### 5.3 Breadcrumb Navigation

Create `/docs-site/components/docs/DocsBreadcrumb.tsx`:

```tsx
'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/lib/utils';

const DOC_TYPE_LABELS: Record<string, string> = {
  user: 'User Docs',
  developer: 'Developer Docs',
  api: 'API Reference',
  sdk: 'SDK Docs',
  clients: 'Client Guides',
};

export function DocsBreadcrumb() {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  // Build breadcrumb items
  const items = segments.map((segment, index) => {
    const href = '/' + segments.slice(0, index + 1).join('/');
    let label = segment
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');

    // Handle doc type labels
    if (index === 1 && DOC_TYPE_LABELS[segment]) {
      label = DOC_TYPE_LABELS[segment];
    }

    return { href, label, isLast: index === segments.length - 1 };
  });

  return (
    <nav className="flex items-center gap-1 text-sm text-muted-foreground mb-4">
      <Link href="/" className="hover:text-foreground">
        <Home className="w-4 h-4" />
      </Link>
      {items.map((item, index) => (
        <div key={item.href} className="flex items-center gap-1">
          <ChevronRight className="w-4 h-4" />
          {item.isLast ? (
            <span className="text-foreground font-medium">{item.label}</span>
          ) : (
            <Link href={item.href} className="hover:text-foreground">
              {item.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}
```

### 5.4 Meta.json Configuration

Each directory needs a `meta.json` for navigation:

Example `/content/docs/user/meta.json`:

```json
{
  "title": "User Documentation",
  "description": "Documentation for business users and analysts",
  "icon": "Users",
  "pages": [
    "index",
    "---Getting Started---",
    "getting-started/...",
    "---Core Concepts---",
    "concepts/...",
    "---How-to Guides---",
    "guides/...",
    "---Use Cases---",
    "use-cases/...",
    "---Best Practices---",
    "best-practices/...",
    "---FAQ---",
    "faq/..."
  ]
}
```

---

## 6. MDX Components

### 6.1 Component Library

Create `/docs-site/components/mdx/index.tsx`:

```tsx
// Re-export all MDX components
export { Callout } from './Callout';
export { CodeBlock } from './CodeBlock';
export { CodeGroup } from './CodeGroup';
export { Tabs, Tab } from './Tabs';
export { Card, Cards } from './Card';
export { Steps, Step } from './Steps';
export { FileTree, Folder, File } from './FileTree';
export { APITable } from './APITable';
export { MermaidDiagram } from './MermaidDiagram';
export { Accordion, AccordionItem } from './Accordion';
export { Badge } from './Badge';
export { TypeTable } from './TypeTable';
export { ResponseExample } from './ResponseExample';
export { ScreenshotFrame } from './ScreenshotFrame';
export { CLICommand } from './CLICommand';
export { APIEndpoint } from './APIEndpoint';
```

### 6.2 Callout Component

Create `/docs-site/components/mdx/Callout.tsx`:

```tsx
import { ReactNode } from 'react';
import {
  Info, AlertTriangle, AlertCircle, Lightbulb, CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

type CalloutType = 'info' | 'warning' | 'error' | 'tip' | 'success' | 'note';

interface CalloutProps {
  type?: CalloutType;
  title?: string;
  children: ReactNode;
}

const calloutConfig = {
  info: {
    icon: Info,
    className: 'border-info bg-info/10 text-info-foreground',
    defaultTitle: 'Info',
  },
  warning: {
    icon: AlertTriangle,
    className: 'border-warning bg-warning/10 text-warning-foreground',
    defaultTitle: 'Warning',
  },
  error: {
    icon: AlertCircle,
    className: 'border-error bg-error/10 text-error-foreground',
    defaultTitle: 'Error',
  },
  tip: {
    icon: Lightbulb,
    className: 'border-primary bg-primary/10 text-primary-foreground',
    defaultTitle: 'Tip',
  },
  success: {
    icon: CheckCircle,
    className: 'border-success bg-success/10 text-success-foreground',
    defaultTitle: 'Success',
  },
  note: {
    icon: Info,
    className: 'border-muted bg-muted text-muted-foreground',
    defaultTitle: 'Note',
  },
};

export function Callout({ type = 'info', title, children }: CalloutProps) {
  const config = calloutConfig[type];
  const Icon = config.icon;

  return (
    <div className={cn(
      'my-4 rounded-lg border-l-4 p-4',
      config.className
    )}>
      <div className="flex items-start gap-3">
        <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          {title && (
            <div className="font-semibold mb-1">
              {title || config.defaultTitle}
            </div>
          )}
          <div className="text-sm">{children}</div>
        </div>
      </div>
    </div>
  );
}
```

### 6.3 Tabs Component

Create `/docs-site/components/mdx/Tabs.tsx`:

```tsx
'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface TabsContextValue {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TabsContext = createContext<TabsContextValue | null>(null);

interface TabsProps {
  defaultValue?: string;
  items?: string[];
  children: ReactNode;
}

export function Tabs({ defaultValue, items = [], children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultValue || items[0] || '');

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="my-4">
        <div className="flex border-b">
          {items.map((item) => (
            <button
              key={item}
              onClick={() => setActiveTab(item)}
              className={cn(
                'px-4 py-2 text-sm font-medium border-b-2 -mb-px',
                'transition-colors',
                activeTab === item
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {item}
            </button>
          ))}
        </div>
        <div className="mt-4">{children}</div>
      </div>
    </TabsContext.Provider>
  );
}

interface TabProps {
  value: string;
  children: ReactNode;
}

export function Tab({ value, children }: TabProps) {
  const context = useContext(TabsContext);
  if (!context) throw new Error('Tab must be used within Tabs');

  if (context.activeTab !== value) return null;

  return <div>{children}</div>;
}
```

### 6.4 Code Group Component

Create `/docs-site/components/mdx/CodeGroup.tsx`:

```tsx
'use client';

import { useState, ReactNode, Children, isValidElement } from 'react';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';

interface CodeGroupProps {
  children: ReactNode;
}

export function CodeGroup({ children }: CodeGroupProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const [copied, setCopied] = useState(false);

  const items = Children.toArray(children).filter(isValidElement);

  const tabs = items.map((child, index) => {
    const title = child.props['data-title'] ||
                  child.props.filename ||
                  `Tab ${index + 1}`;
    return { title, index };
  });

  const handleCopy = async () => {
    const codeElement = items[activeIndex];
    const code = codeElement?.props?.children?.props?.children || '';
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-lg border bg-muted/50 overflow-hidden">
      <div className="flex items-center justify-between border-b bg-muted/30">
        <div className="flex">
          {tabs.map(({ title, index }) => (
            <button
              key={index}
              onClick={() => setActiveIndex(index)}
              className={cn(
                'px-4 py-2 text-sm font-medium border-b-2 -mb-px',
                activeIndex === index
                  ? 'border-primary text-primary bg-background'
                  : 'border-transparent text-muted-foreground hover:text-foreground'
              )}
            >
              {title}
            </button>
          ))}
        </div>
        <button
          onClick={handleCopy}
          className="p-2 hover:bg-accent rounded-md mr-2"
          title="Copy code"
        >
          {copied ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>
      <div className="p-0">
        {items[activeIndex]}
      </div>
    </div>
  );
}
```

### 6.5 File Tree Component

Create `/docs-site/components/mdx/FileTree.tsx`:

```tsx
import { ReactNode } from 'react';
import { Folder as FolderIcon, File as FileIcon, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileTreeProps {
  children: ReactNode;
}

export function FileTree({ children }: FileTreeProps) {
  return (
    <div className="my-4 rounded-lg border bg-muted/50 p-4 font-mono text-sm">
      <ul className="space-y-1">{children}</ul>
    </div>
  );
}

interface FolderProps {
  name: string;
  open?: boolean;
  children?: ReactNode;
}

export function Folder({ name, open = true, children }: FolderProps) {
  return (
    <li>
      <div className="flex items-center gap-2 py-1">
        <ChevronRight className={cn(
          'w-4 h-4 text-muted-foreground transition-transform',
          open && 'rotate-90'
        )} />
        <FolderIcon className="w-4 h-4 text-primary" />
        <span className="font-medium">{name}</span>
      </div>
      {open && children && (
        <ul className="ml-6 border-l pl-2 space-y-1">{children}</ul>
      )}
    </li>
  );
}

interface FileProps {
  name: string;
  highlight?: boolean;
}

export function File({ name, highlight }: FileProps) {
  return (
    <li className="flex items-center gap-2 py-1 ml-6">
      <FileIcon className={cn(
        'w-4 h-4',
        highlight ? 'text-primary' : 'text-muted-foreground'
      )} />
      <span className={cn(highlight && 'text-primary font-medium')}>
        {name}
      </span>
    </li>
  );
}
```

### 6.6 API Response Example

Create `/docs-site/components/mdx/ResponseExample.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';

interface ResponseExampleProps {
  status: number;
  statusText?: string;
  headers?: Record<string, string>;
  body: object | string;
}

export function ResponseExample({
  status,
  statusText,
  headers,
  body
}: ResponseExampleProps) {
  const [copied, setCopied] = useState(false);

  const statusColor = status >= 200 && status < 300
    ? 'text-success'
    : status >= 400
      ? 'text-error'
      : 'text-warning';

  const jsonBody = typeof body === 'string' ? body : JSON.stringify(body, null, 2);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(jsonBody);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-lg border overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border-b">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">Response</span>
          <span className={cn('font-mono text-sm font-bold', statusColor)}>
            {status}
          </span>
          {statusText && (
            <span className="text-sm text-muted-foreground">{statusText}</span>
          )}
        </div>
        <button
          onClick={handleCopy}
          className="p-1 hover:bg-accent rounded"
        >
          {copied ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <Copy className="w-4 h-4" />
          )}
        </button>
      </div>
      {headers && (
        <div className="px-4 py-2 border-b bg-muted/30">
          <div className="text-xs text-muted-foreground mb-1">Headers</div>
          {Object.entries(headers).map(([key, value]) => (
            <div key={key} className="font-mono text-xs">
              <span className="text-primary">{key}</span>
              <span className="text-muted-foreground">: </span>
              <span>{value}</span>
            </div>
          ))}
        </div>
      )}
      <pre className="p-4 overflow-x-auto bg-background">
        <code className="text-sm font-mono">{jsonBody}</code>
      </pre>
    </div>
  );
}
```

### 6.7 CLI Command Component

Create `/docs-site/components/mdx/CLICommand.tsx`:

```tsx
'use client';

import { useState } from 'react';
import { Copy, Check, Terminal } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CLICommandProps {
  command: string;
  output?: string;
  description?: string;
}

export function CLICommand({ command, output, description }: CLICommandProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(command);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-4 rounded-lg border overflow-hidden">
      {description && (
        <div className="px-4 py-2 border-b bg-muted/30 text-sm">
          {description}
        </div>
      )}
      <div className="flex items-center gap-2 px-4 py-3 bg-zinc-900 text-zinc-100">
        <Terminal className="w-4 h-4 text-zinc-400" />
        <code className="flex-1 font-mono text-sm">{command}</code>
        <button
          onClick={handleCopy}
          className="p-1 hover:bg-zinc-800 rounded"
        >
          {copied ? (
            <Check className="w-4 h-4 text-success" />
          ) : (
            <Copy className="w-4 h-4 text-zinc-400" />
          )}
        </button>
      </div>
      {output && (
        <pre className="px-4 py-3 bg-zinc-800 text-zinc-300 overflow-x-auto">
          <code className="text-sm font-mono">{output}</code>
        </pre>
      )}
    </div>
  );
}
```

### 6.8 MDX Components Provider

Create `/docs-site/mdx-components.tsx`:

```tsx
import type { MDXComponents } from 'mdx/types';
import {
  Callout, CodeGroup, Tabs, Tab, Card, Cards,
  Steps, Step, FileTree, Folder, File, APITable,
  MermaidDiagram, Accordion, AccordionItem, Badge,
  TypeTable, ResponseExample, ScreenshotFrame,
  CLICommand, APIEndpoint
} from '@/components/mdx';
import Link from 'next/link';
import Image from 'next/image';

export function useMDXComponents(components: MDXComponents): MDXComponents {
  return {
    // Default element overrides
    a: ({ href, children }) => (
      <Link href={href || '#'} className="text-primary hover:underline">
        {children}
      </Link>
    ),
    img: ({ src, alt }) => (
      <Image
        src={src || ''}
        alt={alt || ''}
        width={800}
        height={400}
        className="rounded-lg border"
      />
    ),
    table: ({ children }) => (
      <div className="my-4 overflow-x-auto">
        <table className="w-full border-collapse">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border px-4 py-2 bg-muted text-left font-semibold">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="border px-4 py-2">{children}</td>
    ),

    // Custom components
    Callout,
    CodeGroup,
    Tabs,
    Tab,
    Card,
    Cards,
    Steps,
    Step,
    FileTree,
    Folder,
    File,
    APITable,
    MermaidDiagram,
    Accordion,
    AccordionItem,
    Badge,
    TypeTable,
    ResponseExample,
    ScreenshotFrame,
    CLICommand,
    APIEndpoint,

    ...components,
  };
}
```

---

## 7. File Structure

### 7.1 Complete Project Structure

```
docs-site/
├── app/
│   ├── layout.tsx                    # Root layout
│   ├── page.tsx                      # Landing page
│   ├── globals.css
│   ├── docs/
│   │   ├── layout.tsx                # Docs layout with sidebar
│   │   ├── [[...slug]]/
│   │   │   └── page.tsx              # Dynamic docs pages
│   │   ├── user/
│   │   │   └── [[...slug]]/
│   │   │       └── page.tsx
│   │   ├── developer/
│   │   │   └── [[...slug]]/
│   │   │       └── page.tsx
│   │   ├── api/
│   │   │   ├── [[...slug]]/
│   │   │   │   └── page.tsx
│   │   │   └── rest/
│   │   │       └── [...slug]/
│   │   │           └── page.tsx      # OpenAPI generated
│   │   ├── sdk/
│   │   │   └── [[...slug]]/
│   │   │       └── page.tsx
│   │   └── clients/
│   │       └── [[...slug]]/
│   │           └── page.tsx
│   └── api/
│       └── search/
│           └── route.ts              # Search API endpoint
├── components/
│   ├── docs/
│   │   ├── DocTypeSelector.tsx
│   │   ├── DocsSidebar.tsx
│   │   ├── DocsBreadcrumb.tsx
│   │   ├── DocsTableOfContents.tsx
│   │   ├── DocsPagination.tsx
│   │   ├── DocsSearch.tsx
│   │   └── DocsHeader.tsx
│   ├── mdx/
│   │   ├── index.tsx
│   │   ├── Callout.tsx
│   │   ├── Tabs.tsx
│   │   ├── CodeGroup.tsx
│   │   ├── FileTree.tsx
│   │   ├── Steps.tsx
│   │   ├── Card.tsx
│   │   ├── APITable.tsx
│   │   ├── MermaidDiagram.tsx
│   │   ├── ResponseExample.tsx
│   │   ├── CLICommand.tsx
│   │   ├── ScreenshotFrame.tsx
│   │   └── TypeTable.tsx
│   ├── ui/
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   └── ...
│   └── landing/
│       ├── hero-section.tsx
│       ├── features-section.tsx
│       └── quick-links.tsx
├── content/
│   └── docs/
│       ├── user/
│       │   ├── meta.json
│       │   ├── index.mdx
│       │   ├── getting-started/
│       │   ├── concepts/
│       │   ├── guides/
│       │   ├── use-cases/
│       │   ├── best-practices/
│       │   └── faq/
│       ├── developer/
│       │   ├── meta.json
│       │   ├── index.mdx
│       │   ├── setup/
│       │   ├── architecture/
│       │   ├── backend/
│       │   ├── frontend/
│       │   ├── cli/
│       │   ├── internals/
│       │   ├── deployment/
│       │   └── contributing/
│       ├── api/
│       │   ├── meta.json
│       │   ├── index.mdx
│       │   ├── overview/
│       │   ├── authentication/
│       │   ├── rest/                  # OpenAPI integration
│       │   ├── graphql/
│       │   └── webhooks/
│       ├── sdk/
│       │   ├── meta.json
│       │   ├── index.mdx
│       │   ├── python/
│       │   ├── javascript/
│       │   └── go/
│       └── clients/
│           ├── meta.json
│           ├── index.mdx
│           ├── web-ui/
│           ├── cli/
│           └── desktop/
├── lib/
│   ├── source.ts                     # Fumadocs source config
│   ├── utils.ts
│   └── search.ts                     # Search utilities
├── public/
│   ├── specs/
│   │   └── openapi.json              # API spec
│   ├── images/
│   │   ├── screenshots/
│   │   └── diagrams/
│   └── icons/
├── styles/
│   └── syntax-highlighting.css
├── mdx-components.tsx                # MDX component mappings
├── source.config.ts                  # Fumadocs MDX config
├── next.config.ts
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

---

## 8. Search and Indexing

### 8.1 Search Configuration

Create `/docs-site/lib/search.ts`:

```typescript
import { createSearchAPI } from 'fumadocs-core/search/server';
import { allDocs } from './source';

export const searchAPI = createSearchAPI('advanced', {
  indexes: allDocs.getPages().map((page) => ({
    title: page.data.title,
    description: page.data.description,
    url: page.url,
    id: page.url,
    structuredData: page.data.structuredData,
    // Add facets for filtering
    tag: page.data.audience || 'general',
    category: page.url.split('/')[2] || 'docs', // user, developer, api, etc.
  })),
});
```

### 8.2 Search API Route

Create `/docs-site/app/api/search/route.ts`:

```typescript
import { searchAPI } from '@/lib/search';

export const { GET } = searchAPI;
```

### 8.3 Search Component

Create `/docs-site/components/docs/DocsSearch.tsx`:

```tsx
'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { SearchDialog } from 'fumadocs-ui/components/dialog/search';
import { useDocsSearch } from 'fumadocs-core/search/client';

interface SearchResult {
  title: string;
  description?: string;
  url: string;
  tag?: string;
  category?: string;
}

export function DocsSearch() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const { search, query, setQuery } = useDocsSearch({
    type: 'fetch',
    api: '/api/search',
  });

  const handleSelect = useCallback((result: SearchResult) => {
    setOpen(false);
    router.push(result.url);
  }, [router]);

  return (
    <SearchDialog
      open={open}
      onOpenChange={setOpen}
      search={search}
      query={query}
      onQueryChange={setQuery}
      onResultSelect={handleSelect}
      footer={
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <kbd className="px-1.5 py-0.5 rounded bg-muted">Enter</kbd>
          <span>to select</span>
          <kbd className="px-1.5 py-0.5 rounded bg-muted">Esc</kbd>
          <span>to close</span>
        </div>
      }
    />
  );
}
```

### 8.4 Scoped Search by Doc Type

Enhance search to support filtering by doc type:

```tsx
// In DocsSearch component, add filter support
const { search, query, setQuery } = useDocsSearch({
  type: 'fetch',
  api: '/api/search',
  // Add current doc type as filter
  filters: currentDocType ? { category: currentDocType } : undefined,
});
```

---

## 9. Migration Strategy

### 9.1 Phase 1: Infrastructure Setup (Days 1-2)

**Tasks:**
1. Update `source.config.ts` with proper MDX configuration
2. Create `lib/source.ts` with multi-source setup
3. Update `next.config.ts` for Fumadocs integration
4. Install additional dependencies:
   ```bash
   npm install fumadocs-twoslash @shikijs/twoslash
   npm install remark-math rehype-katex
   ```
5. Create MDX component library
6. Set up mdx-components.tsx

**Validation:**
- MDX files render correctly
- Syntax highlighting works
- Components import without errors

### 9.2 Phase 2: Navigation System (Days 3-4)

**Tasks:**
1. Implement DocTypeSelector component
2. Create DocsSidebar with dynamic source switching
3. Build DocsBreadcrumb component
4. Create meta.json files for each section
5. Update docs layout to use new navigation

**Validation:**
- Combobox switches between doc types
- Sidebar shows correct navigation for each type
- Breadcrumbs reflect current location
- URLs route correctly

### 9.3 Phase 3: Content Migration (Days 5-8)

**Tasks:**
1. Restructure content directory:
   ```bash
   # Create new structure
   mkdir -p content/docs/{user,developer,api,sdk,clients}

   # Move and reorganize existing content
   mv content/docs/00-getting-started content/docs/user/getting-started
   mv content/docs/01-wiki content/docs/user/concepts
   # ... etc
   ```
2. Update frontmatter in all MDX files
3. Create index pages for each section
4. Add meta.json files
5. Fix internal links

**Content Priority:**
1. User docs (most viewed)
2. API reference (auto-generated)
3. Developer docs
4. SDK docs
5. Client guides

### 9.4 Phase 4: OpenAPI Integration (Days 9-10)

**Tasks:**
1. Copy OpenAPI spec to `/public/specs/openapi.json`
2. Configure fumadocs-openapi
3. Generate API reference pages
4. Create API overview pages
5. Add authentication documentation

**Validation:**
- API pages auto-generate from spec
- Try-it-out functionality works
- Code samples render correctly

### 9.5 Phase 5: Search Implementation (Days 11-12)

**Tasks:**
1. Set up search API route
2. Configure search indexing
3. Implement search UI
4. Add search filtering by doc type
5. Test search relevance

**Validation:**
- Search returns relevant results
- Filter by doc type works
- Keyboard navigation functional

### 9.6 Phase 6: Polish and Launch (Days 13-14)

**Tasks:**
1. Add screenshots to client guides
2. Create/update Mermaid diagrams
3. Add interactive demos where appropriate
4. Performance optimization
5. SEO optimization (meta tags, sitemap)
6. Deploy to staging
7. QA testing
8. Production deployment

---

## 10. Implementation Phases

### Priority Matrix

| Phase | Priority | Effort | Impact |
|-------|----------|--------|--------|
| Infrastructure | P0 | Medium | High |
| Navigation | P0 | Medium | High |
| Content Migration | P1 | High | High |
| OpenAPI Integration | P1 | Low | Medium |
| Search | P2 | Medium | Medium |
| Polish | P3 | Low | Low |

### Timeline (2 Week Sprint)

```
Week 1:
├── Day 1-2: Infrastructure Setup
│   ├── source.config.ts
│   ├── lib/source.ts
│   ├── MDX components
│   └── mdx-components.tsx
├── Day 3-4: Navigation System
│   ├── DocTypeSelector
│   ├── DocsSidebar
│   ├── DocsBreadcrumb
│   └── Layout updates
└── Day 5: Content Structure
    ├── Directory reorganization
    ├── meta.json creation
    └── Frontmatter updates

Week 2:
├── Day 6-8: Content Migration
│   ├── User docs
│   ├── Developer docs
│   └── Client guides
├── Day 9-10: API Documentation
│   ├── OpenAPI integration
│   ├── Authentication docs
│   └── SDK basics
├── Day 11-12: Search & Indexing
│   ├── Search API
│   ├── Search UI
│   └── Filtering
└── Day 13-14: Polish & Deploy
    ├── Screenshots
    ├── Diagrams
    ├── SEO
    └── Production deploy
```

### Success Metrics

1. **Navigation**
   - Time to find content < 30 seconds
   - Doc type switching < 1 click
   - Zero broken links

2. **Search**
   - Search latency < 100ms
   - Relevant results in top 5
   - Filter accuracy 100%

3. **Content**
   - 100% of pages have proper frontmatter
   - Code examples tested and working
   - API docs auto-generated

4. **Performance**
   - Lighthouse score > 90
   - First Contentful Paint < 1.5s
   - Time to Interactive < 3s

---

## Appendix A: Sample Content Templates

### A.1 User Guide Template

```mdx
---
title: "Creating Your First Traceability Matrix"
description: "Learn how to create and manage a traceability matrix in TraceRTM"
keywords:
  - traceability matrix
  - requirements
  - getting started
audience: user
difficulty: beginner
toc: true
updated: "2025-01-15"
---

# Creating Your First Traceability Matrix

<Callout type="tip">
This guide takes about 10 minutes to complete and will give you a working
traceability matrix.
</Callout>

## Prerequisites

Before you begin, make sure you have:

- [ ] A TraceRTM account
- [ ] At least one project created
- [ ] Basic understanding of requirements

## Step 1: Navigate to Matrix View

<Steps>
<Step>
Open your project from the dashboard
</Step>
<Step>
Click on **Matrix** in the left sidebar
</Step>
<Step>
Select **Create New Matrix** from the toolbar
</Step>
</Steps>

<ScreenshotFrame src="/images/screenshots/matrix-view.png" alt="Matrix View">
The matrix view showing requirements and their relationships
</ScreenshotFrame>

## Step 2: Add Requirements

<Tabs items={["Web UI", "CLI", "API"]}>
<Tab value="Web UI">
Click the **+ Add Item** button and fill in the required fields.
</Tab>
<Tab value="CLI">
<CLICommand
  command="tracertm item create --type requirement --title 'User Authentication'"
  output="Created item REQ-001: User Authentication"
/>
</Tab>
<Tab value="API">
```bash
curl -X POST https://api.tracertm.com/v1/items \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"type": "requirement", "title": "User Authentication"}'
```
</Tab>
</Tabs>

## Next Steps

- [Creating relationships between items](/docs/user/guides/linking-items)
- [Generating compliance reports](/docs/user/guides/reports)
- [Best practices for matrix organization](/docs/user/best-practices/matrix-organization)
```

### A.2 API Reference Template

```mdx
---
title: "Create Item"
description: "Create a new item in a project"
audience: api
method: POST
endpoint: /api/v1/items
---

# Create Item

Create a new requirement, test case, or other item type in a project.

## Endpoint

```
POST /api/v1/items
```

## Authentication

<Callout type="info">
This endpoint requires authentication via API key or OAuth token.
</Callout>

## Request

### Headers

<TypeTable
  type={{
    "Authorization": {
      type: "string",
      required: true,
      description: "Bearer token or API key"
    },
    "Content-Type": {
      type: "string",
      default: "application/json"
    },
  }}
/>

### Body Parameters

<TypeTable
  type={{
    "project_id": {
      type: "string (UUID)",
      required: true,
      description: "ID of the project"
    },
    "type": {
      type: "string",
      required: true,
      description: "Item type: requirement, test_case, user_story, etc."
    },
    "title": {
      type: "string",
      required: true,
      description: "Item title (max 200 characters)"
    },
    "description": {
      type: "string",
      description: "Detailed description (markdown supported)"
    },
    "metadata": {
      type: "object",
      description: "Custom fields as key-value pairs"
    },
  }}
/>

### Example Request

<CodeGroup>
```bash title="cURL"
curl -X POST https://api.tracertm.com/v1/items \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "requirement",
    "title": "User Authentication",
    "description": "Users must be able to authenticate via email/password"
  }'
```
```python title="Python SDK"
from tracertm import Client

client = Client(api_key="your-api-key")
item = client.items.create(
    project_id="550e8400-e29b-41d4-a716-446655440000",
    type="requirement",
    title="User Authentication",
    description="Users must be able to authenticate via email/password"
)
```
```typescript title="TypeScript SDK"
import { TraceRTM } from '@tracertm/sdk';

const client = new TraceRTM({ apiKey: 'your-api-key' });
const item = await client.items.create({
  projectId: '550e8400-e29b-41d4-a716-446655440000',
  type: 'requirement',
  title: 'User Authentication',
  description: 'Users must be able to authenticate via email/password'
});
```
</CodeGroup>

## Response

### Success Response

<ResponseExample
  status={201}
  statusText="Created"
  headers={{
    "Content-Type": "application/json",
    "X-Request-Id": "req_abc123"
  }}
  body={{
    "id": "item_xyz789",
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "type": "requirement",
    "title": "User Authentication",
    "description": "Users must be able to authenticate via email/password",
    "status": "draft",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }}
/>

### Error Responses

<Tabs items={["400", "401", "403", "404"]}>
<Tab value="400">
<ResponseExample
  status={400}
  body={{
    "error": "validation_error",
    "message": "Title is required",
    "details": [
      { "field": "title", "message": "cannot be empty" }
    ]
  }}
/>
</Tab>
<Tab value="401">
<ResponseExample
  status={401}
  body={{
    "error": "unauthorized",
    "message": "Invalid or expired token"
  }}
/>
</Tab>
<Tab value="403">
<ResponseExample
  status={403}
  body={{
    "error": "forbidden",
    "message": "You do not have permission to create items in this project"
  }}
/>
</Tab>
<Tab value="404">
<ResponseExample
  status={404}
  body={{
    "error": "not_found",
    "message": "Project not found"
  }}
/>
</Tab>
</Tabs>
```

### A.3 CLI Command Reference Template

```mdx
---
title: "tracertm item"
description: "Manage items (requirements, test cases, etc.)"
audience: client
client: cli
---

# tracertm item

Manage items including requirements, test cases, and other artifact types.

## Synopsis

```bash
tracertm item <subcommand> [options]
```

## Subcommands

| Command | Description |
|---------|-------------|
| `list` | List items in a project |
| `create` | Create a new item |
| `get` | Get details of an item |
| `update` | Update an existing item |
| `delete` | Delete an item |
| `link` | Create a link between items |

## tracertm item list

List items in the current project.

<CLICommand
  command="tracertm item list"
  description="List all items in the current project"
  output={`ID         TYPE          TITLE                    STATUS
REQ-001    requirement   User Authentication      approved
REQ-002    requirement   Data Export              draft
TC-001     test_case     Login Flow Test          passed
TC-002     test_case     Export CSV Test          pending`}
/>

### Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--type` | `-t` | Filter by item type | all |
| `--status` | `-s` | Filter by status | all |
| `--format` | `-f` | Output format (table, json, csv) | table |
| `--limit` | `-l` | Maximum items to return | 50 |

### Examples

<CodeGroup>
```bash title="Filter by type"
tracertm item list --type requirement
```
```bash title="JSON output"
tracertm item list --format json
```
```bash title="Combine filters"
tracertm item list --type test_case --status pending --limit 10
```
</CodeGroup>

## tracertm item create

Create a new item.

<CLICommand
  command='tracertm item create --type requirement --title "Password Reset"'
  description="Create a new requirement"
  output="Created item REQ-003: Password Reset"
/>

### Required Options

| Option | Short | Description |
|--------|-------|-------------|
| `--type` | `-t` | Item type (requirement, test_case, user_story, etc.) |
| `--title` | n/a | Item title |

### Optional Options

| Option | Short | Description |
|--------|-------|-------------|
| `--description` | `-d` | Item description |
| `--priority` | `-p` | Priority level (low, medium, high, critical) |
| `--assignee` | `-a` | Assign to user |
| `--labels` | `-l` | Comma-separated labels |
| `--parent` | n/a | Parent item ID |

### Interactive Mode

Run without options for interactive prompts:

<CLICommand
  command="tracertm item create"
  output={`? Item type: requirement
? Title: Password Reset
? Description: Users should be able to reset their password via email
? Priority: medium
? Labels (comma-separated): auth, security

Created item REQ-003: Password Reset`}
/>

## See Also

- [tracertm link](/docs/clients/cli/commands/link) - Manage item relationships
- [tracertm project](/docs/clients/cli/commands/project) - Manage projects
- [tracertm analyze](/docs/clients/cli/commands/analyze) - Impact analysis
```

---

## Appendix B: Package Dependencies

### Required Dependencies

```json
{
  "dependencies": {
    "fumadocs-core": "^16.2.1",
    "fumadocs-mdx": "^14.0.4",
    "fumadocs-ui": "^16.2.1",
    "fumadocs-openapi": "^10.1.0",
    "fumadocs-twoslash": "^2.0.0",
    "@shikijs/twoslash": "^1.0.0",
    "cmdk": "^1.1.1",
    "remark-gfm": "^4.0.1",
    "remark-math": "^6.0.0",
    "rehype-katex": "^7.0.0",
    "mermaid": "^11.12.1"
  }
}
```

---

## Appendix C: Configuration Files

### C.1 tsconfig.json additions

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*", "./*"],
      "@/components/*": ["./components/*"],
      "@/lib/*": ["./lib/*"],
      "@/.source": ["./.source"]
    }
  }
}
```

### C.2 .source generation

Fumadocs MDX generates `.source` directory automatically. Add to `.gitignore`:

```
.source/
```

---

*This document was prepared as part of the TraceRTM documentation architecture planning initiative.*

*Last Updated: 2025-01-15*
