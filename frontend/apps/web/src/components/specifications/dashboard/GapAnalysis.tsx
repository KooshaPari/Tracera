/**
 * GapAnalysis - Uncovered items list with priority sorting
 * Shows items without test coverage, ADR links, or contracts
 */

import { motion } from 'framer-motion';
import {
  AlertCircle,
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  FileText,
  Shield,
  Zap,
} from 'lucide-react';
import { useMemo, useState } from 'react';

import { cn } from '@/lib/utils';
import { Button, Card, CardContent, Tabs, TabsContent, TabsList, TabsTrigger } from '@tracertm/ui';

interface GapItem {
  id: string;
  label: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  gapType: 'no_tests' | 'no_adr' | 'no_contract' | 'orphaned';
  affectedItems?: number;
  impact?: string;
  suggestion?: string;
  linkedResources?: {
    type: 'test_case' | 'adr' | 'contract';
    id: string;
    label: string;
  }[];
}

interface GapAnalysisProps {
  items: GapItem[];
  onItemClick?: (item: GapItem) => void;
  onCreateLink?: (gap: GapItem, resourceType: string) => void;
  className?: string;
}

const GAP_TYPE_CONFIG = {
  no_adr: {
    bg: 'bg-amber-50 dark:bg-amber-900/20',
    color: 'text-amber-600',
    icon: FileText,
    label: 'No ADR Link',
  },
  no_contract: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    color: 'text-blue-600',
    icon: Shield,
    label: 'No Contract',
  },
  no_tests: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    color: 'text-red-600',
    icon: AlertCircle,
    label: 'No Test Coverage',
  },
  orphaned: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    color: 'text-purple-600',
    icon: AlertTriangle,
    label: 'Orphaned Item',
  },
};

const PRIORITY_CONFIG = {
  critical: {
    badge: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200',
    color: 'text-red-600',
    icon: AlertCircle,
    label: 'Critical',
  },
  high: {
    badge: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-200',
    color: 'text-orange-600',
    icon: AlertTriangle,
    label: 'High',
  },
  low: {
    badge: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200',
    color: 'text-blue-600',
    icon: CheckCircle2,
    label: 'Low',
  },
  medium: {
    badge: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-200',
    color: 'text-yellow-600',
    icon: AlertTriangle,
    label: 'Medium',
  },
};

export function GapAnalysis({ items, onItemClick, onCreateLink, className }: GapAnalysisProps) {
  const [sortBy, setSortBy] = useState<'priority' | 'impact'>('priority');
  const [selectedGapType, setSelectedGapType] = useState<'all' | string>('all');

  const sortedItems = useMemo(() => {
    let filtered = items;

    if (selectedGapType !== 'all') {
      filtered = items.filter((item) => item.gapType === selectedGapType);
    }

    return [...filtered].toSorted((a: GapItem, b: GapItem) => {
      if (sortBy === 'priority') {
        const priorityOrder = {
          critical: 0,
          high: 1,
          low: 3,
          medium: 2,
        };
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      }
      return (b.affectedItems ?? 0) - (a.affectedItems ?? 0);
    });
  }, [items, sortBy, selectedGapType]);

  const stats = useMemo(
    () => ({
      critical: items.filter((i) => i.priority === 'critical').length,
      highPriority: items.filter((i) => i.priority === 'high').length,
      noAdr: items.filter((i) => i.gapType === 'no_adr').length,
      noContract: items.filter((i) => i.gapType === 'no_contract').length,
      noTests: items.filter((i) => i.gapType === 'no_tests').length,
      totalGaps: items.length,
    }),
    [items],
  );

  return (
    <motion.div
      className={cn('space-y-6', className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {/* Stats Cards */}
      <div className='grid grid-cols-2 gap-3 md:grid-cols-6'>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-red-600'>{stats.totalGaps}</div>
            <p className='text-muted-foreground text-xs'>Total Gaps</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-red-700'>{stats.critical}</div>
            <p className='text-muted-foreground text-xs'>Critical</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-orange-600'>{stats.highPriority}</div>
            <p className='text-muted-foreground text-xs'>High</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-red-600'>{stats.noTests}</div>
            <p className='text-muted-foreground text-xs'>No Tests</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-amber-600'>{stats.noAdr}</div>
            <p className='text-muted-foreground text-xs'>No ADR</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className='pt-4'>
            <div className='text-2xl font-bold text-blue-600'>{stats.noContract}</div>
            <p className='text-muted-foreground text-xs'>No Contract</p>
          </CardContent>
        </Card>
      </div>

      {/* Filter Tabs */}
      <Tabs defaultValue='all' onValueChange={setSelectedGapType}>
        <TabsList className='w-full justify-start'>
          <TabsTrigger value='all'>All Gaps</TabsTrigger>
          <TabsTrigger value='no_tests'>Missing Tests</TabsTrigger>
          <TabsTrigger value='no_adr'>Missing ADR</TabsTrigger>
          <TabsTrigger value='no_contract'>Missing Contract</TabsTrigger>
          <TabsTrigger value='orphaned'>Orphaned</TabsTrigger>
        </TabsList>

        <div className='mt-4 flex items-center justify-between'>
          <div className='text-muted-foreground text-sm'>Showing {sortedItems.length} gap(s)</div>
          <div className='flex gap-2'>
            <Button
              variant={sortBy === 'priority' ? 'default' : 'outline'}
              size='sm'
              onClick={() => {
                setSortBy('priority');
              }}
            >
              By Priority
            </Button>
            <Button
              variant={sortBy === 'impact' ? 'default' : 'outline'}
              size='sm'
              onClick={() => {
                setSortBy('impact');
              }}
            >
              By Impact
            </Button>
          </div>
        </div>

        <TabsContent value='all' className='mt-4 space-y-3'>
          {sortedItems.length === 0 ? (
            <Card>
              <CardContent className='text-muted-foreground py-8 pt-6 text-center'>
                <CheckCircle2 className='mx-auto mb-3 h-12 w-12 opacity-20' />
                <p>No gaps detected - excellent coverage!</p>
              </CardContent>
            </Card>
          ) : (
            sortedItems.map((item: GapItem, idx: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <GapCard
                  item={item}
                  onClick={() => onItemClick?.(item)}
                  onCreateLink={(resourceType) => onCreateLink?.(item, resourceType)}
                />
              </motion.div>
            ))
          )}
        </TabsContent>

        <TabsContent value='no_tests' className='mt-4 space-y-3'>
          {sortedItems.length === 0 ? (
            <Card>
              <CardContent className='text-muted-foreground py-8 pt-6 text-center'>
                <CheckCircle2 className='mx-auto mb-3 h-12 w-12 opacity-20' />
                <p>All items have test coverage!</p>
              </CardContent>
            </Card>
          ) : (
            sortedItems.map((item: GapItem, idx: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <GapCard
                  item={item}
                  onClick={() => onItemClick?.(item)}
                  onCreateLink={(resourceType) => onCreateLink?.(item, resourceType)}
                />
              </motion.div>
            ))
          )}
        </TabsContent>

        <TabsContent value='no_adr' className='mt-4 space-y-3'>
          {sortedItems.length === 0 ? (
            <Card>
              <CardContent className='text-muted-foreground py-8 pt-6 text-center'>
                <CheckCircle2 className='mx-auto mb-3 h-12 w-12 opacity-20' />
                <p>All items have ADR links!</p>
              </CardContent>
            </Card>
          ) : (
            sortedItems.map((item: GapItem, idx: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <GapCard
                  item={item}
                  onClick={() => onItemClick?.(item)}
                  onCreateLink={(resourceType) => onCreateLink?.(item, resourceType)}
                />
              </motion.div>
            ))
          )}
        </TabsContent>

        <TabsContent value='no_contract' className='mt-4 space-y-3'>
          {sortedItems.length === 0 ? (
            <Card>
              <CardContent className='text-muted-foreground py-8 pt-6 text-center'>
                <CheckCircle2 className='mx-auto mb-3 h-12 w-12 opacity-20' />
                <p>All items have contracts!</p>
              </CardContent>
            </Card>
          ) : (
            sortedItems.map((item: GapItem, idx: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <GapCard
                  item={item}
                  onClick={() => onItemClick?.(item)}
                  onCreateLink={(resourceType) => onCreateLink?.(item, resourceType)}
                />
              </motion.div>
            ))
          )}
        </TabsContent>

        <TabsContent value='orphaned' className='mt-4 space-y-3'>
          {sortedItems.length === 0 ? (
            <Card>
              <CardContent className='text-muted-foreground py-8 pt-6 text-center'>
                <CheckCircle2 className='mx-auto mb-3 h-12 w-12 opacity-20' />
                <p>No orphaned items found!</p>
              </CardContent>
            </Card>
          ) : (
            sortedItems.map((item: GapItem, idx: number) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <GapCard
                  item={item}
                  onClick={() => onItemClick?.(item)}
                  onCreateLink={(resourceType) => onCreateLink?.(item, resourceType)}
                />
              </motion.div>
            ))
          )}
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}

interface GapCardProps {
  item: GapItem;
  onClick: () => void;
  onCreateLink: (resourceType: string) => void;
}

function GapCard({ item, onClick, onCreateLink }: GapCardProps) {
  const gapConfig = GAP_TYPE_CONFIG[item.gapType];
  const priorityConfig = PRIORITY_CONFIG[item.priority];
  const GapIcon = gapConfig.icon;

  return (
    <Card
      className='cursor-pointer border-l-4 transition-all hover:shadow-md'
      style={{
        borderLeftColor: {
          critical: '#dc2626',
          high: '#ea580c',
          low: '#0284c7',
          medium: '#eab308',
        }[item.priority],
      }}
      onClick={onClick}
    >
      <CardContent className='pt-6'>
        <div className='flex items-start justify-between gap-4'>
          {/* Left: Icon and Content */}
          <div className='flex min-w-0 flex-1 items-start gap-3'>
            <div className={cn('p-2 rounded-lg shrink-0 mt-0.5', gapConfig.bg)}>
              <GapIcon className={cn('w-4 h-4', gapConfig.color)} />
            </div>

            <div className='min-w-0 flex-1'>
              <div className='mb-1 flex items-center gap-2'>
                <h4 className='truncate font-semibold'>{item.label}</h4>
                <span
                  className={cn(
                    'text-xs font-medium px-2 py-0.5 rounded-full shrink-0',
                    priorityConfig.badge,
                  )}
                >
                  {priorityConfig.label}
                </span>
              </div>

              <p className='text-muted-foreground mb-2 text-sm'>{gapConfig.label}</p>

              {item.suggestion && (
                <p className='text-muted-foreground bg-muted/30 mb-2 rounded px-2 py-1 text-xs'>
                  {item.suggestion}
                </p>
              )}

              {item.linkedResources && item.linkedResources.length > 0 && (
                <div className='flex flex-wrap gap-1'>
                  {item.linkedResources.map((resource) => (
                    <span
                      key={`${resource.type}-${resource.id}`}
                      className='bg-muted inline-flex items-center gap-1 rounded px-2 py-1 text-xs'
                    >
                      {resource.type === 'test_case' && <BookOpen className='h-3 w-3' />}
                      {resource.type === 'adr' && <FileText className='h-3 w-3' />}
                      {resource.type === 'contract' && <Shield className='h-3 w-3' />}
                      {resource.label}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right: Actions */}
          <div className='flex shrink-0 items-center gap-1'>
            {item.affectedItems && (
              <div className='mr-2 text-right'>
                <div className='text-muted-foreground text-xs'>Affects</div>
                <div className='text-sm font-bold'>{item.affectedItems}</div>
              </div>
            )}
            <ChevronRight className='text-muted-foreground h-4 w-4' />
          </div>
        </div>

        {/* Quick Actions */}
        <div className='border-border/50 mt-3 flex gap-2 border-t pt-3'>
          <Button
            variant='ghost'
            size='sm'
            className='h-7 text-xs'
            onClick={(e) => {
              e.stopPropagation();
              onCreateLink('test_case');
            }}
          >
            <Zap className='mr-1 h-3 w-3' />
            Add Test
          </Button>
          <Button
            variant='ghost'
            size='sm'
            className='h-7 text-xs'
            onClick={(e) => {
              e.stopPropagation();
              onCreateLink('adr');
            }}
          >
            <FileText className='mr-1 h-3 w-3' />
            Link ADR
          </Button>
          <Button
            variant='ghost'
            size='sm'
            className='h-7 text-xs'
            onClick={(e) => {
              e.stopPropagation();
              onCreateLink('contract');
            }}
          >
            <Shield className='mr-1 h-3 w-3' />
            Add Contract
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
