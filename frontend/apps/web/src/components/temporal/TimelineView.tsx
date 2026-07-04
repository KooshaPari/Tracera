// Timeline View - Horizontal version timeline with markers and zoom controls

import { CalendarDays, ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';

import { cn } from '@tracertm/ui';
import { Badge } from '@tracertm/ui/components/Badge';
import { Button } from '@tracertm/ui/components/Button';

import type { Version } from './TemporalNavigator';

const MS_PER_DAY = 86_400_000;
const DAYS_PER_WEEK = 7;
const DAYS_PER_MONTH = 30;
const DAYS_PER_YEAR = 365;
const SCROLL_DELTA = 100;
const ZOOM_MIN = 0.5;
const ZOOM_STEP = 0.1;
const ZOOM_MAX = 2;
const CARD_MIN_WIDTH = 150;
const ZOOM_PCT = 100;

export interface TimelineViewProps {
  versions: Version[];
  currentVersionId: string;
  onVersionChange: (versionId: string) => void;
}

const getDaysAgo = (timestamp: Date): string => {
  const now = new Date();
  const diff = now.getTime() - timestamp.getTime();
  const days = Math.floor(diff / MS_PER_DAY);

  if (days === 0) {
    return 'Today';
  }
  if (days === 1) {
    return 'Yesterday';
  }
  if (days < DAYS_PER_WEEK) {
    return `${days} days ago`;
  }
  if (days < DAYS_PER_MONTH) {
    return `${Math.floor(days / DAYS_PER_WEEK)} weeks ago`;
  }
  if (days < DAYS_PER_YEAR) {
    return `${Math.floor(days / DAYS_PER_MONTH)} months ago`;
  }
  return `${Math.floor(days / DAYS_PER_YEAR)} years ago`;
};

export const TimelineView = ({
  versions,
  currentVersionId,
  onVersionChange,
}: TimelineViewProps) => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [scrollOffset, setScrollOffset] = useState(0);

  const sortedVersions = useMemo(
    () =>
      [...versions].toSorted(
        (a: Version, b: Version) => a.timestamp.getTime() - b.timestamp.getTime(),
      ),
    [versions],
  );

  const handleScroll = useCallback((direction: 'left' | 'right') => {
    setScrollOffset((prev) =>
      direction === 'left' ? Math.max(prev - SCROLL_DELTA, 0) : prev + SCROLL_DELTA,
    );
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoomLevel((z) => Math.max(ZOOM_MIN, z - ZOOM_STEP));
  }, []);

  const handleZoomIn = useCallback(() => {
    setZoomLevel((z) => Math.min(ZOOM_MAX, z + ZOOM_STEP));
  }, []);

  const handleScrollLeft = useCallback(() => {
    handleScroll('left');
  }, [handleScroll]);

  const handleScrollRight = useCallback(() => {
    handleScroll('right');
  }, [handleScroll]);

  return (
    <div className='flex flex-col gap-4 bg-white p-4 dark:bg-gray-950'>
      <div className='flex items-center justify-between'>
        <div className='flex items-center gap-2'>
          <Button size='sm' variant='outline' onClick={handleScrollLeft} className='h-8 w-8 p-0'>
            <ChevronLeft className='h-4 w-4' />
          </Button>
          <span className='text-xs text-gray-600 dark:text-gray-400'>
            {sortedVersions.length} versions
          </span>
          <Button size='sm' variant='outline' onClick={handleScrollRight} className='h-8 w-8 p-0'>
            <ChevronRight className='h-4 w-4' />
          </Button>
        </div>

        <div className='flex items-center gap-2'>
          <span className='text-xs text-gray-600 dark:text-gray-400'>
            Zoom: {Math.round(zoomLevel * ZOOM_PCT)}%
          </span>
          <Button size='sm' variant='outline' onClick={handleZoomOut} className='h-8 w-8 p-0'>
            <ZoomOut className='h-4 w-4' />
          </Button>
          <Button size='sm' variant='outline' onClick={handleZoomIn} className='h-8 w-8 p-0'>
            <ZoomIn className='h-4 w-4' />
          </Button>
        </div>
      </div>

      <div className='relative'>
        <div className='absolute top-6 right-0 left-0 h-1 rounded-full bg-gray-200 dark:bg-gray-700' />

        <div
          className='flex gap-4 overflow-x-auto pb-2'
          style={{
            transform: `translateX(-${scrollOffset}px)`,
            transition: 'transform 0.3s ease-out',
          }}
        >
          {sortedVersions.map((version: Version) => {
            const isCurrentVersion = version.id === currentVersionId;

            return (
              <div
                key={version.id}
                className='relative flex-shrink-0 pt-1'
                style={{
                  minWidth: CARD_MIN_WIDTH * zoomLevel,
                }}
                onClick={() => {
                  onVersionChange(version.id);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    onVersionChange(version.id);
                  }
                }}
                role='button'
                tabIndex={0}
              >
                <div
                  className={cn(
                    'absolute left-1/2 top-3 w-4 h-4 rounded-full border-2 transform -translate-x-1/2 cursor-pointer transition-all',
                    isCurrentVersion
                      ? 'bg-blue-500 border-blue-600 ring-2 ring-blue-300 dark:ring-blue-700 scale-125'
                      : 'bg-white dark:bg-gray-800 border-gray-400 dark:border-gray-600 hover:scale-110',
                  )}
                />

                <div
                  className={cn(
                    'mt-8 p-3 rounded-lg border transition-all hover:shadow-md',
                    isCurrentVersion
                      ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700 shadow-md'
                      : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600',
                  )}
                >
                  <div className='truncate text-sm font-medium text-gray-900 dark:text-gray-100'>
                    {version.tag && (
                      <Badge variant='outline' className='mr-1 text-xs'>
                        {version.tag}
                      </Badge>
                    )}
                    {version.title}
                  </div>

                  <div className='mt-1 text-xs text-gray-600 dark:text-gray-400'>
                    <div className='mt-1 flex items-center gap-1'>
                      <CalendarDays className='h-3 w-3' />
                      {getDaysAgo(version.timestamp)}
                    </div>
                  </div>

                  {version.author && (
                    <div className='mt-1 text-xs text-gray-500 dark:text-gray-500'>
                      by {version.author}
                    </div>
                  )}

                  <div className='mt-2'>
                    <Badge
                      variant={
                        version.status === 'published'
                          ? 'default'
                          : version.status === 'draft'
                            ? 'secondary'
                            : 'outline'
                      }
                      className='text-xs'
                    >
                      {version.status}
                    </Badge>
                  </div>

                  {version.description && (
                    <p className='mt-2 line-clamp-2 text-xs text-gray-600 dark:text-gray-400'>
                      {version.description}
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {sortedVersions.length > 0 &&
        (() => {
          const first = sortedVersions[0];
          const last = sortedVersions.at(-1);
          return (
            <div className='flex items-center justify-between border-t border-gray-200 pt-2 text-xs text-gray-600 dark:border-gray-800 dark:text-gray-400'>
              <span>
                {first?.timestamp.toLocaleDateString()} -{last?.timestamp.toLocaleDateString()}
              </span>
              <span>
                {sortedVersions.length} version
                {sortedVersions.length === 1 ? '' : 's'}
              </span>
            </div>
          );
        })()}

      {sortedVersions.length === 0 && (
        <div className='flex items-center justify-center py-8 text-gray-500 dark:text-gray-400'>
          <p>No versions in this branch yet</p>
        </div>
      )}
    </div>
  );
};
