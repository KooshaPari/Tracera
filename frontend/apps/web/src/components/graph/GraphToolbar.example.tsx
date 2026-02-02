// Example: Integrating GraphToolbar into FlowGraphViewInner
// This shows how to use the new toolbar with all features

import { useState, useCallback } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { FlowGraphViewInner } from "./FlowGraphViewInner";
import { GraphToolbar } from "./GraphToolbar";
import type { Item, Link } from "@tracertm/types";
import type { LayoutType } from "./layouts/useDAGLayout";
import type { GraphPerspective } from "./types";
import { logger } from '@/lib/logger';

interface EnhancedGraphViewProps {
	items: Item[];
	links: Link[];
	onNavigateToItem?: (itemId: string) => void;
}

export function EnhancedGraphView({
	items,
	links,
	onNavigateToItem,
}: EnhancedGraphViewProps) {
	// State management
	const [layout, setLayout] = useState<LayoutType>("flow-chart");
	const [perspective, setPerspective] = useState<GraphPerspective>("all");
	const [showDetailPanel, setShowDetailPanel] = useState(true);
	const [isFullscreen, setIsFullscreen] = useState(false);
	const [selectedNodeTypes, setSelectedNodeTypes] = useState<string[]>([]);

	// Derive unique node types from items
	const nodeTypes = Array.from(
		new Set(items.map((item) => item.type || "item").map((t) => t.toLowerCase()))
	);

	// Fullscreen toggle
	const handleFullscreenToggle = useCallback(async () => {
		const container = document.querySelector(".graph-container");
		if (!container) return;

		try {
			if (document.fullscreenElement) {
				await document.exitFullscreen();
				setIsFullscreen(false);
			} else {
				await (container as HTMLElement).requestFullscreen();
				setIsFullscreen(true);
			}
        } catch {
            // Fullscreen not supported or denied
		}
	}, []);

	// Reset all filters and view
	const handleReset = useCallback(() => {
		setPerspective("all");
		setLayout("flow-chart");
		setSelectedNodeTypes([]);
	}, []);

	// Export handler
	const handleExport = useCallback((format: "png" | "svg" | "json" | "csv") => {
		logger.info(`Exporting graph as ${format}`);
		// Export logic is handled by ExportControls internally
	}, []);

	// Filter items by selected types
	const filteredItems =
		selectedNodeTypes.length > 0
			? items.filter((item) =>
					selectedNodeTypes.includes((item.type || "item").toLowerCase())
				)
			: items;

	return (
		<ReactFlowProvider>
			<div className="h-full flex flex-col graph-container">
				{/* Professional Toolbar */}
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
					onToggleFullscreen={handleFullscreenToggle}
					totalNodes={items.length}
					visibleNodes={filteredItems.length}
					totalEdges={links.length}
					visibleEdges={links.length}
					onReset={handleReset}
					onExport={handleExport}
					variant="full" // or "compact" or "minimal"
				/>

				{/* Graph View */}
				<div className="flex-1 mt-3">
					<FlowGraphViewInner
						items={filteredItems}
						links={links}
						perspective={perspective}
						defaultLayout={layout}
						onNavigateToItem={onNavigateToItem}
						showControls={false} // Toolbar provides controls
						autoFit={true}
					/>
				</div>
			</div>
		</ReactFlowProvider>
	);
}

// Compact variant example
export function CompactGraphView({
	items,
	links,
}: {
	items: Item[];
	links: Link[];
}) {
	const [layout, setLayout] = useState<LayoutType>("flow-chart");
	const [showDetailPanel, setShowDetailPanel] = useState(true);

	return (
		<ReactFlowProvider>
			<div className="h-full flex flex-col">
				<GraphToolbar
					layout={layout}
					onLayoutChange={setLayout}
					showDetailPanel={showDetailPanel}
					onToggleDetailPanel={() => setShowDetailPanel(!showDetailPanel)}
					isFullscreen={false}
					onToggleFullscreen={() => {}}
					variant="compact"
				/>

				<div className="flex-1 mt-2">
					<FlowGraphViewInner
						items={items}
						links={links}
						defaultLayout={layout}
						showControls={false}
					/>
				</div>
			</div>
		</ReactFlowProvider>
	);
}

// Minimal variant example
export function MinimalGraphView({
	items,
	links,
}: {
	items: Item[];
	links: Link[];
}) {
	return (
		<ReactFlowProvider>
			<div className="h-full flex flex-col">
				<GraphToolbar
					layout="flow-chart"
					onLayoutChange={() => {}}
					showDetailPanel={false}
					onToggleDetailPanel={() => {}}
					isFullscreen={false}
					onToggleFullscreen={() => {}}
					variant="minimal"
				/>

				<div className="flex-1 mt-1">
					<FlowGraphViewInner items={items} links={links} showControls={false} />
				</div>
			</div>
		</ReactFlowProvider>
	);
}
