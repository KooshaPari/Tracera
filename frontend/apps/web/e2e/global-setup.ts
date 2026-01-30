import { test as base, expect as baseExpect } from "@playwright/test";
import { setupApiMocks } from "./fixtures/api-mocks";

/**
 * Extended test fixture with API mocking enabled by default
 */
export const test = base.extend({
	page: async ({ page }, use) => {
		// Setup API mocks BEFORE any navigation
		await setupApiMocks(page);

		// Override goto to ensure mocks are in place
		const originalGoto = page.goto.bind(page);
		page.goto = async (
			url: string,
			options?: Parameters<typeof originalGoto>[1],
		) => {
			return originalGoto(url, options);
		};

		await use(page);
	},
});

export const expect = baseExpect;
