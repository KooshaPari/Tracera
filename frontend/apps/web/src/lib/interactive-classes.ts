/**
 * Utility classes for interactive elements
 * Provides consistent styling and animations for clickable elements throughout the app
 */

/**
 * Base classes for clickable links (hover, active, transition)
 */
export const clickableLink =
  'cursor-pointer hover:bg-muted/50 hover:text-foreground transition-all duration-200 ease-out rounded-lg px-3 py-2 active:scale-[0.98]';

/**
 * Base classes for clickable divs/containers
 */
export const clickableContainer =
  'cursor-pointer hover:bg-muted/50 hover:shadow-md active:scale-[0.98] transition-all duration-200 ease-out rounded-lg p-4';

/**
 * Base classes for icon buttons
 */
export const iconButton =
  'cursor-pointer hover:bg-muted/50 hover:text-foreground active:scale-95 transition-all duration-150 ease-out rounded-lg p-2';

/**
 * Base classes for card with click handler (lift + shadow on hover)
 */
export const clickableCard =
  'cursor-pointer hover:shadow-lg hover:border-primary/30 hover:-translate-y-0.5 active:translate-y-0 active:scale-[0.99] transition-all duration-200 ease-out';

/**
 * Base classes for tab triggers
 */
export const tabTrigger =
  'cursor-pointer hover:bg-muted/70 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground transition-all duration-200 ease-out';

/**
 * Base classes for dropdown menu items
 */
export const dropdownMenuItem =
  'cursor-pointer hover:bg-accent hover:text-accent-foreground transition-all duration-150 ease-out active:scale-[0.98]';

/**
 * Base classes for destructive dropdown menu items
 */
export const dropdownMenuItemDestructive =
  'cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-all duration-150 ease-out text-destructive focus:text-destructive focus:bg-destructive/10 active:scale-[0.98]';

/**
 * Base classes for select items
 */
export const selectItem = 'cursor-pointer hover:bg-accent transition-colors duration-150 ease-out';

/**
 * Combine classes utility
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
