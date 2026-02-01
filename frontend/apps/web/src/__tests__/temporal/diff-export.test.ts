/**
 * Tests for diff export utilities
 */

import type { VersionDiff } from "@repo/types";
import { describe, expect, it } from "vitest";
import { exportDiff } from "@/lib/diff-export";

const mockDiff: VersionDiff = {
	versionA: "v1",
	versionB: "v2",
	versionANumber: 1,
	versionBNumber: 2,
	added: [
		{
			itemId: "item3",
			type: "feature",
			title: "New Feature",
			changeType: "added",
			significance: "major",
		},
	],
	removed: [
		{
			itemId: "item2",
			type: "bug",
			title: "Old Bug",
			changeType: "removed",
			significance: "minor",
		},
	],
	modified: [
		{
			itemId: "item1",
			type: "requirement",
			title: "Modified Requirement",
			changeType: "modified",
			significance: "moderate",
			fieldChanges: [
				{
					field: "status",
					oldValue: "open",
					newValue: "closed",
					changeType: "modified",
				},
				{
					field: "priority",
					oldValue: "low",
					newValue: "high",
					changeType: "modified",
				},
			],
		},
	],
	unchanged: 5,
	stats: {
		totalChanges: 3,
		addedCount: 1,
		removedCount: 1,
		modifiedCount: 1,
		unchangedCount: 5,
	},
	computedAt: new Date().toISOString(),
};

describe("exportDiff", () => {
	describe("JSON export", () => {
		it("should export diff as JSON", async () => {
			const result = await exportDiff(mockDiff, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			expect(result.mimeType).toBe("application/json");
			expect(result.filename).toMatch(/\.json$/);

			const data = JSON.parse(result.content as string);
			expect(data.metadata.versionA).toBe("v1");
			expect(data.metadata.versionB).toBe("v2");
			expect(data.statistics.totalChanges).toBe(3);
			expect(data.added).toHaveLength(1);
			expect(data.removed).toHaveLength(1);
			expect(data.modified).toHaveLength(1);
		});

		it("should include field changes in JSON export when requested", async () => {
			const result = await exportDiff(mockDiff, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			const data = JSON.parse(result.content as string);
			const modifiedItem = data.modified[0];
			expect(modifiedItem.fieldChanges).toHaveLength(2);
			expect(modifiedItem.fieldChanges[0].field).toBe("status");
		});
	});

	describe("CSV export", () => {
		it("should export diff as CSV", async () => {
			const result = await exportDiff(mockDiff, {
				format: "csv",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			expect(result.mimeType).toBe("text/csv");
			expect(result.filename).toMatch(/\.csv$/);
			expect(result.content).toContain("Item ID,Title,Type");
			expect(result.content).toContain("New Feature");
			expect(result.content).toContain("Old Bug");
		});

		it("should handle CSV field escaping", async () => {
			const diffWithCommas: VersionDiff = {
				...mockDiff,
				added: [
					{
						itemId: "item1",
						type: "feature",
						title: 'Feature with "quotes" and, commas',
						changeType: "added",
						significance: "major",
					},
				],
			};

			const result = await exportDiff(diffWithCommas, {
				format: "csv",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			const content = result.content as string;
			expect(content).toContain('Feature with "quotes" and, commas');
		});
	});

	describe("Markdown export", () => {
		it("should export diff as Markdown", async () => {
			const result = await exportDiff(mockDiff, {
				format: "markdown",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			expect(result.mimeType).toBe("text/markdown");
			expect(result.filename).toMatch(/\.md$/);
			expect(result.content).toContain("# Version Diff Report");
			expect(result.content).toContain("## Added Items");
			expect(result.content).toContain("## Removed Items");
			expect(result.content).toContain("## Modified Items");
		});

		it("should include statistics in Markdown", async () => {
			const result = await exportDiff(mockDiff, {
				format: "markdown",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			const content = result.content as string;
			expect(content).toContain("## Statistics");
			expect(content).toContain("| Added | 1 |");
			expect(content).toContain("| Removed | 1 |");
			expect(content).toContain("| Modified | 1 |");
		});

		it("should include field changes in Markdown when requested", async () => {
			const result = await exportDiff(mockDiff, {
				format: "markdown",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			const content = result.content as string;
			expect(content).toContain("#### Field Changes");
			expect(content).toContain("status");
			expect(content).toContain("priority");
		});
	});

	describe("HTML export", () => {
		it("should export diff as HTML", async () => {
			const result = await exportDiff(mockDiff, {
				format: "html",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			expect(result.mimeType).toBe("text/html");
			expect(result.filename).toMatch(/\.html$/);
			expect(result.content).toContain("<!DOCTYPE html>");
			expect(result.content).toContain("Version Diff Report");
		});

		it("should include statistics in HTML", async () => {
			const result = await exportDiff(mockDiff, {
				format: "html",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			const content = result.content as string;
			expect(content).toContain("1");
			expect(content).toContain("Added");
			expect(content).toContain("Removed");
		});

		it("should format tables properly in HTML", async () => {
			const result = await exportDiff(mockDiff, {
				format: "html",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			const content = result.content as string;
			expect(content).toContain("<table>");
			expect(content).toContain("<thead>");
			expect(content).toContain("<tbody>");
		});
	});

	describe("Filename generation", () => {
		it("should generate correct filename with date", async () => {
			const result = await exportDiff(mockDiff, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			expect(result.filename).toMatch(/diff-v1-v2-\d{4}-\d{2}-\d{2}\.json/);
		});
	});

	describe("Unsupported format", () => {
		it("should throw error for unsupported format", async () => {
			await expect(
				exportDiff(mockDiff, {
					format: "xml" as any,
					includeUnchanged: false,
					includeFieldChanges: false,
				}),
			).rejects.toThrow("Unsupported export format");
		});
	});

	describe("Empty diff handling", () => {
		it("should handle empty diff", async () => {
			const emptyDiff: VersionDiff = {
				...mockDiff,
				added: [],
				removed: [],
				modified: [],
				unchanged: 10,
				stats: {
					totalChanges: 0,
					addedCount: 0,
					removedCount: 0,
					modifiedCount: 0,
					unchangedCount: 10,
				},
			};

			const result = await exportDiff(emptyDiff, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			const data = JSON.parse(result.content as string);
			expect(data.statistics.totalChanges).toBe(0);
		});
	});

	describe("Large dataset handling", () => {
		it("should handle large diff efficiently", async () => {
			const largeItems = Array.from({ length: 1000 }, (_, i) => ({
				itemId: `item${i}`,
				type: "feature",
				title: `Feature ${i}`,
				changeType: "added" as const,
				significance: "minor" as const,
			}));

			const largeDiff: VersionDiff = {
				...mockDiff,
				added: largeItems,
				stats: {
					totalChanges: 1000,
					addedCount: 1000,
					removedCount: 0,
					modifiedCount: 0,
					unchangedCount: 0,
				},
			};

			const result = await exportDiff(largeDiff, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: false,
			});

			expect(result.content).toBeTruthy();
			const data = JSON.parse(result.content as string);
			expect(data.added).toHaveLength(1000);
		});
	});

	describe("Field change serialization", () => {
		it("should properly serialize complex values", async () => {
			const diffWithComplexValues: VersionDiff = {
				...mockDiff,
				modified: [
					{
						itemId: "item1",
						type: "config",
						title: "Configuration",
						changeType: "modified",
						significance: "major",
						fieldChanges: [
							{
								field: "settings",
								oldValue: { timeout: 5000, retries: 3 },
								newValue: { timeout: 10000, retries: 5 },
								changeType: "modified",
							},
							{
								field: "tags",
								oldValue: ["v1", "stable"],
								newValue: ["v2", "stable", "beta"],
								changeType: "modified",
							},
						],
					},
				],
			};

			const result = await exportDiff(diffWithComplexValues, {
				format: "json",
				includeUnchanged: false,
				includeFieldChanges: true,
			});

			const data = JSON.parse(result.content as string);
			expect(data.modified[0].fieldChanges[0].oldValue.timeout).toBe(5000);
			expect(data.modified[0].fieldChanges[1].newValue).toContain("v2");
		});
	});
});
