import { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowRight, LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CardProps {
  title: string;
  description?: string;
  href?: string;
  icon?: LucideIcon;
  children?: ReactNode;
  className?: string;
}

/**
 * Card - Display content in a card format
 *
 * Features:
 * - Optional link wrapper
 * - Optional icon
 * - Hover effects
 * - Dark mode support
 */
export function Card({
  title,
  description,
  href,
  icon: Icon,
  children,
  className,
}: CardProps) {
  const content = (
    <>
      <div className="flex items-start gap-3">
        {Icon && (
          <div className="p-2 rounded-lg bg-primary/10 text-primary">
            <Icon className="w-5 h-5" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-base mb-1 flex items-center gap-2">
            {title}
            {href && (
              <ArrowRight className="w-4 h-4 opacity-0 -translate-x-2 group-hover:opacity-100 group-hover:translate-x-0 transition-all" />
            )}
          </h3>
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      </div>
      {children && <div className="mt-3">{children}</div>}
    </>
  );

  if (href) {
    return (
      <Link
        href={href}
        className={cn(
          'block p-4 rounded-lg border bg-card hover:bg-accent transition-colors group',
          className
        )}
      >
        {content}
      </Link>
    );
  }

  return (
    <div
      className={cn(
        'p-4 rounded-lg border bg-card',
        className
      )}
    >
      {content}
    </div>
  );
}

interface CardsProps {
  children: ReactNode;
  cols?: 1 | 2 | 3 | 4;
  className?: string;
}

/**
 * Cards - Grid container for Card components
 */
export function Cards({ children, cols = 2, className }: CardsProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={cn('grid gap-4 my-4', gridCols[cols], className)}>
      {children}
    </div>
  );
}
