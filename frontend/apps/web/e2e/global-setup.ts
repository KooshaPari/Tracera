import { test as base, expect as baseExpect, type Locator } from "@playwright/test";
import { setupApiMocks } from "./fixtures/api-mocks";

/**
 * Extended test fixture with API mocking enabled by default
 */
export const test = base.extend({
	page: async ({ page }, use, testInfo) => {
		// Setup API mocks BEFORE any navigation
		await setupApiMocks(page);

		const shouldAutoAuth = !/auth|security/i.test(testInfo.file);

		if (shouldAutoAuth) {
			const authState = {
				user: {
					id: "test-user",
					email: "test@example.com",
					name: "Test User",
					role: "admin",
				},
				token: "test-token",
				account: {
					id: "test-account",
					name: "Test Account",
					slug: "test-account",
					account_type: "personal",
				},
				isAuthenticated: true,
			};

			await page.addInitScript((state) => {
				// Mark test environment for route guards
				(globalThis as any).__E2E__ = true;
				const serialized = JSON.stringify({ state, version: 0 });
				localStorage.setItem("tracertm-auth-store", serialized);
				if (state.token) {
					localStorage.setItem("auth_token", state.token);
					localStorage.setItem("authToken", state.token);
				}
			}, authState);
		}

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

export const expect = baseExpect.extend({
	async toBeInTheDocument(locator: Locator) {
		const count = await locator.count();
		const pass = count > 0;
		return {
			pass,
			message: () =>
				`expected locator${pass ? " not" : ""} to be in the document`,
		};
	},
});
