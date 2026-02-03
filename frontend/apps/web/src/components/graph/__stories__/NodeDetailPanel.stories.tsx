import type { Meta, StoryObj } from "@storybook/react";
import type { Item, Link } from "@tracertm/types";
import { NodeDetailPanel } from "../NodeDetailPanel";
import type { EnhancedNodeData } from "../types";

const mockItem: Item = {
	createdAt: new Date().toISOString(),
	description: "A reusable button component with multiple variants",
	id: "item-1",
	priority: "medium",
	projectId: "proj-1",
	status: "todo",
	title: "Button Component",
	type: "feature",
	updatedAt: new Date().toISOString(),
	version: 1,
	view: "technical",
};

const mockNode: EnhancedNodeData = {
	connections: { byType: {}, incoming: 2, outgoing: 3, total: 5 },
	depth: 0,
	hasChildren: true,
	id: "node-1",
	item: mockItem,
	label: "Button Component",
	perspective: ["technical"],
	status: "todo",
	type: "component",
};

const relatedItems: Item[] = [
	{ ...mockItem, id: "item-2", title: "Input Component" },
	{ ...mockItem, id: "item-3", title: "Form Component" },
];

const incomingLinks: Link[] = [];
const outgoingLinks: Link[] = [];

const noop = () => {};

const meta: Meta<typeof NodeDetailPanel> = {
	argTypes: {
		onClose: { action: "closed" },
		onFocusNode: { action: "focusNode" },
		onNavigateToItem: { action: "navigate" },
	},
	component: NodeDetailPanel,
	parameters: {
		chromatic: {
			delay: 300,
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
		},
		layout: "fullscreen",
	},
	tags: ["autodocs"],
	title: "Components/Graph/NodeDetailPanel",
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Open detail panel
 */
export const Open: Story = {
	args: {
		incomingLinks,
		node: mockNode,
		onClose: noop,
		onFocusNode: noop,
		onNavigateToItem: noop,
		outgoingLinks,
		relatedItems,
	},
};

/**
 * Closed detail panel (node null)
 */
export const Closed: Story = {
	args: {
		incomingLinks: [],
		node: null,
		onClose: noop,
		onFocusNode: noop,
		onNavigateToItem: noop,
		outgoingLinks: [],
		relatedItems: [],
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		incomingLinks,
		node: mockNode,
		onClose: noop,
		onFocusNode: noop,
		onNavigateToItem: noop,
		outgoingLinks,
		relatedItems,
	},
	parameters: {
		viewport: {
			defaultViewport: "tablet",
		},
	},
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
	args: {
		incomingLinks,
		node: mockNode,
		onClose: noop,
		onFocusNode: noop,
		onNavigateToItem: noop,
		outgoingLinks,
		relatedItems,
	},
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark">
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
 * With more related items
 */
export const ManyRelated: Story = {
	args: {
		incomingLinks,
		node: { ...mockNode, connections: { ...mockNode.connections, total: 12 } },
		onClose: noop,
		onFocusNode: noop,
		onNavigateToItem: noop,
		outgoingLinks,
		relatedItems: [
			...relatedItems,
			{ ...mockItem, id: "item-4", title: "Card" },
			{ ...mockItem, id: "item-5", title: "Modal" },
		],
	},
};
