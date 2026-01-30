/**
 * DesignTokenBrowser Component Example
 * Demonstrates usage patterns for the Design Token Browser component
 */

import { useState } from "react";
import { DesignTokenBrowser } from "./DesignTokenBrowser";
import type { DesignToken } from "@tracertm/types";

/**
 * Example 1: Basic Usage
 * Shows the component with minimal configuration
 */
export function BasicExample() {
	const tokens: DesignToken[] = [
		{
			id: "color-primary",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary",
			path: ["colors", "primary", "500"],
			description: "Primary brand color",
			type: "color",
			value: "#3B82F6",
			resolvedValue: "#3B82F6",
			usageCount: 12,
			usedByComponentIds: ["btn-1"],
			tags: ["brand"],
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return <DesignTokenBrowser tokens={tokens} />;
}

/**
 * Example 2: With Selection Handling
 * Demonstrates token selection callbacks
 */
export function SelectionExample() {
	const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);

	const tokens: DesignToken[] = [
		{
			id: "color-1",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary",
			path: ["colors", "primary", "500"],
			type: "color",
			value: "#3B82F6",
			resolvedValue: "#3B82F6",
			usageCount: 12,
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
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return (
		<div className="space-y-4">
			<div>
				<h3 className="text-sm font-medium">Selected Token:</h3>
				<p className="text-xs text-muted-foreground">
					{selectedTokenId ? `ID: ${selectedTokenId}` : "None selected"}
				</p>
			</div>
			<DesignTokenBrowser
				tokens={tokens}
				selectedTokenId={selectedTokenId}
				onSelectToken={setSelectedTokenId}
			/>
		</div>
	);
}

/**
 * Example 3: With Component Usage Tracking
 * Shows which components use each token
 */
export function ComponentUsageExample() {
	// Map component IDs to human-readable names
	const componentMap = new Map([
		["btn-primary", "Button Primary"],
		["btn-secondary", "Button Secondary"],
		["link-default", "Link Default"],
		["card-header", "Card Header"],
	]);

	const tokens: DesignToken[] = [
		{
			id: "color-primary",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary",
			path: ["colors", "primary", "500"],
			description: "Primary brand color",
			type: "color",
			value: "#3B82F6",
			resolvedValue: "#3B82F6",
			usageCount: 12,
			usedByComponentIds: ["btn-primary", "link-default", "card-header"],
			tags: ["brand", "interactive"],
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		{
			id: "spacing-md",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "md",
			path: ["spacing", "md"],
			type: "spacing",
			value: "1rem",
			resolvedValue: "1rem",
			usageCount: 25,
			usedByComponentIds: ["btn-primary", "btn-secondary", "card-header"],
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return (
		<DesignTokenBrowser
			tokens={tokens}
			showComponentUsage={true}
			componentMap={componentMap}
		/>
	);
}

/**
 * Example 4: With Figma Integration
 * Shows synced Figma tokens and linking capability
 */
export function FigmaIntegrationExample() {
	const handleLinkToFigma = async (tokenId: string) => {
		console.log(`Linking token ${tokenId} to Figma...`);
		// In a real app, this would call your API
	};

	const tokens: DesignToken[] = [
		{
			id: "color-primary",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary",
			path: ["colors", "primary", "500"],
			type: "color",
			value: "#3B82F6",
			resolvedValue: "#3B82F6",
			usageCount: 12,
			figmaStyleId: "figma-style-abc123", // Already synced
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		{
			id: "color-secondary",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "secondary",
			path: ["colors", "secondary", "500"],
			type: "color",
			value: "#10B981",
			resolvedValue: "#10B981",
			usageCount: 8,
			// Not synced - user can link it
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return (
		<DesignTokenBrowser tokens={tokens} onLinkToFigma={handleLinkToFigma} />
	);
}

/**
 * Example 5: With Token References
 * Shows tokens that reference other tokens
 */
export function TokenReferencesExample() {
	const tokens: DesignToken[] = [
		{
			id: "color-primary-500",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary.500",
			path: ["colors", "primary", "500"],
			type: "color",
			value: "#3B82F6",
			resolvedValue: "#3B82F6",
			usageCount: 5,
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		{
			id: "color-primary-light",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary.light",
			path: ["colors", "primary", "light"],
			description: "Lighter shade of primary color",
			type: "color",
			value: "{colors.primary.500}",
			resolvedValue: "#3B82F6",
			referencesTokenId: "color-primary-500", // References primary.500
			usageCount: 8,
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		{
			id: "color-primary-dark",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "primary.dark",
			path: ["colors", "primary", "dark"],
			description: "Darker shade of primary color",
			type: "color",
			value: "{colors.primary.500}",
			resolvedValue: "#3B82F6",
			referencesTokenId: "color-primary-500",
			usageCount: 6,
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return <DesignTokenBrowser tokens={tokens} />;
}

/**
 * Example 6: Full Featured Example
 * Demonstrates all features combined
 */
export function FullFeaturedExample() {
	const [selectedTokenId, setSelectedTokenId] = useState<string | null>(null);

	const componentMap = new Map([
		["btn-1", "Button Primary"],
		["btn-2", "Button Secondary"],
		["link-1", "Link Text"],
	]);

	const handleLinkToFigma = async (tokenId: string) => {
		console.log(`Linking token ${tokenId} to Figma...`);
		// Call your API
	};

	const tokens: DesignToken[] = [
		// Colors
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
			usedByComponentIds: ["btn-1", "link-1"],
			tags: ["brand", "interactive"],
			figmaStyleId: "figma-1",
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
			usedByComponentIds: ["btn-2"],
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		// Spacing
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
			usedByComponentIds: ["btn-1", "btn-2"],
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
			usedByComponentIds: ["btn-1"],
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		// Typography
		{
			id: "typo-1",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "body",
			path: ["typography", "body"],
			type: "typography",
			value: '16px/1.5 "Inter", sans-serif',
			resolvedValue: '16px/1.5 "Inter", sans-serif',
			usageCount: 25,
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
		// Shadows
		{
			id: "shadow-1",
			libraryId: "lib-1",
			projectId: "proj-1",
			name: "lg",
			path: ["shadows", "lg"],
			type: "shadow",
			value: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
			resolvedValue: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
			usageCount: 5,
			createdAt: "2024-01-01T00:00:00Z",
			updatedAt: "2024-01-01T00:00:00Z",
		},
	];

	return (
		<div className="space-y-4">
			<div>
				<h2 className="text-sm font-semibold">Selected Token</h2>
				<p className="text-xs text-muted-foreground">
					{selectedTokenId ? `ID: ${selectedTokenId}` : "None selected"}
				</p>
			</div>
			<DesignTokenBrowser
				tokens={tokens}
				selectedTokenId={selectedTokenId}
				onSelectToken={setSelectedTokenId}
				onLinkToFigma={handleLinkToFigma}
				showComponentUsage={true}
				componentMap={componentMap}
			/>
		</div>
	);
}

/**
 * Example Usage Index
 * Demonstrates all examples in a tabbed interface
 */
export function ExamplesShowcase() {
	const [activeExample, setActiveExample] = useState<
		"basic" | "selection" | "usage" | "figma" | "references" | "full"
	>("full");

	const examples = {
		basic: {
			title: "Basic Usage",
			description: "Minimal configuration example",
			component: <BasicExample />,
		},
		selection: {
			title: "Token Selection",
			description: "Handle token selection events",
			component: <SelectionExample />,
		},
		usage: {
			title: "Component Usage",
			description: "Track component usage of tokens",
			component: <ComponentUsageExample />,
		},
		figma: {
			title: "Figma Integration",
			description: "Sync tokens with Figma styles",
			component: <FigmaIntegrationExample />,
		},
		references: {
			title: "Token References",
			description: "Display token-to-token references",
			component: <TokenReferencesExample />,
		},
		full: {
			title: "Full Featured",
			description: "All features combined",
			component: <FullFeaturedExample />,
		},
	};

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-2xl font-bold">DesignTokenBrowser Examples</h1>
				<p className="text-sm text-muted-foreground mt-1">
					Browse through different usage patterns
				</p>
			</div>

			{/* Tab buttons */}
			<div className="flex gap-2 flex-wrap">
				{(Object.keys(examples) as Array<keyof typeof examples>).map((key) => (
					<button
						key={key}
						onClick={() => setActiveExample(key)}
						className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
							activeExample === key
								? "bg-primary text-primary-foreground"
								: "bg-muted text-foreground hover:bg-muted/80"
						}`}
					>
						{examples[key].title}
					</button>
				))}
			</div>

			{/* Description */}
			<div className="text-sm text-muted-foreground">
				{examples[activeExample].description}
			</div>

			{/* Example content */}
			<div className="border rounded-lg p-4 h-[600px] overflow-hidden">
				{examples[activeExample].component}
			</div>
		</div>
	);
}
