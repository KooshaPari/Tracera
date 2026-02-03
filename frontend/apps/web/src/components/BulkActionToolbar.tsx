import { Trash2, X } from "lucide-react";
import { useCallback } from "react";

import { cn } from "@/lib/utils";
import { logger } from "@/lib/logger";

export interface BulkAction {
	id: string;
	label: string;
	icon: React.ReactNode;
	action: (selectedIds: string[]) => Promise<void> | void;
	variant?: "default" | "destructive";
	disabled?: boolean;
}

interface BulkActionToolbarProps {
	selectedCount: number;
	totalCount: number;
	onSelectAll: () => void;
	onSelectNone: () => void;
	actions: BulkAction[];
	loading?: boolean;
	onActionComplete?: (actionId: string) => void;
}

export function BulkActionToolbar({
	selectedCount,
	totalCount,
	onSelectAll,
	onSelectNone,
	actions,
	loading = false,
	onActionComplete,
}: BulkActionToolbarProps) {
	const handleAction = useCallback(
		async (action: BulkAction) => {
			if (selectedCount === 0 || loading) {
				return;
			}
			try {
				await action.action(
					[],
				); /* Actual selected IDs would be passed from parent */
				onActionComplete?.(action.id);
			} catch (error) {
				logger.error("Bulk action failed:", error);
			}
		},
		[selectedCount, loading, onActionComplete],
	);

	if (selectedCount === 0) {
		return null;
	}

	return (
		<div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-4 duration-300">
			<div className="flex items-center gap-3 px-6 py-4 bg-card border border-primary/30 rounded-2xl shadow-lg backdrop-blur-sm ring-1 ring-primary/20">
				{/* Selection Info */}
				<div className="flex items-center gap-3 pr-4 border-r border-border/50">
					<span className="text-sm font-bold">
						{selectedCount} of {totalCount} selected
					</span>
					<div className="flex items-center gap-2">
						<button
							onClick={onSelectAll}
							disabled={loading || selectedCount === totalCount}
							className="text-[10px] font-black uppercase tracking-widest text-primary hover:text-primary/80 disabled:text-muted-foreground disabled:cursor-not-allowed transition-all duration-200 ease-out active:scale-95"
						>
							Select All
						</button>
						<span className="text-border/50">•</span>
						<button
							onClick={onSelectNone}
							disabled={loading}
							className="text-[10px] font-black uppercase tracking-widest text-primary hover:text-primary/80 disabled:text-muted-foreground disabled:cursor-not-allowed transition-all duration-200 ease-out active:scale-95"
						>
							Deselect
						</button>
					</div>
				</div>

				{/* Actions */}
				<div className="flex items-center gap-2">
					{actions.map((action) => (
						<button
							key={action.id}
							onClick={() => handleAction(action)}
							disabled={
								loading || selectedCount === 0 || action.disabled === true
							}
							className={cn(
								"flex items-center gap-2 px-4 py-2 rounded-lg font-bold text-[11px] uppercase tracking-widest transition-all duration-200 ease-out active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
								action.variant === "destructive"
									? "bg-destructive/10 text-destructive hover:bg-destructive/20 disabled:hover:bg-destructive/10"
									: "bg-primary/10 text-primary hover:bg-primary/20 disabled:hover:bg-primary/10",
							)}
							title={action.label}
						>
							{action.icon}
							<span className="hidden sm:inline">{action.label}</span>
						</button>
					))}
				</div>

				{/* Close */}
				<button
					onClick={onSelectNone}
					disabled={loading}
					className="p-2 hover:bg-muted rounded-lg transition-all duration-200 ease-out active:scale-95 ml-2 border-l border-border/50 pl-2"
					aria-label="Close toolbar"
				>
					<X className="h-4 w-4" />
				</button>
			</div>
		</div>
	);
}

// Predefined bulk actions
export const commonBulkActions = {
	delete: (onDelete: (ids: string[]) => Promise<void>): BulkAction => ({
		action: onDelete,
		icon: <Trash2 className="h-4 w-4" />,
		id: "delete",
		label: "Delete",
		variant: "destructive",
	}),
};
