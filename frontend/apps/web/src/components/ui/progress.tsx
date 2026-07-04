import * as ProgressPrimitive from '@radix-ui/react-progress';
import * as React from 'react';
import { useMemo } from 'react';

import { cn } from '@/lib/utils';

const PROGRESS_MAX = 100;

const Progress = React.forwardRef<
  React.ComponentRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
>(({ className, value, ...props }, ref) => {
  const indicatorStyle = useMemo(
    () => ({
      transform: `translateX(-${PROGRESS_MAX - (value ?? 0)}%)`,
    }),
    [value],
  );
  return (
    <ProgressPrimitive.Root
      ref={ref}
      className={cn('relative h-4 w-full overflow-hidden rounded-full bg-secondary', className)}
      {...props}
    >
      <ProgressPrimitive.Indicator
        className='bg-primary h-full w-full flex-1 transition-all'
        style={indicatorStyle}
      />
    </ProgressPrimitive.Root>
  );
});
Progress.displayName = ProgressPrimitive.Root.displayName;

export { Progress };
