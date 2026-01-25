import { Link, useNavigate, useSearch } from "@tanstack/react-router";
import type { Project } from "@tracertm/types";
import {
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
} from "@tracertm/ui";
import { Alert } from "@tracertm/ui/components/Alert";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";
import { Dialog } from "@tracertm/ui/components/Dialog";
import { Input } from "@tracertm/ui/components/Input";
import { Label } from "@tracertm/ui/components/Label";
import { Separator } from "@tracertm/ui/components/Separator";
import { Skeleton } from "@tracertm/ui/components/Skeleton";
import { Textarea } from "@tracertm/ui/components/Textarea";
import { ClipboardList, Folder } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useCreateProject, useProjects } from "../hooks/useProjects";

interface ProjectCardProps {
	project: Project;
	itemCount: number;
}

function ProjectCard({ project, itemCount }: ProjectCardProps) {
	return (
		<Card className="p-6 hover:shadow-lg transition-all duration-200 hover:border-primary/50">
			<div className="flex items-start justify-between mb-4">
				<Link to={`/projects/${project.id}`} className="flex-1 group">
					<h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
						{project.name}
					</h3>
				</Link>
			</div>

			{project.description && (
				<p className="text-sm text-muted-foreground mb-4 line-clamp-2">
					{project.description}
				</p>
			)}

			<Separator className="my-4" />

			<div className="flex items-center justify-between">
				<div className="flex items-center gap-4 text-sm text-muted-foreground">
					<div className="flex items-center gap-1.5">
						<ClipboardList className="h-4 w-4" />
						<span>{itemCount} items</span>
					</div>
					<div className="flex items-center gap-1.5">
						<span className="text-lg">📅</span>
						<span>
							{project.createdAt
								? new Date(project.createdAt).toLocaleDateString()
								: "N/A"}
						</span>
					</div>
				</div>
				<Link to={`/projects/${project.id}`}>
					<Button variant="outline" size="sm">
						View
					</Button>
				</Link>
			</div>
		</Card>
	);
}

function CreateProjectDialog({
	open,
	onOpenChange,
}: {
	open: boolean;
	onOpenChange: (open: boolean) => void;
}) {
	const [name, setName] = useState("");
	const [description, setDescription] = useState("");
	const [error, setError] = useState<string | null>(null);
	const createProject = useCreateProject();
	const navigate = useNavigate();

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setError(null);

		if (!name.trim()) {
			setError("Project name is required");
			return;
		}

		try {
			const project = await createProject.mutateAsync({
				name: name.trim(),
				description: description.trim() || undefined,
			});
			setName("");
			setDescription("");
			onOpenChange(false);
			navigate({ to: `/projects/${project.id}` });
		} catch (err) {
			setError(err instanceof Error ? err.message : "Failed to create project");
		}
	};

	return (
		<Dialog open={open} onOpenChange={onOpenChange}>
			<div className="p-6">
				<h2 className="text-xl font-semibold mb-6">Create New Project</h2>
				<form onSubmit={handleSubmit} className="space-y-6">
					{error && <Alert variant="destructive">{error}</Alert>}

					<div className="space-y-2">
						<Label htmlFor="project-name">
							Project Name <span className="text-destructive">*</span>
						</Label>
						<Input
							id="project-name"
							value={name}
							onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
								setName((e.currentTarget as HTMLInputElement).value)
							}
							placeholder="Enter project name"
							autoFocus
						/>
					</div>

					<div className="space-y-2">
						<Label htmlFor="project-description">Description</Label>
						<Textarea
							id="project-description"
							value={description}
							onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
								setDescription((e.currentTarget as HTMLTextAreaElement).value)
							}
							placeholder="Enter project description (optional)"
							rows={4}
						/>
					</div>

					<Separator />

					<div className="flex justify-end gap-3">
						<Button
							type="button"
							variant="outline"
							onClick={() => onOpenChange(false)}
						>
							Cancel
						</Button>
						<Button type="submit" disabled={createProject.isPending}>
							{createProject.isPending ? "Creating..." : "Create Project"}
						</Button>
					</div>
				</form>
			</div>
		</Dialog>
	);
}

export function ProjectsListView() {
	const navigate = useNavigate();
	const searchParams = useSearch({ strict: false }) as any;
	const {
		data: projects,
		isLoading: projectsLoading,
		error: projectsError,
	} = useProjects();
	const [projectItemCounts, setProjectItemCounts] = useState<
		Record<string, number>
	>({});

	const [searchQuery, setSearchQuery] = useState("");
	const [sortBy, setSortBy] = useState<"name" | "date" | "items">("date");
	const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

	const showCreateDialog = searchParams?.action === "create";

	const handleOpenChange = (open: boolean) => {
		if (!open) {
			navigate({
				search: (prev: any) => {
					const newSearch = { ...(prev || {}), action: undefined };
					return newSearch as any;
				},
			} as any);
		}
	};

	// Ensure projects is always an array
	const projectsArray = Array.isArray(projects) ? projects : [];

	// Fetch item counts for each project (with throttling to avoid rate limits)
	useEffect(() => {
		if (projectsArray.length === 0) return;

		const fetchCounts = async () => {
			const counts: Record<string, number> = {};
			const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

			// Fetch counts sequentially with small delays to avoid rate limiting
			for (const project of projectsArray) {
				try {
					// Small delay between requests to avoid rate limiting
					await new Promise((resolve) => setTimeout(resolve, 100));

					const res = await fetch(
						`${apiUrl}/api/v1/items?project_id=${project.id}&limit=1`,
						{
							headers: {
								"X-Bulk-Operation": "true", // Request to skip rate limiting
							},
						},
					);

					if (res.ok) {
						const data = await res.json();
						// Handle both { total, items } and direct array responses
						if (data.total !== undefined) {
							counts[project.id] = data.total;
						} else if (Array.isArray(data)) {
							counts[project.id] = data.length;
						} else if (data.items && Array.isArray(data.items)) {
							counts[project.id] = data.items.length;
						} else {
							counts[project.id] = 0;
						}
					} else {
						// If rate limited, wait and retry once
						if (res.status === 429) {
							await new Promise((resolve) => setTimeout(resolve, 1000));
							const retryRes = await fetch(
								`${apiUrl}/api/v1/items?project_id=${project.id}&limit=1`,
								{
									headers: {
										"X-Bulk-Operation": "true",
									},
								},
							);
							if (retryRes.ok) {
								const retryData = await retryRes.json();
								counts[project.id] = retryData.total || 0;
							} else {
								counts[project.id] = 0;
							}
						} else {
							counts[project.id] = 0;
						}
					}
				} catch (error) {
					console.error(
						`Error fetching items for project ${project.id}:`,
						error,
					);
					counts[project.id] = 0;
				}
			}

			setProjectItemCounts(counts);
		};

		fetchCounts();
	}, [projectsArray]);

	// Filter and sort projects
	const filteredAndSortedProjects = useMemo(() => {
		if (!projectsArray || projectsArray.length === 0) return [];

		const filtered = projectsArray.filter((project) => {
			if (!searchQuery) return true;
			const query = searchQuery.toLowerCase();
			return (
				project.name.toLowerCase().includes(query) ||
				project.description?.toLowerCase().includes(query)
			);
		});

		// Map projects with item counts
		const projectsWithCounts = filtered.map((project) => ({
			project,
			itemCount: projectItemCounts[project.id] || 0,
		}));

		// Sort
		projectsWithCounts.sort((a, b) => {
			let comparison = 0;

			switch (sortBy) {
				case "name":
					comparison = a.project.name.localeCompare(b.project.name);
					break;
				case "date": {
					const dateA = a.project.createdAt
						? new Date(a.project.createdAt).getTime()
						: 0;
					const dateB = b.project.createdAt
						? new Date(b.project.createdAt).getTime()
						: 0;
					comparison = dateA - dateB;
					break;
				}
				case "items":
					comparison = a.itemCount - b.itemCount;
					break;
			}

			return sortOrder === "asc" ? comparison : -comparison;
		});

		return projectsWithCounts;
	}, [
		projectsArray,
		searchQuery,
		sortBy,
		sortOrder,
		projectItemCounts,
	]);

	if (projectsLoading) {
		return (
			<div className="space-y-6">
				<Skeleton className="h-12 w-full" />
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{[...Array(6)].map((_, i) => (
						<Skeleton key={i} className="h-48" />
					))}
				</div>
			</div>
		);
	}

	if (projectsError) {
		return (
			<Alert variant="destructive">
				Failed to load projects: {projectsError.message}
			</Alert>
		);
	}

	return (
		<div className="space-y-6 p-6">
			{/* Header */}
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Projects</h1>
					<p className="mt-2 text-muted-foreground">
						Manage your traceability projects
					</p>
				</div>
				<Button
					onClick={() => navigate({ search: { action: "create" } as any })}
				>
					+ New Project
				</Button>
			</div>

			{/* Filters and Search */}
			<Card className="p-4">
				<div className="flex flex-col md:flex-row gap-4">
					<div className="flex-1">
						<Input
							type="search"
							placeholder="Search projects..."
							value={searchQuery}
							onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
								setSearchQuery((e.currentTarget as HTMLInputElement).value)
							}
						/>
					</div>
					<div className="flex items-center gap-2">
						<Select
							value={sortBy}
							onValueChange={(value) =>
								setSortBy(value as "name" | "date" | "items")
							}
						>
							<SelectTrigger className="w-[180px]">
								<SelectValue />
							</SelectTrigger>
							<SelectContent>
								<SelectItem value="date">Sort by Date</SelectItem>
								<SelectItem value="name">Sort by Name</SelectItem>
								<SelectItem value="items">Sort by Items</SelectItem>
							</SelectContent>
						</Select>
						<Button
							variant="outline"
							size="sm"
							onClick={() => setSortOrder(sortOrder === "asc" ? "desc" : "asc")}
						>
							{sortOrder === "asc" ? "↑" : "↓"}
						</Button>
					</div>
				</div>
			</Card>

			{/* Stats */}
			<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
				<Card className="p-6 hover:shadow-md transition-shadow">
					<div className="text-sm font-medium text-muted-foreground">
						Total Projects
					</div>
					<div className="mt-2 text-3xl font-bold tracking-tight">
						{projectsArray.length || 0}
					</div>
				</Card>
				<Card className="p-6 hover:shadow-md transition-shadow">
					<div className="text-sm font-medium text-muted-foreground">
						Total Items
					</div>
					<div className="mt-2 text-3xl font-bold tracking-tight">
						{Object.values(projectItemCounts).reduce((a, b) => a + b, 0)}
					</div>
				</Card>
				<Card className="p-6 hover:shadow-md transition-shadow">
					<div className="text-sm font-medium text-muted-foreground">
						Avg Items/Project
					</div>
					<div className="mt-2 text-3xl font-bold tracking-tight">
						{projectsArray.length > 0
							? Math.round(
									Object.values(projectItemCounts).reduce((a, b) => a + b, 0) /
										Math.max(projectsArray.length, 1),
								)
							: 0}
					</div>
				</Card>
			</div>

			{/* Projects Grid */}
			{filteredAndSortedProjects.length > 0 ? (
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
					{filteredAndSortedProjects.map(({ project, itemCount }) => (
						<ProjectCard
							key={project.id}
							project={project}
							itemCount={itemCount}
						/>
					))}
				</div>
			) : (
				<Card className="p-12">
					<div className="text-center">
						<Folder className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
						<h3 className="text-xl font-semibold mb-2">
							{searchQuery ? "No projects found" : "No projects yet"}
						</h3>
						<p className="text-muted-foreground mb-6">
							{searchQuery
								? "Try adjusting your search criteria"
								: "Get started by creating your first project"}
						</p>
						{!searchQuery && (
							<Button
								onClick={() =>
									navigate({ search: { action: "create" } as any })
								}
							>
								Create Project
							</Button>
						)}
					</div>
				</Card>
			)}

			{/* Create Dialog */}
			<CreateProjectDialog
				open={showCreateDialog}
				onOpenChange={handleOpenChange}
			/>
		</div>
	);
}
