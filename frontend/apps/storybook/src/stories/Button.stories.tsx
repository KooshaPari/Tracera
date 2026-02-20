import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, fn, userEvent, within } from '@storybook/test';

import { Button } from '@tracertm/ui';

const meta: Meta<typeof Button> = {
  argTypes: {
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
  },
  args: {
    onClick: fn(),
  },
  component: Button,
  parameters: {
    design: {
      type: 'figma',
      url: 'https://www.figma.com/file/xxx/Design-System?node-id=123',
    },
    trace: {
      componentId: 'comp-button-001',
      storyId: 'story-button-001',
    },
  },
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Button',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Default',
    variant: 'default',
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Default' });
    await expect(button).toBeInTheDocument();
    await expect(button).toBeEnabled();
    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalledTimes(1);
  },
};

export const Destructive: Story = {
  args: {
    children: 'Destructive',
    variant: 'destructive',
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Destructive' });
    await expect(button).toBeInTheDocument();
    await userEvent.click(button);
    await expect(args.onClick).toHaveBeenCalled();
  },
};

export const Outline: Story = {
  args: {
    children: 'Outline',
    variant: 'outline',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Outline' });
    await expect(button).toBeInTheDocument();
  },
};

export const Secondary: Story = {
  args: {
    children: 'Secondary',
    variant: 'secondary',
  },
};

export const Ghost: Story = {
  args: {
    children: 'Ghost',
    variant: 'ghost',
  },
};

export const Link: Story = {
  args: {
    children: 'Link',
    variant: 'link',
  },
};

export const Sm: Story = {
  args: {
    children: 'Sm',
    size: 'sm',
  },
};

export const Lg: Story = {
  args: {
    children: 'Lg',
    size: 'lg',
  },
};

export const Icon: Story = {
  args: {
    children: 'Icon',
    size: 'icon',
  },
};

export const KeyboardInteraction: Story = {
  args: {
    children: 'Press Enter',
    variant: 'default',
  },
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Press Enter' });
    await expect(button).toBeInTheDocument();
    await userEvent.tab();
    await expect(button).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    await expect(args.onClick).toHaveBeenCalled();
  },
};

export const Disabled: Story = {
  args: {
    children: 'Disabled',
    disabled: true,
    variant: 'default',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button', { name: 'Disabled' });
    await expect(button).toBeDisabled();
  },
};

export const AllVariants: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const buttons = canvas.getAllByRole('button');
    await expect(buttons).toHaveLength(6);
  },
  render: () => (
    <div className='flex flex-wrap gap-4'>
      <Button variant='default'>Default</Button>
      <Button variant='destructive'>Destructive</Button>
      <Button variant='outline'>Outline</Button>
      <Button variant='secondary'>Secondary</Button>
      <Button variant='ghost'>Ghost</Button>
      <Button variant='link'>Link</Button>
    </div>
  ),
};
