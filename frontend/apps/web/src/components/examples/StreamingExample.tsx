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

export function StreamItemsExample() {
	const [projectId, setProjectId] = useState("");
	const { items, state, startStreaming, stopStreaming, reset } =
		useStreamItems();

	const handleStart = () => {
		if (projectId) {
			startStreaming({ projectId });
		}
	};

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Items Example</h3>

			{/* Controls */}
			<div className="flex gap-2">
				<input
					type="text"
					placeholder="Project ID"
					value={projectId}
					onChange={(e) => setProjectId(e.target.value)}
					className="px-3 py-2 border rounded"
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

			{/* Progress */}
			<StreamingProgress
				stats={state.stats}
				isStreaming={state.isStreaming}
				showThroughput
				showBytes
			/>

			{/* Error display */}
			{state.error && (
				<div className="p-3 bg-destructive/10 text-destructive rounded">
					Error: {state.error.message}
				</div>
			)}

			{/* Items display */}
			<div className="space-y-2">
				<h4 className="font-medium">Received Items ({items.length})</h4>
				<div className="max-h-64 overflow-y-auto space-y-1">
					{items.slice(-10).map((item, i) => (
						<div key={i} className="p-2 bg-muted rounded text-sm">
							{JSON.stringify(item)}
						</div>
					))}
				</div>
			</div>
		</div>
	);
}

export function StreamGraphExample() {
	const [graphId, setGraphId] = useState("");
	const { nodes, edges, state, startStreaming, stopStreaming, reset } =
		useStreamGraph();

	const handleStart = () => {
		if (graphId) {
			startStreaming(graphId);
		}
	};

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Graph Example</h3>

			{/* Controls */}
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

			{/* Progress */}
			<StreamingProgress
				stats={state.stats}
				isStreaming={state.isStreaming}
				showThroughput
			/>

			{/* Graph stats */}
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

			{/* Graph visualization preview */}
			<div className="p-4 bg-muted/50 rounded">
				<div className="text-sm text-muted-foreground mb-2">Graph Preview</div>
				<div className="text-xs space-y-1">
					{nodes.slice(0, 3).map((node, i) => (
						<div key={i}>Node: {JSON.stringify(node)}</div>
					))}
					{nodes.length > 3 && <div>... and {nodes.length - 3} more</div>}
				</div>
			</div>
		</div>
	);
}

export function StreamExportExample() {
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
		const timestamp = new Date().toISOString().split("T")[0];
		downloadAsFile(`export-${projectId}-${timestamp}.json`);
	};

	return (
		<div className="space-y-4 p-4 border rounded-lg">
			<h3 className="text-lg font-semibold">Stream Export Example</h3>

			{/* Controls */}
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
					onChange={(e) => setExportType(e.target.value as "json" | "csv")}
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

			{/* Progress with progress bar */}
			<div className="space-y-2">
				<StreamingProgress
					stats={state.stats}
					isStreaming={state.isStreaming}
					showThroughput
					showBytes
				/>
				{state.stats && (
					<StreamingProgressBar
						current={state.stats.itemsReceived}
						isStreaming={state.isStreaming}
					/>
				)}
			</div>

			{/* Export stats */}
			<div className="p-3 bg-muted rounded">
				<div className="text-sm text-muted-foreground">Export Size</div>
				<div className="text-2xl font-bold">{data.length} items</div>
			</div>

			{/* Download button */}
			{data.length > 0 && !state.isStreaming && (
				<button
					onClick={handleDownload}
					className="px-4 py-2 bg-primary text-white rounded"
				>
					Download Export
				</button>
			)}

			{/* Reset button */}
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

export function StreamingExamples() {
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
