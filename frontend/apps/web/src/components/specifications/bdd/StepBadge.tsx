import { Badge, cn } from "@tracertm/ui";
import { AlertCircle, CheckCircle2, GitBranch, Zap } from "lucide-react";

export type StepType = "Given" | "When" | "Then" | "And" | "But" | "Background";

interface StepBadgeProps {
	type: StepType;
	className?: string;
	compact?: boolean;
}

const stepConfig: Record<
	StepType,
	{
		color: string;
		bgColor: string;
		icon: React.ComponentType<{ className?: string }>;
		description: string;
	}
> = {
	Given: {
		color: "bg-blue-500/10 text-blue-600 border-blue-500/20",
		bgColor: "bg-blue-500/5",
		icon: AlertCircle,
		description: "Precondition",
	},
	When: {
		color: "bg-amber-500/10 text-amber-600 border-amber-500/20",
		bgColor: "bg-amber-500/5",
		icon: Zap,
		description: "Action",
	},
	Then: {
		color: "bg-green-500/10 text-green-600 border-green-500/20",
		bgColor: "bg-green-500/5",
		icon: CheckCircle2,
		description: "Outcome",
	},
	And: {
		color: "bg-gray-500/10 text-gray-600 border-gray-500/20",
		bgColor: "bg-gray-500/5",
		icon: GitBranch,
		description: "Additional",
	},
	But: {
		color: "bg-gray-500/10 text-gray-600 border-gray-500/20",
		bgColor: "bg-gray-500/5",
		icon: GitBranch,
		description: "Alternative",
	},
	Background: {
		color: "bg-purple-500/10 text-purple-600 border-purple-500/20",
		bgColor: "bg-purple-500/5",
		icon: GitBranch,
		description: "Setup",
	},
};

export function StepBadge({
	type,
	className,
	compact = false,
}: StepBadgeProps) {
	const config = stepConfig[type];
	const Icon = config.icon;

	if (compact) {
		return (
			<Badge
				variant="outline"
				className={cn(
					config.color,
					"flex items-center gap-1 font-medium text-xs",
					className,
				)}
				title={config.description}
			>
				<Icon className="w-3 h-3" />
				{type}
			</Badge>
		);
	}

	return (
		<div
			className={cn(
				"inline-flex items-center gap-2 px-2.5 py-1 rounded-md border",
				config.color,
				className,
			)}
		>
			<Icon className="w-4 h-4 flex-shrink-0" />
			<span className="font-medium text-sm">{type}</span>
			<span className="text-xs opacity-75">({config.description})</span>
		</div>
	);
}
