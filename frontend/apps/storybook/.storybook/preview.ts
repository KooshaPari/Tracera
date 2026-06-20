import type { Preview } from '@storybook/react';

import { themes } from '@storybook/theming';

const preview: Preview = {
  parameters: {
    a11y: {
      config: {
        rules: [
          { enabled: true, id: 'color-contrast' },
          { enabled: true, id: 'label' },
        ],
      },
    },
    actions: { argTypesRegex: '^on[A-Z].*' },
    backgrounds: {
      default: 'light',
      values: [
        { name: 'light', value: '#ffffff' },
        { name: 'dark', value: '#1a1a1a' },
      ],
    },
    controls: {
      expanded: true,
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
      sort: 'requiredFirst',
    },
    docs: {
      theme: themes.light,
    },
    themes: {
      default: 'light',
      list: [
        { class: 'light', color: '#ffffff', name: 'Light' },
        { class: 'dark', color: '#1a1a1a', name: 'Dark' },
      ],
    },
  },
  tags: ['autodocs'],
};

export default preview;
