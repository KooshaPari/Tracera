import { useQuery } from "@tanstack/react-query";
import { logger } from '@/lib/logger';
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui/components/Select";
import { useState } from "react";
import { api } from "../api/endpoints";

type ExportFormat = "json" | "csv" | "markdown";

export function ExportView() {
	// Note: projectId would come from route params in actual implementation
	// For now, we'll use state
	const [projectId, setProjectId] = useState<string>("");
	const [format, setFormat] = useState<ExportFormat>("json");
	const [isExporting, setIsExporting] = useState(false);

	const projectsQuery = useQuery({
		queryKey: ["projects"],
		queryFn: () => api.projects.list(),
	});

	const handleExport = async () => {
		if (!projectId) {
			alert("Please select a project");
			return;
		}

		setIsExporting(true);
		try {
			const blob = await api.exportImport.export(projectId, format);
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement("a");
			a.href = url;
			a.download = `project-${projectId}-export.${format === "markdown" ? "md" : format}`;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		} catch (error) {
			logger.error("Export failed:", error);
			alert("Export failed. Please try again.");
		} finally {
			setIsExporting(false);
		}
	};

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-3xl font-bold">Export Project</h1>
				<p className="text-gray-600">Export project data in various formats</p>
			</div>

			<Card className="p-6">
				<div className="space-y-4">
					<div>
						<label
							htmlFor="project-select"
							className="block text-sm font-medium mb-2"
						>
							Project
						</label>
						<Select
							value={projectId || "none"}
							onValueChange={(value) => {
								setProjectId(value === "none" ? "" : value);
							}}
						>
							<SelectTrigger id="project-select" className="mt-2">
								<SelectValue placeholder="Select a project" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="none">Select a project</SelectItem>
								{projectsQuery.data?.map((project) => (
									<SelectItem key={project.id} value={project.id}>
										{project.name}
									</SelectItem>
								))}
							</SelectContent>
						</Select>
					</div>

					<div>
						<label
							htmlFor="format-select"
							className="block text-sm font-medium mb-2"
						>
							Export Format
						</label>
						<Select
							value={format}
							onValueChange={(v) => setFormat(v as ExportFormat)}
						>
							<SelectTrigger id="format-select" className="mt-2">
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="json">JSON</SelectItem>
								<SelectItem value="csv">CSV</SelectItem>
								<SelectItem value="markdown">Markdown</SelectItem>
							</SelectContent>
						</Select>
					</div>

					<div className="space-y-2">
						<h3 className="font-medium">Format Details:</h3>
						<ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
							<li>
								<strong>JSON:</strong> Complete project data with all
								relationships
							</li>
							<li>
								<strong>CSV:</strong> Tabular format suitable for spreadsheets
							</li>
							<li>
								<strong>Markdown:</strong> Human-readable documentation format
							</li>
						</ul>
					</div>

					<Button onClick={handleExport} disabled={!projectId || isExporting}>
						{isExporting ? "Exporting..." : "Export Project"}
					</Button>
				</div>
			</Card>

			{projectId && (
				<Card className="p-6 bg-blue-50 dark:bg-blue-900/20">
					<h3 className="font-medium mb-2">Export Preview</h3>
					<p className="text-sm text-gray-600">
						Project ID:{" "}
						<code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">
							{projectId}
						</code>
					</p>
					<p className="text-sm text-gray-600 mt-2">
						Format:{" "}
						<code className="bg-white dark:bg-gray-800 px-2 py-1 rounded">
							{format.toUpperCase()}
						</code>
					</p>
				</Card>
			)}
		</div>
	);
}
