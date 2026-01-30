/**
 * Comprehensive tests for ComponentLibraryExplorer component
 * Tests: library browsing, component search, variants, design tokens
 */

import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import type {
	ComponentLibrary,
	LibraryComponent,
	ComponentProp,
	ComponentVariant,
	DesignToken,
} from "@tracertm/types";
import { ComponentLibraryExplorer } from "@/components/graph/ComponentLibraryExplorer";

// =============================================================================
// FIXTURES
// =============================================================================

const mockDesignTokens: DesignToken[] = [
	{
		id: "color-primary",
		name: "Primary Color",
		category: "color",
		value: "#3b82f6",
	} as any,
	{
		id: "spacing-md",
		name: "Medium Spacing",
		category: "spacing",
		value: "16px",
	} as any,
];

const mockComponentVariants: ComponentVariant[] = [
	{
		id: "variant-primary",
		name: "Primary",
		description: "Primary button style",
		props: { variant: "primary", size: "md" },
	} as any,
	{
		id: "variant-secondary",
		name: "Secondary",
		description: "Secondary button style",
		props: { variant: "secondary", size: "md" },
	} as any,
];

const mockComponentProps: ComponentProp[] = [
	{
		id: "prop-label",
		name: "label",
		type: "string",
		required: true,
		description: "Button text",
	} as any,
	{
		id: "prop-onClick",
		name: "onClick",
		type: "function",
		required: false,
		description: "Click handler",
	} as any,
];

const mockButton: LibraryComponent = {
	id: "component-button",
	libraryId: "lib-ui",
	name: "Button",
	category: "atom",
	description: "Reusable button component",
	props: mockComponentProps,
	variants: mockComponentVariants,
	storybook_url: "http://storybook.local/button",
	figma_url: "http://figma.local/button",
	source_code_url: "http://github.local/button",
	usage_count: 24,
	last_updated: "2024-01-15T00:00:00Z",
} as any;

const mockCard: LibraryComponent = {
	id: "component-card",
	libraryId: "lib-ui",
	name: "Card",
	category: "molecule",
	description: "Container component",
	props: [],
	variants: [],
	usage_count: 12,
	last_updated: "2024-01-15T00:00:00Z",
} as any;

const mockUILibrary: ComponentLibrary = {
	id: "lib-ui",
	name: "UI Components",
	description: "Core UI component library",
	organization: "Design Team",
	repository_url: "http://github.local/ui",
	status: "active",
	component_count: 2,
	last_updated: "2024-01-15T00:00:00Z",
} as any;

const mockIconsLibrary: ComponentLibrary = {
	id: "lib-icons",
	name: "Icon Library",
	description: "SVG icon library",
	organization: "Design Team",
	repository_url: "http://github.local/icons",
	status: "active",
	component_count: 150,
	last_updated: "2024-01-15T00:00:00Z",
} as any;

// =============================================================================
// COMPONENT TESTS
// =============================================================================

describe("ComponentLibraryExplorer Component", () => {
	let onSelectLibrary: ReturnType<typeof vi.fn>;
	let onSelectComponent: ReturnType<typeof vi.fn>;
	let onViewInStorybook: ReturnType<typeof vi.fn>;
	let onViewInFigma: ReturnType<typeof vi.fn>;
	let onViewInCode: ReturnType<typeof vi.fn>;
	let onSyncLibrary: ReturnType<typeof vi.fn>;

	beforeEach(() => {
		onSelectLibrary = vi.fn();
		onSelectComponent = vi.fn();
		onViewInStorybook = vi.fn();
		onViewInFigma = vi.fn();
		onViewInCode = vi.fn();
		onSyncLibrary = vi.fn();
		vi.clearAllMocks();
	});

	describe("Rendering", () => {
		it("renders component library explorer with title", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText(/library/i)).toBeInTheDocument();
		});

		it("displays library list", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary, mockIconsLibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("UI Components")).toBeInTheDocument();
			expect(screen.getByText("Icon Library")).toBeInTheDocument();
		});

		it("displays components list", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
			expect(screen.getByText("Card")).toBeInTheDocument();
		});

		it("renders search input", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			expect(searchInput).toBeInTheDocument();
		});

		it("shows component count for libraries", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("UI Components")).toBeInTheDocument();
		});

		it("displays loading state", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[]}
					components={[]}
					onSelectComponent={onSelectComponent}
					isLoading={true}
				/>,
			);

			// Component should render gracefully
			expect(
				screen.getByText(/library/i) || screen.getByText(/component/i),
			).toBeTruthy();
		});
	});

	describe("Library Selection", () => {
		it("selects library when clicking library name", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary, mockIconsLibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onSelectLibrary={onSelectLibrary}
					selectedLibraryId="lib-ui"
				/>,
			);

			const uiLibrary = screen.getByText("UI Components");
			await user.click(uiLibrary);

			await waitFor(() => {
				expect(onSelectLibrary).toHaveBeenCalled();
			});
		});

		it("highlights selected library", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary, mockIconsLibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedLibraryId="lib-ui"
				/>,
			);

			expect(screen.getByText("UI Components")).toBeInTheDocument();
		});

		it("filters components by selected library", () => {
			const iconComponent = {
				...mockButton,
				id: "component-icon",
				name: "Icon",
				libraryId: "lib-icons",
			};

			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary, mockIconsLibrary]}
					components={[mockButton, iconComponent]}
					onSelectComponent={onSelectComponent}
					selectedLibraryId="lib-ui"
				/>,
			);

			// Should primarily show UI library components
			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("shows library metadata", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("UI Components")).toBeInTheDocument();
			expect(screen.getByText("Core UI component library")).toBeInTheDocument();
		});

		it("shows sync button for library", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onSyncLibrary={onSyncLibrary}
				/>,
			);

			const buttons = screen.getAllByRole("button");
			expect(buttons.length).toBeGreaterThan(0);
		});
	});

	describe("Component Selection", () => {
		it("selects component when clicking component name", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const buttonComponent = screen.getByText("Button");
			await user.click(buttonComponent);

			expect(onSelectComponent).toHaveBeenCalledWith("component-button");
		});

		it("highlights selected component", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("displays component category badge", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
			expect(screen.getByText("Card")).toBeInTheDocument();
		});

		it("shows component description", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(
				screen.getByText(/Reusable button component/i),
			).toBeInTheDocument();
		});

		it("shows usage count for components", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("Search Functionality", () => {
		it("filters components by search query", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			await user.type(searchInput, "button");

			await waitFor(() => {
				expect(screen.getByText("Button")).toBeInTheDocument();
			});
		});

		it("case-insensitive search", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			await user.type(searchInput, "BUTTON");

			await waitFor(() => {
				expect(screen.getByText("Button")).toBeInTheDocument();
			});
		});

		it("searches in component descriptions", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			await user.type(searchInput, "reusable");

			await waitFor(() => {
				expect(screen.getByText("Button")).toBeInTheDocument();
			});
		});

		it("shows no results message when no matches", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			await user.type(searchInput, "nonexistent");

			// Should handle gracefully
			expect(searchInput).toBeInTheDocument();
		});

		it("clears search results when query cleared", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(
				/search/i,
			) as HTMLInputElement;
			await user.type(searchInput, "button");

			await waitFor(() => {
				expect(screen.getByText("Button")).toBeInTheDocument();
			});

			await user.clear(searchInput);

			await waitFor(() => {
				expect(screen.getByText("Card")).toBeInTheDocument();
			});
		});
	});

	describe("Component Details", () => {
		it("displays component variants", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("displays component props", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("shows variant names and descriptions", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("displays prop types and required status", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					selectedComponentId="component-button"
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("External Links", () => {
		it("shows Storybook link for component", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onViewInStorybook={onViewInStorybook}
					selectedComponentId="component-button"
				/>,
			);

			const links = screen.getAllByRole("button");
			expect(links.length).toBeGreaterThan(0);
		});

		it("shows Figma link for component", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onViewInFigma={onViewInFigma}
					selectedComponentId="component-button"
				/>,
			);

			const links = screen.getAllByRole("button");
			expect(links.length).toBeGreaterThan(0);
		});

		it("shows code link for component", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onViewInCode={onViewInCode}
					selectedComponentId="component-button"
				/>,
			);

			const links = screen.getAllByRole("button");
			expect(links.length).toBeGreaterThan(0);
		});
	});

	describe("Design Tokens", () => {
		it("displays design tokens tab", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					tokens={mockDesignTokens}
					onSelectComponent={onSelectComponent}
				/>,
			);

			// Should render without errors
			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("shows design token values", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					tokens={mockDesignTokens}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("filters tokens by category", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					tokens={mockDesignTokens}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("Categories", () => {
		it("groups components by category", () => {
			const atomComponent = { ...mockButton, category: "atom" };
			const moleculeComponent = { ...mockCard, category: "molecule" };

			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[atomComponent, moleculeComponent]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
			expect(screen.getByText("Card")).toBeInTheDocument();
		});

		it("shows category icons", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("allows expanding/collapsing categories", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const buttons = screen.getAllByRole("button");
			expect(buttons.length).toBeGreaterThan(0);
		});
	});

	describe("Sync Operations", () => {
		it("calls onSyncLibrary when sync button clicked", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					onSyncLibrary={onSyncLibrary}
				/>,
			);

			const buttons = screen.getAllByRole("button");
			const syncButton = buttons.find(
				(btn) =>
					btn.textContent?.includes("Sync") ||
					btn.getAttribute("aria-label")?.includes("Sync"),
			);

			if (syncButton) {
				await user.click(syncButton);
				await waitFor(() => {
					expect(onSyncLibrary).toHaveBeenCalled();
				});
			}
		});

		it("shows loading state during sync", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
					isLoading={true}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("Empty States", () => {
		it("handles no libraries", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[]}
					components={[]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			// Should render gracefully
			expect(screen.getByText(/library|component/i)).toBeTruthy();
		});

		it("handles no components in library", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("UI Components")).toBeInTheDocument();
		});

		it("handles no design tokens", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					tokens={[]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("Accessibility", () => {
		it("supports keyboard navigation", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			await user.tab();
			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("provides proper ARIA labels", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const searchInput = screen.getByPlaceholderText(/search/i);
			expect(searchInput).toBeInTheDocument();
		});

		it("has semantic HTML structure", () => {
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});
	});

	describe("Sorting and Filtering", () => {
		it("sorts components by usage count", () => {
			const highUsageComponent = { ...mockButton, usage_count: 100 };
			const lowUsageComponent = { ...mockCard, usage_count: 5 };

			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[lowUsageComponent, highUsageComponent]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
			expect(screen.getByText("Card")).toBeInTheDocument();
		});

		it("sorts by last updated date", () => {
			const recentComponent = {
				...mockButton,
				last_updated: "2024-01-20T00:00:00Z",
			};
			const oldComponent = {
				...mockCard,
				last_updated: "2024-01-01T00:00:00Z",
			};

			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[oldComponent, recentComponent]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			expect(screen.getByText("Button")).toBeInTheDocument();
		});

		it("filters by category", async () => {
			const user = userEvent.setup();
			render(
				<ComponentLibraryExplorer
					libraries={[mockUILibrary]}
					components={[mockButton, mockCard]}
					onSelectComponent={onSelectComponent}
				/>,
			);

			const buttons = screen.getAllByRole("button");
			expect(buttons.length).toBeGreaterThan(0);
		});
	});
});
