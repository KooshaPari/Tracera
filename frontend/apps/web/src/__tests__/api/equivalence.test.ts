import { describe, expect, it } from "vitest";
import { equivalenceQueryKeys } from "../../api/equivalence";
import type {
	ConfirmEquivalenceInput,
	DetectEquivalencesInput,
	EquivalenceLink,
	RejectEquivalenceInput,
} from "../../api/equivalence";

describe("equivalence API hooks", () => {
	describe("queryKeys", () => {
		it("should generate correct query key for all equivalences", () => {
			const key = equivalenceQueryKeys.all;
			expect(key).toEqual(["equivalences"]);
		});

		it("should generate correct query key for list with projectId and status", () => {
			const key = equivalenceQueryKeys.list("project-1", "pending");
			expect(key).toEqual(["equivalences", "list", "project-1", "pending"]);
		});

		it("should generate correct query key for list with projectId only", () => {
			const key = equivalenceQueryKeys.list("project-1");
			expect(key).toEqual(["equivalences", "list", "project-1", undefined]);
		});

		it("should generate correct query key for detail", () => {
			const key = equivalenceQueryKeys.detail("equiv-1");
			expect(key).toEqual(["equivalences", "detail", "equiv-1"]);
		});
	});

	describe("EquivalenceLink type", () => {
		it("should validate equivalence link structure", () => {
			const link: EquivalenceLink = {
				confidence: 0.88,
				createdAt: "2024-01-01T00:00:00Z",
				id: "equiv-1",
				itemId1: "item-1",
				itemId2: "item-2",
				similarity: 0.95,
				status: "pending",
			};

			expect(link.id).toBeDefined();
			expect(link.itemId1).toBeDefined();
			expect(link.itemId2).toBeDefined();
			expect(link.similarity).toBeGreaterThan(0);
			expect(link.confidence).toBeGreaterThan(0);
			expect(["pending", "confirmed", "rejected"]).toContain(link.status);
		});

		it("should allow optional confirmedAt field", () => {
			const link: EquivalenceLink = {
				confidence: 0.88,
				confirmedAt: "2024-01-02T00:00:00Z",
				createdAt: "2024-01-01T00:00:00Z",
				id: "equiv-1",
				itemId1: "item-1",
				itemId2: "item-2",
				similarity: 0.95,
				status: "confirmed",
			};

			expect(link.confirmedAt).toBeDefined();
		});
	});

	describe("Input types", () => {
		it("should validate DetectEquivalencesInput", () => {
			const input: DetectEquivalencesInput = {
				projectId: "project-1",
				threshold: 0.8,
			};

			expect(input.projectId).toBeDefined();
			expect(input.threshold).toBeDefined();
		});

		it("should validate ConfirmEquivalenceInput", () => {
			const input: ConfirmEquivalenceInput = {
				comment: "Confirmed as equivalent",
				equivalenceId: "equiv-1",
			};

			expect(input.equivalenceId).toBeDefined();
		});

		it("should validate RejectEquivalenceInput", () => {
			const input: RejectEquivalenceInput = {
				equivalenceId: "equiv-1",
				reason: "False positive",
			};

			expect(input.equivalenceId).toBeDefined();
		});
	});

	describe("Query key hierarchies", () => {
		it("should create consistent list query keys", () => {
			const key1 = equivalenceQueryKeys.list("project-1");
			const key2 = equivalenceQueryKeys.list("project-2");

			expect(key1).not.toEqual(key2);
			expect(key1[0]).toEqual(key2[0]); // Same root
		});

		it("should invalidate all lists when using lists key", () => {
			const listsKey = equivalenceQueryKeys.lists();
			const specificKey = equivalenceQueryKeys.list("project-1");

			expect(listsKey).toEqual(["equivalences", "list"]);
			expect(specificKey.slice(0, 2)).toEqual(listsKey);
		});
	});
});
