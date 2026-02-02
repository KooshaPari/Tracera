/* eslint-disable import/no-default-export -- Next.js App Router requires default layout export */
/* eslint-disable import/no-named-export -- Next.js requires export const metadata */
/* eslint-disable import/no-unassigned-import -- side-effect import for global styles */
/* eslint-disable react/jsx-filename-extension -- Next.js uses .tsx for layouts */
/* eslint-disable react/only-export-components -- Next.js requires export const metadata */
/* eslint-disable react-perf/jsx-no-new-object-as-prop -- rootProviderSearch is defined above */
import './global.css';
import { IconSprite } from '@/components/icon-sprite';
import { RootProvider } from 'fumadocs-ui/provider/next';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';

const inter = Inter({
  adjustFontFallback: true,
  display: 'swap',
  fallback: ['system-ui', 'arial'],
  preload: true,
  subsets: ['latin'],
  variable: '--font-inter',
});

const rootProviderSearch = {
  enabled: true,
  hotKey: [
    { ctrl: true, key: 'k' },
    { key: 'k', meta: true },
  ],
};

export default function Layout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex min-h-screen flex-col">
        <IconSprite />
        <RootProvider search={rootProviderSearch}>
          {children}
        </RootProvider>
      </body>
    </html>
  );
}

export const metadata = {
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'TracerTM Docs',
  },
  description: 'Complete documentation for the TracerTM platform',
  icons: {
    apple: '/icon-192x192.png',
    icon: '/icon-192x192.png',
  },
  manifest: '/manifest.json',
  themeColor: '#000000',
  title: {
    default: 'TracerTM Documentation',
    template: '%s | TracerTM',
  },
};
