# Storybook & Visual Regression Testing

Comprehensive visual regression testing for all TraceRTM UI components using Storybook and Chromatic.

## Overview

This Storybook setup provides:

- **Interactive component library** - Browse and test components in isolation
- **Visual regression testing** - Automatically detect visual changes across viewports
- **Responsive design coverage** - Desktop, tablet, and mobile viewports
- **Theme coverage** - Light and dark mode testing
- **Interaction states** - Hover, focus, active, and disabled states
- **CI/CD integration** - Automatic testing on every commit and PR
- **Baseline management** - Easy acceptance/rejection of visual changes

## Files

### Configuration

- **`main.ts`** - Storybook project configuration
- **`preview.tsx`** - Global decorators, viewport definitions, and theme settings
- **`visual-test.config.ts`** - Viewport sizes, theme definitions, and component configs
- **`visual-regression-automation.tsxx`** - Helper functions for writing visual tests

### Documentation

- **`README.md`** - This file

## Quick Start

```bash
# Start dev server
bun run storybook

# Build for Chromatic
bun run storybook:build

# Run visual tests
bun run chromatic

# View test results
# Local: http://localhost:6006
# Cloud: https://www.chromatic.com
```

## Writing Stories

### Basic Story

```typescript
import type { Meta, StoryObj } from "@storybook/react";
import { MyComponent } from "./MyComponent";

const meta: Meta<typeof MyComponent> = {
	title: "Components/MyComponent",
	component: MyComponent,
	tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
	args: {
		label: "Click me",
	},
};
```

### With Visual Test Config

```typescript
const meta: Meta<typeof MyComponent> = {
	title: "Components/MyComponent",
	component: MyComponent,
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 300, // Wait for animations
		},
	},
};
```

### Responsive Viewports

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

### Interaction States

```typescript
export const Hovered: Story = {
	args: { ... },
	play: async ({ canvasElement }) => {
		const button = canvasElement.querySelector("button");
		button?.dispatchEvent(new MouseEvent("mouseenter", { bubbles: true }));
	},
};

export const Focused: Story = {
	args: { ... },
	play: async ({ canvasElement }) => {
		const button = canvasElement.querySelector("button");
		(button as HTMLElement)?.focus();
	},
};
```

### Theme Variants

```typescript
export const DarkMode: Story = {
	args: { ... },
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark">
				<Story />
			</div>
		),
	],
	parameters: {
		chromatic: {
			modes: {
				dark: { query: "[data-theme='dark']" },
			},
		},
	},
};
```

## Automation Helpers

### Generate Test Parameters

```typescript
import { generateVisualTestParameters } from "./visual-regression-automation";

const meta: Meta<typeof Component> = {
	title: "Components/Component",
	component: Component,
	parameters: {
		...generateVisualTestParameters("Component"),
	},
};
```

### Create Viewport Stories

```typescript
import { createViewportStories } from "./visual-regression-automation";

export const Desktop = createViewportStories("Component", baseArgs, ["desktop"]);
export const Tablet = createViewportStories("Component", baseArgs, ["tablet"]);
```

### Create Theme Stories

```typescript
import { createThemeStories } from "./visual-regression-automation";

export const { Light, Dark } = createThemeStories(baseArgs);
```

### Create Interaction Stories

```typescript
import { createInteractionStories } from "./visual-regression-automation";

export const { Hovered, Focused, Active, Disabled } = createInteractionStories(
	baseArgs,
	"button",
);
```

## Viewport Configuration

Defined in `visual-test.config.ts`:

| Viewport | Size | Use Case |
| --- | --- | --- |
| Desktop | 1440x900 | Primary testing viewport |
| Tablet | 768x1024 | iPad-sized devices |
| Mobile | 375x667 | iPhone-sized devices |
| Widescreen | 1920x1080 | Large monitors |

## Theme Configuration

Both automatically tested:

- **Light Mode** - Default light theme
- **Dark Mode** - Dark theme variant

## Component Coverage

### Graph Components

- UnifiedGraphView
- PerspectiveSelector
- GraphSearch
- NodeDetailPanel
- GraphNodePill
- ProgressDashboard
- EditAffordances
- TemporalNavigator

### UI Components

- Button (all variants)
- Input (all states)
- Card (default, hover)
- And more...

## Visual Regression Testing

### How It Works

1. **Snapshot**: Capture screenshot of component
2. **Baseline**: Compare with previous version
3. **Detect**: Identify visual differences
4. **Review**: Accept or reject changes
5. **Update**: Store new baseline if approved

### Running Tests

```bash
# Build Storybook
bun run storybook:build

# Run visual tests
bun run chromatic

# Run in CI mode (for GitHub Actions)
bun run chromatic:ci

# Auto-accept changes (update baselines)
chromatic --auto-accept-changes
```

### Reviewing Changes

1. Go to Chromatic dashboard
2. Open your build
3. Review visual changes
4. Accept (approve changes) or reject (keep old baseline)
5. Changes appear in GitHub PR status

## Best Practices

### Do's

- ✅ Test all component variants
- ✅ Test all viewports (desktop, tablet, mobile)
- ✅ Test light and dark themes
- ✅ Test interaction states (hover, focus, active, disabled)
- ✅ Use meaningful story names
- ✅ Add delays for animations (use `delay: 300`)
- ✅ Set `pauseAnimationAtEnd: true` for consistency
- ✅ Use mock/fixture data (not real data)
- ✅ Review all visual changes
- ✅ Commit baselines to version control

### Don'ts

- ❌ Don't test time-dependent content (timestamps)
- ❌ Don't use random values in visual tests
- ❌ Don't test performance metrics
- ❌ Don't use real API calls
- ❌ Don't skip reviewing changes
- ❌ Don't disable snapshots for components
- ❌ Don't commit without baseline review
- ❌ Don't modify shared component props during tests

## Troubleshooting

### Storybook won't start

```bash
cd frontend/apps/web
rm -rf node_modules storybook-static
bun install
bun run storybook
```

### Build fails

```bash
# Check Storybook build
bun run storybook:build

# Check for TypeScript errors
bun run typecheck

# Check for linting errors
bun run lint
```

### Chromatic token error

```bash
# Verify token is set
echo $CHROMATIC_PROJECT_TOKEN

# Check chromatic.config.json
cat chromatic.config.json

# Try manual test
CHROMATIC_PROJECT_TOKEN=token bun run chromatic --dry
```

### Inconsistent snapshots

- Add `delay: 300+` for animations
- Set `pauseAnimationAtEnd: true`
- Mock API responses consistently
- Use fixed random seeds

### Too many changes detected

- Review visual changes carefully in Chromatic
- Accept or reject intentional changes
- Don't commit without reviewing diffs

## Commands Reference

```bash
# Development
bun run storybook          # Start dev server on :6006
bun run storybook:build    # Build static Storybook

# Visual Testing
bun run chromatic          # Run tests locally
bun run chromatic:ci       # Run in CI mode

# Utilities
bun scripts/chromatic-snapshot-manager.ts --summary       # Show snapshot count
bun scripts/chromatic-snapshot-manager.ts --list-changed  # List changes
bun scripts/chromatic-snapshot-manager.ts --accept-all    # Accept all changes
```

## Environment Variables

```bash
# Required for testing
export CHROMATIC_PROJECT_TOKEN=chroma_xxxxxxxxxxxxx

# Optional
export NODE_ENV=production  # For optimized builds
```

## File Structure

```
.storybook/
├── main.ts                           # Storybook config
├── preview.tsx                       # Global settings
├── visual-test.config.ts             # Viewport/theme config
├── visual-regression-automation.tsx   # Helper utilities
├── README.md                         # This file

src/
├── components/
│   ├── graph/
│   │   ├── UnifiedGraphView.tsx
│   │   ├── __stories__/
│   │   │   ├── UnifiedGraphView.stories.tsx
│   │   │   ├── PerspectiveSelector.stories.tsx
│   │   │   └── ...
│   │   └── ...
│   └── ...
│
├── __tests__/
│   └── visual/
│       └── visual-regression.test.ts

scripts/
└── chromatic-snapshot-manager.ts    # Snapshot utilities
```

## CI/CD Integration

Automatic visual testing on:

- **Push** to main, develop, feature branches
- **Pull requests** to main/develop
- **On changes** to components, stories, or config

Workflow: `.github/workflows/chromatic.yml`

### PR Status Checks

- ✅ **PASSED**: All snapshots match baselines
- ⚠️ **CHANGES**: Visual changes detected (review required)
- ❌ **FAILED**: Regressions found (must fix)

## Performance Tuning

### Build Speed

```bash
# Only test changed components
chromatic --only-changed

# Skip non-visual changes
chromatic --exit-zero-on-changes
```

### Snapshot Count

Currently testing:

- 8 graph components × 2-3 viewports × 2 themes × 2-4 states = ~100+ snapshots
- 15+ UI components × 3 viewports × 2 themes = ~90+ snapshots
- **Total**: ~190+ visual snapshots

## Resources

- [Storybook Documentation](https://storybook.js.org/docs/react)
- [Chromatic Documentation](https://www.chromatic.com/docs)
- [Visual Regression Testing Guide](../../docs/VISUAL_TESTING_GUIDE.md)
- [Quick Start Guide](../../docs/VISUAL_TESTING_QUICK_START.md)

## Support

For issues:

1. Check Storybook build: `bun run storybook:build`
2. Check Chromatic logs: See `chromatic.log`
3. Check GitHub Actions: `.github/workflows/chromatic.yml`
4. Review documentation links above

## Contributing

When adding new components:

1. Create component file
2. Create `.stories.tsx` in `__stories__` directory
3. Include all variants and viewports
4. Add light/dark theme variants
5. Add interaction states
6. Update `visual-test.config.ts` with component config
7. Run visual tests: `bun run chromatic`
8. Review and approve changes
