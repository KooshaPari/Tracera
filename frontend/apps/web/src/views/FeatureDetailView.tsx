import { useNavigate, useParams } from "@tanstack/react-router";
import { FeatureCard } from "@/components/specifications/bdd/FeatureCard";
import { ScenarioCard } from "@/components/specifications/bdd/ScenarioCard";
import { GherkinViewer } from "@/components/specifications/bdd/GherkinViewer";
import { Button, Card } from "@tracertm/ui";
import { ArrowLeft, Plus } from "lucide-react";
import {
	useFeature,
	useFeatureActivities,
	useScenarios,
} from "@/hooks/useSpecifications";
import { format } from "date-fns";
import type { Feature, Scenario } from "@tracertm/types";

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
					<div className="grid gap-4">
						{scenarios.map((scenario: Scenario) => (
							<div
								key={scenario.id}
								className="grid grid-cols-1 md:grid-cols-2 gap-4"
							>
								<ScenarioCard scenario={scenario} />
								<GherkinViewer content={scenario.gherkinText} height="150px" />
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	);
}
