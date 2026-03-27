import { ArrowRight, BookOpen, CheckCircle2, ListTodo, XCircle } from 'lucide-react';

import type { Feature, FeatureStatus } from '@tracertm/types';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
  Progress,
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui';

interface FeatureCardProps {
  feature: Feature;
  onClick?: () => void;
  className?: string;
}

const statusColors: Record<FeatureStatus, string> = {
  active: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  archived: 'bg-muted text-muted-foreground border-border',
  deprecated: 'bg-orange-500/10 text-orange-500 border-orange-500/20',
  draft: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
};

export function FeatureCard({ feature, onClick, className }: FeatureCardProps) {
  const total = feature.scenarioCount || 0;
  const passed = feature.passedScenarios || 0;
  const failed = feature.failedScenarios || 0;
  const pending = feature.pendingScenarios || 0;

  const passRate = total > 0 ? (passed / total) * 100 : 0;

  return (
    <TooltipProvider delayDuration={400}>
      <Tooltip>
        <TooltipTrigger asChild>
    <Card
      className={`hover:bg-muted/30 hover:border-primary/30 cursor-pointer transition-all duration-200 hover:shadow-md ${className}`}
      onClick={onClick}
    >
      <CardHeader className='pb-2'>
        <div className='flex items-start justify-between'>
          <div className='flex items-center gap-2'>
            <Badge variant='outline' className='font-mono text-xs'>
              {feature.featureNumber}
            </Badge>
            <Badge className={statusColors[feature.status]}>{feature.status}</Badge>
          </div>
        </div>
        <CardTitle className='mt-2 flex items-center gap-2 text-lg'>
          <BookOpen className='text-muted-foreground h-4 w-4' />
          {feature.name}
        </CardTitle>
      </CardHeader>
      <CardContent className='pb-4'>
        <div className='space-y-4'>
          {feature.asA && (
            <div className='text-muted-foreground bg-muted/30 border-border/50 rounded border p-2 text-sm italic'>
              "As a <span className='text-foreground font-medium'>{feature.asA}</span>, I want{' '}
              <span className='text-foreground font-medium'>{feature.iWant}</span>, so that{' '}
              <span className='text-foreground font-medium'>{feature.soThat}</span>"
            </div>
          )}

          <div className='space-y-1.5'>
            <div className='flex justify-between text-xs'>
              <span className='font-medium'>Scenario Status</span>
              <span className='text-muted-foreground'>
                {passed}/{total} Passing
              </span>
            </div>
            <Progress value={passRate} className='h-2' />
            <div className='text-muted-foreground flex gap-3 pt-1 text-[10px]'>
              {passed > 0 && (
                <span className='flex items-center gap-1 text-green-600'>
                  <CheckCircle2 className='h-3 w-3' /> {passed} Pass
                </span>
              )}
              {failed > 0 && (
                <span className='flex items-center gap-1 text-red-600'>
                  <XCircle className='h-3 w-3' /> {failed} Fail
                </span>
              )}
              {pending > 0 && (
                <span className='flex items-center gap-1'>
                  <ListTodo className='h-3 w-3' /> {pending} Pending
                </span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className='text-muted-foreground flex items-center justify-between pt-0 text-xs'>
        <div className='flex items-center gap-1'>
          {feature.tags && feature.tags.length > 0 && (
            <div className='flex gap-1'>
              {feature.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant='secondary' className='h-5 px-1 text-[10px]'>
                  {tag}
                </Badge>
              ))}
              {feature.tags.length > 2 && (
                <Badge variant='secondary' className='h-5 px-1 text-[10px]'>
                  +{feature.tags.length - 2}
                </Badge>
              )}
            </div>
          )}
        </div>
        <Button variant='ghost' size='sm' className='hover:bg-muted/50 h-8 gap-1 transition-colors'>
          View Feature <ArrowRight className='h-3 w-3' />
        </Button>
      </CardFooter>
    </Card>
        </TooltipTrigger>
        <TooltipContent
          side='top'
          className='max-w-xs space-y-2 p-3 text-left'
          sideOffset={8}
        >
          <p className='text-xs font-bold'>{feature.name}</p>
          {feature.asA && (
            <p className='text-muted-foreground text-[11px] italic'>
              As a {feature.asA}, I want {feature.iWant}
            </p>
          )}
          <div className='flex gap-3 text-[10px]'>
            <span className='flex items-center gap-1 text-green-600'>
              <CheckCircle2 className='h-3 w-3' /> {passed} pass
            </span>
            {failed > 0 && (
              <span className='flex items-center gap-1 text-red-500'>
                <XCircle className='h-3 w-3' /> {failed} fail
              </span>
            )}
            {pending > 0 && (
              <span className='flex items-center gap-1'>
                <ListTodo className='h-3 w-3' /> {pending} pending
              </span>
            )}
          </div>
          {feature.tags && feature.tags.length > 0 && (
            <div className='flex flex-wrap gap-1'>
              {feature.tags.map((tag) => (
                <span key={tag} className='bg-muted rounded px-1.5 py-0.5 text-[10px] font-medium'>
                  {tag}
                </span>
              ))}
            </div>
          )}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
