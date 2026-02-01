import type { WorkflowRun, WorkflowSchedule } from "@tracertm/types";
import { useState } from "react";
import {
	useBootstrapWorkflowSchedules,
	useDeleteWorkflowSchedule,
	useWorkflowRuns,
	useWorkflowSchedules,
} from "@/hooks/useWorkflows";

interface WorkflowRunsViewProps {
	projectId: string;
}

export function WorkflowRunsView({ projectId }: WorkflowRunsViewProps) {
	const [statusFilter, setStatusFilter] = useState<string>("");
	const { data: runsData, isLoading: runsLoading } = useWorkflowRuns(
		projectId,
		statusFilter || undefined,
	);
	const { data: schedulesData, isLoading: schedulesLoading } =
		useWorkflowSchedules(projectId);
	const bootstrapSchedules = useBootstrapWorkflowSchedules();
	const deleteSchedule = useDeleteWorkflowSchedule();

	const runs = runsData?.runs || [];
	const schedules = schedulesData?.schedules || [];

	return (
		<div className="p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-2xl font-bold text-gray-900 dark:text-white">
						Workflow Runs
					</h1>
					<p className="text-gray-600 dark:text-gray-400">
						History for Temporal workflows and schedules.
					</p>
				</div>
				<div className="flex items-center gap-3">
					<button
						type="button"
						onClick={() => bootstrapSchedules.mutate(projectId)}
						disabled={bootstrapSchedules.isPending}
						className="px-4 py-2 text-sm rounded-md bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60"
					>
						Bootstrap schedules
					</button>
				</div>
			</div>

			<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-lg font-semibold">Schedules</h2>
					{bootstrapSchedules.data && (
						<span className="text-xs text-green-600">
							Created {bootstrapSchedules.data.created?.length || 0}
						</span>
					)}
				</div>
				{schedulesLoading ? (
					<div className="animate-pulse text-sm text-gray-500">
						Loading schedules...
					</div>
				) : schedules.length === 0 ? (
					<div className="text-sm text-gray-500">
						No schedules configured for this project.
					</div>
				) : (
					<div className="space-y-2">
						{schedules.map((schedule: WorkflowSchedule) => (
							<ScheduleRow
								key={String(schedule.id || schedule.cronName)}
								schedule={schedule}
								projectId={projectId}
								onDelete={deleteSchedule.mutate}
								isDeleting={deleteSchedule.isPending}
							/>
						))}
					</div>
				)}
			</div>

			<div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4">
				<div className="flex items-center justify-between mb-4">
					<h2 className="text-lg font-semibold">Recent Runs</h2>
					<select
						className="border rounded-md px-3 py-1 text-sm bg-white dark:bg-gray-900"
						value={statusFilter}
						onChange={(e) => setStatusFilter(e.target.value)}
					>
						<option value="">All statuses</option>
						<option value="queued">Queued</option>
						<option value="running">Running</option>
						<option value="completed">Completed</option>
						<option value="failed">Failed</option>
					</select>
				</div>
				{runsLoading ? (
					<div className="animate-pulse text-sm text-gray-500">
						Loading runs...
					</div>
				) : runs.length === 0 ? (
					<div className="text-sm text-gray-500">No workflow runs yet.</div>
				) : (
					<div className="space-y-2">
						{runs.map((run: WorkflowRun) => (
							<RunRow key={run.id} run={run} />
						))}
					</div>
				)}
			</div>
		</div>
	);
}

function RunRow({ run }: { run: WorkflowRun }) {
	return (
		<div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded">
			<div>
				<div className="font-medium text-sm">{run.workflowName}</div>
				<div className="text-xs text-gray-500">
					{run.graphId ? `Graph ${run.graphId.slice(0, 8)}…` : "Project-level"}
					{run.externalRunId ? ` • ${run.externalRunId}` : ""}
				</div>
			</div>
			<div className="text-right">
				<span
					className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
						run.status === "completed"
							? "bg-green-100 text-green-700"
							: run.status === "failed"
								? "bg-red-100 text-red-700"
								: run.status === "running"
									? "bg-blue-100 text-blue-700"
									: "bg-gray-200 text-gray-600"
					}`}
				>
					{run.status}
				</span>
				<div className="text-xs text-gray-400 mt-1">
					{run.startedAt ? new Date(run.startedAt).toLocaleString() : "-"}
				</div>
			</div>
		</div>
	);
}

function ScheduleRow({
	schedule,
	projectId,
	onDelete,
	isDeleting,
}: {
	schedule: WorkflowSchedule;
	projectId: string;
	onDelete: (input: { projectId: string; cronId: string }) => void;
	isDeleting: boolean;
}) {
	const cronId = String(schedule.id || "");
	return (
		<div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded">
			<div>
				<div className="font-medium text-sm">
					{schedule.workflowName || "workflow"} • {schedule.cronName || "cron"}
				</div>
				<div className="text-xs text-gray-500">{schedule.expression || ""}</div>
			</div>
			<div>
				<button
					type="button"
					onClick={() => onDelete({ projectId, cronId })}
					disabled={!cronId || isDeleting}
					className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 disabled:opacity-60"
				>
					Delete
				</button>
			</div>
		</div>
	);
}
