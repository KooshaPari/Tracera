import type { BurndownDataPoint, Sprint } from "@atoms/types";
import type React from "react";
import { useMemo } from "react";
import {
	CartesianGrid,
	Legend,
	Line,
	LineChart,
	ResponsiveContainer,
	Tooltip,
	XAxis,
	YAxis,
} from "recharts";

export interface BurndownChartProps {
	sprint: Sprint;
	data?: BurndownDataPoint[];
	height?: number;
}

function BurndownCustomTooltip({
	active,
	payload,
}: {
	active?: boolean;
	payload?: Array<{ payload: { date: string; ideal: number; actual: number; completed?: number } }>;
}) {
	if (active && payload && payload.length) {
		const first = payload[0];
		const data = first?.payload;
		if (!data) return null;
		return (
			<div className="bg-white dark:bg-gray-800 p-3 rounded shadow-lg border border-gray-200 dark:border-gray-700">
				<p className="text-sm font-medium text-gray-900 dark:text-gray-100">
					{data.date}
				</p>
				<p className="text-sm text-blue-600 dark:text-blue-400">
					Ideal: {data.ideal} points
				</p>
				<p className="text-sm text-red-600 dark:text-red-400">
					Actual: {data.actual} points
				</p>
				{data.completed !== undefined && (
					<p className="text-sm text-green-600 dark:text-green-400">
						Completed: {data.completed} points
					</p>
				)}
			</div>
		);
	}
	return null;
}

export const BurndownChart: React.FC<BurndownChartProps> = ({
	sprint,
	data = [],
	height = 300,
}) => {
	const chartData = useMemo(() => {
		if (data.length === 0) {
			// Generate mock data for demo
			const days = Math.ceil(
				(new Date(sprint.endDate).getTime() -
					new Date(sprint.startDate).getTime()) /
					(1000 * 60 * 60 * 24),
			);
			const mockData: Array<{
				day: number;
				date: string;
				ideal: number;
				actual: number;
			}> = [];

			for (let i = 0; i <= days; i++) {
				const idealRemaining = Math.max(
					sprint.plannedPoints * ((days - i) / days),
					0,
				);
				const actualRemaining = Math.max(
					sprint.plannedPoints - sprint.completedPoints * (i / days),
					0,
				);

				mockData.push({
					day: i,
					date: new Date(sprint.startDate).toLocaleDateString("en-US", {
						month: "short",
						day: "numeric",
					}),
					ideal: Math.round(idealRemaining),
					actual: Math.round(actualRemaining),
				});
			}

			return mockData;
		}

		return data.map((point, index) => ({
			day: index,
			date: new Date(point.date).toLocaleDateString("en-US", {
				month: "short",
				day: "numeric",
			}),
			ideal: point.idealPoints,
			actual: point.remainingPoints,
			completed: point.completedPoints,
		}));
	}, [sprint, data]);

	return (
		<div className="w-full">
			<ResponsiveContainer width="100%" height={height}>
				<LineChart
					data={chartData}
					margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
				>
					<defs>
						<linearGradient id="colorIdeal" x1="0" y1="0" x2="0" y2="1">
							<stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
							<stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
						</linearGradient>
						<linearGradient id="colorActual" x1="0" y1="0" x2="0" y2="1">
							<stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
							<stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
						</linearGradient>
					</defs>
					<CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
					<XAxis dataKey="date" stroke="#6b7280" style={{ fontSize: "12px" }} />
					<YAxis
						stroke="#6b7280"
						style={{ fontSize: "12px" }}
						label={{
							value: "Points Remaining",
							angle: -90,
							position: "insideLeft",
						}}
					/>
					<Tooltip content={<BurndownCustomTooltip />} />
					<Legend wrapperStyle={{ paddingTop: "20px" }} iconType="line" />
					<Line
						type="monotone"
						dataKey="ideal"
						stroke="#3b82f6"
						strokeWidth={2}
						dot={false}
						name="Ideal Burndown"
						isAnimationActive={false}
					/>
					<Line
						type="monotone"
						dataKey="actual"
						stroke="#ef4444"
						strokeWidth={2}
						dot={false}
						name="Actual Progress"
						isAnimationActive={false}
					/>
				</LineChart>
			</ResponsiveContainer>

			{/* Status Summary */}
			<div className="mt-4 grid grid-cols-3 gap-4 text-sm">
				<div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
					<p className="text-blue-600 dark:text-blue-400 font-medium">
						Ideal Rate
					</p>
					<p className="text-blue-900 dark:text-blue-100 text-lg font-bold">
						{sprint.plannedPoints > 0
							? Math.round(
									(sprint.plannedPoints /
										Math.max(
											Math.ceil(
												(new Date(sprint.endDate).getTime() -
													new Date(sprint.startDate).getTime()) /
													(1000 * 60 * 60 * 24),
											),
											1,
										)) *
										10,
								) / 10
							: 0}
						points/day
					</p>
				</div>
				<div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
					<p className="text-red-600 dark:text-red-400 font-medium">
						Current Rate
					</p>
					<p className="text-red-900 dark:text-red-100 text-lg font-bold">
						{sprint.completedPoints > 0
							? Math.round(
									(sprint.completedPoints /
										Math.max(
											Math.ceil(
												(Date.now() - new Date(sprint.startDate).getTime()) /
													(1000 * 60 * 60 * 24),
											),
											1,
										)) *
										10,
								) / 10
							: 0}
						points/day
					</p>
				</div>
				<div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
					<p className="text-green-600 dark:text-green-400 font-medium">
						Remaining
					</p>
					<p className="text-green-900 dark:text-green-100 text-lg font-bold">
						{sprint.remainingPoints} points
					</p>
				</div>
			</div>
		</div>
	);
};

export default BurndownChart;
