import {
  createRootRoute,
  HeadContent,
  Outlet,
  Scripts,
} from '@tanstack/react-router'
import type { ReactNode } from 'react'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
// import { TooltipProvider } from '@tracertm/ui/components/Tooltip'
// import { Toaster } from '@tracertm/ui/components/Toaster'
import { CommandPalette } from '@/components/CommandPalette'
import '@/styles/globals.css'

interface RootComponentProps {
  children?: ReactNode
}

const RootComponent = RootComponentProps => {
  return (
    <html lang="en" className="dark">
      <head>
        <HeadContent />
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </head>
      <body className="font-sans antialiased">
        <div className="relative flex min-h-screen bg-background">
          <div className="flex-1">
            <CommandPalette />
            <Outlet />
          </div>
        </div>
        <ReactQueryDevtools initialIsOpen={false} />
        <Scripts />
      </body>
    </html>
  )
}

export const Route = createRootRoute({
  component: RootComponent,
  head: () => ({
    meta: [
      {
        charSet: 'utf-8',
      },
      {
        name: 'viewport',
        content: 'width=device-width, initial-scale=1',
      },
      {
        title: 'TraceRTM - Multi-View Requirements Traceability System',
      },
      {
        name: 'description',
        content: 'Enterprise-grade requirements traceability and project management system with 16 professional views and intelligent CRUD operations.',
      },
    ],
    links: [
      {
        rel: 'icon',
        href: '/favicon.svg',
        type: 'image/svg+xml',
      },
    ],
  }),
})
