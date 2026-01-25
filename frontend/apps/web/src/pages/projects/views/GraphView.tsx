// Project-specific Graph View - Unified view with sidebar navigation
// Provides separated views: traceability, page flow, component library, and perspectives

import { useNavigate, useParams } from "@tanstack/react-router";
import { UnifiedGraphView } from "../../../components/graph";
import { useItems } from "../../../hooks/useItems";
import { useLinks } from "../../../hooks/useLinks";

export function GraphView() {
	const { projectId } = useParams({ strict: false }) as { projectId?: string };
	const navigate = useNavigate();

	const { data: itemsData, isLoading: itemsLoading } = useItems({
		projectId: projectId,
	});
	const { data: linksData, isLoading: linksLoading } = useLinks({
		projectId: projectId,
	});

	// Extract arrays from hook structure
	const items = itemsData?.items || [];
	const links = linksData?.links || [];

	const handleNavigateToItem = (itemId: string) => {
		navigate({ to: "/items/$itemId", params: { itemId } });
	};

	return (
		<UnifiedGraphView
			items={items}
			links={links}
			isLoading={itemsLoading || linksLoading}
			projectId={projectId}
			onNavigateToItem={handleNavigateToItem}
		/>
	);
}
