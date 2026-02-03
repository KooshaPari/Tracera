import { memo } from "react";

interface GraphSkeletonProps {
	nodeCount?: number;
	edgeCount?: number;
}

export const GraphSkeleton = memo(function GraphSkeleton({
	nodeCount = 20,
	edgeCount = 30,
}: GraphSkeletonProps) {
	return (
		<div
			className="relative w-full h-full bg-background/50 animate-pulse"
			data-testid="graph-skeleton"
		>
			{/* Skeleton nodes */}
			{Array.from({ length: nodeCount }).map((_, i) => (
				<div
					key={`node-${i}`}
					className="absolute rounded-lg border bg-card"
					style={{
						height: "60px",
						left: `${Math.floor(i / 5) * 20 + 10}%`,
						top: `${(i % 5) * 20 + 10}%`,
						width: "120px",
					}}
				>
					<div className="p-3 space-y-2">
						<div className="h-4 bg-muted rounded w-3/4" />
						<div className="h-3 bg-muted/60 rounded w-1/2" />
					</div>
				</div>
			))}

			{/* Skeleton edges */}
			<svg className="absolute inset-0 pointer-events-none">
				{Array.from({ length: edgeCount }).map((_, i) => {
					const sourceIdx = i % nodeCount;
					const targetIdx = (i + 1) % nodeCount;
					return (
						<line
							key={`edge-${i}`}
							x1={`${Math.floor(sourceIdx / 5) * 20 + 15}%`}
							y1={`${(sourceIdx % 5) * 20 + 15}%`}
							x2={`${Math.floor(targetIdx / 5) * 20 + 15}%`}
							y2={`${(targetIdx % 5) * 20 + 15}%`}
							stroke="currentColor"
							strokeWidth="2"
							className="text-muted"
							opacity="0.3"
						/>
					);
				})}
			</svg>
		</div>
	);
});
