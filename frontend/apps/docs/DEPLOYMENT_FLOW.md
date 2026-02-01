# Documentation Deployment Flow

Visual guide to the deployment process for TraceRTM documentation.

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TraceRTM Repository                       │
│                                                                  │
│  ┌──────────────┐        ┌──────────────┐                      │
│  │   Backend    │        │   Frontend   │                      │
│  │  (Go/Swag)   │        │  apps/docs   │                      │
│  │              │        │  (Next.js)   │                      │
│  └──────┬───────┘        └──────┬───────┘                      │
│         │                       │                               │
│         │ OpenAPI Spec          │ MDX Content                   │
│         │ Generation            │ Components                    │
│         │                       │ Configuration                 │
└─────────┼───────────────────────┼───────────────────────────────┘
          │                       │
          │                       │
          ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Actions CI/CD                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job 1: Generate OpenAPI                                 │  │
│  │  - Setup Go environment                                  │  │
│  │  - Install swag                                          │  │
│  │  - Generate swagger.json/yaml                           │  │
│  │  - Validate spec                                         │  │
│  │  - Upload artifact                                       │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job 2: Build Docs                                       │  │
│  │  - Setup Bun                                             │  │
│  │  - Download OpenAPI spec                                 │  │
│  │  - Install dependencies                                  │  │
│  │  - Build Next.js site                                    │  │
│  │  - Type check                                            │  │
│  │  - Upload build artifact                                 │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job 3a: Deploy Preview (PRs)                           │  │
│  │  - Pull Vercel environment                              │  │
│  │  - Build with Vercel                                     │  │
│  │  - Deploy to preview                                     │  │
│  │  - Comment PR with URL                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job 3b: Deploy Production (Main)                       │  │
│  │  - Pull Vercel production env                            │  │
│  │  - Build with Vercel                                     │  │
│  │  - Deploy to production                                  │  │
│  │  - Create deployment summary                             │  │
│  └────────────────────┬─────────────────────────────────────┘  │
│                       │                                          │
│                       ▼                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Job 4: Validate Deployment                             │  │
│  │  - Wait for propagation                                  │  │
│  │  - Check site accessibility                              │  │
│  │  - Verify OpenAPI spec                                   │  │
│  │  - Test critical pages                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Vercel Platform                          │
│                                                                  │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  Preview           │         │  Production        │         │
│  │  Deployments       │         │  Deployment        │         │
│  │                    │         │                    │         │
│  │  • Unique URL      │         │  • Custom Domain   │         │
│  │  • Per PR          │         │  • SSL/HTTPS       │         │
│  │  • Auto cleanup    │         │  • CDN             │         │
│  └────────────────────┘         └────────────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Public Endpoints                            │
│                                                                  │
│  Preview:     https://docs-xxx.vercel.app                       │
│  Production:  https://docs.tracertm.com                         │
│                                                                  │
│  Content:                                                        │
│  • /                    → Homepage                              │
│  • /docs                → Documentation                         │
│  • /api-reference       → API Reference                         │
│  • /api/openapi.json    → OpenAPI Spec (JSON)                  │
│  • /api/openapi.yaml    → OpenAPI Spec (YAML)                  │
└─────────────────────────────────────────────────────────────────┘
```

## Deployment Triggers

### Automatic Triggers

```
Pull Request (PR)
├── Changes to: frontend/apps/docs/**
├── Changes to: docs/**
├── Changes to: backend/**/*.go
└── Workflow: docs-deploy.yml
    └── Result: Preview deployment
        └── URL posted in PR comment

Push to Main
├── Changes to: frontend/apps/docs/**
├── Changes to: docs/**
├── Changes to: backend/**/*.go
└── Workflow: docs-deploy.yml
    └── Result: Production deployment
        └── URL: https://docs.tracertm.com
```

### Manual Triggers

```
GitHub Actions UI
├── Select: "Deploy Documentation Site"
├── Click: "Run workflow"
├── Choose: Environment (preview/production)
└── Result: Manual deployment
```

## Manual Deployment Flow

### Local Deployment

```
Developer Machine
    │
    ├── Option 1: Quick Deploy Scripts
    │   ├── bun run deploy:preview
    │   └── bun run deploy:prod
    │
    ├── Option 2: Full Deploy Script
    │   ├── bash scripts/deploy.sh preview
    │   └── bash scripts/deploy.sh production
    │
    └── Option 3: Direct Vercel CLI
        ├── vercel (preview)
        └── vercel --prod (production)
```

### Deploy Script Flow

```
Start: ./deploy.sh [preview|production]
    │
    ├── 1. Check Requirements
    │   ├── ✓ Bun installed?
    │   ├── ✓ Vercel CLI installed?
    │   └── ✓ Go installed? (for OpenAPI)
    │
    ├── 2. Generate OpenAPI Spec
    │   ├── Install swag
    │   ├── Generate from backend
    │   └── Copy to docs/public/api/
    │
    ├── 3. Install Dependencies
    │   └── bun install --frozen-lockfile
    │
    ├── 4. Build Site
    │   └── bun run build
    │
    ├── 5. Deploy to Vercel
    │   ├── Pull environment config
    │   ├── Build with Vercel
    │   └── Deploy (preview or prod)
    │
    ├── 6. Validate Deployment
    │   ├── Wait for propagation
    │   └── Check accessibility
    │
    └── 7. Display Summary
        ├── Environment
        ├── Deployment URL
        └── Status
```

## Environment Flow

### Environment Variables

```
Local Development (.env.local)
    │
    ├── NEXT_PUBLIC_API_URL=http://localhost:8000
    └── NEXT_PUBLIC_DOCS_URL=http://localhost:3001
            │
            ▼
Preview Deployment (Vercel Preview)
    │
    ├── NEXT_PUBLIC_API_URL=https://api.tracertm.com
    ├── NEXT_PUBLIC_DOCS_URL=https://docs-xxx.vercel.app
    └── NEXT_TELEMETRY_DISABLED=1
            │
            ▼
Production Deployment (Vercel Production)
    │
    ├── NEXT_PUBLIC_API_URL=https://api.tracertm.com
    ├── NEXT_PUBLIC_DOCS_URL=https://docs.tracertm.com
    └── NEXT_TELEMETRY_DISABLED=1
```

## OpenAPI Integration Flow

```
Backend (Go)
    │
    ├── Swagger annotations in code
    │   ├── @Summary, @Description
    │   ├── @Tags, @Accept, @Produce
    │   ├── @Param, @Success, @Failure
    │   └── @Router definitions
    │
    ├── swag init command
    │   └── Generates: backend/docs/swagger.{json,yaml}
    │
    ├── Copy to docs site
    │   └── frontend/apps/docs/public/api/openapi.{json,yaml}
    │
    └── Fumadocs OpenAPI integration
        ├── Parses spec
        ├── Generates API reference
        └── Creates interactive docs
            │
            ▼
Public API Reference
    ├── /api-reference → Interactive docs
    ├── /api/openapi.json → Raw spec (JSON)
    └── /api/openapi.yaml → Raw spec (YAML)
```

## Validation Flow

```
Post-Deployment Validation
    │
    ├── Automated Checks (CI/CD)
    │   ├── Check: Homepage (200 OK)
    │   ├── Check: Docs page (200 OK)
    │   ├── Check: API reference (200 OK)
    │   ├── Check: OpenAPI JSON (200 OK)
    │   └── Check: OpenAPI YAML (200 OK)
    │
    ├── Manual Checks (Developer)
    │   ├── Run: ./validate-deployment.sh
    │   ├── Test: Navigation
    │   ├── Test: Search
    │   ├── Test: Links
    │   └── Test: Examples
    │
    └── Performance Checks
        ├── Response time < 2s
        ├── Lighthouse score > 90
        └── No console errors
```

## Error Handling Flow

```
Deployment Failure
    │
    ├── 1. Check Build Logs
    │   ├── GitHub Actions logs
    │   └── Vercel deployment logs
    │
    ├── 2. Identify Issue
    │   ├── TypeScript errors?
    │   ├── Build failure?
    │   ├── Vercel auth issue?
    │   └── OpenAPI generation failed?
    │
    ├── 3. Fix Issue
    │   ├── Fix code locally
    │   ├── Test build locally
    │   └── Test deployment locally
    │
    ├── 4. Redeploy
    │   ├── Push fix to branch
    │   └── Wait for CI/CD
    │
    └── 5. Rollback (if needed)
        ├── Option 1: Vercel dashboard
        │   └── Promote previous deployment
        │
        └── Option 2: Git revert
            └── Revert commit and push
```

## Monitoring Flow

```
Continuous Monitoring
    │
    ├── Immediate (First Hour)
    │   ├── Vercel Analytics
    │   ├── Error rates
    │   └── Response times
    │
    ├── Daily
    │   ├── Check analytics
    │   ├── Review errors
    │   └── Check uptime
    │
    └── Periodic
        ├── Performance audits
        ├── Lighthouse scores
        └── Dependency updates
```

## Rollback Flow

```
Rollback Required
    │
    ├── Quick Rollback (Vercel Dashboard)
    │   ├── 1. Go to Deployments
    │   ├── 2. Find last working deployment
    │   ├── 3. Click "Promote to Production"
    │   └── 4. Verify rollback
    │
    ├── Git Rollback
    │   ├── 1. Find working commit
    │   ├── 2. git revert <commit>
    │   ├── 3. git push origin main
    │   └── 4. Wait for auto-deploy
    │
    └── Emergency Rollback
        ├── 1. vercel --prod --force
        └── 2. Specify previous deployment
```

## Summary

The deployment flow is designed to be:

- **Automated**: CI/CD handles most deployments
- **Validated**: Every deployment is tested
- **Secure**: Tokens and secrets properly managed
- **Fast**: Parallel jobs and caching optimize speed
- **Reliable**: Multiple validation steps ensure quality
- **Recoverable**: Easy rollback mechanisms
- **Transparent**: Clear logs and summaries

## Quick Commands Reference

```bash
# Preview deployment
bun run deploy:preview

# Production deployment
bun run deploy:prod

# Validate deployment
bash scripts/validate-deployment.sh https://docs.tracertm.com

# Sync OpenAPI
bun run openapi:sync

# Test build locally
bun run build

# Type check
bun run typecheck

# Performance test
bun run test:performance
```

## Documentation References

- [Deployment Guide](./DEPLOYMENT.md) - Complete deployment documentation
- [GitHub Actions Setup](./GITHUB_ACTIONS_SETUP.md) - CI/CD configuration
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Pre/post deployment checks
- [Quick Start](./QUICK_START.md) - Getting started guide

---

Last updated: 2026-01-30
