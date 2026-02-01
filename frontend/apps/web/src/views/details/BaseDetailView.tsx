/**
 * BaseDetailView - Shared layout for all type-specific detail pages
 *
 * Provides a consistent structure for item detail pages including:
 * - Responsive header with title, type, and status
 * - Tab navigation for different sections
 * - Action toolbar for common operations
 * - Mobile-optimized layout
 */

import type { TypedItem } from "@tracertm/types";
import { Card, Tabs, TabsContent, TabsList, TabsTrigger } from "@tracertm/ui";
import { cn } from "@/lib/utils";
import { DetailHeader } from "./DetailHeader";

export interface DetailAction {
	label: string;
	icon?: React.ComponentType<{ className?: string }>;
	onClick: () => void;
	variant?: "default" | "outline" | "ghost" | "destructive";
	disabled?: boolean;
}

export interface DetailTab {
	id: string;
	label: string;
	content: React.ReactNode;
	badge?: string | number;
	ariaLabel?: string;
}

export interface BaseDetailViewProps {
	/** The item being displayed */
	item: TypedItem;

	/** Tab configurations */
	tabs: DetailTab[];

	/** Default tab to show */
	defaultTab?: string;

	/** Optional actions to display in the header */
	actions?: DetailAction[];

	/** Optional additional content before tabs */
	headerContent?: React.ReactNode;

	/** Optional additional content after tabs */
	footerContent?: React.ReactNode;

	/** Navigation callback for back button */
	onBack?: () => void;

	/** Optional CSS classes for customization */
	className?: string;

	/** Whether the view is in loading state */
	isLoading?: boolean;
}

/**
 * BaseDetailView provides a consistent layout structure for all item detail pages.
 * It handles responsive design, accessibility, and common UI patterns.
 */
export function BaseDetailView({
	item,
	tabs,
	defaultTab,
	actions,
	headerContent,
	footerContent,
	onBack,
	className,
	isLoading = false,
}: BaseDetailViewProps) {
	const activeDefaultTab = defaultTab || (tabs.length > 0 ? tabs[0]?.id : "");

	return (
		<div className={cn("relative min-h-screen flex flex-col", className)}>
			{/* Background gradients */}
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(249,115,22,0.18),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(14,116,144,0.2),transparent_45%),radial-gradient(circle_at_20%_80%,rgba(16,185,129,0.18),transparent_40%)]" />
			<div className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.08),transparent_55%,rgba(2,132,199,0.08))]" />

			<div className="relative flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6 mx-auto md:py-10">
				{/* Header with navigation, title, and actions */}
				<header className="shrink-0 pb-6 border-b border-border/50 md:pb-8">
					<DetailHeader item={item} actions={actions} onBack={onBack} />
				</header>

				{/* Optional header content */}
				{headerContent && <div className="shrink-0 w-full pt-4">{headerContent}</div>}

				{/* Main content card with tabs */}
				<main className="min-h-0 flex-1 overflow-auto pt-6 md:pt-8">
				<Card className="border-0 bg-card/50 backdrop-blur-sm shadow-xl shadow-primary/10 overflow-hidden">
					<Tabs defaultValue={activeDefaultTab} className="w-full">
						<div className="border-b bg-muted/30 px-4 md:px-6">
							<TabsList
								className="h-auto p-0 bg-transparent border-0 gap-0 md:gap-2 w-full overflow-x-auto"
								aria-label="Item details sections"
							>
								{tabs.map((tab) => (
									<TabsTrigger
										key={tab.id}
										value={tab.id}
										className={cn(
											"relative rounded-none border-b-2 border-transparent px-3 py-3 md:px-4 md:py-4",
											"data-[state=active]:border-primary data-[state=active]:bg-transparent",
											"text-sm md:text-base font-medium",
											"hover:bg-muted/40 transition-colors",
											"whitespace-nowrap min-w-[80px] md:min-w-0",
										)}
										aria-label={tab.ariaLabel || tab.label}
									>
										<span className="flex items-center gap-2">
											{tab.label}
											{tab.badge && (
												<span
													className="inline-flex items-center justify-center rounded-full bg-primary/10 px-2 py-0.5 text-xs font-bold text-primary"
													aria-label={`${tab.badge} items`}
												>
													{tab.badge}
												</span>
											)}
										</span>
									</TabsTrigger>
								))}
							</TabsList>
						</div>

						<div className="p-4 md:p-6 lg:p-8">
							{tabs.map((tab) => (
								<TabsContent
									key={tab.id}
									value={tab.id}
									className="mt-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded-lg"
									tabIndex={0}
								>
									{isLoading ? (
										<div className="flex items-center justify-center py-12">
											<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
											<span className="sr-only">Loading {tab.label}...</span>
										</div>
									) : (
										tab.content
									)}
								</TabsContent>
							))}
						</div>
					</Tabs>
				</Card>
				</main>

				{/* Optional footer content */}
				{footerContent && <div className="shrink-0 w-full pt-6">{footerContent}</div>}
			</div>
		</div>
	);
}
