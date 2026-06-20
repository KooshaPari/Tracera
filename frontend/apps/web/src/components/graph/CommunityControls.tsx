/**
 * Community Controls - UI controls for Louvain community detection visualization
 *
 * Provides toggle, legend, and export controls for graph community detection.
 */

import { Check, Download, Info, X } from 'lucide-react';
import { useCallback, useMemo } from 'react';

import { Button } from '@tracertm/ui/components/Button';
import { Label } from '@tracertm/ui/components/Label';
import { Separator } from '@tracertm/ui/components/Separator';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { CommunityResult } from '../../lib/graph/clustering';

import {
  exportCommunitiesCSV,
  exportCommunitiesJSON,
  formatCommunityStats,
} from '../../lib/graph/clustering';

export interface CommunityControlsProps {
  /** Whether community detection is enabled */
  enabled: boolean;

  /** Callback when community detection is toggled */
  onToggle: (enabled: boolean) => void;

  /** Community detection results (if enabled and computed) */
  result?: CommunityResult;

  /** Whether clustering is in progress */
  isLoading?: boolean;

  /** Callback to close the panel */
  onClose?: () => void;

  /** Custom class name */
  className?: string;
}

export function CommunityControls({
  enabled,
  onToggle,
  result,
  isLoading = false,
  onClose,
  className = '',
}: CommunityControlsProps) {
  // Sort communities by size for legend display
  const sortedCommunities = useMemo(() => {
    if (!result) {
      return [];
    }

    return [...result.stats.communitySizes.entries()]
      .map(([communityId, size]) => ({
        color: result.colors.get(communityId) ?? '#64748B',
        id: communityId,
        size,
      }))
      .toSorted((a, b) => b.size - a.size) // Largest first
      .slice(0, 12); // Show top 12 communities
  }, [result]);

  // Export handlers
  const handleExportJSON = useCallback(() => {
    if (!result) {
      return;
    }

    const json = exportCommunitiesJSON(result);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `communities-${Date.now()}.json`;
    document.body.append(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [result]);

  const handleExportCSV = useCallback(() => {
    if (!result) {
      return;
    }

    const csv = exportCommunitiesCSV(result);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `communities-${Date.now()}.csv`;
    document.body.append(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [result]);

  return (
    <TooltipProvider>
      <div
        className={`space-y-4 ${className}`}
        role='region'
        aria-label='Community detection controls'
      >
        {/* Header with close button */}
        <div className='flex items-center justify-between'>
          <h3 className='text-sm font-semibold'>Community Detection</h3>
          {onClose && (
            <Button
              variant='ghost'
              size='sm'
              onClick={onClose}
              className='h-6 w-6 p-0'
              aria-label='Close community controls'
            >
              <X className='h-4 w-4' aria-hidden='true' />
            </Button>
          )}
        </div>

        {/* Enable toggle */}
        <div className='flex items-center justify-between gap-3'>
          <div className='flex items-center gap-2'>
            <Label htmlFor='community-toggle' className='text-sm'>
              Enable Communities
            </Label>
            <Tooltip>
              <TooltipTrigger asChild>
                <Info className='text-muted-foreground h-3.5 w-3.5' aria-hidden='true' />
              </TooltipTrigger>
              <TooltipContent>
                <p className='max-w-xs'>
                  Detects and visualizes node communities using the Louvain algorithm. Nodes in the
                  same community are colored identically.
                </p>
              </TooltipContent>
            </Tooltip>
          </div>

          <Button
            id='community-toggle'
            variant={enabled ? 'default' : 'outline'}
            size='sm'
            onClick={() => {
              onToggle(!enabled);
            }}
            disabled={isLoading}
            aria-label='Toggle community detection'
            aria-pressed={enabled}
            role='switch'
            className='h-8'
          >
            {enabled && <Check className='mr-1 h-3.5 w-3.5' />}
            {enabled ? 'On' : 'Off'}
          </Button>
        </div>

        {/* Loading state */}
        {isLoading && <div className='text-muted-foreground text-sm'>Computing communities...</div>}

        {/* Results section */}
        {enabled && result && !isLoading && (
          <>
            <Separator />

            {/* Statistics */}
            <div className='space-y-2'>
              <div className='text-sm'>
                <span className='font-medium'>Communities: </span>
                <span className='text-muted-foreground'>{result.stats.communityCount}</span>
              </div>

              <div className='text-sm'>
                <span className='font-medium'>Summary: </span>
                <span className='text-muted-foreground'>{formatCommunityStats(result.stats)}</span>
              </div>

              {result.stats.modularity !== undefined && (
                <div className='text-sm'>
                  <span className='font-medium'>Modularity: </span>
                  <span className='text-muted-foreground'>
                    {result.stats.modularity.toFixed(3)}
                  </span>
                </div>
              )}

              <div className='text-muted-foreground text-xs'>
                Computed in {result.performance.clusteringTimeMs.toFixed(0)}ms
              </div>
            </div>

            {/* Community legend */}
            {sortedCommunities.length > 0 && (
              <>
                <Separator />

                <div className='space-y-2'>
                  <h4 className='text-sm font-medium'>
                    Communities
                    {result.stats.communityCount > 12 && (
                      <span className='text-muted-foreground ml-1 text-xs'>(top 12)</span>
                    )}
                  </h4>

                  <div className='grid max-h-48 grid-cols-2 gap-2 overflow-y-auto'>
                    {sortedCommunities.map(({ id, size, color }) => (
                      <div key={id} className='flex items-center gap-2 text-xs' role='listitem'>
                        <div
                          className='h-3 w-3 flex-shrink-0 rounded-sm'
                          style={{ backgroundColor: color }}
                          aria-hidden='true'
                        />
                        <span className='text-muted-foreground truncate'>Community {id}</span>
                        <span className='ml-auto font-medium'>{size}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Export controls */}
            <Separator />

            <div className='space-y-2'>
              <h4 className='text-sm font-medium'>Export</h4>

              <div className='flex gap-2'>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={handleExportJSON}
                      className='flex-1'
                      aria-label='Export communities as JSON'
                    >
                      <Download className='mr-1.5 h-3.5 w-3.5' aria-hidden='true' />
                      JSON
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Export community data as JSON</p>
                  </TooltipContent>
                </Tooltip>

                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant='outline'
                      size='sm'
                      onClick={handleExportCSV}
                      className='flex-1'
                      aria-label='Export communities as CSV'
                    >
                      <Download className='mr-1.5 h-3.5 w-3.5' aria-hidden='true' />
                      CSV
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    <p>Export community data as CSV</p>
                  </TooltipContent>
                </Tooltip>
              </div>
            </div>
          </>
        )}

        {/* No results message */}
        {enabled && !result && !isLoading && (
          <div className='text-muted-foreground text-sm'>No community data available</div>
        )}
      </div>
    </TooltipProvider>
  );
}
