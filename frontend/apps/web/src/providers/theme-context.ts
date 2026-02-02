import { createContext } from "react";

export type Theme = "light" | "dark";

export interface ThemeContextType {
	theme: Theme;
	setTheme: (theme: Theme) => void;
	toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

export default ThemeContext;
