import type { TestSuite, TestSuiteStatus } from "@tracertm/types";
import {
	CheckCircle,
	Clock,
	Filter,
	FolderKanban,
	Layers,
	Plus,
	Search,
} from "lucide-react";
import { useState } from "react";
import { useTestSuiteStats, useTestSuites } from "../../../hooks/useTestSuites";

const statusColors: Record<TestSuiteStatus, string> = {
	draft: "bg-gray-100 text-gray-700",
	active: "bg-green-100 text-green-700",
	deprecated: "bg-yellow-100 text-yellow-700",
	archived: "bg-red-100 text-red-700",
};

const statusLabels: Record<TestSuiteStatus, string> = {
	draft: "Draft",
	active: "Active",
	deprecated: "Deprecated",
	archived: "Archived",
};

interface TestSuiteViewProps {
	projectId: string;
}

export function TestSuiteView({ projectId }: TestSuiteViewProps) {
	const [showCreateModal, setShowCreateModal] = useState(false);
	const [statusFilter, setStatusFilter] = useState<TestSuiteStatus | "">("");
	const [categoryFilter, setCategoryFilter] = useState("");
	const [searchQuery, setSearchQuery] = useState("");

	const filters = {
		projectId,
		...(statusFilter && { status: statusFilter }),
		...(categoryFilter && { category: categoryFilter }),
	};
	const { data, isLoading, error } = useTestSuites(filters);

	const { data: stats } = useTestSuiteStats(projectId);

	const testSuites = data?.testSuites || [];
	const filteredSuites = testSuites.filter((s) =>
		s.name.toLowerCase().includes(searchQuery.toLowerCase()),
	);

	const handleCreateSuccess = () => {
		setShowCreateModal(false);
	};

	if (error) {
		return (
			<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
				Error loading test suites: {error.message}
			</div>
		);
	}

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h3 className="text-lg font-semibold">Test Suites</h3>
					<p className="text-sm text-muted-foreground">
						Organize test cases into logical groups
					</p>
				</div>
				<button
					onClick={() => setShowCreateModal(true)}
					className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
				>
					<Plus className="h-4 w-4" /> New Suite
				</button>
			</div>

			{/* Stats Cards */}
			{stats && (
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<FolderKanban className="h-4 w-4 text-blue-500" />
							Total Suites
						</div>
						<div className="mt-2 text-2xl font-bold">{stats.total || 0}</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<CheckCircle className="h-4 w-4 text-green-500" />
							Active
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.active || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Layers className="h-4 w-4 text-purple-500" />
							Total Test Cases
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.totalTestCases || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Clock className="h-4 w-4 text-cyan-500" />
							Automated
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.automatedTestCases || 0}
						</div>
					</div>
				</div>
			)}

			{/* Filters */}
			<div className="flex flex-wrap items-center gap-4">
				<div className="relative flex-1 min-w-[200px]">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
					<input
						type="text"
						placeholder="Search suites..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="w-full rounded-lg border bg-background pl-10 pr-4 py-2"
					/>
				</div>
				<div className="flex items-center gap-2">
					<Filter className="h-4 w-4 text-muted-foreground" />
					<select
						value={statusFilter}
						onChange={(e) =>
							setStatusFilter(e.target.value as TestSuiteStatus | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Statuses</option>
						<option value="draft">Draft</option>
						<option value="active">Active</option>
						<option value="deprecated">Deprecated</option>
						<option value="archived">Archived</option>
					</select>
					<input
						type="text"
						placeholder="Category..."
						value={categoryFilter}
						onChange={(e) => setCategoryFilter(e.target.value)}
						className="w-32 rounded-lg border bg-background px-3 py-2"
					/>
				</div>
			</div>

			{/* Test Suites List */}
			{isLoading ? (
				<div className="flex items-center justify-center py-12">
					<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				</div>
			) : filteredSuites.length === 0 ? (
				<div className="rounded-lg border border-dashed p-12 text-center">
					<FolderKanban className="mx-auto h-12 w-12 text-muted-foreground" />
					<h3 className="mt-4 text-lg font-semibold">No test suites found</h3>
					<p className="mt-2 text-muted-foreground">
						{searchQuery || statusFilter || categoryFilter
							? "Try adjusting your filters"
							: "Create a new test suite to get started"}
					</p>
					{!searchQuery && !statusFilter && !categoryFilter && (
						<button
							onClick={() => setShowCreateModal(true)}
							className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
						>
							New Suite
						</button>
					)}
				</div>
			) : (
				<div className="rounded-lg border">
					<div className="overflow-x-auto">
						<table className="w-full">
							<thead>
								<tr className="border-b bg-muted/50">
									<th className="px-4 py-3 text-left text-sm font-medium">
										Suite
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Status
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Category
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Test Cases
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Automated
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Pass Rate
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Owner
									</th>
								</tr>
							</thead>
							<tbody>
								{filteredSuites.map((suite) => (
									<TestSuiteRow key={suite.id} suite={suite} />
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}

			{/* Create Modal - placeholder */}
			{showCreateModal && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
					<div
						className="w-full max-w-lg rounded-lg bg-background p-6 shadow-lg"
						role="dialog"
						aria-modal="true"
						aria-labelledby="create-test-suite-title"
					>
						<div className="flex items-center justify-between mb-4">
							<h2 id="create-test-suite-title" className="text-lg font-semibold">
								Create Test Suite
							</h2>
							<button
								type="button"
								onClick={() => setShowCreateModal(false)}
								aria-label="Close dialog"
								className="rounded-lg p-1 hover:bg-accent"
							>
								✕
							</button>
						</div>
						<div className="space-y-3">
							<div>
								<label className="text-xs font-semibold uppercase">
									Suite Name
								</label>
								<input
									type="text"
									placeholder="e.g. Unit Tests, Integration Tests"
									className="mt-1 w-full rounded-lg border bg-muted/50 px-3 py-2 text-sm"
									defaultValue="New Test Suite"
								/>
							</div>
							<div>
								<label className="text-xs font-semibold uppercase">
									Description
								</label>
								<textarea
									placeholder="Test suite description and scope..."
									className="mt-1 w-full rounded-lg border bg-muted/50 px-3 py-2 text-sm min-h-[60px]"
									defaultValue=""
								/>
							</div>
							<div>
								<label className="text-xs font-semibold uppercase">
									Test Type
								</label>
								<select className="mt-1 w-full rounded-lg border bg-muted/50 px-3 py-2 text-sm">
									<option>Unit Tests</option>
									<option>Integration Tests</option>
									<option>E2E Tests</option>
									<option>Performance Tests</option>
									<option>Security Tests</option>
									<option>Accessibility Tests</option>
								</select>
							</div>
						</div>
						<div className="mt-6 flex justify-end gap-2">
							<button
								onClick={() => setShowCreateModal(false)}
								className="rounded-lg border px-4 py-2 text-sm"
							>
								Cancel
							</button>
							<button
								onClick={handleCreateSuccess}
								className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
							>
								Create
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}

function TestSuiteRow({ suite }: { suite: TestSuite }) {
	const automationPercent =
		suite.totalTestCases > 0
			? Math.round((suite.automatedCount / suite.totalTestCases) * 100)
			: 0;

	return (
		<tr className="border-b hover:bg-muted/30">
			<td className="px-4 py-3">
				<div>
					<span className="text-xs text-muted-foreground">
						{suite.suiteNumber}
					</span>
					<div className="font-medium">{suite.name}</div>
					{suite.description && (
						<span className="text-xs text-muted-foreground line-clamp-1">
							{suite.description}
						</span>
					)}
				</div>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
						statusColors[suite.status]
					}`}
				>
					{statusLabels[suite.status]}
				</span>
			</td>
			<td className="px-4 py-3">
				<span className="text-sm">{suite.category || "—"}</span>
			</td>
			<td className="px-4 py-3">
				<span className="text-sm font-medium">{suite.totalTestCases}</span>
			</td>
			<td className="px-4 py-3">
				<div className="flex items-center gap-2">
					<div className="h-2 w-16 rounded-full bg-gray-200">
						<div
							className="h-2 rounded-full bg-cyan-500"
							style={{ width: `${automationPercent}%` }}
						/>
					</div>
					<span className="text-xs text-muted-foreground">
						{automationPercent}%
					</span>
				</div>
			</td>
			<td className="px-4 py-3">
				{suite.passRate !== undefined && suite.passRate !== null ? (
					<span
						className={`text-sm font-medium ${
							suite.passRate >= 90
								? "text-green-600"
								: suite.passRate >= 70
									? "text-yellow-600"
									: "text-red-600"
						}`}
					>
						{suite.passRate.toFixed(1)}%
					</span>
				) : (
					<span className="text-muted-foreground">—</span>
				)}
			</td>
			<td className="px-4 py-3">
				<span className="text-sm">{suite.owner || "—"}</span>
			</td>
		</tr>
	);
}

export default TestSuiteView;
