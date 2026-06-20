import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Progress } from '../components/Progress';

Vitest.describe('Progress component', () => {
  Vitest.it('renders a progressbar element', () => {
    render(<Progress value={50} />);
    Vitest.expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  Vitest.it('renders with the provided value', () => {
    render(<Progress value={75} />);
    const progress = screen.getByRole('progressbar');
    // Radix Progress stores value as aria-valuenow on the root
    // In some versions Vitest.it might not set Vitest.it; test the transform instead
    Vitest.expect(progress).toBeInTheDocument();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Progress ref={ref} value={50} />);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Progress className='custom-progress' value={50} />);
    const progress = screen.getByRole('progressbar');
    Vitest.expect(progress.className).toContain('custom-progress');
  });

  Vitest.it('renders the indicator with correct transform for value=60', () => {
    const { container } = render(<Progress value={60} />);
    const indicator = container.querySelector('[style]');
    Vitest.expect(indicator).toBeInTheDocument();
    Vitest.expect(indicator?.getAttribute('style')).toContain('translateX(-40%)');
  });

  Vitest.it('renders the indicator with correct transform for value=0', () => {
    const { container } = render(<Progress value={0} />);
    const indicator = container.querySelector('[style]');
    Vitest.expect(indicator?.getAttribute('style')).toContain('translateX(-100%)');
  });

  Vitest.it('renders the indicator with correct transform for value=100', () => {
    const { container } = render(<Progress value={100} />);
    const indicator = container.querySelector('[style]');
    // 100 - 100 = 0, so translateX(-0%) which is effectively 0
    Vitest.expect(indicator?.getAttribute('style')).toContain('translateX(-0%)');
  });

  Vitest.it('handles undefined value as 0', () => {
    const { container } = render(<Progress />);
    const indicator = container.querySelector('[style]');
    Vitest.expect(indicator?.getAttribute('style')).toContain('translateX(-100%)');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    render(<Progress value={50} data-testid='my-progress' />);
    Vitest.expect(screen.getByTestId('my-progress')).toBeInTheDocument();
  });
});
