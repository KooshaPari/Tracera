'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { ChevronRight, Home, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

/**
 * Labels for doc type segments
 */
const DOC_TYPE_LABELS: Record<string, string> = {
  user: 'User Docs',
  developer: 'Developer Docs',
  api: 'API Reference',
  sdk: 'SDK Docs',
  clients: 'Client Guides',
};

/**
 * Format a URL segment into a readable label
 */
function formatSegmentLabel(segment: string): string {
  // Check for doc type labels first
  if (DOC_TYPE_LABELS[segment]) {
    return DOC_TYPE_LABELS[segment];
  }

  // Handle numbered prefixes (e.g., "01-getting-started" -> "Getting Started")
  const withoutPrefix = segment.replace(/^\d+-/, '');

  // Convert kebab-case to Title Case
  return withoutPrefix
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

interface BreadcrumbItem {
  href: string;
  label: string;
  isLast: boolean;
}

interface DocsBreadcrumbProps {
  /** Optional page title to use for the last segment */
  pageTitle?: string;
  /** Additional CSS classes */
  className?: string;
  /** Show home icon */
  showHome?: boolean;
}

/**
 * DocsBreadcrumb - Hierarchical navigation showing current location
 *
 * Features:
 * - Auto-generates breadcrumbs from URL path
 * - Formats segment names into readable labels
 * - Supports custom page titles for last segment
 * - Responsive design with truncation
 */
export function DocsBreadcrumb({
  pageTitle,
  className,
  showHome = true,
}: DocsBreadcrumbProps) {
  const pathname = usePathname();

  // Skip if we're on the docs root
  if (pathname === '/docs' || pathname === '/docs/') {
    return null;
  }

  // Build breadcrumb items from path segments
  const segments = pathname.split('/').filter(Boolean);
  const items: BreadcrumbItem[] = segments.map((segment, index) => {
    const href = '/' + segments.slice(0, index + 1).join('/');
    const isLast = index === segments.length - 1;
    const label = isLast && pageTitle ? pageTitle : formatSegmentLabel(segment);

    return { href, label, isLast };
  });

  return (
    <nav
      className={cn(
        'flex items-center gap-1.5 text-sm text-muted-foreground',
        'overflow-x-auto scrollbar-none',
        className
      )}
      aria-label="Breadcrumb"
    >
      {/* Home Link */}
      {showHome && (
        <>
          <Link
            href="/"
            className="flex-shrink-0 hover:text-foreground transition-colors"
            aria-label="Home"
          >
            <Home className="w-4 h-4" />
          </Link>
          <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground/50" />
        </>
      )}

      {/* Breadcrumb Items */}
      {items.map((item, index) => (
        <div key={item.href} className="flex items-center gap-1.5 min-w-0">
          {index > 0 && (
            <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground/50" />
          )}

          {item.isLast ? (
            // Current page (not clickable)
            <span
              className={cn(
                'font-medium text-foreground truncate max-w-[200px]',
                'flex items-center gap-1.5'
              )}
              aria-current="page"
            >
              {item.label}
            </span>
          ) : (
            // Parent page (clickable)
            <Link
              href={item.href}
              className={cn(
                'hover:text-foreground transition-colors truncate max-w-[150px]',
                'hover:underline underline-offset-4'
              )}
            >
              {item.label}
            </Link>
          )}
        </div>
      ))}
    </nav>
  );
}

/**
 * Compact breadcrumb showing only the last two segments
 */
export function DocsBreadcrumbCompact({
  pageTitle,
  className,
}: DocsBreadcrumbProps) {
  const pathname = usePathname();
  const segments = pathname.split('/').filter(Boolean);

  if (segments.length <= 2) {
    return <DocsBreadcrumb pageTitle={pageTitle} className={className} />;
  }

  // Show "..." for collapsed segments
  const parentHref = '/' + segments.slice(0, -1).join('/');
  const parentLabel = formatSegmentLabel(segments[segments.length - 2]);
  const currentLabel = pageTitle || formatSegmentLabel(segments[segments.length - 1]);

  return (
    <nav
      className={cn('flex items-center gap-1.5 text-sm text-muted-foreground', className)}
      aria-label="Breadcrumb"
    >
      <Link
        href="/docs"
        className="hover:text-foreground transition-colors"
        aria-label="Documentation"
      >
        <FileText className="w-4 h-4" />
      </Link>
      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/50" />
      <span className="text-muted-foreground/50">...</span>
      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/50" />
      <Link
        href={parentHref}
        className="hover:text-foreground transition-colors truncate max-w-[100px]"
      >
        {parentLabel}
      </Link>
      <ChevronRight className="w-3.5 h-3.5 text-muted-foreground/50" />
      <span className="font-medium text-foreground truncate max-w-[150px]">
        {currentLabel}
      </span>
    </nav>
  );
}

export default DocsBreadcrumb;
