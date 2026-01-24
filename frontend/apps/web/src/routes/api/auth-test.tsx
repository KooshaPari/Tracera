import { createFileRoute } from "@tanstack/react-router";

/**
 * API Route: POST /api/auth-test
 * Test endpoint for authentication validation
 * Note: This is a placeholder - actual API routes should be handled by the backend
 */
export const Route = createFileRoute("/api/auth-test")({
	component: AuthTestComponent,
	loader: async () => {
		// Placeholder - actual auth test should be handled by backend API
		return { message: "API route - use backend endpoint instead" };
	},
});

function AuthTestComponent() {
	return <div>API route - use backend endpoint instead</div>;
}
