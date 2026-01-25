// Unified Graph View - Renders appropriate view based on mode
// Integrates GraphViewContainer with FlowGraphView, PageInteractionFlow, and UIComponentTree

import { Card } from "@tracertm/ui/components/Card";
import type { Item, Link } from "@tracertm/types";
import { ReactFlowProvider } from "@xyflow/react";
import { Component } from "lucide-react";
import { useMemo } from "react";
import { FlowGraphViewInner } from "./FlowGraphViewInner";
import { GraphViewContainer, type GraphViewMode } from "./GraphViewContainer";
import { PageInteractionFlow } from "./PageInteractionFlow";
import { UIComponentTree } from "./UIComponentTree";
import type { GraphPerspective } from "./types";
import { TYPE_TO_PERSPECTIVE } from "./types";

interface UnifiedGraphViewProps {
  items: Item[];
  links: Link[];
  isLoading?: boolean | undefined;
  projectId?: string | undefined;
  onNavigateToItem?: ((itemId: string) => void) | undefined;
  defaultView?: GraphViewMode | undefined;
}

// Filter items and links by perspective
function filterByPerspective(
  items: Item[],
  links: Link[],
  perspective: GraphPerspective | null
): { filteredItems: Item[]; filteredLinks: Link[] } {
  if (!perspective || perspective === "all") {
    return { filteredItems: items, filteredLinks: links };
  }

  const filteredItems = items.filter((item) => {
    const itemType = (item.type || item.view || "item").toLowerCase();
    const perspectives = TYPE_TO_PERSPECTIVE[itemType] || ["all"];
    return perspectives.includes(perspective);
  });

  const itemIds = new Set(filteredItems.map((i) => i.id));
  const filteredLinks = links.filter(
    (link) => itemIds.has(link.sourceId) && itemIds.has(link.targetId)
  );

  return { filteredItems, filteredLinks };
}

// Full-height component library view
function ComponentLibraryView({
  items,
  links,
  onNavigateToItem,
}: {
  items: Item[];
  links: Link[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}) {
  return (
    <div className="h-full p-4">
      <Card className="h-full overflow-hidden">
        <div className="p-4 border-b flex items-center gap-2">
          <Component className="h-5 w-5 text-primary" />
          <h2 className="font-semibold">UI Component Library</h2>
        </div>
        <div className="h-[calc(100%-60px)]">
          <UIComponentTree
            items={items}
            links={links}
            onSelectItem={onNavigateToItem ?? (() => {})}
            selectedItemId={null}
          />
        </div>
      </Card>
    </div>
  );
}

// Render the appropriate view
function ViewRenderer({
  viewMode,
  perspective,
  items,
  links,
  onNavigateToItem,
}: {
  viewMode: GraphViewMode;
  perspective: GraphPerspective | null;
  items: Item[];
  links: Link[];
  onNavigateToItem?: ((itemId: string) => void) | undefined;
}) {
  // Apply perspective filtering
  const { filteredItems, filteredLinks } = useMemo(
    () => filterByPerspective(items, links, perspective),
    [items, links, perspective]
  );

  // Render based on view mode
  switch (viewMode) {
    case "page-flow":
      return (
        <div className="h-full p-4">
          <PageInteractionFlow
            items={items}
            links={links}
            onSelectItem={onNavigateToItem}
            onPreviewItem={onNavigateToItem}
          />
        </div>
      );

    case "components":
      return (
        <ComponentLibraryView items={items} links={links} onNavigateToItem={onNavigateToItem} />
      );

    case "traceability":
    case "perspective-product":
    case "perspective-business":
    case "perspective-technical":
    case "perspective-ui":
    case "perspective-security":
    case "perspective-performance":
    default:
      // Use the traceability graph view with perspective filtering
      return (
        <div className="h-full p-4">
          <ReactFlowProvider>
            <FlowGraphViewInner
              items={filteredItems}
              links={filteredLinks}
              perspective={perspective ?? "all"}
              onNavigateToItem={onNavigateToItem}
            />
          </ReactFlowProvider>
        </div>
      );
  }
}

export function UnifiedGraphView({
  items,
  links,
  isLoading = false,
  projectId,
  onNavigateToItem,
  defaultView = "traceability",
}: UnifiedGraphViewProps) {
  return (
    <div className="h-[calc(100vh-120px)]">
      <GraphViewContainer
        items={items}
        links={links}
        isLoading={isLoading}
        projectId={projectId}
        onNavigateToItem={onNavigateToItem}
        defaultView={defaultView}
      >
        {({ viewMode, perspective, items, links, onNavigateToItem }) => (
          <ViewRenderer
            viewMode={viewMode}
            perspective={perspective}
            items={items}
            links={links}
            onNavigateToItem={onNavigateToItem}
          />
        )}
      </GraphViewContainer>
    </div>
  );
}
