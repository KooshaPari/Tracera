/**
 * HealthScoreRing - Animated ring chart showing overall health score
 * Displays breakdown by category with color-coded segments
 */

import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { cn } from "@/lib/utils";

interface HealthScoreRingProps {
	score: number; // 0-100
	categories?: {
		name: string;
		value: number;
		color: string;
	}[];
	showAnimation?: boolean;
	showLegend?: boolean;
	size?: number;
	className?: string;
}

const DEFAULT_CATEGORIES = [
	{ color: "#10b981", name: "Excellent", value: 0 },
	{ color: "#3b82f6", name: "Good", value: 0 },
	{ color: "#f59e0b", name: "Fair", value: 0 },
	{ color: "#ef4444", name: "Poor", value: 0 },
];

function getScoreColor(value: number) {
	if (value >= 90) {
		return "#10b981";
	} // Green
	if (value >= 70) {
		return "#3b82f6";
	} // Blue
	if (value >= 50) {
		return "#f59e0b";
	} // Amber
	return "#ef4444"; // Red
}

export function HealthScoreRing({
	score,
	categories,
	showAnimation = true,
	showLegend = true,
	size = 300,
	className,
}: HealthScoreRingProps) {
	const [animatedScore, setAnimatedScore] = useState(0);

	useEffect(() => {
		if (!showAnimation) {
			setAnimatedScore(score);
			return;
		}

		let current = 0;
		const target = score;
		const increment = target / 30; // Animate over ~500ms

		const interval = setInterval(() => {
			current += increment;
			if (current >= target) {
				setAnimatedScore(target);
				clearInterval(interval);
			} else {
				setAnimatedScore(Math.round(current));
			}
		}, 16); // ~60fps

		return () => clearInterval(interval);
	}, [score, showAnimation]);

	// Use provided categories or generate from score
	const data = categories || DEFAULT_CATEGORIES;

	const scoreColor = getScoreColor(animatedScore);

	return (
		<motion.div
			className={cn("flex flex-col items-center gap-6", className)}
			initial={{ opacity: 0, scale: 0.95 }}
			animate={{ opacity: 1, scale: 1 }}
			transition={{ duration: 0.5 }}
		>
			{/* Ring Chart */}
			<div style={{ height: size, width: size }}>
				<ResponsiveContainer width="100%" height="100%">
					<PieChart>
						<Pie
							data={[
								{ name: "Score", value: animatedScore },
								{ name: "Remaining", value: 100 - animatedScore },
							]}
							cx="50%"
							cy="50%"
							innerRadius={size / 2 - 40}
							outerRadius={size / 2}
							startAngle={180}
							endAngle={0}
							dataKey="value"
							stroke="none"
						>
							<Cell fill={scoreColor} />
							<Cell fill="hsl(var(--muted))" />
						</Pie>
					</PieChart>
				</ResponsiveContainer>

				{/* Center Text */}
				<div className="absolute inset-0 flex flex-col items-center justify-center">
					<motion.div
						initial={{ opacity: 0 }}
						animate={{ opacity: 1 }}
						transition={{ delay: 0.3 }}
						className="text-center"
					>
						<motion.div
							className="text-5xl font-bold"
							style={{ color: scoreColor }}
						>
							{animatedScore}%
						</motion.div>
						<div className="text-xs text-muted-foreground uppercase tracking-widest font-medium mt-1">
							Health Score
						</div>
					</motion.div>
				</div>
			</div>

			{/* Legend */}
			{showLegend && data.length > 0 && (
				<motion.div
					className="w-full grid grid-cols-2 gap-3"
					initial={{ opacity: 0, y: 10 }}
					animate={{ opacity: 1, y: 0 }}
					transition={{ delay: 0.4 }}
				>
					{data.map((item, idx) => (
						<div key={idx} className="flex items-center gap-2">
							<div
								className="w-3 h-3 rounded-full shrink-0"
								style={{ backgroundColor: item.color }}
							/>
							<span className="text-xs text-muted-foreground">{item.name}</span>
						</div>
					))}
				</motion.div>
			)}

			{/* Status Message */}
			<motion.div
				className="text-center text-sm"
				initial={{ opacity: 0 }}
				animate={{ opacity: 1 }}
				transition={{ delay: 0.5 }}
			>
				{animatedScore >= 90 && (
					<p className="text-green-600 font-medium">
						Excellent specification health!
					</p>
				)}
				{animatedScore >= 70 && animatedScore < 90 && (
					<p className="text-blue-600 font-medium">
						Good specification coverage.
					</p>
				)}
				{animatedScore >= 50 && animatedScore < 70 && (
					<p className="text-amber-600 font-medium">
						Consider improving specifications.
					</p>
				)}
				{animatedScore < 50 && (
					<p className="text-red-600 font-medium">
						Significant specification gaps detected.
					</p>
				)}
			</motion.div>
		</motion.div>
	);
}
