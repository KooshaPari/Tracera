import type { ContextType } from 'react';

import { useContext } from 'react';

import { ThemeContext } from './theme-context';

type ThemeContextType = ContextType<typeof ThemeContext>;

const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (!context.isReady) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export { useTheme };
