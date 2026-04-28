import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Input } from '../components/Input';

Vitest.describe('Input component', () => {
  Vitest.it('renders an input element', () => {
    render(<Input />);
    Vitest.expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  Vitest.it('accepts and displays a value', () => {
    render(<Input defaultValue='hello' />);
    Vitest.expect(screen.getByRole('textbox')).toHaveValue('hello');
  });

  Vitest.it('handles onChange events', () => {
    const handleChange = Vitest.vi.fn();
    render(<Input onChange={handleChange} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'test' } });
    Vitest.expect(handleChange).toHaveBeenCalledTimes(1);
  });

  Vitest.it('renders with placeholder', () => {
    render(<Input placeholder='Enter text...' />);
    Vitest.expect(screen.getByPlaceholderText('Enter text...')).toBeInTheDocument();
  });

  Vitest.it('can be disabled', () => {
    render(<Input disabled />);
    Vitest.expect(screen.getByRole('textbox')).toBeDisabled();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Input className='custom-input' />);
    Vitest.expect(screen.getByRole('textbox').className).toContain('custom-input');
  });

  Vitest.it('supports different input types', () => {
    const { container } = render(<Input type='password' />);
    const input = container.querySelector('input');
    Vitest.expect(input).toHaveAttribute('type', 'password');
  });

  Vitest.it('supports type=email', () => {
    const { container } = render(<Input type='email' />);
    const input = container.querySelector('input');
    Vitest.expect(input).toHaveAttribute('type', 'email');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    render(<Input data-testid='my-input' name='username' />);
    Vitest.expect(screen.getByTestId('my-input')).toHaveAttribute('name', 'username');
  });
});
