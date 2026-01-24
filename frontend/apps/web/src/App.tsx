// LEGACY FILE - Not currently used (app uses @tanstack/react-router via main.tsx)
// This file is kept for reference but is not imported anywhere
// If you need to use this, install react-router-dom: bun add react-router-dom

// LEGACY FILE - All imports commented out since file is not used
// import { Route, Routes } from 'react-router-dom'
// import { CommandPalette } from './components/CommandPalette'
// import { Layout } from './components/layout/Layout'
// Legacy pages (kept for compatibility)
// import { Dashboard } from './pages/Dashboard'
// import { ProjectDetail } from './pages/projects/ProjectDetail'
// import { ProjectList } from './pages/projects/ProjectList'
// import { ApiView } from './pages/projects/views/ApiView'
// import { CodeView } from './pages/projects/views/CodeView'
// import { DatabaseView } from './pages/projects/views/DatabaseView'
// import { DeploymentView } from './pages/projects/views/DeploymentView'
// import { DocumentationView } from './pages/projects/views/DocumentationView'
// import { FeatureView } from './pages/projects/views/FeatureView'
// import { GraphView as LegacyGraphView } from './pages/projects/views/GraphView'
// import { TestView } from './pages/projects/views/TestView'
// import { WireframeView } from './pages/projects/views/WireframeView'
// import { Settings } from './pages/settings/Settings'
// Import all views
// import {
//   AgentsView,
//   DashboardView,
//   EventsTimelineView,
//   GraphView,
//   ImpactAnalysisView,
//   ItemDetailView,
//   ItemsKanbanView,
//   ItemsTableView,
//   ItemsTreeView,
//   LinksView,
//   ProjectDetailView,
//   ProjectsListView,
//   ReportsView,
//   SearchView,
//   SettingsView,
//   TraceabilityMatrixView,
// } from './views'

export default function App() {
	// Legacy component - not used (app uses @tanstack/react-router)
	// All Routes are commented out to avoid type errors since react-router-dom is not installed
	return (
		<>
			{/* <CommandPalette /> */}
			{/* Legacy routes - uncomment if react-router-dom is installed
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardView />} />
          <Route path="projects" element={<ProjectsListView />} />
          <Route path="projects/:projectId" element={<ProjectDetailView />} />
          <Route path="items" element={<ItemsTableView />} />
          <Route path="items/kanban" element={<ItemsKanbanView />} />
          <Route path="items/tree" element={<ItemsTreeView />} />
          <Route path="items/:itemId" element={<ItemDetailView />} />
          <Route path="links" element={<LinksView />} />
          <Route path="graph" element={<GraphView />} />
          <Route path="agents" element={<AgentsView />} />
          <Route path="events" element={<EventsTimelineView />} />
          <Route path="search" element={<SearchView />} />
          <Route path="matrix" element={<TraceabilityMatrixView />} />
          <Route path="impact" element={<ImpactAnalysisView />} />
          <Route path="reports" element={<ReportsView />} />
          <Route path="settings" element={<SettingsView />} />
          <Route path="legacy/dashboard" element={<Dashboard />} />
          <Route path="legacy/projects" element={<ProjectList />} />
          <Route path="legacy/projects/:projectId" element={<ProjectDetail />}>
            <Route index element={<FeatureView />} />
            <Route path="feature" element={<FeatureView />} />
            <Route path="code" element={<CodeView />} />
            <Route path="test" element={<TestView />} />
            <Route path="graph" element={<LegacyGraphView />} />
            <Route path="api" element={<ApiView />} />
            <Route path="database" element={<DatabaseView />} />
            <Route path="wireframe" element={<WireframeView />} />
            <Route path="documentation" element={<DocumentationView />} />
            <Route path="deployment" element={<DeploymentView />} />
          </Route>
          <Route path="legacy/settings" element={<Settings />} />
        </Route>
      </Routes>
      */}
		</>
	);
}
