import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import {
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@tracertm/ui';

const meta: Meta<typeof DropdownMenuContent> = {
  component: DropdownMenuContent,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/DropdownMenuContent',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  tags: ['skip-tests'],
  render: (args) => (
    <DropdownMenu defaultOpen>
      <DropdownMenuTrigger asChild>
        <button type='button'>Open</button>
      </DropdownMenuTrigger>
      <DropdownMenuContent {...args}>
        <DropdownMenuItem>First</DropdownMenuItem>
        <DropdownMenuItem>Second</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ),
};

export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Actions' });
    await expect(trigger).toBeInTheDocument();
    await userEvent.click(trigger);
    // Menu content renders in a portal; query the document
    const menuItems = document.querySelectorAll('[role="menuitem"]');
    await expect(menuItems.length).toBeGreaterThanOrEqual(2);
  },
  render: () => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant='outline'>Actions</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>Edit</DropdownMenuItem>
        <DropdownMenuItem>Duplicate</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Delete</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ),
};

export const KeyboardNavigation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('button', { name: 'Navigate' });
    await expect(trigger).toBeInTheDocument();
    // Focus the trigger and open with Enter
    await userEvent.tab();
    await expect(trigger).toHaveFocus();
    await userEvent.keyboard('{Enter}');
    // Menu should be open now
    const menuItems = document.querySelectorAll('[role="menuitem"]');
    await expect(menuItems.length).toBeGreaterThanOrEqual(2);
  },
  render: () => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button>Navigate</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>Option A</DropdownMenuItem>
        <DropdownMenuItem>Option B</DropdownMenuItem>
        <DropdownMenuItem>Option C</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  ),
};
