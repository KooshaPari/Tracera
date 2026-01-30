import { lazy, Suspense, type ComponentType, type ReactNode } from "react";

/**
 * Loading skeleton component for lazy-loaded components
 * Shows a minimal loading state while chunks are downloading
 */
export function ChunkLoadingSkeleton({
	message = "Loading...",
}: {
	message?: string;
}) {
	return (
		<div className="flex items-center justify-center min-h-96 bg-muted/50">
			<div className="flex flex-col items-center gap-4">
				<div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent" />
				<p className="text-sm text-muted-foreground">{message}</p>
			</div>
		</div>
	);
}

/**
 * Error fallback component for failed lazy loads
 */
export function ChunkErrorFallback({
	error,
	retry,
}: {
	error: Error;
	retry: () => void;
}) {
	return (
		<div className="flex items-center justify-center min-h-96 bg-destructive/5 border border-destructive/20 rounded-lg p-4">
			<div className="flex flex-col items-center gap-4 text-center">
				<div className="text-sm text-destructive font-semibold">
					Failed to load this component
				</div>
				<p className="text-xs text-muted-foreground max-w-sm">
					{error.message ||
						"An unexpected error occurred while loading this feature."}
				</p>
				<button
					onClick={retry}
					className="text-xs px-3 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90"
				>
					Try again
				</button>
			</div>
		</div>
	);
}

/**
 * Wraps a lazy component with Suspense boundary and error handling
 * Usage: useLazyComponent(() => import('./HeavyComponent'))
 */
export function useLazyComponent<P extends Record<string, any>>(
	importFn: () => Promise<{ default: ComponentType<P> }>,
	fallback?: ReactNode,
) {
	const Component = lazy(importFn);

	return (props: P) => (
		<Suspense fallback={fallback || <ChunkLoadingSkeleton />}>
			<Component {...props} />
		</Suspense>
	);
}

/**
 * Object of lazy-loaded heavy components
 * These are loaded on-demand when needed
 */
export const LazyComponents = {
	// Graph visualization components
	FlowGraphView: lazy(() =>
		import("@/components/graph/FlowGraphView").then((m) => ({
			default: m.FlowGraphView,
		})),
	),
	EnhancedGraphView: lazy(() =>
		import("@/components/graph/EnhancedGraphView").then((m) => ({
			default: m.EnhancedGraphView,
		})),
	),
	UnifiedGraphView: lazy(() =>
		import("@/components/graph/UnifiedGraphView").then((m) => ({
			default: m.UnifiedGraphView,
		})),
	),

	// Code editor
	MonacoEditor: lazy(() => import("@monaco-editor/react")),

	// API documentation
	SwaggerUI: lazy(() => import("swagger-ui-react")),
	ReDoc: lazy(() => import("redoc")),

	// Heavy views - loaded only when user navigates to them
	ReportsView: lazy(() =>
		import("@/views/ReportsView").then((m) => ({
			default: m.ReportsView,
		})),
	),
	SearchView: lazy(() =>
		import("@/views/SearchView").then((m) => ({
			default: m.SearchView,
		})),
	),
};

/**
 * Suspense boundary wrapper for lazy components with consistent styling
 */
export function LazyComponentBoundary({
	children,
	fallback,
	errorFallback,
}: {
	children: ReactNode;
	fallback?: ReactNode;
	errorFallback?: (error: Error) => ReactNode;
}) {
	return (
		<Suspense
			fallback={fallback || <ChunkLoadingSkeleton message="Loading view..." />}
		>
			{children}
		</Suspense>
	);
}
