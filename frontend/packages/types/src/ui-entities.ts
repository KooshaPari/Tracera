// UI Dimension Entity Types
// Extends entity-hierarchy.ts with UI-specific item types for the UI dimension
// Supports page decomposition, component libraries, and design system integration

import type { CodeReference } from "./canonical";
import type { UIEntityType } from "./entity-hierarchy";

// =============================================================================
// UI ITEM (Extended Item for UI Dimension)
// =============================================================================

/**
 * Extended Item type specifically for UI entities
 * Includes additional fields for UI-specific metadata
 */
export interface UIItem {
	id: string;
	projectId: string;

	// Type information
	entityType: UIEntityType;

	// Identity
	name: string;
	title: string;
	description?: string;

	// Hierarchy
	parentId?: string;
	path: string[]; // Full path from root: ["site-1", "page-2", ...]
	depth: number;
	hasChildren: boolean;
	childCount: number;
	childIds?: string[];

	// UI-specific metadata
	route?: string; // URL route for pages
	componentName?: string; // React/Vue component name
	componentPath?: string; // Path to component file

	// Visual information
	screenshot?: UIScreenshot;
	boundingBox?: BoundingBox;

	// Interaction
	interactions?: UIInteraction[];

	// Code reference
	codeRef?: CodeReference;

	// Design system reference
	designTokenRefs?: DesignTokenRef[];
	libraryComponentRef?: LibraryComponentRef;

	// Status
	status: "draft" | "active" | "deprecated" | "archived";

	// Timestamps
	createdAt: string;
	updatedAt: string;
	version: number;
}

/**
 * Screenshot/thumbnail for UI entities
 */
export interface UIScreenshot {
	thumbnailUrl?: string; // Small thumbnail
	screenshotUrl?: string; // Full screenshot
	width?: number;
	height?: number;
	capturedAt?: string;
	viewport?: string; // "desktop" | "tablet" | "mobile"
}

/**
 * Bounding box for element positioning
 */
export interface BoundingBox {
	x: number;
	y: number;
	width: number;
	height: number;
	// Relative to parent or viewport
	relativeTo: "parent" | "viewport" | "page";
}

/**
 * UI interaction definition
 */
export interface UIInteraction {
	id: string;
	type: UIInteractionType;
	trigger: UITrigger;
	targetId?: string; // Target element/page
	targetRoute?: string; // Target route for navigation
	description?: string;
}

export type UIInteractionType =
	| "navigate" // Page navigation
	| "open_modal" // Open modal/dialog
	| "close_modal" // Close modal/dialog
	| "open_drawer" // Open drawer/sidebar
	| "toggle" // Toggle state
	| "submit" // Form submission
	| "expand" // Expand/collapse
	| "scroll_to" // Scroll to element
	| "external_link" // External navigation
	| "api_call"; // Trigger API call

export type UITrigger =
	| "click"
	| "double_click"
	| "hover"
	| "focus"
	| "blur"
	| "submit"
	| "change"
	| "keypress"
	| "scroll"
	| "load";

// =============================================================================
// DESIGN TOKEN REFERENCES
// =============================================================================

/**
 * Reference to a design token used by a UI element
 */
export interface DesignTokenRef {
	tokenId: string;
	tokenName: string; // e.g., "colors.primary.500"
	tokenType: DesignTokenType;
	value: string; // Resolved value
	usage: string; // How it's used: "background", "border", etc.
}

export type DesignTokenType =
	| "color"
	| "spacing"
	| "typography"
	| "shadow"
	| "border"
	| "radius"
	| "opacity"
	| "z-index"
	| "breakpoint"
	| "animation"
	| "custom";

/**
 * Reference to a component from a component library
 */
export interface LibraryComponentRef {
	libraryId: string;
	componentId: string;
	componentName: string;
	version?: string;
	props?: Record<string, unknown>;
	variants?: string[];
}
