import * as React from 'react';

import { cn } from '@/lib/utils';
import { Input } from '@tracertm/ui';

export interface FormInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
  errorMessage?: string;
  required?: boolean;
}

export const FormInput = React.forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, error, errorMessage, required, ...props }, ref) => {
    const errorId = errorMessage ? `${props.id ?? 'input'}-error` : undefined;

    return (
      <>
        <Input
          ref={ref}
          className={cn(error && 'border-red-500 focus-visible:ring-red-500', className)}
          aria-invalid={error}
          aria-describedby={errorId}
          aria-required={required}
          {...props}
        />
        {errorMessage && error && (
          <span id={errorId} className='mt-1 block text-sm text-red-500' role='alert'>
            {errorMessage}
          </span>
        )}
      </>
    );
  },
);

FormInput.displayName = 'FormInput';
