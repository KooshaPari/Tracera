import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock fumadocs DocsLayout
vi.mock('fumadocs-ui/layouts/docs', () => ({
  DocsLayout: ({ children, tree, ...rest }: any) => (
    <div data-testid='docs-layout' data-tree={JSON.stringify(tree)}>
      {children}
    </div>
  ),
}));

// Mock source
vi.mock('@/source', () => ({
  source: {
    pageTree: [
      { name: 'Getting Started', url: '/docs/getting-started' },
      { name: 'Guides', url: '/docs/guides' },
    ],
  },
}));

// Mock layout.config
vi.mock('@/app/layout.config', () => ({
  baseOptions: {
    nav: { title: 'TracerTM' },
    links: [],
  },
}));

import DocsLayoutComponent from '@/app/docs/layout';

describe('DocsLayout', () => {
  it('renders children within DocsLayout', () => {
    render(
      <DocsLayoutComponent>
        <div>Page content</div>
      </DocsLayoutComponent>,
    );
    expect(screen.getByText('Page content')).toBeInTheDocument();
  });

  it('wraps in the fumadocs DocsLayout component', () => {
    render(
      <DocsLayoutComponent>
        <div>Content</div>
      </DocsLayoutComponent>,
    );
    expect(screen.getByTestId('docs-layout')).toBeInTheDocument();
  });

  it('passes the page tree to the DocsLayout', () => {
    render(
      <DocsLayoutComponent>
        <div>Content</div>
      </DocsLayoutComponent>,
    );
    const layout = screen.getByTestId('docs-layout');
    const tree = JSON.parse(layout.getAttribute('data-tree')!);
    expect(tree).toHaveLength(2);
    expect(tree[0].name).toBe('Getting Started');
  });
});
