import { render, screen } from '@testing-library/react';
import { createRef } from 'react';
import * as Vitest from 'vitest';

import { Label } from '../components/Label';

Vitest.describe('Label component', () => {
  Vitest.it('renders as a label element', () => {
    render(<Label>Username</Label>);
    const label = screen.getByText('Username');
    Vitest.expect(label.tagName).toBe('LABEL');
  });

  Vitest.it('renders children text', () => {
    render(<Label>Email address</Label>);
    Vitest.expect(screen.getByText('Email address')).toBeInTheDocument();
  });

  Vitest.it('associates with input via htmlFor', () => {
    render(
      <>
        <Label htmlFor='email'>Email</Label>
        <input id='email' type='email' />
      </>,
    );
    const label = screen.getByText('Email');
    Vitest.expect(label).toHaveAttribute('for', 'email');
  });

  Vitest.it('forwards ref', () => {
    const ref = createRef<HTMLLabelElement>();
    render(<Label ref={ref}>Ref test</Label>);
    Vitest.expect(ref.current).toBeInstanceOf(HTMLLabelElement);
  });

  Vitest.it('applies custom className', () => {
    render(<Label className='custom-label'>Custom</Label>);
    Vitest.expect(screen.getByText('Custom').className).toContain('custom-label');
  });

  Vitest.it('passes through additional HTML attributes', () => {
    render(<Label data-testid='my-label'>Test</Label>);
    Vitest.expect(screen.getByTestId('my-label')).toBeInTheDocument();
  });
});
