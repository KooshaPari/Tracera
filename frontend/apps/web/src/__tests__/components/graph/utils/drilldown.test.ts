// Tests for drill-down navigation utilities

import type { Item, Link } from "../../../../../../../packages/types/src/index";
import { beforeEach, describe, expect, it } from "vitest";
import {
	createBreadcrumbs,
	createDrillDownContext,
	createDrillDownNodeGroups,
	getChildrenByDrillDownLevel,
	getDrillDownPath,
	getDrillDownStats,
	getNextLevel,
	getPreviousLevel,
	inferDrillDownLevel,
	navigateToChild,
	navigateUp,
	toggleDrillDownGroup,
} from "../../../../components/graph/utils/drilldown";
import { buildHierarchy } from "../../../../components/graph/utils/hierarchy";

function createItem(id: string, title: string, type: string): Item {
	return {
		id,
		projectId: "p1",
		view: "technical",
		type,
		title,
		description: `Item ${id}`,
		status: "done" as const,
		priority: "medium" as const,
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	};
}

function createParentOfLink(parentId: string, childId: string): Link {
	return {
		id: `link-${parentId}-${childId}`,
		sourceId: parentId,
		targetId: childId,
		type: "parent_of",
		description: `${parentId} is parent of ${childId}`,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	};
}

describe("Drill-Down Navigation", () => {
	let items: Item[];
	let links: Link[];

	beforeEach(() => {
		// Hierarchy: Project → Repository → Module → File → Function
		items = [
			createItem("proj", "MyProject", "project"),
			createItem("repo", "main-repo", "repository"),
			createItem("mod", "auth-module", "module"),
			createItem("file", "login.ts", "file"),
			createItem("func", "authenticate()", "function"),
		];

		links = [
			createParentOfLink("proj", "repo"),
			createParentOfLink("repo", "mod"),
			createParentOfLink("mod", "file"),
			createParentOfLink("file", "func"),
		];
	});

	describe("inferDrillDownLevel", () => {
		it("should infer drill-down level from item type", () => {
			expect(inferDrillDownLevel("project")).toBe("project");
			expect(inferDrillDownLevel("repository")).toBe("repository");
			expect(inferDrillDownLevel("module")).toBe("module");
			expect(inferDrillDownLevel("file")).toBe("file");
			expect(inferDrillDownLevel("function")).toBe("function");
		});

		it("should handle type variations", () => {
			expect(inferDrillDownLevel("repo")).toBe("repository");
			expect(inferDrillDownLevel("code")).toBe("file");
			expect(inferDrillDownLevel("method")).toBe("function");
		});

		it("should default to module for unknown types", () => {
			expect(inferDrillDownLevel("unknown")).toBe("module");
		});
	});

	describe("getNextLevel", () => {
		it("should return next level in hierarchy", () => {
			expect(getNextLevel("project")).toBe("repository");
			expect(getNextLevel("repository")).toBe("module");
			expect(getNextLevel("module")).toBe("file");
			expect(getNextLevel("file")).toBe("function");
		});

		it("should return null for last level", () => {
			expect(getNextLevel("function")).toBeNull();
		});
	});

	describe("getPreviousLevel", () => {
		it("should return previous level in hierarchy", () => {
			expect(getPreviousLevel("repository")).toBe("project");
			expect(getPreviousLevel("module")).toBe("repository");
			expect(getPreviousLevel("file")).toBe("module");
			expect(getPreviousLevel("function")).toBe("file");
		});

		it("should return null for first level", () => {
			expect(getPreviousLevel("project")).toBeNull();
		});
	});

	describe("createBreadcrumbs", () => {
		it("should create breadcrumbs from item path", () => {
			const hierarchy = buildHierarchy(items, links);
			const breadcrumbs = createBreadcrumbs("func", hierarchy);

			expect(breadcrumbs.length).toBe(5); // All levels
			expect(breadcrumbs[0].itemId).toBe("proj");
			expect(breadcrumbs[breadcrumbs.length - 1].itemId).toBe("func");
		});

		it("should include correct drill-down levels in breadcrumbs", () => {
			const hierarchy = buildHierarchy(items, links);
			const breadcrumbs = createBreadcrumbs("func", hierarchy);

			expect(breadcrumbs[0].level).toBe("project");
			expect(breadcrumbs[breadcrumbs.length - 1].level).toBe("function");
		});

		it("should include icons in breadcrumbs", () => {
			const hierarchy = buildHierarchy(items, links);
			const breadcrumbs = createBreadcrumbs("func", hierarchy);

			for (const crumb of breadcrumbs) {
				expect(crumb.icon).toBeDefined();
				expect(crumb.icon.length).toBeGreaterThan(0);
			}
		});
	});

	describe("getChildrenByDrillDownLevel", () => {
		it("should group children by drill-down level", () => {
			const hierarchy = buildHierarchy(items, links);
			const levelGroups = getChildrenByDrillDownLevel("proj", hierarchy, items);

			expect(levelGroups.size).toBeGreaterThan(0);
			expect(levelGroups.has("repository")).toBe(true);
		});

		it("should return empty map for leaf nodes", () => {
			const hierarchy = buildHierarchy(items, links);
			const levelGroups = getChildrenByDrillDownLevel("func", hierarchy, items);

			expect(levelGroups.size).toBe(0);
		});
	});

	describe("createDrillDownContext", () => {
		it("should create context for current item", () => {
			const hierarchy = buildHierarchy(items, links);
			const context = createDrillDownContext("mod", items, hierarchy);

			expect(context.itemId).toBe("mod");
			expect(context.itemTitle).toBe("auth-module");
			expect(context.currentLevel).toBe("module");
		});

		it("should include parent information", () => {
			const hierarchy = buildHierarchy(items, links);
			const context = createDrillDownContext("mod", items, hierarchy);

			expect(context.parentId).toBe("repo");
			expect(context.parentTitle).toBe("main-repo");
		});

		it("should indicate children availability", () => {
			const hierarchy = buildHierarchy(items, links);

			const parentContext = createDrillDownContext("mod", items, hierarchy);
			expect(parentContext.childrenAvailable).toBe(true);

			const leafContext = createDrillDownContext("func", items, hierarchy);
			expect(leafContext.childrenAvailable).toBe(false);
		});

		it("should include breadcrumbs", () => {
			const hierarchy = buildHierarchy(items, links);
			const context = createDrillDownContext("file", items, hierarchy);

			expect(context.breadcrumbs.length).toBeGreaterThan(0);
		});
	});

	describe("createDrillDownNodeGroups", () => {
		it("should create groups for item children", () => {
			const hierarchy = buildHierarchy(items, links);
			const groups = createDrillDownNodeGroups("proj", items, hierarchy);

			expect(groups.length).toBeGreaterThan(0);
		});

		it("should not create groups for leaf items", () => {
			const hierarchy = buildHierarchy(items, links);
			const groups = createDrillDownNodeGroups("func", items, hierarchy);

			expect(groups.length).toBe(0);
		});

		it("should include drill-down level in groups", () => {
			const hierarchy = buildHierarchy(items, links);
			const groups = createDrillDownNodeGroups("proj", items, hierarchy);

			for (const group of groups) {
				expect(group.level).toBeDefined();
			}
		});

		it("should handle max items per group", () => {
			const hierarchy = buildHierarchy(items, links);
			const groups = createDrillDownNodeGroups("proj", items, hierarchy, 1);

			// With maxItemsPerGroup=1, single-child groups may split
			for (const group of groups) {
				expect(group.itemCount).toBeLessThanOrEqual(1);
			}
		});
	});

	describe("toggleDrillDownGroup", () => {
		it("should add group to expanded set", () => {
			const expanded = new Set<string>();
			const result = toggleDrillDownGroup("group1", expanded);

			expect(result.has("group1")).toBe(true);
		});

		it("should remove group from expanded set", () => {
			const expanded = new Set(["group1"]);
			const result = toggleDrillDownGroup("group1", expanded);

			expect(result.has("group1")).toBe(false);
		});

		it("should not modify original set", () => {
			const expanded = new Set(["group1"]);
			const result = toggleDrillDownGroup("group2", expanded);

			expect(expanded.has("group2")).toBe(false);
			expect(result.has("group2")).toBe(true);
		});
	});

	describe("navigateUp", () => {
		it("should return parent ID", () => {
			const hierarchy = buildHierarchy(items, links);
			const parentId = navigateUp("file", hierarchy);

			expect(parentId).toBe("mod");
		});

		it("should return null for root", () => {
			const hierarchy = buildHierarchy(items, links);
			const parentId = navigateUp("proj", hierarchy);

			expect(parentId).toBeNull();
		});
	});

	describe("navigateToChild", () => {
		it("should navigate to child by index", () => {
			const hierarchy = buildHierarchy(items, links);
			const childId = navigateToChild("proj", 0, hierarchy);

			expect(childId).toBe("repo");
		});

		it("should return null for invalid index", () => {
			const hierarchy = buildHierarchy(items, links);

			const childId1 = navigateToChild("proj", 999, hierarchy);
			expect(childId1).toBeNull();

			const childId2 = navigateToChild("proj", -1, hierarchy);
			expect(childId2).toBeNull();
		});

		it("should return null for no children", () => {
			const hierarchy = buildHierarchy(items, links);
			const childId = navigateToChild("func", 0, hierarchy);

			expect(childId).toBeNull();
		});
	});

	describe("getDrillDownPath", () => {
		it("should return path from root to item", () => {
			const hierarchy = buildHierarchy(items, links);
			const path = getDrillDownPath("func", hierarchy);

			expect(path).toEqual(["proj", "repo", "mod", "file", "func"]);
		});

		it("should return single item for root", () => {
			const hierarchy = buildHierarchy(items, links);
			const path = getDrillDownPath("proj", hierarchy);

			expect(path).toEqual(["proj"]);
		});

		it("should return empty array for non-existent item", () => {
			const hierarchy = buildHierarchy(items, links);
			const path = getDrillDownPath("nonexistent", hierarchy);

			expect(path).toEqual([]);
		});
	});

	describe("getDrillDownStats", () => {
		it("should calculate drill-down statistics", () => {
			const hierarchy = buildHierarchy(items, links);
			const stats = getDrillDownStats("proj", hierarchy);

			expect(stats.totalDescendants).toBe(4); // repo, mod, file, func
			expect(stats.depth).toBe(0);
			expect(stats.childCount).toBe(1);
		});

		it("should report expandable children", () => {
			const hierarchy = buildHierarchy(items, links);

			const projStats = getDrillDownStats("proj", hierarchy);
			expect(projStats.expandableCount).toBeGreaterThan(0);

			const funcStats = getDrillDownStats("func", hierarchy);
			expect(funcStats.expandableCount).toBe(0);
		});

		it("should handle non-existent items", () => {
			const hierarchy = buildHierarchy(items, links);
			const stats = getDrillDownStats("nonexistent", hierarchy);

			expect(stats.totalDescendants).toBe(0);
			expect(stats.childCount).toBe(0);
		});
	});
});
