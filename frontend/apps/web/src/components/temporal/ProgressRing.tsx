import type React from "react";
import { useMemo } from "react";

export interface ProgressRingProps {
	percentage: number;
	radius?: number;
	strokeWidth?: number;
	size?: "sm" | "md" | "lg";
	animated?: boolean;
	showLabel?: boolean;
	color?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
	percentage,
	radius = 45,
	strokeWidth = 4,
	size = "md",
	animated = true,
	showLabel = true,
	color,
}) => {
	// Adjust radius and stroke based on size
	const sizeMap = {
		sm: { radius: 30, strokeWidth: 3, fontSize: "12px" },
		md: { radius: 45, strokeWidth: 4, fontSize: "16px" },
		lg: { radius: 60, strokeWidth: 5, fontSize: "24px" },
	};

	const config = sizeMap[size];
	const normalizedRadius = config.radius;
	const circumference = normalizedRadius * 2 * Math.PI;
	const offset = circumference - (percentage / 100) * circumference;

	// Determine color based on percentage
	let ringColor = color;
	if (!ringColor) {
		if (percentage >= 75) {
			ringColor = "#22c55e"; // green
		} else if (percentage >= 50) {
			ringColor = "#3b82f6"; // blue
		} else if (percentage >= 25) {
			ringColor = "#eab308"; // yellow
		} else {
			ringColor = "#ef4444"; // red
		}
	}

	return (
		<div className="flex items-center justify-center">
			<div className="relative inline-flex items-center justify-center">
				<svg
					height={normalizedRadius * 2 + 10}
					width={normalizedRadius * 2 + 10}
					className="transform -rotate-90"
				>
					{/* Background circle */}
					<circle
						stroke="#e5e7eb"
						fill="none"
						strokeWidth={config.strokeWidth}
						r={normalizedRadius}
						cx={normalizedRadius + 5}
						cy={normalizedRadius + 5}
						className="dark:stroke-gray-700"
					/>
					{/* Progress circle */}
					<circle
						stroke={ringColor}
						fill="none"
						strokeWidth={config.strokeWidth}
						strokeDasharray={circumference + " " + circumference}
						strokeDashoffset={offset}
						strokeLinecap="round"
						r={normalizedRadius}
						cx={normalizedRadius + 5}
						cy={normalizedRadius + 5}
						style={{
							transition: animated ? "stroke-dashoffset 0.5s ease" : "none",
							filter: "drop-shadow(0 1px 2px rgba(0, 0, 0, 0.1))",
						}}
					/>
				</svg>

				{/* Center label */}
				{showLabel && (
					<div className="absolute flex flex-col items-center justify-center">
						<span
							style={{ fontSize: config.fontSize, fontWeight: "600" }}
							className="text-gray-900 dark:text-gray-100"
						>
							{Math.round(percentage)}%
						</span>
					</div>
				)}
			</div>
		</div>
	);
};

export interface ProgressBarProps {
	percentage: number;
	height?: "sm" | "md" | "lg";
	showLabel?: boolean;
	color?: string;
	animated?: boolean;
	className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
	percentage,
	height = "md",
	showLabel = true,
	color,
	animated = true,
	className = "",
}) => {
	const heightMap = {
		sm: "h-1",
		md: "h-2",
		lg: "h-3",
	};

	// Determine color based on percentage
	let barColor = color;
	if (!barColor) {
		if (percentage >= 75) {
			barColor = "bg-green-500";
		} else if (percentage >= 50) {
			barColor = "bg-blue-500";
		} else if (percentage >= 25) {
			barColor = "bg-yellow-500";
		} else {
			barColor = "bg-red-500";
		}
	}

	return (
		<div className={className}>
			<div
				className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden ${heightMap[height]}`}
			>
				<div
					className={`${barColor} ${heightMap[height]} rounded-full ${animated ? "transition-all duration-500" : ""}`}
					style={{ width: `${Math.min(Math.max(percentage, 0), 100)}%` }}
				/>
			</div>
			{showLabel && (
				<p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
					{Math.round(percentage)}%
				</p>
			)}
		</div>
	);
};

export interface LinearProgressProps {
	value: number;
	max: number;
	label?: string;
	color?: string;
	showLabel?: boolean;
}

export const LinearProgress: React.FC<LinearProgressProps> = ({
	value,
	max,
	label,
	color,
	showLabel = true,
}) => {
	const percentage = (value / max) * 100;

	return (
		<div className="space-y-2">
			{(label || showLabel) && (
				<div className="flex items-center justify-between text-sm">
					{label && (
						<span className="font-medium text-gray-700 dark:text-gray-300">
							{label}
						</span>
					)}
					{showLabel && (
						<span className="text-gray-600 dark:text-gray-400">
							{value}/{max}
						</span>
					)}
				</div>
			)}
			<ProgressBar
				percentage={percentage}
				height="md"
				showLabel={false}
				color={color}
			/>
		</div>
	);
};

export default ProgressRing;
