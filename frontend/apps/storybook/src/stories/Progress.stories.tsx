import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, within } from '@storybook/test';

import { Progress } from '@tracertm/ui';

const meta: Meta<typeof Progress> = {
  component: Progress,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Progress',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    value: 50,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const progressBar = canvas.getByRole('progressbar');
    await expect(progressBar).toBeInTheDocument();
    await expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  },
};

export const Empty: Story = {
  args: {
    value: 0,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const progressBar = canvas.getByRole('progressbar');
    await expect(progressBar).toBeInTheDocument();
    await expect(progressBar).toHaveAttribute('aria-valuenow', '0');
  },
};

export const Full: Story = {
  args: {
    value: 100,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const progressBar = canvas.getByRole('progressbar');
    await expect(progressBar).toBeInTheDocument();
    await expect(progressBar).toHaveAttribute('aria-valuenow', '100');
  },
};

export const Partial: Story = {
  args: {
    value: 33,
  },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const progressBar = canvas.getByRole('progressbar');
    await expect(progressBar).toBeInTheDocument();
    await expect(progressBar).toHaveAttribute('aria-valuenow', '33');
    await expect(progressBar).toHaveAttribute('aria-valuemin', '0');
    await expect(progressBar).toHaveAttribute('aria-valuemax', '100');
  },
};
