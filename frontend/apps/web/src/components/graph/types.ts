// Enhanced Graph View Types

import type {
	Item,
	ItemStatus,
	LinkType,
	PerspectiveType,
} from "@tracertm/types";

// Re-export PerspectiveType from canonical types for backward compatibility
export type GraphPerspective = PerspectiveType;

// Mapping of item types to perspectives
export const TYPE_TO_PERSPECTIVE: Record<string, GraphPerspective[]> = {
	// Product/User facing
	requirement: ["product", "business"],
	feature: ["product", "business"],
	user_story: ["product", "business"],
	story: ["product", "business"],
	epic: ["business"],
	journey: ["product"],

	// Technical
	api: ["technical"],
	database: ["technical"],
	code: ["technical"],
	architecture: ["technical"],
	infrastructure: ["technical"],
	configuration: ["technical"],
	dependency: ["technical"],

	// UI
	wireframe: ["ui", "product"],
	ui_component: ["ui"],
	page: ["ui", "product"],
	component: ["ui"],

	// Security
	security: ["security", "technical"],
	vulnerability: ["security"],
	audit: ["security"],

	// Performance
	performance: ["performance", "technical"],
	monitoring: ["performance", "technical"],
	metric: ["performance"],

	// Test
	test: ["technical", "business"],
	test_case: ["technical"],
	test_suite: ["technical"],

	// Tasks
	task: ["business", "technical"],
	bug: ["business", "technical"],
};

// Enhanced node data for rich visualization
export interface EnhancedNodeData {
	id: string;
	item: Item;
	type: string;
	status: ItemStatus;
	label: string;
	perspective: GraphPerspective[];

	// UI preview data (if applicable)
	uiPreview?: {
		screenshotUrl?: string;
		thumbnailUrl?: string;
		componentCode?: string;
		interactiveWidgetUrl?: string;
	};

	// Cross-link summary
	connections: {
		incoming: number;
		outgoing: number;
		total: number;
		byType: Record<LinkType, number>;
	};

	// Hierarchy info
	depth: number;
	hasChildren: boolean;
	parentId?: string;
}

// Rich edge data
export interface EnhancedEdgeData {
	id: string;
	source: string;
	target: string;
	type: LinkType;
	label: string;
	perspective: GraphPerspective[];
}

// Node visual configuration
export interface NodeStyle {
	backgroundColor: string;
	borderColor: string;
	textColor: string;
	opacity: number;
	width: number;
	height: number;
	shape: "pill" | "rectangle" | "circle";
}

// Compatibility interface for graph components
// Maps the canonical PerspectiveConfig to the simpler graph representation
export interface PerspectiveConfig {
	id: GraphPerspective;
	label: string;
	description: string;
	icon: string;
	color: string;
	includeTypes: string[];
	excludeTypes: string[];
	layoutPreference: "cose" | "breadthfirst" | "circle" | "elk";
}

// Build PERSPECTIVE_CONFIGS from canonical DEFAULT_PERSPECTIVES
// Maps perspectiveType -> id for backward compatibility
import { DEFAULT_PERSPECTIVES } from "@tracertm/types";

export const PERSPECTIVE_CONFIGS: PerspectiveConfig[] =
	DEFAULT_PERSPECTIVES.map((config) => ({
		id: config.perspectiveType as GraphPerspective,
		label: config.name,
		description: config.description || "",
		icon: config.icon,
		color: config.color,
		includeTypes: config.includeTypes,
		excludeTypes: config.excludeTypes,
		layoutPreference: config.layoutPreference,
	}));

// Type colors for the enhanced view
export const ENHANCED_TYPE_COLORS: Record<string, string> = {
	// Requirements & Features
	requirement: "#9333ea",
	feature: "#a855f7",
	epic: "#7c3aed",
	user_story: "#8b5cf6",
	story: "#8b5cf6",

	// Technical
	api: "#f59e0b",
	database: "#8b5cf6",
	code: "#3b82f6",
	architecture: "#6366f1",
	infrastructure: "#06b6d4",
	configuration: "#64748b",
	dependency: "#84cc16",

	// UI
	wireframe: "#ec4899",
	ui_component: "#f472b6",
	page: "#db2777",
	component: "#f472b6",

	// Testing
	test: "#22c55e",
	test_case: "#16a34a",
	test_suite: "#15803d",

	// Security & Performance
	security: "#ef4444",
	vulnerability: "#dc2626",
	audit: "#b91c1c",
	performance: "#10b981",
	monitoring: "#14b8a6",
	metric: "#0d9488",

	// Tasks
	task: "#64748b",
	bug: "#ef4444",
	journey: "#f97316",
	domain: "#a855f7",
};

// Status opacity mapping
export const STATUS_OPACITY: Record<ItemStatus | string, number> = {
	done: 1,
	completed: 1,
	in_progress: 0.85,
	todo: 0.6,
	pending: 0.6,
	blocked: 0.5,
	cancelled: 0.3,
};

// Link type colors and styles
export const LINK_STYLES: Record<
	LinkType | string,
	{ color: string; dashed: boolean; arrow: boolean }
> = {
	implements: { color: "#9333ea", dashed: false, arrow: true },
	tests: { color: "#22c55e", dashed: false, arrow: true },
	depends_on: { color: "#f59e0b", dashed: true, arrow: true },
	traces_to: { color: "#3b82f6", dashed: false, arrow: true },
	validates: { color: "#10b981", dashed: false, arrow: true },
	blocks: { color: "#ef4444", dashed: true, arrow: true },
	related_to: { color: "#64748b", dashed: true, arrow: false },
	parent_of: { color: "#8b5cf6", dashed: false, arrow: true },
};
