import { useEffect, useState } from 'react';

export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof globalThis.window === 'undefined') {
      return;
    }

    const media = globalThis.matchMedia(query);

    // Set initial value
    setMatches(media.matches);

    // Create listener
    const listener = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    // Add listener
    if (media.addEventListener) {
      media.addEventListener('change', listener);
    } else {
      // Fallback for older browsers
      media.addListener(listener);
    }

    // Cleanup
    return () => {
      if (media.removeEventListener) {
        media.removeEventListener('change', listener);
      } else {
        media.removeListener(listener);
      }
    };
  }, [query]);

  return matches;
};

// Predefined breakpoint hooks
export const useIsMobile = (): boolean => useMediaQuery('(max-width: 768px)');

export const useIsTablet = (): boolean =>
  useMediaQuery('(min-width: 769px) and (max-width: 1024px)');

export const useIsDesktop = (): boolean => useMediaQuery('(min-width: 1025px)');

export const useIsDarkMode = (): boolean => useMediaQuery('(prefers-color-scheme: dark)');
