import { createFileRoute } from "@tanstack/react-router";
import { RedocWrapper } from "@/components/api-docs/redoc-wrapper";

export const Route = createFileRoute("/api-docs/redoc")({
	component: RedocPage,
	head: () => ({
		meta: [
			{
				title: "API Reference - ReDoc | TraceRTM",
			},
			{
				name: "description",
				content:
					"Comprehensive API reference documentation for TraceRTM using ReDoc. Browse endpoints, schemas, and examples in a clean, responsive interface.",
			},
		],
	}),
});

function RedocPage() {
	return (
		<div className="redoc-page">
			<RedocWrapper
				specUrl="/specs/openapi.json"
				scrollYOffset={80}
				hideDownloadButton={false}
				disableSearch={false}
				expandResponses="200,201"
				requiredPropsFirst={true}
				sortPropsAlphabetically={false}
				expandSingleSchemaField={true}
			/>
		</div>
	);
}
