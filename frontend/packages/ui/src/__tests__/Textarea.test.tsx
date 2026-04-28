import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Textarea } from '../components/Textarea';

Vitest.describe('Textarea component', () => {
  Vitest.it('renders a textarea element', () => {
    render(<Textarea />);
    Vitest.expect(screen.getByRole('textbox')).toBeInTheDocument();
    Vitest.expect(screen.getByRole('textbox').tagName).toBe('TEXTAREA');
  });

  Vitest.it('accepts and displays a default value', () => {
    render(<Textarea defaultValue='Hello world' />);
    Vitest.expect(screen.getByRole('textbox')).toHaveValue('Hello world');
  });

  Vitest.it('handles onChange events', () => {
    const handleChange = Vitest.vi.fn();
    render(<Textarea onChange={handleChange} />);
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'new text' } });
    Vitest.expect(handleChange).toHaveBeenCalledTimes(1);
  });

  Vitest.it('renders with placeholder', () => {
    render(<Textarea placeholder='Type here...' />);
    Vitest.expect(screen.getByPlaceholderText('Type here...')).toBeInTheDocument();
  });

  Vitest.it('can be disabled', () => {
    render(<Textarea disabled />);
    Vitest.expect(screen.getByRole('textbox')).toBeDisabled();
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLTextAreaElement>();
    render(<Textarea ref={ref} />);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Textarea className='custom-textarea' />);
    Vitest.expect(screen.getByRole('textbox').className).toContain('custom-textarea');
  });

  Vitest.it('supports rows attribute', () => {
    render(<Textarea rows={10} />);
    Vitest.expect(screen.getByRole('textbox')).toHaveAttribute('rows', '10');
  });
});
