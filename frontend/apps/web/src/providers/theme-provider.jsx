import { useCallback, useEffect, useMemo, useState } from 'react';

import { ThemeContext } from './theme-context';

const resolveInitialTheme = () => {
  const stored = localStorage.getItem('theme');
  if (stored === 'light' || stored === 'dark') {
    return stored;
  }

  // Default to dark theme for geist-style aesthetic
  return 'dark';
};

const applyThemeToDom = (theme) => {
  const html = document.documentElement;
  html.classList.toggle('dark', theme === 'dark');
  localStorage.setItem('theme', theme);
};

const ThemeProvider = ({ children }) => {
  const [theme, setThemeState] = useState(resolveInitialTheme);

  useEffect(() => {
    applyThemeToDom(theme);
  }, [theme]);

  const setTheme = useCallback((newTheme) => {
    setThemeState(newTheme);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => {
      if (prev === 'light') {
        return 'dark';
      }
      return 'light';
    });
  }, []);

  const value = useMemo(
    () => ({
      isReady: true,
      setTheme,
      theme,
      toggleTheme,
    }),
    [setTheme, theme, toggleTheme],
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

export { ThemeProvider };
