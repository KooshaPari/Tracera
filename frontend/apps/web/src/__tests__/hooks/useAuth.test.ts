/**
 * Tests for useAuth hook
 */

import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { useAuth, useIsAuthenticated, useUser } from "../../hooks/useAuth";
import { useAuthStore } from "../../stores/authStore";

describe("useAuth", () => {
	beforeEach(() => {
		const { logout } = useAuthStore.getState();
		logout();
		localStorage.clear();
	});

	describe("useAuth", () => {
		it("should return auth state and methods", () => {
			const { result } = renderHook(() => useAuth());

			expect(result.current).toHaveProperty("user");
			expect(result.current).toHaveProperty("token");
			expect(result.current).toHaveProperty("isAuthenticated");
			expect(result.current).toHaveProperty("isLoading");
			expect(result.current).toHaveProperty("login");
			expect(result.current).toHaveProperty("logout");
			expect(result.current).toHaveProperty("refreshToken");
			expect(result.current).toHaveProperty("updateProfile");
		});

		it("should handle login", async () => {
			const { result } = renderHook(() => useAuth());

			await act(async () => {
				await result.current.login("test@example.com", "password");
			});

			expect(result.current.isAuthenticated).toBe(true);
			expect(result.current.user).toBeTruthy();
		});

		it("should handle logout", async () => {
			const { result } = renderHook(() => useAuth());

			await act(async () => {
				await result.current.login("test@example.com", "password");
			});

			act(() => {
				result.current.logout();
			});

			expect(result.current.isAuthenticated).toBe(false);
			expect(result.current.user).toBeNull();
		});
	});

	describe("useUser", () => {
		it("should return user when authenticated", async () => {
			const { result: authResult } = renderHook(() => useAuth());

			await act(async () => {
				await authResult.current.login("test@example.com", "password");
			});

			const { result } = renderHook(() => useUser());

			expect(result.current).toBeTruthy();
			expect(result.current?.email).toBe("test@example.com");
		});

		it("should return null when not authenticated", () => {
			const { result } = renderHook(() => useUser());

			expect(result.current).toBeNull();
		});
	});

	describe("useIsAuthenticated", () => {
		it("should return true when authenticated", async () => {
			const { result: authResult } = renderHook(() => useAuth());

			await act(async () => {
				await authResult.current.login("test@example.com", "password");
			});

			const { result } = renderHook(() => useIsAuthenticated());

			expect(result.current).toBe(true);
		});

		it("should return false when not authenticated", () => {
			const { result } = renderHook(() => useIsAuthenticated());

			expect(result.current).toBe(false);
		});
	});
});
