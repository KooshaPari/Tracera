import type { TypedItem } from "@tracertm/types";
import { Link } from "@tanstack/react-router";
import {
	Check,
	ChevronDown,
	ChevronRight,
	Copy,
	Globe,
	Play,
} from "lucide-react";
import { useState } from "react";
import { useItems } from "@/hooks/useItems";
import { Skeleton } from "@tracertm/ui/components/Skeleton";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface ApiViewProps {
	projectId: string;
}

interface Endpoint {
	id: string;
	method: HttpMethod;
	path: string;
	description: string;
	status: "implemented" | "planned" | "deprecated";
	requestBody?: string;
	responseExample?: string;
}

interface ApiGroup {
	id: string;
	name: string;
	baseUrl: string;
	endpoints: Endpoint[];
}

const apiGroups: ApiGroup[] = [
	{
		id: "1",
		name: "Projects",
		baseUrl: "/api/v1/projects",
		endpoints: [
			{
				id: "1.1",
				method: "GET",
				path: "/",
				description: "List all projects",
				status: "implemented",
				responseExample: '[{"id": "uuid", "name": "Project"}]',
			},
			{
				id: "1.2",
				method: "POST",
				path: "/",
				description: "Create a project",
				status: "implemented",
				requestBody: '{"name": "string"}',
			},
			{
				id: "1.3",
				method: "GET",
				path: "/{id}",
				description: "Get project by ID",
				status: "implemented",
			},
			{
				id: "1.4",
				method: "PATCH",
				path: "/{id}",
				description: "Update project",
				status: "implemented",
			},
			{
				id: "1.5",
				method: "DELETE",
				path: "/{id}",
				description: "Delete project",
				status: "planned",
			},
		],
	},
	{
		id: "2",
		name: "Items",
		baseUrl: "/api/v1/items",
		endpoints: [
			{
				id: "2.1",
				method: "GET",
				path: "/",
				description: "List items with filters",
				status: "implemented",
			},
			{
				id: "2.2",
				method: "POST",
				path: "/",
				description: "Create an item",
				status: "implemented",
			},
			{
				id: "2.3",
				method: "GET",
				path: "/{id}",
				description: "Get item by ID",
				status: "implemented",
			},
			{
				id: "2.4",
				method: "PATCH",
				path: "/{id}",
				description: "Update item",
				status: "implemented",
			},
			{
				id: "2.5",
				method: "GET",
				path: "/{id}/history",
				description: "Get item version history",
				status: "planned",
			},
		],
	},
	{
		id: "3",
		name: "Links",
		baseUrl: "/api/v1/links",
		endpoints: [
			{
				id: "3.1",
				method: "GET",
				path: "/",
				description: "List all links",
				status: "implemented",
			},
			{
				id: "3.2",
				method: "POST",
				path: "/",
				description: "Create a link",
				status: "implemented",
			},
			{
				id: "3.3",
				method: "DELETE",
				path: "/{id}",
				description: "Delete a link",
				status: "implemented",
			},
			{
				id: "3.4",
				method: "GET",
				path: "/graph",
				description: "Get full traceability graph",
				status: "planned",
			},
		],
	},
];

const methodColors: Record<HttpMethod, string> = {
	GET: "bg-green-100 text-green-700",
	POST: "bg-blue-100 text-blue-700",
	PUT: "bg-yellow-100 text-yellow-700",
	PATCH: "bg-orange-100 text-orange-700",
	DELETE: "bg-red-100 text-red-700",
};

const statusBadge: Record<string, string> = {
	implemented: "bg-green-500",
	planned: "bg-yellow-500",
	deprecated: "bg-red-500",
};

export function ApiView({ projectId }: ApiViewProps) {
	const [expanded, setExpanded] = useState<Set<string>>(new Set(["1"]));
	const [copied, setCopied] = useState<string | null>(null);

	const { data: projectData, isLoading: projectLoading } = useItems({
		projectId,
		view: "api",
	});
	const projectItems = projectData?.items ?? [];

	const toggle = (id: string) => {
		const next = new Set(expanded);
		if (next.has(id)) {
			next.delete(id);
		} else {
			next.add(id);
		}
		setExpanded(next);
	};

	const copyPath = async (endpoint: Endpoint, group: ApiGroup) => {
		if (navigator.clipboard?.writeText) {
			await navigator.clipboard.writeText(group.baseUrl + endpoint.path);
		}
		setCopied(endpoint.id);
		setTimeout(() => setCopied(null), 2000);
	};

	return (
		<div className="flex-1 space-y-6 p-6">
			<div>
				<h1 className="text-3xl font-bold tracking-tight">API Endpoints</h1>
				<p className="text-muted-foreground">
					REST API contracts and specifications for this project
				</p>
			</div>

			{projectLoading ? (
				<div className="space-y-2">
					<Skeleton className="h-10 w-full rounded-lg" />
					<Skeleton className="h-10 w-full rounded-lg" />
					<Skeleton className="h-10 w-full rounded-lg" />
				</div>
			) : projectItems.length > 0 ? (
				<div className="space-y-2">
					<h2 className="text-lg font-semibold">Project API items</h2>
					<div className="rounded-lg border">
						{projectItems.map((item: TypedItem) => {
							const method =
								(item.metadata as { method?: string })?.method ?? "GET";
							const path = item.title ?? item.id;
							return (
								<Link
									key={item.id}
									to="/projects/$projectId/views/$viewType/$itemId"
									params={{
										projectId,
										viewType: "api",
										itemId: item.id,
									}}
									className="flex items-center gap-3 border-b last:border-b-0 p-3 hover:bg-muted/50"
								>
									<span
										className={`rounded px-2 py-0.5 text-xs font-mono font-bold ${methodColors[method as HttpMethod] ?? methodColors.GET}`}
									>
										{method}
									</span>
									<code className="text-sm">{path}</code>
									<span className="flex-1 truncate text-sm text-muted-foreground">
										{item.description ?? item.type}
									</span>
								</Link>
							);
						})}
					</div>
				</div>
			) : null}

			<div className="space-y-2">
				<h2 className="text-lg font-semibold">Reference</h2>
				<div className="rounded-lg border">
				{apiGroups.map((group) => (
					<div key={group.id} className="border-b last:border-b-0">
						<div
							className="flex cursor-pointer items-center gap-3 p-4 hover:bg-accent/50"
							onClick={() => toggle(group.id)}
						>
							{expanded.has(group.id) ? (
								<ChevronDown className="h-4 w-4" />
							) : (
								<ChevronRight className="h-4 w-4" />
							)}
							<Globe className="h-5 w-5 text-blue-500" />
							<span className="font-medium">{group.name}</span>
							<code className="ml-2 text-xs text-muted-foreground">
								{group.baseUrl}
							</code>
							<span className="ml-auto text-xs text-muted-foreground">
								{group.endpoints.length} endpoints
							</span>
						</div>
						{expanded.has(group.id) && (
							<div className="border-t bg-muted/20">
								{group.endpoints.map((endpoint) => (
									<div
										key={endpoint.id}
										className="flex items-center gap-3 border-b last:border-b-0 p-3 pl-12"
									>
										<span
											className={`rounded px-2 py-0.5 text-xs font-mono font-bold ${methodColors[endpoint.method]}`}
										>
											{endpoint.method}
										</span>
										<code className="text-sm">{endpoint.path}</code>
										<span className="flex-1 text-sm text-muted-foreground">
											{endpoint.description}
										</span>
										<span
											className={`h-2 w-2 rounded-full ${statusBadge[endpoint.status]}`}
											title={endpoint.status}
										/>
										<button
											onClick={() => copyPath(endpoint, group)}
											className="rounded p-1 hover:bg-accent"
										>
											{copied === endpoint.id ? (
												<Check className="h-4 w-4 text-green-500" />
											) : (
												<Copy className="h-4 w-4" />
											)}
										</button>
										<button
											className="rounded p-1 hover:bg-accent"
											title="Try it"
										>
											<Play className="h-4 w-4" />
										</button>
									</div>
								))}
							</div>
						)}
					</div>
				))}
			</div>
			</div>
		</div>
	);
}
