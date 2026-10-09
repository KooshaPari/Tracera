/** Explicit viewport budgeting for the project graph. Fetched data is never discarded. */
export function graphLinkForView<Link extends {
  source_id?: string;
  target_id?: string;
  link_type?: string;
  sourceId?: string;
  targetId?: string;
  type?: string;
  id?: string;
}>(link: Link, projectId: string) {
  const sourceId = link.source_id ?? link.sourceId ?? "";
  const targetId = link.target_id ?? link.targetId ?? "";
  const type = link.link_type ?? link.type ?? "";
  return {
    ...link,
    id: link.id ?? JSON.stringify([projectId, sourceId, targetId, type]),
    projectId,
    sourceId,
    targetId,
    type,
  };
}

export function graphVisibility<Item extends { id: string }, Link extends {
  sourceId: string;
  targetId: string;
}>(
  items: Item[],
  links: Link[],
  visibleNodeCount: number,
  visibleEdgeCount: number,
  hasMoreItemPages: boolean,
  hasMoreLinkPages: boolean,
) {
  const visibleItems = items.slice(0, visibleNodeCount);
  const ids = new Set(visibleItems.map((item) => item.id));
  const eligibleLinks = links.filter(
    (link) => ids.has(link.sourceId) && ids.has(link.targetId),
  );
  const visibleLinks = eligibleLinks.slice(0, visibleEdgeCount);
  return {
    visibleItems,
    visibleLinks,
    unavailableEndpointLinks:
      hasMoreItemPages || hasMoreLinkPages || visibleItems.length < items.length
        ? 0
        : links.length - eligibleLinks.length,
    canLoadMore:
      visibleItems.length < items.length ||
      visibleLinks.length < eligibleLinks.length ||
      hasMoreItemPages ||
      hasMoreLinkPages,
  };
}
