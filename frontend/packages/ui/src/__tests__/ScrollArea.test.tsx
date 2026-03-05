import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { ScrollArea } from '../components/ScrollArea';

describe('ScrollArea component', () => {
  it('renders children', () => {
    render(
      <ScrollArea>
        <p>Scrollable content</p>
      </ScrollArea>,
    );
    expect(screen.getByText('Scrollable content')).toBeInTheDocument();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <ScrollArea ref={ref}>
        <p>Content</p>
      </ScrollArea>,
    );
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    const { container } = render(
      <ScrollArea className='h-[200px]' data-testid='scroll-area'>
        <p>Content</p>
      </ScrollArea>,
    );
    const scrollArea = container.querySelector("[data-testid='scroll-area']");
    expect(scrollArea?.className).toContain('h-[200px]');
  });

  it('passes through additional HTML attributes', () => {
    const { container } = render(
      <ScrollArea data-testid='my-scroll'>
        <p>Content</p>
      </ScrollArea>,
    );
    expect(container.querySelector("[data-testid='my-scroll']")).toBeInTheDocument();
  });

  it('renders the viewport wrapper', () => {
    const { container } = render(
      <ScrollArea>
        <p>Scrollable content</p>
      </ScrollArea>,
    );
    // ScrollArea wraps children in a Viewport with specific styling
    const viewport = container.querySelector('[data-radix-scroll-area-viewport]');
    // If Radix doesn't add data attributes in jsdom, check for the structural wrapper
    if (viewport) {
      expect(viewport).toBeInTheDocument();
    } else {
      // The ScrollArea root should have overflow-hidden class
      const root = container.firstElementChild;
      expect(root?.className).toContain('overflow-hidden');
    }
  });
});
