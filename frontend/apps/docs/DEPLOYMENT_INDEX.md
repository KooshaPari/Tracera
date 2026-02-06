# Deployment Documentation Index

Complete index of all deployment-related documentation for the TraceRTM documentation site.

## Quick Navigation

**Just want to deploy?** → [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) (20 minutes)

**Setting up CI/CD?** → [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) (15 minutes)

**Need a checklist?** → [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

**Want to understand the flow?** → [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md)

**Looking for complete docs?** → [DEPLOYMENT.md](./DEPLOYMENT.md)

## Documentation Overview

### Getting Started (Choose One)

| Document                                                 | Best For                | Time Required |
| -------------------------------------------------------- | ----------------------- | ------------- |
| [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) | First-time deployment   | 20 minutes    |
| [QUICK_START.md](./QUICK_START.md)                       | Local development setup | 10 minutes    |
| [README.md](./README.md)                                 | Project overview        | 5 minutes     |

### Deployment Guides

| Document                                                 | Purpose                   | Detail Level                |
| -------------------------------------------------------- | ------------------------- | --------------------------- |
| [DEPLOYMENT.md](./DEPLOYMENT.md)                         | Complete deployment guide | Comprehensive (9,500 words) |
| [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) | Fast deployment guide     | Quick (2,000 words)         |
| [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md)               | Visual flow diagrams      | Visual/Technical            |
| [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)     | Pre/post deployment tasks | Checklist Format            |

### Setup & Configuration

| Document                                             | Focus Area              | Audience          |
| ---------------------------------------------------- | ----------------------- | ----------------- |
| [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) | CI/CD configuration     | DevOps/Developers |
| `.env.example`                                       | Local environment setup | Developers        |
| `.env.production.example`                            | Production environment  | DevOps            |
| `vercel.json`                                        | Vercel platform config  | DevOps            |

### Reference & Status

| Document                                                 | Content                    | Use Case             |
| -------------------------------------------------------- | -------------------------- | -------------------- |
| [PHASES_6_7_SUMMARY.md](./PHASES_6_7_SUMMARY.md)         | Executive summary          | Quick overview       |
| [PHASES_6_7_COMPLETION.md](./PHASES_6_7_COMPLETION.md)   | Detailed completion report | Technical deep dive  |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | Phase 5 implementation     | Historical reference |

## Documents by Audience

### For Developers

1. **Start Here**: [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)
2. **Local Setup**: [QUICK_START.md](./QUICK_START.md)
3. **Full Reference**: [DEPLOYMENT.md](./DEPLOYMENT.md)
4. **Troubleshooting**: [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting)

### For DevOps Engineers

1. **Start Here**: [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md)
2. **Workflow Details**: [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md)
3. **Configuration**: `vercel.json`, `.github/workflows/docs-deploy.yml`
4. **Validation**: [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)

### For Project Managers

1. **Overview**: [PHASES_6_7_SUMMARY.md](./PHASES_6_7_SUMMARY.md)
2. **Status**: [PHASES_6_7_COMPLETION.md](./PHASES_6_7_COMPLETION.md)
3. **Process**: [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md)

### For New Team Members

1. **Project Overview**: [README.md](./README.md)
2. **Quick Start**: [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md)
3. **Development**: [QUICK_START.md](./QUICK_START.md)

## Documents by Task

### First-Time Setup

**Goal**: Deploy the docs site for the first time

**Documents**:

1. [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) - Initial deployment
2. [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) - CI/CD setup
3. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Verification

**Estimated Time**: 45 minutes

### Regular Deployment

**Goal**: Deploy updates to the docs site

**Documents**:

1. [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md#deploy-now) - Quick deploy commands
2. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md#pre-deployment) - Pre-deployment checks

**Estimated Time**: 10 minutes

### Troubleshooting Issues

**Goal**: Fix deployment problems

**Documents**:

1. [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting) - Common issues
2. [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md#troubleshooting) - CI/CD issues
3. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md#common-issues) - Quick fixes

**Estimated Time**: Varies

### Understanding the System

**Goal**: Learn how deployment works

**Documents**:

1. [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md) - Visual diagrams
2. [DEPLOYMENT.md](./DEPLOYMENT.md) - Complete explanation
3. [PHASES_6_7_COMPLETION.md](./PHASES_6_7_COMPLETION.md) - Technical details

**Estimated Time**: 30 minutes

### Configuring Custom Domain

**Goal**: Set up custom domain (docs.tracertm.com)

**Documents**:

1. [DEPLOYMENT.md](./DEPLOYMENT.md#custom-domain-configuration) - DNS setup
2. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md#domain-configuration) - Verification

**Estimated Time**: 20 minutes (+ DNS propagation)

## Scripts Reference

All deployment scripts are in `frontend/apps/docs/scripts/`:

| Script                   | Purpose                | Usage                               |
| ------------------------ | ---------------------- | ----------------------------------- |
| `deploy.sh`              | Interactive deployment | `./deploy.sh [preview\|production]` |
| `preview-deploy.sh`      | Quick preview deploy   | `./preview-deploy.sh`               |
| `prod-deploy.sh`         | Quick prod deploy      | `./prod-deploy.sh`                  |
| `sync-openapi.sh`        | Sync OpenAPI spec      | `./sync-openapi.sh`                 |
| `validate-deployment.sh` | Validate deployment    | `./validate-deployment.sh [url]`    |

**Note**: All scripts are executable and documented in [DEPLOYMENT.md](./DEPLOYMENT.md#deployment-scripts)

## Configuration Files

| File                                | Purpose                | Documentation                                         |
| ----------------------------------- | ---------------------- | ----------------------------------------------------- |
| `vercel.json`                       | Vercel platform config | [DEPLOYMENT.md](./DEPLOYMENT.md#vercel-configuration) |
| `.vercelignore`                     | Deployment exclusions  | [DEPLOYMENT.md](./DEPLOYMENT.md#vercel-configuration) |
| `.env.example`                      | Local env template     | [DEPLOYMENT.md](./DEPLOYMENT.md#environment-setup)    |
| `.env.production.example`           | Production env         | [DEPLOYMENT.md](./DEPLOYMENT.md#environment-setup)    |
| `.github/workflows/docs-deploy.yml` | CI/CD workflow         | [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md)  |

## NPM Scripts

In `package.json`:

| Script           | Command                          | Purpose            |
| ---------------- | -------------------------------- | ------------------ |
| `deploy`         | `bash scripts/deploy.sh`         | Main deploy script |
| `deploy:preview` | `bash scripts/preview-deploy.sh` | Quick preview      |
| `deploy:prod`    | `bash scripts/prod-deploy.sh`    | Quick production   |
| `openapi:sync`   | `bash scripts/sync-openapi.sh`   | Sync OpenAPI       |

**Usage**: `bun run <script-name>`

## External Resources

### Vercel Documentation

- [Vercel Deployment](https://vercel.com/docs/deployments/overview)
- [Vercel CLI](https://vercel.com/docs/cli)
- [Custom Domains](https://vercel.com/docs/concepts/projects/custom-domains)

### GitHub Actions

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

### Next.js

- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Environment Variables](https://nextjs.org/docs/basic-features/environment-variables)

### Fumadocs

- [Fumadocs Deployment](https://fumadocs.vercel.app/docs/headless/deploy)

## Document Hierarchy

```
Deployment Documentation
│
├── Quick Start
│   ├── DEPLOYMENT_QUICK_START.md (⭐ Start here for deployment)
│   └── QUICK_START.md (For local development)
│
├── Complete Guides
│   ├── DEPLOYMENT.md (⭐ Complete deployment guide)
│   └── GITHUB_ACTIONS_SETUP.md (⭐ CI/CD setup)
│
├── Visual Reference
│   └── DEPLOYMENT_FLOW.md (Flow diagrams)
│
├── Checklists
│   └── DEPLOYMENT_CHECKLIST.md (Pre/post deployment)
│
├── Status & Reports
│   ├── PHASES_6_7_SUMMARY.md (Executive summary)
│   └── PHASES_6_7_COMPLETION.md (Technical completion)
│
└── Configuration
    ├── vercel.json
    ├── .vercelignore
    ├── .env.example
    └── .env.production.example
```

## Recommended Reading Order

### For First-Time Deployment

1. [README.md](./README.md) - 5 min
2. [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) - 10 min
3. [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md) - 15 min
4. [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Reference

**Total**: ~30 minutes reading + 20 minutes doing

### For Understanding the System

1. [PHASES_6_7_SUMMARY.md](./PHASES_6_7_SUMMARY.md) - 10 min
2. [DEPLOYMENT_FLOW.md](./DEPLOYMENT_FLOW.md) - 15 min
3. [DEPLOYMENT.md](./DEPLOYMENT.md) - 30 min
4. [PHASES_6_7_COMPLETION.md](./PHASES_6_7_COMPLETION.md) - 20 min

**Total**: ~75 minutes

## Support & Help

### Quick Reference

- [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md#common-commands)
- [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md#quick-reference)

### Troubleshooting

- [DEPLOYMENT.md](./DEPLOYMENT.md#troubleshooting)
- [GITHUB_ACTIONS_SETUP.md](./GITHUB_ACTIONS_SETUP.md#troubleshooting)

### Contact

- GitHub Issues: Create an issue in the repository
- Vercel Support: support@vercel.com
- Documentation: This index and linked documents

## Version History

- **2026-01-30**: Phases 6-7 completed - Full deployment pipeline implemented
- **2026-01-30**: Phase 5 completed - Search and performance optimization
- Previous phases documented in respective PHASE_X files

## Updates & Maintenance

This index and all deployment documentation should be updated when:

- New deployment methods are added
- CI/CD workflow changes
- New scripts are created
- Configuration changes
- Best practices evolve

---

**Quick Links**:

- 🚀 [Deploy Now](./DEPLOYMENT_QUICK_START.md)
- 🔧 [Setup CI/CD](./GITHUB_ACTIONS_SETUP.md)
- ✅ [Checklist](./DEPLOYMENT_CHECKLIST.md)
- 📊 [Flow Diagrams](./DEPLOYMENT_FLOW.md)
- 📖 [Full Guide](./DEPLOYMENT.md)

Last updated: 2026-01-30
