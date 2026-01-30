import type React from "react";
import { useState, useEffect } from "react";
import { type VelocityDataPoint, calculateVelocity } from "@atoms/types";
import {
	BarChart,
	Bar,
	XAxis,
	YAxis,
	CartesianGrid,
	Tooltip,
	Legend,
	ResponsiveContainer,
	LineChart,
	Line,
	ComposedChart,
} from "recharts";

export interface VelocityChartProps {
	projectId: string;
	history?: VelocityDataPoint[];
	height?: number;
}

export const VelocityChart: React.FC<VelocityChartProps> = ({
	projectId,
	history = [],
	height = 300,
}) => {
	const [data, setData] = useState<any[]>([]);
	const [trend, setTrend] = useState<"improving" | "stable" | "declining">(
		"stable",
	);

	useEffect(() => {
		if (history.length === 0) {
			// Generate mock data for demo
			const mockData = Array.from({ length: 12 }, (_, i) => {
				const baseVelocity = 20 + Math.sin(i / 3) * 5;
				return {
					period: `Sprint ${i + 1}`,
					planned: Math.round(baseVelocity * (1 + Math.random() * 0.2)),
					completed: Math.round(baseVelocity + Math.random() * 5),
					velocity: Math.round(baseVelocity),
				};
			});
			setData(mockData);
		} else {
			const chartData = history.map((point) => ({
				period: point.periodLabel,
				planned: point.plannedPoints,
				completed: point.completedPoints,
				velocity: point.velocity,
			}));
			setData(chartData);

			// Determine trend
			if (chartData.length >= 3) {
				const recent = chartData.slice(-3).map((d) => d.velocity);
				const older = chartData.slice(-6, -3).map((d) => d.velocity);
				const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
				const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
				const percentChange = ((recentAvg - olderAvg) / olderAvg) * 100;

				if (percentChange > 10) {
					setTrend("improving");
				} else if (percentChange < -10) {
					setTrend("declining");
				} else {
					setTrend("stable");
				}
			}
		}
	}, [history]);

	const CustomTooltip = ({ active, payload }: any) => {
		if (active && payload && payload.length) {
			const data = payload[0].payload;
			return (
				<div className="bg-white dark:bg-gray-800 p-3 rounded shadow-lg border border-gray-200 dark:border-gray-700">
					<p className="text-sm font-medium text-gray-900 dark:text-gray-100">
						{data.period}
					</p>
					<p className="text-sm text-blue-600 dark:text-blue-400">
						Planned: {data.planned} points
					</p>
					<p className="text-sm text-green-600 dark:text-green-400">
						Completed: {data.completed} points
					</p>
					<p className="text-sm text-purple-600 dark:text-purple-400">
						Velocity: {data.velocity} points
					</p>
				</div>
			);
		}
		return null;
	};

	const trendColor =
		trend === "improving"
			? "#22c55e"
			: trend === "declining"
				? "#ef4444"
				: "#eab308";

	return (
		<div className="w-full">
			<div
				className="mb-4 p-3 rounded-lg"
				style={{
					backgroundColor: `${trendColor}20`,
					borderLeft: `4px solid ${trendColor}`,
				}}
			>
				<p
					className="text-sm font-medium capitalize"
					style={{ color: trendColor }}
				>
					Trend: {trend}
				</p>
			</div>

			<ResponsiveContainer width="100%" height={height}>
				<ComposedChart
					data={data}
					margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
				>
					<defs>
						<linearGradient id="colorPlanned" x1="0" y1="0" x2="0" y2="1">
							<stop offset="5%" stopColor="#93c5fd" stopOpacity={0.8} />
							<stop offset="95%" stopColor="#93c5fd" stopOpacity={0} />
						</linearGradient>
						<linearGradient id="colorCompleted" x1="0" y1="0" x2="0" y2="1">
							<stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
							<stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
						</linearGradient>
					</defs>
					<CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
					<XAxis
						dataKey="period"
						stroke="#6b7280"
						style={{ fontSize: "12px" }}
						angle={-45}
						textAnchor="end"
						height={80}
					/>
					<YAxis
						stroke="#6b7280"
						style={{ fontSize: "12px" }}
						label={{ value: "Points", angle: -90, position: "insideLeft" }}
					/>
					<Tooltip content={<CustomTooltip />} />
					<Legend wrapperStyle={{ paddingTop: "20px" }} />
					<Bar
						dataKey="planned"
						fill="#93c5fd"
						name="Planned Points"
						opacity={0.7}
					/>
					<Bar
						dataKey="completed"
						fill="#22c55e"
						name="Completed Points"
						opacity={0.7}
					/>
					<Line
						type="monotone"
						dataKey="velocity"
						stroke="#8b5cf6"
						strokeWidth={2}
						name="Velocity"
						yAxisId="right"
						dot={{ fill: "#8b5cf6", r: 4 }}
					/>
					<YAxis
						yAxisId="right"
						orientation="right"
						stroke="#6b7280"
						style={{ fontSize: "12px" }}
						label={{ value: "Velocity", angle: 90, position: "insideRight" }}
					/>
				</ComposedChart>
			</ResponsiveContainer>

			{/* Statistics */}
			<div className="mt-4 grid grid-cols-3 gap-4 text-sm">
				<div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
					<p className="text-blue-600 dark:text-blue-400 font-medium">
						Avg Velocity
					</p>
					<p className="text-blue-900 dark:text-blue-100 text-lg font-bold">
						{data.length > 0
							? Math.round(
									(data.reduce((sum, d) => sum + d.velocity, 0) / data.length) *
										10,
								) / 10
							: 0}
						points
					</p>
				</div>
				<div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
					<p className="text-green-600 dark:text-green-400 font-medium">
						Best Sprint
					</p>
					<p className="text-green-900 dark:text-green-100 text-lg font-bold">
						{data.length > 0 ? Math.max(...data.map((d) => d.velocity)) : 0}
						points
					</p>
				</div>
				<div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
					<p className="text-purple-600 dark:text-purple-400 font-medium">
						Sprints Tracked
					</p>
					<p className="text-purple-900 dark:text-purple-100 text-lg font-bold">
						{data.length}
					</p>
				</div>
			</div>
		</div>
	);
};

export default VelocityChart;
