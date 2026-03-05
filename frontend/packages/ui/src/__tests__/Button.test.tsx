import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it, vi } from 'vitest';

import { Button } from '../components/Button';

describe('Button component', () => {
  it('renders with children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('renders as a button element by default', () => {
    render(<Button>Test</Button>);
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('applies default variant classes', () => {
    render(<Button>Default</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-primary');
  });

  it('applies destructive variant classes', () => {
    render(<Button variant='destructive'>Delete</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-destructive');
  });

  it('applies outline variant classes', () => {
    render(<Button variant='outline'>Outline</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('border');
  });

  it('applies secondary variant classes', () => {
    render(<Button variant='secondary'>Secondary</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('bg-secondary');
  });

  it('applies ghost variant classes', () => {
    render(<Button variant='ghost'>Ghost</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('hover:bg-accent');
  });

  it('applies link variant classes', () => {
    render(<Button variant='link'>Link</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('underline-offset-4');
  });

  it('applies small size', () => {
    render(<Button size='sm'>Small</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('h-9');
  });

  it('applies large size', () => {
    render(<Button size='lg'>Large</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('h-11');
  });

  it('applies icon size', () => {
    render(<Button size='icon'>X</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('w-10');
  });

  it('applies xs size', () => {
    render(<Button size='xs'>Tiny</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('h-8');
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('can be disabled', () => {
    const handleClick = vi.fn();
    render(
      <Button disabled onClick={handleClick}>
        Disabled
      </Button>,
    );
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLButtonElement>();
    render(<Button ref={ref}>Ref</Button>);
    expect(ref.current).toBeInstanceOf(HTMLButtonElement);
  });

  it('merges custom className', () => {
    render(<Button className='my-custom-class'>Custom</Button>);
    const btn = screen.getByRole('button');
    expect(btn.className).toContain('my-custom-class');
  });

  it('renders as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href='/test'>Link Button</a>
      </Button>,
    );
    const link = screen.getByRole('link', { name: 'Link Button' });
    expect(link).toBeInTheDocument();
    expect(link.tagName).toBe('A');
  });

  it('passes through additional HTML attributes', () => {
    render(
      <Button data-testid='custom-btn' type='submit'>
        Submit
      </Button>,
    );
    expect(screen.getByTestId('custom-btn')).toBeInTheDocument();
    expect(screen.getByRole('button')).toHaveAttribute('type', 'submit');
  });
});
