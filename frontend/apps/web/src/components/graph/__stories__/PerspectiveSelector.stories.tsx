import type { Meta, StoryObj } from '@storybook/react';
import type { CSSProperties } from 'react';

import { PerspectiveSelector } from '../PerspectiveSelector';

const DARK_DECORATOR_STYLE: CSSProperties = { padding: '20px' };
const NO_OP = (): void => {};

const meta: Meta<typeof PerspectiveSelector> = {
  argTypes: {
    currentPerspective: {
      control: 'select',
      options: ['all', 'product', 'business', 'technical', 'ui', 'security', 'performance'],
    },
    itemCounts: { control: 'object' },
    onPerspectiveChange: { action: 'perspective changed' },
  },
  component: PerspectiveSelector,
  parameters: {
    chromatic: {
      delay: 300,
      modes: {
        dark: { query: "[data-theme='dark']" },
        light: { query: "[data-theme='light']" },
      },
    },
    test: {
      disable: true,
    },
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Components/Graph/PerspectiveSelector',
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default perspective selector
 */
export const Default: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
};

/**
 * With item counts
 */
export const WithCounts: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: { all: 42, product: 12, technical: 20 },
    onPerspectiveChange: NO_OP,
  },
};

/**
 * Perspective selector on tablet
 */
export const Tablet: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

/**
 * Perspective selector on mobile
 */
export const Mobile: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
  parameters: {
    viewport: {
      defaultViewport: 'mobile',
    },
  },
};

/**
 * Dark mode variant
 */
export const DarkMode: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
  decorators: [
    (Story) => (
      <div className='dark' data-theme='dark' style={DARK_DECORATOR_STYLE}>
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

/**
 * With focused state
 */
export const Focused: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
  play: async ({ canvasElement }) => {
    const selector = canvasElement.querySelector('button');
    if (selector) {
      selector.focus();
    }
  },
};

/**
 * With hover state
 */
export const Hovered: Story = {
  args: {
    currentPerspective: 'all',
    itemCounts: undefined,
    onPerspectiveChange: NO_OP,
  },
  play: async ({ canvasElement }) => {
    const selector = canvasElement.querySelector('button');
    if (selector) {
      selector.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
    }
  },
};
