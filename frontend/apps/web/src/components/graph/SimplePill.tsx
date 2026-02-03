import { memo } from "react";
import type { Node, NodeProps } from "@xyflow/react";
import { ENHANCED_TYPE_COLORS } from "./types";

export interface SimplePillData extends Record<string, unknown> {
	id?: string;
	type?: string;
	label?: string;
	status?: string;
}

export const SimplePill = memo(function SimplePill({
	data,
}: NodeProps<Node<SimplePillData>>) {
	const typeColor = data.type
		? (ENHANCED_TYPE_COLORS[data.type] ?? "#64748b")
		: "#64748b";

	return (
		<div
			className="px-2 py-1 rounded-md border text-xs font-medium"
			style={{
				backgroundColor: typeColor + "20",
				borderColor: typeColor,
				color: typeColor,
			}}
		>
			{data.label ?? "Untitled"}
		</div>
	);
});
