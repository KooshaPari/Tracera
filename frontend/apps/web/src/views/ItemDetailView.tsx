import { Link, useNavigate, useParams } from "@tanstack/react-router";
import {
	Badge,
	Button,
	Card,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
	Input,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Separator,
	Skeleton,
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
	Textarea,
} from "@tracertm/ui";
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
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { ItemSpecTabs } from "@/components/specifications/items/ItemSpecTabs";
import { cn } from "@/lib/utils";
import { logger } from '@/lib/logger';
import {
	useCreateDefectSpec,
	useCreateEpicSpec,
	useCreateRequirementSpec,
	useCreateTaskSpec,
	useCreateTestSpec,
	useCreateUserStorySpec,
} from "../hooks/useItemSpecs";
import { useDeleteItem, useItem, useUpdateItem } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

const statusColors: Record<string, string> = {
	blocked: "bg-rose-500/15 text-rose-700 border-rose-500/30",
	done: "bg-emerald-500/15 text-emerald-700 border-emerald-500/30",
	in_progress: "bg-sky-500/15 text-sky-700 border-sky-500/30",
	todo: "bg-slate-500/10 text-slate-600 border-slate-500/20",
};

const priorityColors: Record<string, string> = {
	critical: "bg-rose-500 text-white",
	high: "bg-orange-500 text-white",
	low: "bg-emerald-500 text-white",
	medium: "bg-indigo-500 text-white",
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
	if (Array.isArray(value)) {return value.join(", ");}
	if (value && typeof value === "object") {return JSON.stringify(value);}
	if (value === null || value === undefined) {return "–";}
	return String(value);
}

export function ItemDetailView() {
	const params = useParams({ strict: false });
	const itemId = params.itemId as string | undefined;
	const projectId = params.projectId as string | undefined;
	const viewTypeParam = params.viewType as string | undefined;
	const navigate = useNavigate();
	const { data: item, isLoading, error } = useItem(itemId!);
	const deleteItem = useDeleteItem();
	const updateItem = useUpdateItem();
	const createRequirementSpec = useCreateRequirementSpec(item?.projectId || "");
	const createTestSpec = useCreateTestSpec(item?.projectId || "");
	const createEpicSpec = useCreateEpicSpec(item?.projectId || "");
	const createUserStorySpec = useCreateUserStorySpec(item?.projectId || "");
	const createTaskSpec = useCreateTaskSpec(item?.projectId || "");
	const createDefectSpec = useCreateDefectSpec(item?.projectId || "");
	const [isEditing, setIsEditing] = useState(false);
	const [metadataSearch, setMetadataSearch] = useState("");
	const [draft, setDraft] = useState({
		description: "",
		owner: "",
		priority: "medium",
		status: "todo",
		title: "",
	});

	useEffect(() => {
		if (!item) {return;}
		setDraft({
			description: item.description ?? "",
			owner: item.owner ?? "",
			priority: item.priority ?? "medium",
			status: item.status ?? "todo",
			title: item.title ?? "",
		});
	}, [item]);

	const defaultViewType = (
		viewTypeParam ||
		(item?.view ? String(item.view) : undefined) ||
		"feature"
	).toLowerCase();

	const buildItemLink = (id: string) =>
		projectId
			? `/projects/${projectId}/views/${defaultViewType}/${id}`
			: "/projects";

	const handleBack = () => {
		if (projectId) {
			undefined;
			return;
		}
		undefined;
	};

	const { data: sourceLinksData } = useLinks({
		projectId: item?.projectId,
		sourceId: itemId,
	});
	const { data: targetLinksData } = useLinks({
		projectId: item?.projectId,
		targetId: itemId,
	});

	const { sourceLinks, targetLinks } = useMemo(() => {
		const s = sourceLinksData?.links ?? [];
		const t = targetLinksData?.links ?? [];
		return { sourceLinks: s, targetLinks: t };
	}, [sourceLinksData, targetLinksData]);

	const metadataEntries = useMemo(() => Object.entries(item?.metadata ?? {}), [item?.metadata]);

	const filteredMetadata = useMemo(() => {
		if (!metadataSearch.trim()) {return metadataEntries;}
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
		if (!item?.dimensions) {return [] as [string, unknown][];}
		const entries: [string, unknown][] = [];
		if (item.dimensions.maturity)
			{entries.push(["Maturity", item.dimensions.maturity]);}
		if (item.dimensions.complexity)
			{entries.push(["Complexity", item.dimensions.complexity]);}
		if (item.dimensions.risk) {entries.push(["Risk", item.dimensions.risk]);}
		if (item.dimensions.coverage)
			{entries.push(["Coverage", item.dimensions.coverage]);}
		if (item.dimensions.custom) {
			Object.entries(item.dimensions.custom).forEach(([key, value]) => {
				entries.push([key, value]);
			});
		}
		return entries;
	}, [item?.dimensions]);

	const timelineEvents = useMemo(() => {
		if (!item)
			{return [] as { label: string; timestamp: string; detail?: string }[];}
		const events: { label: string; timestamp: string; detail?: string }[] =
			[];
		if (item.createdAt) {
			events.push({
				detail: `Status: ${item.status}`,
				label: "Item created",
				timestamp: item.createdAt,
			});
		}
		if (item.updatedAt) {
			events.push({
				detail: `v${item.version}`,
				label: "Item updated",
				timestamp: item.updatedAt,
			});
		}
		if (item.version > 1 && item.updatedAt) {
			events.push({
				detail: `Now at v${item.version}`,
				label: "Version bump",
				timestamp: item.updatedAt,
			});
		}
		if (integrationEntries.length > 0 && item.updatedAt) {
			const integration = integrationEntries.find(
				([key]) => key === "external_system",
			);
			events.push({
				detail: integration
					? `System: ${integration[1]}`
					: "Integration data attached",
				label: "External sync",
				timestamp: item.updatedAt,
			});
		}
		return [...events].toSorted((a, b) => (a.timestamp < b.timestamp ? 1 : -1));
	}, [integrationEntries, item]);

	const upstreamCount = targetLinks.length;
	const downstreamCount = sourceLinks.length;
	const metadataCount = metadataEntries.length;
	const displayStatus = isEditing
		? (draft?.status ?? "todo")
		: (item?.status ?? "todo");
	const displayPriority = isEditing
		? (draft?.priority ?? "medium")
		: (item?.priority ?? "medium");
	const updatedAtLabel = item?.updatedAt
		? new Date(item.updatedAt).toLocaleString()
		: "Unknown";
	const createdAtLabel = item?.createdAt
		? new Date(item.createdAt).toLocaleDateString()
		: "Unknown";

	const handleDelete = async () => {
		if (!itemId) {return;}
		try {
			await deleteItem.mutateAsync(itemId);
			toast.success("Item deleted successfully");
			handleBack();
		} catch {
			toast.error("Failed to delete item");
		}
	};

	const handleCancelEdit = () => {
		if (item) {
			setDraft({
				description: item.description ?? "",
				owner: item.owner ?? "",
				priority: item.priority ?? "medium",
				status: item.status ?? "todo",
				title: item.title ?? "",
			});
		}
		setIsEditing(false);
	};

	const handleSave = async () => {
		if (!itemId) {return;}
		try {
			await updateItem.mutateAsync({
				data: {
					description: draft.description,
					owner: draft.owner || undefined,
					priority: draft.priority as typeof item.priority,
					status: draft.status as typeof item.status,
					title: draft.title,
				},
				id: itemId,
			});
			toast.success("Item updated");
			setIsEditing(false);
		} catch {
			toast.error("Failed to update item");
		}
	};

	const handleCreateSpec = async (specType: string, itemId: string, _projectId?: string) => {
		try {
			switch (specType) {
				case "requirement": {
					await createRequirementSpec.mutateAsync({
						constraint_type: "soft",
						item_id: itemId,
						requirement_type: "ubiquitous",
					});
					toast.success("Requirement spec created");
					break;
				}
				case "test": {
					await createTestSpec.mutateAsync({
						item_id: itemId,
						test_type: "unit",
					});
					toast.success("Test spec created");
					break;
				}
				case "epic": {
					await createEpicSpec.mutateAsync({
						business_value: 0,
						epic_name: "New Epic",
						item_id: itemId,
					});
					toast.success("Epic spec created");
					break;
				}
				case "user_story": {
					await createUserStorySpec.mutateAsync({
						as_a: "User",
						i_want: "To complete task",
						item_id: itemId,
						so_that: "Work is done",
					});
					toast.success("User story spec created");
					break;
				}
				case "task": {
					await createTaskSpec.mutateAsync({
						item_id: itemId,
						task_title: "New Task",
					});
					toast.success("Task spec created");
					break;
				}
				case "defect": {
					await createDefectSpec.mutateAsync({
						defect_title: "New Defect",
						item_id: itemId,
						severity: "minor",
					});
					toast.success("Defect spec created");
					break;
				}
				default: {
					toast.error("Unknown spec type");
				}
			}
		} catch (error) {
			toast.error(`Failed to create ${specType} spec`);
			logger.error(error);
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
				<Button variant="outline" onClick={handleBack}>
					Return to Items
				</Button>
			</div>
		);
	}

	return (
		<div className="relative min-h-screen flex flex-col">
			<div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_15%,rgba(249,115,22,0.18),transparent_45%),radial-gradient(circle_at_80%_10%,rgba(14,116,144,0.2),transparent_45%),radial-gradient(circle_at_20%_80%,rgba(16,185,129,0.18),transparent_40%)]" />
			<div className="pointer-events-none absolute inset-0 bg-[linear-gradient(120deg,rgba(15,23,42,0.08),transparent_55%,rgba(2,132,199,0.08))]" />
			<div className="relative flex min-h-0 w-full max-w-[1600px] flex-1 flex-col px-6 py-6 mx-auto animate-in-fade-up md:py-10">
				<header className="shrink-0 pb-6 border-b border-border/50">
				<div className="flex items-center justify-between">
					<Button
						variant="ghost"
						size="sm"
						onClick={() => globalThis.history.back()}
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
							onClick={() => {
								const shareUrl = `${globalThis.location.origin}${globalThis.location.pathname}`;
								undefined;
								toast.success("Share link copied to clipboard");
							}}
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
								<span>
									<Button variant="ghost" size="icon" className="rounded-full">
										<MoreVertical className="h-4 w-4" />
									</Button>
								</span>
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
				</header>

				<main className="min-h-0 flex-1 overflow-auto pt-6 md:pt-8">
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
										<p className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-1">
											{item.view
												? `${String(item.view).charAt(0).toUpperCase()}${String(item.view).slice(1).toLowerCase()} · ${item.type}`
												: item.type}
										</p>
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
										onClick={() => {
											if (
												sourceLinks.length === 0 &&
												targetLinks.length === 0
											) {
												toast.info("No relationships to analyze");
											} else {
												const total = sourceLinks.length + targetLinks.length;
												toast.success(`Analyzed ${total} relationships`);
											}
										}}
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
												onCreateSpec={(specType) => {
													undefined;
												}}
											/>
										)}
									</TabsContent>

									<TabsContent value="links" className="pt-6 space-y-6">
										<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
											<Card className="border-0 bg-muted/40 p-5 space-y-4">
												<div className="flex items-center gap-2">
													<div className="h-9 w-9 rounded-xl bg-orange-500/15 flex items-center justify-center">
														<ArrowLeft className="h-4 w-4 text-orange-600" />
													</div>
													<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
														Upstream
													</h3>
												</div>
												<div className="space-y-3">
													{targetLinks.length > 0 ? (
														targetLinks.map((link) => (
															<Link
																key={link.id}
																to={buildItemLink(link.sourceId)}
																className="flex items-center gap-4 rounded-xl border border-border/50 bg-card/80 px-4 py-3 shadow-sm transition-all hover:border-orange-500/30 hover:bg-muted/50 hover:shadow-md"
															>
																<div className="h-10 w-10 shrink-0 rounded-xl bg-orange-500/10 flex items-center justify-center">
																	<ArrowLeft className="h-5 w-5 text-orange-500" />
																</div>
																<div className="min-w-0 flex-1 space-y-1">
																	<Badge variant="secondary" className="text-[10px] font-semibold uppercase tracking-wider">
																		{link.type}
																	</Badge>
																	<p className="font-mono text-xs font-medium text-foreground truncate" title={link.sourceId}>
																		{link.sourceId.slice(0, 8)}…
																	</p>
																</div>
																<span className="shrink-0 text-[10px] font-semibold uppercase text-muted-foreground">View</span>
																<ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground" />
															</Link>
														))
													) : (
														<div className="rounded-xl border-2 border-dashed border-border/50 bg-background/50 py-8 text-center">
															<p className="text-sm font-medium text-muted-foreground">No upstream dependencies</p>
															<p className="mt-1 text-xs text-muted-foreground/80">Links from other items will appear here</p>
														</div>
													)}
												</div>
											</Card>
											<Card className="border-0 bg-muted/40 p-5 space-y-4">
												<div className="flex items-center gap-2">
													<div className="h-9 w-9 rounded-xl bg-sky-500/15 flex items-center justify-center">
														<ArrowLeft className="h-4 w-4 text-sky-600 rotate-180" />
													</div>
													<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
														Downstream
													</h3>
												</div>
												<div className="space-y-3">
													{sourceLinks.length > 0 ? (
														sourceLinks.map((link) => (
															<Link
																key={link.id}
																to={buildItemLink(link.targetId)}
																className="flex items-center gap-4 rounded-xl border border-border/50 bg-card/80 px-4 py-3 shadow-sm transition-all hover:border-sky-500/30 hover:bg-muted/50 hover:shadow-md"
															>
																<div className="h-10 w-10 shrink-0 rounded-xl bg-sky-500/10 flex items-center justify-center">
																	<ArrowLeft className="h-5 w-5 text-sky-500 rotate-180" />
																</div>
																<div className="min-w-0 flex-1 space-y-1">
																	<Badge variant="secondary" className="text-[10px] font-semibold uppercase tracking-wider">
																		{link.type}
																	</Badge>
																	<p className="font-mono text-xs font-medium text-foreground truncate" title={link.targetId}>
																		{link.targetId.slice(0, 8)}…
																	</p>
																</div>
																<span className="shrink-0 text-[10px] font-semibold uppercase text-muted-foreground">View</span>
																<ExternalLink className="h-4 w-4 shrink-0 text-muted-foreground" />
															</Link>
														))
													) : (
														<div className="rounded-xl border-2 border-dashed border-border/50 bg-background/50 py-8 text-center">
															<p className="text-sm font-medium text-muted-foreground">No downstream impact</p>
															<p className="mt-1 text-xs text-muted-foreground/80">Items that depend on this will appear here</p>
														</div>
													)}
												</div>
											</Card>
										</div>
									</TabsContent>

									<TabsContent value="metadata" className="pt-6 space-y-6">
										<div className="flex flex-wrap items-center gap-3">
											<Input
												value={metadataSearch}
												onChange={(event) =>
													setMetadataSearch(event.target.value)
												}
												placeholder="Search metadata keys or values..."
												className="h-10 max-w-sm rounded-xl"
											/>
											<Badge
												variant="secondary"
												className="text-[10px] font-semibold uppercase tracking-widest px-3 py-1"
											>
												{filteredMetadata.length} entries
											</Badge>
										</div>
										{integrationEntries.length > 0 && (
											<div className="space-y-4">
												<div className="flex items-center gap-2">
													<div className="h-9 w-9 rounded-xl bg-amber-500/15 flex items-center justify-center">
														<Orbit className="h-4 w-4 text-amber-600" />
													</div>
													<span className="text-xs font-black uppercase tracking-widest text-muted-foreground">
														Integration context
													</span>
												</div>
												<div className="grid grid-cols-2 md:grid-cols-3 gap-3">
													{integrationEntries.map(([key, value]) => (
														<Card
															key={key}
															className="border border-border/50 bg-card/80 p-4 shadow-sm transition-shadow hover:shadow-md"
														>
															<p className="text-[10px] font-black uppercase tracking-wider text-muted-foreground mb-2">
																{key.replaceAll('_', " ")}
															</p>
															<p className="text-sm font-semibold text-foreground truncate" title={formatValue(value)}>
																{formatValue(value)}
															</p>
														</Card>
													))}
												</div>
											</div>
										)}

										{generalMetadata.length > 0 ? (
											<div className="space-y-4">
												<span className="text-xs font-black uppercase tracking-widest text-muted-foreground">
													Custom metadata
												</span>
												<div className="grid grid-cols-2 md:grid-cols-3 gap-3">
													{generalMetadata.map(([key, value]) => (
														<Card
															key={key}
															className="border border-border/50 bg-card/80 p-4 shadow-sm transition-shadow hover:shadow-md"
														>
															<p className="text-[10px] font-black uppercase tracking-wider text-muted-foreground mb-2">
																{key.replaceAll('_', " ")}
															</p>
															<p className="text-sm font-semibold text-foreground truncate" title={formatValue(value)}>
																{formatValue(value)}
															</p>
														</Card>
													))}
												</div>
											</div>
										) : (
											<Card className="border-2 border-dashed border-border/50 bg-muted/20 p-10 text-center">
												<p className="text-sm font-medium text-muted-foreground">No custom metadata defined</p>
												<p className="mt-1 text-xs text-muted-foreground/80">Add metadata to attach context to this item</p>
											</Card>
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
								onClick={() => {
									const impactCount = upstreamCount + downstreamCount;
									if (impactCount === 0) {
										toast.info("No impact relationships detected");
									} else {
										toast.success(
											`Impact analysis: ${impactCount} affected items`,
										);
									}
								}}
							>
								<Target className="h-4 w-4" />
								Open impact analysis
							</Button>
						</Card>

						<Card className="border-0 bg-muted/40 p-6 space-y-4 shadow-sm">
							<div className="flex items-center gap-2">
								<div className="h-9 w-9 rounded-xl bg-sky-500/15 flex items-center justify-center">
									<GitBranch className="h-4 w-4 text-sky-600" />
								</div>
								<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
									Dimensions
								</h3>
							</div>
							{dimensionEntries.length > 0 ? (
								<div className="space-y-3">
									{dimensionEntries.map(([label, value]) => (
										<div
											key={label}
											className="flex items-center justify-between rounded-xl border border-border/40 bg-card/60 px-4 py-3 shadow-sm"
										>
											<span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
												{label}
											</span>
											<span className="text-sm font-semibold text-foreground truncate max-w-[60%]" title={formatValue(value)}>
												{formatValue(value)}
											</span>
										</div>
									))}
								</div>
							) : (
								<p className="rounded-xl border border-dashed border-border/50 bg-background/50 py-4 text-center text-xs text-muted-foreground italic">
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

						<Card className="border-0 bg-muted/40 p-6 space-y-4 shadow-sm">
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Change log
							</h3>
							{timelineEvents.length > 0 ? (
								<div className="relative space-y-0">
									{/* Vertical line */}
									<div className="absolute left-[11px] top-2 bottom-2 w-px bg-border" />
									{timelineEvents.map((event) => (
										<div
											key={`${event.label}-${event.timestamp}`}
											className="relative flex items-start gap-4 pb-6 last:pb-0"
										>
											<div className="relative z-10 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border-2 border-primary/40 bg-primary/10">
												<div className="h-1.5 w-1.5 rounded-full bg-primary" />
											</div>
											<div className="min-w-0 flex-1 rounded-xl border border-border/40 bg-card/60 px-4 py-3 shadow-sm">
												<p className="text-sm font-semibold text-foreground">{event.label}</p>
												{event.detail && (
													<p className="mt-1 text-xs text-muted-foreground">{event.detail}</p>
												)}
												<p className="mt-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
													{new Date(event.timestamp).toLocaleDateString(undefined, {
														day: "numeric",
														hour: "2-digit",
														minute: "2-digit",
														month: "short",
														year: "numeric",
													})}
												</p>
											</div>
										</div>
									))}
								</div>
							) : (
								<p className="rounded-xl border border-dashed border-border/50 bg-background/50 py-6 text-center text-xs text-muted-foreground italic">
									No change events recorded.
								</p>
							)}
						</Card>

						<Card className="border-0 bg-muted/40 p-6 space-y-4 shadow-sm">
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Activity timeline
							</h3>
							<div className="space-y-3">
								<div className="flex items-center justify-between rounded-xl border border-border/40 bg-card/60 px-4 py-3 shadow-sm">
									<span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Created</span>
									<span className="text-sm font-semibold text-foreground">{createdAtLabel}</span>
								</div>
								<div className="flex items-center justify-between rounded-xl border border-border/40 bg-card/60 px-4 py-3 shadow-sm">
									<span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">Updated</span>
									<span className="text-sm font-semibold text-foreground">{updatedAtLabel}</span>
								</div>
								<div className="flex items-center justify-between rounded-xl border border-border/40 bg-card/60 px-4 py-3 shadow-sm">
									<span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">System lag</span>
									<span className="inline-flex items-center gap-1.5 text-sm font-semibold text-foreground">
										<Timer className="h-3.5 w-3.5 text-primary" />
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
				</main>
			</div>
		</div>
	);
}
