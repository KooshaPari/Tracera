/* eslint-disable complexity, func-style, max-lines-per-function, react-perf/jsx-no-new-function-as-prop */
import type {
	Process,
	ProcessCategory,
	ProcessStatus,
} from "../../../../../../packages/types/src/index";
import { CreateProcessForm } from "../../../components/forms/CreateProcessForm";
import { useProcessStats, useProcesses } from "../../../hooks/useProcesses";
import { Archive, Filter, Play, Plus, Search, Workflow } from "lucide-react";
import { useState } from "react";

const statusColors: Record<ProcessStatus, string> = {
	active: "bg-green-100 text-green-700",
	archived: "bg-gray-200 text-gray-500",
	deprecated: "bg-yellow-100 text-yellow-700",
	draft: "bg-gray-100 text-gray-700",
	retired: "bg-orange-100 text-orange-700",
};

const statusLabels: Record<ProcessStatus, string> = {
	active: "Active",
	archived: "Archived",
	deprecated: "Deprecated",
	draft: "Draft",
	retired: "Retired",
};

const categoryLabels: Record<ProcessCategory, string> = {
	compliance: "Compliance",
	development: "Development",
	integration: "Integration",
	management: "Management",
	operational: "Operational",
	other: "Other",
	support: "Support",
};

interface ProcessViewProps {
	projectId: string;
}

export function ProcessView({ projectId }: ProcessViewProps) {
	const [showCreateModal, setShowCreateModal] = useState(false);
	const [statusFilter, setStatusFilter] = useState<ProcessStatus | "">("");
	const [categoryFilter, setCategoryFilter] = useState<ProcessCategory | "">(
		"",
	);
	const [searchQuery, setSearchQuery] = useState("");
	const [activeOnly, setActiveOnly] = useState(false);

	const filters = {
		projectId,
		...(statusFilter && { status: statusFilter }),
		...(categoryFilter && { category: categoryFilter }),
		activeOnly,
	};
	const { data, isLoading, error } = useProcesses(filters);

	const { data: stats } = useProcessStats(projectId);

	const processes = data?.processes || [];
	const filteredProcesses = processes.filter((p) =>
		p.name.toLowerCase().includes(searchQuery.toLowerCase()),
	);

	const handleCreateSuccess = () => {
		setShowCreateModal(false);
	};

	if (error) {
		return (
			<div className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
				Error loading processes: {error.message}
			</div>
		);
	}

	return (
		<div className="space-y-6">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h3 className="text-lg font-semibold">Process Management</h3>
					<p className="text-sm text-muted-foreground">
						Define and manage workflows and procedures
					</p>
				</div>
				<button
					onClick={() => setShowCreateModal(true)}
					className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90"
				>
					<Plus className="h-4 w-4" /> Create Process
				</button>
			</div>

			{/* Stats Cards */}
			{stats && (
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Workflow className="h-4 w-4 text-blue-500" />
							Total Processes
						</div>
						<div className="mt-2 text-2xl font-bold">{stats.total || 0}</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Play className="h-4 w-4 text-green-500" />
							Active
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.["active"] ?? 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Workflow className="h-4 w-4 text-gray-500" />
							Draft
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.["draft"] ?? 0}
						</div>
					</div>
					<div className="rounded-lg border bg-card p-4">
						<div className="flex items-center gap-2 text-sm text-muted-foreground">
							<Archive className="h-4 w-4 text-yellow-500" />
							Deprecated
						</div>
						<div className="mt-2 text-2xl font-bold">
							{stats.byStatus?.["deprecated"] ?? 0}
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
						placeholder="Search processes..."
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
							setStatusFilter(e.target.value as ProcessStatus | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Statuses</option>
						<option value="draft">Draft</option>
						<option value="active">Active</option>
						<option value="deprecated">Deprecated</option>
						<option value="retired">Retired</option>
						<option value="archived">Archived</option>
					</select>
					<select
						value={categoryFilter}
						onChange={(e) =>
							setCategoryFilter(e.target.value as ProcessCategory | "")
						}
						className="rounded-lg border bg-background px-3 py-2"
					>
						<option value="">All Categories</option>
						{Object.entries(categoryLabels).map(([value, label]) => (
							<option key={value} value={value}>
								{label}
							</option>
						))}
					</select>
					<label className="flex items-center gap-2 text-sm">
						<input
							type="checkbox"
							checked={activeOnly}
							onChange={(e) => setActiveOnly(e.target.checked)}
							className="rounded"
						/>
						Active only
					</label>
				</div>
			</div>

			{/* Processes Grid */}
			{isLoading ? (
				<div className="flex items-center justify-center py-12">
					<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				</div>
			) : (filteredProcesses.length === 0 ? (
				<div className="rounded-lg border border-dashed p-12 text-center">
					<Workflow className="mx-auto h-12 w-12 text-muted-foreground" />
					<h3 className="mt-4 text-lg font-semibold">No processes found</h3>
					<p className="mt-2 text-muted-foreground">
						{searchQuery || statusFilter || categoryFilter
							? "Try adjusting your filters"
							: "Create a new process to get started"}
					</p>
					{!searchQuery && !statusFilter && !categoryFilter && (
						<button
							onClick={() => setShowCreateModal(true)}
							className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
						>
							Create Process
						</button>
					)}
				</div>
			) : (
				<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
					{filteredProcesses.map((process) => (
						<ProcessCard key={process.id} process={process} />
					))}
				</div>
			))}

			{/* Create Modal */}
			{showCreateModal && (
				<CreateProcessForm
					projectId={projectId}
					onCancel={() => setShowCreateModal(false)}
					onSuccess={handleCreateSuccess}
				/>
			)}
		</div>
	);
}

function ProcessCard({ process }: { process: Process }) {
	const stageCount = process.stages?.length || 0;
	const swimlaneCount = process.swimlanes?.length || 0;

	return (
		<div className="rounded-lg border bg-card p-4 hover:shadow-md transition-shadow">
			<div className="flex items-start justify-between">
				<div className="flex-1">
					<span className="text-xs text-muted-foreground">
						{process.processNumber}
					</span>
					<h4 className="font-semibold">{process.name}</h4>
				</div>
				<span
					className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
						statusColors[process.status]
					}`}
				>
					{statusLabels[process.status]}
				</span>
			</div>

			{process.description && (
				<p className="mt-2 text-sm text-muted-foreground line-clamp-2">
					{process.description}
				</p>
			)}

			<div className="mt-4 flex items-center gap-4 text-sm text-muted-foreground">
				{process.category && (
					<span className="rounded bg-muted px-2 py-0.5 text-xs">
						{categoryLabels[process.category as ProcessCategory] ||
							process.category}
					</span>
				)}
				{stageCount > 0 && <span>{stageCount} stages</span>}
				{swimlaneCount > 0 && <span>{swimlaneCount} swimlanes</span>}
			</div>

			<div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
				<span>v{process.versionNumber}</span>
				{process.isActiveVersion && (
					<span className="rounded bg-green-100 px-2 py-0.5 text-green-700">
						Active Version
					</span>
				)}
				{process.owner && <span>Owner: {process.owner}</span>}
			</div>

			{process.expectedDurationHours && (
				<div className="mt-2 text-xs text-muted-foreground">
					Expected duration: {process.expectedDurationHours}h
					{process.slaHours && ` (SLA: ${process.slaHours}h)`}
				</div>
			)}
		</div>
	);
}

export default ProcessView;
