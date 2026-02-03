/* eslint-disable complexity, func-style, id-length, max-lines-per-function, max-statements, no-magic-numbers, react-perf/jsx-no-new-array-as-prop, react-perf/jsx-no-new-function-as-prop, react-perf/jsx-no-new-object-as-prop, react/jsx-max-depth, sort-imports */
/**
 * ItemSpecsOverview Component
 *
 * Project-level overview of all item specifications across the 6 spec types.
 * Shows summary metrics, recent specs, and quality analysis.
 */

import {
	Badge,
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	Progress,
	Skeleton,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import {
	AlertTriangle,
	ArrowRight,
	Bug,
	CheckCircle2,
	FileCode,
	FileText,
	Layers,
	ListTodo,
	Plus,
	RefreshCw,
	Target,
	TrendingDown,
	TrendingUp,
	Users,
	XCircle,
} from "lucide-react";
import {
	useDefectSpecs,
	useEpicSpecs,
	useHighRiskRequirements,
	useRequirementSpecs,
	useTaskSpecs,
	useTestSpecs,
	useUnverifiedRequirements,
	useUserStorySpecs,
} from "@/hooks/useItemSpecs";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { DefectSpecCard } from "./DefectSpecCard";
import { EpicSpecCard } from "./EpicSpecCard";
import { RequirementSpecCard } from "./RequirementSpecCard";
import { TaskSpecCard } from "./TaskSpecCard";
import { TestSpecCard } from "./TestSpecCard";
import { UserStorySpecCard } from "./UserStorySpecCard";

interface ItemSpecsOverviewProps {
	projectId: string;
	onViewSpec?: (specType: string, specId: string) => void;
	onCreateSpec?: (specType: string) => void;
	className?: string;
}

const specTypeConfig = [
	{
		bg: "bg-blue-500/10",
		color: "text-blue-600",
		description: "EARS patterns, constraints, quality metrics",
		icon: FileText,
		id: "requirement",
		label: "Requirements",
	},
	{
		bg: "bg-purple-500/10",
		color: "text-purple-600",
		description: "Test cases, flakiness detection, coverage",
		icon: FileCode,
		id: "test",
		label: "Tests",
	},
	{
		bg: "bg-indigo-500/10",
		color: "text-indigo-600",
		description: "Business value, timeline, stories",
		icon: Layers,
		id: "epic",
		label: "Epics",
	},
	{
		bg: "bg-green-500/10",
		color: "text-green-600",
		description: "As a/I want/So that, acceptance criteria",
		icon: Users,
		id: "user_story",
		label: "User Stories",
	},
	{
		bg: "bg-orange-500/10",
		color: "text-orange-600",
		description: "Time tracking, subtasks, blockers",
		icon: ListTodo,
		id: "task",
		label: "Tasks",
	},
	{
		bg: "bg-red-500/10",
		color: "text-red-600",
		description: "Severity, reproduction, root cause",
		icon: Bug,
		id: "defect",
		label: "Defects",
	},
];

export function ItemSpecsOverview({
	projectId,
	onViewSpec,
	onCreateSpec,
	className,
}: ItemSpecsOverviewProps) {
	// Fetch all spec types - these return { specs: T[], total: number }
	const { data: reqData, isLoading: reqLoading } =
		useRequirementSpecs(projectId);
	const { data: testData, isLoading: testLoading } = useTestSpecs(projectId);
	const { data: epicData, isLoading: epicLoading } = useEpicSpecs(projectId);
	const { data: storyData, isLoading: storyLoading } =
		useUserStorySpecs(projectId);
	const { data: taskData, isLoading: taskLoading } = useTaskSpecs(projectId);
	const { data: defectData, isLoading: defectLoading } =
		useDefectSpecs(projectId);

	// Quality insights
	const { data: unverifiedData } = useUnverifiedRequirements(projectId, 10);
	const { data: highRiskData } = useHighRiskRequirements(projectId, 10);

	// Extract specs arrays from response objects
	const reqSpecs = reqData?.specs ?? [];
	const testSpecs = testData?.specs ?? [];
	const epicSpecs = epicData?.specs ?? [];
	const storySpecs = storyData?.specs ?? [];
	const taskSpecs = taskData?.specs ?? [];
	const defectSpecs = defectData?.specs ?? [];
	const unverifiedReqs = unverifiedData?.specs ?? [];
	const highRiskReqs = highRiskData?.specs ?? [];

	const isLoading =
		reqLoading ||
		testLoading ||
		epicLoading ||
		storyLoading ||
		taskLoading ||
		defectLoading;

	// Calculate summary metrics
	const specCounts = {
		defect: defectSpecs.length,
		epic: epicSpecs.length,
		requirement: reqSpecs.length,
		task: taskSpecs.length,
		test: testSpecs.length,
		user_story: storySpecs.length,
	};

	const totalSpecs = Object.values(specCounts).reduce((a, b) => a + b, 0);

	// Calculate quality metrics
	const avgQualityScore =
		reqSpecs.length > 0
			? reqSpecs.reduce((sum, r) => sum + (r.overall_quality_score ?? 0), 0) /
				reqSpecs.length
			: 0;

	// Calculate pass rate from pass_count/total_runs
	const testPassRate =
		testSpecs.length > 0
			? testSpecs.reduce((sum, t) => {
					const rate =
						t.total_runs > 0 ? (t.pass_count / t.total_runs) * 100 : 0;
					return sum + rate;
				}, 0) / testSpecs.length
			: 0;

	const avgFlakiness =
		testSpecs.length > 0
			? testSpecs.reduce((sum, t) => sum + (t.flakiness_score ?? 0), 0) /
				testSpecs.length
			: 0;

	// Get open defects
	const openDefects = defectSpecs.filter(
		(d) =>
			d.status !== "resolved" &&
			d.status !== "closed" &&
			d.status !== "verified",
	);
	const criticalDefects = defectSpecs.filter((d) => d.severity === "critical");

	if (isLoading) {
		return (
			<div className={cn("space-y-6", className)}>
				<div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
					{Array.from({ length: 6 }).map((_, i) => (
						<Skeleton key={i} className="h-24" />
					))}
				</div>
				<Skeleton className="h-64" />
			</div>
		);
	}

	return (
		<div className={cn("space-y-6", className)}>
			{/* Header with Create Button */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold tracking-tight">
						Item Specifications
					</h2>
					<p className="text-muted-foreground">
						{totalSpecs} specifications across {specTypeConfig.length} types
					</p>
				</div>
				<div className="flex gap-2">
					{specTypeConfig.slice(0, 3).map((config) => (
						<Button
							key={config.id}
							variant="outline"
							size="sm"
							onClick={() => onCreateSpec?.(config.id)}
							className="gap-1.5"
						>
							<Plus className="w-3.5 h-3.5" />
							{config.label.slice(0, -1)}
						</Button>
					))}
				</div>
			</div>

			{/* Summary Cards Grid */}
			<div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
				{specTypeConfig.map((config, index) => {
					const Icon = config.icon;
					const count = specCounts[config.id as keyof typeof specCounts];

					return (
						<motion.div
							key={config.id}
							initial={{ opacity: 0, y: 10 }}
							animate={{ opacity: 1, y: 0 }}
							transition={{ delay: index * 0.05 }}
						>
							<Card
								className={cn(
									"cursor-pointer hover:shadow-md transition-all hover:border-primary/30",
									count === 0 && "opacity-60",
								)}
								onClick={() => onViewSpec?.(config.id, "")}
							>
								<CardContent className="p-4">
									<div className="flex items-center justify-between mb-2">
										<div
											className={cn("p-2 rounded-lg", config.bg, config.color)}
										>
											<Icon className="w-4 h-4" />
										</div>
										{count > 0 && (
											<Badge variant="secondary" className="text-xs">
												{count}
											</Badge>
										)}
									</div>
									<h3 className="font-semibold text-sm">{config.label}</h3>
									<p className="text-xs text-muted-foreground line-clamp-1">
										{config.description}
									</p>
								</CardContent>
							</Card>
						</motion.div>
					);
				})}
			</div>

			{/* Quality Metrics Row */}
			<div className="grid gap-4 md:grid-cols-4">
				<Card>
					<CardContent className="p-4">
						<div className="flex items-center justify-between">
							<div>
								<p className="text-sm text-muted-foreground">
									Requirement Quality
								</p>
								<p className="text-2xl font-bold">
									{avgQualityScore.toFixed(0)}%
								</p>
							</div>
							<div
								className={cn(
									"p-2 rounded-full",
									avgQualityScore >= 80
										? "bg-green-500/10 text-green-600"
										: (avgQualityScore >= 60
											? "bg-yellow-500/10 text-yellow-600"
											: "bg-red-500/10 text-red-600"),
								)}
							>
								{avgQualityScore >= 80 ? (
									<TrendingUp className="w-5 h-5" />
								) : (avgQualityScore >= 60 ? (
									<Target className="w-5 h-5" />
								) : (
									<TrendingDown className="w-5 h-5" />
								))}
							</div>
						</div>
						<Progress
							value={avgQualityScore}
							className={cn(
								"h-1 mt-3",
								avgQualityScore < 60 && "[&>div]:bg-red-500",
							)}
						/>
					</CardContent>
				</Card>

				<Card>
					<CardContent className="p-4">
						<div className="flex items-center justify-between">
							<div>
								<p className="text-sm text-muted-foreground">Test Pass Rate</p>
								<p className="text-2xl font-bold">{testPassRate.toFixed(0)}%</p>
							</div>
							<div
								className={cn(
									"p-2 rounded-full",
									testPassRate >= 90
										? "bg-green-500/10 text-green-600"
										: (testPassRate >= 70
											? "bg-yellow-500/10 text-yellow-600"
											: "bg-red-500/10 text-red-600"),
								)}
							>
								<CheckCircle2 className="w-5 h-5" />
							</div>
						</div>
						<Progress
							value={testPassRate}
							className={cn(
								"h-1 mt-3",
								testPassRate < 70 && "[&>div]:bg-red-500",
							)}
						/>
					</CardContent>
				</Card>

				<Card>
					<CardContent className="p-4">
						<div className="flex items-center justify-between">
							<div>
								<p className="text-sm text-muted-foreground">Test Flakiness</p>
								<p className="text-2xl font-bold">{avgFlakiness.toFixed(1)}%</p>
							</div>
							<div
								className={cn(
									"p-2 rounded-full",
									avgFlakiness <= 5
										? "bg-green-500/10 text-green-600"
										: (avgFlakiness <= 15
											? "bg-yellow-500/10 text-yellow-600"
											: "bg-red-500/10 text-red-600"),
								)}
							>
								<RefreshCw className="w-5 h-5" />
							</div>
						</div>
						<p className="text-xs text-muted-foreground mt-2">
							{avgFlakiness <= 5
								? "Stable tests"
								: (avgFlakiness <= 15
									? "Some flaky tests"
									: "High flakiness detected")}
						</p>
					</CardContent>
				</Card>

				<Card>
					<CardContent className="p-4">
						<div className="flex items-center justify-between">
							<div>
								<p className="text-sm text-muted-foreground">Open Defects</p>
								<p className="text-2xl font-bold">{openDefects.length}</p>
							</div>
							<div
								className={cn(
									"p-2 rounded-full",
									criticalDefects.length > 0
										? "bg-red-500/10 text-red-600"
										: (openDefects.length > 5
											? "bg-yellow-500/10 text-yellow-600"
											: "bg-green-500/10 text-green-600"),
								)}
							>
								{criticalDefects.length > 0 ? (
									<XCircle className="w-5 h-5" />
								) : (
									<Bug className="w-5 h-5" />
								)}
							</div>
						</div>
						{criticalDefects.length > 0 && (
							<Badge variant="destructive" className="mt-2 text-xs">
								{criticalDefects.length} critical
							</Badge>
						)}
					</CardContent>
				</Card>
			</div>

			{/* Main Tabs with Spec Lists */}
			<Tabs defaultValue="requirements" className="w-full">
				<TabsList className="w-full justify-start flex-wrap h-auto gap-1 bg-muted/50 p-1">
					{specTypeConfig.map((config) => {
						const Icon = config.icon;
						const count = specCounts[config.id as keyof typeof specCounts];
						return (
							<TabsTrigger
								key={config.id}
								value={config.id}
								className="gap-1.5 text-xs"
							>
								<Icon className="w-3.5 h-3.5" />
								{config.label}
								{count > 0 && (
									<Badge variant="secondary" className="text-[10px] px-1.5">
										{count}
									</Badge>
								)}
							</TabsTrigger>
						);
					})}
					<TabsTrigger value="insights" className="gap-1.5 text-xs ml-auto">
						<AlertTriangle className="w-3.5 h-3.5" />
						Quality Insights
					</TabsTrigger>
				</TabsList>

				{/* Requirements Tab */}
				<TabsContent value="requirement" className="pt-4">
					<SpecListView
						title="Requirement Specifications"
						specs={reqSpecs}
						renderCard={(spec) => (
							<RequirementSpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("requirement", spec.id)}
							/>
						)}
						emptyMessage="No requirement specifications yet"
						onCreateSpec={() => onCreateSpec?.("requirement")}
					/>
				</TabsContent>

				{/* Tests Tab */}
				<TabsContent value="test" className="pt-4">
					<SpecListView
						title="Test Specifications"
						specs={testSpecs}
						renderCard={(spec) => (
							<TestSpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("test", spec.id)}
							/>
						)}
						emptyMessage="No test specifications yet"
						onCreateSpec={() => onCreateSpec?.("test")}
					/>
				</TabsContent>

				{/* Epics Tab */}
				<TabsContent value="epic" className="pt-4">
					<SpecListView
						title="Epic Specifications"
						specs={epicSpecs}
						renderCard={(spec) => (
							<EpicSpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("epic", spec.id)}
							/>
						)}
						emptyMessage="No epic specifications yet"
						onCreateSpec={() => onCreateSpec?.("epic")}
					/>
				</TabsContent>

				{/* User Stories Tab */}
				<TabsContent value="user_story" className="pt-4">
					<SpecListView
						title="User Story Specifications"
						specs={storySpecs}
						renderCard={(spec) => (
							<UserStorySpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("user_story", spec.id)}
							/>
						)}
						emptyMessage="No user story specifications yet"
						onCreateSpec={() => onCreateSpec?.("user_story")}
					/>
				</TabsContent>

				{/* Tasks Tab */}
				<TabsContent value="task" className="pt-4">
					<SpecListView
						title="Task Specifications"
						specs={taskSpecs}
						renderCard={(spec) => (
							<TaskSpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("task", spec.id)}
							/>
						)}
						emptyMessage="No task specifications yet"
						onCreateSpec={() => onCreateSpec?.("task")}
					/>
				</TabsContent>

				{/* Defects Tab */}
				<TabsContent value="defect" className="pt-4">
					<SpecListView
						title="Defect Specifications"
						specs={defectSpecs}
						renderCard={(spec) => (
							<DefectSpecCard
								key={spec.id}
								spec={spec}
								compact
								onClick={() => onViewSpec?.("defect", spec.id)}
							/>
						)}
						emptyMessage="No defect specifications yet"
						onCreateSpec={() => onCreateSpec?.("defect")}
					/>
				</TabsContent>

				{/* Quality Insights Tab */}
				<TabsContent value="insights" className="pt-4">
					<div className="grid gap-6 lg:grid-cols-2">
						{/* Unverified Requirements */}
						<Card>
							<CardHeader>
								<CardTitle className="flex items-center gap-2 text-base">
									<AlertTriangle className="w-4 h-4 text-yellow-500" />
									Unverified Requirements
								</CardTitle>
								<CardDescription>
									Requirements awaiting verification
								</CardDescription>
							</CardHeader>
							<CardContent>
								{unverifiedReqs.length > 0 ? (
									<div className="space-y-2">
										{unverifiedReqs.slice(0, 5).map((req) => (
											<div
												key={req.id}
												className="flex items-center justify-between p-2 rounded-lg bg-muted/30 hover:bg-muted/50 cursor-pointer"
												onClick={() => onViewSpec?.("requirement", req.id)}
											>
												<div className="flex-1 min-w-0">
													<p className="text-sm font-medium truncate">
														{req.requirement_type} - {req.item_id}
													</p>
													<p className="text-xs text-muted-foreground">
														Quality:{" "}
														{(req.overall_quality_score ?? 0).toFixed(0)}%
													</p>
												</div>
												<ArrowRight className="w-4 h-4 text-muted-foreground" />
											</div>
										))}
										{unverifiedReqs.length > 5 && (
											<p className="text-xs text-muted-foreground text-center pt-2">
												+{unverifiedReqs.length - 5} more unverified
											</p>
										)}
									</div>
								) : (
									<div className="flex flex-col items-center justify-center py-8 text-center">
										<CheckCircle2 className="w-8 h-8 text-green-500 mb-2" />
										<p className="text-sm text-muted-foreground">
											All requirements verified
										</p>
									</div>
								)}
							</CardContent>
						</Card>

						{/* High Risk Requirements */}
						<Card>
							<CardHeader>
								<CardTitle className="flex items-center gap-2 text-base">
									<AlertTriangle className="w-4 h-4 text-red-500" />
									High Risk Requirements
								</CardTitle>
								<CardDescription>
									Requirements with elevated risk levels
								</CardDescription>
							</CardHeader>
							<CardContent>
								{highRiskReqs.length > 0 ? (
									<div className="space-y-2">
										{highRiskReqs.slice(0, 5).map((req) => (
											<div
												key={req.id}
												className="flex items-center justify-between p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 cursor-pointer border border-red-500/20"
												onClick={() => onViewSpec?.("requirement", req.id)}
											>
												<div className="flex-1 min-w-0">
													<p className="text-sm font-medium truncate">
														{req.requirement_type} - {req.item_id}
													</p>
													<Badge
														variant="destructive"
														className="text-[10px] mt-1"
													>
														{req.risk_level} risk
													</Badge>
												</div>
												<ArrowRight className="w-4 h-4 text-muted-foreground" />
											</div>
										))}
										{highRiskReqs.length > 5 && (
											<p className="text-xs text-muted-foreground text-center pt-2">
												+{highRiskReqs.length - 5} more high-risk
											</p>
										)}
									</div>
								) : (
									<div className="flex flex-col items-center justify-center py-8 text-center">
										<CheckCircle2 className="w-8 h-8 text-green-500 mb-2" />
										<p className="text-sm text-muted-foreground">
											No high-risk requirements
										</p>
									</div>
								)}
							</CardContent>
						</Card>
					</div>
				</TabsContent>
			</Tabs>
		</div>
	);
}

// Generic list view for specs
interface SpecListViewProps<T extends { id: string }> {
	title: string;
	specs: T[];
	renderCard: (spec: T) => React.ReactNode;
	emptyMessage: string;
	onCreateSpec: () => void;
}

function SpecListView<T extends { id: string }>({
	specs,
	renderCard,
	emptyMessage,
	onCreateSpec,
}: SpecListViewProps<T>) {
	if (specs.length === 0) {
		return (
			<Card className="p-8 border-2 border-dashed flex flex-col items-center justify-center text-center space-y-4">
				<div className="h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center">
					<FileText className="h-6 w-6 text-muted-foreground" />
				</div>
				<div className="space-y-1">
					<h3 className="font-semibold text-sm">{emptyMessage}</h3>
					<p className="text-xs text-muted-foreground max-w-[300px]">
						Create your first specification to start tracking quality metrics
					</p>
				</div>
				<Button size="sm" onClick={onCreateSpec} className="gap-1">
					<Plus className="w-3.5 h-3.5" />
					Create Specification
				</Button>
			</Card>
		);
	}

	return (
		<div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
			{specs.map((spec) => renderCard(spec))}
		</div>
	);
}
