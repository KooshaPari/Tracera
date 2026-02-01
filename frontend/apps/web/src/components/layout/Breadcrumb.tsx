import { Link, useMatches, useParams } from "@tanstack/react-router";
import {
	BreadcrumbItem,
	BreadcrumbLink,
	BreadcrumbList,
	BreadcrumbPage,
	BreadcrumbSeparator,
	Breadcrumb as ShadcnBreadcrumb,
	Skeleton,
} from "@tracertm/ui";
import { Fragment, useMemo } from "react";
import { useItem } from "@/hooks/useItems";
import { useProject } from "@/hooks/useProjects";

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
			const pathname = match?.pathname ?? "";
			if (pathname === "/" || pathname === "") {
				return;
			}

			const pathSegments = pathname.split("/").filter(Boolean);

			pathSegments.forEach((segment, index) => {
				if (segment == null || typeof segment !== "string") return;
				const href = `/${pathSegments.slice(0, index + 1).join("/")}`;

				// Skip IDs and query parameters
				if (segment.match(/^[a-f0-9-]{36}$/i) || segment.startsWith("?")) {
					return;
				}

				// Skip duplicate paths
				if (segments.some((s) => s.href === href)) {
					return;
				}

				// Skip literal "null" segment (bad URL) — show fallback instead of "Null"
				if (segment.toLowerCase() === "null") {
					if (segment === projectId) {
						segments.push({
							label: project?.name?.trim() || "Project",
							href,
							isLoading: projectLoading,
						});
					} else {
						segments.push({ label: "—", href });
					}
					return;
				}

				// Fetch project name if this is a project ID
				if (segment === projectId && project) {
					segments.push({
						label: (project.name ?? "Project").trim() || "Project",
						href,
						isLoading: projectLoading,
					});
					return;
				}

				// Fetch item name if this is an item ID
				if (segment === itemId && currentItem) {
					segments.push({
						label: (currentItem.title ?? "Item").trim() || "Item",
						href,
						isLoading: itemLoading,
					});
					return;
				}

				// Format segment label
				const label = segment
					.split(/[-_]/)
					.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
					.join(" ")
					.trim();

				// Add view type with special handling
				if (segment === viewType && viewType) {
					const viewLabel = viewType
						.split("-")
						.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
						.join(" ")
						.trim();
					segments.push({
						label: viewLabel || "View",
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
			className="hidden md:block max-w-full min-w-0"
			aria-label="breadcrumb"
			role="navigation"
		>
			<BreadcrumbList>
				<BreadcrumbItem className="min-w-0">
					<BreadcrumbLink
						asChild
						className="text-[10px] sm:text-xs font-bold uppercase tracking-[0.2em] sm:tracking-widest text-muted-foreground hover:text-primary transition-colors truncate max-w-[110px] sm:max-w-[140px] md:max-w-[180px]"
					>
						<Link to="/home">Dashboard</Link>
					</BreadcrumbLink>
				</BreadcrumbItem>

				{uniqueBreadcrumbs.map((item, index) => (
					<Fragment key={item.href}>
						<BreadcrumbSeparator className="text-muted-foreground/50" />
						<BreadcrumbItem className="min-w-0">
							{item.isLoading ? (
								<div className="flex items-center gap-2">
									<Skeleton className="h-4 w-16" />
								</div>
							) : index === uniqueBreadcrumbs.length - 1 ? (
								<BreadcrumbPage className="text-[10px] sm:text-xs font-semibold uppercase tracking-[0.2em] sm:tracking-widest text-primary truncate max-w-[110px] sm:max-w-[160px] md:max-w-[220px] lg:max-w-[280px]">
									{item.label}
								</BreadcrumbPage>
							) : (
								<BreadcrumbLink
									asChild
									className="text-[10px] sm:text-xs font-medium uppercase tracking-[0.2em] sm:tracking-widest text-muted-foreground hover:text-primary transition-colors truncate max-w-[110px] sm:max-w-[140px] md:max-w-[180px]"
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
