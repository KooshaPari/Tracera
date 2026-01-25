import { Link } from "@tanstack/react-router";
import type { Project } from "@tracertm/types";
import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import {
	BarChart,
	ClipboardList,
	Edit,
	Folder,
	Link as LinkIcon,
	Network,
	Plus,
	Target,
	TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useProjects } from "../hooks/useProjects";

interface StatCardProps {
	title: string;
	value: number;
	description: string;
	trend?: { value: number; direction: "up" | "down" };
	icon: React.ComponentType<{ className?: string }>;
	color: string;
}

function StatCard({
	title,
	value,
	description,
	trend,
	icon: Icon,
	color,
}: StatCardProps) {
	return (
		<Card className="p-6 hover:shadow-md transition-shadow duration-200">
			<div className="flex items-start justify-between">
				<div className="flex-1">
					<p className="text-sm font-medium text-muted-foreground">{title}</p>
					<p className="mt-2 text-3xl font-bold tracking-tight">{value}</p>
					<p className="mt-1 text-sm text-muted-foreground">{description}</p>
					{trend && (
						<div
							className={`mt-3 flex items-center gap-1 text-sm font-medium ${
								trend.direction === "up"
									? "text-green-600 dark:text-green-400"
									: "text-red-600 dark:text-red-400"
							}`}
						>
							{trend.direction === "up" ? (
								<TrendingUp className="h-4 w-4" />
							) : (
								<TrendingUp className="h-4 w-4 rotate-180" />
							)}
							<span>{Math.abs(trend.value)}%</span>
							<span className="ml-1 text-xs text-muted-foreground font-normal">
								from last week
							</span>
						</div>
					)}
				</div>
				<div
					className={`rounded-lg p-3 ${color} transition-transform hover:scale-110`}
				>
					<Icon className="h-6 w-6" />
				</div>
			</div>
		</Card>
	);
}

interface RecentActivityItem {
	id: string;
	type: "item_created" | "item_updated" | "link_created" | "project_created";
	title: string;
	subtitle: string;
	timestamp: Date | string | null;
	user: string;
}

function RecentActivity({ activities }: { activities: RecentActivityItem[] }) {
	if (activities.length === 0) {
		return (
			<div className="text-center py-12 text-muted-foreground">
				<p>No recent activity</p>
			</div>
		);
	}

	const getActivityIcon = (type: RecentActivityItem["type"]) => {
		switch (type) {
			case "item_created":
				return <Plus className="h-4 w-4" />;
			case "item_updated":
				return <Edit className="h-4 w-4" />;
			case "link_created":
				return <LinkIcon className="h-4 w-4" />;
			case "project_created":
				return <Folder className="h-4 w-4" />;
			default:
				return <div className="h-1 w-1 rounded-full bg-current" />;
		}
	};

	return (
		<div className="space-y-4">
			{activities.map((activity) => (
				<div
					key={activity.id}
					className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
				>
					<div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
						{getActivityIcon(activity.type)}
					</div>
					<div className="flex-1 min-w-0">
						<p className="text-sm font-medium truncate">{activity.title}</p>
						<p className="text-sm text-muted-foreground">
							{activity.subtitle} by {activity.user}
						</p>
					</div>
					<div className="flex-shrink-0 text-sm text-muted-foreground">
						{formatTimeAgo(activity.timestamp)}
					</div>
				</div>
			))}
		</div>
	);
}

function formatTimeAgo(date: Date | string | null | undefined): string {
	if (!date) return "recently";

	let dateObj: Date;
	if (date instanceof Date) {
		dateObj = date;
	} else if (typeof date === "string") {
		dateObj = new Date(date);
	} else {
		return "recently";
	}

	// Check if date is valid
	if (Number.isNaN(dateObj.getTime())) {
		return "recently";
	}

	const seconds = Math.floor((Date.now() - dateObj.getTime()) / 1000);

	if (seconds < 60) return "just now";
	if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
	if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
	if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
	return dateObj.toLocaleDateString();
}

interface QuickAction {
	id: string;
	label: string;
	description: string;
	icon: React.ComponentType<{ className?: string }>;
	href: string;
	color: string;
}

function QuickActions() {
	const actions: QuickAction[] = [
		{
			id: "new-item",
			label: "Create Item",
			description: "Add a new requirement, feature, or test",
			icon: Plus,
			href: "/items?action=create",
			color: "bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400",
		},
		{
			id: "new-project",
			label: "New Project",
			description: "Start a new project",
			icon: Folder,
			href: "/projects?action=create",
			color:
				"bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400",
		},
		{
			id: "view-graph",
			label: "View Graph",
			description: "Visualize relationships",
			icon: Network,
			href: "/graph",
			color:
				"bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400",
		},
		{
			id: "run-analysis",
			label: "Impact Analysis",
			description: "Analyze change impact",
			icon: Target,
			href: "/impact",
			color:
				"bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400",
		},
	];

	return (
		<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
			{actions.map((action) => {
				const IconComponent = action.icon;
				return (
					<Link key={action.id} to={action.href}>
						<Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer h-full">
							<div
								className={`w-12 h-12 rounded-lg ${action.color} flex items-center justify-center mb-4`}
							>
								<IconComponent className="h-6 w-6" />
							</div>
							<h3 className="font-semibold mb-1">{action.label}</h3>
							<p className="text-sm text-muted-foreground">
								{action.description}
							</p>
						</Card>
					</Link>
				);
			})}
		</div>
	);
}

export function DashboardView() {
	const { data: projects, isLoading: projectsLoading } = useProjects();
	const [allItems, setAllItems] = useState<any[]>([]);
	const [itemsLoading, setItemsLoading] = useState(false);
	const [projectItemCounts, setProjectItemCounts] = useState<
		Record<string, number>
	>({});
	const [recentActivity, setRecentActivity] = useState<RecentActivityItem[]>(
		[],
	);

	// Ensure projects is always an array
	const projectsArray = Array.isArray(projects) ? projects : [];

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
						`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/items?project_id=${project.id}&limit=1`,
						{
							headers: {
								"X-Bulk-Operation": "true", // Skip rate limiting for bulk fetches
							},
						},
					);
					if (!res.ok) {
						return { projectId: project.id, count: 0, items: [] };
					}
					const data = await res.json();
					// API returns { total: number, items: Item[] }
					const total = data.total || 0;
					const items = Array.isArray(data) ? data : data.items || [];
					// Ensure each item has project_id set
					return {
						projectId: project.id,
						count: total,
						items: items.map((item: any) => ({
							...item,
							projectId: item.projectId || project.id,
						})),
					};
				} catch {
					return { projectId: project.id, count: 0, items: [] };
				}
			}),
		)
			.then((results) => {
				// Build project counts from results
				const projectCounts: Record<string, number> = {};
				results.forEach((r: any) => {
					if (r.projectId) {
						projectCounts[r.projectId] = r.count || 0;
					}
				});

				// results is now array of { projectId, count, items }
				const allItemsFlat = results.flatMap((r: any) => r.items || []);
				setAllItems(allItemsFlat);
				// Store project counts in both window and state for reactivity
				(window as any).__projectItemCounts = projectCounts;
				setProjectItemCounts(projectCounts);
				setItemsLoading(false);

				// Debug logging (remove in production)
				console.log("Project item counts:", projectCounts);
			})
			.catch(() => {
				setAllItems([]);
				setProjectItemCounts({});
				setItemsLoading(false);
			});
	}, [projectsArray]);

	// Calculate stats - use project counts from API totals instead of fetched items
	// Use state first, then fallback to window global
	const countsForStats =
		projectItemCounts && Object.keys(projectItemCounts).length > 0
			? projectItemCounts
			: (window as any).__projectItemCounts || {};
	const totalItemsFromAPI = Object.values(countsForStats).reduce(
		(sum: number, count: any) => sum + (Number(count) || 0),
		0,
	);

	const stats = {
		totalProjects: projectsArray.length,
		totalItems: totalItemsFromAPI || allItems.length,
		activeItems: allItems.filter(
			(item) => item.status !== "done" && item.status !== "completed",
		).length,
		completionRate: allItems.length
			? Math.round(
					(allItems.filter(
						(item) => item.status === "done" || item.status === "completed",
					).length /
						allItems.length) *
						100,
				)
			: 0,
		avgItemsPerProject:
			projectsArray.length > 0 && totalItemsFromAPI > 0
				? Math.round(totalItemsFromAPI / projectsArray.length)
				: 0,
	};

	// Mock recent activity (in production, this would come from an API)
	useEffect(() => {
		if (allItems && allItems.length > 0) {
			const activities: RecentActivityItem[] = allItems
				.slice(0, 5)
				.map((item) => {
					// Handle different date field names and formats
					const dateValue =
						item.createdAt ||
						(item as any).created_at ||
						new Date().toISOString();

					let timestamp: Date;
					try {
						timestamp =
							dateValue instanceof Date ? dateValue : new Date(dateValue);
						// Validate date
						if (Number.isNaN(timestamp.getTime())) {
							timestamp = new Date();
						}
					} catch {
						timestamp = new Date();
					}

					return {
						id: item.id,
						type: "item_created" as const,
						title: item.title,
						subtitle: item.type || item.view || "item",
						timestamp,
						user: (item as any).owner || (item as any).user || "Unknown",
					};
				});
			setRecentActivity(activities);
		}
	}, [allItems]);

	if (projectsLoading || itemsLoading) {
		return (
			<div className="space-y-6">
				<div>
					<Skeleton className="h-8 w-48 mb-2" />
					<Skeleton className="h-4 w-96" />
				</div>
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
					{[...Array(4)].map((_, i) => (
						<Skeleton key={i} className="h-32" />
					))}
				</div>
			</div>
		);
	}

	return (
		<div className="space-y-8 p-6">
			{/* Header */}
			<div>
				<h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
				<p className="mt-2 text-muted-foreground">
					Welcome back! Here's an overview of your projects and items.
				</p>
			</div>

			{/* Stats Grid */}
			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
				<StatCard
					title="Total Projects"
					value={stats.totalProjects}
					description="Active projects"
					icon={Folder}
					color="bg-blue-100 dark:bg-blue-900"
					trend={{ value: 12, direction: "up" }}
				/>
				<StatCard
					title="Total Items"
					value={stats.totalItems}
					description={`Avg ${stats.avgItemsPerProject} items/project`}
					icon={ClipboardList}
					color="bg-green-100 dark:bg-green-900"
					trend={{ value: 8, direction: "up" }}
				/>
				<StatCard
					title="Active Items"
					value={stats.activeItems}
					description="In progress or pending"
					icon={Target}
					color="bg-yellow-100 dark:bg-yellow-900"
				/>
				<StatCard
					title="Completion"
					value={stats.completionRate}
					description="Overall completion rate"
					icon={BarChart}
					color="bg-purple-100 dark:bg-purple-900"
					trend={{ value: 5, direction: "up" }}
				/>
			</div>

			{/* Quick Actions */}
			<div>
				<h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
				<QuickActions />
			</div>

			{/* Recent Projects & Activity */}
			<div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
				{/* Recent Projects */}
				<Card className="p-6">
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-xl font-semibold">Recent Projects</h2>
						<Link to="/projects">
							<Button variant="ghost" size="sm">
								View All
							</Button>
						</Link>
					</div>
					{projectsArray && projectsArray.length > 0 ? (
						<div className="space-y-3">
							{projectsArray.slice(0, 5).map((project: Project) => (
								<Link key={project.id} to={`/projects/${project.id}`}>
									<div className="p-3 rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
										<div className="flex items-center justify-between">
											<div className="flex-1">
												<h3 className="font-medium">{project.name}</h3>
												{project.description && (
													<p className="text-sm text-muted-foreground mt-1">
														{project.description}
													</p>
												)}
											</div>
											<Badge variant="secondary">
												{(() => {
													const count =
														projectItemCounts[project.id] ??
														(window as any).__projectItemCounts?.[project.id] ??
														allItems.filter(
															(item) => item.projectId === project.id,
														).length ??
														0;
													return count;
												})()} items
											</Badge>
										</div>
									</div>
								</Link>
							))}
						</div>
					) : (
						<div className="text-center py-8 text-muted-foreground">
							<p>No projects yet</p>
							<Link to="/projects?action=create">
								<Button variant="outline" size="sm" className="mt-4">
									Create your first project
								</Button>
							</Link>
						</div>
					)}
				</Card>

				{/* Recent Activity */}
				<Card className="p-6">
					<div className="flex items-center justify-between mb-4">
						<h2 className="text-xl font-semibold">Recent Activity</h2>
						<Link to="/events">
							<Button variant="ghost" size="sm">
								View All
							</Button>
						</Link>
					</div>
					<RecentActivity activities={recentActivity} />
				</Card>
			</div>

			{/* Coverage Overview */}
			<Card className="p-6">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-xl font-semibold">Coverage Overview</h2>
					<Link to="/matrix">
						<Button variant="ghost" size="sm">
							View Matrix
						</Button>
					</Link>
				</div>
				<div className="grid grid-cols-2 md:grid-cols-4 gap-4">
					<div className="text-center">
						<div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
							{allItems.filter((item) => item.type === "requirement").length ||
								0}
						</div>
						<div className="text-sm text-muted-foreground mt-1">
							Requirements
						</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-green-600 dark:text-green-400">
							{allItems.filter((item) => item.type === "feature").length || 0}
						</div>
						<div className="text-sm text-muted-foreground mt-1">Features</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
							{allItems.filter((item) => item.type === "test").length || 0}
						</div>
						<div className="text-sm text-muted-foreground mt-1">Tests</div>
					</div>
					<div className="text-center">
						<div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
							{Math.round(
								((allItems.filter((item) => item.type === "test").length || 0) /
									Math.max(
										allItems.filter((item) => item.type === "requirement")
											.length || 1,
										1,
									)) *
									100,
							)}
							%
						</div>
						<div className="text-sm text-muted-foreground mt-1">
							Test Coverage
						</div>
					</div>
				</div>
			</Card>
		</div>
	);
}
