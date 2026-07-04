import * as React from 'react';

import { cn } from '@/lib/utils';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@tracertm/ui';

export interface FormSelectOption {
  label: string;
  value: string;
}

export interface FormSelectProps {
  value: string | undefined;
  onValueChange: ((value: string) => void) | undefined;
  options: FormSelectOption[];
  placeholder?: string;
  error?: boolean;
  disabled?: boolean;
  className?: string;
  name?: string;
  id?: string;
  'aria-describedby'?: string;
  'aria-invalid'?: boolean;
  'aria-required'?: boolean;
}

export const FormSelect = React.forwardRef<HTMLButtonElement, FormSelectProps>(
  (
    {
      value,
      onValueChange,
      options,
      placeholder = 'Select an option',
      error,
      disabled,
      className,
      ...ariaProps
    },
    ref,
  ) => {
    const selectProps: {
      value?: string;
      onValueChange?: (value: string) => void;
      disabled?: boolean;
    } = {};

    if (value !== undefined) {
      selectProps.value = value;
    }
    if (onValueChange !== undefined) {
      selectProps.onValueChange = onValueChange;
    }
    if (disabled !== undefined) {
      selectProps.disabled = disabled;
    }

    return (
      <Select {...selectProps}>
        <SelectTrigger
          ref={ref}
          className={cn(error && 'border-red-500 focus:ring-red-500', className)}
          {...ariaProps}
        >
          <SelectValue placeholder={placeholder} />
        </SelectTrigger>
        <SelectContent>
          {options.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    );
  },
);

FormSelect.displayName = 'FormSelect';
