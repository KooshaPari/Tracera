import type { Meta, StoryObj } from '@storybook/react';

import { GraphSearch } from '../GraphSearch';

const meta: Meta<typeof GraphSearch> = {
  argTypes: {
    compact: { control: 'boolean' },
    onHighlight: { action: 'highlight' },
    onSearch: { action: 'search performed' },
  },
  component: GraphSearch,
  parameters: {
    chromatic: {
      delay: 300,
      modes: {
        dark: { query: "[data-theme='dark']" },
        light: { query: "[data-theme='light']" },
      },
    },
  },
  tags: ['autodocs'],
  title: 'Components/Graph/GraphSearch',
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default graph search component
 */
export const Default: Story = {
  args: {
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
};

/**
 * With search query
 */
export const WithQuery: Story = {
  args: {
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
  play: async ({ canvasElement }) => {
    const input = canvasElement.querySelector('input');
    if (input) {
      input.value = 'button';
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  },
};

/**
 * Compact search
 */
export const Compact: Story = {
  args: {
    compact: true,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
};

/**
 * On tablet view
 */
export const Tablet: Story = {
  args: {
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

/**
 * On mobile view
 */
export const Mobile: Story = {
  args: {
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
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
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
  decorators: [
    (Story) => (
      <div className='dark' data-theme='dark' style={{ padding: '20px' }}>
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
 * With focus state
 */
export const Focused: Story = {
  args: {
    compact: false,
    items: [],
    onHighlight: () => {},
    onSearch: () => {},
  },
  play: async ({ canvasElement }) => {
    const input = canvasElement.querySelector('input');
    if (input) {
      input.focus();
    }
  },
};
