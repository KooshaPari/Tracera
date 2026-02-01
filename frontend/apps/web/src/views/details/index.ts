/**
 * Detail Views - Type-specific detail page components
 *
 * Exports base components and shared tabs for building consistent
 * detail pages across all item types.
 */

export type {
	BaseDetailViewProps,
	DetailAction,
	DetailTab,
} from "./BaseDetailView";
// Base layout components
export { BaseDetailView } from "./BaseDetailView";
export type { DetailHeaderProps } from "./DetailHeader";
export { DetailHeader } from "./DetailHeader";
export { EpicDetailView } from "./EpicDetailView";
// Router (default export)
export { default, default as ItemDetailRouter } from "./ItemDetailRouter";
// Type-specific views
export { RequirementDetailView } from "./RequirementDetailView";
export { TestDetailView } from "./TestDetailView";
export type { CommentsTabProps } from "./tabs/CommentsTab";
export { CommentsTab } from "./tabs/CommentsTab";
export type { HistoryTabProps } from "./tabs/HistoryTab";
export { HistoryTab } from "./tabs/HistoryTab";
export type { LinksTabProps } from "./tabs/LinksTab";
export { LinksTab } from "./tabs/LinksTab";
export type { OverviewTabProps } from "./tabs/OverviewTab";
// Shared tab components
export { OverviewTab } from "./tabs/OverviewTab";
