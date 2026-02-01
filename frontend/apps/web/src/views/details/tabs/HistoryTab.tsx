/**
 * HistoryTab - Displays audit trail and change history
 *
 * Shows:
 * - Creation timestamp and user
 * - Last update timestamp and user
 * - Version history
 * - Timeline of changes
 */

import type { TypedItem } from "@tracertm/types";
import { Badge, Card } from "@tracertm/ui";
import { CalendarClock, CircleDot, GitBranch, Timer } from "lucide-react";
import { useMemo } from "react";
import { cn } from "@/lib/utils";

export interface HistoryTabProps {
	/** The item to display history for */
	item: TypedItem;

	/** Optional CSS classes */
	className?: string;
}

interface TimelineEvent {
	label: string;
	timestamp: string;
	detail?: string;
	icon?: React.ComponentType<{ className?: string }>;
	color?: string;
}

/**
 * HistoryTab displays the audit trail and change history for an item.
 */
export function HistoryTab({ item, className }: HistoryTabProps) {
	const createdAtLabel = item.createdAt
		? new Date(item.createdAt).toLocaleString(undefined, {
				year: "numeric",
				month: "long",
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit",
			})
		: "Unknown";

	const updatedAtLabel = item.updatedAt
		? new Date(item.updatedAt).toLocaleString(undefined, {
				year: "numeric",
				month: "long",
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit",
			})
		: "Unknown";

	const timelineEvents = useMemo<TimelineEvent[]>(() => {
		const events: TimelineEvent[] = [];

		if (item.createdAt) {
			events.push({
				label: "Item Created",
				timestamp: item.createdAt,
				detail: `Status: ${item.status}`,
				icon: CalendarClock,
				color: "text-emerald-500",
			});
		}

		if (item.updatedAt && item.updatedAt !== item.createdAt) {
			events.push({
				label: "Last Updated",
				timestamp: item.updatedAt,
				detail: `Version ${item.version}`,
				icon: CircleDot,
				color: "text-sky-500",
			});
		}

		if (item.version > 1 && item.updatedAt) {
			events.push({
				label: "Version Bumped",
				timestamp: item.updatedAt,
				detail: `Now at v${item.version}`,
				icon: GitBranch,
				color: "text-violet-500",
			});
		}

		// Sort events by timestamp (newest first)
		return events.sort((a, b) => (a.timestamp > b.timestamp ? -1 : 1));
	}, [item]);

	const timeSinceUpdate = useMemo(() => {
		if (!item.updatedAt) return "Unknown";

		const now = new Date();
		const updated = new Date(item.updatedAt);
		const diffMs = now.getTime() - updated.getTime();
		const diffMins = Math.floor(diffMs / 60000);
		const diffHours = Math.floor(diffMs / 3600000);
		const diffDays = Math.floor(diffMs / 86400000);

		if (diffMins < 60) return `${diffMins} minutes ago`;
		if (diffHours < 24) return `${diffHours} hours ago`;
		return `${diffDays} days ago`;
	}, [item.updatedAt]);

	return (
		<div className={cn("space-y-6", className)}>
			{/* Summary Cards */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				<Card className="border-0 bg-muted/40 p-4 space-y-3">
					<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
						Created
					</p>
					<div className="flex items-center gap-3">
						<div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
							<CalendarClock
								className="h-4 w-4 text-emerald-500"
								aria-hidden="true"
							/>
						</div>
						<div>
							<p className="text-sm font-bold">{createdAtLabel}</p>
							{item.owner && (
								<p className="text-xs text-muted-foreground">by {item.owner}</p>
							)}
						</div>
					</div>
				</Card>

				<Card className="border-0 bg-muted/40 p-4 space-y-3">
					<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
						Last Updated
					</p>
					<div className="flex items-center gap-3">
						<div className="h-10 w-10 rounded-lg bg-sky-500/10 flex items-center justify-center">
							<CircleDot className="h-4 w-4 text-sky-500" aria-hidden="true" />
						</div>
						<div>
							<p className="text-sm font-bold">{updatedAtLabel}</p>
							<p className="text-xs text-muted-foreground">{timeSinceUpdate}</p>
						</div>
					</div>
				</Card>

				<Card className="border-0 bg-muted/40 p-4 space-y-3">
					<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
						Version
					</p>
					<div className="flex items-center gap-3">
						<div className="h-10 w-10 rounded-lg bg-violet-500/10 flex items-center justify-center">
							<GitBranch
								className="h-4 w-4 text-violet-500"
								aria-hidden="true"
							/>
						</div>
						<div>
							<p className="text-2xl font-black">v{item.version}</p>
							<p className="text-xs text-muted-foreground">
								{item.version === 1 ? "Initial version" : "Updated"}
							</p>
						</div>
					</div>
				</Card>
			</div>

			{/* Timeline */}
			<div className="space-y-4">
				<h2 className="text-lg font-black tracking-tight">Activity Timeline</h2>

				<Card className="border-0 bg-muted/40 p-6">
					<div className="space-y-6" role="list" aria-label="Activity timeline">
						{timelineEvents.length > 0 ? (
							timelineEvents.map((event, index) => {
								const Icon = event.icon || CircleDot;
								return (
									<div
										key={`${event.label}-${event.timestamp}`}
										className="flex items-start gap-4 relative"
										role="listitem"
									>
										{/* Connector line */}
										{index < timelineEvents.length - 1 && (
											<div
												className="absolute left-5 top-10 bottom-0 w-px bg-border"
												aria-hidden="true"
											/>
										)}

										{/* Icon */}
										<div
											className={cn(
												"h-10 w-10 rounded-full bg-muted flex items-center justify-center flex-shrink-0 relative z-10",
												event.color,
											)}
										>
											<Icon className="h-5 w-5" aria-hidden="true" />
										</div>

										{/* Content */}
										<div className="flex-1 pt-1.5">
											<div className="flex items-start justify-between gap-4 flex-wrap">
												<div>
													<p className="font-bold text-sm">{event.label}</p>
													{event.detail && (
														<p className="text-xs text-muted-foreground">
															{event.detail}
														</p>
													)}
												</div>
												<Badge
													variant="secondary"
													className="text-xs whitespace-nowrap"
												>
													{new Date(event.timestamp).toLocaleDateString(
														undefined,
														{
															month: "short",
															day: "numeric",
															year: "numeric",
														},
													)}
												</Badge>
											</div>
										</div>
									</div>
								);
							})
						) : (
							<div className="text-center py-8 text-muted-foreground">
								<Timer
									className="h-8 w-8 mx-auto mb-2 opacity-20"
									aria-hidden="true"
								/>
								<p className="text-sm font-medium">No activity recorded</p>
							</div>
						)}
					</div>
				</Card>
			</div>

			{/* Additional Metadata */}
			<div className="space-y-4">
				<h2 className="text-lg font-black tracking-tight">Metadata</h2>

				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					<Card className="border-0 bg-muted/40 p-4">
						<div className="space-y-2 text-sm">
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Canonical ID</span>
								<span className="font-bold truncate ml-2">
									{item.canonicalId || "—"}
								</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Parent ID</span>
								<span className="font-bold truncate ml-2">
									{item.parentId ? `${item.parentId.slice(0, 12)}...` : "Root"}
								</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Perspective</span>
								<span className="font-bold">
									{item.perspective || "Default"}
								</span>
							</div>
						</div>
					</Card>

					<Card className="border-0 bg-muted/40 p-4">
						<div className="space-y-2 text-sm">
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Project ID</span>
								<span className="font-bold truncate ml-2">
									{item.projectId.slice(0, 12)}...
								</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">Item ID</span>
								<span className="font-bold truncate ml-2">
									{item.id.slice(0, 12)}...
								</span>
							</div>
							<div className="flex items-center justify-between">
								<span className="text-muted-foreground">View</span>
								<span className="font-bold capitalize">
									{item.view?.toLowerCase() || "General"}
								</span>
							</div>
						</div>
					</Card>
				</div>
			</div>
		</div>
	);
}
