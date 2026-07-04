import * as React from 'react';

import { cn } from '@/lib/utils';

export interface FormFieldProps {
  label: string;
  htmlFor: string;
  error?: string;
  helpText?: string;
  required?: boolean;
  children: React.ReactNode;
  className?: string;
}

export const FormField = React.forwardRef<HTMLDivElement, FormFieldProps>(
  ({ label, htmlFor, error, helpText, required, children, className }, ref) => {
    const helpId = `${htmlFor}-help`;
    const errorId = `${htmlFor}-error`;

    return (
      <div ref={ref} className={cn('space-y-2', className)}>
        <label htmlFor={htmlFor} className='text-foreground block text-sm font-medium'>
          {label}
          {required && (
            <span className='ml-1 text-red-500' aria-label='required'>
              *
            </span>
          )}
        </label>

        {React.isValidElement(children) &&
          React.cloneElement(children, {
            'aria-describedby': error ? errorId : helpText ? helpId : undefined,
            'aria-invalid': error ? true : undefined,
            'aria-required': required ? true : undefined,
            id: htmlFor,
          } as any)}

        {error ? (
          <p
            id={errorId}
            role='alert'
            className='text-sm text-red-500'
            aria-live='polite'
            aria-atomic='true'
          >
            {error}
          </p>
        ) : helpText ? (
          <p id={helpId} className='text-muted-foreground text-xs'>
            {helpText}
          </p>
        ) : null}
      </div>
    );
  },
);

FormField.displayName = 'FormField';
