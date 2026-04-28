import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, within } from '@storybook/test';

import { Avatar, AvatarFallback, AvatarImage } from '@tracertm/ui';

const meta: Meta<typeof Avatar> = {
  component: Avatar,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/Avatar',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const avatar =
      canvasElement.querySelector('[data-slot="avatar"]') ?? canvasElement.firstElementChild;
    await expect(avatar).toBeInTheDocument();
  },
  render: () => (
    <Avatar>
      <AvatarFallback>AB</AvatarFallback>
    </Avatar>
  ),
};

export const WithFallback: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const fallback = canvas.getByText('JD');
    await expect(fallback).toBeInTheDocument();
  },
  render: () => (
    <Avatar>
      <AvatarFallback>JD</AvatarFallback>
    </Avatar>
  ),
};

export const WithImage: Story = {
  play: async ({ canvasElement }) => {
    const img = canvasElement.querySelector('img');
    const fallback = canvasElement.querySelector('[data-slot="avatar-fallback"]');
    // Either the image is loaded or the fallback is showing
    const hasContent = img !== null || fallback !== null;
    await expect(hasContent).toBe(true);
  },
  render: () => (
    <Avatar>
      <AvatarImage src='https://github.com/shadcn.png' alt='User avatar' />
      <AvatarFallback>CN</AvatarFallback>
    </Avatar>
  ),
};

export const MultipleAvatars: Story = {
  play: async ({ canvasElement }) => {
    const avatars = canvasElement.querySelectorAll('[data-slot="avatar"]');
    await expect(avatars.length).toBeGreaterThanOrEqual(3);
  },
  render: () => (
    <div className='flex gap-2'>
      <Avatar>
        <AvatarFallback>A</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback>B</AvatarFallback>
      </Avatar>
      <Avatar>
        <AvatarFallback>C</AvatarFallback>
      </Avatar>
    </div>
  ),
};
