import { memo, useEffect, useState } from 'react';

import { GraphSkeleton } from './GraphSkeleton';

interface LoadingTransitionProps {
  isLoading: boolean;
  children: React.ReactNode;
  minDisplayTime?: number;
}

export const LoadingTransition = memo(function LoadingTransition({
  isLoading,
  children,
  minDisplayTime = 300,
}: LoadingTransitionProps) {
  const [showSkeleton, setShowSkeleton] = useState(isLoading);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    if (isLoading) {
      setShowSkeleton(true);
      setFadeOut(false);
      return;
    }
    // Smooth transition: fade out skeleton before hiding
    setFadeOut(true);
    const timer = setTimeout(() => {
      setShowSkeleton(false);
    }, minDisplayTime);
    return () => {
      clearTimeout(timer);
    };
  }, [isLoading, minDisplayTime]);

  if (showSkeleton) {
    return (
      <div className={`transition-opacity duration-300 ${fadeOut ? 'opacity-0' : 'opacity-100'}`}>
        <GraphSkeleton />
      </div>
    );
  }

  return children;
});
