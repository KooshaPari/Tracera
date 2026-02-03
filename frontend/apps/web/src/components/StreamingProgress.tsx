/**
 * Streaming Progress Indicator Component
 * Displays progress for NDJSON streaming operations
 */

import type { StreamingStats } from "../lib/ndjson-parser";
import { calculateThroughput } from "../lib/ndjson-parser";

const BYTES_IN_KB = 1024;
const BYTES_IN_MB = BYTES_IN_KB * BYTES_IN_KB;
const DECIMAL_PLACES_BYTES = 2;
const DECIMAL_PLACES_MS = 0;
const DECIMAL_PLACES_SECONDS = 1;
const MS_PER_SECOND = 1000;
const MINUTES_PER_HOUR = 60;
const MS_PER_MINUTE = MINUTES_PER_HOUR * MS_PER_SECOND;
const PERCENTAGE_SCALE = 100;

export interface StreamingProgressProps {
	stats: StreamingStats | null;
	isStreaming: boolean;
	showThroughput?: boolean;
	showBytes?: boolean;
	className?: string;
}

const formatBytes = (bytes: number): string => {
	if (bytes < BYTES_IN_KB) {
		return `${bytes} B`;
	}
	if (bytes < BYTES_IN_MB) {
		return `${(bytes / BYTES_IN_KB).toFixed(DECIMAL_PLACES_BYTES)} KB`;
	}
	return `${(bytes / BYTES_IN_MB).toFixed(DECIMAL_PLACES_BYTES)} MB`;
};

const formatDuration = (ms: number): string => {
	if (ms < MS_PER_SECOND) {
		return `${ms.toFixed(DECIMAL_PLACES_MS)}ms`;
	}
	if (ms < MS_PER_MINUTE) {
		return `${(ms / MS_PER_SECOND).toFixed(DECIMAL_PLACES_SECONDS)}s`;
	}
	return `${(ms / MS_PER_MINUTE).toFixed(DECIMAL_PLACES_SECONDS)}m`;
};

const hasErrors = (stats: StreamingStats | null): boolean => {
	return stats !== null && stats.errors.length > 0;
};

const StatItem = ({
	label,
	value,
}: {
	label: string;
	value: string | number;
}) => (
	<div className="flex flex-col">
		<span className="text-muted-foreground">{label}</span>
		<span className="font-mono font-semibold">{value}</span>
	</div>
);

const ErrorStat = ({ count }: { count: number }) => (
	<div className="flex flex-col">
		<span className="text-destructive">Errors</span>
		<span className="font-mono font-semibold text-destructive">{count}</span>
	</div>
);

const ErrorDetails = ({ errors }: { errors: string[] }) => (
	<div className="mt-2 text-sm text-destructive">
		<details>
			<summary className="cursor-pointer">
				{errors.length} error{errors.length > 1 ? "s" : ""} occurred
			</summary>
			<ul className="list-disc list-inside mt-1 pl-4">
				{errors.map((error, idx) => (
					<li key={`${error}-${idx}`}>{error}</li>
				))}
			</ul>
		</details>
	</div>
);

const StatsRow = ({
	stats,
	showBytes,
	showThroughput,
	throughput,
}: {
	stats: StreamingStats | null;
	showBytes: boolean;
	showThroughput: boolean;
	throughput: ReturnType<typeof calculateThroughput> | null;
}) => (
	<div className="flex gap-6 text-sm">
		<StatItem label="Items" value={stats?.itemsReceived.toLocaleString() || 0} />

		{showBytes && stats && (
			<StatItem label="Data" value={formatBytes(stats.bytesReceived)} />
		)}

		{showThroughput && throughput && (
			<StatItem
				label="Speed"
				value={`${throughput.itemsPerSecond.toFixed(0)} items/s`}
			/>
		)}

		{stats && (
			<StatItem
				label="Duration"
				value={formatDuration((stats.endTime || Date.now()) - stats.startTime)}
			/>
		)}

		{hasErrors(stats) && <ErrorStat count={stats!.errors.length} />}
	</div>
);

const Spinner = () => (
	<div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent" />
);

const ProgressBar = () => (
	<div className="w-full h-1 bg-muted rounded-full overflow-hidden mt-2">
		<div className="h-full bg-primary animate-pulse" />
	</div>
);

const StatusText = ({ isStreaming }: { isStreaming: boolean }) => (
	<div className="text-sm text-muted-foreground ml-auto">
		{isStreaming ? "Streaming..." : "Complete"}
	</div>
);

export const StreamingProgress = ({
	stats,
	isStreaming,
	showThroughput = true,
	showBytes = false,
	className = "",
}: StreamingProgressProps) => {
	if (!stats && !isStreaming) {
		return null;
	}

	const throughput = stats ? calculateThroughput(stats) : null;
	const errorStats = hasErrors(stats) ? stats : null;

	return (
		<div className={`streaming-progress ${className}`}>
			<div className="flex items-center gap-4">
				{isStreaming && <Spinner />}
				<StatsRow
					stats={stats}
					showBytes={showBytes}
					showThroughput={showThroughput}
					throughput={throughput}
				/>
				<StatusText isStreaming={isStreaming} />
			</div>

			{isStreaming && <ProgressBar />}

			{errorStats && <ErrorDetails errors={errorStats.errors} />}
		</div>
	);
};

export interface CompactStreamingProgressProps {
	stats: StreamingStats | null;
	isStreaming: boolean;
}

export const CompactStreamingProgress = ({
	stats,
	isStreaming,
}: CompactStreamingProgressProps) => {
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
};

export interface StreamingProgressBarProps {
	current: number;
	total?: number;
	isStreaming: boolean;
	className?: string;
}

export const StreamingProgressBar = ({
	current,
	total,
	isStreaming,
	className = "",
}: StreamingProgressBarProps) => {
	const percentage = total ? (current / total) * PERCENTAGE_SCALE : 0;
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
						{percentage.toFixed(DECIMAL_PLACES_SECONDS)}%
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
};
