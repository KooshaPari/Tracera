import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Button } from '../components/Button';

Vitest.describe('Button component', () => {
  Vitest.it('renders with children text', () => {
    render(<Button>Click me</Button>);
    Vitest.expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  Vitest.it('renders as a button element by default', () => {
    render(<Button>Test</Button>);
    Vitest.expect(screen.getByRole('button')).toBeInTheDocument();
  });

  Vitest.it('applies default variant classes', () => {
    render(<Button>Default</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('bg-primary');
  });

  Vitest.it('applies destructive variant classes', () => {
    render(<Button variant='destructive'>Delete</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('bg-destructive');
  });

  Vitest.it('applies outline variant classes', () => {
    render(<Button variant='outline'>Outline</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('border');
  });

  Vitest.it('applies secondary variant classes', () => {
    render(<Button variant='secondary'>Secondary</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('bg-secondary');
  });

  Vitest.it('applies ghost variant classes', () => {
    render(<Button variant='ghost'>Ghost</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('hover:bg-accent');
  });

  Vitest.it('applies link variant classes', () => {
    render(<Button variant='link'>Link</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('underline-offset-4');
  });

  Vitest.it('applies small size', () => {
    render(<Button size='sm'>Small</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('h-9');
  });

  Vitest.it('applies large size', () => {
    render(<Button size='lg'>Large</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('h-11');
  });

  Vitest.it('applies icon size', () => {
    render(<Button size='icon'>X</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('w-10');
  });

  Vitest.it('applies xs size', () => {
    render(<Button size='xs'>Tiny</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('h-8');
  });

  Vitest.it('handles click events', () => {
    const handleClick = Vitest.vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    Vitest.expect(handleClick).toHaveBeenCalledTimes(1);
  });

  Vitest.it('can be disabled', () => {
    const handleClick = Vitest.vi.fn();
    render(
      <Button disabled onClick={handleClick}>
        Disabled
      </Button>,
    );
    const btn = screen.getByRole('button');
    Vitest.expect(btn).toBeDisabled();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Ref</Button>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  Vitest.it('merges custom className', () => {
    render(<Button className='my-custom-class'>Custom</Button>);
    const btn = screen.getByRole('button');
    Vitest.expect(btn.className).toContain('my-custom-class');
  });

  Vitest.it('renders as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href='/test'>Link Button</a>
      </Button>,
    );
    const link = screen.getByRole('link', { name: 'Link Button' });
    Vitest.expect(link).toBeInTheDocument();
    Vitest.expect(link.tagName).toBe('A');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    render(
      <Button data-testid='custom-btn' type='submit'>
        Submit
      </Button>,
    );
    Vitest.expect(screen.getByTestId('custom-btn')).toBeInTheDocument();
    Vitest.expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
  });
});
