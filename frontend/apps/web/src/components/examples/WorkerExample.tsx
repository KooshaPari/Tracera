/**
 * Web Workers Usage Example
 *
 * Demonstrates how to use the worker hooks in a React component
 */

import { useState } from "react";
import {
	useDataTransformWorker,
	useExportImportWorker,
	useGraphLayoutWorker,
	useSearchIndexWorker,
	useWorkerSupport,
} from "@/hooks/useWorker";

export function GraphLayoutExample() {
	const { worker, status, createProgressCallback } = useGraphLayoutWorker();
	const [layoutResult, setLayoutResult] = useState<any>(null);

	const handleComputeLayout = async () => {
		if (!worker) {
			return;
		}

		const nodes = [
			{ height: 50, id: "A", width: 100 },
			{ height: 50, id: "B", width: 100 },
			{ height: 50, id: "C", width: 100 },
		];

		const edges = [
			{ id: "AB", source: "A", target: "B" },
			{ id: "BC", source: "B", target: "C" },
		];

		const onProgress = createProgressCallback();

		try {
			const result = await worker.computeLayout(
				nodes,
				edges,
				{ direction: "TB", type: "dagre" },
				onProgress,
			);
			setLayoutResult(result);
		} catch (error) {}
	};

	return (
		<div className="p-4 border rounded">
			<h2 className="text-lg font-bold mb-4">Graph Layout Worker</h2>

			<div className="mb-4">
				<div>Status: {status.isReady ? "✅ Ready" : "⏳ Loading..."}</div>
				{status.error && (
					<div className="text-red-500">Error: {status.error.message}</div>
				)}
				{status.progress > 0 && (
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
	const [result, setResult] = useState<any>(null);

	const handleTransform = async () => {
		if (!worker) {
			return;
		}

		const data = Array.from({ length: 1000 }, (_, i) => ({
			category: ["A", "B", "C"][i % 3],
			id: i,
			value: Math.random() * 100,
		}));

		try {
			// Sort data
			const sorted = await worker.sortData(data, "value", "desc");

			// Calculate statistics
			const stats = await worker.calculateStatistics(data, "value");

			// Aggregate by category
			const aggregated = await worker.aggregateData(
				data,
				"category",
				"value",
				"sum",
			);

			setResult({ aggregated, sorted: sorted.slice(0, 10), stats });
		} catch (error) {}
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
							{result.sorted.map((item: any) => (
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

export function ExportImportExample() {
	const { worker, status } = useExportImportWorker();
	const [exported, setExported] = useState<string>("");

	const handleExport = async () => {
		if (!worker) {
			return;
		}

		const data = [
			{ age: 30, id: 1, name: "Alice" },
			{ age: 25, id: 2, name: "Bob" },
			{ age: 35, id: 3, name: "Charlie" },
		];

		try {
			const ndjson = await worker.generateNDJSON(data);
			setExported(ndjson);
		} catch (error) {}
	};

	const handleImport = async () => {
		if (!worker || !exported) {
			return;
		}

		try {
			const data = await worker.parseNDJSON(exported);

			alert(`Imported ${data.length} items`);
		} catch (error) {}
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

export function SearchIndexExample() {
	const { worker, status } = useSearchIndexWorker();
	const [index, setIndex] = useState<any>(null);
	const [query, setQuery] = useState("");
	const [results, setResults] = useState<any[]>([]);

	const handleBuildIndex = async () => {
		if (!worker) {
			return;
		}

		const documents = [
			{
				fields: {
					content: "React is a JavaScript library for building user interfaces",
					title: "Introduction to React",
				},
				id: "1",
			},
			{
				fields: {
					content:
						"Vue is a progressive framework for building user interfaces",
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

		try {
			const newIndex = await worker.buildIndex(documents, {
				title: 2, // Title has 2x weight
				content: 1, // Content has default weight
			});
			setIndex(newIndex);
		} catch (error) {}
	};

	const handleSearch = async () => {
		if (!worker || !index || !query) {
			return;
		}

		try {
			const searchResults = await worker.search(index, query, {
				fuzzy: true,
				maxDistance: 2,
			});
			setResults(searchResults);
		} catch (error) {}
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
											<div className="font-medium">Document {result.id}</div>
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

	return (
		<div
			className={`p-4 border rounded ${supported ? "bg-green-50" : "bg-red-50"}`}
		>
			<h3 className="font-semibold mb-2">Web Worker Support</h3>
			{supported ? (
				<div className="text-green-700">
					✅ Web Workers are supported in this browser
				</div>
			) : (
				<div className="text-red-700">
					❌ Web Workers are not supported. Some features may be unavailable or
					slower.
				</div>
			)}
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
