# Specification Dashboard - Quick Start

## Files Created

```
frontend/apps/web/src/components/specifications/dashboard/
├── SpecificationDashboard.tsx      # Main dashboard component
├── HealthScoreRing.tsx             # Animated ring chart
├── CoverageHeatmap.tsx             # Coverage grid visualization
├── GapAnalysis.tsx                 # Gap analysis with filtering
├── ComplianceGaugeFull.tsx         # Full circular gauge
├── index.ts                        # Barrel export
└── README.md                       # Component guide
```

## Quick Import

```typescript
import {
	SpecificationDashboard,
	HealthScoreRing,
	CoverageHeatmap,
	GapAnalysis,
	ComplianceGaugeFull,
} from "@/components/specifications/dashboard";
```

## Basic Usage

```tsx
import { SpecificationDashboard } from "@/components/specifications/dashboard";

function DashboardPage() {
	return (
		<SpecificationDashboard
			summary={specificationSummary}
			coverageData={requirements}
			gapItems={gaps}
			onNavigate={(section, id) => console.log(section, id)}
			onCreateNew={(type) => console.log("Create", type)}
			onGapAction={(gap, action) => console.log(gap, action)}
		/>
	);
}
```

## Component Overview

### SpecificationDashboard
Main container with tabs for:
- Coverage visualization
- Gap analysis
- Health details
- Recent activity

### HealthScoreRing
Animated ring chart with:
- Score 0-100
- Category breakdown
- Status indicators
- Custom sizing

### CoverageHeatmap
Grid-based visualization:
- Color-coded cells by coverage %
- Hover tooltips
- Summary statistics
- Click navigation

### GapAnalysis
Gap tracking with:
- Priority filtering
- Gap type tabs
- Quick actions
- Linked resources

### ComplianceGaugeFull
Detailed gauge with:
- Animated fill
- Color gradient
- Score breakdown
- Status descriptions

## Key Features

### Colors & Themes
- Uses Tailwind CSS classes
- Responsive design out-of-the-box
- Dark mode compatible
- Customizable via className prop

### Animations
- Framer Motion for smooth transitions
- Entrance animations on load
- Hover effects
- Responsive to prefers-reduced-motion

### Interactivity
- Click navigation
- Hover tooltips
- Filter controls
- Quick action buttons

### Data Types

```typescript
// From @tracertm/types
interface SpecificationSummary {
	projectId: string;
	adrs: {
		total: number;
		accepted: number;
		proposed: number;
		averageCompliance: number;
	};
	contracts: {
		total: number;
		active: number;
		verified: number;
		violated: number;
	};
	features: {
		total: number;
		scenarios: number;
		passRate: number;
		coverage: number;
	};
	healthScore: number; // 0-100
	healthDetails: Array<{
		category: string;
		score: number;
		issues: string[];
	}>;
}
```

## Event Handlers

### onNavigate
Navigate to a section or resource:
```tsx
onNavigate={(section, id) => {
	// section: "adrs" | "contracts" | "features" | "requirement" | "gap"
	// id: optional resource ID
	router.push(`/specs/${section}/${id}`);
}}
```

### onCreateNew
Create new specification item:
```tsx
onCreateNew={(type) => {
	// type: "adr" | "contract" | "feature" | "test_case"
	openCreateModal(type);
}}
```

### onGapAction
Handle gap-related actions:
```tsx
onGapAction={(gap, action) => {
	// action: "test_case" | "adr" | "contract"
	createLink(gap.id, action);
}}
```

## Customization

### Override Styling
```tsx
<HealthScoreRing
	className="mb-4 shadow-lg"
	size={250}
/>
```

### Disable Animation
```tsx
<HealthScoreRing
	showAnimation={false}
/>
```

### Custom Colors
```tsx
<HealthScoreRing
	categories={[
		{ name: "Critical", value: 30, color: "#dc2626" },
		{ name: "Warnings", value: 50, color: "#f59e0b" },
		{ name: "Good", value: 20, color: "#10b981" },
	]}
/>
```

## Performance Tips

1. Memoize data transformations:
```tsx
const coverageData = useMemo(() => transformData(raw), [raw]);
```

2. Use React.memo for child components:
```tsx
const GapItem = memo(({ item }) => <div>{item.label}</div>);
```

3. Lazy load tab content:
```tsx
<TabsContent value="coverage">
	{activeTab === "coverage" && <CoverageHeatmap />}
</TabsContent>
```

## Testing Integration

Example with Playwright E2E:
```typescript
test("dashboard displays health score", async ({ page }) => {
	await page.goto("/dashboard");
	const gauge = page.locator("[data-testid='health-gauge']");
	await expect(gauge).toBeVisible();
});
```

## Troubleshooting

### Components not rendering
- Verify data is passed correctly
- Check browser console for errors
- Ensure @tracertm/ui is installed

### Animations not smooth
- Check for layout thrashing
- Verify GPU acceleration enabled
- Test in Chrome DevTools performance tab

### Styling not applied
- Confirm Tailwind CSS is loaded
- Check className prop syntax
- Verify shadcn/ui theme is configured

## Next Steps

1. Integrate with your API
2. Implement event handlers
3. Add testing coverage
4. Customize styling for your brand
5. Monitor performance in production

## Support

For issues or questions:
- Check DASHBOARD_COMPONENTS_GUIDE.md for detailed docs
- Review component source code for implementation details
- Test components in Storybook if available

