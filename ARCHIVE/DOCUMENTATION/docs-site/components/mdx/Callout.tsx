import { ReactNode } from 'react';
import {
  Info,
  AlertTriangle,
  AlertCircle,
  Lightbulb,
  CheckCircle,
  MessageSquare,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Callout types with their visual configurations
 */
type CalloutType = 'info' | 'warning' | 'error' | 'tip' | 'success' | 'note';

interface CalloutConfig {
  icon: typeof Info;
  className: string;
  borderClassName: string;
  defaultTitle: string;
}

const calloutConfig: Record<CalloutType, CalloutConfig> = {
  info: {
    icon: Info,
    className: 'bg-blue-50 dark:bg-blue-950/30 text-blue-900 dark:text-blue-100',
    borderClassName: 'border-l-blue-500',
    defaultTitle: 'Info',
  },
  warning: {
    icon: AlertTriangle,
    className: 'bg-yellow-50 dark:bg-yellow-950/30 text-yellow-900 dark:text-yellow-100',
    borderClassName: 'border-l-yellow-500',
    defaultTitle: 'Warning',
  },
  error: {
    icon: AlertCircle,
    className: 'bg-red-50 dark:bg-red-950/30 text-red-900 dark:text-red-100',
    borderClassName: 'border-l-red-500',
    defaultTitle: 'Error',
  },
  tip: {
    icon: Lightbulb,
    className: 'bg-green-50 dark:bg-green-950/30 text-green-900 dark:text-green-100',
    borderClassName: 'border-l-green-500',
    defaultTitle: 'Tip',
  },
  success: {
    icon: CheckCircle,
    className: 'bg-emerald-50 dark:bg-emerald-950/30 text-emerald-900 dark:text-emerald-100',
    borderClassName: 'border-l-emerald-500',
    defaultTitle: 'Success',
  },
  note: {
    icon: MessageSquare,
    className: 'bg-muted text-muted-foreground',
    borderClassName: 'border-l-muted-foreground',
    defaultTitle: 'Note',
  },
};

interface CalloutProps {
  /** Type of callout - determines icon and styling */
  type?: CalloutType;
  /** Optional custom title */
  title?: string;
  /** Show title or just icon */
  showTitle?: boolean;
  /** Content of the callout */
  children: ReactNode;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Callout - Highlighted information box for documentation
 *
 * Usage in MDX:
 * ```mdx
 * <Callout type="info">
 *   This is an informational message.
 * </Callout>
 *
 * <Callout type="warning" title="Breaking Change">
 *   This API has been deprecated.
 * </Callout>
 * ```
 */
export function Callout({
  type = 'info',
  title,
  showTitle = true,
  children,
  className,
}: CalloutProps) {
  const config = calloutConfig[type];
  const Icon = config.icon;
  const displayTitle = title || (showTitle ? config.defaultTitle : null);

  return (
    <div
      className={cn(
        'my-6 rounded-lg border-l-4 p-4',
        config.className,
        config.borderClassName,
        className
      )}
      role="note"
      aria-label={displayTitle || config.defaultTitle}
    >
      <div className="flex gap-3">
        <Icon
          className={cn(
            'w-5 h-5 mt-0.5 flex-shrink-0',
            type === 'info' && 'text-blue-500',
            type === 'warning' && 'text-yellow-500',
            type === 'error' && 'text-red-500',
            type === 'tip' && 'text-green-500',
            type === 'success' && 'text-emerald-500',
            type === 'note' && 'text-muted-foreground'
          )}
          aria-hidden="true"
        />
        <div className="flex-1 min-w-0">
          {displayTitle && (
            <div className="font-semibold mb-1 text-current">{displayTitle}</div>
          )}
          <div
            className={cn(
              'text-sm prose-sm max-w-none',
              '[&>p]:m-0 [&>p:first-child]:mt-0',
              '[&>ul]:my-2 [&>ol]:my-2',
              '[&>pre]:my-2'
            )}
          >
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Pre-configured callout variants for convenience
 */
export function InfoCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="info" title={title} {...props}>{children}</Callout>;
}

export function WarningCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="warning" title={title} {...props}>{children}</Callout>;
}

export function ErrorCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="error" title={title} {...props}>{children}</Callout>;
}

export function TipCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="tip" title={title} {...props}>{children}</Callout>;
}

export function SuccessCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="success" title={title} {...props}>{children}</Callout>;
}

export function NoteCallout({ children, title, ...props }: Omit<CalloutProps, 'type'>) {
  return <Callout type="note" title={title} {...props}>{children}</Callout>;
}

export default Callout;
