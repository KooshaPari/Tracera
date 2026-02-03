// UICodeTracePanel.tsx - Visualize the traceability chain from UI to code to requirements

import type {
	CanonicalConcept,
	CanonicalProjection,
	CodeReference,
	EquivalenceStrategy,
} from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@tracertm/ui/components/Card";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import {
	ArrowDown,
	ArrowRight,
	Badge as BadgeIcon,
	CheckCircle2,
	Code2,
	ExternalLink,
	FileText,
	Sparkles,
	Zap,
} from "lucide-react";
import { memo, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

/**
 * Represents a single level in the traceability chain
 */
export interface TraceLevel {
	id: string;
	type: "ui" | "code" | "requirement" | "concept";
	title: string;
	description?: string;
	perspective?: string;

	// UI Level specific
	componentName?: string;
	componentPath?: string;
	screenshot?: string;

	// Code Level specific
	codeRef?: CodeReference;

	// Requirement Level specific
	requirementId?: string;
	businessValue?: string;

	// Canonical concept
	canonicalId?: string;

	// Confidence and strategy
	confidence: number;
	strategy?: EquivalenceStrategy;
	isConfirmed?: boolean;
}

/**
 * Complete trace chain from UI through code to requirements
 */
export interface UICodeTraceChain {
	id: string;
	name: string;
	description?: string;
	levels: TraceLevel[];
	overallConfidence: number;
	canonicalConcept?: CanonicalConcept;
	projections?: CanonicalProjection[];
	lastUpdated: string;
}

export interface UICodeTracePanelProps {
	traceChain: UICodeTraceChain | null;
	isLoading?: boolean;
	onOpenCode?: (codeRef: CodeReference) => void;
	onOpenRequirement?: (requirementId: string) => void;
	onNavigateToUI?: (componentPath: string) => void;
	onRefreshTrace?: () => void;
}

// =============================================================================
// STRATEGY LABELS AND COLORS
// =============================================================================

const STRATEGY_LABELS: Record<EquivalenceStrategy, string> = {
	api_contract: "API Contract",
	co_occurrence: "Co-occurrence",
	explicit_annotation: "Explicit",
	manual_link: "Manual",
	naming_pattern: "Naming Match",
	semantic_similarity: "Semantic",
	shared_canonical: "Shared Concept",
	structural: "Structural",
	temporal: "Temporal",
};

const CONFIDENCE_COLOR = (confidence: number): string => {
	if (confidence >= 0.9) {
		return "bg-green-100 text-green-900 border-green-300";
	}
	if (confidence >= 0.7) {
		return "bg-blue-100 text-blue-900 border-blue-300";
	}
	if (confidence >= 0.5) {
		return "bg-yellow-100 text-yellow-900 border-yellow-300";
	}
	return "bg-orange-100 text-orange-900 border-orange-300";
};

const CONFIDENCE_ICON = (confidence: number) => {
	if (confidence >= 0.9) {
		return <CheckCircle2 className="w-4 h-4" />;
	}
	if (confidence >= 0.7) {
		return <Zap className="w-4 h-4" />;
	}
	return <Sparkles className="w-4 h-4" />;
};

// =============================================================================
// SUBCOMPONENTS
// =============================================================================

/**
 * Display a single trace level with rich information
 */
const TraceLevelComponent = memo(function TraceLevel({
	level,
	index,
	totalLevels,
	onOpenCode,
	onOpenRequirement,
	onNavigateToUI,
}: {
	level: TraceLevel;
	index: number;
	totalLevels: number;
	onOpenCode?: (codeRef: CodeReference) => void;
	onOpenRequirement?: (requirementId: string) => void;
	onNavigateToUI?: (componentPath: string) => void;
}) {
	const confidencePercent = Math.round(level.confidence * 100);
	const isLast = index === totalLevels - 1;

	return (
		<div className="relative">
			{/* Level Card */}
			<Card className="border border-slate-200 hover:border-slate-300 transition-colors bg-white">
				<CardContent className="p-4">
					{/* Type Badge and Confidence */}
					<div className="flex items-center justify-between mb-3">
						<div className="flex items-center gap-2">
							{level.type === "ui" && (
								<BadgeIcon className="w-4 h-4 text-pink-600" />
							)}
							{level.type === "code" && (
								<Code2 className="w-4 h-4 text-green-600" />
							)}
							{level.type === "requirement" && (
								<FileText className="w-4 h-4 text-blue-600" />
							)}
							{level.type === "concept" && (
								<Sparkles className="w-4 h-4 text-purple-600" />
							)}

							<span className="text-xs font-semibold text-slate-600 uppercase tracking-wider">
								{level.type}
							</span>
						</div>

						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger>
									<Badge
										variant="outline"
										className={`flex items-center gap-1 ${CONFIDENCE_COLOR(level.confidence)}`}
									>
										{CONFIDENCE_ICON(level.confidence)}
										{confidencePercent}%
									</Badge>
								</TooltipTrigger>
								<TooltipContent side="left">
									<div className="text-xs">
										<p className="font-semibold mb-1">
											{STRATEGY_LABELS[level.strategy || "manual_link"]}
										</p>
										<p className="text-xs">{level.description}</p>
									</div>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					</div>

					{/* Title */}
					<h4 className="font-semibold text-sm text-slate-900 mb-2">
						{level.title}
					</h4>

					{/* Perspective Badge */}
					{level.perspective && (
						<div className="flex items-center gap-2 mb-3">
							<Badge variant="secondary" className="text-xs">
								{level.perspective}
							</Badge>
						</div>
					)}

					{/* UI Level Details */}
					{level.type === "ui" && (
						<div className="space-y-2 bg-slate-50 p-3 rounded border border-slate-100">
							{level.componentName && (
								<div className="text-xs">
									<span className="text-slate-600">Component:</span>
									<span className="ml-2 font-mono text-slate-900">
										{level.componentName}
									</span>
								</div>
							)}
							{level.componentPath && (
								<div className="text-xs">
									<span className="text-slate-600">Path:</span>
									<span className="ml-2 font-mono text-slate-700 truncate">
										{level.componentPath}
									</span>
								</div>
							)}
							{level.screenshot && (
								<div className="mt-2">
									<img
										src={level.screenshot}
										alt={level.title}
										className="w-full h-32 object-cover rounded border border-slate-200"
									/>
								</div>
							)}
							{level.componentPath && onNavigateToUI && (
								<Button
									size="sm"
									variant="outline"
									className="w-full mt-2"
									onClick={() => onNavigateToUI(level.componentPath!)}
								>
									<ExternalLink className="w-3 h-3 mr-1" />
									Open Component
								</Button>
							)}
						</div>
					)}

					{/* Code Level Details */}
					{level.type === "code" && level.codeRef && (
						<div className="space-y-2 bg-slate-50 p-3 rounded border border-slate-100">
							<div className="text-xs">
								<span className="text-slate-600">Symbol:</span>
								<span className="ml-2 font-mono font-semibold text-slate-900">
									{level.codeRef.symbolName}
								</span>
							</div>

							<div className="text-xs">
								<span className="text-slate-600">Type:</span>
								<span className="ml-2 font-mono text-slate-700">
									{level.codeRef.symbolType}
								</span>
							</div>

							{level.codeRef.filePath && (
								<div className="text-xs">
									<span className="text-slate-600">File:</span>
									<span className="ml-2 font-mono text-slate-700 block truncate">
										{level.codeRef.filePath}
									</span>
								</div>
							)}

							{(level.codeRef.startLine || level.codeRef.endLine) && (
								<div className="text-xs">
									<span className="text-slate-600">Lines:</span>
									<span className="ml-2 font-mono text-slate-700">
										{level.codeRef.startLine}
										{level.codeRef.endLine &&
										level.codeRef.endLine !== level.codeRef.startLine
											? `–${level.codeRef.endLine}`
											: ""}
									</span>
								</div>
							)}

							{level.codeRef.signature && (
								<div className="text-xs mt-2 bg-white p-2 rounded border border-slate-200 overflow-x-auto">
									<span className="text-slate-600">Signature:</span>
									<pre className="font-mono text-slate-700 text-xs mt-1 overflow-x-auto">
										{level.codeRef.signature}
									</pre>
								</div>
							)}

							{level.codeRef.filePath && onOpenCode && (
								<Button
									size="sm"
									variant="outline"
									className="w-full mt-2"
									onClick={() => onOpenCode(level.codeRef!)}
								>
									<ExternalLink className="w-3 h-3 mr-1" />
									Open in Editor
								</Button>
							)}
						</div>
					)}

					{/* Requirement Level Details */}
					{level.type === "requirement" && (
						<div className="space-y-2 bg-slate-50 p-3 rounded border border-slate-100">
							{level.businessValue && (
								<div className="text-xs">
									<span className="text-slate-600">Business Value:</span>
									<p className="ml-0 text-slate-700 mt-1">
										{level.businessValue}
									</p>
								</div>
							)}
							{level.requirementId && onOpenRequirement && (
								<Button
									size="sm"
									variant="outline"
									className="w-full mt-2"
									onClick={() => onOpenRequirement(level.requirementId!)}
								>
									<ExternalLink className="w-3 h-3 mr-1" />
									View Requirement
								</Button>
							)}
						</div>
					)}

					{/* Canonical Concept Details */}
					{level.type === "concept" && level.canonicalId && (
						<div className="space-y-2 bg-purple-50 p-3 rounded border border-purple-200">
							<div className="text-xs text-purple-900">
								<p className="font-semibold">Canonical Concept</p>
								<p className="text-xs text-purple-700 mt-1">
									This trace is unified under a single canonical concept,
									linking all perspectives (UI, Code, Requirements) to the same
									abstract business entity.
								</p>
							</div>
						</div>
					)}
				</CardContent>
			</Card>

			{/* Arrow to next level */}
			{!isLast && (
				<div className="flex justify-center py-2">
					<ArrowDown className="w-4 h-4 text-slate-400" />
				</div>
			)}
		</div>
	);
});

/**
 * Display canonical concept information
 */
const CanonicalConceptCard = memo(function ConceptCard({
	concept,
}: {
	concept: CanonicalConcept;
}) {
	return (
		<Card className="border-2 border-purple-300 bg-purple-50">
			<CardHeader className="pb-3">
				<div className="flex items-center gap-2">
					<Sparkles className="w-5 h-5 text-purple-600" />
					<CardTitle className="text-sm">Canonical Concept</CardTitle>
				</div>
			</CardHeader>
			<CardContent className="space-y-3">
				<div>
					<p className="text-xs text-slate-600">Name</p>
					<p className="font-semibold text-slate-900">{concept.name}</p>
				</div>

				{concept.description && (
					<div>
						<p className="text-xs text-slate-600">Description</p>
						<p className="text-sm text-slate-700">{concept.description}</p>
					</div>
				)}

				<div className="flex items-center gap-2">
					<Badge variant="outline">{concept.domain}</Badge>
					{concept.tags?.map((tag) => (
						<Badge key={tag} variant="secondary" className="text-xs">
							{tag}
						</Badge>
					))}
				</div>

				<div className="bg-white p-2 rounded border border-purple-200 text-xs">
					<p className="text-slate-600 mb-1">Confidence</p>
					<div className="w-full bg-slate-200 rounded-full h-2">
						<div
							className="bg-purple-600 h-2 rounded-full transition-all"
							style={{ width: `${concept.confidence * 100}%` }}
						/>
					</div>
					<p className="text-slate-700 font-semibold mt-1">
						{Math.round(concept.confidence * 100)}%
					</p>
				</div>

				{concept.projectionCount > 0 && (
					<div className="bg-white p-2 rounded border border-purple-200 text-xs">
						<p className="text-slate-600">
							<span className="font-semibold">{concept.projectionCount}</span>{" "}
							perspective
							{concept.projectionCount !== 1 ? "s" : ""} linked
						</p>
					</div>
				)}
			</CardContent>
		</Card>
	);
});

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const UICodeTracePanel = memo(function UICodeTracePanelComponent({
	traceChain,
	isLoading,
	onOpenCode,
	onOpenRequirement,
	onNavigateToUI,
	onRefreshTrace,
}: UICodeTracePanelProps) {
	const [_expandedLevels, _setExpandedLevels] = useState<Set<string>>(
		new Set(),
	);

	if (!traceChain && !isLoading) {
		return (
			<Card className="w-full">
				<CardContent className="p-8 text-center">
					<FileText className="w-8 h-8 text-slate-400 mx-auto mb-2" />
					<p className="text-sm text-slate-600">No trace chain selected</p>
					<p className="text-xs text-slate-500 mt-1">
						Select a UI component to view its traceability chain
					</p>
				</CardContent>
			</Card>
		);
	}

	if (isLoading) {
		return (
			<Card className="w-full">
				<CardContent className="p-8 text-center">
					<div className="animate-pulse flex flex-col items-center">
						<div className="w-8 h-8 bg-slate-200 rounded-full mb-2" />
						<p className="text-sm text-slate-600">Loading trace chain...</p>
					</div>
				</CardContent>
			</Card>
		);
	}

	if (!traceChain) {
		return null;
	}

	const overallConfidencePercent = Math.round(
		traceChain.overallConfidence * 100,
	);

	return (
		<div className="w-full space-y-4">
			{/* Header */}
			<Card className="border-slate-300 bg-gradient-to-r from-slate-50 to-slate-100">
				<CardHeader className="pb-3">
					<div className="flex items-start justify-between gap-4">
						<div className="flex-1">
							<CardTitle className="flex items-center gap-2 mb-2">
								<Code2 className="w-5 h-5 text-green-600" />
								{traceChain.name}
							</CardTitle>
							{traceChain.description && (
								<p className="text-sm text-slate-600">
									{traceChain.description}
								</p>
							)}
						</div>

						<div className="flex items-center gap-2">
							<TooltipProvider>
								<Tooltip>
									<TooltipTrigger>
										<Badge
											className={`flex items-center gap-1 text-lg px-3 py-1 ${CONFIDENCE_COLOR(
												traceChain.overallConfidence,
											)}`}
										>
											{overallConfidencePercent}%
										</Badge>
									</TooltipTrigger>
									<TooltipContent>Overall trace confidence</TooltipContent>
								</Tooltip>
							</TooltipProvider>

							{onRefreshTrace && (
								<Button
									size="sm"
									variant="outline"
									onClick={onRefreshTrace}
									className="gap-1"
								>
									<ArrowRight className="w-3 h-3" />
									Refresh
								</Button>
							)}
						</div>
					</div>
				</CardHeader>
			</Card>

			{/* Canonical Concept (if available) */}
			{traceChain.canonicalConcept && (
				<CanonicalConceptCard concept={traceChain.canonicalConcept} />
			)}

			{/* Trace Levels */}
			<Card>
				<CardHeader className="pb-3">
					<CardTitle className="text-sm">Traceability Chain</CardTitle>
				</CardHeader>
				<CardContent className="p-0">
					<ScrollArea className="h-[600px] w-full">
						<div className="p-4 space-y-4">
							{traceChain.levels.map((level, index) => (
								<TraceLevelComponent
									key={level.id}
									level={level}
									index={index}
									totalLevels={traceChain.levels.length}
									onOpenCode={onOpenCode}
									onOpenRequirement={onOpenRequirement}
									onNavigateToUI={onNavigateToUI}
								/>
							))}
						</div>
					</ScrollArea>
				</CardContent>
			</Card>

			{/* Metadata Footer */}
			<div className="text-xs text-slate-500 px-1">
				<p>
					Last updated:{" "}
					{new Date(traceChain.lastUpdated).toLocaleString("en-US", {
						day: "numeric",
						hour: "2-digit",
						minute: "2-digit",
						month: "short",
					})}
				</p>
			</div>
		</div>
	);
});

UICodeTracePanel.displayName = "UICodeTracePanel";

export default UICodeTracePanel;
