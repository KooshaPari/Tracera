import type {
	ComponentLibrary,
	ComponentUsage,
	DesignToken,
	LibraryComponent,
} from "@tracertm/types";
import { describe, expect, it } from "vitest";
import componentLibraryApi from "../../api/component-library";

type CreateComponentLibraryInput = {
	projectId: string;
	name: string;
	description?: string;
	version?: string;
};

type CreateLibraryComponentInput = {
	libraryId: string;
	name: string;
	description?: string;
	category: string;
	properties?: Record<string, unknown>;
	variant?: string;
};

type CreateDesignTokenInput = {
	libraryId: string;
	name: string;
	type: string;
	value: unknown;
	category: string;
	description?: string;
};

const { componentLibraryQueryKeys } = componentLibraryApi;

describe("component library API hooks", () => {
	describe("queryKeys", () => {
		it("should generate correct query key for all component libraries", () => {
			const key = componentLibraryQueryKeys.all;
			expect(key).toEqual(["componentLibrary"]);
		});

		it("should generate correct query key for list", () => {
			const key = componentLibraryQueryKeys.list("project-1");
			expect(key).toEqual(["componentLibrary", "list", "project-1"]);
		});

		it("should generate correct query key for detail", () => {
			const key = componentLibraryQueryKeys.detail("library-1");
			expect(key).toEqual(["componentLibrary", "detail", "library-1"]);
		});

		it("should generate correct query key for components", () => {
			const key = componentLibraryQueryKeys.components("library-1");
			expect(key).toEqual(["componentLibrary", "components", "library-1"]);
		});

		it("should generate correct query key for single component", () => {
			const key = componentLibraryQueryKeys.component("component-1");
			expect(key).toEqual(["componentLibrary", "component", "component-1"]);
		});

		it("should generate correct query key for usage", () => {
			const key = componentLibraryQueryKeys.usage("component-1");
			expect(key).toEqual(["componentLibrary", "usage", "component-1"]);
		});

		it("should generate correct query key for tokens", () => {
			const key = componentLibraryQueryKeys.tokens("library-1");
			expect(key).toEqual(["componentLibrary", "tokens", "library-1"]);
		});
	});

	describe("ComponentLibrary type", () => {
		it("should validate component library structure", () => {
			const library: ComponentLibrary = {
				id: "library-1",
				projectId: "project-1",
				name: "UI Components",
				slug: "ui-components",
				description: "Core UI component library",
				version: "1.0.0",
				source: "manual",
				syncStatus: "synced",
				componentCount: 25,
				tokenCount: 10,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-02T00:00:00Z",
			};

			expect(library.id).toBeDefined();
			expect(library.projectId).toBeDefined();
			expect(library.name).toBeDefined();
			expect(library.version).toBeDefined();
			expect(library.componentCount).toBeGreaterThanOrEqual(0);
		});

		it("should allow optional description", () => {
			const library: ComponentLibrary = {
				id: "library-1",
				projectId: "project-1",
				name: "UI Components",
				slug: "ui-components",
				version: "1.0.0",
				source: "manual",
				syncStatus: "synced",
				componentCount: 0,
				tokenCount: 0,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			expect(library.description).toBeUndefined();
		});
	});

	describe("LibraryComponent type", () => {
		it("should validate library component structure", () => {
			const component: LibraryComponent = {
				id: "component-1",
				libraryId: "library-1",
				projectId: "project-1",
				name: "Button",
				displayName: "Primary Button",
				description: "Primary action button",
				category: "atom",
				usageCount: 150,
				status: "stable",
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-02T00:00:00Z",
			};

			expect(component.id).toBeDefined();
			expect(component.libraryId).toBeDefined();
			expect(component.name).toBeDefined();
			expect(component.category).toBeDefined();
			expect(component.usageCount).toBeGreaterThanOrEqual(0);
		});

		it("should allow optional variant", () => {
			const component: LibraryComponent = {
				id: "component-1",
				libraryId: "library-1",
				projectId: "project-1",
				name: "Button",
				displayName: "Button",
				category: "atom",
				usageCount: 0,
				status: "stable",
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			expect(component.variant).toBeUndefined();
		});
	});

	describe("ComponentUsage type", () => {
		it("should validate component usage structure", () => {
			const usage: ComponentUsage = {
				id: "usage-1",
				projectId: "project-1",
				libraryId: "library-1",
				componentId: "component-1",
				usedInItemId: "item-1",
				detectedAt: "2024-01-02T00:00:00Z",
			};

			expect(usage.usedInItemId).toBeDefined();
			expect(usage.componentId).toBeDefined();
			expect(usage.detectedAt).toBeDefined();
		});
	});

	describe("DesignToken type", () => {
		it("should validate design token structure", () => {
			const token: DesignToken = {
				id: "token-1",
				libraryId: "library-1",
				projectId: "project-1",
				name: "colors.primary.500",
				path: ["colors", "primary", "500"],
				type: "color",
				value: "#0066CC",
				usageCount: 5,
				description: "Primary brand color",
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-02T00:00:00Z",
			};

			expect(token.id).toBeDefined();
			expect(token.libraryId).toBeDefined();
			expect(token.name).toBeDefined();
			expect(token.type).toBeDefined();
			expect(token.value).toBeDefined();
			expect(token.usageCount).toBeGreaterThanOrEqual(0);
		});

		it("should store design token values as strings", () => {
			const colorToken: DesignToken = {
				id: "token-1",
				libraryId: "library-1",
				projectId: "project-1",
				name: "colors.primary.500",
				path: ["colors", "primary", "500"],
				type: "color",
				value: "#0066CC",
				usageCount: 0,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			const spacingToken: DesignToken = {
				id: "token-2",
				libraryId: "library-1",
				projectId: "project-1",
				name: "spacing.sm",
				path: ["spacing", "sm"],
				type: "spacing",
				value: "8",
				usageCount: 0,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			const typographyToken: DesignToken = {
				id: "token-3",
				libraryId: "library-1",
				projectId: "project-1",
				name: "typography.body",
				path: ["typography", "body"],
				type: "typography",
				value: "Inter/16/1.5",
				usageCount: 0,
				createdAt: "2024-01-01T00:00:00Z",
				updatedAt: "2024-01-01T00:00:00Z",
			};

			expect(typeof colorToken.value).toBe("string");
			expect(typeof spacingToken.value).toBe("string");
			expect(typeof typographyToken.value).toBe("string");
		});
	});

	describe("Input types", () => {
		it("should validate CreateComponentLibraryInput", () => {
			const input: CreateComponentLibraryInput = {
				projectId: "project-1",
				name: "Design System",
				description: "Complete design system",
				version: "2.0.0",
			};

			expect(input.projectId).toBeDefined();
			expect(input.name).toBeDefined();
		});

		it("should validate CreateLibraryComponentInput", () => {
			const input: CreateLibraryComponentInput = {
				libraryId: "library-1",
				name: "Card",
				description: "Container component",
				category: "layout",
				properties: { padding: "16px" },
				variant: "default",
			};

			expect(input.libraryId).toBeDefined();
			expect(input.name).toBeDefined();
			expect(input.category).toBeDefined();
		});

		it("should validate CreateDesignTokenInput", () => {
			const input: CreateDesignTokenInput = {
				libraryId: "library-1",
				name: "radius-sm",
				type: "radius",
				value: "4",
				category: "radius",
				description: "Small border radius",
			};

			expect(input.libraryId).toBeDefined();
			expect(input.name).toBeDefined();
			expect(input.type).toBeDefined();
			expect(input.value).toBeDefined();
			expect(input.category).toBeDefined();
		});
	});

	describe("Query key hierarchies", () => {
		it("should create consistent component query keys", () => {
			const key1 = componentLibraryQueryKeys.component("component-1");
			const key2 = componentLibraryQueryKeys.component("component-2");

			expect(key1).not.toEqual(key2);
			expect(key1.slice(0, 2)).toEqual(key2.slice(0, 2)); // Same prefix
		});

		it("should create consistent library component keys", () => {
			const key1 = componentLibraryQueryKeys.components("library-1");
			const key2 = componentLibraryQueryKeys.components("library-2");

			expect(key1).not.toEqual(key2);
			expect(key1[1]).toEqual(key2[1]); // Same operation
		});

		it("should create independent token keys", () => {
			const key1 = componentLibraryQueryKeys.tokens("library-1");
			const key2 = componentLibraryQueryKeys.tokens("library-2");

			expect(key1).not.toEqual(key2);
			expect(key1[1]).toEqual(key2[1]); // Same operation
		});

		it("should create separate keys for usage", () => {
			const key1 = componentLibraryQueryKeys.usage("component-1");
			const key2 = componentLibraryQueryKeys.usage("component-2");

			expect(key1).not.toEqual(key2);
			expect(key1[1]).toEqual(key2[1]); // Same operation
		});
	});
});
