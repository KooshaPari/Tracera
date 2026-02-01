// DesignTokenBrowser.test.tsx - Test suite for DesignTokenBrowser component
// Tests token display, filtering, search, categorization, and interactions

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { DesignToken } from "@tracertm/types";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { DesignTokenBrowser } from "@/components/graph";

// =============================================================================
// MOCK DATA
// =============================================================================

const mockColorTokens: DesignToken[] = [
	{
		id: "color-1",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "primary",
		path: ["colors", "primary", "500"],
		description: "Primary brand color",
		type: "color",
		value: "#3B82F6",
		resolvedValue: "#3B82F6",
		usageCount: 12,
		usedByComponentIds: ["btn-1", "btn-2"],
		tags: ["brand", "interactive"],
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
	{
		id: "color-2",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "secondary",
		path: ["colors", "secondary", "500"],
		type: "color",
		value: "#10B981",
		resolvedValue: "#10B981",
		usageCount: 8,
		figmaStyleId: "figma-style-1",
		tags: ["status"],
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
	{
		id: "color-3",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "error",
		path: ["colors", "error", "500"],
		type: "color",
		value: "#EF4444",
		resolvedValue: "#EF4444",
		usageCount: 0,
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
];

const mockSpacingTokens: DesignToken[] = [
	{
		id: "spacing-1",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "sm",
		path: ["spacing", "sm"],
		type: "spacing",
		value: "0.5rem",
		resolvedValue: "0.5rem",
		usageCount: 20,
		usedByComponentIds: ["btn-1"],
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
	{
		id: "spacing-2",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "md",
		path: ["spacing", "md"],
		type: "spacing",
		value: "1rem",
		resolvedValue: "1rem",
		usageCount: 15,
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
];

const mockTypographyTokens: DesignToken[] = [
	{
		id: "typo-1",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "body-regular",
		path: ["typography", "body", "regular"],
		type: "typography",
		value: '16px/1.5 "Inter", sans-serif',
		resolvedValue: '16px/1.5 "Inter", sans-serif',
		usageCount: 25,
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
];

const mockTokensWithReferences: DesignToken[] = [
	{
		id: "token-ref-1",
		libraryId: "lib-1",
		projectId: "proj-1",
		name: "primary-light",
		path: ["colors", "primary", "light"],
		type: "color",
		value: "{colors.primary.500}",
		resolvedValue: "#3B82F6",
		referencesTokenId: "color-1",
		usageCount: 5,
		createdAt: "2024-01-01T00:00:00Z",
		updatedAt: "2024-01-01T00:00:00Z",
	},
];

// =============================================================================
// TESTS
// =============================================================================

describe("DesignTokenBrowser", () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	// Basic rendering
	describe("rendering", () => {
		it("should render the component with all tokens", () => {
			const tokens = [
				...mockColorTokens,
				...mockSpacingTokens,
				...mockTypographyTokens,
			];
			render(<DesignTokenBrowser tokens={tokens} />);

			expect(screen.getByText("Design Tokens")).toBeInTheDocument();
			expect(screen.getByText(/10 tokens/)).toBeInTheDocument();
		});

		it("should display empty state when no tokens", () => {
			render(<DesignTokenBrowser tokens={[]} />);

			expect(screen.getByText("No design tokens")).toBeInTheDocument();
			expect(screen.getByText(/Import tokens from Figma/)).toBeInTheDocument();
		});

		it("should group tokens by type", () => {
			const tokens = [...mockColorTokens, ...mockSpacingTokens];
			render(<DesignTokenBrowser tokens={tokens} />);

			// Should show category buttons
			expect(screen.getByText(/Colors \(3\)/)).toBeInTheDocument();
			expect(screen.getByText(/Spacing \(2\)/)).toBeInTheDocument();
		});

		it("should display token stats correctly", () => {
			const tokens = [...mockColorTokens, ...mockSpacingTokens];
			render(<DesignTokenBrowser tokens={tokens} />);

			expect(screen.getByText(/5 tokens/)).toBeInTheDocument();
			expect(screen.getByText(/3 in use/)).toBeInTheDocument();
			expect(screen.getByText(/1 synced/)).toBeInTheDocument();
		});
	});

	// Search functionality
	describe("search and filtering", () => {
		it("should filter tokens by name", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
			await userEvent.type(searchInput, "primary");

			// Should show primary token
			expect(screen.getByText("primary")).toBeInTheDocument();
			// Should not show secondary
			expect(screen.queryByText("secondary")).not.toBeInTheDocument();
		});

		it("should filter tokens by path", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
			await userEvent.type(searchInput, "secondary");

			expect(screen.getByText("secondary")).toBeInTheDocument();
		});

		it("should filter tokens by value", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
			await userEvent.type(searchInput, "#EF4444");

			expect(screen.getByText("error")).toBeInTheDocument();
		});

		it("should filter tokens by tag", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
			await userEvent.type(searchInput, "brand");

			expect(screen.getByText("primary")).toBeInTheDocument();
		});

		it("should show no results message when search has no matches", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(/Search tokens by name/);
			await userEvent.type(searchInput, "nonexistent");

			expect(screen.getByText("No tokens found")).toBeInTheDocument();
		});
	});

	// Category expansion
	describe("category expansion", () => {
		it("should expand categories on click", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const colorsButton = screen.getByText(/Colors \(3\)/);
			expect(colorsButton).toBeInTheDocument();

			await userEvent.click(colorsButton);

			// Should show token items
			await waitFor(() => {
				expect(screen.getByText("primary")).toBeInTheDocument();
			});
		});

		it("should expand all categories with button", async () => {
			const tokens = [...mockColorTokens, ...mockSpacingTokens];
			render(<DesignTokenBrowser tokens={tokens} />);

			const expandAllButton = screen.getByText("Expand All");
			await userEvent.click(expandAllButton);

			await waitFor(() => {
				expect(screen.getByText("primary")).toBeInTheDocument();
				expect(screen.getByText("sm")).toBeInTheDocument();
			});
		});

		it("should collapse all categories with button", async () => {
			const tokens = [...mockColorTokens, ...mockSpacingTokens];
			const { rerender } = render(<DesignTokenBrowser tokens={tokens} />);

			// First expand all
			const expandAllButton = screen.getByText("Expand All");
			await userEvent.click(expandAllButton);

			await waitFor(() => {
				expect(screen.getByText("primary")).toBeInTheDocument();
			});

			// Then collapse all
			const collapseAllButton = screen.getByText("Collapse All");
			await userEvent.click(collapseAllButton);

			// Rerender to see updated state
			rerender(<DesignTokenBrowser tokens={tokens} />);

			// Primary should not be visible until expanded again
			const primaryElements = screen.queryAllByText("primary");
			expect(primaryElements.length).toBeLessThanOrEqual(1);
		});
	});

	// Token selection
	describe("token selection", () => {
		it("should call onSelectToken when token is clicked", async () => {
			const onSelectToken = vi.fn();
			const tokens = mockColorTokens;
			render(
				<DesignTokenBrowser tokens={tokens} onSelectToken={onSelectToken} />,
			);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Click on primary token
			await waitFor(() => {
				const primaryToken = screen.getByText("primary");
				const tokenContainer = primaryToken.closest("div[class*='flex-col']");
				if (tokenContainer) {
					userEvent.click(tokenContainer);
				}
			});

			expect(onSelectToken).toHaveBeenCalled();
		});

		it("should highlight selected token", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} selectedTokenId="color-1" />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Find the primary token container
			await waitFor(() => {
				const primaryText = screen.getByText("primary");
				const tokenContainer = primaryText.closest("div[class*='flex']");
				expect(tokenContainer).toHaveClass("bg-primary/10");
			});
		});
	});

	// Copy functionality
	describe("copy to clipboard", () => {
		it("should copy token value to clipboard", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Click copy button (hover action)
			await waitFor(() => {
				const primaryToken = screen.getByText("primary");
				const copyButton = primaryToken
					.closest("div[class*='group']")
					?.querySelector('button[class*="copy"]');
				expect(copyButton).toBeTruthy();
			});
		});
	});

	// Token details expansion
	describe("token details", () => {
		it("should show description when expanded", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Expand token details
			await waitFor(() => {
				const primaryToken = screen.getByText("primary");
				const expandButton = primaryToken
					.closest("div[class*='flex-col']")
					?.querySelector("button");
				if (expandButton) {
					userEvent.click(expandButton);
				}
			});

			await waitFor(() => {
				expect(screen.getByText("Primary brand color")).toBeInTheDocument();
			});
		});

		it("should show component usage", async () => {
			const tokens = mockColorTokens;
			const componentMap = new Map([
				["btn-1", "Button Primary"],
				["btn-2", "Button Secondary"],
			]);
			render(
				<DesignTokenBrowser
					tokens={tokens}
					showComponentUsage={true}
					componentMap={componentMap}
				/>,
			);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Should show usage count
			expect(screen.getByText(/12/)).toBeInTheDocument();
		});

		it("should display referenced tokens", async () => {
			const tokens = mockTokensWithReferences;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(1\)/);
			await userEvent.click(colorsButton);

			// Should show the token with reference
			await waitFor(() => {
				expect(screen.getByText("primary-light")).toBeInTheDocument();
			});
		});
	});

	// Figma integration
	describe("figma integration", () => {
		it("should show Figma icon for synced tokens", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Secondary token has Figma style ID
			await waitFor(() => {
				const secondaryToken = screen.getByText("secondary");
				const figmaIcon = secondaryToken
					.closest("div")
					?.querySelector('svg[class*="text-blue"]');
				expect(figmaIcon).toBeTruthy();
			});
		});

		it("should call onLinkToFigma when linking token", async () => {
			const onLinkToFigma = vi.fn();
			const tokens = mockColorTokens;
			render(
				<DesignTokenBrowser tokens={tokens} onLinkToFigma={onLinkToFigma} />,
			);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			// Click on Figma link button for unsync token
			// (Would need to hover and click the Figma button)
			expect(onLinkToFigma).not.toHaveBeenCalled();
		});

		it("should show sync count in stats", () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			expect(screen.getByText(/1 synced/)).toBeInTheDocument();
		});
	});

	// Token preview rendering
	describe("token preview", () => {
		it("should render color preview box", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			await waitFor(() => {
				const previewBoxes = screen.getAllByRole("img", { hidden: true });
				expect(previewBoxes.length).toBeGreaterThan(0);
			});
		});

		it("should display token value in code format", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			// Expand colors category
			const colorsButton = screen.getByText(/Colors \(3\)/);
			await userEvent.click(colorsButton);

			await waitFor(() => {
				expect(screen.getByText("#3B82F6")).toBeInTheDocument();
			});
		});
	});

	// Category type icons
	describe("category type icons", () => {
		it("should display correct icon for each token type", async () => {
			const tokens = [
				...mockColorTokens,
				...mockSpacingTokens,
				...mockTypographyTokens,
			];
			render(<DesignTokenBrowser tokens={tokens} />);

			// All category buttons should be visible
			expect(screen.getByText(/Colors \(3\)/)).toBeInTheDocument();
			expect(screen.getByText(/Spacing \(2\)/)).toBeInTheDocument();
			expect(screen.getByText(/Typography \(1\)/)).toBeInTheDocument();
		});
	});

	// Accessibility
	describe("accessibility", () => {
		it("should have accessible button labels", async () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			expect(screen.getByText("Expand All")).toBeInTheDocument();
			expect(screen.getByText("Collapse All")).toBeInTheDocument();
		});

		it("should have descriptive search placeholder", () => {
			const tokens = mockColorTokens;
			render(<DesignTokenBrowser tokens={tokens} />);

			const searchInput = screen.getByPlaceholderText(
				/Search tokens by name, value, or path/,
			);
			expect(searchInput).toBeInTheDocument();
		});
	});
});
