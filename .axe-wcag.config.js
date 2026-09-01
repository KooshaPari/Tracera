// ---------------------------------------------------------------------------
// axe-core configuration for WCAG 2.2 AA auditing.
// Used by both the CLI (`axe`) and the programmatic API.
// ---------------------------------------------------------------------------

module.exports = {
  // Tags to enforce — WCAG 2.2 Level AA.
  runOnly: {
    type: 'tag',
    values: [
      'wcag2a',
      'wcag2aa',
      'wcag21a',
      'wcag21aa',
      'wcag22aa',
      'best-practice',
    ],
  },

  // Rules to explicitly disable (with documented reason).
  rules: {
    // Landmark landmarks are best-practice, not mandatory.
    'landmark-banner-is-top-level': { enabled: true },
    'landmark-contentinfo-is-top-level': { enabled: true },
    'landmark-main-is-top-level': { enabled: true },
    'landmark-no-duplicate-banner': { enabled: true },
    'landmark-one-main': { enabled: true },

    // Colour-contrast is the primary AA rule — always on.
    'color-contrast': { enabled: true },

    // We enforce our own link-name rules via linting.
    'link-name': { enabled: true },
  },

  // Selectors to exclude from auditing (e.g. third-party widgets).
  exclude: [
    '[data-axe-ignore]',
    '.third-party-widget',
  ],

  // Result types to report.
  resultTypes: ['violations', 'incomplete'],

  // Prefix for axe IDs when using the reporter.
  reporter: 'v2',
};
