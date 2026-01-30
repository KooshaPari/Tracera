/**
 * ODC Classification Card Component
 * Displays IBM Orthogonal Defect Classification for defects
 */

import { cn } from "@/lib/utils";
import type { ODCDefectType, ODCTrigger } from "@/hooks/useItemSpecAnalytics";

interface ODCClassificationCardProps {
	defectType: ODCDefectType;
	trigger: ODCTrigger;
	impact: string;
	confidence?: number;
	likelyInjectionPhase?: string | null;
	suggestedPrevention?: string[];
	className?: string;
}

const defectTypeConfig: Record<
	ODCDefectType,
	{ label: string; description: string; color: string }
> = {
	function: {
		label: "Function",
		description:
			"Affects capability, end-user interfaces, product interfaces, or global data structure",
		color: "bg-red-100 text-red-800 border-red-300",
	},
	interface: {
		label: "Interface",
		description:
			"Incorrect interaction with other components, modules, or drivers",
		color: "bg-orange-100 text-orange-800 border-orange-300",
	},
	checking: {
		label: "Checking",
		description:
			"Missing or incorrect validation of data, values, or conditions",
		color: "bg-yellow-100 text-yellow-800 border-yellow-300",
	},
	assignment: {
		label: "Assignment",
		description: "Incorrect initialization or setting of data values",
		color: "bg-green-100 text-green-800 border-green-300",
	},
	timing: {
		label: "Timing/Serialization",
		description:
			"Race conditions, resource contention, or synchronization issues",
		color: "bg-blue-100 text-blue-800 border-blue-300",
	},
	build: {
		label: "Build/Package",
		description: "Build process, library references, or version control issues",
		color: "bg-indigo-100 text-indigo-800 border-indigo-300",
	},
	documentation: {
		label: "Documentation",
		description: "Issues in publications, maintenance notes, or documentation",
		color: "bg-purple-100 text-purple-800 border-purple-300",
	},
	algorithm: {
		label: "Algorithm",
		description: "Incorrect or inefficient algorithm implementation",
		color: "bg-pink-100 text-pink-800 border-pink-300",
	},
};

const triggerConfig: Record<
	ODCTrigger,
	{ label: string; description: string }
> = {
	coverage: {
		label: "Coverage",
		description: "Found through simple path testing",
	},
	design_conformance: {
		label: "Design Conformance",
		description: "Found by verifying design specifications",
	},
	exception_handling: {
		label: "Exception Handling",
		description: "Found through exception/error path testing",
	},
	simple_path: {
		label: "Simple Path",
		description: "Found through basic code path execution",
	},
	complex_path: {
		label: "Complex Path",
		description: "Found through complex interactions or sequences",
	},
	side_effects: {
		label: "Side Effects",
		description: "Found through interaction with other modules",
	},
	rare_situation: {
		label: "Rare Situation",
		description: "Found in unusual or edge-case conditions",
	},
};

export function ODCClassificationCard({
	defectType,
	trigger,
	impact,
	confidence,
	likelyInjectionPhase,
	suggestedPrevention,
	className,
}: ODCClassificationCardProps) {
	const typeConfig = defectTypeConfig[defectType];
	const triggerInfo = triggerConfig[trigger];

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-start justify-between">
				<div>
					<h3 className="text-sm font-medium text-muted-foreground mb-1">
						ODC Classification
					</h3>
					<div className="flex items-center gap-2">
						<span
							className={cn(
								"px-2 py-1 rounded text-sm font-medium border",
								typeConfig.color,
							)}
						>
							{typeConfig.label}
						</span>
						{confidence !== undefined && (
							<span className="text-sm text-muted-foreground">
								{Math.round(confidence * 100)}% confidence
							</span>
						)}
					</div>
				</div>
			</div>

			{/* Classification Grid */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-4">
				{/* Defect Type */}
				<div className="p-3 bg-muted rounded-lg">
					<div className="text-xs text-muted-foreground mb-1">Defect Type</div>
					<div className="font-medium">{typeConfig.label}</div>
					<p className="text-xs text-muted-foreground mt-1">
						{typeConfig.description}
					</p>
				</div>

				{/* Trigger */}
				<div className="p-3 bg-muted rounded-lg">
					<div className="text-xs text-muted-foreground mb-1">Trigger</div>
					<div className="font-medium">{triggerInfo.label}</div>
					<p className="text-xs text-muted-foreground mt-1">
						{triggerInfo.description}
					</p>
				</div>

				{/* Impact */}
				<div className="p-3 bg-muted rounded-lg">
					<div className="text-xs text-muted-foreground mb-1">Impact</div>
					<div className="font-medium capitalize">{impact}</div>
					{likelyInjectionPhase && (
						<p className="text-xs text-muted-foreground mt-1">
							Likely injected during: {likelyInjectionPhase}
						</p>
					)}
				</div>
			</div>

			{/* Prevention Suggestions */}
			{suggestedPrevention && suggestedPrevention.length > 0 && (
				<div className="border-t pt-4">
					<h4 className="text-sm font-medium mb-2">Prevention Suggestions</h4>
					<ul className="space-y-1.5">
						{suggestedPrevention.map((suggestion, idx) => (
							<li key={idx} className="flex items-start gap-2 text-sm">
								<span className="text-green-600 mt-0.5">✓</span>
								<span>{suggestion}</span>
							</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}

interface ODCBadgeProps {
	defectType: ODCDefectType;
	size?: "sm" | "md";
	className?: string;
}

export function ODCBadge({
	defectType,
	size = "md",
	className,
}: ODCBadgeProps) {
	const config = defectTypeConfig[defectType];
	const sizeClass =
		size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

	return (
		<span
			className={cn(
				"inline-flex items-center rounded border font-medium",
				config.color,
				sizeClass,
				className,
			)}
			title={config.description}
		>
			{config.label}
		</span>
	);
}

interface ODCTriggerBadgeProps {
	trigger: ODCTrigger;
	size?: "sm" | "md";
	className?: string;
}

export function ODCTriggerBadge({
	trigger,
	size = "md",
	className,
}: ODCTriggerBadgeProps) {
	const config = triggerConfig[trigger];
	const sizeClass =
		size === "sm" ? "text-xs px-1.5 py-0.5" : "text-sm px-2 py-1";

	return (
		<span
			className={cn(
				"inline-flex items-center rounded border bg-slate-100 text-slate-800 border-slate-300",
				sizeClass,
				className,
			)}
			title={config.description}
		>
			{config.label}
		</span>
	);
}
