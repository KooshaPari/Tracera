import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

import { BookOpenIcon, CodeIcon, HomeIcon } from 'lucide-react';

/**
 * Shared layout configuration
 * Used by both docs and home layouts
 */
export const baseOptions: BaseLayoutProps = {
  githubUrl: 'https://github.com/yourusername/tracertm',
  links: [
    {
      active: 'nested-url',
      icon: <BookOpenIcon />,
      text: 'Documentation',
      url: '/docs',
    },
    {
      active: 'nested-url',
      icon: <CodeIcon />,
      text: 'API',
      url: '/api',
    },
    {
      icon: <HomeIcon />,
      text: 'Home',
      url: '/',
    },
  ],
  nav: {
    title: 'TracerTM',
    transparentMode: 'top',
  },
};
