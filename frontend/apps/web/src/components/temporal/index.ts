/**
 * Temporal Components - Version/branch navigation and progress tracking UI
 * Provides timeline, branch explorer, version comparison, and progress monitoring views
 */

// ===== Navigation & Visualization Components =====
export {
	TemporalNavigator,
	type TemporalNavigatorProps,
	type ViewMode,
	type Branch,
	type Version,
} from "./TemporalNavigator";

export { TimelineView, type TimelineViewProps } from "./TimelineView";

export {
	BranchExplorer,
	type BranchExplorerProps,
} from "./BranchExplorer";

// ===== Version Comparison Components =====
export { VersionDiff, type VersionDiffProps } from "./VersionDiff";

export { DiffViewer, type DiffViewerProps } from "./DiffViewer";

// ===== Progress Tracking Components =====
export {
	ProgressDashboard,
	type ProgressDashboardProps,
} from "./ProgressDashboard";

export {
	ProgressRing,
	ProgressBar,
	LinearProgress,
	type ProgressRingProps,
	type ProgressBarProps,
	type LinearProgressProps,
} from "./ProgressRing";

export { BurndownChart, type BurndownChartProps } from "./BurndownChart";

export { VelocityChart, type VelocityChartProps } from "./VelocityChart";
