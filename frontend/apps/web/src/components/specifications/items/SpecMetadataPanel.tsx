/**
 * SpecMetadataPanel Component
 *
 * Displays common metadata across all item spec types including
 * timestamps, traceability info, and custom metadata fields.
 */

import {
	Badge,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Separator,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	Calendar,
	Clock,
	FileText,
	GitBranch,
	Link2,
	RefreshCw,
	Tag,
	TrendingDown,
	TrendingUp,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface SpecMetadataPanelProps {
	createdAt: string;
	updatedAt: string;
	metadata?: Record<string, unknown>;
	upstreamCount?: number;
	downstreamCount?: number;
	changeCount?: number;
	volatilityIndex?: number;
	autoTags?: string[];
	sourceReference?: string;
	className?: string;
}

export function SpecMetadataPanel({
	createdAt,
	updatedAt,
	metadata = {},
	upstreamCount,
	downstreamCount,
	changeCount,
	volatilityIndex,
	autoTags = [],
	sourceReference,
	className,
}: SpecMetadataPanelProps) {
	const metadataEntries = Object.entries(metadata).filter(
		([_, v]) => v !== null && v !== undefined,
	);

	return (
		<Card className={cn("border-none bg-muted/30", className)}>
			<CardHeader className="pb-2">
				<CardTitle className="text-xs font-black uppercase tracking-widest text-muted-foreground">
					Specification Metadata
				</CardTitle>
			</CardHeader>
			<CardContent className="space-y-4">
				{/* Timestamps */}
				<div className="space-y-2">
					<div className="flex items-center justify-between text-xs">
						<span className="flex items-center gap-1 text-muted-foreground">
							<Calendar className="w-3 h-3" />
							Created
						</span>
						<span className="font-medium">
							{format(new Date(createdAt), "MMM d, yyyy")}
						</span>
					</div>
					<div className="flex items-center justify-between text-xs">
						<span className="flex items-center gap-1 text-muted-foreground">
							<RefreshCw className="w-3 h-3" />
							Updated
						</span>
						<span className="font-medium">
							{format(new Date(updatedAt), "MMM d, yyyy 'at' HH:mm")}
						</span>
					</div>
				</div>

				{/* Traceability */}
				{(upstreamCount !== undefined ||
					downstreamCount !== undefined ||
					changeCount !== undefined) && (
					<>
						<Separator />
						<div className="space-y-2">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								Traceability
							</h4>
							<div className="grid grid-cols-3 gap-2">
								{upstreamCount !== undefined && (
									<div className="text-center p-2 rounded bg-card/50">
										<div className="flex items-center justify-center gap-1">
											<TrendingUp className="w-3 h-3 text-blue-500" />
											<span className="font-bold text-sm">{upstreamCount}</span>
										</div>
										<div className="text-[10px] text-muted-foreground">
											Upstream
										</div>
									</div>
								)}
								{downstreamCount !== undefined && (
									<div className="text-center p-2 rounded bg-card/50">
										<div className="flex items-center justify-center gap-1">
											<TrendingDown className="w-3 h-3 text-green-500" />
											<span className="font-bold text-sm">
												{downstreamCount}
											</span>
										</div>
										<div className="text-[10px] text-muted-foreground">
											Downstream
										</div>
									</div>
								)}
								{changeCount !== undefined && (
									<div className="text-center p-2 rounded bg-card/50">
										<div className="flex items-center justify-center gap-1">
											<GitBranch className="w-3 h-3 text-purple-500" />
											<span className="font-bold text-sm">{changeCount}</span>
										</div>
										<div className="text-[10px] text-muted-foreground">
											Changes
										</div>
									</div>
								)}
							</div>
						</div>
					</>
				)}

				{/* Volatility */}
				{volatilityIndex !== undefined && (
					<div className="flex items-center justify-between text-xs">
						<span className="flex items-center gap-1 text-muted-foreground">
							<Clock className="w-3 h-3" />
							Volatility Index
						</span>
						<Badge
							variant="outline"
							className={cn(
								"text-[10px]",
								volatilityIndex > 0.7
									? "border-red-500 text-red-600"
									: volatilityIndex > 0.4
										? "border-yellow-500 text-yellow-600"
										: "border-green-500 text-green-600",
							)}
						>
							{(volatilityIndex * 100).toFixed(0)}%
						</Badge>
					</div>
				)}

				{/* Auto Tags */}
				{autoTags.length > 0 && (
					<>
						<Separator />
						<div className="space-y-2">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-1">
								<Tag className="w-3 h-3" />
								Auto-Generated Tags
							</h4>
							<div className="flex flex-wrap gap-1">
								{autoTags.map((tag, i) => (
									<Badge key={i} variant="secondary" className="text-[9px]">
										{tag}
									</Badge>
								))}
							</div>
						</div>
					</>
				)}

				{/* Source Reference */}
				{sourceReference && (
					<div className="flex items-center justify-between text-xs">
						<span className="flex items-center gap-1 text-muted-foreground">
							<Link2 className="w-3 h-3" />
							Source
						</span>
						<span className="font-mono text-[10px] truncate max-w-[150px]">
							{sourceReference}
						</span>
					</div>
				)}

				{/* Custom Metadata */}
				{metadataEntries.length > 0 && (
					<>
						<Separator />
						<div className="space-y-2">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground flex items-center gap-1">
								<FileText className="w-3 h-3" />
								Custom Fields
							</h4>
							<div className="space-y-1.5">
								{metadataEntries.slice(0, 6).map(([key, value]) => (
									<div
										key={key}
										className="flex items-center justify-between text-xs"
									>
										<span className="text-muted-foreground truncate max-w-[100px]">
											{key}
										</span>
										<span className="font-medium truncate max-w-[120px]">
											{typeof value === "object" && value !== null
												? JSON.stringify(value)
												: String(value)}
										</span>
									</div>
								))}
								{metadataEntries.length > 6 && (
									<p className="text-[10px] text-muted-foreground">
										+{metadataEntries.length - 6} more fields
									</p>
								)}
							</div>
						</div>
					</>
				)}
			</CardContent>
		</Card>
	);
}
