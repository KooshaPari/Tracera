// QA Enhanced Node - Graph node with embedded preview image and expandable popup
// Features: Separate image pill click, vertical tab sidebar, QA metrics

import type { Item } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import {
	Dialog,
	DialogContent,
	DialogTrigger,
} from "@tracertm/ui/components/Dialog";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Handle, Position } from "@xyflow/react";
import type { Node, NodeProps } from "@xyflow/react";
import {
	BarChart3,
	Camera,
	CheckCircle2,
	Clock,
	Download,
	ExternalLink,
	FileText,
	Image,
	Link2,
	Play,
	RefreshCw,
	Settings,
	XCircle,
} from "lucide-react";
import { memo, useCallback, useState } from "react";

// === Types ===

export interface QANodeMetrics {
	testCount: number;
	passCount: number;
	failCount: number;
	skipCount: number;
	passRate: number;
	coverage?: number;
	avgDuration?: number;
	lastRunAt?: string;
}

export interface QANodePreview {
	thumbnailUrl?: string;
	screenshotUrl?: string;
	videoUrl?: string;
	gifUrl?: string;
	hasLiveDemo?: boolean;
}

export interface QANodeArtifact {
	id: string;
	type: "screenshot" | "video" | "gif" | "log" | "trace";
	url: string;
	thumbnailUrl?: string;
	name: string;
	capturedAt: string;
}

export interface QAEnhancedNodeData {
	id: string;
	item: Item;
	label: string;
	type: string;
	status: string;
	description?: string;
	metrics?: QANodeMetrics;
	preview?: QANodePreview;
	artifacts?: QANodeArtifact[];
	connections: { incoming: number; outgoing: number; total: number };
	onExpandPopup?: (nodeId: string) => void;
	onRunTests?: (nodeId: string) => void;
	[key: string]: unknown;
}

// === Main Component ===

function getPassRateColor(rate: number): string {
	if (rate >= 90) {
		return "text-green-500 bg-green-500/10 border-green-500/30";
	}
	if (rate >= 70) {
		return "text-yellow-500 bg-yellow-500/10 border-yellow-500/30";
	}
	return "text-red-500 bg-red-500/10 border-red-500/30";
}

function QAEnhancedNodeComponent({
	data,
	selected,
}: NodeProps<Node<QAEnhancedNodeData, "qaEnhanced">>) {
	const [popupOpen, setPopupOpen] = useState(false);

	const hasPreview =
		Boolean(data.preview?.thumbnailUrl) || Boolean(data.preview?.screenshotUrl);
	const passRate = data.metrics?.passRate ?? 0;

	const handleImageClick = useCallback((e: React.MouseEvent) => {
		e.stopPropagation();
		setPopupOpen(true);
	}, []);

	return (
		<TooltipProvider>
			<Handle type="target" position={Position.Left} className="!w-3 !h-3" />

			<Dialog open={popupOpen} onOpenChange={setPopupOpen}>
				<Card
					className={`w-[280px] overflow-hidden transition-all ${
						selected ? "ring-2 ring-primary ring-offset-2" : ""
					}`}
				>
					{/* Header Row */}
					<div className="flex items-center justify-between p-3 border-b bg-muted/30">
						<div className="flex items-center gap-2 min-w-0 flex-1">
							<div className="flex flex-col min-w-0">
								<h4 className="font-semibold text-sm truncate">{data.label}</h4>
								<div className="flex items-center gap-1.5 mt-0.5">
									<Badge variant="outline" className="text-[10px] h-4 px-1.5">
										{data.type}
									</Badge>
									<Badge variant="secondary" className="text-[10px] h-4 px-1.5">
										{data.status}
									</Badge>
								</div>
							</div>
						</div>

						{/* Pass Rate Badge */}
						{data.metrics && (
							<div
								className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${getPassRateColor(passRate)}`}
							>
								{passRate >= 90 ? (
									<CheckCircle2 className="h-3.5 w-3.5" />
								) : (passRate >= 70 ? (
									<Clock className="h-3.5 w-3.5" />
								) : (
									<XCircle className="h-3.5 w-3.5" />
								))}
								{passRate}%
							</div>
						)}
					</div>

					{/* Image Pill - Separately Clickable */}
					{hasPreview && (
						<DialogTrigger asChild>
							<div
								className="relative mx-3 my-2 rounded-xl overflow-hidden cursor-pointer group border-2 border-dashed border-transparent hover:border-primary/50 transition-all"
								onClick={handleImageClick}
							>
								<img
									src={
										data.preview?.thumbnailUrl || data.preview?.screenshotUrl
									}
									alt={data.label}
									className="w-full h-28 object-cover transition-transform group-hover:scale-105"
									loading="lazy"
								/>

								{/* Hover Overlay */}
								<div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-1">
									{data.preview?.hasLiveDemo ? (
										<>
											<Play className="h-8 w-8 text-white" />
											<span className="text-white text-xs font-medium">
												Run Demo
											</span>
										</>
									) : (
										<>
											<Image className="h-6 w-6 text-white" />
											<span className="text-white text-xs font-medium">
												Click to Expand
											</span>
										</>
									)}
								</div>

								{/* Artifact Count Badge */}
								{data.artifacts && data.artifacts.length > 0 && (
									<div className="absolute top-2 right-2 bg-black/70 text-white text-[10px] px-1.5 py-0.5 rounded-full">
										{data.artifacts.length} artifacts
									</div>
								)}
							</div>
						</DialogTrigger>
					)}

					{/* No Preview Placeholder */}
					{!hasPreview && (
						<div className="mx-3 my-2 rounded-xl bg-muted/50 h-20 flex items-center justify-center">
							<span className="text-muted-foreground text-xs">No preview</span>
						</div>
					)}

					{/* Metrics Footer */}
					<div className="flex items-center justify-between px-3 py-2 text-[10px] text-muted-foreground border-t bg-muted/20">
						<div className="flex items-center gap-3">
							<Tooltip>
								<TooltipTrigger asChild>
									<span className="flex items-center gap-0.5">
										<Link2 className="h-3 w-3" />
										{data.connections.total}
									</span>
								</TooltipTrigger>
								<TooltipContent>
									<p>
										{data.connections.incoming} in, {data.connections.outgoing}{" "}
										out
									</p>
								</TooltipContent>
							</Tooltip>

							{data.metrics?.avgDuration && (
								<Tooltip>
									<TooltipTrigger asChild>
										<span className="flex items-center gap-0.5">
											<Clock className="h-3 w-3" />
											{data.metrics.avgDuration}ms
										</span>
									</TooltipTrigger>
									<TooltipContent>
										<p>Average test duration</p>
									</TooltipContent>
								</Tooltip>
							)}

							{data.metrics && (
								<span className="flex items-center gap-0.5">
									🧪 {data.metrics.passCount}/{data.metrics.testCount}
								</span>
							)}
						</div>

						{data.metrics?.coverage !== undefined && (
							<span className="font-medium">📊 {data.metrics.coverage}%</span>
						)}
					</div>
				</Card>

				{/* Expand Popup */}
				<DialogContent className="max-w-4xl h-[80vh] p-0 flex overflow-hidden">
					<NodeExpandPopup data={data} onClose={() => setPopupOpen(false)} />
				</DialogContent>
			</Dialog>

			<Handle type="source" position={Position.Right} className="!w-3 !h-3" />
		</TooltipProvider>
	);
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);

// === Popup Component ===

interface NodeExpandPopupProps {
	data: QAEnhancedNodeData;
	onClose: () => void;
}

function NodeExpandPopup({ data, onClose }: NodeExpandPopupProps) {
	const [activeTab, setActiveTab] = useState<string>("artifacts");

	const tabs = [
		{
			badge: data.artifacts?.length,
			icon: Camera,
			id: "artifacts",
			label: "Artifacts",
		},
		{ icon: Play, id: "demo", label: "Demo" },
		{ icon: FileText, id: "tests", label: "Tests" },
		{ icon: BarChart3, id: "metrics", label: "Metrics" },
		{ icon: Settings, id: "actions", label: "Actions" },
	];

	return (
		<div className="flex w-full h-full">
			{/* Vertical Tab Sidebar */}
			<div className="w-20 bg-muted border-r flex flex-col gap-1 p-2 shrink-0">
				{tabs.map((tab) => (
					<button
						key={tab.id}
						type="button"
						className={`flex flex-col items-center gap-1 p-2.5 rounded-lg text-[10px] transition-colors ${
							activeTab === tab.id
								? "bg-primary text-primary-foreground"
								: "hover:bg-accent text-muted-foreground hover:text-foreground"
						}`}
						onClick={() => setActiveTab(tab.id)}
					>
						<tab.icon className="h-5 w-5" />
						<span className="font-medium">{tab.label}</span>
						{tab.badge !== undefined && tab.badge > 0 && (
							<Badge variant="secondary" className="text-[9px] h-4 px-1">
								{tab.badge}
							</Badge>
						)}
					</button>
				))}
			</div>

			{/* Content Area */}
			<div className="flex-1 overflow-auto p-4">
				{/* Header */}
				<div className="flex items-start justify-between mb-4">
					<div>
						<h2 className="text-xl font-bold">{data.label}</h2>
						<p className="text-sm text-muted-foreground mt-1">
							{data.description || "No description available"}
						</p>
					</div>
					<div className="flex gap-2">
						<Badge variant="outline">{data.type}</Badge>
						<Badge variant="secondary">{data.status}</Badge>
					</div>
				</div>

				{/* Tab Content */}
				{activeTab === "artifacts" && <ArtifactsTab data={data} />}
				{activeTab === "demo" && <DemoTab data={data} />}
				{activeTab === "tests" && <TestsTab data={data} />}
				{activeTab === "metrics" && <MetricsTab data={data} />}
				{activeTab === "actions" && (
					<ActionsTab data={data} onClose={onClose} />
				)}
			</div>
		</div>
	);
}

// === Tab Components ===

function ArtifactsTab({ data }: { data: QAEnhancedNodeData }) {
	if (!data.artifacts || data.artifacts.length === 0) {
		return (
			<div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
				<Camera className="h-12 w-12 mb-2 opacity-50" />
				<p>No artifacts captured yet</p>
				<p className="text-sm mt-1">
					Run tests to generate screenshots and videos
				</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{/* Screenshots */}
			<div>
				<h3 className="font-semibold mb-2">Screenshots</h3>
				<div className="grid grid-cols-3 gap-3">
					{data.artifacts
						.filter((a) => a.type === "screenshot")
						.map((artifact) => (
							<div
								key={artifact.id}
								className="relative aspect-video rounded-lg overflow-hidden bg-muted group cursor-pointer"
							>
								<img
									src={artifact.thumbnailUrl || artifact.url}
									alt={artifact.name}
									className="w-full h-full object-cover"
								/>
								<div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
									<Button variant="secondary" size="sm">
										<ExternalLink className="h-4 w-4 mr-1" />
										View
									</Button>
								</div>
								<span className="absolute bottom-1 left-1 text-[9px] bg-black/70 text-white px-1 rounded">
									{artifact.name}
								</span>
							</div>
						))}
				</div>
			</div>

			{/* Videos/GIFs */}
			<div>
				<h3 className="font-semibold mb-2">Recordings</h3>
				<div className="grid grid-cols-2 gap-3">
					{data.artifacts
						.filter((a) => a.type === "video" || a.type === "gif")
						.map((artifact) => (
							<div
								key={artifact.id}
								className="relative aspect-video rounded-lg overflow-hidden bg-muted group cursor-pointer"
							>
								{artifact.type === "gif" ? (
									<img
										src={artifact.url}
										alt={artifact.name}
										className="w-full h-full object-cover"
									/>
								) : (
									<video
										src={artifact.url}
										className="w-full h-full object-cover"
										muted
										playsInline
										onMouseEnter={(e) => e.currentTarget.play()}
										onMouseLeave={(e) => {
											e.currentTarget.pause();
											e.currentTarget.currentTime = 0;
										}}
									/>
								)}
								<div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
									<Play className="h-8 w-8 text-white" />
								</div>
							</div>
						))}
				</div>
			</div>

			{/* Logs */}
			{data.artifacts.some((a) => a.type === "log") && (
				<div>
					<h3 className="font-semibold mb-2">Logs</h3>
					<div className="space-y-2">
						{data.artifacts
							.filter((a) => a.type === "log")
							.map((artifact) => (
								<div
									key={artifact.id}
									className="flex items-center justify-between p-2 bg-muted rounded-lg"
								>
									<div className="flex items-center gap-2">
										<FileText className="h-4 w-4 text-muted-foreground" />
										<span className="text-sm">{artifact.name}</span>
									</div>
									<Button variant="ghost" size="sm">
										<Download className="h-4 w-4" />
									</Button>
								</div>
							))}
					</div>
				</div>
			)}
		</div>
	);
}

function DemoTab({ data }: { data: QAEnhancedNodeData }) {
	const hasLiveDemo = data.preview?.hasLiveDemo;
	const previewUrl = data.preview?.screenshotUrl || data.preview?.videoUrl;

	if (hasLiveDemo) {
		return (
			<div className="space-y-4">
				<div className="flex items-center justify-between">
					<h3 className="font-semibold">Live Demo</h3>
					<Button variant="outline" size="sm">
						<ExternalLink className="h-4 w-4 mr-1" />
						Open in New Tab
					</Button>
				</div>
				<div className="aspect-video rounded-lg overflow-hidden bg-muted border">
					<iframe
						src={data.preview?.videoUrl}
						title={`Demo: ${data.label}`}
						className="w-full h-full border-0"
						sandbox="allow-scripts allow-same-origin"
					/>
				</div>
			</div>
		);
	}

	if (previewUrl) {
		const isVideo = previewUrl.endsWith(".webm") || previewUrl.endsWith(".mp4");
		const isGif = previewUrl.endsWith(".gif");

		return (
			<div className="space-y-4">
				<h3 className="font-semibold">Preview</h3>
				<div className="aspect-video rounded-lg overflow-hidden bg-muted">
					{isVideo ? (
						<video
							src={previewUrl}
							controls
							className="w-full h-full"
							aria-label="Preview"
						>
							<track kind="captions" />
						</video>
					) : (isGif ? (
						<img
							src={previewUrl}
							alt={data.label}
							className="w-full h-full object-contain"
						/>
					) : (
						<img
							src={previewUrl}
							alt={data.label}
							className="w-full h-full object-contain"
						/>
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
			<Play className="h-12 w-12 mb-2 opacity-50" />
			<p>No demo available</p>
			<p className="text-sm mt-1">Configure demo settings in Actions tab</p>
		</div>
	);
}

function TestsTab({ data }: { data: QAEnhancedNodeData }) {
	const { metrics } = data;

	if (!metrics) {
		return (
			<div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
				<FileText className="h-12 w-12 mb-2 opacity-50" />
				<p>No test results available</p>
				<p className="text-sm mt-1">Run tests to see results</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			{/* Summary Stats */}
			<div className="grid grid-cols-4 gap-4">
				<Card className="p-4 text-center">
					<div className="text-2xl font-bold">{metrics.testCount}</div>
					<div className="text-xs text-muted-foreground">Total Tests</div>
				</Card>
				<Card className="p-4 text-center bg-green-500/10">
					<div className="text-2xl font-bold text-green-600">
						{metrics.passCount}
					</div>
					<div className="text-xs text-muted-foreground">Passed</div>
				</Card>
				<Card className="p-4 text-center bg-red-500/10">
					<div className="text-2xl font-bold text-red-600">
						{metrics.failCount}
					</div>
					<div className="text-xs text-muted-foreground">Failed</div>
				</Card>
				<Card className="p-4 text-center bg-yellow-500/10">
					<div className="text-2xl font-bold text-yellow-600">
						{metrics.skipCount}
					</div>
					<div className="text-xs text-muted-foreground">Skipped</div>
				</Card>
			</div>

			{/* Pass Rate Progress */}
			<Card className="p-4">
				<div className="flex items-center justify-between mb-2">
					<span className="text-sm font-medium">Pass Rate</span>
					<span className="text-sm font-bold">{metrics.passRate}%</span>
				</div>
				<div className="w-full h-2 bg-muted rounded-full overflow-hidden">
					<div
						className={`h-full transition-all ${
							metrics.passRate >= 90
								? "bg-green-500"
								: (metrics.passRate >= 70
									? "bg-yellow-500"
									: "bg-red-500")
						}`}
						style={{ width: `${metrics.passRate}%` }}
					/>
				</div>
			</Card>

			{/* Coverage if available */}
			{metrics.coverage !== undefined && (
				<Card className="p-4">
					<div className="flex items-center justify-between mb-2">
						<span className="text-sm font-medium">Code Coverage</span>
						<span className="text-sm font-bold">{metrics.coverage}%</span>
					</div>
					<div className="w-full h-2 bg-muted rounded-full overflow-hidden">
						<div
							className="h-full bg-blue-500 transition-all"
							style={{ width: `${metrics.coverage}%` }}
						/>
					</div>
				</Card>
			)}

			{/* Last Run */}
			{metrics.lastRunAt && (
				<p className="text-sm text-muted-foreground">
					Last run: {new Date(metrics.lastRunAt).toLocaleString()}
				</p>
			)}
		</div>
	);
}

function MetricsTab({ data }: { data: QAEnhancedNodeData }) {
	const { metrics } = data;

	return (
		<div className="space-y-4">
			<h3 className="font-semibold">Performance Metrics</h3>

			{metrics?.avgDuration && (
				<Card className="p-4">
					<div className="flex items-center justify-between">
						<div>
							<div className="text-sm font-medium">Average Duration</div>
							<div className="text-2xl font-bold">{metrics.avgDuration}ms</div>
						</div>
						<Clock className="h-8 w-8 text-muted-foreground" />
					</div>
				</Card>
			)}

			<Card className="p-4">
				<div className="flex items-center justify-between">
					<div>
						<div className="text-sm font-medium">Connections</div>
						<div className="text-2xl font-bold">{data.connections.total}</div>
					</div>
					<Link2 className="h-8 w-8 text-muted-foreground" />
				</div>
				<div className="mt-2 text-xs text-muted-foreground">
					{data.connections.incoming} incoming · {data.connections.outgoing}{" "}
					outgoing
				</div>
			</Card>

			{/* Trend Analysis Charts */}
			<div className="h-48 bg-muted rounded-lg p-4 flex flex-col items-center justify-center">
				<div className="text-muted-foreground text-center space-y-2">
					<BarChart3 className="h-8 w-8 mx-auto opacity-60" />
					<div>
						<p className="text-sm font-semibold">Quality Trends</p>
						<p className="text-xs text-muted-foreground/60">
							Monitored over time
						</p>
					</div>
					<div className="flex gap-2 justify-center text-[10px] pt-2">
						<span className="px-2 py-1 bg-green-500/10 text-green-700 rounded">
							+2.5% improvement
						</span>
						<span className="px-2 py-1 bg-blue-500/10 text-blue-700 rounded">
							Last 7 days
						</span>
					</div>
				</div>
			</div>
		</div>
	);
}

function ActionsTab({
	data,
	onClose: _onClose,
}: {
	data: QAEnhancedNodeData;
	onClose: () => void;
}) {
	undefined; // Reserved for future use
	const handleRunTests = useCallback(() => {
		data.onRunTests?.(data.id);
	}, [data]);

	return (
		<div className="space-y-4">
			<h3 className="font-semibold">Actions</h3>

			<div className="grid grid-cols-2 gap-3">
				<Button
					variant="default"
					className="h-20 flex-col gap-2"
					onClick={handleRunTests}
				>
					<Play className="h-6 w-6" />
					<span>Run Tests</span>
				</Button>

				<Button variant="outline" className="h-20 flex-col gap-2">
					<RefreshCw className="h-6 w-6" />
					<span>Re-run Failed</span>
				</Button>

				<Button variant="outline" className="h-20 flex-col gap-2">
					<Camera className="h-6 w-6" />
					<span>Capture Screenshot</span>
				</Button>

				<Button variant="outline" className="h-20 flex-col gap-2">
					<Download className="h-6 w-6" />
					<span>Download All</span>
				</Button>
			</div>

			<div className="pt-4 border-t">
				<h4 className="text-sm font-medium mb-2">Quick Links</h4>
				<div className="space-y-2">
					<Button variant="ghost" className="w-full justify-start h-9">
						<ExternalLink className="h-4 w-4 mr-2" />
						Open in Code Editor
					</Button>
					<Button variant="ghost" className="w-full justify-start h-9">
						<ExternalLink className="h-4 w-4 mr-2" />
						View in CI/CD
					</Button>
					<Button variant="ghost" className="w-full justify-start h-9">
						<ExternalLink className="h-4 w-4 mr-2" />
						Open Test Report
					</Button>
				</div>
			</div>
		</div>
	);
}
