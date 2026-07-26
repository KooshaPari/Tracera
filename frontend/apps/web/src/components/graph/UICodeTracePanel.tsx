// UICodeTracePanel.tsx - Visualize the traceability chain from UI to code to requirements

import {
  ArrowDown,
  ArrowRight,
  Badge as BadgeIcon,
  CheckCircle2,
  Code2,
  ExternalLink,
  FileText,
  Sparkles,
  Zap,
} from 'lucide-react';
import { memo, useState } from 'react';

import type {
  CanonicalConcept,
  CanonicalProjection,
  CodeReference,
  EquivalenceStrategy,
} from '@tracertm/types';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui/components/Card';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// =============================================================================
// TYPES
// =============================================================================

/**
 * Represents a single level in the traceability chain
 */
export interface TraceLevel {
  id: string;
  type: 'ui' | 'code' | 'requirement' | 'concept';
  title: string;
  description?: string | undefined;
  perspective?: string | undefined;

  // UI Level specific
  componentName?: string | undefined;
  componentPath?: string | undefined;
  screenshot?: string | undefined;

  // Code Level specific
  codeRef?: CodeReference | undefined;

  // Requirement Level specific
  requirementId?: string | undefined;
  businessValue?: string | undefined;

  // Canonical concept
  canonicalId?: string | undefined;

  // Confidence and strategy
  confidence: number;
  strategy?: EquivalenceStrategy | undefined;
  isConfirmed?: boolean | undefined;
}

/**
 * Complete trace chain from UI through code to requirements
 */
export interface UICodeTraceChain {
  id: string;
  name: string;
  description?: string | undefined;
  levels: TraceLevel[];
  overallConfidence: number;
  canonicalConcept?: CanonicalConcept | undefined;
  projections?: CanonicalProjection[] | undefined;
  lastUpdated: string;
}

export interface UICodeTracePanelProps {
  traceChain: UICodeTraceChain | null;
  isLoading?: boolean | undefined;
  onOpenCode?: ((codeRef: CodeReference) => void) | undefined;
  onOpenRequirement?: ((requirementId: string) => void) | undefined;
  onNavigateToUI?: ((componentPath: string) => void) | undefined;
  onRefreshTrace?: (() => void) | undefined;
}

// =============================================================================
// STRATEGY LABELS AND COLORS
// =============================================================================

const STRATEGY_LABELS: Record<EquivalenceStrategy, string> = {
  api_contract: 'API Contract',
  co_occurrence: 'Co-occurrence',
  explicit_annotation: 'Explicit',
  manual_link: 'Manual',
  naming_pattern: 'Naming Match',
  semantic_similarity: 'Semantic',
  shared_canonical: 'Shared Concept',
  structural: 'Structural',
  temporal: 'Temporal',
};

const CONFIDENCE_COLOR = (confidence: number): string => {
  if (confidence >= 0.9) {
    return 'bg-green-100 text-green-900 border-green-300';
  }
  if (confidence >= 0.7) {
    return 'bg-blue-100 text-blue-900 border-blue-300';
  }
  if (confidence >= 0.5) {
    return 'bg-yellow-100 text-yellow-900 border-yellow-300';
  }
  return 'bg-orange-100 text-orange-900 border-orange-300';
};

const CONFIDENCE_ICON = (confidence: number) => {
  if (confidence >= 0.9) {
    return <CheckCircle2 className='h-4 w-4' />;
  }
  if (confidence >= 0.7) {
    return <Zap className='h-4 w-4' />;
  }
  return <Sparkles className='h-4 w-4' />;
};

// =============================================================================
// SUBCOMPONENTS
// =============================================================================

/**
 * Display a single trace level with rich information
 */
const TraceLevelComponent = memo(function TraceLevel({
  level,
  index,
  totalLevels,
  onOpenCode,
  onOpenRequirement,
  onNavigateToUI,
}: {
  level: TraceLevel;
  index: number;
  totalLevels: number;
  onOpenCode?: ((codeRef: CodeReference) => void) | undefined;
  onOpenRequirement?: ((requirementId: string) => void) | undefined;
  onNavigateToUI?: ((componentPath: string) => void) | undefined;
}) {
  const confidencePercent = Math.round(level.confidence * 100);
  const isLast = index === totalLevels - 1;

  return (
    <div className='relative'>
      {/* Level Card */}
      <Card className='border border-slate-200 bg-white transition-colors hover:border-slate-300'>
        <CardContent className='p-4'>
          {/* Type Badge and Confidence */}
          <div className='mb-3 flex items-center justify-between'>
            <div className='flex items-center gap-2'>
              {level.type === 'ui' && <BadgeIcon className='h-4 w-4 text-pink-600' />}
              {level.type === 'code' && <Code2 className='h-4 w-4 text-green-600' />}
              {level.type === 'requirement' && <FileText className='h-4 w-4 text-blue-600' />}
              {level.type === 'concept' && <Sparkles className='h-4 w-4 text-purple-600' />}

              <span className='text-xs font-semibold tracking-wider text-slate-600 uppercase'>
                {level.type}
              </span>
            </div>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger>
                  <Badge
                    variant='outline'
                    className={`flex items-center gap-1 ${CONFIDENCE_COLOR(level.confidence)}`}
                  >
                    {CONFIDENCE_ICON(level.confidence)}
                    {confidencePercent}%
                  </Badge>
                </TooltipTrigger>
                <TooltipContent side='left'>
                  <div className='text-xs'>
                    <p className='mb-1 font-semibold'>
                      {STRATEGY_LABELS[level.strategy ?? 'manual_link']}
                    </p>
                    <p className='text-xs'>{level.description}</p>
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          {/* Title */}
          <h4 className='mb-2 text-sm font-semibold text-slate-900'>{level.title}</h4>

          {/* Perspective Badge */}
          {level.perspective && (
            <div className='mb-3 flex items-center gap-2'>
              <Badge variant='secondary' className='text-xs'>
                {level.perspective}
              </Badge>
            </div>
          )}

          {/* UI Level Details */}
          {level.type === 'ui' && (
            <div className='space-y-2 rounded border border-slate-100 bg-slate-50 p-3'>
              {level.componentName && (
                <div className='text-xs'>
                  <span className='text-slate-600'>Component:</span>
                  <span className='ml-2 font-mono text-slate-900'>{level.componentName}</span>
                </div>
              )}
              {level.componentPath && (
                <div className='text-xs'>
                  <span className='text-slate-600'>Path:</span>
                  <span className='ml-2 truncate font-mono text-slate-700'>
                    {level.componentPath}
                  </span>
                </div>
              )}
              {level.screenshot && (
                <div className='mt-2'>
                  <img
                    src={level.screenshot}
                    alt={level.title}
                    className='h-32 w-full rounded border border-slate-200 object-cover'
                  />
                </div>
              )}
              {level.componentPath && onNavigateToUI && (
                <Button
                  size='sm'
                  variant='outline'
                  className='mt-2 w-full'
                  onClick={() => {
                    onNavigateToUI(level.componentPath!);
                  }}
                >
                  <ExternalLink className='mr-1 h-3 w-3' />
                  Open Component
                </Button>
              )}
            </div>
          )}

          {/* Code Level Details */}
          {level.type === 'code' && level.codeRef && (
            <div className='space-y-2 rounded border border-slate-100 bg-slate-50 p-3'>
              <div className='text-xs'>
                <span className='text-slate-600'>Symbol:</span>
                <span className='ml-2 font-mono font-semibold text-slate-900'>
                  {level.codeRef.symbolName}
                </span>
              </div>

              <div className='text-xs'>
                <span className='text-slate-600'>Type:</span>
                <span className='ml-2 font-mono text-slate-700'>{level.codeRef.symbolType}</span>
              </div>

              {level.codeRef.filePath && (
                <div className='text-xs'>
                  <span className='text-slate-600'>File:</span>
                  <span className='ml-2 block truncate font-mono text-slate-700'>
                    {level.codeRef.filePath}
                  </span>
                </div>
              )}

              {(level.codeRef.startLine ?? level.codeRef.endLine) && (
                <div className='text-xs'>
                  <span className='text-slate-600'>Lines:</span>
                  <span className='ml-2 font-mono text-slate-700'>
                    {level.codeRef.startLine}
                    {level.codeRef.endLine && level.codeRef.endLine !== level.codeRef.startLine
                      ? `–${level.codeRef.endLine}`
                      : ''}
                  </span>
                </div>
              )}

              {level.codeRef.signature && (
                <div className='mt-2 overflow-x-auto rounded border border-slate-200 bg-white p-2 text-xs'>
                  <span className='text-slate-600'>Signature:</span>
                  <pre className='mt-1 overflow-x-auto font-mono text-xs text-slate-700'>
                    {level.codeRef.signature}
                  </pre>
                </div>
              )}

              {level.codeRef.filePath && onOpenCode && (
                <Button
                  size='sm'
                  variant='outline'
                  className='mt-2 w-full'
                  onClick={() => {
                    onOpenCode(level.codeRef!);
                  }}
                >
                  <ExternalLink className='mr-1 h-3 w-3' />
                  Open in Editor
                </Button>
              )}
            </div>
          )}

          {/* Requirement Level Details */}
          {level.type === 'requirement' && (
            <div className='space-y-2 rounded border border-slate-100 bg-slate-50 p-3'>
              {level.businessValue && (
                <div className='text-xs'>
                  <span className='text-slate-600'>Business Value:</span>
                  <p className='mt-1 ml-0 text-slate-700'>{level.businessValue}</p>
                </div>
              )}
              {level.requirementId && onOpenRequirement && (
                <Button
                  size='sm'
                  variant='outline'
                  className='mt-2 w-full'
                  onClick={() => {
                    onOpenRequirement(level.requirementId!);
                  }}
                >
                  <ExternalLink className='mr-1 h-3 w-3' />
                  View Requirement
                </Button>
              )}
            </div>
          )}

          {/* Canonical Concept Details */}
          {level.type === 'concept' && level.canonicalId && (
            <div className='space-y-2 rounded border border-purple-200 bg-purple-50 p-3'>
              <div className='text-xs text-purple-900'>
                <p className='font-semibold'>Canonical Concept</p>
                <p className='mt-1 text-xs text-purple-700'>
                  This trace is unified under a single canonical concept, linking all perspectives
                  (UI, Code, Requirements) to the same abstract business entity.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Arrow to next level */}
      {!isLast && (
        <div className='flex justify-center py-2'>
          <ArrowDown className='h-4 w-4 text-slate-400' />
        </div>
      )}
    </div>
  );
});

/**
 * Display canonical concept information
 */
const CanonicalConceptCard = memo(function ConceptCard({ concept }: { concept: CanonicalConcept }) {
  return (
    <Card className='border-2 border-purple-300 bg-purple-50'>
      <CardHeader className='pb-3'>
        <div className='flex items-center gap-2'>
          <Sparkles className='h-5 w-5 text-purple-600' />
          <CardTitle className='text-sm'>Canonical Concept</CardTitle>
        </div>
      </CardHeader>
      <CardContent className='space-y-3'>
        <div>
          <p className='text-xs text-slate-600'>Name</p>
          <p className='font-semibold text-slate-900'>{concept.name}</p>
        </div>

        {concept.description && (
          <div>
            <p className='text-xs text-slate-600'>Description</p>
            <p className='text-sm text-slate-700'>{concept.description}</p>
          </div>
        )}

        <div className='flex items-center gap-2'>
          <Badge variant='outline'>{concept.domain}</Badge>
          {concept.tags?.map((tag) => (
            <Badge key={tag} variant='secondary' className='text-xs'>
              {tag}
            </Badge>
          ))}
        </div>

        <div className='rounded border border-purple-200 bg-white p-2 text-xs'>
          <p className='mb-1 text-slate-600'>Confidence</p>
          <div className='h-2 w-full rounded-full bg-slate-200'>
            <div
              className='h-2 rounded-full bg-purple-600 transition-all'
              style={{ width: `${concept.confidence * 100}%` }}
            />
          </div>
          <p className='mt-1 font-semibold text-slate-700'>
            {Math.round(concept.confidence * 100)}%
          </p>
        </div>

        {concept.projectionCount > 0 && (
          <div className='rounded border border-purple-200 bg-white p-2 text-xs'>
            <p className='text-slate-600'>
              <span className='font-semibold'>{concept.projectionCount}</span> perspective
              {concept.projectionCount !== 1 ? 's' : ''} linked
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
});

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const UICodeTracePanel = memo(function UICodeTracePanelComponent({
  traceChain,
  isLoading,
  onOpenCode,
  onOpenRequirement,
  onNavigateToUI,
  onRefreshTrace,
}: UICodeTracePanelProps) {
  const [_expandedLevels, _setExpandedLevels] = useState<Set<string>>(new Set());

  if (!traceChain && !isLoading) {
    return (
      <Card className='w-full'>
        <CardContent className='p-8 text-center'>
          <FileText className='mx-auto mb-2 h-8 w-8 text-slate-400' />
          <p className='text-sm text-slate-600'>No trace chain selected</p>
          <p className='mt-1 text-xs text-slate-500'>
            Select a UI component to view its traceability chain
          </p>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className='w-full'>
        <CardContent className='p-8 text-center'>
          <LoadingSpinner size='sm' text='Loading trace chain...' />
        </CardContent>
      </Card>
    );
  }

  if (!traceChain) {
    return null;
  }

  const overallConfidencePercent = Math.round(traceChain.overallConfidence * 100);

  return (
    <div className='w-full space-y-4'>
      {/* Header */}
      <Card className='border-slate-300 bg-gradient-to-r from-slate-50 to-slate-100'>
        <CardHeader className='pb-3'>
          <div className='flex items-start justify-between gap-4'>
            <div className='flex-1'>
              <CardTitle className='mb-2 flex items-center gap-2'>
                <Code2 className='h-5 w-5 text-green-600' />
                {traceChain.name}
              </CardTitle>
              {traceChain.description && (
                <p className='text-sm text-slate-600'>{traceChain.description}</p>
              )}
            </div>

            <div className='flex items-center gap-2'>
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger>
                    <Badge
                      className={`flex items-center gap-1 px-3 py-1 text-lg ${CONFIDENCE_COLOR(
                        traceChain.overallConfidence,
                      )}`}
                    >
                      {overallConfidencePercent}%
                    </Badge>
                  </TooltipTrigger>
                  <TooltipContent>Overall trace confidence</TooltipContent>
                </Tooltip>
              </TooltipProvider>

              {onRefreshTrace && (
                <Button size='sm' variant='outline' onClick={onRefreshTrace} className='gap-1'>
                  <ArrowRight className='h-3 w-3' />
                  Refresh
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Canonical Concept (if available) */}
      {traceChain.canonicalConcept && (
        <CanonicalConceptCard concept={traceChain.canonicalConcept} />
      )}

      {/* Trace Levels */}
      <Card>
        <CardHeader className='pb-3'>
          <CardTitle className='text-sm'>Traceability Chain</CardTitle>
        </CardHeader>
        <CardContent className='p-0'>
          <ScrollArea className='h-[600px] w-full'>
            <div className='space-y-4 p-4'>
              {traceChain.levels.map((level, index) => (
                <TraceLevelComponent
                  key={level.id}
                  level={level}
                  index={index}
                  totalLevels={traceChain.levels.length}
                  onOpenCode={onOpenCode}
                  onOpenRequirement={onOpenRequirement}
                  onNavigateToUI={onNavigateToUI}
                />
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Metadata Footer */}
      <div className='px-1 text-xs text-slate-500'>
        <p>
          Last updated:{' '}
          {new Date(traceChain.lastUpdated).toLocaleString('en-US', {
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            month: 'short',
          })}
        </p>
      </div>
    </div>
  );
});

UICodeTracePanel.displayName = 'UICodeTracePanel';

export default UICodeTracePanel;
