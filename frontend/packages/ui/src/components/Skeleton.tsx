import { cn } from '../lib/utils';

export function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>): React.ReactElement {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-muted/60 relative overflow-hidden transition-opacity duration-200 ease-out',
        'after:absolute after:inset-0 after:-translate-x-full after:animate-[shimmer_2s_infinite] after:bg-gradient-to-r after:from-transparent after:via-white/10 after:to-transparent',
        className,
      )}
      {...props}
    />
  );
}
