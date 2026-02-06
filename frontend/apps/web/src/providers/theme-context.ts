import { createContext } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  isReady: boolean;
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

const createNoop = (): void => {};

const DEFAULT_THEME_CONTEXT: ThemeContextType = {
  isReady: false,
  setTheme: createNoop,
  theme: 'light',
  toggleTheme: createNoop,
};

const ThemeContext = createContext<ThemeContextType>(DEFAULT_THEME_CONTEXT);

export { ThemeContext };
