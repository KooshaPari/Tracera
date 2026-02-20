'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { AlertCircle, Home } from 'lucide-react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Global application error:', error)
  }, [error])

  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen items-center justify-center bg-background p-4">
          <div className="max-w-md w-full text-center space-y-6">
            <AlertCircle className="w-16 h-16 text-destructive mx-auto" />
            <div>
              <h1 className="text-3xl font-bold mb-2">Something went wrong!</h1>
              <p className="text-muted-foreground mb-6">
                {error.message || 'An unexpected error occurred.'}
              </p>
            </div>
            <div className="flex gap-4 justify-center">
              <button
                onClick={reset}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Try again
              </button>
              <Link
                href="/"
                className="px-4 py-2 border rounded-md hover:bg-muted transition-colors inline-flex items-center gap-2"
              >
                <Home className="w-4 h-4" />
                Go home
              </Link>
            </div>
            {process.env.NODE_ENV === 'development' && (
              <details className="text-left">
                <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground">
                  Error details (development only)
                </summary>
                <pre className="mt-4 p-4 bg-muted rounded-md overflow-auto text-xs">
                  {error.stack || error.toString()}
                </pre>
              </details>
            )}
          </div>
        </div>
      </body>
    </html>
  )
}
