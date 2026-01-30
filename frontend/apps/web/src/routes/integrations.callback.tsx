import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useCompleteOAuth } from "../hooks/useIntegrations";

export const Route = createFileRoute("/integrations/callback" as any)({
	component: OAuthCallbackPage,
});

function OAuthCallbackPage() {
	const navigate = useNavigate();
	const completeOAuth = useCompleteOAuth();
	const [error, setError] = useState<string | null>(null);
	const [processing, setProcessing] = useState(true);

	useEffect(() => {
		const handleCallback = async () => {
			const params = new URLSearchParams(window.location.search);
			const code = params.get("code");
			const state = params.get("state");
			const errorParam = params.get("error");
			const errorDescription = params.get("error_description");

			if (errorParam) {
				setError(errorDescription || errorParam);
				setProcessing(false);
				return;
			}

			if (!code || !state) {
				setError("Missing authorization code or state parameter");
				setProcessing(false);
				return;
			}

			try {
				// Extract project ID from state
				const [projectId] = state.split(":");

				await completeOAuth.mutateAsync({
					code,
					state,
					redirectUri: `${window.location.origin}/integrations/callback`,
				});

				// Redirect back to integrations page
				navigate({
					to: `/projects/${projectId}/views/integrations`,
					replace: true,
				});
			} catch (err) {
				setError(
					err instanceof Error ? err.message : "Failed to complete OAuth",
				);
				setProcessing(false);
			}
		};

		handleCallback();
	}, [completeOAuth, navigate]);

	if (error) {
		return (
			<div className="min-h-screen flex items-center justify-center p-6">
				<div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
					<div className="text-center">
						<div className="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
							<svg
								className="w-6 h-6 text-red-600 dark:text-red-400"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<title>Error</title>
								<path
									strokeLinecap="round"
									strokeLinejoin="round"
									strokeWidth={2}
									d="M6 18L18 6M6 6l12 12"
								/>
							</svg>
						</div>
						<h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
							Authorization Failed
						</h1>
						<p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
						<button
							type="button"
							onClick={() => navigate({ to: "/projects" })}
							className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
						>
							Return to Projects
						</button>
					</div>
				</div>
			</div>
		);
	}

	if (processing) {
		return (
			<div className="min-h-screen flex items-center justify-center p-6">
				<div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
					<div className="text-center">
						<div className="w-12 h-12 mx-auto mb-4 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
							<div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
						</div>
						<h1 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
							Completing Authorization
						</h1>
						<p className="text-gray-600 dark:text-gray-400">
							Please wait while we connect your account...
						</p>
					</div>
				</div>
			</div>
		);
	}

	return null;
}
