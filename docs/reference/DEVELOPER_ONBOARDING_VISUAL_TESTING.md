# Developer Onboarding: Visual Regression Testing

Welcome to TraceRTM's visual regression testing system! This guide will get you up to speed in 30 minutes.

## What You'll Learn

- How to view components in Storybook
- How to run visual tests locally
- How to write visual test stories
- How to review visual changes on PRs
- How visual testing integrates with your workflow

## Time Estimates

- Read this guide: 5 minutes
- Setup and first test: 10 minutes
- Writing a story: 5 minutes
- **Total: 20 minutes**

## Part 1: Understanding Visual Testing (5 min)

### What is Visual Regression Testing?

Visual regression testing automatically captures screenshots of UI components and detects visual changes. When you modify a component, the system:

1. Takes screenshots of the component in different viewports and themes
2. Compares them with previous versions (baselines)
3. Flags any visual differences
4. Lets you approve or reject the changes

### Why We Use It

- **Catch visual bugs** that code reviews miss
- **Test responsiveness** across devices automatically
- **Verify accessibility** contrast and sizing
- **Prevent regressions** when refactoring
- **Document design** through living examples

### How It Works in Our Project

```
You write        Storybook     Chromatic         GitHub
components  →   renders   →   tests visually →  shows results
              → stories
```

## Part 2: Your First Visual Test (10 min)

### Step 1: Install Dependencies

```bash
cd frontend/apps/web
bun install
```

### Step 2: Start Storybook

```bash
bun run storybook
```

Visit http://localhost:6006 and explore the component library!

### Step 3: Build for Testing

```bash
bun run storybook:build
```

### Step 4: Run Visual Tests

Set your environment variable first:

```bash
export CHROMATIC_PROJECT_TOKEN=chroma_xxxxxxxxxxxxx
```

Then run tests:

```bash
bun run chromatic --dry
```

This does a dry run without uploading results. Great for testing!

## Part 3: Viewing Components (3 min)

### In Storybook (http://localhost:6006)

- **Left sidebar**: Browse all stories by category
- **Canvas**: See the component rendered
- **Controls**: Adjust props and see live updates
- **Viewport selector** (top right): Test different screen sizes
  - Desktop (1440x900)
  - Tablet (768x1024)
  - Mobile (375x667)

### Stories We Have

Look for **Components > Graph** in the sidebar:

- **UnifiedGraphView** - Full graph visualization
- **PerspectiveSelector** - Perspective controls
- **GraphSearch** - Search interface
- **NodeDetailPanel** - Node details panel
- **GraphNodePill** - Individual node display
- **ProgressDashboard** - Progress tracking
- **EditAffordances** - Edit controls

Each story shows the component in different states and viewports!

## Part 4: Writing Your First Story (5 min)

### Use the Template

Copy the template from:

```
src/components/graph/__stories__/TEMPLATE.stories.tsx
```

### Basic Story Example

```typescript
import type { Meta, StoryObj } from "@storybook/react";
import { MyComponent } from "../MyComponent";

const meta: Meta<typeof MyComponent> = {
	title: "Components/Graph/MyComponent",
	component: MyComponent,
	tags: ["autodocs"],
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

### Key Points

- **Title**: Use path convention `Components/Graph/ComponentName`
- **Component**: Pass the component to test
- **Parameters**: Configure visual testing (viewports, themes)
- **Stories**: Create a story for each variant
- **Args**: Pass props to test different states

### Test All Variants

For each component, include stories for:

- ✅ Default state
- ✅ Disabled state
- ✅ Loading state (if applicable)
- ✅ Error state (if applicable)
- ✅ Different sizes
- ✅ Different variants
- ✅ Mobile viewport
- ✅ Dark mode

## Part 5: Your Workflow

### Writing Code + Visual Tests

```
1. Modify component
   └─> Update/create .stories.tsx file

2. Test locally
   └─> bun run storybook
   └─> View at http://localhost:6006

3. Run visual tests
   └─> bun run storybook:build
   └─> bun run chromatic --dry

4. Build and push
   └─> git commit and push

5. GitHub Actions runs tests
   └─> Chromatic tests run automatically
   └─> Results show on PR
```

### Reviewing PR Visual Changes

When you open a PR:

1. GitHub Actions automatically runs visual tests
2. Check the "Visual Regression Tests" status on your PR
3. Click "Details" to see the Chromatic build
4. Review visual changes:
   - ✅ Expected? Approve
   - ❌ Unexpected? Request changes
5. Approve PR once visual tests pass

## Part 6: Common Tasks

### View Existing Components

```bash
bun run storybook
```

Visit http://localhost:6006 and browse!

### Test a Component During Development

```bash
# Terminal 1: Start Storybook
bun run storybook

# Terminal 2: Edit your component
vim src/components/MyComponent.tsx

# In browser: Changes reload automatically!
```

### Add a New Component Story

1. Create `.stories.tsx` file next to component
2. Copy structure from TEMPLATE.stories.tsx
3. Define your stories with different variants
4. Save and see in Storybook immediately
5. Run `bun run chromatic --dry` to test visually

### Update Visual Baselines

After intentional design changes:

```bash
cd frontend/apps/web

# Review changes in Chromatic dashboard first!
# Then accept them:

bun scripts/chromatic-snapshot-manager.ts --accept-all
```

### Fix Visual Regression

If visual tests fail:

1. Review the change in Chromatic dashboard
2. View side-by-side comparison
3. Fix the component
4. Re-run tests
5. Accept changes when correct

## Part 7: Testing Checklist

When you write a story, verify:

- [ ] Component renders without errors
- [ ] All props are testable via controls
- [ ] Story loads in Storybook without errors
- [ ] Try different viewports (mobile, tablet, desktop)
- [ ] Try both themes (light, dark)
- [ ] Test interaction states if applicable
- [ ] No random values (consistent data)
- [ ] Run visual tests: `bun run chromatic --dry`
- [ ] Review results in terminal

## Part 8: Common Questions

### Q: How long do tests take?

A: First run 3-5 minutes, subsequent 1-2 minutes. GitHub Actions runs in parallel.

### Q: What if I break something visually?

A: Don't panic! You can:
1. Review changes in Chromatic
2. Fix the component
3. Re-run tests
4. Approve when correct

### Q: Do I need to approve every change?

A: On feature branches, yes. On main, changes auto-approve (if configured). Review PRs carefully!

### Q: Can I test offline?

A: Storybook works offline. Visual testing requires internet for Chromatic.

### Q: What if tests are flaky?

A: Add `delay: 500` to chromatic parameters or `pauseAnimationAtEnd: true`.

### Q: How do I test multiple viewports?

A: Create different stories for each viewport:

```typescript
export const Mobile: Story = {
	args: { ... },
	parameters: {
		viewport: { defaultViewport: "mobile" }
	}
};
```

### Q: How do I test dark mode?

A: Automatically! Both light and dark modes tested. Or use decorator:

```typescript
decorators: [
	(Story) => (
		<div className="dark" data-theme="dark">
			<Story />
		</div>
	),
]
```

## Part 9: Resources

### Documentation

- **Quick Start**: `docs/VISUAL_TESTING_QUICK_START.md` (15 min read)
- **Complete Guide**: `docs/VISUAL_TESTING_GUIDE.md` (full reference)
- **Storybook Docs**: `frontend/apps/web/.storybook/README.md`
- **Examples**: Look at existing stories in `__stories__/` folders

### External Resources

- [Storybook Documentation](https://storybook.js.org/docs/react)
- [Chromatic Documentation](https://www.chromatic.com/docs)
- [Visual Testing Best Practices](https://www.chromatic.com/blog)

### Getting Help

1. Check the documentation links above
2. Look at existing stories for examples
3. Ask your team lead
4. Check GitHub issues

## Part 10: Next Steps

### Immediate (Today)

1. ✅ Read this guide (5 min)
2. ✅ Setup Storybook locally (10 min)
3. ✅ Explore at http://localhost:6006 (5 min)

### This Week

1. Write a story for a component you work on
2. Run `bun run chromatic --dry` locally
3. Review changes in Storybook
4. Create a test PR and see visual tests run

### Ongoing

1. Write stories for new components
2. Review visual changes on PRs
3. Keep components visually consistent
4. Expand visual test coverage

## Key Takeaways

- 📖 **Storybook**: Interactive component library at http://localhost:6006
- 🎨 **Visual Testing**: Automatic screenshot comparison across viewports/themes
- 📝 **Stories**: Easy to write using template and helpers
- ✅ **Quality**: Catch visual bugs before they reach production
- 🚀 **Workflow**: Integrated with GitHub for automatic PR testing
- 📚 **Documentation**: Complete guides and examples provided

## Quick Command Reference

```bash
# Development
bun run storybook              # Start interactive dev server
bun run storybook:build        # Build for Chromatic

# Visual Testing
bun run chromatic              # Run tests (requires token)
bun run chromatic -- --dry     # Test without uploading

# Management
bun scripts/chromatic-snapshot-manager.ts --summary    # Show stats
bun scripts/chromatic-snapshot-manager.ts --list-changed # See changes
```

## You're Ready!

You now understand:
- How visual regression testing works
- How to use Storybook
- How to write visual test stories
- How it integrates with your workflow
- Where to find help and resources

**Next action:** Start Storybook and explore! 🎉

```bash
cd frontend/apps/web
bun run storybook
```

Welcome to the team!
