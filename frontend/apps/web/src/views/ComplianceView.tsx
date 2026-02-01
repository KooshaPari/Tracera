import { useNavigate, useParams } from "@tanstack/react-router";
import type { SmellType } from "@tracertm/types";
import { Button, Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import { SmellIndicator } from "@/components/specifications/quality/SmellIndicator";
import { useQualityReport } from "@/hooks/useSpecifications";

export function ComplianceView() {
	const { projectId } = useParams({ strict: false });
	const navigate = useNavigate();
	const { data: qualityReports } = useQualityReport(projectId || "");
	const reports = qualityReports ?? [];

	return (
		<div className="p-6 space-y-6">
			<div>
				<h1 className="text-2xl font-bold">Compliance & Quality</h1>
				<p className="text-muted-foreground">
					Automated quality analysis and smell detection (ISO 29148).
				</p>
			</div>

			<div className="grid gap-4">
				{reports.length === 0 ? (
					<Card className="border-none bg-muted/20 py-12">
						<div className="flex flex-col items-center justify-center text-muted-foreground/70">
							<p className="text-sm font-medium">No quality reports yet</p>
							<p className="text-xs text-muted-foreground/50 mt-1">
								Create specifications to start tracking compliance metrics.
							</p>
							<Button
								variant="outline"
								className="mt-4"
								onClick={() =>
									projectId
										? navigate({
												to: "/projects/$projectId/views/$viewType",
												params: { projectId, viewType: "feature" },
											})
										: navigate({ to: "/projects" })
								}
							>
								View Items
							</Button>
						</div>
					</Card>
				) : (
					reports.map((report) => (
						<Card key={report.id}>
							<CardHeader className="pb-2">
								<div className="flex justify-between">
									<CardTitle className="text-base">
										Item Analysis: {report.itemId}
									</CardTitle>
									<span className="font-mono text-sm">
										Score: {Math.round(report.completenessScore * 100)}/100
									</span>
								</div>
							</CardHeader>
							<CardContent>
								<div className="flex flex-col gap-4">
									<div className="flex items-center gap-2">
										<span className="text-sm font-medium">
											Detected Smells:
										</span>
										<SmellIndicator smells={report.smells as SmellType[]} />
									</div>
									{report.suggestions.length > 0 && (
										<div className="bg-muted/30 p-3 rounded text-sm">
											<p className="font-medium mb-1">AI Suggestions:</p>
											<ul className="list-disc pl-4 space-y-1">
												{report.suggestions.map((s, i) => (
													<li key={i}>{s}</li>
												))}
											</ul>
										</div>
									)}
								</div>
							</CardContent>
						</Card>
					))
				)}
			</div>
		</div>
	);
}
