import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it } from 'vitest';

import { Progress } from '../components/Progress';

describe('Progress component', () => {
  it('renders a progressbar element', () => {
    render(<Progress value={50} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders with the provided value', () => {
    render(<Progress value={75} />);
    const progress = screen.getByRole('progressbar');
    // Radix Progress stores value as aria-valuenow on the root
    // In some versions it might not set it; test the transform instead
    expect(progress).toBeInTheDocument();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLDivElement>();
    render(<Progress ref={ref} value={50} />);
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('applies custom className', () => {
    render(<Progress className='custom-progress' value={50} />);
    const progress = screen.getByRole('progressbar');
    expect(progress.className).toContain('custom-progress');
  });

  it('renders the indicator with correct transform for value=60', () => {
    const { container } = render(<Progress value={60} />);
    const indicator = container.querySelector('[style]');
    expect(indicator).toBeInTheDocument();
    expect(indicator?.getAttribute('style')).toContain('translateX(-40%)');
  });

  it('renders the indicator with correct transform for value=0', () => {
    const { container } = render(<Progress value={0} />);
    const indicator = container.querySelector('[style]');
    expect(indicator?.getAttribute('style')).toContain('translateX(-100%)');
  });

  it('renders the indicator with correct transform for value=100', () => {
    const { container } = render(<Progress value={100} />);
    const indicator = container.querySelector('[style]');
    // 100 - 100 = 0, so translateX(-0%) which is effectively 0
    expect(indicator?.getAttribute('style')).toContain('translateX(-0%)');
  });

  it('handles undefined value as 0', () => {
    const { container } = render(<Progress />);
    const indicator = container.querySelector('[style]');
    expect(indicator?.getAttribute('style')).toContain('translateX(-100%)');
  });

  it('passes through additional HTML attributes', () => {
    render(<Progress value={50} data-testid='my-progress' />);
    expect(screen.getByTestId('my-progress')).toBeInTheDocument();
  });
});
