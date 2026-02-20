import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it, vi } from 'vitest';

import { Input } from '../components/Input';

describe('Input', () => {
  it('renders an input element', () => {
    render(<Input />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  it('accepts and displays a value', () => {
    render(<Input defaultValue='hello' />);
    expect(screen.getByRole('textbox')).toHaveValue('hello');
  });

  it('handles onChange events', () => {
    const handleChange = vi.fn();
    render(<Input onChange={handleChange} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'test' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('renders with placeholder', () => {
    render(<Input placeholder='Enter text...' />);
    expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument();
  });

  it('can be disabled', () => {
    render(<Input disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('applies custom className', () => {
    render(<Input className='custom-input' />);
    expect(screen.getByRole('textbox').className).toContain('custom-input');
  });

  it('supports different input types', () => {
    const { container } = render(<Input type='password' />);
    const input = container.querySelector('input');
    expect(input).toHaveAttribute('type', 'password');
  });

  it('supports type=email', () => {
    const { container } = render(<Input type='email' />);
    const input = container.querySelector('input');
    expect(input).toHaveAttribute('type', 'email');
  });

  it('passes through additional HTML attributes', () => {
    render(<Input data-testid='my-input' name='username' />);
    expect(screen.getByTestId('my-input')).toHaveAttribute('name', 'username');
  });
});
