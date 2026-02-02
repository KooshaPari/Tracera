/**
 * PageHeader Component Tests
 *
 * Comprehensive tests covering:
 * - Title and description rendering
 * - Icon display
 * - Actions rendering
 * - Breadcrumbs navigation
 * - Layout and styling
 * - Edge cases
 */

import { render, screen } from "@testing-library/react";
import { FileText, Plus } from "lucide-react";
import { describe, expect, it } from "vitest";
import { PageHeader } from "@/components/layout/PageHeader";

describe("PageHeader Component", () => {
	describe("Basic Rendering", () => {
		it("should render with title only", () => {
			render(<PageHeader title="Dashboard" />);

			expect(screen.getByText("Dashboard")).toBeInTheDocument();
		});

		it("should render title with correct styling", () => {
			render(<PageHeader title="Dashboard" />);

			const title = screen.getByText("Dashboard");
			expect(title).toHaveClass("text-2xl", "font-bold");
		});

		it("should render description when provided", () => {
			render(
				<PageHeader
					title="Projects"
					description="Manage all your requirements projects"
				/>,
			);

			expect(
				screen.getByText("Manage all your requirements projects"),
			).toBeInTheDocument();
		});

		it("should not render description when not provided", () => {
			const { container } = render(<PageHeader title="Dashboard" />);

			const description = container.querySelector(".text-sm.text-gray-600");
			expect(description).not.toBeInTheDocument();
		});
	});

	describe("Icon Display", () => {
		it("should render icon when provided", () => {
			render(
				<PageHeader
					title="Documents"
					icon={<FileText data-testid="header-icon" />}
				/>,
			);

			expect(screen.getByTestId("header-icon")).toBeInTheDocument();
		});

		it("should not render icon container when icon not provided", () => {
			render(<PageHeader title="Dashboard" />);

			const iconContainer = container.querySelector(".w-10.h-10");
			expect(iconContainer).not.toBeInTheDocument();
		});

		it("should render icon with correct container styles", () => {
			render(
				<PageHeader
					title="Documents"
					icon={<FileText data-testid="header-icon" />}
				/>,
			);

			const iconContainer = container.querySelector(".w-10.h-10");
			expect(iconContainer).toHaveClass(
				"rounded-lg",
				"bg-primary-100",
				"dark:bg-primary-900",
			);
		});

		it("should render icon with proper color classes", () => {
			render(
				<PageHeader
					title="Documents"
					icon={<FileText data-testid="header-icon" />}
				/>,
			);

			const iconContainer = container.querySelector(".text-primary-600");
			expect(iconContainer).toBeInTheDocument();
		});
	});

	describe("Actions", () => {
		it("should render actions when provided", () => {
			render(
				<PageHeader
					title="Projects"
					actions={
						<button data-testid="create-button">
							<Plus /> Create
						</button>
					}
				/>,
			);

			expect(screen.getByTestId("create-button")).toBeInTheDocument();
		});

		it("should render multiple actions", () => {
			render(
				<PageHeader
					title="Projects"
					actions={
						<>
							<button data-testid="action-1">Action 1</button>
							<button data-testid="action-2">Action 2</button>
							<button data-testid="action-3">Action 3</button>
						</>
					}
				/>,
			);

			expect(screen.getByTestId("action-1")).toBeInTheDocument();
			expect(screen.getByTestId("action-2")).toBeInTheDocument();
			expect(screen.getByTestId("action-3")).toBeInTheDocument();
		});

		it("should not render actions container when actions not provided", () => {
			render(<PageHeader title="Dashboard" />);

			const actionsContainer = container.querySelector(
				".flex.items-center.space-x-2",
			);
			expect(actionsContainer).not.toBeInTheDocument();
		});

		it("should render complex action components", () => {
			render(
				<PageHeader
					title="Projects"
					actions={
						<div data-testid="complex-actions" className="flex gap-2">
							<button>Export</button>
							<button>Import</button>
						</div>
					}
				/>,
			);

			expect(screen.getByTestId("complex-actions")).toBeInTheDocument();
		});
	});

	describe("Breadcrumbs", () => {
		it("should render breadcrumbs when provided", () => {
			render(
				<PageHeader
					title="Project Details"
					breadcrumbs={[
						{ label: "Home", href: "/" },
						{ label: "Projects", href: "/projects" },
						{ label: "Project 1" },
					]}
				/>,
			);

			expect(screen.getByText("Home")).toBeInTheDocument();
			expect(screen.getByText("Projects")).toBeInTheDocument();
			expect(screen.getByText("Project 1")).toBeInTheDocument();
		});

		it("should render clickable breadcrumb links", () => {
			render(
				<PageHeader
					title="Project Details"
					breadcrumbs={[{ label: "Home", href: "/" }, { label: "Projects" }]}
				/>,
			);

			const homeLink = screen.getByText("Home");
			expect(homeLink).toBeInTheDocument();
			expect(homeLink.tagName).toBe("A");
			expect(homeLink).toHaveAttribute("href", "/");
		});

		it("should render current breadcrumb without link", () => {
			render(
				<PageHeader
					title="Project Details"
					breadcrumbs={[
						{ label: "Home", href: "/" },
						{ label: "Current Page" },
					]}
				/>,
			);

			const currentCrumb = screen.getByText("Current Page");
			expect(currentCrumb.tagName).toBe("SPAN");
			expect(currentCrumb).not.toHaveAttribute("href");
		});

		it("should render breadcrumb separators", () => {
			render(
				<PageHeader
					title="Project Details"
					breadcrumbs={[
						{ label: "Home", href: "/" },
						{ label: "Projects", href: "/projects" },
						{ label: "Current" },
					]}
				/>,
			);

			const separators = container.querySelectorAll("svg");
			// Should have 2 separators (between 3 items)
			expect(separators.length).toBeGreaterThanOrEqual(2);
		});

		it("should not render breadcrumbs when not provided", () => {
			render(<PageHeader title="Dashboard" />);

			const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
			expect(nav).not.toBeInTheDocument();
		});

		it("should not render breadcrumbs when empty array", () => {
			render(
				<PageHeader title="Dashboard" breadcrumbs={[]} />,
			);

			const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
			expect(nav).not.toBeInTheDocument();
		});

		it("should have proper breadcrumb styling", () => {
			render(
				<PageHeader
					title="Project Details"
					breadcrumbs={[{ label: "Home", href: "/" }, { label: "Projects" }]}
				/>,
			);

			const breadcrumbList = container.querySelector(
				".flex.items-center.space-x-2",
			);
			expect(breadcrumbList).toBeInTheDocument();
		});
	});

	describe("Combined Props", () => {
		it("should render all props together", () => {
			render(
				<PageHeader
					title="Project Details"
					description="View and manage project requirements"
					icon={<FileText data-testid="project-icon" />}
					breadcrumbs={[
						{ label: "Home", href: "/" },
						{ label: "Projects", href: "/projects" },
						{ label: "Project 1" },
					]}
					actions={<button data-testid="edit-button">Edit</button>}
				/>,
			);

			expect(screen.getByText("Project Details")).toBeInTheDocument();
			expect(
				screen.getByText("View and manage project requirements"),
			).toBeInTheDocument();
			expect(screen.getByTestId("project-icon")).toBeInTheDocument();
			expect(screen.getByText("Home")).toBeInTheDocument();
			expect(screen.getByTestId("edit-button")).toBeInTheDocument();
		});

		it("should render title and icon only", () => {
			render(
				<PageHeader title="Documents" icon={<FileText data-testid="icon" />} />,
			);

			expect(screen.getByText("Documents")).toBeInTheDocument();
			expect(screen.getByTestId("icon")).toBeInTheDocument();
		});

		it("should render title and description only", () => {
			render(
				<PageHeader
					title="Settings"
					description="Configure your application preferences"
				/>,
			);

			expect(screen.getByText("Settings")).toBeInTheDocument();
			expect(
				screen.getByText("Configure your application preferences"),
			).toBeInTheDocument();
		});
	});

	describe("Layout and Styling", () => {
		it("should have border at bottom", () => {
			render(<PageHeader title="Dashboard" />);

			const header = container.querySelector(".border-b");
			expect(header).toBeInTheDocument();
		});

		it("should have correct background color", () => {
			render(<PageHeader title="Dashboard" />);

			const header = container.querySelector(".bg-white");
			expect(header).toBeInTheDocument();
		});

		it("should have correct padding", () => {
			render(<PageHeader title="Dashboard" />);

			const contentContainer = container.querySelector(".px-6.py-4");
			expect(contentContainer).toBeInTheDocument();
		});

		it("should have flex layout for title and actions", () => {
			render(
				<PageHeader title="Dashboard" actions={<button>Action</button>} />,
			);

			const flexContainer = container.querySelector(
				".flex.items-start.justify-between",
			);
			expect(flexContainer).toBeInTheDocument();
		});
	});

	describe("Dark Mode", () => {
		it("should have dark mode classes for border", () => {
			render(<PageHeader title="Dashboard" />);

			const header = container.querySelector(".dark\\:border-gray-800");
			expect(header).toBeInTheDocument();
		});

		it("should have dark mode classes for background", () => {
			render(<PageHeader title="Dashboard" />);

			const header = container.querySelector(".dark\\:bg-gray-900");
			expect(header).toBeInTheDocument();
		});

		it("should have dark mode classes for title", () => {
			render(<PageHeader title="Dashboard" />);

			const title = screen.getByText("Dashboard");
			expect(title).toHaveClass("dark:text-gray-100");
		});

		it("should have dark mode classes for description", () => {
			render(<PageHeader title="Dashboard" description="Welcome back" />);

			const description = screen.getByText("Welcome back");
			expect(description).toHaveClass("dark:text-gray-400");
		});
	});

	describe("Edge Cases", () => {
		it("should handle very long titles", () => {
			const longTitle = "A".repeat(200);
			render(<PageHeader title={longTitle} />);

			expect(screen.getByText(longTitle)).toBeInTheDocument();
		});

		it("should handle very long descriptions", () => {
			const longDescription = "B".repeat(500);
			render(<PageHeader title="Title" description={longDescription} />);

			expect(screen.getByText(longDescription)).toBeInTheDocument();
		});

		it("should handle special characters in title", () => {
			render(<PageHeader title="<Project> & 'Details'" />);

			expect(screen.getByText("<Project> & 'Details'")).toBeInTheDocument();
		});

		it("should handle special characters in description", () => {
			render(<PageHeader title="Title" description="<Data> & 'information'" />);

			expect(screen.getByText("<Data> & 'information'")).toBeInTheDocument();
		});

		it("should handle empty string title", () => {
			render(<PageHeader title="" />);

			render(<PageHeader title="" />);
			const title = container.querySelector(".text-2xl");
			expect(title).toBeInTheDocument();
		});

		it("should handle complex React nodes in actions", () => {
			render(
				<PageHeader
					title="Dashboard"
					actions={
						<div data-testid="complex">
							<button>A</button>
							<div>B</div>
							<span>C</span>
						</div>
					}
				/>,
			);

			expect(screen.getByTestId("complex")).toBeInTheDocument();
		});

		it("should handle single breadcrumb", () => {
			render(
				<PageHeader title="Current Page" breadcrumbs={[{ label: "Home" }]} />,
			);

			expect(screen.getByText("Home")).toBeInTheDocument();
		});

		it("should handle breadcrumb without href", () => {
			render(
				<PageHeader
					title="Page"
					breadcrumbs={[{ label: "No Link 1" }, { label: "No Link 2" }]}
				/>,
			);

			expect(screen.getByText("No Link 1")).toBeInTheDocument();
			expect(screen.getByText("No Link 2")).toBeInTheDocument();
		});
	});

	describe("Accessibility", () => {
		it("should have semantic heading element", () => {
			render(<PageHeader title="Dashboard" />);

			const heading = container.querySelector("h1");
			expect(heading).toBeInTheDocument();
			expect(heading?.textContent).toBe("Dashboard");
		});

		it("should have proper breadcrumb navigation", () => {
			render(
				<PageHeader
					title="Page"
					breadcrumbs={[{ label: "Home", href: "/" }, { label: "Projects" }]}
				/>,
			);

			const nav = container.querySelector('nav[aria-label="Breadcrumb"]');
			expect(nav).toBeInTheDocument();
		});

		it("should have ordered list for breadcrumbs", () => {
			render(
				<PageHeader
					title="Page"
					breadcrumbs={[{ label: "Home", href: "/" }, { label: "Projects" }]}
				/>,
			);

			const ol = container.querySelector("ol");
			expect(ol).toBeInTheDocument();
		});

		it("should have descriptive link text", () => {
			render(
				<PageHeader
					title="Page"
					breadcrumbs={[
						{ label: "Home", href: "/" },
						{ label: "Projects", href: "/projects" },
					]}
				/>,
			);

			const homeLink = screen.getByText("Home");
			expect(homeLink).toHaveAttribute("href", "/");
		});
	});

	describe("Real-world Scenarios", () => {
		it("should render dashboard header", () => {
			render(
				<PageHeader
					title="Dashboard"
					description="Welcome to your TracerTM dashboard"
				/>,
			);

			expect(screen.getByText("Dashboard")).toBeInTheDocument();
			expect(
				screen.getByText("Welcome to your TracerTM dashboard"),
			).toBeInTheDocument();
		});

		it("should render project list header with action", () => {
			render(
				<PageHeader
					title="Projects"
					description="Manage all your requirements projects"
					actions={<button>New Project</button>}
				/>,
			);

			expect(screen.getByText("Projects")).toBeInTheDocument();
			expect(screen.getByText("New Project")).toBeInTheDocument();
		});

		it("should render nested page with breadcrumbs", () => {
			render(
				<PageHeader
					title="Feature Details"
					breadcrumbs={[
						{ label: "Dashboard", href: "/" },
						{ label: "Projects", href: "/projects" },
						{ label: "Project 1", href: "/projects/1" },
						{ label: "Features" },
					]}
					actions={<button>Edit</button>}
				/>,
			);

			expect(screen.getByText("Dashboard")).toBeInTheDocument();
			expect(screen.getByText("Projects")).toBeInTheDocument();
			expect(screen.getByText("Project 1")).toBeInTheDocument();
			expect(screen.getByText("Features")).toBeInTheDocument();
		});
	});
});
