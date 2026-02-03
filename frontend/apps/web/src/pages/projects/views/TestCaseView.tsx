import type {
	AutomationStatus,
	TestCase,
	TestCasePriority,
	TestCaseStatus,
	TestCaseType,
} from "@tracertm/types";
import {
	CheckCircle,
	Clock,
	Cog,
	FileCheck,
	Filter,
	FlaskConical,
	PlayCircle,
	Plus,
	Search,
	XCircle,
} from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { CreateTestCaseForm } from "../../../components/forms/CreateTestCaseForm";
import { useTestCaseStats, useTestCases } from "../../../hooks/useTestCases";

const statusColors: Record<TestCaseStatus, string> = {
	approved: "bg-green-100 text-green-700",
	archived: "bg-slate-100 text-slate-700",
	deprecated: "bg-orange-100 text-orange-700",
	draft: "bg-gray-100 text-gray-700",
	review: "bg-yellow-100 text-yellow-700",
};

const priorityColors: Record<TestCasePriority, string> = {
	critical: "bg-red-500 text-white",
	high: "bg-orange-500 text-white",
	low: "bg-gray-300 text-gray-700",
	medium: "bg-yellow-500 text-black",
};

const automationColors: Record<AutomationStatus, string> = {
	automated: "bg-green-100 text-green-700",
	cannot_automate: "bg-red-100 text-red-700",
	in_progress: "bg-blue-100 text-blue-700",
	not_automated: "bg-gray-100 text-gray-600",
};

const statusLabels: Record<TestCaseStatus, string> = {
	approved: "Approved",
	archived: "Archived",
	deprecated: "Deprecated",
	draft: "Draft",
	review: "In Review",
};

const typeLabels: Record<TestCaseType, string> = {
	accessibility: "Accessibility",
	e2e: "E2E",
	exploratory: "Exploratory",
	functional: "Functional",
	integration: "Integration",
	performance: "Performance",
	regression: "Regression",
	security: "Security",
	smoke: "Smoke",
	unit: "Unit",
};

const automationLabels: Record<AutomationStatus, string> = {
	automated: "Automated",
	cannot_automate: "Cannot Automate",
	in_progress: "Automating",
	not_automated: "Manual",
};

interface TestCaseViewProps {
	projectId: string;
}

export function TestCaseView({ projectId }: TestCaseViewProps) {
	const [showCreateModal, setShowCreateModal] = useState(false);
	const [statusFilter, setStatusFilter] = useState<TestCaseStatus | "">("");
	const [typeFilter, setTypeFilter] = useState<TestCaseType | "">("");
	const [priorityFilter, setPriorityFilter] = useState<TestCasePriority | "">(
		"",
	);
	const [automationFilter, setAutomationFilter] = useState<
		AutomationStatus | ""
	>("");
	const [searchQuery, setSearchQuery] = useState("");

	const filters = {
		projectId,
		...(statusFilter && { status: statusFilter }),
		...(typeFilter && { testType: typeFilter }),
		...(priorityFilter && { priority: priorityFilter }),
		...(automationFilter && { automationStatus: automationFilter }),
		...(searchQuery && { search: searchQuery }),
	};
	const { data, isLoading, error } = useTestCases(filters);

	const { data: stats } = useTestCaseStats(projectId);

	const testCases = data?.testCases || [];

	const handleCreateSuccess = () => {
		setShowCreateModal(false);
	};

	// Surface load failures to the user via toast
	useEffect(() => {
		if (error) {
			toast.error("Failed to load test cases", {
				action: {
					label: "Retry",
					onClick: () => window.location.reload(),
				},
				description: error.message,
			});
		}
	}, [error]);

	if (error) {
		return (
			<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
				<p className="font-medium">Error loading test cases</p>
				<p className="mt-1 text-sm">{error.message}</p>
				<p className="mt-2 text-sm text-red-600">
					If the API reports missing tables, run Python migrations:{" "}
					<code className="rounded bg-red-100 px-1">
						./scripts/run_python_migrations.sh
					</code>
				</p>
			</div>
		);
	}

	// Calculate pass rate
	const passRate = stats?.executionSummary
		? (stats.executionSummary.totalRuns > 0
			? Math.round(
					(stats.executionSummary.totalPassed /
						stats.executionSummary.totalRuns) *
						100,
				)
			: 0)
		: 0;

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h3 className="text-lg font-semibold">Test Case Management</h3>
					<p className="text-sm text-muted-foreground">
						Create, manage, and track test cases for quality assurance
					</p>
				</div>
				<button
					onClick={() => setShowCreateModal(true)}
					className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
				>
					<Plus className="h-4 w-4" /> Create Test Case
				</button>
			</div>

			{/* Stats Cards */}
			{stats && (
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<FileCheck className="h-4 w-4 text-blue-500" />
							Total Test Cases
						</div>
						<div className="mt-2 text-2xl font-bold">{stats.total}</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<CheckCircle className="h-4 w-4 text-green-500" />
							Approved
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.approved || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Cog className="h-4 w-4 text-purple-500" />
							Automated
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byAutomationStatus?.automated || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<PlayCircle className="h-4 w-4 text-cyan-500" />
							Total Runs
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.executionSummary?.totalRuns || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<FlaskConical className="h-4 w-4 text-green-500" />
							Pass Rate
						</div>
						<div className="mt-2 text-2xl font-bold">{passRate}%</div>
					</div>
				</div>
			)}

			{/* Filters */}
			<div className="flex flex-wrap items-center gap-4">
				<div className="relative flex-1 min-w-[200px]">
					<Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
					<input
						type="text"
						placeholder="Search test cases..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="w-full rounded-lg border bg-background pl-10 pr-4 py-2"
					/>
				</div>
				<div className="flex items-center gap-2 flex-wrap">
					<Filter className="h-4 w-4 text-muted-foreground" />
					<select
						value={statusFilter}
						onChange={(e) =>
							setStatusFilter(e.target.value as TestCaseStatus | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Statuses</option>
						<option value="draft">Draft</option>
						<option value="review">In Review</option>
						<option value="approved">Approved</option>
						<option value="deprecated">Deprecated</option>
						<option value="archived">Archived</option>
					</select>
					<select
						value={typeFilter}
						onChange={(e) => setTypeFilter(e.target.value as TestCaseType | "")}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Types</option>
						<option value="functional">Functional</option>
						<option value="integration">Integration</option>
						<option value="unit">Unit</option>
						<option value="e2e">E2E</option>
						<option value="performance">Performance</option>
						<option value="security">Security</option>
						<option value="accessibility">Accessibility</option>
						<option value="regression">Regression</option>
						<option value="smoke">Smoke</option>
						<option value="exploratory">Exploratory</option>
					</select>
					<select
						value={priorityFilter}
						onChange={(e) =>
							setPriorityFilter(e.target.value as TestCasePriority | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Priorities</option>
						<option value="critical">Critical</option>
						<option value="high">High</option>
						<option value="medium">Medium</option>
						<option value="low">Low</option>
					</select>
					<select
						value={automationFilter}
						onChange={(e) =>
							setAutomationFilter(e.target.value as AutomationStatus | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Automation</option>
						<option value="not_automated">Manual</option>
						<option value="in_progress">Automating</option>
						<option value="automated">Automated</option>
						<option value="cannot_automate">Cannot Automate</option>
					</select>
				</div>
			</div>

			{/* Test Cases List */}
			{isLoading ? (
				<div className="flex items-center justify-center py-12">
					<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				</div>
			) : (testCases.length === 0 ? (
				<div className="rounded-lg border border-dashed p-12 text-center">
					<FlaskConical className="mx-auto h-12 w-12 text-muted-foreground" />
					<h3 className="mt-4 text-lg font-semibold">No test cases found</h3>
					<p className="mt-2 text-muted-foreground">
						{searchQuery ||
						statusFilter ||
						typeFilter ||
						priorityFilter ||
						automationFilter
							? "Try adjusting your filters"
							: "Create a new test case to get started"}
					</p>
					{!searchQuery &&
						!statusFilter &&
						!typeFilter &&
						!priorityFilter &&
						!automationFilter && (
							<button
								onClick={() => setShowCreateModal(true)}
								className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
							>
								Create Test Case
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
										Test Case
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Status
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Type
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Priority
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Automation
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Last Result
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Pass/Fail
									</th>
								</tr>
							</thead>
							<tbody>
								{testCases.map((testCase) => (
									<TestCaseRow key={testCase.id} testCase={testCase} />
								))}
							</tbody>
						</table>
					</div>
				</div>
			))}

			{/* Create Modal */}
			{showCreateModal && (
				<CreateTestCaseForm
					projectId={projectId}
					onCancel={() => setShowCreateModal(false)}
					onSuccess={handleCreateSuccess}
				/>
			)}
		</div>
	);
}

function TestCaseRow({ testCase }: { testCase: TestCase }) {
	return (
		<tr className="border-b hover:bg-muted/30">
			<td className="px-4 py-3">
				<div>
					<span className="text-xs text-muted-foreground">
						{testCase.testCaseNumber}
					</span>
					<div className="font-medium">{testCase.title}</div>
					{testCase.category && (
						<span className="text-xs text-muted-foreground">
							{testCase.category}
						</span>
					)}
				</div>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
						statusColors[testCase.status]
					}`}
				>
					{statusLabels[testCase.status]}
				</span>
			</td>
			<td className="px-4 py-3">
				<span className="text-sm">{typeLabels[testCase.testType]}</span>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
						priorityColors[testCase.priority]
					}`}
				>
					{testCase.priority}
				</span>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
						automationColors[testCase.automationStatus]
					}`}
				>
					{automationLabels[testCase.automationStatus]}
				</span>
			</td>
			<td className="px-4 py-3">
				{testCase.lastExecutionResult ? (
					<span
						className={`inline-flex items-center gap-1 text-sm ${
							testCase.lastExecutionResult === "passed"
								? "text-green-600"
								: (testCase.lastExecutionResult === "failed"
									? "text-red-600"
									: "text-yellow-600")
						}`}
					>
						{testCase.lastExecutionResult === "passed" ? (
							<CheckCircle className="h-4 w-4" />
						) : (testCase.lastExecutionResult === "failed" ? (
							<XCircle className="h-4 w-4" />
						) : (
							<Clock className="h-4 w-4" />
						))}
						{testCase.lastExecutionResult}
					</span>
				) : (
					<span className="text-muted-foreground">—</span>
				)}
			</td>
			<td className="px-4 py-3">
				{testCase.totalExecutions > 0 ? (
					<span className="text-sm">
						<span className="text-green-600">{testCase.passCount}</span>
						{" / "}
						<span className="text-red-600">{testCase.failCount}</span>
					</span>
				) : (
					<span className="text-muted-foreground">—</span>
				)}
			</td>
		</tr>
	);
}

export default TestCaseView;
