import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';

import { Icon, IconSprite } from '../icon-sprite';

describe('IconSprite', () => {
  it('renders an SVG element with display:none', () => {
    const { container } = render(<IconSprite />);
    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    expect(svg?.style.display).toBe('none');
  });

  it('is marked aria-hidden', () => {
    const { container } = render(<IconSprite />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('aria-hidden')).toBe('true');
  });

  it('contains all expected icon symbols', () => {
    const { container } = render(<IconSprite />);
    const expectedIcons = [
      'icon-home',
      'icon-book-open',
      'icon-code',
      'icon-chevron-left',
      'icon-chevron-right',
      'icon-external-link',
      'icon-search',
      'icon-menu',
      'icon-close',
      'icon-github',
      'icon-info',
      'icon-warning',
      'icon-check-circle',
      'icon-error',
    ];

    expectedIcons.forEach((iconId) => {
      const symbol = container.querySelector(`#${iconId}`);
      expect(symbol, `Expected symbol #${iconId} to exist`).not.toBeNull();
    });
  });

  it('has defs element wrapping symbols', () => {
    const { container } = render(<IconSprite />);
    const defs = container.querySelector('defs');
    expect(defs).not.toBeNull();
    const symbols = defs?.querySelectorAll('symbol');
    expect(symbols?.length).toBeGreaterThan(0);
  });
});

describe('Icon', () => {
  it('renders an SVG element with a use tag referencing the sprite', () => {
    const { container } = render(<Icon name='home' />);
    const svg = container.querySelector('svg');
    expect(svg).not.toBeNull();
    const use = svg?.querySelector('use');
    expect(use?.getAttribute('href')).toBe('#icon-home');
  });

  it('applies the default size of 24', () => {
    const { container } = render(<Icon name='search' />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('width')).toBe('24');
    expect(svg?.getAttribute('height')).toBe('24');
  });

  it('applies custom size', () => {
    const { container } = render(<Icon name='menu' size={16} />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('width')).toBe('16');
    expect(svg?.getAttribute('height')).toBe('16');
  });

  it('applies custom className', () => {
    const { container } = render(<Icon name='close' className='text-red-500' />);
    const svg = container.querySelector('svg');
    expect(svg?.classList.contains('text-red-500')).toBe(true);
  });

  it('sets aria-label and role="img" when aria-label is provided', () => {
    render(<Icon name='home' aria-label='Home icon' />);
    const svg = screen.getByRole('img', { name: 'Home icon' });
    expect(svg).toBeInTheDocument();
  });

  it('does not set role when aria-label is not provided', () => {
    const { container } = render(<Icon name='home' />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('role')).toBeNull();
    expect(svg?.getAttribute('aria-label')).toBeNull();
  });

  it('has stroke="currentColor" and fill="none" for line icons', () => {
    const { container } = render(<Icon name='search' />);
    const svg = container.querySelector('svg');
    expect(svg?.getAttribute('stroke')).toBe('currentColor');
    expect(svg?.getAttribute('fill')).toBe('none');
  });
});
