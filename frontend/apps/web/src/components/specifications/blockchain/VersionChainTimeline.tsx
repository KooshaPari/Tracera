/**
 * Version Chain Timeline Component
 * Displays the blockchain-style version history of a specification
 */

import { cn } from "@/lib/utils";

interface VersionChainEntry {
	version_hash: string;
	version_number: number;
	content_hash: string;
	previous_hash: string | null;
	created_at: string;
	created_by: string | null;
	change_summary: string | null;
}

interface VersionChainTimelineProps {
	chainHead: string;
	chainLength: number;
	entries: VersionChainEntry[];
	chainValid: boolean;
	brokenLinks?: string[];
	maxDisplay?: number;
	className?: string;
}

export function VersionChainTimeline({
	chainHead,
	chainLength,
	entries,
	chainValid,
	brokenLinks = [],
	maxDisplay = 10,
	className,
}: VersionChainTimelineProps) {
	const displayEntries = entries.slice(0, maxDisplay);
	const hasMore = entries.length > maxDisplay;

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-lg font-semibold flex items-center gap-2">
						<span>⛓</span>
						Version Chain
					</h3>
					<p className="text-sm text-muted-foreground">
						{chainLength} versions in chain
					</p>
				</div>
				<div className="flex items-center gap-2">
					{chainValid ? (
						<span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-md font-medium">
							✓ Chain Valid
						</span>
					) : (
						<span className="px-2 py-1 text-xs bg-red-100 text-red-700 rounded-md font-medium">
							✕ Chain Invalid
						</span>
					)}
				</div>
			</div>

			{/* Chain Head */}
			<div className="p-2 bg-muted rounded">
				<div className="text-xs text-muted-foreground mb-1">Chain Head</div>
				<code className="text-xs font-mono break-all">{chainHead}</code>
			</div>

			{/* Broken Links Warning */}
			{brokenLinks.length > 0 && (
				<div className="p-3 bg-red-50 border border-red-200 rounded-lg">
					<div className="flex items-center gap-2 text-red-700 font-medium mb-1">
						<span>⚠</span>
						<span>Broken Links Detected</span>
					</div>
					<ul className="text-sm text-red-600 space-y-1">
						{brokenLinks.map((link, idx) => (
							<li key={idx} className="font-mono text-xs">
								{link}
							</li>
						))}
					</ul>
				</div>
			)}

			{/* Timeline */}
			<div className="relative">
				{/* Vertical line */}
				<div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

				{/* Entries */}
				<div className="space-y-4">
					{displayEntries.map((entry, idx) => (
						<VersionChainEntry
							key={entry.version_hash}
							entry={entry}
							isHead={idx === 0}
							isLast={idx === displayEntries.length - 1 && !hasMore}
						/>
					))}

					{hasMore && (
						<div className="relative pl-10">
							<div className="absolute left-[14px] top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-muted-foreground" />
							<div className="text-sm text-muted-foreground">
								+{entries.length - maxDisplay} more versions...
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}

interface VersionChainEntryProps {
	entry: VersionChainEntry;
	isHead?: boolean;
	isLast?: boolean;
}

function VersionChainEntry({ entry, isHead }: VersionChainEntryProps) {
	const date = new Date(entry.created_at);
	const formattedDate = date.toLocaleDateString(undefined, {
		day: "numeric",
		month: "short",
		year: "numeric",
	});
	const formattedTime = date.toLocaleTimeString(undefined, {
		hour: "2-digit",
		minute: "2-digit",
	});

	return (
		<div className="relative pl-10">
			{/* Node */}
			<div
				className={cn(
					"absolute left-[10px] top-2 w-3 h-3 rounded-full border-2 bg-background",
					isHead ? "border-primary bg-primary" : "border-muted-foreground",
				)}
			/>

			{/* Content */}
			<div
				className={cn(
					"p-3 rounded-lg border",
					isHead ? "bg-primary/5 border-primary/20" : "bg-muted/50",
				)}
			>
				<div className="flex items-start justify-between gap-2 mb-2">
					<div className="flex items-center gap-2">
						<span className="font-semibold">v{entry.version_number}</span>
						{isHead && (
							<span className="px-1.5 py-0.5 text-xs bg-primary text-primary-foreground rounded">
								HEAD
							</span>
						)}
					</div>
					<div className="text-xs text-muted-foreground text-right">
						<div>{formattedDate}</div>
						<div>{formattedTime}</div>
					</div>
				</div>

				{entry.change_summary && (
					<p className="text-sm mb-2">{entry.change_summary}</p>
				)}

				{entry.created_by && (
					<div className="text-xs text-muted-foreground mb-2">
						by {entry.created_by}
					</div>
				)}

				<div className="grid grid-cols-2 gap-2 text-xs">
					<div>
						<span className="text-muted-foreground">Hash: </span>
						<code className="font-mono">
							{entry.version_hash.slice(0, 8)}...
						</code>
					</div>
					<div>
						<span className="text-muted-foreground">Content: </span>
						<code className="font-mono">
							{entry.content_hash.slice(0, 8)}...
						</code>
					</div>
				</div>

				{entry.previous_hash && (
					<div className="mt-2 pt-2 border-t text-xs">
						<span className="text-muted-foreground">Previous: </span>
						<code className="font-mono">
							{entry.previous_hash.slice(0, 8)}...
						</code>
					</div>
				)}
			</div>
		</div>
	);
}

interface VersionChainBadgeProps {
	chainLength: number;
	chainValid: boolean;
	className?: string;
}

export function VersionChainBadge({
	chainLength,
	chainValid,
	className,
}: VersionChainBadgeProps) {
	return (
		<div
			className={cn(
				"inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-sm font-medium",
				chainValid ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700",
				className,
			)}
		>
			<span>⛓</span>
			<span>{chainLength} versions</span>
			{chainValid ? (
				<span className="text-green-600">✓</span>
			) : (
				<span className="text-red-600">✕</span>
			)}
		</div>
	);
}
