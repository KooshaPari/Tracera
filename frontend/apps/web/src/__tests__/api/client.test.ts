/**
 * Comprehensive tests for API client
 * Goal: Increase coverage from 58% to 95%
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	ApiError,
	apiClient,
	handleApiResponse,
	safeApiCall,
} from "@/api/client";

// Mock openapi-fetch
vi.mock("openapi-fetch", () => {
	const mockClient = {
		GET: vi.fn(),
		POST: vi.fn(),
		PUT: vi.fn(),
		DELETE: vi.fn(),
		use: vi.fn(),
	};
	return {
		default: vi.fn(() => mockClient),
	};
});

// Mock localStorage
const localStorageMock = {
	getItem: vi.fn(),
	setItem: vi.fn(),
	removeItem: vi.fn(),
	clear: vi.fn(),
};
global.localStorage = localStorageMock as any;

describe("API Client", () => {
	beforeEach(() => {
		vi.clearAllMocks();
		localStorageMock.getItem.mockReturnValue(null);
	});

	describe("apiClient initialization", () => {
		it("should initialize apiClient", () => {
			expect(apiClient).toBeDefined();
			expect(apiClient.GET).toBeDefined();
			expect(apiClient.POST).toBeDefined();
			expect(apiClient.PUT).toBeDefined();
			expect(apiClient.DELETE).toBeDefined();
		});

		it("should have use method for interceptors", () => {
			expect(apiClient.use).toBeDefined();
		});
	});

	describe("safeApiCall", () => {
		it("should return promise when valid", async () => {
			const mockPromise = Promise.resolve({
				data: "test",
				error: undefined,
				response: new Response(),
			});
			const result = await safeApiCall(mockPromise);
			expect(result).toEqual({
				data: "test",
				error: undefined,
				response: expect.any(Response),
			});
		});

		it("should reject when promise is null", async () => {
			await expect(safeApiCall(null)).rejects.toThrow(ApiError);
			await expect(safeApiCall(null)).rejects.toThrow(
				"API request failed: promise is null",
			);
		});

		it("should reject when promise is undefined", async () => {
			await expect(safeApiCall(undefined)).rejects.toThrow(ApiError);
		});
	});

	describe("handleApiResponse", () => {
		it("should return data when successful", async () => {
			const mockPromise = Promise.resolve({
				data: { id: "1", name: "Test" },
				error: undefined,
				response: new Response(),
			});

			const result = await handleApiResponse(mockPromise);
			expect(result).toEqual({ id: "1", name: "Test" });
		});

		it("should throw ApiError when promise is null", async () => {
			await expect(handleApiResponse(null)).rejects.toThrow(ApiError);
			await expect(handleApiResponse(null)).rejects.toThrow(
				"API request failed: promise is null",
			);
		});

		it("should throw ApiError when promise is undefined", async () => {
			await expect(handleApiResponse(undefined)).rejects.toThrow(ApiError);
		});

		it("should throw ApiError when error is present", async () => {
			const mockPromise = Promise.resolve({
				data: undefined,
				error: { message: "Not found" },
				response: new Response(null, { status: 404, statusText: "Not Found" }),
			});

			await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
			try {
				await handleApiResponse(mockPromise);
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).status).toBe(404);
				expect((error as ApiError).statusText).toBe("Not Found");
			}
		});

		it("should throw ApiError when no data returned", async () => {
			const mockPromise = Promise.resolve({
				data: undefined,
				error: undefined,
				response: new Response(null, { status: 204, statusText: "No Content" }),
			});

			await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
			try {
				await handleApiResponse(mockPromise);
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).status).toBe(204);
				expect((error as ApiError).statusText).toBe("No data returned");
			}
		});

		it("should handle error without response", async () => {
			const mockPromise = Promise.resolve({
				data: undefined,
				error: { message: "Error" },
				response: undefined as any,
			});

			await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
			try {
				await handleApiResponse(mockPromise);
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).status).toBe(500);
				expect((error as ApiError).statusText).toBe("Unknown error");
			}
		});

		it("should handle no data without response", async () => {
			const mockPromise = Promise.resolve({
				data: undefined,
				error: undefined,
				response: undefined as any,
			});

			await expect(handleApiResponse(mockPromise)).rejects.toThrow(ApiError);
			try {
				await handleApiResponse(mockPromise);
			} catch (error) {
				expect(error).toBeInstanceOf(ApiError);
				expect((error as ApiError).status).toBe(500);
				expect((error as ApiError).statusText).toBe("No data returned");
			}
		});
	});

	describe("ApiError class", () => {
		it("should create ApiError with status and statusText", () => {
			const error = new ApiError(404, "Not Found", {
				message: "Resource not found",
			});
			expect(error).toBeInstanceOf(Error);
			expect(error).toBeInstanceOf(ApiError);
			expect(error.status).toBe(404);
			expect(error.statusText).toBe("Not Found");
			expect(error.data).toEqual({ message: "Resource not found" });
			expect(error.message).toBe("API Error 404: Not Found");
			expect(error.name).toBe("ApiError");
		});

		it("should create ApiError without data", () => {
			const error = new ApiError(500, "Internal Server Error");
			expect(error.status).toBe(500);
			expect(error.statusText).toBe("Internal Server Error");
			expect(error.data).toBeUndefined();
		});
	});

	describe("interceptors", () => {
		it("should have use method for interceptors", () => {
			expect(apiClient.use).toBeDefined();
			expect(typeof apiClient.use).toBe("function");
		});

		it("should call use method", () => {
			const interceptor = {
				onRequest: vi.fn(async ({ request }) => request),
				onResponse: vi.fn(async ({ response }) => response),
			};

			apiClient.use(interceptor);
			expect(apiClient.use).toHaveBeenCalledWith(interceptor);
		});
	});
});
