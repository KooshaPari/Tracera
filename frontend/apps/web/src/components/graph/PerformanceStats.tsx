import { memo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Activity, Cpu, Database, Zap } from "lucide-react";

interface PerformanceStatsProps {
	fps: number;
	nodeCount: number;
	edgeCount: number;
	visibleNodeCount: number;
	visibleEdgeCount: number;
	memoryUsage?: number; // MB
	renderTime?: number; // Ms
	variant?: "compact" | "detailed";
}

export const PerformanceStats = memo(function PerformanceStats({
	fps,
	nodeCount,
	edgeCount,
	visibleNodeCount,
	visibleEdgeCount,
	memoryUsage,
	renderTime,
	variant = "compact",
}: PerformanceStatsProps) {
	const cullPercentage = Math.round((1 - visibleNodeCount / nodeCount) * 100);

	const fpsColor =
		fps >= 55
			? "text-green-600"
			: (fps >= 30
				? "text-yellow-600"
				: "text-red-600");

	if (variant === "compact") {
		return (
			<div className="flex items-center gap-2 text-xs">
				<Badge variant="outline" className={fpsColor}>
					{Math.round(fps)} FPS
				</Badge>
				<span className="text-muted-foreground">
					{visibleNodeCount}/{nodeCount} nodes
				</span>
				{cullPercentage > 0 && (
					<span className="text-green-600">{cullPercentage}% culled</span>
				)}
			</div>
		);
	}

	return (
		<Card className="w-64">
			<CardHeader className="pb-3">
				<CardTitle className="text-sm flex items-center gap-2">
					<Activity className="h-4 w-4" />
					Performance
				</CardTitle>
			</CardHeader>
			<CardContent className="space-y-3">
				{/* FPS */}
				<div className="space-y-1">
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground">Frame Rate</span>
						<span className={`font-medium ${fpsColor}`}>
							{Math.round(fps)} FPS
						</span>
					</div>
					<Progress value={(fps / 60) * 100} className="h-1" />
				</div>

				{/* Nodes */}
				<div className="space-y-1">
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground flex items-center gap-1">
							<Database className="h-3 w-3" />
							Nodes
						</span>
						<span className="font-medium">
							{visibleNodeCount}/{nodeCount}
						</span>
					</div>
					<Progress
						value={(visibleNodeCount / nodeCount) * 100}
						className="h-1"
					/>
				</div>

				{/* Edges */}
				<div className="space-y-1">
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground">Edges</span>
						<span className="font-medium">
							{visibleEdgeCount}/{edgeCount}
						</span>
					</div>
					<Progress
						value={(visibleEdgeCount / edgeCount) * 100}
						className="h-1"
					/>
				</div>

				{/* Culling Efficiency */}
				{cullPercentage > 0 && (
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground flex items-center gap-1">
							<Zap className="h-3 w-3" />
							Culling
						</span>
						<span className="font-medium text-green-600">
							{cullPercentage}%
						</span>
					</div>
				)}

				{/* Memory */}
				{memoryUsage !== undefined && (
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground flex items-center gap-1">
							<Cpu className="h-3 w-3" />
							Memory
						</span>
						<span className="font-medium">{memoryUsage.toFixed(1)} MB</span>
					</div>
				)}

				{/* Render Time */}
				{renderTime !== undefined && (
					<div className="flex justify-between text-xs">
						<span className="text-muted-foreground">Render</span>
						<span className="font-medium">{renderTime.toFixed(1)} ms</span>
					</div>
				)}
			</CardContent>
		</Card>
	);
});
