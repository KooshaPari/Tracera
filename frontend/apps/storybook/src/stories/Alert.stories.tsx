import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, within } from '@storybook/test';

import { Alert } from '@tracertm/ui';

const meta: Meta<typeof Alert> = {
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'success', 'warning'],
    },
  },
  component: Alert,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Alert',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    children: 'Default alert message',
    variant: 'default',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alert = canvas.getByRole('alert');
    await expect(alert).toBeInTheDocument();
    await expect(alert).toHaveTextContent('Default alert message');
  },
};

export const Destructive: Story = {
  args: {
    children: 'Destructive alert message',
    variant: 'destructive',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alert = canvas.getByRole('alert');
    await expect(alert).toBeInTheDocument();
    await expect(alert).toHaveTextContent('Destructive alert message');
  },
};

export const Success: Story = {
  args: {
    children: 'Success alert message',
    variant: 'success',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alert = canvas.getByRole('alert');
    await expect(alert).toBeInTheDocument();
    await expect(alert).toHaveTextContent('Success alert message');
  },
};

export const Warning: Story = {
  args: {
    children: 'Warning alert message',
    variant: 'warning',
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alert = canvas.getByRole('alert');
    await expect(alert).toBeInTheDocument();
    await expect(alert).toHaveTextContent('Warning alert message');
  },
};

export const AllVariants: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const alerts = canvas.getAllByRole('alert');
    await expect(alerts).toHaveLength(4);
  },
  render: () => (
    <div className='flex flex-wrap gap-4'>
      <Alert variant='default'>Default</Alert>
      <Alert variant='destructive'>Destructive</Alert>
      <Alert variant='success'>Success</Alert>
      <Alert variant='warning'>Warning</Alert>
    </div>
  ),
};
