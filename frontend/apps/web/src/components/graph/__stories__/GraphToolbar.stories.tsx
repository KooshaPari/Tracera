// Storybook Stories for GraphToolbar
// Demonstrates all toolbar variants and configurations

import type { Meta, StoryObj } from "@storybook/react";
import { ReactFlowProvider } from "@xyflow/react";
import { GraphToolbar } from "../GraphToolbar";
import { useState } from "react";
import type { LayoutType } from "../layouts/useDAGLayout";
import type { GraphPerspective } from "../types";

const meta: Meta<typeof GraphToolbar> = {
	title: "Graph/GraphToolbar",
	component: GraphToolbar,
	decorators: [
		(Story) => (
			<ReactFlowProvider>
				<div className="h-screen bg-background p-4">
					<Story />
				</div>
			</ReactFlowProvider>
		),
	],
	parameters: {
		layout: "fullscreen",
	},
	tags: ["autodocs"],
};

export default meta;
type Story = StoryObj<typeof GraphToolbar>;

// Interactive wrapper for stateful toolbar
function ToolbarWrapper({ variant }: { variant?: "full" | "compact" | "minimal" }) {
	const [layout, setLayout] = useState<LayoutType>("flow-chart");
	const [perspective, setPerspective] = useState<GraphPerspective>("all");
	const [showDetailPanel, setShowDetailPanel] = useState(true);
	const [isFullscreen, setIsFullscreen] = useState(false);
	const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([]);

	const nodeTypes = [
		"requirement",
		"feature",
		"user_story",
		"epic",
		"task",
		"test_case",
		"bug",
		"api",
		"database",
		"ui_component",
	];

	return (
		<GraphToolbar
			layout={layout}
			onLayoutChange={setLayout}
			perspective={perspective}
			onPerspectiveChange={setPerspective}
			nodeTypes={nodeTypes}
			selectedNodeTypes={selectedNodeTypes}
			onNodeTypeFilterChange={setSelectedNodeTypes}
			showDetailPanel={showDetailPanel}
			onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
			isFullscreen={isFullscreen}
			onToggleFullscreen={() => setIsFullscreen(!isFullscreen)}
			totalNodes={150}
			visibleNodes={120}
			totalEdges={300}
			visibleEdges={250}
			onReset={() => {
				setPerspective("all");
				setLayout("flow-chart");
				setSelectedNodeTypes([]);
			}}
			onExport={(format) => logger.info("Export:", format)}
			variant={variant}
		/>
	);
}

// Full variant with all features
export const Full: Story = {
	render: () => <ToolbarWrapper variant="full" />,
	parameters: {
		docs: {
			description: {
				story:
					"Complete toolbar with layout selector, filters, export controls, zoom, and view options. Best for desktop graph views.",
			},
		},
	},
};

// Compact variant
export const Compact: Story = {
	render: () => <ToolbarWrapper variant="compact" />,
	parameters: {
		docs: {
			description: {
				story:
					"Compact toolbar with essential controls - layout selector and zoom controls. Good for tablet views.",
			},
		},
	},
};

// Minimal variant
export const Minimal: Story = {
	render: () => <ToolbarWrapper variant="minimal" />,
	parameters: {
		docs: {
			description: {
				story:
					"Minimal toolbar with only zoom controls. Ideal for mobile views or embedded graphs.",
			},
		},
	},
};

// With active filters
export const WithFilters: Story = {
	render: () => {
		const [layout, setLayout] = useState<LayoutType>("flow-chart");
		const [perspective, setPerspective] = useState<GraphPerspective>("technical");
		const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([
			"api",
			"database",
			"code",
		]);
		const [showDetailPanel, setShowDetailPanel] = useState(true);

		return (
			<GraphToolbar
				layout={layout}
				onLayoutChange={setLayout}
				perspective={perspective}
				onPerspectiveChange={setPerspective}
				nodeTypes={[
					"requirement",
					"feature",
					"api",
					"database",
					"code",
					"test_case",
				]}
				selectedNodeTypes={selectedNodeTypes}
				onNodeTypeFilterChange={setSelectedNodeTypes}
				showDetailPanel={showDetailPanel}
				onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
				isFullscreen={false}
				onToggleFullscreen={() => {}}
				totalNodes={150}
				visibleNodes={45}
				totalEdges={300}
				visibleEdges={90}
				variant="full"
			/>
		);
	},
	parameters: {
		docs: {
			description: {
				story:
					"Toolbar with active filters showing how it displays selected perspectives and node types.",
			},
		},
	},
};

// Large dataset
export const LargeDataset: Story = {
	render: () => <ToolbarWrapper variant="full" />,
	args: {
		totalNodes: 5000,
		visibleNodes: 500,
		totalEdges: 12000,
		visibleEdges: 1200,
	},
	parameters: {
		docs: {
			description: {
				story: "Toolbar with large dataset statistics showing culling information.",
			},
		},
	},
};

// Disabled state
export const Disabled: Story = {
	render: () => (
		<GraphToolbar
			layout="flow-chart"
			onLayoutChange={() => {}}
			showDetailPanel={false}
			onToggleDetailPanel={() => {}}
			isFullscreen={false}
			onToggleFullscreen={() => {}}
			totalNodes={0}
			visibleNodes={0}
			variant="full"
		/>
	),
	parameters: {
		docs: {
			description: {
				story: "Toolbar with no data (disabled state).",
			},
		},
	},
};

// Fullscreen mode
export const Fullscreen: Story = {
	render: () => {
		const [isFullscreen, setIsFullscreen] = useState(true);

		return (
			<GraphToolbar
				layout="flow-chart"
				onLayoutChange={() => {}}
				showDetailPanel={true}
				onToggleDetailPanel={() => {}}
				isFullscreen={isFullscreen}
				onToggleFullscreen={() => setIsFullscreen(!isFullscreen)}
				totalNodes={100}
				visibleNodes={100}
				variant="full"
			/>
		);
	},
	parameters: {
		docs: {
			description: {
				story: "Toolbar in fullscreen mode showing exit fullscreen button.",
			},
		},
	},
};

// Keyboard shortcuts documentation
export const KeyboardShortcuts: Story = {
	render: () => (
		<div className="space-y-4">
			<h2 className="text-2xl font-bold">Keyboard Shortcuts</h2>

			<div className="grid grid-cols-2 gap-4">
				<div className="space-y-2">
					<h3 className="text-lg font-semibold">Zoom Controls</h3>
					<div className="space-y-1 text-sm">
						<div className="flex justify-between">
							<span>Zoom In</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + Plus</kbd>
						</div>
						<div className="flex justify-between">
							<span>Zoom Out</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + Minus</kbd>
						</div>
						<div className="flex justify-between">
							<span>Fit View</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + 0</kbd>
						</div>
						<div className="flex justify-between">
							<span>Actual Size</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + 1</kbd>
						</div>
					</div>
				</div>

				<div className="space-y-2">
					<h3 className="text-lg font-semibold">View Controls</h3>
					<div className="space-y-1 text-sm">
						<div className="flex justify-between">
							<span>Fullscreen</span>
							<kbd className="px-2 py-1 bg-muted rounded">F</kbd>
						</div>
						<div className="flex justify-between">
							<span>Toggle Detail Panel</span>
							<kbd className="px-2 py-1 bg-muted rounded">P</kbd>
						</div>
						<div className="flex justify-between">
							<span>Toggle Mini-map</span>
							<kbd className="px-2 py-1 bg-muted rounded">M</kbd>
						</div>
					</div>
				</div>

				<div className="space-y-2">
					<h3 className="text-lg font-semibold">Actions</h3>
					<div className="space-y-1 text-sm">
						<div className="flex justify-between">
							<span>Export</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + E</kbd>
						</div>
						<div className="flex justify-between">
							<span>Toggle Filters</span>
							<kbd className="px-2 py-1 bg-muted rounded">Cmd/Ctrl + F</kbd>
						</div>
						<div className="flex justify-between">
							<span>Reset View</span>
							<kbd className="px-2 py-1 bg-muted rounded">
								Cmd/Ctrl + Shift + R
							</kbd>
						</div>
					</div>
				</div>
			</div>

			<div className="mt-8">
				<ToolbarWrapper variant="full" />
			</div>
		</div>
	),
	parameters: {
		docs: {
			description: {
				story:
					"Complete keyboard shortcuts reference for the graph toolbar. All shortcuts work when the graph has focus.",
			},
		},
	},
};
