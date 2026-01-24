import { ChevronDown, ChevronRight, Plus } from "lucide-react";
import { useState } from "react";

const items = [
	{
		id: "1",
		type: "epic",
		title: "Foundation & Monorepo Setup",
		status: "in_progress",
		children: [
			{
				id: "1.1",
				type: "feature",
				title: "Bun Workspace Setup",
				status: "done",
			},
			{
				id: "1.2",
				type: "feature",
				title: "Turborepo Configuration",
				status: "in_progress",
			},
			{
				id: "1.3",
				type: "feature",
				title: "Shared Packages Structure",
				status: "todo",
			},
		],
	},
	{
		id: "2",
		type: "epic",
		title: "Web Application",
		status: "todo",
		children: [
			{
				id: "2.1",
				type: "feature",
				title: "Vite + React 19 Setup",
				status: "todo",
			},
			{
				id: "2.2",
				type: "feature",
				title: "Legend State Integration",
				status: "todo",
			},
		],
	},
	{
		id: "3",
		type: "epic",
		title: "Desktop Application",
		status: "todo",
		children: [],
	},
];

const statusColors: Record<string, string> = {
	todo: "bg-gray-100 text-gray-600",
	in_progress: "bg-blue-100 text-blue-600",
	done: "bg-green-100 text-green-600",
};

export function FeatureView() {
	const [expanded, setExpanded] = useState<Set<string>>(new Set(["1", "2"]));

	const toggle = (id: string) => {
		const next = new Set(expanded);
		if (next.has(id)) {
			next.delete(id);
		} else {
			next.add(id);
		}
		setExpanded(next);
	};

	return (
		<div className="space-y-4">
			<div className="flex items-center justify-between">
				<h3 className="text-lg font-semibold">Feature View</h3>
				<button className="flex items-center gap-2 rounded-lg bg-primary px-3 py-1.5 text-sm text-primary-foreground">
					<Plus className="h-4 w-4" /> Add Epic
				</button>
			</div>

			<div className="rounded-lg border">
				{items.map((epic) => (
					<div key={epic.id} className="border-b last:border-b-0">
						<div
							className="flex cursor-pointer items-center gap-3 p-4 hover:bg-accent/50"
							onClick={() => toggle(epic.id)}
						>
							{epic.children.length > 0 ? (
								expanded.has(epic.id) ? (
									<ChevronDown className="h-4 w-4" />
								) : (
									<ChevronRight className="h-4 w-4" />
								)
							) : (
								<div className="w-4" />
							)}
							<span className="rounded bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-600">
								epic
							</span>
							<span className="flex-1 font-medium">{epic.title}</span>
							<span
								className={`rounded-full px-2 py-0.5 text-xs ${statusColors[epic.status]}`}
							>
								{epic.status}
							</span>
						</div>
						{expanded.has(epic.id) &&
							epic.children.map((child) => (
								<div
									key={child.id}
									className="flex items-center gap-3 border-t bg-muted/30 p-4 pl-12"
								>
									<span className="rounded bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-600">
										feature
									</span>
									<span className="flex-1">{child.title}</span>
									<span
										className={`rounded-full px-2 py-0.5 text-xs ${statusColors[child.status]}`}
									>
										{child.status}
									</span>
								</div>
							))}
					</div>
				))}
			</div>
		</div>
	);
}
