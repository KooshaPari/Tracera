import { render } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Skeleton } from '../components/Skeleton';

describe('Skeleton', () => {
  it('renders a div element', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toBeInstanceOf(HTMLDivElement);
  });

  it('applies animate-pulse class', () => {
    const { container } = render(<Skeleton />);
    expect((container.firstChild as HTMLElement).className).toContain('animate-pulse');
  });

  it('applies custom className', () => {
    const { container } = render(<Skeleton className='h-4 w-[200px]' />);
    const el = container.firstChild as HTMLElement;
    expect(el.className).toContain('h-4');
    expect(el.className).toContain('w-[200px]');
  });

  it('passes through additional HTML attributes', () => {
    const { container } = render(<Skeleton data-testid='skeleton' />);
    expect(container.querySelector("[data-testid='skeleton']")).toBeInTheDocument();
  });

  it('renders with aria attributes for accessibility', () => {
    const { container } = render(<Skeleton aria-label='Loading content' />);
    expect(container.firstChild).toHaveAttribute('aria-label', 'Loading content');
  });
});
