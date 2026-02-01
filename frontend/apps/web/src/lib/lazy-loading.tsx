import { type ComponentType, lazy, type ReactNode, Suspense } from "react";

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
 * Standardized loading skeleton for list/table views.
 * Use in place of ad-hoc Skeleton grids for consistent UX.
 */
export function ListLoadingSkeleton({
	message = "Loading...",
	rowCount = 6,
	className,
	dataTestId,
}: {
	message?: string;
	rowCount?: number;
	className?: string;
	dataTestId?: string;
}) {
	return (
		<div
			className={className ?? "p-6 space-y-8 animate-pulse"}
			role="status"
			aria-live="polite"
			aria-atomic="true"
			data-testid={dataTestId}
		>
			<p className="text-xs text-muted-foreground">{message}</p>
			<div className="flex items-center gap-2">
				<div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
				<div className="h-10 w-48 rounded-md bg-muted" />
			</div>
			<div className="space-y-4">
				{Array.from({ length: rowCount }, (_, i) => (
					<div
						key={i}
						className="h-16 w-full rounded-xl bg-muted"
						aria-hidden
					/>
				))}
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
 * Unified error fallback for list rows (e.g. table row, list item).
 * Use when a single row/item fails to load or fails an action.
 */
export function ListItemErrorFallback({
	message = "Failed to load",
	detail,
	retry,
	className,
}: {
	message?: string;
	detail?: string;
	retry?: () => void;
	className?: string;
}) {
	return (
		<div
			className={
				className ??
				"flex items-center gap-3 p-3 rounded-lg border border-destructive/20 bg-destructive/5 text-destructive"
			}
			role="alert"
		>
			<span className="text-sm font-medium shrink-0">{message}</span>
			{detail && (
				<span className="text-xs text-muted-foreground truncate flex-1 min-w-0">
					{detail}
				</span>
			)}
			{retry && (
				<button
					type="button"
					onClick={retry}
					className="text-xs px-2 py-1 bg-primary text-primary-foreground rounded hover:bg-primary/90 shrink-0"
				>
					Retry
				</button>
			)}
		</div>
	);
}

/**
 * Unified error fallback for cards (e.g. search result card, detail card, view-level error).
 * Use when a card or view fails to load or shows an error state.
 */
export function CardErrorFallback({
	title = "Something went wrong",
	message,
	error,
	retry,
	className,
}: {
	title?: string;
	message?: string;
	error?: Error | null;
	retry?: () => void;
	className?: string;
}) {
	const displayMessage =
		message ?? (error?.message || "An unexpected error occurred. Please try again.");
	return (
		<div
			className={
				className ??
				"flex flex-col items-center justify-center text-center p-6 rounded-lg border border-destructive/20 bg-destructive/5"
			}
			role="alert"
		>
			<p className="text-sm font-semibold text-destructive">{title}</p>
			<p className="text-xs text-muted-foreground mt-1 max-w-sm">{displayMessage}</p>
			{retry && (
				<button
					type="button"
					onClick={retry}
					className="mt-4 text-xs px-3 py-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/90"
				>
					Try again
				</button>
			)}
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
