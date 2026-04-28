import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import { Input } from '@tracertm/ui';

const meta: Meta<typeof Input> = {
  component: Input,
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/xxx/Design-System?node-id=456',
    },
    trace: {
      componentId: 'comp-input-001',
      storyId: 'story-input-001',
    },
  },
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Input',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    placeholder: 'Enter text...',
    type: 'text',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText('Enter text...');
    await expect(input).toBeInTheDocument();
    await expect(input).toBeEnabled();
    await userEvent.click(input);
    await expect(input).toHaveFocus();
    await userEvent.type(input, 'Hello World');
    await expect(input).toHaveValue('Hello World');
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
    placeholder: 'Disabled input',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText('Disabled input');
    await expect(input).toBeDisabled();
  },
};

export const WithValue: Story = {
  args: {
    defaultValue: 'Pre-filled value',
    placeholder: 'Enter text...',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByDisplayValue('Pre-filled value');
    await expect(input).toBeInTheDocument();
    await userEvent.clear(input);
    await userEvent.type(input, 'New value');
    await expect(input).toHaveValue('New value');
  },
};

export const Password: Story = {
  args: {
    placeholder: 'Enter password',
    type: 'password',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText('Enter password');
    await expect(input).toHaveAttribute('type', 'password');
    await userEvent.type(input, 'secret123');
    await expect(input).toHaveValue('secret123');
  },
};

export const KeyboardFocus: Story = {
  args: {
    placeholder: 'Tab to focus',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const input = canvas.getByPlaceholderText('Tab to focus');
    await userEvent.tab();
    await expect(input).toHaveFocus();
  },
};
