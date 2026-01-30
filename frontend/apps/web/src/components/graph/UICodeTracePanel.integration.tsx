/**
 * UICodeTracePanel Integration Examples
 * Demonstrates how to integrate the UICodeTracePanel component with your application
 */

import { useCallback, useState } from "react";
import type { CodeReference } from "@tracertm/types";
import { UICodeTracePanel, type UICodeTraceChain } from "./UICodeTracePanel";

// =============================================================================
// EXAMPLE 1: Basic Integration with State Management
// =============================================================================

/**
 * Basic example showing how to manage trace chain state
 * and handle user interactions
 */
export function BasicUICodeTracePanelExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
	const [isLoading, setIsLoading] = useState(false);

	// Simulate fetching trace chain from API
	const handleFetchTraceChain = useCallback(async (componentId: string) => {
		setIsLoading(true);
		try {
			// In real app, call your tRPC endpoint
			// const trace = await trpc.traces.getUICodeTrace.query({ componentId });
			// setTraceChain(trace);

			// Mock delay
			await new Promise((resolve) => setTimeout(resolve, 1000));
			// Mock data would be set here
		} finally {
			setIsLoading(false);
		}
	}, []);

	const handleOpenCode = useCallback((codeRef: CodeReference) => {
		// Option 1: VS Code Extension
		if (codeRef.filePath) {
			const lineParam = codeRef.startLine ? `:${codeRef.startLine}` : "";
			window.open(`vscode://open?${codeRef.filePath}${lineParam}`);
		}
	}, []);

	const handleOpenRequirement = useCallback((requirementId: string) => {
		// Navigate to requirement detail page
		window.location.href = `/items/${requirementId}`;
	}, []);

	const handleNavigateToUI = useCallback((componentPath: string) => {
		// Navigate to component file or preview
		window.location.href = `/components/${componentPath}`;
	}, []);

	const handleRefreshTrace = useCallback(async () => {
		if (traceChain) {
			setIsLoading(true);
			try {
				// Refetch the trace chain
				// const fresh = await trpc.traces.getUICodeTrace.query({
				//   componentId: traceChain.id
				// });
				// setTraceChain(fresh);
			} finally {
				setIsLoading(false);
			}
		}
	}, [traceChain]);

	return (
		<UICodeTracePanel
			traceChain={traceChain}
			isLoading={isLoading}
			onOpenCode={handleOpenCode}
			onOpenRequirement={handleOpenRequirement}
			onNavigateToUI={handleNavigateToUI}
			onRefreshTrace={handleRefreshTrace}
		/>
	);
}

// =============================================================================
// EXAMPLE 2: Integration with tRPC Query
// =============================================================================

/**
 * Example using tRPC with React Query for data fetching
 * Requires: trpc client and React Query setup
 */
export function TRPCIntegrationExample() {
	const [selectedComponentId, setSelectedComponentId] = useState<string | null>(
		null,
	);

	// Example tRPC query (you need to set this up in your router)
	// const { data: traceChain, isLoading, refetch } = trpc.traces.getUICodeTrace.useQuery(
	//   { componentId: selectedComponentId! },
	//   { enabled: !!selectedComponentId }
	// );

	// For now, using mock data
	const traceChain: UICodeTraceChain | null = null;
	const isLoading = false;

	const handleOpenCode = useCallback((codeRef: CodeReference) => {
		// Open code in editor
		console.log("Open code:", codeRef);
	}, []);

	const handleRefresh = useCallback(async () => {
		// refetch(); // If using tRPC
	}, []);

	return (
		<div className="space-y-4">
			{/* Component selector */}
			<div>
				<label className="block text-sm font-medium mb-2">
					Select Component:
				</label>
				<input
					type="text"
					placeholder="Enter component ID"
					value={selectedComponentId || ""}
					onChange={(e) => setSelectedComponentId(e.target.value)}
					className="border rounded px-3 py-2 w-full"
				/>
			</div>

			{/* Trace panel */}
			<UICodeTracePanel
				traceChain={traceChain}
				isLoading={isLoading}
				onOpenCode={handleOpenCode}
				onRefreshTrace={handleRefresh}
			/>
		</div>
	);
}

// =============================================================================
// EXAMPLE 3: Integration with Atoms/State Atom
// =============================================================================

/**
 * Example using Jotai atoms for state management
 * Requires: jotai setup
 */
export function AtomStateIntegrationExample() {
	// In real app:
	// const [selectedTrace, setSelectedTrace] = useAtom(selectedTraceAtom);
	// const [traceHistory, setTraceHistory] = useAtom(traceHistoryAtom);

	// Mock state
	const [selectedTrace, setSelectedTrace] = useState<UICodeTraceChain | null>(
		null,
	);
	const [isRefreshing, setIsRefreshing] = useState(false);

	const handleRefreshTrace = useCallback(async () => {
		setIsRefreshing(true);
		try {
			// Fetch fresh trace data
			// const fresh = await api.traces.getUICodeTrace(selectedTrace?.id);
			// setSelectedTrace(fresh);
		} finally {
			setIsRefreshing(false);
		}
	}, [selectedTrace]);

	return (
		<UICodeTracePanel
			traceChain={selectedTrace}
			isLoading={isRefreshing}
			onRefreshTrace={handleRefreshTrace}
		/>
	);
}

// =============================================================================
// EXAMPLE 4: Integration with Side Panel Layout
// =============================================================================

/**
 * Example showing UICodeTracePanel in a side panel layout
 * Common pattern for detailed views
 */
export function SidePanelLayoutExample() {
	const [selectedItemId, setSelectedItemId] = useState<string | null>(null);
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
	const [isLoading, setIsLoading] = useState(false);

	const handleSelectItem = useCallback(async (itemId: string) => {
		setSelectedItemId(itemId);
		setIsLoading(true);
		try {
			// Fetch trace chain for selected item
			// const trace = await api.traces.getUICodeTrace({ componentId: itemId });
			// setTraceChain(trace);
		} finally {
			setIsLoading(false);
		}
	}, []);

	return (
		<div className="flex h-screen gap-4">
			{/* Main content area */}
			<div className="flex-1 border-r p-4 overflow-auto">
				<h2 className="text-lg font-semibold mb-4">Components</h2>
				{/* List of components */}
				<div className="space-y-2">
					{["LoginForm", "NavBar", "Dashboard"].map((name) => (
						<button
							key={name}
							onClick={() => handleSelectItem(name)}
							className={`block w-full text-left px-4 py-2 rounded ${
								selectedItemId === name
									? "bg-blue-100 text-blue-900"
									: "hover:bg-gray-100"
							}`}
						>
							{name}
						</button>
					))}
				</div>
			</div>

			{/* Side panel with trace */}
			<div className="w-96 border-l p-4 overflow-auto bg-gray-50">
				<UICodeTracePanel
					traceChain={traceChain}
					isLoading={isLoading}
					onOpenCode={(codeRef) => {
						console.log("Open code:", codeRef);
					}}
					onRefreshTrace={async () => {
						if (traceChain) {
							setIsLoading(true);
							try {
								// Refetch trace
							} finally {
								setIsLoading(false);
							}
						}
					}}
				/>
			</div>
		</div>
	);
}

// =============================================================================
// EXAMPLE 5: Integration with Modal Dialog
// =============================================================================

/**
 * Example showing UICodeTracePanel in a modal dialog
 * Good for detailed trace inspection
 */
export function ModalDialogExample() {
	const [isOpen, setIsOpen] = useState(false);
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);

	const handleOpenTraceModal = useCallback(async (componentId: string) => {
		// Fetch trace data
		// const trace = await api.traces.getUICodeTrace({ componentId });
		// setTraceChain(trace);
		setIsOpen(true);
	}, []);

	return (
		<div>
			{/* Open modal button */}
			<button
				onClick={() => handleOpenTraceModal("component-1")}
				className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
			>
				View Trace
			</button>

			{/* Modal dialog */}
			{isOpen && (
				<div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
					<div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
						{/* Modal header */}
						<div className="flex items-center justify-between p-4 border-b">
							<h2 className="text-lg font-semibold">Traceability Chain</h2>
							<button
								onClick={() => setIsOpen(false)}
								className="text-gray-500 hover:text-gray-700"
							>
								✕
							</button>
						</div>

						{/* Modal content */}
						<div className="flex-1 overflow-auto p-4">
							<UICodeTracePanel
								traceChain={traceChain}
								onOpenCode={(codeRef) => {
									window.open(
										`vscode://open?${codeRef.filePath}:${codeRef.startLine}`,
									);
								}}
							/>
						</div>

						{/* Modal footer */}
						<div className="flex justify-end gap-2 p-4 border-t">
							<button
								onClick={() => setIsOpen(false)}
								className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
							>
								Close
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

// =============================================================================
// EXAMPLE 6: Integration with Error Handling
// =============================================================================

/**
 * Example showing how to handle errors when fetching trace data
 */
export function ErrorHandlingExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleFetchTrace = useCallback(async (componentId: string) => {
		setIsLoading(true);
		setError(null);
		try {
			// const trace = await api.traces.getUICodeTrace({ componentId });
			// setTraceChain(trace);
		} catch (err) {
			const message =
				err instanceof Error ? err.message : "Failed to fetch trace chain";
			setError(message);
			setTraceChain(null);
		} finally {
			setIsLoading(false);
		}
	}, []);

	return (
		<div className="space-y-4">
			{/* Error message */}
			{error && (
				<div className="p-4 bg-red-50 border border-red-200 rounded text-red-800">
					<p className="font-semibold">Error</p>
					<p className="text-sm mt-1">{error}</p>
					<button
						onClick={() => handleFetchTrace("component-1")}
						className="mt-2 text-sm text-red-700 hover:text-red-900 underline"
					>
						Try again
					</button>
				</div>
			)}

			{/* Trace panel */}
			<UICodeTracePanel traceChain={traceChain} isLoading={isLoading} />
		</div>
	);
}

// =============================================================================
// EXAMPLE 7: Integration with URL Search Params
// =============================================================================

/**
 * Example showing integration with URL query parameters
 * Good for bookmarkable trace chains
 */
export function URLSearchParamsExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
	const [isLoading, setIsLoading] = useState(false);

	// Get componentId from URL
	const searchParams = new URLSearchParams(window.location.search);
	const componentId = searchParams.get("component");

	// Fetch trace when component changes
	const fetchTrace = useCallback(async () => {
		if (!componentId) return;

		setIsLoading(true);
		try {
			// const trace = await api.traces.getUICodeTrace({ componentId });
			// setTraceChain(trace);
		} finally {
			setIsLoading(false);
		}
	}, [componentId]);

	// Effect to fetch when component ID changes
	React.useEffect(() => {
		fetchTrace();
	}, [fetchTrace]);

	return (
		<UICodeTracePanel
			traceChain={traceChain}
			isLoading={isLoading}
			onRefreshTrace={fetchTrace}
		/>
	);
}

// =============================================================================
// EXAMPLE 8: Integration with Breadcrumb Navigation
// =============================================================================

/**
 * Example showing UICodeTracePanel with breadcrumb navigation
 * Helps users understand context in the trace hierarchy
 */
export function BreadcrumbNavigationExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);
	const [selectedLevelIndex, setSelectedLevelIndex] = useState(0);

	const selectedLevel = traceChain?.levels[selectedLevelIndex];

	return (
		<div className="space-y-4">
			{/* Breadcrumb navigation */}
			{traceChain && (
				<div className="flex items-center gap-2 text-sm text-gray-600">
					{traceChain.levels.map((level, index) => (
						<React.Fragment key={level.id}>
							<button
								onClick={() => setSelectedLevelIndex(index)}
								className={`px-2 py-1 rounded ${
									index === selectedLevelIndex
										? "bg-blue-100 text-blue-900"
										: "hover:bg-gray-100"
								}`}
							>
								{level.title}
							</button>
							{index < traceChain.levels.length - 1 && <span>→</span>}
						</React.Fragment>
					))}
				</div>
			)}

			{/* Trace panel */}
			<UICodeTracePanel
				traceChain={traceChain}
				onOpenCode={(codeRef) => {
					console.log("Open code:", codeRef);
				}}
			/>

			{/* Selected level details */}
			{selectedLevel && (
				<div className="p-4 bg-blue-50 border border-blue-200 rounded">
					<h3 className="font-semibold text-blue-900">{selectedLevel.title}</h3>
					<p className="text-sm text-blue-800 mt-2">
						{selectedLevel.description}
					</p>
				</div>
			)}
		</div>
	);
}

// =============================================================================
// EXAMPLE 9: Integration with Analytics/Telemetry
// =============================================================================

/**
 * Example showing how to track user interactions for analytics
 */
export function AnalyticsIntegrationExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);

	const trackEvent = (eventName: string, data: Record<string, unknown>) => {
		// Send to analytics service
		console.log("Analytics:", eventName, data);
		// In real app: analytics.track(eventName, data);
	};

	const handleOpenCode = (codeRef: CodeReference) => {
		trackEvent("trace:open_code", {
			filePath: codeRef.filePath,
			symbol: codeRef.symbolName,
		});
	};

	const handleOpenRequirement = (requirementId: string) => {
		trackEvent("trace:open_requirement", {
			requirementId,
		});
	};

	return (
		<UICodeTracePanel
			traceChain={traceChain}
			onOpenCode={handleOpenCode}
			onOpenRequirement={handleOpenRequirement}
			onRefreshTrace={() => {
				trackEvent("trace:refresh", {
					traceId: traceChain?.id,
				});
			}}
		/>
	);
}

// =============================================================================
// EXAMPLE 10: Integration with Export/Share
// =============================================================================

/**
 * Example showing how to export trace chain as JSON or PDF
 */
export function ExportShareExample() {
	const [traceChain, setTraceChain] = useState<UICodeTraceChain | null>(null);

	const handleExportJSON = () => {
		if (!traceChain) return;

		const json = JSON.stringify(traceChain, null, 2);
		const blob = new Blob([json], { type: "application/json" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `trace-${traceChain.id}.json`;
		a.click();
	};

	const handleCopyShareLink = () => {
		if (!traceChain) return;

		const url = `${window.location.origin}?trace=${traceChain.id}`;
		navigator.clipboard.writeText(url);
		alert("Trace link copied to clipboard!");
	};

	return (
		<div className="space-y-4">
			<UICodeTracePanel traceChain={traceChain} />

			{/* Export controls */}
			{traceChain && (
				<div className="flex gap-2">
					<button
						onClick={handleExportJSON}
						className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
					>
						Export JSON
					</button>
					<button
						onClick={handleCopyShareLink}
						className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
					>
						Copy Share Link
					</button>
				</div>
			)}
		</div>
	);
}
