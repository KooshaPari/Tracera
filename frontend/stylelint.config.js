/** @type {import('stylelint').Config} */
export default {
  extends: ['stylelint-config-recommended', 'stylelint-config-tailwindcss'],
  ignoreFiles: [
    '**/node_modules/**',
    '**/dist/**',
    '**/.next/**',
    '**/.turbo/**',
    '**/storybook-static/**',
    '**/*.gen.*',
  ],
  rules: {
    // Allow Tailwind @tailwind, @layer, @apply
    'at-rule-no-unknown': null,
    'at-rule-prelude-no-invalid': null,
    'declaration-block-no-redundant-longhand-properties': null,
    // Prefer modern color/alpha notation where it doesn’t fight design tokens
    'alpha-value-notation': ['percentage', { exceptProperties: ['opacity'] }],
    'color-function-notation': 'modern',
    // clip is still used for .sr-only and similar patterns
    'property-no-deprecated': [true, { severity: 'warning' }],
  },
};
