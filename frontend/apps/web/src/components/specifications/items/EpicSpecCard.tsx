/**
 * EpicSpec Card Component
 *
 * Displays epic specification with business value, timeline,
 * story tracking, and risk visualization.
 */

import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Progress,
} from "@tracertm/ui";
import { differenceInDays, format } from "date-fns";
import {
	AlertTriangle,
	ArrowRight,
	Calendar,
	CheckCircle2,
	Clock,
	FileText,
	Flag,
	GitBranch,
	Target,
	TrendingUp,
	Users,
} from "lucide-react";
import type { EpicSpec } from "@/hooks/useItemSpecs";
import { cn } from "@/lib/utils";

interface EpicSpecCardProps {
	spec: EpicSpec;
	onClick?: () => void;
	className?: string;
	compact?: boolean;
	showRisks?: boolean;
}

const statusStyles = {
	archived: { bg: "bg-gray-500/10", icon: FileText, text: "text-gray-600" },
	backlog: { bg: "bg-muted", icon: Clock, text: "text-muted-foreground" },
	completed: {
		bg: "bg-green-500/10",
		icon: CheckCircle2,
		text: "text-green-600",
	},
	in_progress: {
		bg: "bg-blue-500/10",
		icon: TrendingUp,
		text: "text-blue-600",
	},
};

const riskImpactStyles = {
	critical: "bg-red-500 text-white",
	high: "bg-orange-500 text-white",
	low: "bg-green-500 text-white",
	medium: "bg-yellow-500 text-white",
	minimal: "bg-blue-500 text-white",
};

export function EpicSpecCard({
	spec,
	onClick,
	className,
	compact = false,
	showRisks = true,
}: EpicSpecCardProps) {
	const statusStyle = statusStyles[spec.status];
	const StatusIcon = statusStyle.icon;

	// Calculate progress based on objectives completed (if tracked in metrics)
	const storiesCompleted =
		(spec.metrics as Record<string, number>)?.["stories_completed"] ?? 0;
	const storiesTotal =
		spec.child_stories_count || spec.user_stories.length || 1;
	const progressPercent = Math.min(
		(storiesCompleted / storiesTotal) * 100,
		100,
	);

	// Calculate days remaining
	const daysRemaining = spec.end_date
		? differenceInDays(new Date(spec.end_date), new Date())
		: null;

	if (compact) {
		return (
			<Card
				className={cn(
					"hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer",
					className,
				)}
				onClick={onClick}
			>
				<CardContent className="p-3">
					<div className="flex items-start justify-between gap-2">
						<div className="flex-1 min-w-0">
							<div className="flex items-center gap-2 mb-1 flex-wrap">
								<Badge
									className={cn(
										"text-[10px]",
										statusStyle.bg,
										statusStyle.text,
									)}
								>
									<StatusIcon className="w-2.5 h-2.5 mr-1" />
									{spec.status.replace("_", " ")}
								</Badge>
								<Badge variant="outline" className="text-[10px]">
									<TrendingUp className="w-2.5 h-2.5 mr-1" />
									BV: {spec.business_value}
								</Badge>
							</div>
							<p className="text-xs font-semibold truncate">{spec.epic_name}</p>
							<div className="flex items-center gap-2 mt-2">
								<span className="text-[10px] text-muted-foreground">
									Progress:
								</span>
								<Progress value={progressPercent} className="h-1 flex-1" />
								<span className="text-xs font-bold tabular-nums">
									{storiesCompleted}/{storiesTotal}
								</span>
							</div>
						</div>
						<Button variant="ghost" size="sm" className="h-7 shrink-0">
							<ArrowRight className="w-3 h-3" />
						</Button>
					</div>
				</CardContent>
			</Card>
		);
	}

	return (
		<Card
			className={cn(
				"hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200",
				onClick && "cursor-pointer",
				className,
			)}
			onClick={onClick}
		>
			<CardHeader className="pb-3">
				<div className="flex justify-between items-start gap-4">
					<div className="flex-1">
						<div className="flex items-center gap-2 mb-2 flex-wrap">
							<Badge
								className={cn("text-[10px]", statusStyle.bg, statusStyle.text)}
							>
								<StatusIcon className="w-2.5 h-2.5 mr-1" />
								{spec.status.replace("_", " ")}
							</Badge>
							<Badge variant="outline" className="text-[10px]">
								<TrendingUp className="w-2.5 h-2.5 mr-1" />
								Business Value: {spec.business_value}
							</Badge>
							{spec.target_release && (
								<Badge variant="secondary" className="text-[10px]">
									<Flag className="w-2.5 h-2.5 mr-1" />
									{spec.target_release}
								</Badge>
							)}
						</div>
						<CardTitle className="text-base">{spec.epic_name}</CardTitle>
						{spec.scope_statement && (
							<p className="text-xs text-muted-foreground mt-1 line-clamp-2">
								{spec.scope_statement}
							</p>
						)}
					</div>

					{/* Progress Ring */}
					<div className="text-right">
						<div className="text-2xl font-black tabular-nums">
							{progressPercent.toFixed(0)}%
						</div>
						<div className="text-[10px] text-muted-foreground uppercase">
							Complete
						</div>
					</div>
				</div>
			</CardHeader>

			<CardContent className="space-y-4">
				{/* Timeline */}
				{(spec.start_date || spec.end_date) && (
					<div className="flex items-center gap-4 p-3 rounded-lg bg-muted/30">
						<Calendar className="w-4 h-4 text-muted-foreground" />
						<div className="flex-1">
							<div className="flex justify-between text-xs">
								<span className="text-muted-foreground">
									{spec.start_date
										? format(new Date(spec.start_date), "MMM d, yyyy")
										: "Not started"}
								</span>
								<span className="font-medium">
									{spec.end_date
										? format(new Date(spec.end_date), "MMM d, yyyy")
										: "No deadline"}
								</span>
							</div>
							{daysRemaining !== null && (
								<div className="mt-1">
									<Progress
										value={Math.max(
											0,
											Math.min(100, 100 - (daysRemaining / 90) * 100),
										)}
										className="h-1"
									/>
									<span
										className={cn(
											"text-[10px] font-medium",
											daysRemaining < 0
												? "text-red-500"
												: (daysRemaining < 7
													? "text-orange-500"
													: "text-muted-foreground"),
										)}
									>
										{daysRemaining < 0
											? `${Math.abs(daysRemaining)} days overdue`
											: `${daysRemaining} days remaining`}
									</span>
								</div>
							)}
						</div>
					</div>
				)}

				{/* Stories Progress */}
				<div className="space-y-2">
					<div className="flex items-center justify-between">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
							User Stories
						</h4>
						<span className="text-xs font-bold">
							{storiesCompleted} / {storiesTotal}
						</span>
					</div>
					<Progress value={progressPercent} className="h-2" />
					{spec.user_stories.length > 0 && (
						<div className="flex flex-wrap gap-1 mt-1">
							{spec.user_stories.slice(0, 5).map((story, i) => (
								<Badge key={i} variant="outline" className="text-[9px]">
									{story}
								</Badge>
							))}
							{spec.user_stories.length > 5 && (
								<Badge variant="secondary" className="text-[9px]">
									+{spec.user_stories.length - 5} more
								</Badge>
							)}
						</div>
					)}
				</div>

				{/* Objectives & Success Criteria */}
				{spec.objectives.length > 0 && (
					<div className="space-y-2">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
							Objectives
						</h4>
						<ul className="text-xs space-y-1">
							{spec.objectives.slice(0, 3).map((obj, i) => (
								<li key={i} className="flex items-start gap-2">
									<Target className="w-3 h-3 text-primary mt-0.5 shrink-0" />
									<span className="line-clamp-1">{obj}</span>
								</li>
							))}
							{spec.objectives.length > 3 && (
								<li className="text-muted-foreground text-[10px] pl-5">
									+{spec.objectives.length - 3} more objectives
								</li>
							)}
						</ul>
					</div>
				)}

				{/* Risks */}
				{showRisks && spec.risks.length > 0 && (
					<div className="space-y-2">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
							Risks ({spec.risks.length})
						</h4>
						<div className="space-y-2">
							{spec.risks.slice(0, 2).map((risk, i) => (
								<div
									key={i}
									className="p-2 rounded-lg bg-muted/30 border border-muted"
								>
									<div className="flex items-start gap-2">
										<AlertTriangle className="w-3.5 h-3.5 text-orange-500 mt-0.5 shrink-0" />
										<div className="flex-1 min-w-0">
											<div className="flex items-center gap-2 mb-0.5">
												<Badge
													className={cn(
														"text-[9px]",
														riskImpactStyles[
															risk.impact as keyof typeof riskImpactStyles
														],
													)}
												>
													{risk.impact}
												</Badge>
											</div>
											<p className="text-xs line-clamp-1">{risk.description}</p>
											{risk.mitigation && (
												<p className="text-[10px] text-muted-foreground mt-0.5 line-clamp-1">
													Mitigation: {risk.mitigation}
												</p>
											)}
										</div>
									</div>
								</div>
							))}
							{spec.risks.length > 2 && (
								<p className="text-[10px] text-muted-foreground">
									+{spec.risks.length - 2} more risks
								</p>
							)}
						</div>
					</div>
				)}

				{/* Dependencies & Stakeholders */}
				<div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
					<div className="flex items-center gap-4">
						{spec.dependencies.length > 0 && (
							<div className="flex items-center gap-1">
								<GitBranch className="w-3 h-3" />
								<span>{spec.dependencies.length} deps</span>
							</div>
						)}
						{spec.stakeholders.length > 0 && (
							<div className="flex items-center gap-1">
								<Users className="w-3 h-3" />
								<span>{spec.stakeholders.length} stakeholders</span>
							</div>
						)}
					</div>
					{spec.themes.length > 0 && (
						<div className="flex gap-1">
							{spec.themes.slice(0, 2).map((theme, i) => (
								<Badge key={i} variant="secondary" className="text-[9px]">
									{theme}
								</Badge>
							))}
						</div>
					)}
				</div>
			</CardContent>
		</Card>
	);
}
