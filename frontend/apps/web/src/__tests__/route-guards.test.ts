/**
 * Tests for route guard utilities
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import {
	requireAuth,
	requireAuthWithAccount,
	checkAuth,
} from "@/lib/route-guards";
import { useAuthStore } from "@/stores/authStore";

// Mock the redirect function
vi.mock("@tanstack/react-router", () => ({
	redirect: (options: any) => {
		throw new Error(JSON.stringify(options));
	},
}));

describe("Route Guards", () => {
	beforeEach(() => {
		// Reset auth store before each test
		useAuthStore.setState({
			user: null,
			token: null,
			account: null,
			isAuthenticated: false,
		});
	});

	describe("requireAuth", () => {
		it("should throw redirect when user is not authenticated", () => {
			expect(() => requireAuth()).toThrow();
		});

		it("should throw redirect when user is null", () => {
			useAuthStore.setState({
				isAuthenticated: true,
				user: null,
			});

			expect(() => requireAuth()).toThrow();
		});

		it("should not throw when user is authenticated", () => {
			useAuthStore.setState({
				isAuthenticated: true,
				user: { id: "1", email: "test@example.com" },
			});

			expect(() => requireAuth()).not.toThrow();
		});

		it("should redirect to custom path when specified", () => {
			try {
				requireAuth({ redirectTo: "/auth/login" });
			} catch (error) {
				const redirectOptions = JSON.parse((error as Error).message);
				expect(redirectOptions.to).toBe("/auth/login");
			}
		});

		it("should include returnTo parameter by default", () => {
			const originalLocation = window.location;
			delete (window as any).location;
			window.location = {
				pathname: "/projects/123",
				search: "?tab=features",
			} as any;

			try {
				requireAuth();
			} catch (error) {
				const redirectOptions = JSON.parse((error as Error).message);
				expect(redirectOptions.search).toEqual({
					returnTo: "/projects/123?tab=features",
				});
			}

			window.location = originalLocation;
		});

		it("should not include returnTo when disabled", () => {
			try {
				requireAuth({ includeReturnUrl: false });
			} catch (error) {
				const redirectOptions = JSON.parse((error as Error).message);
				expect(redirectOptions.search).toBeUndefined();
			}
		});
	});

	describe("requireAuthWithAccount", () => {
		it("should throw redirect when user is not authenticated", () => {
			expect(() => requireAuthWithAccount()).toThrow();
		});

		it("should redirect to account selection when authenticated but no account", () => {
			useAuthStore.setState({
				isAuthenticated: true,
				user: { id: "1", email: "test@example.com" },
				account: null,
			});

			try {
				requireAuthWithAccount();
			} catch (error) {
				const redirectOptions = JSON.parse((error as Error).message);
				expect(redirectOptions.to).toBe("/account/select");
			}
		});

		it("should not throw when user is authenticated with account", () => {
			useAuthStore.setState({
				isAuthenticated: true,
				user: { id: "1", email: "test@example.com" },
				account: {
					id: "acc1",
					name: "Test Account",
					slug: "test",
					account_type: "team",
				},
			});

			expect(() => requireAuthWithAccount()).not.toThrow();
		});
	});

	describe("checkAuth", () => {
		it("should return current auth state", () => {
			useAuthStore.setState({
				isAuthenticated: false,
				user: null,
				account: null,
			});

			const result = checkAuth();
			expect(result).toEqual({
				isAuthenticated: false,
				user: null,
				account: null,
			});
		});

		it("should return authenticated state", () => {
			const mockUser = { id: "1", email: "test@example.com" };
			const mockAccount = {
				id: "acc1",
				name: "Test Account",
				slug: "test",
				account_type: "team",
			};

			useAuthStore.setState({
				isAuthenticated: true,
				user: mockUser,
				account: mockAccount,
			});

			const result = checkAuth();
			expect(result).toEqual({
				isAuthenticated: true,
				user: mockUser,
				account: mockAccount,
			});
		});
	});
});
