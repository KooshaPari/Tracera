# Visual Regression Testing - Quick Start

Get Storybook and Chromatic visual testing running in minutes.

## Prerequisites

- Node.js 20+
- Bun package manager
- GitHub repository access

## 1. Install Dependencies (2 min)

```bash
cd frontend/apps/web
bun install
```

## 2. Start Storybook Locally (1 min)

```bash
bun run storybook
# Opens http://localhost:6006
```

Browse and test your components interactively. Changes auto-reload.

## 3. Build Storybook (2 min)

```bash
bun run storybook:build
# Creates storybook-static/ folder
```

## 4. Set Up Chromatic Account (5 min)

1. Go to https://www.chromatic.com
2. Click "Sign in with GitHub"
3. Authorize Chromatic
4. Click "Create Project"
5. Copy your **project token** (looks like `chroma_xxxxxxxxxxxxx`)

## 5. Configure Project Token (1 min)

**Option A: Local Testing**

```bash
export CHROMATIC_PROJECT_TOKEN=chroma_xxxxxxxxxxxxx
```

**Option B: GitHub Actions**

1. Go to repository Settings
2. Secrets and variables → Actions
3. New secret: `CHROMATIC_PROJECT_TOKEN`
4. Paste your token

## 6. Update Configuration (1 min)

Edit `/frontend/apps/web/chromatic.config.json`:

```json
{
	"projectToken": "chroma_xxxxxxxxxxxxx",
	...
}
```

## 7. Run Visual Tests (3 min)

```bash
cd frontend/apps/web

# Build and test
bun run storybook:build
bun run chromatic
```

Or with CI mode:

```bash
bun run chromatic:ci
```

## 8. View Results (1 min)

- **Local**: Check console output
- **Chromatic Dashboard**: https://www.chromatic.com/builds
- **GitHub PR**: Check status checks section

## Common Tasks

### View Component Library

```bash
bun run storybook
# Visit http://localhost:6006
```

### Update Visual Baselines

After intentional design changes:

```bash
cd frontend/apps/web
bun run chromatic -- --auto-accept-changes
```

### Test Specific Viewport

Stories automatically test:

- Desktop (1440x900)
- Tablet (768x1024)
- Mobile (375x667)

View in Storybook toolbar to see different viewports.

### Test Light/Dark Modes

Stories automatically test both themes. They toggle using:

```typescript
decorators: [
	(Story) => (
		<div className="dark" data-theme="dark">
			<Story />
		</div>
	),
]
```

### Debug Visual Diffs

1. Go to Chromatic build
2. Click on changed snapshot
3. View side-by-side comparison
4. Accept or request changes

### Write New Stories

Create `/src/components/MyComponent/__stories__/MyComponent.stories.tsx`:

```typescript
import type { Meta, StoryObj } from "@storybook/react";
import { MyComponent } from "../MyComponent";

const meta: Meta<typeof MyComponent> = {
	title: "Components/MyComponent",
	component: MyComponent,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
		},
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
	args: {
		label: "Click me",
	},
};

export const Disabled: Story = {
	args: {
		label: "Click me",
		disabled: true,
	},
};
```

## GitHub Actions Workflow

Chromatic runs automatically on:

- **Push** to main, develop, feature branches
- **Pull requests** to main/develop
- **On changes** to components, stories, or Storybook config

Check: PR → Checks section → "Visual Regression Tests"

## Troubleshooting

### Build fails

```bash
cd frontend/apps/web
rm -rf node_modules storybook-static
bun install
bun run storybook:build
```

### Token not recognized

```bash
# Verify token is set
echo $CHROMATIC_PROJECT_TOKEN

# Test token validity
chromatic --project-token $CHROMATIC_PROJECT_TOKEN --dry
```

### Too many changes

Review your changes:

1. Go to Chromatic dashboard
2. View the build
3. Accept intentional changes
4. Reject unintended changes

## Next Steps

- Read [Visual Testing Guide](./VISUAL_TESTING_GUIDE.md) for detailed documentation
- Check `.storybook/visual-test.config.ts` for viewport/theme configs
- View example stories in `src/components/graph/__stories__/`
- Set up GitHub Actions (already configured in `.github/workflows/chromatic.yml`)

## Time Estimates

| Task | Time |
| --- | --- |
| Setup | ~15 minutes |
| First build | ~3-5 minutes |
| Subsequent builds | ~1-2 minutes |
| Review changes | ~5-10 minutes |
| Approve changes | < 1 minute |

## Key Files

```
frontend/apps/web/
├── .storybook/
│   ├── main.ts              # Storybook config
│   ├── preview.ts           # Global settings
│   ├── visual-test.config.ts # Viewport/theme settings
│   └── visual-regression-automation.ts
├── chromatic.config.json    # Chromatic settings
├── src/
│   ├── components/**/*.stories.tsx # Component stories
│   └── __tests__/
│       └── visual/ # Visual regression tests
└── scripts/
    └── chromatic-snapshot-manager.ts
```

## Support

- Chromatic Docs: https://www.chromatic.com/docs
- Storybook Docs: https://storybook.js.org/docs
- GitHub Issues: Check repo issue tracker

## Tips & Tricks

1. **Speed up builds**: Use `--only-changed` flag to test only modified components
2. **Skip non-visual changes**: Chromatic skips tests if only code (not visual) changed
3. **Batch updates**: Use automation scripts to approve multiple changes at once
4. **Theme testing**: Automatic light/dark mode testing - no extra work needed
5. **Responsive**: Viewports tested automatically - responsive design verified
