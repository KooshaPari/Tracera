import * as React from 'react';

import type { CheckboxProps } from '@/components/ui/checkbox';

import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';

const CHECKBOX_ID_RADIX = 36;
const CHECKBOX_ID_RANDOM_LENGTH = 9;
const CHECKBOX_ID_RANDOM_START = 2;
const CHECKBOX_ID_RANDOM_END = CHECKBOX_ID_RANDOM_START + CHECKBOX_ID_RANDOM_LENGTH;

export interface FormCheckboxProps extends Omit<CheckboxProps, 'id'> {
  className?: string;
  label?: string;
  error?: boolean;
  errorMessage?: string;
  required?: boolean;
  id?: string;
}

export const FormCheckbox = React.forwardRef<HTMLInputElement, FormCheckboxProps>(
  ({ className, label, error, errorMessage, required, id, ...props }, ref) => {
    const checkboxId =
      id ??
      `checkbox-${Math.random()
        .toString(CHECKBOX_ID_RADIX)
        .slice(CHECKBOX_ID_RANDOM_START, CHECKBOX_ID_RANDOM_END)}`;
    const errorId = errorMessage ? `${checkboxId}-error` : undefined;

    return (
      <div className='flex flex-col'>
        <div className='flex items-center space-x-2'>
          <Checkbox
            ref={ref}
            id={checkboxId}
            className={cn(error && 'border-red-500', className)}
            aria-invalid={error}
            aria-describedby={errorId}
            aria-required={required}
            {...props}
          />
          {label && (
            <label
              htmlFor={checkboxId}
              className='text-sm leading-none font-medium peer-disabled:cursor-not-allowed peer-disabled:opacity-70'
            >
              {label}
              {required && (
                <span className='ml-1 text-red-500' aria-label='required'>
                  *
                </span>
              )}
            </label>
          )}
        </div>
        {errorMessage && error && (
          <span id={errorId} className='mt-1 text-sm text-red-500' role='alert'>
            {errorMessage}
          </span>
        )}
      </div>
    );
  },
);

FormCheckbox.displayName = 'FormCheckbox';
