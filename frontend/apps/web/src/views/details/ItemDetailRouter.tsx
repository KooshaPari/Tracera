/**
 * ItemDetailRouter
 *
 * Routes to type-specific detail views based on item type.
 * Uses type guards to determine the correct view component to render.
 */

import type { TypedItem } from "@tracertm/types";

import { ItemDetailView } from "@/views/ItemDetailView";
import {
  isDefectItem,
  isEpicItem,
  isRequirementItem,
  isTaskItem,
  isTestItem,
  isUserStoryItem,
} from "@tracertm/types";

import { EpicDetailView } from "./EpicDetailView";
import { RequirementDetailView } from "./RequirementDetailView";
import { TestDetailView } from "./TestDetailView";
import { WorkItemDetailView } from "./WorkItemDetailView";

interface ItemDetailRouterProps {
  item: TypedItem;
  projectId: string;
}

/**
 * Routes item to the appropriate detail view based on type.
 * Falls back to generic ItemDetailView if no specific view exists.
 */
export default function ItemDetailRouter({ item, projectId }: ItemDetailRouterProps) {
  // Route to requirement view
  if (isRequirementItem(item)) {
    return <RequirementDetailView item={item} projectId={projectId} />;
  }

  // Route to test view
  if (isTestItem(item)) {
    return <TestDetailView item={item} projectId={projectId} />;
  }

  // Route to epic view
  if (isEpicItem(item)) {
    return <EpicDetailView item={item} projectId={projectId} />;
  }

  // User story, task and defect share one work-item detail view
  if (isUserStoryItem(item) || isTaskItem(item) || isDefectItem(item)) {
    return <WorkItemDetailView item={item} projectId={projectId} />;
  }

  // Fallback to generic item detail view for other types
  return <ItemDetailView />;
}
