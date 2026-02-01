// Tests for hierarchy utilities

import type { Item, Link } from "@tracertm/types";
import { beforeEach, describe, expect, it } from "vitest";
import {
	buildHierarchy,
	findCommonAncestor,
	getAncestorChain,
	getBreadcrumbPath,
	getChildren,
	getDepth,
	getDescendantNodes,
	getHierarchyStats,
	getItemsAtDepth,
	getParent,
	getSiblings,
	isAncestor,
	isDescendant,
} from "../../../../components/graph/utils/hierarchy";

describe("Hierarchy Utilities", () => {
	let items: Item[];
	let links: Link[];

	const createItem = (id: string, title: string): Item => ({
		id,
		projectId: "p1",
		view: "technical",
		type: "Component",
		title,
		description: `Item ${id}`,
		status: "done" as const,
		priority: "medium" as const,
		version: 1,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	});

	const createParentOfLink = (parentId: string, childId: string): Link => ({
		id: `link-${parentId}-${childId}`,
		sourceId: parentId,
		targetId: childId,
		type: "parent_of",
		description: `${parentId} is parent of ${childId}`,
		createdAt: new Date().toISOString(),
		updatedAt: new Date().toISOString(),
	});

	beforeEach(() => {
		// Build a hierarchy:
		//     root
		//    /    \
		//   a      b
		//  / \
		// a1  a2
		//
		items = [
			createItem("root", "Root"),
			createItem("a", "Component A"),
			createItem("b", "Component B"),
			createItem("a1", "Component A1"),
			createItem("a2", "Component A2"),
		];

		links = [
			createParentOfLink("root", "a"),
			createParentOfLink("root", "b"),
			createParentOfLink("a", "a1"),
			createParentOfLink("a", "a2"),
		];
	});

	describe("buildHierarchy", () => {
		it("should create hierarchy from parent_of links", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(hierarchy.size).toBe(items.length);
		});

		it("should identify root nodes correctly", () => {
			const hierarchy = buildHierarchy(items, links);
			const rootNode = hierarchy.get("root");

			expect(rootNode?.isRoot).toBe(true);
			expect(rootNode?.parentId).toBeUndefined();
		});

		it("should identify leaf nodes correctly", () => {
			const hierarchy = buildHierarchy(items, links);
			const leafNode = hierarchy.get("a1");

			expect(leafNode?.isLeaf).toBe(true);
			expect(leafNode?.childrenIds.length).toBe(0);
		});

		it("should build parent-child relationships", () => {
			const hierarchy = buildHierarchy(items, links);
			const parentNode = hierarchy.get("a");

			expect(parentNode?.childrenIds).toContain("a1");
			expect(parentNode?.childrenIds).toContain("a2");
			expect(parentNode?.childrenIds.length).toBe(2);
		});

		it("should calculate correct depths", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(getDepth("root", hierarchy)).toBe(0);
			expect(getDepth("a", hierarchy)).toBe(1);
			expect(getDepth("a1", hierarchy)).toBe(2);
		});

		it("should mark unconnected items as roots", () => {
			const unconnectedItem = createItem("orphan", "Orphan Item");
			const testItems = [...items, unconnectedItem];

			const hierarchy = buildHierarchy(testItems, links);
			const unconnectedNode = hierarchy.get("orphan");

			// Items without parents are roots, not orphans
			expect(unconnectedNode?.isRoot).toBe(true);
			expect(unconnectedNode?.isLeaf).toBe(true);
		});
	});

	describe("getParent", () => {
		it("should return parent node", () => {
			const hierarchy = buildHierarchy(items, links);
			const parent = getParent("a1", hierarchy);

			expect(parent?.id).toBe("a");
		});

		it("should return undefined for root nodes", () => {
			const hierarchy = buildHierarchy(items, links);
			const parent = getParent("root", hierarchy);

			expect(parent).toBeUndefined();
		});
	});

	describe("getChildren", () => {
		it("should return all children", () => {
			const hierarchy = buildHierarchy(items, links);
			const children = getChildren("a", hierarchy);

			expect(children.length).toBe(2);
			expect(children.some((c) => c.id === "a1")).toBe(true);
			expect(children.some((c) => c.id === "a2")).toBe(true);
		});

		it("should return empty array for leaf nodes", () => {
			const hierarchy = buildHierarchy(items, links);
			const children = getChildren("a1", hierarchy);

			expect(children.length).toBe(0);
		});
	});

	describe("getAncestorChain", () => {
		it("should return ancestor chain from immediate parent to root", () => {
			const hierarchy = buildHierarchy(items, links);
			const chain = getAncestorChain("a1", hierarchy);

			expect(chain.length).toBe(2); // a, root
			expect(chain[0].id).toBe("a");
			expect(chain[1].id).toBe("root");
		});

		it("should return empty array for root nodes", () => {
			const hierarchy = buildHierarchy(items, links);
			const chain = getAncestorChain("root", hierarchy);

			expect(chain.length).toBe(0);
		});
	});

	describe("getDescendantNodes", () => {
		it("should return all descendants recursively", () => {
			const hierarchy = buildHierarchy(items, links);
			const descendants = getDescendantNodes("a", hierarchy);

			expect(descendants.length).toBe(2); // a1, a2
			expect(descendants.some((d) => d.id === "a1")).toBe(true);
			expect(descendants.some((d) => d.id === "a2")).toBe(true);
		});

		it("should return all descendants from root", () => {
			const hierarchy = buildHierarchy(items, links);
			const descendants = getDescendantNodes("root", hierarchy);

			expect(descendants.length).toBe(4); // a, b, a1, a2
		});

		it("should return empty array for leaf nodes", () => {
			const hierarchy = buildHierarchy(items, links);
			const descendants = getDescendantNodes("a1", hierarchy);

			expect(descendants.length).toBe(0);
		});
	});

	describe("getBreadcrumbPath", () => {
		it("should return breadcrumb path for item", () => {
			const hierarchy = buildHierarchy(items, links);
			const breadcrumbs = getBreadcrumbPath("a1", hierarchy);

			expect(breadcrumbs.length).toBe(3); // root, a, a1
			expect(breadcrumbs[0].title).toBe("Root");
			expect(breadcrumbs[1].title).toBe("Component A");
			expect(breadcrumbs[2].title).toBe("Component A1");
		});

		it("should return single item for root", () => {
			const hierarchy = buildHierarchy(items, links);
			const breadcrumbs = getBreadcrumbPath("root", hierarchy);

			expect(breadcrumbs.length).toBe(1);
			expect(breadcrumbs[0].id).toBe("root");
		});
	});

	describe("findCommonAncestor", () => {
		it("should find common ancestor of siblings", () => {
			const hierarchy = buildHierarchy(items, links);
			const ancestor = findCommonAncestor("a1", "a2", hierarchy);

			expect(ancestor).toBe("a");
		});

		it("should find common ancestor at different levels", () => {
			const hierarchy = buildHierarchy(items, links);
			const ancestor = findCommonAncestor("a1", "b", hierarchy);

			expect(ancestor).toBe("root");
		});

		it("should return undefined if no common ancestor", () => {
			const item3 = createItem("c", "Component C");
			const testItems = [...items, item3];

			const hierarchy = buildHierarchy(testItems, links);
			const ancestor = findCommonAncestor("a1", "c", hierarchy);

			expect(ancestor).toBeUndefined();
		});
	});

	describe("getSiblings", () => {
		it("should return all siblings", () => {
			const hierarchy = buildHierarchy(items, links);
			const siblings = getSiblings("a1", hierarchy);

			expect(siblings.length).toBe(1);
			expect(siblings[0].id).toBe("a2");
		});

		it("should return siblings with same parent", () => {
			const hierarchy = buildHierarchy(items, links);
			const siblings = getSiblings("a", hierarchy);

			expect(siblings.length).toBe(1);
			expect(siblings[0].id).toBe("b");
		});

		it("should return empty for only child", () => {
			const singleChildLink = [createParentOfLink("root", "a")];
			const hierarchy = buildHierarchy(items, singleChildLink);
			const siblings = getSiblings("a", hierarchy);

			expect(siblings.length).toBe(0);
		});
	});

	describe("isAncestor", () => {
		it("should identify ancestor correctly", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(isAncestor("root", "a1", hierarchy)).toBe(true);
			expect(isAncestor("a", "a1", hierarchy)).toBe(true);
		});

		it("should return false for non-ancestor", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(isAncestor("a1", "a", hierarchy)).toBe(false);
			expect(isAncestor("b", "a1", hierarchy)).toBe(false);
		});
	});

	describe("isDescendant", () => {
		it("should identify descendant correctly", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(isDescendant("a1", "root", hierarchy)).toBe(true);
			expect(isDescendant("a1", "a", hierarchy)).toBe(true);
		});

		it("should return false for non-descendant", () => {
			const hierarchy = buildHierarchy(items, links);

			expect(isDescendant("a", "a1", hierarchy)).toBe(false);
			expect(isDescendant("a1", "b", hierarchy)).toBe(false);
		});
	});

	describe("getItemsAtDepth", () => {
		it("should return all items at specific depth", () => {
			const hierarchy = buildHierarchy(items, links);

			const depthZero = getItemsAtDepth(0, hierarchy);
			expect(depthZero.length).toBe(1);
			expect(depthZero[0].id).toBe("root");

			const depthOne = getItemsAtDepth(1, hierarchy);
			expect(depthOne.length).toBe(2);

			const depthTwo = getItemsAtDepth(2, hierarchy);
			expect(depthTwo.length).toBe(2);
		});

		it("should return empty array for non-existent depth", () => {
			const hierarchy = buildHierarchy(items, links);
			const depthFive = getItemsAtDepth(5, hierarchy);

			expect(depthFive.length).toBe(0);
		});
	});

	describe("getHierarchyStats", () => {
		it("should calculate hierarchy statistics", () => {
			const hierarchy = buildHierarchy(items, links);
			const stats = getHierarchyStats(hierarchy);

			expect(stats.totalNodes).toBe(5);
			expect(stats.maxDepth).toBe(2);
			expect(stats.rootCount).toBe(1);
			expect(stats.leafCount).toBe(3); // a1, a2, b
		});

		it("should include depth distribution", () => {
			const hierarchy = buildHierarchy(items, links);
			const stats = getHierarchyStats(hierarchy);

			expect(stats.depthDistribution["0"]).toBe(1);
			expect(stats.depthDistribution["1"]).toBe(2);
			expect(stats.depthDistribution["2"]).toBe(2);
		});
	});
});
