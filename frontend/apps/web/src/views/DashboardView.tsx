import { Link, useNavigate } from "@tanstack/react-router";
import {
	Badge,
	Button,
	Card,
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuSeparator,
	DropdownMenuTrigger,
	Input,
	Progress,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Skeleton,
	Tabs,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui";
import {
	Activity,
	BarChart3,
	Edit,
	ExternalLink,
	Folder,
	Layers,
	LayoutGrid,
	List,
	MoreVertical,
	Pin,
	Plus,
	Search,
	Trash2,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
	Bar,
	BarChart,
	CartesianGrid,
	Cell,
	Pie,
	PieChart,
	PolarAngleAxis,
	PolarGrid,
	Radar,
	RadarChart,
	Tooltip as RechartsTooltip,
	ResponsiveContainer,
	XAxis,
	YAxis,
} from "recharts";
import { toast } from "sonner";
import { getProjectDisplayName } from "@/lib/project-name-utils";
import { cn } from "@/lib/utils";
import { useDeleteProject, useProjects } from "../hooks/useProjects";
import client from "@/api/client";

const { getAuthHeaders } = client;

interface DashboardViewProps {
	systemStatus?: {
		status?: string;
		mcp?: { baseUrl?: string | null };
	};
}

export function DashboardView({ systemStatus }: DashboardViewProps) {
	const navigate = useNavigate();
	const { data: projects, isLoading: projectsLoading } = useProjects();
	const deleteProject = useDeleteProject();
	const [allItems, setAllItems] = useState<any[]>([]);
	const [itemsLoading, setItemsLoading] = useState(false);
	const [projectItemCounts, setProjectItemCounts] = useState<
		Record<string, number>
	>({});
	const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
	const [searchQuery, setSearchQuery] = useState("");
	const [sortBy, setSortBy] = useState<"name" | "items" | "progress">("name");
	const [pinnedProjectId, setPinnedProjectId] = useState<string | null>(null);

	const [slot1Tab, setSlot1Tab] = useState("distribution");
	const [slot2Tab, setSlot2Tab] = useState("status");

	// Ensure projects is always an array - memoize to prevent infinite loops
	const projectsArray = useMemo(() => Array.isArray(projects) ? projects : [], [projects]);

	// Set default pinned project
	useEffect(() => {
		if (projectsArray.length > 0 && !pinnedProjectId) {
			const firstProject = projectsArray[0];
			if (firstProject?.id) {
				setPinnedProjectId(firstProject.id);
			}
		}
	}, [projectsArray, pinnedProjectId]);

	// Fetch items from all projects for dashboard stats
	useEffect(() => {
		if (!projectsArray || projectsArray.length === 0) {
			setAllItems([]);
			setItemsLoading(false);
			return;
		}

		setItemsLoading(true);

		Promise.all(
			projectsArray.map(async (project) => {
				try {
					const res = await fetch(
						`${import.meta.env.VITE_API_URL || "http://localhost:4000"}/api/v1/items?project_id=${project.id}&limit=200`,
						{
							headers: {
								"X-Bulk-Operation": "true",
								...getAuthHeaders(),
							},
						},
					);
					if (!res.ok) {
						return { count: 0, items: [], projectId: project.id };
					}
					const data = await res.json();
					const total = data.total || 0;
					const items = Array.isArray(data) ? data : data.items || [];
					return {
						count: total,
						items: items.map((item: any) => (Object.assign(item, {projectId:item.projectId||project.id}))),
						projectId: project.id,
					};
				} catch {
					return { count: 0, items: [], projectId: project.id };
				}
			}),
		)
			.then((results) => {
				const projectCounts: Record<string, number> = {};
				results.forEach((r: any) => {
					if (r.projectId) {
						projectCounts[r.projectId] = r.count || 0;
					}
				});

				const allItemsFlat = results.flatMap((r: any) => r.items || []);
				setAllItems(allItemsFlat);
				setProjectItemCounts(projectCounts);
				setItemsLoading(false);
			})
			.catch(() => {
				setAllItems([]);
				setProjectItemCounts({});
				setItemsLoading(false);
			});
	}, [projectsArray]);

	const statusData = useMemo(() => {
		const counts: Record<string, number> = {};
		for (const item of allItems) {
			const status = item.status || "unknown";
			counts[status] = (counts[status] || 0) + 1;
		}
		return Object.entries(counts).map(([name, value]) => ({ name, value }));
	}, [allItems]);

	const typeData = useMemo(() => {
		const counts: Record<string, number> = {};
		for (const item of allItems) {
			const type = item.type || "other";
			counts[type] = (counts[type] || 0) + 1;
		}
		return Object.entries(counts).map(([name, value]) => ({ name, value }));
	}, [allItems]);

	const COLORS = [
		"#3b82f6",
		"#10b981",
		"#f59e0b",
		"#ef4444",
		"#8b5cf6",
		"#ec4899",
	];

	const projectsWithStats = useMemo(() => projectsArray.map((project) => {
			const pItems = allItems.filter((item) => item.projectId === project.id);
			const completed = pItems.filter(
				(item) => item.status === "done" || item.status === "completed",
			).length;
			const progress =
				pItems.length > 0 ? (completed / pItems.length) * 100 : 0;
			return {
				...project,
				displayName: getProjectDisplayName(project),
				itemCount: projectItemCounts[project.id] || pItems.length,
				progress,
			};
		}), [projectsArray, allItems, projectItemCounts]);

	const pinnedProject = useMemo(() => (
			projectsWithStats.find((p) => p.id === pinnedProjectId) ||
			projectsWithStats[0]
		), [projectsWithStats, pinnedProjectId]);

	const pinnedProjectDetails = useMemo(() => {
		if (!pinnedProject) {return [];}
		const pItems = allItems.filter(
			(item) => item.projectId === pinnedProject.id,
		);
		const types = ["requirement", "feature", "test", "task", "bug"];
		return types.map((type) => ({
			A: pItems.filter((i) => i.type === type).length,
			fullMark: Math.max(
				...types.map((t) => pItems.filter((i) => i.type === t).length),
				10,
			),
			subject: type.charAt(0).toUpperCase() + type.slice(1),
		}));
	}, [pinnedProject, allItems]);

	const filteredProjects = useMemo(() => {
		let result = projectsWithStats.filter((p) =>
			(p.displayName || p.name)
				.toLowerCase()
				.includes(searchQuery.toLowerCase()),
		);

		result = [...result].toSorted((a, b) => {
			if (sortBy === "name") {
				const aName = a.displayName || a.name;
				const bName = b.displayName || b.name;
				return aName.localeCompare(bName);
			}
			if (sortBy === "items") {return b.itemCount - a.itemCount;}
			if (sortBy === "progress") {return b.progress - a.progress;}
			return 0;
		});

		return result;
	}, [projectsWithStats, searchQuery, sortBy]);

	if (projectsLoading || itemsLoading) {
		return (
			<div className="p-6 space-y-6">
				<div className="flex justify-between items-center">
					<Skeleton className="h-10 w-48" />
					<Skeleton className="h-10 w-32" />
				</div>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
					{[...Array(3)].map((_, i) => (
						<Skeleton key={i} className="h-64" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in-fade-up">
			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
				<div>
					<h1 className="text-2xl font-bold tracking-tight">
						Traceability Dashboard
					</h1>
					<p className="text-sm text-muted-foreground">
						Monitor project health and system-wide traceability status.
					</p>
					<div className="flex flex-wrap items-center gap-2 mt-3">
						<Badge variant="outline" className="text-xs">
							System: {systemStatus?.status ?? "healthy"}
						</Badge>
						<Badge
							variant={systemStatus?.mcp?.baseUrl ? "default" : "secondary"}
							className="text-xs"
						>
							MCP: {systemStatus?.mcp?.baseUrl ? "connected" : "not configured"}
						</Badge>
						{systemStatus?.mcp?.baseUrl ? (
							<Button
								variant="outline"
								size="sm"
								className="h-7 px-2 text-xs"
								onClick={() => {
									window.open(systemStatus.mcp?.baseUrl ?? "#", "_blank");
								}}
							>
								Open MCP
							</Button>
						) : null}
					</div>
				</div>
			</div>

			{/* Visual Insights Section */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
				{/* Slot 1: Large Widget (Distribution / Pinned Project Detail) */}
				<Card className="p-0 col-span-1 lg:col-span-2 overflow-hidden border-none shadow-sm bg-card/50">
					<Tabs value={slot1Tab} onValueChange={setSlot1Tab} className="w-full">
						<div className="px-6 pt-6 flex items-center justify-between">
							<div className="flex items-center gap-3">
								<div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
									{slot1Tab === "distribution" ? (
										<BarChart3 className="h-4 w-4 text-primary" />
									) : (
										<Pin className="h-4 w-4 text-primary" />
									)}
								</div>
								<h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground/80">
									{slot1Tab === "distribution"
										? "Global Distribution"
										: `Project Focus: ${pinnedProject?.displayName || pinnedProject?.name}`}
								</h3>
							</div>
							<TabsList className="bg-muted/50">
								<TabsTrigger
									value="distribution"
									className="text-xs cursor-pointer hover:bg-muted/70 transition-colors"
								>
									Network
								</TabsTrigger>
								<TabsTrigger
									value="focus"
									className="text-xs cursor-pointer hover:bg-muted/70 transition-colors"
								>
									Pinned
								</TabsTrigger>
							</TabsList>
						</div>

						<div className="p-6 h-[320px]">
							{slot1Tab === "distribution" ? (
								<ResponsiveContainer width="100%" height="100%">
									<BarChart data={projectsWithStats.slice(0, 12)}>
										<CartesianGrid
											strokeDasharray="3 3"
											vertical={false}
											stroke="hsl(var(--muted)/0.3)"
										/>
										<XAxis
											dataKey="displayName"
											fontSize={10}
											tickLine={false}
											axisLine={false}
											tick={{ fill: "hsl(var(--muted-foreground))" }}
										/>
										<YAxis
											fontSize={10}
											tickLine={false}
											axisLine={false}
											tick={{ fill: "hsl(var(--muted-foreground))" }}
										/>
										<RechartsTooltip
											cursor={{ fill: "hsl(var(--muted)/0.2)" }}
											contentStyle={{
												backgroundColor: "hsl(var(--card))",
												borderColor: "hsl(var(--border))",
												borderRadius: "8px",
												fontSize: "12px",
											}}
										/>
										<Bar
											dataKey="itemCount"
											fill="hsl(var(--primary))"
											radius={[4, 4, 0, 0]}
										/>
									</BarChart>
								</ResponsiveContainer>
							) : (
								<div className="grid grid-cols-1 md:grid-cols-2 h-full gap-4">
									<div className="h-full">
										<ResponsiveContainer width="100%" height="100%">
											<RadarChart
												cx="50%"
												cy="50%"
												outerRadius="80%"
												data={pinnedProjectDetails}
											>
												<PolarGrid stroke="hsl(var(--muted))" />
												<PolarAngleAxis
													dataKey="subject"
													fontSize={10}
													tick={{ fill: "hsl(var(--muted-foreground))" }}
												/>
												<Radar
													name={
														pinnedProject?.displayName || pinnedProject?.name
													}
													dataKey="A"
													stroke="hsl(var(--primary))"
													fill="hsl(var(--primary))"
													fillOpacity={0.6}
												/>
											</RadarChart>
										</ResponsiveContainer>
									</div>
									<div className="flex flex-col justify-center space-y-4 px-4">
										<div>
											<div className="flex justify-between text-xs mb-1">
												<span className="text-muted-foreground">
													Overall Completion
												</span>
												<span className="font-bold">
													{Math.round(pinnedProject?.progress || 0)}%
												</span>
											</div>
											<Progress
												value={pinnedProject?.progress}
												className="h-2"
											/>
										</div>
										<div className="grid grid-cols-2 gap-4">
											<div className="bg-muted/30 p-3 rounded-lg border border-border/50">
												<div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">
													Total Items
												</div>
												<div className="text-xl font-bold">
													{pinnedProject?.itemCount}
												</div>
											</div>
											<div className="bg-muted/30 p-3 rounded-lg border border-border/50">
												<div className="text-[10px] text-muted-foreground uppercase font-bold mb-1">
													Activity
												</div>
												<div className="text-xl font-bold text-green-500">
													High
												</div>
											</div>
										</div>
									</div>
								</div>
							)}
						</div>
					</Tabs>
				</Card>

				{/* Slot 2: Smaller Widget (Status / Priority / Type) */}
				<Card className="p-0 overflow-hidden border-none shadow-sm bg-card/50">
					<Tabs value={slot2Tab} onValueChange={setSlot2Tab} className="w-full">
						<div className="px-6 pt-6 flex items-center justify-between">
							<div className="flex items-center gap-3">
								<div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
									<Layers className="h-4 w-4 text-primary" />
								</div>
								<h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground/80">
									Metrics
								</h3>
							</div>
							<TabsList className="bg-muted/50">
								<TabsTrigger
									value="status"
									className="text-xs cursor-pointer hover:bg-muted/70 transition-colors"
								>
									Status
								</TabsTrigger>
								<TabsTrigger
									value="type"
									className="text-xs cursor-pointer hover:bg-muted/70 transition-colors"
								>
									Type
								</TabsTrigger>
							</TabsList>
						</div>

						<div className="p-6 h-[320px] flex flex-col">
							<div className="flex-1">
								<ResponsiveContainer width="100%" height="100%">
									<PieChart>
										<Pie
											data={slot2Tab === "status" ? statusData : typeData}
											cx="50%"
											cy="50%"
											innerRadius={60}
											outerRadius={80}
											paddingAngle={5}
											dataKey="value"
										>
											{(slot2Tab === "status" ? statusData : typeData).map(
												(_, index) => (
													<Cell
														key={`cell-${index}`}
														fill={COLORS[index % COLORS.length]}
													/>
												),
											)}
										</Pie>
										<RechartsTooltip
											contentStyle={{
												backgroundColor: "hsl(var(--card))",
												borderColor: "hsl(var(--border))",
												borderRadius: "8px",
												fontSize: "12px",
											}}
										/>
									</PieChart>
								</ResponsiveContainer>
							</div>
							<div className="mt-4 grid grid-cols-2 gap-x-4 gap-y-1">
								{(slot2Tab === "status" ? statusData : typeData)
									.slice(0, 6)
									.map((entry, index) => (
										<div
											key={entry.name}
											className="flex items-center gap-2 min-w-0"
										>
											<div
												className="w-1.5 h-1.5 rounded-full shrink-0"
												style={{
													backgroundColor: COLORS[index % COLORS.length],
												}}
											/>
											<span className="text-[10px] text-muted-foreground truncate uppercase font-medium">
												{entry.name}
											</span>
											<span className="text-[10px] font-bold ml-auto">
												{entry.value}
											</span>
										</div>
									))}
							</div>
						</div>
					</Tabs>
				</Card>
			</div>

			{/* Projects Section */}
			<div className="space-y-4">
				<div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
					<div className="flex items-center gap-2">
						<Activity className="h-5 w-5 text-primary" />
						<h2 className="text-lg font-bold tracking-tight">
							Active Projects
						</h2>
					</div>
					<div className="flex items-center gap-2 w-full sm:w-auto">
						<div className="relative flex-1 sm:w-64">
							<Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
							<Input
								placeholder="Search projects..."
								className="pl-9 h-9 border-none bg-muted/50 focus-visible:ring-1"
								value={searchQuery}
								onChange={(e) => setSearchQuery(e.target.value)}
							/>
						</div>
						<Select value={sortBy} onValueChange={(v: any) => setSortBy(v)}>
							<SelectTrigger className="h-9 w-[130px] border-none bg-muted/50">
								<SelectValue placeholder="Sort by" />
							</SelectTrigger>
							<SelectContent>
								<SelectItem
									value="name"
									className="cursor-pointer hover:bg-accent"
								>
									Name
								</SelectItem>
								<SelectItem
									value="items"
									className="cursor-pointer hover:bg-accent"
								>
									Item Count
								</SelectItem>
								<SelectItem
									value="progress"
									className="cursor-pointer hover:bg-accent"
								>
									Progress
								</SelectItem>
							</SelectContent>
						</Select>
						<Tabs value={viewMode} onValueChange={(v: any) => setViewMode(v)}>
							<TabsList className="h-9 p-0.5 bg-muted/50">
								<TabsTrigger
									value="grid"
									className="h-8 px-2 cursor-pointer hover:bg-muted/70 transition-colors"
								>
									<LayoutGrid className="h-4 w-4" />
								</TabsTrigger>
								<TabsTrigger
									value="list"
									className="h-8 px-2 cursor-pointer hover:bg-muted/70 transition-colors"
								>
									<List className="h-4 w-4" />
								</TabsTrigger>
							</TabsList>
						</Tabs>
						<Link to="/projects" search={{ action: "create" } as any}>
							<Button size="sm" className="h-9 shadow-sm">
								<Plus className="h-4 w-4 mr-2" />
								New Project
							</Button>
						</Link>
					</div>
				</div>

				{viewMode === "grid" ? (
					<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 stagger-children">
						{filteredProjects.map((project) => {
							const handlePin = (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								const wasPinned = pinnedProjectId === project.id;
								setPinnedProjectId(wasPinned ? null : project.id);
								if (!wasPinned) {
									toast.success(
										`Pinned ${project.displayName || project.name} to dashboard`,
									);
								}
							};

							const handleDelete = async (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								const projectDisplayName = project.displayName || project.name;
								if (
									!confirm(
										`Are you sure you want to delete "${projectDisplayName}"? This action cannot be undone.`,
									)
								) {
									return;
								}
								try {
									await deleteProject.mutateAsync(project.id);
									toast.success(`Project "${projectDisplayName}" deleted`);
									if (pinnedProjectId === project.id) {
										setPinnedProjectId(null);
									}
								} catch {
									toast.error("Failed to delete project");
								}
							};

							const handleEdit = (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								undefined;
								toast.info("Edit project in project details");
							};

							return (
								<div key={project.id} className="relative group">
									<Link
										to={`/projects/${project.id}`}
										className="cursor-pointer"
									>
										<Card className="p-5 hover:shadow-xl transition-all h-full border border-border/50 bg-card hover:bg-card/90 shadow-md hover:border-primary/30">
											{/* Pin button - top left */}
											<button
												onClick={handlePin}
												className={cn(
													"absolute top-3 left-3 p-1.5 rounded-lg transition-all z-10 cursor-pointer",
													pinnedProjectId === project.id
														? "bg-primary text-primary-foreground opacity-100 hover:bg-primary/90"
														: "bg-muted/50 text-muted-foreground opacity-0 group-hover:opacity-100 hover:bg-primary/20 hover:text-primary",
												)}
												title={
													pinnedProjectId === project.id
														? "Unpin project"
														: "Pin project"
												}
											>
												<Pin
													className={cn(
														"h-3.5 w-3.5",
														pinnedProjectId === project.id && "fill-current",
													)}
												/>
											</button>

											{/* 3-dot menu - top right */}
											<DropdownMenu>
												<DropdownMenuTrigger asChild>
													<span>
														<Button
															variant="ghost"
															size="icon"
															className="absolute top-3 right-3 h-7 w-7 text-muted-foreground hover:text-foreground hover:bg-muted opacity-0 group-hover:opacity-100 transition-all z-10"
															onClick={(e) => e.stopPropagation()}
														>
															<MoreVertical className="h-4 w-4" />
															<span className="sr-only">Project options</span>
														</Button>
													</span>
												</DropdownMenuTrigger>
												<DropdownMenuContent align="end" className="w-48">
													<DropdownMenuItem
														onClick={(e) => {
															e.stopPropagation();
															undefined;
														}}
														className="gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors"
													>
														<ExternalLink className="h-4 w-4" />
														Open Project
													</DropdownMenuItem>
													<DropdownMenuItem
														onClick={(e) => {
															e.stopPropagation();
															handleEdit(e);
														}}
														className="gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors"
													>
														<Edit className="h-4 w-4" />
														Edit
													</DropdownMenuItem>
													<DropdownMenuSeparator />
													<DropdownMenuItem
														onClick={(e) => {
															e.stopPropagation();
															undefined;
														}}
														className="gap-2 text-destructive focus:text-destructive focus:bg-destructive/10 cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
													>
														<Trash2 className="h-4 w-4" />
														Delete
													</DropdownMenuItem>
												</DropdownMenuContent>
											</DropdownMenu>

											<div className="pt-2">
												<div className="flex justify-between items-start mb-3">
													<h3 className="font-bold text-sm group-hover:text-primary transition-colors truncate pr-2 flex-1">
														{project.displayName || project.name}
													</h3>
													<Badge
														variant="secondary"
														className="text-[9px] px-1.5 h-4 font-bold uppercase tracking-tighter shrink-0 ml-2"
													>
														{project.itemCount}
													</Badge>
												</div>
												<p className="text-xs text-muted-foreground line-clamp-2 mb-4 h-8 leading-relaxed">
													{project.description ||
														"System generated project for traceability management."}
												</p>
												<div className="space-y-2">
													<div className="flex justify-between text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60">
														<span>Coverage</span>
														<span>{Math.round(project.progress)}%</span>
													</div>
													<Progress
														value={project.progress}
														className="h-1.5 bg-muted"
													/>
												</div>
											</div>
										</Card>
									</Link>
								</div>
							);
						})}
					</div>
				) : (
					<Card className="divide-y border border-border/50 bg-card/50 overflow-hidden">
						{filteredProjects.map((project) => {
							const handlePin = (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								const wasPinned = pinnedProjectId === project.id;
								setPinnedProjectId(wasPinned ? null : project.id);
								if (!wasPinned) {
									toast.success(
										`Pinned ${project.displayName || project.name} to dashboard`,
									);
								}
							};

							const handleDelete = async (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								const projectDisplayName = project.displayName || project.name;
								if (
									!confirm(
										`Are you sure you want to delete "${projectDisplayName}"? This action cannot be undone.`,
									)
								) {
									return;
								}
								try {
									await deleteProject.mutateAsync(project.id);
									toast.success(`Project "${projectDisplayName}" deleted`);
									if (pinnedProjectId === project.id) {
										setPinnedProjectId(null);
									}
								} catch {
									toast.error("Failed to delete project");
								}
							};

							const handleEdit = (e: React.MouseEvent) => {
								e.preventDefault();
								e.stopPropagation();
								undefined;
								toast.info("Edit project in project details");
							};

							return (
								<div key={project.id} className="relative group">
									<Link
										to={`/projects/${project.id}`}
										className="block cursor-pointer"
									>
										<div className="p-4 hover:bg-muted/50 transition-colors flex items-center gap-6">
											{/* Pin button - left side */}
											<button
												onClick={handlePin}
												className={cn(
													"cursor-pointer",
													"p-1.5 rounded-lg transition-all shrink-0",
													pinnedProjectId === project.id
														? "bg-primary text-primary-foreground opacity-100"
														: "bg-muted/50 text-muted-foreground opacity-0 group-hover:opacity-100 hover:bg-primary/20",
												)}
												title={
													pinnedProjectId === project.id
														? "Unpin project"
														: "Pin project"
												}
											>
												<Pin
													className={cn(
														"h-3.5 w-3.5",
														pinnedProjectId === project.id && "fill-current",
													)}
												/>
											</button>

											<div
												className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 transition-colors ${
													pinnedProjectId === project.id
														? "bg-primary text-primary-foreground"
														: "bg-primary/10 text-primary"
												}`}
											>
												<Folder className="h-5 w-5" />
											</div>
											<div className="flex-1 min-w-0">
												<div className="flex items-center gap-2">
													<h3 className="text-sm font-bold truncate">
														{project.displayName || project.name}
													</h3>
												</div>
												<p className="text-xs text-muted-foreground truncate max-w-md">
													{project.description}
												</p>
											</div>
											<div className="w-48 hidden lg:block">
												<div className="flex justify-between text-[9px] font-bold uppercase text-muted-foreground/60 mb-1">
													<span>Progress</span>
													<span>{Math.round(project.progress)}%</span>
												</div>
												<Progress value={project.progress} className="h-1" />
											</div>
											<div className="text-right shrink-0 min-w-[80px]">
												<div className="text-xs font-black">
													{project.itemCount}
												</div>
												<div className="text-[9px] text-muted-foreground uppercase font-bold tracking-tighter">
													Items
												</div>
											</div>
										</div>
									</Link>
									{/* 3-dot menu - right side */}
									<DropdownMenu>
										<DropdownMenuTrigger asChild>
											<span>
												<Button
													variant="ghost"
													size="icon"
													className="absolute right-4 top-1/2 -translate-y-1/2 h-8 w-8 text-muted-foreground hover:text-foreground hover:bg-muted opacity-0 group-hover:opacity-100 transition-all"
													onClick={(e) => e.stopPropagation()}
												>
													<MoreVertical className="h-4 w-4" />
													<span className="sr-only">Project options</span>
												</Button>
											</span>
										</DropdownMenuTrigger>
										<DropdownMenuContent align="end" className="w-48">
											<DropdownMenuItem
												onClick={(e) => {
													e.stopPropagation();
													undefined;
												}}
												className="gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors"
											>
												<ExternalLink className="h-4 w-4" />
												Open Project
											</DropdownMenuItem>
											<DropdownMenuItem
												onClick={(e) => {
													e.stopPropagation();
													handleEdit(e);
												}}
												className="gap-2 cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors"
											>
												<Edit className="h-4 w-4" />
												Edit
											</DropdownMenuItem>
											<DropdownMenuSeparator />
											<DropdownMenuItem
												onClick={(e) => {
													e.stopPropagation();
													undefined;
												}}
												className="gap-2 text-destructive focus:text-destructive focus:bg-destructive/10 cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
											>
												<Trash2 className="h-4 w-4" />
												Delete
											</DropdownMenuItem>
										</DropdownMenuContent>
									</DropdownMenu>
								</div>
							);
						})}
					</Card>
				)}

				{filteredProjects.length === 0 && (
					<div className="text-center py-20 bg-muted/20 rounded-2xl border-2 border-dashed border-muted">
						<Folder className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-20" />
						<p className="text-muted-foreground font-medium">
							No projects match your current search criteria.
						</p>
						<Button
							variant="link"
							onClick={() => setSearchQuery("")}
							className="mt-2 text-primary"
						>
							Clear search
						</Button>
					</div>
				)}
			</div>
		</div>
	);
}
