import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import type { ReactNode } from "react";

/**
 * API Route: GET /api/swagger-config
 * Returns Swagger UI configuration
 */
export const Route = createFileRoute("/api/swagger-config")({
	component: SwaggerConfigComponent,
	loader: async () => {
		const config = {
			apiUrl: (process.env as any).API_URL || "http://localhost:8000",
			authType: "bearer",
			persistAuth: true,
			tryItOut: true,
			displayRequestDuration: true,
			filter: true,
			deepLinking: true,
			docExpansion: "list",
			defaultModelsExpandDepth: 1,
			supportedSubmitMethods: [
				"get",
				"put",
				"post",
				"delete",
				"options",
				"head",
				"patch",
			],
			oauth2RedirectUrl: `${(process.env as any).PUBLIC_URL || "http://localhost:3000"}/api-docs/swagger/oauth2-redirect.html`,
			requestInterceptor: {
				enabled: true,
				addAuthHeader: true,
				addCorsHeaders: true,
			},
			responseInterceptor: {
				enabled: true,
				logResponses: true,
			},
		};
		return config;
	},
});

function SwaggerConfigComponent(): ReactNode {
	const data = useLoaderData({ from: "/api/swagger-config" });
	return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
