import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock next/link
vi.mock('next/link', () => ({
  default: ({
    href,
    children,
    className,
  }: {
    href: string;
    children: React.ReactNode;
    className?: string;
  }) => (
    <a href={href} className={className}>
      {children}
    </a>
  ),
}));

import HomePage from '../page';

describe('HomePage', () => {
  it('renders the main heading', () => {
    render(<HomePage />);
    expect(screen.getByText('TracerTM Documentation')).toBeInTheDocument();
  });

  it('renders the description', () => {
    render(<HomePage />);
    expect(
      screen.getByText('Complete documentation for the TracerTM platform'),
    ).toBeInTheDocument();
  });

  it('has a Get Started link pointing to /docs', () => {
    render(<HomePage />);
    const link = screen.getByText('Get Started').closest('a');
    expect(link?.getAttribute('href')).toBe('/docs');
  });

  it('has an API Reference link pointing to /api', () => {
    render(<HomePage />);
    const link = screen.getByText('API Reference').closest('a');
    expect(link?.getAttribute('href')).toBe('/api');
  });

  it('renders a main element', () => {
    render(<HomePage />);
    expect(screen.getByRole('main')).toBeInTheDocument();
  });
});
