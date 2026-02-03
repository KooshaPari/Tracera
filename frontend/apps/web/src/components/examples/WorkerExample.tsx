/**
 * Web Workers Usage Example
 *
 * Demonstrates how to use the worker hooks in a React component
 */

import {
	useDataTransformWorker,
	useExportImportWorker,
	useGraphLayoutWorker,
	useSearchIndexWorker,
	useWorkerSupport,
} from "@/hooks/useWorker";
import { useState } from "react";

const NODE_HEIGHT = 50;
const NODE_WIDTH = 100;
const NODE_COUNT = 3;
const CATEGORY_MODULO = 3;
const MAX_ITEMS_DISPLAY = 10;
const DATA_LENGTH = 1000;
const TITLE_WEIGHT = 2;
const DEFAULT_WEIGHT = 1;
const MAX_DISTANCE = 2;

const defaultNodes = [
	{ height: NODE_HEIGHT, id: "A", width: NODE_WIDTH },
	{ height: NODE_HEIGHT, id: "B", width: NODE_WIDTH },
	{ height: NODE_HEIGHT, id: "C", width: NODE_WIDTH },
];

const defaultEdges = [
	{ id: "AB", source: "A", target: "B" },
	{ id: "BC", source: "B", target: "C" },
];

const layoutOptions = { direction: "TB", type: "dagre" as const };

const categoryList = ["A", "B", "C"] as const;

const generateData = (length: number) =>
	Array.from({ length }, (_, i) => ({
		category: categoryList[i % CATEGORY_MODULO],
		id: i,
		value: Math.random() * 100,
	}));

const indexFieldWeights = {
	content: DEFAULT_WEIGHT,
	title: TITLE_WEIGHT,
};

const searchOptions = {
	fuzzy: true,
	maxDistance: MAX_DISTANCE,
};

export function GraphLayoutExample() {
	const { worker, status, createProgressCallback } = useGraphLayoutWorker();
	const [layoutResult, setLayoutResult] = useState<unknown>(null);

	const handleComputeLayout = async () => {
		if (!worker) {
			return;
		}

		const onProgress = createProgressCallback();

		try {
			const result = await worker.computeLayout(
				defaultNodes,
				defaultEdges,
				layoutOptions,
				onProgress,
			);
			setLayoutResult(result);
		} catch {
			// Error handling is managed through status.error
		}
	};

	const statusMessage = status.isReady ? "Ready" : "Loading...";
	const progressPercent = status.progress.toFixed(0);

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Graph Layout Worker</h2>

			<div className="mb-4">
				<div>Status: {statusMessage}</div>
				{status.error && (
					<div className="text-red-500">Error: {status.error.message}</div>
				)}
				{status.progress > 0 && (
					<div className="mt-2">
						<div className="text-sm mb-1">
							Progress: {progressPercent}%
						</div>
						<div className="w-full bg-gray-200 rounded">
							<div
								className="bg-blue-500 h-2 rounded transition-all"
								style={{ width: `${status.progress}%` }}
							/>
						</div>
					</div>
				)}
			</div>

			<button
				onClick={handleComputeLayout}
				disabled={!status.isReady}
				className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
			>
				Compute Layout
			</button>

			{layoutResult && (
				<div className="mt-4">
					<h3 className="font-semibold">Result:</h3>
					<pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
						{JSON.stringify(layoutResult, null, 2)}
					</pre>
				</div>
			)}
		</div>
	);
}

export function DataTransformExample() {
	const { worker, status } = useDataTransformWorker();
	const [result, setResult] = useState<unknown>(null);

	const handleTransform = async () => {
		if (!worker) {
			return;
		}

		const data = generateData(DATA_LENGTH);

		try {
			const sorted = await worker.sortData(data, "value", "desc");
			const stats = await worker.calculateStatistics(data, "value");
			const aggregated = await worker.aggregateData(
				data,
				"category",
				"value",
				"sum",
			);

			setResult({
				aggregated,
				sorted: sorted.slice(0, MAX_ITEMS_DISPLAY),
				stats,
			});
		} catch {
			// Error handling is managed through status.error
		}
	};

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Data Transform Worker</h2>

			<button
				onClick={handleTransform}
				disabled={!status.isReady}
				className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
			>
				Transform 1000 Items
			</button>

			{result && (
				<div className="mt-4 space-y-2">
					<div>
						<h3 className="font-semibold">Statistics:</h3>
						<pre className="mt-1 p-2 bg-gray-100 rounded text-xs">
							{JSON.stringify(result.stats, null, 2)}
						</pre>
					</div>
					<div>
						<h3 className="font-semibold">Top 10 (sorted):</h3>
						<ul className="mt-1 text-sm">
							{result.sorted.map((item: { id: number; value: number }) => (
								<li key={item.id}>
									ID: {item.id}, Value: {item.value.toFixed(2)}
								</li>
							))}
						</ul>
					</div>
					<div>
						<h3 className="font-semibold">Aggregated by Category:</h3>
						<pre className="mt-1 p-2 bg-gray-100 rounded text-xs">
							{JSON.stringify(result.aggregated, null, 2)}
						</pre>
					</div>
				</div>
			)}
		</div>
	);
}

const sampleExportData = [
	{ age: 30, id: 1, name: "Alice" },
	{ age: 25, id: 2, name: "Bob" },
	{ age: 35, id: 3, name: "Charlie" },
];

export function ExportImportExample() {
	const { worker, status } = useExportImportWorker();
	const [exported, setExported] = useState("");

	const handleExport = async () => {
		if (!worker) {
			return;
		}

		try {
			const ndjson = await worker.generateNDJSON(sampleExportData);
			setExported(ndjson);
		} catch {
			// Error handling is managed through status.error
		}
	};

	const handleImport = async () => {
		if (!worker || !exported) {
			return;
		}

		try {
			const data = await worker.parseNDJSON(exported);
			// eslint-disable-next-line no-console
			console.log(`Imported ${data.length} items`);
		} catch {
			// Error handling is managed through status.error
		}
	};

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Export/Import Worker</h2>

			<div className="space-x-2 mb-4">
				<button
					onClick={handleExport}
					disabled={!status.isReady}
					className="px-4 py-2 bg-purple-500 text-white rounded disabled:opacity-50"
				>
					Export to NDJSON
				</button>
				<button
					onClick={handleImport}
					disabled={!status.isReady || !exported}
					className="px-4 py-2 bg-purple-700 text-white rounded disabled:opacity-50"
				>
					Import from NDJSON
				</button>
			</div>

			{exported && (
				<div className="mt-4">
					<h3 className="font-semibold">Exported NDJSON:</h3>
					<pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
						{exported}
					</pre>
				</div>
			)}
		</div>
	);
}

const sampleDocuments = [
	{
		id: "1",
		fields: {
			content: "React is a JavaScript library for building user interfaces",
			title: "Introduction to React",
		},
	},
	{
		id: "2",
		fields: {
			content: "Vue is a progressive framework for building user interfaces",
			title: "Vue.js Basics",
		},
	},
	{
		id: "3",
		fields: {
			content: "Angular is a platform for building web applications",
			title: "Angular Guide",
		},
	},
];

export function SearchIndexExample() {
	const { worker, status } = useSearchIndexWorker();
	const [index, setIndex] = useState<unknown>(null);
	const [query, setQuery] = useState("");
	const [results, setResults] = useState<
		ReadonlyArray<{ id: string; score: number }>
	>([]);

	const handleBuildIndex = async () => {
		if (!worker) {
			return;
		}

		try {
			const newIndex = await worker.buildIndex(
				sampleDocuments,
				indexFieldWeights,
			);
			setIndex(newIndex);
		} catch {
			// Error handling is managed through status.error
		}
	};

	const handleSearch = async () => {
		if (!worker || !index || !query) {
			return;
		}

		try {
			const searchResults = await worker.search(index, query, searchOptions);
			setResults(searchResults);
		} catch {
			// Error handling is managed through status.error
		}
	};

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Search Index Worker</h2>

			<div className="space-y-4">
				<button
					onClick={handleBuildIndex}
					disabled={!status.isReady}
					className="px-4 py-2 bg-orange-500 text-white rounded disabled:opacity-50"
				>
					Build Index
				</button>

				{index && (
					<>
						<div className="flex gap-2">
							<input
								type="text"
								value={query}
								onChange={(e) => setQuery(e.target.value)}
								placeholder="Search query..."
								className="flex-1 px-3 py-2 border rounded"
							/>
							<button
								onClick={handleSearch}
								className="px-4 py-2 bg-orange-700 text-white rounded"
							>
								Search
							</button>
						</div>

						{results.length > 0 && (
							<div className="mt-4">
								<h3 className="font-semibold">Results:</h3>
								<ul className="mt-2 space-y-2">
									{results.map((result) => (
										<li key={result.id} className="p-2 bg-gray-100 rounded">
											<div className="font-medium">
												Document {result.id}
											</div>
											<div className="text-sm text-gray-600">
												Score: {result.score.toFixed(2)}
											</div>
										</li>
									))}
								</ul>
							</div>
						)}
					</>
				)}
			</div>
		</div>
	);
}

export function WorkerSupportCheck() {
	const { supported, checked } = useWorkerSupport();

	if (!checked) {
		return <div>Checking Web Worker support...</div>;
	}

	const containerClass = supported ? "bg-green-50" : "bg-red-50";
	const messageClass = supported ? "text-green-700" : "text-red-700";
	const supportMessage = supported
		? "Web Workers are supported in this browser"
		: "Web Workers are not supported. Some features may be unavailable or slower.";

	return (
		<div className={`p-4 border rounded ${containerClass}`}>
			<h3 className="font-semibold mb-2">Web Worker Support</h3>
			<div className={messageClass}>
				{supported ? "✓" : "✗"} {supportMessage}
			</div>
		</div>
	);
}

/**
 * Main demo component showing all worker examples
 */
export function WebWorkersDemo() {
	return (
		<div className="p-8 max-w-6xl mx-auto">
			<h1 className="text-3xl font-bold mb-8">Web Workers Demo</h1>

			<div className="space-y-6">
				<WorkerSupportCheck />
				<GraphLayoutExample />
				<DataTransformExample />
				<ExportImportExample />
				<SearchIndexExample />
			</div>
		</div>
	);
}
