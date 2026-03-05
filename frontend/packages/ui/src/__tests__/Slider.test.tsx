import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Slider } from '../components/Slider';

describe('Slider component', () => {
  it('renders a slider root element', () => {
    const { container } = render(<Slider value={[50]} />);
    const root = container.firstChild as HTMLElement;
    expect(root).toBeInTheDocument();
    expect(root.getAttribute('data-orientation')).toBe('horizontal');
  });

  it('renders the track and range elements', () => {
    const { container } = render(<Slider value={[50]} />);
    // Track is the bg-secondary element
    const track = container.querySelector("[data-orientation='horizontal']");
    expect(track).toBeInTheDocument();
  });

  it('applies custom className to the root', () => {
    const { container } = render(<Slider className='custom-slider' value={[50]} />);
    const root = container.firstChild as HTMLElement;
    expect(root.className).toContain('custom-slider');
  });

  it('renders thumb elements with role=slider (hidden in jsdom)', () => {
    render(<Slider value={[50]} />);
    // Radix Slider thumbs are display:none in jsdom
    const sliders = screen.getAllByRole('slider', { hidden: true });
    expect(sliders.length).toBeGreaterThanOrEqual(1);
  });

  it('renders multiple thumbs for range slider', () => {
    render(<Slider value={[25, 75]} />);
    const sliders = screen.getAllByRole('slider', { hidden: true });
    expect(sliders).toHaveLength(2);
  });

  it('renders with min and max attributes on thumbs', () => {
    render(<Slider value={[30]} min={10} max={90} />);
    const slider = screen.getByRole('slider', { hidden: true });
    expect(slider).toHaveAttribute('aria-valuemin', '10');
    expect(slider).toHaveAttribute('aria-valuemax', '90');
  });

  it('passes through additional HTML attributes', () => {
    const { container } = render(<Slider value={[50]} data-testid='my-slider' />);
    expect(container.querySelector("[data-testid='my-slider']")).toBeInTheDocument();
  });
});
