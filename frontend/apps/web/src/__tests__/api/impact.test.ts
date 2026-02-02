/**
 * Tests for Impact API (re-exports from graph)
 */

import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchDependencyAnalysis, fetchImpactAnalysis } from "../../api/impact";

// Mock endpoints
vi.mock("../../api/endpoints", () => ({
	graphApi: {
		getImpactAnalysis: vi.fn(),
		getDependencyAnalysis: vi.fn(),
	},
}));

import { graphApi } from "../../api/endpoints";

describe("Impact API", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe("fetchImpactAnalysis", () => {
		it("should fetch impact analysis", async () => {
			const mockAnalysis = {
				item_id: "item-1",
				affected_items: [],
				affected_count: 0,
				depth: 5,
			};
			vi.mocked(graphApi.getImpactAnalysis).mockResolvedValue(mockAnalysis);

			const result = await fetchImpactAnalysis("item-1", 5);
			expect(result).toEqual(mockAnalysis);
			expect(graphApi.getImpactAnalysis).toHaveBeenCalledWith("item-1", 5);
		});
	});

	describe("fetchDependencyAnalysis", () => {
		it("should fetch dependency analysis", async () => {
			const mockAnalysis = {
				item_id: "item-1",
				dependencies: [],
				dependency_count: 0,
				depth: 5,
			};
			vi.mocked(graphApi.getDependencyAnalysis).mockResolvedValue(mockAnalysis);

			const result = await fetchDependencyAnalysis("item-1", 5);
			expect(result).toEqual(mockAnalysis);
			expect(graphApi.getDependencyAnalysis).toHaveBeenCalledWith("item-1", 5);
		});
	});
});
