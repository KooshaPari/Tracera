// Journey Explorer - Visualize and manage derived journeys
// Displays user flows, data paths, call chains, and test traces
// Supports filtering, overlay, coverage metrics, and export

import {
  Activity,
  ArrowRight,
  Beaker,
  ChevronDown,
  ChevronRight,
  Download,
  Edit2,
  Eye,
  Grid3X3,
  Layers,
  Plus,
  Search,
  Trash2,
  X,
  Zap,
} from 'lucide-react';
import { memo, useCallback, useMemo, useState } from 'react';

import type { Item, Link } from '@tracertm/types';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@tracertm/ui/components/Card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@tracertm/ui/components/Dialog';
import { Input } from '@tracertm/ui/components/Input';
import { Progress } from '@tracertm/ui/components/Progress';
import { ScrollArea } from '@tracertm/ui/components/ScrollArea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

// =============================================================================
// TYPES
// =============================================================================

export interface DerivedJourney {
  id: string;
  name: string;
  type: 'user_flow' | 'data_path' | 'call_chain' | 'test_trace';
  nodeIds: string[];
  links: { sourceId: string; targetId: string; type: string }[];
  color?: string;
}

interface JourneyExplorerProps {
  // Core data
  items: Item[];
  links: Link[];
  journeys: DerivedJourney[];

  // Callbacks
  onJourneySelect?: (journey: DerivedJourney) => void;
  onJourneyOverlay?: (journeyIds: string[]) => void;
  onJourneyCreate?: (journey: Omit<DerivedJourney, 'id'>) => void;
  onJourneyDelete?: (journeyId: string) => void;
  onJourneyUpdate?: (journeyId: string, updates: Partial<DerivedJourney>) => void;
  onExport?: (format: 'json' | 'csv' | 'svg') => void;

  // UI state
  selectedJourneyIds?: string[];
  isLoading?: boolean;
  compact?: boolean;
}

interface JourneyMetrics {
  nodeCount: number;
  linkCount: number;
  coverage: number;
  confidence: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

const JOURNEY_TYPE_CONFIG = {
  call_chain: {
    color: '#f59e0b',
    description: 'Function/method invocation sequences',
    icon: Layers,
    label: 'Call Chain',
  },
  data_path: {
    color: '#3b82f6',
    description: 'Data flow between components and databases',
    icon: Zap,
    label: 'Data Path',
  },
  test_trace: {
    color: '#22c55e',
    description: 'Test execution flows and coverage',
    icon: Beaker,
    label: 'Test Trace',
  },
  user_flow: {
    color: '#9333ea',
    description: 'User interaction paths through the system',
    icon: Activity,
    label: 'User Flow',
  },
};

const JOURNEY_COLORS = [
  '#9333ea',
  '#3b82f6',
  '#f59e0b',
  '#22c55e',
  '#ef4444',
  '#ec4899',
  '#10b981',
  '#06b6d4',
];

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function calculateJourneyMetrics(
  journey: DerivedJourney,
  _items: Item[],
  _links: Link[],
  allNodeIds: string[],
): JourneyMetrics {
  const nodeCount = journey.nodeIds.length;
  const linkCount = journey.links.length;
  const coverage = allNodeIds.length > 0 ? (nodeCount / allNodeIds.length) * 100 : 0;

  // Calculate confidence based on link density and node coverage
  const maxPossibleLinks = (nodeCount * (nodeCount - 1)) / 2;
  const linkDensity = maxPossibleLinks > 0 ? linkCount / maxPossibleLinks : 0;
  const confidence = Math.round((linkDensity * coverage) / 100);

  return { confidence, coverage, linkCount, nodeCount };
}

function getJourneyNodeNames(journey: DerivedJourney, items: Item[]): Map<string, string> {
  const itemMap = new Map(items.map((item) => [item.id, item.title]));
  const names = new Map<string, string>();
  journey.nodeIds.forEach((nodeId) => {
    names.set(nodeId, itemMap.get(nodeId) ?? nodeId);
  });
  return names;
}

// =============================================================================
// COMPONENTS
// =============================================================================

interface JourneyFlowVisualizerProps {
  journey: DerivedJourney;
  itemNames: Map<string, string>;
  compact?: boolean;
}

function JourneyFlowVisualizer({
  journey,
  itemNames,
  compact = false,
}: JourneyFlowVisualizerProps) {
  const [isExpanded] = useState(!compact);
  const maxVisible = compact ? 3 : 7;
  const visibleNodes = journey.nodeIds.slice(0, maxVisible);
  const hiddenCount = Math.max(0, journey.nodeIds.length - maxVisible);

  return (
    <div className='flex flex-col gap-2'>
      <div className='flex items-center gap-2 overflow-x-auto pb-2'>
        {visibleNodes.map((nodeId, idx) => (
          <div key={nodeId} className='flex shrink-0 items-center gap-2'>
            <div className='bg-muted flex items-center rounded-full px-2 py-1 text-xs font-medium whitespace-nowrap'>
              {itemNames.get(nodeId) ?? nodeId}
            </div>
            {idx < visibleNodes.length - 1 && (
              <ArrowRight className='text-muted-foreground h-4 w-4 shrink-0' />
            )}
          </div>
        ))}
        {hiddenCount > 0 && (
          <div className='text-muted-foreground px-2 py-1 text-xs'>+{hiddenCount} more</div>
        )}
      </div>
      {isExpanded && journey.links.length > 0 && (
        <div className='text-muted-foreground mt-1 space-y-1 text-xs'>
          <div className='font-medium'>Links ({journey.links.length})</div>
          <div className='max-h-32 space-y-1 overflow-y-auto'>
            {journey.links.slice(0, 5).map((link, idx) => (
              <div key={`${link.sourceId}-${link.targetId}-${idx}`}>
                <span className='text-muted-foreground'>
                  {itemNames.get(link.sourceId) ?? link.sourceId}
                  {' → '}
                  {itemNames.get(link.targetId) ?? link.targetId}
                  {link.type && (
                    <Badge variant='outline' className='ml-1 text-xs'>
                      {link.type}
                    </Badge>
                  )}
                </span>
              </div>
            ))}
            {journey.links.length > 5 && (
              <div className='text-muted-foreground text-xs'>
                +{journey.links.length - 5} more links
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

interface JourneyCardProps {
  journey: DerivedJourney;
  metrics: JourneyMetrics;
  isSelected: boolean;
  itemNames: Map<string, string>;
  onSelect: () => void;
  onDelete?: () => void;
  onUpdate?: (updates: Partial<DerivedJourney>) => void;
  compact?: boolean;
}

function JourneyCard({
  journey,
  metrics,
  isSelected,
  itemNames,
  onSelect,
  onDelete,
  onUpdate,
  compact = false,
}: JourneyCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const config = JOURNEY_TYPE_CONFIG[journey.type];
  const TypeIcon = config.icon;

  const bgColor = journey.color ?? config.color;

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all border-2',
        isSelected ? 'border-primary bg-primary/5' : 'border-muted hover:border-primary/30',
      )}
      onClick={onSelect}
    >
      <CardHeader className='pb-3'>
        <div className='flex items-start justify-between gap-2'>
          <div className='flex min-w-0 flex-1 items-start gap-2'>
            <div
              className='mt-1 shrink-0 rounded-lg p-2'
              style={{ backgroundColor: `${bgColor}20` }}
            >
              <TypeIcon className='h-4 w-4' style={{ color: bgColor }} />
            </div>
            <div className='min-w-0 flex-1'>
              <h4 className='truncate text-sm leading-tight font-semibold'>{journey.name}</h4>
              <p className='text-muted-foreground mt-1 text-xs'>{config.label}</p>
            </div>
          </div>
          {onDelete && (
            <Button
              variant='ghost'
              size='sm'
              className='h-6 w-6 p-0 opacity-0 group-hover:opacity-100'
              onClick={(e) => {
                e.stopPropagation();
                onDelete();
              }}
            >
              <Trash2 className='h-3 w-3' />
            </Button>
          )}
        </div>

        {/* Metrics Row */}
        <div className='text-muted-foreground mt-3 flex items-center gap-3 text-xs'>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <span className='font-medium'>{metrics.nodeCount} nodes</span>
              </TooltipTrigger>
              <TooltipContent>Journey contains {metrics.nodeCount} items</TooltipContent>
            </Tooltip>
          </TooltipProvider>
          <span>•</span>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <span className='font-medium'>{metrics.linkCount} links</span>
              </TooltipTrigger>
              <TooltipContent>{metrics.linkCount} connections between nodes</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>

      <CardContent className='space-y-3 pb-3'>
        {/* Coverage Bar */}
        <div className='space-y-1'>
          <div className='flex items-center justify-between text-xs'>
            <span className='text-muted-foreground'>Coverage</span>
            <span className='font-medium'>{metrics.coverage.toFixed(1)}%</span>
          </div>
          <Progress value={Math.min(metrics.coverage, 100)} className='h-1' />
        </div>

        {/* Flow Visualization */}
        {!compact && (
          <div className='bg-muted/50 rounded-lg p-2'>
            <JourneyFlowVisualizer journey={journey} itemNames={itemNames} compact />
          </div>
        )}

        {/* Actions */}
        <div className='flex items-center justify-between gap-1 pt-2'>
          <Button
            variant='ghost'
            size='sm'
            className='h-7 text-xs'
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
          >
            {isExpanded ? (
              <ChevronDown className='mr-1 h-3 w-3' />
            ) : (
              <ChevronRight className='mr-1 h-3 w-3' />
            )}
            Details
          </Button>
          <Button
            variant='outline'
            size='sm'
            className='h-7 text-xs'
            onClick={(e) => {
              e.stopPropagation();
              onUpdate?.({
                color:
                  JOURNEY_COLORS[Math.floor(Math.random() * JOURNEY_COLORS.length)] ?? '#9333ea',
              });
            }}
          >
            <Edit2 className='mr-1 h-3 w-3' />
            Edit
          </Button>
        </div>

        {/* Expanded Details */}
        {isExpanded && (
          <>
            <Separator className='my-2' />
            <div className='space-y-3 text-xs'>
              <JourneyFlowVisualizer journey={journey} itemNames={itemNames} />
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}

interface CreateJourneyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreate: (journey: Omit<DerivedJourney, 'id'>) => void;
  isLoading?: boolean;
}

function CreateJourneyDialog({
  open,
  onOpenChange,
  onCreate,
  isLoading = false,
}: CreateJourneyDialogProps) {
  const [name, setName] = useState('');
  const [type, setType] = useState<DerivedJourney['type']>('user_flow');
  const [selectedNodes, setSelectedNodes] = useState<string[]>([]);

  const handleCreate = () => {
    if (!name.trim()) {
      return;
    }

    onCreate({
      color: JOURNEY_TYPE_CONFIG[type].color,
      links: [],
      name: name.trim(),
      nodeIds: selectedNodes,
      type,
    });

    setName('');
    setSelectedNodes([]);
    setType('user_flow');
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='max-w-md'>
        <DialogHeader>
          <DialogTitle>Create Manual Journey</DialogTitle>
          <DialogDescription>
            Define a new journey by selecting nodes and specifying its type
          </DialogDescription>
        </DialogHeader>

        <div className='space-y-4'>
          {/* Name */}
          <div className='space-y-2'>
            <label className='text-sm font-medium'>Journey Name</label>
            <Input
              placeholder='e.g., Checkout Flow'
              value={name}
              onChange={(e) => {
                setName(e.target.value);
              }}
              disabled={isLoading}
            />
          </div>

          {/* Type */}
          <div className='space-y-2'>
            <label className='text-sm font-medium'>Journey Type</label>
            <Select
              value={type}
              onValueChange={(v) => {
                setType(v as DerivedJourney['type']);
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(JOURNEY_TYPE_CONFIG).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    <div className='flex items-center gap-2'>
                      <config.icon className='h-4 w-4' />
                      {config.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Node Selection Helper Text */}
          <div className='bg-muted/50 text-muted-foreground rounded-lg p-3 text-xs'>
            <p>
              After creating the journey, you can edit it to add nodes and links in the journey
              editor.
            </p>
          </div>
        </div>

        <div className='flex justify-end gap-2 pt-4'>
          <Button
            variant='outline'
            onClick={() => {
              onOpenChange(false);
            }}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button onClick={handleCreate} disabled={!name.trim() || isLoading}>
            {isLoading ? 'Creating...' : 'Create Journey'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export const JourneyExplorer = memo(function JourneyExplorer({
  items,
  links,
  journeys,
  onJourneySelect,
  onJourneyOverlay,
  onJourneyCreate,
  onJourneyDelete,
  onJourneyUpdate,
  onExport,
  selectedJourneyIds = [],
  isLoading = false,
  compact = false,
}: JourneyExplorerProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState<DerivedJourney['type'] | 'all'>('all');
  const [overlayMode, setOverlayMode] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  // Calculate overall metrics
  const allNodeIds = useMemo(() => new Set(items.map((i) => i.id)), [items]);

  const journeyMetrics = useMemo(
    () =>
      journeys.reduce<Record<string, JourneyMetrics>>((acc, journey) => {
        acc[journey.id] = calculateJourneyMetrics(journey, items, links, [...allNodeIds]);
        return acc;
      }, {}),
    [journeys, items, links, allNodeIds],
  );

  const journeyNames = useMemo(
    () =>
      journeys.reduce<Record<string, Map<string, string>>>((acc, journey) => {
        acc[journey.id] = getJourneyNodeNames(journey, items);
        return acc;
      }, {}),
    [journeys, items],
  );

  // Filter journeys
  const filteredJourneys = useMemo(
    () =>
      journeys.filter((journey) => {
        const matchesSearch =
          journey.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          journey.type.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesType = selectedType === 'all' || journey.type === selectedType;
        return matchesSearch && matchesType;
      }),
    [journeys, searchTerm, selectedType],
  );

  // Calculate coverage metrics
  const coverageMetrics = useMemo(() => {
    const journeyNodeSet = new Set<string>();
    selectedJourneyIds.forEach((journeyId) => {
      const journey = journeys.find((j) => j.id === journeyId);
      journey?.nodeIds.forEach((nodeId) => journeyNodeSet.add(nodeId));
    });

    const coverage = allNodeIds.size > 0 ? (journeyNodeSet.size / allNodeIds.size) * 100 : 0;
    return {
      coverage,
      nodesInJourneys: journeyNodeSet.size,
      totalNodes: allNodeIds.size,
    };
  }, [selectedJourneyIds, journeys, allNodeIds]);

  const handleSelectJourney = useCallback(
    (journeyId: string) => {
      const journey = journeys.find((j) => j.id === journeyId);
      if (journey) {
        onJourneySelect?.(journey);
      }
    },
    [journeys, onJourneySelect],
  );

  const handleOverlay = useCallback(() => {
    onJourneyOverlay?.(selectedJourneyIds);
  }, [selectedJourneyIds, onJourneyOverlay]);

  const handleExport = useCallback(
    (format: 'json' | 'csv' | 'svg') => {
      onExport?.(format);
    },
    [onExport],
  );

  const handleCreateJourney = useCallback(
    (journey: Omit<DerivedJourney, 'id'>) => {
      onJourneyCreate?.(journey);
    },
    [onJourneyCreate],
  );

  if (compact && journeys.length === 0) {
    return (
      <Card className='border-dashed'>
        <CardContent className='text-muted-foreground py-6 text-center'>
          <Layers className='mx-auto mb-2 h-8 w-8 opacity-50' />
          <p className='text-sm'>No journeys detected</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <TooltipProvider>
      <div className='space-y-4'>
        {/* Header */}
        <div className='flex items-center justify-between gap-2'>
          <div className='flex items-center gap-2'>
            <Layers className='text-primary h-5 w-5' />
            <h3 className='text-base font-semibold'>Journey Explorer</h3>
            <Badge variant='secondary' className='text-xs'>
              {journeys.length}
            </Badge>
          </div>
          <div className='flex items-center gap-1'>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant='outline'
                  size='sm'
                  className='h-8 px-2'
                  onClick={() => {
                    setCreateDialogOpen(true);
                  }}
                  disabled={isLoading}
                >
                  <Plus className='h-4 w-4' />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Create manual journey</TooltipContent>
            </Tooltip>

            {selectedJourneyIds.length > 0 && (
              <>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant={overlayMode ? 'default' : 'outline'}
                      size='sm'
                      className='h-8 px-2'
                      onClick={() => {
                        setOverlayMode(!overlayMode);
                        if (!overlayMode) {
                          handleOverlay();
                        }
                      }}
                      disabled={isLoading}
                    >
                      <Eye className='h-4 w-4' />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {overlayMode ? 'Hide overlay' : 'Overlay selected journeys'}
                  </TooltipContent>
                </Tooltip>

                <Dialog>
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <DialogTrigger asChild>
                        <Button
                          variant='outline'
                          size='sm'
                          className='h-8 px-2'
                          disabled={isLoading}
                        >
                          <Download className='h-4 w-4' />
                        </Button>
                      </DialogTrigger>
                    </TooltipTrigger>
                    <TooltipContent>Export journeys</TooltipContent>
                  </Tooltip>

                  <DialogContent className='max-w-sm'>
                    <DialogHeader>
                      <DialogTitle>Export Journeys</DialogTitle>
                      <DialogDescription>
                        Choose export format for selected journeys
                      </DialogDescription>
                    </DialogHeader>

                    <div className='space-y-2'>
                      <Button
                        variant='outline'
                        className='w-full justify-start'
                        onClick={() => {
                          handleExport('json');
                        }}
                      >
                        <Grid3X3 className='mr-2 h-4 w-4' />
                        JSON Format
                      </Button>
                      <Button
                        variant='outline'
                        className='w-full justify-start'
                        onClick={() => {
                          handleExport('csv');
                        }}
                      >
                        <Grid3X3 className='mr-2 h-4 w-4' />
                        CSV Format
                      </Button>
                      <Button
                        variant='outline'
                        className='w-full justify-start'
                        onClick={() => {
                          handleExport('svg');
                        }}
                      >
                        <Grid3X3 className='mr-2 h-4 w-4' />
                        SVG Visualization
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>
              </>
            )}
          </div>
        </div>

        {/* Coverage Metrics */}
        {selectedJourneyIds.length > 0 && (
          <Card className='bg-muted/30'>
            <CardContent className='pt-4'>
              <div className='space-y-2'>
                <div className='flex items-center justify-between text-sm'>
                  <span className='text-muted-foreground'>Coverage</span>
                  <span className='font-semibold'>
                    {coverageMetrics.nodesInJourneys} / {coverageMetrics.totalNodes} items
                  </span>
                </div>
                <Progress value={Math.min(coverageMetrics.coverage, 100)} className='h-2' />
                <p className='text-muted-foreground text-right text-xs'>
                  {coverageMetrics.coverage.toFixed(1)}%
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Search & Filter */}
        <div className='flex items-center gap-2'>
          <div className='relative flex-1'>
            <Search className='text-muted-foreground absolute top-1/2 left-2 h-4 w-4 -translate-y-1/2' />
            <Input
              placeholder='Search journeys...'
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
              }}
              className='h-8 pl-8 text-sm'
              disabled={isLoading}
            />
          </div>
          <Select
            value={selectedType}
            onValueChange={(v) => {
              setSelectedType(v as DerivedJourney['type'] | 'all');
            }}
            disabled={isLoading}
          >
            <SelectTrigger className='h-8 w-40 text-sm'>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>All Types</SelectItem>
              {Object.entries(JOURNEY_TYPE_CONFIG).map(([key, config]) => (
                <SelectItem key={key} value={key}>
                  {config.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {(searchTerm || selectedType !== 'all') && (
            <Button
              variant='ghost'
              size='sm'
              className='h-8 px-2'
              onClick={() => {
                setSearchTerm('');
                setSelectedType('all');
              }}
              disabled={isLoading}
            >
              <X className='h-4 w-4' />
            </Button>
          )}
        </div>

        {/* Journey List */}
        {filteredJourneys.length > 0 ? (
          <ScrollArea className={cn('rounded-lg border', compact ? 'h-96' : 'h-[500px]')}>
            <div className='space-y-3 p-3'>
              {filteredJourneys.map((journey) => (
                <JourneyCard
                  key={journey.id}
                  journey={journey}
                  metrics={
                    journeyMetrics[journey.id] ?? {
                      confidence: 0,
                      coverage: 0,
                      linkCount: 0,
                      nodeCount: 0,
                    }
                  }
                  isSelected={selectedJourneyIds.includes(journey.id)}
                  itemNames={journeyNames[journey.id] ?? new Map()}
                  onSelect={() => {
                    handleSelectJourney(journey.id);
                  }}
                  onDelete={() => onJourneyDelete?.(journey.id)}
                  onUpdate={(updates) => onJourneyUpdate?.(journey.id, updates)}
                  compact={compact}
                />
              ))}
            </div>
          </ScrollArea>
        ) : (
          <Card className='border-dashed'>
            <CardContent className='text-muted-foreground py-8 text-center'>
              <Layers className='mx-auto mb-2 h-8 w-8 opacity-50' />
              <p className='text-sm'>
                {searchTerm || selectedType !== 'all'
                  ? 'No journeys match your filters'
                  : 'No journeys detected'}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Legend */}
        <Card className='bg-muted/20'>
          <CardHeader className='pb-3'>
            <CardTitle className='text-sm'>Journey Types</CardTitle>
          </CardHeader>
          <CardContent>
            <div className='grid grid-cols-2 gap-2'>
              {Object.entries(JOURNEY_TYPE_CONFIG).map(([key, config]) => (
                <div key={key} className='flex items-center gap-2 text-xs'>
                  <div className='h-3 w-3 rounded' style={{ backgroundColor: config.color }} />
                  <span className='text-muted-foreground'>{config.label}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Create Journey Dialog */}
        <CreateJourneyDialog
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
          onCreate={handleCreateJourney}
          isLoading={isLoading}
        />
      </div>
    </TooltipProvider>
  );
});

JourneyExplorer.displayName = 'JourneyExplorer';
