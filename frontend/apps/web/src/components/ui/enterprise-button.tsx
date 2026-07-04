/**
 * Enterprise Button Component
 *
 * Professional button with subtle animations, loading states, and micro-interactions
 * Matches enterprise applications like Salesforce, Jira, Linear
 */

import type { VariantProps } from 'class-variance-authority';

import { Slot } from '@radix-ui/react-slot';
import { cva } from 'class-variance-authority';
import { motion } from 'framer-motion';
import * as React from 'react';

import { cn } from '@/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    defaultVariants: {
      size: 'default',
      variant: 'default',
    },
    variants: {
      size: {
        default: 'h-10 px-4 py-2',
        icon: 'h-10 w-10',
        lg: 'h-11 rounded-md px-8',
        sm: 'h-9 rounded-md px-3',
        xl: 'h-13 rounded-lg px-10 text-base',
        xs: 'h-7 rounded px-2 text-xs',
      },
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'text-primary underline-offset-4 hover:underline',

        // Enterprise variants
        enterprise:
          'bg-gradient-to-r from-primary to-primary/90 text-primary-foreground shadow-sm hover:from-primary/90 hover:to-primary/80 hover:shadow-md',
        success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500',
        warning: 'bg-amber-600 text-white hover:bg-amber-700 focus:ring-amber-500',
        info: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500',
      },
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  loading?: boolean;
  success?: boolean;
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  ripple?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      asChild = false,
      loading = false,
      success = false,
      iconLeft,
      iconRight,
      ripple = true,
      children,
      disabled,
      ...props
    },
    ref,
  ) => {
    const Comp = asChild ? Slot : motion.button;

    return (
      <Comp
        className={cn(
          buttonVariants({ className, size, variant }),
          loading && 'relative overflow-hidden',
          success && variant === 'default' && 'bg-green-600 hover:bg-green-700',
          'cursor-pointer',
        )}
        ref={ref}
        disabled={disabled ?? loading}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        transition={{ damping: 17, stiffness: 400, type: 'spring' }}
        {...(props.style ? { style: props.style } : {})}
        {...(Object.fromEntries(Object.entries(props).filter(([key]) => key !== 'style')) as any)}
      >
        {/* Ripple effect */}
        {ripple && !loading && !success && (
          <span className='pointer-events-none absolute inset-0 overflow-hidden rounded-md'>
            <span className='absolute inset-0 -translate-x-full -skew-x-12 transform bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 transition-opacity duration-300 hover:translate-x-full hover:opacity-100' />
          </span>
        )}

        {/* Loading state */}
        {loading && (
          <motion.div
            className='absolute inset-0 flex items-center justify-center rounded-md bg-black/10'
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className='h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent' />
          </motion.div>
        )}

        {/* Success state */}
        {success && (
          <motion.div
            className='absolute inset-0 flex items-center justify-center rounded-md bg-green-500/10'
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, type: 'spring' }}
          >
            <svg
              className='h-5 w-5 text-green-600'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <motion.path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M5 13l4 4L19 7'
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.2, duration: 0.3 }}
              />
            </svg>
          </motion.div>
        )}

        {/* Content */}
        <span className={cn('flex items-center gap-2', loading && 'opacity-0')}>
          {iconLeft}
          {children}
          {iconRight}
        </span>
      </Comp>
    );
  },
);

Button.displayName = 'Button';

// Enterprise button group
export interface ButtonGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  variant?: 'default' | 'segmented' | 'toolbar';
  size?: 'default' | 'sm' | 'lg';
}

export const ButtonGroup = React.forwardRef<HTMLDivElement, ButtonGroupProps>(
  ({ children, variant = 'default', size: _size = 'default', className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'inline-flex',
        {
          // Default vertical grouping
          'flex-col': variant === 'default',
          // Segmented horizontal buttons
          'items-center rounded-md shadow-sm': variant === 'segmented',
          // ToolBar spacing
          'items-center gap-1': variant === 'toolbar',
        },
        className,
      )}
      {...props}
    >
      {variant === 'segmented' &&
        React.Children.map(children, (child, index) => {
          if (React.isValidElement(child)) {
            const childProps = child.props as { className?: string };
            return React.cloneElement(child, {
              className: cn(
                index === 0 && 'rounded-l-md rounded-r-none',
                index === React.Children.count(children) - 1 && 'rounded-r-md rounded-l-none',
                index !== 0 && index !== React.Children.count(children) - 1 && 'rounded-none',
                childProps.className,
              ),
            } as any);
          }
          return child;
        })}
      {variant !== 'segmented' && children}
    </div>
  ),
);

ButtonGroup.displayName = 'ButtonGroup';

// Toolbar button with keyboard shortcuts
export interface ToolbarButtonProps extends Omit<ButtonProps, 'size'> {
  shortcut?: string;
  tooltip?: string;
}

export const ToolbarButton = React.forwardRef<HTMLButtonElement, ToolbarButtonProps>(
  ({ shortcut, tooltip, children, className, ...props }, ref) => (
    <Button
      ref={ref}
      size='sm'
      variant='ghost'
      className={cn('h-8 px-3 group relative', className)}
      {...props}
    >
      <div className='flex items-center gap-2'>
        {children}
        {shortcut && (
          <kbd className='text-muted-foreground bg-muted hidden items-center rounded px-1.5 py-0.5 font-mono text-xs md:inline-flex'>
            {shortcut}
          </kbd>
        )}
      </div>

      {tooltip && (
        <div className='pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 rounded bg-black/80 px-2 py-1 text-xs whitespace-nowrap text-white opacity-0 transition-opacity group-hover:opacity-100'>
          {tooltip}
          <div className='absolute top-full left-1/2 -mt-px -translate-x-1/2'>
            <div className='border-4 border-transparent border-t-black/80' />
          </div>
        </div>
      )}
    </Button>
  ),
);

ToolbarButton.displayName = 'ToolbarButton';

export { Button, buttonVariants };
export default Button;
