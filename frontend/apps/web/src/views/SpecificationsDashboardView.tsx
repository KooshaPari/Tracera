import { useNavigate, useSearch } from "@tanstack/react-router";
import {
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Skeleton,
} from "@tracertm/ui";
import { FileText, Shield, BookOpen, ArrowRight } from "lucide-react";
import { useMemo } from "react";
import { SpecificationDashboard } from "@/components/specifications/dashboard/SpecificationDashboard";
import { useADRs, useContracts, useFeatures } from "@/hooks/useSpecifications";
import { useItems } from "@/hooks/useItems";
import type { SpecificationSummary } from "@tracertm/types";

interface SpecificationsDashboardViewProps {
	projectId: string;
}

export function SpecificationsDashboardView({
	projectId,
}: SpecificationsDashboardViewProps) {
	const navigate = useNavigate();
	// Search params available for future filtering
	void useSearch({ strict: false });

	// Fetch all specification data
	const { data: adrsData, isLoading: adrsLoading } = useADRs({ projectId });
	const { data: contractsData, isLoading: contractsLoading } = useContracts({
		projectId,
	});
	const { data: featuresData, isLoading: featuresLoading } = useFeatures({
		projectId,
	});
	const { data: itemsData } = useItems({ projectId, limit: 500 });

	const adrs = adrsData?.adrs ?? [];
	const contracts = contractsData?.contracts ?? [];
	const features = featuresData?.features ?? [];
	const items = itemsData?.items ?? [];

	const isLoading = adrsLoading || contractsLoading || featuresLoading;

	const typeDistribution = useMemo(() => {
		if (!items.length) return [];
		const counts = new Map<string, number>();
		for (const item of items) {
			const type = String(item.type || "unknown").toLowerCase();
			counts.set(type, (counts.get(type) || 0) + 1);
		}
		return Array.from(counts.entries())
			.map(([type, count]) => ({ type, count }))
			.sort((a, b) => b.count - a.count);
	}, [items]);

	const totalItems = items.length;

	// Calculate summary metrics
	const summary = useMemo(() => {
		const calculateADRMetrics = () => {
			const total = adrs.length;
			const accepted = adrs.filter((a: any) => a.status === "accepted").length;
			const proposed = adrs.filter((a: any) => a.status === "proposed").length;
			const avgCompliance =
				adrs.length > 0
					? adrs.reduce(
							(sum: number, a: any) => sum + (a.complianceScore || 0),
							0,
						) / adrs.length
					: 0;

			return { total, accepted, proposed, averageCompliance: avgCompliance };
		};

		const calculateContractMetrics = () => {
			const total = contracts.length;
			const active = contracts.filter((c: any) => c.status === "active").length;
			const verified = contracts.filter(
				(c: any) => c.status === "verified",
			).length;
			const violated = contracts.filter(
				(c: any) => c.status === "violated",
			).length;

			return { total, active, verified, violated };
		};

		const calculateFeatureMetrics = () => {
			const total = features.length;
			const totalScenarios = features.reduce(
				(sum: number, f: any) => sum + (f.scenarioCount || 0),
				0,
			);
			const passedScenarios = features.reduce(
				(sum: number, f: any) => sum + (f.passedScenarios || 0),
				0,
			);
			const passRate =
				totalScenarios > 0 ? (passedScenarios / totalScenarios) * 100 : 0;
			const coverage = total > 0 ? passRate : 0;

			return { total, scenarios: totalScenarios, passRate, coverage };
		};

		const calculateHealthScore = () => {
			const adrMetrics = calculateADRMetrics();
			const contractMetrics = calculateContractMetrics();
			const featureMetrics = calculateFeatureMetrics();

			// Simple health calculation: average of compliance areas
			const adrHealth =
				adrMetrics.total > 0 ? adrMetrics.averageCompliance : 100;
			const contractHealth =
				contractMetrics.total > 0
					? (contractMetrics.verified / contractMetrics.active) * 100
					: 100;
			const featureHealth =
				featureMetrics.total > 0 ? featureMetrics.passRate : 100;

			const weights = {
				adr: 0.3,
				contract: 0.35,
				feature: 0.35,
			};

			const health =
				adrHealth * weights.adr +
				contractHealth * weights.contract +
				featureHealth * weights.feature;

			return Math.min(100, Math.max(0, health));
		};

		const adrMetrics = calculateADRMetrics();
		const contractMetrics = calculateContractMetrics();
		const featureMetrics = calculateFeatureMetrics();
		const healthScore = calculateHealthScore();

		// Generate health details
		const healthDetails = [
			{
				category: "Architecture Decisions",
				score: Math.round(adrMetrics.averageCompliance),
				issues:
					adrMetrics.total > 0
						? adrMetrics.accepted < adrMetrics.total / 2
							? ["Less than 50% ADRs accepted"]
							: []
						: ["No ADRs created yet"],
			},
			{
				category: "API Contracts",
				score:
					contractMetrics.total > 0
						? Math.round(
								(contractMetrics.verified / contractMetrics.active) * 100,
							)
						: 100,
				issues:
					contractMetrics.total > 0 &&
					contractMetrics.verified < contractMetrics.active
						? [
								`${contractMetrics.active - contractMetrics.verified} contracts unverified`,
							]
						: contractMetrics.total === 0
							? ["No contracts defined"]
							: [],
			},
			{
				category: "Feature Testing",
				score: Math.round(featureMetrics.passRate),
				issues:
					featureMetrics.total > 0 && featureMetrics.passRate < 80
						? ["Pass rate below 80%", "Pending scenarios detected"]
						: featureMetrics.total === 0
							? ["No features defined"]
							: [],
			},
		];

		const result: SpecificationSummary = {
			projectId,
			healthScore,
			adrs: adrMetrics,
			contracts: contractMetrics,
			features: featureMetrics,
			healthDetails,
		};

		return result;
	}, [adrs, contracts, features]);

	// Generate coverage data
	const coverageData = useMemo(() => {
		const items = [
			...features.map((f: any) => ({
				id: f.id,
				label: f.name,
				coverage:
					f.scenarioCount > 0
						? ((f.passedScenarios + f.pendingScenarios) / f.scenarioCount) * 100
						: 0,
				testCases: f.scenarioCount,
				linked: true,
			})),
			...adrs.slice(0, 5).map((a: any) => ({
				id: a.id,
				label: a.title,
				coverage: a.complianceScore || 0,
				adrs: 1,
				linked: true,
			})),
		];

		return items;
	}, [features, adrs]);

	// Generate gap analysis
	const gapItems = useMemo(() => {
		const gaps: any[] = [];

		// Find features without contracts
		features.forEach((f: any) => {
			if (f.scenarioCount > 0 && f.passRate < 80) {
				gaps.push({
					id: `gap-${f.id}`,
					label: f.name,
					priority: "high" as const,
					gapType: "no_tests" as const,
					affectedItems: 1,
					impact: `${f.failedScenarios} failing scenarios`,
					suggestion: "Review and fix failing test scenarios",
				});
			}
		});

		// Find contracts without tests
		contracts.forEach((c: any) => {
			if (c.status === "violated") {
				gaps.push({
					id: `gap-${c.id}`,
					label: c.title,
					priority: "critical" as const,
					gapType: "no_tests" as const,
					affectedItems: 1,
					impact: "Contract verification failed",
					suggestion: "Run tests and fix contract violations",
				});
			}
		});

		return gaps.slice(0, 5); // Show top 5 gaps
	}, [features, contracts]);

	const handleNavigate = (section: string, _id?: string) => {
		navigate({
			to: "/projects/$projectId/specifications",
			params: { projectId },
			search: { tab: section },
		});
	};

	const handleCreateNew = (type: string) => {
		const tab = type === "adr" ? "adrs" : "features";
		navigate({
			to: "/projects/$projectId/specifications",
			params: { projectId },
			search: { tab, action: "create" },
		});
	};

	if (isLoading) {
		return (
			<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="grid gap-4 md:grid-cols-4">
					{[1, 2, 3, 4].map((i) => (
						<Skeleton key={i} className="h-32 rounded-xl" />
					))}
				</div>
				<Skeleton className="h-96 w-full rounded-xl" />
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in fade-in duration-500 pb-20">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-black tracking-tight uppercase">
						Specifications Hub
					</h1>
					<p className="text-sm text-muted-foreground font-medium">
						Unified view of all architecture, contract, and feature
						specifications.
					</p>
				</div>
				<div className="flex gap-2">
					<Button
						variant="outline"
						size="sm"
						onClick={() => handleNavigate("adrs")}
						className="gap-2"
					>
						<FileText className="h-4 w-4" /> ADRs
					</Button>
					<Button
						variant="outline"
						size="sm"
						onClick={() => handleNavigate("contracts")}
						className="gap-2"
					>
						<Shield className="h-4 w-4" /> Contracts
					</Button>
					<Button
						variant="outline"
						size="sm"
						onClick={() => handleNavigate("features")}
						className="gap-2"
					>
						<BookOpen className="h-4 w-4" /> Features
					</Button>
				</div>
			</div>

			{/* Item Type Distribution */}
			<Card className="border-none bg-card/50">
				<CardHeader className="pb-3">
					<CardTitle className="text-sm">Item Type Mix</CardTitle>
				</CardHeader>
				<CardContent>
					{typeDistribution.length === 0 ? (
						<div className="text-sm text-muted-foreground">
							No items yet. Create a requirement, task, or story to start
							populating distribution.
						</div>
					) : (
						<div className="space-y-3">
							{typeDistribution.slice(0, 8).map((row) => {
								const percent = totalItems
									? Math.round((row.count / totalItems) * 100)
									: 0;
								return (
									<div key={row.type} className="space-y-1">
										<div className="flex items-center justify-between text-xs">
											<span className="uppercase tracking-wide text-muted-foreground">
												{row.type}
											</span>
											<span className="font-semibold">
												{row.count} ({percent}%)
											</span>
										</div>
										<div className="h-2 w-full rounded-full bg-muted/40 overflow-hidden">
											<div
												className="h-full bg-primary/70"
												style={{ width: `${percent}%` }}
											/>
										</div>
									</div>
								);
							})}
						</div>
					)}
				</CardContent>
			</Card>

			{/* Quick Navigation Cards */}
			<div className="grid gap-4 md:grid-cols-3">
				<button
					onClick={() => handleNavigate("adrs")}
					className="text-left group"
				>
					<Card className="border-none bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/20 dark:to-blue-900/20 hover:shadow-md transition-all">
						<CardHeader className="pb-3">
							<div className="flex items-center justify-between">
								<CardTitle className="text-sm">
									Architecture Decisions
								</CardTitle>
								<ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
							</div>
						</CardHeader>
						<CardContent className="space-y-3">
							<div className="text-3xl font-bold text-blue-600">
								{summary.adrs.total}
							</div>
							<div className="grid grid-cols-2 gap-2 text-xs">
								<div>
									<div className="text-muted-foreground">Accepted</div>
									<div className="font-bold text-blue-600">
										{summary.adrs.accepted}
									</div>
								</div>
								<div>
									<div className="text-muted-foreground">Compliance</div>
									<div className="font-bold text-blue-600">
										{Math.round(summary.adrs.averageCompliance)}%
									</div>
								</div>
							</div>
						</CardContent>
					</Card>
				</button>

				<button
					onClick={() => handleNavigate("contracts")}
					className="text-left group"
				>
					<Card className="border-none bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/20 dark:to-green-900/20 hover:shadow-md transition-all">
						<CardHeader className="pb-3">
							<div className="flex items-center justify-between">
								<CardTitle className="text-sm">API Contracts</CardTitle>
								<ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
							</div>
						</CardHeader>
						<CardContent className="space-y-3">
							<div className="text-3xl font-bold text-green-600">
								{summary.contracts.total}
							</div>
							<div className="grid grid-cols-2 gap-2 text-xs">
								<div>
									<div className="text-muted-foreground">Active</div>
									<div className="font-bold text-green-600">
										{summary.contracts.active}
									</div>
								</div>
								<div>
									<div className="text-muted-foreground">Verified</div>
									<div className="font-bold text-green-600">
										{summary.contracts.verified}
									</div>
								</div>
							</div>
						</CardContent>
					</Card>
				</button>

				<button
					onClick={() => handleNavigate("features")}
					className="text-left group"
				>
					<Card className="border-none bg-gradient-to-br from-purple-50 to-purple-100/50 dark:from-purple-950/20 dark:to-purple-900/20 hover:shadow-md transition-all">
						<CardHeader className="pb-3">
							<div className="flex items-center justify-between">
								<CardTitle className="text-sm">BDD Features</CardTitle>
								<ArrowRight className="h-4 w-4 text-muted-foreground group-hover:translate-x-1 transition-transform" />
							</div>
						</CardHeader>
						<CardContent className="space-y-3">
							<div className="text-3xl font-bold text-purple-600">
								{summary.features.total}
							</div>
							<div className="grid grid-cols-2 gap-2 text-xs">
								<div>
									<div className="text-muted-foreground">Scenarios</div>
									<div className="font-bold text-purple-600">
										{summary.features.scenarios}
									</div>
								</div>
								<div>
									<div className="text-muted-foreground">Pass Rate</div>
									<div className="font-bold text-purple-600">
										{Math.round(summary.features.passRate)}%
									</div>
								</div>
							</div>
						</CardContent>
					</Card>
				</button>
			</div>

			{/* Main Dashboard Component */}
			<SpecificationDashboard
				summary={summary}
				coverageData={coverageData}
				gapItems={gapItems}
				onNavigate={handleNavigate}
				onCreateNew={handleCreateNew}
			/>
		</div>
	);
}
