'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { BookOpen, AlertCircle } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Documentation page error:', error)
  }, [error])

  return (
    <div className="flex h-screen">
      <aside className="w-80 border-r bg-muted/50 overflow-y-auto">
        <div className="sticky top-0 bg-background border-b p-4 z-10">
          <Link href="/docs" className="flex items-center gap-2 font-bold text-lg hover:opacity-75 transition-opacity">
            <BookOpen className="w-5 h-5" />
            TraceRTM Docs
          </Link>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-8">
          <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
            <AlertCircle className="w-16 h-16 text-destructive mb-4" />
            <h1 className="text-4xl font-bold mb-4">Something went wrong!</h1>
            <p className="text-lg text-muted-foreground mb-6 max-w-md">
              {error.message || 'An unexpected error occurred while loading this documentation page.'}
            </p>
            <div className="flex gap-4">
              <button
                onClick={reset}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
              >
                Try again
              </button>
              <Link
                href="/docs"
                className="px-4 py-2 border rounded-md hover:bg-muted transition-colors"
              >
                Go to documentation home
              </Link>
            </div>
            {process.env.NODE_ENV === 'development' && (
              <details className="mt-8 text-left max-w-2xl w-full">
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
      </main>
    </div>
  )
}
