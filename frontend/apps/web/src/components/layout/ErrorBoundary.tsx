import { Button } from "@tracertm/ui";
import { logger } from "@/lib/logger";
import { AlertTriangle, RefreshCcw, RotateCw } from "lucide-react";
import { Component } from "react";
import type { ReactNode } from "react";

interface ErrorBoundaryProps {
	children: ReactNode;
	fallback?: (error: Error, reset: () => void) => ReactNode;
	onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface ErrorBoundaryState {
	hasError: boolean;
	error: Error | null;
}

export class ErrorBoundary extends Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { error: null, hasError: false };
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { error, hasError: true };
	}

	override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		logger.error("ErrorBoundary caught error:", error, errorInfo);
		this.props.onError?.(error, errorInfo);
	}

	reset = () => {
		this.setState({ error: null, hasError: false });
	};

	override render() {
		if (this.state.hasError && this.state.error) {
			if (this.props.fallback) {
				return this.props.fallback(this.state.error, this.reset);
			}

			return (
				<div className="flex items-center justify-center p-6 animate-in fade-in zoom-in-95 duration-300">
					<div className="max-w-md w-full bg-card border border-destructive/20 rounded-2xl shadow-2xl p-8 space-y-6">
						<div className="flex flex-col items-center text-center space-y-4">
							<div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center text-destructive">
								<AlertTriangle className="w-8 h-8" />
							</div>

							<div className="space-y-1">
								<h2 className="text-xl font-bold tracking-tight">
									Component Failure
								</h2>
								<p className="text-sm text-muted-foreground">
									A sub-system encountered an unrecoverable state.
								</p>
							</div>
						</div>

						<div className="bg-muted/30 rounded-xl p-4 font-mono text-xs border border-border/50 max-h-40 overflow-auto">
							<p className="text-destructive font-bold mb-1">EXCEPTION:</p>
							<p className="text-muted-foreground break-all">
								{this.state.error.message || "An unexpected error occurred"}
							</p>
						</div>

						<div className="flex gap-3">
							<Button onClick={this.reset} className="flex-1 gap-2" size="sm">
								<RefreshCcw className="w-3.5 h-3.5" />
								Try Reset
							</Button>
							<Button
								onClick={() => globalThis.location.reload()}
								variant="outline"
								className="flex-1 gap-2"
								size="sm"
							>
								<RotateCw className="w-3.5 h-3.5" />
								Hard Reload
							</Button>
						</div>
					</div>
				</div>
			);
		}

		return this.props.children;
	}
}
