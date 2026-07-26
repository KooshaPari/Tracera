import { cn } from '@tracertm/ui';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  fullScreen?: boolean;
  text?: string;
}

const sizeClasses = {
  lg: 'w-12 h-12 border-3',
  md: 'w-8 h-8 border-2',
  sm: 'w-4 h-4 border-2',
  xl: 'w-16 h-16 border-4',
};

export const LoadingSpinner = function LoadingSpinner({
  size = 'md',
  className,
  fullScreen = false,
  text,
}: LoadingSpinnerProps) {
  const spinner = (
    <div className='flex flex-col items-center justify-center gap-3'>
      <div
        className={cn(
          'animate-spin rounded-full border-gray-200 dark:border-gray-800 border-t-primary-600 dark:border-t-primary-400',
          sizeClasses[size],
          className,
        )}
      />
      {text && <p className='text-sm text-gray-600 dark:text-gray-400'>{text}</p>}
    </div>
  );

  if (fullScreen) {
    return (
      <div className='fixed inset-0 z-50 flex items-center justify-center bg-white/80 backdrop-blur-sm dark:bg-gray-900/80'>
        {spinner}
      </div>
    );
  }

  return spinner;
};
