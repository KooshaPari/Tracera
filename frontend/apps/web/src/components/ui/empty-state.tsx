/**
 * Empty State Component
 *
 * Displays a friendly message when no data is available.
 * Includes icon, title, description, and optional action buttons.
 */

import type { LucideIcon } from 'lucide-react';

import { motion } from 'framer-motion';
import { AlertCircle, FilterX, Inbox, SearchX } from 'lucide-react';
import * as React from 'react';

import { cn } from '@/lib/utils';

/**
 * Empty State Props
 */
export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Icon component to display */
  icon: LucideIcon;

  /** Main title text */
  title: string;

  /** Description/subtitle text */
  description: string;

  /** Action button configurations */
  actions?: EmptyStateAction[] | undefined;

  /** Optional icon size (default: "md") */
  iconSize?: 'sm' | 'md' | 'lg' | undefined;

  /** Animate in on mount */
  animate?: boolean | undefined;

  /** Illustration variant (default: "default") */
  variant?: 'default' | 'compact' | 'full' | undefined;

  /** Show subtle background pattern */
  showPattern?: boolean | undefined;

  /** Additional helpers text below actions */
  helpText?: string | undefined;
}

/**
 * Empty State Action Button Config
 */
export interface EmptyStateAction {
  /** Button label */
  label: string;

  /** Button variant */
  variant?: 'default' | 'outline' | 'ghost' | undefined;

  /** Icon to display in button */
  icon?: React.ReactNode | undefined;

  /** Click handler */
  onClick: () => void;

  /** Disabled state */
  disabled?: boolean | undefined;

  /** Loading state */
  loading?: boolean | undefined;
}

const iconSizeMap = {
  lg: 'h-24 w-24',
  md: 'h-16 w-16',
  sm: 'h-12 w-12',
};

/**
 * Empty State Component
 *
 * Usage:
 * ```tsx
 * <EmptyState
 *   icon={InboxIcon}
 *   title="No items yet"
 *   description="Create your first item to get started"
 *   actions={[
 *     { label: "Create Item", onClick: () => {} }
 *   ]}
 * />
 * ```
 */
const EmptyState = React.forwardRef<HTMLDivElement, EmptyStateProps>(
  (
    {
      icon: Icon,
      title,
      description,
      actions,
      iconSize = 'md',
      animate = true,
      variant = 'default',
      showPattern = true,
      helpText,
      className,
      ...props
    },
    ref,
  ) => {
    const containerVariants = {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          delayChildren: 0.2,
          staggerChildren: 0.1,
        },
      },
    };

    const itemVariants = {
      hidden: { opacity: 0, y: 16 },
      visible: {
        opacity: 1,
        transition: { damping: 24, stiffness: 300, type: 'spring' },
        y: 0,
      },
    };

    const variantClasses = {
      compact: 'py-8 px-4',
      default: 'py-12 px-4',
      full: 'py-20 px-6',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'relative flex flex-col items-center justify-center text-center',
          variantClasses[variant],
          className,
        )}
        {...props}
      >
        {/* Background pattern */}
        {showPattern && (
          <div className='pointer-events-none absolute inset-0 overflow-hidden'>
            <div className='via-primary/[0.02] absolute inset-0 bg-gradient-to-b from-transparent to-transparent' />
            <div className='via-primary/10 absolute top-0 right-0 left-0 h-px bg-gradient-to-r from-transparent to-transparent' />
          </div>
        )}

        {/* Content */}
        <motion.div
          className='relative w-full max-w-sm'
          variants={containerVariants}
          initial={animate ? 'hidden' : 'visible'}
          animate='visible'
        >
          {/* Icon */}
          <motion.div variants={itemVariants} className='mb-4 flex justify-center'>
            <div className='relative'>
              {/* Icon glow */}
              <div className='bg-primary/20 absolute inset-0 rounded-full opacity-0 blur-xl transition-opacity group-hover:opacity-100' />

              <Icon
                className={cn(
                  'relative text-muted-foreground/60 dark:text-muted-foreground/50',
                  iconSizeMap[iconSize],
                )}
                strokeWidth={1.5}
              />
            </div>
          </motion.div>

          {/* Title */}
          <motion.h3 variants={itemVariants} className='text-foreground mb-2 text-lg font-semibold'>
            {title}
          </motion.h3>

          {/* Description */}
          <motion.p variants={itemVariants} className='text-muted-foreground mb-6 text-sm'>
            {description}
          </motion.p>

          {/* Actions */}
          {actions && actions.length > 0 && (
            <motion.div
              variants={itemVariants}
              className='mb-4 flex flex-col justify-center gap-3 sm:flex-row'
            >
              {actions.map((action, index) => (
                <EmptyStateButton
                  key={index}
                  action={action}
                  variant={action.variant ?? (index === 0 ? 'default' : 'outline')}
                />
              ))}
            </motion.div>
          )}

          {/* Help text */}
          {helpText && (
            <motion.p variants={itemVariants} className='text-muted-foreground/70 mt-4 text-xs'>
              {helpText}
            </motion.p>
          )}
        </motion.div>
      </div>
    );
  },
);

EmptyState.displayName = 'EmptyState';

/**
 * Empty State Button Component
 */
const EmptyStateButton: React.FC<{
  action: EmptyStateAction;
  variant: 'default' | 'outline' | 'ghost';
}> = ({ action, variant }) => {
  const variantClasses = {
    default:
      'px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/90 rounded-md text-sm font-medium transition-colors',
    ghost: 'px-4 py-2 hover:bg-muted rounded-md text-sm font-medium transition-colors',
    outline:
      'px-4 py-2 border border-input bg-background hover:bg-accent rounded-md text-sm font-medium transition-colors',
  };

  return (
    <motion.button
      onClick={action.onClick}
      disabled={action.disabled ?? action.loading}
      className={cn(
        variantClasses[variant],
        'disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 justify-center',
      )}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {action.loading ? (
        <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
      ) : (
        action.icon && <span>{action.icon}</span>
      )}
      {action.label}
    </motion.button>
  );
};

/**
 * Specialized Empty State variants
 */

export interface NoItemsEmptyStateProps extends Omit<
  EmptyStateProps,
  'icon' | 'title' | 'description'
> {
  /** Type of items */
  itemType?: string | undefined;
}

export const NoItemsEmptyState = React.forwardRef<HTMLDivElement, NoItemsEmptyStateProps>(
  ({ itemType = 'items', actions, ...props }, ref) => (
    <EmptyState
      ref={ref}
      icon={Inbox}
      title={`No ${itemType} yet`}
      description={`Create your first ${itemType.toLowerCase()} to get started`}
      actions={actions}
      {...props}
    />
  ),
);

NoItemsEmptyState.displayName = 'NoItemsEmptyState';

export interface NoSearchResultsEmptyStateProps extends Omit<
  EmptyStateProps,
  'icon' | 'title' | 'description'
> {
  /** Search query that returned no results */
  query: string;
}

export const NoSearchResultsEmptyState = React.forwardRef<
  HTMLDivElement,
  NoSearchResultsEmptyStateProps
>(({ query, ...props }, ref) => (
  <EmptyState
    ref={ref}
    icon={SearchX}
    title='No results found'
    description={`We couldn't find any matches for "${query}". Try adjusting your search terms.`}
    {...props}
  />
));

NoSearchResultsEmptyState.displayName = 'NoSearchResultsEmptyState';

export interface FilteredEmptyStateProps extends Omit<
  EmptyStateProps,
  'icon' | 'title' | 'description'
> {
  /** Applied filters */
  filters: string[];
}

export const FilteredEmptyState = React.forwardRef<HTMLDivElement, FilteredEmptyStateProps>(
  ({ filters, ...props }, ref) => (
    <EmptyState
      ref={ref}
      icon={FilterX}
      title='No items match your filters'
      description={`No results found for: ${filters.join(', ')}. Try removing or adjusting your filters.`}
      {...props}
    />
  ),
);

FilteredEmptyState.displayName = 'FilteredEmptyState';

export interface ErrorEmptyStateProps extends Omit<EmptyStateProps, 'icon' | 'title'> {
  /** Error message to display */
  error: string;
}

export const ErrorEmptyState = React.forwardRef<HTMLDivElement, ErrorEmptyStateProps>(
  ({ error, description: _desc, ...props }, ref) => (
    <EmptyState
      ref={ref}
      icon={AlertCircle}
      title='Something went wrong'
      description={error}
      {...props}
    />
  ),
);

ErrorEmptyState.displayName = 'ErrorEmptyState';

export { EmptyState, EmptyStateButton };
