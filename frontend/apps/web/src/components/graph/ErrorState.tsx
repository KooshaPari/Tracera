import { memo } from "react";
import { Button } from "@tracertm/ui/components/Button";
import { AlertCircle, RefreshCcw } from "lucide-react";

interface ErrorStateProps {
	title?: string;
	message?: string;
	onRetry?: () => void;
}

export const ErrorState = memo(function ErrorState({
	title = "Failed to load graph",
	message = "An error occurred while loading the graph data.",
	onRetry,
}: ErrorStateProps) {
	return (
		<div className="flex flex-col items-center justify-center h-full space-y-4 p-8">
			<AlertCircle className="w-12 h-12 text-destructive" />
			<div className="text-center space-y-2">
				<h3 className="text-lg font-semibold">{title}</h3>
				<p className="text-sm text-muted-foreground max-w-md">{message}</p>
			</div>
			{onRetry && (
				<Button onClick={onRetry} variant="outline" className="gap-2">
					<RefreshCcw className="w-4 h-4" />
					Retry
				</Button>
			)}
		</div>
	);
});
