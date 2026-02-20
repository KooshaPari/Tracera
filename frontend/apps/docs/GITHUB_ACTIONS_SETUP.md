# GitHub Actions Setup Guide

This guide walks through setting up the CI/CD pipeline for automatic documentation deployment.

## Overview

The documentation site uses GitHub Actions to:

1. Generate OpenAPI specification from the backend
2. Build the documentation site
3. Deploy to Vercel (preview for PRs, production for main)
4. Validate the deployment

## Required Secrets

### 1. Vercel Token

Create a Vercel authentication token:

1. Go to [vercel.com/account/tokens](https://vercel.com/account/tokens)
2. Click "Create Token"
3. Name: `GitHub Actions - TraceRTM Docs`
4. Scope: Select your account or team
5. Expiration: Set appropriate expiration (e.g., No Expiration for production)
6. Click "Create"
7. Copy the token (shown only once)

Add to GitHub:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VERCEL_TOKEN`
4. Value: Paste the token
5. Click "Add secret"

### 2. Vercel Organization ID

Get your organization ID:

```bash
# Login to Vercel (if not already)
vercel login

# Link the project (if not already)
cd frontend/apps/docs
vercel link

# View the project configuration
cat .vercel/project.json
```

Example output:

```json
{
  "orgId": "team_xxx123yyy456zzz",
  "projectId": "prj_abc123def456ghi"
}
```

Add to GitHub:

1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VERCEL_ORG_ID`
4. Value: The `orgId` from project.json
5. Click "Add secret"

### 3. Vercel Project ID

From the same `project.json` file:

Add to GitHub:

1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VERCEL_DOCS_PROJECT_ID`
4. Value: The `projectId` from project.json
5. Click "Add secret"

### 4. Optional: API URL Override

If your API is at a different URL:

Add to GitHub:

1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `NEXT_PUBLIC_API_URL`
4. Value: Your API URL (e.g., `https://api.tracertm.com`)
5. Click "Add secret"

### 5. Optional: Docs URL Override

If your docs site is at a different URL:

Add to GitHub:

1. Repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `NEXT_PUBLIC_DOCS_URL`
4. Value: Your docs URL (e.g., `https://docs.tracertm.com`)
5. Click "Add secret"

## Summary of Required Secrets

| Secret Name              | Description                 | Required    |
| ------------------------ | --------------------------- | ----------- |
| `VERCEL_TOKEN`           | Vercel authentication token | ✅ Yes      |
| `VERCEL_ORG_ID`          | Vercel organization/team ID | ✅ Yes      |
| `VERCEL_DOCS_PROJECT_ID` | Vercel project ID for docs  | ✅ Yes      |
| `NEXT_PUBLIC_API_URL`    | API endpoint URL            | ⚠️ Optional |
| `NEXT_PUBLIC_DOCS_URL`   | Docs site URL               | ⚠️ Optional |

## Verifying Setup

### 1. Check Secrets

Go to: Repository → Settings → Secrets and variables → Actions

You should see all three required secrets listed (values are hidden).

### 2. Test Workflow

Create a test PR:

```bash
# Create a test branch
git checkout -b test-docs-deployment

# Make a small change to trigger the workflow
echo "# Test" >> frontend/apps/docs/content/index.mdx

# Commit and push
git add frontend/apps/docs/content/index.mdx
git commit -m "test: trigger docs deployment"
git push origin test-docs-deployment
```

Create the PR on GitHub and watch the Actions tab.

### 3. Manual Trigger

You can also manually trigger the workflow:

1. Go to Actions tab
2. Select "Deploy Documentation Site"
3. Click "Run workflow"
4. Select branch and environment
5. Click "Run workflow"

## Workflow Files

### Main Deployment Workflow

**File**: `.github/workflows/docs-deploy.yml`

**Triggers**:

- Push to `main` → Production deployment
- Pull request → Preview deployment
- Manual trigger → Choose environment

**Jobs**:

1. `generate-openapi` - Generate OpenAPI spec from backend
2. `build-docs` - Build the documentation site
3. `deploy-preview` - Deploy preview for PRs
4. `deploy-production` - Deploy to production
5. `validate-deployment` - Validate production deployment

### OpenAPI Generation Workflow

**File**: `.github/workflows/openapi-docs.yml`

**Triggers**:

- Changes to backend Go files
- Manual trigger

**Jobs**:

1. Generate and validate OpenAPI spec
2. Deploy spec to docs site
3. Generate client SDKs (optional)

## Troubleshooting

### Token Expired or Invalid

**Symptoms**: Deployment fails with authentication error

**Solution**:

1. Create a new Vercel token
2. Update `VERCEL_TOKEN` secret in GitHub
3. Re-run the workflow

### Wrong Organization/Project ID

**Symptoms**: "Project not found" error

**Solution**:

1. Verify IDs in `.vercel/project.json`
2. Update secrets in GitHub
3. Ensure token has access to the organization

### Workflow Not Triggering

**Symptoms**: No workflow runs on push/PR

**Solution**:

1. Check workflow file syntax (YAML)
2. Verify path filters match changed files
3. Check if workflows are enabled in repository settings

### Build Failures

**Symptoms**: Build step fails

**Solution**:

1. Check build logs in Actions tab
2. Test build locally: `bun run build`
3. Verify dependencies are correct
4. Check for TypeScript errors

### Deployment Fails

**Symptoms**: Deploy step fails

**Solution**:

1. Verify all secrets are set correctly
2. Check Vercel status page
3. Try manual deployment to isolate issue
4. Review Vercel deployment logs

## Best Practices

1. **Use Expiring Tokens**: Set reasonable expiration dates for security
2. **Rotate Tokens**: Periodically rotate Vercel tokens
3. **Monitor Workflows**: Set up notifications for failed workflows
4. **Review Logs**: Check deployment logs after each deployment
5. **Test Locally**: Always test builds locally before pushing
6. **Use Preview**: Review preview deployments before merging

## GitHub Actions Features

### Preview Deployments

Every PR gets a unique preview URL:

- Automatically deployed on PR creation
- Updated on each push to PR branch
- URL posted in PR comments
- Deleted when PR is closed

### Production Deployments

Automatic deployment to production:

- Triggered on push to `main` branch
- Includes validation checks
- Deployment summary in Actions tab
- Rollback available via Vercel dashboard

### Manual Deployments

Trigger deployments manually:

1. Go to Actions tab
2. Select "Deploy Documentation Site"
3. Click "Run workflow"
4. Choose environment (preview/production)
5. Click "Run workflow"

## Monitoring

### GitHub Actions

Monitor workflow runs:

1. Go to repository → Actions tab
2. View workflow runs and logs
3. Set up notifications for failures

### Vercel Dashboard

Monitor deployments:

1. Go to [vercel.com](https://vercel.com)
2. Select your project
3. View deployment history
4. Check analytics and logs

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vercel Deployment Documentation](https://vercel.com/docs/deployments/overview)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

Last updated: 2026-01-30
