// TestNode - Type-specific node for test items
// Shows test-specific metrics and status

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Shield,
  TestTube2,
  XCircle,
} from 'lucide-react';
import { memo } from 'react';

import type { TestItem } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// Test-specific node data
export interface TestNodeData {
  id: string;
  item: TestItem;
  label: string;
  type: string;
  status: string;

  // Test-specific fields
  testType?: string; // Unit, integration, e2e, etc.
  framework?: string; // Jest, playwright, vitest, etc.
  flakinessScore?: number; // 0-100, higher = more flaky
  coveragePercent?: number; // 0-100
  safetyLevel?: 'safe' | 'quarantined' | 'disabled';
  lastRunStatus?: 'passed' | 'failed' | 'skipped' | 'error';

  // Connection counts
  connections: {
    incoming: number;
    outgoing: number;
    total: number;
  };

  // Callbacks
  onSelect?: ((id: string) => void) | undefined;

  // Index signature for React Flow compatibility
  [key: string]: unknown;
}

// Safety level colors
const SAFETY_COLORS = {
  disabled: '#ef4444',
  quarantined: '#f59e0b',
  safe: '#22c55e',
};

// Status colors
const STATUS_COLORS = {
  error: '#dc2626',
  failed: '#ef4444',
  passed: '#22c55e',
  skipped: '#94a3b8',
};

function TestNodeComponent({ data, selected }: NodeProps<Node<TestNodeData, 'test'>>) {
  const safetyColor = SAFETY_COLORS[data.safetyLevel ?? 'safe'];
  const statusColor = STATUS_COLORS[data.lastRunStatus ?? 'passed'];
  const isQuarantined = data.safetyLevel === 'quarantined';
  const isFlaky = (data.flakinessScore ?? 0) > 50;

  const handleClick = () => {
    data.onSelect?.(data.id);
  };

  return (
    <TooltipProvider>
      {/* Input handle */}
      <Handle
        type='target'
        position={Position.Left}
        className='!bg-background !h-3 !w-3 !border-2'
        style={{ borderColor: '#22c55e' }}
      />

      {/* Main card */}
      <Card
        className={`relative w-[260px] cursor-pointer overflow-hidden transition-all duration-200 ${selected ? 'ring-offset-background ring-2 ring-white ring-offset-2' : ''} ${isQuarantined ? 'border-yellow-500/50' : ''} `}
        onClick={handleClick}
      >
        {/* Color accent bar */}
        <div className='absolute top-0 right-0 left-0 h-1' style={{ backgroundColor: '#22c55e' }} />

        {/* Quarantine warning banner */}
        {isQuarantined && (
          <div className='flex items-center gap-1.5 border-b border-yellow-500/20 bg-yellow-500/10 px-3 py-1.5'>
            <AlertTriangle className='h-3.5 w-3.5 text-yellow-600' />
            <span className='text-xs font-medium text-yellow-700'>Quarantined</span>
          </div>
        )}

        {/* Content section */}
        <div className='p-3 pt-3.5'>
          {/* Header: Icon + Type badges */}
          <div className='mb-2 flex items-start gap-2'>
            <div className='flex-shrink-0 rounded p-1.5' style={{ backgroundColor: '#22c55e20' }}>
              <TestTube2 className='h-4 w-4 text-green-600' />
            </div>

            <div className='min-w-0 flex-1 space-y-1'>
              <div className='flex flex-wrap items-center gap-1.5'>
                {/* Test Type */}
                {data.testType && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge
                        variant='outline'
                        className='h-5 px-1.5 text-[10px]'
                        style={{
                          backgroundColor: '#22c55e15',
                          borderColor: '#22c55e40',
                          color: '#16a34a',
                        }}
                      >
                        {data.testType}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Test Type: {data.testType}</p>
                    </TooltipContent>
                  </Tooltip>
                )}

                {/* Framework */}
                {data.framework && (
                  <Badge variant='secondary' className='h-5 px-1.5 text-[10px]'>
                    {data.framework}
                  </Badge>
                )}

                {/* Safety Level */}
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Badge
                      variant='outline'
                      className='ml-auto h-5 px-1 text-[10px]'
                      style={{
                        backgroundColor: `${safetyColor}15`,
                        borderColor: `${safetyColor}40`,
                        color: safetyColor,
                      }}
                    >
                      <Shield className='mr-0.5 h-3 w-3' />
                      {data.safetyLevel ?? 'safe'}
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Safety: {data.safetyLevel ?? 'safe'}</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
          </div>

          {/* Title */}
          <h4 className='mb-2 line-clamp-2 text-sm leading-tight font-semibold'>{data.label}</h4>

          {/* Metrics Grid */}
          <div className='mb-2 grid grid-cols-2 gap-2'>
            {/* Flakiness Score */}
            {data.flakinessScore !== undefined && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className='flex items-center gap-1.5 text-xs'>
                    <Activity
                      className={`h-3.5 w-3.5 ${isFlaky ? 'text-yellow-600' : 'text-gray-500'}`}
                    />
                    <span
                      className={`font-medium ${isFlaky ? 'text-yellow-700' : 'text-muted-foreground'}`}
                    >
                      {data.flakinessScore}%
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>
                    Flakiness Score: {data.flakinessScore}%{isFlaky && ' (High)'}
                  </p>
                </TooltipContent>
              </Tooltip>
            )}

            {/* Coverage */}
            {data.coveragePercent !== undefined && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className='flex items-center gap-1.5 text-xs'>
                    <div className='flex h-3.5 w-3.5 items-center justify-center rounded-full bg-blue-500/20'>
                      <div className='h-2 w-2 rounded-full bg-blue-500' />
                    </div>
                    <span className='text-muted-foreground font-medium'>
                      {data.coveragePercent}%
                    </span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Coverage: {data.coveragePercent}%</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>

          {/* Last Run Status */}
          {data.lastRunStatus && (
            <div
              className='flex items-center gap-1.5 rounded px-2 py-1 text-xs font-medium'
              style={{
                backgroundColor: `${statusColor}15`,
                color: statusColor,
              }}
            >
              {data.lastRunStatus === 'passed' && <CheckCircle2 className='h-3.5 w-3.5' />}
              {data.lastRunStatus === 'failed' && <XCircle className='h-3.5 w-3.5' />}
              {data.lastRunStatus === 'skipped' && <Clock className='h-3.5 w-3.5' />}
              {data.lastRunStatus === 'error' && <AlertTriangle className='h-3.5 w-3.5' />}
              <span>Last run: {data.lastRunStatus}</span>
            </div>
          )}

          {/* Footer: Status badge */}
          <div className='text-muted-foreground mt-2 flex items-center justify-between border-t pt-2 text-[10px]'>
            <Badge variant='secondary' className='h-4 px-1.5 text-[10px]'>
              {data.status}
            </Badge>
            <span className='flex items-center gap-0.5'>{data.connections.total} links</span>
          </div>
        </div>
      </Card>

      {/* Output handle */}
      <Handle
        type='source'
        position={Position.Right}
        className='!bg-background !h-3 !w-3 !border-2'
        style={{ borderColor: '#22c55e' }}
      />
    </TooltipProvider>
  );
}

export const TestNode = memo(TestNodeComponent);
