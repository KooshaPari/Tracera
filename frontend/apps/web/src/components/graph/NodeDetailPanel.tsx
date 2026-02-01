// Node Detail Panel - Rich information display for selected nodes

import type { Item, Link } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { ScrollArea } from "@tracertm/ui/components/ScrollArea";
import { Separator } from "@tracertm/ui/components/Separator";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import {
	ArrowDownRight,
	ArrowUpRight,
	ChevronRight,
	Circle,
	Code,
	ExternalLink,
	FileText,
	GitBranch,
	Image,
	Link2,
	User,
	X,
} from "lucide-react";
import { memo } from "react";
import type { EnhancedNodeData } from "./types";
import { ENHANCED_TYPE_COLORS, LINK_STYLES } from "./types";

interface NodeDetailPanelProps {
	node: EnhancedNodeData | null;
	relatedItems: Item[];
	incomingLinks: Link[];
	outgoingLinks: Link[];
	onClose: () => void;
	onNavigateToItem: (itemId: string) => void;
	onFocusNode: (nodeId: string) => void;
}

function NodeDetailPanelComponent({
	node,
	relatedItems,
	incomingLinks,
	outgoingLinks,
	onClose,
	onNavigateToItem,
	onFocusNode,
}: NodeDetailPanelProps) {
	if (!node) return null;

	const bgColor = ENHANCED_TYPE_COLORS[node.type] || "#64748b";

	// Group links by type
	const incomingByType = incomingLinks.reduce(
		(acc, link) => {
			const type = link.type || "related_to";
			if (!acc[type]) acc[type] = [];
			acc[type].push(link);
			return acc;
		},
		{} as Record<string, Link[]>,
	);

	const outgoingByType = outgoingLinks.reduce(
		(acc, link) => {
			const type = link.type || "related_to";
			if (!acc[type]) acc[type] = [];
			acc[type].push(link);
			return acc;
		},
		{} as Record<string, Link[]>,
	);

	return (
		<Card
			className="w-full min-w-0 max-w-[22rem] sm:max-w-[24rem] h-full flex flex-col overflow-hidden border-l-4 shrink-0"
			style={{ borderLeftColor: bgColor }}
		>
			{/* Header */}
			<div className="p-2 sm:p-4 border-b bg-muted/30 min-w-0">
				<div className="flex items-start justify-between gap-2 min-w-0">
					<div className="flex-1 min-w-0">
						<div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mb-1.5 sm:mb-2">
							<Badge
								variant="outline"
								className="text-[10px] sm:text-xs px-1.5 sm:px-2 shrink-0"
								style={{
									backgroundColor: `${bgColor}20`,
									color: bgColor,
									borderColor: bgColor,
								}}
							>
								{node.type.replace(/_/g, " ")}
							</Badge>
							<Badge variant="secondary" className="text-[10px] sm:text-xs shrink-0">
								{node.status}
							</Badge>
						</div>
						<h3 className="font-semibold text-sm sm:text-base md:text-lg leading-tight truncate">
							{node.label}
						</h3>
					</div>
					<Button
						variant="ghost"
						size="sm"
						className="h-7 w-7 sm:h-8 sm:w-8 p-0 shrink-0"
						onClick={onClose}
					>
						<X className="h-3.5 w-3.5 sm:h-4 sm:w-4" />
					</Button>
				</div>

				{/* Quick stats */}
				<div className="mt-2 sm:mt-3 flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-muted-foreground">
					<div className="flex items-center gap-1">
						<ArrowDownRight className="h-4 w-4 text-green-500" />
						<span>{incomingLinks.length} incoming</span>
					</div>
					<div className="flex items-center gap-1">
						<ArrowUpRight className="h-4 w-4 text-blue-500" />
						<span>{outgoingLinks.length} outgoing</span>
					</div>
				</div>
			</div>

			{/* Tabs */}
			<Tabs
				defaultValue="details"
				className="flex-1 flex flex-col overflow-hidden"
			>
				<TabsList className="w-full justify-start rounded-none border-b bg-transparent p-0">
					<TabsTrigger
						value="details"
						className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent text-xs sm:text-sm"
					>
						<FileText className="h-3 w-3 sm:h-4 sm:w-4 mr-1 shrink-0" />
						<span className="truncate">Details</span>
					</TabsTrigger>
					<TabsTrigger
						value="links"
						className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent text-xs sm:text-sm"
					>
						<Link2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1 shrink-0" />
						<span className="truncate">Links</span>
					</TabsTrigger>
					{node.uiPreview && (
						<TabsTrigger
							value="preview"
							className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent text-xs sm:text-sm"
						>
							<Image className="h-3 w-3 sm:h-4 sm:w-4 mr-1 shrink-0" />
							<span className="truncate">Preview</span>
						</TabsTrigger>
					)}
					<TabsTrigger
						value="code"
						className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary data-[state=active]:bg-transparent text-xs sm:text-sm"
					>
						<Code className="h-3 w-3 sm:h-4 sm:w-4 mr-1 shrink-0" />
						<span className="truncate">Code</span>
					</TabsTrigger>
				</TabsList>

				<ScrollArea className="flex-1">
					{/* Details Tab */}
					<TabsContent value="details" className="p-4 m-0 space-y-4">
						{/* Description */}
						<div className="min-w-0">
							<h4 className="text-xs sm:text-sm font-medium text-muted-foreground mb-1">
								Description
							</h4>
							<p className="text-xs sm:text-sm line-clamp-4 md:line-clamp-none">
								{node.item.description || "No description provided"}
							</p>
						</div>

						<Separator />

						{/* Metadata */}
						<div className="grid grid-cols-2 gap-2 sm:gap-3 text-xs sm:text-sm">
							{node.item.owner && (
								<div>
									<span className="text-muted-foreground flex items-center gap-1">
										<User className="h-3 w-3" /> Owner
									</span>
									<p className="font-medium">{node.item.owner}</p>
								</div>
							)}
							<div>
								<span className="text-muted-foreground">Priority</span>
								<p className="font-medium capitalize">
									{node.item.priority || "—"}
								</p>
							</div>
							<div>
								<span className="text-muted-foreground">Version</span>
								<p className="font-medium">{node.item.version || 1}</p>
							</div>
							<div>
								<span className="text-muted-foreground">View</span>
								<p className="font-medium">{node.item.view || "—"}</p>
							</div>
						</div>

						{/* Hierarchy */}
						{node.parentId && (
							<>
								<Separator />
								<div>
									<h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
										<GitBranch className="h-3 w-3" /> Hierarchy
									</h4>
									<Button
										variant="outline"
										size="sm"
										className="w-full justify-start"
										onClick={() => onFocusNode(node.parentId!)}
									>
										<ChevronRight className="h-4 w-4 mr-2 -rotate-90" />
										Go to parent
									</Button>
								</div>
							</>
						)}

						{/* Timestamps */}
						<Separator />
						<div className="text-xs text-muted-foreground space-y-1">
							<p>Created: {new Date(node.item.createdAt).toLocaleString()}</p>
							<p>Updated: {new Date(node.item.updatedAt).toLocaleString()}</p>
						</div>
					</TabsContent>

					{/* Links Tab */}
					<TabsContent value="links" className="p-4 m-0 space-y-4">
						{/* Incoming Links */}
						<div>
							<h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
								<ArrowDownRight className="h-4 w-4 text-green-500" />
								Incoming ({incomingLinks.length})
							</h4>
							{Object.entries(incomingByType).length > 0 ? (
								<div className="space-y-3">
									{Object.entries(incomingByType).map(([type, links]) => (
										<div key={type}>
											<div className="flex items-center gap-2 mb-1.5">
												<div
													className="h-1 w-6 rounded"
													style={{
														backgroundColor:
															LINK_STYLES[type]?.color || "#64748b",
													}}
												/>
												<span className="text-xs text-muted-foreground">
													{type.replace(/_/g, " ")} ({links.length})
												</span>
											</div>
											<div className="space-y-1 pl-4">
												{links.slice(0, 5).map((link) => {
													const sourceItem = relatedItems.find(
														(i) => i.id === link.sourceId,
													);
													return (
														<Button
															key={link.id}
															variant="ghost"
															size="sm"
															className="w-full justify-start text-xs h-7 px-2"
															onClick={() => onFocusNode(link.sourceId)}
														>
															<Circle
																className="h-2 w-2 mr-2"
																style={{
																	color:
																		ENHANCED_TYPE_COLORS[
																			sourceItem?.type || ""
																		] || "#64748b",
																	fill:
																		ENHANCED_TYPE_COLORS[
																			sourceItem?.type || ""
																		] || "#64748b",
																}}
															/>
															<span className="truncate">
																{sourceItem?.title || link.sourceId}
															</span>
														</Button>
													);
												})}
												{links.length > 5 && (
													<p className="text-xs text-muted-foreground pl-2">
														+{links.length - 5} more
													</p>
												)}
											</div>
										</div>
									))}
								</div>
							) : (
								<p className="text-sm text-muted-foreground">
									No incoming links
								</p>
							)}
						</div>

						<Separator />

						{/* Outgoing Links */}
						<div>
							<h4 className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
								<ArrowUpRight className="h-4 w-4 text-blue-500" />
								Outgoing ({outgoingLinks.length})
							</h4>
							{Object.entries(outgoingByType).length > 0 ? (
								<div className="space-y-3">
									{Object.entries(outgoingByType).map(([type, links]) => (
										<div key={type}>
											<div className="flex items-center gap-2 mb-1.5">
												<div
													className="h-1 w-6 rounded"
													style={{
														backgroundColor:
															LINK_STYLES[type]?.color || "#64748b",
													}}
												/>
												<span className="text-xs text-muted-foreground">
													{type.replace(/_/g, " ")} ({links.length})
												</span>
											</div>
											<div className="space-y-1 pl-4">
												{links.slice(0, 5).map((link) => {
													const targetItem = relatedItems.find(
														(i) => i.id === link.targetId,
													);
													return (
														<Button
															key={link.id}
															variant="ghost"
															size="sm"
															className="w-full justify-start text-xs h-7 px-2"
															onClick={() => onFocusNode(link.targetId)}
														>
															<Circle
																className="h-2 w-2 mr-2"
																style={{
																	color:
																		ENHANCED_TYPE_COLORS[
																			targetItem?.type || ""
																		] || "#64748b",
																	fill:
																		ENHANCED_TYPE_COLORS[
																			targetItem?.type || ""
																		] || "#64748b",
																}}
															/>
															<span className="truncate">
																{targetItem?.title || link.targetId}
															</span>
														</Button>
													);
												})}
												{links.length > 5 && (
													<p className="text-xs text-muted-foreground pl-2">
														+{links.length - 5} more
													</p>
												)}
											</div>
										</div>
									))}
								</div>
							) : (
								<p className="text-sm text-muted-foreground">
									No outgoing links
								</p>
							)}
						</div>
					</TabsContent>

					{/* Preview Tab */}
					{node.uiPreview && (
						<TabsContent value="preview" className="p-4 m-0 space-y-4">
							{node.uiPreview.screenshotUrl ? (
								<div className="space-y-3">
									<img
										src={node.uiPreview.screenshotUrl}
										alt={`Preview of ${node.label}`}
										className="w-full rounded-lg border shadow-sm"
									/>
									{node.uiPreview.interactiveWidgetUrl && (
										<a
											href={node.uiPreview.interactiveWidgetUrl}
											target="_blank"
											rel="noopener noreferrer"
											className="flex items-center justify-center gap-2 w-full h-9 px-3 text-sm font-medium rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground"
										>
											<ExternalLink className="h-4 w-4" />
											Open Interactive Preview
										</a>
									)}
								</div>
							) : (
								<div className="text-center py-8 text-muted-foreground">
									<Image className="h-12 w-12 mx-auto mb-2 opacity-50" />
									<p className="text-sm">No preview available</p>
								</div>
							)}
						</TabsContent>
					)}

					{/* Code Tab */}
					<TabsContent value="code" className="p-4 m-0 space-y-4">
						{node.uiPreview?.componentCode ? (
							<div className="space-y-2">
								<h4 className="text-sm font-medium text-muted-foreground">
									Component Code
								</h4>
								<pre className="bg-muted p-3 rounded-lg text-xs overflow-x-auto">
									<code>{node.uiPreview.componentCode}</code>
								</pre>
							</div>
						) : (
							<div className="text-center py-8 text-muted-foreground">
								<Code className="h-12 w-12 mx-auto mb-2 opacity-50" />
								<p className="text-sm">No code linked to this item</p>
								<p className="text-xs mt-1">Link code items to see them here</p>
							</div>
						)}
					</TabsContent>
				</ScrollArea>
			</Tabs>

			{/* Actions Footer */}
			<div className="p-3 border-t bg-muted/30 flex gap-2">
				<Button
					variant="outline"
					size="sm"
					className="flex-1"
					onClick={() => onNavigateToItem(node.id)}
				>
					<ExternalLink className="h-4 w-4 mr-2" />
					Open Details
				</Button>
			</div>
		</Card>
	);
}

export const NodeDetailPanel = memo(NodeDetailPanelComponent);
