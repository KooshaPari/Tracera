/**
 * Streaming Progress Indicator Component
 * Displays progress for NDJSON streaming operations
 */

import _React from "react";
import type { StreamingStats } from "../lib/ndjson-parser";
import { calculateThroughput } from "../lib/ndjson-parser";

export interface StreamingProgressProps {
	stats: StreamingStats | null;
	isStreaming: boolean;
	showThroughput?: boolean;
	showBytes?: boolean;
	className?: string;
}

function formatBytes(bytes: number): string {
	if (bytes < 1024) {
		return `${bytes} B`;
	}
	if (bytes < 1024 * 1024) {
		return `${(bytes / 1024).toFixed(2)} KB`;
	}
	return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
}

function formatDuration(ms: number): string {
	if (ms < 1000) {
		return `${ms.toFixed(0)}ms`;
	}
	if (ms < 60_000) {
		return `${(ms / 1000).toFixed(1)}s`;
	}
	return `${(ms / 60_000).toFixed(1)}m`;
}

export function StreamingProgress({
	stats,
	isStreaming,
	showThroughput = true,
	showBytes = false,
	className = "",
}: StreamingProgressProps) {
	if (!stats && !isStreaming) {
		return null;
	}

	const throughput = stats ? calculateThroughput(stats) : null;

	return (
		<div className={`streaming-progress ${className}`}>
			<div className="flex items-center gap-4">
				{/* Spinner */}
				{isStreaming && (
					<div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent" />
				)}

				{/* Stats */}
				<div className="flex gap-6 text-sm">
					{/* Items received */}
					<div className="flex flex-col">
						<span className="text-muted-foreground">Items</span>
						<span className="font-mono font-semibold">
							{stats?.itemsReceived.toLocaleString() || 0}
						</span>
					</div>

					{/* Bytes received */}
					{showBytes && stats && (
						<div className="flex flex-col">
							<span className="text-muted-foreground">Data</span>
							<span className="font-mono font-semibold">
								{formatBytes(stats.bytesReceived)}
							</span>
						</div>
					)}

					{/* Throughput */}
					{showThroughput && throughput && (
						<div className="flex flex-col">
							<span className="text-muted-foreground">Speed</span>
							<span className="font-mono font-semibold">
								{throughput.itemsPerSecond.toFixed(0)} items/s
							</span>
						</div>
					)}

					{/* Duration */}
					{stats && (
						<div className="flex flex-col">
							<span className="text-muted-foreground">Duration</span>
							<span className="font-mono font-semibold">
								{formatDuration(
									(stats.endTime || Date.now()) - stats.startTime,
								)}
							</span>
						</div>
					)}

					{/* Errors */}
					{stats && stats.errors.length > 0 && (
						<div className="flex flex-col">
							<span className="text-destructive">Errors</span>
							<span className="font-mono font-semibold text-destructive">
								{stats.errors.length}
							</span>
						</div>
					)}
				</div>

				{/* Status text */}
				<div className="text-sm text-muted-foreground ml-auto">
					{isStreaming ? "Streaming..." : "Complete"}
				</div>
			</div>

			{/* Progress bar (indeterminate when streaming) */}
			{isStreaming && (
				<div className="w-full h-1 bg-muted rounded-full overflow-hidden mt-2">
					<div className="h-full bg-primary animate-pulse" />
				</div>
			)}

			{/* Error messages */}
			{stats && stats.errors.length > 0 && (
				<div className="mt-2 text-sm text-destructive">
					<details>
						<summary className="cursor-pointer">
							{stats.errors.length} error{stats.errors.length > 1 ? "s" : ""}{" "}
							occurred
						</summary>
						<ul className="list-disc list-inside mt-1 pl-4">
							{stats.errors.map((error, i) => (
								<li key={i}>{error}</li>
							))}
						</ul>
					</details>
				</div>
			)}
		</div>
	);
}

export interface CompactStreamingProgressProps {
	stats: StreamingStats | null;
	isStreaming: boolean;
}

export function CompactStreamingProgress({
	stats,
	isStreaming,
}: CompactStreamingProgressProps) {
	if (!stats && !isStreaming) {
		return null;
	}

	return (
		<div className="inline-flex items-center gap-2 text-sm text-muted-foreground">
			{isStreaming && (
				<div className="animate-spin rounded-full h-3 w-3 border-2 border-primary border-t-transparent" />
			)}
			<span className="font-mono">
				{stats?.itemsReceived.toLocaleString() || 0} items
			</span>
			{isStreaming && <span>streaming...</span>}
		</div>
	);
}

export interface StreamingProgressBarProps {
	current: number;
	total?: number;
	isStreaming: boolean;
	className?: string;
}

export function StreamingProgressBar({
	current,
	total,
	isStreaming,
	className = "",
}: StreamingProgressBarProps) {
	const percentage = total ? (current / total) * 100 : 0;
	const showPercentage = total && total > 0;

	return (
		<div className={`streaming-progress-bar ${className}`}>
			<div className="flex justify-between text-sm mb-1">
				<span className="text-muted-foreground">
					{current.toLocaleString()}
					{total ? ` / ${total.toLocaleString()}` : ""} items
				</span>
				{showPercentage && (
					<span className="font-mono font-semibold">
						{percentage.toFixed(1)}%
					</span>
				)}
			</div>
			<div className="w-full h-2 bg-muted rounded-full overflow-hidden">
				{showPercentage ? (
					<div
						className="h-full bg-primary transition-all duration-300"
						style={{ width: `${percentage}%` }}
					/>
				) : (
					isStreaming && <div className="h-full bg-primary animate-pulse" />
				)}
			</div>
		</div>
	);
}
