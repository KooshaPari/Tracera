import { BookOpenIcon, CodeIcon, HomeIcon } from 'lucide-react';
import type { BaseLayoutProps } from 'fumadocs-ui/layouts/shared';

/**
 * Shared layout configuration
 * Used by both docs and home layouts
 */
export const baseOptions: BaseLayoutProps = {
  githubUrl: 'https://github.com/yourusername/tracertm',
  links: [
    {
      text: 'Documentation',
      url: '/docs',
      active: 'nested-url',
      icon: <BookOpenIcon />,
    },
    {
      text: 'API',
      url: '/api',
      active: 'nested-url',
      icon: <CodeIcon />,
    },
    {
      text: 'Home',
      url: '/',
      icon: <HomeIcon />,
    },
  ],
  nav: {
    title: 'TracerTM',
    transparentMode: 'top',
  },
};
