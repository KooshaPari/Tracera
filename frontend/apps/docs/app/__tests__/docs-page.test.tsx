import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock notFound
const mockNotFound = vi.fn();
vi.mock('next/navigation', () => ({
  notFound: () => {
    mockNotFound();
    throw new Error('NEXT_NOT_FOUND');
  },
}));

// Mock fumadocs page components
vi.mock('fumadocs-ui/page', () => ({
  DocsPage: ({ children, toc, full }: any) => (
    <div data-testid='docs-page' data-toc={JSON.stringify(toc)} data-full={String(full)}>
      {children}
    </div>
  ),
  DocsTitle: ({ children }: any) => <h1 data-testid='docs-title'>{children}</h1>,
  DocsDescription: ({ children }: any) => <p data-testid='docs-description'>{children}</p>,
  DocsBody: ({ children }: any) => <div data-testid='docs-body'>{children}</div>,
}));

// Mock mdx-components
vi.mock('@/components/mdx-components', () => ({
  mdxComponents: { p: 'p', h1: 'h1' },
}));

// Mock source
const mockGetPage = vi.fn();
const mockGenerateParams = vi
  .fn()
  .mockReturnValue([{ slug: ['getting-started'] }, { slug: ['guides', 'deployment'] }]);

vi.mock('@/source', () => ({
  source: {
    getPage: (...args: any[]) => mockGetPage(...args),
    generateParams: () => mockGenerateParams(),
  },
}));

import { render, screen } from '@testing-library/react';

// Import using the @ alias to avoid the [[...slug]] path issue
import Page, { generateStaticParams, generateMetadata } from '@/app/docs/[[...slug]]/page';

describe('Docs Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders page title and description when page exists', async () => {
    const mockMDX = ({ components }: any) => <div data-testid='mdx-content'>MDX Content</div>;
    mockGetPage.mockReturnValue({
      url: '/docs/getting-started',
      data: {
        title: 'Getting Started',
        description: 'Learn how to get started',
        body: mockMDX,
        toc: [],
        full: false,
        info: { path: 'getting-started.mdx' },
        structuredData: {},
      },
    });

    const Component = await Page({ params: Promise.resolve({ slug: ['getting-started'] }) });
    render(Component);

    expect(screen.getByTestId('docs-title')).toHaveTextContent('Getting Started');
    expect(screen.getByTestId('docs-description')).toHaveTextContent('Learn how to get started');
    expect(screen.getByTestId('mdx-content')).toBeInTheDocument();
  });

  it('calls notFound when page does not exist', async () => {
    mockGetPage.mockReturnValue(null);

    try {
      await Page({ params: Promise.resolve({ slug: ['nonexistent'] }) });
      // Should not reach here
      expect.unreachable('Expected notFound to throw');
    } catch (error) {
      expect(mockNotFound).toHaveBeenCalled();
      expect((error as Error).message).toBe('NEXT_NOT_FOUND');
    }
  });

  it('passes toc data to DocsPage', async () => {
    const tocItems = [{ title: 'Introduction', url: '#intro', depth: 2 }];
    const mockMDX = () => <div>Content</div>;
    mockGetPage.mockReturnValue({
      url: '/docs/test',
      data: {
        title: 'Test',
        description: '',
        body: mockMDX,
        toc: tocItems,
        full: true,
        info: { path: 'test.mdx' },
        structuredData: {},
      },
    });

    const Component = await Page({ params: Promise.resolve({ slug: ['test'] }) });
    render(Component);

    const docsPage = screen.getByTestId('docs-page');
    expect(JSON.parse(docsPage.getAttribute('data-toc')!)).toEqual(tocItems);
  });

  it('uses full=false as default when page.data.full is undefined', async () => {
    const mockMDX = () => <div>Content</div>;
    mockGetPage.mockReturnValue({
      url: '/docs/test',
      data: {
        title: 'Test',
        description: '',
        body: mockMDX,
        toc: [],
        info: { path: 'test.mdx' },
      },
    });

    const Component = await Page({ params: Promise.resolve({ slug: ['test'] }) });
    render(Component);

    const docsPage = screen.getByTestId('docs-page');
    expect(docsPage.getAttribute('data-full')).toBe('false');
  });
});

describe('generateStaticParams', () => {
  it('returns params from source.generateParams', async () => {
    const params = await generateStaticParams();
    expect(params).toEqual([{ slug: ['getting-started'] }, { slug: ['guides', 'deployment'] }]);
  });
});

describe('generateMetadata', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns metadata with title and description', async () => {
    mockGetPage.mockReturnValue({
      url: '/docs/test',
      data: {
        title: 'Test Page',
        description: 'A test page description',
      },
    });

    const meta = await generateMetadata({ params: Promise.resolve({ slug: ['test'] }) });

    expect(meta.title).toBe('Test Page');
    expect(meta.description).toBe('A test page description');
    expect(meta.openGraph?.title).toBe('Test Page');
    expect(meta.openGraph?.type).toBe('article');
    expect((meta as any).twitter?.card).toBe('summary_large_image');
  });

  it('uses empty string for missing description in openGraph', async () => {
    mockGetPage.mockReturnValue({
      url: '/docs/test',
      data: {
        title: 'Title Only',
        description: undefined,
      },
    });

    const meta = await generateMetadata({ params: Promise.resolve({ slug: ['test'] }) });

    expect(meta.openGraph?.description).toBe('');
    expect((meta as any).twitter?.description).toBe('');
  });

  it('calls notFound when page does not exist', async () => {
    mockGetPage.mockReturnValue(null);

    try {
      await generateMetadata({ params: Promise.resolve({ slug: ['missing'] }) });
      expect.unreachable('Expected notFound to throw');
    } catch (error) {
      expect(mockNotFound).toHaveBeenCalled();
      expect((error as Error).message).toBe('NEXT_NOT_FOUND');
    }
  });
});
