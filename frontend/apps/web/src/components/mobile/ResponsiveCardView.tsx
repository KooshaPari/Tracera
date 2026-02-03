import { useCallback } from "react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const SKELETON_COUNT = 6;

export interface CardItem {
	id: string;
	title: string;
	subtitle?: string;
	badge?: ReactNode;
	status?: ReactNode;
	priority?: ReactNode;
	owner?: ReactNode;
	actions?: ReactNode;
	metadata?: Record<string, ReactNode>;
	onClick?: () => void;
}

interface ResponsiveCardViewProps {
	items: CardItem[];
	isLoading?: boolean;
	emptyState?: ReactNode;
	className?: string;
	cardClassName?: string;
	onItemClick?: (item: CardItem) => void;
}

/**
 * Responsive card view component that displays items as cards on mobile
 * and transitions to grid on tablet/desktop. Designed for accessibility
 * with minimum 44px touch targets.
 */
export const ResponsiveCardView = function ResponsiveCardView({
	items,
	isLoading,
	emptyState,
	className,
	cardClassName,
	onItemClick,
}: ResponsiveCardViewProps) {
	if (isLoading) {
		return (
			<div className={cn("space-y-3 sm:space-y-4 md:space-y-0", className)}>
				{Array.from({ length: SKELETON_COUNT }, (_, i) => i + 1).map((i) => (
					<div
						key={i}
						className="h-32 sm:h-40 bg-muted rounded-xl animate-pulse"
					/>
				))}
			</div>
		);
	}

	if (items.length === 0) {
		return (
			emptyState || <div className="text-center py-12">No items found</div>
		);
	}

	return (
		<div
			className={cn(
				"grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4",
				className,
			)}
		>
			{items.map((item) => (
				<CardItemComponent
					key={item.id}
					item={item}
					cardClassName={cardClassName}
					onItemClick={onItemClick}
				/>
			))}
		</div>
	);
};

interface CardItemComponentProps {
	item: CardItem;
	cardClassName?: string;
	onItemClick?: (item: CardItem) => void;
}

const CardItemComponent = function CardItemComponent({
	item,
	cardClassName,
	onItemClick,
}: CardItemComponentProps) {
	const handleClick = useCallback(() => {
		if (item.onClick) {
			item.onClick();
		}
		if (onItemClick) {
			onItemClick(item);
		}
	}, [item, onItemClick]);

	const handleKeyDown = useCallback(
		(e: React.KeyboardEvent) => {
			if (e.key === "Enter" || e.key === " ") {
				e.preventDefault();
				handleClick();
			}
		},
		[handleClick],
	);

	const handleActionsClick = useCallback((e: React.MouseEvent) => {
		e.stopPropagation();
	}, []);

	const handleActionsKeyDown = useCallback((e: React.KeyboardEvent) => {
		e.stopPropagation();
	}, []);

	return (
		<button
			type="button"
			onClick={handleClick}
			onKeyDown={handleKeyDown}
			className={cn(
				"group relative p-4 sm:p-5 rounded-xl border border-border",
				"bg-card hover:bg-card/80 transition-all duration-200",
				"text-left min-h-[120px] sm:min-h-[140px] flex flex-col justify-between",
				"focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
				"active:scale-95 sm:active:scale-100 transition-transform",
				"hover:shadow-lg hover:border-primary/50 cursor-pointer",
				cardClassName,
			)}
		>
			{/* Top section: Title and badge */}
			<div className="flex items-start justify-between gap-3 mb-3">
				<div className="flex-1 min-w-0">
					<h3 className="text-sm sm:text-base font-bold truncate text-foreground group-hover:text-primary transition-colors">
						{item.title}
					</h3>
					{item.subtitle && (
						<p className="text-xs sm:text-sm text-muted-foreground truncate mt-0.5">
							{item.subtitle}
						</p>
					)}
				</div>
				{item.badge && <div className="shrink-0 ml-2">{item.badge}</div>}
			</div>

			{/* Status and priority section */}
			{(item.status || item.priority) && (
				<div className="flex items-center gap-2 flex-wrap mb-2">
					{item.status && <div className="shrink-0">{item.status}</div>}
					{item.priority && <div className="shrink-0">{item.priority}</div>}
				</div>
			)}

			{/* Owner and metadata */}
			<div className="flex flex-col gap-2 text-xs sm:text-sm text-muted-foreground mb-3">
				{item.owner && (
					<div className="flex items-center gap-2">{item.owner}</div>
				)}
				{item.metadata &&
					Object.entries(item.metadata).map(([key, value]) => (
						<div key={key} className="flex items-center gap-2">
							<span className="font-medium">{key}:</span>
							{value}
						</div>
					))}
			</div>

			{/* Actions footer */}
			{item.actions && (
				<div
					className="flex items-center gap-2 pt-2 border-t border-border/30"
					onClick={handleActionsClick}
					onKeyDown={handleActionsKeyDown}
					role="presentation"
				>
					{item.actions}
				</div>
			)}
		</button>
	);
};
