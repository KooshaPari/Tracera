/**
 * Web Workers Usage Example
 *
 * Demonstrates how to use the worker hooks in a React component
 */

import { useState } from "react";
import {
	type WorkerStatus,
	useDataTransformWorker,
	useExportImportWorker,
	useGraphLayoutWorker,
	useSearchIndexWorker,
	useWorkerSupport,
} from "@/hooks/useWorker";

const DEFAULT_NODE_SIZE = 50;
const DIRECTION_TB = "TB";
const LAYOUT_TYPE_DAGRE = "dagre";
const MAX_DISPLAY_ITEMS = 10;
const CATEGORY_COUNT = 3;
const DEFAULT_WEIGHT = 1;
const TITLE_WEIGHT_MULTIPLIER = 2;
const MAX_DISTANCE = 2;
const DEFAULT_CATEGORY_LIST = ["A", "B", "C"] as const;

const defaultNode = { height: DEFAULT_NODE_SIZE, width: DEFAULT_NODE_SIZE * 2 };

const defaultNodes = [
	{ ...defaultNode, id: "A" },
	{ ...defaultNode, id: "B" },
	{ ...defaultNode, id: "C" },
];

const defaultEdges = [
	{ id: "AB", source: "A", target: "B" },
	{ id: "BC", source: "B", target: "C" },
];

const layoutOptions = { direction: DIRECTION_TB, type: LAYOUT_TYPE_DAGRE };

const indexFieldWeights = {
	content: DEFAULT_WEIGHT,
	title: TITLE_WEIGHT_MULTIPLIER,
};

function GraphLayoutExample() {
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

	const renderStatus = () => {
		if (status.error) {
			return (
				<div className="text-red-500">
					Error: {status.error.message}
				</div>
			);
		}
		if (status.progress > 0) {
			return (
				<div className="mt-2">
					<div className="text-sm mb-1">
						Progress: {status.progress.toFixed(0)}%
					</div>
					<div className="w-full bg-gray-200 rounded">
						<div
							className="bg-blue-500 h-2 rounded transition-all"
							style={{ width: `${status.progress}%` }}
						/>
					</div>
				</div>
			);
		}
		return null;
	};

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Graph Layout Worker</h2>

			<div className="mb-4">
				<div>Status: {status.isReady ? "Ready" : "Loading..."}</div>
				{renderStatus()}
			</div>

			<button
				disabled={!status.isReady}
				className="px-4 py-2 bg-blue-500 text-white rounded disabled:opacity-50"
				onClick={handleComputeLayout}
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

const generateRandomData = (count: number) =>
	Array.from({ length: count }, (_, i) => ({
		category: DEFAULT_CATEGORY_LIST[i % CATEGORY_COUNT],
		id: i,
		value: Math.random() * 100,
	}));

const transformResultDisplay = (
	result: Readonly<{
		readonly aggregated: unknown;
		readonly sorted: ReadonlyArray<{ id: number; value: number }>;
		readonly stats: unknown;
	}>,
) => (
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
				{result.sorted.map((item) => (
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
);

function DataTransformExample() {
	const { worker, status } = useDataTransformWorker();
	const [result, setResult] = useState<Readonly<{
		readonly aggregated: unknown;
		readonly sorted: ReadonlyArray<{ id: number; value: number }>;
		readonly stats: unknown;
	}> | null>(null);

	const handleTransform = async () => {
		if (!worker) {
			return;
		}

		const data = generateRandomData(1000);

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
				sorted: sorted.slice(0, MAX_DISPLAY_ITEMS),
				stats,
			});
		} catch {
			// Error handling is managed through status.error
		}
	};

	const isDisabled = !status.isReady;

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Data Transform Worker</h2>

			<button
				disabled={isDisabled}
				className="px-4 py-2 bg-green-500 text-white rounded disabled:opacity-50"
				onClick={handleTransform}
			>
				Transform 1000 Items
			</button>

			{result && transformResultDisplay(result)}
		</div>
	);
}

const sampleExportData = [
	{ age: 30, id: 1, name: "Alice" },
	{ age: 25, id: 2, name: "Bob" },
	{ age: 35, id: 3, name: "Charlie" },
];

function ExportImportExample() {
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
					disabled={!status.isReady}
					className="px-4 py-2 bg-purple-500 text-white rounded disabled:opacity-50"
					onClick={handleExport}
				>
					Export to NDJSON
				</button>
				<button
					disabled={!status.isReady || !exported}
					className="px-4 py-2 bg-purple-700 text-white rounded disabled:opacity-50"
					onClick={handleImport}
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
		fields: {
			content: "React is a JavaScript library for building user interfaces",
			title: "Introduction to React",
		},
		id: "1",
	},
	{
		fields: {
			content: "Vue is a progressive framework for building user interfaces",
			title: "Vue.js Basics",
		},
		id: "2",
	},
	{
		fields: {
			content: "Angular is a platform for building web applications",
			title: "Angular Guide",
		},
		id: "3",
	},
];

const defaultSearchOptions = {
	fuzzy: true,
	maxDistance: MAX_DISTANCE,
};

function SearchIndexExample() {
	const { worker, status } = useSearchIndexWorker();
	const [index, setIndex] = useState<unknown>(null);
	const [query, setQuery] = useState("");
	const [results, setResults] = useState<ReadonlyArray<{
		id: string;
		score: number;
	}>>([]);

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
			const searchResults = await worker.search(
				index,
				query,
				defaultSearchOptions,
			);
			setResults(searchResults);
		} catch {
			// Error handling is managed through status.error
		}
	};

	const renderSearchResults = () => {
		if (results.length === 0) {
			return null;
		}

		return (
			<div className="mt-4">
				<h3 className="font-semibold">Results:</h3>
				<ul className="mt-2 space-y-2">
					{results.map((result) => (
						<li key={result.id} className="p-2 bg-gray-100 rounded">
							<div className="font-medium">Document {result.id}</div>
							<div className="text-sm text-gray-600">
								Score: {result.score.toFixed(2)}
							</div>
						</li>
					))}
				</ul>
			</div>
		);
	};

	const isBuildDisabled = !status.isReady;
	const isSearchDisabled = !status.isReady || !index || !query;

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Search Index Worker</h2>

			<div className="space-y-4">
				<button
					disabled={isBuildDisabled}
					className="px-4 py-2 bg-orange-500 text-white rounded disabled:opacity-50"
					onClick={handleBuildIndex}
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
								disabled={isSearchDisabled}
								className="px-4 py-2 bg-orange-700 text-white rounded"
								onClick={handleSearch}
							>
								Search
							</button>
						</div>

						{renderSearchResults()}
					</>
				)}
			</div>
		</div>
	);
}

function WorkerSupportCheck() {
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
function WebWorkersDemo() {
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

export {
	WebWorkersDemo,
	GraphLayoutExample,
	DataTransformExample,
	ExportImportExample,
	SearchIndexExample,
	WorkerSupportCheck,
};
