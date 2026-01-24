import { createFileRoute, useLoaderData } from "@tanstack/react-router";
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
import { SECURITY_VIEW } from "@/routes/projects.$projectId.views.security";
import { TEST_VIEW } from "@/routes/projects.$projectId.views.test";
import { WIREFRAME_VIEW } from "@/routes/projects.$projectId.views.wireframe";

function ViewTypeComponent() {
	const { viewType } = useLoaderData({
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
		default:
			throw new Error(`Unknown view type: ${viewType}`);
	}
}

export const Route = createFileRoute("/projects/$projectId/views/$viewType")({
	component: ViewTypeComponent,
	loader: async ({ params }) => {
		return { viewType: params.viewType };
	},
});
