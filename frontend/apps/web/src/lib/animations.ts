/**
 * Animation and transition utility class names for consistent effects site-wide.
 * Use with Tailwind; respects prefers-reduced-motion via global CSS.
 */

/** Page/section entrance: fade in and slide up */
export const animateInFadeUp = 'animate-in-fade-up';

/** Page/section entrance: fade in only */
export const animateInFade = 'animate-in-fade';

/** Card/section entrance: scale in */
export const animateInScale = 'animate-in-scale';

/** Stagger children (list items, cards) - use on parent */
export const staggerChildren = 'stagger-children';

/** Interactive hover/active: lift and shadow (cards, list rows) */
export const interactiveCard =
  'transition-all duration-200 ease-out hover:shadow-md hover:-translate-y-0.5 hover:border-primary/20 active:translate-y-0 active:scale-[0.99]';

/** Interactive hover/active: subtle background (buttons, nav items) */
export const interactiveSoft =
  'transition-all duration-150 ease-out hover:bg-accent/80 active:bg-accent';

/** Nav link / sidebar item: hover and active state */
export const navLink =
  'transition-all duration-150 ease-out hover:bg-accent/80 hover:text-accent-foreground rounded-md active:scale-[0.98]';

/** Tab trigger style transitions */
export const tabTrigger = 'transition-all duration-200 ease-out data-[state=active]:shadow-sm';
