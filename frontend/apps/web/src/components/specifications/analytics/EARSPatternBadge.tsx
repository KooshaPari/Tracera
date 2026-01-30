/**
 * EARS Pattern Badge Component
 * Displays the EARS (Easy Approach to Requirements Syntax) classification
 * for a requirement specification.
 */

import { cn } from "@/lib/utils";
import type { EARSPatternType } from "@/hooks/useItemSpecAnalytics";

interface EARSPatternBadgeProps {
	patternType: EARSPatternType;
	confidence?: number;
	isWellFormed?: boolean;
	showConfidence?: boolean;
	size?: "sm" | "md" | "lg";
	className?: string;
}

const patternConfig: Record<
	EARSPatternType,
	{ label: string; description: string; color: string; icon: string }
> = {
	ubiquitous: {
		label: "Ubiquitous",
		description: "The system shall always...",
		color: "bg-blue-100 text-blue-800 border-blue-300",
		icon: "∀",
	},
	event_driven: {
		label: "Event-Driven",
		description: "When <trigger>, the system shall...",
		color: "bg-purple-100 text-purple-800 border-purple-300",
		icon: "⚡",
	},
	state_driven: {
		label: "State-Driven",
		description: "While <state>, the system shall...",
		color: "bg-green-100 text-green-800 border-green-300",
		icon: "◉",
	},
	optional: {
		label: "Optional",
		description: "Where <feature>, the system shall...",
		color: "bg-yellow-100 text-yellow-800 border-yellow-300",
		icon: "?",
	},
	complex: {
		label: "Complex",
		description: "Multiple conditions combined",
		color: "bg-orange-100 text-orange-800 border-orange-300",
		icon: "⊕",
	},
	unwanted: {
		label: "Unwanted",
		description: "If <condition>, the system shall not...",
		color: "bg-red-100 text-red-800 border-red-300",
		icon: "⊘",
	},
};

const sizeClasses = {
	sm: "text-xs px-2 py-0.5",
	md: "text-sm px-2.5 py-1",
	lg: "text-base px-3 py-1.5",
};

export function EARSPatternBadge({
	patternType,
	confidence,
	isWellFormed,
	showConfidence = false,
	size = "md",
	className,
}: EARSPatternBadgeProps) {
	const config = patternConfig[patternType];

	return (
		<div
			className={cn(
				"inline-flex items-center gap-1.5 rounded-md border font-medium",
				config.color,
				sizeClasses[size],
				className,
			)}
			title={config.description}
		>
			<span className="font-mono">{config.icon}</span>
			<span>{config.label}</span>
			{showConfidence && confidence !== undefined && (
				<span className="opacity-70">({Math.round(confidence * 100)}%)</span>
			)}
			{isWellFormed === false && (
				<span
					className="text-red-600"
					title="Requirement is not well-formed according to EARS syntax"
				>
					⚠
				</span>
			)}
		</div>
	);
}

interface EARSPatternDetailProps {
	patternType: EARSPatternType;
	trigger?: string | null;
	precondition?: string | null;
	postcondition?: string | null;
	systemName?: string | null;
	formalStructure?: string | null;
	suggestions?: string[];
	className?: string;
}

export function EARSPatternDetail({
	patternType,
	trigger,
	precondition,
	postcondition,
	systemName,
	formalStructure,
	suggestions,
	className,
}: EARSPatternDetailProps) {
	const config = patternConfig[patternType];

	return (
		<div className={cn("space-y-3 rounded-lg border p-4", className)}>
			<div className="flex items-center justify-between">
				<EARSPatternBadge patternType={patternType} size="lg" />
				<span className="text-sm text-muted-foreground">
					{config.description}
				</span>
			</div>

			<div className="grid gap-2 text-sm">
				{systemName && (
					<div className="flex gap-2">
						<span className="font-medium text-muted-foreground w-24">
							System:
						</span>
						<span>{systemName}</span>
					</div>
				)}
				{trigger && (
					<div className="flex gap-2">
						<span className="font-medium text-muted-foreground w-24">
							Trigger:
						</span>
						<span className="font-mono text-xs bg-muted px-2 py-1 rounded">
							{trigger}
						</span>
					</div>
				)}
				{precondition && (
					<div className="flex gap-2">
						<span className="font-medium text-muted-foreground w-24">
							Precondition:
						</span>
						<span className="font-mono text-xs bg-muted px-2 py-1 rounded">
							{precondition}
						</span>
					</div>
				)}
				{postcondition && (
					<div className="flex gap-2">
						<span className="font-medium text-muted-foreground w-24">
							Postcondition:
						</span>
						<span className="font-mono text-xs bg-muted px-2 py-1 rounded">
							{postcondition}
						</span>
					</div>
				)}
				{formalStructure && (
					<div className="flex gap-2">
						<span className="font-medium text-muted-foreground w-24">
							Formal:
						</span>
						<code className="text-xs bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
							{formalStructure}
						</code>
					</div>
				)}
			</div>

			{suggestions && suggestions.length > 0 && (
				<div className="border-t pt-3 mt-3">
					<p className="text-sm font-medium mb-2">Suggestions:</p>
					<ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
						{suggestions.map((suggestion, idx) => (
							<li key={idx}>{suggestion}</li>
						))}
					</ul>
				</div>
			)}
		</div>
	);
}
