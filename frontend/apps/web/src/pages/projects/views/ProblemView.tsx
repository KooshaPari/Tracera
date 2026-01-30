import {
	AlertTriangle,
	CheckCircle,
	Clock,
	Plus,
	Search,
	Filter,
} from "lucide-react";
import { useState } from "react";
import { useProblems, useProblemStats } from "../../../hooks/useProblems";
import { CreateProblemForm } from "../../../components/forms/CreateProblemForm";
import type { Problem, ProblemStatus, ImpactLevel } from "@tracertm/types";

const statusColors: Record<ProblemStatus, string> = {
	open: "bg-red-100 text-red-700",
	in_investigation: "bg-yellow-100 text-yellow-700",
	pending_workaround: "bg-orange-100 text-orange-700",
	known_error: "bg-purple-100 text-purple-700",
	awaiting_fix: "bg-blue-100 text-blue-700",
	closed: "bg-green-100 text-green-700",
};

const impactColors: Record<ImpactLevel, string> = {
	critical: "bg-red-500 text-white",
	high: "bg-orange-500 text-white",
	medium: "bg-yellow-500 text-black",
	low: "bg-gray-300 text-gray-700",
};

const statusLabels: Record<ProblemStatus, string> = {
	open: "Open",
	in_investigation: "Investigating",
	pending_workaround: "Pending Workaround",
	known_error: "Known Error",
	awaiting_fix: "Awaiting Fix",
	closed: "Closed",
};

interface ProblemViewProps {
	projectId: string;
}

export function ProblemView({ projectId }: ProblemViewProps) {
	const [showCreateModal, setShowCreateModal] = useState(false);
	const [statusFilter, setStatusFilter] = useState<ProblemStatus | "">("");
	const [priorityFilter, setPriorityFilter] = useState<ImpactLevel | "">("");
	const [searchQuery, setSearchQuery] = useState("");

	const filters = {
		projectId,
		...(statusFilter && { status: statusFilter }),
		...(priorityFilter && { priority: priorityFilter }),
	};
	const { data, isLoading, error } = useProblems(filters);

	const { data: stats } = useProblemStats(projectId);

	const problems = data?.problems || [];
	const filteredProblems = problems.filter((p) =>
		p.title.toLowerCase().includes(searchQuery.toLowerCase()),
	);

	const handleCreateSuccess = () => {
		setShowCreateModal(false);
	};

	if (error) {
		return (
			<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
				Error loading problems: {error.message}
			</div>
		);
	}

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h3 className="text-lg font-semibold">Problem Management</h3>
					<p className="text-sm text-muted-foreground">
						Track and resolve problems with root cause analysis
					</p>
				</div>
				<button
					onClick={() => setShowCreateModal(true)}
					className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
				>
					<Plus className="h-4 w-4" /> Report Problem
				</button>
			</div>

			{/* Stats Cards */}
			{stats && (
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<AlertTriangle className="h-4 w-4 text-red-500" />
							Open Problems
						</div>
						<div className="mt-2 text-2xl font-bold">
							{(stats.byStatus?.["open"] || 0) +
								(stats.byStatus?.["in_investigation"] || 0)}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Clock className="h-4 w-4 text-yellow-500" />
							Known Errors
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.["known_error"] || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<CheckCircle className="h-4 w-4 text-green-500" />
							Resolved
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.["closed"] || 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<AlertTriangle className="h-4 w-4 text-orange-500" />
							Critical
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byPriority?.["critical"] || 0}
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
						placeholder="Search problems..."
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
							setStatusFilter(e.target.value as ProblemStatus | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Statuses</option>
						<option value="open">Open</option>
						<option value="in_investigation">Investigating</option>
						<option value="pending_workaround">Pending Workaround</option>
						<option value="known_error">Known Error</option>
						<option value="awaiting_fix">Awaiting Fix</option>
						<option value="closed">Closed</option>
					</select>
					<select
						value={priorityFilter}
						onChange={(e) =>
							setPriorityFilter(e.target.value as ImpactLevel | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Priorities</option>
						<option value="critical">Critical</option>
						<option value="high">High</option>
						<option value="medium">Medium</option>
						<option value="low">Low</option>
					</select>
				</div>
			</div>

			{/* Problems List */}
			{isLoading ? (
				<div className="flex items-center justify-center py-12">
					<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				</div>
			) : filteredProblems.length === 0 ? (
				<div className="rounded-lg border border-dashed p-12 text-center">
					<AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground" />
					<h3 className="mt-4 text-lg font-semibold">No problems found</h3>
					<p className="mt-2 text-muted-foreground">
						{searchQuery || statusFilter || priorityFilter
							? "Try adjusting your filters"
							: "Report a new problem to get started"}
					</p>
					{!searchQuery && !statusFilter && !priorityFilter && (
						<button
							onClick={() => setShowCreateModal(true)}
							className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
						>
							Report Problem
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
										Problem
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Status
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Priority
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Impact
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Assigned
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										RCA
									</th>
									<th className="px-4 py-3 text-left text-sm font-medium">
										Created
									</th>
								</tr>
							</thead>
							<tbody>
								{filteredProblems.map((problem) => (
									<ProblemRow key={problem.id} problem={problem} />
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}

			{/* Create Modal */}
			{showCreateModal && (
				<CreateProblemForm
					projectId={projectId}
					onCancel={() => setShowCreateModal(false)}
					onSuccess={handleCreateSuccess}
				/>
			)}
		</div>
	);
}

function ProblemRow({ problem }: { problem: Problem }) {
	const createdDate = problem.createdAt
		? new Date(problem.createdAt).toLocaleDateString()
		: "—";

	return (
		<tr className="border-b hover:bg-muted/30">
			<td className="px-4 py-3">
				<div>
					<span className="text-xs text-muted-foreground">
						{problem.problemNumber}
					</span>
					<div className="font-medium">{problem.title}</div>
					{problem.category && (
						<span className="text-xs text-muted-foreground">
							{problem.category}
						</span>
					)}
				</div>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
						statusColors[problem.status]
					}`}
				>
					{statusLabels[problem.status]}
				</span>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
						impactColors[problem.priority]
					}`}
				>
					{problem.priority}
				</span>
			</td>
			<td className="px-4 py-3">
				<span
					className={`inline-flex rounded px-2 py-0.5 text-xs font-medium ${
						impactColors[problem.impactLevel]
					}`}
				>
					{problem.impactLevel}
				</span>
			</td>
			<td className="px-4 py-3">
				<span className="text-sm">{problem.assignedTo || "—"}</span>
			</td>
			<td className="px-4 py-3">
				{problem.rootCauseIdentified ? (
					<span className="text-green-600">✓ Identified</span>
				) : problem.workaroundAvailable ? (
					<span className="text-yellow-600">Workaround</span>
				) : (
					<span className="text-muted-foreground">—</span>
				)}
			</td>
			<td className="px-4 py-3 text-sm text-muted-foreground">{createdDate}</td>
		</tr>
	);
}

export default ProblemView;
