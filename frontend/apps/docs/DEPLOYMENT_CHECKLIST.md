# Deployment Checklist

Use this checklist to ensure a smooth deployment of the TraceRTM documentation site.

## Pre-Deployment

### Local Testing

- [ ] Code compiles without TypeScript errors

  ```bash
  bun run typecheck
  ```

- [ ] Build succeeds locally

  ```bash
  bun run build
  ```

- [ ] Dev server works correctly

  ```bash
  bun run dev
  # Visit http://localhost:3001
  ```

- [ ] OpenAPI spec generates successfully

  ```bash
  bun run openapi:sync
  ```

- [ ] All tests pass
  ```bash
  bun run test:all
  ```

### Code Quality

- [ ] Code is linted

  ```bash
  bun run lint
  ```

- [ ] No console errors in browser
- [ ] Navigation works correctly
- [ ] Search functionality works
- [ ] API reference loads correctly
- [ ] All links work

### Content Review

- [ ] Documentation is up to date
- [ ] Code examples are correct
- [ ] Images and assets load properly
- [ ] Metadata (titles, descriptions) is correct
- [ ] No placeholder content remains

## GitHub Setup

### Secrets Configuration

- [ ] `VERCEL_TOKEN` is set in GitHub secrets
- [ ] `VERCEL_ORG_ID` is set in GitHub secrets
- [ ] `VERCEL_DOCS_PROJECT_ID` is set in GitHub secrets
- [ ] Optional: `NEXT_PUBLIC_API_URL` is configured
- [ ] Optional: `NEXT_PUBLIC_DOCS_URL` is configured

**Verify**: Go to Repository → Settings → Secrets and variables → Actions

### Workflow Status

- [ ] GitHub Actions workflow file exists (`.github/workflows/docs-deploy.yml`)
- [ ] Workflow is enabled
- [ ] No syntax errors in workflow file
- [ ] Branch protection rules are configured (if needed)

## Vercel Setup

### Project Configuration

- [ ] Vercel project is created
- [ ] Project is linked to GitHub repository
- [ ] Build settings are correct:
  - Framework: Next.js
  - Build Command: `bun run build`
  - Output Directory: `.next`
  - Install Command: `cd ../.. && bun install`

### Environment Variables

Set in Vercel project settings:

- [ ] `NEXT_PUBLIC_API_URL` (Production)
- [ ] `NEXT_PUBLIC_DOCS_URL` (Production)
- [ ] `NEXT_TELEMETRY_DISABLED=1`

### Domain Configuration

- [ ] Custom domain added (docs.tracertm.com)
- [ ] DNS records configured correctly
- [ ] SSL certificate provisioned
- [ ] HTTPS redirect enabled

## Deployment

### Preview Deployment

- [ ] Create test PR
- [ ] GitHub Action runs successfully
- [ ] Preview URL is generated
- [ ] Preview URL is accessible
- [ ] Preview deployment works correctly

### Production Deployment

- [ ] Merge to main branch
- [ ] GitHub Action runs successfully
- [ ] Production deployment completes
- [ ] Site is accessible at https://docs.tracertm.com

## Post-Deployment Validation

### Automated Checks

Run validation script:

```bash
cd frontend/apps/docs
bash scripts/validate-deployment.sh
```

- [ ] All automated checks pass

### Manual Verification

#### Homepage

- [ ] https://docs.tracertm.com loads
- [ ] No console errors
- [ ] Navigation works
- [ ] Links work

#### Documentation

- [ ] https://docs.tracertm.com/docs loads
- [ ] Sidebar navigation works
- [ ] Search works
- [ ] Code blocks render correctly
- [ ] Images load

#### API Reference

- [ ] https://docs.tracertm.com/api-reference loads
- [ ] OpenAPI spec displays correctly
- [ ] Try It Out feature works (if enabled)
- [ ] Examples are correct

#### OpenAPI Endpoints

- [ ] https://docs.tracertm.com/api/openapi.json returns valid JSON
- [ ] https://docs.tracertm.com/api/openapi.yaml returns valid YAML
- [ ] Both specs are identical in content

### Performance

- [ ] Lighthouse score > 90 (Performance)
- [ ] Lighthouse score > 90 (Accessibility)
- [ ] Lighthouse score > 90 (Best Practices)
- [ ] Lighthouse score > 90 (SEO)

Run performance audit:

```bash
bun run test:performance
```

### Browser Compatibility

Test in multiple browsers:

- [ ] Chrome/Edge (Chromium)
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Responsive Design

Test at different viewport sizes:

- [ ] Mobile (320px - 767px)
- [ ] Tablet (768px - 1023px)
- [ ] Desktop (1024px+)
- [ ] Large Desktop (1440px+)

## Monitoring

### Initial Monitoring

- [ ] Check Vercel Analytics (first hour)
- [ ] Monitor error rates in Vercel dashboard
- [ ] Check GitHub Actions for any issues
- [ ] Review deployment logs

### Ongoing Monitoring

- [ ] Set up uptime monitoring (optional)
- [ ] Configure error alerting (optional)
- [ ] Schedule periodic manual checks
- [ ] Monitor analytics regularly

## Rollback Plan

### If Issues Arise

1. **Immediate Rollback**:
   - [ ] Identify last working deployment in Vercel
   - [ ] Click "Promote to Production"
   - [ ] Verify rollback successful

2. **Fix and Redeploy**:
   - [ ] Identify and fix the issue
   - [ ] Test locally
   - [ ] Deploy fix
   - [ ] Validate deployment

### Emergency Contacts

- Vercel Support: support@vercel.com
- GitHub Support: GitHub repository issues
- Team Lead: [Your contact info]

## Documentation

### Post-Deployment Documentation

- [ ] Update CHANGELOG.md
- [ ] Document any configuration changes
- [ ] Update deployment date in docs
- [ ] Share deployment notes with team

### Knowledge Base

- [ ] Add deployment to team knowledge base
- [ ] Document any issues encountered
- [ ] Update runbooks if needed

## Sign-Off

- [ ] Deployment validated by: **\*\***\_\_\_**\*\***
- [ ] Date: **\*\***\_\_\_**\*\***
- [ ] Production URL verified: **\*\***\_\_\_**\*\***
- [ ] All stakeholders notified: **\*\***\_\_\_**\*\***

---

## Quick Reference

### Common Commands

```bash
# Deploy preview
bun run deploy:preview

# Deploy production
bun run deploy:prod

# Validate deployment
bash scripts/validate-deployment.sh

# Run performance tests
bun run test:performance

# Sync OpenAPI spec
bun run openapi:sync
```

### Common Issues

| Issue               | Solution                                          |
| ------------------- | ------------------------------------------------- |
| Build fails         | Check TypeScript errors: `bun run typecheck`      |
| OpenAPI missing     | Run: `bun run openapi:sync`                       |
| Deployment fails    | Check GitHub Actions logs                         |
| Site not accessible | Check DNS propagation (up to 48h)                 |
| Slow performance    | Run bundle analyzer: `ANALYZE=true bun run build` |

### Support Resources

- [Deployment Guide](./DEPLOYMENT.md)
- [GitHub Actions Setup](./GITHUB_ACTIONS_SETUP.md)
- [Quick Start](./QUICK_START.md)
- [Vercel Documentation](https://vercel.com/docs)

---

Last updated: 2026-01-30
