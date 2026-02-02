import { useNavigate, useParams } from "@tanstack/react-router";
import { Button, Card } from "@tracertm/ui";
import { format } from "date-fns";
import { ArrowLeft } from "lucide-react";
import { useState } from "react";
import { GherkinViewer } from "@/components/specifications/bdd/GherkinViewer";
import { ScenarioCard } from "@/components/specifications/bdd/ScenarioCard";
import { useScenario, useScenarioActivities } from "@/hooks/useSpecifications";

export function ScenarioDetailView() {
	const params = useParams({ strict: false }) as {
		projectId?: string;
		featureId?: string;
		scenarioId?: string;
	};
	const navigate = useNavigate();
	const scenarioId = params.scenarioId || "";
	const { data: scenario, isLoading } = useScenario(scenarioId);
	const [page, setPage] = useState(1);
	const [pageSize, setPageSize] = useState(10);
	const { data: activityData } = useScenarioActivities(scenarioId, {
		limit: pageSize,
		offset: (page - 1) * pageSize,
	});
	const activities = activityData?.activities ?? [];
	const totalActivities = activityData?.total ?? 0;
	const totalPages = Math.max(1, Math.ceil(totalActivities / pageSize));

	if (isLoading) {
		return (
			<div className="p-6 space-y-6">
				<div className="h-8 w-40 bg-muted/40 rounded" />
				<div className="h-32 bg-muted/30 rounded-xl" />
				<div className="h-64 bg-muted/20 rounded-xl" />
			</div>
		);
	}

	if (!scenario) {
		return (
			<div className="p-6 space-y-4">
				<Button
					variant="ghost"
					onClick={() =>
						navigate({
							params: { projectId: params.projectId || "" },
							search: { tab: "features" },
							to: "/projects/$projectId/specifications",
						})
					}
				>
					<ArrowLeft className="h-4 w-4 mr-2" />
					Back to Features
				</Button>
				<Card className="border-none bg-muted/20 p-6 text-sm text-muted-foreground">
					Scenario not found.
				</Card>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-6">
			<Button
				variant="ghost"
				onClick={() =>
					navigate({
						params: {
							featureId: params.featureId || "",
							projectId: params.projectId || "",
						},
						to: "/projects/$projectId/features/$featureId",
					})
				}
			>
				<ArrowLeft className="h-4 w-4 mr-2" />
				Back to Feature
			</Button>

			<ScenarioCard scenario={scenario} />
			<GherkinViewer content={scenario.gherkinText} height="220px" />

			<Card className="border-none bg-card/50 p-6">
				<h2 className="text-base font-semibold mb-4">Scenario Activity</h2>
				<div className="space-y-3 text-sm text-muted-foreground">
					{activities.length > 0 ? (
						activities.map((activity) => (
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
										? format(new Date(activity.createdAt), "MMM d, yyyy HH:mm")
										: "—"}
								</div>
							</div>
						))
					) : (
						<div>No activity yet.</div>
					)}
					{totalActivities > activities.length && (
						<div className="text-xs text-muted-foreground">
							Showing {activities.length} of {totalActivities} activities.
						</div>
					)}
				</div>
				<div className="flex items-center justify-between text-xs text-muted-foreground mt-4">
					<button
						className="px-2 py-1 rounded border border-border/50"
						onClick={() => {
							setPage(1);
							setPageSize(totalActivities || 1000);
						}}
						disabled={totalActivities <= pageSize}
					>
						Show all
					</button>
					<span>or</span>
					<button
						className="px-2 py-1 rounded border border-border/50"
						onClick={() => {
							setPage(1);
							setPageSize(10);
						}}
						disabled={pageSize === 10}
					>
						Compact
					</button>
				</div>
				<div className="flex items-center gap-2 text-xs text-muted-foreground mt-4">
					<label>Rows</label>
					<select
						className="border border-border/50 rounded px-2 py-1 bg-transparent"
						value={pageSize}
						onChange={(e) => {
							setPageSize(Number(e.target.value));
							setPage(1);
						}}
					>
						<option value={10}>10</option>
						<option value={20}>20</option>
						<option value={50}>50</option>
					</select>
				</div>
				{totalActivities > pageSize && (
					<div className="flex items-center justify-between text-xs text-muted-foreground mt-4">
						<button
							className="px-2 py-1 rounded border border-border/50 disabled:opacity-50"
							disabled={page === 1}
							onClick={() => setPage((p) => Math.max(1, p - 1))}
						>
							Prev
						</button>
						<span>
							Page {page} of {totalPages}
						</span>
						<button
							className="px-2 py-1 rounded border border-border/50 disabled:opacity-50"
							disabled={page >= totalPages}
							onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
						>
							Next
						</button>
					</div>
				)}
				{totalActivities > pageSize && (
					<div className="mt-4">
						<div
							className="h-1.5 rounded-full bg-muted/40 overflow-hidden"
							aria-hidden
						>
							<div
								className="h-full bg-primary/70"
								style={{
									width: `${Math.min(100, (page / totalPages) * 100)}%`,
								}}
							/>
						</div>
					</div>
				)}
			</Card>
		</div>
	);
}
