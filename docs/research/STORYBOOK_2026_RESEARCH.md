# Storybook 8.x Best Practices Research (2026)

**Research Date:** 2026-02-02
**Target:** AI-Coded Projects with React + TypeScript
**Version:** Storybook 8.x

---

## Executive Summary

This document provides comprehensive research on Storybook 8.x best practices specifically tailored for AI-coded projects. The research focuses on:

- Latest addon ecosystem recommendations
- Component testing patterns for React + TypeScript
- Visual regression testing configurations
- Accessibility testing integration
- AI-specific development patterns
- CI/CD automation strategies

---

## 1. Recommended Addons

### 1.1 Core Addons (addon-essentials)

Storybook Essentials is a curated collection maintained by the core team and automatically upgraded alongside Storybook. It provides zero-config setup with recommended defaults.

**Included Addons:**

| Addon | Purpose | Key Features |
|-------|---------|--------------|
| **Actions** | Event visualization | Logs event handlers like `onClick` in the actions panel |
| **Controls** | Dynamic prop editing | Interactive prop manipulation in real-time |
| **Docs** | Documentation generation | Transforms stories into component documentation |
| **Viewport** | Responsive testing | Display stories in different layouts and sizes |
| **Backgrounds** | Background customization | Test components against various backgrounds |
| **Toolbars** | Custom controls | Add custom toolbar controls for global settings |

**Configuration:**

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/your-framework';

const config: StorybookConfig = {
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],
  addons: [
    {
      name: '@storybook/addon-essentials',
      options: {
        // Optionally disable specific addons
        backgrounds: false, // if not needed
        // All addons enabled by default
      },
    },
  ],
};

export default config;
```

**Why for AI Projects:**
- Zero configuration reduces setup complexity
- Consistent behavior across AI-generated stories
- Automatic documentation from generated stories

**Sources:**
- [Essential addons | Storybook docs](https://storybook.js.org/docs/8/essentials)
- [addon-essentials npm](https://www.npmjs.com/package/@storybook/addon-essentials)

---

### 1.2 Visual Testing Addon

**New in Storybook 8:** The headline feature is the Visual Tests addon for automated UI regression testing.

**Key Capabilities:**
- Test all stories simultaneously
- Compare each story to previous versions
- Pinpoint visual changes automatically
- Filter sidebar to show only stories with differences

**Installation:**

```bash
bun add -d @storybook/addon-visual-tests
```

**Configuration:**

```typescript
// .storybook/main.ts
export default {
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-visual-tests',
  ],
};
```

**Why for AI Projects:**
- Catch visual regressions in AI-generated components
- Validate UI consistency across iterations
- Automated regression detection reduces manual QA

**Sources:**
- [Storybook 8 announcement](https://storybook.js.org/blog/storybook-8/)

---

### 1.3 Accessibility Testing (@storybook/addon-a11y)

**Purpose:** Automated accessibility testing using axe-core, which finds 57% of WCAG issues automatically.

**Installation:**

```bash
bun add -d @storybook/addon-a11y
```

**Configuration:**

```typescript
// .storybook/main.ts
export default {
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
  ],
};
```

**Story-Level Configuration:**

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  component: Button,
  parameters: {
    a11y: {
      // Axe configuration
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
        ],
      },
      // Test behavior in CI
      test: 'error', // 'error' | 'todo' | 'skip'
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
};
```

**Best Practices:**

1. **Development Workflow:**
   - Use the accessibility panel during component development
   - Fix violations before committing
   - Use toolbar to simulate vision impairments

2. **CI Configuration:**
   - Set `parameters.a11y.test: 'error'` to fail CI on violations
   - Use `'todo'` for known issues you're tracking separately
   - Combine with automated test runner

3. **Comprehensive Testing:**
   - Test all interactive states (hover, focus, disabled)
   - Include keyboard navigation tests
   - Test with different color schemes

**Why for AI Projects:**
- AI-generated components may miss accessibility requirements
- Automated checks catch common WCAG violations
- Standardizes accessibility across all components

**Sources:**
- [Accessibility tests | Storybook docs](https://storybook.js.org/docs/writing-tests/accessibility-testing)
- [Automate accessibility tests](https://storybook.js.org/blog/automate-accessibility-tests-with-storybook/)

---

### 1.4 Interaction Testing (Built-in)

**Purpose:** Test user interactions using play functions with Testing Library and Vitest.

**Key Features:**
- Built-in Vitest and Testing Library integration
- Visual debugging via Interactions panel
- Real browser testing
- Component-level unit tests

**Installation:**

```bash
bun add -d @storybook/test
```

**Basic Usage:**

```typescript
// LoginForm.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { within, userEvent, expect } from '@storybook/test';
import { LoginForm } from './LoginForm';

const meta: Meta<typeof LoginForm> = {
  component: LoginForm,
};

export default meta;
type Story = StoryObj<typeof LoginForm>;

export const FilledForm: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Simulate user interactions
    await userEvent.type(canvas.getByLabelText('Email'), 'user@example.com');
    await userEvent.type(canvas.getByLabelText('Password'), 'password123');

    // Assert on results
    await expect(canvas.getByRole('button', { name: 'Login' })).toBeEnabled();
  },
};

export const SubmitsForm: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    await userEvent.type(canvas.getByLabelText('Email'), 'user@example.com');
    await userEvent.type(canvas.getByLabelText('Password'), 'password123');
    await userEvent.click(canvas.getByRole('button', { name: 'Login' }));

    // Assert on post-submission state
    await expect(canvas.getByText('Loading...')).toBeInTheDocument();
  },
};
```

**Best Practices:**

1. **Always use `canvas` for queries:**
   ```typescript
   // ✅ Correct - scoped to story
   const canvas = within(canvasElement);
   const button = canvas.getByRole('button');

   // ❌ Wrong - queries entire document
   const button = screen.getByRole('button');
   ```

2. **Always await user events and assertions:**
   ```typescript
   // ✅ Correct
   await userEvent.click(button);
   await expect(result).toBe(expected);

   // ❌ Wrong - won't log properly
   userEvent.click(button);
   expect(result).toBe(expected);
   ```

3. **Use `screen` only for elements outside canvas:**
   ```typescript
   import { screen } from '@storybook/test';

   // For dialogs/portals outside story root
   const dialog = screen.getByRole('dialog');
   ```

4. **Destructure `mount` when needed:**
   ```typescript
   export const AsyncStory: Story = {
     play: async ({ mount, canvasElement }) => {
       // Mount the component manually
       await mount(<Component />);

       const canvas = within(canvasElement);
       // ... rest of test
     },
   };
   ```

**Why for AI Projects:**
- Validate AI-generated component logic
- Test complex user workflows automatically
- Visual debugging without external tools
- Stories become executable tests

**Sources:**
- [Interaction tests | Storybook docs](https://storybook.js.org/docs/writing-tests/interaction-testing)
- [Play function | Storybook docs](https://storybook.js.org/docs/writing-stories/play-function)

---

### 1.5 Test Coverage (@storybook/addon-coverage)

**Purpose:** Generate code coverage reports from your Storybook tests.

**Installation:**

```bash
bun add -d @storybook/addon-coverage vite-plugin-istanbul
```

**Configuration:**

```typescript
// .storybook/main.ts
const config: StorybookConfig = {
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-coverage',
  ],
  viteFinal: async (config) => {
    // Add istanbul plugin for coverage instrumentation
    config.plugins?.push(
      require('vite-plugin-istanbul')({
        include: 'src/**/*',
        exclude: ['node_modules', 'test/'],
        extension: ['.ts', '.tsx'],
        requireEnv: false,
      })
    );
    return config;
  },
};
```

**Running Tests with Coverage:**

```bash
# Via Vitest (recommended for Vite projects)
bun test --coverage

# Via test-runner
bun test-storybook --coverage
```

**Viewing Coverage:**

- Summary displayed in testing widget
- Full interactive report at `/coverage/index.html`
- Coverage reports saved to `./coverage` directory

**CI Configuration:**

```json
// package.json
{
  "scripts": {
    "test-storybook:ci": "concurrently -k -s first -n \"SB,TEST\" -c \"magenta,blue\" \"bun build-storybook --quiet && npx http-server storybook-static --port 6006 --silent\" \"wait-on tcp:6006 && bun test-storybook --coverage\""
  }
}
```

**Why for AI Projects:**
- Measure test coverage from AI-generated stories
- Identify untested code paths
- Track coverage improvements over time

**Sources:**
- [Test coverage | Storybook docs](https://storybook.js.org/docs/writing-tests/test-coverage)
- [Code coverage with test runner](https://storybook.js.org/blog/code-coverage-with-the-storybook-test-runner/)

---

### 1.6 Additional Recommended Addons

| Addon | Purpose | Installation | AI Relevance |
|-------|---------|--------------|--------------|
| **MSW (Mock Service Worker)** | Mock API requests | `@storybook/addon-msw` | Test AI-generated components with API dependencies |
| **Pseudo States** | CSS pseudo-classes | `@storybook/addon-pseudo-states` | Test hover/focus/active states automatically |
| **Design Tokens** | Design system integration | `@storybook/addon-design-tokens` | Document design tokens in stories |
| **Measure** | Layout measurements | `@storybook/addon-measure` | Debug spacing and alignment issues |

---

## 2. Visual Regression Testing

### 2.1 Chromatic (Recommended for Storybook Projects)

**Why Chromatic:**
- Built by the Storybook team
- Deepest Storybook integration
- Automatic story-to-test conversion
- Excellent for component-driven development

**Key Features:**
- Pixel-perfect screenshot comparison
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Multiple viewport testing
- Theme/mode testing
- Parallel test execution
- Collaboration features

**Setup:**

```bash
# Install
bun add -d chromatic

# First run (generates project token)
bunx chromatic --project-token=<your-token>

# Add to package.json
{
  "scripts": {
    "chromatic": "chromatic"
  }
}
```

**Configuration:**

```typescript
// .storybook/main.ts
export default {
  addons: [
    '@storybook/addon-essentials',
    '@chromatic-com/storybook', // Chromatic addon
  ],
};
```

**Story Configuration:**

```typescript
// Component.stories.tsx
const meta: Meta<typeof Component> = {
  component: Component,
  parameters: {
    chromatic: {
      // Test specific viewports
      viewports: [320, 1200],
      // Delay before snapshot
      delay: 300,
      // Disable for specific stories
      disableSnapshot: false,
    },
  },
};
```

**CI Integration (GitHub Actions):**

```yaml
# .github/workflows/chromatic.yml
name: Chromatic
on: push

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: bun install
      - run: bunx chromatic --project-token=${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

**Pricing (2026):**
- Free tier: 5,000 snapshots/month
- Paid plans: Starting at $149/month

**When to Choose Chromatic:**
- Primary focus is component development
- Using Storybook extensively
- Need tight Storybook integration
- Want collaborative review workflow

**Sources:**
- [Visual testing for Storybook • Chromatic](https://www.chromatic.com/storybook)
- [Chromatic addon](https://github.com/chromaui/addon-visual-tests)

---

### 2.2 Percy (Alternative for Full-Page Testing)

**Why Percy:**
- Better for full-page testing
- AI-powered visual diffing
- Broader testing capabilities beyond components
- Strong CI integration

**Key Features:**
- Full-page and component testing
- AI to ignore dynamic content
- Cross-browser and cross-device testing
- Robust CI integration
- Real device testing (unlike Chromatic)

**Setup:**

```bash
bun add -d @percy/cli @percy/storybook
```

**Configuration:**

```javascript
// .percy.yml
version: 2
storybook:
  args: '--ci'
```

**Running Percy:**

```bash
bunx percy storybook http://localhost:6006
```

**CI Integration:**

```yaml
# .github/workflows/percy.yml
name: Percy
on: [push]

jobs:
  percy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: bun install
      - run: bun build-storybook
      - run: bunx percy storybook ./storybook-static
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}
```

**When to Choose Percy:**
- Need full-page visual testing
- Require real device testing
- AI-powered diff detection is important
- Testing beyond just components

**Comparison:**

| Feature | Chromatic | Percy |
|---------|-----------|-------|
| Storybook Integration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Component Testing | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Full-Page Testing | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| AI Diffing | ❌ | ✅ |
| Real Devices | ❌ | ✅ |
| Collaboration | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Pricing | $$ | $$$ |

**Sources:**
- [Percy vs Chromatic comparison](https://medium.com/@crissyjoshua/percy-vs-chromatic-which-visual-regression-testing-tool-to-use-6cdce77238dc)
- [Visual Regression Testing comparison](https://sparkbox.com/foundry/visual_regression_testing_with_backstopjs_applitools_webdriverio_wraith_percy_chromatic)

---

### 2.3 Applitools (AI-Powered Alternative)

**Key Features:**
- Visual AI mimics human perception
- Tests in Storybook UI directly
- Real-time debugging
- Cross-browser testing

**When to Use:**
- Need advanced AI visual testing
- Want in-Storybook testing experience
- Budget for premium tooling

**Sources:**
- [Visual Testing Storybook - Applitools](https://applitools.com/solutions/storybook/)

---

## 3. Component Testing Patterns (React + TypeScript)

### 3.1 CSF3 Format (Component Story Format 3)

**Why CSF3:**
- Less boilerplate than CSF2
- Better TypeScript support
- Improved ergonomics
- AI-friendly syntax

**CSF2 vs CSF3 Comparison:**

```typescript
// ❌ CSF2 (Old Style)
import { ComponentMeta, ComponentStory } from '@storybook/react';
import { Button } from './Button';

export default {
  title: 'Components/Button',
  component: Button,
} as ComponentMeta<typeof Button>;

const Template: ComponentStory<typeof Button> = (args) => <Button {...args} />;

export const Primary = Template.bind({});
Primary.args = {
  variant: 'primary',
  children: 'Button',
};

// ✅ CSF3 (New Style)
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  component: Button,
  // Auto-title based on file location
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = {
  args: {
    variant: 'primary',
    children: 'Button',
  },
};
```

**TypeScript Configuration:**

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true, // Required for type inference
    "strictBindCallApply": true // Required for proper types
  }
}
```

**Migration:**

```bash
# Automatic migration from CSF2 to CSF3
npx storybook@latest migrate csf-2-to-3 --glob="**/*.stories.tsx"
```

**Why for AI Projects:**
- Simpler syntax for AI to generate
- Fewer errors from boilerplate
- Better type inference reduces bugs
- Auto-title reduces manual configuration

**Sources:**
- [Component Story Format 3 is here](https://storybook.js.org/blog/storybook-csf3-is-here/)
- [CSF3 side-by-side comparison](https://mostafakmilly.vercel.app/blog/storybook-component-story-format-3-a-side-by-side-comparison/)

---

### 3.2 Story Composition Patterns

**1. Shared Meta Configuration:**

```typescript
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'tertiary'],
    },
    size: {
      control: 'radio',
      options: ['small', 'medium', 'large'],
    },
  },
  decorators: [
    (Story) => (
      <div style={{ padding: '1rem' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Button>;
```

**2. Story Variants:**

```typescript
// Create variations efficiently
export const Small: Story = {
  args: {
    size: 'small',
    children: 'Small Button',
  },
};

export const Medium: Story = {
  args: {
    size: 'medium',
    children: 'Medium Button',
  },
};

export const Large: Story = {
  args: {
    size: 'large',
    children: 'Large Button',
  },
};

// Extend existing stories
export const LargePrimary: Story = {
  ...Large,
  args: {
    ...Large.args,
    variant: 'primary',
  },
};
```

**3. Interactive States:**

```typescript
// Test all interactive states
export const AllStates: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column' }}>
      <Button>Default</Button>
      <Button data-hover>Hover</Button>
      <Button data-focus>Focus</Button>
      <Button data-active>Active</Button>
      <Button disabled>Disabled</Button>
    </div>
  ),
  parameters: {
    pseudo: {
      hover: '[data-hover]',
      focus: '[data-focus]',
      active: '[data-active]',
    },
  },
};
```

**4. Component with Dependencies:**

```typescript
import { within, userEvent } from '@storybook/test';
import { http, HttpResponse } from 'msw';

const meta: Meta<typeof UserProfile> = {
  component: UserProfile,
  parameters: {
    msw: {
      handlers: [
        http.get('/api/user/:id', () => {
          return HttpResponse.json({
            id: 1,
            name: 'John Doe',
            email: 'john@example.com',
          });
        }),
      ],
    },
  },
};

export const LoadedState: Story = {
  args: {
    userId: 1,
  },
};

export const LoadingState: Story = {
  args: {
    userId: 1,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/user/:id', async () => {
          // Delay response to show loading state
          await new Promise(resolve => setTimeout(resolve, 10000));
          return HttpResponse.json({});
        }),
      ],
    },
  },
};

export const ErrorState: Story = {
  args: {
    userId: 999,
  },
  parameters: {
    msw: {
      handlers: [
        http.get('/api/user/:id', () => {
          return HttpResponse.json(
            { error: 'User not found' },
            { status: 404 }
          );
        }),
      ],
    },
  },
};
```

---

### 3.3 Testing Library Integration

**Best Practices:**

```typescript
import { within, userEvent, expect, waitFor } from '@storybook/test';

export const InteractiveForm: Story = {
  play: async ({ canvasElement, step }) => {
    const canvas = within(canvasElement);

    // Use step() to organize tests
    await step('Fill out form', async () => {
      await userEvent.type(
        canvas.getByLabelText('Name'),
        'John Doe'
      );
      await userEvent.type(
        canvas.getByLabelText('Email'),
        'john@example.com'
      );
    });

    await step('Submit form', async () => {
      await userEvent.click(
        canvas.getByRole('button', { name: 'Submit' })
      );
    });

    await step('Verify success', async () => {
      await waitFor(async () => {
        await expect(
          canvas.getByText('Form submitted successfully')
        ).toBeInTheDocument();
      });
    });
  },
};
```

**Query Priorities (from Testing Library):**

1. **Accessible queries (Preferred):**
   - `getByRole`
   - `getByLabelText`
   - `getByPlaceholderText`
   - `getByText`

2. **Semantic queries:**
   - `getByAltText`
   - `getByTitle`

3. **Test IDs (Last resort):**
   - `getByTestId`

**Sources:**
- [Component tests | Storybook docs](https://storybook.js.org/docs/8/writing-tests/component-testing)
- [Testing Library integration](https://medium.com/storybookjs/testing-lib-storybook-react-8c36716fab86)

---

### 3.4 Portable Stories Pattern

**Purpose:** Reuse Storybook stories in unit tests (Jest, Vitest, etc.)

```typescript
// Component.test.tsx
import { composeStories } from '@storybook/react';
import { render, screen } from '@testing-library/react';
import * as stories from './Component.stories';

const { Primary, Secondary } = composeStories(stories);

test('renders primary button', () => {
  render(<Primary />);
  expect(screen.getByRole('button')).toBeInTheDocument();
});

test('runs play function', async () => {
  const { container } = render(<Primary />);

  // Execute the play function from the story
  if (Primary.play) {
    await Primary.play({ canvasElement: container });
  }

  // Assert on results
  expect(screen.getByText('Expected result')).toBeInTheDocument();
});
```

**Why for AI Projects:**
- Stories become single source of truth
- Reduce test duplication
- Apply decorators/args to unit tests
- Consistent testing across tools

**Sources:**
- [Stories in unit tests | Storybook docs](https://storybook.js.org/docs/writing-tests/stories-in-unit-tests/)

---

## 4. AI-Specific Considerations

### 4.1 StorybookGPT and AI Integrations

**Storybook MCP Addon:**

A Model Context Protocol (MCP) server exists specifically for AI agents working with Storybook:

```bash
bun add -d @storybookjs/addon-mcp
```

**What it provides:**
- Helps AI agents write stories in CSF3 format
- Ensures consistency with project conventions
- Automatically generates and links stories for components
- Provides component development best practices

**AI Agent Instructions:**

When working with AI tools (Claude Code, Cursor, etc.), provide these instructions:

```markdown
When creating or modifying UI components:

1. Always generate corresponding Storybook stories
2. Use CSF3 format (not CSF2)
3. Include multiple story variants:
   - Default state
   - All prop variations
   - Interactive states (hover, focus, disabled)
   - Loading/error states
   - Edge cases
4. Add play functions for interactive components
5. Configure accessibility testing
6. Document props with JSDoc comments
```

**Sources:**
- [Build your own Storybook GPT](https://storybook.js.org/blog/build-your-own-storybook-gpt/)
- [Storybook MCP addon](https://mcpindex.net/en/mcpserver/storybookjs-addon-mcp)

---

### 4.2 AI-Powered Story Generation

**Automated Story Generation:**

Teams have built custom AI generators that save 100+ developer hours:

```typescript
// Example AI-generated story template
import type { Meta, StoryObj } from '@storybook/react';
import { Component } from './Component';

/**
 * AI-generated stories for Component
 * Generated: ${timestamp}
 * Coverage: ${coveragePercentage}%
 */
const meta: Meta<typeof Component> = {
  component: Component,
  tags: ['autodocs', 'ai-generated'],
};

export default meta;
type Story = StoryObj<typeof Component>;

// AI generates comprehensive prop combinations
${generatedStories}
```

**Benefits:**
- Consistent documentation across components
- Edge cases AI might discover
- Massive time savings (100+ hours for 200 components)
- Fill in gaps left by manual work

**Quality Assurance:**
- Human review of generated stories
- Verify accuracy of functionality
- Check for missing edge cases
- Validate accessibility compliance

**Sources:**
- [Supercharging Design Systems with AI](https://medium.com/zencity-engineering/supercharging-design-systems-5ec043d3d055)
- [AI-powered Storybook assistant](https://github.com/flight505/storybook-assistant)

---

### 4.3 Cursor + Storybook Workflow

**Browser-Aware Testing:**

Cursor's AI agent can:
1. Open Storybook in browser
2. Navigate through components
3. Take screenshots to verify states
4. Self-correct and iterate on issues

**Workflow:**
```
1. AI generates component + story
2. Storybook renders component
3. AI opens browser to verify
4. AI takes screenshot
5. AI analyzes visual result
6. AI corrects issues
7. Repeat until correct
```

**Why it works:**
- Visual verification catches AI mistakes
- Immediate feedback loop
- Self-correcting behavior
- Reduces human review time

**Sources:**
- [Rapid Frontend Prototyping with AI, Cursor & Storybook](https://www.uxpin.com/studio/blog/rapid-frontend-prototyping-ai-cursor-storybook/)

---

### 4.4 AI Testing Best Practices

**1. Generate Comprehensive Coverage:**

```typescript
// AI should generate stories for:
// - All prop combinations
// - All component states
// - Error conditions
// - Loading states
// - Empty states
// - Edge cases

const meta: Meta<typeof DataTable> = {
  component: DataTable,
};

export default meta;
type Story = StoryObj<typeof DataTable>;

export const Default: Story = {
  args: {
    data: mockData,
  },
};

export const Empty: Story = {
  args: {
    data: [],
  },
};

export const Loading: Story = {
  args: {
    data: [],
    isLoading: true,
  },
};

export const Error: Story = {
  args: {
    data: [],
    error: 'Failed to load data',
  },
};

export const LargeDataset: Story = {
  args: {
    data: generateMockData(1000),
  },
};

export const WithPagination: Story = {
  args: {
    data: mockData,
    pagination: {
      page: 1,
      pageSize: 10,
      total: 100,
    },
  },
};
```

**2. Include Play Functions:**

```typescript
// AI should add interaction tests
export const SortableColumns: Story = {
  args: {
    data: mockData,
    sortable: true,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);

    // Click column header to sort
    await userEvent.click(
      canvas.getByRole('button', { name: 'Name' })
    );

    // Verify sort indicator
    await expect(
      canvas.getByLabelText('Sorted ascending')
    ).toBeInTheDocument();
  },
};
```

**3. Document with JSDoc:**

```typescript
/**
 * DataTable component displays tabular data with sorting, filtering, and pagination.
 *
 * @component
 * @example
 * <DataTable
 *   data={users}
 *   columns={['name', 'email', 'role']}
 *   sortable
 *   pagination={{ page: 1, pageSize: 10 }}
 * />
 */
export const DataTable = ({ data, columns, ...props }: DataTableProps) => {
  // Implementation
};
```

---

## 5. CI/CD Integration

### 5.1 GitHub Actions Configuration

**Option 1: Test Against Deployed Storybook (Recommended)**

```yaml
# .github/workflows/storybook-tests.yml
name: Storybook Tests
on: deployment_status

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: bun install

      - name: Run Storybook tests
        run: bun test-storybook
        env:
          TARGET_URL: '${{ github.event.deployment_status.target_url }}'

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          directory: ./coverage
```

**Option 2: Build and Test Locally**

```yaml
# .github/workflows/storybook-tests.yml
name: Storybook Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: bun install

      - name: Build and test Storybook
        run: bun run test-storybook:ci

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          directory: ./coverage
```

**Package.json Scripts:**

```json
{
  "scripts": {
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "test-storybook": "test-storybook",
    "test-storybook:ci": "concurrently -k -s first -n \"SB,TEST\" -c \"magenta,blue\" \"bun build-storybook --quiet && npx http-server storybook-static --port 6006 --silent\" \"wait-on tcp:6006 && bun test-storybook --coverage\""
  }
}
```

**Sources:**
- [Test runner | Storybook docs](https://storybook.js.org/docs/writing-tests/integrations/test-runner)
- [Testing in CI | Storybook docs](https://storybook.js.org/docs/writing-tests/in-ci)

---

### 5.2 Visual Regression in CI

**Chromatic CI:**

```yaml
# .github/workflows/chromatic.yml
name: Chromatic

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # Required for Chromatic

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: bun install

      - name: Run Chromatic
        uses: chromaui/action@latest
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          exitZeroOnChanges: true # Don't fail on visual changes
          exitOnceUploaded: true # Speed up builds
```

**Percy CI:**

```yaml
# .github/workflows/percy.yml
name: Percy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  percy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: bun install

      - name: Build Storybook
        run: bun build-storybook

      - name: Run Percy
        run: bunx percy storybook ./storybook-static
        env:
          PERCY_TOKEN: ${{ secrets.PERCY_TOKEN }}
```

---

### 5.3 Accessibility Testing in CI

```yaml
# .github/workflows/a11y-tests.yml
name: Accessibility Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install dependencies
        run: bun install

      - name: Build Storybook
        run: bun build-storybook

      - name: Run accessibility tests
        run: |
          bunx concurrently -k -s first -n "SB,TEST" \
            "bunx http-server storybook-static --port 6006 --silent" \
            "bunx wait-on tcp:6006 && bun test-storybook --coverage"
        env:
          STORYBOOK_A11Y_TEST: 'error' # Fail on violations

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: a11y-results
          path: .test-results/
```

---

## 6. Configuration Templates

### 6.1 Complete Storybook Configuration

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/react-vite';
import { mergeConfig } from 'vite';

const config: StorybookConfig = {
  stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|jsx|mjs|ts|tsx)'],

  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-coverage',
    '@storybook/addon-visual-tests',
    '@storybook/addon-interactions',
  ],

  framework: {
    name: '@storybook/react-vite',
    options: {
      builder: {
        viteConfigPath: '.storybook/vite.config.ts',
      },
    },
  },

  docs: {
    autodocs: 'tag',
  },

  typescript: {
    check: true,
    reactDocgen: 'react-docgen-typescript',
    reactDocgenTypescriptOptions: {
      shouldExtractLiteralValuesFromEnum: true,
      shouldRemoveUndefinedFromOptional: true,
      propFilter: (prop) => {
        // Filter out props from node_modules except specific ones
        if (prop.parent) {
          return !prop.parent.fileName.includes('node_modules');
        }
        return true;
      },
    },
  },

  viteFinal: async (config) => {
    return mergeConfig(config, {
      plugins: [
        // Add istanbul for coverage
        require('vite-plugin-istanbul')({
          include: 'src/**/*',
          exclude: ['node_modules', '**/*.stories.tsx', '**/*.test.tsx'],
          extension: ['.ts', '.tsx'],
          requireEnv: false,
        }),
      ],
    });
  },
};

export default config;
```

---

### 6.2 Preview Configuration

```typescript
// .storybook/preview.ts
import type { Preview } from '@storybook/react';
import { themes } from '@storybook/theming';

const preview: Preview = {
  parameters: {
    // Actions
    actions: { argTypesRegex: '^on[A-Z].*' },

    // Controls
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
      expanded: true,
      sort: 'requiredFirst',
    },

    // Backgrounds
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a1a' },
        { name: 'gray', value: '#f5f5f5' },
      ],
    },

    // Viewport
    viewport: {
      viewports: {
        mobile: {
          name: 'Mobile',
          styles: { width: '375px', height: '667px' },
        },
        tablet: {
          name: 'Tablet',
          styles: { width: '768px', height: '1024px' },
        },
        desktop: {
          name: 'Desktop',
          styles: { width: '1920px', height: '1080px' },
        },
      },
    },

    // Accessibility
    a11y: {
      config: {
        rules: [
          {
            id: 'color-contrast',
            enabled: true,
          },
          {
            id: 'label',
            enabled: true,
          },
        ],
      },
      test: 'error', // Fail CI on violations
    },

    // Docs
    docs: {
      theme: themes.light,
    },
  },

  // Global decorators
  decorators: [
    (Story) => (
      <div style={{ padding: '2rem' }}>
        <Story />
      </div>
    ),
  ],

  // Tags
  tags: ['autodocs'],
};

export default preview;
```

---

### 6.3 Story Template

```typescript
// src/components/Component.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { within, userEvent, expect } from '@storybook/test';
import { Component } from './Component';

/**
 * Component description goes here.
 *
 * ## Usage
 *
 * ```tsx
 * <Component prop="value" />
 * ```
 */
const meta: Meta<typeof Component> = {
  title: 'Components/Component',
  component: Component,
  tags: ['autodocs'],

  parameters: {
    docs: {
      description: {
        component: 'Detailed component documentation.',
      },
    },
  },

  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary'],
      description: 'Visual variant',
    },
  },

  decorators: [
    (Story) => (
      <div style={{ padding: '1rem' }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof Component>;

/**
 * Default component state
 */
export const Default: Story = {
  args: {
    // Default props
  },
};

/**
 * Interactive example with user interactions
 */
export const Interactive: Story = {
  args: {
    // Props
  },
  play: async ({ canvasElement, step }) => {
    const canvas = within(canvasElement);

    await step('Initial state', async () => {
      await expect(canvas.getByRole('button')).toBeInTheDocument();
    });

    await step('User interaction', async () => {
      await userEvent.click(canvas.getByRole('button'));
      await expect(canvas.getByText('Result')).toBeInTheDocument();
    });
  },
};

/**
 * All visual states
 */
export const AllStates: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: '1rem', flexDirection: 'column' }}>
      <Component>Default</Component>
      <Component data-hover>Hover</Component>
      <Component data-focus>Focus</Component>
      <Component disabled>Disabled</Component>
    </div>
  ),
  parameters: {
    pseudo: {
      hover: '[data-hover]',
      focus: '[data-focus]',
    },
  },
};
```

---

## 7. Best Practices Summary

### 7.1 Development Workflow

1. **Component-First Development:**
   - Create component
   - Write stories immediately
   - Test in isolation
   - Iterate visually

2. **Story Coverage:**
   - Default state
   - All prop variations
   - Interactive states
   - Loading/error states
   - Edge cases

3. **Testing Strategy:**
   - Visual tests (Chromatic/Percy)
   - Interaction tests (play functions)
   - Accessibility tests (@storybook/addon-a11y)
   - Unit tests (portable stories)

4. **CI/CD Pipeline:**
   - Run test-runner on PR
   - Visual regression on PR
   - Accessibility checks (fail on error)
   - Coverage reporting

---

### 7.2 AI-Specific Guidelines

1. **Story Generation:**
   - Always use CSF3 format
   - Generate comprehensive variants
   - Include play functions
   - Add JSDoc documentation

2. **Quality Checks:**
   - Human review of generated stories
   - Verify accessibility compliance
   - Check visual regression results
   - Validate interaction tests

3. **Consistency:**
   - Use story templates
   - Follow naming conventions
   - Maintain file structure
   - Document patterns

---

### 7.3 Performance Optimization

1. **Build Performance:**
   - Use Vite for fast dev server
   - Enable SWC for faster transpilation
   - Lazy load heavy dependencies
   - Split stories into modules

2. **Test Performance:**
   - Run tests in parallel
   - Use selective testing in CI
   - Cache dependencies
   - Optimize visual tests

3. **Runtime Performance:**
   - Mock API calls
   - Use MSW for network requests
   - Lazy load components
   - Optimize re-renders

---

## 8. Migration Guide

### 8.1 From Storybook 7 to 8

```bash
# Automated migration
npx storybook@latest upgrade

# Run codemods
npx storybook@latest automigrate
```

**Key Changes:**
- New Visual Tests addon
- Improved Vitest integration
- Better TypeScript support
- Performance improvements

---

### 8.2 From CSF2 to CSF3

```bash
# Automated migration
npx storybook@latest migrate csf-2-to-3 --glob="**/*.stories.tsx"
```

**Manual Changes:**
- Replace `ComponentMeta` with `Meta`
- Replace `ComponentStory` with `StoryObj`
- Remove `Template.bind({})`
- Use direct story objects

---

## 9. Resources and References

### Official Documentation
- [Storybook 8 Documentation](https://storybook.js.org/docs/8)
- [Writing Tests | Storybook](https://storybook.js.org/docs/writing-tests)
- [Component Story Format 3](https://storybook.js.org/blog/storybook-csf3-is-here/)
- [Storybook Addons](https://storybook.js.org/addons)

### Visual Testing
- [Visual testing for Storybook • Chromatic](https://www.chromatic.com/storybook)
- [Percy vs Chromatic comparison](https://medium.com/@crissyjoshua/percy-vs-chromatic-which-visual-regression-testing-tool-to-use-6cdce77238dc)
- [Visual Tests addon](https://github.com/chromaui/addon-visual-tests)

### Accessibility
- [Accessibility tests | Storybook docs](https://storybook.js.org/docs/writing-tests/accessibility-testing)
- [Automate accessibility tests](https://storybook.js.org/blog/automate-accessibility-tests-with-storybook/)
- [Accessibility testing tutorial](https://storybook.js.org/tutorials/ui-testing-handbook/react/en/accessibility-testing/)

### Interaction Testing
- [Interaction tests | Storybook docs](https://storybook.js.org/docs/writing-tests/interaction-testing)
- [Play function | Storybook docs](https://storybook.js.org/docs/writing-stories/play-function)
- [Component tests | Storybook docs](https://storybook.js.org/docs/8/writing-tests/component-testing)

### AI Integration
- [Build your own Storybook GPT](https://storybook.js.org/blog/build-your-own-storybook-gpt/)
- [Supercharging Design Systems with AI](https://medium.com/zencity-engineering/supercharging-design-systems-5ec043d3d055)
- [Rapid Frontend Prototyping with AI, Cursor & Storybook](https://www.uxpin.com/studio/blog/rapid-frontend-prototyping-ai-cursor-storybook/)
- [AI-powered Storybook assistant](https://github.com/flight505/storybook-assistant)

### CI/CD
- [Test runner | Storybook docs](https://storybook.js.org/docs/writing-tests/integrations/test-runner)
- [Testing in CI | Storybook docs](https://storybook.js.org/docs/writing-tests/in-ci)
- [Automate UI tests with GitHub Actions](https://storybook.js.org/tutorials/ui-testing-handbook/react/en/automate/)

### Coverage
- [Test coverage | Storybook docs](https://storybook.js.org/docs/writing-tests/test-coverage)
- [Code coverage with test runner](https://storybook.js.org/blog/code-coverage-with-the-storybook-test-runner/)

---

## 10. Recommended Package.json

```json
{
  "name": "your-project",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "storybook": "storybook dev -p 6006",
    "build-storybook": "storybook build",
    "test": "vitest",
    "test-storybook": "test-storybook",
    "test-storybook:ci": "concurrently -k -s first -n \"SB,TEST\" -c \"magenta,blue\" \"bun build-storybook --quiet && npx http-server storybook-static --port 6006 --silent\" \"wait-on tcp:6006 && bun test-storybook --coverage\"",
    "chromatic": "chromatic"
  },
  "devDependencies": {
    "@storybook/addon-a11y": "^8.5.0",
    "@storybook/addon-coverage": "^1.0.0",
    "@storybook/addon-essentials": "^8.5.0",
    "@storybook/addon-interactions": "^8.5.0",
    "@storybook/addon-visual-tests": "^8.5.0",
    "@storybook/react": "^8.5.0",
    "@storybook/react-vite": "^8.5.0",
    "@storybook/test": "^8.5.0",
    "@storybook/test-runner": "^0.19.0",
    "chromatic": "^11.0.0",
    "concurrently": "^8.2.0",
    "http-server": "^14.1.1",
    "storybook": "^8.5.0",
    "vite-plugin-istanbul": "^6.0.0",
    "vitest": "^2.0.0",
    "wait-on": "^7.2.0"
  }
}
```

---

## Conclusion

Storybook 8.x provides a comprehensive testing and development platform for AI-coded React + TypeScript projects. By following these best practices and configurations, you can:

- Automate visual regression testing
- Ensure accessibility compliance
- Write comprehensive interaction tests
- Generate test coverage from stories
- Integrate with CI/CD pipelines
- Leverage AI for story generation

The key to success is treating stories as first-class citizens in your testing strategy and using AI tools to generate comprehensive coverage while maintaining human oversight for quality assurance.
