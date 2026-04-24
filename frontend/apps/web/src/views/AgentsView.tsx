import type { ReactElement } from 'react';

import React from 'react';

import { Button, Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';

const MINUTE_IN_MS = Number('60000');
const HOUR_IN_MS = Number('60') * MINUTE_IN_MS;
const TASKS_DEFAULT = Number('0');

type AgentStatus = 'active' | 'idle' | 'running' | 'offline';

interface AgentSummary {
  capabilities?: string[];
  id: string;
  lastRun?: string;
  name: string;
  status: AgentStatus;
  tasksCompleted?: number;
}

const fallbackAgents: AgentSummary[] = [
  {
    capabilities: ['sync', 'dependency-check'],
    id: 'agent-1',
    lastRun: new Date(Date.now() - HOUR_IN_MS).toISOString(),
    name: 'Sync Agent',
    status: 'active',
    tasksCompleted: 24,
  },
  {
    capabilities: ['validation', 'quality-checks'],
    id: 'agent-2',
    lastRun: new Date(Date.now() - 2 * HOUR_IN_MS).toISOString(),
    name: 'Validation Agent',
    status: 'idle',
    tasksCompleted: 12,
  },
  {
    capabilities: ['coverage-report', 'test-execution'],
    id: 'agent-3',
    lastRun: new Date(Date.now() - 15 * MINUTE_IN_MS).toISOString(),
    name: 'Coverage Agent',
    status: 'running',
    tasksCompleted: 7,
  },
];

const statusVariant = (status: AgentStatus): 'default' | 'outline' | 'secondary' => {
  switch (status) {
    case 'active': {
      return 'default';
    }
    case 'running': {
      return 'secondary';
    }
    case 'idle': {
      return 'outline';
    }
    default: {
      return 'outline';
    }
  }
};

const formatLastRun = (iso?: string): string => {
  if (!iso) {
    return 'Last run: —';
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return 'Last run: —';
  }
  return `Last run: ${date.toLocaleString()}`;
};

const AgentCard = ({ agent }: { agent: AgentSummary }): ReactElement => (
  <Card className='border-border/60 border'>
    <CardHeader className='space-y-2'>
      <div className='flex items-center justify-between gap-3'>
        <CardTitle className='text-base'>{agent.name}</CardTitle>
        <Badge variant={statusVariant(agent.status)}>{agent.status}</Badge>
      </div>
      <p className='text-muted-foreground text-xs'>
        {agent.tasksCompleted ?? TASKS_DEFAULT} tasks completed
      </p>
      <p className='text-muted-foreground text-xs'>{formatLastRun(agent.lastRun)}</p>
    </CardHeader>
    <CardContent className='space-y-3'>
      {agent.capabilities?.length ? (
        <p className='text-muted-foreground text-xs'>
          Capabilities: {agent.capabilities.join(', ')}
        </p>
      ) : null}
      <div className='flex flex-wrap gap-2'>
        <Button size='sm' variant='secondary'>
          View Logs
        </Button>
        <Button size='sm' variant='outline'>
          Configure
        </Button>
      </div>
    </CardContent>
  </Card>
);

export const AgentsView = (): ReactElement => {
  const agents = fallbackAgents;

  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold tracking-tight'>Agents</h1>
        <p className='text-muted-foreground text-sm'>
          Manage automation agents, status, and workflows.
        </p>
      </div>

      <div className='grid gap-4 md:grid-cols-2 xl:grid-cols-3'>
        {agents.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>
    </div>
  );
};
