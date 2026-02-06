import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@tracertm/ui';

const meta: Meta<typeof SelectTrigger> = {
  component: SelectTrigger,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/SelectTrigger',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  tags: ['skip-tests'],
  render: (args) => (
    <Select defaultValue='one'>
      <SelectTrigger {...args}>
        <SelectValue placeholder='Select an option' />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value='one'>Option one</SelectItem>
        <SelectItem value='two'>Option two</SelectItem>
      </SelectContent>
    </Select>
  ),
};

export const Interactive: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('combobox');
    await expect(trigger).toBeInTheDocument();
    await expect(trigger).toHaveTextContent('Option one');
    await userEvent.click(trigger);
    // Select listbox renders in a portal
    const listbox = document.querySelector('[role="listbox"]');
    await expect(listbox).toBeInTheDocument();
  },
  render: () => (
    <Select defaultValue='one'>
      <SelectTrigger className='w-[200px]'>
        <SelectValue placeholder='Pick one' />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value='one'>Option one</SelectItem>
        <SelectItem value='two'>Option two</SelectItem>
        <SelectItem value='three'>Option three</SelectItem>
      </SelectContent>
    </Select>
  ),
};

export const WithPlaceholder: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const trigger = canvas.getByRole('combobox');
    await expect(trigger).toBeInTheDocument();
    // Should display placeholder text when no value is selected
    await expect(trigger).toHaveTextContent('Choose an item');
  },
  render: () => (
    <Select>
      <SelectTrigger className='w-[200px]'>
        <SelectValue placeholder='Choose an item' />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value='alpha'>Alpha</SelectItem>
        <SelectItem value='beta'>Beta</SelectItem>
      </SelectContent>
    </Select>
  ),
};
