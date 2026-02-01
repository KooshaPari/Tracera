// Simple Node Pill - LOD-reduced node (label only, minimal DOM)
// Used when zoom is low or node count is high (B3 perf)

import { Handle, type Node, type NodeProps, Position } from "@xyflow/react";
import { memo } from "react";
import { ENHANCED_TYPE_COLORS } from "./types";

export interface SimpleNodePillData {
	id: string;
	type: string;
	label: string;
	status?: string;
	/** Optional; when provided, clicking selects/focuses */
	onSelect?: ((id: string) => void) | undefined;
	[key: string]: unknown;
}

function SimpleNodePillComponent({
	data,
	selected,
}: NodeProps<Node<SimpleNodePillData, "simplePill">>) {
	const bgColor = ENHANCED_TYPE_COLORS[data.type] ?? "#64748b";

	const handleClick = () => {
		data.onSelect?.(data.id);
	};

	return (
		<>
			<Handle
				type="target"
				position={Position.Left}
				className="!w-2 !h-2 !min-w-2 !min-h-2 !-left-1 !border-2"
				style={{ borderColor: bgColor, backgroundColor: "var(--background)" }}
			/>
			<div
				role="button"
				tabIndex={0}
				onClick={handleClick}
				onKeyDown={(e) => {
					if (e.key === "Enter" || e.key === " ") {
						e.preventDefault();
						handleClick();
					}
				}}
				className={`
					px-2 py-1 rounded-md text-xs font-medium truncate max-w-[140px]
					border transition-colors cursor-pointer
					${selected ? "ring-2 ring-primary ring-offset-2 ring-offset-background" : ""}
				`}
				style={{
					backgroundColor: `${bgColor}20`,
					borderColor: bgColor,
					color: "var(--foreground)",
				}}
				title={data.label}
			>
				{data.label}
			</div>
			<Handle
				type="source"
				position={Position.Right}
				className="!w-2 !h-2 !min-w-2 !min-h-2 !-right-1 !border-2"
				style={{ borderColor: bgColor, backgroundColor: "var(--background)" }}
			/>
		</>
	);
}

export const SimpleNodePill = memo(SimpleNodePillComponent);
