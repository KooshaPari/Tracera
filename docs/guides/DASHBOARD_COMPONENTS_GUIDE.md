# Specification Dashboard Components Guide

## Overview

A comprehensive set of React components for visualizing specification health, coverage, and gaps in the TracerTM application. Built with shadcn/ui, Tailwind CSS, Recharts, and Framer Motion.

**Location**: `/frontend/apps/web/src/components/specifications/dashboard/`

## Components

### 1. SpecificationDashboard

**File**: `SpecificationDashboard.tsx`

Main dashboard component that integrates all other dashboard components. Provides an overview of your specifications with tabs for Coverage, Gap Analysis, Health Details, and Recent Activity.

#### Features
- Summary cards for ADRs, Contracts, and Features
- Overall health score display
- Tabbed interface for different views
- Coverage heatmap preview
- Gap analysis visualization
- Health details breakdown
- Recent activity feed
- Quick action buttons

#### Props
```typescript
interface SpecificationDashboardProps {
	summary: SpecificationSummary;
	coverageData?: Array<{
		id: string;
		label: string;
		coverage: number;
		testCases?: number;
		adrs?: number;
		contracts?: number;
		linked?: boolean;
	}>;
	gapItems?: Array<{
		id: string;
		label: string;
		priority: "critical" | "high" | "medium" | "low";
		gapType: "no_tests" | "no_adr" | "no_contract" | "orphaned";
		affectedItems?: number;
		impact?: string;
		suggestion?: string;
		linkedResources?: Array<{
			type: "test_case" | "adr" | "contract";
			id: string;
			label: string;
		}>;
	}>;
	recentActivity?: Array<{
		id: string;
		type: string;
		title: string;
		timestamp: string;
		actor: string;
	}>;
	onNavigate?: (section: string, id?: string) => void;
	onCreateNew?: (type: string) => void;
	onGapAction?: (gap: any, action: string) => void;
	className?: string;
}
```

#### Usage
```tsx
<SpecificationDashboard
	summary={summary}
	coverageData={coverageData}
	gapItems={gaps}
	recentActivity={activity}
	onNavigate={handleNavigate}
	onCreateNew={handleCreateNew}
	onGapAction={handleGapAction}
/>
```

---

### 2. HealthScoreRing

**File**: `HealthScoreRing.tsx`

Animated ring chart showing overall health score with breakdown by category. Features color-coded segments and smooth entrance animations.

#### Features
- Animated ring chart (0-100%)
- Color-coded segments by category
- Dynamic status messages based on score
- Legend with category colors
- Customizable size
- Smooth animation on mount

#### Score Color Scale
- 90-100: Green (Excellent)
- 70-90: Blue (Good)
- 50-70: Amber (Fair)
- <50: Red (Poor)

#### Props
```typescript
interface HealthScoreRingProps {
	score: number; // 0-100
	categories?: Array<{
		name: string;
		value: number;
		color: string;
	}>;
	showAnimation?: boolean;
	showLegend?: boolean;
	size?: number;
	className?: string;
}
```

#### Usage
```tsx
<HealthScoreRing
	score={75}
	size={300}
	showAnimation={true}
	showLegend={true}
/>
```

---

### 3. CoverageHeatmap

**File**: `CoverageHeatmap.tsx`

Grid-based visualization of requirement coverage levels. Shows color intensity for coverage percentage with hover tooltips.

#### Features
- Responsive grid layout (customizable columns)
- Color intensity based on coverage level
- Summary statistics
- Interactive hover tooltips with details
- Linked item indicators
- Click navigation support
- Low coverage warnings
- Legend with coverage ranges

#### Grid Colors
- Emerald-600: ≥90% (Excellent)
- Emerald-500: 70-89%
- Amber-500: 50-69% (Fair)
- Orange-500: 30-49%
- Red-500: 10-29%
- Slate-300: 0% (No coverage)

#### Props
```typescript
interface CoverageHeatmapProps {
	data: Array<{
		id: string;
		label: string;
		coverage: number;
		testCases?: number;
		adrs?: number;
		contracts?: number;
		linked?: boolean;
	}>;
	onCellClick?: (cell: CoverageCell) => void;
	columns?: number;
	className?: string;
}
```

#### Usage
```tsx
<CoverageHeatmap
	data={requirements}
	columns={8}
	onCellClick={(cell) => navigateTo(cell.id)}
/>
```

---

### 4. GapAnalysis

**File**: `GapAnalysis.tsx`

Comprehensive gap analysis tool showing uncovered items with filtering and priority sorting.

#### Features
- Summary statistics cards
- Multiple gap type filters:
  - Missing Tests
  - Missing ADR Links
  - Missing Contracts
  - Orphaned Items
- Priority-based sorting (Critical, High, Medium, Low)
- Impact-based sorting (by affected items count)
- Quick action buttons for each gap
- Linked resources display
- Color-coded priority badges
- Detailed suggestions

#### Gap Types
- `no_tests`: Items without test coverage
- `no_adr`: Items without ADR links
- `no_contract`: Items without contracts
- `orphaned`: Items with no links to other resources

#### Priority Colors
- Critical: Red (#dc2626)
- High: Orange (#ea580c)
- Medium: Yellow (#eab308)
- Low: Blue (#0284c7)

#### Props
```typescript
interface GapAnalysisProps {
	items: Array<{
		id: string;
		label: string;
		priority: "critical" | "high" | "medium" | "low";
		gapType: "no_tests" | "no_adr" | "no_contract" | "orphaned";
		affectedItems?: number;
		impact?: string;
		suggestion?: string;
		linkedResources?: Array<{
			type: "test_case" | "adr" | "contract";
			id: string;
			label: string;
		}>;
	}>;
	onItemClick?: (item: GapItem) => void;
	onCreateLink?: (gap: GapItem, resourceType: string) => void;
	className?: string;
}
```

#### Usage
```tsx
<GapAnalysis
	items={gaps}
	onItemClick={(gap) => viewGapDetails(gap.id)}
	onCreateLink={(gap, type) => createLink(gap.id, type)}
/>
```

---

### 5. ComplianceGaugeFull

**File**: `ComplianceGaugeFull.tsx`

Full circular compliance gauge with animated fill and gradient coloring. More detailed than the simple compliance gauge.

#### Features
- SVG-based circular gauge
- Animated fill on mount
- Color gradient (red → orange → amber → blue → cyan → emerald)
- Dynamic status text
- Score/remaining breakdown
- Detailed metrics display

#### Status Descriptions
- 90-100: Excellent
- 80-90: Very Good
- 70-80: Good
- 60-70: Fair
- 40-60: Poor
- <40: Critical

#### Props
```typescript
interface ComplianceGaugeFullProps {
	score: number; // 0-100
	size?: number;
	strokeWidth?: number;
	showAnimation?: boolean;
	label?: string;
	showSubtext?: boolean;
	className?: string;
}
```

#### Usage
```tsx
<ComplianceGaugeFull
	score={85}
	size={200}
	label="Overall Compliance"
	showAnimation={true}
/>
```

---

## Integration Example

```tsx
import {
	SpecificationDashboard,
	HealthScoreRing,
	CoverageHeatmap,
	GapAnalysis,
	ComplianceGaugeFull,
} from "@/components/specifications/dashboard";

function SpecDashboardPage() {
	const [summary, setSummary] = useState<SpecificationSummary | null>(null);
	const [coverage, setCoverage] = useState([]);
	const [gaps, setGaps] = useState([]);

	useEffect(() => {
		// Fetch data
		fetchSpecifications();
	}, []);

	const handleNavigate = (section: string, id?: string) => {
		// Navigate to specific section
		router.push(`/specs/${section}${id ? `/${id}` : ""}`);
	};

	const handleCreateNew = (type: string) => {
		// Open create modal
		openCreateModal(type);
	};

	const handleGapAction = (gap: GapItem, action: string) => {
		// Handle gap action (create link, add test, etc.)
	};

	if (!summary) return <div>Loading...</div>;

	return (
		<SpecificationDashboard
			summary={summary}
			coverageData={coverage}
			gapItems={gaps}
			onNavigate={handleNavigate}
			onCreateNew={handleCreateNew}
			onGapAction={handleGapAction}
		/>
	);
}
```

---

## Styling

### Theme Integration
All components use Tailwind CSS and shadcn/ui theming:
- `bg-card`: Card background
- `bg-muted`: Muted background
- `text-muted-foreground`: Muted text
- `border-border`: Border color
- Color utilities: `text-green-600`, `bg-red-500/10`, etc.

### Animation Framework
Components use Framer Motion with:
- `initial`: Starting state
- `animate`: Final state
- `transition`: Animation timing
- `whileHover`: Hover effects
- `whileTap`: Click effects

### Customization
Pass `className` prop to override styles:
```tsx
<HealthScoreRing className="mb-4 px-2" />
```

---

## Types

All components export TypeScript interfaces for props:

```typescript
// Import types
import type {
	SpecificationDashboardProps,
	HealthScoreRingProps,
	CoverageHeatmapProps,
	GapAnalysisProps,
	ComplianceGaugeFullProps,
} from "@/components/specifications/dashboard";
```

---

## Best Practices

1. **Data Loading**: Fetch all required data before rendering dashboard
2. **Event Handlers**: Implement navigation and action handlers for interactive features
3. **Responsive Design**: All components are mobile-responsive out of the box
4. **Performance**: Use React.memo for expensive computations
5. **Accessibility**: Components include proper labels, ARIA attributes, and keyboard navigation
6. **Animation**: Disable animations on mobile with `@media (prefers-reduced-motion)`

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers with ES2020+ support

---

## Dependencies

- `react`: UI components
- `framer-motion`: Animations
- `recharts`: Charts and visualizations
- `@tracertm/ui`: shadcn/ui components
- `tailwindcss`: Styling
- `lucide-react`: Icons

---

## Migration from Old Dashboard

If migrating from an older dashboard component:

```tsx
// Old
import { SpecificationDashboard } from "@/components/specs/old-dashboard";

// New
import { SpecificationDashboard } from "@/components/specifications/dashboard";
```

The new components have enhanced features and better performance.

---

## Future Enhancements

- [ ] Export data as CSV/JSON
- [ ] Custom threshold configurations
- [ ] Drilldown analytics
- [ ] Time-series trends
- [ ] Comparison views
- [ ] Advanced filtering
- [ ] Custom color schemes

