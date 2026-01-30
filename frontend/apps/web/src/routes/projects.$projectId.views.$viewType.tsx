import {
	createFileRoute,
	useLoaderData,
	useParams,
} from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { ChunkLoadingSkeleton } from "@/lib/lazy-loading";
import { API_VIEW } from "@/routes/projects.$projectId.views.api";
import { ARCHITECTURE_VIEW } from "@/routes/projects.$projectId.views.architecture";
import { CODE_VIEW } from "@/routes/projects.$projectId.views.code";
import { CONFIGURATION_VIEW } from "@/routes/projects.$projectId.views.configuration";
import { DATABASE_VIEW } from "@/routes/projects.$projectId.views.database";
import { DATAFLOW_VIEW } from "@/routes/projects.$projectId.views.dataflow";
import { DEPENDENCY_VIEW } from "@/routes/projects.$projectId.views.dependency";
import { DOMAIN_VIEW } from "@/routes/projects.$projectId.views.domain";
import { FEATURE_VIEW } from "@/routes/projects.$projectId.views.feature";
import { INFRASTRUCTURE_VIEW } from "@/routes/projects.$projectId.views.infrastructure";
import { JOURNEY_VIEW } from "@/routes/projects.$projectId.views.journey";
import { MONITORING_VIEW } from "@/routes/projects.$projectId.views.monitoring";
import { PERFORMANCE_VIEW } from "@/routes/projects.$projectId.views.performance";
import { PROBLEM_VIEW } from "@/routes/projects.$projectId.views.problem";
import { PROCESS_VIEW } from "@/routes/projects.$projectId.views.process";
import { SECURITY_VIEW } from "@/routes/projects.$projectId.views.security";
import { TEST_VIEW } from "@/routes/projects.$projectId.views.test";
import { WIREFRAME_VIEW } from "@/routes/projects.$projectId.views.wireframe";

// Lazy load heavy components that use graph visualization
// These components import elkjs, cytoscape, @xyflow which are all heavy
const GraphViewLazy = lazy(() =>
	import("@/pages/projects/views/GraphView").then((m) => ({
		default: m.GraphView,
	})),
);
const IntegrationsViewLazy = lazy(
	() => import("@/pages/projects/views/IntegrationsView"),
);
const CoverageMatrixViewLazy = lazy(() =>
	import("@/pages/projects/views/CoverageMatrixView").then((m) => ({
		default: m.CoverageMatrixView,
	})),
);
const QADashboardViewLazy = lazy(() =>
	import("@/pages/projects/views/QADashboardView").then((m) => ({
		default: m.QADashboardView,
	})),
);
const TestCaseViewLazy = lazy(() =>
	import("@/pages/projects/views/TestCaseView").then((m) => ({
		default: m.TestCaseView,
	})),
);
const TestRunViewLazy = lazy(() =>
	import("@/pages/projects/views/TestRunView").then((m) => ({
		default: m.TestRunView,
	})),
);
const TestSuiteViewLazy = lazy(() =>
	import("@/pages/projects/views/TestSuiteView").then((m) => ({
		default: m.TestSuiteView,
	})),
);
const WebhookIntegrationsViewLazy = lazy(() =>
	import("@/pages/projects/views/WebhookIntegrationsView").then((m) => ({
		default: m.WebhookIntegrationsView,
	})),
);
const WorkflowRunsViewLazy = lazy(() =>
	import("@/pages/projects/views/WorkflowRunsView").then((m) => ({
		default: m.WorkflowRunsView,
	})),
);

function LoadingFallback() {
	return <ChunkLoadingSkeleton message="Loading view..." />;
}

function ViewTypeComponent() {
	const { viewType } = useLoaderData({
		from: "/projects/$projectId/views/$viewType",
	});
	const { projectId } = useParams({
		from: "/projects/$projectId/views/$viewType",
	});

	// Based on viewType, render the appropriate view component
	switch (viewType) {
		case "feature":
			return <FEATURE_VIEW />;
		case "code":
			return <CODE_VIEW />;
		case "test":
			return <TEST_VIEW />;
		case "api":
			return <API_VIEW />;
		case "database":
			return <DATABASE_VIEW />;
		case "wireframe":
			return <WIREFRAME_VIEW />;
		case "architecture":
			return <ARCHITECTURE_VIEW />;
		case "infrastructure":
			return <INFRASTRUCTURE_VIEW />;
		case "dataflow":
			return <DATAFLOW_VIEW />;
		case "security":
			return <SECURITY_VIEW />;
		case "performance":
			return <PERFORMANCE_VIEW />;
		case "monitoring":
			return <MONITORING_VIEW />;
		case "domain":
			return <DOMAIN_VIEW />;
		case "journey":
			return <JOURNEY_VIEW />;
		case "configuration":
			return <CONFIGURATION_VIEW />;
		case "dependency":
			return <DEPENDENCY_VIEW />;
		case "problem":
			return <PROBLEM_VIEW />;
		case "process":
			return <PROCESS_VIEW />;
		case "graph":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<GraphViewLazy />
				</Suspense>
			);
		case "integrations":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<IntegrationsViewLazy projectId={projectId} />
				</Suspense>
			);
		case "webhooks":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<WebhookIntegrationsViewLazy projectId={projectId} />
				</Suspense>
			);
		case "coverage":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<CoverageMatrixViewLazy projectId={projectId} />
				</Suspense>
			);
		case "qa-dashboard":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<QADashboardViewLazy projectId={projectId} />
				</Suspense>
			);
		case "test-cases":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<TestCaseViewLazy projectId={projectId} />
				</Suspense>
			);
		case "test-runs":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<TestRunViewLazy projectId={projectId} />
				</Suspense>
			);
		case "test-suites":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<TestSuiteViewLazy projectId={projectId} />
				</Suspense>
			);
		case "workflows":
			return (
				<Suspense fallback={<LoadingFallback />}>
					<WorkflowRunsViewLazy projectId={projectId} />
				</Suspense>
			);
		default:
			return (
				<div className="p-6">
					<h1 className="text-2xl font-semibold">Unknown view</h1>
					<p className="text-muted-foreground">Unknown view type: {viewType}</p>
				</div>
			);
	}
}

export const Route = createFileRoute("/projects/$projectId/views/$viewType")({
	component: ViewTypeComponent,
	loader: async ({ params }: { params: { viewType: string } }) => {
		return { viewType: params.viewType };
	},
});
