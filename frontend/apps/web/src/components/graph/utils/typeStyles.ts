// Type-based styling utilities for graph nodes
// Maps entity types to icons and colors

import {
	Box,
	Boxes,
	Bug,
	Check,
	CheckSquare,
	Circle,
	CircleDot,
	Code,
	Cog,
	Component,
	Database,
	File,
	FileCode,
	FileText,
	FolderTree,
	GitBranch,
	Globe,
	Grid,
	Hash,
	Image,
	Layers,
	Layout,
	LayoutGrid,
	Link2,
	List,
	ListChecks,
	Loader,
	Maximize,
	MessageSquare,
	Monitor,
	Palette,
	PanelBottom,
	PanelLeft,
	Play,
	Puzzle,
	Server,
	Settings,
	Shapes,
	Square,
	Star,
	Target,
	TestTube,
	Type,
	User,
	Workflow,
	Zap,
	type LucideIcon,
} from "lucide-react";

// ============================================================================
// TYPE TO ICON MAPPING
// ============================================================================

const TYPE_ICONS: Record<string, LucideIcon> = {
	// UI Entity Types
	site: Globe,
	page: FileText,
	layout: Layout,
	section: Grid,
	subsection: LayoutGrid,
	component: Component,
	subcomponent: Puzzle,
	element: Square,
	modal: Maximize,
	popup: MessageSquare,
	toast: PanelBottom,
	drawer: PanelLeft,

	// Product Entity Types
	initiative: Star,
	epic: Layers,
	feature: Zap,
	user_story: User,
	acceptance_criteria: Check,
	task: CheckSquare,
	subtask: List,
	requirement: Target,
	story: User,

	// Technical Entity Types
	service: Server,
	module: FolderTree,
	class: Boxes,
	function: Code,
	api_endpoint: Link2,
	api: Link2,
	database_table: Database,
	database_field: Hash,
	config: Settings,
	code: FileCode,

	// Test Entity Types
	test_suite: ListChecks,
	test_case: TestTube,
	test_step: Play,
	assertion: CircleDot,
	fixture: Box,
	mock: Circle,
	test: TestTube,

	// Design Entity Types
	wireframe: Shapes,
	mockup: Image,
	prototype: Monitor,
	design_token: Palette,
	style_guide: Type,
	design: Image,
	ui: Monitor,

	// Documentation Types
	doc_root: FileText,
	doc_section: File,
	doc_page: FileText,
	doc_block: Grid,
	documentation: FileText,

	// Other common types
	workflow: Workflow,
	process: GitBranch,
	integration: Link2,
	deployment: Server,
	database: Database,
	bug: Bug,
	issue: Bug,
	loading: Loader,
	default: Cog,
};

// ============================================================================
// TYPE TO COLOR MAPPING
// ============================================================================

const TYPE_COLORS: Record<string, string> = {
	// UI Entity Types - Blue spectrum
	site: "#3b82f6", // blue-500
	page: "#60a5fa", // blue-400
	layout: "#2563eb", // blue-600
	section: "#3b82f6", // blue-500
	subsection: "#60a5fa", // blue-400
	component: "#6366f1", // indigo-500
	subcomponent: "#818cf8", // indigo-400
	element: "#a5b4fc", // indigo-300
	modal: "#4f46e5", // indigo-600
	popup: "#6366f1", // indigo-500
	toast: "#818cf8", // indigo-400
	drawer: "#4f46e5", // indigo-600

	// Product Entity Types - Purple spectrum
	initiative: "#7c3aed", // violet-600
	epic: "#8b5cf6", // violet-500
	feature: "#a78bfa", // violet-400
	user_story: "#c4b5fd", // violet-300
	acceptance_criteria: "#e879f9", // fuchsia-400
	task: "#d946ef", // fuchsia-500
	subtask: "#f0abfc", // fuchsia-300
	requirement: "#a855f7", // purple-500
	story: "#c4b5fd", // violet-300

	// Technical Entity Types - Green spectrum
	service: "#10b981", // emerald-500
	module: "#34d399", // emerald-400
	class: "#059669", // emerald-600
	function: "#14b8a6", // teal-500
	api_endpoint: "#2dd4bf", // teal-400
	api: "#2dd4bf", // teal-400
	database_table: "#0d9488", // teal-600
	database_field: "#0d9488", // teal-600
	config: "#22c55e", // green-500
	code: "#4ade80", // green-400

	// Test Entity Types - Orange spectrum
	test_suite: "#f97316", // orange-500
	test_case: "#fb923c", // orange-400
	test_step: "#fdba74", // orange-300
	assertion: "#fed7aa", // orange-200
	fixture: "#ea580c", // orange-600
	mock: "#dc2626", // red-600
	test: "#fb923c", // orange-400

	// Design Entity Types - Pink spectrum
	wireframe: "#ec4899", // pink-500
	mockup: "#f472b6", // pink-400
	prototype: "#f9a8d4", // pink-300
	design_token: "#be185d", // pink-700
	style_guide: "#db2777", // pink-600
	design: "#ec4899", // pink-500
	ui: "#f472b6", // pink-400

	// Documentation Types - Yellow spectrum
	doc_root: "#eab308", // yellow-500
	doc_section: "#facc15", // yellow-400
	doc_page: "#fde047", // yellow-300
	doc_block: "#fef08a", // yellow-200
	documentation: "#eab308", // yellow-500

	// Other common types
	workflow: "#0ea5e9", // sky-500
	process: "#38bdf8", // sky-400
	integration: "#7dd3fc", // sky-300
	deployment: "#0284c7", // sky-600
	database: "#0d9488", // teal-600
	bug: "#ef4444", // red-500
	issue: "#f87171", // red-400

	// Default
	default: "#64748b", // slate-500
};

// ============================================================================
// CATEGORY COLORS
// ============================================================================

export const CATEGORY_COLORS = {
	ui: "#3b82f6", // blue-500
	product: "#8b5cf6", // violet-500
	technical: "#10b981", // emerald-500
	test: "#f97316", // orange-500
	design: "#ec4899", // pink-500
	documentation: "#eab308", // yellow-500
	default: "#64748b", // slate-500
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get icon component for an entity type
 */
export function getTypeIcon(type: string): LucideIcon {
	const normalizedType = type.toLowerCase().replace(/[_-]/g, "_");
	return (TYPE_ICONS[normalizedType] ?? TYPE_ICONS["default"])!;
}

/**
 * Get color for an entity type
 */
export function getTypeColor(type: string): string {
	const normalizedType = type.toLowerCase().replace(/[_-]/g, "_");
	return (TYPE_COLORS[normalizedType] ?? TYPE_COLORS["default"])!;
}

/**
 * Get category for an entity type
 */
export function getTypeCategory(
	type: string,
):
	| "ui"
	| "product"
	| "technical"
	| "test"
	| "design"
	| "documentation"
	| "default" {
	const normalizedType = type.toLowerCase();

	// UI types
	if (
		[
			"site",
			"page",
			"layout",
			"section",
			"subsection",
			"component",
			"subcomponent",
			"element",
			"modal",
			"popup",
			"toast",
			"drawer",
			"ui",
			"wireframe",
			"mockup",
		].includes(normalizedType)
	) {
		return "ui";
	}

	// Product types
	if (
		[
			"initiative",
			"epic",
			"feature",
			"user_story",
			"story",
			"acceptance_criteria",
			"task",
			"subtask",
			"requirement",
		].includes(normalizedType)
	) {
		return "product";
	}

	// Technical types
	if (
		[
			"service",
			"module",
			"class",
			"function",
			"api_endpoint",
			"api",
			"database_table",
			"database_field",
			"config",
			"code",
			"workflow",
			"process",
			"integration",
			"deployment",
			"database",
		].includes(normalizedType)
	) {
		return "technical";
	}

	// Test types
	if (
		[
			"test_suite",
			"test_case",
			"test_step",
			"assertion",
			"fixture",
			"mock",
			"test",
		].includes(normalizedType)
	) {
		return "test";
	}

	// Design types
	if (
		[
			"wireframe",
			"mockup",
			"prototype",
			"design_token",
			"style_guide",
			"design",
		].includes(normalizedType)
	) {
		return "design";
	}

	// Documentation types
	if (
		[
			"doc_root",
			"doc_section",
			"doc_page",
			"doc_block",
			"documentation",
		].includes(normalizedType)
	) {
		return "documentation";
	}

	return "default";
}

/**
 * Get category color
 */
export function getCategoryColor(
	category:
		| "ui"
		| "product"
		| "technical"
		| "test"
		| "design"
		| "documentation"
		| "default",
): string {
	return CATEGORY_COLORS[category] ?? CATEGORY_COLORS.default;
}

/**
 * Get status color
 */
export function getStatusColor(status: string): string {
	const normalizedStatus = status.toLowerCase();

	switch (normalizedStatus) {
		case "todo":
		case "draft":
		case "pending":
			return "#94a3b8"; // slate-400
		case "in_progress":
		case "active":
		case "running":
			return "#3b82f6"; // blue-500
		case "done":
		case "complete":
		case "completed":
		case "approved":
			return "#22c55e"; // green-500
		case "blocked":
		case "failed":
		case "error":
			return "#ef4444"; // red-500
		case "cancelled":
		case "deprecated":
		case "archived":
			return "#6b7280"; // gray-500
		default:
			return "#94a3b8"; // slate-400
	}
}

/**
 * Get priority color
 */
export function getPriorityColor(priority: string): string {
	const normalizedPriority = priority.toLowerCase();

	switch (normalizedPriority) {
		case "critical":
		case "highest":
		case "p0":
			return "#ef4444"; // red-500
		case "high":
		case "p1":
			return "#f97316"; // orange-500
		case "medium":
		case "normal":
		case "p2":
			return "#eab308"; // yellow-500
		case "low":
		case "p3":
			return "#22c55e"; // green-500
		case "lowest":
		case "p4":
			return "#3b82f6"; // blue-500
		default:
			return "#64748b"; // slate-500
	}
}
