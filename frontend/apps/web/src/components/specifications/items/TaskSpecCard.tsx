/**
 * TaskSpec Card Component
 *
 * Displays task specification with time tracking,
 * blockers, and completion status.
 */

import { cn } from "@/lib/utils";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Progress,
} from "@tracertm/ui";
import {
	AlertTriangle,
	ArrowRight,
	Calendar,
	CheckCircle2,
	Circle,
	GitBranch,
	Hourglass,
	Play,
	Search,
	Timer,
	User,
	XCircle,
} from "lucide-react";
import type { TaskSpec } from "@/hooks/useItemSpecs";
import { format, differenceInDays } from "date-fns";

interface TaskSpecCardProps {
	spec: TaskSpec;
	onClick?: () => void;
	className?: string;
	compact?: boolean;
	showBlockers?: boolean;
}

const statusStyles = {
	todo: { bg: "bg-muted", text: "text-muted-foreground", icon: Circle },
	in_progress: { bg: "bg-blue-500/10", text: "text-blue-600", icon: Play },
	review: { bg: "bg-purple-500/10", text: "text-purple-600", icon: Search },
	done: { bg: "bg-green-500/10", text: "text-green-600", icon: CheckCircle2 },
	blocked: { bg: "bg-red-500/10", text: "text-red-600", icon: XCircle },
};

function formatDuration(minutes: number): string {
	if (minutes < 60) return `${minutes}m`;
	const hours = Math.floor(minutes / 60);
	const mins = minutes % 60;
	if (hours < 24) return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
	const days = Math.floor(hours / 24);
	const remainingHours = hours % 24;
	return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
}

export function TaskSpecCard({
	spec,
	onClick,
	className,
	compact = false,
	showBlockers = true,
}: TaskSpecCardProps) {
	const statusStyle = statusStyles[spec.status];
	const StatusIcon = statusStyle.icon;

	// Calculate time tracking
	const estimatedMinutes = spec.estimated_hours
		? spec.estimated_hours * 60
		: null;
	const actualMinutes = spec.actual_hours ? spec.actual_hours * 60 : null;
	const timeProgress =
		estimatedMinutes && actualMinutes
			? Math.min((actualMinutes / estimatedMinutes) * 100, 150)
			: 0;
	const isOvertime =
		actualMinutes && estimatedMinutes && actualMinutes > estimatedMinutes;

	// Calculate subtask completion
	const subtasksCompleted =
		spec.subtasks?.filter((s) => s.completed).length ?? 0;
	const subtasksTotal = spec.subtasks?.length ?? 0;
	const subtaskProgress =
		subtasksTotal > 0 ? (subtasksCompleted / subtasksTotal) * 100 : 0;

	// Check if overdue
	const isOverdue =
		spec.due_date &&
		new Date(spec.due_date) < new Date() &&
		spec.status !== "done";

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
								{isOverdue && (
									<Badge variant="destructive" className="text-[10px]">
										Overdue
									</Badge>
								)}
								{spec.assigned_to && (
									<Badge variant="outline" className="text-[10px]">
										<User className="w-2.5 h-2.5 mr-1" />
										{spec.assigned_to}
									</Badge>
								)}
							</div>
							<p className="text-xs font-medium truncate">{spec.task_title}</p>
							{subtasksTotal > 0 && (
								<div className="flex items-center gap-2 mt-2">
									<span className="text-[10px] text-muted-foreground">
										Subtasks:
									</span>
									<Progress value={subtaskProgress} className="h-1 flex-1" />
									<span className="text-xs font-bold tabular-nums">
										{subtasksCompleted}/{subtasksTotal}
									</span>
								</div>
							)}
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
							{isOverdue && (
								<Badge variant="destructive" className="text-[10px]">
									<AlertTriangle className="w-2.5 h-2.5 mr-1" />
									Overdue
								</Badge>
							)}
						</div>
						<CardTitle className="text-sm font-semibold">
							{spec.task_title}
						</CardTitle>
						{spec.description && (
							<p className="text-xs text-muted-foreground mt-1 line-clamp-2">
								{spec.description}
							</p>
						)}
					</div>

					{/* Assignee */}
					{spec.assigned_to && (
						<div className="flex items-center gap-2 text-xs">
							<div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center">
								<User className="h-3 w-3 text-primary" />
							</div>
							<span className="font-medium">{spec.assigned_to}</span>
						</div>
					)}
				</div>
			</CardHeader>

			<CardContent className="space-y-4">
				{/* Time Tracking */}
				{(estimatedMinutes || actualMinutes) && (
					<div className="space-y-2">
						<div className="flex items-center justify-between">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								Time Tracking
							</h4>
							{isOvertime && (
								<Badge variant="destructive" className="text-[9px]">
									Over budget
								</Badge>
							)}
						</div>
						<div className="grid grid-cols-2 gap-3">
							{estimatedMinutes && (
								<div className="p-2 rounded-lg bg-muted/30 text-center">
									<div className="flex items-center justify-center gap-1 text-sm font-bold">
										<Hourglass className="w-3 h-3 text-muted-foreground" />
										{formatDuration(estimatedMinutes)}
									</div>
									<div className="text-[10px] text-muted-foreground">
										Estimated
									</div>
								</div>
							)}
							{actualMinutes !== null && (
								<div
									className={cn(
										"p-2 rounded-lg text-center",
										isOvertime ? "bg-red-500/10" : "bg-green-500/10",
									)}
								>
									<div
										className={cn(
											"flex items-center justify-center gap-1 text-sm font-bold",
											isOvertime ? "text-red-600" : "text-green-600",
										)}
									>
										<Timer className="w-3 h-3" />
										{formatDuration(actualMinutes)}
									</div>
									<div className="text-[10px] text-muted-foreground">
										Actual
									</div>
								</div>
							)}
						</div>
						{estimatedMinutes && actualMinutes !== null && (
							<Progress
								value={Math.min(timeProgress, 100)}
								className={cn("h-1", isOvertime && "[&>div]:bg-red-500")}
							/>
						)}
					</div>
				)}

				{/* Due Date */}
				{spec.due_date && (
					<div className="flex items-center gap-2 p-2 rounded-lg bg-muted/30">
						<Calendar
							className={cn(
								"w-4 h-4",
								isOverdue ? "text-red-500" : "text-muted-foreground",
							)}
						/>
						<div className="flex-1">
							<span
								className={cn(
									"text-xs font-medium",
									isOverdue && "text-red-600",
								)}
							>
								Due {format(new Date(spec.due_date), "MMM d, yyyy")}
							</span>
							{isOverdue && (
								<span className="text-[10px] text-red-500 ml-2">
									(
									{Math.abs(
										differenceInDays(new Date(spec.due_date), new Date()),
									)}{" "}
									days overdue)
								</span>
							)}
						</div>
					</div>
				)}

				{/* Subtasks */}
				{subtasksTotal > 0 && (
					<div className="space-y-2">
						<div className="flex items-center justify-between">
							<h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
								Subtasks
							</h4>
							<span className="text-xs font-bold">
								{subtasksCompleted} / {subtasksTotal}
							</span>
						</div>
						<Progress value={subtaskProgress} className="h-2" />
						<div className="space-y-1.5 mt-2">
							{spec.subtasks?.slice(0, 4).map((subtask, i) => (
								<div
									key={i}
									className={cn(
										"flex items-center gap-2 p-1.5 rounded text-xs",
										subtask.completed ? "bg-green-500/10" : "bg-muted/30",
									)}
								>
									{subtask.completed ? (
										<CheckCircle2 className="w-3 h-3 text-green-600" />
									) : (
										<Circle className="w-3 h-3 text-muted-foreground" />
									)}
									<span
										className={cn(
											"flex-1 truncate",
											subtask.completed && "line-through text-muted-foreground",
										)}
									>
										{subtask.title}
									</span>
								</div>
							))}
							{subtasksTotal > 4 && (
								<p className="text-[10px] text-muted-foreground pl-5">
									+{subtasksTotal - 4} more subtasks
								</p>
							)}
						</div>
					</div>
				)}

				{/* Blocking Items */}
				{showBlockers && spec.blocking.length > 0 && (
					<div className="space-y-2">
						<h4 className="text-[10px] font-black uppercase tracking-widest text-red-500">
							Blocking ({spec.blocking.length})
						</h4>
						<div className="space-y-1.5">
							{spec.blocking.slice(0, 2).map((blocked, i) => (
								<div
									key={i}
									className="flex items-start gap-2 p-2 rounded-lg bg-red-500/10 border border-red-500/20"
								>
									<XCircle className="w-3.5 h-3.5 text-red-600 mt-0.5 shrink-0" />
									<span className="text-xs">{blocked}</span>
								</div>
							))}
							{spec.blocking.length > 2 && (
								<p className="text-[10px] text-muted-foreground">
									+{spec.blocking.length - 2} more
								</p>
							)}
						</div>
					</div>
				)}

				{/* Dependencies & Labels */}
				<div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
					<div className="flex items-center gap-4">
						{spec.dependencies.length > 0 && (
							<div className="flex items-center gap-1">
								<GitBranch className="w-3 h-3" />
								<span>{spec.dependencies.length} deps</span>
							</div>
						)}
						{spec.parent_story && (
							<div className="flex items-center gap-1">
								<span>Story: {spec.parent_story}</span>
							</div>
						)}
					</div>
					{spec.labels.length > 0 && (
						<div className="flex gap-1">
							{spec.labels.slice(0, 2).map((label, i) => (
								<Badge key={i} variant="secondary" className="text-[9px]">
									{label}
								</Badge>
							))}
						</div>
					)}
				</div>
			</CardContent>
		</Card>
	);
}
