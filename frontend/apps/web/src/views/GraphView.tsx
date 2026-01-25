// Global Graph View - Unified view with sidebar navigation and separated views
import { useSearch } from "@tanstack/react-router";
import { useNavigate } from "@tanstack/react-router";
import { UnifiedGraphView } from "../components/graph";
import { useItems } from "../hooks/useItems";
import { useLinks } from "../hooks/useLinks";

export function GraphView() {
	const searchParams = useSearch({ strict: false }) as Record<string, string | undefined>;
	const projectFilter = searchParams?.["project"] || undefined;
	const navigate = useNavigate();

	const { data: itemsData, isLoading: itemsLoading } = useItems({
		projectId: projectFilter,
	});
	const { data: linksData, isLoading: linksLoading } = useLinks({
		projectId: projectFilter,
	});

	// Extract arrays from new hook structure
	const items = itemsData?.items || [];
	const links = linksData?.links || [];

	const handleNavigateToItem = (itemId: string) => {
		// Navigate to item detail page
		navigate({ to: "/items/$itemId", params: { itemId } });
	};

	return (
		<UnifiedGraphView
			items={items}
			links={links}
			isLoading={itemsLoading || linksLoading}
			projectId={projectFilter}
			onNavigateToItem={handleNavigateToItem}
		/>
	);
}
