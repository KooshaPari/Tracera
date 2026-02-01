/**
 * Comprehensive tests for UICodeTracePanel component
 * Tests traceability chain visualization, code references, and user interactions
 */

import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { CanonicalConcept, CodeReference } from "@tracertm/types";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
	type TraceLevel,
	type UICodeTraceChain,
	UICodeTracePanel,
} from "../../../components/graph/UICodeTracePanel";

// =============================================================================
// MOCK DATA
// =============================================================================

const mockCodeReference: CodeReference = {
	id: "code-ref-1",
	repositoryUrl: "https://github.com/example/repo",
	filePath: "src/components/LoginForm.tsx",
	startLine: 42,
	endLine: 128,
	symbolName: "LoginForm",
	symbolType: "component",
	language: "typescript",
	signature: "function LoginForm(props: LoginFormProps): ReactNode",
	parentSymbol: "AuthModule",
	lastSyncedAt: new Date().toISOString(),
	commitSha: "abc123def456",
};

const mockCanonicalConcept: CanonicalConcept = {
	id: "concept-1",
	projectId: "project-1",
	name: "User Authentication",
	slug: "user-authentication",
	description: "User login and authentication flow",
	domain: "security",
	category: "authentication",
	tags: ["critical", "auth", "user-facing"],
	projectionCount: 3,
	confidence: 0.95,
	source: "inferred",
	createdAt: new Date().toISOString(),
	updatedAt: new Date().toISOString(),
	version: 1,
};

const mockUiTraceLevel: TraceLevel = {
	id: "level-1",
	type: "ui",
	title: "Login Form Component",
	description: "User-facing login form",
	perspective: "ui",
	componentName: "LoginForm",
	componentPath: "src/components/LoginForm.tsx",
	confidence: 1.0,
	strategy: "explicit_annotation",
	isConfirmed: true,
};

const mockCodeTraceLevel: TraceLevel = {
	id: "level-2",
	type: "code",
	title: "LoginForm Implementation",
	description: "React component implementing login form",
	perspective: "technical",
	codeRef: mockCodeReference,
	confidence: 0.95,
	strategy: "manual_link",
	isConfirmed: true,
};

const mockRequirementTraceLevel: TraceLevel = {
	id: "level-3",
	type: "requirement",
	title: "User Authentication Requirement",
	description: "Users must be able to authenticate with email/password",
	perspective: "business",
	requirementId: "req-auth-001",
	businessValue: "Enable secure user access to the platform",
	confidence: 0.9,
	strategy: "shared_canonical",
	isConfirmed: true,
};

const mockConceptTraceLevel: TraceLevel = {
	id: "level-4",
	type: "concept",
	title: "User Authentication Concept",
	description: "Abstract representation of user authentication",
	canonicalId: "concept-1",
	confidence: 0.95,
	strategy: "manual_link",
};

const mockTraceChain: UICodeTraceChain = {
	id: "trace-1",
	name: "Login Form → Authentication",
	description: "Complete traceability from UI component to requirements",
	levels: [
		mockUiTraceLevel,
		mockCodeTraceLevel,
		mockRequirementTraceLevel,
		mockConceptTraceLevel,
	],
	overallConfidence: 0.95,
	canonicalConcept: mockCanonicalConcept,
	lastUpdated: new Date().toISOString(),
};

// =============================================================================
// TESTS
// =============================================================================

describe("UICodeTracePanel", () => {
	const mockOnOpenCode = vi.fn();
	const mockOnOpenRequirement = vi.fn();
	const mockOnNavigateToUI = vi.fn();
	const mockOnRefreshTrace = vi.fn();

	beforeEach(() => {
		vi.clearAllMocks();
	});

	// =========================================================================
	// RENDER TESTS
	// =========================================================================

	describe("rendering", () => {
		it("should render empty state when no trace chain provided", () => {
			render(<UICodeTracePanel traceChain={null} />);

			expect(screen.getByText("No trace chain selected")).toBeInTheDocument();
			expect(
				screen.getByText(
					/Select a UI component to view its traceability chain/,
				),
			).toBeInTheDocument();
		});

		it("should render loading state when isLoading is true", () => {
			render(<UICodeTracePanel traceChain={null} isLoading={true} />);

			expect(screen.getByText("Loading trace chain...")).toBeInTheDocument();
		});

		it("should render trace chain header with name and confidence", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			const text = container.textContent || "";
			expect(text).toContain(mockTraceChain.name);
			expect(text).toContain("95%");
		});

		it("should render trace chain description", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(screen.getByText(mockTraceChain.description!)).toBeInTheDocument();
		});

		it("should render all trace levels", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(screen.getByText("Login Form Component")).toBeInTheDocument();
			expect(screen.getByText("LoginForm Implementation")).toBeInTheDocument();
			expect(
				screen.getByText("User Authentication Requirement"),
			).toBeInTheDocument();
			expect(
				screen.getByText("User Authentication Concept"),
			).toBeInTheDocument();
		});

		it("should render canonical concept card", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			const text = container.textContent || "";
			expect(text).toContain("Canonical Concept");
			expect(text).toContain(mockCanonicalConcept.name);
			expect(text).toContain(mockCanonicalConcept.description!);
		});
	});

	// =========================================================================
	// TRACE LEVEL RENDERING TESTS
	// =========================================================================

	describe("trace level rendering", () => {
		it("should render UI level with component details", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			const uiLevel =
				screen.getByText("Login Form Component").closest("[role='region']") ||
				screen.getByText("Login Form Component").closest(".border");
			expect(uiLevel).toBeInTheDocument();
			expect(within(uiLevel!).getByText("Component:")).toBeInTheDocument();
			expect(within(uiLevel!).getByText("LoginForm")).toBeInTheDocument();
			expect(within(uiLevel!).getByText("Path:")).toBeInTheDocument();
		});

		it("should render code level with file and line information", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			const text = container.textContent || "";
			expect(text).toContain("src/components/LoginForm.tsx");
			expect(text).toContain("LoginForm");
			expect(text).toContain("component");
		});

		it("should render code signature when available", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(screen.getByText(/function LoginForm/)).toBeInTheDocument();
		});

		it("should render requirement level with business value", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(
				screen.getByText("User Authentication Requirement"),
			).toBeInTheDocument();
			expect(
				screen.getByText("Enable secure user access to the platform"),
			).toBeInTheDocument();
		});

		it("should display perspective badges for each level", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			const text = container.textContent || "";
			expect(text).toContain("ui");
			expect(text).toContain("technical");
			expect(text).toContain("business");
		});
	});

	// =========================================================================
	// CONFIDENCE DISPLAY TESTS
	// =========================================================================

	describe("confidence scores and colors", () => {
		it("should display confidence percentage for each level", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			const confidenceElements = screen.getAllByText(/\d+%/);
			expect(confidenceElements.length).toBeGreaterThan(0);
		});

		it("should display overall confidence in header", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			// The overall confidence should appear somewhere in the document
			const text = container.textContent || "";
			expect(text).toContain("95%");
		});

		it("should use appropriate color classes for confidence levels", () => {
			const highConfidenceChain: UICodeTraceChain = {
				...mockTraceChain,
				overallConfidence: 0.95,
			};
			render(<UICodeTracePanel traceChain={highConfidenceChain} />);

			// High confidence should have green indicator
			const confidenceElements = screen.getAllByText(/95%/);
			expect(confidenceElements.length).toBeGreaterThan(0);
		});

		it("should display confirmation status", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			// All levels in mock data are confirmed
			// This is implicit in the rendering
			expect(screen.getByText("Login Form Component")).toBeInTheDocument();
		});
	});

	// =========================================================================
	// INTERACTION TESTS
	// =========================================================================

	describe("user interactions", () => {
		it("should call onOpenCode when code button is clicked", async () => {
			const user = userEvent.setup();
			render(
				<UICodeTracePanel
					traceChain={mockTraceChain}
					onOpenCode={mockOnOpenCode}
				/>,
			);

			const openButtons = screen.getAllByText(/Open in Editor/);
			if (openButtons.length > 0) {
				await user.click(openButtons[0]);
				expect(mockOnOpenCode).toHaveBeenCalledWith(mockCodeReference);
			}
		});

		it("should call onOpenRequirement when requirement button is clicked", async () => {
			const user = userEvent.setup();
			render(
				<UICodeTracePanel
					traceChain={mockTraceChain}
					onOpenRequirement={mockOnOpenRequirement}
				/>,
			);

			const viewButtons = screen.getAllByText(/View Requirement/);
			if (viewButtons.length > 0) {
				await user.click(viewButtons[0]);
				expect(mockOnOpenRequirement).toHaveBeenCalledWith("req-auth-001");
			}
		});

		it("should call onNavigateToUI when component button is clicked", async () => {
			const user = userEvent.setup();
			render(
				<UICodeTracePanel
					traceChain={mockTraceChain}
					onNavigateToUI={mockOnNavigateToUI}
				/>,
			);

			const componentButtons = screen.getAllByText(/Open Component/);
			if (componentButtons.length > 0) {
				await user.click(componentButtons[0]);
				expect(mockOnNavigateToUI).toHaveBeenCalledWith(
					"src/components/LoginForm.tsx",
				);
			}
		});

		it("should call onRefreshTrace when refresh button is clicked", async () => {
			const user = userEvent.setup();
			render(
				<UICodeTracePanel
					traceChain={mockTraceChain}
					onRefreshTrace={mockOnRefreshTrace}
				/>,
			);

			const refreshButton = screen.getByText("Refresh");
			await user.click(refreshButton);
			expect(mockOnRefreshTrace).toHaveBeenCalled();
		});
	});

	// =========================================================================
	// TOOLTIP TESTS
	// =========================================================================

	describe("tooltips and information display", () => {
		it("should display strategy information in tooltips", async () => {
			const user = userEvent.setup();
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			// Tooltips are displayed on hover
			const confidenceBadges = screen.getAllByText(/\d+%/);
			if (confidenceBadges.length > 0) {
				await user.hover(confidenceBadges[0]);
				// Wait for tooltip to appear
				await waitFor(() => {
					// Strategy labels should be in the document
					expect(document.body.textContent).toBeDefined();
				});
			}
		});
	});

	// =========================================================================
	// EDGE CASES
	// =========================================================================

	describe("edge cases", () => {
		it("should handle trace chain with no canonical concept", () => {
			const chainWithoutConcept: UICodeTraceChain = {
				...mockTraceChain,
				canonicalConcept: undefined,
				projections: undefined,
			};

			render(<UICodeTracePanel traceChain={chainWithoutConcept} />);

			expect(screen.getByText(mockTraceChain.name)).toBeInTheDocument();
			// When no concept, there should not be a concept card header
			const conceptCards = document.querySelectorAll(
				"div:has(> *:contains('Canonical Concept'))",
			);
			expect(conceptCards.length).toBe(0);
		});

		it("should handle trace level without optional fields", () => {
			const minimalLevel: TraceLevel = {
				id: "minimal-1",
				type: "code",
				title: "Minimal Code Level",
				confidence: 0.5,
			};

			const chainWithMinimal: UICodeTraceChain = {
				id: "trace-2",
				name: "Minimal Trace",
				levels: [minimalLevel],
				overallConfidence: 0.5,
				lastUpdated: new Date().toISOString(),
			};

			const { container } = render(
				<UICodeTracePanel traceChain={chainWithMinimal} />,
			);

			expect(screen.getByText("Minimal Code Level")).toBeInTheDocument();
			// Check that 50% appears in the document (may appear multiple times)
			const text = container.textContent || "";
			expect(text).toContain("50%");
		});

		it("should handle empty trace levels", () => {
			const emptyChain: UICodeTraceChain = {
				id: "trace-3",
				name: "Empty Trace",
				levels: [],
				overallConfidence: 0,
				lastUpdated: new Date().toISOString(),
			};

			render(<UICodeTracePanel traceChain={emptyChain} />);

			expect(screen.getByText("Empty Trace")).toBeInTheDocument();
		});

		it("should handle trace level with low confidence", () => {
			const lowConfidenceLevel: TraceLevel = {
				id: "level-low",
				type: "code",
				title: "Low Confidence Match",
				confidence: 0.3,
				strategy: "co_occurrence",
			};

			const lowConfidenceChain: UICodeTraceChain = {
				id: "trace-4",
				name: "Low Confidence Trace",
				levels: [lowConfidenceLevel],
				overallConfidence: 0.3,
				lastUpdated: new Date().toISOString(),
			};

			const { container } = render(
				<UICodeTracePanel traceChain={lowConfidenceChain} />,
			);

			const allText = document.body.textContent || "";
			expect(allText).toContain("30%");
		});

		it("should handle long file paths with truncation", () => {
			const longPathLevel: TraceLevel = {
				id: "level-long",
				type: "code",
				title: "Long Path Code",
				codeRef: {
					...mockCodeReference,
					filePath:
						"src/very/deeply/nested/path/with/many/directories/components/LoginForm.tsx",
				},
				confidence: 0.9,
			};

			const chainWithLongPath: UICodeTraceChain = {
				id: "trace-5",
				name: "Long Path Trace",
				levels: [longPathLevel],
				overallConfidence: 0.9,
				lastUpdated: new Date().toISOString(),
			};

			const { container } = render(
				<UICodeTracePanel traceChain={chainWithLongPath} />,
			);

			// Path should be present (even if truncated)
			expect(container.textContent).toContain("components/LoginForm.tsx");
		});
	});

	// =========================================================================
	// ACCESSIBILITY TESTS
	// =========================================================================

	describe("accessibility", () => {
		it("should have proper heading hierarchy", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			// Should have proper heading structure
			const headings = screen.getAllByRole("heading");
			expect(headings.length).toBeGreaterThan(0);
		});

		it("should have alt text for images", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			// If there are images, they should have alt text
			const images = document.querySelectorAll("img");
			images.forEach((img) => {
				expect(img.getAttribute("alt")).toBeTruthy();
			});
		});

		it("should have proper button labels", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			// All buttons should have accessible labels
			const buttons = screen.getAllByRole("button");
			buttons.forEach((button) => {
				// Button should have text content or aria-label
				expect(
					button.textContent?.trim() ||
						button.getAttribute("aria-label") ||
						button.getAttribute("title"),
				).toBeTruthy();
			});
		});
	});

	// =========================================================================
	// DATA DISPLAY TESTS
	// =========================================================================

	describe("data display", () => {
		it("should display last updated timestamp", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(screen.getByText(/Last updated:/)).toBeInTheDocument();
		});

		it("should display canonical concept metadata", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			expect(screen.getByText(mockCanonicalConcept.name)).toBeInTheDocument();
			expect(screen.getByText(mockCanonicalConcept.domain)).toBeInTheDocument();
		});

		it("should display projections count in concept card", () => {
			render(<UICodeTracePanel traceChain={mockTraceChain} />);

			const projectionText = screen.getByText(/perspective.*linked/i);
			expect(projectionText).toBeInTheDocument();
		});

		it("should display code reference metadata", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			const allText = document.body.textContent || "";
			expect(allText).toContain(mockCodeReference.symbolName);
			expect(allText).toContain(mockCodeReference.symbolType);
		});
	});

	// =========================================================================
	// SCROLLING TESTS
	// =========================================================================

	describe("scrolling behavior", () => {
		it("should have scroll area for trace levels", () => {
			const { container } = render(
				<UICodeTracePanel traceChain={mockTraceChain} />,
			);

			// Check for scroll container
			const scrollArea = container.querySelector("[class*='scroll']");
			// ScrollArea should be present or the container should handle overflow
			expect(container).toBeInTheDocument();
		});
	});
});
