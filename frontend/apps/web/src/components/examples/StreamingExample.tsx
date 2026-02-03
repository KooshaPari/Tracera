/**
 * Example component demonstrating NDJSON streaming usage
 */

import { useState } from "react";
import {
	useStreamExport,
	useStreamGraph,
	useStreamItems,
} from "../../hooks/useStreaming";
import { StreamingProgress, StreamingProgressBar } from "../StreamingProgress";

const DEFAULT_SLICE_SIZE = 10;
const DEFAULT_PREVIEW_SIZE = 3;
const MILLISECOND_OFFSET = -10;
const PREVIEW_OFFSET = 1;

function StreamItemsExample() {
	const [projectId, setProjectId] = useState("");
	const { items, state, startStreaming, stopStreaming, reset } =
		useStreamItems();

	const handleStart = () => {
		if (projectId) {
			startStreaming({ projectId });
		}
	};

	const renderItems = () => {
		const displayItems = items.slice(-DEFAULT_SLICE_SIZE);
		return (
			<div className="max-h-64 overflow-y-auto space-y-1">
				{displayItems.map((item, index) => {
					const itemKey = `item-${item.id ?? index}`;
					return (
						<div key={itemKey} className="p-2 bg-muted rounded text-sm">
							{JSON.stringify(item)}
						</div>
					);
				})}
			</div>
		);
	};

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Items Example</h3>

			<div className="flex gap-2">
				<input
					type="text"
					placeholder="Project ID"
					value={projectId}
					onChange={(e) => setProjectId(e.target.value)}
					className="flex-1 px-3 py-2 border rounded"
					disabled={state.isStreaming}
				/>
				<button
					onClick={handleStart}
					disabled={state.isStreaming || !projectId}
					className="px-4 py-2 bg-primary text-white rounded disabled:opacity-50"
				>
					Start Streaming
				</button>
				<button
					onClick={stopStreaming}
					disabled={!state.isStreaming}
					className="px-4 py-2 bg-destructive text-white rounded disabled:opacity-50"
				>
					Stop
				</button>
				<button
					onClick={reset}
					disabled={state.isStreaming}
					className="px-4 py-2 bg-secondary rounded disabled:opacity-50"
				>
					Reset
				</button>
			</div>

			<StreamingProgress
				stats={state.stats}
				isStreaming={state.isStreaming}
				showThroughput
				showBytes
			/>

			{state.error && (
				<div className="p-3 bg-destructive/10 text-destructive rounded">
					Error: {state.error.message}
				</div>
			)}

			<div className="space-y-2">
				<h4 className="font-medium">Received Items ({items.length})</h4>
				{renderItems()}
			</div>
		</div>
	);
}

function StreamGraphExample() {
	const [graphId, setGraphId] = useState("");
	const { nodes, edges, state, startStreaming, stopStreaming, reset } =
		useStreamGraph();

	const handleStart = () => {
		if (graphId) {
			startStreaming(graphId);
		}
	};

	const renderGraphPreview = () => {
		const previewNodes = nodes.slice(0, DEFAULT_PREVIEW_SIZE);
		const remainingCount = nodes.length - DEFAULT_PREVIEW_SIZE;

		return (
			<div className="p-4 bg-muted/50 rounded">
				<div className="text-sm text-muted-foreground mb-2">
					Graph Preview
				</div>
				<div className="text-xs space-y-1">
					{previewNodes.map((node, index) => (
						<div key={`node-${node.id ?? index}`}>
							Node: {JSON.stringify(node)}
						</div>
					))}
					{remainingCount > 0 && (
						<div>... and {remainingCount} more</div>
					)}
				</div>
			</div>
		);
	};

	const renderGraphStats = () => (
		<div className="grid grid-cols-2 gap-4">
			<div className="p-3 bg-muted rounded">
				<div className="text-sm text-muted-foreground">Nodes</div>
				<div className="text-2xl font-bold">{nodes.length}</div>
			</div>
			<div className="p-3 bg-muted rounded">
				<div className="text-sm text-muted-foreground">Edges</div>
				<div className="text-2xl font-bold">{edges.length}</div>
			</div>
		</div>
	);

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Graph Example</h3>

			<div className="flex gap-2">
				<input
					type="text"
					placeholder="Graph ID"
					value={graphId}
					onChange={(e) => setGraphId(e.target.value)}
					className="px-3 py-2 border rounded"
					disabled={state.isStreaming}
				/>
				<button
					onClick={handleStart}
					disabled={state.isStreaming || !graphId}
					className="px-4 py-2 bg-primary text-white rounded disabled:opacity-50"
				>
					Stream Graph
				</button>
				<button
					onClick={stopStreaming}
					disabled={!state.isStreaming}
					className="px-4 py-2 bg-destructive text-white rounded disabled:opacity-50"
				>
					Stop
				</button>
				<button
					onClick={reset}
					disabled={state.isStreaming}
					className="px-4 py-2 bg-secondary rounded disabled:opacity-50"
				>
					Reset
				</button>
			</div>

			<StreamingProgress
				stats={state.stats}
				isStreaming={state.isStreaming}
				showThroughput
			/>

			{renderGraphStats()}
			{renderGraphPreview()}
		</div>
	);
}

function StreamExportExample() {
	const [projectId, setProjectId] = useState("");
	const [exportType, setExportType] = useState<"json" | "csv">("json");
	const { data, state, startExport, stopExport, downloadAsFile, reset } =
		useStreamExport();

	const handleStart = () => {
		if (projectId) {
			startExport({ projectId, type: exportType });
		}
	};

	const handleDownload = () => {
		const timestamp = new Date()
			.toISOString()
			.split("T")[PREVIEW_OFFSET];
		downloadAsFile(`export-${projectId}-${timestamp}.json`);
	};

	const renderProgressBar = () => {
		if (!state.stats) {
			return null;
		}

		return (
			<StreamingProgressBar
				current={state.stats.itemsReceived}
				isStreaming={state.isStreaming}
			/>
		);
	};

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Export Example</h3>

			<div className="flex gap-2">
				<input
					type="text"
					placeholder="Project ID"
					value={projectId}
					onChange={(e) => setProjectId(e.target.value)}
					className="px-3 py-2 border rounded"
					disabled={state.isStreaming}
				/>
				<select
					value={exportType}
					onChange={(e) =>
						setExportType(e.target.value as "json" | "csv")
					}
					className="px-3 py-2 border rounded"
					disabled={state.isStreaming}
				>
					<option value="json">JSON</option>
					<option value="csv">CSV</option>
				</select>
				<button
					onClick={handleStart}
					disabled={state.isStreaming || !projectId}
					className="px-4 py-2 bg-primary text-white rounded disabled:opacity-50"
				>
					Start Export
				</button>
				<button
					onClick={stopExport}
					disabled={!state.isStreaming}
					className="px-4 py-2 bg-destructive text-white rounded disabled:opacity-50"
				>
					Stop
				</button>
			</div>

			<div className="space-y-2">
				<StreamingProgress
					stats={state.stats}
					isStreaming={state.isStreaming}
					showThroughput
					showBytes
				/>
				{renderProgressBar()}
			</div>

			<div className="p-3 bg-muted rounded">
				<div className="text-sm text-muted-foreground">Export Size</div>
				<div className="text-2xl font-bold">{data.length} items</div>
			</div>

			{data.length > 0 && !state.isStreaming && (
				<button
					onClick={handleDownload}
					className="px-4 py-2 bg-primary text-white rounded"
				>
					Download Export
				</button>
			)}

			<button
				onClick={reset}
				disabled={state.isStreaming}
				className="px-4 py-2 bg-secondary rounded disabled:opacity-50"
			>
				Reset
			</button>
		</div>
	);
}

function StreamingExamples() {
	return (
		<div className="space-y-8 p-6">
			<h2 className="text-2xl font-bold">NDJSON Streaming Examples</h2>
			<div className="grid gap-6">
				<StreamItemsExample />
				<StreamGraphExample />
				<StreamExportExample />
			</div>
		</div>
	);
}

export {
	StreamingExamples,
	StreamItemsExample,
	StreamGraphExample,
	StreamExportExample,
};
