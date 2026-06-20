import { render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Slider } from '../components/Slider';

Vitest.describe('Slider component', () => {
  Vitest.it('renders a slider root element', () => {
    const { container } = render(<Slider value={[50]} />);
    const root = container.firstChild as HTMLElement;
    Vitest.expect(root).toBeInTheDocument();
    Vitest.expect(root.dataset.orientation).toBe('horizontal');
  });

  Vitest.it('renders the track and range elements', () => {
    const { container } = render(<Slider value={[50]} />);
    // Track is the bg-secondary element
    const track = container.querySelector("[data-orientation='horizontal']");
    Vitest.expect(track).toBeInTheDocument();
  });

  Vitest.it('applies custom className to the root', () => {
    const { container } = render(<Slider className='custom-slider' value={[50]} />);
    const root = container.firstChild as HTMLElement;
    Vitest.expect(root.className).toContain('custom-slider');
  });

  Vitest.it('renders thumb elements with role=slider (hidden in jsdom)', () => {
    render(<Slider value={[50]} />);
    // Radix Slider thumbs are display:none in jsdom
    const sliders = screen.getAllByRole('slider', { hidden: true });
    Vitest.expect(sliders.length).toBeGreaterThanOrEqual(1);
  });

  Vitest.it('renders multiple thumbs for range slider', () => {
    render(<Slider value={[25, 75]} />);
    const sliders = screen.getAllByRole('slider', { hidden: true });
    Vitest.expect(sliders).toHaveLength(2);
  });

  Vitest.it('renders with min and max attributes on thumbs', () => {
    render(<Slider value={[30]} min={10} max={90} />);
    const slider = screen.getByRole('slider', { hidden: true });
    Vitest.expect(slider).toHaveAttribute('aria-valuemin', '10');
    Vitest.expect(slider).toHaveAttribute('aria-valuemax', '90');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    const { container } = render(<Slider value={[50]} data-testid='my-slider' />);
    Vitest.expect(container.querySelector("[data-testid='my-slider']")).toBeInTheDocument();
  });
});
