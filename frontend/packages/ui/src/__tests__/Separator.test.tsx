import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Separator } from '../components/Separator';

describe('Separator component', () => {
  it('renders with role=separator', () => {
    render(<Separator />);
    expect(screen.getByRole('separator')).toBeInTheDocument();
  });

  it('defaults to horizontal orientation', () => {
    render(<Separator />);
    const sep = screen.getByRole('separator');
    expect(sep).toHaveAttribute('aria-orientation', 'horizontal');
  });

  it('supports vertical orientation', () => {
    render(<Separator orientation='vertical' />);
    const sep = screen.getByRole('separator');
    expect(sep).toHaveAttribute('aria-orientation', 'vertical');
  });

  it('applies horizontal classes by default', () => {
    render(<Separator />);
    const sep = screen.getByRole('separator');
    expect(sep.className).toContain('w-full');
  });

  it('applies vertical classes when vertical', () => {
    render(<Separator orientation='vertical' />);
    const sep = screen.getByRole('separator');
    expect(sep.className).toContain('h-full');
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Separator ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    render(<Separator className='my-separator' />);
    expect(screen.getByRole('separator').className).toContain('my-separator');
  });
});
