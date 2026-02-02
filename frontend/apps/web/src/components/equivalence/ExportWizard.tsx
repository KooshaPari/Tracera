import { AlertCircle, Download, Loader2 } from "lucide-react";
import { logger } from '@/lib/logger';
import React, { useCallback, useState } from "react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
	Dialog,
	DialogContent,
	DialogDescription,
	DialogFooter,
	DialogHeader,
	DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import client from "@/api/client";

const { getAuthHeaders } = client;

export interface ExportWizardProps {
	projectId: string;
	projectName: string;
	isOpen: boolean;
	onClose: () => void;
	onExport?: (config: ExportConfig) => Promise<void>;
}

export interface ExportConfig {
	format: "json" | "yaml";
	includeEmbeddings: boolean;
	includeMetadata: boolean;
	includeItemInfo: boolean;
	pretty: boolean;
	filters?: {
		status?: string;
		minConfidence?: number;
		perspective?: string;
	};
}

interface ExportStats {
	concepts: number;
	projections: number;
	links: number;
	perspectives: number;
	averageConfidence: number;
}

function formatSize(bytes: number): string {
	const units = ["B", "KB", "MB", "GB"];
	let size = bytes;
	let unitIndex = 0;
	while (size >= 1024 && unitIndex < units.length - 1) {
		size /= 1024;
		unitIndex++;
	}
	return `${size.toFixed(2)} ${units[unitIndex]}`;
}

export const ExportWizard: React.FC<ExportWizardProps> = ({
	projectId,
	projectName,
	isOpen,
	onClose,
	onExport,
}) => {
	const [step, setStep] = useState<"options" | "review">("options");
	const [format, setFormat] = useState<"json" | "yaml">("json");
	const [includeEmbeddings, setIncludeEmbeddings] = useState(false);
	const [includeMetadata, setIncludeMetadata] = useState(true);
	const [includeItemInfo, setIncludeItemInfo] = useState(true);
	const [pretty, setPretty] = useState(true);
	const [isLoading, setIsLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);
	const [stats, setStats] = useState<ExportStats | null>(null);

	const fetchStats = useCallback(async () => {
		try {
			const response = await fetch(
				`/api/v1/projects/${projectId}/equivalence/export-statistics`,
				{ headers: getAuthHeaders() },
			);
			if (!response.ok) throw new Error("Failed to fetch statistics");
			const data = await response.json();
			setStats(data);
		} catch (err) {
			logger.error("Failed to fetch export statistics:", err);
			setError("Failed to load export statistics");
		}
	}, [projectId]);

	// Fetch statistics when dialog opens
	React.useEffect(() => {
		if (isOpen && !stats) {
			void fetchStats();
		}
	}, [isOpen, stats, fetchStats]);

	const handleNext = () => {
		setStep("review");
	};

	const handleBack = () => {
		setStep("options");
	};

	const handleExport = async () => {
		setIsLoading(true);
		setError(null);

		try {
			const config: ExportConfig = {
				format,
				includeEmbeddings,
				includeMetadata,
				includeItemInfo,
				pretty,
			};

			if (onExport) {
				await onExport(config);
			} else {
				// Default export behavior
				const response = await fetch(
					`/api/v1/projects/${projectId}/equivalence/export?format=${format}` +
						`&include_embeddings=${includeEmbeddings}` +
						`&include_metadata=${includeMetadata}`,
					{ headers: getAuthHeaders() },
				);

				if (!response.ok) throw new Error("Export failed");

				const blob = await response.blob();
				const url = URL.createObjectURL(blob);
				const link = document.createElement("a");
				link.href = url;
				link.download = `equivalence-${projectName}-${new Date().toISOString().split("T")[0]}.${format}`;
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
				URL.revokeObjectURL(url);
			}

			onClose();
		} catch (err) {
			setError(err instanceof Error ? err.message : "Export failed");
		} finally {
			setIsLoading(false);
		}
	};

	const handleClose = () => {
		setStep("options");
		setError(null);
		onClose();
	};

	const estimateSize = (): string => {
		if (!stats) return "Calculating...";
		// Rough estimation: ~500 bytes per concept, projection, and link
		const baseSize = (stats.concepts + stats.projections + stats.links) * 500;
		const embeddingsSize = includeEmbeddings ? stats.concepts * 12800 : 0; // ~3200 floats
		return formatSize(baseSize + embeddingsSize);
	};

	return (
		<Dialog open={isOpen} onOpenChange={handleClose}>
			<DialogContent className="max-w-2xl">
				<DialogHeader>
					<DialogTitle>Export Equivalence Data</DialogTitle>
					<DialogDescription>
						Export canonical concepts, projections, and equivalence links from{" "}
						{projectName}
					</DialogDescription>
				</DialogHeader>

				{step === "options" && (
					<div className="space-y-6">
						{error && (
							<Alert variant="destructive">
								<AlertCircle className="h-4 w-4" />
								<AlertDescription>{error}</AlertDescription>
							</Alert>
						)}

						{stats && (
							<div className="rounded-lg bg-blue-50 p-4 border border-blue-200">
								<h3 className="font-semibold text-blue-900 mb-2">
									Export Summary
								</h3>
								<div className="grid grid-cols-2 gap-4 text-sm text-blue-800">
									<div>
										<div className="font-medium">{stats.concepts}</div>
										<div className="text-xs">Canonical Concepts</div>
									</div>
									<div>
										<div className="font-medium">{stats.projections}</div>
										<div className="text-xs">Projections</div>
									</div>
									<div>
										<div className="font-medium">{stats.links}</div>
										<div className="text-xs">Equivalence Links</div>
									</div>
									<div>
										<div className="font-medium">{stats.perspectives}</div>
										<div className="text-xs">Perspectives</div>
									</div>
								</div>
							</div>
						)}

						<div className="space-y-4">
							<div>
								<Label className="text-base font-semibold mb-3 block">
									Format
								</Label>
								<RadioGroup
									value={format}
									onValueChange={(v: string) => setFormat(v as "json" | "yaml")}
								>
									<div className="flex items-center space-x-2 mb-2">
										<RadioGroupItem value="json" id="json" />
										<Label
											htmlFor="json"
											className="font-normal cursor-pointer"
										>
											JSON - Universal format with detailed structure
										</Label>
									</div>
									<div className="flex items-center space-x-2">
										<RadioGroupItem value="yaml" id="yaml" />
										<Label
											htmlFor="yaml"
											className="font-normal cursor-pointer"
										>
											YAML - Human-readable format
										</Label>
									</div>
								</RadioGroup>
							</div>

							<div className="space-y-3">
								<Label className="text-base font-semibold">Options</Label>
								<div className="space-y-2">
									<div className="flex items-center space-x-2">
										<Checkbox
											id="embeddings"
											checked={includeEmbeddings}
											onCheckedChange={(checked) =>
												setIncludeEmbeddings(!!checked)
											}
										/>
										<Label
											htmlFor="embeddings"
											className="font-normal cursor-pointer"
										>
											Include embeddings (larger file size)
										</Label>
									</div>
									<div className="flex items-center space-x-2">
										<Checkbox
											id="metadata"
											checked={includeMetadata}
											onCheckedChange={(checked) =>
												setIncludeMetadata(!!checked)
											}
										/>
										<Label
											htmlFor="metadata"
											className="font-normal cursor-pointer"
										>
											Include metadata and evidence
										</Label>
									</div>
									<div className="flex items-center space-x-2">
										<Checkbox
											id="iteminfo"
											checked={includeItemInfo}
											onCheckedChange={(checked) =>
												setIncludeItemInfo(!!checked)
											}
										/>
										<Label
											htmlFor="iteminfo"
											className="font-normal cursor-pointer"
										>
											Include item information (titles, types)
										</Label>
									</div>
									<div className="flex items-center space-x-2">
										<Checkbox
											id="pretty"
											checked={pretty}
											onCheckedChange={(checked) => setPretty(!!checked)}
										/>
										<Label
											htmlFor="pretty"
											className="font-normal cursor-pointer"
										>
											Pretty print (larger but human-readable)
										</Label>
									</div>
								</div>
							</div>

							<div className="pt-2 pb-2 border-t">
								<div className="flex justify-between items-center">
									<span className="text-sm text-gray-600">
										Estimated file size:
									</span>
									<span className="font-semibold">{estimateSize()}</span>
								</div>
							</div>
						</div>
					</div>
				)}

				{step === "review" && (
					<div className="space-y-4">
						<div className="rounded-lg bg-gray-50 p-4 space-y-3">
							<div className="grid grid-cols-2 gap-4 text-sm">
								<div>
									<span className="text-gray-600">Format:</span>
									<span className="font-semibold ml-2">
										{format.toUpperCase()}
									</span>
								</div>
								<div>
									<span className="text-gray-600">File size:</span>
									<span className="font-semibold ml-2">{estimateSize()}</span>
								</div>
							</div>
							<div className="border-t pt-3">
								<div className="text-sm text-gray-600 mb-2">
									Options enabled:
								</div>
								<ul className="text-sm space-y-1 list-disc list-inside">
									{includeEmbeddings && <li>Embeddings</li>}
									{includeMetadata && <li>Metadata & Evidence</li>}
									{includeItemInfo && <li>Item Information</li>}
									{pretty && <li>Pretty Print</li>}
								</ul>
							</div>
						</div>

						<Alert>
							<AlertCircle className="h-4 w-4" />
							<AlertDescription>
								The export file will contain all equivalence data for this
								project. You can import it later into another project or keep it
								as a backup.
							</AlertDescription>
						</Alert>
					</div>
				)}

				<DialogFooter>
					{step === "options" ? (
						<>
							<Button variant="outline" onClick={handleClose}>
								Cancel
							</Button>
							<Button onClick={handleNext} disabled={isLoading}>
								Next
							</Button>
						</>
					) : (
						<>
							<Button
								variant="outline"
								onClick={handleBack}
								disabled={isLoading}
							>
								Back
							</Button>
							<Button
								onClick={handleExport}
								disabled={isLoading}
								className="gap-2"
							>
								{isLoading ? (
									<>
										<Loader2 className="h-4 w-4 animate-spin" />
										Exporting...
									</>
								) : (
									<>
										<Download className="h-4 w-4" />
										Export
									</>
								)}
							</Button>
						</>
					)}
				</DialogFooter>
			</DialogContent>
		</Dialog>
	);
};
