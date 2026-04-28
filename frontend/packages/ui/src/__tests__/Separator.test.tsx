import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Separator } from '../components/Separator';

Vitest.describe('Separator component', () => {
  Vitest.it('renders with role=separator', () => {
    render(<Separator />);
    Vitest.expect(screen.getByRole('separator')).toBeInTheDocument();
  });

  Vitest.it('defaults to horizontal orientation', () => {
    render(<Separator />);
    const sep = screen.getByRole('separator');
    Vitest.expect(sep).toHaveAttribute('aria-orientation', 'horizontal');
  });

  Vitest.it('supports vertical orientation', () => {
    render(<Separator orientation='vertical' />);
    const sep = screen.getByRole('separator');
    Vitest.expect(sep).toHaveAttribute('aria-orientation', 'vertical');
  });

  Vitest.it('applies horizontal classes by default', () => {
    render(<Separator />);
    const sep = screen.getByRole('separator');
    Vitest.expect(sep.className).toContain('w-full');
  });

  Vitest.it('applies vertical classes when vertical', () => {
    render(<Separator orientation='vertical' />);
    const sep = screen.getByRole('separator');
    Vitest.expect(sep.className).toContain('h-full');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Separator ref={ref} />);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Separator className='my-separator' />);
    Vitest.expect(screen.getByRole('separator').className).toContain('my-separator');
  });
});
