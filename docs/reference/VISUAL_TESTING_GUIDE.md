# Visual Regression Testing Guide

This guide explains how to use Chromatic for automated visual regression testing of TraceRTM components.

## Overview

Visual regression testing automatically captures screenshots of UI components and detects visual changes across different viewports and themes. Chromatic provides:

- **Automated snapshots** across multiple viewports (desktop, tablet, mobile)
- **Theme coverage** (light and dark modes)
- **Interaction states** (hover, focus, active, disabled)
- **PR integration** with visual change notifications
- **Baseline management** for approving intentional design changes

## Quick Start

### Run Visual Tests Locally

```bash
cd frontend/apps/web

# Start Storybook dev server (for interactive testing)
bun run storybook

# Build Storybook for Chromatic
bun run storybook:build

# Run Chromatic tests (requires project token)
export CHROMATIC_PROJECT_TOKEN=your_token_here
bun run chromatic
```

### View Results

- **Local Storybook**: http://localhost:6006
- **Chromatic Dashboard**: https://www.chromatic.com

## Setting Up Chromatic

### 1. Create Chromatic Account

1. Go to [chromatic.com](https://www.chromatic.com)
2. Sign in with GitHub
3. Create a new project
4. Copy your project token

### 2. Configure Project Token

Store the token as a GitHub secret:

```bash
# In your GitHub repository settings:
# Settings > Secrets and variables > Actions > New repository secret
# Name: CHROMATIC_PROJECT_TOKEN
# Value: chroma_xxxxxxxxxxxxx
```

### 3. Update chromatic.config.json

Update `/frontend/apps/web/chromatic.config.json`:

```json
{
	"projectToken": "chroma_xxxxxxxxxxxxx",
	"buildScriptName": "storybook:build",
	"autoAcceptChanges": true,
	"onlyChanged": true
}
```

## Writing Visual Tests

### Basic Story with Visual Test

```typescript
import type { Meta, StoryObj } from "@storybook/react";
import { MyComponent } from "./MyComponent";

const meta: Meta<typeof MyComponent> = {
	title: "Components/MyComponent",
	component: MyComponent,
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 300,
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

// Automatically tested in light and dark modes
export const Default: Story = {
	args: {
		variant: "default",
	},
};

export const Dark: Story = {
	args: {
		variant: "default",
	},
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark">
				<Story />
			</div>
		),
	],
};
```

### Testing Responsive Designs

```typescript
export const Mobile: Story = {
	args: { ... },
	parameters: {
		viewport: {
			defaultViewport: "mobile",
		},
	},
};

export const Tablet: Story = {
	args: { ... },
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

export const Desktop: Story = {
	args: { ... },
	parameters: {
		viewport: {
			defaultViewport: "desktop",
		},
	},
};
```

### Testing Interactive States

```typescript
export const Hovered: Story = {
	args: { ... },
	play: async ({ canvasElement }) => {
		const element = canvasElement.querySelector("button");
		if (element) {
			element.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
		}
	},
};

export const Focused: Story = {
	args: { ... },
	play: async ({ canvasElement }) => {
		const element = canvasElement.querySelector("button");
		if (element) {
			(element as HTMLElement).focus();
		}
	},
};

export const Disabled: Story = {
	args: {
		disabled: true,
	},
};
```

### Viewports Available

Configure in `.storybook/preview.ts`:

```typescript
const viewports = {
	mobile: "375x667",      // iPhone size
	tablet: "768x1024",     // iPad size
	desktop: "1440x900",    // Standard desktop
	widescreen: "1920x1080" // Large monitors
};
```

### Themes Available

Chromatic automatically tests both light and dark modes:

```typescript
chromatic: {
	modes: {
		light: { query: "[data-theme='light']" },
		dark: { query: "[data-theme='dark']" },
	},
}
```

## Managing Visual Changes

### Review Changes on Chromatic

1. Go to Chromatic dashboard
2. Open your build
3. Review the visual changes
4. Accept or reject changes

### Accept Changes in GitHub

When you submit a PR:

1. Chromatic checks for visual changes
2. GitHub displays a status check
3. Click "Details" to review changes
4. Approve or request changes

### Batch Accept Changes

On Chromatic dashboard:

```bash
# Accept all changes in a build
chromatic --auto-accept-changes
```

### Update Baselines

To intentionally update the baseline:

```bash
cd frontend/apps/web

# Run Chromatic with changes acceptance
CHROMATIC_PROJECT_TOKEN=token bun run chromatic -- --auto-accept-changes
```

## CI/CD Integration

The `.github/workflows/chromatic.yml` workflow automatically:

1. **Triggers on**: push to main/develop/feature branches, PRs
2. **Runs visual tests** on every commit
3. **Comments on PR** with results
4. **Blocks merge** if regressions found
5. **Auto-accepts** minor changes on main branch

### PR Status Checks

Visual testing results show as a GitHub check on PRs:

- ✅ All snapshots passed
- ⚠️ Changes found (review required)
- ❌ Regressions detected (must fix)

## Best Practices

### Do's

- **Test all variants**: Include all props combinations
- **Test all viewports**: Desktop, tablet, mobile
- **Test all themes**: Light and dark modes
- **Test interaction states**: Hover, focus, active, disabled
- **Use meaningful names**: Describe what's being tested
- **Add delays**: Use `delay: 300` for animations to settle
- **Pause animations**: Set `pauseAnimationAtEnd: true` for consistency
- **Version your baselines**: Commit baseline snapshots

### Don'ts

- **Don't test time-dependent**: Avoid timestamps, random values
- **Don't use real data**: Use consistent mock data
- **Don't test performance**: Use Chromatic for visual only
- **Don't ignore warnings**: Review all visual changes
- **Don't commit without review**: Always review visual diffs
- **Don't disable snapshots**: Keep visual coverage comprehensive

## Ignoring Elements

To ignore non-deterministic elements:

```typescript
// In visual-test.config.ts
export const IGNORE_SNAPSHOT_REGIONS = [
	".timestamp",
	".random-id",
	"[data-random]",
];
```

## Troubleshooting

### Storybook won't build

```bash
cd frontend/apps/web
bun install
bun run storybook:build
```

### Chromatic authentication fails

```bash
# Verify token is set
echo $CHROMATIC_PROJECT_TOKEN

# Try manual build
CHROMATIC_PROJECT_TOKEN=token bun run chromatic
```

### Inconsistent snapshots

- Add `delay: 300+` for animations
- Set `pauseAnimationAtEnd: true`
- Mock external data consistently
- Use fixed seeds for randomization

### Too many changes detected

- Review your changes carefully
- Accept or reject in Chromatic dashboard
- Don't commit without reviewing diffs

## Commands Reference

```bash
# Development
bun run storybook              # Start dev server
bun run storybook:build        # Build Storybook

# Visual Testing
bun run chromatic              # Run tests (local)
bun run chromatic:ci          # Run tests (CI mode)

# With options
chromatic --auto-accept-changes  # Accept all changes
chromatic --only-changed          # Only test changed files
chromatic --dry                   # Preview without uploading
```

## Component Coverage

Currently testing with visual snapshots:

- **Graph Components**
  - UnifiedGraphView (desktop, tablet, mobile, light/dark)
  - PerspectiveSelector (all viewports, all themes)
  - GraphSearch (all viewports, interactive states)
  - NodeDetailPanel (desktop, tablet, light/dark)

- **UI Components**
  - Button (all variants, sizes, states)
  - Input (text, focus, disabled states)
  - Card (default, hover states)
  - And more...

## Adding New Components

When adding a new component:

1. Create component file
2. Create `.stories.tsx` file
3. Add all variants and viewports
4. Add light/dark theme variants
5. Add interaction states
6. Run visual tests
7. Review and accept changes

Example structure:

```
src/components/MyComponent/
├── MyComponent.tsx           # Component implementation
├── MyComponent.test.tsx      # Unit tests
└── __stories__/
    └── MyComponent.stories.tsx  # Visual tests
```

## Resources

- [Chromatic Docs](https://www.chromatic.com/docs)
- [Storybook Visual Testing](https://storybook.js.org/docs/react/writing-tests/visual-testing)
- [GitHub Actions Integration](https://www.chromatic.com/docs/github-actions)
- [Accessibility Testing](./ACCESSIBILITY_GUIDE.md)

## Support

For questions or issues:

1. Check Chromatic dashboard logs
2. Review GitHub Actions workflow logs
3. Check Storybook build logs: `frontend/apps/web/storybook-static`
4. Refer to troubleshooting section above
