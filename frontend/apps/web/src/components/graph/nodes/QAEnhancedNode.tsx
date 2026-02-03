// QA Enhanced Node - Graph node with QA metrics and expandable popup
// Extends RichNodePill with QA-specific features: pass rate, artifacts, demo runner

import type { Item } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Card } from "@tracertm/ui/components/Card";
import {
	Dialog,
	DialogContent,
	DialogTrigger,
} from "@tracertm/ui/components/Dialog";
import { Handle, Position } from "@xyflow/react";
import type { Node, NodeProps } from "@xyflow/react";
import { CheckCircle2, Clock, Image, Link2, Play, XCircle } from "lucide-react";
import { memo, useCallback, useState } from "react";
import { NodeExpandPopup } from "./NodeExpandPopup";

// === Types ===

export interface QANodeMetrics {
	passRate: number; // 0-100
	testCount: number;
	passCount: number;
	failCount: number;
	coverage?: number; // 0-100
	avgDuration?: number; // Ms
	flakiness?: number; // 0-100
	lastRunAt?: string;
}

export interface QANodePreview {
	thumbnailUrl?: string;
	screenshotUrl?: string;
	videoUrl?: string;
	gifUrl?: string;
	hasLiveDemo?: boolean;
	demoUrl?: string;
}

export interface QANodeArtifact {
	id: string;
	type: "screenshot" | "video" | "gif" | "log" | "trace";
	url: string;
	thumbnailUrl?: string;
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
	[key: string]: unknown; // Index signature for React Flow compatibility
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

	const hasPreview = Boolean(data.preview?.thumbnailUrl);
	const passRate = data.metrics?.passRate ?? 0;

	const handleImageClick = useCallback((e: React.MouseEvent) => {
		e.stopPropagation();
		setPopupOpen(true);
	}, []);

	return (
		<>
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
								className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold border ${getPassRateColor(
									passRate,
								)}`}
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
									src={data.preview?.thumbnailUrl}
									alt={data.label}
									className="w-full h-28 object-cover transition-transform group-hover:scale-105"
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

					{/* Metrics Footer */}
					<div className="flex items-center justify-between px-3 py-2 text-[10px] text-muted-foreground border-t bg-muted/20">
						<div className="flex items-center gap-3">
							<span className="flex items-center gap-0.5">
								<Link2 className="h-3 w-3" />
								{data.connections.total}
							</span>

							{data.metrics?.avgDuration && (
								<span className="flex items-center gap-0.5">
									<Clock className="h-3 w-3" />
									{data.metrics.avgDuration}ms
								</span>
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
		</>
	);
}

export const QAEnhancedNode = memo(QAEnhancedNodeComponent);
