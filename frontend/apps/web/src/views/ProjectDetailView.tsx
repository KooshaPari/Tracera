import { Link, useNavigate, useParams } from "@tanstack/react-router";
import { Badge, Button, Card, Progress, Skeleton } from "@tracertm/ui";
import {
	Activity,
	AlertCircle,
	BarChart3,
	BookOpen,
	Bot,
	Calendar,
	ChevronDown,
	ChevronUp,
	Code,
	Database,
	Edit,
	ExternalLink,
	FileText,
	Globe,
	History,
	Layers,
	Layout,
	Network,
	Plus,
	Rocket,
	Shield,
	Target,
	TestTube,
	Zap,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import {
	Bar,
	BarChart,
	CartesianGrid,
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

function formatProjectDate(value: string | null | undefined): string {
	if (value == null || value === "") {
		return "—";
	}
	const d = new Date(value);
	return Number.isNaN(d.getTime()) ? "—" : d.toLocaleDateString();
}
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";
import { useProject } from "../hooks/useProjects";
import { useProjectStore } from "../stores";
import { AgentWorkflowView } from "./AgentWorkflowView";

/**
 * Type icon component mapping
 */
type TypeIconMap = Record<string, any>;

const typeIcons: TypeIconMap = {
	api: Network,
	component: Layout,
	database: Database,
	deployment: Rocket,
	documentation: BookOpen,
	feature: Code,
	performance: Zap,
	requirement: FileText,
	security: Shield,
	test: TestTube,
};

export function ProjectDetailView() {
	const params = useParams({ strict: false });
	const projectId = params.projectId as string | undefined;
	const navigate = useNavigate();
	const [showAgentWorkflows, setShowAgentWorkflows] = useState(false);

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

	const items = itemsData?.items || [];
	const itemsTotal = itemsData?.total || 0;
	const linksTotal = linksData?.total || 0;
	// Subscribe only to the setter so store updates (currentProject/recentProjects) don't re-render this component and cause an update loop
	const setCurrentProject = useProjectStore((s) => s.setCurrentProject);
	const lastSyncedProjectIdRef = useRef<string | null>(null);

	// Sync project to store only when project id changes to avoid infinite update loops
	useEffect(() => {
		if (!project) {
			if (lastSyncedProjectIdRef.current !== null) {
				lastSyncedProjectIdRef.current = null;
				setCurrentProject(null);
			}
			return;
		}
		if (lastSyncedProjectIdRef.current === project.id) {
			return;
		}
		lastSyncedProjectIdRef.current = project.id;
		setCurrentProject(project);
	}, [project?.id, project, setCurrentProject]);

	const stats = useMemo(() => {
		const byStatus = items.reduce(
			(acc, item) => {
				acc[item.status] = (acc[item.status] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>,
		);

		const byType = items.reduce(
			(acc, item) => {
				acc[item.type] = (acc[item.type] || 0) + 1;
				return acc;
			},
			{} as Record<string, number>,
		);

		const typeData = Object.entries(byType).map(([name, value]) => ({
			name,
			value,
		}));

		const radarData = [
			{ A: byType["requirement"] || 0, fullMark: 20, subject: "Reqs" },
			{ A: byType["feature"] || 0, fullMark: 20, subject: "Features" },
			{ A: byType["test"] || 0, fullMark: 20, subject: "Tests" },
			{ A: byType["documentation"] || 0, fullMark: 20, subject: "Docs" },
			{ A: byType["bug"] || 0, fullMark: 20, subject: "Bugs" },
		];

		const completionRate =
			itemsTotal > 0
				? Math.round(((byStatus["done"] || 0) / itemsTotal) * 100)
				: 0;

		return { byStatus, byType, completionRate, radarData, typeData };
	}, [items, itemsTotal]);

	if (projectLoading || itemsLoading || linksLoading) {
		return (
			<div className="p-6 space-y-8 animate-pulse">
				<Skeleton className="h-10 w-48" />
				<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
					{[1, 2, 3, 4].map((i) => (
						<Skeleton key={i} className="h-32" />
					))}
				</div>
				<Skeleton className="h-[400px] w-full" />
			</div>
		);
	}

	if (projectError || !project) {
		return (
			<div className="p-12 flex flex-col items-center justify-center space-y-4">
				<AlertCircle className="h-12 w-12 text-destructive" />
				<h2 className="text-xl font-bold">Project Not Found</h2>
				<Button onClick={() => navigate({ to: "/projects" })}>
					Return to Projects
				</Button>
			</div>
		);
	}

	return (
		<div className="p-6 space-y-8 max-w-[1600px] mx-auto animate-in fade-in duration-500">
			{/* Professional Header */}
			<div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
				<div className="space-y-4 max-w-4xl">
					<div className="flex items-center gap-3">
						<div className="h-12 w-12 rounded-2xl bg-primary flex items-center justify-center shadow-lg shadow-primary/20">
							<Rocket className="h-6 w-6 text-primary-foreground" />
						</div>
						<div>
							<h1 className="text-3xl font-black tracking-tight">
								{getProjectDisplayName(project) || "Unnamed Project"}
							</h1>
							<div className="flex items-center gap-2 mt-1">
								<Badge
									variant="outline"
									className="font-bold uppercase tracking-tighter text-[10px]"
								>
									{projectId?.slice(0, 8) ?? "—"}
								</Badge>
								<span className="text-xs text-muted-foreground flex items-center gap-1">
									<Calendar className="h-3 w-3" />
									{formatProjectDate(project.createdAt)}
								</span>
							</div>
						</div>
					</div>
					{(project.description ?? "").trim() ? (
						<p className="text-muted-foreground leading-relaxed">
							{project.description}
						</p>
					) : null}
				</div>
				<div className="flex gap-2 shrink-0">
					<Button
						variant="outline"
						size="sm"
						className="gap-2 rounded-full px-4"
						onClick={() => toast.info("Exporting data...")}
					>
						<ExternalLink className="h-4 w-4" />
						Export
					</Button>
					<Button
						size="sm"
						className="gap-2 rounded-full px-4"
						onClick={() =>
							navigate({
								params: { projectId: project.id, viewType: "feature" },
								search: { action: "create" } as any,
								to: "/projects/$projectId/views/$viewType",
							})
						}
						aria-label="New Feature"
					>
						<Plus className="h-4 w-4" />
						New Feature
					</Button>
				</div>
			</div>

			{/* Executive Summary Cards */}
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				{[
					{
						color: "text-blue-500",
						icon: Target,
						label: "Completion",
						progress: stats.completionRate,
						value: `${stats.completionRate}%`,
					},
					{
						color: "text-purple-500",
						icon: Network,
						label: "Active Links",
						sub: "Traceability links",
						value:
							typeof linksTotal === "number"
								? linksTotal.toLocaleString()
								: String(linksTotal),
					},
					{
						color: "text-green-500",
						icon: Layers,
						label: "Total Items",
						sub: "Across all types",
						value:
							typeof itemsTotal === "number"
								? itemsTotal.toLocaleString()
								: String(itemsTotal),
					},
					{
						color: stats.byStatus["blocked"]
							? "text-red-500"
							: "text-emerald-500",
						icon: AlertCircle,
						label: "Risk Level",
						sub: `${stats.byStatus["blocked"] || 0} Blockers`,
						value: stats.byStatus["blocked"] ? "High" : "Low",
					},
				].map((card, i) => (
					<Card
						key={i}
						className="p-5 border-none bg-card/50 shadow-sm flex flex-col justify-between h-32 hover:bg-card transition-colors"
					>
						<div className="flex justify-between items-start">
							<div>
								<p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
									{card.label}
								</p>
								<h3 className="text-2xl font-black mt-1">{card.value}</h3>
							</div>
							<card.icon className={cn("h-5 w-5 opacity-40", card.color)} />
						</div>
						{card.progress !== undefined ? (
							<Progress value={card.progress} className="h-1" />
						) : (
							<p className="text-[10px] font-bold text-muted-foreground">
								{card.sub}
							</p>
						)}
					</Card>
				))}
			</div>

			{/* Visual Intelligence Section */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<Card className="p-6 col-span-1 lg:col-span-2 border-none bg-card/50">
					<div className="flex items-center justify-between mb-8">
						<div className="flex items-center gap-2">
							<Activity className="h-4 w-4 text-primary" />
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Item Distribution
							</h3>
						</div>
						<div className="flex gap-1">
							<Badge
								variant="secondary"
								className="text-[9px] uppercase font-bold"
							>
								Real-time
							</Badge>
						</div>
					</div>
					<div className="h-[280px]">
						<ResponsiveContainer width="100%" height="100%">
							<BarChart data={stats.typeData}>
								<CartesianGrid
									strokeDasharray="3 3"
									vertical={false}
									stroke="hsl(var(--muted)/0.3)"
								/>
								<XAxis
									dataKey="name"
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
									dataKey="value"
									fill="hsl(var(--primary))"
									radius={[4, 4, 0, 0]}
								/>
							</BarChart>
						</ResponsiveContainer>
					</div>
				</Card>

				<Card className="p-6 border-none bg-card/50 flex flex-col">
					<div className="flex items-center gap-2 mb-8">
						<Shield className="h-4 w-4 text-primary" />
						<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
							Project Health
						</h3>
					</div>
					<div className="flex-1">
						<ResponsiveContainer width="100%" height="100%">
							<RadarChart
								cx="50%"
								cy="50%"
								outerRadius="80%"
								data={stats.radarData}
							>
								<PolarGrid stroke="hsl(var(--muted))" />
								<PolarAngleAxis
									dataKey="subject"
									fontSize={10}
									tick={{ fill: "hsl(var(--muted-foreground))" }}
								/>
								<Radar
									name="Coverage"
									dataKey="A"
									stroke="hsl(var(--primary))"
									fill="hsl(var(--primary))"
									fillOpacity={0.5}
								/>
							</RadarChart>
						</ResponsiveContainer>
					</div>
					<div className="mt-4 flex justify-center gap-4">
						<div className="flex items-center gap-1.5">
							<div className="h-2 w-2 rounded-full bg-primary" />
							<span className="text-[10px] font-bold uppercase text-muted-foreground">
								Coverage
							</span>
						</div>
					</div>
				</Card>
			</div>

			{/* Agent Workflows - Inline Section */}
			<div className="space-y-4">
				<div className="flex items-center justify-between">
					<div className="flex items-center gap-2">
						<Bot className="h-4 w-4 text-primary" />
						<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
							AI Agent Workflows
						</h3>
					</div>
					<Button
						variant="ghost"
						size="sm"
						onClick={() => setShowAgentWorkflows(!showAgentWorkflows)}
						className="text-[10px] font-black uppercase tracking-widest gap-2"
					>
						{showAgentWorkflows ? (
							<>
								<ChevronUp className="h-3 w-3" />
								Hide
							</>
						) : (
							<>
								<ChevronDown className="h-3 w-3" />
								Show
							</>
						)}
					</Button>
				</div>
				{showAgentWorkflows && (
					<div className="animate-in fade-in slide-in-from-top-2 duration-200">
						<AgentWorkflowView />
					</div>
				)}
			</div>

			{/* Views Navigation */}
			<div className="space-y-4">
				<div className="flex items-center gap-2">
					<Layout className="h-4 w-4 text-primary" />
					<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
						Available Views
					</h3>
				</div>
				<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
					{[
						{
							color: "text-blue-500",
							href: "feature",
							icon: Layers,
							label: "Features",
						},
						{
							color: "text-purple-500",
							href: "graph",
							icon: Network,
							label: "Traceability",
						},
						{
							color: "text-green-500",
							href: "test",
							icon: TestTube,
							label: "Test Suite",
						},
						{
							color: "text-orange-500",
							href: "api",
							icon: Globe,
							label: "API Docs",
						},
						{
							color: "text-cyan-500",
							href: "database",
							icon: Database,
							label: "Database",
						},
						{
							color: "text-pink-500",
							href: "matrix",
							icon: BarChart3,
							label: "Matrix",
						},
						{
							color: "text-amber-500",
							href: "workflows",
							icon: Activity,
							label: "Workflows",
						},
					].map((v, i) => (
						<Link
							key={i}
							to={`/projects/${project.id}/views/${v.href}` as any}
							className="cursor-pointer"
						>
							<Card className="p-4 flex flex-col items-center justify-center gap-3 hover:bg-muted/50 hover:shadow-md transition-all border-none shadow-sm group">
								<v.icon
									className={cn(
										"h-6 w-6 transition-transform group-hover:scale-110",
										v.color,
									)}
								/>
								<span className="text-[10px] font-bold uppercase tracking-tighter">
									{v.label}
								</span>
							</Card>
						</Link>
					))}
				</div>
			</div>

			{/* Activity & Recent Section */}
			<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
				<Card className="p-6 col-span-1 lg:col-span-2 border-none bg-card/50">
					<div className="flex items-center justify-between mb-6">
						<div className="flex items-center gap-2">
							<History className="h-4 w-4 text-primary" />
							<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
								Recent Item Activity
							</h3>
						</div>
						<Button
							variant="ghost"
							size="sm"
							className="text-[10px] font-black uppercase tracking-widest"
							onClick={() =>
								navigate({
									params: { projectId: project.id, viewType: "feature" },
									to: "/projects/$projectId/views/$viewType",
								})
							}
						>
							View All
						</Button>
					</div>
					<div className="space-y-3">
						{items.slice(0, 5).map((item) => (
							<Link
								key={item.id}
								to={`/projects/${project.id}/views/${String(item.view || "feature").toLowerCase()}/${item.id}`}
								className="cursor-pointer"
							>
								<div className="flex items-center gap-4 p-3 rounded-xl hover:bg-muted/50 transition-colors group border border-transparent hover:border-border/50">
									<div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
										{(() => {
											const Icon = typeIcons[item.type] || FileText;
											return <Icon className="h-4 w-4 text-primary" />;
										})()}
									</div>
									<div className="flex-1 min-w-0">
										<h4 className="text-sm font-bold truncate group-hover:text-primary transition-colors">
											{item.title}
										</h4>
										<div className="flex items-center gap-2 mt-0.5">
											<Badge className="text-[8px] h-3.5 px-1 uppercase font-black tracking-tighter">
												{item.type}
											</Badge>
											<span className="text-[10px] text-muted-foreground font-medium uppercase tracking-widest">
												{item.status}
											</span>
										</div>
									</div>
									<div className="text-right shrink-0">
										<div className="text-[10px] text-muted-foreground font-bold">
											{formatProjectDate(item.createdAt)}
										</div>
									</div>
								</div>
							</Link>
						))}
					</div>
				</Card>

				<Card className="p-6 border-none bg-card/50">
					<div className="flex items-center gap-2 mb-6">
						<Activity className="h-4 w-4 text-primary" />
						<h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
							Quick Config
						</h3>
					</div>
					<div className="space-y-4">
						<div className="p-4 rounded-2xl bg-primary/5 border border-primary/10">
							<h4 className="text-xs font-bold mb-2 uppercase tracking-widest">
								Metadata
							</h4>
							<div className="space-y-2">
								{project.metadata && typeof project.metadata === "object" ? (
									Object.entries(project.metadata)
										.slice(0, 3)
										.map(([k, v]) => (
											<div
												key={k}
												className="flex justify-between items-center"
											>
												<span className="text-[10px] text-muted-foreground font-medium uppercase">
													{k}
												</span>
												<span className="text-[10px] font-bold">
													{String(v)}
												</span>
											</div>
										))
								) : (
									<p className="text-[10px] text-muted-foreground">
										No metadata available
									</p>
								)}
							</div>
						</div>
						<Button
							variant="outline"
							className="w-full text-[10px] font-black uppercase tracking-widest gap-2"
							size="sm"
							onClick={() =>
								navigate({ to: `/projects/${project.id}/settings` })
							}
						>
							<Edit className="h-3 w-3" />
							Project Settings
						</Button>
					</div>
				</Card>
			</div>
		</div>
	);
}
