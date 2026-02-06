import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it, vi } from 'vitest';

import { Textarea } from '../components/Textarea';

describe('Textarea', () => {
  it('renders a textarea element', () => {
    render(<Textarea />);
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('textbox').tagName).toBe('TEXTAREA');
  });

  it('accepts and displays a default value', () => {
    render(<Textarea defaultValue='Hello world' />);
    expect(screen.getByRole('textbox')).toHaveValue('Hello world');
  });

  it('handles onChange events', () => {
    const handleChange = vi.fn();
    render(<Textarea onChange={handleChange} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'new text' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('renders with placeholder', () => {
    render(<Textarea placeholder='Type here...' />);
    expect(screen.getByPlaceholderText('Type here...')).toBeInTheDocument();
  });

  it('can be disabled', () => {
    render(<Textarea disabled />);
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('forwards ref', () => {
    const ref = createRef<HTMLTextAreaElement>();
    render(<Textarea ref={ref} />);
    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('applies custom className', () => {
    render(<Textarea className='custom-textarea' />);
    expect(screen.getByRole('textbox').className).toContain('custom-textarea');
  });

  it('supports rows attribute', () => {
    render(<Textarea rows={10} />);
    expect(screen.getByRole('textbox')).toHaveAttribute('rows', '10');
  });
});
