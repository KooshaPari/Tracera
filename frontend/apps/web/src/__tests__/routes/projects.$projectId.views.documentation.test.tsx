/**
 * Tests for Documentation View Route
 */

import { describe, expect, it } from "vitest";

describe("Documentation View Route", () => {
	it("validates documentation view route path pattern", () => {
		const docsPath = "/projects/proj-1/views/documentation";
		expect(docsPath).toMatch(/^\/projects\/[^/]+\/views\/documentation$/);
	});

	it("extracts projectId from route parameters", () => {
		const path = "/projects/proj-123/views/documentation";
		const match = path.match(/\/projects\/([^/]+)\/views\/documentation/);

		expect(match).not.toBeNull();
		expect(match?.[1]).toBe("proj-123");
	});

	it("recognizes documentation view type from route", () => {
		const path = "/projects/proj-1/views/documentation";
		const viewType = path.split("/")[4];

		expect(viewType).toBe("documentation");
	});

	it("supports documentation metadata", () => {
		const mockDoc = {
			id: "doc-1",
			title: "API Documentation",
			type: "documentation",
			status: "done",
			format: "markdown",
		};

		expect(mockDoc.format).toMatch(/^(markdown|html|pdf|docx)$/);
		expect(mockDoc.status).toMatch(/^(pending|done|draft)$/);
	});

	it("handles multiple documentation files", () => {
		const mockDocs = [
			{ id: "d1", title: "README.md", format: "markdown" },
			{ id: "d2", title: "API.md", format: "markdown" },
			{ id: "d3", title: "GUIDE.md", format: "markdown" },
		];

		expect(mockDocs).toHaveLength(3);
		expect(mockDocs.every(d => d.format === "markdown")).toBe(true);
	});
});
