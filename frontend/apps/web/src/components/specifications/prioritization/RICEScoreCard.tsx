/**
 * RICE Score Card Component
 * Reach, Impact, Confidence, Effort scoring for product prioritization
 */

import { useState } from "react";
import { cn } from "@/lib/utils";

interface RICEScore {
	reach: number;
	impact: number;
	confidence: number;
	effort: number;
	rice_score: number;
}

interface RICEScoreCardProps {
	initialValues?: Partial<RICEScore>;
	onCalculate?: (score: RICEScore) => void;
	readOnly?: boolean;
	className?: string;
}

const impactLevels = [
	{ value: 3, label: "Massive", description: "3x improvement" },
	{ value: 2, label: "High", description: "2x improvement" },
	{ value: 1, label: "Medium", description: "Notable improvement" },
	{ value: 0.5, label: "Low", description: "Minor improvement" },
	{ value: 0.25, label: "Minimal", description: "Barely noticeable" },
];

const confidenceLevels = [
	{ value: 100, label: "High", description: "Strong evidence" },
	{ value: 80, label: "Medium", description: "Some evidence" },
	{ value: 50, label: "Low", description: "Limited evidence" },
];

function getScoreColor(score: number): string {
	if (score >= 1000) return "text-green-600";
	if (score >= 500) return "text-blue-600";
	if (score >= 100) return "text-yellow-600";
	return "text-gray-600";
}

export function RICEScoreCard({
	initialValues,
	onCalculate,
	readOnly = false,
	className,
}: RICEScoreCardProps) {
	const [reach, setReach] = useState(initialValues?.reach ?? 1000);
	const [impact, setImpact] = useState(initialValues?.impact ?? 1);
	const [confidence, setConfidence] = useState(initialValues?.confidence ?? 80);
	const [effort, setEffort] = useState(initialValues?.effort ?? 1);

	// Calculate RICE score
	const riceScore =
		effort > 0 ? (reach * impact * (confidence / 100)) / effort : 0;

	const handleCalculate = () => {
		if (onCalculate) {
			onCalculate({
				reach,
				impact,
				confidence,
				effort,
				rice_score: riceScore,
			});
		}
	};

	return (
		<div className={cn("rounded-lg border p-4 space-y-4", className)}>
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h3 className="text-lg font-semibold">RICE Score</h3>
					<p className="text-sm text-muted-foreground">
						Reach × Impact × Confidence ÷ Effort
					</p>
				</div>
				<div className="text-right">
					<div className={cn("text-3xl font-bold", getScoreColor(riceScore))}>
						{riceScore.toFixed(0)}
					</div>
					<div className="text-sm text-muted-foreground">RICE Score</div>
				</div>
			</div>

			{/* Formula Display */}
			<div className="p-3 bg-muted rounded-lg text-sm">
				<div className="font-mono text-center">
					({reach} × {impact} × {confidence}%) ÷ {effort} ={" "}
					{riceScore.toFixed(0)}
				</div>
			</div>

			{/* Inputs */}
			<div className="space-y-4">
				{/* Reach */}
				<div className="space-y-1.5">
					<div className="flex justify-between text-sm">
						<span className="font-medium">Reach</span>
						<span className="font-mono">{reach.toLocaleString()}</span>
					</div>
					<p className="text-xs text-muted-foreground">
						Number of users/customers affected per time period
					</p>
					{!readOnly ? (
						<input
							type="number"
							value={reach}
							onChange={(e) =>
								setReach(Math.max(0, parseInt(e.target.value, 10) || 0))
							}
							className="w-full px-3 py-2 border rounded-md text-sm"
							min={0}
						/>
					) : (
						<div className="h-2 bg-muted rounded-full overflow-hidden">
							<div
								className="h-full bg-blue-500 rounded-full"
								style={{ width: `${Math.min((reach / 10000) * 100, 100)}%` }}
							/>
						</div>
					)}
				</div>

				{/* Impact */}
				<div className="space-y-1.5">
					<div className="flex justify-between text-sm">
						<span className="font-medium">Impact</span>
						<span className="font-mono">{impact}x</span>
					</div>
					<p className="text-xs text-muted-foreground">
						How much will this impact each user?
					</p>
					{!readOnly ? (
						<div className="flex gap-1">
							{impactLevels.map((level) => (
								<button
									key={level.value}
									onClick={() => setImpact(level.value)}
									className={cn(
										"flex-1 py-2 text-xs rounded border transition-colors",
										impact === level.value
											? "bg-primary text-primary-foreground border-primary"
											: "bg-muted hover:bg-muted/80 border-transparent",
									)}
									title={level.description}
								>
									{level.label}
								</button>
							))}
						</div>
					) : (
						<div className="text-sm">
							{impactLevels.find((l) => l.value === impact)?.label || impact}
						</div>
					)}
				</div>

				{/* Confidence */}
				<div className="space-y-1.5">
					<div className="flex justify-between text-sm">
						<span className="font-medium">Confidence</span>
						<span className="font-mono">{confidence}%</span>
					</div>
					<p className="text-xs text-muted-foreground">
						How confident are you in your estimates?
					</p>
					{!readOnly ? (
						<div className="flex gap-1">
							{confidenceLevels.map((level) => (
								<button
									key={level.value}
									onClick={() => setConfidence(level.value)}
									className={cn(
										"flex-1 py-2 text-xs rounded border transition-colors",
										confidence === level.value
											? "bg-primary text-primary-foreground border-primary"
											: "bg-muted hover:bg-muted/80 border-transparent",
									)}
									title={level.description}
								>
									{level.label}
								</button>
							))}
						</div>
					) : (
						<div className="h-2 bg-muted rounded-full overflow-hidden">
							<div
								className="h-full bg-green-500 rounded-full"
								style={{ width: `${confidence}%` }}
							/>
						</div>
					)}
				</div>

				{/* Effort */}
				<div className="space-y-1.5">
					<div className="flex justify-between text-sm">
						<span className="font-medium">Effort</span>
						<span className="font-mono">{effort} person-weeks</span>
					</div>
					<p className="text-xs text-muted-foreground">
						Estimated effort in person-weeks
					</p>
					{!readOnly ? (
						<input
							type="number"
							value={effort}
							onChange={(e) =>
								setEffort(Math.max(0.1, parseFloat(e.target.value) || 0.1))
							}
							className="w-full px-3 py-2 border rounded-md text-sm"
							min={0.1}
							step={0.5}
						/>
					) : (
						<div className="h-2 bg-muted rounded-full overflow-hidden">
							<div
								className="h-full bg-orange-500 rounded-full"
								style={{ width: `${Math.min((effort / 20) * 100, 100)}%` }}
							/>
						</div>
					)}
				</div>
			</div>

			{/* Calculate Button */}
			{!readOnly && onCalculate && (
				<button
					onClick={handleCalculate}
					className="w-full py-2 px-4 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Save RICE Score
				</button>
			)}
		</div>
	);
}

interface RICEScoreBadgeProps {
	score: number;
	size?: "sm" | "md" | "lg";
	className?: string;
}

export function RICEScoreBadge({
	score,
	size = "md",
	className,
}: RICEScoreBadgeProps) {
	const color =
		score >= 1000
			? "bg-green-100 text-green-700 border-green-300"
			: score >= 500
				? "bg-blue-100 text-blue-700 border-blue-300"
				: score >= 100
					? "bg-yellow-100 text-yellow-700 border-yellow-300"
					: "bg-gray-100 text-gray-700 border-gray-300";

	const sizeClass = {
		sm: "text-xs px-1.5 py-0.5",
		md: "text-sm px-2 py-1",
		lg: "text-base px-3 py-1.5",
	}[size];

	return (
		<span
			className={cn(
				"inline-flex items-center gap-1 rounded border font-medium",
				color,
				sizeClass,
				className,
			)}
		>
			<span>📊</span>
			<span>RICE: {score.toFixed(0)}</span>
		</span>
	);
}

interface RICEBreakdownProps {
	reach: number;
	impact: number;
	confidence: number;
	effort: number;
	className?: string;
}

export function RICEBreakdown({
	reach,
	impact,
	confidence,
	effort,
	className,
}: RICEBreakdownProps) {
	const score = effort > 0 ? (reach * impact * (confidence / 100)) / effort : 0;

	return (
		<div
			className={cn("grid grid-cols-5 gap-2 text-center text-sm", className)}
		>
			<div className="p-2 bg-blue-50 rounded">
				<div className="font-bold text-blue-700">{reach.toLocaleString()}</div>
				<div className="text-xs text-blue-600">Reach</div>
			</div>
			<div className="p-2 bg-purple-50 rounded">
				<div className="font-bold text-purple-700">{impact}x</div>
				<div className="text-xs text-purple-600">Impact</div>
			</div>
			<div className="p-2 bg-green-50 rounded">
				<div className="font-bold text-green-700">{confidence}%</div>
				<div className="text-xs text-green-600">Confidence</div>
			</div>
			<div className="p-2 bg-orange-50 rounded">
				<div className="font-bold text-orange-700">{effort}w</div>
				<div className="text-xs text-orange-600">Effort</div>
			</div>
			<div className="p-2 bg-primary/10 rounded">
				<div className="font-bold text-primary">{score.toFixed(0)}</div>
				<div className="text-xs text-primary/80">Score</div>
			</div>
		</div>
	);
}
