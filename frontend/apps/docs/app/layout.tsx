import './global.css';
import { RootProvider } from 'fumadocs-ui/provider/next';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';
import { IconSprite } from '@/components/icon-sprite';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  preload: true,
  fallback: ['system-ui', 'arial'],
  adjustFontFallback: true,
});

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body className="flex min-h-screen flex-col">
        <IconSprite />
        <RootProvider
          search={{
            enabled: true,
            hotKey: [
              {
                key: 'k',
                ctrl: true,
              },
              {
                key: 'k',
                meta: true,
              },
            ],
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}

export const metadata = {
  title: {
    default: 'TracerTM Documentation',
    template: '%s | TracerTM',
  },
  description: 'Complete documentation for the TracerTM platform',
  manifest: '/manifest.json',
  themeColor: '#000000',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'TracerTM Docs',
  },
  icons: {
    icon: '/icon-192x192.png',
    apple: '/icon-192x192.png',
  },
};
