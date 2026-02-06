/**
 * SpecMetadataPanel Component
 *
 * Displays common metadata across all item spec types including
 * timestamps, traceability info, and custom metadata fields.
 */

import { format } from 'date-fns';
import {
  Calendar,
  Clock,
  FileText,
  GitBranch,
  Link2,
  RefreshCw,
  Tag,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';

import { cn } from '@/lib/utils';
import { Badge, Card, CardContent, CardHeader, CardTitle, Separator } from '@tracertm/ui';

interface SpecMetadataPanelProps {
  createdAt: string;
  updatedAt: string;
  metadata?: Record<string, unknown>;
  upstreamCount?: number;
  downstreamCount?: number;
  changeCount?: number;
  volatilityIndex?: number;
  autoTags?: string[];
  sourceReference?: string;
  className?: string;
}

export function SpecMetadataPanel({
  createdAt,
  updatedAt,
  metadata = {},
  upstreamCount,
  downstreamCount,
  changeCount,
  volatilityIndex,
  autoTags = [],
  sourceReference,
  className,
}: SpecMetadataPanelProps) {
  const metadataEntries = Object.entries(metadata).filter(
    ([_, v]) => v !== null && v !== undefined,
  );

  return (
    <Card className={cn('border-none bg-muted/30', className)}>
      <CardHeader className='pb-2'>
        <CardTitle className='text-muted-foreground text-xs font-black tracking-widest uppercase'>
          Specification Metadata
        </CardTitle>
      </CardHeader>
      <CardContent className='space-y-4'>
        {/* Timestamps */}
        <div className='space-y-2'>
          <div className='flex items-center justify-between text-xs'>
            <span className='text-muted-foreground flex items-center gap-1'>
              <Calendar className='h-3 w-3' />
              Created
            </span>
            <span className='font-medium'>{format(new Date(createdAt), 'MMM d, yyyy')}</span>
          </div>
          <div className='flex items-center justify-between text-xs'>
            <span className='text-muted-foreground flex items-center gap-1'>
              <RefreshCw className='h-3 w-3' />
              Updated
            </span>
            <span className='font-medium'>
              {format(new Date(updatedAt), "MMM d, yyyy 'at' HH:mm")}
            </span>
          </div>
        </div>

        {/* Traceability */}
        {(upstreamCount !== undefined ||
          downstreamCount !== undefined ||
          changeCount !== undefined) && (
          <>
            <Separator />
            <div className='space-y-2'>
              <h4 className='text-muted-foreground text-[10px] font-black tracking-widest uppercase'>
                Traceability
              </h4>
              <div className='grid grid-cols-3 gap-2'>
                {upstreamCount !== undefined && (
                  <div className='bg-card/50 rounded p-2 text-center'>
                    <div className='flex items-center justify-center gap-1'>
                      <TrendingUp className='h-3 w-3 text-blue-500' />
                      <span className='text-sm font-bold'>{upstreamCount}</span>
                    </div>
                    <div className='text-muted-foreground text-[10px]'>Upstream</div>
                  </div>
                )}
                {downstreamCount !== undefined && (
                  <div className='bg-card/50 rounded p-2 text-center'>
                    <div className='flex items-center justify-center gap-1'>
                      <TrendingDown className='h-3 w-3 text-green-500' />
                      <span className='text-sm font-bold'>{downstreamCount}</span>
                    </div>
                    <div className='text-muted-foreground text-[10px]'>Downstream</div>
                  </div>
                )}
                {changeCount !== undefined && (
                  <div className='bg-card/50 rounded p-2 text-center'>
                    <div className='flex items-center justify-center gap-1'>
                      <GitBranch className='h-3 w-3 text-purple-500' />
                      <span className='text-sm font-bold'>{changeCount}</span>
                    </div>
                    <div className='text-muted-foreground text-[10px]'>Changes</div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Volatility */}
        {volatilityIndex !== undefined && (
          <div className='flex items-center justify-between text-xs'>
            <span className='text-muted-foreground flex items-center gap-1'>
              <Clock className='h-3 w-3' />
              Volatility Index
            </span>
            <Badge
              variant='outline'
              className={cn(
                'text-[10px]',
                volatilityIndex > 0.7
                  ? 'border-red-500 text-red-600'
                  : volatilityIndex > 0.4
                    ? 'border-yellow-500 text-yellow-600'
                    : 'border-green-500 text-green-600',
              )}
            >
              {(volatilityIndex * 100).toFixed(0)}%
            </Badge>
          </div>
        )}

        {/* Auto Tags */}
        {autoTags.length > 0 && (
          <>
            <Separator />
            <div className='space-y-2'>
              <h4 className='text-muted-foreground flex items-center gap-1 text-[10px] font-black tracking-widest uppercase'>
                <Tag className='h-3 w-3' />
                Auto-Generated Tags
              </h4>
              <div className='flex flex-wrap gap-1'>
                {autoTags.map((tag, i) => (
                  <Badge key={i} variant='secondary' className='text-[9px]'>
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Source Reference */}
        {sourceReference && (
          <div className='flex items-center justify-between text-xs'>
            <span className='text-muted-foreground flex items-center gap-1'>
              <Link2 className='h-3 w-3' />
              Source
            </span>
            <span className='max-w-[150px] truncate font-mono text-[10px]'>{sourceReference}</span>
          </div>
        )}

        {/* Custom Metadata */}
        {metadataEntries.length > 0 && (
          <>
            <Separator />
            <div className='space-y-2'>
              <h4 className='text-muted-foreground flex items-center gap-1 text-[10px] font-black tracking-widest uppercase'>
                <FileText className='h-3 w-3' />
                Custom Fields
              </h4>
              <div className='space-y-1.5'>
                {metadataEntries.slice(0, 6).map(([key, value]) => (
                  <div key={key} className='flex items-center justify-between text-xs'>
                    <span className='text-muted-foreground max-w-[100px] truncate'>{key}</span>
                    <span className='max-w-[120px] truncate font-medium'>
                      {typeof value === 'object' && value !== null
                        ? JSON.stringify(value)
                        : String(value)}
                    </span>
                  </div>
                ))}
                {metadataEntries.length > 6 && (
                  <p className='text-muted-foreground text-[10px]'>
                    +{metadataEntries.length - 6} more fields
                  </p>
                )}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
