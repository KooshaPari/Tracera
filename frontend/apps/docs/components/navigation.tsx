/**
 * Navigation Components
 *
 * Enhanced navigation utilities including:
 * - Previous/Next page navigation
 * - Breadcrumb navigation
 * - Table of Contents
 */

import Link from 'next/link';

import { cn } from '@/lib/utils';

import { Icon } from './icon-sprite';

interface PageNavigationProps {
  previous?: {
    title: string;
    url: string;
  };
  next?: {
    title: string;
    url: string;
  };
}

/**
 * Previous/Next Page Navigation
 * Shows at the bottom of each documentation page
 */
export function PageNavigation({ previous, next }: PageNavigationProps) {
  if (!previous && !next) {
    return null;
  }

  return (
    <div className='grid grid-cols-1 gap-4 sm:grid-cols-2 border-t mt-12 pt-8'>
      {previous ? (
        <Link
          href={previous.url}
          className={cn(
            'flex flex-col gap-2 rounded-lg border p-4 transition-colors hover:bg-accent',
            !next && 'sm:col-span-2',
          )}
        >
          <div className='flex items-center gap-2 text-sm text-muted-foreground'>
            <Icon name='chevron-left' size={16} />
            <span>Previous</span>
          </div>
          <div className='font-medium'>{previous.title}</div>
        </Link>
      ) : (
        <div />
      )}
      {next && (
        <Link
          href={next.url}
          className='flex flex-col gap-2 rounded-lg border p-4 transition-colors hover:bg-accent'
        >
          <div className='flex items-center justify-end gap-2 text-sm text-muted-foreground'>
            <span>Next</span>
            <Icon name='chevron-right' size={16} />
          </div>
          <div className='font-medium text-right'>{next.title}</div>
        </Link>
      )}
    </div>
  );
}

interface BreadcrumbItem {
  title: string;
  url?: string;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
}

/**
 * Breadcrumb Navigation
 * Shows the current page's location in the documentation hierarchy
 */
export function Breadcrumbs({ items }: BreadcrumbsProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <nav className='flex items-center gap-2 text-sm text-muted-foreground mb-4'>
      {items.map((item, index) => (
        <div key={index} className='flex items-center gap-2'>
          {index > 0 && <span>/</span>}
          {item.url ? (
            <Link href={item.url} className='hover:text-foreground transition-colors'>
              {item.title}
            </Link>
          ) : (
            <span className='text-foreground font-medium'>{item.title}</span>
          )}
        </div>
      ))}
    </nav>
  );
}

interface TOCItem {
  title: string;
  url: string;
  depth: number;
}

interface TableOfContentsProps {
  items: TOCItem[];
  activeId?: string;
}

/**
 * Table of Contents
 * Sticky navigation showing headings on the current page
 */
export function TableOfContents({ items, activeId }: TableOfContentsProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <div className='space-y-2'>
      <p className='font-medium mb-4'>On this page</p>
      <div className='space-y-2'>
        {items.map((item) => (
          <a
            key={item.url}
            href={item.url}
            className={cn(
              'block text-sm transition-colors hover:text-foreground',
              item.depth === 2 && 'pl-0',
              item.depth === 3 && 'pl-4',
              item.depth > 3 && 'pl-8',
              activeId === item.url.slice(1)
                ? 'text-foreground font-medium'
                : 'text-muted-foreground',
            )}
          >
            {item.title}
          </a>
        ))}
      </div>
    </div>
  );
}
