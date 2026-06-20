import { render, screen } from '@testing-library/react';
import * as Vitest from 'vitest';

import { Badge } from '../components/Badge';

Vitest.describe('Badge component', () => {
  Vitest.it('renders with children', () => {
    render(<Badge>New</Badge>);
    Vitest.expect(screen.getByText('New')).toBeInTheDocument();
  });

  Vitest.it('applies default variant', () => {
    render(<Badge>Default</Badge>);
    const badge = screen.getByText('Default');
    Vitest.expect(badge.className).toContain('bg-primary');
  });

  Vitest.it('applies secondary variant', () => {
    render(<Badge variant='secondary'>Secondary</Badge>);
    Vitest.expect(screen.getByText('Secondary').className).toContain('bg-secondary');
  });

  Vitest.it('applies destructive variant', () => {
    render(<Badge variant='destructive'>Destructive</Badge>);
    Vitest.expect(screen.getByText('Destructive').className).toContain('bg-destructive');
  });

  Vitest.it('applies outline variant', () => {
    render(<Badge variant='outline'>Outline</Badge>);
    Vitest.expect(screen.getByText('Outline').className).toContain('text-foreground');
  });

  Vitest.it('applies success variant', () => {
    render(<Badge variant='success'>Success</Badge>);
    Vitest.expect(screen.getByText('Success').className).toContain('bg-green-500');
  });

  Vitest.it('applies warning variant', () => {
    render(<Badge variant='warning'>Warning</Badge>);
    Vitest.expect(screen.getByText('Warning').className).toContain('bg-yellow-500');
  });

  Vitest.it('applies info variant', () => {
    render(<Badge variant='info'>Info</Badge>);
    Vitest.expect(screen.getByText('Info').className).toContain('bg-blue-500');
  });

  Vitest.it('merges custom className', () => {
    render(<Badge className='my-badge'>Custom</Badge>);
    Vitest.expect(screen.getByText('Custom').className).toContain('my-badge');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    render(<Badge data-testid='test-badge'>Test</Badge>);
    Vitest.expect(screen.getByTestId('test-badge')).toBeInTheDocument();
  });
});
