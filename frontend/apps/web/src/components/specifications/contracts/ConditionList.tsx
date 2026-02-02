import type { ContractCondition } from "@tracertm/types";
import { Card } from "@tracertm/ui";
import { AnimatePresence, motion } from "framer-motion";
import {
	AlertCircle,
	AlertTriangle,
	CheckCircle,
	Circle,
	Code,
	Shield,
} from "lucide-react";

interface ConditionListProps {
	preconditions?: ContractCondition[];
	postconditions?: ContractCondition[];
	invariants?: ContractCondition[];
	onConditionClick?: (condition: ContractCondition) => void;
	className?: string;
}

/**
 * Severity style configuration
 */
interface SeverityStyle {
	bg: string;
	text: string;
	icon: React.ComponentType<{ className?: string }>;
}

/**
 * Severity styles map
 */
interface ConditionSeverityStyleMap {
	critical: SeverityStyle;
	high: SeverityStyle;
	medium: SeverityStyle;
	low: SeverityStyle;
	[key: string]: SeverityStyle;
}

/**
 * Verification status icon map
 */
interface VerificationStatusIconMap {
	pass: React.ComponentType<{ className?: string }>;
	fail: React.ComponentType<{ className?: string }>;
	skip: React.ComponentType<{ className?: string }>;
	undefined: React.ComponentType<{ className?: string }>;
	[key: string]: React.ComponentType<{ className?: string }>;
}

const conditionSeverityStyles: ConditionSeverityStyleMap = {
	critical: {
		bg: "bg-red-500/10",
		text: "text-red-600",
		icon: AlertCircle,
	},
	high: {
		bg: "bg-orange-500/10",
		text: "text-orange-600",
		icon: AlertTriangle,
	},
	medium: {
		bg: "bg-yellow-500/10",
		text: "text-yellow-600",
		icon: Circle,
	},
	low: {
		bg: "bg-blue-500/10",
		text: "text-blue-600",
		icon: Circle,
	},
};

const verificationStatusIcons: VerificationStatusIconMap = {
	pass: CheckCircle,
	fail: AlertCircle,
	skip: Circle,
	undefined: Circle,
};

const verificationStatusColors: Record<string, string> = {
	pass: "text-green-600",
	fail: "text-red-600",
	skip: "text-gray-600",
	undefined: "text-gray-400",
};

interface ConditionItemProps {
	condition: ContractCondition;
	type: "precondition" | "postcondition" | "invariant";
	onClick?: () => void;
}

function ConditionItem({ condition, type, onClick }: ConditionItemProps) {
	const severity = (condition as ContractCondition & { severity?: string }).severity || "medium";
	const status = condition.lastVerifiedResult || "undefined";
	const StatusIcon = verificationStatusIcons[status] || Circle;
	const severityStyle = conditionSeverityStyles[severity];

	return (
		<motion.div
			initial={{ opacity: 0, x: -10 }}
			animate={{ opacity: 1, x: 0 }}
			exit={{ opacity: 0, x: -10 }}
			transition={{ duration: 0.2 }}
			className={`p-4 rounded-lg border transition-colors cursor-pointer hover:shadow-sm ${severityStyle?.bg}`}
			onClick={onClick}
		>
			<div className="space-y-3">
				{/* Header with Type, Severity, and Status */}
				<div className="flex items-start justify-between gap-3">
					<div className="flex items-center gap-2 flex-1 min-w-0">
						{/* Type Icon */}
						{type === "precondition" && (
							<Shield className="w-4 h-4 text-blue-600 flex-shrink-0" />
						)}
						{type === "postcondition" && (
							<Shield className="w-4 h-4 text-green-600 flex-shrink-0" />
						)}
						{type === "invariant" && (
							<Shield className="w-4 h-4 text-purple-600 flex-shrink-0" />
						)}

						{/* Condition Description */}
						<p
							className={`text-sm font-medium ${severityStyle?.text} truncate`}
						>
							{condition.description}
						</p>
					</div>

					{/* Verification Status */}
					<div className="flex items-center gap-1 flex-shrink-0">
						<StatusIcon
							className={`w-4 h-4 ${verificationStatusColors[status]}`}
							title={`Verification: ${status}`}
						/>
					</div>
				</div>

				{/* Expression (if available) */}
				{condition.expression && (
					<div className="bg-background/60 rounded border border-border/50 p-2 overflow-x-auto">
						<code className="text-xs font-mono text-muted-foreground whitespace-nowrap">
							{condition.expression}
						</code>
					</div>
				)}

				{/* Metadata Row */}
				<div className="flex items-center justify-between text-xs text-muted-foreground">
					<div className="flex items-center gap-2">
						{!condition.isRequired && (
							<span className="px-1.5 py-0.5 bg-yellow-500/10 text-yellow-600 rounded text-[10px] font-medium">
								Optional
							</span>
						)}
						<span className="flex items-center gap-1">
							<Code className="w-3 h-3" />
							{condition.expression ? "Expression" : "Descriptive"}
						</span>
					</div>
					{status !== "undefined" && (
						<span className={`font-medium ${verificationStatusColors[status]}`}>
							{status === "pass"
								? "✓ Verified"
								: status === "fail"
									? "✗ Failed"
									: "⊘ Skipped"}
						</span>
					)}
				</div>
			</div>
		</motion.div>
	);
}

export function ConditionList({
	preconditions,
	postconditions,
	invariants,
	onConditionClick,
	className = "",
}: ConditionListProps) {
	const hasAnyConditions =
		(preconditions?.length || 0) > 0 ||
		(postconditions?.length || 0) > 0 ||
		(invariants?.length || 0) > 0;

	if (!hasAnyConditions) {
		return (
			<Card className={`p-6 text-center text-muted-foreground ${className}`}>
				<Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
				<p className="text-sm">No conditions defined yet.</p>
				<p className="text-xs">
					Add preconditions, postconditions, or invariants to this contract.
				</p>
			</Card>
		);
	}

	return (
		<div className={`space-y-6 ${className}`}>
			{/* Preconditions Section */}
			{preconditions && preconditions.length > 0 && (
				<div className="space-y-3">
					<div className="flex items-center gap-2">
						<Shield className="w-4 h-4 text-blue-600" />
						<h3 className="font-semibold text-sm text-blue-600">
							Preconditions ({preconditions.length})
						</h3>
					</div>
					<div className="grid gap-3">
						<AnimatePresence mode="popLayout">
							{preconditions.map((condition) => (
								<ConditionItem
									key={condition.id}
									condition={condition}
									type="precondition"
									onClick={() => onConditionClick?.(condition)}
								/>
							))}
						</AnimatePresence>
					</div>
				</div>
			)}

			{/* Postconditions Section */}
			{postconditions && postconditions.length > 0 && (
				<div className="space-y-3">
					<div className="flex items-center gap-2">
						<Shield className="w-4 h-4 text-green-600" />
						<h3 className="font-semibold text-sm text-green-600">
							Postconditions ({postconditions.length})
						</h3>
					</div>
					<div className="grid gap-3">
						<AnimatePresence mode="popLayout">
							{postconditions.map((condition) => (
								<ConditionItem
									key={condition.id}
									condition={condition}
									type="postcondition"
									onClick={() => onConditionClick?.(condition)}
								/>
							))}
						</AnimatePresence>
					</div>
				</div>
			)}

			{/* Invariants Section */}
			{invariants && invariants.length > 0 && (
				<div className="space-y-3">
					<div className="flex items-center gap-2">
						<Shield className="w-4 h-4 text-purple-600" />
						<h3 className="font-semibold text-sm text-purple-600">
							Invariants ({invariants.length})
						</h3>
					</div>
					<div className="grid gap-3">
						<AnimatePresence mode="popLayout">
							{invariants.map((condition) => (
								<ConditionItem
									key={condition.id}
									condition={condition}
									type="invariant"
									onClick={() => onConditionClick?.(condition)}
								/>
							))}
						</AnimatePresence>
					</div>
				</div>
			)}
		</div>
	);
}
