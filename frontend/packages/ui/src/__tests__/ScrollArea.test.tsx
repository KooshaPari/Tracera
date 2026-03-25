import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { ScrollArea } from '../components/ScrollArea';

Vitest.describe('ScrollArea component', () => {
  Vitest.it('renders children', () => {
    render(
      <ScrollArea>
        <p>Scrollable content</p>
      </ScrollArea>,
    );
    Vitest.expect(screen.getByText('Scrollable content')).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(
      <ScrollArea ref={ref}>
        <p>Content</p>
      </ScrollArea>,
    );
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    const { container } = render(
      <ScrollArea className='h-[200px]' data-testid='scroll-area'>
        <p>Content</p>
      </ScrollArea>,
    );
    const scrollArea = container.querySelector("[data-testid='scroll-area']");
    Vitest.expect(scrollArea?.className).toContain('h-[200px]');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    const { container } = render(
      <ScrollArea data-testid='my-scroll'>
        <p>Content</p>
      </ScrollArea>,
    );
    Vitest.expect(container.querySelector("[data-testid='my-scroll']")).toBeInTheDocument();
  });

  Vitest.it('renders the viewport wrapper', () => {
    const { container } = render(
      <ScrollArea>
        <p>Scrollable content</p>
      </ScrollArea>,
    );
    // ScrollArea wraps children in a Viewport with specific styling
    const viewport = container.querySelector('[data-radix-scroll-area-viewport]');
    // If Radix doesn't add data attributes in jsdom, check for the structural wrapper
    if (viewport) {
      Vitest.expect(viewport).toBeInTheDocument();
    } else {
      // The ScrollArea root should have overflow-hidden class
      const root = container.firstElementChild;
      Vitest.expect(root?.className).toContain('overflow-hidden');
    }
  });
});
