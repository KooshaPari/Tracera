/**
 * Tests for Search API
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchSearchResults } from "@/api/search";

// Mock endpoints
vi.mock("@/api/endpoints", () => ({
	searchApi: {
		search: vi.fn(),
	},
}));

import { searchApi } from "@/api/endpoints";

describe("Search API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchSearchResults", () => {
		it("should fetch search results", async () => {
			const mockResult = {
				items: [],
				total: 0,
				query: "test",
				page: 1,
				per_page: 10,
			};
			vi.mocked(searchApi.search).mockResolvedValue(mockResult);

			const result = await fetchSearchResults({ q: "test" });
			expect(result).toEqual(mockResult);
			expect(searchApi.search).toHaveBeenCalledWith({ q: "test" });
		});

		it("should handle complex search queries", async () => {
			const mockResult = {
				items: [],
				total: 0,
				query: "complex search",
				page: 1,
				per_page: 20,
			};
			vi.mocked(searchApi.search).mockResolvedValue(mockResult);

			const query = {
				q: "complex search",
				type: "item",
				projectId: "proj-1",
				limit: 20,
				offset: 0,
			};
			const result = await fetchSearchResults(query);
			expect(result).toEqual(mockResult);
			expect(searchApi.search).toHaveBeenCalledWith(query);
		});
	});
});
