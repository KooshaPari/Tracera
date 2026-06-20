import './global.css';
import type { JSX, ReactNode } from 'react';

import { RootProvider } from 'fumadocs-ui/provider/next';
import { Inter } from 'next/font/google';

import { IconSprite } from '@/components/icon-sprite';

const inter = Inter({
  adjustFontFallback: true,
  display: 'swap',
  fallback: ['system-ui', 'arial'],
  preload: true,
  subsets: ['latin'],
  variable: '--font-inter',
});

export default function Layout({ children }: { children: ReactNode }): JSX.Element {
  return (
    <RootProvider>
      <html lang='en' className={inter.className} suppressHydrationWarning>
        <body className='flex min-h-screen flex-col'>
          <IconSprite />
          {children}
        </body>
      </html>
    </RootProvider>
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
  title: {
    default: 'TracerTM Documentation',
    template: '%s | TracerTM',
  },
};

export const viewport = {
  themeColor: '#000000',
};
