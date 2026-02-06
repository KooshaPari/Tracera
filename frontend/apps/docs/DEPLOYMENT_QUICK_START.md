# Deployment Quick Start Guide

Get the TraceRTM documentation site deployed in minutes.

## Prerequisites (5 minutes)

1. **Install Bun** (if not already installed):

   ```bash
   curl -fsSL https://bun.sh/install | bash
   ```

2. **Install Vercel CLI**:

   ```bash
   bun install --global vercel@latest
   ```

3. **Login to Vercel**:
   ```bash
   vercel login
   ```

## First-Time Setup (10 minutes)

### 1. Link Vercel Project

```bash
cd frontend/apps/docs
vercel link
```

Follow the prompts to create or link a project.

### 2. Get Vercel Credentials

```bash
# View project configuration
cat .vercel/project.json
```

You'll see:

```json
{
  "orgId": "team_xxxxx",
  "projectId": "prj_xxxxx"
}
```

### 3. Configure GitHub Secrets

Go to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:

| Secret Name              | Value      | Where to Get                                                   |
| ------------------------ | ---------- | -------------------------------------------------------------- |
| `VERCEL_TOKEN`           | your_token | [vercel.com/account/tokens](https://vercel.com/account/tokens) |
| `VERCEL_ORG_ID`          | team_xxxxx | From `.vercel/project.json`                                    |
| `VERCEL_DOCS_PROJECT_ID` | prj_xxxxx  | From `.vercel/project.json`                                    |

### 4. Configure Environment (Optional)

Create `.env.local`:

```bash
cp .env.example .env.local
```

Edit values as needed.

## Deploy Now! (2 minutes)

### Option 1: Preview Deployment

```bash
bun run deploy:preview
```

You'll get a preview URL like: `https://docs-xxx.vercel.app`

### Option 2: Production Deployment

```bash
bun run deploy:prod
```

Site will be available at your configured domain.

### Option 3: Automatic Deployment

Just push to GitHub:

```bash
# For preview
git checkout -b my-feature
git add .
git commit -m "Update docs"
git push origin my-feature
# Create PR → Automatic preview deployment

# For production
git checkout main
git pull
git merge my-feature
git push origin main
# Automatic production deployment
```

## Verify Deployment (1 minute)

```bash
# Validate everything works
bash scripts/validate-deployment.sh https://docs.tracertm.com
```

You should see all green checkmarks ✓

## Custom Domain Setup (Optional, 15 minutes)

### 1. Add Domain in Vercel

1. Go to your project in [Vercel Dashboard](https://vercel.com)
2. Settings → Domains
3. Add `docs.tracertm.com`

### 2. Configure DNS

Add this record to your DNS provider:

```
Type: A
Name: docs
Value: 76.76.21.21
```

Or use CNAME:

```
Type: CNAME
Name: docs
Value: cname.vercel-dns.com
```

### 3. Wait for SSL

Vercel automatically provisions SSL. Wait up to 48 hours for DNS propagation.

### 4. Test

```bash
curl -I https://docs.tracertm.com
```

Should return `HTTP/2 200`

## Common Commands

```bash
# Development
bun run dev                    # Start dev server (localhost:3001)

# Building
bun run build                  # Build for production
bun run typecheck              # Check TypeScript

# OpenAPI
bun run openapi:sync           # Sync spec from backend

# Deployment
bun run deploy:preview         # Deploy preview
bun run deploy:prod            # Deploy production

# Validation
bash scripts/validate-deployment.sh [url]

# Testing
bun run test:e2e               # E2E tests
bun run test:performance       # Performance tests
```

## Troubleshooting

### Build Fails

```bash
# Check TypeScript errors
bun run typecheck

# Check for syntax errors
bun run lint

# Test build locally
bun run build
```

### Deployment Fails

```bash
# Check Vercel connection
vercel whoami

# Check project link
vercel ls

# Try manual deployment
vercel --prod
```

### OpenAPI Missing

```bash
# Sync from backend
bun run openapi:sync

# Verify file exists
ls -la public/api/openapi.json
```

## What Happens in Each Deployment?

### Preview Deployment

1. Generates OpenAPI spec from backend
2. Builds documentation site
3. Deploys to unique preview URL
4. Posts URL in PR comments
5. Validates deployment

### Production Deployment

1. Generates fresh OpenAPI spec
2. Builds documentation site
3. Deploys to production domain
4. Validates deployment
5. Creates deployment summary

## Next Steps

- [Complete Deployment Guide](./DEPLOYMENT.md) - Full documentation
- [GitHub Actions Setup](./GITHUB_ACTIONS_SETUP.md) - Automate deployments
- [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md) - Pre/post deployment checks
- [Deployment Flow](./DEPLOYMENT_FLOW.md) - Visual diagrams

## Quick Reference

| Need                | Command                               |
| ------------------- | ------------------------------------- |
| Start dev server    | `bun run dev`                         |
| Deploy preview      | `bun run deploy:preview`              |
| Deploy production   | `bun run deploy:prod`                 |
| Sync OpenAPI        | `bun run openapi:sync`                |
| Validate deployment | `bash scripts/validate-deployment.sh` |
| Test build          | `bun run build`                       |
| Type check          | `bun run typecheck`                   |

## Support

- Check [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed troubleshooting
- Review GitHub Actions logs for CI/CD issues
- Check Vercel dashboard for deployment logs
- See [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) for CI/CD setup

---

**Total Time**: ~20-30 minutes for first-time setup
**Subsequent Deploys**: ~2 minutes or automatic via CI/CD

Last updated: 2026-01-30
