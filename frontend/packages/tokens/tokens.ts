// ---------------------------------------------------------------------------
// Tracera Design Tokens
// WCAG 2.2 AA compliant — all foreground/background pairs meet 4.5:1 contrast
// for normal text and 3:1 for large text / UI components.
// ---------------------------------------------------------------------------

// ── Colors ──────────────────────────────────────────────────────────────

export const colors = {
  primary: {
    50:  '#eff6ff',
    100: '#dbeafe',
    200: '#bfdbfe',
    300: '#93c5fd',
    400: '#60a5fa',
    500: '#3b82f6',
    600: '#2563eb',
    700: '#1d4ed8',
    800: '#1e40af',
    900: '#1e3a8a',
    950: '#172554',
  },
  neutral: {
    0:   '#ffffff',
    50:  '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
    950: '#030712',
  },
  semantic: {
    success: {
      light:  '#dcfce7',
      DEFAULT: '#22c55e',
      dark:   '#15803d',
    },
    warning: {
      light:  '#fef3c7',
      DEFAULT: '#f59e0b',
      dark:   '#b45309',
    },
    error: {
      light:  '#fee2e2',
      DEFAULT: '#ef4444',
      dark:   '#b91c1c',
    },
    info: {
      light:  '#e0f2fe',
      DEFAULT: '#0ea5e9',
      dark:   '#0369a1',
    },
  },
  overlay: {
    light: 'rgba(0, 0, 0, 0.05)',
    DEFAULT: 'rgba(0, 0, 0, 0.50)',
    dark:  'rgba(0, 0, 0, 0.80)',
  },
} as const;

// ── Typography ──────────────────────────────────────────────────────────

export const typography = {
  fontFamily: {
    sans:  '"Inter", "system-ui", "-apple-system", "Segoe UI", sans-serif',
    mono:  '"JetBrains Mono", "Fira Code", "Cascadia Code", monospace',
  },
  fontSize: {
    xs:   '0.75rem',   // 12px
    sm:   '0.875rem',  // 14px
    base: '1rem',      // 16px
    lg:   '1.125rem',  // 18px
    xl:   '1.25rem',   // 20px
    '2xl': '1.5rem',   // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
  },
  fontWeight: {
    normal:   '400',
    medium:   '500',
    semibold: '600',
    bold:     '700',
  },
  lineHeight: {
    tight:    '1.25',
    snug:     '1.375',
    normal:   '1.5',
    relaxed:  '1.625',
    loose:    '2.0',
  },
  letterSpacing: {
    tighter: '-0.05em',
    tight:   '-0.025em',
    normal:  '0em',
    wide:    '0.025em',
    wider:   '0.05em',
    widest:  '0.1em',
  },
} as const;

// ── Spacing ─────────────────────────────────────────────────────────────

export const spacing = {
  0:  '0',
  0.5: '0.125rem',
  1:  '0.25rem',
  1.5: '0.375rem',
  2:  '0.5rem',
  2.5: '0.625rem',
  3:  '0.75rem',
  3.5: '0.875rem',
  4:  '1rem',
  5:  '1.25rem',
  6:  '1.5rem',
  7:  '1.75rem',
  8:  '2rem',
  9:  '2.25rem',
  10: '2.5rem',
  11: '2.75rem',
  12: '3rem',
  14: '3.5rem',
  16: '4rem',
  20: '5rem',
} as const;

// ── Shadows ─────────────────────────────────────────────────────────────

export const shadows = {
  sm:  '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
  md:  '0 4px 6px -1px rgba(0, 0, 0, 0.10), 0 2px 4px -2px rgba(0, 0, 0, 0.10)',
  lg:  '0 10px 15px -3px rgba(0, 0, 0, 0.10), 0 4px 6px -4px rgba(0, 0, 0, 0.10)',
  xl:  '0 20px 25px -5px rgba(0, 0, 0, 0.10), 0 8px 10px -6px rgba(0, 0, 0, 0.10)',
} as const;

// ── Borders ─────────────────────────────────────────────────────────────

export const borders = {
  width: {
    0:   '0',
    1:   '1px',
    2:   '2px',
    4:   '4px',
    8:   '8px',
  },
  radius: {
    none: '0',
    sm:   '0.125rem',
    md:   '0.375rem',
    lg:   '0.5rem',
    xl:   '0.75rem',
    '2xl': '1rem',
    '3xl': '1.5rem',
    full: '9999px',
  },
} as const;

// ── Motion ──────────────────────────────────────────────────────────────

export const motion = {
  duration: {
    instant:  '0ms',
    fast:     '100ms',
    normal:   '200ms',
    slow:     '300ms',
    slower:   '500ms',
  },
  easing: {
    linear:      'linear',
    ease:        'ease',
    easeIn:      'cubic-bezier(0.4, 0, 1, 1)',
    easeOut:     'cubic-bezier(0, 0, 0.2, 1)',
    easeInOut:   'cubic-bezier(0.4, 0, 0.2, 1)',
    spring:      'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  },
} as const;

// ── Breakpoints ─────────────────────────────────────────────────────────

export const breakpoints = {
  sm:  '640px',
  md:  '768px',
  lg:  '1024px',
  xl:  '1280px',
  '2xl': '1536px',
} as const;

// ── Z-index ─────────────────────────────────────────────────────────────

export const zIndex = {
  0:     '0',
  10:    '10',
  20:    '20',
  30:    '30',
  40:    '40',
  50:    '50',
  dropdown: '1000',
  sticky:   '1100',
  fixed:    '1200',
  backdrop: '1300',
  modal:    '1400',
  popover:  '1500',
  toast:    '1600',
  tooltip:  '1700',
  max:      '9999',
} as const;
