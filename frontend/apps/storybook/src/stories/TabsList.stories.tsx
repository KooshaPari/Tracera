import type { Meta, StoryObj } from '@storybook/react-vite';

import { expect, userEvent, within } from '@storybook/test';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui';

const meta: Meta<typeof TabsList> = {
  component: TabsList,
  tags: ['autodocs', 'a11y-test'],
  title: 'Components/TabsList',
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tabOne = canvas.getByRole('tab', { name: 'One' });
    const tabTwo = canvas.getByRole('tab', { name: 'Two' });
    await expect(tabOne).toBeInTheDocument();
    await expect(tabTwo).toBeInTheDocument();
    // Tab one should be selected by default
    await expect(tabOne).toHaveAttribute('data-state', 'active');
    await expect(canvas.getByText('Tab one content')).toBeInTheDocument();
    // Click tab two
    await userEvent.click(tabTwo);
    await expect(tabTwo).toHaveAttribute('data-state', 'active');
    await expect(canvas.getByText('Tab two content')).toBeInTheDocument();
  },
  render: (args) => (
    <Tabs defaultValue='one'>
      <TabsList {...args}>
        <TabsTrigger value='one'>One</TabsTrigger>
        <TabsTrigger value='two'>Two</TabsTrigger>
      </TabsList>
      <TabsContent value='one'>Tab one content</TabsContent>
      <TabsContent value='two'>Tab two content</TabsContent>
    </Tabs>
  ),
};

export const KeyboardNavigation: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tabA = canvas.getByRole('tab', { name: 'Alpha' });
    const tabB = canvas.getByRole('tab', { name: 'Beta' });
    const tabC = canvas.getByRole('tab', { name: 'Gamma' });
    // Focus the first tab
    await userEvent.click(tabA);
    await expect(tabA).toHaveAttribute('data-state', 'active');
    // Use arrow key to navigate to the next tab
    await userEvent.keyboard('{ArrowRight}');
    await expect(tabB).toHaveFocus();
    await userEvent.keyboard('{ArrowRight}');
    await expect(tabC).toHaveFocus();
  },
  render: () => (
    <Tabs defaultValue='alpha'>
      <TabsList>
        <TabsTrigger value='alpha'>Alpha</TabsTrigger>
        <TabsTrigger value='beta'>Beta</TabsTrigger>
        <TabsTrigger value='gamma'>Gamma</TabsTrigger>
      </TabsList>
      <TabsContent value='alpha'>Alpha content</TabsContent>
      <TabsContent value='beta'>Beta content</TabsContent>
      <TabsContent value='gamma'>Gamma content</TabsContent>
    </Tabs>
  ),
};

export const ThreeTabs: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const tabs = canvas.getAllByRole('tab');
    await expect(tabs).toHaveLength(3);
    await expect(canvas.getByText('First panel')).toBeInTheDocument();
    // Switch to second tab
    await userEvent.click(tabs[1]);
    await expect(canvas.getByText('Second panel')).toBeInTheDocument();
    // Switch to third tab
    await userEvent.click(tabs[2]);
    await expect(canvas.getByText('Third panel')).toBeInTheDocument();
  },
  render: () => (
    <Tabs defaultValue='first'>
      <TabsList>
        <TabsTrigger value='first'>First</TabsTrigger>
        <TabsTrigger value='second'>Second</TabsTrigger>
        <TabsTrigger value='third'>Third</TabsTrigger>
      </TabsList>
      <TabsContent value='first'>First panel</TabsContent>
      <TabsContent value='second'>Second panel</TabsContent>
      <TabsContent value='third'>Third panel</TabsContent>
    </Tabs>
  ),
};
