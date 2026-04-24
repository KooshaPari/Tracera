// RequirementNode - Type-specific node for requirement items
// Shows EARS pattern, risk level, and quality metrics

import type { Node, NodeProps } from '@xyflow/react';

import { Handle, Position } from '@xyflow/react';
import { AlertCircle, CheckCircle2, FileText, ShieldCheck, TrendingUp } from 'lucide-react';
import { memo } from 'react';

import type { RequirementItem } from '@tracertm/types';

import { Badge } from '@tracertm/ui/components/Badge';
import { Card } from '@tracertm/ui/components/Card';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// Requirement-specific node data
export interface RequirementNodeData {
  id: string;
  item: RequirementItem;
  label: string;
  type: string;
  status: string;

  // Requirement-specific fields
  earsPatternType?: 'ubiquitous' | 'event_driven' | 'state_driven' | 'optional' | 'unwanted';
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
  wsjfScore?: number; // Weighted Shortest Job First score
  verifiabilityScore?: number; // 0-100, how testable is this
  verificationStatus?: 'not_verified' | 'partially_verified' | 'verified';

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

// EARS pattern colors
const EARS_COLORS = {
  event_driven: '#3b82f6',
  optional: '#f59e0b',
  state_driven: '#10b981',
  ubiquitous: '#8b5cf6',
  unwanted: '#ef4444',
};

// Risk level colors
const RISK_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  low: '#22c55e',
  medium: '#f59e0b',
};

// Verification status icons
const VERIFICATION_ICONS = {
  not_verified: AlertCircle,
  partially_verified: TrendingUp,
  verified: CheckCircle2,
};

const VERIFICATION_COLORS = {
  not_verified: '#94a3b8',
  partially_verified: '#f59e0b',
  verified: '#22c55e',
};

function RequirementNodeComponent({
  data,
  selected,
}: NodeProps<Node<RequirementNodeData, 'requirement'>>) {
  const earsColor = EARS_COLORS[data.earsPatternType ?? 'ubiquitous'];
  const riskColor = RISK_COLORS[data.riskLevel ?? 'low'];
  const VerificationIcon = VERIFICATION_ICONS[data.verificationStatus ?? 'not_verified'];
  const verificationColor = VERIFICATION_COLORS[data.verificationStatus ?? 'not_verified'];

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
        style={{ borderColor: '#9333ea' }}
      />

      {/* Main card */}
      <Card
        className={`relative w-[260px] cursor-pointer overflow-hidden transition-all duration-200 ${selected ? 'ring-offset-background ring-2 ring-white ring-offset-2' : ''} `}
        onClick={handleClick}
      >
        {/* Color accent bar */}
        <div className='absolute top-0 right-0 left-0 h-1' style={{ backgroundColor: '#9333ea' }} />

        {/* Content section */}
        <div className='p-3 pt-3.5'>
          {/* Header: Icon + Badges */}
          <div className='mb-2 flex items-start gap-2'>
            <div className='flex-shrink-0 rounded p-1.5' style={{ backgroundColor: '#9333ea20' }}>
              <FileText className='h-4 w-4 text-purple-600' />
            </div>

            <div className='min-w-0 flex-1 space-y-1'>
              <div className='flex flex-wrap items-center gap-1.5'>
                {/* EARS Pattern Badge */}
                {data.earsPatternType && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge
                        variant='outline'
                        className='h-5 px-1.5 text-[10px]'
                        style={{
                          backgroundColor: `${earsColor}15`,
                          borderColor: `${earsColor}40`,
                          color: earsColor,
                        }}
                      >
                        {data.earsPatternType.replaceAll('_', ' ')}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>EARS Pattern: {data.earsPatternType.replaceAll('_', ' ')}</p>
                    </TooltipContent>
                  </Tooltip>
                )}

                {/* Risk Badge */}
                {data.riskLevel && (
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <Badge
                        variant='outline'
                        className='ml-auto h-5 px-1.5 text-[10px]'
                        style={{
                          backgroundColor: `${riskColor}15`,
                          borderColor: `${riskColor}40`,
                          color: riskColor,
                        }}
                      >
                        <AlertCircle className='mr-0.5 h-3 w-3' />
                        {data.riskLevel}
                      </Badge>
                    </TooltipTrigger>
                    <TooltipContent>
                      <p>Risk Level: {data.riskLevel}</p>
                    </TooltipContent>
                  </Tooltip>
                )}
              </div>
            </div>
          </div>

          {/* Title */}
          <h4 className='mb-2 line-clamp-2 text-sm leading-tight font-semibold'>{data.label}</h4>

          {/* Quality Metrics */}
          <div className='mb-2 space-y-2'>
            {/* WSJF Score */}
            {data.wsjfScore !== undefined && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className='flex items-center justify-between text-xs'>
                    <span className='text-muted-foreground'>WSJF Score</span>
                    <span className='font-medium text-purple-600'>{data.wsjfScore.toFixed(1)}</span>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Weighted Shortest Job First: {data.wsjfScore.toFixed(2)}</p>
                </TooltipContent>
              </Tooltip>
            )}

            {/* Verifiability Gauge */}
            {data.verifiabilityScore !== undefined && (
              <Tooltip>
                <TooltipTrigger asChild>
                  <div className='space-y-1'>
                    <div className='flex items-center justify-between text-xs'>
                      <span className='text-muted-foreground flex items-center gap-1'>
                        <ShieldCheck className='h-3 w-3' />
                        Verifiable
                      </span>
                      <span className='font-medium'>{data.verifiabilityScore}%</span>
                    </div>
                    <div className='bg-muted h-1.5 w-full overflow-hidden rounded-full'>
                      <div
                        className='h-full bg-purple-500 transition-all'
                        style={{ width: `${data.verifiabilityScore}%` }}
                      />
                    </div>
                  </div>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Verifiability: {data.verifiabilityScore}%</p>
                </TooltipContent>
              </Tooltip>
            )}
          </div>

          {/* Verification Status */}
          {data.verificationStatus && (
            <div
              className='flex items-center gap-1.5 rounded px-2 py-1 text-xs font-medium'
              style={{
                backgroundColor: `${verificationColor}15`,
                color: verificationColor,
              }}
            >
              <VerificationIcon className='h-3.5 w-3.5' />
              <span>{data.verificationStatus.replaceAll('_', ' ')}</span>
            </div>
          )}

          {/* Footer: Status badge and connections */}
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
        style={{ borderColor: '#9333ea' }}
      />
    </TooltipProvider>
  );
}

export const RequirementNode = memo(RequirementNodeComponent);
