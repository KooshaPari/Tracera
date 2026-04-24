import type { Meta, StoryObj } from '@storybook/react';

import type { Item, LinkType } from '@tracertm/types';

import type { EnhancedNodeData } from '../types';

import { GraphNodePill } from '../GraphNodePill';

function makeNode(
  overrides: Partial<{
    id: string;
    label: string;
    type: string;
    status: Item['status'];
  }> = {},
): EnhancedNodeData {
  const linkTypes: LinkType[] = [
    'implements',
    'tests',
    'depends_on',
    'related_to',
    'blocks',
    'parent_of',
    'same_as',
    'represents',
    'manifests_as',
    'documents',
    'mentions',
    'calls',
    'imports',
    'derives_from',
    'alternative_to',
    'conflicts_with',
    'supersedes',
    'validates',
    'traces_to',
  ];
  const emptyLinkTypeCounts = Object.fromEntries(linkTypes.map((type) => [type, 0])) as Record<
    LinkType,
    number
  >;
  const item: Item = {
    createdAt: new Date().toISOString(),
    description: '',
    id: overrides.id ?? 'item-1',
    priority: 'medium',
    projectId: 'proj-1',
    status: overrides.status ?? 'todo',
    title: overrides.label ?? 'Button Component',
    type: overrides.type! ?? 'feature',
    updatedAt: new Date().toISOString(),
    version: 1,
    view: 'feature',
  };
  return {
    connections: {
      byType: emptyLinkTypeCounts,
      incoming: 0,
      outgoing: 0,
      total: 0,
    },
    depth: 0,
    hasChildren: false,
    id: item.id,
    item,
    label: overrides.label ?? 'Button Component',
    perspective: ['technical'],
    status: overrides.status ?? 'todo',
    type: overrides.type ?? 'component',
  };
}

const defaultNode = makeNode({ label: 'Button Component', type: 'component' });
const viewNode = makeNode({ label: 'Dashboard View', type: 'view' });
const routeNode = makeNode({ label: '/components', type: 'route' });
const stateNode = makeNode({ label: 'Loading', type: 'state' });
const eventNode = makeNode({ label: 'onClick', type: 'event' });

const meta: Meta<typeof GraphNodePill> = {
  argTypes: {
    isHighlighted: { control: 'boolean' },
    isSelected: { control: 'boolean' },
    onExpand: { action: 'expand' },
    onSelect: { action: 'select' },
    showPreview: { control: 'boolean' },
  },
  component: GraphNodePill,
  parameters: {
    chromatic: {
      delay: 200,
      modes: {
        dark: { query: "[data-theme='dark']" },
        light: { query: "[data-theme='light']" },
      },
    },
    test: {
      disable: true,
    },
  },
  tags: ['autodocs', 'skip-tests'],
  title: 'Components/Graph/GraphNodePill',
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default node pill
 */
export const Default: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: defaultNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * Selected state
 */
export const Selected: Story = {
  args: {
    isHighlighted: false,
    isSelected: true,
    node: defaultNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * Highlighted state
 */
export const Highlighted: Story = {
  args: {
    isHighlighted: true,
    isSelected: false,
    node: defaultNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * View variant
 */
export const ViewVariant: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: viewNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * Route variant
 */
export const RouteVariant: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: routeNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * State variant
 */
export const StateVariant: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: stateNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * Event variant
 */
export const EventVariant: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: eventNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
  args: {
    isHighlighted: false,
    isSelected: false,
    node: defaultNode,
    onExpand: () => {},
    onSelect: () => {},
    showPreview: false,
  },
  decorators: [
    (Story) => (
      <div className='dark' data-theme='dark' style={{ padding: '20px' }}>
        <Story />
      </div>
    ),
  ],
  parameters: {
    chromatic: {
      modes: {
        dark: { query: "[data-theme='dark']" },
      },
    },
  },
};

/**
 * All variants together
 */
export const AllVariants: Story = {
  render: () => {
    const noop = () => {};
    return (
      <div className='flex flex-wrap gap-2 p-4'>
        <GraphNodePill
          node={defaultNode}
          isSelected={false}
          isHighlighted={false}
          onSelect={noop}
          onExpand={noop}
          showPreview={false}
        />
        <GraphNodePill
          node={viewNode}
          isSelected={false}
          isHighlighted={false}
          onSelect={noop}
          onExpand={noop}
          showPreview={false}
        />
        <GraphNodePill
          node={routeNode}
          isSelected={false}
          isHighlighted={false}
          onSelect={noop}
          onExpand={noop}
          showPreview={false}
        />
        <GraphNodePill
          node={stateNode}
          isSelected={false}
          isHighlighted={false}
          onSelect={noop}
          onExpand={noop}
          showPreview={false}
        />
        <GraphNodePill
          node={eventNode}
          isSelected={false}
          isHighlighted={false}
          onSelect={noop}
          onExpand={noop}
          showPreview={false}
        />
      </div>
    );
  },
};
