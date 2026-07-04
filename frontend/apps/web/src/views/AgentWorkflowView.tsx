import type { LucideIcon } from 'lucide-react';

import { Bot, FileText, GitMerge, Zap } from 'lucide-react';

import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from '@tracertm/ui';

interface WorkflowCardProps {
  description: string;
  icon: LucideIcon;
  title: string;
}

const WorkflowCard = ({ icon: Icon, title, description }: WorkflowCardProps) => (
  <Card className='hover:border-primary/50 bg-card/50 cursor-pointer border-none transition-colors'>
    <CardHeader className='pb-3'>
      <CardTitle className='flex items-center gap-2 text-sm'>
        <Icon className='text-primary h-4 w-4' />
        {title}
      </CardTitle>
      <CardDescription className='text-xs'>{description}</CardDescription>
    </CardHeader>
    <CardContent className='pt-0'>
      <Button size='sm' className='w-full text-xs'>
        Start Agent
      </Button>
    </CardContent>
  </Card>
);

export const AgentWorkflowView = () => (
  <div className='space-y-4'>
    <div className='grid grid-cols-1 gap-4 md:grid-cols-2'>
      <WorkflowCard
        icon={GitMerge}
        title='Task Decomposition'
        description='Break down Epics into User Stories automatically.'
      />
      <WorkflowCard
        icon={FileText}
        title='Scenario Generation'
        description='Generate BDD scenarios from requirements using RAG.'
      />
      <WorkflowCard
        icon={Bot}
        title='Impact Analysis'
        description='Analyze blast radius of proposed changes.'
      />
      <WorkflowCard
        icon={Zap}
        title='Auto-Link Recovery'
        description='Recover missing traceability links from code.'
      />
    </div>
  </div>
);
