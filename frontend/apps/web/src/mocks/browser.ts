// MSW browser setup for TraceRTM
import { setupWorker } from "msw/browser";
import { handlers } from "./handlers";

// This configures a Service Worker with the given request handlers.
export const worker = setupWorker(...handlers);

// Start the worker with custom options
export async function startMockServiceWorker() {
	if (typeof window === "undefined") {
		return;
	}

	try {
		await worker.start({
			onUnhandledRequest: "bypass", // Don't warn about unhandled requests
			serviceWorker: {
				url: "/mockServiceWorker.js",
			},
		});
		console.log("[MSW] Mock Service Worker started successfully");
	} catch (error) {
		console.error("[MSW] Failed to start Mock Service Worker:", error);
	}
}
