import { createRetryFetch } from "@/lib/fetch-retry";
import { renderPreflightFailure, runFrontendPreflight } from "@/lib/preflight";
import { initSentry } from "@/lib/sentry";
import { createRouter } from "./router";
import "./index.css";

// Initialize Sentry error tracking before anything else
initSentry();

// Patch global fetch with wait+retry so all API and preflight calls use robust retry
if (typeof globalThis.fetch !== "undefined") {
	// eslint-disable-next-line @typescript-eslint/no-unsafe-type-assertion -- intentional global fetch override
	(globalThis as unknown as Window & { fetch: typeof fetch }).fetch =
		createRetryFetch(globalThis.fetch, { maxRetries: 3, timeoutMs: 15_000 });
}

// Initialize MSW in development mode - DISABLED to use real backend
const enableMocking = false; // Set to false to use real backend API

function _prepare(): Promise<boolean> {
	return runFrontendPreflight().then((preflight) => {
		if (!preflight.ok) {
			renderPreflightFailure(preflight);
			return false;
		}
		if (enableMocking) {
			return import("./mocks").then(({ startMockServiceWorker }) =>
				startMockServiceWorker().then(() => true),
			);
		}
		return true;
	});
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
				onClick={() => globalThis.location.reload()}
				className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
			>
				Try again
			</button>
		</div>
	),
});
