import type { Meta, StoryObj } from '@storybook/react';

import { EditAffordances } from '../EditAffordances';

const meta: Meta<typeof EditAffordances> = {
  argTypes: {
    compact: { control: 'boolean' },
    editType: {
      control: 'select',
      options: ['instant', 'agent_required', 'manual'],
    },
    isEditing: { control: 'boolean' },
    onEdit: { action: 'edit clicked' },
    showLabel: { control: 'boolean' },
  },
  component: EditAffordances,
  parameters: {
    chromatic: {
      delay: 300,
      modes: {
        dark: { query: "[data-theme='dark']" },
        light: { query: "[data-theme='light']" },
      },
    },
    layout: 'fullscreen',
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Components/Graph/EditAffordances',
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default edit affordances
 */
export const Default: Story = {
  args: {
    editType: 'instant',
    isEditing: false,
  },
};

/**
 * Agent-required edit type
 */
export const AgentRequired: Story = {
  args: {
    editType: 'agent_required',
    isEditing: false,
  },
};

/**
 * On tablet
 */
export const Tablet: Story = {
  args: {
    editType: 'instant',
    isEditing: false,
  },
  parameters: {
    viewport: {
      defaultViewport: 'tablet',
    },
  },
};

/**
 * On mobile
 */
export const Mobile: Story = {
  args: {
    editType: 'instant',
    isEditing: false,
  },
  parameters: {
    viewport: {
      defaultViewport: 'mobile',
    },
  },
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
  args: {
    editType: 'instant',
    isEditing: false,
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
 * With hover state
 */
export const Hovered: Story = {
  args: {
    editType: 'instant',
    isEditing: false,
  },
  play: async ({ canvasElement }) => {
    const element = canvasElement.querySelector("[role='group']");
    if (element) {
      element.dispatchEvent(new MouseEvent('mouseenter', { bubbles: true }));
    }
  },
};
