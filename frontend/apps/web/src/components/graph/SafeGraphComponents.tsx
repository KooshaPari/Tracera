/**
 * Safe Graph Components - Graph components wrapped with error boundaries
 *
 * This file provides error-boundary-wrapped versions of critical graph components
 * to prevent entire page crashes when a graph rendering error occurs.
 */

import { lazy, Suspense } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { Loader2 } from "lucide-react";

// Lazy load heavy graph components for better code splitting
const GraphViewContainer = lazy(() =>
	import("./GraphViewContainer").then((m) => ({
		default: m.GraphViewContainer,
	})),
);
const FlowGraphView = lazy(() =>
	import("./FlowGraphView").then((m) => ({ default: m.FlowGraphView })),
);
const EnhancedGraphView = lazy(() =>
	import("./EnhancedGraphView").then((m) => ({
		default: m.EnhancedGraphView,
	})),
);
const VirtualizedGraphView = lazy(() =>
	import("./VirtualizedGraphView").then((m) => ({
		default: m.VirtualizedGraphView,
	})),
);
const UnifiedGraphView = lazy(() =>
	import("./UnifiedGraphView").then((m) => ({
		default: m.UnifiedGraphView,
	})),
);

// Loading fallback for graph components
function GraphLoadingFallback() {
	return (
		<div className="flex items-center justify-center h-full min-h-[400px] bg-muted/5">
			<div className="flex flex-col items-center gap-4 text-muted-foreground">
				<Loader2 className="h-8 w-8 animate-spin" />
				<p className="text-sm">Loading graph...</p>
			</div>
		</div>
	);
}

// Error fallback for graph components
function GraphErrorFallback(error: Error, reset: () => void) {
	return (
		<div className="flex items-center justify-center h-full min-h-[400px] border-2 border-dashed border-destructive/50 rounded-lg bg-destructive/5 p-8">
			<div className="max-w-md text-center space-y-4">
				<h3 className="text-lg font-semibold text-destructive">
					Graph Rendering Error
				</h3>
				<p className="text-sm text-muted-foreground">
					{error.message || "Unable to render graph visualization"}
				</p>
				<button
					onClick={reset}
					className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Retry
				</button>
			</div>
		</div>
	);
}

/**
 * Safe wrapper for GraphViewContainer with error boundary and lazy loading
 */
export function SafeGraphViewContainer(props: React.ComponentProps<typeof GraphViewContainer>) {
	return (
		<ErrorBoundary name="GraphViewContainer" fallback={GraphErrorFallback}>
			<Suspense fallback={<GraphLoadingFallback />}>
				<GraphViewContainer {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for FlowGraphView with error boundary and lazy loading
 */
export function SafeFlowGraphView(props: React.ComponentProps<typeof FlowGraphView>) {
	return (
		<ErrorBoundary name="FlowGraphView" fallback={GraphErrorFallback}>
			<Suspense fallback={<GraphLoadingFallback />}>
				<FlowGraphView {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for EnhancedGraphView with error boundary and lazy loading
 */
export function SafeEnhancedGraphView(props: React.ComponentProps<typeof EnhancedGraphView>) {
	return (
		<ErrorBoundary name="EnhancedGraphView" fallback={GraphErrorFallback}>
			<Suspense fallback={<GraphLoadingFallback />}>
				<EnhancedGraphView {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for VirtualizedGraphView with error boundary and lazy loading
 */
export function SafeVirtualizedGraphView(props: React.ComponentProps<typeof VirtualizedGraphView>) {
	return (
		<ErrorBoundary name="VirtualizedGraphView" fallback={GraphErrorFallback}>
			<Suspense fallback={<GraphLoadingFallback />}>
				<VirtualizedGraphView {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}

/**
 * Safe wrapper for UnifiedGraphView with error boundary and lazy loading
 */
export function SafeUnifiedGraphView(props: React.ComponentProps<typeof UnifiedGraphView>) {
	return (
		<ErrorBoundary name="UnifiedGraphView" fallback={GraphErrorFallback}>
			<Suspense fallback={<GraphLoadingFallback />}>
				<UnifiedGraphView {...props} />
			</Suspense>
		</ErrorBoundary>
	);
}
