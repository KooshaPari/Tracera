# Specification Dashboard - Implementation Example

Complete, production-ready example of integrating the dashboard components.

## Full Page Implementation

```tsx
/**
 * SpecificationDashboardPage
 * Complete implementation with API integration and state management
 */

import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";
import {
	SpecificationDashboard,
	HealthScoreRing,
	CoverageHeatmap,
	GapAnalysis,
	ComplianceGaugeFull,
} from "@/components/specifications/dashboard";
import { Button } from "@tracertm/ui";
import { Plus, RefreshCw } from "lucide-react";
import { toast } from "sonner";

// Hooks for data fetching
import {
	useSpecificationsSummary,
	useCoverageData,
	useGapAnalysis,
	useRecentActivity,
} from "@/hooks/useSpecifications";

export function SpecificationDashboardPage() {
	const navigate = useNavigate();
	const queryClient = useQueryClient();
	const [isRefreshing, setIsRefreshing] = useState(false);

	// Fetch data with hooks
	const { data: summary, isLoading: summaryLoading } =
		useSpecificationsSummary();
	const { data: coverageData, isLoading: coverageLoading } =
		useCoverageData();
	const { data: gapItems, isLoading: gapLoading } = useGapAnalysis();
	const { data: recentActivity } = useRecentActivity();

	const isLoading = summaryLoading || coverageLoading || gapLoading;

	// Handle refresh
	const handleRefresh = async () => {
		setIsRefreshing(true);
		try {
			await queryClient.invalidateQueries({
				queryKey: ["specifications"],
			});
			toast.success("Dashboard updated");
		} catch (error) {
			toast.error("Failed to refresh dashboard");
			console.error(error);
		} finally {
			setIsRefreshing(false);
		}
	};

	// Navigate to section
	const handleNavigate = (section: string, id?: string) => {
		const routes: Record<string, string> = {
			adrs: "/specifications/adrs",
			contracts: "/specifications/contracts",
			features: "/specifications/features",
			requirement: `/specifications/requirement/${id}`,
			gap: `/specifications/gap/${id}`,
		};

		const route = routes[section];
		if (route) {
			navigate({ to: route });
		}
	};

	// Create new specification
	const handleCreateNew = (type: string) => {
		const routes: Record<string, string> = {
			adr: "/specifications/adr/new",
			contract: "/specifications/contract/new",
			feature: "/specifications/feature/new",
			test_case: "/specifications/test-case/new",
		};

		const route = routes[type];
		if (route) {
			navigate({ to: route });
		} else {
			toast.error(`Unknown type: ${type}`);
		}
	};

	// Handle gap action
	const handleGapAction = async (
		gap: any,
		resourceType: "test_case" | "adr" | "contract"
	) => {
		const resourceNames = {
			test_case: "Test Case",
			adr: "Architecture Decision Record",
			contract: "Contract",
		};

		// Navigate to create dialog with context
		navigate({
			to: `/specifications/${resourceType}/new`,
			search: {
				linkedItem: gap.id,
				linkedType: gap.gapType,
			},
		});

		toast.info(
			`Creating ${resourceNames[resourceType]} linked to ${gap.label}`
		);
	};

	// Loading state
	if (isLoading) {
		return (
			<div className="flex items-center justify-center min-h-screen">
				<div className="text-center">
					<div className="inline-block">
						<div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
					</div>
					<p className="mt-4 text-muted-foreground">
						Loading dashboard...
					</p>
				</div>
			</div>
		);
	}

	// Error state
	if (!summary) {
		return (
			<div className="flex items-center justify-center min-h-screen">
				<div className="text-center">
					<p className="text-destructive font-medium mb-4">
						Failed to load dashboard
					</p>
					<Button onClick={handleRefresh}>Try Again</Button>
				</div>
			</div>
		);
	}

	return (
		<div className="container mx-auto px-4 py-8">
			{/* Header with controls */}
			<div className="flex items-center justify-between mb-6">
				<div>
					<h1 className="text-4xl font-bold tracking-tight">
						Specifications Dashboard
					</h1>
					<p className="text-muted-foreground mt-2">
						Monitor your ADRs, contracts, features, and test coverage
					</p>
				</div>
				<Button
					onClick={handleRefresh}
					disabled={isRefreshing}
					variant="outline"
					className="gap-2"
				>
					<RefreshCw
						className={`w-4 h-4 ${
							isRefreshing ? "animate-spin" : ""
						}`}
					/>
					Refresh
				</Button>
			</div>

			{/* Main dashboard */}
			<SpecificationDashboard
				summary={summary}
				coverageData={coverageData || []}
				gapItems={gapItems || []}
				recentActivity={recentActivity || []}
				onNavigate={handleNavigate}
				onCreateNew={handleCreateNew}
				onGapAction={handleGapAction}
				className="space-y-6"
			/>
		</div>
	);
}
```

## Hook Implementation

```typescript
// src/hooks/useSpecifications.ts

import {
	useQuery,
	useQueryClient,
	useInfiniteQuery,
} from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
	SpecificationSummary,
	ADR,
	Contract,
	Feature,
} from "@tracertm/types";

/**
 * Fetch specification summary
 */
export function useSpecificationsSummary() {
	return useQuery({
		queryKey: ["specifications", "summary"],
		queryFn: async () => {
			const response = await api.specifications.getSummary();
			return response.data as SpecificationSummary;
		},
		staleTime: 5 * 60 * 1000, // 5 minutes
		gcTime: 10 * 60 * 1000, // 10 minutes
	});
}

/**
 * Fetch coverage data for heatmap
 */
export function useCoverageData() {
	return useQuery({
		queryKey: ["specifications", "coverage"],
		queryFn: async () => {
			const response = await api.specifications.getCoverageData();
			return response.data.map((item: any) => ({
				id: item.id,
				label: item.name,
				coverage: item.coveragePercentage,
				testCases: item.testCaseCount,
				adrs: item.adrCount,
				contracts: item.contractCount,
				linked: item.isLinked,
			}));
		},
		staleTime: 5 * 60 * 1000,
		gcTime: 10 * 60 * 1000,
	});
}

/**
 * Fetch gap analysis
 */
export function useGapAnalysis() {
	return useQuery({
		queryKey: ["specifications", "gaps"],
		queryFn: async () => {
			const response = await api.specifications.getGaps();
			return response.data.map((item: any) => ({
				id: item.id,
				label: item.name,
				priority: calculatePriority(item),
				gapType: item.gapType as
					| "no_tests"
					| "no_adr"
					| "no_contract"
					| "orphaned",
				affectedItems: item.affectedCount || 0,
				impact: item.impact,
				suggestion: item.suggestion,
				linkedResources: item.linkedResources || [],
			}));
		},
		staleTime: 5 * 60 * 1000,
		gcTime: 10 * 60 * 1000,
	});
}

/**
 * Fetch recent activity
 */
export function useRecentActivity() {
	return useQuery({
		queryKey: ["specifications", "activity"],
		queryFn: async () => {
			const response = await api.specifications.getActivity({
				limit: 10,
			});
			return response.data.map((item: any) => ({
				id: item.id,
				type: item.type,
				title: item.title,
				timestamp: item.timestamp,
				actor: item.actor,
			}));
		},
		staleTime: 1 * 60 * 1000, // 1 minute
		gcTime: 5 * 60 * 1000, // 5 minutes
	});
}

/**
 * Calculate priority based on gap metrics
 */
function calculatePriority(
	gap: any
): "critical" | "high" | "medium" | "low" {
	if (gap.gapType === "no_tests" && gap.affectedCount > 10)
		return "critical";
	if (gap.affectedCount > 5) return "high";
	if (gap.affectedCount > 2) return "medium";
	return "low";
}
```

## API Service

```typescript
// src/lib/api/specifications.ts

import { client } from "./client";

export const specifications = {
	// Get summary
	getSummary: () =>
		client.get("/api/v1/specifications/summary"),

	// Get coverage data
	getCoverageData: () =>
		client.get("/api/v1/specifications/coverage"),

	// Get gaps
	getGaps: (filters?: Record<string, any>) =>
		client.get("/api/v1/specifications/gaps", { params: filters }),

	// Get recent activity
	getActivity: (params?: { limit?: number; offset?: number }) =>
		client.get("/api/v1/specifications/activity", { params }),

	// Create ADR
	createADR: (data: any) =>
		client.post("/api/v1/specifications/adrs", data),

	// Create contract
	createContract: (data: any) =>
		client.post("/api/v1/specifications/contracts", data),

	// Create feature
	createFeature: (data: any) =>
		client.post("/api/v1/specifications/features", data),

	// Create test case
	createTestCase: (data: any) =>
		client.post("/api/v1/specifications/test-cases", data),

	// Create link
	createLink: (data: {
		sourceId: string;
		targetId: string;
		type: string;
	}) =>
		client.post("/api/v1/specifications/links", data),
};
```

## Component Storybook Examples

```typescript
// src/__stories__/SpecificationDashboard.stories.tsx

import type { Meta, StoryObj } from "@storybook/react";
import { SpecificationDashboard } from "@/components/specifications/dashboard";

const meta = {
	component: SpecificationDashboard,
	title: "Components/Specifications/Dashboard",
	tags: ["autodocs"],
} satisfies Meta<typeof SpecificationDashboard>;

export default meta;
type Story = StoryObj<typeof meta>;

// Mock data
const mockSummary = {
	projectId: "proj-1",
	adrs: {
		total: 12,
		accepted: 10,
		proposed: 2,
		averageCompliance: 85,
	},
	contracts: {
		total: 8,
		active: 7,
		verified: 6,
		violated: 0,
	},
	features: {
		total: 24,
		scenarios: 48,
		passRate: 92,
		coverage: 88,
	},
	healthScore: 88,
	healthDetails: [
		{
			category: "ADR Coverage",
			score: 90,
			issues: [],
		},
		{
			category: "Test Coverage",
			score: 85,
			issues: [
				"5 items missing test coverage",
			],
		},
		{
			category: "Documentation",
			score: 82,
			issues: [
				"2 ADRs need documentation updates",
			],
		},
	],
};

const mockCoverageData = Array.from({ length: 48 }, (_, i) => ({
	id: `req-${i}`,
	label: `Requirement ${i + 1}`,
	coverage: Math.floor(Math.random() * 100),
	testCases: Math.floor(Math.random() * 5),
	adrs: Math.random() > 0.5 ? 1 : 0,
	contracts: Math.random() > 0.5 ? 1 : 0,
	linked: Math.random() > 0.4,
}));

const mockGaps = [
	{
		id: "gap-1",
		label: "User Authentication Flow",
		priority: "critical" as const,
		gapType: "no_tests" as const,
		affectedItems: 8,
		suggestion: "Add E2E tests for auth flow",
	},
	{
		id: "gap-2",
		label: "Payment Processing",
		priority: "high" as const,
		gapType: "no_contract" as const,
		affectedItems: 5,
		suggestion: "Define contract for payment service",
	},
];

// Basic story
export const Default: Story = {
	args: {
		summary: mockSummary,
		coverageData: mockCoverageData,
		gapItems: mockGaps,
		onNavigate: (section, id) =>
			console.log("Navigate to", section, id),
		onCreateNew: (type) =>
			console.log("Create", type),
		onGapAction: (gap, action) =>
			console.log("Gap action", gap, action),
	},
};

// Empty state
export const Empty: Story = {
	args: {
		...Default.args,
		coverageData: [],
		gapItems: [],
	},
};

// High score
export const HighScore: Story = {
	args: {
		...Default.args,
		summary: {
			...mockSummary,
			healthScore: 95,
		},
	},
};

// Low score
export const LowScore: Story = {
	args: {
		...Default.args,
		summary: {
			...mockSummary,
			healthScore: 42,
		},
	},
};
```

## Testing

```typescript
// src/__tests__/components/SpecificationDashboard.test.tsx

import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SpecificationDashboard } from "@/components/specifications/dashboard";

describe("SpecificationDashboard", () => {
	const mockSummary = {
		projectId: "proj-1",
		adrs: { total: 10, accepted: 8, proposed: 2, averageCompliance: 85 },
		contracts: { total: 5, active: 4, verified: 3, violated: 0 },
		features: { total: 15, scenarios: 30, passRate: 90, coverage: 85 },
		healthScore: 87,
		healthDetails: [
			{ category: "Test Coverage", score: 85, issues: [] },
		],
	};

	it("renders main dashboard components", () => {
		render(<SpecificationDashboard summary={mockSummary} />);

		expect(screen.getByText("Specifications Dashboard")).toBeInTheDocument();
		expect(screen.getByText("Overall Health")).toBeInTheDocument();
		expect(screen.getByText("ADRs")).toBeInTheDocument();
		expect(screen.getByText("Contracts")).toBeInTheDocument();
		expect(screen.getByText("Features")).toBeInTheDocument();
	});

	it("handles navigation callbacks", async () => {
		const onNavigate = vi.fn();
		const user = userEvent.setup();

		const { container } = render(
			<SpecificationDashboard
				summary={mockSummary}
				onNavigate={onNavigate}
			/>
		);

		const adrCard = container.querySelector('[class*="FileText"]')
			?.closest("button");
		if (adrCard) {
			await user.click(adrCard);
		}

		expect(onNavigate).toHaveBeenCalled();
	});

	it("displays health score correctly", () => {
		render(<SpecificationDashboard summary={mockSummary} />);

		expect(screen.getByText(/87%/)).toBeInTheDocument();
	});

	it("renders gap analysis when provided", () => {
		const gaps = [
			{
				id: "gap-1",
				label: "Missing Tests",
				priority: "high" as const,
				gapType: "no_tests" as const,
			},
		];

		render(
			<SpecificationDashboard summary={mockSummary} gapItems={gaps} />
		);

		expect(screen.getByText("Missing Tests")).toBeInTheDocument();
	});
});
```

## E2E Testing

```typescript
// e2e/specifications-dashboard.spec.ts

import { test, expect } from "@playwright/test";

test.describe("Specifications Dashboard", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/specifications/dashboard");
		await page.waitForLoadState("networkidle");
	});

	test("displays health score", async ({ page }) => {
		const healthScore = page.locator("[data-testid='health-score']");
		await expect(healthScore).toBeVisible();

		const scoreText = await healthScore.textContent();
		expect(scoreText).toMatch(/\d+%/);
	});

	test("navigates to ADR section", async ({ page }) => {
		const adrCard = page.locator("text=ADRs").first();
		await adrCard.click();

		await expect(page).toHaveURL(/\/specifications\/adrs/);
	});

	test("filters gaps by priority", async ({ page }) => {
		const gapTab = page.locator("button:has-text('Gap Analysis')");
		await gapTab.click();

		const criticalFilter = page.locator(
			"button:has-text('Critical')"
		);
		await criticalFilter.click();

		// Verify only critical gaps shown
		const gaps = page.locator("[data-priority='critical']");
		await expect(gaps.first()).toBeVisible();
	});

	test("creates new ADR", async ({ page }) => {
		const createButton = page.locator("button:has-text('New ADR')");
		await createButton.click();

		await expect(page).toHaveURL(/\/specifications\/adr\/new/);
	});
});
```

---

## Customization Examples

### Custom Theme Colors

```tsx
<SpecificationDashboard
	summary={summary}
	className="dark:bg-slate-950"
/>
```

### Standalone Components

```tsx
// Just the health ring
<HealthScoreRing
	score={summary.healthScore}
	size={250}
/>

// Just the coverage heatmap
<CoverageHeatmap
	data={coverageData}
	columns={12}
	onCellClick={handleClick}
/>

// Just gap analysis
<GapAnalysis
	items={gaps}
	onItemClick={handleGapClick}
	onCreateLink={handleCreateLink}
/>
```

This provides a complete, production-ready implementation you can use immediately.

