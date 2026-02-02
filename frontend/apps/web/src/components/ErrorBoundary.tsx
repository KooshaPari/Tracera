import {
	Alert,
	AlertDescription,
	AlertTitle,
} from "@tracertm/ui/components/Alert";
import { logger } from '@/lib/logger';
import { Button } from "@tracertm/ui/components/Button";
import { AlertCircle, Bug, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";
import React from "react";

// Sentry integration
import { captureException as sentryCaptureException } from "@/lib/sentry";

interface ErrorBoundaryProps {
	children: ReactNode;
	fallback?: (error: Error, reset: () => void) => ReactNode;
	/**
	 * Name to identify this error boundary in logs/Sentry
	 * @example "GraphView", "FormDialog", "RouteComponent"
	 */
	name?: string;
	/**
	 * Show error details in production (default: false)
	 */
	showDetails?: boolean;
	/**
	 * Callback when error is caught
	 */
	onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
	hasError: boolean;
	error: Error | null;
	errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary Component
 *
 * Catches React errors in child components and displays a fallback UI.
 * Integrates with Sentry if available for error tracking.
 *
 * @example
 * ```tsx
 * <ErrorBoundary name="GraphView">
 *   <GraphViewContainer />
 * </ErrorBoundary>
 * ```
 *
 * @example Custom fallback
 * ```tsx
 * <ErrorBoundary
 *   name="FormDialog"
 *   fallback={(error, reset) => (
 *     <div>
 *       <p>Form error: {error.message}</p>
 *       <button onClick={reset}>Try again</button>
 *     </div>
 *   )}
 * >
 *   <CreateItemForm />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends React.Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { hasError: false, error: null, errorInfo: null };
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { hasError: true, error, errorInfo: null };
	}

	override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		const { name, onError } = this.props;

		// Log to console with boundary name
		logger.error(
			`Error caught by ${name || "ErrorBoundary"}:`,
			error,
			errorInfo
		);

		// Store error info in state for display
		this.setState({ errorInfo });

		// Report to Sentry
		try {
			sentryCaptureException(error, {
				react: {
					componentStack: errorInfo.componentStack,
					errorBoundary: name || "UnnamedBoundary",
				},
			});
		} catch (sentryError) {
			// Sentry might not be initialized, that's OK
			logger.warn("Failed to report error to Sentry:", sentryError);
		}

		// Call custom error handler if provided
		if (onError) {
			try {
				onError(error, errorInfo);
			} catch (callbackError) {
				logger.error("Error in onError callback:", callbackError);
			}
		}
	}

	reset = () => {
		this.setState({ hasError: false, error: null, errorInfo: null });
	};

	override render() {
		if (this.state.hasError && this.state.error) {
			if (this.props.fallback) {
				return this.props.fallback(this.state.error, this.reset);
			}

			const isDevelopment = import.meta.env.DEV;
			const showDetails = isDevelopment || this.props.showDetails;

			return (
				<Alert variant="destructive" className="m-4">
					<AlertCircle className="h-4 w-4" />
					<AlertTitle className="flex items-center gap-2">
						Something went wrong
						{this.props.name && (
							<span className="text-xs font-mono bg-destructive/10 px-2 py-1 rounded">
								{this.props.name}
							</span>
						)}
					</AlertTitle>
					<AlertDescription className="mt-2 space-y-3">
						<p className="text-sm">{this.state.error.message}</p>

						{showDetails && this.state.errorInfo?.componentStack && (
							<details className="text-xs">
								<summary className="cursor-pointer hover:text-destructive-foreground font-medium flex items-center gap-1">
									<Bug className="h-3 w-3" />
									Component Stack
								</summary>
								<pre className="mt-2 p-2 bg-muted/50 rounded overflow-x-auto max-h-32 text-xs">
									{this.state.errorInfo.componentStack}
								</pre>
							</details>
						)}

						{showDetails && this.state.error.stack && (
							<details className="text-xs">
								<summary className="cursor-pointer hover:text-destructive-foreground font-medium flex items-center gap-1">
									<Bug className="h-3 w-3" />
									Error Stack
								</summary>
								<pre className="mt-2 p-2 bg-muted/50 rounded overflow-x-auto max-h-32 text-xs">
									{this.state.error.stack}
								</pre>
							</details>
						)}

						<div className="flex gap-2 pt-2">
							<Button
								variant="outline"
								size="sm"
								onClick={this.reset}
								className="gap-1"
							>
								<RefreshCw className="h-3 w-3" />
								Try again
							</Button>

							<Button
								variant="ghost"
								size="sm"
								onClick={() => window.location.reload()}
								className="gap-1"
							>
								Reload page
							</Button>
						</div>
					</AlertDescription>
				</Alert>
			);
		}

		return this.props.children;
	}
}

/**
 * Higher-order component to wrap any component with an error boundary
 *
 * @example
 * ```tsx
 * const SafeGraphView = withErrorBoundary(GraphView, { name: "GraphView" });
 * ```
 */
export function withErrorBoundary<P extends object>(
	Component: React.ComponentType<P>,
	options?: Omit<ErrorBoundaryProps, "children">
) {
	const WrappedComponent = (props: P) => (
		<ErrorBoundary {...options}>
			<Component {...props} />
		</ErrorBoundary>
	);

	WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name || "Component"})`;

	return WrappedComponent;
}
