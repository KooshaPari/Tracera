// ComponentUsageMatrix.stories.tsx - Storybook stories for ComponentUsageMatrix

import type { Meta, StoryObj } from "@storybook/react";
import type { LibraryComponent, ComponentUsage } from "@tracertm/types";
import { ComponentUsageMatrix } from "../ComponentUsageMatrix";

const meta = {
	title: "Graph/ComponentUsageMatrix",
	component: ComponentUsageMatrix,
	parameters: {
		layout: "fullscreen",
	},
	tags: ["autodocs"],
} satisfies Meta<typeof ComponentUsageMatrix>;

export default meta;
type Story = StoryObj<typeof meta>;

// =============================================================================
// MOCK DATA
// =============================================================================

const mockComponents: LibraryComponent[] = [
	// Atoms
	{
		id: "btn-primary",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Button",
		displayName: "Primary Button",
		description: "Primary call-to-action button component",
		category: "atom",
		status: "stable",
		usageCount: 45,
		usageLocations: ["page-1", "page-2", "page-3"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{
				name: "variant",
				type: '"primary" | "secondary" | "danger"',
				required: false,
			},
			{ name: "size", type: '"sm" | "md" | "lg"', required: false },
			{ name: "disabled", type: "boolean", required: false },
			{ name: "loading", type: "boolean", required: false },
			{
				name: "onClick",
				type: "(e: React.MouseEvent) => void",
				required: false,
			},
		],
		variants: [
			{ name: "Primary", props: { variant: "primary" } },
			{ name: "Secondary", props: { variant: "secondary" } },
			{ name: "Danger", props: { variant: "danger" } },
			{ name: "Small", props: { size: "sm" } },
			{ name: "Large", props: { size: "lg" } },
		],
	},
	{
		id: "input-text",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Input",
		displayName: "Text Input",
		description: "Basic text input field for forms",
		category: "atom",
		status: "stable",
		usageCount: 32,
		usageLocations: ["page-2", "page-3"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{ name: "type", type: "string", required: false },
			{ name: "placeholder", type: "string", required: false },
			{ name: "disabled", type: "boolean", required: false },
			{ name: "required", type: "boolean", required: false },
		],
	},
	{
		id: "badge-info",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Badge",
		displayName: "Status Badge",
		description: "Small status indicator badge",
		category: "atom",
		status: "stable",
		usageCount: 28,
		usageLocations: ["page-1"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		variants: [
			{ name: "Success", props: { variant: "success" } },
			{ name: "Error", props: { variant: "error" } },
			{ name: "Warning", props: { variant: "warning" } },
			{ name: "Info", props: { variant: "info" } },
		],
	},
	{
		id: "icon-star",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Icon",
		displayName: "Icon Library",
		description: "Lucide-based icon system",
		category: "atom",
		status: "stable",
		usageCount: 89,
		usageLocations: ["page-1", "page-2", "page-3"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},

	// Molecules
	{
		id: "search-bar",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "SearchBar",
		displayName: "Search Bar",
		description: "Search input with suggestions",
		category: "molecule",
		status: "stable",
		usageCount: 12,
		usageLocations: ["page-1"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{ name: "onSearch", type: "(query: string) => void", required: true },
			{ name: "suggestions", type: "string[]", required: false },
			{ name: "debounceMs", type: "number", required: false },
		],
	},
	{
		id: "form-field",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "FormField",
		displayName: "Form Field",
		description: "Labeled input with validation",
		category: "molecule",
		status: "stable",
		usageCount: 24,
		usageLocations: ["page-2", "page-3"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{ name: "label", type: "string", required: true },
			{ name: "error", type: "string", required: false },
			{ name: "required", type: "boolean", required: false },
		],
	},

	// Organisms
	{
		id: "navbar",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Navbar",
		displayName: "Navigation Bar",
		description: "Top navigation bar with menu",
		category: "organism",
		status: "stable",
		usageCount: 3,
		usageLocations: ["page-1"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},
	{
		id: "sidebar",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Sidebar",
		displayName: "Side Navigation",
		description: "Left sidebar navigation",
		category: "organism",
		status: "stable",
		usageCount: 5,
		usageLocations: ["page-1", "page-2"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},
	{
		id: "card-component",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Card",
		displayName: "Card Container",
		description: "Content card with header and body",
		category: "organism",
		status: "stable",
		usageCount: 18,
		usageLocations: ["page-1", "page-2", "page-3"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{ name: "title", type: "string", required: false },
			{ name: "elevation", type: "number", required: false },
		],
	},

	// Overlay
	{
		id: "modal-dialog",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Modal",
		displayName: "Modal Dialog",
		description: "Modal overlay for dialogs",
		category: "overlay",
		status: "stable",
		usageCount: 0,
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},
	{
		id: "tooltip-popup",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "Tooltip",
		displayName: "Tooltip",
		description: "Hover tooltip popup",
		category: "overlay",
		status: "stable",
		usageCount: 7,
		usageLocations: ["page-1"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},

	// Deprecated
	{
		id: "old-btn",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "LegacyButton",
		displayName: "Legacy Button (Deprecated)",
		description: "Old button component - do not use",
		category: "atom",
		status: "deprecated",
		deprecationMessage:
			"Use Button component instead. This will be removed in v3.0",
		usageCount: 4,
		usageLocations: ["page-4"],
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},
	{
		id: "old-input",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "OldInput",
		displayName: "Old Input Field",
		description: "Legacy input - use Input instead",
		category: "atom",
		status: "deprecated",
		deprecationMessage: "Use Input component instead",
		usageCount: 2,
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
	},

	// Experimental
	{
		id: "new-table",
		libraryId: "ds-1",
		projectId: "proj-1",
		name: "DataTable",
		displayName: "Data Table",
		description: "New advanced data table component",
		category: "data-display",
		status: "experimental",
		usageCount: 1,
		createdAt: "2025-01-01T00:00:00Z",
		updatedAt: "2025-01-29T00:00:00Z",
		props: [
			{ name: "columns", type: "Column[]", required: true },
			{ name: "data", type: "Row[]", required: true },
			{ name: "sortable", type: "boolean", required: false },
			{ name: "filterable", type: "boolean", required: false },
		],
	},
];

const mockUsage: ComponentUsage[] = [
	// Button usage
	{
		id: "u1",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "btn-primary",
		usedInItemId: "page-1",
		usedInFilePath: "pages/dashboard.tsx",
		usedInLine: 45,
		variantUsed: "Primary",
		detectedAt: "2025-01-28T10:00:00Z",
	},
	{
		id: "u2",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "btn-primary",
		usedInItemId: "page-2",
		usedInFilePath: "pages/profile.tsx",
		usedInLine: 120,
		variantUsed: "Secondary",
		detectedAt: "2025-01-28T10:00:00Z",
	},
	{
		id: "u3",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "btn-primary",
		usedInItemId: "page-3",
		usedInFilePath: "pages/settings.tsx",
		usedInLine: 87,
		variantUsed: "Primary",
		detectedAt: "2025-01-28T10:00:00Z",
	},

	// Input usage
	{
		id: "u4",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "input-text",
		usedInItemId: "page-2",
		usedInFilePath: "pages/profile.tsx",
		usedInLine: 95,
		detectedAt: "2025-01-28T10:00:00Z",
	},
	{
		id: "u5",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "input-text",
		usedInItemId: "page-3",
		usedInFilePath: "pages/settings.tsx",
		usedInLine: 112,
		detectedAt: "2025-01-28T10:00:00Z",
	},

	// Legacy button
	{
		id: "u6",
		projectId: "proj-1",
		libraryId: "ds-1",
		componentId: "old-btn",
		usedInItemId: "page-4",
		usedInFilePath: "pages/legacy.tsx",
		usedInLine: 30,
		detectedAt: "2025-01-28T10:00:00Z",
	},
];

const mockPages = [
	"pages/dashboard.tsx",
	"pages/profile.tsx",
	"pages/settings.tsx",
	"pages/legacy.tsx",
];

// =============================================================================
// STORIES
// =============================================================================

export const Default: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
	},
};

export const WithSearch: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		enableFiltering: true,
	},
};

export const HighlightUnused: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		highlightUnused: true,
	},
	parameters: {
		docs: {
			description: {
				story:
					"Unused and deprecated components are highlighted with special colors",
			},
		},
	},
};

export const WithVariantsAndProps: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		showVariants: true,
		showProps: true,
	},
	parameters: {
		docs: {
			description: {
				story: "Component rows can be expanded to show variants and props",
			},
		},
	},
};

export const CustomPageLabels: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		pageLabels: {
			"pages/dashboard.tsx": "Dashboard",
			"pages/profile.tsx": "User Profile",
			"pages/settings.tsx": "Settings",
			"pages/legacy.tsx": "Legacy System",
		},
		showVariants: true,
		showProps: true,
	},
	parameters: {
		docs: {
			description: {
				story: "Custom labels can be provided for page names",
			},
		},
	},
};

export const NoFiltering: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		enableFiltering: false,
	},
	parameters: {
		docs: {
			description: {
				story: "Filtering controls can be disabled",
			},
		},
	},
};

export const LoadingState: Story = {
	args: {
		components: [],
		usage: [],
		pages: [],
		isLoading: true,
	},
};

export const Empty: Story = {
	args: {
		components: [],
		usage: [],
		pages: [],
		enableFiltering: true,
	},
	parameters: {
		docs: {
			description: {
				story: "Shows when no components are available",
			},
		},
	},
};

export const OnlyAtoms: Story = {
	args: {
		components: mockComponents.filter((c) => c.category === "atom"),
		usage: mockUsage,
		pages: mockPages,
		selectedCategory: "atom",
	},
	parameters: {
		docs: {
			description: {
				story: "Filtered to show only atom components",
			},
		},
	},
};

export const WithCallbacks: Story = {
	args: {
		components: mockComponents,
		usage: mockUsage,
		pages: mockPages,
		onSelectComponent: (componentId) => {
			alert(`Selected component: ${componentId}`);
		},
		onCategoryChange: (category) => {
			alert(`Changed category to: ${category}`);
		},
		onViewInCode: (componentId) => {
			alert(`View in code: ${componentId}`);
		},
	},
	parameters: {
		docs: {
			description: {
				story: "All callback props are functional",
			},
		},
	},
};
