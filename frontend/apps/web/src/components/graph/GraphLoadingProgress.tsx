/* eslint-disable complexity, func-style, max-lines-per-function, no-magic-numbers, sort-imports */
/**
 * GraphLoadingProgress - UI component for streaming graph loading progress
 *
 * Features:
 * - Real-time progress visualization
 * - Stage-based progress tracking
 * - Estimated completion time
 * - Smooth animations
 * - Cancellable loading
 */

import type {
	ProgressInfo,
	StreamMetadata,
} from "../../lib/graph/IncrementalGraphBuilder";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Progress } from "../ui/progress";
import {
	CheckCircle2,
	Database,
	Loader2,
	Network,
	XCircle,
} from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";

const ELAPSED_TICK_MS = 100;
const MS_IN_SECOND = 1000;
const SECONDS_IN_MINUTE = 60;

export interface GraphLoadingProgressProps {
	progress?: ProgressInfo;
	metadata?: StreamMetadata;
	isLoading: boolean;
	onCancel?: () => void;
	className?: string;
}

type StageInfo = {
	icon: ReactNode;
	label: string;
};

const getStageInfo = (stage: string): StageInfo => {
	switch (stage) {
		case "nodes":
			return { icon: <Database className="h-3 w-3" />, label: "Loading Nodes" };
		case "edges":
			return { icon: <Network className="h-3 w-3" />, label: "Loading Edges" };
		case "complete":
			return { icon: <CheckCircle2 className="h-3 w-3" />, label: "Complete" };
		default:
			return {
				icon: <Loader2 className="h-3 w-3 animate-spin" />,
				label: "Loading",
			};
	}
};

const formatTime = (ms: number): string => {
	if (ms < MS_IN_SECOND) {
		return "<1s";
	}

	const seconds = Math.ceil(ms / MS_IN_SECOND);
	if (seconds < SECONDS_IN_MINUTE) {
		return `${seconds}s`;
	}

	const minutes = Math.floor(seconds / SECONDS_IN_MINUTE);
	const remainingSeconds = seconds % SECONDS_IN_MINUTE;
	if (remainingSeconds === 0) {
		return `${minutes}m`;
	}

	return `${minutes}m ${remainingSeconds}s`;
};

type ProgressHeaderProps = { isLoading: boolean };

const ProgressHeader = ({ isLoading }: ProgressHeaderProps) => (
	<CardHeader className="pb-3">
		<CardTitle className="flex items-center gap-2 text-sm font-medium">
			{isLoading ? (
				<>
					<Loader2 className="h-4 w-4 animate-spin text-primary" />
					Loading Graph
				</>
			) : (
				<>
					<CheckCircle2 className="h-4 w-4 text-green-500" />
					Loaded
				</>
			)}
		</CardTitle>
	</CardHeader>
);

type ProgressStageProps = {
	percentage: number;
	stageInfo: StageInfo;
};

const ProgressStage = ({ percentage, stageInfo }: ProgressStageProps) => (
	<div className="space-y-1">
		<div className="flex justify-between text-xs text-muted-foreground">
			<span className="flex items-center gap-1">
				{stageInfo.icon}
				{stageInfo.label}
			</span>
			<span className="font-mono">{Math.round(percentage)}%</span>
		</div>
		<Progress value={percentage} className="h-2" />
	</div>
);

type ProgressStatsProps = {
	progress?: ProgressInfo;
	estimatedTime: number;
	remainingTime: number;
};

const ProgressStats = ({
	progress,
	estimatedTime,
	remainingTime,
}: ProgressStatsProps) => {
	if (!progress) {
		return null;
	}

	return (
		<div className="grid grid-cols-2 gap-2 text-xs">
			<div className="flex items-center gap-1.5 text-muted-foreground">
				<Database className="h-3.5 w-3.5" />
				<span>
					{progress.current.toLocaleString()} /{" "}
					{progress.total.toLocaleString()}
				</span>
			</div>

			{estimatedTime > 0 && (
				<div className="flex items-center gap-1.5 text-muted-foreground">
					<Network className="h-3.5 w-3.5" />
					<span>{formatTime(remainingTime)} remaining</span>
				</div>
			)}
		</div>
	);
};

type MetadataSectionProps = { metadata?: StreamMetadata };

const MetadataSection = ({ metadata }: MetadataSectionProps) => {
	if (!metadata) {
		return null;
	}

	return (
		<div className="pt-2 border-t text-xs text-muted-foreground space-y-1">
			<div className="flex justify-between">
				<span>Total Nodes:</span>
				<span className="font-mono">
					{metadata.totalNodes.toLocaleString()}
				</span>
			</div>
			<div className="flex justify-between">
				<span>Total Edges:</span>
				<span className="font-mono">
					{metadata.totalEdges.toLocaleString()}
				</span>
			</div>
			<div className="flex justify-between">
				<span>Chunk Size:</span>
				<span className="font-mono">{metadata.chunkSize}</span>
			</div>
		</div>
	);
};

type CancelButtonProps = { isLoading: boolean; onCancel?: () => void };

const CancelButton = ({ isLoading, onCancel }: CancelButtonProps) => {
	if (!isLoading || !onCancel) {
		return null;
	}

	return (
		<Button
			variant="outline"
			size="sm"
			className="w-full"
			onClick={onCancel}
		>
			<XCircle className="h-3.5 w-3.5 mr-1.5" />
			Cancel Loading
		</Button>
	);
};

const LoadingDots = ({ isLoading }: { isLoading: boolean }) => {
	if (!isLoading) {
		return null;
	}

	return (
		<div className="flex items-center justify-center gap-1 pt-2">
			<div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:0ms]" />
			<div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:150ms]" />
			<div className="h-1 w-1 rounded-full bg-primary animate-pulse [animation-delay:300ms]" />
		</div>
	);
};

const GraphLoadingProgress = ({
	progress,
	metadata,
	isLoading,
	onCancel,
	className = "",
}: GraphLoadingProgressProps) => {
	const [elapsedTime, setElapsedTime] = useState(0);
	const [startTime] = useState(Date.now());

	useEffect(() => {
		if (!isLoading) {
			setElapsedTime(0);
			return;
		}

		const interval = setInterval(() => {
			setElapsedTime(Date.now() - startTime);
		}, ELAPSED_TICK_MS);

		return () => clearInterval(interval);
	}, [isLoading, startTime]);

	if (!isLoading && !progress) {
		return null;
	}

	const percentage = progress?.percentage ?? 0;
	const stage = progress?.stage ?? "nodes";
	const estimatedTime = metadata?.estimatedTime ?? 0;
	const remainingTime = Math.max(0, estimatedTime - elapsedTime);
	const stageInfo = getStageInfo(stage);

	return (
		<Card className={`${className} border-primary/20`}>
			<ProgressHeader isLoading={isLoading} />
			<CardContent className="space-y-3">
				<ProgressStage percentage={percentage} stageInfo={stageInfo} />
				<ProgressStats
					progress={progress}
					estimatedTime={estimatedTime}
					remainingTime={remainingTime}
				/>
				<MetadataSection metadata={metadata} />
				<CancelButton isLoading={isLoading} onCancel={onCancel} />
				<LoadingDots isLoading={isLoading} />
			</CardContent>
		</Card>
	);
};

type CompactProps = GraphLoadingProgressProps;

const GraphLoadingProgressCompact = ({
	progress,
	isLoading,
	onCancel,
	className = "",
}: CompactProps) => {
	if (!isLoading && !progress) {
		return null;
	}

	const percentage = progress?.percentage ?? 0;
	const stage = progress?.stage ?? "nodes";
	const stageInfo = getStageInfo(stage);

	return (
		<div
			className={`${className} flex items-center gap-3 rounded-lg border bg-card p-3 text-sm shadow-sm`}
		>
			{isLoading ? (
				<Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
			) : (
				<CheckCircle2 className="h-4 w-4 text-green-500 flex-shrink-0" />
			)}

			<div className="flex-1 min-w-0">
				<div className="flex items-center gap-2 mb-1">
					<span className="text-xs text-muted-foreground flex items-center gap-1">
						{stageInfo.icon}
						{stageInfo.label}
					</span>
					<span className="text-xs font-mono text-muted-foreground ml-auto">
						{Math.round(percentage)}%
					</span>
				</div>
				<Progress value={percentage} className="h-1.5" />
			</div>

			{isLoading && onCancel && (
				<Button
					variant="ghost"
					size="sm"
					className="h-8 w-8 p-0 flex-shrink-0"
					onClick={onCancel}
				>
					<XCircle className="h-4 w-4" />
				</Button>
			)}
		</div>
	);
};

type InlineProps = Pick<GraphLoadingProgressProps, "progress" | "isLoading">;

const GraphLoadingProgressInline = ({ progress, isLoading }: InlineProps) => {
	if (!isLoading && !progress) {
		return null;
	}

	const percentage = progress?.percentage ?? 0;

	return (
		<div className="space-y-1">
			<Progress value={percentage} className="h-1" />
			<div className="flex justify-between text-xs text-muted-foreground">
				<span>Loading graph...</span>
				<span className="font-mono">{Math.round(percentage)}%</span>
			</div>
		</div>
	);
};

type LoadingEstimate = {
	total: number;
	remaining: number;
	speed: number;
} | null;

const useLoadingEstimate = (
	metadata?: StreamMetadata,
	progress?: ProgressInfo,
): LoadingEstimate => {
	const [estimate, setEstimate] = useState<LoadingEstimate>(null);
	const [startTime] = useState(Date.now());

	useEffect(() => {
		if (!metadata || !progress || progress.current === 0) {
			setEstimate(null);
			return;
		}

		const elapsed = Date.now() - startTime;
		const speed = progress.current / (elapsed / MS_IN_SECOND);
		const remaining = progress.total - progress.current;
		const remainingTime = (remaining / speed) * MS_IN_SECOND;

		setEstimate({
			remaining: remainingTime,
			speed,
			total: metadata.estimatedTime,
		});
	}, [metadata, progress, startTime]);

	return estimate;
};

export {
	GraphLoadingProgress,
	GraphLoadingProgressCompact,
	GraphLoadingProgressInline,
	useLoadingEstimate,
};
