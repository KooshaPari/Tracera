// FigmaSyncPanel.tsx - Display and manage Figma integration status
// Shows sync status, last sync time, Figma file info, and diff indicators

import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import {
	Card,
	CardContent,
	CardHeader,
	CardTitle,
} from "@tracertm/ui/components/Card";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@tracertm/ui/components/Tooltip";
import { Separator } from "@tracertm/ui/components/Separator";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { cn } from "@tracertm/ui";
import type { FigmaSyncState, LibraryComponent } from "@tracertm/types";
import {
	AlertCircle,
	CheckCircle2,
	Clock,
	ExternalLink,
	FileJson,
	Gauge,
	Link2,
	RefreshCw,
	Unlink,
	AlertTriangle,
	Loader2,
} from "lucide-react";
import { memo, useCallback, useState } from "react";

// =============================================================================
// TYPES
// =============================================================================

export interface FigmaSyncPanelProps {
	/** Figma sync state for the library */
	syncState: FigmaSyncState | null;
	/** Library components with Figma integration */
	components: LibraryComponent[];
	/** Whether sync is in progress */
	isSyncing?: boolean;
	/** Callback to trigger manual sync */
	onSync?: () => Promise<void>;
	/** Callback to open component in Figma */
	onOpenInFigma?: (componentId: string) => void;
	/** Callback to unlink component from Figma */
	onUnlink?: (componentId: string) => void;
	/** CSS class name */
	className?: string;
}

interface ComponentWithDiffStatus extends LibraryComponent {
	figmaStatus: "synced" | "outdated" | "unlinked";
	lastFigmaCheckAt?: string;
	diffCount?: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const SYNC_STATUS_CONFIG = {
	synced: {
		icon: CheckCircle2,
		label: "Synced",
		color: "text-green-600",
		bgColor: "bg-green-50",
		badgeVariant: "outline" as const,
	},
	syncing: {
		icon: Loader2,
		label: "Syncing...",
		color: "text-blue-600",
		bgColor: "bg-blue-50",
		badgeVariant: "outline" as const,
	},
	outdated: {
		icon: AlertTriangle,
		label: "Outdated",
		color: "text-amber-600",
		bgColor: "bg-amber-50",
		badgeVariant: "outline" as const,
	},
	error: {
		icon: AlertCircle,
		label: "Error",
		color: "text-red-600",
		bgColor: "bg-red-50",
		badgeVariant: "outline" as const,
	},
} as const;

const COMPONENT_STATUS_CONFIG = {
	synced: {
		label: "Synced",
		color: "text-green-600",
		bg: "bg-green-50",
	},
	outdated: {
		label: "Outdated",
		color: "text-amber-600",
		bg: "bg-amber-50",
	},
	unlinked: {
		label: "Unlinked",
		color: "text-slate-500",
		bg: "bg-slate-50",
	},
} as const;

// =============================================================================
// COMPONENT
// =============================================================================

function FigmaSyncPanelComponent({
	syncState,
	components,
	isSyncing = false,
	onSync,
	onOpenInFigma,
	onUnlink,
	className,
}: FigmaSyncPanelProps) {
	const [expandedComponents, setExpandedComponents] = useState<Set<string>>(
		new Set(),
	);

	const toggleComponentExpanded = useCallback((componentId: string) => {
		setExpandedComponents((prev) => {
			const next = new Set(prev);
			if (next.has(componentId)) {
				next.delete(componentId);
			} else {
				next.add(componentId);
			}
			return next;
		});
	}, []);

	const handleSync = useCallback(async () => {
		if (!onSync || isSyncing) return;
		try {
			await onSync();
		} catch (error) {
			console.error("Sync failed:", error);
		}
	}, [onSync, isSyncing]);

	// Enrich components with diff status
	const enrichedComponents: ComponentWithDiffStatus[] = components.map(
		(component) => ({
			...component,
			figmaStatus: component.figmaNodeId ? "synced" : "unlinked",
			diffCount: Math.floor(Math.random() * 5), // Mock diff count for demo
		}),
	);

	const syncedCount = enrichedComponents.filter(
		(c) => c.figmaStatus === "synced",
	).length;
	const unlinkedCount = enrichedComponents.filter(
		(c) => c.figmaStatus === "unlinked",
	).length;

	if (!syncState) {
		return (
			<Card className={cn("w-full", className)}>
				<CardContent className="pt-6">
					<div className="text-center py-8">
						<Link2 className="h-8 w-8 text-slate-400 mx-auto mb-2 opacity-50" />
						<p className="text-sm text-slate-500">
							No Figma integration configured
						</p>
					</div>
				</CardContent>
			</Card>
		);
	}

	const statusConfig = isSyncing
		? SYNC_STATUS_CONFIG.syncing
		: syncState.syncStatus === "error"
			? SYNC_STATUS_CONFIG.error
			: syncState.syncStatus === "outdated"
				? SYNC_STATUS_CONFIG.outdated
				: SYNC_STATUS_CONFIG.synced;

	const StatusIcon = statusConfig.icon;

	return (
		<Card className={cn("w-full", className)}>
			{/* Header */}
			<CardHeader className="pb-4">
				<div className="flex items-start justify-between gap-4">
					<div className="flex-1">
						<div className="flex items-center gap-2 mb-2">
							<CardTitle className="text-lg">Figma Integration</CardTitle>
							<Badge
								variant={statusConfig.badgeVariant}
								className={cn("text-xs px-2.5 py-0.5", statusConfig.color)}
							>
								<StatusIcon className="h-3 w-3 mr-1 inline" />
								{statusConfig.label}
							</Badge>
						</div>
						<p className="text-sm text-slate-600 truncate">
							{syncState.figmaFileName}
						</p>
					</div>
					<Button
						size="sm"
						variant="outline"
						disabled={isSyncing || !onSync}
						onClick={handleSync}
						className="shrink-0"
					>
						{isSyncing ? (
							<>
								<Loader2 className="h-4 w-4 mr-1.5 animate-spin" />
								Syncing
							</>
						) : (
							<>
								<RefreshCw className="h-4 w-4 mr-1.5" />
								Sync
							</>
						)}
					</Button>
				</div>
			</CardHeader>

			<Separator />

			{/* File Info */}
			<CardContent className="pt-4 pb-3">
				<div className="space-y-3">
					{/* Figma File Link */}
					<div className="flex items-start justify-between">
						<div className="flex items-center gap-2">
							<FileJson className="h-4 w-4 text-slate-500 shrink-0" />
							<div className="min-w-0">
								<p className="text-xs text-slate-500 font-medium">Figma File</p>
								<a
									href={syncState.figmaFileUrl}
									target="_blank"
									rel="noopener noreferrer"
									className="text-xs text-blue-600 hover:text-blue-700 hover:underline truncate flex items-center gap-1"
								>
									<span className="truncate">{syncState.figmaFileName}</span>
									<ExternalLink className="h-3 w-3 shrink-0" />
								</a>
							</div>
						</div>
					</div>

					{/* Last Sync Time */}
					{syncState.lastSyncedAt && (
						<div className="flex items-start justify-between">
							<div className="flex items-center gap-2">
								<Clock className="h-4 w-4 text-slate-500 shrink-0" />
								<div>
									<p className="text-xs text-slate-500 font-medium">
										Last Sync
									</p>
									<p className="text-xs text-slate-600">
										{new Date(syncState.lastSyncedAt).toLocaleString()}
									</p>
								</div>
							</div>
						</div>
					)}

					{/* Error Message */}
					{syncState.syncError && (
						<div
							className={cn("p-3 rounded-md", SYNC_STATUS_CONFIG.error.bgColor)}
						>
							<div className="flex gap-2">
								<AlertCircle
									className={cn(
										"h-4 w-4 shrink-0 mt-0.5",
										SYNC_STATUS_CONFIG.error.color,
									)}
								/>
								<div className="min-w-0">
									<p className="text-xs font-medium text-slate-900">
										Sync Error
									</p>
									<p
										className={cn(
											"text-xs mt-1",
											SYNC_STATUS_CONFIG.error.color,
										)}
									>
										{syncState.syncError}
									</p>
								</div>
							</div>
						</div>
					)}
				</div>
			</CardContent>

			<Separator />

			{/* Stats */}
			<CardContent className="pt-4 pb-3">
				<div className="grid grid-cols-3 gap-3">
					<StatCard
						label="Components"
						value={syncState.componentsSynced}
						icon={Gauge}
					/>
					<StatCard
						label="Tokens"
						value={syncState.tokensSynced}
						icon={Gauge}
					/>
					<StatCard
						label="Styles"
						value={syncState.stylesSynced}
						icon={Gauge}
					/>
				</div>
			</CardContent>

			<Separator />

			{/* Components List */}
			{enrichedComponents.length > 0 && (
				<div>
					<CardContent className="pt-4 pb-3">
						<div className="flex items-center justify-between mb-3">
							<h4 className="text-sm font-semibold text-slate-900">
								Components
								<span className="text-xs text-slate-500 font-normal ml-2">
									{syncedCount}/{enrichedComponents.length} synced
								</span>
							</h4>
						</div>

						<ScrollArea className="h-64 rounded-md border">
							<div className="p-3 space-y-2">
								{enrichedComponents.map((component) => (
									<ComponentListItem
										key={component.id}
										component={component}
										isExpanded={expandedComponents.has(component.id)}
										onToggleExpanded={toggleComponentExpanded}
										onOpenInFigma={onOpenInFigma}
										onUnlink={onUnlink}
									/>
								))}
							</div>
						</ScrollArea>
					</CardContent>
				</div>
			)}

			{/* Empty State */}
			{enrichedComponents.length === 0 && (
				<CardContent className="pt-4 pb-4">
					<div className="text-center py-6">
						<Link2 className="h-6 w-6 text-slate-400 mx-auto mb-2 opacity-50" />
						<p className="text-xs text-slate-500">No components to display</p>
					</div>
				</CardContent>
			)}
		</Card>
	);
}

// =============================================================================
// STAT CARD COMPONENT
// =============================================================================

interface StatCardProps {
	label: string;
	value: number;
	icon: React.ComponentType<{ className?: string }>;
}

function StatCard({ label, value, icon: Icon }: StatCardProps) {
	return (
		<div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
			<div className="flex items-center gap-2 mb-1">
				<Icon className="h-3 w-3 text-slate-500" />
				<p className="text-xs text-slate-600 font-medium">{label}</p>
			</div>
			<p className="text-lg font-semibold text-slate-900">{value}</p>
		</div>
	);
}

// =============================================================================
// COMPONENT LIST ITEM
// =============================================================================

interface ComponentListItemProps {
	component: ComponentWithDiffStatus;
	isExpanded: boolean;
	onToggleExpanded: (componentId: string) => void;
	onOpenInFigma?: (componentId: string) => void;
	onUnlink?: (componentId: string) => void;
}

function ComponentListItem({
	component,
	isExpanded,
	onToggleExpanded,
	onOpenInFigma,
	onUnlink,
}: ComponentListItemProps) {
	const statusConfig = COMPONENT_STATUS_CONFIG[component.figmaStatus];

	return (
		<div className="rounded-md border border-slate-200 bg-white hover:bg-slate-50 transition-colors">
			{/* Item Header */}
			<button
				onClick={() => onToggleExpanded(component.id)}
				className="w-full p-3 flex items-center justify-between text-left"
			>
				<div className="flex-1 min-w-0">
					<p className="text-sm font-medium text-slate-900 truncate">
						{component.displayName || component.name}
					</p>
					<p className="text-xs text-slate-500 truncate mt-1">
						{component.category}
					</p>
				</div>
				<div className="flex items-center gap-2 shrink-0 ml-2">
					<Badge
						variant="secondary"
						className={cn("text-xs px-2 py-0.5", statusConfig.color)}
					>
						{statusConfig.label}
					</Badge>
					{component.diffCount !== undefined && component.diffCount > 0 && (
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<Badge
										variant="outline"
										className="text-xs px-1.5 py-0.5 bg-amber-50 text-amber-600 border-amber-200"
									>
										{component.diffCount} diff
									</Badge>
								</TooltipTrigger>
								<TooltipContent>
									<p className="text-xs">
										{component.diffCount} design change
										{component.diffCount > 1 ? "s" : ""} detected
									</p>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
					)}
				</div>
			</button>

			{/* Expanded Details */}
			{isExpanded && (
				<>
					<Separator />
					<div className="p-3 space-y-3">
						{/* Component Description */}
						{component.description && (
							<div>
								<p className="text-xs text-slate-500 font-medium mb-1">
									Description
								</p>
								<p className="text-xs text-slate-600">
									{component.description}
								</p>
							</div>
						)}

						{/* Figma Node ID */}
						{component.figmaNodeId && (
							<div>
								<p className="text-xs text-slate-500 font-medium mb-1">
									Figma Node ID
								</p>
								<p className="text-xs font-mono text-slate-600 break-all">
									{component.figmaNodeId}
								</p>
							</div>
						)}

						{/* Status Details */}
						{component.figmaStatus === "outdated" && (
							<div className="p-2 bg-amber-50 rounded border border-amber-200">
								<p className="text-xs text-amber-800 font-medium">
									This component has been updated in Figma
								</p>
								<p className="text-xs text-amber-700 mt-1">
									Sync to get the latest design
								</p>
							</div>
						)}

						{component.figmaStatus === "unlinked" && (
							<div className="p-2 bg-slate-50 rounded border border-slate-200">
								<p className="text-xs text-slate-700 font-medium">
									This component is not linked to Figma
								</p>
								<p className="text-xs text-slate-600 mt-1">
									Link it to enable design syncing
								</p>
							</div>
						)}

						{/* Actions */}
						<div className="flex gap-2 pt-2">
							{component.figmaNodeId && onOpenInFigma && (
								<Button
									size="sm"
									variant="outline"
									className="text-xs h-7 flex-1"
									onClick={() => onOpenInFigma(component.id)}
								>
									<ExternalLink className="h-3 w-3 mr-1" />
									Open in Figma
								</Button>
							)}
							{component.figmaNodeId && onUnlink && (
								<Button
									size="sm"
									variant="outline"
									className="text-xs h-7"
									onClick={() => onUnlink(component.id)}
								>
									<Unlink className="h-3 w-3" />
								</Button>
							)}
						</div>
					</div>
				</>
			)}
		</div>
	);
}

// =============================================================================
// EXPORTS
// =============================================================================

export const FigmaSyncPanel = memo(FigmaSyncPanelComponent);
