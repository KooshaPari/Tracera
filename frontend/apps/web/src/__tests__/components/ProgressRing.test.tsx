import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, expect, it } from 'vitest';

import { LinearProgress, ProgressBar, ProgressRing } from '../../components/temporal/ProgressRing';

describe(ProgressRing, () => {
  it('renders with correct percentage', () => {
    const { container } = render(<ProgressRing percentage={50} />);
    const circles = container.querySelectorAll('circle');
    expect(circles.length).toBeGreaterThan(0);
  });

  it('displays percentage label', () => {
    render(<ProgressRing percentage={75} showLabel />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('hides label when showLabel is false', () => {
    render(<ProgressRing percentage={75} showLabel={false} />);
    expect(screen.queryByText('75%')).not.toBeInTheDocument();
  });

  it('renders with small size', () => {
    const { container } = render(<ProgressRing percentage={50} size='sm' />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('renders with medium size', () => {
    const { container } = render(<ProgressRing percentage={50} size='md' />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('renders with large size', () => {
    const { container } = render(<ProgressRing percentage={50} size='lg' />);
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('applies correct color based on percentage', () => {
    const { container: highContainer } = render(<ProgressRing percentage={80} />);
    const { container: mediumContainer } = render(<ProgressRing percentage={50} />);
    const { container: lowContainer } = render(<ProgressRing percentage={25} />);

    // All should render without errors
    expect(highContainer.querySelector('circle')).toBeInTheDocument();
    expect(mediumContainer.querySelector('circle')).toBeInTheDocument();
    expect(lowContainer.querySelector('circle')).toBeInTheDocument();
  });

  it('accepts custom color', () => {
    const { container } = render(<ProgressRing percentage={50} color='#ff0000' />);
    expect(container.querySelector('circle')).toBeInTheDocument();
  });

  it('rounds percentage correctly', () => {
    render(<ProgressRing percentage={75.6} showLabel />);
    expect(screen.getByText('76%')).toBeInTheDocument();
  });

  it('handles 0% progress', () => {
    render(<ProgressRing percentage={0} showLabel />);
    expect(screen.getByText('0%')).toBeInTheDocument();
  });

  it('handles 100% progress', () => {
    render(<ProgressRing percentage={100} showLabel />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});

describe(ProgressBar, () => {
  it('renders progress bar', () => {
    const { container } = render(<ProgressBar percentage={50} />);
    expect(container.querySelector('.h-2')).toBeInTheDocument();
  });

  it('displays label with percentage', () => {
    render(<ProgressBar percentage={60} showLabel />);
    expect(screen.getByText('60%')).toBeInTheDocument();
  });

  it('hides label when showLabel is false', () => {
    render(<ProgressBar percentage={60} showLabel={false} />);
    expect(screen.queryByText('60%')).not.toBeInTheDocument();
  });

  it('applies correct height classes', () => {
    const { container: smContainer } = render(<ProgressBar percentage={50} height='sm' />);
    const { container: mdContainer } = render(<ProgressBar percentage={50} height='md' />);
    const { container: lgContainer } = render(<ProgressBar percentage={50} height='lg' />);

    expect(smContainer.querySelector('.h-1')).toBeInTheDocument();
    expect(mdContainer.querySelector('.h-2')).toBeInTheDocument();
    expect(lgContainer.querySelector('.h-3')).toBeInTheDocument();
  });

  it('applies color based on percentage', () => {
    const { container: highContainer } = render(<ProgressBar percentage={80} />);
    const { container: lowContainer } = render(<ProgressBar percentage={20} />);

    expect(highContainer.innerHTML).toContain('green');
    expect(lowContainer.innerHTML).toContain('red');
  });

  it('applies custom color', () => {
    const { container } = render(<ProgressBar percentage={50} color='bg-purple-500' />);
    expect(container.innerHTML).toContain('purple');
  });

  it('handles 0% progress', () => {
    const { container } = render(<ProgressBar percentage={0} />);
    const progressDiv = container.querySelector('div > div');
    expect(progressDiv).toHaveStyle('width: 0%');
  });

  it('handles 100% progress', () => {
    const { container } = render(<ProgressBar percentage={100} />);
    const progressDiv = container.querySelector('div > div');
    expect(progressDiv).toHaveStyle('width: 100%');
  });

  it('caps percentage at 100', () => {
    render(<ProgressBar percentage={150} showLabel />);
    expect(screen.getByText('100%')).toBeInTheDocument();
  });

  it('handles animation prop', () => {
    const { rerender } = render(<ProgressBar percentage={50} animated />);
    expect(screen.getByText('50%')).toBeInTheDocument();

    rerender(<ProgressBar percentage={75} animated={false} />);
    expect(screen.getByText('75%')).toBeInTheDocument();
  });
});

describe(LinearProgress, () => {
  it('renders with label', () => {
    render(<LinearProgress value={5} max={10} label='Progress' />);
    expect(screen.getByText('Progress')).toBeInTheDocument();
  });

  it('displays value and max', () => {
    render(<LinearProgress value={5} max={10} label='Progress' showLabel />);
    expect(screen.getByText('5/10')).toBeInTheDocument();
  });

  it('calculates correct percentage', () => {
    render(<LinearProgress value={5} max={10} label='Progress' showLabel />);
    expect(screen.getByText('5/10')).toBeInTheDocument();
  });

  it('renders without label', () => {
    render(<LinearProgress value={5} max={10} showLabel={false} />);
    expect(screen.queryByText('5/10')).not.toBeInTheDocument();
  });

  it('handles zero progress', () => {
    render(<LinearProgress value={0} max={10} label='Empty' showLabel />);
    expect(screen.getByText('Empty')).toBeInTheDocument();
    expect(screen.getByText('0/10')).toBeInTheDocument();
  });

  it('handles complete progress', () => {
    render(<LinearProgress value={10} max={10} label='Complete' showLabel />);
    expect(screen.getByText('Complete')).toBeInTheDocument();
    expect(screen.getByText('10/10')).toBeInTheDocument();
  });

  it('applies custom color', () => {
    const { container } = render(<LinearProgress value={5} max={10} color='bg-red-500' />);
    expect(container.innerHTML).toContain('red');
  });
});
