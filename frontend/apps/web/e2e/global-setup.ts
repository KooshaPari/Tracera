/**
 * Global Setup - Runs once before all tests
 *
 * Use for:
 * - Starting mock API servers
 * - Seeding test database
 * - Generating authentication tokens
 */
import type { FullConfig } from "@playwright/test";

async function globalSetup(config: FullConfig) {
	console.log("🚀 Global setup starting...");

	// Example: Start mock API server
	// const mockServer = await startMockServer();
	// process.env.MOCK_SERVER_URL = mockServer.url;

	console.log("✅ Global setup complete");
}

export default globalSetup;
