import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogTitle,
  DialogTrigger,
} from '@tracertm/ui';

const meta: Meta<typeof DialogOverlay> = {
  component: DialogOverlay,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/DialogOverlay',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  tags: ['skip-tests'],
  render: (args) => (
    <Dialog open>
      <DialogPortal>
        <DialogOverlay {...args} />
        <DialogContent>
          <div className='space-y-2'>
            <DialogTitle>Dialog title</DialogTitle>
            <DialogDescription>Dialog body content.</DialogDescription>
          </div>
        </DialogContent>
      </DialogPortal>
    </Dialog>
  ),
};

export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const openButton = canvas.getByRole('button', { name: 'Open Dialog' });
    await expect(openButton).toBeInTheDocument();
    await userEvent.click(openButton);
    // After clicking, the dialog should appear in the document body
    await expect(document.querySelector('[role="dialog"]')).toBeInTheDocument();
    const dialogTitle = within(document.querySelector('[role="dialog"]') as HTMLElement).getByText(
      'Interactive Dialog',
    );
    await expect(dialogTitle).toBeInTheDocument();
  },
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open Dialog</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Interactive Dialog</DialogTitle>
        <DialogDescription>This dialog can be opened and closed interactively.</DialogDescription>
      </DialogContent>
    </Dialog>
  ),
};

export const WithCloseButton: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const openButton = canvas.getByRole('button', { name: 'Open with Close' });
    await expect(openButton).toBeInTheDocument();
    await userEvent.click(openButton);
    const dialog = document.querySelector('[role="dialog"]') as HTMLElement;
    await expect(dialog).toBeInTheDocument();
    const closeButton = within(dialog).getByRole('button', { name: 'Close' });
    await expect(closeButton).toBeInTheDocument();
    await userEvent.click(closeButton);
  },
  render: () => (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Open with Close</Button>
      </DialogTrigger>
      <DialogContent>
        <DialogTitle>Closable Dialog</DialogTitle>
        <DialogDescription>Click the close button below.</DialogDescription>
        <DialogClose asChild>
          <Button variant='outline'>Close</Button>
        </DialogClose>
      </DialogContent>
    </Dialog>
  ),
};
