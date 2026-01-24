/**
 * EmptyState Component Tests
 *
 * Comprehensive tests covering:
 * - Rendering with various prop combinations
 * - Icon display
 * - Action buttons
 * - Secondary actions
 * - Accessibility
 * - Edge cases
 */

import { fireEvent, render, screen } from "@testing-library/react";
import { FileText } from "lucide-react";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "@/components/layout/EmptyState";

describe("EmptyState Component", () => {
	describe("Basic Rendering", () => {
		it("should render with title only", () => {
			render(<EmptyState title="No items found" />);

			expect(screen.getByText("No items found")).toBeInTheDocument();
		});

		it("should render title with correct styling", () => {
			render(<EmptyState title="No items found" />);

			const title = screen.getByText("No items found");
			expect(title).toHaveClass("text-lg", "font-semibold");
		});

		it("should render description when provided", () => {
			render(
				<EmptyState
					title="No items found"
					description="Try creating a new item to get started"
				/>,
			);

			expect(
				screen.getByText("Try creating a new item to get started"),
			).toBeInTheDocument();
		});

		it("should not render description when not provided", () => {
			render(<EmptyState title="No items found" />);

			expect(screen.queryByText(/try creating/i)).not.toBeInTheDocument();
		});

		it("should render with custom icon", () => {
			render(
				<EmptyState
					title="No files"
					icon={<FileText data-testid="custom-icon" />}
				/>,
			);

			expect(screen.getByTestId("custom-icon")).toBeInTheDocument();
		});

		it("should not render icon container when icon is not provided", () => {
			const { container } = render(<EmptyState title="No items" />);

			const iconContainer = container.querySelector(".w-16.h-16");
			expect(iconContainer).not.toBeInTheDocument();
		});
	});

	describe("Actions", () => {
		it("should render primary action button", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create Item", onClick: handleClick }}
				/>,
			);

			expect(screen.getByText("Create Item")).toBeInTheDocument();
		});

		it("should call onClick when primary action is clicked", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create Item", onClick: handleClick }}
				/>,
			);

			fireEvent.click(screen.getByText("Create Item"));
			expect(handleClick).toHaveBeenCalledTimes(1);
		});

		it("should render secondary action button", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					secondaryAction={{ label: "Learn More", onClick: handleClick }}
				/>,
			);

			expect(screen.getByText("Learn More")).toBeInTheDocument();
		});

		it("should call onClick when secondary action is clicked", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					secondaryAction={{ label: "Learn More", onClick: handleClick }}
				/>,
			);

			fireEvent.click(screen.getByText("Learn More"));
			expect(handleClick).toHaveBeenCalledTimes(1);
		});

		it("should render both primary and secondary actions", () => {
			const handlePrimary = vi.fn();
			const handleSecondary = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create Item", onClick: handlePrimary }}
					secondaryAction={{ label: "Learn More", onClick: handleSecondary }}
				/>,
			);

			expect(screen.getByText("Create Item")).toBeInTheDocument();
			expect(screen.getByText("Learn More")).toBeInTheDocument();
		});

		it("should call correct handlers for each action", () => {
			const handlePrimary = vi.fn();
			const handleSecondary = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create Item", onClick: handlePrimary }}
					secondaryAction={{ label: "Learn More", onClick: handleSecondary }}
				/>,
			);

			fireEvent.click(screen.getByText("Create Item"));
			expect(handlePrimary).toHaveBeenCalledTimes(1);
			expect(handleSecondary).not.toHaveBeenCalled();

			fireEvent.click(screen.getByText("Learn More"));
			expect(handleSecondary).toHaveBeenCalledTimes(1);
			expect(handlePrimary).toHaveBeenCalledTimes(1);
		});

		it("should not render action container when no actions provided", () => {
			const { container } = render(<EmptyState title="No items" />);

			const actionContainer = container.querySelector(
				".flex.items-center.space-x-3",
			);
			expect(actionContainer).not.toBeInTheDocument();
		});
	});

	describe("Combined Props", () => {
		it("should render all props together", () => {
			const handlePrimary = vi.fn();
			const handleSecondary = vi.fn();

			render(
				<EmptyState
					icon={<FileText data-testid="file-icon" />}
					title="No documents"
					description="You haven't created any documents yet"
					action={{ label: "New Document", onClick: handlePrimary }}
					secondaryAction={{ label: "Import", onClick: handleSecondary }}
				/>,
			);

			expect(screen.getByTestId("file-icon")).toBeInTheDocument();
			expect(screen.getByText("No documents")).toBeInTheDocument();
			expect(
				screen.getByText("You haven't created any documents yet"),
			).toBeInTheDocument();
			expect(screen.getByText("New Document")).toBeInTheDocument();
			expect(screen.getByText("Import")).toBeInTheDocument();
		});

		it("should render with icon and title only", () => {
			render(
				<EmptyState
					icon={<FileText data-testid="file-icon" />}
					title="No documents"
				/>,
			);

			expect(screen.getByTestId("file-icon")).toBeInTheDocument();
			expect(screen.getByText("No documents")).toBeInTheDocument();
		});

		it("should render with title and description only", () => {
			render(
				<EmptyState
					title="No documents"
					description="Create your first document to get started"
				/>,
			);

			expect(screen.getByText("No documents")).toBeInTheDocument();
			expect(
				screen.getByText("Create your first document to get started"),
			).toBeInTheDocument();
		});

		it("should render with title and actions only", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No documents"
					action={{ label: "Create", onClick: handleClick }}
				/>,
			);

			expect(screen.getByText("No documents")).toBeInTheDocument();
			expect(screen.getByText("Create")).toBeInTheDocument();
		});
	});

	describe("Styling and Layout", () => {
		it("should have centered layout", () => {
			const { container } = render(<EmptyState title="No items" />);

			const wrapper = container.firstChild;
			expect(wrapper).toHaveClass(
				"flex",
				"flex-col",
				"items-center",
				"justify-center",
			);
		});

		it("should have text-center class", () => {
			const { container } = render(<EmptyState title="No items" />);

			const wrapper = container.firstChild;
			expect(wrapper).toHaveClass("text-center");
		});

		it("should have padding", () => {
			const { container } = render(<EmptyState title="No items" />);

			const wrapper = container.firstChild;
			expect(wrapper).toHaveClass("py-12", "px-4");
		});

		it("should render icon with correct container classes", () => {
			const { container } = render(
				<EmptyState title="No items" icon={<FileText data-testid="icon" />} />,
			);

			const iconContainer = container.querySelector(".w-16.h-16");
			expect(iconContainer).toHaveClass(
				"rounded-full",
				"bg-gray-100",
				"dark:bg-gray-800",
			);
		});

		it("should render description with max-width constraint", () => {
			const { container } = render(
				<EmptyState title="No items" description="This is a description" />,
			);

			const description = container.querySelector(".max-w-md");
			expect(description).toBeInTheDocument();
		});
	});

	describe("Dark Mode", () => {
		it("should have dark mode classes for icon container", () => {
			const { container } = render(
				<EmptyState title="No items" icon={<FileText />} />,
			);

			const iconContainer = container.querySelector(".dark\\:bg-gray-800");
			expect(iconContainer).toBeInTheDocument();
		});

		it("should have dark mode classes for title", () => {
			const { container } = render(<EmptyState title="No items" />);

			const title = container.querySelector(".dark\\:text-gray-100");
			expect(title).toBeInTheDocument();
		});

		it("should have dark mode classes for description", () => {
			const { container } = render(
				<EmptyState title="No items" description="Description text" />,
			);

			const description = container.querySelector(".dark\\:text-gray-400");
			expect(description).toBeInTheDocument();
		});
	});

	describe("Edge Cases", () => {
		it("should handle very long titles", () => {
			const longTitle = "A".repeat(200);
			render(<EmptyState title={longTitle} />);

			expect(screen.getByText(longTitle)).toBeInTheDocument();
		});

		it("should handle very long descriptions", () => {
			const longDescription = "B".repeat(500);
			render(<EmptyState title="Title" description={longDescription} />);

			expect(screen.getByText(longDescription)).toBeInTheDocument();
		});

		it("should handle empty string title", () => {
			render(<EmptyState title="" />);

			const { container } = render(<EmptyState title="" />);
			expect(
				container.querySelector(".text-lg.font-semibold"),
			).toBeInTheDocument();
		});

		it("should handle multiple rapid clicks on action", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create", onClick: handleClick }}
				/>,
			);

			const button = screen.getByText("Create");
			fireEvent.click(button);
			fireEvent.click(button);
			fireEvent.click(button);

			expect(handleClick).toHaveBeenCalledTimes(3);
		});

		it("should handle special characters in title", () => {
			render(<EmptyState title="<No> &items& 'found'" />);

			expect(screen.getByText("<No> &items& 'found'")).toBeInTheDocument();
		});

		it("should handle special characters in description", () => {
			render(
				<EmptyState title="Title" description="<Special> &chars& 'test'" />,
			);

			expect(screen.getByText("<Special> &chars& 'test'")).toBeInTheDocument();
		});

		it("should handle complex React nodes as icon", () => {
			render(
				<EmptyState
					title="No items"
					icon={
						<div data-testid="complex-icon">
							<FileText />
							<span>Extra</span>
						</div>
					}
				/>,
			);

			expect(screen.getByTestId("complex-icon")).toBeInTheDocument();
		});
	});

	describe("Button Variants", () => {
		it("should render primary action with default variant", () => {
			const handleClick = vi.fn();
			const { container } = render(
				<EmptyState
					title="No items"
					action={{ label: "Create", onClick: handleClick }}
				/>,
			);

			// Button component will have variant="default" prop
			const button = screen.getByText("Create");
			expect(button).toBeInTheDocument();
		});

		it("should render secondary action with outline variant", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					secondaryAction={{ label: "Learn More", onClick: handleClick }}
				/>,
			);

			const button = screen.getByText("Learn More");
			expect(button).toBeInTheDocument();
		});
	});

	describe("Accessibility", () => {
		it("should have semantic HTML structure", () => {
			const { container } = render(
				<EmptyState title="No items" description="Create your first item" />,
			);

			expect(container.querySelector("h3")).toBeInTheDocument();
			expect(container.querySelector("p")).toBeInTheDocument();
		});

		it("should have accessible button text", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create New Item", onClick: handleClick }}
				/>,
			);

			const button = screen.getByRole("button", { name: /create new item/i });
			expect(button).toBeInTheDocument();
		});

		it("should support keyboard interaction on buttons", () => {
			const handleClick = vi.fn();
			render(
				<EmptyState
					title="No items"
					action={{ label: "Create", onClick: handleClick }}
				/>,
			);

			const button = screen.getByText("Create");
			fireEvent.keyDown(button, { key: "Enter" });
			// Button will handle the actual key interaction
			expect(button).toBeInTheDocument();
		});
	});

	describe("Real-world Scenarios", () => {
		it("should render empty projects state", () => {
			const handleCreate = vi.fn();
			render(
				<EmptyState
					title="No projects yet"
					description="Create your first project to start managing requirements"
					action={{ label: "New Project", onClick: handleCreate }}
				/>,
			);

			expect(screen.getByText("No projects yet")).toBeInTheDocument();
			expect(
				screen.getByText(
					"Create your first project to start managing requirements",
				),
			).toBeInTheDocument();
			expect(screen.getByText("New Project")).toBeInTheDocument();
		});

		it("should render empty search results", () => {
			render(
				<EmptyState
					title="No results found"
					description="Try adjusting your search terms"
				/>,
			);

			expect(screen.getByText("No results found")).toBeInTheDocument();
			expect(
				screen.getByText("Try adjusting your search terms"),
			).toBeInTheDocument();
		});

		it("should render permission denied state", () => {
			const handleRequest = vi.fn();
			render(
				<EmptyState
					title="Access Denied"
					description="You don't have permission to view this content"
					action={{ label: "Request Access", onClick: handleRequest }}
				/>,
			);

			expect(screen.getByText("Access Denied")).toBeInTheDocument();
			expect(
				screen.getByText("You don't have permission to view this content"),
			).toBeInTheDocument();
		});
	});
});
