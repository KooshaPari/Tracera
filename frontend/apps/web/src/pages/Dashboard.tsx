import { Link } from "@tanstack/react-router";
import {
	Activity,
	ArrowRight,
	FolderOpen,
	GitBranch,
	Link2,
} from "lucide-react";

const stats = [
	{ name: "Projects", value: "12", icon: FolderOpen, href: "/projects" },
	{ name: "Items", value: "1,234", icon: GitBranch },
	{ name: "Links", value: "3,456", icon: Link2 },
	{ name: "Active Agents", value: "8", icon: Activity },
];

const recentProjects = [
	{
		id: "1",
		name: "TraceRTM Frontend",
		items: 44,
		links: 5,
		updated: "2 hours ago",
	},
	{
		id: "2",
		name: "Pokemon Go Demo",
		items: 28,
		links: 12,
		updated: "1 day ago",
	},
	{
		id: "3",
		name: "E-Commerce Platform",
		items: 156,
		links: 234,
		updated: "3 days ago",
	},
];

export function Dashboard() {
	return (
		<div className="space-y-8">
			{/* Welcome */}
			<div>
				<h2 className="text-3xl font-bold">Welcome to TraceRTM</h2>
				<p className="mt-2 text-muted-foreground">
					Agent-native requirements traceability and project management
				</p>
			</div>

			{/* Stats */}
			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
				{stats.map((stat) => (
					<div
						key={stat.name}
						className="rounded-xl border bg-card p-6 shadow-sm"
					>
						<div className="flex items-center gap-4">
							<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
								<stat.icon className="h-6 w-6 text-primary" />
							</div>
							<div>
								<p className="text-sm font-medium text-muted-foreground">
									{stat.name}
								</p>
								<p className="text-2xl font-bold">{stat.value}</p>
							</div>
						</div>
					</div>
				))}
			</div>

			{/* Recent Projects */}
			<div className="rounded-xl border bg-card shadow-sm">
				<div className="flex items-center justify-between border-b p-6">
					<h3 className="text-lg font-semibold">Recent Projects</h3>
					<Link
						to="/projects"
						className="flex items-center gap-1 text-sm text-primary hover:underline"
					>
						View all
						<ArrowRight className="h-4 w-4" />
					</Link>
				</div>
				<div className="divide-y">
					{recentProjects.map((project) => (
						<Link
							key={project.id}
							to={`/projects/${project.id}`}
							className="flex items-center justify-between p-6 hover:bg-accent/50"
						>
							<div className="flex items-center gap-4">
								<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
									<FolderOpen className="h-5 w-5 text-primary" />
								</div>
								<div>
									<p className="font-medium">{project.name}</p>
									<p className="text-sm text-muted-foreground">
										{project.items} items · {project.links} links
									</p>
								</div>
							</div>
							<p className="text-sm text-muted-foreground">{project.updated}</p>
						</Link>
					))}
				</div>
			</div>

			{/* Quick Actions */}
			<div className="grid gap-4 md:grid-cols-3">
				<button className="flex items-center gap-4 rounded-xl border bg-card p-6 text-left hover:bg-accent/50">
					<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10">
						<FolderOpen className="h-6 w-6 text-green-500" />
					</div>
					<div>
						<p className="font-medium">Create Project</p>
						<p className="text-sm text-muted-foreground">Start a new project</p>
					</div>
				</button>
				<button className="flex items-center gap-4 rounded-xl border bg-card p-6 text-left hover:bg-accent/50">
					<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
						<GitBranch className="h-6 w-6 text-blue-500" />
					</div>
					<div>
						<p className="font-medium">Import Items</p>
						<p className="text-sm text-muted-foreground">Import from file</p>
					</div>
				</button>
				<button className="flex items-center gap-4 rounded-xl border bg-card p-6 text-left hover:bg-accent/50">
					<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-purple-500/10">
						<Activity className="h-6 w-6 text-purple-500" />
					</div>
					<div>
						<p className="font-medium">Agent Activity</p>
						<p className="text-sm text-muted-foreground">View agent logs</p>
					</div>
				</button>
			</div>
		</div>
	);
}
