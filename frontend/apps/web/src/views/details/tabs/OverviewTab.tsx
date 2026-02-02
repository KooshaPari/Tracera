/**
 * OverviewTab - Generic overview information for items
 *
 * Displays:
 * - Title and description
 * - Creation and update dates
 * - Owner and assignee
 * - Version and perspective
 * - Status and priority
 */

import type { TypedItem } from "@tracertm/types";
import { Badge, Card } from "@tracertm/ui";
import { CalendarClock, CircleDot, Hash, User } from "lucide-react";
import { cn } from "@/lib/utils";

const statusColors: Record<string, string> = {
	blocked: "bg-rose-500/15 text-rose-700 border-rose-500/30",
	cancelled: "bg-gray-500/15 text-gray-700 border-gray-500/30",
	done: "bg-emerald-500/15 text-emerald-700 border-emerald-500/30",
	in_progress: "bg-sky-500/15 text-sky-700 border-sky-500/30",
	todo: "bg-slate-500/10 text-slate-600 border-slate-500/20",
};

const priorityColors: Record<string, string> = {
	critical: "bg-rose-500 text-white",
	high: "bg-orange-500 text-white",
	low: "bg-emerald-500 text-white",
	medium: "bg-indigo-500 text-white",
};

export interface OverviewTabProps {
	/** The item to display */
	item: TypedItem;

	/** Optional additional content */
	children?: React.ReactNode;

	/** Optional CSS classes */
	className?: string;
}

/**
 * OverviewTab displays basic item information in a consistent layout.
 */
export function OverviewTab({ item, children, className }: OverviewTabProps) {
	const createdAtLabel = item.createdAt
		? new Date(item.createdAt).toLocaleDateString(undefined, {
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit",
				month: "long",
				year: "numeric",
			})
		: "Unknown";

	const updatedAtLabel = item.updatedAt
		? new Date(item.updatedAt).toLocaleDateString(undefined, {
				day: "numeric",
				hour: "2-digit",
				minute: "2-digit",
				month: "long",
				year: "numeric",
			})
		: "Unknown";

	const detailsHeading =
		item.view && typeof item.view === "string"
			? `${item.view.charAt(0).toUpperCase()}${item.view.slice(1).toLowerCase()} Details`
			: "Item Details";

	return (
		<div className={cn("space-y-6", className)}>
			{/* Primary Information */}
			<div className="space-y-4">
				<h2 className="text-lg font-black tracking-tight">{detailsHeading}</h2>

				<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
					{/* Status & Priority */}
					<Card className="border-0 bg-muted/40 p-4 space-y-3">
						<p
							className="text-[10px] font-black uppercase tracking-widest text-muted-foreground"
							id="status-priority-label"
						>
							Status & Priority
						</p>
						<div
							className="flex items-center gap-2"
							aria-labelledby="status-priority-label"
						>
							<Badge
								className={cn(
									"text-[10px] font-black uppercase tracking-widest",
									statusColors[item.status] || statusColors["todo"],
								)}
							>
								{item.status.replace("_", " ")}
							</Badge>
							<Badge
								className={cn(
									"text-[10px] font-black uppercase tracking-widest",
									priorityColors[item.priority] || priorityColors["medium"],
								)}
							>
								{item.priority}
							</Badge>
						</div>
					</Card>

					{/* Owner */}
					<Card className="border-0 bg-muted/40 p-4 space-y-3">
						<p
							className="text-[10px] font-black uppercase tracking-widest text-muted-foreground"
							id="owner-label"
						>
							Owner
						</p>
						<div
							className="flex items-center gap-2"
							aria-labelledby="owner-label"
						>
							<div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center">
								<User className="h-3 w-3 text-primary" aria-hidden="true" />
							</div>
							<span className="text-sm font-bold">
								{item.owner || "Unassigned"}
							</span>
						</div>
					</Card>

					{/* Version & Perspective */}
					<Card className="border-0 bg-muted/40 p-4 space-y-3">
						<p
							className="text-[10px] font-black uppercase tracking-widest text-muted-foreground"
							id="version-label"
						>
							Version & Perspective
						</p>
						<div
							className="flex items-center justify-between text-sm font-bold"
							aria-labelledby="version-label"
						>
							<span>
								<span className="sr-only">Version </span>v{item.version}
							</span>
							<span className="text-muted-foreground">
								{item.perspective || "default"}
							</span>
						</div>
					</Card>

					{/* Identifiers */}
					<Card className="border-0 bg-muted/40 p-4 space-y-3">
						<p
							className="text-[10px] font-black uppercase tracking-widest text-muted-foreground"
							id="identifiers-label"
						>
							Identifiers
						</p>
						<div className="space-y-2" aria-labelledby="identifiers-label">
							<div className="flex items-center gap-2 text-xs">
								<Hash
									className="h-3 w-3 text-muted-foreground"
									aria-hidden="true"
								/>
								<span className="font-mono text-muted-foreground">ID:</span>
								<span className="font-bold truncate">{item.id}</span>
							</div>
							{item.canonicalId && (
								<div className="flex items-center gap-2 text-xs">
									<CircleDot
										className="h-3 w-3 text-muted-foreground"
										aria-hidden="true"
									/>
									<span className="font-mono text-muted-foreground">
										Canonical:
									</span>
									<span className="font-bold truncate">{item.canonicalId}</span>
								</div>
							)}
							{item.parentId && (
								<div className="flex items-center gap-2 text-xs">
									<CircleDot
										className="h-3 w-3 text-muted-foreground"
										aria-hidden="true"
									/>
									<span className="font-mono text-muted-foreground">
										Parent:
									</span>
									<span className="font-bold truncate">
										{item.parentId.slice(0, 8)}...
									</span>
								</div>
							)}
						</div>
					</Card>
				</div>
			</div>

			{/* Timestamps */}
			<div className="space-y-4">
				<h2 className="text-lg font-black tracking-tight">Timeline</h2>

				<Card className="border-0 bg-muted/40 p-4">
					<div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
						<div className="flex items-center gap-3">
							<div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
								<CalendarClock
									className="h-4 w-4 text-primary"
									aria-hidden="true"
								/>
							</div>
							<div>
								<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Created
								</p>
								<p className="font-bold">{createdAtLabel}</p>
							</div>
						</div>

						<div className="flex items-center gap-3">
							<div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
								<CircleDot
									className="h-4 w-4 text-primary"
									aria-hidden="true"
								/>
							</div>
							<div>
								<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
									Last Updated
								</p>
								<p className="font-bold">{updatedAtLabel}</p>
							</div>
						</div>
					</div>
				</Card>
			</div>

			{/* Description */}
			{item.description && (
				<div className="space-y-4">
					<h2 className="text-lg font-black tracking-tight">Description</h2>
					<Card className="border-0 bg-muted/40 p-4">
						<p className="text-sm leading-relaxed whitespace-pre-wrap">
							{item.description}
						</p>
					</Card>
				</div>
			)}

			{/* Additional content */}
			{children}
		</div>
	);
}
