import {
	Alert,
	AlertDescription,
	AlertTitle,
} from "@tracertm/ui/components/Alert";
import { Button } from "@tracertm/ui/components/Button";
import { AlertCircle } from "lucide-react";
import React from "react";
import type { ReactNode } from "react";

interface ErrorBoundaryProps {
	children: ReactNode;
	fallback?: (error: Error, reset: () => void) => ReactNode;
}

interface ErrorBoundaryState {
	hasError: boolean;
	error: Error | null;
}

export class ErrorBoundary extends React.Component<
	ErrorBoundaryProps,
	ErrorBoundaryState
> {
	constructor(props: ErrorBoundaryProps) {
		super(props);
		this.state = { hasError: false, error: null };
	}

	static getDerivedStateFromError(error: Error): ErrorBoundaryState {
		return { hasError: true, error };
	}

	override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
		console.error("Error caught by boundary:", error, errorInfo);
	}

	reset = () => {
		this.setState({ hasError: false, error: null });
	};

	override render() {
		if (this.state.hasError && this.state.error) {
			if (this.props.fallback) {
				return this.props.fallback(this.state.error, this.reset);
			}

			return (
				<Alert variant="destructive" className="m-4">
					<AlertCircle className="h-4 w-4" />
					<AlertTitle>Something went wrong</AlertTitle>
					<AlertDescription className="mt-2">
						<p className="mb-4">{this.state.error.message}</p>
						<Button variant="outline" size="sm" onClick={this.reset}>
							Try again
						</Button>
					</AlertDescription>
				</Alert>
			);
		}

		return this.props.children;
	}
}
