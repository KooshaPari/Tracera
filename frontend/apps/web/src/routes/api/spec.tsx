import { createFileRoute, useLoaderData } from "@tanstack/react-router";

/**
 * API Route: GET /api/spec
 * Returns the OpenAPI specification
 * Note: This is a placeholder - actual API routes should be handled by the backend
 */

export const Route = createFileRoute("/api/spec")({
	component: SpecComponent,
	loader: async () => {
		// Placeholder - actual spec should come from backend
		return { message: "API route - use backend endpoint instead" };
	},
});

function SpecComponent() {
	const data = useLoaderData({ from: "/api/spec" });
	return <pre>{JSON.stringify(data, undefined, 2)}</pre>;
}
