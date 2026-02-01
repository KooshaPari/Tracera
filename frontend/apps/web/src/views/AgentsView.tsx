import { useEffect, useState } from "react";
import { Button, Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";

type AgentStatus = "active" | "idle" | "running" | "offline";

interface AgentSummary {
	id: string;
	name: string;
	status: AgentStatus;
	tasksCompleted?: number;
	lastRun?: string;
	capabilities?: string[];
}

const fallbackAgents: AgentSummary[] = [
	{
		id: "agent-1",
		name: "Sync Agent",
		status: "active",
		tasksCompleted: 24,
		lastRun: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
		capabilities: ["sync", "dependency-check"],
	},
	{
		id: "agent-2",
		name: "Validation Agent",
		status: "idle",
		tasksCompleted: 12,
		lastRun: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
		capabilities: ["validation", "quality-checks"],
	},
	{
		id: "agent-3",
		name: "Coverage Agent",
		status: "running",
		tasksCompleted: 7,
		lastRun: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
		capabilities: ["coverage-report", "test-execution"],
	},
];

const statusVariant = (status: AgentStatus) => {
	switch (status) {
		case "active":
			return "default";
		case "running":
			return "secondary";
		case "idle":
			return "outline";
		default:
			return "outline";
	}
};

const formatLastRun = (iso?: string) => {
	if (!iso) return "Last run: —";
	const date = new Date(iso);
	if (Number.isNaN(date.getTime())) return "Last run: —";
	return `Last run: ${date.toLocaleString()}`;
};

export function AgentsView() {
	const [agents, setAgents] = useState<AgentSummary[]>(fallbackAgents);

	useEffect(() => {
		let active = true;
		const load = async () => {
			try {
				const response = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:4000"}/api/v1/agents`);
				if (!response.ok) return;
				const data = await response.json();
				const list = Array.isArray(data) ? data : data?.agents;
				if (active && Array.isArray(list) && list.length > 0) {
					setAgents(
						list.map((agent: any) => ({
							id: String(agent.id ?? agent.agent_id ?? agent.name),
							name: String(agent.name ?? "Agent"),
							status: (agent.status ?? "idle") as AgentStatus,
							tasksCompleted: agent.tasksCompleted ?? agent.tasks_completed ?? 0,
							lastRun: agent.lastRun ?? agent.last_run ?? agent.lastHeartbeat,
							capabilities: agent.capabilities ?? [],
						})),
					);
				}
			} catch {
				// Fall back to static data
			}
		};

		load();
		return () => {
			active = false;
		};
	}, []);

	return (
		<div className="space-y-6">
			<div>
				<h1 className="text-2xl font-bold tracking-tight">Agents</h1>
				<p className="text-sm text-muted-foreground">
					Manage automation agents, status, and workflows.
				</p>
			</div>

			<div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
				{agents.map((agent) => (
					<Card key={agent.id} className="border border-border/60">
						<CardHeader className="space-y-2">
							<div className="flex items-center justify-between gap-3">
								<CardTitle className="text-base">{agent.name}</CardTitle>
								<Badge variant={statusVariant(agent.status)}>
									{agent.status}
								</Badge>
							</div>
							<p className="text-xs text-muted-foreground">
								{agent.tasksCompleted ?? 0} tasks completed
							</p>
							<p className="text-xs text-muted-foreground">
								{formatLastRun(agent.lastRun)}
							</p>
						</CardHeader>
						<CardContent className="space-y-3">
							{agent.capabilities?.length ? (
								<p className="text-xs text-muted-foreground">
									Capabilities: {agent.capabilities.join(", ")}
								</p>
							) : null}
							<div className="flex flex-wrap gap-2">
								<Button size="sm" variant="secondary">
									View Logs
								</Button>
								<Button size="sm" variant="outline">
									Configure
								</Button>
							</div>
						</CardContent>
					</Card>
				))}
			</div>
		</div>
	);
}
