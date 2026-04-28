# Phase 1: Foundation & Setup - Implementation Guide

**Date**: 2025-11-22
**Duration**: 2-3 weeks
**Scope**: Initialize monorepo, setup all apps, configure external services
**Package Manager**: Bun

---

## TASK 1.1: Initialize Monorepo (Turborepo + Bun)

### Step 1: Create Project Directory

```bash
mkdir tracertm
cd tracertm
git init
```

### Step 2: Initialize Bun Workspaces

```bash
# Create bunfig.toml
cat > bunfig.toml << 'EOF'
[install]
# Bun workspaces configuration
root_dir = "."

[build]
root = "."
EOF

# Create root package.json
cat > package.json << 'EOF'
{
  "name": "tracertm",
  "version": "0.1.0",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "turbo run dev --parallel",
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check",
    "clean": "turbo run clean && rm -rf node_modules"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
EOF

# Install Bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies with Bun
bun install
```

### Step 3: Initialize Turborepo

```bash
# Create turbo.json
cat > turbo.json << 'EOF'
{
  "tasks": {
    "build": {
      "outputs": ["dist/**", ".next/**"],
      "cache": false
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "outputs": ["coverage/**"],
      "cache": false
    },
    "lint": {
      "outputs": [".eslintcache"],
      "cache": true
    },
    "type-check": {
      "cache": true
    }
  }
}
EOF
```

### Step 4: Create Directory Structure

```bash
mkdir -p apps/{web,api,docs,email,storybook}
mkdir -p packages/{ui,types,config,scripts}
```

---

## TASK 1.2: Create Shared Packages

### packages/types

```bash
cd packages/types
cat > package.json << 'EOF'
{
  "name": "@tracertm/types",
  "version": "0.1.0",
  "main": "index.ts",
  "types": "index.ts"
}
EOF

mkdir -p src
cat > src/index.ts << 'EOF'
// Domain types
export interface Item {
  id: string;
  title: string;
  type: ItemType;
  description?: string;
  status: ItemStatus;
  createdAt: Date;
  updatedAt: Date;
}

export enum ItemType {
  REQUIREMENT = "REQUIREMENT",
  DESIGN = "DESIGN",
  IMPLEMENTATION = "IMPLEMENTATION",
  TEST = "TEST",
  DEPLOYMENT = "DEPLOYMENT"
}

export enum ItemStatus {
  DRAFT = "DRAFT",
  ACTIVE = "ACTIVE",
  ARCHIVED = "ARCHIVED"
}

export interface Link {
  id: string;
  type: LinkType;
  source: string;
  target: string;
  metadata?: Record<string, any>;
}

export enum LinkType {
  DEPENDS_ON = "DEPENDS_ON",
  BLOCKS = "BLOCKS",
  RELATES_TO = "RELATES_TO",
  IMPLEMENTS = "IMPLEMENTS"
}

export interface Agent {
  id: string;
  name: string;
  status: AgentStatus;
  currentItem?: string;
  lastSeen: Date;
}

export enum AgentStatus {
  IDLE = "IDLE",
  WORKING = "WORKING",
  ERROR = "ERROR"
}
EOF
```

### packages/ui

```bash
cd packages/ui
cat > package.json << 'EOF'
{
  "name": "@tracertm/ui",
  "version": "0.1.0",
  "main": "index.ts",
  "types": "index.ts",
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@radix-ui/react-dialog": "^1.1.0",
    "@radix-ui/react-dropdown-menu": "^2.0.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.0.0",
    "tailwind-merge": "^2.0.0"
  }
}
EOF

mkdir -p src/components
cat > src/index.ts << 'EOF'
export * from './components'
EOF
```

### packages/config

```bash
cd packages/config
cat > package.json << 'EOF'
{
  "name": "@tracertm/config",
  "version": "0.1.0"
}
EOF

mkdir -p src
cat > src/tailwind.config.ts << 'EOF'
import type { Config } from 'tailwindcss'

export default {
  content: [
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config
EOF
```

---

## TASK 1.3: Setup Frontend App (Vite + React)

```bash
cd apps/web

# Create Vite project
npm create vite@latest . -- --template react-ts

# Install dependencies
pnpm install

# Add additional dependencies
pnpm add \
  react-router-dom \
  @tanstack/react-query \
  @tanstack/react-table \
  @apollo/client \
  graphql \
  zod \
  react-hook-form \
  react-flow-renderer \
  cytoscape \
  monaco-editor \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  tailwindcss \
  postcss \
  autoprefixer

# Add dev dependencies
pnpm add -D \
  @types/react \
  @types/react-dom \
  typescript \
  vite \
  @vitejs/plugin-react \
  tailwindcss \
  postcss \
  autoprefixer
```

---

## TASK 1.4: Setup Backend App (Go + Echo)

```bash
cd apps/api

# Initialize Go module
go mod init github.com/kooshapari/tracertm/api

# Create project structure
mkdir -p cmd/server internal/{handler,service,repository,model} pkg/{config,logger}

# Create main.go
cat > cmd/server/main.go << 'EOF'
package main

import (
  "github.com/labstack/echo/v4"
  "github.com/labstack/echo/v4/middleware"
)

func main() {
  e := echo.New()
  
  e.Use(middleware.Logger())
  e.Use(middleware.Recover())
  
  e.GET("/health", func(c echo.Context) error {
    return c.JSON(200, map[string]string{"status": "ok"})
  })
  
  e.Logger.Fatal(e.Start(":8080"))
}
EOF

# Add dependencies
go get github.com/labstack/echo/v4
go get github.com/99designs/gqlgen
go get github.com/lib/pq
go get github.com/joho/godotenv
```

---

## TASK 1.5: Setup Documentation App

```bash
cd apps/docs

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind

# Install Nextra
pnpm add nextra nextra-theme-docs

# Create docs structure
mkdir -p pages/{getting-started,api,architecture}
```

---

## TASK 1.6: Setup Email Templates App

```bash
cd apps/email

# Create Next.js app
npx create-next-app@latest . --typescript

# Install React Email
pnpm add react-email @react-email/components

# Create email templates
mkdir -p emails
cat > emails/invite.tsx << 'EOF'
import { Html, Body, Head, Hr, Container, Preview, Section, Text } from '@react-email/components';

export default function InviteEmail({ inviteUrl }: { inviteUrl: string }) {
  return (
    <Html>
      <Head />
      <Preview>You're invited to TraceRTM</Preview>
      <Body style={main}>
        <Container style={container}>
          <Text style={heading}>You're invited to TraceRTM</Text>
          <Text style={paragraph}>Click the link below to accept your invite:</Text>
          <Section style={buttonContainer}>
            <a href={inviteUrl} style={button}>Accept Invite</a>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}
EOF
```

---

## TASK 1.7: Setup Storybook

```bash
cd apps/storybook

# Initialize Storybook
npx storybook@latest init --builder vite

# Create stories directory
mkdir -p stories

# Create example story
cat > stories/Button.stories.ts << 'EOF'
import type { Meta, StoryObj } from '@storybook/react';

const meta = {
  title: 'Components/Button',
  component: Button,
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: {
    children: 'Click me',
  },
};
EOF
```

---

## TASK 1.8: Configure Database (Supabase)

### Step 1: Create Supabase Project

```bash
# Go to https://supabase.com
# Create new project
# Save credentials to .env.local
```

### Step 2: Create Database Schema

```sql
-- Items table
CREATE TABLE items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  type TEXT NOT NULL,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'DRAFT',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Links table
CREATE TABLE links (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL,
  source_id UUID NOT NULL REFERENCES items(id),
  target_id UUID NOT NULL REFERENCES items(id),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agents table
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'IDLE',
  current_item_id UUID REFERENCES items(id),
  last_seen TIMESTAMP DEFAULT NOW()
);

-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embeddings column
ALTER TABLE items ADD COLUMN embedding vector(1536);
```

---

## TASK 1.9: Configure External Services

### WorkOS

```bash
# Create .env.local
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=project_...
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

### Upstash

```bash
# Redis
UPSTASH_REDIS_URL=redis://...

# Kafka
UPSTASH_KAFKA_URL=kafka://...
UPSTASH_KAFKA_USERNAME=...
UPSTASH_KAFKA_PASSWORD=...
```

### Inngest

```bash
INNGEST_EVENT_KEY=...
INNGEST_SIGNING_KEY=...
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly apps create tracertm
```

---

## TASK 1.10: Setup CI/CD Pipeline

### GitHub Actions

```bash
mkdir -p .github/workflows

cat > .github/workflows/test.yml << 'EOF'
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
          cache: 'pnpm'
      - run: pnpm install
      - run: pnpm run lint
      - run: pnpm run type-check
      - run: pnpm run test
EOF
```

---

## DELIVERABLES

✅ Monorepo structure (Turborepo + pnpm)
✅ Shared packages (types, ui, config)
✅ Frontend app (Vite + React)
✅ Backend app (Go + Echo)
✅ Documentation app
✅ Email templates app
✅ Storybook
✅ Database (Supabase)
✅ External services configured
✅ CI/CD pipeline


