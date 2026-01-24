import { Badge } from "@tracertm/ui/components/Badge";
import { Button } from "@tracertm/ui/components/Button";
import { Card } from "@tracertm/ui/components/Card";

export function AgentsView() {
	// Mock agent data - replace with actual API call
	const agents = [
		{
			id: "1",
			name: "Sync Agent",
			status: "active",
			lastRun: new Date(),
			tasks: 24,
		},
		{
			id: "2",
			name: "Validation Agent",
			status: "idle",
			lastRun: new Date(),
			tasks: 12,
		},
		{
			id: "3",
			name: "Coverage Agent",
			status: "running",
			lastRun: new Date(),
			tasks: 8,
		},
	];

	return (
		<div className="space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold">Agents</h1>
					<p className="text-gray-600">Monitor and manage automation agents</p>
				</div>
				<Button>+ New Agent</Button>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
				{agents.map((agent) => (
					<Card key={agent.id} className="p-6">
						<div className="flex items-start justify-between mb-4">
							<div>
								<h3 className="font-semibold text-lg">{agent.name}</h3>
								<p className="text-sm text-gray-500">
									{agent.tasks} tasks completed
								</p>
							</div>
							<Badge
								variant={
									agent.status === "active"
										? "success"
										: agent.status === "running"
											? "info"
											: "secondary"
								}
							>
								{agent.status}
							</Badge>
						</div>
						<div className="text-sm text-gray-600">
							Last run: {agent.lastRun.toLocaleString()}
						</div>
						<div className="mt-4 flex gap-2">
							<Button size="sm" variant="outline">
								View Logs
							</Button>
							<Button size="sm" variant="outline">
								Configure
							</Button>
						</div>
					</Card>
				))}
			</div>
		</div>
	);
}
