import type { Metadata } from "next"
import { Inter } from "next/font/google"
import Link from "next/link"
import "./globals.css"
import { ThemeToggle } from "@/components/theme-toggle"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "TraceRTM Documentation",
  description: "Multi-View Requirements Traceability System - Official Documentation",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
            <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">TR</span>
              </div>
              <span className="font-bold text-xl">TraceRTM</span>
            </Link>
            <nav className="flex items-center gap-6">
              <Link href="/docs/wiki" className="text-sm font-medium hover:text-primary transition-colors">
                Wiki
              </Link>
              <Link href="/docs/api-reference" className="text-sm font-medium hover:text-primary transition-colors">
                API
              </Link>
              <ThemeToggle />
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t bg-muted/50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="space-y-3">
                <h3 className="font-semibold text-lg">TraceRTM</h3>
                <p className="text-sm text-muted-foreground">
                  Multi-View Requirements Traceability System
                </p>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Documentation</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><Link href="/docs/getting-started" className="hover:text-foreground transition-colors">Getting Started</Link></li>
                  <li><Link href="/docs/api-reference" className="hover:text-foreground transition-colors">API Reference</Link></li>
                  <li><Link href="/docs/wiki" className="hover:text-foreground transition-colors">Wiki</Link></li>
                </ul>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Resources</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><Link href="/docs/architecture" className="hover:text-foreground transition-colors">Architecture</Link></li>
                  <li><Link href="/docs/development" className="hover:text-foreground transition-colors">Development</Link></li>
                  <li><Link href="/docs/contributing" className="hover:text-foreground transition-colors">Contributing</Link></li>
                </ul>
              </div>
              <div className="space-y-3">
                <h4 className="font-semibold">Legal</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li><a href="#" className="hover:text-foreground transition-colors">Privacy</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">Terms</a></li>
                  <li><a href="#" className="hover:text-foreground transition-colors">License</a></li>
                </ul>
              </div>
            </div>
            <div className="mt-8 pt-8 border-t text-center text-sm text-muted-foreground">
              <p>© 2025 TraceRTM. Built with Next.js and Tailwind CSS.</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  )
}
