import { Link, useNavigate, useParams } from "@tanstack/react-router";
import {
	ArrowLeft,
	BookText,
	CalendarClock,
	ChevronRight,
	CircleDot,
	Code2,
	Edit3,
	ExternalLink,
	GitBranch,
	Hash,
	Link2,
	MoreVertical,
	Orbit,
	ShieldAlert,
	Sparkles,
	Target,
	Timer,
	Trash2,
	User,
	X,
	XCircle,
} from "lucide-react";
import {
	Badge,
	Button,
	Card,
	Input,
	Separator,
	Skeleton,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
	Textarea,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { useDeleteItem, useItem, useUpdateItem } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";
import { cn } from "@/lib/utils";
import { ItemSpecTabs } from "@/components/specifications/items/ItemSpecTabs";

const statusColors: Record<string, string> = {
	done: "bg-emerald-500/15 text-emerald-700 border-emerald-500/30",
	in_progress: "bg-sky-500/15 text-sky-700 border-sky-500/30",
	todo: "bg-slate-500/10 text-slate-600 border-slate-500/20",
	blocked: "bg-rose-500/15 text-rose-700 border-rose-500/30",
};

const priorityColors: Record<string, string> = {
	critical: "bg-rose-500 text-white",
	high: "bg-orange-500 text-white",
	medium: "bg-indigo-500 text-white",
	low: "bg-emerald-500 text-white",
};

const statusOptions = ["todo", "in_progress", "blocked", "done"] as const;
const priorityOptions = ["critical", "high", "medium", "low"] as const;

const integrationKeys = new Set([
	"external_system",
	"external_id",
	"external_key",
	"external_url",
	"repo_full_name",
	"issue_number",
	"state",
	"labels",
	"project_id",
	"team_id",
	"identifier",
	"url",
]);

function formatValue(value: unknown) {
	if (Array.isArray(value)) return value.join(", ");
	if (value && typeof value === "object") return JSON.stringify(value);
	if (value === null || value === undefined) return "–";
	return String(value);
}

export function ItemDetailView() {
	const params = useParams({ strict: false });
	const itemId = params.itemId as string | undefined;
	const navigate = useNavigate();
	const { data: item, isLoading, error } = useItem(itemId!);
	const deleteItem = useDeleteItem();
	const updateItem = useUpdateItem();
	const [isEditing, setIsEditing] = useState(false);
	const [metadataSearch, setMetadataSearch] = useState("");
	const [draft, setDraft] = useState({
		title: "",
		description: "",
		status: "todo",
		priority: "medium",
		owner: "",
	});

	useEffect(() => {
		if (!item) return;
		setDraft({
			title: item.title ?? "",
			description: item.description ?? "",
			status: item.status ?? "todo",
			priority: item.priority ?? "medium",
			owner: item.owner ?? "",
		});
	}, [item]);

	const { data: sourceLinksData } = useLinks({
		sourceId: itemId,
		projectId: item?.projectId,
	});
	const { data: targetLinksData } = useLinks({
		targetId: itemId,
		projectId: item?.projectId,
	});

	const { sourceLinks, targetLinks } = useMemo(() => {
		const s = sourceLinksData?.links ?? [];
		const t = targetLinksData?.links ?? [];
		return { sourceLinks: s, targetLinks: t };
	}, [sourceLinksData, targetLinksData]);

	const metadataEntries = useMemo(() => {
		return Object.entries(item?.metadata ?? {});
	}, [item?.metadata]);

	const filteredMetadata = useMemo(() => {
		if (!metadataSearch.trim()) return metadataEntries;
		const query = metadataSearch.trim().toLowerCase();
		return metadataEntries.filter(([key, value]) => {
			const haystack = `${key} ${formatValue(value)}`.toLowerCase();
			return haystack.includes(query);
		});
	}, [metadataEntries, metadataSearch]);

	const integrationEntries = useMemo(
		() => filteredMetadata.filter(([key]) => integrationKeys.has(key)),
		[filteredMetadata],
	);

	const generalMetadata = useMemo(
		() => filteredMetadata.filter(([key]) => !integrationKeys.has(key)),
		[filteredMetadata],
	);

	const dimensionEntries = useMemo(() => {
		if (!item?.dimensions) return [] as Array<[string, unknown]>;
		const entries: Array<[string, unknown]> = [];
		if (item.dimensions.maturity)
			entries.push(["Maturity", item.dimensions.maturity]);
		if (item.dimensions.complexity)
			entries.push(["Complexity", item.dimensions.complexity]);
		if (item.dimensions.risk) entries.push(["Risk", item.dimensions.risk]);
		if (item.dimensions.coverage)
			entries.push(["Coverage", item.dimensions.coverage]);
		if (item.dimensions.custom) {
			Object.entries(item.dimensions.custom).forEach(([key, value]) => {
				entries.push([key, value]);
			});
		}
		return entries;
	}, [item?.dimensions]);

	const timelineEvents = useMemo(() => {
		if (!item)
			return [] as Array<{ label: string; timestamp: string; detail?: string }>;
		const events: Array<{ label: string; timestamp: string; detail?: string }> =
			[];
		if (item.createdAt) {
			events.push({
				label: "Item created",
				timestamp: item.createdAt,
				detail: `Status: ${item.status}`,
			});
		}
		if (item.updatedAt) {
			events.push({
				label: "Item updated",
				timestamp: item.updatedAt,
				detail: `v${item.version}`,
			});
		}
		if (item.version > 1 && item.updatedAt) {
			events.push({
				label: "Version bump",
				timestamp: item.updatedAt,
				detail: `Now at v${item.version}`,
			});
		}
		if (integrationEntries.length > 0 && item.updatedAt) {
			const integration = integrationEntries.find(
				([key]) => key === "external_system",
			);
			events.push({
				label: "External sync",
				timestamp: item.updatedAt,
				detail: integration
					? `System: ${integration[1]}`
					: "Integration data attached",
			});
		}
		return events.sort((a, b) => (a.timestamp < b.timestamp ? 1 : -1));
	}, [integrationEntries, item]);

	const upstreamCount = targetLinks.length;
	const downstreamCount = sourceLinks.length;
	const metadataCount = metadataEntries.length;
	const displayStatus = isEditing ? draft.status : item.status;
	const displayPriority = isEditing ? draft.priority : item.priority;
	const updatedAtLabel = item?.updatedAt
		? new Date(item.updatedAt).toLocaleString()
		: "Unknown";
	const createdAtLabel = item?.createdAt
		? new Date(item.createdAt).toLocaleDateString()
		: "Unknown";

	const handleDelete = async () => {
		if (!itemId) return;
		try {
			await deleteItem.mutateAsync(itemId);
			toast.success("Item deleted successfully");
			navigate({ to: "/items" });
		} catch (err) {
			toast.error("Failed to delete item");
		}
	};

	const handleCancelEdit = () => {
		if (item) {
			setDraft({
				title: item.title ?? "",
				description: item.description ?? "",
				status: item.status ?? "todo",
				priority: item.priority ?? "medium",
				owner: item.owner ?? "",
			});
		}
		setIsEditing(false);
	};

	const handleSave = async () => {
		if (!itemId) return;
		try {
			await updateItem.mutateAsync({
				id: itemId,
				data: {
					title: draft.title,
					description: draft.description,
					status: draft.status as typeof item.status,
					priority: draft.priority as typeof item.priority,
					owner: draft.owner || undefined,
				},
			});
			toast.success("Item updated");
			setIsEditing(false);
		} catch (err) {
			toast.error("Failed to update item");
		}
	};

	if (isLoading) {
		return (
			<div className="px-0 py-10 space-y-8 animate-pulse w-full">
				<Skeleton className="h-8 w-48" />
				<div className="flex justify-between items-start">
					<div className="space-y-4 flex-1">
						<Skeleton className="h-12 w-3/4" />
						<Skeleton className="h-6 w-1/2" />
					</div>
					<Skeleton className="h-10 w-32" />
				</div>
				<Skeleton className="h-[400px] w-full" />
			</div>
		);
	}

	if (error || !item) {
		return (
			<div className="p-20 flex flex-col items-center justify-center space-y-4">
				<XCircle className="h-12 w-12 text-destructive opacity-20" />
				<h2 className="text-xl font-bold">Item Not Found</h2>
				<Button variant="outline" onClick={() => navigate({ to: "/items" })}>
					Return to Items
				</Button>
			</div>
		);
	}

	return (
		<div className="relative min-h-screen">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(249,115,22,0.18),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(14,116,144,0.2),transparent_45%),radial-gradient(circle_at_20%_80%,rgba(16,185,129,0.18),transparent_40%)]" />
			<div className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.08),transparent_55%,rgba(2,132,199,0.08))]" />
			<div className="relative w-full px-0 py-10 space-y-8">
				<div className="flex items-center justify-between">
					<Button
						variant="ghost"
						size="sm"
						onClick={() => window.history.back()}
						className="gap-2 text-muted-foreground hover:text-foreground"
					>
						<ArrowLeft className="h-4 w-4" />
						Back
					</Button>
					<div className="flex items-center gap-2">
						<Button
							variant="outline"
							size="sm"
							className="gap-2 rounded-full"
							onClick={() => toast.info("Link sharing coming soon")}
						>
							<ExternalLink className="h-3.5 w-3.5" />
							Share
						</Button>
						{isEditing ? (
							<>
								<Button
									size="sm"
									className="gap-2 rounded-full"
									onClick={handleSave}
								>
									<ChevronRight className="h-4 w-4" />
									Save
								</Button>
								<Button
									variant="outline"
									size="sm"
									className="gap-2 rounded-full"
									onClick={handleCancelEdit}
								>
									<X className="h-4 w-4" />
									Cancel
								</Button>
							</>
						) : (
							<Button
								variant="outline"
								size="sm"
								className="gap-2 rounded-full"
								onClick={() => setIsEditing(true)}
							>
								<Edit3 className="h-3.5 w-3.5" />
								Edit
							</Button>
						)}
						<DropdownMenu>
							<DropdownMenuTrigger asChild>
								<Button variant="ghost" size="icon" className="rounded-full">
									<MoreVertical className="h-4 w-4" />
								</Button>
							</DropdownMenuTrigger>
							<DropdownMenuContent align="end" className="w-48">
								<DropdownMenuItem className="gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors">
									<ChevronRight className="h-4 w-4" /> Open in New Tab
								</DropdownMenuItem>
								<Separator className="my-1" />
								<DropdownMenuItem
									className="gap-2 text-destructive focus:text-destructive focus:bg-destructive/10 cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
									onClick={handleDelete}
								>
									<Trash2 className="h-4 w-4" /> Delete Item
								</DropdownMenuItem>
							</DropdownMenuContent>
						</DropdownMenu>
					</div>
				</div>

				<Card className="border-0 bg-card/60 backdrop-blur-sm shadow-xl shadow-primary/10 overflow-hidden">
					<div className="p-8 space-y-6">
						<div className="flex flex-wrap items-center gap-2">
							<Badge
								variant="outline"
								className="font-black uppercase tracking-[0.35em] text-[10px]"
							>
								{item.view || "general"}
							</Badge>
							<Badge
								variant="outline"
								className="font-black uppercase tracking-[0.35em] text-[10px]"
							>
								{item.type}
							</Badge>
							<Badge
								className={cn(
									"text-[10px] font-black uppercase tracking-[0.35em]",
									statusColors[displayStatus],
								)}
							>
								{displayStatus.replace("_", " ")}
							</Badge>
							<Badge
								className={cn(
									"text-[10px] font-black",
									priorityColors[displayPriority || "medium"],
								)}
							>
								{displayPriority || "medium"}
							</Badge>
							<Badge
								variant="secondary"
								className="gap-1 text-[10px] uppercase tracking-[0.35em]"
							>
								<Hash className="h-3 w-3" />
								{item.id}
							</Badge>
						</div>

						<div className="grid grid-cols-1 lg:grid-cols-[1.4fr_1fr] gap-8">
							<div className="space-y-4">
								{isEditing ? (
									<div className="space-y-3">
										<Input
											value={draft.title}
											onChange={(event) =>
												setDraft((prev) => ({
													...prev,
													title: event.target.value,
												}))
											}
											placeholder="Item title"
											className="h-12 text-2xl font-black"
										/>
										<Textarea
											value={draft.description}
											onChange={(event) =>
												setDraft((prev) => ({
													...prev,
													description: event.target.value,
												}))
											}
											placeholder="Describe the item..."
											className="min-h-[120px]"
										/>
									</div>
								) : (
									<>
										<h1
											className="text-4xl md:text-5xl font-black leading-tight tracking-tight"
											style={{
												fontFamily:
													'"Space Grotesk","Sora","IBM Plex Sans",sans-serif',
											}}
										>
											{item.title}
										</h1>
										<p className="text-lg text-muted-foreground leading-relaxed">
											{item.description ||
												"No description provided for this item."}
										</p>
									</>
								)}
								<div className="flex flex-wrap items-center gap-3 text-xs font-bold uppercase tracking-widest text-muted-foreground">
									<span className="inline-flex items-center gap-2">
										<CalendarClock className="h-3.5 w-3.5" />
										Created {createdAtLabel}
									</span>
									<span className="inline-flex items-center gap-2">
										<CircleDot className="h-3.5 w-3.5" />
										Updated {updatedAtLabel}
									</span>
									<span className="inline-flex items-center gap-2">
										<Link2 className="h-3.5 w-3.5" />
										{upstreamCount + downstreamCount} total links
									</span>
								</div>
							</div>

							<div className="grid gap-3">
								<Card className="border-0 bg-muted/40 px-4 py-3 space-y-3">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Status & Priority
									</p>
									{isEditing ? (
										<div className="grid grid-cols-2 gap-2">
											<Select
												value={draft.status}
												onValueChange={(value) =>
													setDraft((prev) => ({ ...prev, status: value }))
												}
											>
												<SelectTrigger className="h-8 text-xs">
													<SelectValue placeholder="Status" />
												</SelectTrigger>
												<SelectContent>
													{statusOptions.map((status) => (
														<SelectItem key={status} value={status}>
															{status.replace("_", " ")}
														</SelectItem>
													))}
												</SelectContent>
											</Select>
											<Select
												value={draft.priority}
												onValueChange={(value) =>
													setDraft((prev) => ({ ...prev, priority: value }))
												}
											>
												<SelectTrigger className="h-8 text-xs">
													<SelectValue placeholder="Priority" />
												</SelectTrigger>
												<SelectContent>
													{priorityOptions.map((priority) => (
														<SelectItem key={priority} value={priority}>
															{priority}
														</SelectItem>
													))}
												</SelectContent>
											</Select>
										</div>
									) : (
										<div className="flex items-center gap-2">
											<Badge
												className={cn(
													"text-[10px] font-black uppercase tracking-widest",
													statusColors[displayStatus],
												)}
											>
												{displayStatus.replace("_", " ")}
											</Badge>
											<Badge
												className={cn(
													"text-[10px] font-black uppercase tracking-widest",
													priorityColors[displayPriority || "medium"],
												)}
											>
												{displayPriority || "medium"}
											</Badge>
										</div>
									)}
								</Card>
								<Card className="border-0 bg-muted/40 px-4 py-3">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Owner
									</p>
									<div className="mt-2 flex items-center gap-2">
										<div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center">
											<User className="h-3 w-3 text-primary" />
										</div>
										{isEditing ? (
											<Input
												value={draft.owner}
												onChange={(event) =>
													setDraft((prev) => ({
														...prev,
														owner: event.target.value,
													}))
												}
												placeholder="Owner name"
												className="h-8 text-xs"
											/>
										) : (
											<span className="text-xs font-bold">
												{item.owner || "Unassigned"}
											</span>
										)}
									</div>
								</Card>
								<Card className="border-0 bg-muted/40 px-4 py-3">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Version & Perspective
									</p>
									<div className="mt-2 flex items-center justify-between text-xs font-bold">
										<span>v{item.version}</span>
										<span className="text-muted-foreground">
											{item.perspective || "default"}
										</span>
									</div>
								</Card>
								<Card className="border-0 bg-muted/40 px-4 py-3">
									<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
										Canonical & Parent
									</p>
									<div className="mt-2 flex items-center justify-between text-xs font-bold">
										<span className="truncate">{item.canonicalId || "—"}</span>
										<span className="text-muted-foreground">
											{item.parentId ? item.parentId.slice(0, 8) : "Root"}
										</span>
									</div>
								</Card>
							</div>
						</div>
					</div>
				</Card>

				<div className="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-8">
					<div className="space-y-8">
						<Card className="border-0 bg-card/50 shadow-lg shadow-slate-950/5">
							<div className="p-6 space-y-6">
								<div className="flex items-center justify-between">
									<div className="space-y-1">
										<p className="text-[10px] uppercase tracking-[0.3em] text-muted-foreground font-black">
											Traceability
										</p>
										<h2 className="text-lg font-black tracking-tight">
											Relationship map
										</h2>
									</div>
									<Button
										size="sm"
										className="gap-2 rounded-full"
										onClick={() => toast.info("Trace analysis coming soon")}
									>
										<Sparkles className="h-4 w-4" />
										Run analysis
									</Button>
								</div>

								<div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
									<Card className="border-0 bg-muted/40 p-4 space-y-2">
										<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
											Upstream
										</p>
										<p className="text-2xl font-black">{upstreamCount}</p>
										<p className="text-xs text-muted-foreground">
											Dependencies tied in
										</p>
									</Card>
									<Card className="border-0 bg-muted/40 p-4 space-y-2">
										<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
											Downstream
										</p>
										<p className="text-2xl font-black">{downstreamCount}</p>
										<p className="text-xs text-muted-foreground">
											Impacted items
										</p>
									</Card>
									<Card className="border-0 bg-muted/40 p-4 space-y-2">
										<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
											Metadata
										</p>
										<p className="text-2xl font-black">{metadataCount}</p>
										<p className="text-xs text-muted-foreground">
											Context signals
										</p>
									</Card>
								</div>

								<Separator />

								<Tabs defaultValue="specs" className="w-full">
									<TabsList className="bg-muted/60 p-1 rounded-xl">
										<TabsTrigger value="specs" className="rounded-lg">
											Specifications
										</TabsTrigger>
										<TabsTrigger value="links" className="rounded-lg">
											Relationships
										</TabsTrigger>
										<TabsTrigger value="metadata" className="rounded-lg">
											Metadata
										</TabsTrigger>
									</TabsList>

									<TabsContent value="specs" className="pt-6 space-y-4">
										{item.projectId && itemId && (
											<ItemSpecTabs
												projectId={item.projectId}
												itemId={itemId}
												itemType={item.type}
												onCreateSpec={(specType) =>
													toast.info(`Create ${specType} spec coming soon`)
												}
											/>
										)}
									</TabsContent>

									<TabsContent value="links" className="pt-6 space-y-6">
										<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
											<Card className="border-0 bg-muted/40 p-4 space-y-3">
												<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
													Upstream
												</h3>
												<div className="space-y-2">
													{targetLinks.length > 0 ? (
														targetLinks.map((link) => (
															<Link
																key={link.id}
																to={`/items/${link.sourceId}`}
																className="flex items-center gap-3 rounded-xl border bg-card/50 px-3 py-2 hover:bg-muted/60 transition-colors"
															>
																<div className="h-8 w-8 rounded-lg bg-orange-500/10 flex items-center justify-center">
																	<ArrowLeft className="h-4 w-4 text-orange-500" />
																</div>
																<div className="flex-1 min-w-0">
																	<p className="text-[10px] font-black text-muted-foreground uppercase">
																		{link.type}
																	</p>
																	<p className="text-xs font-bold truncate">
																		{link.sourceId}
																	</p>
																</div>
																<ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
															</Link>
														))
													) : (
														<p className="text-xs text-muted-foreground italic text-center py-4">
															No upstream dependencies
														</p>
													)}
												</div>
											</Card>
											<Card className="border-0 bg-muted/40 p-4 space-y-3">
												<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
													Downstream
												</h3>
												<div className="space-y-2">
													{sourceLinks.length > 0 ? (
														sourceLinks.map((link) => (
															<Link
																key={link.id}
																to={`/items/${link.targetId}`}
																className="flex items-center gap-3 rounded-xl border bg-card/50 px-3 py-2 hover:bg-muted/60 transition-colors"
															>
																<div className="h-8 w-8 rounded-lg bg-sky-500/10 flex items-center justify-center">
																	<ArrowLeft className="h-4 w-4 text-sky-500 rotate-180" />
																</div>
																<div className="flex-1 min-w-0">
																	<p className="text-[10px] font-black text-muted-foreground uppercase">
																		{link.type}
																	</p>
																	<p className="text-xs font-bold truncate">
																		{link.targetId}
																	</p>
																</div>
																<ExternalLink className="h-3.5 w-3.5 text-muted-foreground" />
															</Link>
														))
													) : (
														<p className="text-xs text-muted-foreground italic text-center py-4">
															No downstream impact
														</p>
													)}
												</div>
											</Card>
										</div>
									</TabsContent>

									<TabsContent value="metadata" className="pt-6 space-y-6">
										<div className="flex items-center gap-3">
											<Input
												value={metadataSearch}
												onChange={(event) =>
													setMetadataSearch(event.target.value)
												}
												placeholder="Search metadata keys or values..."
												className="h-9"
											/>
											<Badge
												variant="secondary"
												className="text-[10px] uppercase tracking-widest"
											>
												{filteredMetadata.length} entries
											</Badge>
										</div>
										{integrationEntries.length > 0 && (
											<div className="space-y-3">
												<div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-muted-foreground">
													<Orbit className="h-4 w-4 text-amber-500" />
													Integration context
												</div>
												<div className="grid grid-cols-2 md:grid-cols-3 gap-3">
													{integrationEntries.map(([key, value]) => (
														<div
															key={key}
															className="p-3 rounded-xl border bg-card/50"
														>
															<p className="text-[10px] font-black text-muted-foreground uppercase mb-1">
																{key.replace(/_/g, " ")}
															</p>
															<p className="text-xs font-bold truncate">
																{formatValue(value)}
															</p>
														</div>
													))}
												</div>
											</div>
										)}

										{generalMetadata.length > 0 ? (
											<div className="grid grid-cols-2 md:grid-cols-3 gap-3">
												{generalMetadata.map(([key, value]) => (
													<div
														key={key}
														className="p-3 rounded-xl border bg-card/50"
													>
														<p className="text-[10px] font-black text-muted-foreground uppercase mb-1">
															{key.replace(/_/g, " ")}
														</p>
														<p className="text-xs font-bold truncate">
															{formatValue(value)}
														</p>
													</div>
												))}
											</div>
										) : (
											<div className="p-8 rounded-2xl border-2 border-dashed flex flex-col items-center justify-center text-muted-foreground italic">
												<p className="text-sm">No custom metadata defined</p>
											</div>
										)}
									</TabsContent>
								</Tabs>
							</div>
						</Card>
					</div>

					<div className="space-y-6">
						<Card className="border-0 bg-card/60 shadow-lg shadow-slate-950/5 p-6 space-y-4">
							<div className="flex items-center justify-between">
								<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									Signal stack
								</h3>
								<ShieldAlert className="h-4 w-4 text-orange-500" />
							</div>
							<div className="flex items-center gap-3">
								<div className="h-10 w-10 rounded-2xl bg-amber-500/15 flex items-center justify-center">
									<Target className="h-4 w-4 text-amber-600" />
								</div>
								<div>
									<p className="text-2xl font-black">
										{upstreamCount + downstreamCount}
									</p>
									<p className="text-xs text-muted-foreground">
										Connected items affecting delivery
									</p>
								</div>
							</div>
							<Button
								variant="outline"
								size="sm"
								className="w-full gap-2"
								onClick={() => toast.info("Impact analysis coming soon")}
							>
								<Target className="h-4 w-4" />
								Open impact analysis
							</Button>
						</Card>

						<Card className="border-0 bg-muted/40 p-6 space-y-4">
							<div className="flex items-center justify-between">
								<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									Dimensions
								</h3>
								<GitBranch className="h-4 w-4 text-sky-500" />
							</div>
							{dimensionEntries.length > 0 ? (
								<div className="space-y-2">
									{dimensionEntries.map(([label, value]) => (
										<div
											key={label}
											className="flex items-center justify-between text-xs font-bold"
										>
											<span className="text-muted-foreground uppercase tracking-widest text-[10px]">
												{label}
											</span>
											<span className="text-right max-w-[60%] truncate">
												{formatValue(value)}
											</span>
										</div>
									))}
								</div>
							) : (
								<p className="text-xs text-muted-foreground italic">
									No dimensions configured.
								</p>
							)}
						</Card>

						<Card className="border-0 bg-card/60 shadow-lg shadow-slate-950/5 p-6 space-y-4">
							<div className="flex items-center justify-between">
								<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									References
								</h3>
								<BookText className="h-4 w-4 text-emerald-500" />
							</div>
							<div className="space-y-3 text-xs">
								<div className="flex items-start gap-2">
									<Code2 className="h-4 w-4 text-slate-500" />
									<div>
										<p className="font-bold">Code reference</p>
										<p className="text-muted-foreground">
											{item.codeRef
												? `${item.codeRef.filePath} · ${item.codeRef.symbolName}`
												: "No code reference attached"}
										</p>
									</div>
								</div>
								<div className="flex items-start gap-2">
									<BookText className="h-4 w-4 text-slate-500" />
									<div>
										<p className="font-bold">Documentation</p>
										<p className="text-muted-foreground">
											{item.docRef
												? `${item.docRef.documentTitle} · ${item.docRef.sectionTitle || item.docRef.documentPath}`
												: "No doc reference attached"}
										</p>
									</div>
								</div>
							</div>
						</Card>

						<Card className="border-0 bg-muted/40 p-6 space-y-3">
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Change log
							</h3>
							<div className="space-y-3 text-xs">
								{timelineEvents.length > 0 ? (
									timelineEvents.map((event) => (
										<div
											key={`${event.label}-${event.timestamp}`}
											className="flex items-start justify-between gap-3"
										>
											<div>
												<p className="font-bold">{event.label}</p>
												{event.detail && (
													<p className="text-muted-foreground">
														{event.detail}
													</p>
												)}
											</div>
											<span className="text-muted-foreground">
												{new Date(event.timestamp).toLocaleDateString()}
											</span>
										</div>
									))
								) : (
									<p className="text-xs text-muted-foreground italic">
										No change events recorded.
									</p>
								)}
							</div>
						</Card>

						<Card className="border-0 bg-muted/40 p-6 space-y-3">
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Activity timeline
							</h3>
							<div className="space-y-2 text-xs font-bold">
								<div className="flex items-center justify-between">
									<span className="text-muted-foreground">Created</span>
									<span>{createdAtLabel}</span>
								</div>
								<div className="flex items-center justify-between">
									<span className="text-muted-foreground">Updated</span>
									<span>{updatedAtLabel}</span>
								</div>
								<div className="flex items-center justify-between">
									<span className="text-muted-foreground">System lag</span>
									<span className="inline-flex items-center gap-1">
										<Timer className="h-3 w-3" />
										recent
									</span>
								</div>
							</div>
						</Card>

						<Card className="border-0 bg-primary text-primary-foreground shadow-lg shadow-primary/20 p-6 space-y-3">
							<div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest opacity-80">
								<Sparkles className="h-4 w-4" />
								Insight snapshot
							</div>
							<p className="text-sm font-medium leading-relaxed italic">
								"This item touches {downstreamCount} downstream links,{" "}
								{upstreamCount} upstream dependencies, and {metadataCount}{" "}
								metadata signals. Lock a baseline before major edits."
							</p>
						</Card>
					</div>
				</div>
			</div>
		</div>
	);
}
