import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, fn, userEvent, within } from '@storybook/test';

import { Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';

const meta: Meta<typeof Card> = {
  component: Card,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Card',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText('Card Title')).toBeInTheDocument();
    await expect(
      canvas.getByText('Card content goes here. This is a sample card component.'),
    ).toBeInTheDocument();
  },
  render: () => (
    <Card className='w-[350px]'>
      <CardHeader>
        <CardTitle>Card Title</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Card content goes here. This is a sample card component.</p>
      </CardContent>
    </Card>
  ),
};

export const WithActions: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText('Project Card')).toBeInTheDocument();
    const cancelButton = canvas.getByRole('button', { name: 'Cancel' });
    const openButton = canvas.getByRole('button', { name: 'Open' });
    await expect(cancelButton).toBeInTheDocument();
    await expect(openButton).toBeInTheDocument();
    await userEvent.click(openButton);
    await userEvent.click(cancelButton);
  },
  render: () => {
    const onCancel = fn();
    const onOpen = fn();
    return (
      <Card className='w-[350px]'>
        <CardHeader>
          <CardTitle>Project Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-muted-foreground mb-4'>A sample project with some description text.</p>
          <div className='flex gap-2'>
            <Button variant='outline' size='sm' onClick={onCancel}>
              Cancel
            </Button>
            <Button size='sm' onClick={onOpen}>
              Open
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  },
};

export const Stats: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await expect(canvas.getByText('Total Items')).toBeInTheDocument();
    await expect(canvas.getByText('In Progress')).toBeInTheDocument();
    await expect(canvas.getByText('Completed')).toBeInTheDocument();
    await expect(canvas.getByText('1,234')).toBeInTheDocument();
    await expect(canvas.getByText('42')).toBeInTheDocument();
    await expect(canvas.getByText('892')).toBeInTheDocument();
  },
  render: () => (
    <div className='grid grid-cols-3 gap-4'>
      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-muted-foreground text-sm font-medium'>Total Items</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-2xl font-bold'>1,234</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-muted-foreground text-sm font-medium'>In Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-2xl font-bold text-blue-500'>42</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className='pb-2'>
          <CardTitle className='text-muted-foreground text-sm font-medium'>Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-2xl font-bold text-green-500'>892</p>
        </CardContent>
      </Card>
    </div>
  ),
};
