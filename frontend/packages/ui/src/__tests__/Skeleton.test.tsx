import { render } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Skeleton } from '../components/Skeleton';

Vitest.describe('Skeleton component', () => {
  Vitest.it('renders a div element', () => {
    const { container } = render(<Skeleton />);
    Vitest.expect(container.firstChild).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies animate-pulse class', () => {
    const { container } = render(<Skeleton />);
    Vitest.expect((container.firstChild as HTMLElement).className).toContain('animate-pulse');
  });

  Vitest.it('applies custom className', () => {
    const { container } = render(<Skeleton className='h-4 w-[200px]' />);
    const el = container.firstChild as HTMLElement;
    Vitest.expect(el.className).toContain('h-4');
    Vitest.expect(el.className).toContain('w-[200px]');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    const { container } = render(<Skeleton data-testid='skeleton' />);
    Vitest.expect(container.querySelector("[data-testid='skeleton']")).toBeInTheDocument();
  });

  Vitest.it('renders with aria attributes for accessibility', () => {
    const { container } = render(<Skeleton aria-label='Loading content' />);
    Vitest.expect(container.firstChild).toHaveAttribute('aria-label', 'Loading content');
  });
});
