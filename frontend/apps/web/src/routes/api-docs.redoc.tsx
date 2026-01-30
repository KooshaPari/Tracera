import { createFileRoute } from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { ChunkLoadingSkeleton } from "@/lib/lazy-loading";

const RedocWrapper = lazy(() =>
	import("@/components/api-docs/redoc-wrapper").then((m) => ({
		default: m.RedocWrapper,
	})),
);

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
			<Suspense
				fallback={<ChunkLoadingSkeleton message="Loading API reference..." />}
			>
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
			</Suspense>
		</div>
	);
}
