import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

import { Breadcrumbs, PageNavigation, TableOfContents } from '../navigation';

// Mock next/link to render simple anchor tags
vi.mock('next/link', () => ({
  default: ({
    href,
    children,
    className,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

// Mock the Icon component since it relies on the sprite sheet
vi.mock('../icon-sprite', () => ({
  Icon: ({ name, size, className }: { name: string; size?: number; className?: string }) => (
    <span data-testid={`icon-${name}`} data-size={size} className={className} />
  ),
}));

describe('PageNavigation', () => {
  it('renders nothing when neither previous nor next is provided', () => {
    const { container } = render(<PageNavigation />);
    expect(container.firstChild).toBeNull();
  });

  it('renders previous link when provided', () => {
    render(<PageNavigation previous={{ title: 'Introduction', url: '/docs/intro' }} />);

    expect(screen.getByText('Introduction')).toBeInTheDocument();
    expect(screen.getByText('Previous')).toBeInTheDocument();
    const link = screen.getByText('Introduction').closest('a');
    expect(link?.getAttribute('href')).toBe('/docs/intro');
  });

  it('renders next link when provided', () => {
    render(<PageNavigation next={{ title: 'Getting Started', url: '/docs/getting-started' }} />);

    expect(screen.getByText('Getting Started')).toBeInTheDocument();
    expect(screen.getByText('Next')).toBeInTheDocument();
    const link = screen.getByText('Getting Started').closest('a');
    expect(link?.getAttribute('href')).toBe('/docs/getting-started');
  });

  it('renders both previous and next links', () => {
    render(
      <PageNavigation
        previous={{ title: 'Prev Page', url: '/prev' }}
        next={{ title: 'Next Page', url: '/next' }}
      />,
    );

    expect(screen.getByText('Prev Page')).toBeInTheDocument();
    expect(screen.getByText('Next Page')).toBeInTheDocument();
  });

  it('shows chevron-left icon for previous navigation', () => {
    render(<PageNavigation previous={{ title: 'Back', url: '/back' }} />);

    expect(screen.getByTestId('icon-chevron-left')).toBeInTheDocument();
  });

  it('shows chevron-right icon for next navigation', () => {
    render(<PageNavigation next={{ title: 'Forward', url: '/forward' }} />);

    expect(screen.getByTestId('icon-chevron-right')).toBeInTheDocument();
  });
});

describe('Breadcrumbs', () => {
  it('renders nothing when items array is empty', () => {
    const { container } = render(<Breadcrumbs items={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders breadcrumb items', () => {
    render(
      <Breadcrumbs
        items={[
          { title: 'Docs', url: '/docs' },
          { title: 'Guides', url: '/docs/guides' },
          { title: 'Quick Start' },
        ]}
      />,
    );

    expect(screen.getByText('Docs')).toBeInTheDocument();
    expect(screen.getByText('Guides')).toBeInTheDocument();
    expect(screen.getByText('Quick Start')).toBeInTheDocument();
  });

  it('renders links for items with urls', () => {
    render(<Breadcrumbs items={[{ title: 'Docs', url: '/docs' }, { title: 'Current Page' }]} />);

    const link = screen.getByText('Docs').closest('a');
    expect(link).not.toBeNull();
    expect(link?.getAttribute('href')).toBe('/docs');
  });

  it('renders span (no link) for items without url', () => {
    render(<Breadcrumbs items={[{ title: 'Current Page' }]} />);

    const element = screen.getByText('Current Page');
    expect(element.tagName.toLowerCase()).toBe('span');
  });

  it('renders separator between items', () => {
    const { container } = render(
      <Breadcrumbs
        items={[
          { title: 'A', url: '/a' },
          { title: 'B', url: '/b' },
        ]}
      />,
    );

    // Second item should have a "/" separator
    const separators = container.querySelectorAll('span');
    const slashFound = Array.from(separators).some((s) => s.textContent === '/');
    expect(slashFound).toBe(true);
  });

  it('has a nav element as root', () => {
    render(<Breadcrumbs items={[{ title: 'Test' }]} />);

    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });
});

describe('TableOfContents', () => {
  it('renders nothing when items array is empty', () => {
    const { container } = render(<TableOfContents items={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders the "On this page" heading', () => {
    render(<TableOfContents items={[{ title: 'Introduction', url: '#introduction', depth: 2 }]} />);

    expect(screen.getByText('On this page')).toBeInTheDocument();
  });

  it('renders TOC items as links', () => {
    render(
      <TableOfContents
        items={[
          { title: 'Section A', url: '#section-a', depth: 2 },
          { title: 'Section B', url: '#section-b', depth: 2 },
        ]}
      />,
    );

    const linkA = screen.getByText('Section A').closest('a');
    expect(linkA?.getAttribute('href')).toBe('#section-a');

    const linkB = screen.getByText('Section B').closest('a');
    expect(linkB?.getAttribute('href')).toBe('#section-b');
  });

  it('applies active styling to the active item', () => {
    render(
      <TableOfContents
        items={[
          { title: 'Active Section', url: '#active', depth: 2 },
          { title: 'Inactive Section', url: '#inactive', depth: 2 },
        ]}
        activeId='active'
      />,
    );

    const activeLink = screen.getByText('Active Section').closest('a');
    expect(activeLink?.className).toContain('font-medium');

    const inactiveLink = screen.getByText('Inactive Section').closest('a');
    expect(inactiveLink?.className).toContain('text-muted-foreground');
  });

  it('applies indentation based on depth', () => {
    render(
      <TableOfContents
        items={[
          { title: 'H2 Item', url: '#h2', depth: 2 },
          { title: 'H3 Item', url: '#h3', depth: 3 },
          { title: 'H4 Item', url: '#h4', depth: 4 },
        ]}
      />,
    );

    const h2Link = screen.getByText('H2 Item').closest('a');
    expect(h2Link?.className).toContain('pl-0');

    const h3Link = screen.getByText('H3 Item').closest('a');
    expect(h3Link?.className).toContain('pl-4');

    const h4Link = screen.getByText('H4 Item').closest('a');
    expect(h4Link?.className).toContain('pl-8');
  });
});
