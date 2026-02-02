/**
 * SpecificationDashboard - Combined overview of specifications
 * Integrates all dashboard components with health score, coverage, and gap analysis
 */

import type { SpecificationSummary } from "@tracertm/types";
import {
	Button,
	Card,
	CardContent,
	CardDescription,
	CardHeader,
	CardTitle,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { motion } from "framer-motion";
import {
	Activity,
	AlertCircle,
	BookOpen,
	CheckCircle2,
	FileText,
	Plus,
	Shield,
	TrendingUp,
} from "lucide-react";
import { useMemo } from "react";
import { cn } from "@/lib/utils";
import { ComplianceGauge } from "../adr/ComplianceGauge";
import { ComplianceGaugeFull } from "./ComplianceGaugeFull";
import { CoverageHeatmap } from "./CoverageHeatmap";
import { GapAnalysis } from "./GapAnalysis";
import { HealthScoreRing } from "./HealthScoreRing";

interface SpecificationDashboardProps {
	summary: SpecificationSummary;
	coverageData?: Array<{
		id: string;
		label: string;
		coverage: number;
		testCases?: number;
		adrs?: number;
		contracts?: number;
		linked?: boolean;
	}>;
	gapItems?: Array<{
		id: string;
		label: string;
		priority: "critical" | "high" | "medium" | "low";
		gapType: "no_tests" | "no_adr" | "no_contract" | "orphaned";
		affectedItems?: number;
		impact?: string;
		suggestion?: string;
		linkedResources?: Array<{
			type: "test_case" | "adr" | "contract";
			id: string;
			label: string;
		}>;
	}>;
	recentActivity?: Array<{
		id: string;
		type: string;
		title: string;
		timestamp: string;
		actor: string;
	}>;
	onNavigate?: (section: string, id?: string) => void;
	onCreateNew?: (type: string) => void;
	onGapAction?: (gap: { id: string; [key: string]: unknown }, resourceType: string) => void;
	className?: string;
}

function getHealthStatus(score: number) {
	if (score >= 90)
		return {
			text: "Excellent",
			color: "text-green-600",
			bg: "bg-green-50 dark:bg-green-900/20",
		};
	if (score >= 70)
		return {
			text: "Good",
			color: "text-blue-600",
			bg: "bg-blue-50 dark:bg-blue-900/20",
		};
	if (score >= 50)
		return {
			text: "Fair",
			color: "text-amber-600",
			bg: "bg-amber-50 dark:bg-amber-900/20",
		};
	return {
		text: "Poor",
		color: "text-red-600",
		bg: "bg-red-50 dark:bg-red-900/20",
	};
}

export function SpecificationDashboard({
	summary,
	coverageData = [],
	gapItems = [],
	recentActivity = [],
	onNavigate,
	onCreateNew,
	onGapAction,
	className,
}: SpecificationDashboardProps) {
	// Calculate coverage stats (for future use in analytics)
	useMemo(() => {
		if (coverageData.length === 0) return null;
		const avgCoverage =
			coverageData.reduce((sum, c) => sum + c.coverage, 0) /
			coverageData.length;
		const fullyCovered = coverageData.filter((c) => c.coverage >= 90).length;
		const uncovered = coverageData.filter((c) => c.coverage === 0).length;
		return { avgCoverage, fullyCovered, uncovered };
	}, [coverageData]);

	const healthStatus = getHealthStatus(summary.healthScore);

	return (
		<motion.div
			className={cn("space-y-6", className)}
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			transition={{ duration: 0.3 }}
		>
			{/* Header with Overall Status */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-3xl font-bold tracking-tight">
						Specifications Dashboard
					</h2>
					<p className="text-muted-foreground mt-1">
						Monitor your ADRs, contracts, features, and test coverage
					</p>
				</div>
				<div className="flex gap-2">
					<Button variant="outline" onClick={() => onCreateNew?.("adr")}>
						<Plus className="w-4 h-4 mr-2" />
						New ADR
					</Button>
					<Button variant="outline" onClick={() => onCreateNew?.("feature")}>
						<Plus className="w-4 h-4 mr-2" />
						New Feature
					</Button>
				</div>
			</div>

			{/* Health Score Overview */}
			<div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
				<Card className="lg:col-span-1 bg-gradient-to-br from-card to-muted/20">
					<CardHeader className="pb-2">
						<CardTitle className="text-sm font-medium uppercase text-muted-foreground">
							Overall Health
						</CardTitle>
					</CardHeader>
					<CardContent className="flex justify-center py-4">
						<ComplianceGauge score={summary.healthScore} size={140} />
					</CardContent>
					<CardContent className="pt-0">
						<motion.div
							className={cn("text-center py-2 rounded-lg", healthStatus.bg)}
							initial={{ opacity: 0 }}
							animate={{ opacity: 1 }}
							transition={{ delay: 0.2 }}
						>
							<p className={cn("text-sm font-medium", healthStatus.color)}>
								{healthStatus.text}
							</p>
						</motion.div>
					</CardContent>
				</Card>

				{/* Summary Cards */}
				<div className="lg:col-span-3 grid grid-cols-3 gap-4">
					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.05 }}
					>
						<Card
							className="cursor-pointer hover:shadow-md transition-shadow"
							onClick={() => onNavigate?.("adrs")}
						>
							<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
								<CardTitle className="text-sm font-medium">ADRs</CardTitle>
								<FileText className="h-4 w-4 text-muted-foreground" />
							</CardHeader>
							<CardContent>
								<div className="text-2xl font-bold">{summary.adrs.total}</div>
								<p className="text-xs text-muted-foreground">
									{summary.adrs.accepted} accepted
								</p>
								<div className="mt-3 flex items-center text-xs">
									<span className="text-muted-foreground mr-2">
										Compliance:
									</span>
									<span
										className={
											summary.adrs.averageCompliance > 80
												? "text-green-500 font-medium"
												: "text-yellow-500 font-medium"
										}
									>
										{Math.round(summary.adrs.averageCompliance)}%
									</span>
								</div>
							</CardContent>
						</Card>
					</motion.div>

					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.1 }}
					>
						<Card
							className="cursor-pointer hover:shadow-md transition-shadow"
							onClick={() => onNavigate?.("contracts")}
						>
							<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
								<CardTitle className="text-sm font-medium">Contracts</CardTitle>
								<Shield className="h-4 w-4 text-muted-foreground" />
							</CardHeader>
							<CardContent>
								<div className="text-2xl font-bold">
									{summary.contracts.total}
								</div>
								<p className="text-xs text-muted-foreground">
									{summary.contracts.active} active
								</p>
								<div className="mt-3 flex items-center text-xs">
									<span className="text-muted-foreground mr-2">Verified:</span>
									<span
										className={
											summary.contracts.verified === summary.contracts.active
												? "text-green-500 font-medium"
												: "text-yellow-500 font-medium"
										}
									>
										{summary.contracts.verified}/{summary.contracts.active}
									</span>
								</div>
							</CardContent>
						</Card>
					</motion.div>

					<motion.div
						initial={{ opacity: 0, y: 10 }}
						animate={{ opacity: 1, y: 0 }}
						transition={{ delay: 0.15 }}
					>
						<Card
							className="cursor-pointer hover:shadow-md transition-shadow"
							onClick={() => onNavigate?.("features")}
						>
							<CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
								<CardTitle className="text-sm font-medium">Features</CardTitle>
								<BookOpen className="h-4 w-4 text-muted-foreground" />
							</CardHeader>
							<CardContent>
								<div className="text-2xl font-bold">
									{summary.features.total}
								</div>
								<p className="text-xs text-muted-foreground">
									{summary.features.scenarios} scenarios
								</p>
								<div className="mt-3 flex items-center text-xs">
									<span className="text-muted-foreground mr-2">Pass Rate:</span>
									<span
										className={
											summary.features.passRate > 90
												? "text-green-500 font-medium"
												: "text-red-500 font-medium"
										}
									>
										{Math.round(summary.features.passRate)}%
									</span>
								</div>
							</CardContent>
						</Card>
					</motion.div>
				</div>
			</div>

			{/* Main Tabs */}
			<Tabs defaultValue="coverage" className="w-full">
				<TabsList className="w-full justify-start">
					<TabsTrigger value="coverage">
						<TrendingUp className="w-4 h-4 mr-2" />
						Coverage
					</TabsTrigger>
					<TabsTrigger value="gaps">
						<AlertCircle className="w-4 h-4 mr-2" />
						Gap Analysis
					</TabsTrigger>
					<TabsTrigger value="health">
						<CheckCircle2 className="w-4 h-4 mr-2" />
						Health Details
					</TabsTrigger>
					<TabsTrigger value="activity">
						<Activity className="w-4 h-4 mr-2" />
						Recent Activity
					</TabsTrigger>
				</TabsList>

				{/* Coverage Tab */}
				<TabsContent value="coverage" className="mt-6">
					{coverageData.length > 0 ? (
						<CoverageHeatmap
							data={coverageData}
							onCellClick={(cell) => onNavigate?.("requirement", cell.id)}
							columns={8}
						/>
					) : (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-12">
								<TrendingUp className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>No coverage data available</p>
							</CardContent>
						</Card>
					)}
				</TabsContent>

				{/* Gap Analysis Tab */}
				<TabsContent value="gaps" className="mt-6">
					{gapItems.length > 0 ? (
						<GapAnalysis
							items={gapItems}
							onItemClick={(item) => onNavigate?.("gap", item.id)}
							onCreateLink={(gap, resourceType) =>
								onGapAction?.(gap, resourceType)
							}
						/>
					) : (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-12">
								<CheckCircle2 className="h-12 w-12 mx-auto mb-3 opacity-20 text-green-500" />
								<p className="text-green-600 font-medium">
									No gaps detected - excellent coverage!
								</p>
							</CardContent>
						</Card>
					)}
				</TabsContent>

				{/* Health Details Tab */}
				<TabsContent value="health" className="mt-6">
					<div className="grid gap-6 lg:grid-cols-2">
						{/* Health Score Ring */}
						<Card>
							<CardHeader>
								<CardTitle>Health Breakdown</CardTitle>
								<CardDescription>Score by category</CardDescription>
							</CardHeader>
							<CardContent className="flex justify-center py-6">
								<HealthScoreRing
									score={summary.healthScore}
									size={250}
									showAnimation={true}
									showLegend={true}
								/>
							</CardContent>
						</Card>

						{/* Full Gauge */}
						<Card>
							<CardHeader>
								<CardTitle>Compliance Gauge</CardTitle>
								<CardDescription>Overall compliance status</CardDescription>
							</CardHeader>
							<CardContent className="flex justify-center py-6">
								<ComplianceGaugeFull
									score={summary.healthScore}
									size={180}
									showAnimation={true}
									label="Compliance"
								/>
							</CardContent>
						</Card>
					</div>

					{/* Detailed Issues */}
					<div className="mt-6 space-y-4">
						<h3 className="text-lg font-semibold">Issues by Category</h3>
						<div className="grid gap-4 md:grid-cols-2">
							{summary.healthDetails.map((detail: { category: string; score: number; issues: string[] }, i: number) => (
								<motion.div
									key={i}
									initial={{ opacity: 0, y: 10 }}
									animate={{ opacity: 1, y: 0 }}
									transition={{ delay: i * 0.1 }}
								>
									<Card>
										<CardHeader className="pb-3">
											<div className="flex justify-between items-start">
												<div>
													<CardTitle className="text-base">
														{detail.category}
													</CardTitle>
													<CardDescription>
														Score: {detail.score}
														/100
													</CardDescription>
												</div>
												<motion.span
													className={cn(
														"text-lg font-bold px-3 py-1 rounded-full",
														detail.score >= 80
															? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200"
															: detail.score >= 60
																? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200"
																: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200",
													)}
													initial={{ scale: 0 }}
													animate={{ scale: 1 }}
													transition={{
														type: "spring",
													}}
												>
													{detail.score}%
												</motion.span>
											</div>
										</CardHeader>
										<CardContent>
											{detail.issues.length > 0 ? (
												<ul className="space-y-2">
													{detail.issues.map((issue: string, j: number) => (
														<li
															key={j}
															className="text-sm text-muted-foreground flex items-start gap-2"
														>
															<AlertCircle className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5" />
															{issue}
														</li>
													))}
												</ul>
											) : (
												<div className="flex items-center gap-2 text-sm text-green-600">
													<CheckCircle2 className="w-4 h-4 shrink-0" />
													No issues detected
												</div>
											)}
										</CardContent>
									</Card>
								</motion.div>
							))}
						</div>
					</div>
				</TabsContent>

				{/* Activity Tab */}
				<TabsContent value="activity" className="mt-6">
					{recentActivity.length > 0 ? (
						<Card>
							<CardHeader>
								<CardTitle>Recent Activity</CardTitle>
								<CardDescription>
									Latest updates to specifications
								</CardDescription>
							</CardHeader>
							<CardContent>
								<div className="space-y-4">
									{recentActivity.map((activity, idx) => (
										<motion.div
											key={activity.id}
											className="flex gap-4 pb-4 border-b border-border/50 last:border-0 last:pb-0"
											initial={{
												opacity: 0,
												x: -10,
											}}
											animate={{
												opacity: 1,
												x: 0,
											}}
											transition={{
												delay: idx * 0.05,
											}}
										>
											<div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center shrink-0 mt-0.5">
												<Activity className="w-4 h-4 text-muted-foreground" />
											</div>
											<div className="flex-1 min-w-0">
												<p className="font-medium text-sm">{activity.title}</p>
												<p className="text-xs text-muted-foreground mt-0.5">
													by{" "}
													<span className="font-medium">{activity.actor}</span>{" "}
													· {new Date(activity.timestamp).toLocaleDateString()}
												</p>
											</div>
										</motion.div>
									))}
								</div>
							</CardContent>
						</Card>
					) : (
						<Card>
							<CardContent className="pt-6 text-center text-muted-foreground py-12">
								<Activity className="h-12 w-12 mx-auto mb-3 opacity-20" />
								<p>No recent activity yet. Create your first specification!</p>
							</CardContent>
						</Card>
					)}
				</TabsContent>
			</Tabs>
		</motion.div>
	);
}
