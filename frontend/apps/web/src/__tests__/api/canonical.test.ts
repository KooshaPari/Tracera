import { describe, it, expect, beforeEach, vi } from "vitest";
import {
	canonicalQueryKeys,
	type CanonicalConcept,
	type CanonicalProjection,
	type PivotTarget,
	type CreateCanonicalConceptInput,
	type UpdateCanonicalConceptInput,
} from "../../api/canonical";

describe("canonical API hooks", () => {
	describe("queryKeys", () => {
		it("should generate correct query key for all canonical", () => {
			const key = canonicalQueryKeys.all;
			expect(key).toEqual(["canonical"]);
		});

		it("should generate correct query key for list", () => {
			const key = canonicalQueryKeys.list("project-1");
			expect(key).toEqual(["canonical", "list", "project-1"]);
		});

		it("should generate correct query key for detail", () => {
			const key = canonicalQueryKeys.detail("concept-1");
			expect(key).toEqual(["canonical", "detail", "concept-1"]);
		});

		it("should generate correct query key for projections", () => {
			const key = canonicalQueryKeys.projections("concept-1");
			expect(key).toEqual(["canonical", "projections", "concept-1"]);
		});

		it("should generate correct query key for pivots", () => {
			const key = canonicalQueryKeys.pivots("item-1");
			expect(key).toEqual(["canonical", "pivots", "item-1"]);
		});
	});

	describe("CanonicalConcept type", () => {
		it("should validate canonical concept structure", () => {
			const concept: CanonicalConcept = {
				id: "concept-1",
				projectId: "project-1",
				name: "User Authentication",
				description: "Core authentication concept",
				category: "security",
				properties: { requiresMFA: true, sessionTimeout: 3600 },
				itemCount: 5,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-02T00:00:00Z",
			};

			expect(concept.id).toBeDefined();
			expect(concept.projectId).toBeDefined();
			expect(concept.name).toBeDefined();
			expect(concept.properties).toBeDefined();
			expect(concept.itemCount).toBeGreaterThanOrEqual(0);
		});

		it("should allow optional description and category", () => {
			const concept: CanonicalConcept = {
				id: "concept-1",
				projectId: "project-1",
				name: "User Authentication",
				properties: {},
				itemCount: 0,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			expect(concept.description).toBeUndefined();
			expect(concept.category).toBeUndefined();
		});
	});

	describe("CanonicalProjection type", () => {
		it("should validate canonical projection structure", () => {
			const projection: CanonicalProjection = {
				id: "proj-1",
				conceptId: "concept-1",
				itemId: "item-1",
				confidence: 0.92,
				mappedProperties: { name: "mapped_name", type: "mapped_type" },
				createdAt: "2024-01-01T00:00:00Z",
			};

			expect(projection.id).toBeDefined();
			expect(projection.conceptId).toBeDefined();
			expect(projection.itemId).toBeDefined();
			expect(projection.confidence).toBeGreaterThan(0);
			expect(projection.confidence).toBeLessThanOrEqual(1);
		});
	});

	describe("PivotTarget type", () => {
		it("should validate pivot target structure", () => {
			const pivot: PivotTarget = {
				itemId: "item-1",
				conceptId: "concept-1",
				confidence: 0.85,
				distance: 2,
			};

			expect(pivot.itemId).toBeDefined();
			expect(pivot.conceptId).toBeDefined();
			expect(pivot.confidence).toBeGreaterThan(0);
			expect(pivot.distance).toBeGreaterThanOrEqual(0);
		});
	});

	describe("Input types", () => {
		it("should validate CreateCanonicalConceptInput", () => {
			const input: CreateCanonicalConceptInput = {
				projectId: "project-1",
				name: "New Concept",
				description: "A new canonical concept",
				category: "architecture",
				properties: { version: "1.0" },
			};

			expect(input.projectId).toBeDefined();
			expect(input.name).toBeDefined();
		});

		it("should validate UpdateCanonicalConceptInput", () => {
			const input: UpdateCanonicalConceptInput = {
				name: "Updated Concept",
				properties: { updated: true },
			};

			expect(input.name).toBeDefined();
		});
	});

	describe("Query key hierarchies", () => {
		it("should create consistent detail query keys", () => {
			const key1 = canonicalQueryKeys.detail("concept-1");
			const key2 = canonicalQueryKeys.detail("concept-2");

			expect(key1).not.toEqual(key2);
			expect(key1.slice(0, 2)).toEqual(key2.slice(0, 2)); // Same prefix
		});

		it("should create consistent projection query keys", () => {
			const key1 = canonicalQueryKeys.projections("concept-1");
			const key2 = canonicalQueryKeys.projections("concept-2");

			expect(key1).not.toEqual(key2);
			expect(key1[1]).toEqual(key2[1]); // Same operation type
		});

		it("should create independent pivot query keys", () => {
			const key1 = canonicalQueryKeys.pivots("item-1");
			const key2 = canonicalQueryKeys.pivots("item-2");

			expect(key1).not.toEqual(key2);
			expect(key1[1]).toEqual(key2[1]); // Same operation type
		});
	});
});
