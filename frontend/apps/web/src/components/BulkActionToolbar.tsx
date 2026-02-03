import { Trash2, X } from "lucide-react";
import { useCallback } from "react";

import { logger } from "@/lib/logger";
import { cn } from "@/lib/utils";

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

const runBulkAction = async (
	action: BulkAction,
	onActionComplete?: (id: string) => void,
): Promise<void> => {
	try {
		await action.action([]);
		onActionComplete?.(action.id);
	} catch (error) {
		logger.error("Bulk action failed:", error);
	}
};

interface BulkActionButtonProps {
	action: BulkAction;
	disabled: boolean;
	onRun: (action: BulkAction) => void;
}

const BulkActionButton = ({ action, disabled, onRun }: BulkActionButtonProps) => {
	const handleClick = useCallback(() => {
		onRun(action);
	}, [action, onRun]);
	return (
		<button
			type="button"
			onClick={handleClick}
			disabled={disabled}
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
	);
};

export const BulkActionToolbar = ({
	selectedCount,
	totalCount,
	onSelectAll,
	onSelectNone,
	actions,
	loading = false,
	onActionComplete,
}: BulkActionToolbarProps) => {
	const handleAction = useCallback(
		(action: BulkAction) => {
			if (selectedCount === 0 || loading) return;
			void runBulkAction(action, onActionComplete);
		},
		[selectedCount, loading, onActionComplete],
	);

	if (selectedCount === 0) return null;

	return (
		<div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 animate-in slide-in-from-bottom-4 duration-300">
			<div className="flex items-center gap-3 px-6 py-4 bg-card border border-primary/30 rounded-2xl shadow-lg backdrop-blur-sm ring-1 ring-primary/20">
				<div className="flex items-center gap-3 pr-4 border-r border-border/50">
					<span className="text-sm font-bold">
						{selectedCount} of {totalCount} selected
					</span>
					<div className="flex items-center gap-2">
						<button
							type="button"
							onClick={onSelectAll}
							disabled={loading || selectedCount === totalCount}
							className="text-[10px] font-black uppercase tracking-widest text-primary hover:text-primary/80 disabled:text-muted-foreground disabled:cursor-not-allowed transition-all duration-200 ease-out active:scale-95"
						>
							Select All
						</button>
						<span className="text-border/50">•</span>
						<button
							type="button"
							onClick={onSelectNone}
							disabled={loading}
							className="text-[10px] font-black uppercase tracking-widest text-primary hover:text-primary/80 disabled:text-muted-foreground disabled:cursor-not-allowed transition-all duration-200 ease-out active:scale-95"
						>
							Deselect
						</button>
					</div>
				</div>
				<div className="flex items-center gap-2">
					{actions.map((action) => (
						<BulkActionButton
							key={action.id}
							action={action}
							disabled={loading || selectedCount === 0 || action.disabled === true}
							onRun={handleAction}
						/>
					))}
				</div>
				<button
					type="button"
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
};

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
