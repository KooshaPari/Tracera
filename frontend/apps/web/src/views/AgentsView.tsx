import type { ReactElement } from "react";

import React from "react";

import { Button, Card, CardContent, CardHeader, CardTitle } from "@tracertm/ui";
import { Badge } from "@tracertm/ui/components/Badge";

type AgentStatus = "active" | "idle" | "running" | "offline";

interface AgentSummary {
  capabilities?: string[];
  id: string;
  lastRun?: string;
  name: string;
  status: AgentStatus;
  tasksCompleted?: number;
}

const statusVariant = (status: AgentStatus): "default" | "outline" | "secondary" => {
  switch (status) {
    case "active": {
      return "default";
    }
    case "running": {
      return "secondary";
    }
    case "idle": {
      return "outline";
    }
    default: {
      return "outline";
    }
  }
};

const formatLastRun = (iso?: string): string => {
  if (!iso) {
    return "Last run: —";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return "Last run: —";
  }
  return `Last run: ${date.toLocaleString()}`;
};

const AgentCard = ({ agent }: { agent: AgentSummary }): ReactElement => (
  <Card className="border-border/60 border">
    <CardHeader className="space-y-2">
      <div className="flex items-center justify-between gap-3">
        <CardTitle className="text-base">{agent.name}</CardTitle>
        <Badge variant={statusVariant(agent.status)}>{agent.status}</Badge>
      </div>
      {agent.tasksCompleted === undefined ? null : (
        <p className="text-muted-foreground text-xs">{agent.tasksCompleted} tasks completed</p>
      )}
      {agent.lastRun ? <p className="text-muted-foreground text-xs">{formatLastRun(agent.lastRun)}</p> : null}
    </CardHeader>
    <CardContent className="space-y-3">
      {agent.capabilities?.length ? (
        <p className="text-muted-foreground text-xs">
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
);

export const AgentsView = (): ReactElement => {
  const [agents, setAgents] = React.useState<AgentSummary[]>([]);
  const [note, setNote] = React.useState<string>("Loading live agents...");
  React.useEffect(() => {
    let alive = true;
    const load = async (): Promise<void> => {
      try {
        const res = await fetch("/api/v1/agents", { credentials: "same-origin" });
        const data = (await res.json()) as { agents?: AgentSummary[]; as_of?: string; source?: string };
        if (!alive) {
          return;
        }
        setAgents(Array.isArray(data.agents) ? data.agents : []);
        setNote(res.ok ? `Live from ${data.source ?? "local daemon"} at ${data.as_of ?? ""}` : "Local agent daemon unavailable");
      } catch {
        if (alive) {
          setNote("Local agent daemon unavailable");
        }
      }
    };
    void load();
    const timer = globalThis.setInterval(() => void load(), Number("15000"));
    return () => {
      alive = false;
      globalThis.clearInterval(timer);
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
        <p className="text-muted-foreground text-sm">
          Live agents from your local herdr sessions. {note}
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};
