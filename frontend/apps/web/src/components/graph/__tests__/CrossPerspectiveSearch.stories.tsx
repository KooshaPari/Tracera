import type { Meta, StoryObj } from "@storybook/react";
import { logger } from '@/lib/logger';
import type { Item, Link } from "@tracertm/types";
import { useState } from "react";
import { CrossPerspectiveSearch } from "../CrossPerspectiveSearch";

const meta = {
	title: "Graph/CrossPerspectiveSearch",
	component: CrossPerspectiveSearch,
	parameters: {
		layout: "padded",
	},
	tags: ["autodocs"],
} satisfies Meta<typeof CrossPerspectiveSearch>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Sample data for stories
 */
const createSampleItems = (): Item[] => [
	{
		id: "feat-auth",
		projectId: "proj-1",
		view: "feature",
		type: "Feature",
		title: "User Authentication System",
		description:
			"Implement OAuth 2.0 based user authentication with social login support",
		status: "in_progress",
		priority: "critical",
		perspective: "feature",
		version: 1,
		createdAt: "2025-01-01",
		updatedAt: "2025-01-28",
		owner: "alice@example.com",
	},
	{
		id: "code-auth-service",
		projectId: "proj-1",
		view: "code",
		type: "Service",
		title: "AuthenticationService",
		description:
			"Core service implementing OAuth 2.0 flows and token management",
		status: "done",
		priority: "critical",
		perspective: "code",
		version: 2,
		createdAt: "2025-01-05",
		updatedAt: "2025-01-27",
		equivalentItemIds: ["feat-auth"],
	},
	{
		id: "code-login-component",
		projectId: "proj-1",
		view: "code",
		type: "Component",
		title: "LoginForm",
		description:
			"React component for user login interface with form validation",
		status: "done",
		priority: "high",
		perspective: "code",
		version: 3,
		createdAt: "2025-01-10",
		updatedAt: "2025-01-25",
	},
	{
		id: "test-auth",
		projectId: "proj-1",
		view: "test",
		type: "TestSuite",
		title: "Authentication Integration Tests",
		description: "Comprehensive tests for auth flows including edge cases",
		status: "in_progress",
		priority: "high",
		perspective: "test",
		version: 1,
		createdAt: "2025-01-12",
		updatedAt: "2025-01-28",
	},
	{
		id: "api-login",
		projectId: "proj-1",
		view: "api",
		type: "Endpoint",
		title: "POST /api/auth/login",
		description: "User login endpoint accepting email and password",
		status: "done",
		priority: "critical",
		perspective: "api",
		version: 1,
		createdAt: "2025-01-01",
		updatedAt: "2025-01-20",
		equivalentItemIds: ["feat-auth"],
	},
	{
		id: "api-refresh",
		projectId: "proj-1",
		view: "api",
		type: "Endpoint",
		title: "POST /api/auth/refresh",
		description: "Token refresh endpoint",
		status: "done",
		priority: "high",
		perspective: "api",
		version: 1,
		createdAt: "2025-01-02",
		updatedAt: "2025-01-20",
	},
	{
		id: "db-users",
		projectId: "proj-1",
		view: "database",
		type: "Table",
		title: "users_table",
		description: "Stores user account information and auth credentials",
		status: "done",
		priority: "critical",
		perspective: "database",
		version: 1,
		createdAt: "2025-01-01",
		updatedAt: "2025-01-15",
	},
	{
		id: "db-sessions",
		projectId: "proj-1",
		view: "database",
		type: "Table",
		title: "sessions_table",
		description: "Stores active user sessions and tokens",
		status: "done",
		priority: "high",
		perspective: "database",
		version: 1,
		createdAt: "2025-01-03",
		updatedAt: "2025-01-15",
	},
	{
		id: "wire-login",
		projectId: "proj-1",
		view: "wireframe",
		type: "Wireframe",
		title: "Login Page Layout",
		description: "Wireframe showing login form layout and components",
		status: "done",
		priority: "medium",
		perspective: "wireframe",
		version: 2,
		createdAt: "2025-01-08",
		updatedAt: "2025-01-22",
	},
	{
		id: "sec-auth",
		projectId: "proj-1",
		view: "security",
		type: "SecurityControl",
		title: "Authentication Security Hardening",
		description:
			"Implement rate limiting, CSRF protection, and secure token storage",
		status: "blocked",
		priority: "critical",
		perspective: "security",
		version: 1,
		createdAt: "2025-01-20",
		updatedAt: "2025-01-28",
	},
	{
		id: "perf-auth",
		projectId: "proj-1",
		view: "performance",
		type: "PerformanceOptimization",
		title: "Auth Endpoint Optimization",
		description: "Optimize login endpoint response time (target: <200ms)",
		status: "todo",
		priority: "medium",
		perspective: "performance",
		version: 1,
		createdAt: "2025-01-25",
		updatedAt: "2025-01-25",
	},
];

const createSampleLinks = (): Link[] => [
	{
		id: "link-1",
		projectId: "proj-1",
		sourceId: "feat-auth",
		targetId: "code-auth-service",
		type: "represents",
		confidence: 0.95,
		status: "confirmed",
		createdAt: "2025-01-10",
	},
	{
		id: "link-2",
		projectId: "proj-1",
		sourceId: "feat-auth",
		targetId: "api-login",
		type: "same_as",
		confidence: 0.98,
		status: "confirmed",
		createdAt: "2025-01-10",
	},
	{
		id: "link-3",
		projectId: "proj-1",
		sourceId: "code-auth-service",
		targetId: "db-users",
		type: "depends_on",
		confidence: 1.0,
		status: "auto",
		createdAt: "2025-01-10",
	},
	{
		id: "link-4",
		projectId: "proj-1",
		sourceId: "test-auth",
		targetId: "feat-auth",
		type: "tests",
		confidence: 0.9,
		status: "confirmed",
		createdAt: "2025-01-15",
	},
	{
		id: "link-5",
		projectId: "proj-1",
		sourceId: "wire-login",
		targetId: "code-login-component",
		type: "represents",
		confidence: 0.85,
		status: "suggested",
		createdAt: "2025-01-20",
	},
	{
		id: "link-6",
		projectId: "proj-1",
		sourceId: "sec-auth",
		targetId: "feat-auth",
		type: "related_to",
		confidence: 0.8,
		status: "confirmed",
		createdAt: "2025-01-25",
	},
];

/**
 * Basic full-featured search component
 */
export const Default: Story = {
	render: () => {
		const [selectedId, setSelectedId] = useState<string | null>(null);
		const [highlightedId, setHighlightedId] = useState<string | null>(null);

		return (
			<div className="max-w-4xl mx-auto space-y-4">
				<CrossPerspectiveSearch
					items={createSampleItems()}
					links={createSampleLinks()}
					onSelect={(itemId) => {
						setSelectedId(itemId);
						logger.info("Selected item:", itemId);
					}}
					onHighlight={(itemId) => {
						setHighlightedId(itemId);
						logger.info("Highlighted item:", itemId);
					}}
				/>
				{selectedId && (
					<div className="p-4 bg-accent rounded-lg border">
						<p className="text-sm font-semibold">Selected item ID:</p>
						<code className="text-xs">{selectedId}</code>
					</div>
				)}
			</div>
		);
	},
};

/**
 * Compact search component for inline use
 */
export const Compact: Story = {
	render: () => {
		const [selectedId, setSelectedId] = useState<string | null>(null);

		return (
			<div className="max-w-2xl mx-auto space-y-4">
				<div className="p-4 bg-muted rounded-lg">
					<p className="text-sm font-semibold mb-3">
						Compact Mode (inline search)
					</p>
					<CrossPerspectiveSearch
						items={createSampleItems()}
						links={createSampleLinks()}
						onSelect={(itemId) => setSelectedId(itemId)}
						onHighlight={() => {}}
						compact={true}
					/>
				</div>
				{selectedId && (
					<div className="p-4 bg-accent rounded-lg border">
						<p className="text-sm font-semibold">Selected:</p>
						<code className="text-xs">{selectedId}</code>
					</div>
				)}
			</div>
		);
	},
};

/**
 * Search with demonstrated keyboard navigation
 */
export const KeyboardNavigation: Story = {
	render: () => {
		const [selectedId, setSelectedId] = useState<string | null>(null);
		const [keyboardTips] = useState(
			"Use ↑↓ to navigate results | Enter to select | Esc to clear",
		);

		return (
			<div className="max-w-4xl mx-auto space-y-4">
				<div className="p-3 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded text-sm">
					<p className="font-semibold text-blue-900 dark:text-blue-100">
						Keyboard Navigation
					</p>
					<p className="text-blue-700 dark:text-blue-300 text-xs">
						{keyboardTips}
					</p>
				</div>
				<CrossPerspectiveSearch
					items={createSampleItems()}
					links={createSampleLinks()}
					onSelect={(itemId) => setSelectedId(itemId)}
					onHighlight={() => {}}
				/>
				{selectedId && (
					<div className="p-4 bg-accent rounded-lg border">
						<p className="text-sm">
							Selected: <code className="text-xs font-mono">{selectedId}</code>
						</p>
					</div>
				)}
			</div>
		);
	},
};

/**
 * Search demonstrating cross-perspective linking
 */
export const CrossPerspectiveExample: Story = {
	render: () => {
		const [selectedId, setSelectedId] = useState<string | null>(null);

		return (
			<div className="max-w-4xl mx-auto space-y-4">
				<div className="space-y-2">
					<h2 className="text-lg font-bold">
						Cross-Perspective Search Example
					</h2>
					<p className="text-sm text-muted-foreground">
						Try searching for "auth" to see how the same concept appears in
						multiple perspectives (Feature, Code, API, Database, etc.) with
						equivalence relationships shown below each result.
					</p>
				</div>
				<CrossPerspectiveSearch
					items={createSampleItems()}
					links={createSampleLinks()}
					onSelect={(itemId) => {
						setSelectedId(itemId);
						logger.info("Selected:", itemId);
					}}
					onHighlight={() => {}}
					maxResultsPerPerspective={3}
				/>
				{selectedId && (
					<div className="p-4 bg-accent rounded-lg border space-y-2">
						<p className="text-sm font-semibold">Selected Item</p>
						<code className="text-xs block">{selectedId}</code>
						<p className="text-xs text-muted-foreground">
							This item now shows in the details panel and its equivalences are
							highlighted
						</p>
					</div>
				)}
			</div>
		);
	},
};

/**
 * Empty state
 */
export const EmptyState: Story = {
	render: () => {
		return (
			<div className="max-w-4xl mx-auto">
				<CrossPerspectiveSearch
					items={[]}
					links={[]}
					onSelect={() => {}}
					onHighlight={() => {}}
				/>
			</div>
		);
	},
};

/**
 * With custom max results per perspective
 */
export const CustomMaxResults: Story = {
	render: () => {
		return (
			<div className="max-w-4xl mx-auto space-y-4">
				<p className="text-sm text-muted-foreground">
					Showing only 2 results per perspective (normally 5)
				</p>
				<CrossPerspectiveSearch
					items={createSampleItems()}
					links={createSampleLinks()}
					onSelect={(id) => logger.info("Selected:", id)}
					onHighlight={() => {}}
					maxResultsPerPerspective={2}
				/>
			</div>
		);
	},
};
