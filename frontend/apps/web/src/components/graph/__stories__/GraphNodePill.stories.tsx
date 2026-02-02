import type { Meta, StoryObj } from "@storybook/react";
import type { Item } from "@tracertm/types";
import { GraphNodePill } from "../GraphNodePill";
import type { EnhancedNodeData } from "../types";

function makeNode(
	overrides: Partial<{
		id: string;
		label: string;
		type: string;
		status: Item["status"];
	}> = {},
): EnhancedNodeData {
	const item: Item = {
		id: overrides.id ?? "item-1",
		projectId: "proj-1",
		view: "technical",
		type: (overrides.type as Item["type"]) ?? "feature",
		title: overrides.label ?? "Button Component",
		description: "",
		status: overrides.status ?? "todo",
		priority: "medium",
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	};
	return {
		id: item.id,
		item,
		type: overrides.type ?? "component",
		status: overrides.status ?? "todo",
		label: overrides.label ?? "Button Component",
		perspective: ["technical"],
		connections: { incoming: 0, outgoing: 0, total: 0, byType: {} },
		depth: 0,
		hasChildren: false,
	};
}

const defaultNode = makeNode({ label: "Button Component", type: "component" });
const viewNode = makeNode({ label: "Dashboard View", type: "view" });
const routeNode = makeNode({ label: "/components", type: "route" });
const stateNode = makeNode({ label: "Loading", type: "state" });
const eventNode = makeNode({ label: "onClick", type: "event" });

const meta: Meta<typeof GraphNodePill> = {
	title: "Components/Graph/GraphNodePill",
	component: GraphNodePill,
	tags: ["autodocs"],
	parameters: {
		chromatic: {
			modes: {
				light: { query: "[data-theme='light']" },
				dark: { query: "[data-theme='dark']" },
			},
			delay: 200,
		},
	},
	argTypes: {
		onSelect: { action: "select" },
		onExpand: { action: "expand" },
		isSelected: { control: "boolean" },
		isHighlighted: { control: "boolean" },
		showPreview: { control: "boolean" },
	},
};

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Default node pill
 */
export const Default: Story = {
	args: {
		node: defaultNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * Selected state
 */
export const Selected: Story = {
	args: {
		node: defaultNode,
		isSelected: true,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * Highlighted state
 */
export const Highlighted: Story = {
	args: {
		node: defaultNode,
		isSelected: false,
		isHighlighted: true,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * View variant
 */
export const ViewVariant: Story = {
	args: {
		node: viewNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * Route variant
 */
export const RouteVariant: Story = {
	args: {
		node: routeNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * State variant
 */
export const StateVariant: Story = {
	args: {
		node: stateNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * Event variant
 */
export const EventVariant: Story = {
	args: {
		node: eventNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
};

/**
 * Dark mode
 */
export const DarkMode: Story = {
	args: {
		node: defaultNode,
		isSelected: false,
		isHighlighted: false,
		onSelect: () => {},
		onExpand: () => {},
		showPreview: false,
	},
	decorators: [
		(Story) => (
			<div className="dark" data-theme="dark" style={{ padding: "20px" }}>
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
			<div className="flex gap-2 flex-wrap p-4">
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
