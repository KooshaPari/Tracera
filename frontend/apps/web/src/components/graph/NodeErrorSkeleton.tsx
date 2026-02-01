// Graph node error skeleton — LOD-shaped (Phase 3, 2.2)
// Renders an error placeholder by lodLevel: dot → minimal pill → compact pill → full pill/card + retry

import { Button } from "@tracertm/ui/components/Button";
import { Handle, type Node, type NodeProps, Position } from "@xyflow/react";
import { AlertCircle } from "lucide-react";
import { memo } from "react";
import { LODLevel } from "./utils/lod";

export interface NodeErrorSkeletonData {
	id: string;
	lodLevel?: number;
	errorMessage?: string;
	onRetry?: ((id: string) => void) | undefined;
	[key: string]: unknown;
}

function NodeErrorSkeletonComponent({
	data,
}: NodeProps<Node<NodeErrorSkeletonData, "nodeError">>) {
	const lod = (data.lodLevel ?? LODLevel.VeryClose) as LODLevel;
	const message =
		data.errorMessage ??
		(typeof data.error === "string" ? data.error : "Error");
	const onRetry = data.onRetry;

	return (
		<>
			<Handle
				type="target"
				position={Position.Left}
				className="!w-2 !h-2 !min-w-2 !min-h-2 !-left-1 !border-2 !border-destructive/50"
			/>
			<LodErrorShape lod={lod} message={message} nodeId={data.id} onRetry={onRetry} />
			<Handle
				type="source"
				position={Position.Right}
				className="!w-2 !h-2 !min-w-2 !min-h-2 !-right-1 !border-2 !border-destructive/50"
			/>
		</>
	);
}

function LodErrorShape({
	lod,
	message,
	nodeId,
	onRetry,
}: {
	lod: LODLevel;
	message: string;
	nodeId: string;
	onRetry?: (id: string) => void;
}) {
	switch (lod) {
		case LODLevel.VeryFar:
			return (
				<div
					className="h-2 w-2 min-w-2 min-h-2 rounded-full bg-destructive/80"
					title={message}
				/>
			);
		case LODLevel.Far:
			return (
				<div
					className="h-2 w-4 min-w-[8px] rounded bg-destructive/60"
					title={message}
				/>
			);
		case LODLevel.Medium:
			return (
				<div
					className="flex items-center gap-0.5 px-1.5 py-0.5 rounded-md bg-destructive/10 border border-destructive/30 text-destructive"
					title={message}
				>
					<AlertCircle className="h-3 w-3 shrink-0" />
					<span className="text-[10px] truncate max-w-[60px]">Error</span>
				</div>
			);
		case LODLevel.Close:
		case LODLevel.VeryClose:
		default:
			return (
				<div className="px-2 py-1.5 rounded-md bg-destructive/10 border border-destructive/30 text-destructive text-xs max-w-[160px]">
					<div className="flex items-center gap-1 mb-1">
						<AlertCircle className="h-3.5 w-3.5 shrink-0" />
						<span className="font-medium truncate">Error</span>
					</div>
					<p className="text-[10px] text-muted-foreground line-clamp-2 mb-1">
						{message}
					</p>
					{onRetry && (
						<Button
							variant="outline"
							size="sm"
							className="h-5 px-1.5 text-[10px]"
							onClick={() => onRetry(nodeId)}
						>
							Retry
						</Button>
					)}
				</div>
			);
	}
}

export const NodeErrorSkeleton = memo(NodeErrorSkeletonComponent);
