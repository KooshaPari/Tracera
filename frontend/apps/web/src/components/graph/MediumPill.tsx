import { memo } from "react";
import type { Node, NodeProps } from "@xyflow/react";

export interface MediumPillData extends Record<string, unknown> {
	id?: string;
	type?: string;
	label?: string;
	status?: string;
}

export const MediumPill = memo(function MediumPill({
	data,
}: NodeProps<Node<MediumPillData>>) {
	const typeColors: Record<string, string> = {
		default: "#64748b",
		defect: "#ef4444",
		epic: "#8b5cf6",
		requirement: "#3b82f6",
		story: "#f59e0b",
		task: "#06b6d4",
		test: "#10b981",
	};

	const typeColor = data.type
		? (typeColors[data.type] ?? typeColors["default"])
		: typeColors["default"];

	return (
		<div className="px-3 py-2 rounded-lg border bg-card">
			<div className="flex items-center gap-2">
				<div
					className="w-2 h-2 rounded-full flex-shrink-0"
					style={{ backgroundColor: typeColor }}
				/>
				<span className="text-sm font-medium truncate max-w-[120px]">
					{data.label ?? "Untitled"}
				</span>
				{data.status && (
					<span className="text-[10px] px-1 rounded bg-muted flex-shrink-0">
						{data.status}
					</span>
				)}
			</div>
		</div>
	);
});
