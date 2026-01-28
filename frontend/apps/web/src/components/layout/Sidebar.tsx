import { Link, useLocation, useParams } from "@tanstack/react-router";
import {
	AlertTriangle,
	Code,
	Database,
	FileText,
	FolderOpen,
	GitBranch,
	Globe,
	Image as ImageIcon,
	LayoutDashboard,
	Rocket,
	Settings,
	TestTube,
	Workflow,
	ChevronRight,
	History,
	Activity,
	Layers,
	BarChart3,
	Search,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useProjects } from "../../hooks/useProjects";
import { useEffect, useState, useMemo } from "react";
import { Badge, ScrollArea, Separator, Progress } from "@tracertm/ui";

const navigation = [
	{ name: "Dashboard", href: "/", icon: LayoutDashboard },
	{ name: "All Projects", href: "/projects", icon: FolderOpen },
];

const viewGroups = [
	{
		title: "Core Traceability",
		views: [
			{ name: "Features", href: "feature", icon: Layers },
			{ name: "Requirements", href: "requirements", icon: FileText },
			{ name: "Graph View", href: "graph", icon: GitBranch },
		]
	},
	{
		title: "Technical",
		views: [
			{ name: "Codebase", href: "code", icon: Code },
			{ name: "Test Suite", href: "test", icon: TestTube },
			{ name: "API Docs", href: "api", icon: Globe },
			{ name: "Database", href: "database", icon: Database },
		]
	},
	{
		title: "Operational",
		views: [
			{ name: "Problems", href: "problem", icon: AlertTriangle },
			{ name: "Processes", href: "process", icon: Workflow },
			{ name: "Deployment", href: "deployment", icon: Rocket },
		]
	}
];

export function Sidebar() {
	const location = useLocation();
	const params = useParams({ strict: false }) as { projectId?: string };
	const { data: projects } = useProjects();
	const [recentIds, setRecentIds] = useState<string[]>([]);
	
	const activeProjectId = params.projectId;
	const activeProject = useMemo(() => 
		projects?.find(p => p.id === activeProjectId),
	[projects, activeProjectId]);

	// Update recent projects list
	useEffect(() => {
		if (activeProjectId) {
			setRecentIds(prev => {
				const filtered = prev.filter(id => id !== activeProjectId);
				return [activeProjectId, ...filtered].slice(0, 5);
			});
		}
	}, [activeProjectId]);

	const recentProjects = useMemo(() => {
		return recentIds
			.map(id => projects?.find(p => p.id === id))
			.filter(Boolean) as any[];
	}, [recentIds, projects]);

	return (
		<aside
			role="navigation"
			aria-label="Main navigation"
			className="group/sidebar flex w-72 flex-col bg-card/50 backdrop-blur-xl border-r transition-all duration-300 ease-in-out"
		>
			{/* Logo Area */}
			<div className="flex h-16 items-center gap-3 px-6 border-b border-border/50 bg-background/50">
				<div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary shadow-lg shadow-primary/20">
					<GitBranch className="h-5 w-5 text-primary-foreground" />
				</div>
				<div className="flex flex-col">
					<span className="text-sm font-black tracking-tighter uppercase">TraceRTM</span>
					<span className="text-[10px] text-muted-foreground font-bold leading-none">v0.1.0-alpha</span>
				</div>
			</div>

			<ScrollArea className="flex-1">
				<div className="p-4 space-y-8">
					{/* Main Navigation */}
					<div className="space-y-1">
						<p className="px-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 mb-2">Platform</p>
						{navigation.map((item) => {
							const isActive = location.pathname === item.href;
							return (
								<Link
									key={item.name}
									to={item.href}
									className={cn(
										"group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm font-semibold transition-all duration-200",
										isActive
											? "bg-primary text-primary-foreground shadow-md shadow-primary/20"
											: "text-muted-foreground hover:bg-muted hover:text-foreground"
									)}
								>
									<div className="flex items-center gap-3">
										<item.icon className={cn("h-4 w-4 transition-transform group-hover:scale-110", isActive ? "text-primary-foreground" : "text-primary")} />
										{item.name}
									</div>
									{isActive && <div className="h-1.5 w-1.5 rounded-full bg-primary-foreground animate-pulse" />}
								</Link>
							);
						})}
					</div>

					{/* Active Project Context */}
					{activeProject ? (
						<div className="space-y-6 animate-in slide-in-from-left-4 duration-500">
							<div className="px-3 py-4 rounded-2xl bg-primary/5 border border-primary/10 space-y-3">
								<div className="flex items-center gap-2">
									<div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
									<span className="text-[10px] font-black uppercase tracking-widest text-primary/80">Active Context</span>
								</div>
								<h3 className="text-sm font-bold truncate pr-2">{activeProject.name}</h3>
								<div className="space-y-1">
									<div className="flex justify-between text-[10px] font-bold text-muted-foreground">
										<span>SYNC STATUS</span>
										<span>98%</span>
									</div>
									<Progress value={98} className="h-1 bg-primary/10" />
								</div>
							</div>

							<div className="space-y-6">
								{viewGroups.map((group) => (
									<div key={group.title} className="space-y-1">
										<p className="px-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 mb-2">{group.title}</p>
										{group.views.map((view) => {
											const viewPath = `/projects/${activeProject.id}/views/${view.href}`;
											const isActive = location.pathname.includes(`/views/${view.href}`);
											return (
												<Link
													key={view.name}
													to={viewPath as any}
													className={cn(
														"flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-all",
														isActive
															? "bg-primary/10 text-primary border-r-2 border-primary"
															: "text-muted-foreground/80 hover:bg-muted/50 hover:text-foreground"
													)}
												>
													<view.icon className="h-4 w-4 shrink-0" />
													<span className="truncate">{view.name}</span>
												</Link>
											);
										})}
									</div>
								))}
							</div>
						</div>
					) : (
						/* Recent Projects (Only shown when no active project) */
						recentProjects.length > 0 && (
							<div className="space-y-1 animate-in fade-in duration-700">
								<p className="px-3 text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 mb-2">Recently Viewed</p>
								{recentProjects.map((project) => (
									<Link
										key={project.id}
										to={`/projects/${project.id}`}
										className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-all"
									>
										<div className="h-6 w-6 rounded-lg bg-muted flex items-center justify-center shrink-0">
											<History className="h-3 w-3" />
										</div>
										<span className="truncate font-medium">{project.name}</span>
									</Link>
								))}
							</div>
						)
					)}
				</div>
			</ScrollArea>

			{/* Sidebar Footer */}
			<div className="p-4 border-t border-border/50 bg-background/30 backdrop-blur-sm">
				<div className="flex flex-col gap-1">
					<Link
						to="/settings"
						className={cn(
							"flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-all",
							location.pathname === "/settings"
								? "bg-muted text-foreground"
								: "text-muted-foreground hover:bg-muted hover:text-foreground"
						)}
					>
						<Settings className="h-4 w-4" />
						Settings
					</Link>
					<div className="px-3 py-4 mt-2 rounded-2xl bg-gradient-to-br from-primary/10 to-transparent border border-primary/5">
						<div className="flex items-center gap-2 mb-2">
							<Activity className="h-3 w-3 text-primary" />
							<span className="text-[10px] font-black tracking-tighter uppercase">System Load</span>
						</div>
						<div className="flex gap-1">
							{[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
								<div 
									key={i} 
									className={cn(
										"h-4 w-1 rounded-full animate-pulse",
										i > 6 ? "bg-primary/20" : "bg-primary"
									)} 
									style={{ animationDelay: `${i * 100}ms` }}
								/>
							))}
						</div>
					</div>
				</div>
			</div>
		</aside>
	);
}