import type { Meta, StoryObj } from "@storybook/react";
import type { Item, Link } from "@tracertm/types";
import { NodeDetailPanel } from "../NodeDetailPanel";
import type { EnhancedNodeData } from "../types";

const mockItem: Item = {
	id: "item-1",
	projectId: "proj-1",
	view: "technical",
	type: "feature",
	title: "Button Component",
	description: "A reusable button component with multiple variants",
	status: "todo",
	priority: "medium",
	version: 1,
	createdAt: new Date().toISOString(),
	updatedAt: new Date().toISOString(),
};

const mockNode: EnhancedNodeData = {
	id: "node-1",
	item: mockItem,
	type: "component",
	status: "todo",
	label: "Button Component",
	perspective: ["technical"],
	connections: { incoming: 2, outgoing: 3, total: 5, byType: {} },
	depth: 0,
	hasChildren: true,
};

const relatedItems: Item[] = [
	{ ...mockItem, id: "item-2", title: "Input Component" },
	{ ...mockItem, id: "item-3", title: "Form Component" },
];

const incomingLinks: Link[] = [];
const outgoingLinks: Link[] = [];

const noop = () => {};

const meta: Meta<typeof NodeDetailPanel> = {
	title: "Components/Graph/NodeDetailPanel",
	component: NodeDetailPanel,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 300,
		},
		layout: "fullscreen",
	},
	argTypes: {
		onClose: { action: "closed" },
		onNavigateToItem: { action: "navigate" },
		onFocusNode: { action: "focusNode" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Open detail panel
 */
export const Open: Story = {
	args: {
		node: mockNode,
		relatedItems,
		incomingLinks,
		outgoingLinks,
		onClose: noop,
		onNavigateToItem: noop,
		onFocusNode: noop,
	},
};

/**
 * Closed detail panel (node null)
 */
export const Closed: Story = {
	args: {
		node: null,
		relatedItems: [],
		incomingLinks: [],
		outgoingLinks: [],
		onClose: noop,
		onNavigateToItem: noop,
		onFocusNode: noop,
	},
};

/**
 * On tablet
 */
export const Tablet: Story = {
	args: {
		node: mockNode,
		relatedItems,
		incomingLinks,
		outgoingLinks,
		onClose: noop,
		onNavigateToItem: noop,
		onFocusNode: noop,
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
		node: mockNode,
		relatedItems,
		incomingLinks,
		outgoingLinks,
		onClose: noop,
		onNavigateToItem: noop,
		onFocusNode: noop,
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
		node: { ...mockNode, connections: { ...mockNode.connections, total: 12 } },
		relatedItems: [
			...relatedItems,
			{ ...mockItem, id: "item-4", title: "Card" },
			{ ...mockItem, id: "item-5", title: "Modal" },
		],
		incomingLinks,
		outgoingLinks,
		onClose: noop,
		onNavigateToItem: noop,
		onFocusNode: noop,
	},
};
