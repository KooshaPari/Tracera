/* eslint-disable no-unused-vars -- test compiles type-only props */
/* eslint-disable unicorn/consistent-function-scoping -- test helper at module scope */
import type { Item } from "@tracertm/types";
import {
	hasSpec,
	isDefectItem,
	isEpicItem,
	isRequirementItem,
	isTaskItem,
	isTestItem,
	isUserStoryItem,
} from "@tracertm/types";
import { describe, expect, it } from "vitest";

function createMockItem(type: string): Item {
	return {
		createdAt: "2026-01-30T00:00:00Z",
		id: "test-id",
		priority: "medium",
		projectId: "project-1",
		status: "todo",
		title: "Test Item",
		type,
		updatedAt: "2026-01-30T00:00:00Z",
		version: 1,
		view: "FEATURE",
	};
}

describe("Type Guards", () => {
	describe(isRequirementItem, () => {
		it("should return true for requirement type", () => {
			const item = createMockItem("requirement");
			expect(isRequirementItem(item)).toBe(true);
		});

		it("should return false for non-requirement types", () => {
			expect(isRequirementItem(createMockItem("test"))).toBe(false);
			expect(isRequirementItem(createMockItem("epic"))).toBe(false);
			expect(isRequirementItem(createMockItem("task"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("requirement");
			if (isRequirementItem(item)) {
				// TypeScript should allow accessing RequirementItem-specific properties
				const adrId = item.adrId; // Should compile
				const contractId = item.contractId; // Should compile
				expect(adrId).toBeUndefined(); // These are optional
				expect(contractId).toBeUndefined();
			}
		});
	});

	describe(isTestItem, () => {
		it("should return true for test types", () => {
			expect(isTestItem(createMockItem("test"))).toBe(true);
			expect(isTestItem(createMockItem("test_case"))).toBe(true);
			expect(isTestItem(createMockItem("test_suite"))).toBe(true);
		});

		it("should return false for non-test types", () => {
			expect(isTestItem(createMockItem("requirement"))).toBe(false);
			expect(isTestItem(createMockItem("epic"))).toBe(false);
			expect(isTestItem(createMockItem("bug"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("test");
			if (isTestItem(item)) {
				const testType = item.testType; // Should compile
				const automationStatus = item.automationStatus; // Should compile
				expect(testType).toBeUndefined(); // Optional properties
				expect(automationStatus).toBeUndefined();
			}
		});
	});

	describe(isEpicItem, () => {
		it("should return true for epic type", () => {
			expect(isEpicItem(createMockItem("epic"))).toBe(true);
		});

		it("should return false for non-epic types", () => {
			expect(isEpicItem(createMockItem("requirement"))).toBe(false);
			expect(isEpicItem(createMockItem("user_story"))).toBe(false);
			expect(isEpicItem(createMockItem("task"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("epic");
			if (isEpicItem(item)) {
				const acceptanceCriteria = item.acceptanceCriteria; // Should compile
				const businessValue = item.businessValue; // Should compile
				expect(acceptanceCriteria).toBeUndefined();
				expect(businessValue).toBeUndefined();
			}
		});
	});

	describe(isUserStoryItem, () => {
		it("should return true for user story types", () => {
			expect(isUserStoryItem(createMockItem("user_story"))).toBe(true);
			expect(isUserStoryItem(createMockItem("story"))).toBe(true);
		});

		it("should return false for non-story types", () => {
			expect(isUserStoryItem(createMockItem("epic"))).toBe(false);
			expect(isUserStoryItem(createMockItem("requirement"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("user_story");
			if (isUserStoryItem(item)) {
				const asA = item.asA; // Should compile
				const iWant = item.iWant; // Should compile
				const soThat = item.soThat; // Should compile
				const storyPoints = item.storyPoints; // Should compile
				expect(asA).toBeUndefined();
				expect(iWant).toBeUndefined();
				expect(soThat).toBeUndefined();
				expect(storyPoints).toBeUndefined();
			}
		});
	});

	describe(isTaskItem, () => {
		it("should return true for task type", () => {
			expect(isTaskItem(createMockItem("task"))).toBe(true);
		});

		it("should return false for non-task types", () => {
			expect(isTaskItem(createMockItem("bug"))).toBe(false);
			expect(isTaskItem(createMockItem("user_story"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("task");
			if (isTaskItem(item)) {
				const estimatedHours = item.estimatedHours; // Should compile
				const actualHours = item.actualHours; // Should compile
				expect(estimatedHours).toBeUndefined();
				expect(actualHours).toBeUndefined();
			}
		});
	});

	describe(isDefectItem, () => {
		it("should return true for defect types", () => {
			expect(isDefectItem(createMockItem("bug"))).toBe(true);
			expect(isDefectItem(createMockItem("defect"))).toBe(true);
		});

		it("should return false for non-defect types", () => {
			expect(isDefectItem(createMockItem("task"))).toBe(false);
			expect(isDefectItem(createMockItem("test"))).toBe(false);
		});

		it("should enable type-specific property access", () => {
			const item = createMockItem("bug");
			if (isDefectItem(item)) {
				const severity = item.severity; // Should compile
				const reproducible = item.reproducible; // Should compile
				const stepsToReproduce = item.stepsToReproduce; // Should compile
				expect(severity).toBeUndefined();
				expect(reproducible).toBeUndefined();
				expect(stepsToReproduce).toBeUndefined();
			}
		});
	});

	describe(hasSpec, () => {
		it("should return true for requirement items", () => {
			expect(hasSpec(createMockItem("requirement"))).toBe(true);
		});

		it("should return false for non-specification items", () => {
			expect(hasSpec(createMockItem("test"))).toBe(false);
			expect(hasSpec(createMockItem("epic"))).toBe(false);
			expect(hasSpec(createMockItem("bug"))).toBe(false);
		});

		it("should be equivalent to isRequirementItem", () => {
			const requirementItem = createMockItem("requirement");
			const testItem = createMockItem("test");

			expect(hasSpec(requirementItem)).toBe(isRequirementItem(requirementItem));
			expect(hasSpec(testItem)).toBe(isRequirementItem(testItem));
		});
	});

	describe("Type narrowing in switch statements", () => {
		it("should work with discriminated union", () => {
			const item = createMockItem("requirement");

			switch (item.type) {
				case "requirement": {
					// TypeScript should narrow to RequirementItem
					expect(item.type).toBe("requirement");
					break;
				}
				case "test":
				case "test_case":
				case "test_suite": {
					// TypeScript should narrow to TestItem
					expect(item.type).toMatch(/^test/);
					break;
				}
				default: {
					// Other types
					break;
				}
			}
		});
	});

	describe("Type guard composition", () => {
		it("should work with multiple type guards", () => {
			const items = [
				createMockItem("requirement"),
				createMockItem("test"),
				createMockItem("epic"),
				createMockItem("bug"),
			];

			const requirements = items.filter(isRequirementItem);
			const tests = items.filter(isTestItem);
			const defects = items.filter(isDefectItem);

			expect(requirements).toHaveLength(1);
			expect(tests).toHaveLength(1);
			expect(defects).toHaveLength(1);
		});
	});
});
