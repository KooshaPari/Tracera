# Quick Start Guide - Storybook Story Generator

## Installation

Already done! Dependencies are installed.

## Basic Usage

### 1. Generate All Stories

```bash
cd /Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend
bun run generate:stories
```

This will:

- Scan all components in `packages/ui/src/components/` and `apps/web/src/components/`
- Generate CSF 3.0 stories in `apps/storybook/src/stories/`
- Create an example design metadata file at `.trace/.meta/designs.yaml` if it doesn't exist
- Skip existing stories (use `--force` to overwrite)

### 2. Generate for Specific Component

```bash
bun run generate:stories --component Button
```

### 3. Force Regenerate (Overwrite Existing)

```bash
bun run generate:stories --force
```

### 4. Verbose Output

```bash
bun run generate:stories --verbose
```

## What Gets Generated

For a component like `Button.tsx` with CVA variants:

```typescript
// packages/ui/src/components/Button.tsx
const buttonVariants = cva('base', {
  variants: {
    variant: { default: '...', destructive: '...', outline: '...' },
    size: { default: '...', sm: '...', lg: '...' },
  },
  defaultVariants: { variant: 'default', size: 'default' },
});
```

You get:

```typescript
// apps/storybook/src/stories/Button.stories.tsx
export const Default: Story = { args: { variant: 'default' } };
export const Destructive: Story = { args: { variant: 'destructive' } };
export const Outline: Story = { args: { variant: 'outline' } };
export const Sm: Story = { args: { size: 'sm' } };
export const Lg: Story = { args: { size: 'lg' } };
export const AllVariants: Story = {
  /* showcase render */
};
```

## Adding Figma Links

Edit `.trace/.meta/designs.yaml`:

```yaml
components:
  Button:
    figmaUrl: 'https://www.figma.com/file/YOUR-FILE-ID/Design-System?node-id=123'
    componentId: 'comp-button-001'
    storyId: 'story-button-001'
```

Then regenerate:

```bash
bun run generate:stories --component Button --force
```

## View in Storybook

```bash
bun run dev:storybook
```

Open http://localhost:6006

## Workflow Tips

### After Creating a New Component

```bash
# 1. Create your component
# packages/ui/src/components/NewComponent.tsx

# 2. Generate its story
bun run generate:stories --component NewComponent

# 3. Add Figma link (optional)
# Edit .trace/.meta/designs.yaml

# 4. Regenerate with Figma link
bun run generate:stories --component NewComponent --force

# 5. View in Storybook
bun run dev:storybook
```

### Batch Regenerate All Stories

```bash
bun run generate:stories --force
```

### Generate Only New Stories

```bash
bun run generate:stories
```

This skips existing stories, only creating new ones.

## Supported Component Patterns

### ✅ CVA Components (Best Support)

```typescript
import { cva, type VariantProps } from 'class-variance-authority'

const variants = cva('base', {
  variants: { variant: { default: '...', primary: '...' } }
})

export interface ButtonProps extends VariantProps<typeof variants> {}
export const Button = forwardRef<HTMLButtonElement, ButtonProps>(...)
```

**Generates:** Stories for each variant with controls

### ✅ Standard Components

```typescript
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}
export const Input = forwardRef<HTMLInputElement, InputProps>(...)
```

**Generates:** Basic story with auto-detected props

### ✅ Composite Components

```typescript
export const Card = ...
export const CardHeader = ...
export const CardTitle = ...
```

**Generates:** Story for the main component (Card)

## Troubleshooting

### "No components found"

Check that:

- Component files are `.tsx`
- Files are in `packages/ui/src/components/` or `apps/web/src/components/`
- Files aren't named `*.test.tsx` or `*.stories.tsx`

### Import path errors

Update `config.ts` `importPathMapping` if you have custom package names:

```typescript
importPathMapping: {
  'packages/ui/src/components': '@tracertm/ui',
  'apps/web/src/components': '@tracertm/web/components',
}
```

### Variants not detected

Ensure:

- Using `class-variance-authority` package
- CVA object uses exact structure (see examples)
- Component has `VariantProps<typeof variants>` in props type

## Advanced Usage

### Custom Configuration

Edit `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/tools/storybook-generator/config.ts`:

```typescript
export const defaultConfig: GeneratorConfig = {
  componentsDir: ['packages/ui/src/components'],
  storiesDir: 'apps/storybook/src/stories',
  generateVariants: true,
  generateShowcase: true,
  overwriteExisting: false,
};
```

### Custom Templates

Edit `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/tools/storybook-generator/templates/story.template.ts`

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
cd frontend
bun run generate:stories
git add apps/storybook/src/stories/
```

## Examples

### Generate all UI components

```bash
bun run generate:stories
```

Output:

```
🎨 TraceRTM Storybook Story Generator
=====================================

📦 Found 24 component(s)
🔍 Analyzing components...
✅ Analyzed 11 component(s)

✅ Generated Button.stories.tsx
✅ Generated Input.stories.tsx
✅ Generated Card.stories.tsx
...

✨ Story generation complete!
   Generated: 11
   Skipped: 0
```

### Regenerate specific component

```bash
bun run generate:stories --component Button --force --verbose
```

Output:

```
🎨 TraceRTM Storybook Story Generator
=====================================

📦 Found 1 component(s)
🔍 Analyzing components...
✅ Analyzed 1 component(s)

♻️  Regenerated Button.stories.tsx
   Import: @tracertm/ui
   Variants: 2
   Props: 0
   Figma: https://www.figma.com/file/xxx/Design-System?node-id=123

✨ Story generation complete!
   Generated: 1
   Skipped: 0
```

## Next Steps

1. Generate stories for all components: `bun run generate:stories`
2. Add Figma URLs to `.trace/.meta/designs.yaml`
3. Regenerate with `--force` to include Figma links
4. Start Storybook: `bun run dev:storybook`
5. View your auto-generated stories at http://localhost:6006

## Files Created

```
frontend/
├── tools/storybook-generator/
│   ├── config.ts                   # Configuration
│   ├── analyzer.ts                 # Component analyzer (ts-morph)
│   ├── design-metadata.ts          # YAML loader
│   ├── generate-stories.ts         # Main CLI script
│   ├── templates/
│   │   └── story.template.ts       # Story generator
│   ├── index.ts                    # Exports
│   ├── README.md                   # Full documentation
│   └── QUICKSTART.md              # This file
├── .trace/.meta/designs.yaml       # Design metadata (auto-created)
└── apps/storybook/src/stories/     # Generated stories
    ├── Button.stories.tsx
    ├── Input.stories.tsx
    └── ...
```

## Need Help?

- Full docs: `tools/storybook-generator/README.md`
- Configuration: `tools/storybook-generator/config.ts`
- Issues? Run with `--verbose` flag
