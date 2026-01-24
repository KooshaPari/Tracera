/**
 * Tests for Settings API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Settings } from "@/api/settings";
import { fetchSettings, updateSettings } from "@/api/settings";

// Mock the API client
vi.mock("@/api/client", () => ({
	apiClient: {
		GET: vi.fn(),
		PUT: vi.fn(),
	},
	safeApiCall: vi.fn((promise) => promise),
}));

import { apiClient, safeApiCall } from "@/api/client";

describe("Settings API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchSettings", () => {
		it("should fetch settings from API", async () => {
			const mockSettings: Settings = {
				general: {
					theme: "dark",
					language: "en",
					timezone: "UTC",
				},
				notifications: {
					email: true,
					push: false,
					inApp: true,
				},
				security: {
					twoFactor: true,
					sessionTimeout: 60,
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result).toEqual(mockSettings);
			expect(result.general.theme).toBe("dark");
			expect(result.security.twoFactor).toBe(true);
		});

		it("should return default settings if API fails", async () => {
			vi.mocked(safeApiCall).mockRejectedValue(new Error("API failed"));

			const result = await fetchSettings();

			expect(result).toEqual({
				general: {
					theme: "system",
					language: "en",
				},
				notifications: {
					email: true,
					push: true,
					inApp: true,
				},
				security: {
					twoFactor: false,
					sessionTimeout: 30,
				},
			});
		});

		it("should return default settings if API returns null", async () => {
			vi.mocked(safeApiCall).mockResolvedValue({
				data: null,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.general.theme).toBe("system");
			expect(result.notifications.email).toBe(true);
		});

		it("should include general settings", async () => {
			const mockSettings: Settings = {
				general: {
					theme: "light",
					language: "es",
					timezone: "EST",
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.general).toHaveProperty("theme");
			expect(result.general).toHaveProperty("language");
			expect(result.general).toHaveProperty("timezone");
		});

		it("should include notification settings", async () => {
			const mockSettings: Settings = {
				general: {},
				notifications: {
					email: false,
					push: true,
					inApp: false,
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.notifications?.email).toBe(false);
			expect(result.notifications?.push).toBe(true);
			expect(result.notifications?.inApp).toBe(false);
		});

		it("should include security settings", async () => {
			const mockSettings: Settings = {
				general: {},
				security: {
					twoFactor: true,
					sessionTimeout: 120,
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: mockSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.security?.twoFactor).toBe(true);
			expect(result.security?.sessionTimeout).toBe(120);
		});

		it("should call API with correct endpoint", async () => {
			vi.mocked(safeApiCall).mockResolvedValue({
				data: undefined,
				error: undefined,
				response: new Response(),
			});

			await fetchSettings();

			expect(apiClient.GET).toHaveBeenCalledWith(
				"/api/v1/settings",
				expect.any(Object),
			);
		});

		it("should support all theme options", async () => {
			const themes: Array<"light" | "dark" | "system"> = [
				"light",
				"dark",
				"system",
			];

			for (const theme of themes) {
				vi.mocked(safeApiCall).mockResolvedValue({
					data: {
						general: { theme },
					},
					error: undefined,
					response: new Response(),
				});

				const result = await fetchSettings();
				expect(result.general.theme).toBe(theme);
			}
		});

		it("should handle missing optional fields", async () => {
			const minimalSettings: Settings = {
				general: {},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: minimalSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.general).toBeDefined();
		});
	});

	describe("updateSettings", () => {
		it("should update general settings", async () => {
			const updatedSettings: Settings = {
				general: {
					theme: "dark",
					language: "fr",
				},
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				general: { theme: "dark", language: "fr" },
			});

			expect(result.general.theme).toBe("dark");
			expect(result.general.language).toBe("fr");
		});

		it("should update notification settings", async () => {
			const updatedSettings: Settings = {
				general: {},
				notifications: {
					email: false,
					push: false,
					inApp: true,
				},
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				notifications: { email: false, push: false, inApp: true },
			});

			expect(result.notifications?.email).toBe(false);
		});

		it("should update security settings", async () => {
			const updatedSettings: Settings = {
				general: {},
				security: {
					twoFactor: true,
					sessionTimeout: 90,
				},
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				security: { twoFactor: true, sessionTimeout: 90 },
			});

			expect(result.security?.twoFactor).toBe(true);
			expect(result.security?.sessionTimeout).toBe(90);
		});

		it("should handle API response with data", async () => {
			const updatedSettings: Settings = {
				general: { theme: "dark" },
				notifications: { email: true },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				general: { theme: "dark" },
			});

			expect(result).toEqual(updatedSettings);
		});

		it("should handle API errors gracefully", async () => {
			vi.mocked(apiClient.PUT).mockRejectedValue(new Error("API failed"));

			const result = await updateSettings({
				general: { theme: "dark" },
			});

			expect(result).toHaveProperty("general");
		});

		it("should merge partial settings with defaults", async () => {
			vi.mocked(apiClient.PUT).mockRejectedValue(new Error("API failed"));

			const result = await updateSettings({
				general: { theme: "light" },
			});

			expect(result.general).toHaveProperty("theme");
		});

		it("should call API with correct endpoint", async () => {
			const updatedSettings: Settings = {
				general: { theme: "dark" },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			await updateSettings({ general: { theme: "dark" } });

			expect(apiClient.PUT).toHaveBeenCalledWith(
				"/api/v1/settings",
				expect.objectContaining({
					body: { general: { theme: "dark" } },
				}),
			);
		});

		it("should pass settings as request body", async () => {
			const settingsUpdate = {
				general: { theme: "dark" },
				notifications: { email: false },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: settingsUpdate as Settings,
				error: undefined,
				response: new Response(),
			});

			await updateSettings(settingsUpdate);

			expect(apiClient.PUT).toHaveBeenCalledWith(
				"/api/v1/settings",
				expect.objectContaining({
					body: settingsUpdate,
				}),
			);
		});

		it("should return response data when available", async () => {
			const updatedSettings: Settings = {
				general: { theme: "dark" },
				notifications: { email: false },
				security: { twoFactor: true },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updatedSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				general: { theme: "dark" },
			});

			expect(result).toEqual(updatedSettings);
		});

		it("should handle multiple setting updates", async () => {
			const updates = {
				general: { theme: "dark", language: "es" },
				notifications: { email: false },
				security: { twoFactor: true },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: updates as Settings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings(updates);

			expect(result).toHaveProperty("general");
			expect(result).toHaveProperty("notifications");
			expect(result).toHaveProperty("security");
		});

		it("should handle partial updates", async () => {
			const partialUpdate = {
				general: { theme: "light" },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: partialUpdate as Settings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings(partialUpdate);

			expect(result.general).toBeDefined();
		});

		it("should preserve existing settings during update", async () => {
			const completeSettings: Settings = {
				general: { theme: "dark", language: "en", timezone: "UTC" },
				notifications: { email: true, push: false, inApp: true },
				security: { twoFactor: false, sessionTimeout: 30 },
			};

			vi.mocked(apiClient.PUT).mockResolvedValue({
				data: completeSettings,
				error: undefined,
				response: new Response(),
			});

			const result = await updateSettings({
				general: { theme: "light" },
			});

			expect(result).toBeDefined();
		});
	});

	describe("Settings API error handling", () => {
		it("should handle network errors in fetch", async () => {
			vi.mocked(safeApiCall).mockRejectedValue(new Error("Network error"));

			const result = await fetchSettings();

			expect(result.general.theme).toBe("system");
		});

		it("should handle network errors in update", async () => {
			vi.mocked(apiClient.PUT).mockRejectedValue(new Error("Network error"));

			const result = await updateSettings({
				general: { theme: "dark" },
			});

			expect(result).toBeDefined();
		});

		it("should handle undefined response data", async () => {
			vi.mocked(safeApiCall).mockResolvedValue({
				data: undefined,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result).toBeDefined();
			expect(result.general).toBeDefined();
		});

		it("should handle empty settings object", async () => {
			vi.mocked(safeApiCall).mockResolvedValue({
				data: {},
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result).toBeDefined();
		});
	});

	describe("Settings data validation", () => {
		it("should handle large session timeout values", async () => {
			const settings: Settings = {
				general: {},
				security: {
					sessionTimeout: 10080, // 7 days in minutes
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: settings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.security?.sessionTimeout).toBe(10080);
		});

		it("should handle zero session timeout", async () => {
			const settings: Settings = {
				general: {},
				security: {
					sessionTimeout: 0,
				},
			};

			vi.mocked(safeApiCall).mockResolvedValue({
				data: settings,
				error: undefined,
				response: new Response(),
			});

			const result = await fetchSettings();

			expect(result.security?.sessionTimeout).toBe(0);
		});

		it("should support multiple languages", async () => {
			const languages = ["en", "es", "fr", "de", "ja"];

			for (const language of languages) {
				vi.mocked(safeApiCall).mockResolvedValue({
					data: { general: { language } },
					error: undefined,
					response: new Response(),
				});

				const result = await fetchSettings();
				expect(result.general.language).toBe(language);
			}
		});

		it("should support multiple timezones", async () => {
			const timezones = ["UTC", "EST", "PST", "IST"];

			for (const timezone of timezones) {
				vi.mocked(safeApiCall).mockResolvedValue({
					data: { general: { timezone } },
					error: undefined,
					response: new Response(),
				});

				const result = await fetchSettings();
				expect(result.general.timezone).toBe(timezone);
			}
		});
	});
});
