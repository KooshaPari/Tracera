import { useParams } from "@tanstack/react-router";
import type { TestItem } from "@tracertm/types";
import { isTestItem } from "@tracertm/types";
import {
	Badge,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Progress,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { format } from "date-fns";
import {
	Activity,
	AlertTriangle,
	Ban,
	BarChart3,
	CheckCircle2,
	Clock,
	FileCode,
	History,
	Link2,
	PlayCircle,
	Shield,
	TestTube2,
	TrendingUp,
	XCircle,
} from "lucide-react";
import { useMemo } from "react";
import { useTestSpecByItem } from "@/hooks/useItemSpecs";
import { cn } from "@/lib/utils";

interface TestDetailViewProps {
	item: TestItem;
	projectId: string;
}

// Safety level colors and metadata
const SAFETY_LEVELS = {
	safe: {
		color: "bg-green-500/10 text-green-600 border-green-500/30",
		icon: Shield,
		label: "Safe",
	},
	quarantined: {
		color: "bg-yellow-500/10 text-yellow-600 border-yellow-500/30",
		icon: AlertTriangle,
		label: "Quarantined",
	},
	disabled: {
		color: "bg-red-500/10 text-red-600 border-red-500/30",
		icon: Ban,
		label: "Disabled",
	},
} as const;

// Test result status colors
const TEST_RESULT_COLORS = {
	passed: "bg-green-500/15 text-green-700",
	failed: "bg-red-500/15 text-red-700",
	skipped: "bg-slate-500/15 text-slate-700",
	blocked: "bg-orange-500/15 text-orange-700",
	error: "bg-red-600/15 text-red-800",
	flaky: "bg-yellow-500/15 text-yellow-700",
	timeout: "bg-purple-500/15 text-purple-700",
} as const;

// DO-178C safety levels
const DO178C_LEVELS = {
	A: { label: "Level A (Catastrophic)", color: "text-red-600" },
	B: { label: "Level B (Hazardous)", color: "text-orange-600" },
	C: { label: "Level C (Major)", color: "text-yellow-600" },
	D: { label: "Level D (Minor)", color: "text-blue-600" },
	E: { label: "Level E (No Effect)", color: "text-green-600" },
};

export function TestDetailView({ item, projectId }: TestDetailViewProps) {
	const params = useParams({ strict: false });

	// Fetch test spec data (must be called unconditionally)
	const { data: testSpec, isLoading: specLoading } = useTestSpecByItem(
		projectId,
		item.id,
	);

	// Compute derived values (hooks must be called unconditionally)
	const safetyLevel = useMemo(() => {
		if (testSpec?.is_quarantined) return "quarantined";
		return "safe";
	}, [testSpec?.is_quarantined]);

	const flakinessScore = testSpec?.flakiness_score ?? 0;
	const isFlakyTest = flakinessScore > 30;
	const flakinessColor = useMemo(() => {
		if (flakinessScore > 30) return "text-red-600";
		if (flakinessScore > 10) return "text-yellow-600";
		return "text-green-600";
	}, [flakinessScore]);

	const coveragePercent = useMemo(() => {
		if (!testSpec) return 0;
		return testSpec.line_coverage ?? 0;
	}, [testSpec]);

	const passRate = useMemo(() => {
		if (!testSpec || testSpec.total_runs === 0) return 0;
		return Math.round((testSpec.pass_count / testSpec.total_runs) * 100);
	}, [testSpec]);

	// Type guard check
	if (!isTestItem(item)) {
		return (
			<div className="p-6">
				<Card className="border-yellow-500/50 bg-yellow-500/10">
					<CardContent className="pt-6">
						<div className="flex items-center gap-2 text-yellow-700">
							<AlertTriangle className="h-5 w-5" />
							<p className="font-medium">
								This item is not a test. Expected test, test_case, or test_suite
								type.
							</p>
						</div>
					</CardContent>
				</Card>
			</div>
		);
	}

	const safetyConfig = SAFETY_LEVELS[safetyLevel];
	const SafetyIcon = safetyConfig.icon;

	return (
		<div className="space-y-6">
			{/* Quarantine Warning Banner */}
			{testSpec?.is_quarantined && (
				<Card className="border-yellow-500/50 bg-yellow-500/10">
					<CardContent className="pt-6">
						<div className="flex items-start gap-3">
							<AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
							<div className="flex-1">
								<h4 className="font-semibold text-yellow-800">
									Test Quarantined
								</h4>
								<p className="text-sm text-yellow-700 mt-1">
									{testSpec.quarantine_reason ||
										"This test is unstable and has been quarantined."}
								</p>
								{testSpec.quarantined_at && (
									<p className="text-xs text-yellow-600 mt-2">
										Quarantined on{" "}
										{format(new Date(testSpec.quarantined_at), "MMM d, yyyy")}
									</p>
								)}
							</div>
						</div>
					</CardContent>
				</Card>
			)}

			<Tabs defaultValue="overview" className="w-full">
				<TabsList className="grid w-full grid-cols-6">
					<TabsTrigger value="overview">Overview</TabsTrigger>
					<TabsTrigger value="spec">Test Spec</TabsTrigger>
					<TabsTrigger value="execution">Execution</TabsTrigger>
					<TabsTrigger value="metrics">Metrics</TabsTrigger>
					<TabsTrigger value="links">Links</TabsTrigger>
					<TabsTrigger value="history">History</TabsTrigger>
				</TabsList>

				{/* Overview Tab */}
				<TabsContent value="overview" className="space-y-6">
					<Card className="border-none bg-card/50">
						<CardHeader>
							<CardTitle className="text-base flex items-center gap-2">
								<TestTube2 className="h-4 w-4 text-green-600" />
								Basic Information
							</CardTitle>
						</CardHeader>
						<CardContent className="space-y-4">
							<div className="grid grid-cols-2 gap-4">
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
										Title
									</p>
									<p className="font-medium">{item.title}</p>
								</div>
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
										Owner
									</p>
									<p className="font-medium">{item.owner || "Unassigned"}</p>
								</div>
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
										Created
									</p>
									<p className="text-sm">
										{format(new Date(item.createdAt), "MMM d, yyyy")}
									</p>
								</div>
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
										Updated
									</p>
									<p className="text-sm">
										{format(new Date(item.updatedAt), "MMM d, yyyy HH:mm")}
									</p>
								</div>
							</div>

							{item.description && (
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
										Description
									</p>
									<p className="text-sm leading-relaxed">{item.description}</p>
								</div>
							)}
						</CardContent>
					</Card>
				</TabsContent>

				{/* Test Specification Tab */}
				<TabsContent value="spec" className="space-y-6">
					{specLoading ? (
						<Card className="border-none bg-card/50">
							<CardContent className="pt-6">
								<p className="text-sm text-muted-foreground">
									Loading specification...
								</p>
							</CardContent>
						</Card>
					) : !testSpec ? (
						<Card className="border-none bg-card/50">
							<CardContent className="pt-6">
								<p className="text-sm text-muted-foreground">
									No test specification data available
								</p>
							</CardContent>
						</Card>
					) : (
						<>
							{/* Test Configuration */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<FileCode className="h-4 w-4" />
										Test Configuration
									</CardTitle>
								</CardHeader>
								<CardContent className="space-y-4">
									<div className="grid grid-cols-2 md:grid-cols-3 gap-4">
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Test Type
											</p>
											<Badge
												variant="outline"
												className="bg-green-500/10 text-green-600 border-green-500/30"
											>
												{testSpec.test_type || "Not specified"}
											</Badge>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Framework
											</p>
											<p className="text-sm font-medium">
												{testSpec.test_framework || "Not specified"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Language
											</p>
											<p className="text-sm font-medium">
												{(testSpec.spec_metadata?.language as string) ||
													"Not specified"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Oracle Type
											</p>
											<p className="text-sm font-medium">
												{(testSpec.spec_metadata?.oracle_type as string) ||
													"Not specified"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Coverage Type
											</p>
											<p className="text-sm font-medium">
												{(testSpec.spec_metadata?.coverage_type as string) ||
													"Not specified"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Expected Duration
											</p>
											<p className="text-sm font-medium">
												{testSpec.performance_baseline_ms
													? `${testSpec.performance_baseline_ms}ms`
													: "Not specified"}
											</p>
										</div>
									</div>

									{/* Safety Level */}
									<div className="border-t pt-4">
										<p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
											Safety Level
										</p>
										<div className="flex items-center gap-2">
											<Badge className={safetyConfig.color}>
												<SafetyIcon className="h-3.5 w-3.5 mr-1.5" />
												{safetyConfig.label}
											</Badge>
											{testSpec.spec_metadata?.do178c_level && (
												<Badge
													variant="outline"
													className={cn(
														DO178C_LEVELS[
															testSpec.spec_metadata
																.do178c_level as keyof typeof DO178C_LEVELS
														]?.color,
													)}
												>
													DO-178C{" "}
													{
														DO178C_LEVELS[
															testSpec.spec_metadata
																.do178c_level as keyof typeof DO178C_LEVELS
														]?.label
													}
												</Badge>
											)}
										</div>
									</div>

									{/* Critical Path */}
									{testSpec.spec_metadata?.is_critical_path && (
										<div className="border-t pt-4">
											<div className="flex items-center gap-2 text-red-600">
												<AlertTriangle className="h-4 w-4" />
												<p className="text-sm font-semibold">
													Critical Path Test
												</p>
											</div>
										</div>
									)}

									{/* File Path */}
									{testSpec.test_file_path && (
										<div className="border-t pt-4">
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Test File
											</p>
											<code className="text-xs bg-muted px-2 py-1 rounded">
												{testSpec.test_file_path}
											</code>
										</div>
									)}
								</CardContent>
							</Card>

							{/* Dependencies */}
							{(testSpec.required_services.length > 0 ||
								testSpec.mocked_dependencies.length > 0) && (
								<Card className="border-none bg-card/50">
									<CardHeader>
										<CardTitle className="text-base">Dependencies</CardTitle>
									</CardHeader>
									<CardContent className="space-y-3">
										{testSpec.required_services.length > 0 && (
											<div>
												<p className="text-xs text-muted-foreground mb-2">
													Required Services
												</p>
												<div className="flex flex-wrap gap-2">
													{testSpec.required_services.map((service) => (
														<Badge key={service} variant="secondary">
															{service}
														</Badge>
													))}
												</div>
											</div>
										)}
										{testSpec.mocked_dependencies.length > 0 && (
											<div>
												<p className="text-xs text-muted-foreground mb-2">
													Mocked Dependencies
												</p>
												<div className="flex flex-wrap gap-2">
													{testSpec.mocked_dependencies.map((dep) => (
														<Badge key={dep} variant="outline">
															{dep}
														</Badge>
													))}
												</div>
											</div>
										)}
									</CardContent>
								</Card>
							)}
						</>
					)}
				</TabsContent>

				{/* Execution Tab */}
				<TabsContent value="execution" className="space-y-6">
					{!testSpec ? (
						<Card className="border-none bg-card/50">
							<CardContent className="pt-6">
								<p className="text-sm text-muted-foreground">
									No execution data available
								</p>
							</CardContent>
						</Card>
					) : (
						<>
							{/* Last Run Status */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<PlayCircle className="h-4 w-4" />
										Last Execution
									</CardTitle>
								</CardHeader>
								<CardContent className="space-y-4">
									<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Status
											</p>
											{testSpec.last_run_status ? (
												<Badge
													className={
														TEST_RESULT_COLORS[testSpec.last_run_status]
													}
												>
													{testSpec.last_run_status === "passed" && (
														<CheckCircle2 className="h-3.5 w-3.5 mr-1" />
													)}
													{testSpec.last_run_status === "failed" && (
														<XCircle className="h-3.5 w-3.5 mr-1" />
													)}
													{testSpec.last_run_status === "skipped" && (
														<Clock className="h-3.5 w-3.5 mr-1" />
													)}
													{testSpec.last_run_status === "error" && (
														<AlertTriangle className="h-3.5 w-3.5 mr-1" />
													)}
													{testSpec.last_run_status}
												</Badge>
											) : (
												<p className="text-sm text-muted-foreground">
													Never run
												</p>
											)}
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Duration
											</p>
											<p className="text-sm font-medium">
												{testSpec.last_run_duration_ms
													? `${testSpec.last_run_duration_ms}ms`
													: "—"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Timestamp
											</p>
											<p className="text-sm">
												{testSpec.last_run_at
													? format(
															new Date(testSpec.last_run_at),
															"MMM d, HH:mm",
														)
													: "—"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Flakiness
											</p>
											<div className="flex items-center gap-2">
												<Activity className={cn("h-4 w-4", flakinessColor)} />
												<span
													className={cn(
														"text-sm font-semibold",
														flakinessColor,
													)}
												>
													{flakinessScore}%
												</span>
											</div>
										</div>
									</div>

									{testSpec.last_run_error && (
										<div className="border-t pt-4">
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
												Error Message
											</p>
											<div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
												<code className="text-xs text-red-700">
													{testSpec.last_run_error}
												</code>
											</div>
										</div>
									)}
								</CardContent>
							</Card>

							{/* Flakiness Indicator */}
							{isFlakyTest && (
								<Card className="border-yellow-500/50 bg-yellow-500/10">
									<CardContent className="pt-6">
										<div className="flex items-start gap-3">
											<Activity className="h-5 w-5 text-yellow-600 flex-shrink-0" />
											<div className="flex-1">
												<h4 className="font-semibold text-yellow-800">
													High Flakiness Detected
												</h4>
												<p className="text-sm text-yellow-700 mt-1">
													This test has a flakiness score of {flakinessScore}%,
													which is above the recommended threshold of 30%.
												</p>
												{testSpec.flaky_patterns.length > 0 && (
													<div className="mt-3">
														<p className="text-xs text-yellow-600 uppercase tracking-wider mb-1">
															Flaky Patterns
														</p>
														<ul className="text-sm text-yellow-700 list-disc list-inside space-y-1">
															{testSpec.flaky_patterns.map((pattern, idx) => (
																<li key={idx}>{pattern}</li>
															))}
														</ul>
													</div>
												)}
											</div>
										</div>
									</CardContent>
								</Card>
							)}

							{/* Test Steps */}
							{item.testSteps && item.testSteps.length > 0 && (
								<Card className="border-none bg-card/50">
									<CardHeader>
										<CardTitle className="text-base">Test Steps</CardTitle>
									</CardHeader>
									<CardContent>
										<div className="space-y-3">
											{item.testSteps.map((step) => (
												<div
													key={step.stepNumber}
													className="border-l-2 border-green-500/30 pl-4"
												>
													<div className="flex items-start gap-2">
														<span className="text-xs font-bold text-green-600">
															Step {step.stepNumber}
														</span>
													</div>
													<p className="text-sm mt-1">{step.action}</p>
													{step.expectedResult && (
														<p className="text-xs text-muted-foreground mt-1">
															Expected: {step.expectedResult}
														</p>
													)}
												</div>
											))}
										</div>
									</CardContent>
								</Card>
							)}

							{/* Expected vs Actual */}
							{item.expectedResult && (
								<Card className="border-none bg-card/50">
									<CardHeader>
										<CardTitle className="text-base">
											Expected vs Actual Results
										</CardTitle>
									</CardHeader>
									<CardContent className="space-y-3">
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Expected
											</p>
											<p className="text-sm">{item.expectedResult}</p>
										</div>
										{testSpec.last_run_error && (
											<div>
												<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
													Actual (Last Run)
												</p>
												<p className="text-sm text-red-600">
													{testSpec.last_run_error}
												</p>
											</div>
										)}
									</CardContent>
								</Card>
							)}
						</>
					)}
				</TabsContent>

				{/* Metrics Tab */}
				<TabsContent value="metrics" className="space-y-6">
					{!testSpec ? (
						<Card className="border-none bg-card/50">
							<CardContent className="pt-6">
								<p className="text-sm text-muted-foreground">
									No metrics available
								</p>
							</CardContent>
						</Card>
					) : (
						<>
							{/* Coverage */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<BarChart3 className="h-4 w-4" />
										Coverage Metrics
									</CardTitle>
								</CardHeader>
								<CardContent className="space-y-4">
									<div className="space-y-3">
										<div>
											<div className="flex items-center justify-between mb-2">
												<p className="text-sm font-medium">Line Coverage</p>
												<p className="text-sm font-bold text-green-600">
													{coveragePercent}%
												</p>
											</div>
											<Progress value={coveragePercent} className="h-2" />
										</div>

										{testSpec.branch_coverage !== undefined &&
											testSpec.branch_coverage !== null && (
												<div>
													<div className="flex items-center justify-between mb-2">
														<p className="text-sm font-medium">
															Branch Coverage
														</p>
														<p className="text-sm font-bold text-blue-600">
															{testSpec.branch_coverage}%
														</p>
													</div>
													<Progress
														value={testSpec.branch_coverage}
														className="h-2"
													/>
												</div>
											)}

										{testSpec.mutation_score !== undefined &&
											testSpec.mutation_score !== null && (
												<div>
													<div className="flex items-center justify-between mb-2">
														<p className="text-sm font-medium">
															Mutation Score
														</p>
														<p className="text-sm font-bold text-purple-600">
															{testSpec.mutation_score}%
														</p>
													</div>
													<Progress
														value={testSpec.mutation_score}
														className="h-2"
													/>
												</div>
											)}

										{testSpec.mcdc_coverage !== undefined &&
											testSpec.mcdc_coverage !== null && (
												<div>
													<div className="flex items-center justify-between mb-2">
														<p className="text-sm font-medium">
															MC/DC Coverage
														</p>
														<p className="text-sm font-bold text-indigo-600">
															{testSpec.mcdc_coverage}%
														</p>
													</div>
													<Progress
														value={testSpec.mcdc_coverage}
														className="h-2"
													/>
												</div>
											)}
									</div>
								</CardContent>
							</Card>

							{/* Execution Stats */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<TrendingUp className="h-4 w-4" />
										Execution Statistics
									</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Total Runs
											</p>
											<p className="text-2xl font-bold">
												{testSpec.total_runs}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Pass Rate
											</p>
											<p className="text-2xl font-bold text-green-600">
												{passRate}%
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Passed
											</p>
											<p className="text-2xl font-bold text-green-600">
												{testSpec.pass_count}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Failed
											</p>
											<p className="text-2xl font-bold text-red-600">
												{testSpec.fail_count}
											</p>
										</div>
									</div>
								</CardContent>
							</Card>

							{/* Execution Time Trends */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base">
										Execution Time Trends
									</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Average
											</p>
											<p className="text-sm font-medium">
												{testSpec.avg_duration_ms
													? `${testSpec.avg_duration_ms}ms`
													: "—"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												P50
											</p>
											<p className="text-sm font-medium">
												{testSpec.p50_duration_ms
													? `${testSpec.p50_duration_ms}ms`
													: "—"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												P95
											</p>
											<p className="text-sm font-medium">
												{testSpec.p95_duration_ms
													? `${testSpec.p95_duration_ms}ms`
													: "—"}
											</p>
										</div>
										<div>
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												P99
											</p>
											<p className="text-sm font-medium">
												{testSpec.p99_duration_ms
													? `${testSpec.p99_duration_ms}ms`
													: "—"}
											</p>
										</div>
									</div>
									{testSpec.duration_trend && (
										<div className="mt-4">
											<p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
												Trend
											</p>
											<Badge variant="outline">{testSpec.duration_trend}</Badge>
										</div>
									)}
								</CardContent>
							</Card>

							{/* Flakiness Trend */}
							<Card className="border-none bg-card/50">
								<CardHeader>
									<CardTitle className="text-base flex items-center gap-2">
										<Activity className={cn("h-4 w-4", flakinessColor)} />
										Flakiness Trend
									</CardTitle>
								</CardHeader>
								<CardContent>
									<div className="flex items-center justify-between mb-3">
										<p className="text-sm text-muted-foreground">
											Current Flakiness Score
										</p>
										<p className={cn("text-3xl font-bold", flakinessColor)}>
											{flakinessScore}%
										</p>
									</div>
									<Progress
										value={flakinessScore}
										className={cn(
											"h-3",
											flakinessScore > 30
												? "[&>*]:bg-red-500"
												: flakinessScore > 10
													? "[&>*]:bg-yellow-500"
													: "[&>*]:bg-green-500",
										)}
									/>
									<p className="text-xs text-muted-foreground mt-2">
										Based on last {testSpec.flakiness_window_runs} runs
									</p>
								</CardContent>
							</Card>
						</>
					)}
				</TabsContent>

				{/* Links Tab */}
				<TabsContent value="links" className="space-y-6">
					<Card className="border-none bg-card/50">
						<CardHeader>
							<CardTitle className="text-base flex items-center gap-2">
								<Link2 className="h-4 w-4" />
								Traceability Links
							</CardTitle>
						</CardHeader>
						<CardContent>
							{testSpec?.verifies_requirements &&
							testSpec.verifies_requirements.length > 0 ? (
								<div>
									<p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">
										Verifies Requirements
									</p>
									<div className="space-y-2">
										{testSpec.verifies_requirements.map((reqId) => (
											<div
												key={reqId}
												className="flex items-center gap-2 p-2 rounded-lg border bg-card/50"
											>
												<CheckCircle2 className="h-4 w-4 text-green-600" />
												<span className="text-sm font-medium">{reqId}</span>
											</div>
										))}
									</div>
								</div>
							) : (
								<p className="text-sm text-muted-foreground">
									No requirement links configured
								</p>
							)}

							{testSpec?.verifies_contracts &&
								testSpec.verifies_contracts.length > 0 && (
									<div className="mt-6">
										<p className="text-xs text-muted-foreground uppercase tracking-wider mb-3">
											Verifies Contracts
										</p>
										<div className="space-y-2">
											{testSpec.verifies_contracts.map((contractId) => (
												<div
													key={contractId}
													className="flex items-center gap-2 p-2 rounded-lg border bg-card/50"
												>
													<FileCode className="h-4 w-4 text-blue-600" />
													<span className="text-sm font-medium">
														{contractId}
													</span>
												</div>
											))}
										</div>
									</div>
								)}
						</CardContent>
					</Card>
				</TabsContent>

				{/* History Tab */}
				<TabsContent value="history" className="space-y-6">
					<Card className="border-none bg-card/50">
						<CardHeader>
							<CardTitle className="text-base flex items-center gap-2">
								<History className="h-4 w-4" />
								Change History
							</CardTitle>
						</CardHeader>
						<CardContent>
							<div className="space-y-4">
								<div className="flex gap-4 pb-4 border-b">
									<div className="flex-shrink-0">
										<Badge variant="secondary">Update</Badge>
									</div>
									<div className="flex-1">
										<p className="font-medium text-sm">Item updated</p>
										<p className="text-xs text-muted-foreground mt-1">
											Version {item.version} ·{" "}
											{format(new Date(item.updatedAt), "MMM d, yyyy HH:mm")}
										</p>
									</div>
								</div>

								<div className="flex gap-4 pb-4 border-b">
									<div className="flex-shrink-0">
										<Badge variant="secondary">Create</Badge>
									</div>
									<div className="flex-1">
										<p className="font-medium text-sm">Item created</p>
										<p className="text-xs text-muted-foreground mt-1">
											Status: {item.status} ·{" "}
											{format(new Date(item.createdAt), "MMM d, yyyy")}
										</p>
									</div>
								</div>

								{testSpec?.is_quarantined && testSpec.quarantined_at && (
									<div className="flex gap-4 pb-4">
										<div className="flex-shrink-0">
											<Badge className="bg-yellow-500/10 text-yellow-600 border-yellow-500/30">
												Quarantine
											</Badge>
										</div>
										<div className="flex-1">
											<p className="font-medium text-sm">Test quarantined</p>
											<p className="text-xs text-muted-foreground mt-1">
												{testSpec.quarantine_reason} ·{" "}
												{format(
													new Date(testSpec.quarantined_at),
													"MMM d, yyyy HH:mm",
												)}
											</p>
										</div>
									</div>
								)}
							</div>
						</CardContent>
					</Card>
				</TabsContent>
			</Tabs>
		</div>
	);
}
