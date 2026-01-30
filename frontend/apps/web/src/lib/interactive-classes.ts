/**
 * Utility classes for interactive elements
 * Provides consistent styling for clickable elements throughout the app
 */

/**
 * Base classes for clickable links
 */
export const clickableLink =
	"cursor-pointer hover:bg-muted/50 hover:text-foreground transition-colors rounded-lg px-3 py-2";

/**
 * Base classes for clickable divs/containers
 */
export const clickableContainer =
	"cursor-pointer hover:bg-muted/50 hover:shadow-md active:scale-[0.98] transition-all duration-200 rounded-lg p-4";

/**
 * Base classes for icon buttons
 */
export const iconButton =
	"cursor-pointer hover:bg-muted/50 hover:text-foreground active:bg-muted transition-colors rounded-lg p-2";

/**
 * Base classes for card with click handler
 */
export const clickableCard =
	"cursor-pointer hover:shadow-lg hover:border-primary/30 transition-all duration-200";

/**
 * Base classes for tab triggers
 */
export const tabTrigger =
	"cursor-pointer hover:bg-muted/70 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-colors";

/**
 * Base classes for dropdown menu items
 */
export const dropdownMenuItem =
	"cursor-pointer hover:bg-accent hover:text-accent-foreground transition-colors";

/**
 * Base classes for destructive dropdown menu items
 */
export const dropdownMenuItemDestructive =
	"cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors text-destructive focus:text-destructive focus:bg-destructive/10";

/**
 * Base classes for select items
 */
export const selectItem = "cursor-pointer hover:bg-accent";

/**
 * Combine classes utility
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
	return classes.filter(Boolean).join(" ");
}
