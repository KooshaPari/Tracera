// Export Controls for Graph Visualization
// Provides options to export graph in various formats (PNG, SVG, JSON, CSV)

import { Button } from "@tracertm/ui/components/Button";
import { Badge } from "@tracertm/ui/components/Badge";
import { Alert } from "@tracertm/ui/components/Alert";
import {
	Download,
	FileImage,
	FileJson,
	FileSpreadsheet,
	FileText,
	X,
	Loader2,
} from "lucide-react";
import { useCallback, useState } from "react";
import { useReactFlow, getNodesBounds, getViewportForBounds } from "@xyflow/react";
import { toPng, toSvg } from "html-to-image";

interface ExportControlsProps {
	onExport?: (format: "png" | "svg" | "json" | "csv") => void;
	onClose?: () => void;
	disabled?: boolean;
	className?: string;
}

export function ExportControls({
	onExport,
	onClose,
	disabled = false,
	className,
}: ExportControlsProps) {
	const { getNodes, getEdges } = useReactFlow();
	const [exporting, setExporting] = useState(false);
	const [exportFormat, setExportFormat] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);

	// Export to PNG
	const handleExportPNG = useCallback(async () => {
		try {
			setExporting(true);
			setExportFormat("png");
			setError(null);

			const element = document.querySelector(".react-flow") as HTMLElement;
			if (!element) {
				throw new Error("Graph container not found");
			}

			const dataUrl = await toPng(element, {
				backgroundColor: "#1a1a2e",
				quality: 1.0,
				pixelRatio: 2,
			});

			// Download
			const link = document.createElement("a");
			link.download = `graph-${Date.now()}.png`;
			link.href = dataUrl;
			link.click();

			onExport?.("png");
		} catch (err) {
			logger.error("Export PNG failed:", err);
			setError("Failed to export PNG. Please try again.");
		} finally {
			setExporting(false);
			setExportFormat(null);
		}
	}, [onExport]);

	// Export to SVG
	const handleExportSVG = useCallback(async () => {
		try {
			setExporting(true);
			setExportFormat("svg");
			setError(null);

			const element = document.querySelector(".react-flow") as HTMLElement;
			if (!element) {
				throw new Error("Graph container not found");
			}

			const dataUrl = await toSvg(element, {
				backgroundColor: "#1a1a2e",
			});

			// Download
			const link = document.createElement("a");
			link.download = `graph-${Date.now()}.svg`;
			link.href = dataUrl;
			link.click();

			onExport?.("svg");
		} catch (err) {
			logger.error("Export SVG failed:", err);
			setError("Failed to export SVG. Please try again.");
		} finally {
			setExporting(false);
			setExportFormat(null);
		}
	}, [onExport]);

	// Export to JSON
	const handleExportJSON = useCallback(() => {
		try {
			setExporting(true);
			setExportFormat("json");
			setError(null);

			const nodes = getNodes();
			const edges = getEdges();

			const data = {
				nodes: nodes.map((node) => ({
					id: node.id,
					type: node.type,
					position: node.position,
					data: node.data,
				})),
				edges: edges.map((edge) => ({
					id: edge.id,
					source: edge.source,
					target: edge.target,
					type: edge.type,
					label: edge.label,
				})),
				metadata: {
					exportDate: new Date().toISOString(),
					nodeCount: nodes.length,
					edgeCount: edges.length,
				},
			};

			const blob = new Blob([JSON.stringify(data, null, 2)], {
				type: "application/json",
			});
			const url = URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.download = `graph-${Date.now()}.json`;
			link.href = url;
			link.click();
			URL.revokeObjectURL(url);

			onExport?.("json");
		} catch (err) {
			logger.error("Export JSON failed:", err);
			setError("Failed to export JSON. Please try again.");
		} finally {
			setExporting(false);
			setExportFormat(null);
		}
	}, [getNodes, getEdges, onExport]);

	// Export to CSV
	const handleExportCSV = useCallback(() => {
		try {
			setExporting(true);
			setExportFormat("csv");
			setError(null);

			const nodes = getNodes();
			const edges = getEdges();

			// Create node CSV
			const nodeHeaders = ["id", "type", "label", "x", "y"];
			const nodeRows = nodes.map((node) => [
				node.id,
				node.type || "",
				(node.data as any)?.label || "",
				node.position.x,
				node.position.y,
			]);
			const nodeCSV = [
				nodeHeaders.join(","),
				...nodeRows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
			].join("\n");

			// Create edge CSV
			const edgeHeaders = ["id", "source", "target", "type", "label"];
			const edgeRows = edges.map((edge) => [
				edge.id,
				edge.source,
				edge.target,
				edge.type || "",
				edge.label || "",
			]);
			const edgeCSV = [
				edgeHeaders.join(","),
				...edgeRows.map((row) => row.map((cell) => `"${cell}"`).join(",")),
			].join("\n");

			// Combine both CSVs
			const fullCSV = `# Nodes\n${nodeCSV}\n\n# Edges\n${edgeCSV}`;

			const blob = new Blob([fullCSV], { type: "text/csv" });
			const url = URL.createObjectURL(blob);
			const link = document.createElement("a");
			link.download = `graph-${Date.now()}.csv`;
			link.href = url;
			link.click();
			URL.revokeObjectURL(url);

			onExport?.("csv");
		} catch (err) {
			logger.error("Export CSV failed:", err);
			setError("Failed to export CSV. Please try again.");
		} finally {
			setExporting(false);
			setExportFormat(null);
		}
	}, [getNodes, getEdges, onExport]);

	return (
		<div className={`flex flex-col gap-3 ${className || ""}`}>
			<div className="flex items-center justify-between">
				<h3 className="text-sm font-medium">Export Graph</h3>
				{onClose && (
					<Button
						variant="ghost"
						size="sm"
						onClick={onClose}
						className="h-7 w-7 p-0"
					>
						<X className="h-3.5 w-3.5" />
					</Button>
				)}
			</div>

			{error && (
				<Alert variant="destructive" className="text-sm">
					<p>{error}</p>
				</Alert>
			)}

			<div className="grid grid-cols-2 gap-2">
				{/* PNG Export */}
				<Button
					variant="outline"
					onClick={handleExportPNG}
					disabled={disabled || exporting}
					className="h-auto flex-col gap-2 p-3"
				>
					{exporting && exportFormat === "png" ? (
						<Loader2 className="h-8 w-8 animate-spin text-primary" />
					) : (
						<FileImage className="h-8 w-8 text-primary" />
					)}
					<div className="flex flex-col items-center">
						<span className="text-sm font-medium">PNG</span>
						<span className="text-xs text-muted-foreground">Raster image</span>
					</div>
				</Button>

				{/* SVG Export */}
				<Button
					variant="outline"
					onClick={handleExportSVG}
					disabled={disabled || exporting}
					className="h-auto flex-col gap-2 p-3"
				>
					{exporting && exportFormat === "svg" ? (
						<Loader2 className="h-8 w-8 animate-spin text-primary" />
					) : (
						<FileText className="h-8 w-8 text-primary" />
					)}
					<div className="flex flex-col items-center">
						<span className="text-sm font-medium">SVG</span>
						<span className="text-xs text-muted-foreground">Vector image</span>
					</div>
				</Button>

				{/* JSON Export */}
				<Button
					variant="outline"
					onClick={handleExportJSON}
					disabled={disabled || exporting}
					className="h-auto flex-col gap-2 p-3"
				>
					{exporting && exportFormat === "json" ? (
						<Loader2 className="h-8 w-8 animate-spin text-primary" />
					) : (
						<FileJson className="h-8 w-8 text-primary" />
					)}
					<div className="flex flex-col items-center">
						<span className="text-sm font-medium">JSON</span>
						<span className="text-xs text-muted-foreground">Graph data</span>
					</div>
				</Button>

				{/* CSV Export */}
				<Button
					variant="outline"
					onClick={handleExportCSV}
					disabled={disabled || exporting}
					className="h-auto flex-col gap-2 p-3"
				>
					{exporting && exportFormat === "csv" ? (
						<Loader2 className="h-8 w-8 animate-spin text-primary" />
					) : (
						<FileSpreadsheet className="h-8 w-8 text-primary" />
					)}
					<div className="flex flex-col items-center">
						<span className="text-sm font-medium">CSV</span>
						<span className="text-xs text-muted-foreground">Spreadsheet</span>
					</div>
				</Button>
			</div>

			<div className="text-xs text-muted-foreground space-y-1">
				<p>
					<strong>PNG/SVG:</strong> Visual snapshot of current view
				</p>
				<p>
					<strong>JSON:</strong> Complete graph data with positions
				</p>
				<p>
					<strong>CSV:</strong> Node and edge lists for spreadsheet analysis
				</p>
			</div>
		</div>
	);
}
