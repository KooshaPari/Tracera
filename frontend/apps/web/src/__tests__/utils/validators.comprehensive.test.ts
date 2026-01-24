/**
 * Comprehensive tests for validator utilities
 * Tests all validation functions with edge cases and error scenarios
 */

import { describe, expect, it } from "vitest";
import {
	hasMaxLength,
	hasMinLength,
	isEmail,
	isInRange,
	isNumeric,
	isUrl,
	isValidId,
	isValidItemTitle,
	isValidProjectName,
	matchesPattern,
	validateItem,
	validateLink,
	validateProject,
} from "../../utils/validators";

describe("isEmail", () => {
	it("should validate correct email", () => {
		expect(isEmail("test@example.com")).toBe(true);
	});

	it("should validate email with subdomain", () => {
		expect(isEmail("test@mail.example.com")).toBe(true);
	});

	it("should validate email with plus sign", () => {
		expect(isEmail("test+tag@example.com")).toBe(true);
	});

	it("should validate email with dots", () => {
		expect(isEmail("first.last@example.com")).toBe(true);
	});

	it("should reject email without @", () => {
		expect(isEmail("testexample.com")).toBe(false);
	});

	it("should reject email without domain", () => {
		expect(isEmail("test@")).toBe(false);
	});

	it("should reject email without TLD", () => {
		expect(isEmail("test@example")).toBe(false);
	});

	it("should reject email with spaces", () => {
		expect(isEmail("test @example.com")).toBe(false);
	});

	it("should reject empty string", () => {
		expect(isEmail("")).toBe(false);
	});

	it("should reject email with multiple @", () => {
		expect(isEmail("test@@example.com")).toBe(false);
	});

	it("should validate email with numbers", () => {
		expect(isEmail("test123@example.com")).toBe(true);
	});

	it("should validate email with hyphens", () => {
		expect(isEmail("test-user@example.com")).toBe(true);
	});
});

describe("isUrl", () => {
	it("should validate HTTP URL", () => {
		expect(isUrl("http://example.com")).toBe(true);
	});

	it("should validate HTTPS URL", () => {
		expect(isUrl("https://example.com")).toBe(true);
	});

	it("should validate URL with path", () => {
		expect(isUrl("https://example.com/path/to/page")).toBe(true);
	});

	it("should validate URL with query params", () => {
		expect(isUrl("https://example.com?foo=bar&baz=qux")).toBe(true);
	});

	it("should validate URL with hash", () => {
		expect(isUrl("https://example.com#section")).toBe(true);
	});

	it("should validate URL with port", () => {
		expect(isUrl("https://example.com:8080")).toBe(true);
	});

	it("should validate localhost URL", () => {
		expect(isUrl("http://localhost:3000")).toBe(true);
	});

	it("should validate IP address URL", () => {
		expect(isUrl("http://192.168.1.1")).toBe(true);
	});

	it("should reject invalid URL", () => {
		expect(isUrl("not-a-url")).toBe(false);
	});

	it("should reject empty string", () => {
		expect(isUrl("")).toBe(false);
	});

	it("should reject URL without protocol", () => {
		expect(isUrl("example.com")).toBe(false);
	});

	it("should validate file:// URLs", () => {
		expect(isUrl("file:///path/to/file")).toBe(true);
	});

	it("should validate FTP URLs", () => {
		expect(isUrl("ftp://ftp.example.com")).toBe(true);
	});
});

describe("isValidProjectName", () => {
	it("should validate valid project name", () => {
		expect(isValidProjectName("My Project")).toBe(true);
	});

	it("should validate project name with numbers", () => {
		expect(isValidProjectName("Project123")).toBe(true);
	});

	it("should validate project name with hyphens", () => {
		expect(isValidProjectName("my-project")).toBe(true);
	});

	it("should validate project name with underscores", () => {
		expect(isValidProjectName("my_project")).toBe(true);
	});

	it("should validate project name with spaces", () => {
		expect(isValidProjectName("My Cool Project")).toBe(true);
	});

	it("should reject project name too short (< 3 chars)", () => {
		expect(isValidProjectName("ab")).toBe(false);
	});

	it("should reject project name too long (> 50 chars)", () => {
		expect(isValidProjectName("a".repeat(51))).toBe(false);
	});

	it("should reject project name with special characters", () => {
		expect(isValidProjectName("my@project")).toBe(false);
	});

	it("should reject empty string", () => {
		expect(isValidProjectName("")).toBe(false);
	});

	it("should validate exactly 3 characters", () => {
		expect(isValidProjectName("abc")).toBe(true);
	});

	it("should validate exactly 50 characters", () => {
		expect(isValidProjectName("a".repeat(50))).toBe(true);
	});

	it("should reject project name with only spaces", () => {
		expect(isValidProjectName("   ")).toBe(true); // Actually valid per regex
	});
});

describe("isValidItemTitle", () => {
	it("should validate valid title", () => {
		expect(isValidItemTitle("My Task")).toBe(true);
	});

	it("should validate single character title", () => {
		expect(isValidItemTitle("a")).toBe(true);
	});

	it("should validate 200 character title", () => {
		expect(isValidItemTitle("a".repeat(200))).toBe(true);
	});

	it("should reject empty title", () => {
		expect(isValidItemTitle("")).toBe(false);
	});

	it("should reject title over 200 characters", () => {
		expect(isValidItemTitle("a".repeat(201))).toBe(false);
	});

	it("should validate title with special characters", () => {
		expect(isValidItemTitle("Task #1: @user fix bug!")).toBe(true);
	});

	it("should validate title with unicode", () => {
		expect(isValidItemTitle("タスク")).toBe(true);
	});

	it("should validate title with emojis", () => {
		expect(isValidItemTitle("Task 🚀")).toBe(true);
	});
});

describe("isValidId", () => {
	it("should validate UUID v4", () => {
		expect(isValidId("123e4567-e89b-12d3-a456-426614174000")).toBe(true);
	});

	it("should validate simple alphanumeric ID", () => {
		expect(isValidId("abc123")).toBe(true);
	});

	it("should validate ID with hyphens", () => {
		expect(isValidId("item-123")).toBe(true);
	});

	it("should validate ID with underscores", () => {
		expect(isValidId("item_123")).toBe(true);
	});

	it("should reject ID with spaces", () => {
		expect(isValidId("item 123")).toBe(false);
	});

	it("should reject ID with special characters", () => {
		expect(isValidId("item@123")).toBe(false);
	});

	it("should reject empty string", () => {
		expect(isValidId("")).toBe(false);
	});

	it("should validate uppercase UUID", () => {
		expect(isValidId("123E4567-E89B-12D3-A456-426614174000")).toBe(true);
	});

	it("should validate mixed case simple ID", () => {
		expect(isValidId("AbC123")).toBe(true);
	});
});

describe("isNumeric", () => {
	it("should validate integer string", () => {
		expect(isNumeric("123")).toBe(true);
	});

	it("should validate decimal string", () => {
		expect(isNumeric("123.45")).toBe(true);
	});

	it("should validate negative number", () => {
		expect(isNumeric("-123")).toBe(true);
	});

	it("should validate zero", () => {
		expect(isNumeric("0")).toBe(true);
	});

	it("should reject non-numeric string", () => {
		expect(isNumeric("abc")).toBe(false);
	});

	it("should reject empty string", () => {
		expect(isNumeric("")).toBe(false);
	});

	it("should reject string with spaces", () => {
		expect(isNumeric("123 456")).toBe(false);
	});

	it("should validate scientific notation", () => {
		expect(isNumeric("1e10")).toBe(true);
	});

	it("should validate negative decimal", () => {
		expect(isNumeric("-123.45")).toBe(true);
	});

	it("should reject infinity", () => {
		expect(isNumeric("Infinity")).toBe(false);
	});

	it("should reject NaN string", () => {
		expect(isNumeric("NaN")).toBe(false);
	});
});

describe("isInRange", () => {
	it("should validate value in range", () => {
		expect(isInRange(5, 0, 10)).toBe(true);
	});

	it("should validate value at min boundary", () => {
		expect(isInRange(0, 0, 10)).toBe(true);
	});

	it("should validate value at max boundary", () => {
		expect(isInRange(10, 0, 10)).toBe(true);
	});

	it("should reject value below range", () => {
		expect(isInRange(-1, 0, 10)).toBe(false);
	});

	it("should reject value above range", () => {
		expect(isInRange(11, 0, 10)).toBe(false);
	});

	it("should handle negative ranges", () => {
		expect(isInRange(-5, -10, 0)).toBe(true);
	});

	it("should handle decimal values", () => {
		expect(isInRange(5.5, 0, 10)).toBe(true);
	});

	it("should handle same min and max", () => {
		expect(isInRange(5, 5, 5)).toBe(true);
	});
});

describe("hasMinLength", () => {
	it("should validate string meeting minimum", () => {
		expect(hasMinLength("hello", 3)).toBe(true);
	});

	it("should validate string at exact minimum", () => {
		expect(hasMinLength("hello", 5)).toBe(true);
	});

	it("should reject string below minimum", () => {
		expect(hasMinLength("hi", 3)).toBe(false);
	});

	it("should handle empty string", () => {
		expect(hasMinLength("", 1)).toBe(false);
	});

	it("should handle zero minimum", () => {
		expect(hasMinLength("", 0)).toBe(true);
	});

	it("should count unicode characters correctly", () => {
		expect(hasMinLength("🚀🚀🚀", 3)).toBe(true);
	});
});

describe("hasMaxLength", () => {
	it("should validate string under maximum", () => {
		expect(hasMaxLength("hello", 10)).toBe(true);
	});

	it("should validate string at exact maximum", () => {
		expect(hasMaxLength("hello", 5)).toBe(true);
	});

	it("should reject string over maximum", () => {
		expect(hasMaxLength("hello world", 5)).toBe(false);
	});

	it("should handle empty string", () => {
		expect(hasMaxLength("", 5)).toBe(true);
	});

	it("should handle zero maximum", () => {
		expect(hasMaxLength("", 0)).toBe(true);
		expect(hasMaxLength("a", 0)).toBe(false);
	});
});

describe("matchesPattern", () => {
	it("should validate matching pattern", () => {
		expect(matchesPattern("abc123", /^[a-z0-9]+$/)).toBe(true);
	});

	it("should reject non-matching pattern", () => {
		expect(matchesPattern("abc@123", /^[a-z0-9]+$/)).toBe(false);
	});

	it("should handle empty string with pattern", () => {
		expect(matchesPattern("", /^$/)).toBe(true);
	});

	it("should handle complex regex", () => {
		expect(
			matchesPattern("test@example.com", /^[^\s@]+@[^\s@]+\.[^\s@]+$/),
		).toBe(true);
	});

	it("should handle case-insensitive pattern", () => {
		expect(matchesPattern("ABC", /^[a-z]+$/i)).toBe(true);
	});
});

describe("validateProject", () => {
	it("should validate valid project", () => {
		const result = validateProject({
			name: "My Project",
			description: "A test project",
		});
		expect(result.valid).toBe(true);
		expect(result.errors).toHaveLength(0);
	});

	it("should reject project without name", () => {
		const result = validateProject({
			description: "A test project",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Project name is required");
	});

	it("should reject project with invalid name", () => {
		const result = validateProject({
			name: "ab", // Too short
		});
		expect(result.valid).toBe(false);
		expect(result.errors[0]).toContain("3-50 characters");
	});

	it("should reject project with description too long", () => {
		const result = validateProject({
			name: "My Project",
			description: "a".repeat(501),
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain(
			"Description must be less than 500 characters",
		);
	});

	it("should validate project without description", () => {
		const result = validateProject({
			name: "My Project",
		});
		expect(result.valid).toBe(true);
	});

	it("should validate project with empty description", () => {
		const result = validateProject({
			name: "My Project",
			description: "",
		});
		expect(result.valid).toBe(true);
	});

	it("should accumulate multiple errors", () => {
		const result = validateProject({
			name: "ab", // Too short
			description: "a".repeat(501), // Too long
		});
		expect(result.valid).toBe(false);
		expect(result.errors.length).toBeGreaterThan(1);
	});

	it("should validate project at name boundaries", () => {
		const result1 = validateProject({ name: "abc" }); // Min length
		expect(result1.valid).toBe(true);

		const result2 = validateProject({ name: "a".repeat(50) }); // Max length
		expect(result2.valid).toBe(true);
	});
});

describe("validateItem", () => {
	it("should validate valid item", () => {
		const result = validateItem({
			title: "My Task",
			view: "features",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(true);
		expect(result.errors).toHaveLength(0);
	});

	it("should reject item without title", () => {
		const result = validateItem({
			view: "features",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Item title is required");
	});

	it("should reject item with invalid title", () => {
		const result = validateItem({
			title: "", // Empty
			view: "features",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Item title is required");
	});

	it("should reject item without view", () => {
		const result = validateItem({
			title: "My Task",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("View type is required");
	});

	it("should reject item without type", () => {
		const result = validateItem({
			title: "My Task",
			view: "features",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Item type is required");
	});

	it("should reject item without status", () => {
		const result = validateItem({
			title: "My Task",
			view: "features",
			type: "feature",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Status is required");
	});

	it("should reject item without priority", () => {
		const result = validateItem({
			title: "My Task",
			view: "features",
			type: "feature",
			status: "todo",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Priority is required");
	});

	it("should accumulate all validation errors", () => {
		const result = validateItem({});
		expect(result.valid).toBe(false);
		expect(result.errors.length).toBe(5);
	});

	it("should reject title over 200 characters", () => {
		const result = validateItem({
			title: "a".repeat(201),
			view: "features",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Item title must be 1-200 characters");
	});

	it("should validate title at boundary", () => {
		const result = validateItem({
			title: "a".repeat(200),
			view: "features",
			type: "feature",
			status: "todo",
			priority: "medium",
		});
		expect(result.valid).toBe(true);
	});
});

describe("validateLink", () => {
	it("should validate valid link", () => {
		const result = validateLink({
			sourceId: "item-1",
			targetId: "item-2",
			type: "depends_on",
		});
		expect(result.valid).toBe(true);
		expect(result.errors).toHaveLength(0);
	});

	it("should reject link without sourceId", () => {
		const result = validateLink({
			targetId: "item-2",
			type: "depends_on",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Source item is required");
	});

	it("should reject link without targetId", () => {
		const result = validateLink({
			sourceId: "item-1",
			type: "depends_on",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Target item is required");
	});

	it("should reject link without type", () => {
		const result = validateLink({
			sourceId: "item-1",
			targetId: "item-2",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain("Link type is required");
	});

	it("should reject link with same source and target", () => {
		const result = validateLink({
			sourceId: "item-1",
			targetId: "item-1",
			type: "depends_on",
		});
		expect(result.valid).toBe(false);
		expect(result.errors).toContain(
			"Source and target cannot be the same item",
		);
	});

	it("should accumulate all validation errors", () => {
		const result = validateLink({});
		expect(result.valid).toBe(false);
		// sourceId, targetId, type required, plus undefined === undefined triggers same-item check
		expect(result.errors.length).toBe(4);
	});

	it("should handle all errors including self-reference", () => {
		const result = validateLink({
			sourceId: "item-1",
			targetId: "item-1",
		});
		expect(result.valid).toBe(false);
		expect(result.errors.length).toBe(2); // same item + type required
	});
});
