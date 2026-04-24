import type { ReactNode } from 'react';

import React from 'react';

import { cn } from '@/lib/utils';

interface MobileFormLayoutProps {
  children: ReactNode;
  className?: string;
  title?: string;
  description?: string;
}

/**
 * Mobile-optimized form layout that stacks all fields vertically
 * with increased touch targets and optimized spacing
 */
export const MobileFormLayout = function MobileFormLayout({
  children,
  className,
  title,
  description,
}: MobileFormLayoutProps) {
  return (
    <div className={cn('mx-auto w-full px-4 sm:px-6 py-6 sm:py-8', 'max-w-2xl', className)}>
      {title && (
        <div className='mb-6 sm:mb-8'>
          <h1 className='text-foreground text-xl font-bold sm:text-2xl'>{title}</h1>
          {description && (
            <p className='text-muted-foreground mt-2 text-sm sm:text-base'>{description}</p>
          )}
        </div>
      )}
      <form className='space-y-4 sm:space-y-5'>{children}</form>
    </div>
  );
};

interface FormFieldProps {
  label?: string;
  error?: string;
  required?: boolean;
  children: ReactNode;
  helperText?: string;
  className?: string;
}

/**
 * Form field wrapper that ensures proper spacing and touch targets
 */
export const FormField = function FormField({
  label,
  error,
  required,
  children,
  helperText,
  className,
}: FormFieldProps) {
  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <label className='text-foreground block text-sm font-semibold sm:text-base'>
          {label}
          {required && <span className='text-destructive ml-1'>*</span>}
        </label>
      )}

      {/* Input wrapper - ensures minimum 44px height */}
      <div className='relative'>{children}</div>

      {error && <p className='text-destructive text-xs font-medium sm:text-sm'>{error}</p>}

      {helperText && <p className='text-muted-foreground text-xs sm:text-sm'>{helperText}</p>}
    </div>
  );
};

interface FormGroupProps {
  children: ReactNode;
  columns?: '1' | '2';
  className?: string;
}

/**
 * Groups multiple form fields together
 * Stacks on mobile, can arrange in columns on larger screens
 */
export const FormGroup = function FormGroup({
  children,
  columns = '1',
  className,
}: FormGroupProps) {
  const gridClass = {
    '1': 'grid-cols-1',
    '2': 'grid-cols-1 sm:grid-cols-2',
  }[columns];

  return <div className={cn(`grid ${gridClass} gap-4 sm:gap-5`, className)}>{children}</div>;
};

interface FormActionsProps {
  children: ReactNode;
  className?: string;
  justify?: 'start' | 'end' | 'center' | 'between';
  stacked?: boolean;
}

/**
 * Actions footer for forms with proper spacing and touch targets
 * Buttons are full-width on mobile
 */
export const FormActions = function FormActions({
  children,
  className,
  justify = 'end',
  stacked = false,
}: FormActionsProps) {
  const justifyClass = {
    between: 'justify-between',
    center: 'justify-center',
    end: 'justify-end',
    start: 'justify-start',
  }[justify];

  return (
    <div
      className={cn(
        'pt-4 sm:pt-6 border-t border-border/30',
        stacked
          ? 'flex flex-col sm:flex-row gap-3 sm:gap-4'
          : `flex ${justifyClass} gap-3 sm:gap-4`,
        className,
      )}
    >
      {children}
    </div>
  );
};

interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  isMobile?: boolean;
}

/**
 * Mobile-optimized input with minimum 44px height
 */
export const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, isMobile = true, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'w-full px-4 py-3 sm:py-3 rounded-lg',
        'bg-background border border-border',
        'text-sm sm:text-base',
        'placeholder:text-muted-foreground',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-all duration-200',
        isMobile && 'min-h-[44px]',
        className,
      )}
      {...props}
    />
  ),
);

FormInput.displayName = 'FormInput';

interface FormSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  isMobile?: boolean;
}

/**
 * Mobile-optimized select with minimum 44px height
 */
export const FormSelect = React.forwardRef<HTMLSelectElement, FormSelectProps>(
  ({ className, isMobile = true, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        'w-full px-4 py-3 rounded-lg',
        'bg-background border border-border',
        'text-sm sm:text-base',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-all duration-200',
        isMobile && 'min-h-[44px]',
        className,
      )}
      {...props}
    />
  ),
);

FormSelect.displayName = 'FormSelect';

interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  isMobile?: boolean;
}

/**
 * Mobile-optimized textarea
 */
export const FormTextarea = React.forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ className, isMobile = true, ...props }, ref) => (
    <textarea
      ref={ref}
      className={cn(
        'w-full px-4 py-3 rounded-lg',
        'bg-background border border-border',
        'text-sm sm:text-base',
        'placeholder:text-muted-foreground',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'transition-all duration-200',
        'resize-vertical min-h-[120px] sm:min-h-[140px]',
        isMobile && 'min-h-[44px]',
        className,
      )}
      {...props}
    />
  ),
);

FormTextarea.displayName = 'FormTextarea';
