import * as React from 'react';

import { cn } from '@/lib/utils';
import { Textarea } from '@tracertm/ui';

export interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const FormTextarea = React.forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ className, error, ...props }, ref) => (
    <Textarea
      ref={ref}
      className={cn(error && 'border-red-500 focus-visible:ring-red-500', className)}
      {...props}
    />
  ),
);

FormTextarea.displayName = 'FormTextarea';
