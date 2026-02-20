import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { Badge } from '../components/Badge';

describe('Badge', () => {
  it('renders with children', () => {
    render(<Badge>New</Badge>);
    expect(screen.getByText('New')).toBeInTheDocument();
  });

  it('applies default variant', () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText('Default');
    expect(badge.className).toContain('bg-primary');
  });

  it('applies secondary variant', () => {
    render(<Badge variant='secondary'>Secondary</Badge>);
    expect(screen.getByText('Secondary').className).toContain('bg-secondary');
  });

  it('applies destructive variant', () => {
    render(<Badge variant='destructive'>Destructive</Badge>);
    expect(screen.getByText('Destructive').className).toContain('bg-destructive');
  });

  it('applies outline variant', () => {
    render(<Badge variant='outline'>Outline</Badge>);
    expect(screen.getByText('Outline').className).toContain('text-foreground');
  });

  it('applies success variant', () => {
    render(<Badge variant='success'>Success</Badge>);
    expect(screen.getByText('Success').className).toContain('bg-green-500');
  });

  it('applies warning variant', () => {
    render(<Badge variant='warning'>Warning</Badge>);
    expect(screen.getByText('Warning').className).toContain('bg-yellow-500');
  });

  it('applies info variant', () => {
    render(<Badge variant='info'>Info</Badge>);
    expect(screen.getByText('Info').className).toContain('bg-blue-500');
  });

  it('merges custom className', () => {
    render(<Badge className='my-badge'>Custom</Badge>);
    expect(screen.getByText('Custom').className).toContain('my-badge');
  });

  it('passes through additional HTML attributes', () => {
    render(<Badge data-testid='test-badge'>Test</Badge>);
    expect(screen.getByTestId('test-badge')).toBeInTheDocument();
  });
});
