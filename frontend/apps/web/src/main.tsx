import { RouterProvider } from "@tanstack/react-router";
import { createRoot } from "react-dom/client";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AppProviders } from "@/providers/AppProviders";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { createRetryFetch } from "@/lib/fetch-retry";
import { renderPreflightFailure, runFrontendPreflight } from "@/lib/preflight";
import { createRouter } from "./router";
import "./index.css";

// Patch global fetch with wait+retry so all API and preflight calls use robust retry
if (typeof globalThis.fetch !== "undefined") {
	(globalThis as Window & { fetch: typeof fetch }).fetch = createRetryFetch(
		globalThis.fetch,
		{ maxRetries: 3, timeoutMs: 15_000 },
	);
}

// Initialize MSW in development mode - DISABLED to use real backend
const enableMocking = false; // Set to false to use real backend API

async function prepare(): Promise<boolean> {
	const preflight = await runFrontendPreflight();
	if (!preflight.ok) {
		renderPreflightFailure(preflight);
		return false;
	}

	if (enableMocking) {
		const { startMockServiceWorker } = await import("./mocks");
		await startMockServiceWorker();
	}

	return true;
}

// Create router
const router = createRouter();
router.update({
	defaultErrorComponent: ({ error }) => (
		<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
			<h1 className="text-2xl font-bold text-destructive mb-4">
				Something went wrong
			</h1>
			<p className="text-muted-foreground mb-4">{error.message}</p>
			<button
				onClick={() => window.location.reload()}
				className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
			>
				Try again
			</button>
		</div>
	),
});

prepare().then((ready) => {
	if (!ready) {
		return;
	}

	const rootElement = document.getElementById("root");
	if (!rootElement) throw new Error("Root element not found");

	// Create root and render
	const root = createRoot(rootElement);

	root.render(
		<ThemeProvider>
			<AppProviders>
				<TooltipProvider>
					<RouterProvider router={router} />
				</TooltipProvider>
			</AppProviders>
		</ThemeProvider>,
	);
});
