/**
 * Views Barrel Export
 * Comprehensive collection of all application views
 */

// ============================================================================
// Core Views
// ============================================================================
export { DashboardView } from "./DashboardView";
export { ProjectsListView } from "./ProjectsListView";
export { ProjectDetailView } from "./ProjectDetailView";
export { ProjectSettingsView } from "./ProjectSettingsView";
export { ProjectMappingGraphView } from "./ProjectMappingGraphView";

// ============================================================================
// Item Management Views
// ============================================================================
export { ItemDetailView } from "./ItemDetailView";
export { ItemsTableView } from "./ItemsTableView";
export { ItemsTreeView } from "./ItemsTreeView";
export { ItemsKanbanView } from "./ItemsKanbanView";

// ============================================================================
// Specification Views (ADR, Contracts, BDD Features)
// ============================================================================
export { ADRView } from "./ADRView";
export { ContractView } from "./ContractView";
export { ComplianceView } from "./ComplianceView";
export { FeatureDetailView } from "./FeatureDetailView";

// New comprehensive specification views
export { ADRListView } from "./ADRListView";
export { ADRDetailView } from "./ADRDetailView";
export { ContractListView } from "./ContractListView";
export { FeatureListView } from "./FeatureListView";
export { FeatureDetailView as FeatureDetailViewV2 } from "./FeatureDetailView2";
export { SpecificationsDashboardView } from "./SpecificationsDashboardView";

// ============================================================================
// Analysis & Reporting Views
// ============================================================================
export { GraphView } from "./GraphView";
export { SearchView } from "./SearchView";
export { AdvancedSearchView } from "./AdvancedSearchView";
export { TraceabilityMatrixView } from "./TraceabilityMatrixView";
export { ImpactAnalysisView } from "./ImpactAnalysisView";
export { EventsTimelineView } from "./EventsTimelineView";
export { ReportsView } from "./ReportsView";

// ============================================================================
// Link Management Views
// ============================================================================
export { LinksView } from "./LinksView";

// ============================================================================
// Import/Export Views
// ============================================================================
export { ImportView } from "./ImportView";
export { ExportView } from "./ExportView";

// ============================================================================
// Settings & Configuration Views
// ============================================================================
export { SettingsView } from "./SettingsView";

// ============================================================================
// Workflow & Automation Views
// ============================================================================
export { AgentWorkflowView } from "./AgentWorkflowView";
