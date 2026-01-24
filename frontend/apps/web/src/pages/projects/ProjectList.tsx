import { Link } from "@tanstack/react-router";
import { FolderOpen, MoreVertical, Plus, Search } from "lucide-react";

const projects = [
	{
		id: "1",
		name: "TraceRTM Frontend",
		description: "Desktop App + Website",
		items: 44,
		links: 5,
		status: "active",
	},
	{
		id: "2",
		name: "Pokemon Go Demo",
		description: "Sample project demonstration",
		items: 28,
		links: 12,
		status: "active",
	},
	{
		id: "3",
		name: "E-Commerce Platform",
		description: "Full-stack e-commerce",
		items: 156,
		links: 234,
		status: "active",
	},
	{
		id: "4",
		name: "Mobile Banking App",
		description: "React Native banking",
		items: 89,
		links: 145,
		status: "archived",
	},
];

export function ProjectList() {
	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-2xl font-bold">Projects</h2>
					<p className="text-muted-foreground">Manage your TraceRTM projects</p>
				</div>
				<button className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
					<Plus className="h-4 w-4" />
					New Project
				</button>
			</div>

			{/* Search & Filter */}
			<div className="flex gap-4">
				<div className="relative flex-1">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
					<input
						type="text"
						placeholder="Search projects..."
						className="h-10 w-full rounded-lg border bg-background pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
					/>
				</div>
				<select className="h-10 rounded-lg border bg-background px-4 text-sm">
					<option>All Status</option>
					<option>Active</option>
					<option>Archived</option>
				</select>
			</div>

			{/* Project Grid */}
			<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
				{projects.map((project) => (
					<Link
						key={project.id}
						to={`/projects/${project.id}`}
						className="group rounded-xl border bg-card p-6 shadow-sm transition-all hover:shadow-md"
					>
						<div className="flex items-start justify-between">
							<div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
								<FolderOpen className="h-6 w-6 text-primary" />
							</div>
							<button
								onClick={(e) => {
									e.preventDefault();
									// Handle menu
								}}
								className="rounded-lg p-1 opacity-0 hover:bg-accent group-hover:opacity-100"
							>
								<MoreVertical className="h-4 w-4 text-muted-foreground" />
							</button>
						</div>
						<div className="mt-4">
							<h3 className="font-semibold">{project.name}</h3>
							<p className="mt-1 text-sm text-muted-foreground">
								{project.description}
							</p>
						</div>
						<div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
							<span>{project.items} items</span>
							<span>·</span>
							<span>{project.links} links</span>
						</div>
						<div className="mt-4">
							<span
								className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
									project.status === "active"
										? "bg-green-500/10 text-green-500"
										: "bg-gray-500/10 text-gray-500"
								}`}
							>
								{project.status}
							</span>
						</div>
					</Link>
				))}
			</div>
		</div>
	);
}
