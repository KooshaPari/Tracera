import type { Preview } from '@storybook/react';

import '../src/index.css';

const preview: Preview = {
  decorators: [
    (Story) => (
      <div className='min-h-screen bg-white dark:bg-slate-950'>
        <Story />
      </div>
    ),
  ],
  parameters: {
    actions: { argTypesRegex: '^on[A-Z].*' },
    a11y: {
      config: {
        rules: [
          { enabled: true, id: 'color-contrast' },
          { enabled: true, id: 'label' },
        ],
      },
    },
    chromatic: {
      delay: 300,
      modes: {
        dark: {
          matcherUrl: '**/dark',
          query: "[data-theme='dark']",
        },
        light: {
          matcherUrl: '**/light',
          query: "[data-theme='light']",
        },
      },
      pauseAnimationAtEnd: true,
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    layout: 'fullscreen',
    themes: {
      default: 'light',
      list: [
        { class: 'light', color: '#ffffff', name: 'Light' },
        { class: 'dark', color: '#0f172a', name: 'Dark' },
      ],
    },
    viewport: {
      viewports: {
        desktop: {
          name: 'Desktop',
          styles: {
            height: '900px',
            width: '1440px',
          },
        },
        mobile: {
          name: 'Mobile',
          styles: {
            height: '667px',
            width: '375px',
          },
        },
        tablet: {
          name: 'Tablet',
          styles: {
            height: '1024px',
            width: '768px',
          },
        },
      },
    },
  },
};

export default preview;
