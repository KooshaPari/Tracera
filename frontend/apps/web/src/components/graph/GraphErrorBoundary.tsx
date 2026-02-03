import React, { Component } from "react";
import type { ReactNode } from "react";
import { logger } from "@/lib/logger";
import { EnhancedErrorState } from "./EnhancedErrorState";

interface Props {
	children: ReactNode;
	fallback?: (error: Error, reset: () => void) => ReactNode;
	onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
	hasError: boolean;
	error: Error | null;
}

export class GraphErrorBoundary extends Component<Props, State> {
	constructor(props: Props) {
		super(props);
		this.state = { error: null, hasError: false };
	}

	static override getDerivedStateFromError(error: Error): State {
		return { error, hasError: true };
	}

	override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		logger.error("Graph error boundary caught:", error, errorInfo);
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
				<div className="flex items-center justify-center h-full p-4">
					<EnhancedErrorState error={this.state.error} onRetry={this.reset} />
				</div>
			);
		}

		return this.props.children;
	}
}
