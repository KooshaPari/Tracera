import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import { Button, Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@tracertm/ui';

const meta: Meta<typeof TooltipContent> = {
  component: TooltipContent,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/TooltipContent',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  tags: ['skip-tests'],
  render: (args) => (
    <TooltipProvider>
      <Tooltip defaultOpen>
        <TooltipTrigger asChild>
          <button type='button'>Hover</button>
        </TooltipTrigger>
        <TooltipContent {...args}>Tooltip content</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};

export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Hover me' });
    await expect(trigger).toBeInTheDocument();
    // Hover over the trigger to show tooltip
    await userEvent.hover(trigger);
    // Tooltip renders in a portal; check document for the tooltip role
    const tooltip = document.querySelector('[role="tooltip"]');
    await expect(tooltip).toBeInTheDocument();
    await expect(tooltip).toHaveTextContent('Helpful tooltip text');
    // Unhover to dismiss
    await userEvent.unhover(trigger);
  },
  render: () => (
    <TooltipProvider delayDuration={0}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant='outline'>Hover me</Button>
        </TooltipTrigger>
        <TooltipContent>Helpful tooltip text</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};

export const FocusToShow: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Focus me' });
    await expect(trigger).toBeInTheDocument();
    // Tab to the trigger to show tooltip via focus
    await userEvent.tab();
    await expect(trigger).toHaveFocus();
  },
  render: () => (
    <TooltipProvider delayDuration={0}>
      <Tooltip>
        <TooltipTrigger asChild>
          <Button variant='outline'>Focus me</Button>
        </TooltipTrigger>
        <TooltipContent>Focus-triggered tooltip</TooltipContent>
      </Tooltip>
    </TooltipProvider>
  ),
};
