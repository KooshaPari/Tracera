// equivalenceIO.test.ts - Tests for equivalence import/export utilities

import { describe, it, expect, beforeEach } from "vitest";
import type {
	EquivalenceLink,
	CanonicalConcept,
	CanonicalProjection,
} from "@tracertm/types";
import {
	serializeToJSON,
	deserializeFromJSON,
	serializeToCSV,
	deserializeLinksFromCSV,
	deserializeConceptsFromCSV,
	deserializeProjectionsFromCSV,
	validateExportPackage,
	validateImportOptions,
	mergeExportPackages,
	createExportSummary,
} from "../components/graph/utils/equivalenceIO";
import type {
	EquivalenceExportPackage,
	EquivalenceImportOptions,
} from "../components/graph/utils/equivalenceIO";

// =============================================================================
// TEST DATA
// =============================================================================

const mockEquivalenceLink: EquivalenceLink = {
	id: "link-1",
	projectId: "proj-1",
	sourceItemId: "item-1",
	targetItemId: "item-2",
	equivalenceType: "same_as",
	confidence: 0.95,
	strategies: [
		{
			strategy: "manual_link",
			confidence: 0.95,
			details: "User confirmed equivalence",
			detectedAt: "2024-01-15T10:00:00Z",
		},
	],
	canonicalId: "canon-1",
	status: "confirmed",
	confirmedBy: "user-1",
	confirmedAt: "2024-01-15T10:05:00Z",
	createdAt: "2024-01-15T10:00:00Z",
	updatedAt: "2024-01-15T10:05:00Z",
};

const mockCanonicalConcept: CanonicalConcept = {
	id: "canon-1",
	projectId: "proj-1",
	name: "User Authentication",
	slug: "user-authentication",
	description: "The concept of authenticating users in the system",
	domain: "security",
	category: "identity",
	tags: ["security", "auth", "identity"],
	confidence: 0.9,
	source: "manual",
	projectionCount: 3,
	createdAt: "2024-01-15T10:00:00Z",
	updatedAt: "2024-01-15T10:00:00Z",
	version: 1,
};

const mockCanonicalProjection: CanonicalProjection = {
	id: "proj-1",
	canonicalId: "canon-1",
	itemId: "item-1",
	projectId: "proj-1",
	perspective: "technical",
	confidence: 0.95,
	strategy: "manual_link",
	isConfirmed: true,
	isRejected: false,
	confirmedBy: "user-1",
	confirmedAt: "2024-01-15T10:05:00Z",
	createdAt: "2024-01-15T10:00:00Z",
	updatedAt: "2024-01-15T10:05:00Z",
};

const mockExportPackage: EquivalenceExportPackage = {
	version: "1.0",
	exportedAt: "2024-01-15T10:00:00Z",
	projectId: "proj-1",
	exportedBy: "user-1",
	metadata: {
		totalLinks: 1,
		totalConcepts: 1,
		totalProjections: 1,
		confidence: {
			min: 0.9,
			max: 0.95,
			average: 0.925,
		},
	},
	equivalenceLinks: [mockEquivalenceLink],
	canonicalConcepts: [mockCanonicalConcept],
	canonicalProjections: [mockCanonicalProjection],
};

// =============================================================================
// SERIALIZATION TESTS
// =============================================================================

describe("equivalenceIO - Serialization", () => {
	describe("serializeToJSON", () => {
		it("should serialize package to JSON string", () => {
			const json = serializeToJSON(mockExportPackage);
			expect(typeof json).toBe("string");
			expect(json).toContain('"version": "1.0"');
			expect(json).toContain('"User Authentication"');
		});

		it("should produce valid JSON that can be parsed", () => {
			const json = serializeToJSON(mockExportPackage);
			const parsed = JSON.parse(json);
			expect(parsed.version).toBe("1.0");
			expect(parsed.projectId).toBe("proj-1");
			expect(parsed.equivalenceLinks).toHaveLength(1);
		});

		it("should preserve nested structures", () => {
			const json = serializeToJSON(mockExportPackage);
			const parsed = JSON.parse(json);
			expect(parsed.equivalenceLinks[0].strategies).toHaveLength(1);
			expect(parsed.canonicalConcepts[0].tags).toHaveLength(3);
		});
	});

	describe("deserializeFromJSON", () => {
		it("should deserialize valid JSON to package", () => {
			const json = serializeToJSON(mockExportPackage);
			const deserialized = deserializeFromJSON(json);
			expect(deserialized.version).toBe("1.0");
			expect(deserialized.projectId).toBe("proj-1");
		});

		it("should validate schema during deserialization", () => {
			const invalidJSON = JSON.stringify({
				version: "1.0",
				exportedAt: "2024-01-15T10:00:00Z",
				// Missing required fields
				equivalenceLinks: [],
				canonicalConcepts: [],
				canonicalProjections: [],
			});

			expect(() => deserializeFromJSON(invalidJSON)).toThrow();
		});

		it("should preserve data integrity through serialize/deserialize cycle", () => {
			const json = serializeToJSON(mockExportPackage);
			const deserialized = deserializeFromJSON(json);
			expect(deserialized.equivalenceLinks[0].confidence).toBe(0.95);
			expect(deserialized.canonicalConcepts[0].name).toBe(
				"User Authentication",
			);
		});
	});

	describe("serializeToCSV", () => {
		it("should serialize to CSV with proper headers", () => {
			const csv = serializeToCSV(mockExportPackage);
			expect(csv.links).toContain("id,projectId,sourceItemId");
			expect(csv.concepts).toContain("id,projectId,name,slug");
			expect(csv.projections).toContain("id,canonicalId,itemId,projectId");
		});

		it("should escape special characters in CSV", () => {
			const packageWithSpecial: EquivalenceExportPackage = {
				...mockExportPackage,
				canonicalConcepts: [
					{
						...mockCanonicalConcept,
						description: 'Contains "quotes" and, commas',
					},
				],
			};

			const csv = serializeToCSV(packageWithSpecial);
			expect(csv.concepts).toContain('"Contains ""quotes"" and, commas"');
		});

		it("should handle empty arrays gracefully", () => {
			const emptyPackage: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [],
				canonicalConcepts: [],
				canonicalProjections: [],
			};

			const csv = serializeToCSV(emptyPackage);
			expect(csv.links).toContain("id,projectId");
			expect(csv.concepts).toContain("id,projectId");
			expect(csv.projections).toContain("id,canonicalId");
		});
	});

	describe("CSV deserialization", () => {
		it("should deserialize links from CSV", () => {
			const csv = serializeToCSV(mockExportPackage);
			const links = deserializeLinksFromCSV(csv.links);
			expect(links).toHaveLength(1);
			expect(links[0].id).toBe("link-1");
			expect(links[0].confidence).toBe(0.95);
		});

		it("should deserialize concepts from CSV", () => {
			const csv = serializeToCSV(mockExportPackage);
			const concepts = deserializeConceptsFromCSV(csv.concepts);
			expect(concepts).toHaveLength(1);
			expect(concepts[0].name).toBe("User Authentication");
			expect(concepts[0].tags).toEqual(["security", "auth", "identity"]);
		});

		it("should deserialize projections from CSV", () => {
			const csv = serializeToCSV(mockExportPackage);
			const projections = deserializeProjectionsFromCSV(csv.projections);
			expect(projections).toHaveLength(1);
			expect(projections[0].itemId).toBe("item-1");
			expect(projections[0].isConfirmed).toBe(true);
		});

		it("should handle CSV with escaped values", () => {
			// Serialize then deserialize to ensure consistency
			const conceptWithSpecial: CanonicalConcept = {
				...mockCanonicalConcept,
				id: "canon-2",
				description: 'Test with "quotes"',
			};

			const pkg: EquivalenceExportPackage = {
				...mockExportPackage,
				canonicalConcepts: [conceptWithSpecial],
			};

			const csv = serializeToCSV(pkg);
			const concepts = deserializeConceptsFromCSV(csv.concepts);
			expect(concepts).toHaveLength(1);
			expect(concepts[0].description).toContain("Test");
		});
	});
});

// =============================================================================
// VALIDATION TESTS
// =============================================================================

describe("equivalenceIO - Validation", () => {
	describe("validateExportPackage", () => {
		it("should validate correct package", () => {
			const result = validateExportPackage(mockExportPackage);
			expect(result.valid).toBe(true);
			expect(result.errors).toHaveLength(0);
		});

		it("should reject invalid package with missing fields", () => {
			const invalid = { version: "1.0" };
			const result = validateExportPackage(invalid);
			expect(result.valid).toBe(false);
			expect(result.errors.length).toBeGreaterThan(0);
		});

		it("should reject invalid confidence values", () => {
			const invalid: any = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						confidence: 1.5, // Out of range
					},
				],
			};

			const result = validateExportPackage(invalid);
			expect(result.valid).toBe(false);
		});

		it("should validate arrays of items", () => {
			const result = validateExportPackage(mockExportPackage);
			expect(result.valid).toBe(true);
		});
	});

	describe("validateImportOptions", () => {
		it("should validate correct options", () => {
			const options: EquivalenceImportOptions = {
				mode: "merge",
				conflictResolution: "skip",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: true,
			};

			const result = validateImportOptions(options);
			expect(result.valid).toBe(true);
		});

		it("should reject invalid mode", () => {
			const options = { mode: "invalid" };
			const result = validateImportOptions(options);
			expect(result.valid).toBe(false);
		});

		it("should apply default values", () => {
			const options = { mode: "replace" as const };
			const result = validateImportOptions(options);
			expect(result.valid).toBe(true);
		});
	});
});

// =============================================================================
// MERGE TESTS
// =============================================================================

describe("equivalenceIO - Merging", () => {
	describe("mergeExportPackages", () => {
		it("should merge packages in merge mode", () => {
			const existing: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						id: "link-existing",
					},
				],
			};

			const incoming: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						id: "link-new",
					},
				],
			};

			const options: EquivalenceImportOptions = {
				mode: "merge",
				conflictResolution: "skip",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: false,
			};

			const merged = mergeExportPackages(existing, incoming, options);
			expect(merged.equivalenceLinks).toHaveLength(2);
		});

		it("should replace in replace mode", () => {
			const existing: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [mockEquivalenceLink],
			};

			const incoming: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						id: "link-new",
					},
				],
			};

			const options: EquivalenceImportOptions = {
				mode: "replace",
				conflictResolution: "skip",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: false,
			};

			const merged = mergeExportPackages(existing, incoming, options);
			expect(merged.equivalenceLinks).toHaveLength(1);
			expect(merged.equivalenceLinks[0].id).toBe("link-new");
		});

		it("should skip conflicts when configured", () => {
			const existing: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [mockEquivalenceLink],
			};

			const incoming: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						confidence: 0.85, // Different confidence
					},
				],
			};

			const options: EquivalenceImportOptions = {
				mode: "merge",
				conflictResolution: "skip",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: false,
			};

			const merged = mergeExportPackages(existing, incoming, options);
			expect(merged.equivalenceLinks[0].confidence).toBe(0.95); // Original value kept
		});

		it("should overwrite conflicts when configured", () => {
			const existing: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [mockEquivalenceLink],
			};

			const incoming: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					{
						...mockEquivalenceLink,
						confidence: 0.85,
					},
				],
			};

			const options: EquivalenceImportOptions = {
				mode: "merge",
				conflictResolution: "overwrite",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: false,
			};

			const merged = mergeExportPackages(existing, incoming, options);
			expect(merged.equivalenceLinks[0].confidence).toBe(0.85); // Updated value
		});

		it("should update project IDs when configured", () => {
			const options: EquivalenceImportOptions = {
				mode: "merge",
				conflictResolution: "skip",
				validateReferences: true,
				preserveTimestamps: false,
				updateProjectId: true,
				targetProjectId: "proj-new",
			};

			const merged = mergeExportPackages(
				mockExportPackage,
				mockExportPackage,
				options,
			);

			expect(merged.equivalenceLinks[0].projectId).toBe("proj-new");
			expect(merged.canonicalConcepts[0].projectId).toBe("proj-new");
			expect(merged.canonicalProjections[0].projectId).toBe("proj-new");
		});
	});
});

// =============================================================================
// SUMMARY TESTS
// =============================================================================

describe("equivalenceIO - Summary", () => {
	describe("createExportSummary", () => {
		it("should create summary with correct counts", () => {
			const summary = createExportSummary(mockExportPackage);
			expect(summary.totalLinks).toBe(1);
			expect(summary.totalConcepts).toBe(1);
			expect(summary.totalProjections).toBe(1);
		});

		it("should calculate confidence stats", () => {
			const summary = createExportSummary(mockExportPackage);
			expect(summary.confidenceStats.min).toBeLessThanOrEqual(
				summary.confidenceStats.average,
			);
			expect(summary.confidenceStats.average).toBeLessThanOrEqual(
				summary.confidenceStats.max,
			);
		});

		it("should break down by domain", () => {
			const summary = createExportSummary(mockExportPackage);
			expect(summary.domainBreakdown.security).toBe(1);
		});

		it("should break down by strategy", () => {
			const summary = createExportSummary(mockExportPackage);
			expect(summary.strategyBreakdown.manual_link).toBe(1);
		});

		it("should count link statuses", () => {
			const summary = createExportSummary(mockExportPackage);
			expect(summary.confirmedCount).toBe(1);
			expect(summary.suggestedCount).toBe(0);
			expect(summary.rejectedCount).toBe(0);
		});

		it("should handle multiple items with different statuses", () => {
			const pkg: EquivalenceExportPackage = {
				...mockExportPackage,
				equivalenceLinks: [
					mockEquivalenceLink,
					{ ...mockEquivalenceLink, id: "link-2", status: "suggested" },
					{
						...mockEquivalenceLink,
						id: "link-3",
						status: "rejected",
					},
				],
			};

			const summary = createExportSummary(pkg);
			expect(summary.confirmedCount).toBe(1);
			expect(summary.suggestedCount).toBe(1);
			expect(summary.rejectedCount).toBe(1);
		});
	});
});
