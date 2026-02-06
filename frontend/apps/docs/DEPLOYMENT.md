# Documentation Site Deployment Guide

This guide covers the deployment process for the TraceRTM documentation site using Vercel.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Deployment Methods](#deployment-methods)
- [CI/CD Pipeline](#cicd-pipeline)
- [Custom Domain Configuration](#custom-domain-configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

1. **Bun** (package manager)

   ```bash
   curl -fsSL https://bun.sh/install | bash
   ```

2. **Vercel CLI** (for manual deployments)

   ```bash
   bun install --global vercel@latest
   ```

3. **Go** (for OpenAPI spec generation)
   - Download from [golang.org](https://golang.org/dl/)
   - Required version: 1.23 or higher

### Required Secrets

Set up these secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `VERCEL_TOKEN` - Vercel authentication token
- `VERCEL_ORG_ID` - Your Vercel organization ID
- `VERCEL_DOCS_PROJECT_ID` - Vercel project ID for docs site
- `NEXT_PUBLIC_API_URL` (optional) - API endpoint URL (default: https://api.tracertm.com)
- `NEXT_PUBLIC_DOCS_URL` (optional) - Docs site URL (default: https://docs.tracertm.com)

### Getting Vercel Credentials

1. **Install Vercel CLI**:

   ```bash
   bun install --global vercel@latest
   ```

2. **Login and link project**:

   ```bash
   cd frontend/apps/docs
   vercel login
   vercel link
   ```

3. **Get credentials**:

   ```bash
   # This will display your org and project IDs
   cat .vercel/project.json
   ```

4. **Create Vercel token**:
   - Go to [vercel.com/account/tokens](https://vercel.com/account/tokens)
   - Create a new token with appropriate scope
   - Save it as `VERCEL_TOKEN` secret

## Environment Setup

### Local Development

1. **Install dependencies**:

   ```bash
   cd frontend
   bun install
   ```

2. **Sync OpenAPI spec** (optional):

   ```bash
   cd frontend/apps/docs
   bun run openapi:sync
   ```

3. **Start development server**:

   ```bash
   bun run dev
   ```

   The site will be available at http://localhost:3001

### Environment Variables

Create a `.env.local` file in `frontend/apps/docs/`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DOCS_URL=http://localhost:3001
```

## Deployment Methods

### 1. Automated Deployment (CI/CD)

The documentation site automatically deploys when changes are pushed:

**Preview Deployments** (Pull Requests):

- Trigger: Any PR with changes to `frontend/apps/docs/**` or `docs/**`
- Environment: Preview
- URL: Unique preview URL (posted in PR comments)

**Production Deployments** (Main Branch):

- Trigger: Push to `main` branch
- Environment: Production
- URL: https://docs.tracertm.com

### 2. Manual Deployment

#### Quick Deploy Scripts

**Deploy preview**:

```bash
cd frontend/apps/docs
bun run deploy:preview
```

**Deploy to production**:

```bash
cd frontend/apps/docs
bun run deploy:prod
```

#### Full Deploy Script

For more control:

```bash
cd frontend/apps/docs
bash scripts/deploy.sh [preview|production]
```

The script will:

1. Check requirements (bun, vercel CLI, Go)
2. Generate OpenAPI specification from backend
3. Install dependencies
4. Build the site
5. Deploy to Vercel
6. Validate deployment

#### Vercel CLI Direct

**Preview deployment**:

```bash
cd frontend/apps/docs
vercel
```

**Production deployment**:

```bash
cd frontend/apps/docs
vercel --prod
```

## CI/CD Pipeline

### Workflow Overview

The GitHub Actions workflow (`.github/workflows/docs-deploy.yml`) includes:

1. **Generate OpenAPI** - Extracts API spec from Go backend
2. **Build Docs** - Compiles the documentation site
3. **Deploy Preview** - Deploys to preview environment for PRs
4. **Deploy Production** - Deploys to production for main branch
5. **Validate Deployment** - Verifies site accessibility and critical pages

### Workflow Triggers

- **Push to main**: Full production deployment
- **Pull request**: Preview deployment with URL in PR comment
- **Manual trigger**: Workflow dispatch with environment selection
- **Backend changes**: Updates OpenAPI spec automatically

### Viewing Workflow Results

1. Go to GitHub Actions tab in your repository
2. Select "Deploy Documentation Site" workflow
3. View deployment logs and summary
4. Check deployment URLs in workflow output

## Custom Domain Configuration

### Setting Up Custom Domain (docs.tracertm.com)

#### 1. Configure Domain in Vercel

1. Go to your Vercel project dashboard
2. Navigate to Settings → Domains
3. Add domain: `docs.tracertm.com`
4. Vercel will provide DNS records

#### 2. Configure DNS

Add these DNS records to your domain provider:

**For root domain**:

```
Type: A
Name: docs
Value: 76.76.21.21
```

**For www**:

```
Type: CNAME
Name: www.docs
Value: cname.vercel-dns.com
```

**Alternative (CNAME for docs subdomain)**:

```
Type: CNAME
Name: docs
Value: cname.vercel-dns.com
```

#### 3. Enable HTTPS

1. Vercel automatically provisions SSL certificate
2. Wait for DNS propagation (can take up to 48 hours)
3. Certificate auto-renews via Let's Encrypt

#### 4. Verify Configuration

```bash
# Check DNS propagation
dig docs.tracertm.com

# Test HTTPS
curl -I https://docs.tracertm.com

# Verify redirects
curl -I http://docs.tracertm.com
```

### Domain Configuration in Vercel

The `vercel.json` file includes:

- **Redirects**: HTTP → HTTPS, /docs → /
- **Rewrites**: API endpoint proxying
- **Headers**: Security headers (CSP, HSTS, etc.)

## Deployment Validation

### Automated Checks

The CI/CD pipeline validates:

1. **Site Accessibility** - HTTP 200 response
2. **OpenAPI Spec** - Available at /api/openapi.json
3. **Critical Pages**:
   - Homepage (/)
   - Documentation (/docs)
   - API Reference (/api-reference)

### Manual Validation

After deployment, verify:

```bash
# Check homepage
curl -I https://docs.tracertm.com/

# Check OpenAPI spec
curl -I https://docs.tracertm.com/api/openapi.json

# Check API reference page
curl -I https://docs.tracertm.com/api-reference

# Full site check (if you have the script)
bash scripts/validate-deployment.sh
```

## Monitoring and Analytics

### Vercel Analytics

Enable in Vercel dashboard:

1. Go to project Settings → Analytics
2. Enable Web Analytics
3. View real-time and historical data

### Performance Monitoring

```bash
# Run Lighthouse audit
cd frontend/apps/docs
bun run lighthouse

# Run performance tests
bun run test:performance
```

### Error Monitoring

Check Vercel deployment logs:

1. Go to Vercel dashboard → Deployments
2. Select deployment
3. View build and runtime logs

## Troubleshooting

### Build Failures

**Issue**: Build fails during `bun run build`

**Solutions**:

1. Check build logs in GitHub Actions or Vercel
2. Verify all dependencies are installed
3. Check for TypeScript errors: `bun run typecheck`
4. Validate OpenAPI spec exists in `public/api/`

```bash
# Local build test
cd frontend/apps/docs
bun install
bun run build
```

### OpenAPI Generation Issues

**Issue**: OpenAPI spec not generated

**Solutions**:

1. Verify Go is installed: `go version`
2. Install swag: `go install github.com/swaggo/swag/cmd/swag@latest`
3. Check backend directory exists
4. Manually sync spec: `bun run openapi:sync`

### Deployment Fails

**Issue**: Deployment to Vercel fails

**Solutions**:

1. Verify Vercel token is valid
2. Check project is linked: `vercel ls`
3. Ensure all secrets are set in GitHub
4. Try manual deployment to identify issue

```bash
# Test Vercel connection
vercel whoami

# List projects
vercel ls

# Test deployment
vercel --prod --confirm
```

### DNS/Domain Issues

**Issue**: Custom domain not working

**Solutions**:

1. Verify DNS records are correct
2. Wait for DNS propagation (up to 48 hours)
3. Check domain configuration in Vercel dashboard
4. Test DNS: `dig docs.tracertm.com`
5. Flush local DNS: `sudo dscacheutil -flushcache` (macOS)

### Performance Issues

**Issue**: Site loads slowly

**Solutions**:

1. Run bundle analyzer: `ANALYZE=true bun run build`
2. Check Vercel Analytics for bottlenecks
3. Optimize images and assets
4. Review and optimize third-party scripts

## Rollback Procedure

### Quick Rollback in Vercel

1. Go to Vercel dashboard → Deployments
2. Find the last working deployment
3. Click "Promote to Production"

### Rollback via Git

```bash
# Find the last working commit
git log --oneline

# Revert to that commit
git revert <commit-hash>

# Push to trigger new deployment
git push origin main
```

### Emergency Rollback

If site is completely broken:

```bash
# Redeploy previous version manually
cd frontend/apps/docs
vercel --prod --force
```

## Best Practices

1. **Always test locally** before deploying
2. **Use preview deployments** for testing changes
3. **Monitor build times** and optimize if needed
4. **Keep dependencies updated** regularly
5. **Review deployment logs** after each deploy
6. **Test critical paths** after production deployment
7. **Document all configuration changes**

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Fumadocs Deployment](https://fumadocs.vercel.app/docs/headless/deploy)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

For deployment issues:

1. Check this guide first
2. Review GitHub Actions logs
3. Check Vercel deployment logs
4. Consult Vercel support documentation
5. Create an issue in the repository

---

Last updated: 2026-01-30
