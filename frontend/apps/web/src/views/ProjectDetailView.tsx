import { Link, useNavigate, useParams } from "@tanstack/react-router";
import type { Item, Link as LinkType } from "@tracertm/types";
import {
	Alert,
	AlertDescription,
	AlertTitle,
} from "@tracertm/ui/components/Alert";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Progress } from "@tracertm/ui/components/Progress";
import { Separator } from "@tracertm/ui/components/Separator";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	Tabs,
	TabsContent,
	TabsList,
	TabsTrigger,
} from "@tracertm/ui/components/Tabs";
import {
	Activity,
	AlertCircle,
	ArrowRight,
	BarChart,
	BookOpen,
	Calendar,
	CheckCircle2,
	ClipboardList,
	Clock,
	Code,
	Database,
	Edit,
	FileText,
	Layout,
	Link2,
	Network,
	Plus,
	Rocket,
	Shield,
	TestTube,
	TrendingUp,
	XCircle,
	Zap,
} from "lucide-react";
import { useMemo } from "react";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";
import { useProject, useUpdateProject } from "../hooks/useProjects";
import { useProjectStore } from "../stores";

interface ItemsByType {
	[key: string]: Item[];
}

interface ProjectStatsProps {
	items: Item[];
	itemsTotal: number;
	links: LinkType[];
	linksTotal: number;
}

const typeIcons: Record<string, any> = {
	requirement: FileText,
	feature: Code,
	test: TestTube,
	api: Network,
	database: Database,
	component: Layout,
	documentation: BookOpen,
	security: Shield,
	performance: Zap,
	deployment: Rocket,
};

const statusColors: Record<string, string> = {
	done: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200",
	in_progress: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200",
	todo: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200",
	blocked: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200",
	cancelled:
		"bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200",
};

const priorityColors: Record<string, string> = {
	"0": "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
	"1": "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400",
	"2": "bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-400",
	"3": "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400",
	low: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
	medium: "bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400",
	high: "bg-orange-100 text-orange-600 dark:bg-orange-900 dark:text-orange-400",
	critical: "bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400",
};

function ProjectStats({
	items,
	itemsTotal,
	links,
	linksTotal,
}: ProjectStatsProps & { itemsTotal: number; linksTotal: number }) {
	const stats = useMemo(() => {
		const itemsByStatus = items.reduce(
			(acc, item) => {
				acc[item.status] = (acc[item.status] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>,
		);

		const itemsByType = items.reduce(
			(acc, item) => {
				acc[item.type] = (acc[item.type] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>,
		);

		const completionRate =
			itemsTotal > 0
				? Math.round(((itemsByStatus.completed || 0) / itemsTotal) * 100)
				: 0;

		return {
			total: itemsTotal,
			todo: itemsByStatus.pending || 0,
			in_progress: itemsByStatus.in_progress || 0,
			done: itemsByStatus.completed || 0,
			blocked: itemsByStatus.blocked || 0,
			completionRate,
			links: linksTotal,
			itemsByType,
		};
	}, [items, itemsTotal, linksTotal]);

	return (
		<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			<Card className="p-6 border-l-4 border-l-blue-500">
				<div className="flex items-center justify-between">
					<div>
						<p className="text-sm font-medium text-muted-foreground">
							Total Items
						</p>
						<p className="text-3xl font-bold mt-2">{stats.total}</p>
					</div>
					<ClipboardList className="h-8 w-8 text-blue-500 opacity-50" />
				</div>
			</Card>

			<Card className="p-6 border-l-4 border-l-green-500">
				<div className="flex items-center justify-between">
					<div>
						<p className="text-sm font-medium text-muted-foreground">
							Completed
						</p>
						<p className="text-3xl font-bold mt-2 text-green-600 dark:text-green-400">
							{stats.done}
						</p>
						<Progress value={stats.completionRate} className="mt-2 h-2" />
					</div>
					<CheckCircle2 className="h-8 w-8 text-green-500 opacity-50" />
				</div>
			</Card>

			<Card className="p-6 border-l-4 border-l-orange-500">
				<div className="flex items-center justify-between">
					<div>
						<p className="text-sm font-medium text-muted-foreground">
							In Progress
						</p>
						<p className="text-3xl font-bold mt-2 text-orange-600 dark:text-orange-400">
							{stats.in_progress}
						</p>
					</div>
					<Clock className="h-8 w-8 text-orange-500 opacity-50" />
				</div>
			</Card>

			<Card className="p-6 border-l-4 border-l-purple-500">
				<div className="flex items-center justify-between">
					<div>
						<p className="text-sm font-medium text-muted-foreground">
							Traceability Links
						</p>
						<p className="text-3xl font-bold mt-2 text-purple-600 dark:text-purple-400">
							{stats.links}
						</p>
					</div>
					<Link2 className="h-8 w-8 text-purple-500 opacity-50" />
				</div>
			</Card>
		</div>
	);
}

interface RichItemCardProps {
	item: Item;
	projectId?: string;
}

function RichItemCard({ item }: RichItemCardProps) {
	const Icon = typeIcons[item.type] || FileText;
	const statusColor =
		statusColors[item.status] ||
		"bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200";
	const priorityColor =
		priorityColors[item.priority?.toString() || "0"] ||
		"bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400";

	return (
		<Link to={`/items/${item.id}`}>
			<Card className="p-5 hover:shadow-lg transition-all duration-200 border-l-4 border-l-blue-500 group cursor-pointer">
				<div className="flex items-start justify-between gap-4">
					<div className="flex-1 min-w-0">
						<div className="flex items-start gap-3 mb-3">
							<div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/30 transition-colors">
								<Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
							</div>
							<div className="flex-1 min-w-0">
								<h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors line-clamp-2">
									{item.title}
								</h3>
								{item.description && (
									<p className="text-sm text-muted-foreground mt-1 line-clamp-2">
										{item.description}
									</p>
								)}
							</div>
						</div>

						<div className="flex flex-wrap items-center gap-2 mt-4">
							<Badge className={statusColor}>
								{item.status === "in_progress" && (
									<Clock className="h-3 w-3 mr-1" />
								)}
								{item.status === "completed" && (
									<CheckCircle2 className="h-3 w-3 mr-1" />
								)}
								{item.status === "blocked" && (
									<XCircle className="h-3 w-3 mr-1" />
								)}
								{item.status.replace("_", " ")}
							</Badge>
							<Badge variant="outline" className={priorityColor}>
								Priority: {item.priority || "medium"}
							</Badge>
							<Badge variant="outline">{item.type}</Badge>
						</div>

						{item.createdAt && (
							<div className="flex items-center gap-2 mt-3 text-xs text-muted-foreground">
								<Calendar className="h-3 w-3" />
								<span>
									Created: {new Date(item.createdAt).toLocaleDateString()}
								</span>
							</div>
						)}
					</div>
					<ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors opacity-0 group-hover:opacity-100" />
				</div>
			</Card>
		</Link>
	);
}

interface TypeSectionProps {
	type: string;
	items: Item[];
	projectId: string;
	itemsTotal?: number;
}

function TypeSection({ type, items, projectId }: TypeSectionProps) {
	const Icon = typeIcons[type] || FileText;
	// Use actual count from items array (which may be paginated), but show total in badge
	const displayedCount = items.length;
	const completedCount = items.filter((i) => i.status === "done").length;
	// Calculate progress based on displayed items, but show total count
	const progress =
		displayedCount > 0 ? (completedCount / displayedCount) * 100 : 0;

	return (
		<Card className="p-6">
			<div className="flex items-center justify-between mb-4">
				<div className="flex items-center gap-3">
					<div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
						<Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
					</div>
					<div>
						<h3 className="text-lg font-semibold text-gray-900 dark:text-white capitalize">
							{type}s
						</h3>
						<p className="text-sm text-muted-foreground">
							{completedCount} of {displayedCount} completed
						</p>
					</div>
				</div>
				<Badge variant="secondary" className="text-lg px-3 py-1">
					{displayedCount}
				</Badge>
			</div>

			<Progress value={progress} className="mb-4 h-2" />

			<div className="space-y-3">
				{items.slice(0, 5).map((item) => (
					<RichItemCard key={item.id} item={item} projectId={projectId} />
				))}
				{items.length > 5 && (
					<Link to={`/items?project=${projectId}&type=${type}`}>
						<Button variant="ghost" className="w-full mt-2">
							View all {displayedCount} {type}s
							<ArrowRight className="ml-2 h-4 w-4" />
						</Button>
					</Link>
				)}
			</div>
		</Card>
	);
}

function QuickActions({ projectId }: { projectId: string }) {
	return (
		<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
			<Link to={`/items?project=${projectId}`}>
				<Card className="p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group border-2 border-transparent hover:border-blue-500">
					<ClipboardList className="h-10 w-10 mb-3 text-blue-600 dark:text-blue-400 group-hover:scale-110 transition-transform" />
					<div className="font-semibold text-gray-900 dark:text-white mb-1">
						View Items
					</div>
					<div className="text-sm text-muted-foreground">Table view</div>
				</Card>
			</Link>
			<Link to={`/items/kanban?project=${projectId}`}>
				<Card className="p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group border-2 border-transparent hover:border-green-500">
					<BarChart className="h-10 w-10 mb-3 text-green-600 dark:text-green-400 group-hover:scale-110 transition-transform" />
					<div className="font-semibold text-gray-900 dark:text-white mb-1">
						Kanban Board
					</div>
					<div className="text-sm text-muted-foreground">Workflow view</div>
				</Card>
			</Link>
			<Link to={`/graph?project=${projectId}`}>
				<Card className="p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group border-2 border-transparent hover:border-purple-500">
					<Network className="h-10 w-10 mb-3 text-purple-600 dark:text-purple-400 group-hover:scale-110 transition-transform" />
					<div className="font-semibold text-gray-900 dark:text-white mb-1">
						Graph View
					</div>
					<div className="text-sm text-muted-foreground">Relationships</div>
				</Card>
			</Link>
			<Link to={`/matrix?project=${projectId}`}>
				<Card className="p-6 hover:shadow-lg transition-all duration-200 cursor-pointer group border-2 border-transparent hover:border-orange-500">
					<TrendingUp className="h-10 w-10 mb-3 text-orange-600 dark:text-orange-400 group-hover:scale-110 transition-transform" />
					<div className="font-semibold text-gray-900 dark:text-white mb-1">
						Matrix
					</div>
					<div className="text-sm text-muted-foreground">Coverage</div>
				</Card>
			</Link>
		</div>
	);
}

export function ProjectDetailView() {
	const params = useParams({ strict: false });
	const projectId = params.projectId as string | undefined;
	const navigate = useNavigate();

	// Call all hooks unconditionally (before any early returns)
	const {
		data: project,
		isLoading: projectLoading,
		error: projectError,
	} = useProject(projectId || "");
	const { data: itemsData, isLoading: itemsLoading } = useItems({
		projectId: projectId || "",
	});
	const { data: linksData, isLoading: linksLoading } = useLinks({
		projectId: projectId || "",
	});

	// Extract items and total from the new hook structure
	const items = itemsData?.items || [];
	const itemsTotal = itemsData?.total || 0;
	const links = linksData?.links || [];
	const linksTotal = linksData?.total || 0;
	const { setCurrentProject } = useProjectStore();
	useUpdateProject();

	// Set current project in store
	useMemo(() => {
		if (project) {
			setCurrentProject(project);
		}
	}, [project, setCurrentProject]);

	// Group items by type
	const itemsByType = useMemo(() => {
		if (!items) return {};
		return items.reduce((acc, item) => {
			if (!acc[item.type]) {
				acc[item.type] = [];
			}
			acc[item.type]?.push(item);
			return acc;
		}, {} as ItemsByType);
	}, [items]);

	// Recent items (last 10)
	const recentItems = useMemo(() => {
		if (!items) return [];
		return [...items]
			.sort(
				(a, b) =>
					new Date(b.createdAt || 0).getTime() -
					new Date(a.createdAt || 0).getTime(),
			)
			.slice(0, 10);
	}, [items]);

	// Type breakdown stats - use itemsTotal for accurate counts
	const typeStats = useMemo(() => {
		return Object.entries(itemsByType).map(([type, typeItems]) => ({
			type,
			count: typeItems.length, // Displayed count (may be paginated)
			completed: typeItems.filter((i) => i.status === "done").length,
			items: typeItems,
		}));
	}, [itemsByType]);

	// Check for missing projectId AFTER hooks are called
	if (!projectId) {
		return (
			<Alert variant="destructive" className="m-4">
				<AlertCircle className="h-4 w-4" />
				<AlertTitle>Invalid Project</AlertTitle>
				<AlertDescription>Project ID is missing from the URL.</AlertDescription>
			</Alert>
		);
	}

	if (projectLoading || itemsLoading || linksLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<div className="grid grid-cols-4 gap-4">
					{[...Array(4)].map((_, i) => (
						<Skeleton key={i} className="h-32" />
					))}
				</div>
				<Skeleton className="h-64" />
			</div>
		);
	}

	// Show error only if we're not loading and there's an error or no project
	if (!projectLoading && (projectError || !project)) {
		return (
			<div className="container mx-auto p-6">
				<Alert variant="destructive" className="m-4">
					<AlertCircle className="h-4 w-4" />
					<AlertTitle>Failed to load project</AlertTitle>
					<AlertDescription>
						{projectError?.message || "Project not found or access denied"}
						{projectId && (
							<div className="mt-2 text-xs text-muted-foreground">
								Project ID: {projectId}
							</div>
						)}
						<div className="mt-4">
							<Button
								variant="outline"
								onClick={() => navigate({ to: "/projects" })}
							>
								Back to Projects
							</Button>
						</div>
					</AlertDescription>
				</Alert>
			</div>
		);
	}

	// TypeScript guard: project is guaranteed to exist here
	if (!project) {
		return null;
	}

	return (
		<div className="space-y-8 pb-8">
			{/* Breadcrumb */}
			<nav className="flex items-center text-sm text-muted-foreground">
				<Link
					to="/projects"
					className="hover:text-foreground transition-colors"
				>
					Projects
				</Link>
				<span className="mx-2">/</span>
				<span className="text-foreground font-medium">{project.name}</span>
			</nav>

			{/* Header */}
			<div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
				<div className="flex-1">
					<div className="flex items-center gap-3 mb-3">
						<h1 className="text-4xl font-bold text-gray-900 dark:text-white">
							{project.name}
						</h1>
						{project.metadata?.domain && (
							<Badge variant="outline" className="text-sm">
								{project.metadata.domain}
							</Badge>
						)}
					</div>
					{project.description && (
						<p className="text-lg text-muted-foreground mb-4 max-w-3xl">
							{project.description}
						</p>
					)}
					<div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
						<div className="flex items-center gap-2">
							<Calendar className="h-4 w-4" />
							<span>
								Created:{" "}
								{project.createdAt
									? new Date(project.createdAt).toLocaleDateString()
									: "N/A"}
							</span>
						</div>
						{project.updatedAt && (
							<div className="flex items-center gap-2">
								<Activity className="h-4 w-4" />
								<span>
									Updated: {new Date(project.updatedAt).toLocaleDateString()}
								</span>
							</div>
						)}
					</div>
				</div>
				<div className="flex items-center gap-2">
					<Link to={`/items?project=${project.id}&action=create`}>
						<Button size="lg" className="gap-2">
							<Plus className="h-4 w-4" />
							Add Item
						</Button>
					</Link>
					<Button variant="outline" size="lg" className="gap-2">
						<Edit className="h-4 w-4" />
						Edit Project
					</Button>
				</div>
			</div>

			<Separator />

			{/* Stats */}
			<ProjectStats
				items={items || []}
				itemsTotal={itemsTotal}
				links={links || []}
				linksTotal={linksTotal}
			/>

			{/* Quick Actions */}
			<div>
				<h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
					Quick Actions
				</h2>
				<QuickActions projectId={project.id} />
			</div>

			<Separator />

			{/* Content Tabs */}
			<Card className="p-0">
				<Tabs defaultValue="overview" className="w-full">
					<div className="border-b px-6 pt-6">
						<TabsList className="grid w-full max-w-md grid-cols-3">
							<TabsTrigger value="overview">Overview</TabsTrigger>
							<TabsTrigger value="items">Items by Type</TabsTrigger>
							<TabsTrigger value="recent">Recent Activity</TabsTrigger>
						</TabsList>
					</div>

					<TabsContent value="overview" className="p-6 space-y-6">
						{typeStats.length > 0 ? (
							<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
								{typeStats.map(
									({ type, items: typeItems, count, completed }) => (
										<TypeSection
											key={type}
											type={type}
											items={typeItems}
											projectId={project.id}
											itemsTotal={itemsTotal}
										/>
									),
								)}
							</div>
						) : (
							<div className="text-center py-16">
								<ClipboardList className="h-16 w-16 mx-auto text-muted-foreground mb-4 opacity-50" />
								<h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
									No items yet
								</h3>
								<p className="text-muted-foreground mb-6">
									Get started by creating your first item for this project
								</p>
								<Link to={`/items?project=${project.id}&action=create`}>
									<Button size="lg" className="gap-2">
										<Plus className="h-4 w-4" />
										Create First Item
									</Button>
								</Link>
							</div>
						)}
					</TabsContent>

					<TabsContent value="items" className="p-6 space-y-8">
						{typeStats.length > 0 ? (
							typeStats.map(({ type, items: typeItems, count }) => (
								<div key={type}>
									<div className="flex items-center justify-between mb-4">
										<div className="flex items-center gap-3">
											{typeIcons[type] && (
												<div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/20">
													{(() => {
														const Icon = typeIcons[type];
														return (
															<Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
														);
													})()}
												</div>
											)}
											<h3 className="text-2xl font-bold text-gray-900 dark:text-white capitalize">
												{type}s
											</h3>
											<Badge
												variant="secondary"
												className="text-base px-3 py-1"
											>
												{count}
											</Badge>
										</div>
										<Link to={`/items?project=${project.id}&type=${type}`}>
											<Button variant="ghost" size="sm" className="gap-2">
												View All
												<ArrowRight className="h-4 w-4" />
											</Button>
										</Link>
									</div>
									<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
										{typeItems.slice(0, 6).map((item) => (
											<RichItemCard
												key={item.id}
												item={item}
												projectId={project.id}
											/>
										))}
									</div>
									{typeItems.length > 6 && (
										<div className="mt-4 text-center">
											<Link to={`/items?project=${project.id}&type=${type}`}>
												<Button variant="outline" className="gap-2">
													View all {typeItems.length} {type}s
													<ArrowRight className="h-4 w-4" />
												</Button>
											</Link>
										</div>
									)}
								</div>
							))
						) : (
							<div className="text-center py-16">
								<ClipboardList className="h-16 w-16 mx-auto text-muted-foreground mb-4 opacity-50" />
								<h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
									No items yet
								</h3>
								<p className="text-muted-foreground mb-6">
									Get started by creating your first item
								</p>
								<Link to={`/items?project=${project.id}&action=create`}>
									<Button size="lg" className="gap-2">
										<Plus className="h-4 w-4" />
										Create First Item
									</Button>
								</Link>
							</div>
						)}
					</TabsContent>

					<TabsContent value="recent" className="p-6">
						{recentItems.length > 0 ? (
							<div className="space-y-4">
								<h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
									Recent Activity
								</h3>
								<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
									{recentItems.map((item) => (
										<RichItemCard
											key={item.id}
											item={item}
											projectId={project.id}
										/>
									))}
								</div>
							</div>
						) : (
							<div className="text-center py-16">
								<Activity className="h-16 w-16 mx-auto text-muted-foreground mb-4 opacity-50" />
								<h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
									No recent activity
								</h3>
								<p className="text-muted-foreground">
									Items will appear here as they are created
								</p>
							</div>
						)}
					</TabsContent>
				</Tabs>
			</Card>
		</div>
	);
}
