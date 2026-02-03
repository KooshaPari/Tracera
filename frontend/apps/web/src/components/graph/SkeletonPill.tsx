import type { Node, NodeProps } from "@xyflow/react";
import { memo } from "react";

export interface SkeletonPillData extends Record<string, unknown> {
	distance?: "near" | "medium" | "far";
	state?: "loading" | "error";
}

export const SkeletonPill = memo(function SkeletonPill({
	data,
}: NodeProps<Node<SkeletonPillData>>) {
	const typedData: SkeletonPillData = data as SkeletonPillData;
	const distance: SkeletonPillData["distance"] = typedData.distance ?? "near";
	const state: SkeletonPillData["state"] = typedData.state ?? "loading";

	if (state === "error") {
		return (
			<div className="px-3 py-2 rounded-lg border border-destructive bg-destructive/10">
				<span className="text-xs text-destructive">Failed to load</span>
			</div>
		);
	}

	// Loading skeleton - detail varies by distance
	if (distance === "near") {
		// Full detail skeleton (matches RichNodePill structure)
		return (
			<div className="px-4 py-3 rounded-lg border bg-card animate-pulse">
				<div className="h-4 bg-muted rounded w-24 mb-2" />
				<div className="h-3 bg-muted/60 rounded w-16" />
			</div>
		);
	} else if (distance === "medium") {
		// Medium skeleton
		return (
			<div className="px-3 py-2 rounded-lg border bg-card animate-pulse">
				<div className="h-3 bg-muted rounded w-20" />
			</div>
		);
	}
	// Far skeleton (minimal)
	return <div className="w-4 h-4 rounded-full bg-muted animate-pulse" />;
});
