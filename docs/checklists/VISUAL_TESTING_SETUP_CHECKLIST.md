# Visual Testing Setup Verification Checklist

Use this checklist to verify that all visual regression testing components are properly configured.

## Prerequisites

- [ ] Node.js 20+ installed (`node --version`)
- [ ] Bun package manager installed (`bun --version`)
- [ ] GitHub repository access
- [ ] GitHub Actions enabled for repository

## Installation & Configuration

### 1. Dependencies Installed

- [ ] Dependencies installed: `cd frontend/apps/web && bun install`
- [ ] Storybook dependency added: Check `package.json` has `@storybook/react`
- [ ] Chromatic dependency added: Check `package.json` has `chromatic`
- [ ] All Storybook addons installed: `@storybook/addon-docs`, `@storybook/addon-links`

### 2. Storybook Configuration

- [ ] `.storybook/main.ts` exists and has correct configuration
- [ ] `.storybook/preview.ts` exists with viewport and theme settings
- [ ] `.storybook/visual-test.config.ts` exists with component configurations
- [ ] Viewport sizes defined: desktop (1440x900), tablet (768x1024), mobile (375x667)
- [ ] Theme modes configured: light and dark

### 3. Chromatic Configuration

- [ ] `chromatic.config.json` exists
- [ ] Project token placeholder or actual token present
- [ ] `buildScriptName` set to `storybook:build`
- [ ] `autoAcceptChanges` set appropriately (true for main, false for feature branches)

### 4. NPM Scripts

Check `frontend/apps/web/package.json` has:

- [ ] `"storybook": "storybook dev -p 6006"`
- [ ] `"storybook:build": "storybook build"`
- [ ] `"chromatic": "chromatic"`
- [ ] `"chromatic:ci": "chromatic --ci --exit-zero-on-changes"`

## Storybook Setup

### 5. Storybook Builds Successfully

```bash
cd frontend/apps/web
bun run storybook:build
```

- [ ] Build completes without errors
- [ ] `storybook-static/` directory created
- [ ] No TypeScript errors
- [ ] No missing component errors

### 6. Storybook Starts Locally

```bash
cd frontend/apps/web
bun run storybook
```

- [ ] Development server starts on port 6006
- [ ] http://localhost:6006 accessible
- [ ] Component library loads
- [ ] Viewport selector visible
- [ ] Theme selector visible (if configured)

### 7. Component Stories Exist

- [ ] `src/components/graph/__stories__/UnifiedGraphView.stories.tsx` exists
- [ ] `src/components/graph/__stories__/PerspectiveSelector.stories.tsx` exists
- [ ] `src/components/graph/__stories__/GraphSearch.stories.tsx` exists
- [ ] `src/components/graph/__stories__/NodeDetailPanel.stories.tsx` exists
- [ ] `src/components/graph/__stories__/GraphNodePill.stories.tsx` exists
- [ ] `src/components/graph/__stories__/ProgressDashboard.stories.tsx` exists
- [ ] `src/components/graph/__stories__/EditAffordances.stories.tsx` exists
- [ ] Story template exists: `__stories__/TEMPLATE.stories.tsx`

### 8. Stories Load Correctly

In http://localhost:6006:

- [ ] Graph stories visible in sidebar
- [ ] Each story renders without errors
- [ ] Viewport selector works
- [ ] Theme toggle works (if implemented)
- [ ] Interaction controls visible in controls panel

## Visual Testing Setup

### 9. Chromatic Account & Token

- [ ] Chromatic account created at https://www.chromatic.com
- [ ] Project created in Chromatic
- [ ] Project token obtained (format: `chroma_xxxxxxxxxxxxx`)
- [ ] Token stored securely

### 10. Local Environment

- [ ] Environment variable set: `export CHROMATIC_PROJECT_TOKEN=chroma_xxxxxxxxxxxxx`
- [ ] `.env.local` created with token (if using env file)
- [ ] `chromatic.config.json` updated with token

### 11. Chromatic Connection Test

```bash
cd frontend/apps/web
CHROMATIC_PROJECT_TOKEN=your_token bun run chromatic --dry
```

- [ ] Dry run completes successfully
- [ ] No authentication errors
- [ ] No network errors

## Automation & Utilities

### 12. Automation Functions Available

Check `frontend/apps/web/.storybook/visual-regression-automation.ts`:

- [ ] `generateVisualTestParameters()` function exists
- [ ] `createViewportStories()` function exists
- [ ] `createThemeStories()` function exists
- [ ] `createInteractionStories()` function exists
- [ ] `generateSnapshotName()` function exists
- [ ] `VisualRegressionTracker` class exists
- [ ] `VisualTestMetrics` class exists

### 13. Snapshot Manager Script

- [ ] `scripts/chromatic-snapshot-manager.ts` exists
- [ ] Script is executable: `chmod +x scripts/chromatic-snapshot-manager.ts`
- [ ] Help works: `bun scripts/chromatic-snapshot-manager.ts --help`
- [ ] Commands available:
  - [ ] `--list-changed`
  - [ ] `--accept-all`
  - [ ] `--reject-all`
  - [ ] `--summary`
  - [ ] `--validate`

### 14. Setup Script

- [ ] `scripts/setup-chromatic.sh` exists
- [ ] Script is executable: `chmod +x scripts/setup-chromatic.sh`
- [ ] Script checks prerequisites
- [ ] Script guides through setup

## Testing Infrastructure

### 15. Visual Regression Tests

- [ ] `src/__tests__/visual/visual-regression.test.ts` exists
- [ ] Tests run without errors: `bun test src/__tests__/visual`
- [ ] Test coverage for:
  - [ ] Snapshot name generation
  - [ ] Parameter generation
  - [ ] Story creation helpers
  - [ ] Regression tracking
  - [ ] Metrics collection

## GitHub Actions

### 16. Workflow File

- [ ] `.github/workflows/chromatic.yml` exists
- [ ] Workflow has correct triggers:
  - [ ] Push to main, develop, feature/* branches
  - [ ] Pull requests to main, develop
  - [ ] Paths filter for components and stories

### 17. GitHub Secrets

In GitHub repository Settings > Secrets and variables > Actions:

- [ ] `CHROMATIC_PROJECT_TOKEN` secret created
- [ ] Token value matches Chromatic project token
- [ ] Secret can be viewed in workflow runs (check GitHub Actions logs)

### 18. Workflow Execution

- [ ] Make test commit to trigger workflow
- [ ] Workflow job "Visual Regression Tests" runs
- [ ] Storybook builds successfully in workflow
- [ ] Chromatic tests run without errors
- [ ] Results reported in PR or commit

## Documentation

### 19. Quick Start Guide

- [ ] `docs/VISUAL_TESTING_QUICK_START.md` exists
- [ ] Contains setup steps
- [ ] Contains common tasks
- [ ] Contains troubleshooting
- [ ] Time estimates provided

### 20. Comprehensive Guide

- [ ] `docs/VISUAL_TESTING_GUIDE.md` exists
- [ ] Covers Chromatic setup
- [ ] Covers writing tests
- [ ] Covers managing changes
- [ ] Covers best practices
- [ ] Covers troubleshooting

### 21. Implementation Guide

- [ ] `docs/VISUAL_TESTING_IMPLEMENTATION.md` exists
- [ ] Documents all created files
- [ ] Documents configuration
- [ ] Documents coverage
- [ ] Documents next steps

### 22. Storybook README

- [ ] `frontend/apps/web/.storybook/README.md` exists
- [ ] Configuration details documented
- [ ] Story examples provided
- [ ] Helper utilities explained
- [ ] Best practices listed

## First Test Run

### 23. Build Storybook

```bash
cd frontend/apps/web
bun run storybook:build
```

- [ ] Build succeeds
- [ ] No errors in output
- [ ] `storybook-static/` directory created

### 24. Run Visual Tests

```bash
cd frontend/apps/web
CHROMATIC_PROJECT_TOKEN=your_token bun run chromatic
```

- [ ] Tests complete successfully
- [ ] Snapshots uploaded to Chromatic
- [ ] Build URL provided in output
- [ ] Changes appear in Chromatic dashboard

### 25. Review Results

On Chromatic dashboard:

- [ ] Build visible in project
- [ ] Snapshots captured for all stories
- [ ] Changes detected or all matched
- [ ] Can view individual component snapshots
- [ ] Can see viewports and themes

## Validation Tests

### 26. Configuration Validation

```bash
cd frontend/apps/web
bun scripts/chromatic-snapshot-manager.ts --validate
```

- [ ] Configuration validates successfully
- [ ] Component count reported
- [ ] No validation errors

### 27. Snapshot Summary

```bash
cd frontend/apps/web
bun scripts/chromatic-snapshot-manager.ts --summary
```

- [ ] Summary displays correctly
- [ ] Component list shown
- [ ] Total snapshot count displayed
- [ ] Viewport and theme counts accurate

### 28. Unit Tests Pass

```bash
cd frontend/apps/web
bun test src/__tests__/visual/visual-regression.test.ts
```

- [ ] All tests pass
- [ ] No failures
- [ ] All 60+ test cases run

## Responsive Design Testing

### 29. Mobile Viewport

In http://localhost:6006:

- [ ] Select mobile viewport (375x667)
- [ ] All stories render correctly
- [ ] Layout adapts to small screen
- [ ] No horizontal scroll
- [ ] All interactive elements accessible

### 30. Tablet Viewport

In http://localhost:6006:

- [ ] Select tablet viewport (768x1024)
- [ ] All stories render correctly
- [ ] Layout optimized for medium screen
- [ ] All features visible
- [ ] Touch-friendly sizing

### 31. Desktop Viewport

In http://localhost:6006:

- [ ] Default viewport (1440x900)
- [ ] All stories render correctly
- [ ] Full layout visible
- [ ] Optimal spacing and sizing

## Theme Testing

### 32. Light Mode

In http://localhost:6006:

- [ ] Light theme applied (if theme toggle exists)
- [ ] All stories visible in light mode
- [ ] Good contrast and readability
- [ ] Consistent styling

### 33. Dark Mode

In http://localhost:6006:

- [ ] Dark theme applied
- [ ] All stories visible in dark mode
- [ ] Good contrast in dark mode
- [ ] Colors adjusted appropriately
- [ ] No white flashes or artifacts

## Performance Verification

### 34. Build Performance

- [ ] Storybook build time: < 5 minutes
- [ ] Chromatic upload time: < 3 minutes
- [ ] Total first run: < 10 minutes

### 35. Runtime Performance

- [ ] Storybook dev server responsive
- [ ] Page loads quickly at http://localhost:6006
- [ ] Interactions smooth and responsive
- [ ] No console errors

## Integration Verification

### 36. GitHub Integration

- [ ] Workflow runs on push to feature branch
- [ ] Workflow completes successfully
- [ ] PR shows status checks
- [ ] Chromatic status visible in PR

### 37. PR Workflow

- [ ] Create test PR with component changes
- [ ] Visual regression tests run automatically
- [ ] PR shows visual changes status
- [ ] Can view changes in Chromatic from PR
- [ ] Can approve/request changes

## Final Checklist

- [ ] All prerequisites met
- [ ] Installation complete
- [ ] Configuration verified
- [ ] Storybook working locally
- [ ] Chromatic connected
- [ ] Automation utilities functional
- [ ] GitHub Actions running
- [ ] Documentation complete
- [ ] First test run successful
- [ ] Responsive design verified
- [ ] Theme testing verified
- [ ] Performance acceptable

## Sign Off

**Setup Date:** ________________

**Verified By:** ________________

**Notes:**

```
[Add any notes or issues encountered]
```

## Troubleshooting Quick Reference

| Issue | Solution |
| --- | --- |
| Storybook won't build | `rm -rf node_modules storybook-static && bun install && bun run storybook:build` |
| Chromatic auth fails | Check token with `echo $CHROMATIC_PROJECT_TOKEN` |
| Inconsistent snapshots | Add `delay: 500` and `pauseAnimationAtEnd: true` |
| GitHub workflow not running | Check workflow file syntax and event triggers |
| Too many changes | Review carefully in Chromatic dashboard |

## Success Criteria

All items should be checked for production-ready setup.

**Items Checked:** _____ / 37

**Ready for Production:** [ ] Yes [ ] No

If "No", address unchecked items and return to this checklist.
