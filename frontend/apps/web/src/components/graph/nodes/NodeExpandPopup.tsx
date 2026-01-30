// Node Expand Popup - Modal with vertical tabs for artifacts, demo, tests, metrics, actions

import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	Camera,
	Video,
	FileText,
	BarChart3,
	Settings,
	Play,
	Download,
	RefreshCw,
	ExternalLink,
} from "lucide-react";
import { useState } from "react";
import type {
	QAEnhancedNodeData,
	QANodeArtifact,
	QANodeMetrics,
	QANodePreview,
} from "./QAEnhancedNode";

interface NodeExpandPopupProps {
	data: QAEnhancedNodeData;
	onClose?: () => void;
}

export function NodeExpandPopup({ data }: NodeExpandPopupProps) {
	const [activeTab, setActiveTab] = useState<string>("artifacts");

	const tabs = [
		{
			id: "artifacts",
			icon: Camera,
			label: "Artifacts",
			badge: data.artifacts?.length,
		},
		{ id: "demo", icon: Play, label: "Demo" },
		{ id: "tests", icon: FileText, label: "Tests" },
		{ id: "metrics", icon: BarChart3, label: "Metrics" },
		{ id: "actions", icon: Settings, label: "Actions" },
	];

	return (
		<div className="flex w-full h-full">
			{/* Vertical Tab Sidebar */}
			<div className="w-20 bg-muted border-r flex flex-col gap-1 p-2 shrink-0">
				{tabs.map((tab) => (
					<button
						key={tab.id}
						className={`flex flex-col items-center gap-1 p-2.5 rounded-lg text-[10px] transition-colors cursor-pointer ${
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
			<div className="flex-1 overflow-auto p-6">
				{activeTab === "artifacts" && (
					<ArtifactsTab
						{...(data.artifacts ? { artifacts: data.artifacts } : {})}
					/>
				)}
				{activeTab === "demo" && (
					<DemoTab {...(data.preview ? { preview: data.preview } : {})} />
				)}
				{activeTab === "tests" && (
					<TestsTab {...(data.metrics ? { metrics: data.metrics } : {})} />
				)}
				{activeTab === "metrics" && (
					<MetricsTab {...(data.metrics ? { metrics: data.metrics } : {})} />
				)}
				{activeTab === "actions" && <ActionsTab nodeId={data.id} />}
			</div>
		</div>
	);
}

// === Tab Components ===

function ArtifactsTab({ artifacts }: { artifacts?: QANodeArtifact[] }) {
	if (!artifacts || artifacts.length === 0) {
		return (
			<div className="flex flex-col items-center justify-center h-full text-muted-foreground">
				<Camera className="h-12 w-12 mb-4 opacity-50" />
				<p>No artifacts available</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold">Artifacts</h2>
			<div className="grid grid-cols-2 md:grid-cols-3 gap-4">
				{artifacts.map((artifact) => (
					<div
						key={artifact.id}
						className="border rounded-lg overflow-hidden hover:shadow-md hover:bg-muted/30 transition-all cursor-pointer"
					>
						{artifact.type === "screenshot" || artifact.type === "gif" ? (
							<img
								src={artifact.thumbnailUrl || artifact.url}
								alt={artifact.type}
								className="w-full h-32 object-cover"
							/>
						) : artifact.type === "video" ? (
							<div className="w-full h-32 bg-muted flex items-center justify-center">
								<Video className="h-8 w-8 text-muted-foreground" />
							</div>
						) : (
							<div className="w-full h-32 bg-muted flex items-center justify-center">
								<FileText className="h-8 w-8 text-muted-foreground" />
							</div>
						)}
						<div className="p-2">
							<div className="flex items-center justify-between">
								<Badge variant="outline" className="text-xs">
									{artifact.type}
								</Badge>
								<Button
									variant="ghost"
									size="sm"
									className="h-6 w-6 p-0 hover:bg-muted/50 transition-colors"
								>
									<Download className="h-3 w-3" />
								</Button>
							</div>
							<p className="text-xs text-muted-foreground mt-1">
								{new Date(artifact.capturedAt).toLocaleString()}
							</p>
						</div>
					</div>
				))}
			</div>
		</div>
	);
}

function DemoTab({ preview }: { preview?: QANodePreview }) {
	if (!preview) {
		return (
			<div className="flex flex-col items-center justify-center h-full text-muted-foreground">
				<Play className="h-12 w-12 mb-4 opacity-50" />
				<p>No demo available</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold">Demo</h2>
			{preview.hasLiveDemo && preview.demoUrl ? (
				<div className="border rounded-lg overflow-hidden">
					<iframe
						src={preview.demoUrl}
						className="w-full h-[600px]"
						title="Demo"
						sandbox="allow-scripts allow-same-origin"
					/>
				</div>
			) : preview.gifUrl ? (
				<div className="border rounded-lg overflow-hidden">
					<img src={preview.gifUrl} alt="Demo GIF" className="w-full" />
				</div>
			) : preview.videoUrl ? (
				<div className="border rounded-lg overflow-hidden">
					<video src={preview.videoUrl} controls className="w-full" />
				</div>
			) : (
				<p className="text-muted-foreground">No demo media available</p>
			)}
		</div>
	);
}

function TestsTab({ metrics }: { metrics?: QANodeMetrics }) {
	if (!metrics) {
		return (
			<div className="flex flex-col items-center justify-center h-full text-muted-foreground">
				<FileText className="h-12 w-12 mb-4 opacity-50" />
				<p>No test data available</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold">Test Results</h2>
			<div className="grid grid-cols-2 gap-4">
				<div className="border rounded-lg p-4">
					<div className="text-sm text-muted-foreground">Total Tests</div>
					<div className="text-2xl font-bold">{metrics.testCount}</div>
				</div>
				<div className="border rounded-lg p-4">
					<div className="text-sm text-muted-foreground">Passed</div>
					<div className="text-2xl font-bold text-green-500">
						{metrics.passCount}
					</div>
				</div>
				<div className="border rounded-lg p-4">
					<div className="text-sm text-muted-foreground">Failed</div>
					<div className="text-2xl font-bold text-red-500">
						{metrics.failCount}
					</div>
				</div>
				{metrics.coverage !== undefined && (
					<div className="border rounded-lg p-4">
						<div className="text-sm text-muted-foreground">Coverage</div>
						<div className="text-2xl font-bold">{metrics.coverage}%</div>
					</div>
				)}
			</div>
			{metrics.flakiness !== undefined && (
				<div className="border rounded-lg p-4">
					<div className="text-sm text-muted-foreground mb-2">Flakiness</div>
					<div className="w-full bg-muted rounded-full h-2">
						<div
							className="bg-yellow-500 h-2 rounded-full"
							style={{ width: `${metrics.flakiness}%` }}
						/>
					</div>
					<div className="text-xs text-muted-foreground mt-1">
						{metrics.flakiness}% flaky tests
					</div>
				</div>
			)}
		</div>
	);
}

function MetricsTab({ metrics }: { metrics?: QANodeMetrics }) {
	if (!metrics) {
		return (
			<div className="flex flex-col items-center justify-center h-full text-muted-foreground">
				<BarChart3 className="h-12 w-12 mb-4 opacity-50" />
				<p>No metrics available</p>
			</div>
		);
	}

	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold">Metrics</h2>
			<div className="space-y-4">
				<div className="border rounded-lg p-4">
					<div className="text-sm text-muted-foreground mb-2">Pass Rate</div>
					<div className="text-3xl font-bold">{metrics.passRate}%</div>
					<div className="w-full bg-muted rounded-full h-2 mt-2">
						<div
							className={`h-2 rounded-full ${
								metrics.passRate >= 90
									? "bg-green-500"
									: metrics.passRate >= 70
										? "bg-yellow-500"
										: "bg-red-500"
							}`}
							style={{ width: `${metrics.passRate}%` }}
						/>
					</div>
				</div>
				{metrics.avgDuration !== undefined && (
					<div className="border rounded-lg p-4">
						<div className="text-sm text-muted-foreground">Avg Duration</div>
						<div className="text-2xl font-bold">{metrics.avgDuration}ms</div>
					</div>
				)}
				{metrics.lastRunAt && (
					<div className="border rounded-lg p-4">
						<div className="text-sm text-muted-foreground">Last Run</div>
						<div className="text-sm">
							{new Date(metrics.lastRunAt).toLocaleString()}
						</div>
					</div>
				)}
			</div>
		</div>
	);
}

function ActionsTab({ nodeId: _nodeId }: { nodeId: string }) {
	return (
		<div className="space-y-4">
			<h2 className="text-xl font-semibold">Actions</h2>
			<div className="space-y-2">
				<Button
					className="w-full justify-start hover:bg-accent transition-colors"
					variant="outline"
				>
					<RefreshCw className="h-4 w-4 mr-2" />
					Re-run Tests
				</Button>
				<Button
					className="w-full justify-start hover:bg-accent transition-colors"
					variant="outline"
				>
					<Download className="h-4 w-4 mr-2" />
					Download Artifacts
				</Button>
				<Button
					className="w-full justify-start hover:bg-accent transition-colors"
					variant="outline"
				>
					<ExternalLink className="h-4 w-4 mr-2" />
					Open in Browser
				</Button>
			</div>
		</div>
	);
}
