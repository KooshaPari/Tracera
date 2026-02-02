import type { Scenario, ScenarioStatus } from "@tracertm/types";
import {
	Badge,
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	cn,
} from "@tracertm/ui";
import {
	ArrowRight,
	BarChart3,
	CheckCircle2,
	Clock,
	FileText,
	Play,
	XCircle,
} from "lucide-react";

interface ScenarioCardProps {
	scenario: Scenario;
	onRun?: () => void;
	onClick?: () => void;
	onViewTestCases?: () => void;
	className?: string;
	showExecutionStats?: boolean;
}

const statusColors: Record<ScenarioStatus, string> = {
	draft: "bg-gray-500/10 text-gray-500 border-gray-500/20",
	pending: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
	passing: "bg-green-500/10 text-green-500 border-green-500/20",
	failing: "bg-red-500/10 text-red-500 border-red-500/20",
	skipped: "bg-muted text-muted-foreground border-border",
};

const statusIcons: Record<ScenarioStatus, React.ComponentType<{ className?: string }>> = {
	draft: FileText,
	pending: Clock,
	passing: CheckCircle2,
	failing: XCircle,
	skipped: Clock,
};

export function ScenarioCard({
	scenario,
	onRun,
	onClick,
	onViewTestCases,
	className,
	showExecutionStats = true,
}: ScenarioCardProps) {
	const StatusIcon = statusIcons[scenario.status] || FileText;
	// Compute total steps but mark as intentionally unused
	void (
		(scenario.givenSteps?.length || 0) +
		(scenario.whenSteps?.length || 0) +
		(scenario.thenSteps?.length || 0)
	);
	const executionCount = scenario.executionCount || 0;
	const lastExecuted = scenario.lastRunAt
		? new Date(scenario.lastRunAt).toLocaleDateString()
		: null;

	return (
		<Card
			className={cn(
				"hover:shadow-md hover:bg-muted/30 hover:border-primary/30 transition-all duration-200 cursor-pointer",
				className,
			)}
			onClick={onClick}
		>
			<CardHeader className="pb-3">
				<div className="flex justify-between items-start">
					<div className="flex items-center gap-2">
						<Badge variant="outline" className="font-mono text-xs">
							{scenario.scenarioNumber}
						</Badge>
						<Badge className={statusColors[scenario.status]}>
							<StatusIcon className="w-3 h-3 mr-1" />
							{scenario.status}
						</Badge>
						{scenario.isOutline && (
							<Badge variant="secondary" className="text-[10px] h-5">
								Outline
							</Badge>
						)}
					</div>
					{onRun && (
						<Button
							size="icon"
							variant="ghost"
							className="h-6 w-6 hover:bg-muted/50 transition-colors"
							onClick={(e) => {
								e.stopPropagation();
								onRun();
							}}
							title="Run scenario"
						>
							<Play className="w-3 h-3" />
						</Button>
					)}
				</div>
				<CardTitle className="text-base mt-2">{scenario.title}</CardTitle>
			</CardHeader>

			<CardContent className="pb-4 pt-0 space-y-3">
				{/* Step counts */}
				<div className="flex gap-4 text-xs text-muted-foreground">
					<div className="flex items-center gap-1">
						<span className="font-bold text-foreground">
							{scenario.givenSteps?.length || 0}
						</span>
						Given
					</div>
					<div className="flex items-center gap-1">
						<span className="font-bold text-foreground">
							{scenario.whenSteps?.length || 0}
						</span>
						When
					</div>
					<div className="flex items-center gap-1">
						<span className="font-bold text-foreground">
							{scenario.thenSteps?.length || 0}
						</span>
						Then
					</div>
				</div>

				{/* Execution stats */}
				{showExecutionStats && (
					<div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border/50">
						<div className="flex items-center gap-2">
							<BarChart3 className="w-3 h-3" />
							<span>
								<span className="font-semibold text-foreground">
									{executionCount}
								</span>
								{" runs"}
							</span>
						</div>
						{lastExecuted && (
							<span className="text-[10px]">Last: {lastExecuted}</span>
						)}
					</div>
				)}

				{/* Test cases link */}
				{onViewTestCases && (
					<Button
						onClick={(e) => {
							e.stopPropagation();
							onViewTestCases();
						}}
						variant="outline"
						size="sm"
						className="w-full text-xs h-7 gap-1"
					>
						View Test Cases
						<ArrowRight className="w-3 h-3" />
					</Button>
				)}
			</CardContent>
		</Card>
	);
}
