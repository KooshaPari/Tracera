import { Link, useMatches, useParams } from "@tanstack/react-router";
import { Fragment, useMemo } from "react";
import {
	Breadcrumb as ShadcnBreadcrumb,
	BreadcrumbItem,
	BreadcrumbLink,
	BreadcrumbList,
	BreadcrumbPage,
	BreadcrumbSeparator,
} from "@tracertm/ui";
import { useProject } from "@/hooks/useProjects";
import { useItem } from "@/hooks/useItems";
import { Skeleton } from "@tracertm/ui";

interface BreadcrumbSegment {
	label: string;
	href: string;
	isLoading?: boolean;
}

export function Breadcrumbs() {
	const matches = useMatches();
	const params = useParams({ strict: false });
	const projectId = params.projectId as string | undefined;
	const itemId = params.itemId as string | undefined;
	const viewType = params.viewType as string | undefined;

	// Fetch project data
	const { data: project, isLoading: projectLoading } = useProject(
		projectId || "",
	);

	// Fetch item data if itemId exists
	const { data: currentItem, isLoading: itemLoading } = useItem(itemId || "");

	// Generate breadcrumbs from matches with smart data fetching
	const breadcrumbs = useMemo(() => {
		const segments: BreadcrumbSegment[] = [];

		matches.forEach((match) => {
			if (match.pathname === "/" || match.pathname === "") {
				return;
			}

			const pathSegments = match.pathname.split("/").filter(Boolean);

			pathSegments.forEach((segment, index) => {
				const href = "/" + pathSegments.slice(0, index + 1).join("/");

				// Skip IDs and query parameters
				if (segment.match(/^[a-f0-9-]{36}$/i) || segment.startsWith("?")) {
					return;
				}

				// Skip duplicate paths
				if (segments.some((s) => s.href === href)) {
					return;
				}

				// Fetch project name if this is a project ID
				if (segment === projectId && project) {
					segments.push({
						label: project.name || "Project",
						href,
						isLoading: projectLoading,
					});
					return;
				}

				// Fetch item name if this is an item ID
				if (segment === itemId && currentItem) {
					segments.push({
						label: currentItem.title || "Item",
						href,
						isLoading: itemLoading,
					});
					return;
				}

				// Format segment label
				const label = segment
					.split(/[-_]/)
					.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
					.join(" ");

				// Add view type with special handling
				if (segment === viewType && viewType) {
					const viewLabel = viewType
						.split("-")
						.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
						.join(" ");
					segments.push({
						label: viewLabel,
						href,
					});
				} else if (!segments.some((s) => s.label === label)) {
					segments.push({
						label: label || "Page",
						href,
					});
				}
			});
		});

		return segments;
	}, [
		matches,
		projectId,
		project,
		projectLoading,
		itemId,
		currentItem,
		itemLoading,
		viewType,
	]);

	// De-duplicate breadcrumbs
	const uniqueBreadcrumbs = Array.from(
		new Map(breadcrumbs.map((b) => [b.href, b])).values(),
	);

	if (uniqueBreadcrumbs.length === 0) {
		return null;
	}

	return (
		<ShadcnBreadcrumb
			separator="/"
			className="hidden lg:block"
			aria-label="breadcrumb"
		>
			<BreadcrumbList>
				<BreadcrumbItem>
					<BreadcrumbLink
						asChild
						className="text-xs font-bold uppercase tracking-widest text-muted-foreground hover:text-primary transition-colors"
					>
						<Link to="/">Dashboard</Link>
					</BreadcrumbLink>
				</BreadcrumbItem>

				{uniqueBreadcrumbs.map((item, index) => (
					<Fragment key={item.href}>
						<BreadcrumbSeparator className="text-muted-foreground/50" />
						<BreadcrumbItem>
							{item.isLoading ? (
								<div className="flex items-center gap-2">
									<Skeleton className="h-4 w-16" />
								</div>
							) : index === uniqueBreadcrumbs.length - 1 ? (
								<BreadcrumbPage className="text-xs font-semibold uppercase tracking-widest text-primary">
									{item.label}
								</BreadcrumbPage>
							) : (
								<BreadcrumbLink
									asChild
									className="text-xs font-medium uppercase tracking-widest text-muted-foreground hover:text-primary transition-colors"
								>
									<Link to={item.href}>{item.label}</Link>
								</BreadcrumbLink>
							)}
						</BreadcrumbItem>
					</Fragment>
				))}
			</BreadcrumbList>
		</ShadcnBreadcrumb>
	);
}
