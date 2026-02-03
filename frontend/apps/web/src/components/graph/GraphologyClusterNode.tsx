import { memo } from "react";
import type { NodeProps } from "@xyflow/react";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { ChevronDown, ChevronUp } from "lucide-react";

interface ClusterNodeData {
	label: string;
	size: number; // Number of nodes in cluster
	memberIds: string[];
	color?: string;
	onExpand?: (clusterId: string) => void;
	onCollapse?: (clusterId: string) => void;
	isExpanded?: boolean;
}

export const GraphologyClusterNode = memo(function GraphologyClusterNode({
	id,
	data,
}: NodeProps<ClusterNodeData>) {
	const handleToggle = () => {
		if (data.isExpanded && data.onCollapse) {
			data.onCollapse(id);
		} else if (!data.isExpanded && data.onExpand) {
			data.onExpand(id);
		}
	};

	return (
		<div
			className="px-4 py-3 rounded-lg border-2 bg-card shadow-md"
			style={{
				borderColor: data.color || "#64748b",
				minWidth: "120px",
			}}
		>
			<div className="flex items-center justify-between gap-2">
				<div>
					<div className="font-semibold text-sm">{data.label}</div>
					<Badge variant="secondary" className="mt-1 text-xs">
						{data.size} nodes
					</Badge>
				</div>

				<Button
					size="sm"
					variant="ghost"
					onClick={handleToggle}
					className="h-6 w-6 p-0"
				>
					{data.isExpanded ? (
						<ChevronUp className="h-4 w-4" />
					) : (
						<ChevronDown className="h-4 w-4" />
					)}
				</Button>
			</div>
		</div>
	);
});
