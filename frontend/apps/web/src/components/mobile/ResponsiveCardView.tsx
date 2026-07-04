import type { ReactNode } from 'react';

import { useCallback } from 'react';

import { cn } from '@/lib/utils';

const SKELETON_COUNT = 6;

export interface CardItem {
  id: string;
  title: string;
  subtitle?: string | undefined;
  badge?: ReactNode | undefined;
  status?: ReactNode | undefined;
  priority?: ReactNode | undefined;
  owner?: ReactNode | undefined;
  actions?: ReactNode | undefined;
  metadata?: Record<string, ReactNode> | undefined;
  onClick?: (() => void) | undefined;
}

interface ResponsiveCardViewProps {
  items: CardItem[];
  isLoading?: boolean | undefined;
  emptyState?: ReactNode | undefined;
  className?: string | undefined;
  cardClassName?: string | undefined;
  onItemClick?: ((item: CardItem) => void) | undefined;
}

/**
 * Responsive card view component that displays items as cards on mobile
 * and transitions to grid on tablet/desktop. Designed for accessibility
 * with minimum 44px touch targets.
 */
export const ResponsiveCardView = function ResponsiveCardView({
  items,
  isLoading,
  emptyState,
  className,
  cardClassName,
  onItemClick,
}: ResponsiveCardViewProps) {
  if (isLoading) {
    return (
      <div className={cn('space-y-3 sm:space-y-4 md:space-y-0', className)}>
        {Array.from({ length: SKELETON_COUNT }, (_, i) => i + 1).map((i) => (
          <div key={i} className='bg-muted h-32 animate-pulse rounded-xl sm:h-40' />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return emptyState ?? <div className='py-12 text-center'>No items found</div>;
  }

  return (
    <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4', className)}>
      {items.map((item) => (
        <CardItemComponent
          key={item.id}
          item={item}
          cardClassName={cardClassName}
          onItemClick={onItemClick}
        />
      ))}
    </div>
  );
};

interface CardItemComponentProps {
  item: CardItem;
  cardClassName?: string | undefined;
  onItemClick?: ((item: CardItem) => void) | undefined;
}

const CardItemComponent = function CardItemComponent({
  item,
  cardClassName,
  onItemClick,
}: CardItemComponentProps) {
  const handleClick = useCallback(() => {
    if (item.onClick) {
      item.onClick();
    }
    if (onItemClick) {
      onItemClick(item);
    }
  }, [item, onItemClick]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleClick();
      }
    },
    [handleClick],
  );

  const handleActionsClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
  }, []);

  const handleActionsKeyDown = useCallback((e: React.KeyboardEvent) => {
    e.stopPropagation();
  }, []);

  return (
    <button
      type='button'
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      className={cn(
        'group relative p-4 sm:p-5 rounded-xl border border-border',
        'bg-card hover:bg-card/80 transition-all duration-200',
        'text-left min-h-[120px] sm:min-h-[140px] flex flex-col justify-between',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
        'active:scale-95 sm:active:scale-100 transition-transform',
        'hover:shadow-lg hover:border-primary/50 cursor-pointer',
        cardClassName,
      )}
    >
      {/* Top section: Title and badge */}
      <div className='mb-3 flex items-start justify-between gap-3'>
        <div className='min-w-0 flex-1'>
          <h3 className='text-foreground group-hover:text-primary truncate text-sm font-bold transition-colors sm:text-base'>
            {item.title}
          </h3>
          {item.subtitle && (
            <p className='text-muted-foreground mt-0.5 truncate text-xs sm:text-sm'>
              {item.subtitle}
            </p>
          )}
        </div>
        {item.badge && <div className='ml-2 shrink-0'>{item.badge}</div>}
      </div>

      {/* Status and priority section */}
      {(item.status ?? item.priority) && (
        <div className='mb-2 flex flex-wrap items-center gap-2'>
          {item.status && <div className='shrink-0'>{item.status}</div>}
          {item.priority && <div className='shrink-0'>{item.priority}</div>}
        </div>
      )}

      {/* Owner and metadata */}
      <div className='text-muted-foreground mb-3 flex flex-col gap-2 text-xs sm:text-sm'>
        {item.owner && <div className='flex items-center gap-2'>{item.owner}</div>}
        {item.metadata &&
          Object.entries(item.metadata).map(([key, value]) => (
            <div key={key} className='flex items-center gap-2'>
              <span className='font-medium'>{key}:</span>
              {value}
            </div>
          ))}
      </div>

      {/* Actions footer */}
      {item.actions && (
        <div
          className='border-border/30 flex items-center gap-2 border-t pt-2'
          onClick={handleActionsClick}
          onKeyDown={handleActionsKeyDown}
          role='presentation'
        >
          {item.actions}
        </div>
      )}
    </button>
  );
};
