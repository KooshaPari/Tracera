import { ChevronDown } from 'lucide-react';
import * as React from 'react';

import { cn } from '../lib/utils';

interface CollapsibleProps extends Omit<React.HTMLAttributes<HTMLDivElement>, 'onOpenChange'> {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

interface CollapsibleChildProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

const Collapsible = React.forwardRef<HTMLDivElement, CollapsibleProps>(
  ({ open = false, onOpenChange, children, className, ...props }, ref) => (
    <div ref={ref} className={cn('space-y-2', className)} {...props}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as React.ReactElement<CollapsibleChildProps>, {
            ...(onOpenChange !== undefined && { onOpenChange }),
            open,
          });
        }
        return child;
      })}
    </div>
  ),
);

Collapsible.displayName = 'Collapsible';

interface CollapsibleTriggerProps extends Omit<
  React.ButtonHTMLAttributes<HTMLButtonElement>,
  'onOpenChange'
> {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

const CollapsibleTrigger = React.forwardRef<HTMLButtonElement, CollapsibleTriggerProps>(
  ({ open = false, onOpenChange, children, className, ...props }, ref) => {
    const handleClick = React.useCallback(() => {
      onOpenChange?.(!open);
    }, [onOpenChange, open]);

    return (
      <button
        ref={ref}
        type='button'
        onClick={handleClick}
        className={cn('w-full flex items-center justify-between transition-all', className)}
        {...props}
      >
        <div className='flex flex-1 items-center gap-2'>{children}</div>
        <ChevronDown
          className={cn(
            'h-3 w-3 text-muted-foreground transition-transform duration-200 shrink-0',
            open && 'rotate-180',
          )}
        />
      </button>
    );
  },
);

CollapsibleTrigger.displayName = 'CollapsibleTrigger';

interface CollapsibleContentProps extends Omit<
  React.HTMLAttributes<HTMLDivElement>,
  'onOpenChange'
> {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
  className?: string;
}

const CollapsibleContent = React.forwardRef<HTMLDivElement, CollapsibleContentProps>(
  ({ open = false, onOpenChange: _onOpenChange, children, className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'overflow-hidden transition-all duration-200',
        open ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0',
        className,
      )}
      {...props}
    >
      {open && children}
    </div>
  ),
);

CollapsibleContent.displayName = 'CollapsibleContent';

export { Collapsible, CollapsibleTrigger, CollapsibleContent };
