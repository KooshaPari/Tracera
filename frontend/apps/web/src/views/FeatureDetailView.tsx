import { useNavigate, useParams } from "@tanstack/react-router";
import type { Scenario } from "@tracertm/types";
import {
	Button,
	Card,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import { format } from "date-fns";
import { ArrowLeft, Plus } from "lucide-react";
import { useEffect, useState } from "react";
import { FeatureCard } from "@/components/specifications/bdd/FeatureCard";
import { GherkinViewer } from "@/components/specifications/bdd/GherkinViewer";
import { ScenarioCard } from "@/components/specifications/bdd/ScenarioCard";
import {
	useFeature,
	useFeatureActivities,
	useScenarioActivities,
	useScenarios,
} from "@/hooks/useSpecifications";

export function FeatureDetailView() {
	const params = useParams({ strict: false }) as {
		projectId?: string;
		featureId?: string;
	};
	const navigate = useNavigate();
	const featureId = params.featureId || "";
	const { data: feature, isLoading } = useFeature(featureId);
	const { data: scenariosData } = useScenarios(featureId);
	const { data: featureActivities } = useFeatureActivities(featureId);
	const scenarios = scenariosData?.scenarios ?? [];
	const [selectedScenarioId, setSelectedScenarioId] = useState<string>("");
	const [activityPage, setActivityPage] = useState(1);
	const [activityPageSize, setActivityPageSize] = useState(10);
	const { data: scenarioActivityData } = useScenarioActivities(
		selectedScenarioId || "",
		{ limit: activityPageSize, offset: (activityPage - 1) * activityPageSize },
	);
	const scenarioActivities = scenarioActivityData?.activities ?? [];
	const scenarioActivityTotal = scenarioActivityData?.total ?? 0;
	const activityTotalPages = Math.max(
		1,
		Math.ceil(scenarioActivityTotal / activityPageSize),
	);

	useEffect(() => {
		if (!selectedScenarioId && scenarios.length > 0) {
			setSelectedScenarioId(scenarios[0]?.id || "");
		}
	}, [scenarios, selectedScenarioId]);

	useEffect(() => {
		setActivityPage(1);
	}, []);
	useEffect(() => {
		setActivityPage(1);
	}, []);

	if (isLoading) {
		return (
			<div className="p-6 space-y-6">
				<div className="h-8 w-40 bg-muted/40 rounded" />
				<div className="h-32 bg-muted/30 rounded-xl" />
				<div className="h-64 bg-muted/20 rounded-xl" />
			</div>
		);
	}

	if (!feature) {
		return (
			<div className="p-6 space-y-4">
				<Button
					variant="ghost"
					onClick={() =>
						navigate({
							to: "/projects/$projectId/specifications",
							params: { projectId: params.projectId || "" },
							search: { tab: "features" },
						})
					}
				>
					<ArrowLeft className="h-4 w-4 mr-2" />
					Back to Features
				</Button>
				<Card className="border-none bg-muted/20 p-6 text-sm text-muted-foreground">
					Feature not found.
				</Card>
			</div>
		);
	}

	return (
		<div className="space-y-6 p-6">
			<div className="flex justify-between items-start">
				<div>
					<h1 className="text-2xl font-bold mb-2">Feature Details</h1>
					<p className="text-muted-foreground">
						Manage feature specifications and scenarios.
					</p>
				</div>
				<Button>
					<Plus className="w-4 h-4 mr-2" />
					New Scenario
				</Button>
			</div>

			<FeatureCard feature={feature} className="border-l-4 border-l-blue-500" />

			<Card className="border-none bg-card/50">
				<div className="p-6 space-y-3 text-sm text-muted-foreground">
					<h2 className="text-base font-semibold text-foreground">Activity</h2>
					{featureActivities && featureActivities.length > 0
						? featureActivities.map((activity) => (
								<div
									key={activity.id}
									className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0"
								>
									<div>
										<div className="font-medium text-foreground">
											{activity.activityType}
										</div>
										<div className="text-xs text-muted-foreground">
											{activity.description || "Feature updated"}
										</div>
									</div>
									<div className="text-xs text-muted-foreground">
										{activity.createdAt
											? format(
													new Date(activity.createdAt),
													"MMM d, yyyy HH:mm",
												)
											: "—"}
									</div>
								</div>
							))
						: [
								feature.createdAt
									? {
											label: "Created",
											detail: `Feature ${feature.featureNumber}`,
											date: feature.createdAt,
										}
									: null,
								feature.updatedAt
									? {
											label: "Updated",
											detail: "Metadata updated",
											date: feature.updatedAt,
										}
									: null,
							]
								.filter(Boolean)
								.map((entry: any) => (
									<div
										key={`${entry.label}-${entry.date}`}
										className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0"
									>
										<div>
											<div className="font-medium text-foreground">
												{entry.label}
											</div>
											<div className="text-xs text-muted-foreground">
												{entry.detail}
											</div>
										</div>
										<div className="text-xs text-muted-foreground">
											{format(new Date(entry.date), "MMM d, yyyy HH:mm")}
										</div>
									</div>
								))}
					<div className="text-xs text-muted-foreground">
						Scenarios: {feature.scenarioCount || 0} total ·{" "}
						{feature.passedScenarios || 0} passing ·{" "}
						{feature.failedScenarios || 0} failing
					</div>
				</div>
			</Card>

			<div className="space-y-4">
				<h2 className="text-xl font-semibold">Scenarios</h2>
				{scenarios.length === 0 ? (
					<Card className="border-none bg-muted/20 p-6 text-sm text-muted-foreground">
						No scenarios yet.
					</Card>
				) : (
					<Tabs defaultValue="scenarios" className="w-full">
						<TabsList className="w-full justify-start">
							<TabsTrigger value="scenarios">Scenarios</TabsTrigger>
							<TabsTrigger value="activity">Scenario Activity</TabsTrigger>
						</TabsList>

						<TabsContent value="scenarios" className="mt-4">
							<div className="grid gap-4">
								{scenarios.map((scenario: Scenario) => (
									<div
										key={scenario.id}
										className="grid grid-cols-1 md:grid-cols-2 gap-4"
									>
										<ScenarioCard scenario={scenario} />
										<div className="space-y-2">
											<GherkinViewer
												content={scenario.gherkinText}
												height="150px"
											/>
											<Button
												variant="ghost"
												size="sm"
												onClick={() =>
													navigate({
														to: "/projects/$projectId/features/$featureId/scenarios/$scenarioId",
														params: {
															projectId: params.projectId || "",
															featureId: params.featureId || "",
															scenarioId: scenario.id,
														},
													})
												}
											>
												Open Scenario
											</Button>
										</div>
									</div>
								))}
							</div>
						</TabsContent>

						<TabsContent value="activity" className="mt-4">
							<div className="space-y-3">
								<Select
									value={selectedScenarioId}
									onValueChange={(value) => setSelectedScenarioId(value)}
								>
									<SelectTrigger className="w-[320px]">
										<SelectValue placeholder="Select a scenario" />
									</SelectTrigger>
									<SelectContent>
										{scenarios.map((scenario) => (
											<SelectItem key={scenario.id} value={scenario.id}>
												{scenario.scenarioNumber} · {scenario.title}
											</SelectItem>
										))}
									</SelectContent>
								</Select>

								<Card className="border-none bg-card/50 p-4">
									<div className="space-y-3 text-sm text-muted-foreground">
										{scenarioActivities.length > 0 ? (
											scenarioActivities.map((activity) => (
												<div
													key={activity.id}
													className="flex items-center justify-between border-b border-border/50 pb-2 last:border-0"
												>
													<div>
														<div className="font-medium text-foreground">
															{activity.activityType}
														</div>
														<div className="text-xs text-muted-foreground">
															{activity.description || "Scenario updated"}
														</div>
													</div>
													<div className="text-xs text-muted-foreground">
														{activity.createdAt
															? format(
																	new Date(activity.createdAt),
																	"MMM d, yyyy HH:mm",
																)
															: "—"}
													</div>
												</div>
											))
										) : (
											<div>No activity yet.</div>
										)}
										{scenarioActivityTotal > scenarioActivities.length && (
											<div className="text-xs text-muted-foreground">
												Showing {scenarioActivities.length} of{" "}
												{scenarioActivityTotal} activities.
											</div>
										)}
										{scenarioActivityTotal > activityPageSize && (
											<div className="flex items-center justify-between text-xs text-muted-foreground">
												<button
													className="px-2 py-1 rounded border border-border/50 disabled:opacity-50"
													disabled={activityPage === 1}
													onClick={() =>
														setActivityPage((p) => Math.max(1, p - 1))
													}
												>
													Prev
												</button>
												<span>
													Page {activityPage} of {activityTotalPages}
												</span>
												<button
													className="px-2 py-1 rounded border border-border/50 disabled:opacity-50"
													disabled={activityPage >= activityTotalPages}
													onClick={() =>
														setActivityPage((p) =>
															Math.min(activityTotalPages, p + 1),
														)
													}
												>
													Next
												</button>
											</div>
										)}
										<div className="flex items-center justify-between text-xs text-muted-foreground">
											<button
												className="px-2 py-1 rounded border border-border/50"
												onClick={() => {
													setActivityPage(1);
													setActivityPageSize(scenarioActivityTotal || 1000);
												}}
												disabled={scenarioActivityTotal <= activityPageSize}
											>
												Show all
											</button>
											<span>or</span>
											<button
												className="px-2 py-1 rounded border border-border/50"
												onClick={() => {
													setActivityPage(1);
													setActivityPageSize(10);
												}}
												disabled={activityPageSize === 10}
											>
												Compact
											</button>
										</div>
										<div className="flex items-center gap-2 text-xs text-muted-foreground">
											<label>Rows</label>
											<select
												className="border border-border/50 rounded px-2 py-1 bg-transparent"
												value={activityPageSize}
												onChange={(e) =>
													setActivityPageSize(Number(e.target.value))
												}
											>
												<option value={10}>10</option>
												<option value={20}>20</option>
												<option value={50}>50</option>
											</select>
										</div>
										{scenarioActivityTotal > activityPageSize && (
											<div className="mt-3">
												<div
													className="h-1.5 rounded-full bg-muted/40 overflow-hidden"
													aria-hidden
												>
													<div
														className="h-full bg-primary/70"
														style={{
															width: `${Math.min(
																100,
																(activityPage / activityTotalPages) * 100,
															)}%`,
														}}
													/>
												</div>
											</div>
										)}
									</div>
								</Card>
							</div>
						</TabsContent>
					</Tabs>
				)}
			</div>
		</div>
	);
}
