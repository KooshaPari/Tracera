// Branch Explorer - Tree visualization of branch structure
// Shows branch hierarchy, status indicators, and merge operations

import { cn } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	AlertCircle,
	ChevronRight,
	GitBranch,
	GitMerge,
	Plus,
	Trash2,
} from "lucide-react";
import { useMemo, useState } from "react";
import type { Branch } from "./TemporalNavigator";

export interface BranchExplorerProps {
	projectId: string;
	branches: Branch[];
	currentBranchId: string;
	onBranchChange: (branchId: string) => void;
	onMergeRequest?: (sourceBranchId: string, targetBranchId: string) => void;
	onBranchCreate?: () => void;
}

export function BranchExplorer({
	projectId,
	branches,
	currentBranchId,
	onBranchChange,
	onMergeRequest,
	onBranchCreate,
}: BranchExplorerProps) {
	const [expandedBranches, setExpandedBranches] = useState<Set<string>>(
		new Set([currentBranchId]),
	);
	const [mergeSource, setMergeSource] = useState<string | null>(null);

	const branchTree = useMemo(() => {
		const tree = new Map<string | null, Branch[]>();

		branches.forEach((branch) => {
			const parent = branch.parentId || null;
			if (!tree.has(parent)) {
				tree.set(parent, []);
			}
			tree.get(parent)!.push(branch);
		});

		return tree;
	}, [branches]);

	const getStatusColor = (status: Branch["status"]) => {
		switch (status) {
			case "active":
				return "bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-300";
			case "review":
				return "bg-orange-100 dark:bg-orange-900/20 text-orange-700 dark:text-orange-300";
			case "merged":
				return "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300";
			case "abandoned":
				return "bg-red-100 dark:bg-red-900/20 text-red-700 dark:text-red-300";
			default:
				return "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300";
		}
	};

	const toggleExpanded = (branchId: string) => {
		const newExpanded = new Set(expandedBranches);
		if (newExpanded.has(branchId)) {
			newExpanded.delete(branchId);
		} else {
			newExpanded.add(branchId);
		}
		setExpandedBranches(newExpanded);
	};

	const renderBranchNode = (branch: Branch, depth: number) => {
		const isCurrentBranch = branch.id === currentBranchId;
		const hasChildren =
			branchTree.has(branch.id) && branchTree.get(branch.id)!.length > 0;
		const isExpanded = expandedBranches.has(branch.id);
		const isMergeSource = mergeSource === branch.id;
		const paddingPx = 12 + depth * 16;

		return (
			<div key={branch.id}>
				<div
					className={cn(
						"flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors group",
						isCurrentBranch
							? "bg-blue-100 dark:bg-blue-900/20"
							: "hover:bg-gray-100 dark:hover:bg-gray-800",
					)}
					style={{ paddingLeft: paddingPx }}
				>
					{hasChildren && (
						<Button
							variant="ghost"
							size="sm"
							className="w-5 h-5 p-0"
							onClick={() => toggleExpanded(branch.id)}
						>
							<ChevronRight
								className={cn(
									"w-4 h-4 transition-transform",
									isExpanded && "rotate-90",
								)}
							/>
						</Button>
					)}
					{!hasChildren && <div className="w-5" />}

					<GitBranch
						className={cn(
							"w-4 h-4",
							branch.status === "active"
								? "text-green-600 dark:text-green-400"
								: "text-gray-600 dark:text-gray-400",
						)}
					/>

					<div
						className="flex-1 min-w-0"
						onClick={() => onBranchChange(branch.id)}
						onKeyDown={(e) => {
							if (e.key === "Enter") onBranchChange(branch.id);
						}}
						role="button"
						tabIndex={0}
					>
						<div className="flex items-center gap-2">
							<span className="font-medium text-sm text-gray-900 dark:text-gray-100 truncate">
								{branch.name}
							</span>
							<Badge
								variant="outline"
								className={cn("text-xs", getStatusColor(branch.status))}
							>
								{branch.status}
							</Badge>
						</div>
						{branch.description && (
							<p className="text-xs text-gray-600 dark:text-gray-400 truncate">
								{branch.description}
							</p>
						)}
					</div>

					<div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
						{mergeSource && mergeSource !== branch.id && onMergeRequest && (
							<Button
								size="sm"
								variant="outline"
								className="gap-1 text-xs"
								onClick={() => {
									onMergeRequest(mergeSource, branch.id);
									setMergeSource(null);
								}}
								title="Merge source branch into this branch"
							>
								<GitMerge className="w-3 h-3" />
								Merge
							</Button>
						)}

						{!isMergeSource && onMergeRequest && (
							<Button
								size="sm"
								variant="ghost"
								className="w-7 h-7 p-0"
								onClick={() => setMergeSource(branch.id)}
								title="Use as merge source"
							>
								<GitMerge className="w-3 h-3" />
							</Button>
						)}

						{isMergeSource && (
							<Button
								size="sm"
								variant="ghost"
								className="w-7 h-7 p-0 text-orange-600 dark:text-orange-400"
								onClick={() => setMergeSource(null)}
								title="Cancel merge"
							>
								<AlertCircle className="w-3 h-3" />
							</Button>
						)}

						{branch.status === "abandoned" && (
							<Button
								size="sm"
								variant="ghost"
								className="w-7 h-7 p-0 text-red-600 dark:text-red-400"
								title="Delete abandoned branch"
							>
								<Trash2 className="w-3 h-3" />
							</Button>
						)}
					</div>
				</div>

				{isExpanded && hasChildren && (
					<div>
						{branchTree
							.get(branch.id)!
							.map((child) => renderBranchNode(child, depth + 1))}
					</div>
				)}
			</div>
		);
	};

	const rootBranches = branchTree.get(null) || [];

	return (
		<div className="flex flex-col gap-3 p-4 bg-white dark:bg-gray-950">
			{onBranchCreate && (
				<div className="flex items-center justify-between">
					<h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
						Branches
					</h3>
					<Button
						size="sm"
						variant="outline"
						onClick={onBranchCreate}
						className="gap-1 text-xs"
					>
						<Plus className="w-3 h-3" />
						New Branch
					</Button>
				</div>
			)}

			{mergeSource && (
				<div className="flex items-center gap-2 p-2 bg-orange-50 dark:bg-orange-900/10 border border-orange-200 dark:border-orange-800 rounded text-xs text-orange-700 dark:text-orange-300">
					<AlertCircle className="w-3 h-3 flex-shrink-0" />
					<span>
						Merging from {branches.find((b) => b.id === mergeSource)?.name}
					</span>
					<Button
						size="sm"
						variant="ghost"
						className="ml-auto h-5 p-0 text-xs"
						onClick={() => setMergeSource(null)}
					>
						Cancel
					</Button>
				</div>
			)}

			<div className="space-y-0 max-h-96 overflow-y-auto">
				{rootBranches.length > 0 ? (
					rootBranches.map((branch) => renderBranchNode(branch, 0))
				) : (
					<div className="flex items-center justify-center py-8 text-gray-500 dark:text-gray-400 text-sm">
						No branches found
					</div>
				)}
			</div>

			{branches.length > 0 && (
				<div className="border-t border-gray-200 dark:border-gray-800 pt-3 space-y-1 text-xs text-gray-600 dark:text-gray-400">
					<div className="flex justify-between">
						<span>Active:</span>
						<span className="font-medium">
							{branches.filter((b) => b.status === "active").length}
						</span>
					</div>
					<div className="flex justify-between">
						<span>In Review:</span>
						<span className="font-medium">
							{branches.filter((b) => b.status === "review").length}
						</span>
					</div>
					<div className="flex justify-between">
						<span>Total:</span>
						<span className="font-medium">{branches.length}</span>
					</div>
				</div>
			)}
		</div>
	);
}
