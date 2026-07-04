// Thumbnail Preview Component
// Displays thumbnails on hover, lazy loads full screenshots
// Supports version selector and fallback to component code

import { Code, ExternalLink, Image as ImageIcon } from 'lucide-react';
import { memo, useCallback, useEffect, useMemo, useState } from 'react';

import { logger } from '@/lib/logger';
import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';
import { Card } from '@tracertm/ui/components/Card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@tracertm/ui/components/Select';
import { Skeleton } from '@tracertm/ui/components/Skeleton';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@tracertm/ui/components/Tooltip';

import type { ScreenshotMetadata } from '../../utils/screenshot';

import { generateThumbnail } from '../../utils/screenshot';

export type VersionType = 'design' | 'draft' | 'review' | 'release';

const VERSION_COLORS: Record<VersionType, string> = {
  design: '#8b5cf6', // Violet
  draft: '#f59e0b', // Amber
  review: '#3b82f6', // Blue
  release: '#22c55e', // Green
};

const VERSION_LABELS: Record<VersionType, string> = {
  design: 'Design',
  draft: 'Draft',
  release: 'Release',
  review: 'Review',
};

interface ThumbnailPreviewProps {
  /** URL of the screenshot thumbnail */
  thumbnailUrl?: string;
  /** URL of the full screenshot */
  screenshotUrl?: string;
  /** Component code to display as fallback */
  componentCode?: string;
  /** Version of the screenshot */
  version?: string;
  /** Type of version */
  versionType?: VersionType;
  /** Available versions to select from */
  versions?: ScreenshotMetadata[];
  /** Called when version is selected */
  onVersionChange?: (metadata: ScreenshotMetadata) => void;
  /** Title/label */
  label?: string;
  /** Show as card or inline */
  variant?: 'card' | 'inline';
  /** Custom CSS class */
  className?: string;
}

function ThumbnailPreviewComponent({
  thumbnailUrl,
  screenshotUrl,
  componentCode,
  version,
  versionType = 'draft',
  versions = [],
  onVersionChange,
  label,
  variant = 'card',
  className,
}: ThumbnailPreviewProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [selectedVersion, setSelectedVersion] = useState(versionType);
  const [displayScreenshot, setDisplayScreenshot] = useState<string | null>(null);
  const [showFullScreenshot, setShowFullScreenshot] = useState(false);

  // Generate thumbnail from screenshot URL if needed
  useEffect(() => {}, [thumbnailUrl, screenshotUrl]);

  const handleVersionSelect = useCallback(
    (versionId: string) => {
      const selected = versions.find((v) => v.id === versionId);
      if (selected) {
        setSelectedVersion(selected.versionType);
        setDisplayScreenshot(selected.thumbnailUrl ?? selected.url);
        onVersionChange?.(selected);
      }
    },
    [versions, onVersionChange],
  );

  const versionColor = VERSION_COLORS[selectedVersion];
  const versionLabel = VERSION_LABELS[selectedVersion];

  // Content rendering based on available data
  const hasScreenshot = displayScreenshot ?? screenshotUrl;
  const hasCode = componentCode;

  const content = useMemo(() => {
    if (showFullScreenshot && screenshotUrl) {
      return (
        <div className='bg-muted/50 relative w-full overflow-hidden rounded-lg'>
          <img
            src={screenshotUrl}
            alt='Full screenshot'
            className='h-auto w-full'
            onLoad={() => {
              setIsLoading(false);
            }}
            onError={() => {
              setIsLoading(false);
            }}
          />
          <Button
            variant='secondary'
            size='sm'
            className='absolute top-2 right-2'
            onClick={() => {
              setShowFullScreenshot(false);
            }}
          >
            Close
          </Button>
        </div>
      );
    }

    if (isLoading) {
      return <Skeleton className='h-48 w-full rounded-lg' />;
    }

    if (hasScreenshot && displayScreenshot) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <div
                className='bg-muted/50 group relative w-full cursor-pointer overflow-hidden rounded-lg'
                onClick={() => {
                  setShowFullScreenshot(true);
                }}
              >
                <img
                  src={displayScreenshot}
                  alt={label ?? 'Screenshot'}
                  className='h-auto w-full transition-opacity group-hover:opacity-75'
                />
                <div className='absolute inset-0 flex items-center justify-center bg-black/0 opacity-0 transition-colors group-hover:bg-black/10 group-hover:opacity-100'>
                  <ImageIcon className='h-6 w-6 text-white' />
                </div>
              </div>
            </TooltipTrigger>
            <TooltipContent>Click to view full screenshot</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    if (hasCode) {
      return (
        <div className='bg-muted relative max-h-48 w-full overflow-x-auto rounded-lg p-3 font-mono text-xs'>
          <Code className='text-muted-foreground mb-2 h-4 w-4' />
          <pre className='text-muted-foreground'>
            <code>{componentCode}</code>
          </pre>
        </div>
      );
    }

    return (
      <div className='border-muted-foreground/20 flex h-48 w-full items-center justify-center rounded-lg border-2 border-dashed'>
        <div className='text-center'>
          <ImageIcon className='text-muted-foreground/40 mx-auto mb-2 h-8 w-8' />
          <p className='text-muted-foreground text-sm'>No preview available</p>
        </div>
      </div>
    );
  }, [
    showFullScreenshot,
    screenshotUrl,
    displayScreenshot,
    isLoading,
    hasScreenshot,
    hasCode,
    componentCode,
    label,
  ]);

  if (variant === 'inline') {
    return (
      <div className={cn('inline-block', className)}>
        <TooltipProvider>
          <Tooltip delayDuration={300}>
            <TooltipTrigger asChild>
              <div className='bg-muted/50 h-24 w-24 cursor-pointer overflow-hidden rounded-lg border'>
                {displayScreenshot ? (
                  <img src={displayScreenshot} alt={label} className='h-full w-full object-cover' />
                ) : (
                  <div className='flex h-full w-full items-center justify-center'>
                    <ImageIcon className='text-muted-foreground/50 h-4 w-4' />
                  </div>
                )}
              </div>
            </TooltipTrigger>
            <TooltipContent side='right' className='w-72'>
              <div className='space-y-2'>
                {label && <p className='font-semibold'>{label}</p>}
                {displayScreenshot && (
                  <img src={displayScreenshot} alt={label} className='w-full rounded-md border' />
                )}
                {version && (
                  <Badge variant='secondary' className='text-xs'>
                    {version}
                  </Badge>
                )}
              </div>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    );
  }

  return (
    <Card className={cn('overflow-hidden', className)}>
      {/* Header */}
      {label && (
        <div className='bg-muted/30 border-b p-3'>
          <div className='flex items-center justify-between gap-2'>
            <h4 className='text-sm font-semibold'>{label}</h4>
            {versions.length > 1 && (
              <Select value={selectedVersion} onValueChange={handleVersionSelect}>
                <SelectTrigger className='h-7 w-24 text-xs'>
                  <SelectValue placeholder='Version' />
                </SelectTrigger>
                <SelectContent>
                  {versions.map((v) => (
                    <SelectItem key={v.id} value={v.id}>
                      <Badge
                        variant='outline'
                        style={{
                          backgroundColor: `${VERSION_COLORS[v.versionType]}20`,
                          borderColor: VERSION_COLORS[v.versionType],
                          color: VERSION_COLORS[v.versionType],
                        }}
                      >
                        {VERSION_LABELS[v.versionType]}
                      </Badge>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>
        </div>
      )}

      {/* Content */}
      <div className='space-y-3 p-3'>
        {content}

        {/* Version badge */}
        {version && (
          <div className='flex items-center justify-between'>
            <span className='text-muted-foreground text-xs'>Version</span>
            <Badge
              style={{
                backgroundColor: `${versionColor}20`,
                borderColor: versionColor,
                color: versionColor,
              }}
            >
              {versionLabel} {version}
            </Badge>
          </div>
        )}

        {/* Actions */}
        <div className='flex gap-2'>
          {screenshotUrl && (
            <Button
              variant='outline'
              size='sm'
              className='flex-1 text-xs'
              onClick={() => window.open(screenshotUrl, '_blank')}
            >
              <ExternalLink className='mr-1 h-3 w-3' />
              Open
            </Button>
          )}
          {displayScreenshot && (
            <Button
              variant='secondary'
              size='sm'
              className='flex-1 text-xs'
              onClick={() => {
                setShowFullScreenshot(!showFullScreenshot);
              }}
            >
              <ImageIcon className='mr-1 h-3 w-3' />
              {showFullScreenshot ? 'Collapse' : 'Expand'}
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}

export const ThumbnailPreview = memo(ThumbnailPreviewComponent);
