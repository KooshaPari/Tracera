/**
 * Template for Visual Regression Test Stories
 *
 * Use this template when creating new Storybook stories for visual regression testing.
 * Replace COMPONENT_NAME with your actual component name.
 *
 * Reference documentation:
 * - Visual Testing Guide: ../../docs/VISUAL_TESTING_GUIDE.md
 * - Storybook Setup: ../../.storybook/README.md
 */

import type { Meta, StoryObj } from '@storybook/react';

// Import { COMPONENT_NAME } from "../COMPONENT_NAME";

const meta: Meta = {
  // Set the title following the naming convention: Type/Category/ComponentName
  title: 'Components/Graph/ComponentName',
  // Component: COMPONENT_NAME,
  tags: ['autodocs', 'skip-tests'],

  // Configure visual regression testing
  parameters: {
    // Chromatic configuration for visual snapshots
    chromatic: {
      // Test both light and dark modes
      modes: {
        dark: {
          matcherUrl: '**/dark',
          query: "[data-theme='dark']",
        },
        light: {
          matcherUrl: '**/light',
          query: "[data-theme='light']",
        },
      },
      // Delay before taking snapshot (wait for animations)
      // Increase if component has longer animations
      delay: 300,
      // Pause animations at the end for consistency
      pauseAnimationAtEnd: true,
      // Don't skip visual snapshots for this component
      disableSnapshot: false,
    },
    // Define available viewports
    viewport: {
      defaultViewport: 'desktop',
    },
  },

  // Define component props for interactive control in Storybook UI
  argTypes: {
    // Example arg type definitions
    // Variant: {
    // 	Control: "select",
    // 	Options: ["primary", "secondary", "outline"],
    // 	Description: "Button visual style variant",
    // },
    // Disabled: {
    // 	Control: "boolean",
    // 	Description: "Disable the component",
    // },
    // OnClick: {
    // 	Action: "clicked",
    // 	Description: "Click handler",
    // },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * DEFAULT STORY
 * The primary/default state of the component
 *
 * This is the main story that most users will interact with.
 * Use realistic but minimal props to showcase the component's typical usage.
 */
export const Default: Story = {
  args: {
    // Add props for your component
    // Label: "Default Button",
    // Variant: "primary",
  },
};

/**
 * DISABLED STATE
 * Component in disabled state
 *
 * Test that disabled components are visually distinct and cannot be interacted with.
 */
export const Disabled: Story = {
  args: {
    // ...Default.args,
    // Disabled: true,
  },
};

/**
 * MOBILE VIEWPORT
 * Component tested on mobile device size
 *
 * Tests responsive behavior on smaller screens.
 * Viewport: 375x667 (iPhone size)
 */
export const Mobile: Story = {
  args: {
    // ...Default.args,
  },
  parameters: {
    viewport: {
      defaultViewport: 'mobile',
    },
  },
};

/**
 * TABLET VIEWPORT
 * Component tested on tablet device size
 *
 * Tests responsive behavior on medium screens.
 * Viewport: 768x1024 (iPad size)
 */
export const Tablet: Story = {
  args: {
    // ...Default.args,
  },
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

/**
 * DARK MODE
 * Component in dark theme
 *
 * Tests that component is properly themed for dark mode.
 * Light mode is tested automatically, this explicitly tests dark.
 */
export const DarkMode: Story = {
  args: {
    // ...Default.args,
  },
  decorators: [
    (Story) => (
      <div className='dark' data-theme='dark' style={{ minHeight: '100vh' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    chromatic: {
      // Only test dark mode for this variant
      modes: {
        dark: {
          query: "[data-theme='dark']",
        },
      },
    },
  },
};

/**
 * HOVER STATE
 * Component when user hovers over it
 *
 * Uses play function to simulate hover for visual testing.
 * This captures the visual hover effect for regression detection.
 */
export const Hovered: Story = {
  args: {
    // ...Default.args,
  },
  play: async ({ canvasElement }) => {
    // Find the interactive element to hover over
    const element = canvasElement.querySelector('button') ?? canvasElement.firstChild;
    if (element && element instanceof HTMLElement) {
      element.dispatchEvent(
        new MouseEvent('mouseenter', {
          bubbles: true,
          cancelable: true,
          view: window,
        }),
      );
    }
  },
};

/**
 * FOCUS STATE
 * Component when focused (keyboard navigation)
 *
 * Uses play function to simulate focus for keyboard accessibility.
 * Tests that focus styles are visible and provide good contrast.
 */
export const Focused: Story = {
  args: {
    // ...Default.args,
  },
  play: async ({ canvasElement }) => {
    const element = canvasElement.querySelector('button') ?? canvasElement.firstChild;
    if (element instanceof HTMLElement) {
      element.focus();
    }
  },
};

/**
 * ACTIVE STATE
 * Component when in active/pressed state
 *
 * For buttons, toggles, and other interactive elements.
 * Shows the visual feedback when the element is actively being used.
 */
export const Active: Story = {
  args: {
    // ...Default.args,
  },
  play: async ({ canvasElement }) => {
    const element = canvasElement.querySelector('button') ?? canvasElement.firstChild;
    if (element instanceof HTMLElement) {
      element.classList.add('active');
      element.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
    }
  },
};

/**
 * LOADING STATE
 * Component while loading
 *
 * For async components, shows the loading visual state.
 * Example: Spinner, skeleton loader, disabled state with message.
 */
// Export const Loading: Story = {
// 	Args: {
// 		// ...Default.args,
// 		// isLoading: true,
// 	},
// };

/**
 * ERROR STATE
 * Component in error state
 *
 * Shows error messaging and visual indication of error.
 * Example: Red border, error icon, error message text.
 */
// Export const Error: Story = {
// 	Args: {
// 		// ...Default.args,
// 		// error: "Something went wrong",
// 		// status: "error",
// 	},
// };

/**
 * SUCCESS STATE
 * Component after successful action
 *
 * Shows success messaging and visual indication of success.
 * Example: Green checkmark, success message.
 */
// Export const Success: Story = {
// 	Args: {
// 		// ...Default.args,
// 		// status: "success",
// 		// message: "Successfully updated",
// 	},
// };

/**
 * ALL VARIANTS
 * Showcase all component variants together
 *
 * Useful for comparing different variants side-by-side.
 * Helps catch inconsistencies between variants.
 */
// Export const AllVariants: Story = {
// 	Render: () => (
// 		<div className="flex flex-wrap gap-4 p-4">
// 			{/* Render all variants */}
// 			{/* <COMPONENT_NAME variant="primary">Primary</COMPONENT_NAME> */}
// 			{/* <COMPONENT_NAME variant="secondary">Secondary</COMPONENT_NAME> */}
// 			{/* <COMPONENT_NAME variant="outline">Outline</COMPONENT_NAME> */}
// 		</div>
// 	),
// };

/**
 * INTERACTIVE PLAYGROUND
 * Full interactive example with user interaction
 *
 * Use this for complex components that benefit from
 * user interaction during visual testing.
 */
// Export const Interactive: Story = {
// 	Args: {
// 		// ...Default.args,
// 	},
// 	Play: async ({ canvasElement }) => {
// 		// Perform a sequence of user interactions
// 		// This helps catch visual issues that occur after interactions
// 	},
// };

/**
 * GUIDELINES FOR WRITING STORIES
 *
 * 1. NAMING:
 *    - Use PascalCase for story names
 *    - Be descriptive but concise
 *    - Include viewport or state in name if specific (e.g., "Mobile", "Focused")
 *
 * 2. COVERAGE:
 *    - Test default state
 *    - Test all major variants/props
 *    - Test disabled state (if applicable)
 *    - Test responsive viewports (mobile, tablet, desktop)
 *    - Test light and dark themes
 *    - Test interaction states (hover, focus, active)
 *
 * 3. PROPS:
 *    - Use realistic but minimal props
 *    - Mock data should be consistent and deterministic
 *    - Avoid random values that would break snapshot matching
 *
 * 4. DELAY SETTINGS:
 *    - Default: 300ms (standard animations)
 *    - Increase to 500ms+ for complex animations
 *    - Use pauseAnimationAtEnd: true for moving elements
 *
 * 5. ACCESSIBILITY:
 *    - Include aria labels and roles
 *    - Test keyboard navigation (focus states)
 *    - Ensure color contrast in dark mode
 *
 * 6. DOCUMENTATION:
 *    - Write clear JSDoc comments for each story
 *    - Explain what the story tests and why
 *    - Include any special considerations
 *
 * 7. BEST PRACTICES:
 *    ✅ Do test all variants and sizes
 *    ✅ Do test responsive behavior
 *    ✅ Do test light and dark themes
 *    ✅ Do test interaction states
 *    ✅ Do use descriptive story names
 *
 *    ❌ Don't use random values
 *    ❌ Don't test performance
 *    ❌ Don't use real API calls
 *    ❌ Don't make snapshots too large (>1000px)
 *    ❌ Don't skip dark mode testing
 *
 * 8. TESTING CHECKLIST:
 *    - Run `bun run storybook` to view locally
 *    - Test all stories in interactive mode
 *    - Build: `bun run storybook:build`
 *    - Run: `bun run chromatic`
 *    - Review changes in Chromatic dashboard
 *    - Accept or request changes
 *
 * For more information, see:
 * - ../../docs/VISUAL_TESTING_GUIDE.md
 * - ../../.storybook/README.md
 */
