import type { Meta, StoryObj } from "@storybook/react";
import { logger } from "@/lib/logger";
import { useState } from "react";
import {
	NodeActions,
	NodeContextMenu,
	NodeHoverTooltip,
	NodeQuickActions,
} from "../index";

// NodeActions Stories
const NodeActionsMeta: Meta<typeof NodeActions> = {
	args: {
		isExpanded: false,
		nodeId: "node-123",
		onExpand: () => {},
		onNavigate: () => {},
		onShowMenu: () => {},
	},
	component: NodeActions,
	tags: ["autodocs"],
	title: "Graph/Interactions/NodeActions",
};

export default NodeActionsMeta;

type NodeActionsStory = StoryObj<typeof NodeActions>;

export const Default: NodeActionsStory = {};

export const Expanded: NodeActionsStory = {
	args: {
		isExpanded: true,
	},
};

export const Interactive: NodeActionsStory = {
	render: (args) => {
		const [isExpanded, setIsExpanded] = useState(false);
		return (
			<NodeActions
				{...args}
				isExpanded={isExpanded}
				onExpand={() => setIsExpanded(!isExpanded)}
			/>
		);
	},
};

// NodeContextMenu Stories
export const ContextMenuStory: Meta<typeof NodeContextMenu> = {
	args: {
		nodeId: "node-123",
		nodeType: "requirement",
		onCopyId: () => {},
		onDelete: () => {},
		onDuplicate: () => {},
		onViewDetails: () => {},
	},
	component: NodeContextMenu,
	render: (args) => (
		<NodeContextMenu {...args}>
			<div className="p-8 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer">
				Right-click me to see the context menu
			</div>
		</NodeContextMenu>
	),
	tags: ["autodocs"],
	title: "Graph/Interactions/NodeContextMenu",
};

export const ContextMenuWithCard: StoryObj<typeof NodeContextMenu> = {
	...ContextMenuStory,
	render: (args) => (
		<NodeContextMenu {...args}>
			<div className="w-64 p-4 bg-white border rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-shadow">
				<h3 className="font-semibold text-sm mb-2">Test Requirement</h3>
				<p className="text-xs text-gray-600">
					Right-click to see available actions
				</p>
			</div>
		</NodeContextMenu>
	),
};

// NodeHoverTooltip Stories
export const HoverTooltipStory: Meta<typeof NodeHoverTooltip> = {
	args: {
		label: "User Authentication System",
		nodeId: "node-123",
		nodeType: "requirement",
		position: { x: 100, y: 100 },
		status: "in_progress",
	},
	component: NodeHoverTooltip,
	tags: ["autodocs"],
	title: "Graph/Interactions/NodeHoverTooltip",
};

export const BasicTooltip: StoryObj<typeof NodeHoverTooltip> = {
	...HoverTooltipStory,
};

export const TooltipWithMetadata: StoryObj<typeof NodeHoverTooltip> = {
	...HoverTooltipStory,
	args: {
		...HoverTooltipStory.args,
		metadata: {
			assignee: "John Doe",
			deadline: "2024-12-31",
			priority: "high",
			progress: "75%",
		},
	},
};

export const TooltipDifferentTypes: StoryObj<typeof NodeHoverTooltip> = {
	...HoverTooltipStory,
	render: () => (
		<div className="space-y-4">
			<NodeHoverTooltip
				nodeId="1"
				nodeType="requirement"
				label="User Authentication"
				status="done"
				position={{ x: 20, y: 20 }}
			/>
			<NodeHoverTooltip
				nodeId="2"
				nodeType="feature"
				label="OAuth Integration"
				status="in_progress"
				position={{ x: 20, y: 150 }}
				metadata={{ assignee: "Jane Smith" }}
			/>
			<NodeHoverTooltip
				nodeId="3"
				nodeType="test_case"
				label="Login Flow Test"
				status="todo"
				position={{ x: 20, y: 300 }}
				metadata={{ coverage: "85%" }}
			/>
		</div>
	),
};

// NodeQuickActions Stories
export const QuickActionsStory: Meta<typeof NodeQuickActions> = {
	args: {
		nodeId: "node-123",
		onAddLink: () => {},
		onAddTag: () => {},
		onEditNote: () => {},
	},
	component: NodeQuickActions,
	tags: ["autodocs"],
	title: "Graph/Interactions/NodeQuickActions",
};

export const QuickActionsDefault: StoryObj<typeof NodeQuickActions> = {
	...QuickActionsStory,
};

export const QuickActionsInteractive: StoryObj<typeof NodeQuickActions> = {
	...QuickActionsStory,
	render: (args) => {
		const [links, setLinks] = useState<string[]>([]);
		const [tags, setTags] = useState<string[]>([]);
		const [notes, setNotes] = useState<string[]>([]);

		return (
			<div className="space-y-4">
				<div className="p-4 border rounded-lg">
					<NodeQuickActions
						{...args}
						onAddLink={(id, target) => {
							setLinks([...links, target]);
							args.onAddLink(id, target);
						}}
						onAddTag={(id, tag) => {
							setTags([...tags, tag]);
							args.onAddTag(id, tag);
						}}
						onEditNote={(id, note) => {
							setNotes([...notes, note]);
							args.onEditNote(id, note);
						}}
					/>
				</div>
				{links.length > 0 && (
					<div className="p-3 bg-blue-50 rounded">
						<h4 className="font-semibold text-sm mb-2">Links:</h4>
						<ul className="text-xs space-y-1">
							{links.map((link, i) => (
								<li key={i}>{link}</li>
							))}
						</ul>
					</div>
				)}
				{tags.length > 0 && (
					<div className="p-3 bg-green-50 rounded">
						<h4 className="font-semibold text-sm mb-2">Tags:</h4>
						<div className="flex flex-wrap gap-1">
							{tags.map((tag, i) => (
								<span
									key={i}
									className="px-2 py-1 bg-green-200 text-green-800 rounded text-xs"
								>
									{tag}
								</span>
							))}
						</div>
					</div>
				)}
				{notes.length > 0 && (
					<div className="p-3 bg-yellow-50 rounded">
						<h4 className="font-semibold text-sm mb-2">Notes:</h4>
						<ul className="text-xs space-y-1">
							{notes.map((note, i) => (
								<li key={i}>{note}</li>
							))}
						</ul>
					</div>
				)}
			</div>
		);
	},
};

// Combined interactions story
export const AllInteractions: Meta = {
	render: () => {
		const [isExpanded, setIsExpanded] = useState(false);
		const [hoverPosition, setHoverPosition] = useState({ x: 0, y: 0 });
		const [showTooltip, setShowTooltip] = useState(false);

		return (
			<div className="p-8 space-y-8">
				<div className="space-y-4">
					<h2 className="text-xl font-bold">All Node Interactions</h2>
					<p className="text-sm text-gray-600">
						Demonstrates all interactive features working together
					</p>
				</div>

				<NodeContextMenu
					nodeId="demo-node"
					nodeType="requirement"
					onCopyId={(id) => logger.info("Copy ID:", id)}
					onDuplicate={(id) => logger.info("Duplicate:", id)}
					onDelete={(id) => logger.info("Delete:", id)}
					onViewDetails={(id) => logger.info("View:", id)}
				>
					<div
						className="relative w-80 p-4 bg-white border-2 rounded-lg shadow-md cursor-pointer hover:shadow-lg transition-all"
						onMouseMove={(e) => {
							setHoverPosition({ x: e.clientX, y: e.clientY });
							setShowTooltip(true);
						}}
						onMouseLeave={() => setShowTooltip(false)}
					>
						{/* Header */}
						<div className="flex items-center justify-between mb-3">
							<h3 className="font-semibold text-sm">User Authentication</h3>
							<span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
								in_progress
							</span>
						</div>

						{/* Content */}
						<p className="text-xs text-gray-600 mb-4">
							Implement secure user authentication with OAuth 2.0 support
						</p>

						{/* Actions */}
						<div className="space-y-3">
							<div className="flex items-center justify-between">
								<span className="text-xs text-gray-500">Actions:</span>
								<NodeActions
									nodeId="demo-node"
									isExpanded={isExpanded}
									onExpand={() => setIsExpanded(!isExpanded)}
									onNavigate={(id) => logger.info("Navigate:", id)}
									onShowMenu={(id) => logger.info("Menu:", id)}
								/>
							</div>

							{isExpanded && (
								<div className="pt-3 border-t">
									<NodeQuickActions
										nodeId="demo-node"
										onAddLink={(id, target) =>
											logger.info("Link:", id, "->", target)
										}
										onAddTag={(id, tag) => logger.info("Tag:", id, tag)}
										onEditNote={(id, note) => logger.info("Note:", id, note)}
									/>
								</div>
							)}
						</div>

						{/* Instructions */}
						<div className="mt-4 pt-3 border-t text-xs text-gray-500">
							<p>• Hover to see tooltip</p>
							<p>• Right-click for context menu</p>
							<p>• Click expand for quick actions</p>
						</div>
					</div>
				</NodeContextMenu>

				{/* Tooltip overlay */}
				{showTooltip && (
					<NodeHoverTooltip
						nodeId="demo-node"
						nodeType="requirement"
						label="User Authentication"
						status="in_progress"
						metadata={{
							assignee: "John Doe",
							deadline: "2024-12-31",
							priority: "high",
						}}
						position={hoverPosition}
					/>
				)}
			</div>
		);
	},
	title: "Graph/Interactions/Combined",
};
